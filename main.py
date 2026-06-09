"""
PingGuard - Cross-platform game ping monitor
Entry point
"""
import sys
import os

# Ensure single instance
import socket
_lock_socket = None

def check_single_instance():
    global _lock_socket
    _lock_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        _lock_socket.bind(('localhost', 47823))
    except OSError:
        print("PingGuard is already running.")
        sys.exit(0)

def main():
    check_single_instance()

    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from app import PingGuardApp

    # High DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in tray
    app.setApplicationName("PingGuard")
    app.setApplicationVersion("1.5.0")
    app.setOrganizationName("PingGuard")

    # Set app icon
    from app import get_app_icon
    app.setWindowIcon(get_app_icon())

    pingguard = PingGuardApp(app)
    pingguard.start()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
