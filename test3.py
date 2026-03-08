"""
MechForge AI  —  CAE Workbench  (PySide6)
══════════════════════════════════════════
Dark glassmorphism cyberpunk aesthetic.
Components:
  • AnimatedWhaleWidget  — floating mascot with glow / particles (reused)
  • ModelTreePanel       — assembly / mesh / BC / results tree
  • FEAViewport          — animated 3-D mesh + stress colormap (QPainter)
  • AnalysisPanel        — solver settings, colorbar, run button
  • SolverLogPanel       — live log + convergence chart
  • CAEWorkbenchWindow   — frameless main window

Run:  python mechforge_cae_workbench.py
Deps: pip install PySide6
"""

import sys, math, base64, random
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect, QSpacerItem, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QProgressBar,
)
from PySide6.QtCore  import Qt, QTimer, QPoint, QRectF, QSize, QPointF
from PySide6.QtGui   import (
    QPainter, QPen, QColor, QBrush, QPainterPath, QFont, QFontMetrics,
    QLinearGradient, QRadialGradient, QConicalGradient,
    QPixmap, QCursor, QPalette, QTransform, QPolygonF,
)

# ─────────────────────────────────────────────────────────────────────────────
# Embedded whale sprite (160 px)
# ─────────────────────────────────────────────────────────────────────────────
WHALE_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAKAAAACeCAYAAAC1vwHwAAABCGlDQ1BJQ0MgUHJvZmlsZQAAeJxjYGA8wQAELAYM"
    "DLl5JUVB7k4KEZFRCuwPGBiBEAwSk4sLGHADoKpv1yBqL+viUYcLcKakFicD6Q9ArFIEtBxopAiQLZIOYWuA2Ek"
    "Qtg2IXV5SUAJkB4DYRSFBzkB2CpCtkY7ETkJiJxcUgdT3ANk2uTmlyQh3M/Ck5oUGA2kOIJZhKGYIYnBncAL5"
    "H6IkfxEDg8VXBgbmCQixpJkMDNtbGRgkbiHEVBYwMPC3MDBsO48QQ4RJQWJRIliIBYiZ0tIYGD4tZ2DgjWRgEL"
    "7AwMAVDQsIHG5TALvNnSEfCNMZchhSgSKeDHkMyQx6QJYRgwGDIYMZAKbWPz9HbOBQAADLMUlEQVR4nOz9d7RlVbX"
    "2jf7GmGnlnXOotCsnKlBUIuecBEEEERGPOQfMOSsKBlRUVASRIFFyKAqoKipQOYedc1g5zDDG/WMV6jntfe/x+"
    "u49iB6f1nartlZbtfdcsz+zjzF6eLoANP/Gv/EPgvxHX8C/8b8b/ybgv/EPxb8J+G/8Q/FvAv4b/1D8m4D/xj8U"
    "/ybgv/EPxb8J+G/8Q2H+oy/gjQfBX0Oj4ui/GiHEX94Sf/tZYYJWR/+PQmuB1hqE/i+/6y+/6t/4G/wf7tD/Zk"
    "jKpFIIAeLoa60VWqu//9cIgUAgpAR0mZAaNOJvyPpvwL8JCMBfnJsQgEApAQT/6TPhiE0kamOHIBQyqaoOEwoZ"
    "+K6gkPcoFHzyOY9M2iWTKfzXvwAIpCzfbq2PkvLf+DcBhQAhJEppXrsVhgVNrSE6ZlQzY3YN0+dUMGVaNTV1Ncw"
    "SEQqQODQBRPJBRVIBFYiZ0tIYGD4tZ2DgjWRgEL7AwMAVDQsIHG5TALvNnSEfCNMZchhSgSKeDHkMyQx6QJYR"
    "gwGDIYMZAA=="
)

def _px_from_b64(b64: str, size: int | None = None) -> QPixmap:
    data = base64.b64decode(b64)
    px = QPixmap()
    ok = px.loadFromData(data)
    if not ok or px.isNull():
        # fallback: plain colored circle
        px = QPixmap(size or 80, size or 80)
        px.fill(QColor("#00e5ff"))
    if size:
        px = px.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return px

def _circle_crop(px: QPixmap) -> QPixmap:
    s = min(px.width(), px.height())
    result = QPixmap(s, s)
    result.fill(Qt.transparent)
    p = QPainter(result)
    p.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0, 0, s, s)
    p.setClipPath(path)
    p.drawPixmap(0, 0, px)
    p.end()
    return result

# ─────────────────────────────────────────────────────────────────────────────
# Shared color palette
# ─────────────────────────────────────────────────────────────────────────────
C = {
    "void":    QColor("#020509"),
    "deep":    QColor("#050c14"),
    "panel":   QColor("#0a121d"),
    "panel2":  QColor("#0d1825"),
    "border":  QColor("#0e2030"),
    "border2": QColor("#1a3050"),
    "cyan":    QColor("#00c8ff"),
    "cyan2":   QColor("#00e5ff"),
    "cyan3":   QColor("#0097a7"),
    "text":    QColor("#c8e8ff"),
    "dim":     QColor("#2a5070"),
    "mid":     QColor("#6aaac8"),
    "green":   QColor("#00ff9d"),
    "orange":  QColor("#ff6b00"),
    "red":     QColor("#ff2244"),
    "yellow":  QColor("#e8ff00"),
    "magenta": QColor("#ff00aa"),
}

def stress_color(t: float) -> QColor:
    """Map t∈[0,1] to stress colormap  blue→cyan→green→yellow→red."""
    t = max(0.0, min(1.0, t))
    if t < 0.25:
        r = 0;   g = int(t / 0.25 * 255); b = 255
    elif t < 0.5:
        r = 0;   g = 255; b = int((0.5 - t) / 0.25 * 255)
    elif t < 0.75:
        r = int((t - 0.5) / 0.25 * 255); g = 255; b = 0
    else:
        r = 255; g = int((1.0 - t) / 0.25 * 255); b = 0
    return QColor(r, g, b)


# ══════════════════════════════════════════════════════════════════════════════
# ①  ANIMATED WHALE MASCOT  (engineering edition)
# ══════════════════════════════════════════════════════════════════════════════
class AnimatedWhaleWidget(QWidget):
    """
    Floating whale with:
      bob float · glow pulse · hex-gear spin · scanlines · orbit particles
    In CAE mode: particles take on stress-map colours; gear shows FEA symbol.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.setAttribute(Qt.WA_TranslucentBackground)
        raw = _px_from_b64(WHALE_B64, 100)
        self._whale = _circle_crop(raw)
        self._t = 0.0
        self._gear_angle = 0.0
        self._particles = [
            {"angle": i * (360 / 10), "radius": 82,
             "speed": 0.7 + random.random() * 0.5,
             "size":  1.5 + random.random() * 2.0,
             "phase": random.random() * math.pi * 2}
            for i in range(10)
        ]
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)

    def _tick(self):
        self._t += 0.04
        self._gear_angle = (self._gear_angle + 1.4) % 360
        for p in self._particles:
            p["angle"] = (p["angle"] + p["speed"]) % 360
        self.update()

    # ── helpers ──────────────────────────────────────────────────────────────
    @staticmethod
    def _hex_path(cx, cy, r) -> QPainterPath:
        path = QPainterPath()
        for i in range(6):
            a = math.radians(i * 60 - 30)
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.closeSubpath()
        return path

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width() // 2, self.height() // 2
        t        = self._t
        bob_y    = math.sin(t * 0.8) * 5
        glow_a   = int(70 + math.sin(t) * 45)
        glow_r   = 78 + math.sin(t * 1.3) * 6

        # outer glow
        for extra, div in [(18,5),(10,3),(3,2)]:
            g = QRadialGradient(cx, cy + bob_y, glow_r + extra)
            g.setColorAt(0,   QColor(0, 200, 255, glow_a // div))
            g.setColorAt(0.7, QColor(0, 120, 200, glow_a // (div*2)))
            g.setColorAt(1,   QColor(0, 0, 0, 0))
            p.setBrush(QBrush(g)); p.setPen(Qt.NoPen)
            r = int(glow_r + extra)
            p.drawEllipse(cx - r, int(cy + bob_y) - r, r*2, r*2)

        # spinning hex gear (behind whale)
        p.save()
        p.translate(cx, cy + bob_y + 60)
        p.rotate(self._gear_angle)
        gear_path = self._hex_path(0, 0, 30)
        gp = QPen(QColor(0, 200, 255, 100), 1.5)
        gp.setStyle(Qt.DashLine)
        p.setPen(gp); p.setBrush(QColor(0, 40, 80, 60))
        p.drawPath(gear_path)
        # gear teeth (small rects)
        for i in range(6):
            a = math.radians(i * 60)
            tx, ty = 33 * math.cos(a), 33 * math.sin(a)
            p.save(); p.translate(tx, ty); p.rotate(math.degrees(a))
            p.fillRect(-2, -3, 4, 6, QColor(0, 200, 255, 120))
            p.restore()
        p.restore()

        # dashed ring border
        ring_r = 70
        rpen = QPen(QColor(0, 200, 255, 130), 1.5, Qt.DashLine)
        rpen.setDashOffset(self._gear_angle / 8)
        p.setPen(rpen); p.setBrush(Qt.NoBrush)
        p.drawEllipse(int(cx - ring_r), int(cy + bob_y - ring_r), ring_r*2, ring_r*2)

        # inner circle
        ir = 64
        bg = QRadialGradient(cx, cy + bob_y, ir)
        bg.setColorAt(0, QColor("#101c2c")); bg.setColorAt(1, QColor("#050c14"))
        p.setBrush(QBrush(bg)); p.setPen(Qt.NoPen)
        p.drawEllipse(int(cx - ir), int(cy + bob_y - ir), ir*2, ir*2)

        # whale pixmap
        pw, ph = self._whale.width(), self._whale.height()
        p.drawPixmap(int(cx - pw//2), int(cy + bob_y - ph//2), self._whale)

        # scanlines
        scan_pen = QPen(QColor(0, 0, 0, 30), 1)
        p.setPen(scan_pen)
        clip = QPainterPath(); clip.addEllipse(cx-ir, cy+bob_y-ir, ir*2, ir*2)
        p.setClipPath(clip)
        for y in range(int(cy+bob_y-ir), int(cy+bob_y+ir), 3):
            p.drawLine(int(cx-ir), y, int(cx+ir), y)
        p.setClipping(False)

        # orbiting stress-coloured particles
        for pp in self._particles:
            rad = math.radians(pp["angle"])
            px_x = cx + math.cos(rad) * pp["radius"]
            px_y = cy + bob_y + math.sin(rad) * pp["radius"] * 0.32
            norm  = (math.sin(t + pp["phase"]) + 1) / 2
            col   = stress_color(norm)
            col.setAlpha(int(120 + math.sin(t + pp["phase"]) * 80))
            p.setBrush(QBrush(col)); p.setPen(Qt.NoPen)
            s = pp["size"]
            p.drawEllipse(QRectF(px_x-s, px_y-s, s*2, s*2))

        # bottom label
        p.setClipping(False)
        font = QFont("Courier New", 8)
        p.setFont(font); p.setPen(C["cyan"])
        lbl = "⚙ MECH AI ONLINE ⚙"
        fm = QFontMetrics(font)
        tw = fm.horizontalAdvance(lbl)
        p.drawText(int(cx - tw//2), int(cy + bob_y + 95), lbl)
        p.end()


# ══════════════════════════════════════════════════════════════════════════════
# ②  FEA VIEWPORT  (animated mesh + stress field)
# ══════════════════════════════════════════════════════════════════════════════
class FEAViewport(QWidget):
    """
    Centre-piece: draws a simplified FEA bracket in isometric projection.
    Animations:
      • Model slowly oscillates (±8°) around Y axis (perspective warp)
      • Stress colormap pulses (simulates solver convergence)
      • Scanner line sweeps across the viewport
      • Grid flickers subtly
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #020509;")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._t = 0.0
        self._scan_y = 0.0
        self._stress_t = 0.6     # converged stress level
        self._solving  = False
        self._solve_progress = 0.0
        self._log_lines: list[str] = []
        self._view_mode = "STRESS"  # STRESS | WIRE | SOLID
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)

    def set_view_mode(self, mode: str):
        self._view_mode = mode
        self.update()

    def start_solve(self):
        """Animate a solve sequence."""
        self._solving = True
        self._solve_progress = 0.0
        self._stress_t = 0.0
        self._stimer = QTimer(self)
        self._stimer.timeout.connect(self._advance_solve)
        self._stimer.start(30)

    def _advance_solve(self):
        self._solve_progress = min(1.0, self._solve_progress + 0.012)
        self._stress_t = self._solve_progress * 0.75
        if self._solve_progress >= 1.0:
            self._stimer.stop()
            self._solving = False
            self._stress_t = 0.75
        self.update()

    def _tick(self):
        self._t += 0.025
        self._scan_y = (self._scan_y + 2.0) % (self.height() + 80)
        self.update()

    # ── painting ─────────────────────────────────────────────────────────────
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2 - 20

        # 1. Background grid
        self._draw_grid(p, w, h)

        # 2. FEA model
        tilt = math.sin(self._t * 0.35) * 8  # ±8° tilt
        self._draw_model(p, cx, cy, tilt)

        # 3. Scanner line
        scan_pen = QPen(QColor(0, 200, 255, 40), 2)
        p.setPen(scan_pen)
        sy = int(self._scan_y) - 40
        p.drawLine(0, sy, w, sy)
        gline = QLinearGradient(0, sy-20, 0, sy+20)
        gline.setColorAt(0, QColor(0, 200, 255, 0))
        gline.setColorAt(0.5, QColor(0, 200, 255, 15))
        gline.setColorAt(1, QColor(0, 200, 255, 0))
        p.setBrush(QBrush(gline)); p.setPen(Qt.NoPen)
        p.drawRect(0, sy-20, w, 40)

        # 4. Corner decorators
        self._draw_corners(p, w, h)

        # 5. Overlay text
        self._draw_overlays(p, w, h)

        # 6. Solve progress bar
        if self._solving:
            p.setBrush(QColor(0, 200, 255, 40)); p.setPen(Qt.NoPen)
            bar_w = int(w * self._solve_progress)
            p.drawRect(0, h-3, bar_w, 3)

        p.end()

    def _draw_grid(self, p, w, h):
        """Perspective-fading grid."""
        grid_c = QColor(0, 100, 180, 22)
        gpen = QPen(grid_c, 0.7)
        p.setPen(gpen)
        step = 40
        for x in range(0, w + step, step):
            p.drawLine(x, 0, x, h)
        for y in range(0, h + step, step):
            p.drawLine(0, y, w, y)
        # Diagonal accent lines
        diag = QPen(QColor(0, 200, 255, 8), 0.5)
        p.setPen(diag)
        for x in range(-h, w + h, 120):
            p.drawLine(x, 0, x + h, h)

    def _iso(self, x3, y3, z3, cx, cy, tilt=0.0):
        """Simple isometric + tilt projection."""
        angle = math.radians(tilt)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        rx = x3 * cos_a + z3 * sin_a
        rz = -x3 * sin_a + z3 * cos_a
        sx = (rx - rz) * math.cos(math.radians(30))
        sy = (rx + rz) * math.sin(math.radians(30)) - y3
        return cx + sx, cy + sy

    def _draw_model(self, p, cx, cy, tilt):
        """Draw the FEA bracket model with mesh and stress field."""
        vm = self._view_mode
        st = self._stress_t

        def iso(*args): return self._iso(*args, cx, cy, tilt)

        # ── model geometry (L-shaped bracket, 4 faces) ──
        # Base plate:  x∈[-120,120], z∈[-40,40], y=0 → y=-50
        # Vertical arm: x∈[-20,20],  z∈[-40,40], y=0 → y=-140

        faces = [
            # (vertices list, stress_u, face_label)
            # bottom of base plate
            ([(-120,0,-40),(-120,0, 40),( 120,0, 40),( 120,0,-40)],       0.05, "base-bot"),
            # front face of base plate
            ([(-120,0,-40),(-120,-50,-40),( 120,-50,-40),( 120,0,-40)],    0.12, "base-front"),
            # top of base plate (truncated by arm)
            ([(  20,0,-40),(  20,0, 40),(120,0, 40),(120,0,-40)],          0.18, "base-top-r"),
            ([(-120,0,-40),(-120,0, 40),(-20,0, 40),(-20,0,-40)],          0.15, "base-top-l"),
            # arm front face
            ([(-20,0,-40),(-20,-140,-40),(20,-140,-40),(20,0,-40)],         0.95, "arm-front"),
            # arm side face (right)
            ([(20,0,-40),(20,-140,-40),(20,-140,40),(20,0,40)],             0.60, "arm-right"),
            # arm top face
            ([(-20,-140,-40),(-20,-140,40),(20,-140,40),(20,-140,-40)],     1.00, "arm-top"),
            # base side face (right)
            ([(120,0,-40),(120,-50,-40),(120,-50,40),(120,0,40)],           0.08, "base-right"),
        ]

        # Draw filled stress faces (except in WIRE mode)
        if vm != "WIRE":
            for verts, stress_base, label in faces:
                # stress level animated toward converged value
                actual_stress = stress_base * st
                col = stress_color(actual_stress)
                if vm == "SOLID":
                    col = QColor(20, 50, 90)
                col.setAlpha(200)
                path = QPainterPath()
                for i, v in enumerate(verts):
                    sx, sy = iso(*v)
                    if i == 0:
                        path.moveTo(sx, sy)
                    else:
                        path.lineTo(sx, sy)
                path.closeSubpath()
                p.setBrush(QBrush(col))
                edge_col = QColor(0, 200, 255, 60) if vm != "SOLID" else QColor(0, 100, 160, 80)
                p.setPen(QPen(edge_col, 0.8))
                p.drawPath(path)

        # Draw mesh wireframe overlay
        wire_alpha = 180 if vm == "WIRE" else 80
        wpen = QPen(QColor(0, 200, 255, wire_alpha), 0.6)
        p.setPen(wpen); p.setBrush(Qt.NoBrush)

        # Horizontal lines on arm face
        for yi in range(0, -140, -20):
            x1s, y1s = iso(-20, yi, -40)
            x2s, y2s = iso( 20, yi, -40)
            p.drawLine(int(x1s), int(y1s), int(x2s), int(y2s))
        # Vertical lines on arm face
        for xi in (-20, -10, 0, 10, 20):
            x1s, y1s = iso(xi, 0, -40)
            x2s, y2s = iso(xi, -140, -40)
            p.drawLine(int(x1s), int(y1s), int(x2s), int(y2s))
        # Lines on base plate top
        for xi in range(-120, 121, 20):
            if abs(xi) > 20:
                x1s, y1s = iso(xi, 0, -40)
                x2s, y2s = iso(xi, 0,  40)
                p.drawLine(int(x1s), int(y1s), int(x2s), int(y2s))
        for zi in (-40, -20, 0, 20, 40):
            x1s, y1s = iso(-120, 0, zi)
            x2s, y2s = iso( 120, 0, zi)
            p.drawLine(int(x1s), int(y1s), int(x2s), int(y2s))

        # ── node dots ──
        key_nodes = [
            (-120, 0, -40), (-120, 0, 40), (120, 0, -40), (120, 0, 40),
            (-20, -140, -40), (20, -140, -40), (-20, -140, 40), (20, -140, 40),
            (0, -140, 0),  # max stress point
        ]
        for i, n in enumerate(key_nodes):
            sx, sy = iso(*n)
            is_hot = (n[1] == -140)
            col = QColor(255, 80, 0, 230) if is_hot else QColor(0, 229, 255, 200)
            r = 4 if is_hot else 2
            p.setBrush(QBrush(col)); p.setPen(Qt.NoPen)
            p.drawEllipse(QRectF(sx-r, sy-r, r*2, r*2))

        # ── fixed support (bottom of base plate) ──
        p.setPen(QPen(C["green"], 1.5))
        p.setBrush(Qt.NoBrush)
        for xi in range(-120, 121, 30):
            bx, by = iso(xi, -50, 0)
            p.drawLine(int(bx), int(by), int(bx), int(by+12))
            # hatch
            p.drawLine(int(bx-8), int(by+12), int(bx+8), int(by+12))

        # ── force arrow (top of arm) ──
        ax, ay = iso(0, -140, 0)
        arrow_col = C["orange"]
        p.setPen(QPen(arrow_col, 2.5)); p.setBrush(QBrush(arrow_col))
        # shaft
        p.drawLine(int(ax), int(ay - 40), int(ax), int(ay - 18))
        # arrowhead
        tri = QPolygonF([
            QPointF(ax, ay - 8),
            QPointF(ax - 7, ay - 22),
            QPointF(ax + 7, ay - 22),
        ])
        p.drawPolygon(tri)
        # label
        p.setPen(QPen(arrow_col, 1))
        p.setFont(QFont("Courier New", 9))
        p.drawText(int(ax + 10), int(ay - 28), "F = 5 kN")

        # ── max stress annotation (arm top) ──
        if st > 0.5:
            hot_x, hot_y = iso(0, -140, 0)
            p.setPen(QPen(QColor(255, 80, 0, 180), 1, Qt.DashLine))
            p.drawLine(int(hot_x + 8), int(hot_y), int(hot_x + 80), int(hot_y - 20))
            p.setPen(QPen(QColor(255, 80, 0, 200), 1))
            p.setFont(QFont("Courier New", 9))
            stress_val = 312.4 * st
            p.drawText(int(hot_x + 82), int(hot_y - 16), f"σ = {stress_val:.1f} MPa")

        # ── axis triad ──
        self._draw_triad(p, 60, self.height() - 60, tilt)

    def _draw_triad(self, p, ox, oy, tilt):
        """XYZ axis triad in corner."""
        axes = [("X", 1,0,0, QColor(255,60,60)), ("Y", 0,1,0, QColor(60,255,80)), ("Z", 0,0,1, QColor(60,120,255))]
        for name, dx, dy, dz, col in axes:
            a = math.radians(tilt)
            rx = dx * math.cos(a) + dz * math.sin(a)
            rz = -dx * math.sin(a) + dz * math.cos(a)
            sx = (rx - rz) * math.cos(math.radians(30)) * 30
            sy = (rx + rz) * math.sin(math.radians(30)) * 30 - dy * 30
            p.setPen(QPen(col, 2))
            p.drawLine(ox, oy, int(ox + sx), int(oy + sy))
            p.setFont(QFont("Courier New", 8, QFont.Bold))
            p.setPen(col)
            p.drawText(int(ox + sx + 4), int(oy + sy + 4), name)

    def _draw_corners(self, p, w, h):
        """Cyberpunk corner bracket decorations."""
        size, thick = 14, 2
        col = QColor(0, 200, 255, 160)
        pen = QPen(col, thick)
        p.setPen(pen)
        for cx2, cy2, sx, sy in [(0,0,1,1),(w,0,-1,1),(0,h,1,-1),(w,h,-1,-1)]:
            p.drawLine(cx2, cy2, cx2 + sx*size, cy2)
            p.drawLine(cx2, cy2, cx2, cy2 + sy*size)

    def _draw_overlays(self, p, w, h):
        p.setFont(QFont("Courier New", 9))
        p.setPen(QPen(QColor(0, 200, 255, 120)))
        info_lines = [
            f"NODES: 12,480  ELEMENTS: 9,864  DOF: 37,440",
            f"SOLVER: CalculiX 2.21  METHOD: IMPLICIT STATIC",
            f"ITER: 12  CONV: 1.2e-6  TIME: 2.4s",
        ]
        for i, line in enumerate(info_lines):
            p.drawText(14, h - 14 - (len(info_lines)-1-i)*14, line)

        # top-right cursor coords
        p.setPen(QPen(QColor(0, 200, 255, 80)))
        p.setFont(QFont("Courier New", 9))
        coords = ["X: 124.5 mm", "Y:  83.2 mm", "Z:   0.0 mm"]
        for i, c in enumerate(coords):
            p.drawText(w - 110, 20 + i * 14, c)

        # view mode label
        p.setPen(QPen(C["cyan2"]))
        p.setFont(QFont("Courier New", 11, QFont.Bold))
        p.drawText(14, 22, f"  {self._view_mode} VIEW  ")


# ══════════════════════════════════════════════════════════════════════════════
# ③  MODEL TREE PANEL
# ══════════════════════════════════════════════════════════════════════════════
def _tree_item(label: str, icon: str = "·", color: str = "#6aaac8", bold=False) -> QTreeWidgetItem:
    item = QTreeWidgetItem([f"  {icon}  {label}"])
    font = QFont("Courier New", 11)
    if bold:
        font.setBold(True)
    item.setFont(0, font)
    item.setForeground(0, QColor(color))
    return item

class ModelTreePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(236)
        self.setStyleSheet(f"background: {C['panel'].name()};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        hdr = self._make_header("MODEL TREE")
        layout.addWidget(hdr)

        # Whale mascot
        self._whale_widget = AnimatedWhaleWidget()
        whale_wrapper = QWidget()
        whale_wrapper.setFixedHeight(204)
        whale_wrapper.setStyleSheet("background: transparent;")
        wl = QVBoxLayout(whale_wrapper)
        wl.setContentsMargins(0, 2, 0, 0)
        wl.addWidget(self._whale_widget, 0, Qt.AlignHCenter)
        layout.addWidget(whale_wrapper)

        # Thin divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {C['border2'].name()};")
        layout.addWidget(div)

        # Tree widget
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setStyleSheet("""
            QTreeWidget {
                background: transparent; border: none;
                color: #6aaac8; font-family: 'Courier New'; font-size: 11px;
            }
            QTreeWidget::item:selected {
                background: #0a2040; color: #00e5ff;
                border-left: 2px solid #00c8ff;
            }
            QTreeWidget::item:hover {
                background: #071828;
            }
            QTreeWidget::branch { background: transparent; }
        """)
        self._tree.setIndentation(14)
        self._populate_tree()
        layout.addWidget(self._tree, 1)

        # Bottom info strip
        info = QLabel("  42CrMo4  ·  FEA Static  ·  v0.4.0")
        info.setFont(QFont("Courier New", 9))
        info.setStyleSheet("color: #1a4060; padding: 4px 0;")
        layout.addWidget(info)

    def _make_header(self, title: str) -> QWidget:
        w = QWidget()
        w.setFixedHeight(32)
        w.setStyleSheet(f"background: {C['panel2'].name()}; border-bottom: 1px solid {C['border2'].name()};")
        l = QHBoxLayout(w)
        l.setContentsMargins(10, 0, 8, 0)
        bar = QLabel("▌")
        bar.setStyleSheet("color: #00c8ff; font-size: 14px;")
        l.addWidget(bar)
        lbl = QLabel(title)
        lbl.setFont(QFont("Courier New", 9, QFont.Bold))
        lbl.setStyleSheet("color: #00c8ff; letter-spacing: 2px;")
        l.addWidget(lbl)
        l.addStretch()
        return w

    def _populate_tree(self):
        t = self._tree

        def section(label):
            it = QTreeWidgetItem([f"  ── {label} ──"])
            it.setFont(0, QFont("Courier New", 8))
            it.setForeground(0, QColor("#1a4060"))
            it.setFlags(it.flags() & ~Qt.ItemIsSelectable)
            return it

        t.addTopLevelItem(section("ASSEMBLY"))
        asm = _tree_item("Bracket_v3.step", "◈", "#00e5ff", bold=True)
        t.addTopLevelItem(asm)
        asm.addChild(_tree_item("Body_001", "▷"))
        asm.addChild(_tree_item("Body_002", "▷"))
        asm.setExpanded(True)

        t.addTopLevelItem(section("MESH"))
        mesh = _tree_item("Hex_Mesh 4mm", "⊞", "#00c8ff")
        mesh.addChild(_tree_item("Surface mesh", "·"))
        mesh.addChild(_tree_item("Volume mesh",  "·"))
        t.addTopLevelItem(mesh)
        mesh.setExpanded(True)

        t.addTopLevelItem(section("BOUNDARY CONDITIONS"))
        t.addTopLevelItem(_tree_item("Fixed Support",   "⊡", "#00ff9d"))
        t.addTopLevelItem(_tree_item("Force  5 kN",     "↑", "#ff6b00"))
        t.addTopLevelItem(_tree_item("Pressure  2 MPa", "≡", "#ff6b00"))

        t.addTopLevelItem(section("MATERIALS"))
        t.addTopLevelItem(_tree_item("42CrMo4  Steel",  "◇", "#e8ff00"))
        t.addTopLevelItem(_tree_item("Al 7075-T6",      "◇", "#c8d0d8"))

        t.addTopLevelItem(section("RESULTS"))
        t.addTopLevelItem(_tree_item("von Mises Stress", "◉", "#ff6b00"))
        t.addTopLevelItem(_tree_item("Displacement",     "◉", "#00e5ff"))
        t.addTopLevelItem(_tree_item("Safety Factor",    "◉", "#00ff9d"))


# ══════════════════════════════════════════════════════════════════════════════
# ④  ANALYSIS SETTINGS PANEL
# ══════════════════════════════════════════════════════════════════════════════
class StressColorbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(14)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        g = QLinearGradient(0, 0, self.width(), 0)
        stops = [(0,"#0000ff"),(0.25,"#00ffff"),(0.5,"#00ff00"),(0.75,"#ffff00"),(1,"#ff3300")]
        for pos, col in stops:
            g.setColorAt(pos, QColor(col))
        p.fillRect(0, 0, self.width(), self.height(), QBrush(g))
        p.end()

class AnalysisPanel(QWidget):
    solve_requested = None  # will be set by main window

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(256)
        self.setStyleSheet(f"background: {C['panel'].name()};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        layout.addWidget(self._make_header("ANALYSIS"))

        # Scrollable settings area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none;} QScrollBar:vertical{width:3px;background:transparent;} QScrollBar::handle:vertical{background:#0e2030;border-radius:2px;} QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}")
        inner = QWidget(); inner.setStyleSheet("background:transparent;")
        il = QVBoxLayout(inner); il.setContentsMargins(12, 8, 12, 8); il.setSpacing(10)
        scroll.setWidget(inner)
        layout.addWidget(scroll, 1)

        def field(label, value, highlight=False, warn=False):
            w = QWidget(); w.setStyleSheet("background:transparent;")
            wl = QVBoxLayout(w); wl.setContentsMargins(0,0,0,0); wl.setSpacing(2)
            lbl = QLabel(label); lbl.setFont(QFont("Courier New", 8))
            lbl.setStyleSheet("color: #1e4060; letter-spacing:1px; background:transparent;")
            wl.addWidget(lbl)
            val = QLabel(value); val.setFont(QFont("Courier New", 11))
            color = "#ff8800" if warn else ("#00ff9d" if highlight else "#c8e8ff")
            val.setStyleSheet(f"color:{color}; background:#060f1a; border:1px solid #0e2030; padding:3px 6px;")
            wl.addWidget(val)
            return w

        def row(*widgets):
            w = QWidget(); w.setStyleSheet("background:transparent;")
            wl = QHBoxLayout(w); wl.setContentsMargins(0,0,0,0); wl.setSpacing(6)
            for ww in widgets:
                wl.addWidget(ww)
            return w

        def sep():
            s = QFrame(); s.setFixedHeight(1)
            s.setStyleSheet("background: #0a2030;")
            return s

        def section_label(t):
            l = QLabel(t); l.setFont(QFont("Courier New", 8, QFont.Bold))
            l.setStyleSheet("color: #1a4060; letter-spacing:2px; background:transparent; margin-top:6px;")
            return l

        il.addWidget(field("SOLVER", "CalculiX 2.21"))
        il.addWidget(field("ANALYSIS TYPE", "Linear Static", highlight=True))
        il.addWidget(row(field("MESH SIZE","4.0 mm"), field("ELEMENT ORDER","2nd")))
        il.addWidget(sep())

        il.addWidget(section_label("RESULT DISPLAY"))
        il.addWidget(field("RESULT TYPE", "von Mises Stress", highlight=True))

        il.addWidget(QLabel("STRESS RANGE").also(lambda l: (l.setFont(QFont("Courier New",8)), l.setStyleSheet("color:#1e4060;letter-spacing:1px;"))) if False else self._colorbar_section())

        il.addWidget(sep())
        il.addWidget(field("MAX von Mises", "312.4 MPa", warn=True))

        # Stress utilisation bar
        util_lbl = QLabel("UTILISATION  78%")
        util_lbl.setFont(QFont("Courier New", 8)); util_lbl.setStyleSheet("color:#1e4060; background:transparent;")
        il.addWidget(util_lbl)
        bar = QProgressBar(); bar.setValue(78); bar.setFixedHeight(6); bar.setTextVisible(False)
        bar.setStyleSheet("QProgressBar{background:#060f1a;border:1px solid #0e2030;border-radius:3px;} QProgressBar::chunk{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0000ff,stop:0.4 #00ff00,stop:0.8 #ffff00,stop:1 #ff4400);}")
        il.addWidget(bar)

        il.addWidget(row(field("YIELD STR.","450 MPa"), field("SAFETY F.","1.44", highlight=True)))
        il.addWidget(field("MAX DISPLACEMENT", "0.42 mm"))

        il.addWidget(sep())
        il.addWidget(section_label("CONVERGENCE"))
        self._conv_widget = ConvergenceChart()
        self._conv_widget.setFixedHeight(70)
        il.addWidget(self._conv_widget)

        il.addStretch()

        # Bottom button strip
        btn_area = QWidget(); btn_area.setStyleSheet(f"background:{C['panel2'].name()}; border-top:1px solid {C['border2'].name()};")
        bl = QVBoxLayout(btn_area); bl.setContentsMargins(10,8,10,8); bl.setSpacing(6)

        self._run_btn = QPushButton("▶  RUN SOLVE")
        self._run_btn.setFixedHeight(36)
        self._run_btn.setFont(QFont("Courier New", 11, QFont.Bold))
        self._run_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._run_btn.setStyleSheet("""
            QPushButton{
                background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #003066,stop:1 #001840);
                border:1px solid #004080; color:#00c8ff; border-radius:4px;
                letter-spacing:2px;
            }
            QPushButton:hover{ background:#004080; border-color:#00c8ff; color:#00e5ff;
                box-shadow: 0 0 12px rgba(0,200,255,0.4); }
            QPushButton:pressed{ background:#001830; }
        """)
        bl.addWidget(self._run_btn)

        sub_row = QHBoxLayout(); sub_row.setSpacing(4)
        for lbl_text in ["MESH", "POST", "EXPORT"]:
            btn = QPushButton(lbl_text)
            btn.setFixedHeight(26)
            btn.setFont(QFont("Courier New", 9, QFont.Bold))
            btn.setStyleSheet("QPushButton{background:#060f1a;border:1px solid #0e2030;color:#2a6080;border-radius:3px;} QPushButton:hover{border-color:#00c8ff;color:#00c8ff;}")
            sub_row.addWidget(btn)
        bl.addLayout(sub_row)
        layout.addWidget(btn_area)

    def _make_header(self, title):
        w = QWidget(); w.setFixedHeight(32)
        w.setStyleSheet(f"background:{C['panel2'].name()};border-bottom:1px solid {C['border2'].name()};")
        l = QHBoxLayout(w); l.setContentsMargins(10,0,8,0)
        bar = QLabel("▌"); bar.setStyleSheet("color:#00c8ff;font-size:14px;")
        l.addWidget(bar)
        lbl = QLabel(title); lbl.setFont(QFont("Courier New",9,QFont.Bold))
        lbl.setStyleSheet("color:#00c8ff;letter-spacing:2px;")
        l.addWidget(lbl); l.addStretch()
        chip = QLabel("STATIC")
        chip.setFont(QFont("Courier New", 8)); chip.setStyleSheet("color:#00ff9d;background:#002820;border:1px solid #00ff9d;padding:1px 5px;")
        l.addWidget(chip)
        return w

    def _colorbar_section(self):
        w = QWidget(); w.setStyleSheet("background:transparent;")
        wl = QVBoxLayout(w); wl.setContentsMargins(0,0,0,0); wl.setSpacing(2)
        lbl = QLabel("STRESS RANGE"); lbl.setFont(QFont("Courier New",8))
        lbl.setStyleSheet("color:#1e4060;letter-spacing:1px; background:transparent;")
        wl.addWidget(lbl)
        wl.addWidget(StressColorbar())
        ticks = QLabel("0           78.1         156.2        312 MPa")
        ticks.setFont(QFont("Courier New", 7)); ticks.setStyleSheet("color:#1a3040; background:transparent;")
        wl.addWidget(ticks)
        return w

    def connect_run(self, callback):
        self._run_btn.clicked.connect(callback)


# ══════════════════════════════════════════════════════════════════════════════
# ⑤  CONVERGENCE CHART
# ══════════════════════════════════════════════════════════════════════════════
class ConvergenceChart(QWidget):
    """Animated convergence history graph."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        self._points: list[float] = [1.0, 0.45, 0.18, 0.07, 0.025, 0.009, 0.003, 0.001, 0.0004, 0.00015, 0.00006, 0.00002]
        self._draw_count = len(self._points)
        self._t = 0.0
        self._timer = QTimer(self); self._timer.timeout.connect(self._tick); self._timer.start(50)

    def _tick(self):
        self._t += 0.03; self.update()

    def start_solve(self):
        self._draw_count = 0
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._add_point)
        self._anim_timer.start(120)

    def _add_point(self):
        self._draw_count = min(len(self._points), self._draw_count + 1)
        if self._draw_count >= len(self._points):
            self._anim_timer.stop()
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        pad = 4

        # background
        p.fillRect(0,0,w,h, QColor("#020810"))

        # grid
        gpen = QPen(QColor(0,100,180,30), 0.5)
        p.setPen(gpen)
        for i in range(4):
            y = int(pad + (h-2*pad)*i/3)
            p.drawLine(pad, y, w-pad, y)

        # y-axis labels (log scale)
        p.setFont(QFont("Courier New", 7))
        p.setPen(QColor(0,100,180,80))
        for i, lbl in enumerate(["1e0","1e-2","1e-4","1e-6"]):
            y = int(pad + (h-2*pad)*i/3)
            p.drawText(0, y+4, lbl)

        # convergence curve
        n = self._draw_count
        if n >= 2:
            xs = [(w - 2*pad) / max(len(self._points)-1, 1) * i + pad for i in range(n)]
            # log-scale y mapping
            def ly(val):
                log_min, log_max = math.log10(1e-6), math.log10(1.0)
                lv = math.log10(max(val, 1e-7))
                return pad + (h - 2*pad) * (1 - (lv - log_min)/(log_max - log_min))

            # glow fill
            path = QPainterPath()
            path.moveTo(xs[0], h)
            for i in range(n):
                path.lineTo(xs[i], ly(self._points[i]))
            path.lineTo(xs[-1], h)
            path.closeSubpath()
            gfill = QLinearGradient(0, 0, 0, h)
            gfill.setColorAt(0, QColor(0,200,255,60))
            gfill.setColorAt(1, QColor(0,200,255,0))
            p.setBrush(QBrush(gfill)); p.setPen(Qt.NoPen)
            p.drawPath(path)

            # line
            path2 = QPainterPath()
            path2.moveTo(xs[0], ly(self._points[0]))
            for i in range(1,n):
                path2.lineTo(xs[i], ly(self._points[i]))
            lpen = QPen(QColor(0,229,255), 1.5)
            lpen.setCapStyle(Qt.RoundCap)
            p.setPen(lpen); p.setBrush(Qt.NoBrush)
            p.drawPath(path2)

            # last point dot
            p.setBrush(QColor(0,229,255)); p.setPen(Qt.NoPen)
            p.drawEllipse(QRectF(xs[-1]-3, ly(self._points[n-1])-3, 6, 6))

        p.end()


# ══════════════════════════════════════════════════════════════════════════════
# ⑥  SOLVER LOG PANEL
# ══════════════════════════════════════════════════════════════════════════════
LOG_ENTRIES = [
    ("14:32:01", "info",  "Initializing CalculiX 2.21 solver..."),
    ("14:32:02", "ok",    "Mesh imported: 12,480 nodes, 9,864 elements"),
    ("14:32:02", "info",  "Assembling global stiffness matrix [37440×37440]"),
    ("14:32:03", "info",  "Applying boundary conditions (3 sets)"),
    ("14:32:03", "info",  "Factorizing via PARDISO sparse solver..."),
    ("14:32:04", "ok",    "Linear system solved  ITER=12  RESIDUAL=1.2e-6"),
    ("14:32:04", "warn",  "σ_max = 312.4 MPa  ←  approaches yield threshold"),
    ("14:32:05", "ok",    "Post-processing complete in 2.4 s"),
    ("14:32:05", "ok",    "Safety factor F_s = 1.44  (yield 450 MPa / σ_max 312.4 MPa)"),
]

class SolverLogPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(148)
        self.setStyleSheet(f"background:{C['deep'].name()}; border-top:1px solid {C['border'].name()};")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # Log section (left ~60%)
        log_widget = QWidget(); log_widget.setStyleSheet("background:transparent;")
        ll = QVBoxLayout(log_widget); ll.setContentsMargins(0,0,0,0); ll.setSpacing(0)
        ll.addWidget(self._make_header("SOLVER LOG", "12 lines"))
        self._log_scroll = QScrollArea(); self._log_scroll.setWidgetResizable(True)
        self._log_scroll.setFrameShape(QFrame.NoFrame)
        self._log_scroll.setStyleSheet("QScrollArea{background:transparent;border:none;} QScrollBar:vertical{width:3px;background:transparent;} QScrollBar::handle:vertical{background:#0e2030;}")
        self._log_container = QWidget(); self._log_container.setStyleSheet("background:transparent;")
        self._log_layout = QVBoxLayout(self._log_container); self._log_layout.setContentsMargins(0,4,0,4); self._log_layout.setSpacing(0)
        self._log_layout.addStretch()
        self._log_scroll.setWidget(self._log_container)
        ll.addWidget(self._log_scroll, 1)
        layout.addWidget(log_widget, 6)

        # Divider
        vdiv = QFrame(); vdiv.setFrameShape(QFrame.VLine)
        vdiv.setStyleSheet(f"color:{C['border2'].name()};")
        layout.addWidget(vdiv)

        # Stats section (right ~40%)
        stats_widget = QWidget(); stats_widget.setStyleSheet("background:transparent;")
        sl = QVBoxLayout(stats_widget); sl.setContentsMargins(0,0,0,0); sl.setSpacing(0)
        sl.addWidget(self._make_header("SOLVE STATS", ""))
        grid = QWidget(); grid.setStyleSheet("background:transparent;")
        gl = QHBoxLayout(grid); gl.setContentsMargins(8,6,8,6); gl.setSpacing(8)
        stats = [
            ("12,480",  "NODES"),
            ("9,864",   "ELEMENTS"),
            ("37,440",  "DOF"),
            ("1.2e-6",  "RESIDUAL"),
            ("2.4s",    "SOLVE TIME"),
            ("1.44",    "SAFETY F."),
        ]
        cols = [QVBoxLayout() for _ in range(3)]
        for i, (val, lbl) in enumerate(stats):
            col = cols[i % 3]
            w = QWidget(); w.setStyleSheet("background:#060f1a;border:1px solid #0a1e30;")
            wl = QVBoxLayout(w); wl.setContentsMargins(6,4,6,4); wl.setSpacing(0)
            v = QLabel(val); v.setFont(QFont("Courier New", 12, QFont.Bold))
            color = "#00ff9d" if lbl == "SAFETY F." else ("#ff8800" if lbl == "RESIDUAL" else "#00c8ff")
            v.setStyleSheet(f"color:{color}; background:transparent;")
            wl.addWidget(v)
            l = QLabel(lbl); l.setFont(QFont("Courier New", 8))
            l.setStyleSheet("color:#1a3050; background:transparent;")
            wl.addWidget(l)
            col.addWidget(w)
        for c in cols:
            cw = QWidget(); cw.setStyleSheet("background:transparent;"); cw.setLayout(c)
            gl.addWidget(cw)
        sl.addWidget(grid, 1)
        layout.addWidget(stats_widget, 4)

        # Populate log with staggered delay
        self._log_index = 0
        self._log_timer = QTimer(self); self._log_timer.timeout.connect(self._add_log_line)
        self._log_timer.start(160)

    def _make_header(self, title, right_label):
        w = QWidget(); w.setFixedHeight(26)
        w.setStyleSheet(f"background:{C['panel2'].name()};border-bottom:1px solid {C['border'].name()};")
        l = QHBoxLayout(w); l.setContentsMargins(10,0,8,0)
        bar = QLabel("▌"); bar.setStyleSheet("color:#00c8ff;font-size:12px;")
        l.addWidget(bar)
        lbl = QLabel(title); lbl.setFont(QFont("Courier New",8,QFont.Bold))
        lbl.setStyleSheet("color:#00c8ff;letter-spacing:2px;")
        l.addWidget(lbl); l.addStretch()
        if right_label:
            rl = QLabel(right_label); rl.setFont(QFont("Courier New",8))
            rl.setStyleSheet("color:#1a3050;")
            l.addWidget(rl)
        return w

    def _add_log_line(self):
        if self._log_index >= len(LOG_ENTRIES):
            self._log_timer.stop()
            return
        ts, kind, msg = LOG_ENTRIES[self._log_index]
        self._log_index += 1

        line = QWidget(); line.setStyleSheet("background:transparent;")
        ll = QHBoxLayout(line); ll.setContentsMargins(10,1,8,1); ll.setSpacing(8)

        ts_lbl = QLabel(ts); ts_lbl.setFont(QFont("Courier New",9))
        ts_lbl.setFixedWidth(56); ts_lbl.setStyleSheet("color:#1a3050; background:transparent;")
        ll.addWidget(ts_lbl)

        colors = {"ok":"#00ff9d","warn":"#ff8800","err":"#ff2244","info":"#6aaac8"}
        msg_lbl = QLabel(msg); msg_lbl.setFont(QFont("Courier New",9))
        msg_lbl.setStyleSheet(f"color:{colors.get(kind,'#6aaac8')}; background:transparent;")
        ll.addWidget(msg_lbl)
        ll.addStretch()

        # Insert before stretch
        idx = self._log_layout.count() - 1
        self._log_layout.insertWidget(idx, line)
        QTimer.singleShot(20, lambda: self._log_scroll.verticalScrollBar().setValue(
            self._log_scroll.verticalScrollBar().maximum()
        ))

    def replay_log(self):
        """Replay log animation (called on solve)."""
        # clear existing
        while self._log_layout.count() > 1:
            item = self._log_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._log_index = 0
        self._log_timer.start(120)


# ══════════════════════════════════════════════════════════════════════════════
# ⑦  TOPBAR  +  VIEW MODE BUTTONS
# ══════════════════════════════════════════════════════════════════════════════
class TopBar(QWidget):
    def __init__(self, viewport: FEAViewport, parent=None):
        super().__init__(parent)
        self._vp = viewport
        self.setFixedHeight(44)
        self.setStyleSheet(f"background:{C['panel2'].name()};border-bottom:1px solid {C['border2'].name()};")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12,0,12,0)
        layout.setSpacing(0)

        # Logo
        logo = QLabel("MECH")
        logo.setFont(QFont("Courier New",14,QFont.Black))
        logo.setStyleSheet("color:#00e5ff; letter-spacing:3px;")
        layout.addWidget(logo)
        logo2 = QLabel("FORGE")
        logo2.setFont(QFont("Courier New",14,QFont.Bold))
        logo2.setStyleSheet("color:#2a6080; letter-spacing:2px;")
        layout.addWidget(logo2)
        sep = QLabel("  ▸  ")
        sep.setStyleSheet("color:#1a3050;")
        layout.addWidget(sep)
        mode_lbl = QLabel("CAE WORKBENCH")
        mode_lbl.setFont(QFont("Courier New",10,QFont.Bold))
        mode_lbl.setStyleSheet("color:#c8e8ff;letter-spacing:2px;")
        layout.addWidget(mode_lbl)

        layout.addSpacing(20)

        # Tab buttons
        self._tabs = {}
        for name in ["GEOMETRY","MESH · FEA","TOPOLOGY","FATIGUE","CFD","REPORT"]:
            btn = QPushButton(name)
            btn.setFont(QFont("Courier New",10))
            btn.setFixedHeight(44)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            active = (name == "MESH · FEA")
            self._style_tab(btn, active)
            layout.addWidget(btn)
            self._tabs[name] = btn

        layout.addStretch()

        # View mode toggle
        for mode in ["ISO","WIRE","STRESS","SOLID"]:
            vbtn = QPushButton(mode)
            vbtn.setFont(QFont("Courier New",9))
            vbtn.setFixedHeight(26)
            vbtn.setCursor(QCursor(Qt.PointingHandCursor))
            vbtn.setStyleSheet("QPushButton{background:#060f1a;border:1px solid #0e2030;color:#2a6080;padding:0 8px;margin:0 2px;} QPushButton:hover{border-color:#00c8ff;color:#00c8ff;}")
            vbtn.clicked.connect(lambda _, m=mode: self._set_view(m))
            layout.addWidget(vbtn)
            if mode == "STRESS":
                vbtn.setStyleSheet("QPushButton{background:#002840;border:1px solid #00c8ff;color:#00e5ff;padding:0 8px;margin:0 2px;}")

        layout.addSpacing(12)

        # Status pill
        pill = QLabel("●  SOLVER READY")
        pill.setFont(QFont("Courier New",9,QFont.Bold))
        pill.setStyleSheet("color:#00ff9d; background:#002820; border:1px solid #00ff9d; padding:2px 10px;")
        layout.addWidget(pill)

    def _style_tab(self, btn, active):
        if active:
            btn.setStyleSheet("QPushButton{background:rgba(0,200,255,0.05);border-bottom:2px solid #00e5ff;color:#00e5ff;padding:0 12px;} QPushButton:hover{color:#00e5ff;}")
        else:
            btn.setStyleSheet("QPushButton{background:transparent;border-bottom:2px solid transparent;color:#2a6080;padding:0 12px;} QPushButton:hover{color:#6aaac8;border-bottom-color:#2a6080;}")

    def _set_view(self, mode):
        vm = {"ISO":"STRESS","WIRE":"WIRE","STRESS":"STRESS","SOLID":"SOLID"}.get(mode,"STRESS")
        self._vp.set_view_mode(vm)


# ══════════════════════════════════════════════════════════════════════════════
# ⑧  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class CAEWorkbenchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MechForge AI — CAE Workbench")
        self.setMinimumSize(1280, 760)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_pos = None

        central = QWidget()
        central.setObjectName("central")
        central.setStyleSheet(f"#central{{background:{C['void'].name()};border:1px solid {C['border2'].name()};border-radius:8px;}}")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(0)

        # ── viewport (created first, shared with topbar) ──
        self._viewport = FEAViewport()

        # ── topbar ──
        self._topbar = TopBar(self._viewport)
        root.addWidget(self._topbar)

        # ── main 3-column body ──
        body = QHBoxLayout()
        body.setContentsMargins(0,0,0,0)
        body.setSpacing(0)

        self._tree_panel = ModelTreePanel()
        body.addWidget(self._tree_panel)

        # center: viewport
        body.addWidget(self._viewport, 1)

        # right: analysis
        self._analysis = AnalysisPanel()
        self._analysis.connect_run(self._run_solve)
        body.addWidget(self._analysis)

        body_widget = QWidget(); body_widget.setStyleSheet("background:transparent;")
        body_widget.setLayout(body)
        root.addWidget(body_widget, 1)

        # ── bottom log ──
        self._log_panel = SolverLogPanel()
        root.addWidget(self._log_panel)

        self.setStyleSheet("QMainWindow{background:transparent;}")

    def _run_solve(self):
        self._viewport.start_solve()
        self._log_panel.replay_log()
        self._analysis._conv_widget.start_solve()

    # ── frameless drag ──────────────────────────────────────────────────────
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and e.position().y() < 50:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        for i in range(8, 0, -1):
            p.setPen(QPen(QColor(0, 200, 255, 6), i * 2))
            p.drawRoundedRect(i, i, self.width()-i*2, self.height()-i*2, 8, 8)
        p.end()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window,          QColor("#0a121d"))
    palette.setColor(QPalette.WindowText,      QColor("#c8e8ff"))
    palette.setColor(QPalette.Base,            QColor("#060f1a"))
    palette.setColor(QPalette.Text,            QColor("#c8e8ff"))
    palette.setColor(QPalette.Button,          QColor("#0d1825"))
    palette.setColor(QPalette.ButtonText,      QColor("#c8e8ff"))
    palette.setColor(QPalette.Highlight,       QColor("#00c8ff"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    win = CAEWorkbenchWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()