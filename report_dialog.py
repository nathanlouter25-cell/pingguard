"""
report_dialog.py - "This game isn't working" report dialog
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from reporter import send_report


ISSUE_TYPES = [
    ("game_not_working", "Ping always fails / shows as offline"),
    ("wrong_ping", "Ping seems incorrect"),
    ("game_not_detected", "Game running but not being detected"),
    ("other", "Other issue"),
]


class ReportDialog(QDialog):
    def __init__(self, game, webhook_url, parent=None):
        super().__init__(parent)
        self.game = game
        self.webhook_url = webhook_url
        self.setWindowTitle(f"Report Issue — {game['name']}")
        self.setModal(True)
        self.setFixedSize(440, 360)
        self.setStyleSheet("""
            QDialog { background: #13131f; color: #e0e0e0; }
            QLabel { color: #e0e0e0; }
            QTextEdit, QComboBox {
                background: #1e1e2e;
                border: 1px solid #3a3a5e;
                border-radius: 6px;
                padding: 6px 10px;
                color: #e0e0e0;
                font-size: 12px;
            }
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel(f"⚠ Report Issue: {self.game['name']}")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #ff9800;")
        layout.addWidget(title)

        info = QLabel(
            "This sends an anonymous report to the developer so the game\n"
            "can be fixed in a future update. No personal data is sent."
        )
        info.setStyleSheet("color: #666680; font-size: 11px;")
        layout.addWidget(info)

        # Issue type
        type_label = QLabel("What's the issue?")
        type_label.setStyleSheet("color: #aaaacc; font-size: 11px; font-weight: bold;")
        layout.addWidget(type_label)

        self.issue_combo = QComboBox()
        for value, label in ISSUE_TYPES:
            self.issue_combo.addItem(label, value)
        layout.addWidget(self.issue_combo)

        # Details
        details_label = QLabel("Additional details (optional):")
        details_label.setStyleSheet("color: #aaaacc; font-size: 11px; font-weight: bold;")
        layout.addWidget(details_label)

        self.details_input = QTextEdit()
        self.details_input.setPlaceholderText("e.g. 'Game loads fine but ping always shows as failed'")
        self.details_input.setMaximumHeight(80)
        layout.addWidget(self.details_input)

        layout.addStretch()

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.status_label)

        # Buttons
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(36)
        cancel_btn.setStyleSheet("""
            QPushButton { background: #1e1e2e; color: #e0e0e0; border: 1px solid #3a3a5e;
                          border-radius: 6px; padding: 4px 16px; }
            QPushButton:hover { background: #262637; }
        """)
        cancel_btn.clicked.connect(self.reject)

        self.send_btn = QPushButton("Send Report")
        self.send_btn.setFixedHeight(36)
        self.send_btn.setStyleSheet("""
            QPushButton { background: #ff6b35; color: white; border: none;
                          border-radius: 6px; padding: 4px 16px; font-weight: bold; }
            QPushButton:hover { background: #ff8555; }
        """)
        self.send_btn.clicked.connect(self._send)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self.send_btn)
        layout.addLayout(btn_row)

    def _send(self):
        if not self.webhook_url:
            self.status_label.setText("⚠ No webhook configured in settings.")
            self.status_label.setStyleSheet("color: #ff9800; font-size: 11px;")
            return

        self.send_btn.setEnabled(False)
        self.send_btn.setText("Sending…")

        issue_type = self.issue_combo.currentData()
        details = self.details_input.toPlainText().strip()
        history = self.game.get("ping_history", [])

        success, msg = send_report(self.webhook_url, self.game, issue_type, details, history)

        if success:
            self.status_label.setText("✓ Report sent! Thank you.")
            self.status_label.setStyleSheet("color: #00e676; font-size: 11px;")
            self.send_btn.setText("Sent!")
        else:
            self.status_label.setText(f"✗ Failed to send: {msg}")
            self.status_label.setStyleSheet("color: #f44336; font-size: 11px;")
            self.send_btn.setText("Send Report")
            self.send_btn.setEnabled(True)
