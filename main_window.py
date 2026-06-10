"""
main_window.py - The main PingGuard UI window
Shows all games with their ping status, history graph, controls.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QMessageBox, QDialog,
    QLineEdit, QComboBox, QCheckBox, QSpinBox, QTabWidget,
    QTextEdit, QFileDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QIcon, QPixmap, QBrush, QPolygonF
from PyQt6.QtCore import QPointF
from games import get_ping_status, DEFAULT_GAMES
from add_game_dialog import AddGameDialog
from report_dialog import ReportDialog
import datetime


class PingBar(QWidget):
    """Mini ping history sparkline graph."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = []
        self.setMinimumSize(80, 30)
        self.setMaximumSize(120, 30)

    def set_history(self, history):
        self.history = [h.get("ms") for h in history[-20:] if h.get("ms") is not None]
        self.update()

    def paintEvent(self, event):
        if not self.history or len(self.history) < 2:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        margin = 3
        max_val = max(max(self.history), 100)
        min_val = 0

        points = []
        for i, val in enumerate(self.history):
            x = margin + (i / (len(self.history) - 1)) * (w - 2 * margin)
            y = h - margin - ((val - min_val) / (max_val - min_val)) * (h - 2 * margin)
            points.append((x, y))

        _, color = get_ping_status(self.history[-1])
        pen = QPen(QColor(color), 1.5)
        painter.setPen(pen)

        for i in range(len(points) - 1):
            painter.drawLine(int(points[i][0]), int(points[i][1]),
                           int(points[i+1][0]), int(points[i+1][1]))


class PingDot(QWidget):
    """Status dot."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = "#888888"
        self.setFixedSize(14, 14)

    def set_color(self, color):
        self.color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(self.color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 10, 10)


class PingHistoryChart(QWidget):
    """Expanded full ping history chart with filled area, gridlines, stats."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = []   # list of ms values (ints)
        self.color = "#00e676"
        self.setMinimumHeight(110)
        self.setMaximumHeight(110)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_history(self, history, color):
        self.history = [h.get("ms") for h in history if h.get("ms") is not None]
        self.color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        left_margin = 28
        right_margin = 8
        top_margin = 10
        bottom_margin = 22   # room for stats text

        chart_w = w - left_margin - right_margin
        chart_h = h - top_margin - bottom_margin

        # Background
        painter.fillRect(0, 0, w, h, QColor("#13131f"))

        if not self.history or len(self.history) < 2:
            painter.setPen(QColor("#444466"))
            painter.drawText(0, 0, w, h, Qt.AlignmentFlag.AlignCenter, "No data yet")
            return

        max_val = max(max(self.history), 100)
        min_val = 0

        # Gridlines + Y labels
        grid_pen = QPen(QColor("#1e1e35"), 1)
        grid_pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        label_font = QFont("Consolas", 7)
        painter.setFont(label_font)

        for grid_val in [0, 50, 100, 150, 200]:
            if grid_val > max_val * 1.1:
                continue
            y = top_margin + chart_h - (grid_val / max_val) * chart_h
            painter.setPen(grid_pen)
            painter.drawLine(left_margin, int(y), left_margin + chart_w, int(y))
            painter.setPen(QColor("#444466"))
            painter.drawText(0, int(y) - 6, left_margin - 2, 12,
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             str(grid_val))

        # Build points
        points = []
        for i, val in enumerate(self.history):
            x = left_margin + (i / (len(self.history) - 1)) * chart_w
            y = top_margin + chart_h - ((val - min_val) / (max_val - min_val)) * chart_h
            points.append(QPointF(x, y))

        # Filled area under the line
        fill_color = QColor(self.color)
        fill_color.setAlpha(35)
        poly = QPolygonF()
        poly.append(QPointF(points[0].x(), top_margin + chart_h))
        for p in points:
            poly.append(p)
        poly.append(QPointF(points[-1].x(), top_margin + chart_h))
        painter.setBrush(QBrush(fill_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(poly)

        # Line
        line_pen = QPen(QColor(self.color), 1.8)
        line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(line_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i + 1])

        # Dot at last point
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(Qt.PenStyle.NoPen)
        lp = points[-1]
        painter.drawEllipse(lp, 3.5, 3.5)

        # Stats bar at bottom
        stats_y = h - bottom_margin + 6
        painter.setFont(QFont("Consolas", 8))
        painter.setPen(QColor("#667788"))

        mn = min(self.history)
        avg = int(sum(self.history) / len(self.history))
        mx = max(self.history)
        samples = len(self.history)

        stats_text = f"min {mn}ms    avg {avg}ms    max {mx}ms    samples {samples}"
        painter.drawText(left_margin, stats_y, chart_w, 14,
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         stats_text)


class GameRow(QFrame):
    """A single game row — click to expand/collapse ping history chart."""
    report_clicked = pyqtSignal(dict)

    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self._expanded = False
        self._history = []
        self._last_ms = None
        self._last_color = "#888888"

        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            GameRow {
                background: #1e1e2e;
                border-radius: 8px;
                margin: 2px 0;
            }
            GameRow:hover {
                background: #222235;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Top row ──────────────────────────────────────────────
        top_widget = QWidget()
        top_widget.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(top_widget)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        self.dot = PingDot()
        layout.addWidget(self.dot)

        icon_label = QLabel(game.get("icon", "🎮"))
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        icon_label.setFixedWidth(28)
        layout.addWidget(icon_label)

        name_layout = QVBoxLayout()
        name_layout.setSpacing(1)
        self.name_label = QLabel(game["name"])
        self.name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.name_label.setStyleSheet("color: #e0e0e0;")
        self.category_label = QLabel(game.get("category", "") + " • " + game.get("region_note", ""))
        self.category_label.setFont(QFont("Segoe UI", 8))
        self.category_label.setStyleSheet("color: #666680;")
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.category_label)
        layout.addLayout(name_layout)
        layout.addStretch()

        self.spark = PingBar()
        layout.addWidget(self.spark)

        self.ping_label = QLabel("—")
        self.ping_label.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        self.ping_label.setStyleSheet("color: #888888;")
        self.ping_label.setFixedWidth(65)
        self.ping_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.ping_label)

        self.report_btn = QPushButton("⚠")
        self.report_btn.setToolTip("Report this game isn't working correctly")
        self.report_btn.setFixedSize(28, 28)
        self.report_btn.setVisible(False)
        self.report_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #888888;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #33334a;
                color: #ff9800;
            }
        """)
        self.report_btn.clicked.connect(self._on_report_clicked)
        layout.addWidget(self.report_btn)

        outer.addWidget(top_widget)

        # ── Expanded chart panel ──────────────────────────────────
        self.chart_panel = QWidget()
        self.chart_panel.setStyleSheet("background: transparent;")
        chart_layout = QVBoxLayout(self.chart_panel)
        chart_layout.setContentsMargins(12, 0, 12, 8)
        chart_layout.setSpacing(2)

        self.chart_label = QLabel("▴ ping history")
        self.chart_label.setFont(QFont("Segoe UI", 7))
        self.chart_label.setStyleSheet("color: #444466;")
        chart_layout.addWidget(self.chart_label)

        self.chart = PingHistoryChart()
        chart_layout.addWidget(self.chart)

        self.chart_panel.hide()
        outer.addWidget(self.chart_panel)

    def _on_report_clicked(self):
        self.report_clicked.emit(self.game)

    def mousePressEvent(self, event):
        # Don't toggle if clicking the report button
        if self.report_btn.underMouse():
            return
        self._toggle_expand()
        super().mousePressEvent(event)

    def _toggle_expand(self):
        self._expanded = not self._expanded
        if self._expanded:
            self.chart.set_history(self._history, self._last_color)
            self.chart_panel.show()
            self.chart_label.setText("▾ ping history")
        else:
            self.chart_panel.hide()
            self.chart_label.setText("▴ ping history")

    def enterEvent(self, event):
        self.report_btn.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.report_btn.setVisible(False)
        super().leaveEvent(event)

    def update_ping(self, ms, history):
        status, color = get_ping_status(ms)
        self._last_ms = ms
        self._last_color = color
        self._history = history

        self.dot.set_color(color)
        self.spark.set_history(history)

        if ms is not None:
            self.ping_label.setText(f"{ms} ms")
            self.ping_label.setStyleSheet(f"color: {color};")
        else:
            self.ping_label.setText("—")
            self.ping_label.setStyleSheet("color: #555566;")

        # Refresh chart if expanded
        if self._expanded:
            self.chart.set_history(history, color)


class MainWindow(QMainWindow):
    check_now_requested = pyqtSignal()
    settings_requested = pyqtSignal()

    def __init__(self, game_manager, settings, ping_worker):
        super().__init__()
        self.game_manager = game_manager
        self.settings = settings
        self.ping_worker = ping_worker
        self.game_rows = {}

        self.setWindowTitle("PingGuard")
        self.setMinimumSize(520, 600)
        self.resize(560, 680)
        self.setStyleSheet(self._stylesheet())

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)

        # Header
        header = QHBoxLayout()
        title = QLabel("🎮 PingGuard")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0ff;")
        header.addWidget(title)
        header.addStretch()

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666680; font-size: 11px;")
        header.addWidget(self.status_label)

        self.check_btn = QPushButton("Check Now")
        self.check_btn.setFixedHeight(34)
        self.check_btn.setStyleSheet(self._button_style("#4c4cff", "#6666ff"))
        self.check_btn.clicked.connect(self._on_check_now)
        header.addWidget(self.check_btn)

        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(34, 34)
        settings_btn.setToolTip("Settings")
        settings_btn.setStyleSheet(self._button_style("#2a2a3e", "#3a3a5e"))
        settings_btn.clicked.connect(self.settings_requested.emit)
        header.addWidget(settings_btn)

        main_layout.addLayout(header)

        # Running games indicator
        self.running_bar = QLabel("")
        self.running_bar.setStyleSheet("""
            background: #1a1a2e;
            color: #00e676;
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 11px;
        """)
        self.running_bar.hide()
        main_layout.addWidget(self.running_bar)

        # Next check countdown
        self.countdown_label = QLabel("")
        self.countdown_label.setStyleSheet("color: #444466; font-size: 10px;")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.countdown_label)

        # Scroll area for game rows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        self.games_layout = QVBoxLayout(scroll_widget)
        self.games_layout.setSpacing(4)
        self.games_layout.setContentsMargins(0, 0, 4, 0)
        self.games_layout.addStretch()

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll, stretch=1)

        # Bottom bar
        bottom = QHBoxLayout()
        add_btn = QPushButton("+ Add Game")
        add_btn.setFixedHeight(32)
        add_btn.setStyleSheet(self._button_style("#1e3a1e", "#2a502a", text_color="#69f0ae"))
        add_btn.clicked.connect(self._on_add_game)
        bottom.addWidget(add_btn)
        bottom.addStretch()

        open_logs_btn = QPushButton("📁 Session Logs")
        open_logs_btn.setFixedHeight(32)
        open_logs_btn.setStyleSheet(self._button_style("#1a1a2e", "#262637"))
        open_logs_btn.clicked.connect(self._open_logs)
        bottom.addWidget(open_logs_btn)

        main_layout.addLayout(bottom)

        self._populate_games()

    def _populate_games(self):
        while self.games_layout.count() > 1:
            item = self.games_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        games = self.game_manager.games
        for game in games:
            if not game.get("enabled", True):
                continue
            row = GameRow(game)
            row.report_clicked.connect(self._on_report)

            if game.get("last_ping") is not None:
                row.update_ping(game["last_ping"], game.get("ping_history", []))

            self.game_rows[game["name"]] = row
            self.games_layout.insertWidget(self.games_layout.count() - 1, row)

    def update_game_ping(self, result):
        row = self.game_rows.get(result.game_name)
        if row:
            game = next((g for g in self.game_manager.games if g["name"] == result.game_name), None)
            history = game.get("ping_history", []) if game else []
            row.update_ping(result.ms, history)

    def set_checking(self, is_checking):
        if is_checking:
            self.check_btn.setText("Checking…")
            self.check_btn.setEnabled(False)
            self.status_label.setText("Checking…")
        else:
            self.check_btn.setText("Check Now")
            self.check_btn.setEnabled(True)
            self.status_label.setText(f"Last check: {datetime.datetime.now().strftime('%H:%M:%S')}")

    def set_countdown(self, seconds_remaining):
        if seconds_remaining > 0:
            m, s = divmod(seconds_remaining, 60)
            self.countdown_label.setText(f"Next check in {m}:{s:02d}")
        else:
            self.countdown_label.setText("")

    def show_running_games(self, games):
        if games:
            names = ", ".join(games)
            self.running_bar.setText(f"▶ Running: {names}")
            self.running_bar.show()
        else:
            self.running_bar.hide()

    def _on_check_now(self):
        self.set_checking(True)
        self.check_now_requested.emit()

    def _on_add_game(self):
        dialog = AddGameDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            game_data = dialog.get_game_data()
            if game_data:
                self.game_manager.add_game(game_data)
                self._populate_games()

    def _on_report(self, game):
        webhook = self.settings.get("discord_webhook", "")
        dialog = ReportDialog(game, webhook, self)
        dialog.exec()

    def _open_logs(self):
        from settings import LOGS_DIR
        import subprocess, sys
        try:
            if sys.platform == "win32":
                subprocess.Popen(["explorer", str(LOGS_DIR)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(LOGS_DIR)])
            else:
                subprocess.Popen(["xdg-open", str(LOGS_DIR)])
        except Exception as e:
            QMessageBox.information(self, "Logs", f"Logs are saved to:\n{LOGS_DIR}")

    def _stylesheet(self):
        return """
            QMainWindow, QWidget {
                background-color: #13131f;
                color: #e0e0e0;
            }
            QScrollBar:vertical {
                background: #1a1a2e;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #3a3a5e;
                border-radius: 3px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """

    def _button_style(self, bg, hover_bg, text_color="#e0e0e0"):
        return f"""
            QPushButton {{
                background: {bg};
                color: {text_color};
                border: none;
                border-radius: 6px;
                padding: 4px 14px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {hover_bg};
            }}
            QPushButton:pressed {{
                background: {bg};
            }}
            QPushButton:disabled {{
                color: #444466;
            }}
        """
