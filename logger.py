"""
logger.py - Session logging for ping history
Writes CSV logs per session that users can review or send for support.
"""
import csv
import os
from datetime import datetime
from pathlib import Path
from settings import LOGS_DIR


class SessionLogger:
    def __init__(self):
        self.session_start = datetime.now()
        self.log_file = LOGS_DIR / f"session_{self.session_start.strftime('%Y%m%d_%H%M%S')}.csv"
        self._init_log()
        self._cleanup_old_logs()

    def _init_log(self):
        with open(self.log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "game", "ping_ms", "status", "endpoint", "error"])

    def log(self, result):
        """Log a PingResult to the session file."""
        from games import get_ping_status
        status, _ = get_ping_status(result.ms)
        try:
            with open(self.log_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    result.timestamp,
                    result.game_name,
                    result.ms if result.ms is not None else "timeout",
                    status,
                    result.endpoint_used or "",
                    result.error or ""
                ])
        except Exception as e:
            print(f"Log error: {e}")

    def _cleanup_old_logs(self, keep_days=30):
        """Remove logs older than keep_days."""
        cutoff = datetime.now().timestamp() - (keep_days * 86400)
        try:
            for log_file in LOGS_DIR.glob("session_*.csv"):
                if log_file.stat().st_mtime < cutoff:
                    log_file.unlink()
        except Exception:
            pass

    def get_log_path(self):
        return str(self.log_file)

    def get_all_logs(self):
        """Return list of all log files, newest first."""
        logs = sorted(LOGS_DIR.glob("session_*.csv"), 
                     key=lambda f: f.stat().st_mtime, reverse=True)
        return [str(f) for f in logs]
