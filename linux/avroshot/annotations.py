"""Annotation shapes and Undo/Redo command stack for AvroShot."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QPolygonF


class AnnotationShape(ABC):
    """Base class for all drawn annotations on a screenshot."""

    def __init__(self, color: QColor, thickness: int) -> None:
        self.color = QColor(color)
        self.thickness = max(1, int(thickness))

    @abstractmethod
    def draw(self, painter: QPainter) -> None:
        """Render this shape onto the QPainter."""

    @abstractmethod
    def update_end(self, pt: QPointF) -> None:
        """Update shape geometry while dragging the mouse."""


class PenShape(AnnotationShape):
    """Freehand smooth pen stroke."""

    def __init__(self, start_pt: QPointF, color: QColor, thickness: int) -> None:
        super().__init__(color, thickness)
        self.points: list[QPointF] = [QPointF(start_pt)]

    def update_end(self, pt: QPointF) -> None:
        self.points.append(QPointF(pt))

    def draw(self, painter: QPainter) -> None:
        if not self.points:
            return
        painter.save()
        pen = QPen(
            self.color,
            self.thickness,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        if len(self.points) == 1:
            painter.drawPoint(self.points[0])
        else:
            path = QPainterPath(self.points[0])
            for i in range(1, len(self.points)):
                p0 = self.points[i - 1]
                p1 = self.points[i]
                mid = QPointF((p0.x() + p1.x()) / 2.0, (p0.y() + p1.y()) / 2.0)
                path.quadTo(p0, mid)
            path.lineTo(self.points[-1])
            painter.drawPath(path)
        painter.restore()


class MarkerShape(PenShape):
    """Semi-transparent highlighter stroke."""

    def __init__(self, start_pt: QPointF, color: QColor, thickness: int) -> None:
        highlight_color = QColor(color)
        highlight_color.setAlpha(105)
        super().__init__(start_pt, highlight_color, max(12, thickness * 4))

    def draw(self, painter: QPainter) -> None:
        if not self.points:
            return
        painter.save()
        pen = QPen(
            self.color,
            self.thickness,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.SquareCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if len(self.points) == 1:
            painter.drawPoint(self.points[0])
        else:
            path = QPainterPath(self.points[0])
            for pt in self.points[1:]:
                path.lineTo(pt)
            painter.drawPath(path)
        painter.restore()


class LineShape(AnnotationShape):
    """Straight line segment."""

    def __init__(self, start_pt: QPointF, end_pt: QPointF, color: QColor, thickness: int) -> None:
        super().__init__(color, thickness)
        self.start_pt = QPointF(start_pt)
        self.end_pt = QPointF(end_pt)

    def update_end(self, pt: QPointF) -> None:
        self.end_pt = QPointF(pt)

    def draw(self, painter: QPainter) -> None:
        painter.save()
        pen = QPen(
            self.color,
            self.thickness,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        painter.setPen(pen)
        painter.drawLine(self.start_pt, self.end_pt)
        painter.restore()


class ArrowShape(AnnotationShape):
    """Lightshot-style directional arrow with crisp filled arrowhead."""

    def __init__(self, start_pt: QPointF, end_pt: QPointF, color: QColor, thickness: int) -> None:
        super().__init__(color, thickness)
        self.start_pt = QPointF(start_pt)
        self.end_pt = QPointF(end_pt)

    def update_end(self, pt: QPointF) -> None:
        self.end_pt = QPointF(pt)

    def draw(self, painter: QPainter) -> None:
        painter.save()
        dx = self.end_pt.x() - self.start_pt.x()
        dy = self.end_pt.y() - self.start_pt.y()
        length = math.hypot(dx, dy)
        if length < 2.0:
            painter.restore()
            return

        angle = math.atan2(dy, dx)
        head_len = max(12.0, self.thickness * 4.2)
        head_len = min(head_len, length * 0.85)
        head_angle = math.radians(28)

        p1 = QPointF(
            self.end_pt.x() - head_len * math.cos(angle - head_angle),
            self.end_pt.y() - head_len * math.sin(angle - head_angle),
        )
        p2 = QPointF(
            self.end_pt.x() - head_len * math.cos(angle + head_angle),
            self.end_pt.y() - head_len * math.sin(angle + head_angle),
        )

        # Shorten shaft slightly so it meets inside the arrowhead cleanly
        shaft_end = QPointF(
            self.end_pt.x() - (head_len * 0.65) * math.cos(angle),
            self.end_pt.y() - (head_len * 0.65) * math.sin(angle),
        )

        pen = QPen(
            self.color,
            self.thickness,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        painter.setPen(pen)
        painter.drawLine(self.start_pt, shaft_end)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color)
        head_poly = QPolygonF([self.end_pt, p1, p2])
        painter.drawPolygon(head_poly)
        painter.restore()


class RectShape(AnnotationShape):
    """Rectangle border annotation."""

    def __init__(self, start_pt: QPointF, end_pt: QPointF, color: QColor, thickness: int) -> None:
        super().__init__(color, thickness)
        self.start_pt = QPointF(start_pt)
        self.end_pt = QPointF(end_pt)

    def update_end(self, pt: QPointF) -> None:
        self.end_pt = QPointF(pt)

    def draw(self, painter: QPainter) -> None:
        painter.save()
        pen = QPen(
            self.color,
            self.thickness,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.SquareCap,
            Qt.PenJoinStyle.MiterJoin,
        )
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        rect = QRectF(self.start_pt, self.end_pt).normalized()
        painter.drawRect(rect)
        painter.restore()


class TextShape(AnnotationShape):
    """Text annotation with subtle contrast outline for readability on any background."""

    def __init__(self, pos: QPointF, text: str, color: QColor, font_size: int = 16) -> None:
        super().__init__(color, 1)
        self.pos = QPointF(pos)
        self.text = text
        self.font_size = max(10, int(font_size))

    def update_end(self, pt: QPointF) -> None:
        self.pos = QPointF(pt)

    def draw(self, painter: QPainter) -> None:
        if not self.text.strip():
            return
        painter.save()
        font = QFont("Sans Serif", self.font_size, QFont.Weight.Bold)
        painter.setFont(font)

        lines = self.text.splitlines()
        metrics = painter.fontMetrics()
        line_height = metrics.height()

        # Subtle dark drop shadow for crisp visibility on bright areas
        shadow_color = QColor(0, 0, 0, 170) if self.color.lightness() > 60 else QColor(255, 255, 255, 170)

        for idx, line in enumerate(lines):
            y = self.pos.y() + (idx + 1) * line_height - metrics.descent()
            painter.setPen(shadow_color)
            painter.drawText(QPointF(self.pos.x() + 1.5, y + 1.5), line)
            painter.setPen(self.color)
            painter.drawText(QPointF(self.pos.x(), y), line)

        painter.restore()


@dataclass
class AnnotationHistory:
    """Manages Undo and Redo stacks of AnnotationShape objects."""

    shapes: list[AnnotationShape] = field(default_factory=list)
    redo_stack: list[AnnotationShape] = field(default_factory=list)

    def add(self, shape: AnnotationShape) -> None:
        self.shapes.append(shape)
        self.redo_stack.clear()

    def undo(self) -> bool:
        if not self.shapes:
            return False
        self.redo_stack.append(self.shapes.pop())
        return True

    def redo(self) -> bool:
        if not self.redo_stack:
            return False
        self.shapes.append(self.redo_stack.pop())
        return True

    def clear(self) -> None:
        self.shapes.clear()
        self.redo_stack.clear()

    def can_undo(self) -> bool:
        return len(self.shapes) > 0

    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0
