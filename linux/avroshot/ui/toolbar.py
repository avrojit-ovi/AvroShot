"""Floating Lightshot-style annotation and action toolbars for AvroShot."""

from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import QPointF, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import (
    QColorDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


TOOLBAR_STYLE = """
QFrame#AvroToolbar {
    background-color: rgba(24, 24, 32, 238);
    border: 1px solid rgba(255, 255, 255, 45);
    border-radius: 8px;
}
QToolButton {
    background-color: transparent;
    color: #f1f5f9;
    border: 1px solid transparent;
    border-radius: 5px;
    padding: 4px;
    font-size: 11px;
    font-weight: 600;
}
QToolButton:hover {
    background-color: rgba(255, 255, 255, 32);
    border: 1px solid rgba(255, 255, 255, 50);
}
QToolButton:checked {
    background-color: rgba(244, 63, 94, 210);
    border: 1px solid #fb7185;
    color: #ffffff;
}
QToolButton:disabled {
    color: rgba(255, 255, 255, 70);
}
QLabel {
    color: #e2e8f0;
    font-size: 11px;
    font-weight: 600;
}
QSlider::groove:horizontal {
    height: 4px;
    background: rgba(255, 255, 255, 65);
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #f43f5e;
    border: 1px solid #ffffff;
    width: 12px;
    margin: -4px 0;
    border-radius: 6px;
}
"""


def _draw_tool_icon(kind: str, color: str = "#f8fafc") -> QIcon:
    """Render crisp 20x20 vector icons for all Lightshot tools and actions."""
    pix = QPixmap(20, 20)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    c = QColor(color)
    pen = QPen(c, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)

    if kind == "select":
        # Cursor pointer icon
        path = QPainterPath()
        path.moveTo(5, 3)
        path.lineTo(5, 16)
        path.lineTo(8.5, 12.8)
        path.lineTo(11.2, 17.5)
        path.lineTo(13.0, 16.5)
        path.lineTo(10.3, 11.8)
        path.lineTo(15, 11.8)
        path.closeSubpath()
        p.setBrush(c)
        p.drawPath(path)
    elif kind == "pen":
        path = QPainterPath(QPointF(3, 15))
        path.cubicTo(QPointF(7, 4), QPointF(12, 18), QPointF(17, 5))
        p.drawPath(path)
    elif kind == "line":
        p.drawLine(QPointF(3, 16), QPointF(17, 4))
    elif kind == "arrow":
        p.drawLine(QPointF(3, 16), QPointF(16, 4))
        p.drawLine(QPointF(16, 4), QPointF(10, 4.5))
        p.drawLine(QPointF(16, 4), QPointF(15.5, 10))
    elif kind == "rect":
        p.drawRect(QRectF(3.5, 4.5, 13, 11))
    elif kind == "marker":
        hl = QColor("#facc15")
        hl.setAlpha(200)
        p.setPen(QPen(hl, 5.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap))
        p.drawLine(QPointF(4, 14), QPointF(16, 6))
    elif kind == "text":
        f = p.font()
        f.setBold(True)
        f.setPixelSize(15)
        p.setFont(f)
        p.drawText(QRectF(0, 0, 20, 20), Qt.AlignmentFlag.AlignCenter, "T")
    elif kind == "undo":
        path = QPainterPath(QPointF(6, 8))
        path.lineTo(12, 8)
        path.arcTo(QRectF(8, 8, 8, 7), 90, -180)
        path.lineTo(7, 15)
        p.drawPath(path)
        p.drawLine(QPointF(5, 8), QPointF(8.5, 5))
        p.drawLine(QPointF(5, 8), QPointF(8.5, 11))
    elif kind == "redo":
        path = QPainterPath(QPointF(14, 8))
        path.lineTo(8, 8)
        path.arcTo(QRectF(4, 8, 8, 7), 90, 180)
        path.lineTo(13, 15)
        p.drawPath(path)
        p.drawLine(QPointF(15, 8), QPointF(11.5, 5))
        p.drawLine(QPointF(15, 8), QPointF(11.5, 11))
    elif kind == "upload":
        # Cloud with up arrow
        p.drawRoundedRect(QRectF(3, 9, 14, 7), 3.5, 3.5)
        p.drawLine(QPointF(10, 13), QPointF(10, 4))
        p.drawLine(QPointF(10, 4), QPointF(7, 7))
        p.drawLine(QPointF(10, 4), QPointF(13, 7))
    elif kind == "copy":
        p.drawRect(QRectF(6.5, 6.5, 9.5, 10.5))
        p.drawLine(QPointF(4, 13), QPointF(4, 3.5))
        p.drawLine(QPointF(4, 3.5), QPointF(13, 3.5))
    elif kind == "save":
        p.drawRoundedRect(QRectF(3.5, 3.5, 13, 13), 2, 2)
        p.drawRect(QRectF(6.5, 3.5, 7, 4.5))
        p.drawRect(QRectF(6, 11, 8, 5.5))
    elif kind == "close":
        p.setPen(QPen(QColor("#fb7185"), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(QPointF(5, 5), QPointF(15, 15))
        p.drawLine(QPointF(15, 5), QPointF(5, 15))

    p.end()
    return QIcon(pix)


def _draw_color_swatch(color: QColor) -> QIcon:
    pix = QPixmap(20, 20)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setPen(QPen(QColor("#ffffff"), 1.5))
    p.setBrush(color)
    p.drawEllipse(QRectF(2.5, 2.5, 15, 15))
    p.end()
    return QIcon(pix)


class AnnotationToolbar(QFrame):
    """Vertical/compact Lightshot drawing toolbar (Pen, Line, Arrow, Rect, Marker, Text, Color, Thickness, Undo/Redo)."""

    tool_selected = pyqtSignal(str)
    color_changed = pyqtSignal(QColor)
    thickness_changed = pyqtSignal(int)
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()

    def __init__(
        self,
        parent: QWidget | None = None,
        initial_tool: str = "pen",
        initial_color: str = "#ff2e55",
        initial_thickness: int = 3,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("AvroToolbar")
        self.setStyleSheet(TOOLBAR_STYLE)
        self.setCursor(Qt.CursorShape.ArrowCursor)

        self._current_color = QColor(initial_color)
        self._tool_buttons: dict[str, QToolButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 6, 5, 6)
        layout.setSpacing(4)

        tools = [
            ("select", "Move / Resize Selection (V)"),
            ("pen", "Freehand Pen (P)"),
            ("line", "Line (L)"),
            ("arrow", "Arrow (A)"),
            ("rect", "Rectangle (R)"),
            ("marker", "Highlighter Marker (M)"),
            ("text", "Text Tool (T)"),
        ]

        for tool_id, tooltip in tools:
            btn = QToolButton(self)
            btn.setIcon(_draw_tool_icon(tool_id))
            btn.setIconSize(QSize(20, 20))
            btn.setFixedSize(30, 28)
            btn.setCheckable(True)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda _checked, tid=tool_id: self.set_active_tool(tid))
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
            self._tool_buttons[tool_id] = btn

        # Color picker button
        self.color_btn = QToolButton(self)
        self.color_btn.setIcon(_draw_color_swatch(self._current_color))
        self.color_btn.setIconSize(QSize(20, 20))
        self.color_btn.setFixedSize(30, 28)
        self.color_btn.setToolTip("Choose Color (C)")
        self.color_btn.clicked.connect(self._pick_color)
        layout.addWidget(self.color_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Thickness indicator + compact cycle button
        self.thickness_btn = QToolButton(self)
        self.thickness_btn.setFixedSize(30, 24)
        self._thickness = max(1, min(15, int(initial_thickness)))
        self._update_thickness_label()
        self.thickness_btn.setToolTip("Click to cycle Line Thickness (or use mouse wheel / [ and ])")
        self.thickness_btn.clicked.connect(self._cycle_thickness)
        layout.addWidget(self.thickness_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Undo & Redo buttons
        self.undo_btn = QToolButton(self)
        self.undo_btn.setIcon(_draw_tool_icon("undo"))
        self.undo_btn.setIconSize(QSize(20, 20))
        self.undo_btn.setFixedSize(30, 28)
        self.undo_btn.setToolTip("Undo (Ctrl+Z)")
        self.undo_btn.clicked.connect(self.undo_requested.emit)
        layout.addWidget(self.undo_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.redo_btn = QToolButton(self)
        self.redo_btn.setIcon(_draw_tool_icon("redo"))
        self.redo_btn.setIconSize(QSize(20, 20))
        self.redo_btn.setFixedSize(30, 28)
        self.redo_btn.setToolTip("Redo (Ctrl+Y / Ctrl+Shift+Z)")
        self.redo_btn.clicked.connect(self.redo_requested.emit)
        layout.addWidget(self.redo_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.set_active_tool(initial_tool if initial_tool in self._tool_buttons else "pen")
        self.adjustSize()

    def set_active_tool(self, tool_id: str) -> None:
        for tid, btn in self._tool_buttons.items():
            btn.setChecked(tid == tool_id)
        self.tool_selected.emit(tool_id)

    def set_undo_redo_enabled(self, can_undo: bool, can_redo: bool) -> None:
        self.undo_btn.setEnabled(can_undo)
        self.redo_btn.setEnabled(can_redo)

    def set_thickness(self, val: int) -> None:
        self._thickness = max(1, min(20, val))
        self._update_thickness_label()
        self.thickness_changed.emit(self._thickness)

    def _cycle_thickness(self) -> None:
        presets = [2, 3, 5, 8, 12]
        for p in presets:
            if p > self._thickness:
                self.set_thickness(p)
                return
        self.set_thickness(presets[0])

    def _update_thickness_label(self) -> None:
        self.thickness_btn.setText(f"{self._thickness}px")

    def _pick_color(self) -> None:
        chosen = QColorDialog.getColor(
            self._current_color,
            self.parentWidget(),
            "Select Annotation Color",
        )
        if chosen.isValid():
            self._current_color = chosen
            self.color_btn.setIcon(_draw_color_swatch(self._current_color))
            self.color_changed.emit(self._current_color)


class ActionToolbar(QFrame):
    """Horizontal Lightshot bottom action bar (Upload/Share, Copy, Save, Cancel)."""

    upload_requested = pyqtSignal()
    copy_requested = pyqtSignal()
    save_requested = pyqtSignal()
    close_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("AvroToolbar")
        self.setStyleSheet(TOOLBAR_STYLE)
        self.setCursor(Qt.CursorShape.ArrowCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 5, 6, 5)
        layout.setSpacing(5)

        self.upload_btn = self._make_btn("upload", "Upload", "Upload & Copy Shareable Link (Ctrl+U)", self.upload_requested.emit)
        self.copy_btn = self._make_btn("copy", "Copy", "Copy to Clipboard (Ctrl+C / Enter)", self.copy_requested.emit)
        self.save_btn = self._make_btn("save", "Save", "Save Screenshot (Ctrl+S)", self.save_requested.emit)
        self.close_btn = self._make_btn("close", "", "Cancel (Esc)", self.close_requested.emit)

        layout.addWidget(self.upload_btn)
        layout.addWidget(self.copy_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.close_btn)
        self.adjustSize()

    def _make_btn(self, icon_kind: str, label: str, tooltip: str, slot: Callable[[], None]) -> QToolButton:
        btn = QToolButton(self)
        btn.setIcon(_draw_tool_icon(icon_kind))
        btn.setIconSize(QSize(18, 18))
        if label:
            btn.setText(f" {label}")
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            btn.setFixedHeight(28)
        else:
            btn.setFixedSize(28, 28)
        btn.setToolTip(tooltip)
        btn.clicked.connect(slot)
        return btn
