"""
app.py - Main PingGuard application controller
Manages tray icon, windows, timers, and all component wiring.
"""
import sys
import os
from PyQt6.QtWidgets import (
    QSystemTrayIcon, QMenu, QApplication, QDialog
)
from PyQt6.QtCore import QTimer, Qt, QObject
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QBrush

from settings import Settings, GameManager
from ping_engine import PingWorker
from main_window import MainWindow
from logger import SessionLogger


def get_app_icon():
    """Load the app icon from assets folder."""
    import os, sys
    from PyQt6.QtGui import QIcon
    # Look relative to the script or executable
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    ico_path = os.path.join(base, "assets", "icon.ico")
    png_path = os.path.join(base, "assets", "icon.png")
    if os.path.exists(ico_path):
        return QIcon(ico_path)
    elif os.path.exists(png_path):
        return QIcon(png_path)
    return make_tray_icon()  # fallback to generated


def make_tray_icon(color="#4c4cff"):
    """Generate a simple tray icon with a ping wave symbol."""
    size = 64
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Background circle
    painter.setBrush(QBrush(QColor(color)))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, size - 8, size - 8)

    # White WiFi-like arcs
    from PyQt6.QtGui import QPen
    pen = QPen(QColor("white"), 4)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    cx, cy = size // 2, size // 2 + 6

    # Dot
    painter.setBrush(QBrush(QColor("white")))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(cx - 3, cy + 8, 6, 6)

    # Arcs
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(pen)
    from PyQt6.QtCore import QRectF
    for r, span in [(12, 90), (20, 80), (29, 70)]:
        rect = QRectF(cx - r, cy - r, r * 2, r * 2)
        painter.drawArc(rect, (90 + (90 - span) // 2) * 16, span * 16)

    painter.end()
    return QIcon(px)


class PingGuardApp(QObject):
    def __init__(self, qt_app):
        super().__init__()
        self.qt_app = qt_app
        self.settings = Settings()
        self.game_manager = GameManager()
        self.logger = SessionLogger()
        self.window = None
        self.tray = None
        self._countdown = 0
        self._checking = False

    def start(self):
        # First run wizard
        if self.settings.get("first_run", True):
            self._run_wizard()

        # Setup ping worker
        self.ping_worker = PingWorker(self.game_manager, self.settings)
        self.ping_worker.result_ready.connect(self._on_ping_result)
        self.ping_worker.batch_done.connect(self._on_batch_done)
        self.ping_worker.game_detected.connect(self._on_game_detected)

        # Build tray
        self._setup_tray()

        # Build main window
        self.window = MainWindow(self.game_manager, self.settings, self.ping_worker)
        self.window.check_now_requested.connect(self._check_now)
        self.window.settings_requested.connect(self._open_settings)

        if not self.settings.get("start_minimized", True):
            self.window.show()

        # Auto-check timer
        self._auto_timer = QTimer()
        self._auto_timer.timeout.connect(self._auto_tick)
        self._auto_timer.start(1000)  # tick every second
        self._countdown = self.settings.get("auto_check_interval", 120)

        # Game detection timer (every 10 seconds)
        self._detect_timer = QTimer()
        self._detect_timer.timeout.connect(self._check_running_games)
        self._detect_timer.start(10000)

        # Run first check after 3 seconds
        QTimer.singleShot(3000, self._check_now)

    def _run_wizard(self):
        from setup_wizard import SetupWizard
        wizard = SetupWizard(self.settings, self.game_manager)
        wizard.exec()

    def _setup_tray(self):
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(get_app_icon())
        self.tray.setToolTip("PingGuard — Click to open")

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background: #1e1e2e;
                color: #e0e0e0;
                border: 1px solid #3a3a5e;
                border-radius: 8px;
                padding: 4px;
                font-size: 12px;
            }
            QMenu::item { padding: 8px 20px; border-radius: 4px; }
            QMenu::item:selected { background: #3a3a5e; }
            QMenu::separator { height: 1px; background: #2a2a3e; margin: 4px 0; }
        """)

        open_action = menu.addAction("🎮  Open PingGuard")
        open_action.triggered.connect(self._show_window)

        check_action = menu.addAction("🔄  Check Now")
        check_action.triggered.connect(self._check_now)

        menu.addSeparator()

        settings_action = menu.addAction("⚙  Settings")
        settings_action.triggered.connect(self._open_settings)

        menu.addSeparator()

        quit_action = menu.addAction("✕  Quit")
        quit_action.triggered.connect(self.qt_app.quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_window()

    def _show_window(self):
        if self.window:
            self.window.show()
            self.window.raise_()
            self.window.activateWindow()

    def _check_now(self):
        if self._checking:
            return
        self._checking = True
        self._countdown = self.settings.get("auto_check_interval", 120)
        if self.window:
            self.window.set_checking(True)
        self.tray.setIcon(make_tray_icon("#ffeb3b"))
        self.ping_worker.ping_all()

    def _on_ping_result(self, result):
        self.logger.log(result)
        if self.window:
            self.window.update_game_ping(result)

        # Alert check
        threshold = self.settings.get("alert_threshold_ms", 150)
        if result.ms is not None and result.ms > threshold:
            self._alert_high_ping(result)
        elif not result.success:
            self._alert_unreachable(result)

    def _on_batch_done(self):
        self._checking = False
        if self.window:
            self.window.set_checking(False)
        self.tray.setIcon(make_tray_icon("#4c4cff"))

    def _on_game_detected(self, game_name):
        """Trigger a check when a monitored game is launched."""
        if self.settings.get("check_on_game_launch", True):
            QTimer.singleShot(5000, self._check_now)

        running = self.ping_worker.get_running_games()
        if self.window:
            self.window.show_running_games(list(running))

    def _check_running_games(self):
        self.ping_worker.check_running_games()
        running = self.ping_worker.get_running_games()
        if self.window:
            self.window.show_running_games(list(running))

    def _auto_tick(self):
        self._countdown -= 1
        if self.window:
            self.window.set_countdown(self._countdown)
        if self._countdown <= 0:
            self._check_now()

    def _alert_high_ping(self, result):
        if self.settings.get("notifications_enabled", True):
            from games import get_ping_status
            _, color = get_ping_status(result.ms)
            self.tray.showMessage(
                f"High Ping — {result.game_name}",
                f"Your ping to {result.game_name} is {result.ms}ms",
                QSystemTrayIcon.MessageIcon.Warning,
                3000
            )
        if self.settings.get("sound_enabled", True):
            self._play_alert_sound()

    def _alert_unreachable(self, result):
        if self.settings.get("notifications_enabled", True):
            self.tray.showMessage(
                f"Connection Failed — {result.game_name}",
                f"Could not reach {result.game_name} servers",
                QSystemTrayIcon.MessageIcon.Critical,
                3000
            )

    def _play_alert_sound(self):
        try:
            if sys.platform == "win32":
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            elif sys.platform == "darwin":
                os.system("afplay /System/Library/Sounds/Ping.aiff &")
            else:
                # Try paplay (PulseAudio) then aplay (ALSA) as fallback
                if os.system("paplay /usr/share/sounds/freedesktop/stereo/bell.oga &") != 0:
                    os.system("aplay /usr/share/sounds/alsa/Front_Center.wav &")
        except Exception:
            pass

    def _open_settings(self):
        from settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.settings, self.window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Apply startup setting
            self._apply_startup_setting()
            # Reset timer with new interval
            self._countdown = self.settings.get("auto_check_interval", 120)

    def _apply_startup_setting(self):
        """Set or remove Windows startup registry key."""
        if sys.platform != "win32":
            return
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if self.settings.get("start_with_windows", False):
                exe = sys.executable
                winreg.SetValueEx(key, "PingGuard", 0, winreg.REG_SZ, f'"{exe}"')
            else:
                try:
                    winreg.DeleteValue(key, "PingGuard")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception:
            pass
