"""
MechForge AI - PySide6 Cyberpunk Interface
Converted from React implementation
"""

import sys
import math
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import (
    Qt, QTimer, QPoint, QRect, QSize, Signal, QThread, QPropertyAnimation,
    QEasingCurve, Property, QObject
)
from PySide6.QtGui import (
    QPainter, QPen, QColor, QBrush, QPainterPath, QFont, QFontMetrics,
    QLinearGradient, QPolygon, QPalette, QIcon, QPixmap, QCursor,
    QRadialGradient
)

# ─── Color Palette ────────────────────────────────────────────────────────────
C_BG_DEEP   = QColor("#0a0e14")
C_BG_PANEL  = QColor("#0d1117")
C_BG_SIDEBAR= QColor("#0a0e14")
C_BG_STATUS = QColor("#080c10")
C_BORDER    = QColor("#1a2535")
C_BORDER2   = QColor("#1e2d3d")
C_CYAN      = QColor("#00e5ff")
C_CYAN_DIM  = QColor("#00b8d4")
C_CYAN_DARK = QColor("#0097a7")
C_TEXT      = QColor("#c8d8e0")
C_TEXT_DIM  = QColor("#3a6070")
C_TEXT_MID  = QColor("#8ab4c8")
C_INPUT_BG  = QColor("#111820")

# ─── Boot sequence ────────────────────────────────────────────────────────────
BOOT_LINES = [
    {"text": "[{time}] SYSTEM: Initializing MechForge AI...", "style": "normal", "delay": 0},
    {"text": "> AI Assistant Ready",                           "style": "cyan",   "delay": 600},
    {"text": "Model: qwen2.5:3b",                             "style": "kv",     "delay": 1000},
    {"text": "RAG Status: Active",                            "style": "kv",     "delay": 1200},
    {"text": "API: Ollama",                                   "style": "kv",     "delay": 1400},
    {"text": "Memory: 42 KB",                                 "style": "kv",     "delay": 1600},
    {"text": "Awaiting input...",                             "style": "normal", "delay": 2000},
]


# ─── Hex Grid Background Widget ───────────────────────────────────────────────
class HexGridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAutoFillBackground(False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw hex grid
        pen = QPen(C_CYAN, 0.8)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.setOpacity(0.07)

        hex_w, hex_h = 56, 48
        cols = self.width() // hex_w + 2
        rows = self.height() // hex_h + 2

        for row in range(rows):
            for col in range(cols):
                x = col * hex_w
                y = row * hex_h
                # offset every other row
                if row % 2 == 1:
                    x += hex_w // 2
                pts = [
                    QPoint(int(x + 14), int(y + 2)),
                    QPoint(int(x + 42), int(y + 2)),
                    QPoint(int(x + 56), int(y + 24)),
                    QPoint(int(x + 42), int(y + 46)),
                    QPoint(int(x + 14), int(y + 46)),
                    QPoint(int(x +  0), int(y + 24)),
                ]
                painter.drawPolygon(QPolygon(pts))

        # Draw node network (top-right area)
        painter.setOpacity(0.15)
        w, h = self.width(), self.height()
        nodes_pct = [
            (0.75, 0.30), (0.85, 0.55), (0.90, 0.20),
            (0.70, 0.70), (0.95, 0.40), (0.80, 0.80),
        ]
        edges = [(0,1),(1,3),(0,4),(4,1),(2,4),(3,5),(1,5)]
        nodes_px = [(int(p[0]*w), int(p[1]*h)) for p in nodes_pct]

        line_pen = QPen(C_CYAN, 0.5)
        painter.setPen(line_pen)
        for a, b in edges:
            painter.drawLine(nodes_px[a][0], nodes_px[a][1],
                             nodes_px[b][0], nodes_px[b][1])

        painter.setBrush(QBrush(C_CYAN))
        painter.setPen(Qt.NoPen)
        for nx, ny in nodes_px:
            painter.drawEllipse(QPoint(nx, ny), 2, 2)

        painter.end()


# ─── Sidebar Icon Button ──────────────────────────────────────────────────────
class SidebarButton(QPushButton):
    def __init__(self, icon_name: str, label: str = "", parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self.label_text = label
        self.setFixedSize(52, 52 if not label else 58)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._active = False
        self._hovered = False

    def setActive(self, active: bool):
        self._active = active
        self.update()

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Background
        if self._active:
            grad = QLinearGradient(0, 0, w, h)
            grad.setColorAt(0, QColor("#00b8d4"))
            grad.setColorAt(1, QColor("#0097a7"))
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(0, 0, w, h, 8, 8)
            # Glow
            glow = QRadialGradient(w/2, h/2, w)
            glow.setColorAt(0, QColor(0, 229, 255, 60))
            glow.setColorAt(1, QColor(0, 229, 255, 0))
            painter.setBrush(QBrush(glow))
            painter.drawRoundedRect(-4, -4, w+8, h+8, 10, 10)
        else:
            painter.setBrush(Qt.NoBrush)
            painter.setPen(Qt.NoPen)

        # Icon color
        if self._active:
            icon_color = QColor("#ffffff")
        elif self._hovered:
            icon_color = C_CYAN
        else:
            icon_color = C_TEXT_DIM

        # Draw icon via QPainterPath
        painter.setPen(QPen(icon_color, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        icon_y_offset = -4 if self.label_text else 0
        self._draw_icon(painter, w//2, h//2 + icon_y_offset, icon_color)

        # Label
        if self.label_text:
            painter.setPen(QPen(icon_color))
            font = QFont("Arial", 7)
            painter.setFont(font)
            lines = self.label_text.split("\n")
            y_start = h - (len(lines) * 10) - 2
            for i, line in enumerate(lines):
                painter.drawText(QRect(0, y_start + i*10, w, 10),
                                 Qt.AlignHCenter | Qt.AlignVCenter, line)
        painter.end()

    def _draw_icon(self, painter, cx, cy, color):
        """Draw icon based on icon_name"""
        painter.setPen(QPen(color, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        s = 9  # half-size

        if self.icon_name == "assistant":
            # Smiley face
            painter.drawEllipse(QPoint(cx, cy), s, s)
            painter.drawArc(cx-4, cy, 8, 5, 0, -180*16)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPoint(cx-3, cy-2), 1, 1)
            painter.drawEllipse(QPoint(cx+3, cy-2), 1, 1)

        elif self.icon_name == "shield":
            path = QPainterPath()
            path.moveTo(cx, cy - s)
            path.lineTo(cx - s, cy - s//2)
            path.lineTo(cx - s, cy + 2)
            path.quadTo(cx - s, cy + s, cx, cy + s + 2)
            path.quadTo(cx + s, cy + s, cx + s, cy + 2)
            path.lineTo(cx + s, cy - s//2)
            path.closeSubpath()
            painter.drawPath(path)

        elif self.icon_name == "doc":
            painter.drawRoundedRect(cx-s+2, cy-s, s*2-2, s*2, 1, 1)
            painter.drawLine(cx-3, cy-3, cx+4, cy-3)
            painter.drawLine(cx-3, cy, cx+2, cy)
            painter.drawLine(cx-3, cy+3, cx, cy+3)

        elif self.icon_name == "scan":
            # Corner brackets + scan line
            d = 5
            painter.drawLine(cx-s, cy-s, cx-s+d, cy-s)
            painter.drawLine(cx-s, cy-s, cx-s, cy-s+d)
            painter.drawLine(cx+s, cy-s, cx+s-d, cy-s)
            painter.drawLine(cx+s, cy-s, cx+s, cy-s+d)
            painter.drawLine(cx-s, cy+s, cx-s+d, cy+s)
            painter.drawLine(cx-s, cy+s, cx-s, cy+s-d)
            painter.drawLine(cx+s, cy+s, cx+s-d, cy+s)
            painter.drawLine(cx+s, cy+s, cx+s, cy+s-d)
            painter.setPen(QPen(color, 1.0))
            painter.drawLine(cx-s, cy, cx+s, cy)

        elif self.icon_name == "plugin":
            painter.drawRoundedRect(cx-s, cy-s, s-1, s-1, 1, 1)
            painter.drawRoundedRect(cx+1, cy-s, s-1, s-1, 1, 1)
            painter.drawRoundedRect(cx-s, cy+1, s-1, s-1, 1, 1)
            painter.drawRoundedRect(cx+1, cy+1, s-1, s-1, 1, 1)

        elif self.icon_name == "db":
            painter.drawEllipse(cx-s, cy-s, s*2, 5)
            painter.drawLine(cx-s, cy-s+2, cx-s, cy)
            painter.drawLine(cx+s, cy-s+2, cx+s, cy)
            painter.drawEllipse(cx-s, cy-2, s*2, 5)
            painter.drawLine(cx-s, cy+1, cx-s, cy+s-1)
            painter.drawLine(cx+s, cy+1, cx+s, cy+s-1)
            painter.drawEllipse(cx-s, cy+s-3, s*2, 5)


# ─── Message Bubble ───────────────────────────────────────────────────────────
class MessageWidget(QWidget):
    def __init__(self, msg_type: str, text: str, time_str: str, parent=None):
        super().__init__(parent)
        self.msg_type = msg_type
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(0)

        label = QLabel()
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        mono = QFont("Courier New", 13)
        label.setFont(mono)

        if msg_type == "user":
            html = (f'<span style="color:#3a6070;">{time_str} </span>'
                    f'<span style="color:#00e5ff;">&gt; </span>'
                    f'<span style="color:#c8d8e0;">{text}</span>')
            label.setText(html)
            label.setTextFormat(Qt.RichText)
            layout.addWidget(label)
        else:
            # AI response with left border effect via a colored frame
            border = QFrame()
            border.setFixedWidth(2)
            border.setStyleSheet("background: #00e5ff33;")
            layout.addWidget(border)
            layout.addSpacing(8)

            lines = text.split("\n")
            html_lines = []
            for line in lines:
                if line.startswith(">"):
                    html_lines.append(f'<span style="color:#00e5ff;">{line}</span>')
                else:
                    html_lines.append(f'<span style="color:#8ab4c8;">{line}</span>')
            label.setText("<br>".join(html_lines))
            label.setTextFormat(Qt.RichText)
            layout.addWidget(label)

        label.setStyleSheet("background: transparent;")


# ─── Chat Output Area ─────────────────────────────────────────────────────────
class ChatOutput(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: transparent; width: 4px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #1a2535; border-radius: 2px; min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.v_layout = QVBoxLayout(self.container)
        self.v_layout.setContentsMargins(20, 16, 20, 8)
        self.v_layout.setSpacing(0)
        self.v_layout.addStretch()

        self.setWidget(self.container)

        # Cursor blink label
        self.cursor_label = QLabel("█")
        self.cursor_label.setFont(QFont("Courier New", 13))
        self.cursor_label.setStyleSheet("color: #00e5ff; background: transparent;")
        self.cursor_label.setFixedHeight(20)
        self.v_layout.addWidget(self.cursor_label)
        self.cursor_label.hide()

        self._cursor_visible = True
        self.cursor_timer = QTimer(self)
        self.cursor_timer.timeout.connect(self._blink_cursor)

        # Separator line (hidden initially)
        self.separator = QFrame()
        self.separator.setFixedHeight(1)
        self.separator.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #00e5ff33, stop:1 transparent);")
        self.separator.hide()

    def start_cursor(self):
        self.cursor_label.show()
        self.cursor_timer.start(530)

    def show_separator(self):
        # Insert separator before cursor
        idx = self.v_layout.indexOf(self.cursor_label)
        self.v_layout.insertWidget(idx, self.separator)
        self.separator.show()

    def _blink_cursor(self):
        self._cursor_visible = not self._cursor_visible
        self.cursor_label.setText("█" if self._cursor_visible else " ")

    def add_boot_line(self, text: str, style: str):
        label = QLabel()
        label.setFont(QFont("Courier New", 13))
        label.setStyleSheet("background: transparent;")
        label.setTextFormat(Qt.RichText)
        label.setWordWrap(True)

        if style == "normal":
            label.setText(f'<span style="color:#c8d8e0;">{text}</span>')
        elif style == "cyan":
            label.setText(f'<span style="color:#00e5ff;">{text}</span>')
        elif style == "kv":
            parts = text.split(": ", 1)
            if len(parts) == 2:
                label.setText(
                    f'<span style="color:#c8d8e0;">{parts[0]}: </span>'
                    f'<span style="color:#00e5ff;">{parts[1]}</span>'
                )
            else:
                label.setText(f'<span style="color:#c8d8e0;">{text}</span>')

        # Insert before cursor
        idx = self.v_layout.indexOf(self.cursor_label)
        self.v_layout.insertWidget(idx, label)
        self.scroll_to_bottom()

    def add_message(self, msg_type: str, text: str, time_str: str):
        widget = MessageWidget(msg_type, text, time_str)
        idx = self.v_layout.indexOf(self.cursor_label)
        self.v_layout.insertWidget(idx, widget)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        QTimer.singleShot(50, lambda: self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()
        ))


# ─── Main Window ──────────────────────────────────────────────────────────────
class MechForgeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MechForge AI")
        self.setFixedSize(900, 620)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_pos = None

        self._build_ui()
        self._start_boot_sequence()

    # ── UI Construction ────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        central.setObjectName("central")
        central.setStyleSheet("""
            #central {
                background: #0d1117;
                border: 1px solid #1e2d3d;
                border-radius: 8px;
            }
        """)
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_titlebar())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._build_sidebar())
        body.addWidget(self._build_main_panel(), 1)

        body_widget = QWidget()
        body_widget.setLayout(body)
        body_widget.setStyleSheet("background: transparent;")
        root.addWidget(body_widget, 1)

        root.addWidget(self._build_statusbar())

        # Shadow effect via stylesheet on main window
        self.setStyleSheet("""
            QMainWindow { background: transparent; }
        """)

    def _build_titlebar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(44)
        bar.setStyleSheet("background: #0d1117; border-bottom: 1px solid #1a2535; border-radius: 0;")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 12, 0)
        layout.setSpacing(8)

        # Logo box
        logo_box = QLabel()
        logo_box.setFixedSize(28, 28)
        logo_box.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #00b8d4, stop:1 #0097a7);
            border-radius: 6px;
        """)
        logo_box.setAlignment(Qt.AlignCenter)
        logo_box.setText("⚙")
        logo_box.setFont(QFont("Arial", 12))
        layout.addWidget(logo_box)

        title = QLabel("MechForge AI")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        title.setStyleSheet("color: #c8d8e0; letter-spacing: 1px; background: transparent;")
        layout.addWidget(title)

        version = QLabel("v0.5.0")
        version.setFont(QFont("Courier New", 11))
        version.setStyleSheet("color: #3a5068; background: transparent;")
        layout.addWidget(version)

        layout.addStretch()

        for sym, tip in [("−", "minimize"), ("□", "maximize"), ("×", "close")]:
            btn = QPushButton(sym)
            btn.setFixedSize(24, 24)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent; border: none;
                    color: #3a5068; font-size: 14px; font-family: Arial;
                }
                QPushButton:hover { color: #00e5ff; }
            """)
            if tip == "close":
                btn.clicked.connect(self.close)
            elif tip == "minimize":
                btn.clicked.connect(self.showMinimized)
            layout.addWidget(btn)

        return bar

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setFixedWidth(68)
        sidebar.setStyleSheet("background: #0a0e14; border-right: 1px solid #1a2535;")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(4)

        icons_def = [
            ("assistant", "AI\nAssistant"),
            ("shield",    ""),
            ("doc",       ""),
            ("scan",      ""),
            ("plugin",    ""),
            ("db",        ""),
        ]
        self.sidebar_buttons = {}
        for icon_id, label in icons_def:
            btn = SidebarButton(icon_id, label)
            btn.setActive(icon_id == "assistant")
            btn.clicked.connect(lambda checked, iid=icon_id: self._on_sidebar_click(iid))
            self.sidebar_buttons[icon_id] = btn
            layout.addWidget(btn, 0, Qt.AlignHCenter)

        layout.addStretch()
        return sidebar

    def _build_main_panel(self) -> QWidget:
        panel = QWidget()
        panel.setStyleSheet("background: #0d1117;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Background decorations (hex grid)
        self.bg_widget = HexGridWidget(panel)
        self.bg_widget.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Chat area
        self.chat_output = ChatOutput()
        layout.addWidget(self.chat_output, 1)

        # Input row
        layout.addWidget(self._build_input_row())

        return panel

    def _build_input_row(self) -> QWidget:
        row = QWidget()
        row.setFixedHeight(56)
        row.setStyleSheet("background: #0d1117; border-top: 1px solid #1a2535;")

        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(0)

        # Input container
        container = QWidget()
        container.setStyleSheet("""
            background: #111820;
            border: 1px solid #1e2d3d;
            border-radius: 20px;
        """)
        c_layout = QHBoxLayout(container)
        c_layout.setContentsMargins(14, 0, 6, 0)
        c_layout.setSpacing(8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your query here...")
        self.input_field.setFont(QFont("Courier New", 12))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: transparent; border: none; outline: none;
                color: #c8d8e0;
            }
            QLineEdit::placeholder { color: #3a6070; }
        """)
        self.input_field.returnPressed.connect(self._on_send)
        c_layout.addWidget(self.input_field, 1)

        send_btn = QPushButton("  ➤  Send")
        send_btn.setFixedSize(90, 32)
        send_btn.setFont(QFont("Arial", 12, QFont.Bold))
        send_btn.setCursor(QCursor(Qt.PointingHandCursor))
        send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #00b8d4, stop:1 #0097a7);
                color: white; border: none; border-radius: 16px;
                font-size: 12px; font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #00e5ff, stop:1 #00b8d4);
            }
            QPushButton:pressed { background: #0097a7; }
        """)
        send_btn.clicked.connect(self._on_send)
        c_layout.addWidget(send_btn)

        layout.addWidget(container, 1)
        return row

    def _build_statusbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(32)
        bar.setStyleSheet("background: #080c10; border-top: 1px solid #1a2535;")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(0)

        def lbl(text, color="#3a6070", bold=False):
            l = QLabel(text)
            l.setFont(QFont("Courier New", 10, QFont.Bold if bold else QFont.Normal))
            l.setStyleSheet(f"color: {color}; background: transparent;")
            return l

        layout.addWidget(lbl("? MechForge", "#00b8d4", bold=True))
        layout.addSpacing(8)

        for k, v, vc in [("API","Ollama","#3a6070"),("Model","qwen2.5:3b","#3a6070"),
                          ("RAG","ON","#00e5ff"),("Memory","42 KB","#3a6070")]:
            layout.addWidget(lbl(f"  |  {k}: ", "#3a6070"))
            layout.addWidget(lbl(v, vc))

        layout.addStretch()

        for sym in ["◇", "≡", "+", "○"]:
            l = lbl(sym)
            l.setFixedWidth(20)
            l.setAlignment(Qt.AlignCenter)
            layout.addWidget(l)

        return bar

    # ── Boot Sequence ──────────────────────────────────────────────────────────
    def _start_boot_sequence(self):
        now = datetime.now().strftime("%H:%M")
        for i, line_def in enumerate(BOOT_LINES):
            text = line_def["text"].replace("{time}", now)
            QTimer.singleShot(
                line_def["delay"],
                lambda t=text, s=line_def["style"], last=(i == len(BOOT_LINES)-1):
                    self._show_boot_line(t, s, last)
            )

    def _show_boot_line(self, text: str, style: str, is_last: bool):
        self.chat_output.add_boot_line(text, style)
        if is_last:
            QTimer.singleShot(200, self._on_boot_complete)

    def _on_boot_complete(self):
        self.chat_output.show_separator()
        self.chat_output.start_cursor()

    # ── Event Handlers ─────────────────────────────────────────────────────────
    def _on_sidebar_click(self, icon_id: str):
        for btn_id, btn in self.sidebar_buttons.items():
            btn.setActive(btn_id == icon_id)

    def _on_send(self):
        text = self.input_field.text().strip()
        if not text:
            return
        now = datetime.now().strftime("%H:%M")
        time_str = f"[{now}]"
        self.chat_output.add_message("user", text, time_str)
        self.input_field.clear()

        # Simulate AI response
        query = text
        QTimer.singleShot(800, lambda: self.chat_output.add_message(
            "ai",
            f'Processing query: "{query}"\n> Analysis complete. RAG retrieval active.\nResponse generated by qwen2.5:3b.',
            time_str
        ))

    # ── Window Drag (frameless) ────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    # ── Resize bg widget ──────────────────────────────────────────────────────
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'bg_widget'):
            # Match bg_widget to main panel size
            pass

    def paintEvent(self, event):
        """Draw window drop shadow"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Outer glow
        glow = QColor(0, 229, 255, 15)
        for i in range(8, 0, -1):
            painter.setPen(QPen(glow, i * 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(i, i, self.width()-i*2, self.height()-i*2, 9, 9)
        painter.end()


# ─── Entry Point ──────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette base
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#0d1117"))
    palette.setColor(QPalette.WindowText, QColor("#c8d8e0"))
    palette.setColor(QPalette.Base, QColor("#111820"))
    palette.setColor(QPalette.AlternateBase, QColor("#0a0e14"))
    palette.setColor(QPalette.Text, QColor("#c8d8e0"))
    palette.setColor(QPalette.Button, QColor("#0d1117"))
    palette.setColor(QPalette.ButtonText, QColor("#c8d8e0"))
    palette.setColor(QPalette.Highlight, QColor("#00b8d4"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    win = MechForgeWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()