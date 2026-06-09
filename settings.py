"""
settings.py - Persistent settings and game config storage
Uses JSON files in the user's AppData/config directory
"""
import json
import os
import sys
from pathlib import Path
from games import DEFAULT_GAMES


def get_data_dir():
    """Get the platform-appropriate data directory."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home())
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
    
    data_dir = Path(base) / "PingGuard"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


DATA_DIR = get_data_dir()
SETTINGS_FILE = DATA_DIR / "settings.json"
GAMES_FILE = DATA_DIR / "games.json"
LOGS_DIR = DATA_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
(DATA_DIR / "assets").mkdir(exist_ok=True)
(DATA_DIR / "data").mkdir(exist_ok=True)


DEFAULT_SETTINGS = {
    "first_run": True,
    "auto_check_interval": 120,       # seconds
    "sound_enabled": True,
    "notifications_enabled": True,
    "start_minimized": True,
    "start_with_windows": False,
    "alert_threshold_ms": 150,         # alert if ping goes above this
    "discord_webhook": "https://discord.com/api/webhooks/1513504673343078552/FMb7PLlskpWCk4gqXsVEUFOG5yOMgrYpO2YkAVgOV9h9PVLvE1AmIYmvXwIXT1S6FU9y",
    "user_region": "EU",
    "check_on_game_launch": True,
    "theme": "dark",
    "version": "1.0.0",
}


class Settings:
    def __init__(self):
        self._data = {}
        self.load()

    def load(self):
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r") as f:
                    saved = json.load(f)
                # Merge with defaults (adds new keys from updates)
                self._data = {**DEFAULT_SETTINGS, **saved}
            except Exception:
                self._data = DEFAULT_SETTINGS.copy()
        else:
            self._data = DEFAULT_SETTINGS.copy()

    def save(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self.set(key, value)



def migrate_game_endpoints(games_list):
    """Update endpoints for games that had bad defaults."""
    fixes = {
        'CS2': [
            {'host': 'steamcommunity.com', 'port': 443},
            {'host': 'api.steampowered.com', 'port': 443},
        ],
        'Dota 2': [
            {'host': 'steamcommunity.com', 'port': 443},
            {'host': 'api.steampowered.com', 'port': 443},
        ],
    }
    changed = False
    for game in games_list:
        if game['name'] in fixes:
            current_hosts = [e['host'] for e in game.get('endpoints', [])]
            if any(h.startswith('185.') or h.startswith('146.') for h in current_hosts):
                game['endpoints'] = fixes[game['name']]
                game['region_note'] = 'Steam servers'
                changed = True
    return changed

class GameManager:
    def __init__(self):
        self._games = []
        self.load()

    def load(self):
        if GAMES_FILE.exists():
            try:
                with open(GAMES_FILE, "r") as f:
                    self._games = json.load(f)
                if migrate_game_endpoints(self._games):
                    self.save()
            except Exception:
                self._reset_to_defaults()
        else:
            self._reset_to_defaults()

    def _reset_to_defaults(self):
        """Load default games with enabled=True and empty history."""
        self._games = []
        for g in DEFAULT_GAMES:
            game = dict(g)
            game["enabled"] = True
            game["last_ping"] = None
            game["last_checked"] = None
            game["ping_history"] = []   # list of {ts, ms} dicts
            self._games.append(game)
        self.save()

    def save(self):
        try:
            with open(GAMES_FILE, "w") as f:
                json.dump(self._games, f, indent=2)
        except Exception as e:
            print(f"Failed to save games: {e}")

    @property
    def games(self):
        return self._games

    def get_enabled(self):
        return [g for g in self._games if g.get("enabled", True)]

    def update_ping(self, game_name, ping_ms, timestamp):
        for game in self._games:
            if game["name"] == game_name:
                game["last_ping"] = ping_ms
                game["last_checked"] = timestamp
                # Keep last 60 readings (2hrs at 2min intervals)
                history = game.get("ping_history", [])
                history.append({"ts": timestamp, "ms": ping_ms})
                game["ping_history"] = history[-60:]
                break
        self.save()

    def add_game(self, game_dict):
        game_dict["enabled"] = True
        game_dict["last_ping"] = None
        game_dict["last_checked"] = None
        game_dict["ping_history"] = []
        self._games.append(game_dict)
        self.save()

    def remove_game(self, game_name):
        self._games = [g for g in self._games if g["name"] != game_name]
        self.save()

    def update_game(self, game_name, updates):
        for game in self._games:
            if game["name"] == game_name:
                game.update(updates)
                break
        self.save()
