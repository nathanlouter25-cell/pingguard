"""
settings_dialog.py - Settings window
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QSpinBox, QTabWidget, QWidget,
    QFormLayout, QComboBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("PingGuard Settings")
        self.setModal(True)
        self.setFixedSize(460, 440)
        self.setStyleSheet("""
            QDialog { background: #13131f; color: #e0e0e0; }
            QLabel { color: #e0e0e0; }
            QLineEdit, QSpinBox, QComboBox {
                background: #1e1e2e;
                border: 1px solid #3a3a5e;
                border-radius: 6px;
                padding: 6px 10px;
                color: #e0e0e0;
                font-size: 12px;
            }
            QCheckBox { color: #e0e0e0; font-size: 12px; spacing: 8px; }
            QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px;
                background: #1e1e2e; border: 1px solid #3a3a5e; }
            QCheckBox::indicator:checked { background: #4c4cff; border-color: #6666ff; }
            QTabWidget::pane { border: 1px solid #2a2a3e; border-radius: 8px; background: #13131f; }
            QTabBar::tab { background: #1a1a2e; color: #888888; padding: 8px 16px;
                           border-radius: 6px 6px 0 0; margin-right: 2px; }
            QTabBar::tab:selected { background: #13131f; color: #e0e0e0; border-bottom: 2px solid #4c4cff; }
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("⚙ Settings")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0ff;")
        layout.addWidget(title)

        tabs = QTabWidget()

        # --- General tab ---
        general = QWidget()
        gen_layout = QFormLayout(general)
        gen_layout.setSpacing(12)
        gen_layout.setContentsMargins(16, 16, 16, 16)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(30, 600)
        self.interval_spin.setSuffix(" seconds")
        self.interval_spin.setValue(self.settings.get("auto_check_interval", 120))
        gen_layout.addRow("Auto-check every:", self.interval_spin)

        self.alert_spin = QSpinBox()
        self.alert_spin.setRange(50, 500)
        self.alert_spin.setSuffix(" ms")
        self.alert_spin.setValue(self.settings.get("alert_threshold_ms", 150))
        gen_layout.addRow("Alert if ping above:", self.alert_spin)

        self.region_combo = QComboBox()
        for r in ["EU", "NA", "Asia", "SA", "OCE"]:
            self.region_combo.addItem(r)
        self.region_combo.setCurrentText(self.settings.get("user_region", "EU"))
        gen_layout.addRow("Your Region:", self.region_combo)

        self.sound_check = QCheckBox("Play sound on high ping / disconnect")
        self.sound_check.setChecked(self.settings.get("sound_enabled", True))
        gen_layout.addRow("", self.sound_check)

        self.notif_check = QCheckBox("Show desktop notifications")
        self.notif_check.setChecked(self.settings.get("notifications_enabled", True))
        gen_layout.addRow("", self.notif_check)

        self.minimized_check = QCheckBox("Start minimized to tray")
        self.minimized_check.setChecked(self.settings.get("start_minimized", True))
        gen_layout.addRow("", self.minimized_check)

        self.startup_check = QCheckBox("Start with Windows")
        self.startup_check.setChecked(self.settings.get("start_with_windows", False))
        gen_layout.addRow("", self.startup_check)

        tabs.addTab(general, "General")

        # --- Reporting tab ---
        reporting = QWidget()
        rep_layout = QVBoxLayout(reporting)
        rep_layout.setContentsMargins(16, 16, 16, 16)
        rep_layout.setSpacing(12)

        rep_info = QLabel(
            "Set up a Discord webhook to receive anonymous reports\n"
            "when users report game issues. This helps you fix detection\n"
            "for games that aren't working correctly."
        )
        rep_info.setStyleSheet("color: #666680; font-size: 11px;")
        rep_info.setWordWrap(True)
        rep_layout.addWidget(rep_info)

        webhook_label = QLabel("Discord Webhook URL:")
        webhook_label.setStyleSheet("color: #aaaacc; font-size: 11px; font-weight: bold;")
        rep_layout.addWidget(webhook_label)

        self.webhook_input = QLineEdit()
        self.webhook_input.setPlaceholderText("https://discord.com/api/webhooks/...")
        self.webhook_input.setText(self.settings.get("discord_webhook", ""))
        rep_layout.addWidget(self.webhook_input)

        how_to = QLabel("How to get a webhook URL:\nDiscord → Server → Edit → Integrations → Webhooks → New Webhook")
        how_to.setStyleSheet("color: #444466; font-size: 10px;")
        rep_layout.addWidget(how_to)

        test_btn = QPushButton("Test Webhook")
        test_btn.setFixedHeight(32)
        test_btn.setStyleSheet("""
            QPushButton { background: #1e1e2e; color: #e0e0e0; border: 1px solid #3a3a5e;
                          border-radius: 6px; padding: 4px 14px; font-size: 12px; }
            QPushButton:hover { background: #262637; }
        """)
        test_btn.clicked.connect(self._test_webhook)
        rep_layout.addWidget(test_btn)

        self.webhook_status = QLabel("")
        self.webhook_status.setStyleSheet("font-size: 11px;")
        rep_layout.addWidget(self.webhook_status)

        rep_layout.addStretch()
        tabs.addTab(reporting, "Reporting")

        layout.addWidget(tabs, stretch=1)

        # Save / Cancel
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(36)
        cancel_btn.setStyleSheet("""
            QPushButton { background: #1e1e2e; color: #e0e0e0; border: 1px solid #3a3a5e;
                          border-radius: 6px; padding: 4px 16px; }
            QPushButton:hover { background: #262637; }
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Settings")
        save_btn.setFixedHeight(36)
        save_btn.setStyleSheet("""
            QPushButton { background: #4c4cff; color: white; border: none;
                          border-radius: 6px; padding: 4px 16px; font-weight: bold; }
            QPushButton:hover { background: #6666ff; }
        """)
        save_btn.clicked.connect(self._save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _test_webhook(self):
        url = self.webhook_input.text().strip()
        if not url:
            self.webhook_status.setText("⚠ Enter a webhook URL first.")
            self.webhook_status.setStyleSheet("color: #ff9800; font-size: 11px;")
            return

        from reporter import send_report
        test_game = {"name": "Test", "category": "Test", "endpoints": [], "last_ping": 42, "ping_history": []}
        success, msg = send_report(url, test_game, "other", "This is a test message from PingGuard settings.")
        if success:
            self.webhook_status.setText("✓ Webhook works!")
            self.webhook_status.setStyleSheet("color: #00e676; font-size: 11px;")
        else:
            self.webhook_status.setText(f"✗ {msg}")
            self.webhook_status.setStyleSheet("color: #f44336; font-size: 11px;")

    def _save(self):
        self.settings.set("auto_check_interval", self.interval_spin.value())
        self.settings.set("alert_threshold_ms", self.alert_spin.value())
        self.settings.set("user_region", self.region_combo.currentText())
        self.settings.set("sound_enabled", self.sound_check.isChecked())
        self.settings.set("notifications_enabled", self.notif_check.isChecked())
        self.settings.set("start_minimized", self.minimized_check.isChecked())
        self.settings.set("start_with_windows", self.startup_check.isChecked())
        self.settings.set("discord_webhook", self.webhook_input.text().strip())
        self.accept()
