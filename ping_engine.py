"""
ping_engine.py - TCP connection testing and game process detection
Uses TCP SYN (connect) instead of ICMP ping to bypass server blocks.
"""
import sys
import socket
import time
import threading
import psutil
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class PingResult:
    def __init__(self, game_name, ms, success, endpoint_used, error=None):
        self.game_name = game_name
        self.ms = ms
        self.success = success
        self.endpoint_used = endpoint_used
        self.error = error
        self.timestamp = datetime.now().isoformat()


def tcp_ping(host, port, timeout=3.0):
    """
    Measure TCP connection time to host:port.
    Returns (ms, success, error_message)
    This bypasses ICMP blocks that game servers often use.
    """
    start = time.perf_counter()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        elapsed = (time.perf_counter() - start) * 1000
        sock.close()

        if result == 0:
            return round(elapsed), True, None
        else:
            # Connection refused still gives us a RTT — server is reachable
            # errno 111 = connection refused (Linux), 10061 = Windows refused
            if result in (111, 10061):
                return round(elapsed), True, None
            return None, False, f"Connect error {result}"

    except socket.timeout:
        elapsed = (time.perf_counter() - start) * 1000
        return None, False, f"Timeout after {timeout}s"
    except socket.gaierror as e:
        return None, False, f"DNS error: {e}"
    except Exception as e:
        return None, False, str(e)


def ping_game(game):
    """
    Try each endpoint for a game until one succeeds.
    Returns PingResult.
    """
    endpoints = game.get("endpoints", [])

    if not endpoints:
        return PingResult(game["name"], None, False, None, "No endpoints configured")

    last_error = None
    for endpoint in endpoints:
        host = endpoint["host"]
        port = endpoint["port"]
        ms, success, error = tcp_ping(host, port)

        if success:
            return PingResult(game["name"], ms, True, f"{host}:{port}")
        last_error = error

    return PingResult(game["name"], None, False,
                      f"{endpoints[-1]['host']}:{endpoints[-1]['port']}",
                      last_error)


def get_process_name_for_game(game):
    """
    Return the correct process name for the current platform.
    Falls back to stripping .exe from the Windows name if no
    platform-specific entry is defined.
    """
    if sys.platform == "darwin":
        return game.get("exe_mac") or game.get("exe", "").replace(".exe", "")
    elif sys.platform.startswith("linux"):
        return game.get("exe_linux") or game.get("exe", "").replace(".exe", "")
    else:
        return game.get("exe", "")


def get_running_game_exes():
    """
    Return set of currently running process names (lowercase).
    On Windows these include the .exe suffix; on Mac/Linux they don't.
    """
    running = set()
    try:
        for proc in psutil.process_iter(["name"]):
            try:
                name = proc.info["name"]
                if name:
                    running.add(name.lower())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception:
        pass
    return running


class PingWorker(QObject):
    """
    Background worker that periodically pings all enabled games.
    Emits signals when results are ready.
    """
    result_ready = pyqtSignal(object)   # PingResult
    batch_done = pyqtSignal()
    game_detected = pyqtSignal(str)     # game name

    def __init__(self, game_manager, settings):
        super().__init__()
        self.game_manager = game_manager
        self.settings = settings
        self._stop = False
        self._running_games = set()

    def ping_all(self):
        """Ping all enabled games in background threads."""
        games = self.game_manager.get_enabled()
        threads = []

        for game in games:
            t = threading.Thread(target=self._ping_one, args=(game,), daemon=True)
            threads.append(t)
            t.start()

        def wait_and_signal():
            for t in threads:
                t.join(timeout=10)
            self.batch_done.emit()

        threading.Thread(target=wait_and_signal, daemon=True).start()

    def _ping_one(self, game):
        result = ping_game(game)
        ts = datetime.now().isoformat()
        self.game_manager.update_ping(game["name"], result.ms, ts)
        self.result_ready.emit(result)

    def ping_single(self, game):
        """Ping a single game."""
        threading.Thread(target=self._ping_one, args=(game,), daemon=True).start()

    def check_running_games(self):
        """
        Check if any monitored games are currently running.
        Uses platform-appropriate process names for matching.
        """
        running_exes = get_running_game_exes()
        games = self.game_manager.get_enabled()

        for game in games:
            proc_name = get_process_name_for_game(game).lower()

            # Minecraft special case: 'java' matches too broadly on Mac/Linux.
            # Only match if the game is Minecraft and we're on Windows, where
            # the process is the specific 'javaw.exe'.
            if game["name"] == "Minecraft" and sys.platform != "win32":
                self._running_games.discard(game["name"])
                continue

            if proc_name and proc_name in running_exes:
                if game["name"] not in self._running_games:
                    self._running_games.add(game["name"])
                    self.game_detected.emit(game["name"])
            else:
                self._running_games.discard(game["name"])

    def get_running_games(self):
        return set(self._running_games)
