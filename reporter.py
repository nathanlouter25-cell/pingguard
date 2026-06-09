"""
reporter.py - Sends "game not working" reports to Discord webhook
Also handles crash reporting. Completely anonymous - no personal data.
"""
import json
import platform
import sys
from datetime import datetime


def send_report(webhook_url, game, issue_type, details, ping_history=None):
    """
    Send a report to the developer's Discord webhook.
    All data is anonymous - no user info, no IP, just game data.
    """
    if not webhook_url:
        return False, "No webhook configured"

    try:
        import urllib.request

        # Build the Discord embed
        color = 0xFF6B35 if issue_type == "game_not_working" else 0xFF0000

        history_text = ""
        if ping_history:
            recent = ping_history[-5:]
            vals = [str(r.get("ms", "?")) for r in recent]
            history_text = f"\n**Last pings:** {' → '.join(vals)} ms"

        embed = {
            "title": f"🚨 Report: {game['name']}",
            "color": color,
            "fields": [
                {"name": "Issue", "value": issue_type.replace("_", " ").title(), "inline": True},
                {"name": "Game", "value": game["name"], "inline": True},
                {"name": "Category", "value": game.get("category", "Unknown"), "inline": True},
                {"name": "Endpoints tried", 
                 "value": "\n".join([f"{e['host']}:{e['port']}" for e in game.get("endpoints", [])]),
                 "inline": False},
                {"name": "Last ping", "value": f"{game.get('last_ping', 'N/A')} ms", "inline": True},
                {"name": "Platform", "value": sys.platform, "inline": True},
                {"name": "Details", "value": details or "No details provided", "inline": False},
            ],
            "footer": {"text": f"PingGuard v1.0.0 • {datetime.now().strftime('%Y-%m-%d %H:%M')}"},
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        if history_text:
            embed["description"] = history_text

        payload = json.dumps({"embeds": [embed]}).encode("utf-8")

        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "PingGuard/1.0"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status in (200, 204):
                return True, "Report sent successfully"
            return False, f"HTTP {resp.status}"

    except Exception as e:
        return False, str(e)


def send_crash_report(webhook_url, error_info):
    """Send an automatic crash report (opt-in only)."""
    if not webhook_url:
        return

    try:
        import urllib.request

        embed = {
            "title": "💥 Crash Report",
            "color": 0xFF0000,
            "description": f"```\n{str(error_info)[:1800]}\n```",
            "fields": [
                {"name": "Platform", "value": sys.platform, "inline": True},
                {"name": "Python", "value": sys.version.split()[0], "inline": True},
            ],
            "footer": {"text": f"PingGuard v1.0.0 • {datetime.now().strftime('%Y-%m-%d %H:%M')}"},
        }

        payload = json.dumps({"embeds": [embed]}).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "PingGuard/1.0"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass  # Never crash on crash reporting
