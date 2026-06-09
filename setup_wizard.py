"""
setup_wizard.py - First-time setup wizard shown on first launch
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QWidget, QCheckBox, QComboBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from games import DEFAULT_GAMES


class SetupWizard(QDialog):
    def __init__(self, settings, game_manager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.game_manager = game_manager
        self.setWindowTitle("Welcome to PingGuard")
        self.setModal(True)
        self.setFixedSize(500, 520)
        self.setStyleSheet("""
            QDialog { background: #13131f; color: #e0e0e0; }
            QLabel { color: #e0e0e0; }
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, stretch=1)

        self.stack.addWidget(self._page_welcome())
        self.stack.addWidget(self._page_games())
        self.stack.addWidget(self._page_region())
        self.stack.addWidget(self._page_ready())

        # Navigation bar
        nav = QWidget()
        nav.setStyleSheet("background: #0d0d1a; border-top: 1px solid #2a2a3e;")
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(20, 14, 20, 14)

        self.back_btn = QPushButton("← Back")
        self.back_btn.setFixedHeight(36)
        self.back_btn.setStyleSheet("""
            QPushButton { background: #1e1e2e; color: #888888; border: 1px solid #2a2a3e;
                          border-radius: 6px; padding: 4px 16px; }
            QPushButton:hover { color: #e0e0e0; background: #262637; }
        """)
        self.back_btn.clicked.connect(self._go_back)
        self.back_btn.hide()

        self.step_label = QLabel("Step 1 of 4")
        self.step_label.setStyleSheet("color: #444466; font-size: 11px;")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.next_btn = QPushButton("Next →")
        self.next_btn.setFixedHeight(36)
        self.next_btn.setStyleSheet("""
            QPushButton { background: #4c4cff; color: white; border: none;
                          border-radius: 6px; padding: 4px 20px; font-weight: bold; }
            QPushButton:hover { background: #6666ff; }
        """)
        self.next_btn.clicked.connect(self._go_next)

        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.step_label)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)

        layout.addWidget(nav)

    def _page_welcome(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 30)
        layout.setSpacing(16)

        emoji = QLabel("🎮")
        emoji.setFont(QFont("Segoe UI Emoji", 48))
        emoji.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(emoji)

        title = QLabel("Welcome to PingGuard")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0ff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(
            "PingGuard monitors your connection to game servers\n"
            "and alerts you when your ping spikes or drops out —\n"
            "so you know if it's you or the servers."
        )
        desc.setStyleSheet("color: #888899; font-size: 13px; line-height: 1.6;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        features = QLabel("✓  Real ping testing, not fake ICMP\n✓  Runs quietly in your system tray\n✓  Alerts before you queue into a laggy game")
        features.setStyleSheet("color: #666680; font-size: 12px; line-height: 1.8;")
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(features)

        layout.addStretch()
        return page

    def _page_games(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 12)
        layout.setSpacing(10)

        title = QLabel("Which games do you play?")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0ff;")
        layout.addWidget(title)

        subtitle = QLabel("PingGuard will monitor these. You can change this later.")
        subtitle.setStyleSheet("color: #666680; font-size: 11px;")
        layout.addWidget(subtitle)

        # Select all
        sel_row = QHBoxLayout()
        sel_all = QPushButton("Select All")
        sel_all.setFixedHeight(28)
        sel_all.setStyleSheet("""
            QPushButton { background: transparent; color: #4c4cff; border: none; font-size: 11px; }
            QPushButton:hover { color: #8888ff; }
        """)
        sel_none = QPushButton("Select None")
        sel_none.setFixedHeight(28)
        sel_none.setStyleSheet(sel_all.styleSheet())

        sel_row.addWidget(sel_all)
        sel_row.addWidget(sel_none)
        sel_row.addStretch()
        layout.addLayout(sel_row)

        # Scrollable game list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(4)
        scroll_layout.setContentsMargins(0, 0, 4, 0)

        self.game_checks = {}
        for game in DEFAULT_GAMES:
            cb = QCheckBox(f"  {game['name']}  -  {game.get('category','')}")
            cb.setChecked(True)
            cb.setTristate(False)
            cb.setStyleSheet("""
                QCheckBox { color: #ccccdd; font-size: 12px; padding: 5px 4px; }
                QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px;
                    background: #1e1e2e; border: 2px solid #3a3a5e; }
                QCheckBox::indicator:checked { background: #4c4cff; border-color: #6666ff; }
                QCheckBox::indicator:unchecked { background: #1e1e2e; border-color: #3a3a5e; }
            """)
            self.game_checks[game["name"]] = cb
            scroll_layout.addWidget(cb)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, stretch=1)

        sel_all.clicked.connect(lambda: [cb.setChecked(True) for cb in self.game_checks.values()])
        sel_none.clicked.connect(lambda: [cb.setChecked(False) for cb in self.game_checks.values()])

        return page

    def _page_region(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 20)
        layout.setSpacing(16)

        title = QLabel("Where are you located?")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0ff;")
        layout.addWidget(title)

        desc = QLabel(
            "This helps PingGuard pick the right server endpoints\n"
            "to test against for accurate results."
        )
        desc.setStyleSheet("color: #666680; font-size: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(20)

        self.region_combo = QComboBox()
        regions = [
            ("🌍  Europe", "EU"),
            ("🌎  North America", "NA"),
            ("🌏  Asia Pacific", "Asia"),
            ("🌎  South America", "SA"),
            ("🌏  Oceania", "OCE"),
        ]
        for label, value in regions:
            self.region_combo.addItem(label, value)
        self.region_combo.setStyleSheet("""
            QComboBox {
                background: #1e1e2e; border: 1px solid #3a3a5e;
                border-radius: 8px; padding: 10px 16px;
                color: #e0e0e0; font-size: 14px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: #1e1e2e; color: #e0e0e0;
                border: 1px solid #3a3a5e; selection-background-color: #3a3a5e;
            }
        """)
        layout.addWidget(self.region_combo)

        layout.addStretch()

        note = QLabel("ℹ This can be changed in Settings at any time.")
        note.setStyleSheet("color: #444466; font-size: 11px;")
        layout.addWidget(note)

        return page

    def _page_ready(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 30)
        layout.setSpacing(16)

        emoji = QLabel("🚀")
        emoji.setFont(QFont("Segoe UI Emoji", 48))
        emoji.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(emoji)

        title = QLabel("You're all set!")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0ff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(
            "PingGuard will now run in your system tray.\n"
            "Right-click the tray icon to open, check ping, or quit.\n\n"
            "Click 'Start PingGuard' to run your first ping check!"
        )
        desc.setStyleSheet("color: #888899; font-size: 13px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()
        return page

    def _go_next(self):
        idx = self.stack.currentIndex()
        if idx == self.stack.count() - 1:
            self._finish()
            return

        self.stack.setCurrentIndex(idx + 1)
        self._update_nav()

    def _go_back(self):
        idx = self.stack.currentIndex()
        if idx > 0:
            self.stack.setCurrentIndex(idx - 1)
        self._update_nav()

    def _update_nav(self):
        idx = self.stack.currentIndex()
        total = self.stack.count()
        self.step_label.setText(f"Step {idx + 1} of {total}")
        self.back_btn.setVisible(idx > 0)
        self.next_btn.setText("Start PingGuard 🚀" if idx == total - 1 else "Next →")

    def _finish(self):
        # Save game selections
        for game in self.game_manager.games:
            checked = self.game_checks.get(game["name"])
            if checked is not None:
                game["enabled"] = checked.isChecked()
        self.game_manager.save()

        # Save region
        self.settings.set("user_region", self.region_combo.currentData())
        self.settings.set("first_run", False)

        self.accept()
