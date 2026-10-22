"""UI package for AvroShot."""

from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap


def create_app_icon(size: int = 64) -> QIcon:
    """Create the AvroShot crisp vector-rendered application icon."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # Rounded gradient background
    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0.0, QColor("#7c3aed"))  # Feather violet
    grad.setColorAt(0.5, QColor("#db2777"))  # Vibrant magenta
    grad.setColorAt(1.0, QColor("#f43f5e"))  # Crimson rose

    rect = QRectF(size * 0.06, size * 0.06, size * 0.88, size * 0.88)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(grad)
    p.drawRoundedRect(rect, size * 0.22, size * 0.22)

    # Selection frame corners + camera aperture symbol
    pen = QPen(QColor("#ffffff"), max(2.0, size * 0.065), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    m = size * 0.24
    s = size - 2 * m
    crop_rect = QRectF(m, m, s, s)
    p.drawRoundedRect(crop_rect, size * 0.06, size * 0.06)

    # Corner handles
    h = max(4.0, size * 0.11)
    p.setBrush(QColor("#ffffff"))
    p.setPen(Qt.PenStyle.NoPen)
    for cx, cy in [
        (crop_rect.left(), crop_rect.top()),
        (crop_rect.right(), crop_rect.top()),
        (crop_rect.left(), crop_rect.bottom()),
        (crop_rect.right(), crop_rect.bottom()),
    ]:
        p.drawEllipse(QPointF(cx, cy), h * 0.55, h * 0.55)

    # Center lens dot
    p.setBrush(QColor(255, 255, 255, 220))
    p.drawEllipse(QPointF(size * 0.5, size * 0.5), size * 0.10, size * 0.10)

    p.end()
    return QIcon(pix)
