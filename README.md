# PingGuard

Know your lag before the game does.

PingGuard sits in your system tray and monitors ping to 20 popular game servers in real time — using TCP instead of ICMP so it actually works even when servers block standard pings.

![PingGuard cover](assets/cover.png)

## Features

- 20 pre-loaded games (Valorant, CS2, League, Fortnite, Apex and more)
- TCP-based ping — bypasses ICMP blocks on game servers
- Sparkline history graph per game
- Colour-coded status: excellent / good / fair / poor / critical
- System tray only — no taskbar clutter
- Auto-check every 2 minutes, or on demand
- Detects when a monitored game is running and checks automatically
- Desktop notifications + sound alert on high ping
- Session CSV logs
- Discord webhook reporting
- Add your own custom game endpoints

## Downloads

| Platform | Status |
|----------|--------|
| Windows | ✅ Stable |
| macOS | 🧪 Beta |
| Linux | 🧪 Beta |

[→ Latest release](../../releases/latest)

## Running from source

```bash
pip install PyQt6 psutil
python main.py
```

Requires Python 3.10+.

## Building

Builds are automated via GitHub Actions on every `v*` tag push:

```bash
git tag v2.0
git push origin v2.0
```

This triggers a build for Windows, macOS, and Linux. Binaries appear under [Releases](../../releases).

## Platform notes

**macOS:** First launch requires right-click → Open due to Gatekeeper. System tray lives in the menu bar.

**Linux:** Requires a system tray. Works out of the box on KDE and XFCE. On GNOME you need the [AppIndicator extension](https://extensions.gnome.org/extension/615/appindicator-support/).

## License

MIT
