"""
add_game_dialog.py - Dialog for adding a custom game
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


CATEGORIES = ["FPS", "MOBA", "MMO", "ARPG", "Battle Royale", "Sports", "Sandbox", "Open World", "Other"]
ICONS = ["🎮", "🎯", "🔫", "⚔️", "🏆", "🛡️", "💥", "🚀", "⚡", "🌙", "💀", "🗺️", "⚽", "🚗", "🪟", "🌌"]


class AddGameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Game")
        self.setModal(True)
        self.setFixedSize(420, 400)
        self.setStyleSheet("""
            QDialog { background: #13131f; color: #e0e0e0; }
            QLabel { color: #e0e0e0; }
            QLineEdit, QComboBox, QSpinBox {
                background: #1e1e2e;
                border: 1px solid #3a3a5e;
                border-radius: 6px;
                padding: 6px 10px;
                color: #e0e0e0;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #6666ff;
            }
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Add a Game")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0ff;")
        layout.addWidget(title)

        subtitle = QLabel("PingGuard will test the connection to this game's servers.")
        subtitle.setStyleSheet("color: #666680; font-size: 11px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. My Game")
        form.addRow("Game Name:", self.name_input)

        self.exe_input = QLineEdit()
        self.exe_input.setPlaceholderText("e.g. mygame.exe")
        form.addRow("Process (.exe):", self.exe_input)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("e.g. api.mygame.com")
        form.addRow("Server Host:", self.host_input)

        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(443)
        form.addRow("Port:", self.port_input)

        self.category_input = QComboBox()
        for c in CATEGORIES:
            self.category_input.addItem(c)
        form.addRow("Category:", self.category_input)

        self.icon_input = QComboBox()
        for icon in ICONS:
            self.icon_input.addItem(icon)
        form.addRow("Icon:", self.icon_input)

        layout.addLayout(form)
        layout.addStretch()

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

        add_btn = QPushButton("Add Game")
        add_btn.setFixedHeight(36)
        add_btn.setStyleSheet("""
            QPushButton { background: #4c4cff; color: white; border: none;
                          border-radius: 6px; padding: 4px 16px; font-weight: bold; }
            QPushButton:hover { background: #6666ff; }
        """)
        add_btn.clicked.connect(self.accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(add_btn)
        layout.addLayout(btn_row)

    def get_game_data(self):
        name = self.name_input.text().strip()
        host = self.host_input.text().strip()
        if not name or not host:
            return None
        return {
            "name": name,
            "exe": self.exe_input.text().strip(),
            "icon": self.icon_input.currentText(),
            "category": self.category_input.currentText(),
            "region_note": "Custom",
            "endpoints": [{"host": host, "port": self.port_input.value()}],
        }
