"""Fullscreen Lightshot-style screenshot overlay with 8 resize handles, annotations, and output actions."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QPoint, QPointF, QRect, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QCursor,
    QFont,
    QGuiApplication,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QWheelEvent,
)
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLineEdit,
    QMessageBox,
    QWidget,
)

from avroshot import APP_NAME
from avroshot.annotations import (
    AnnotationHistory,
    AnnotationShape,
    ArrowShape,
    LineShape,
    MarkerShape,
    PenShape,
    RectShape,
    TextShape,
)
from avroshot.config import AppSettings
from avroshot.history import HistoryManager
from avroshot.platforms import get_platform_backend
from avroshot.ui.toolbar import ActionToolbar, AnnotationToolbar
from avroshot.uploader import UploadResult, UploadWorker


HANDLE_SIZE = 8
HANDLE_HIT_RADIUS = 10


class CaptureOverlay(QWidget):
    """Frameless fullscreen Lightshot overlay displaying the frozen screen and interactive region."""

    capture_completed = pyqtSignal(str)  # emits status message when closed/done

    def __init__(
        self,
        screenshot: QPixmap,
        settings: AppSettings | None = None,
        history_manager: HistoryManager | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.settings = settings or AppSettings.load()
        self.history_manager = history_manager or HistoryManager(self.settings.max_history_items)
        self.backend = get_platform_backend()

        self.original_pixmap = screenshot
        self.annotations = AnnotationHistory()
        self.active_shape: AnnotationShape | None = None

        self.current_tool: str = self.settings.default_tool
        self.current_color: QColor = QColor(self.settings.default_color)
        self.current_thickness: int = self.settings.default_thickness

        # Selection state
        self.selection_rect: QRectF = QRectF()
        self._interaction_mode: str = "none"  # "creating", "moving", "resizing", "drawing"
        self._active_handle: str = ""
        self._drag_start_pos: QPointF = QPointF()
        self._initial_rect_on_drag: QRectF = QRectF()
        self._status_banner: str = ""

        # Inline text editor for Text tool
        self._text_input: QLineEdit | None = None
        self._text_pos: QPointF = QPointF()

        self._upload_worker: UploadWorker | None = None

        self._init_window()
        self._init_toolbars()

    def _init_window(self) -> None:
        self.setWindowTitle(f"{APP_NAME} Capture")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.CrossCursor)

        # Span all available screens (multi-monitor virtual geometry)
        screens = QGuiApplication.screens()
        if screens:
            virtual_rect = QRect()
            for scr in screens:
                virtual_rect = virtual_rect.united(scr.geometry())
            self.setGeometry(virtual_rect)
        else:
            self.resize(self.original_pixmap.size())

    def _init_toolbars(self) -> None:
        self.annotation_bar = AnnotationToolbar(
            self,
            initial_tool=self.current_tool,
            initial_color=self.current_color.name(),
            initial_thickness=self.current_thickness,
        )
        self.annotation_bar.tool_selected.connect(self._on_tool_selected)
        self.annotation_bar.color_changed.connect(self._on_color_changed)
        self.annotation_bar.thickness_changed.connect(self._on_thickness_changed)
        self.annotation_bar.undo_requested.connect(self.undo_annotation)
        self.annotation_bar.redo_requested.connect(self.redo_annotation)
        self.annotation_bar.hide()

        self.action_bar = ActionToolbar(self)
        self.action_bar.upload_requested.connect(self.upload_selection)
        self.action_bar.copy_requested.connect(self.copy_selection)
        self.action_bar.save_requested.connect(self.save_selection)
        self.action_bar.close_requested.connect(self.cancel_capture)
        self.action_bar.hide()

        self._sync_undo_redo_buttons()

    def show_fullscreen_overlay(self) -> None:
        """Display the overlay across the screen."""
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
        self.setFocus()

    # ─── Selection & Handle Helpers ──────────────────────────────────────────

    def has_selection(self) -> bool:
        return self.selection_rect.width() >= 4 and self.selection_rect.height() >= 4

    def set_selection_rect(self, rect: QRectF) -> None:
        """Programmatically set selection rectangle (also used by tests)."""
        bounded = rect.normalized().intersected(QRectF(self.rect()))
        self.selection_rect = bounded
        self._update_toolbars_position()
        self.update()

    def _handle_points(self) -> dict[str, QPointF]:
        r = self.selection_rect
        cx = r.center().x()
        cy = r.center().y()
        return {
            "tl": r.topLeft(),
            "tc": QPointF(cx, r.top()),
            "tr": r.topRight(),
            "rc": QPointF(r.right(), cy),
            "br": r.bottomRight(),
            "bc": QPointF(cx, r.bottom()),
            "bl": r.bottomLeft(),
            "lc": QPointF(r.left(), cy),
        }

    def _hit_test_handle(self, pos: QPointF) -> str:
        if not self.has_selection():
            return ""
        for name, pt in self._handle_points().items():
            if abs(pos.x() - pt.x()) <= HANDLE_HIT_RADIUS and abs(pos.y() - pt.y()) <= HANDLE_HIT_RADIUS:
                return name
        return ""

    def _cursor_for_handle(self, handle: str) -> Qt.CursorShape:
        mapping = {
            "tl": Qt.CursorShape.SizeFDiagCursor,
            "br": Qt.CursorShape.SizeFDiagCursor,
            "tr": Qt.CursorShape.SizeBDiagCursor,
            "bl": Qt.CursorShape.SizeBDiagCursor,
            "tc": Qt.CursorShape.SizeVerCursor,
            "bc": Qt.CursorShape.SizeVerCursor,
            "lc": Qt.CursorShape.SizeHorCursor,
            "rc": Qt.CursorShape.SizeHorCursor,
        }
        return mapping.get(handle, Qt.CursorShape.CrossCursor)

    def _update_toolbars_position(self) -> None:
        if not self.has_selection() or self._interaction_mode in ("creating", "resizing", "moving"):
            self.annotation_bar.hide()
            self.action_bar.hide()
            return

        r = self.selection_rect.toRect()
        margin = 6

        # Place vertical annotation toolbar on the right of selection (or left if near right edge)
        ann_w = self.annotation_bar.width()
        ann_h = self.annotation_bar.height()
        ann_x = r.right() + margin
        if ann_x + ann_w > self.width() - 4:
            ann_x = r.left() - ann_w - margin
        if ann_x < 4:
            ann_x = max(4, r.right() - ann_w - margin)

        ann_y = r.bottom() - ann_h
        ann_y = max(4, min(ann_y, self.height() - ann_h - 42))
        self.annotation_bar.move(ann_x, ann_y)
        self.annotation_bar.show()
        self.annotation_bar.raise_()

        # Place horizontal action toolbar below the bottom-right of selection (or above/inside if near bottom edge)
        act_w = self.action_bar.width()
        act_h = self.action_bar.height()
        act_x = r.right() - act_w
        act_x = max(4, min(act_x, self.width() - act_w - 4))
        act_y = r.bottom() + margin
        if act_y + act_h > self.height() - 4:
            act_y = r.top() - act_h - margin
        if act_y < 4:
            act_y = r.bottom() - act_h - margin
        self.action_bar.move(act_x, act_y)
        self.action_bar.show()
        self.action_bar.raise_()

    # ─── Painting (Lightshot Overlay, Bright Cutout, Size Badge, Handles) ────

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        # 1. Draw frozen desktop screenshot
        painter.drawPixmap(self.rect(), self.original_pixmap)

        # 2. Draw semi-transparent dark overlay outside selection
        dim_color = QColor(0, 0, 0, self.settings.overlay_dim_opacity)
        if self.has_selection():
            full_path = QPainterPath()
            full_path.addRect(QRectF(self.rect()))
            sel_path = QPainterPath()
            sel_path.addRect(self.selection_rect)
            outside_path = full_path.subtracted(sel_path)
            painter.fillPath(outside_path, dim_color)
        else:
            painter.fillRect(self.rect(), dim_color)
            self._draw_initial_Crosshair_hint(painter)

        # 3. Draw annotations clipped to the screenshot (or selection)
        for shape in self.annotations.shapes:
            shape.draw(painter)
        if self.active_shape is not None:
            self.active_shape.draw(painter)

        # 4. Draw selection border, 8 handles, and W×H dimension pill
        if self.has_selection():
            # Outer high-contrast border + inner white dashed line (classic Lightshot look)
            painter.setPen(QPen(QColor("#f43f5e"), 1.6))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.selection_rect)

            dash_pen = QPen(QColor(255, 255, 255, 210), 1.0, Qt.PenStyle.DashLine)
            painter.setPen(dash_pen)
            painter.drawRect(self.selection_rect)

            # 8 resize handles
            painter.setPen(QPen(QColor("#1e1b4b"), 1.2))
            painter.setBrush(QColor("#ffffff"))
            half = HANDLE_SIZE / 2.0
            for pt in self._handle_points().values():
                h_rect = QRectF(pt.x() - half, pt.y() - half, HANDLE_SIZE, HANDLE_SIZE)
                painter.drawRect(h_rect)

            # Dimension badge (e.g., "800 × 600")
            self._draw_dimension_badge(painter)

        if self._status_banner:
            self._draw_status_banner(painter)

        painter.end()

    def _draw_initial_Crosshair_hint(self, painter: QPainter) -> None:
        """Show subtle Lightshot instruction prompt before dragging."""
        hint = "Select an area with mouse  •  Ctrl+A Fullscreen  •  Esc Cancel"
        font = QFont("Sans Serif", 11, QFont.Weight.DemiBold)
        painter.setFont(font)
        fm = painter.fontMetrics()
        tw = fm.horizontalAdvance(hint) + 28
        th = fm.height() + 14
        rect = QRectF((self.width() - tw) / 2.0, 28, tw, th)
        painter.setPen(QPen(QColor(255, 255, 255, 50), 1.0))
        painter.setBrush(QColor(15, 23, 42, 215))
        painter.drawRoundedRect(rect, 8, 8)
        painter.setPen(QColor("#f8fafc"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, hint)

    def _draw_dimension_badge(self, painter: QPainter) -> None:
        w = int(round(self.selection_rect.width()))
        h = int(round(self.selection_rect.height()))
        label = f"{w} × {h}"
        font = QFont("Sans Serif", 10, QFont.Weight.Bold)
        painter.setFont(font)
        fm = painter.fontMetrics()
        bw = fm.horizontalAdvance(label) + 16
        bh = fm.height() + 8

        bx = self.selection_rect.left()
        by = self.selection_rect.top() - bh - 6
        if by < 4:
            by = self.selection_rect.top() + 6
            bx = self.selection_rect.left() + 6
        bx = max(4.0, min(bx, self.width() - bw - 4.0))

        badge_rect = QRectF(bx, by, bw, bh)
        painter.setPen(QPen(QColor(255, 255, 255, 45), 1.0))
        painter.setBrush(QColor(15, 23, 42, 225))
        painter.drawRoundedRect(badge_rect, 5, 5)
        painter.setPen(QColor("#f8fafc"))
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, label)

    def _draw_status_banner(self, painter: QPainter) -> None:
        font = QFont("Sans Serif", 11, QFont.Weight.Bold)
        painter.setFont(font)
        fm = painter.fontMetrics()
        bw = fm.horizontalAdvance(self._status_banner) + 28
        bh = fm.height() + 14
        rect = QRectF((self.width() - bw) / 2.0, self.height() - bh - 36, bw, bh)
        painter.setPen(QPen(QColor("#f43f5e"), 1.5))
        painter.setBrush(QColor(15, 23, 42, 235))
        painter.drawRoundedRect(rect, 8, 8)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._status_banner)

    # ─── Mouse & Drawing Events ──────────────────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            if self.has_selection():
                # Reset selection so user can re-drag
                self._commit_pending_text()
                self.selection_rect = QRectF()
                self.annotations.clear()
                self._sync_undo_redo_buttons()
                self._update_toolbars_position()
                self.update()
            else:
                self.cancel_capture()
            return

        if event.button() != Qt.MouseButton.LeftButton:
            return

        pos = event.position()
        self._commit_pending_text()

        # 1. Check 8 resize handles first
        handle = self._hit_test_handle(pos)
        if handle:
            self._interaction_mode = "resizing"
            self._active_handle = handle
            self._drag_start_pos = pos
            self._initial_rect_on_drag = QRectF(self.selection_rect)
            self._update_toolbars_position()
            return

        # 2. If no selection yet, or clicking outside selection, start a new selection
        if not self.has_selection() or not self.selection_rect.contains(pos):
            self.annotations.clear()
            self._sync_undo_redo_buttons()
            self._interaction_mode = "creating"
            self._drag_start_pos = pos
            self.selection_rect = QRectF(pos, pos)
            self._update_toolbars_position()
            self.update()
            return

        # 3. Clicking inside the selection: either move selection ("select" tool) or draw annotation
        if self.current_tool == "select":
            self._interaction_mode = "moving"
            self._drag_start_pos = pos
            self._initial_rect_on_drag = QRectF(self.selection_rect)
            self.setCursor(Qt.CursorShape.SizeAllCursor)
            self._update_toolbars_position()
            return

        if self.current_tool == "text":
            self._open_text_editor(pos)
            return

        # Start drawing shape
        self._interaction_mode = "drawing"
        self.active_shape = self._create_shape(pos)
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = event.position()

        if self._interaction_mode == "creating":
            self.selection_rect = QRectF(self._drag_start_pos, pos).normalized().intersected(QRectF(self.rect()))
            self.update()
            return

        if self._interaction_mode == "moving":
            delta = pos - self._drag_start_pos
            r = self._initial_rect_on_drag.translated(delta)
            # Keep inside screen bounds
            if r.left() < 0:
                r.moveLeft(0)
            if r.top() < 0:
                r.moveTop(0)
            if r.right() > self.width():
                r.moveRight(self.width())
            if r.bottom() > self.height():
                r.moveBottom(self.height())
            self.selection_rect = r
            self.update()
            return

        if self._interaction_mode == "resizing":
            r = QRectF(self._initial_rect_on_drag)
            h = self._active_handle
            if "l" in h:
                r.setLeft(pos.x())
            if "r" in h:
                r.setRight(pos.x())
            if "t" in h:
                r.setTop(pos.y())
            if "b" in h:
                r.setBottom(pos.y())
            self.selection_rect = r.normalized().intersected(QRectF(self.rect()))
            self.update()
            return

        if self._interaction_mode == "drawing" and self.active_shape is not None:
            self.active_shape.update_end(pos)
            self.update()
            return

        # Hover cursor updates
        handle = self._hit_test_handle(pos)
        if handle:
            self.setCursor(self._cursor_for_handle(handle))
        elif self.has_selection() and self.selection_rect.contains(pos):
            if self.current_tool == "select":
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            elif self.current_tool == "text":
                self.setCursor(Qt.CursorShape.IBeamCursor)
            else:
                self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.CrossCursor)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return

        if self._interaction_mode == "drawing" and self.active_shape is not None:
            self.active_shape.update_end(event.position())
            self.annotations.add(self.active_shape)
            self.active_shape = None
            self._sync_undo_redo_buttons()

        self._interaction_mode = "none"
        self._active_handle = ""
        self._update_toolbars_position()
        self.update()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Double-clicking inside the selection copies it immediately (classic Lightshot behavior)."""
        if event.button() == Qt.MouseButton.LeftButton and self.has_selection():
            if self.selection_rect.contains(event.position()) and self.current_tool == "select":
                self.copy_selection()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Scroll wheel adjusts stroke thickness quickly."""
        delta = event.angleDelta().y()
        if delta > 0:
            self.annotation_bar.set_thickness(self.current_thickness + 1)
        elif delta < 0:
            self.annotation_bar.set_thickness(self.current_thickness - 1)

    # ─── Annotation Helpers ──────────────────────────────────────────────────

    def _create_shape(self, start_pos: QPointF) -> AnnotationShape:
        t = self.current_tool
        if t == "pen":
            return PenShape(start_pos, self.current_color, self.current_thickness)
        if t == "marker":
            return MarkerShape(start_pos, self.current_color, self.current_thickness)
        if t == "line":
            return LineShape(start_pos, start_pos, self.current_color, self.current_thickness)
        if t == "arrow":
            return ArrowShape(start_pos, start_pos, self.current_color, self.current_thickness)
        if t == "rect":
            return RectShape(start_pos, start_pos, self.current_color, self.current_thickness)
        return PenShape(start_pos, self.current_color, self.current_thickness)

    def _open_text_editor(self, pos: QPointF) -> None:
        self._commit_pending_text()
        editor = QLineEdit(self)
        font_px = max(12, self.settings.default_font_size + (self.current_thickness - 3) * 2)
        editor.setFont(QFont("Sans Serif", font_px, QFont.Weight.Bold))
        editor.setStyleSheet(
            f"QLineEdit {{"
            f"  background-color: rgba(15, 23, 42, 200);"
            f"  color: {self.current_color.name()};"
            f"  border: 1px dashed #f43f5e;"
            f"  border-radius: 4px;"
            f"  padding: 2px 6px;"
            f"}}"
        )
        editor.move(int(pos.x()), int(pos.y() - font_px))
        editor.resize(220, font_px + 18)
        editor.returnPressed.connect(self._commit_pending_text)
        editor.show()
        editor.setFocus()
        self._text_input = editor
        self._text_pos = pos

    def _commit_pending_text(self) -> None:
        if self._text_input is None:
            return
        text = self._text_input.text().strip()
        font_px = max(12, self.settings.default_font_size + (self.current_thickness - 3) * 2)
        self._text_input.hide()
        self._text_input.deleteLater()
        self._text_input = None
        if text:
            self.annotations.add(TextShape(self._text_pos, text, self.current_color, font_px))
            self._sync_undo_redo_buttons()
            self.update()
        self.setFocus()

    def _on_tool_selected(self, tool_id: str) -> None:
        self._commit_pending_text()
        self.current_tool = tool_id

    def _on_color_changed(self, color: QColor) -> None:
        self.current_color = color

    def _on_thickness_changed(self, thickness: int) -> None:
        self.current_thickness = thickness

    def undo_annotation(self) -> None:
        self._commit_pending_text()
        if self.annotations.undo():
            self._sync_undo_redo_buttons()
            self.update()

    def redo_annotation(self) -> None:
        self._commit_pending_text()
        if self.annotations.redo():
            self._sync_undo_redo_buttons()
            self.update()

    def _sync_undo_redo_buttons(self) -> None:
        self.annotation_bar.set_undo_redo_enabled(
            self.annotations.can_undo(),
            self.annotations.can_redo(),
        )

    # ─── Rendering Final Cropped Output ──────────────────────────────────────

    def render_selected_pixmap(self) -> QPixmap:
        """Render the frozen screenshot + all annotations and crop to the selection rectangle."""
        self._commit_pending_text()

        # Composite full image with annotations first
        composed = QPixmap(self.original_pixmap.size())
        composed.fill(Qt.GlobalColor.transparent)
        painter = QPainter(composed)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.drawPixmap(0, 0, self.original_pixmap)

        # Account for potential DPI scaling between logical widget coords and pixmap pixel coords
        scale_x = self.original_pixmap.width() / max(1, self.width())
        scale_y = self.original_pixmap.height() / max(1, self.height())
        if abs(scale_x - 1.0) > 0.01 or abs(scale_y - 1.0) > 0.01:
            painter.scale(scale_x, scale_y)

        for shape in self.annotations.shapes:
            shape.draw(painter)
        painter.end()

        if not self.has_selection():
            return composed

        r = self.selection_rect
        crop_rect = QRect(
            int(round(r.left() * scale_x)),
            int(round(r.top() * scale_y)),
            max(1, int(round(r.width() * scale_x))),
            max(1, int(round(r.height() * scale_y))),
        ).intersected(composed.rect())

        return composed.copy(crop_rect)

    # ─── Output Actions (Copy, Save, Upload, Cancel) ─────────────────────────

    def copy_selection(self) -> bool:
        if not self.has_selection():
            self.set_selection_rect(QRectF(self.rect()))
        cropped = self.render_selected_pixmap()
        ok = self.backend.copy_to_clipboard(cropped)
        if self.settings.save_to_history:
            self.history_manager.record(cropped, action="copy")
        if self.settings.show_notifications:
            self.backend.send_notification(
                APP_NAME,
                f"Copied screenshot ({cropped.width()}×{cropped.height()}) to clipboard",
            )
        if self.settings.close_after_copy:
            self.capture_completed.emit("copied")
            self.close()
        return ok

    def save_selection(self, target_path: str | None = None) -> str | None:
        if not self.has_selection():
            self.set_selection_rect(QRectF(self.rect()))
        cropped = self.render_selected_pixmap()

        if not target_path:
            save_dir = Path(self.settings.save_directory)
            save_dir.mkdir(parents=True, exist_ok=True)
            default_name = datetime.now().strftime(self.settings.filename_pattern)
            default_path = str(save_dir / default_name)

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Save {APP_NAME} Screenshot",
                default_path,
                "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;WebP Image (*.webp);;All Files (*)",
            )
            if not file_path:
                return None
            target_path = file_path
        else:
            Path(target_path).parent.mkdir(parents=True, exist_ok=True)

        ext = Path(target_path).suffix.lower()
        fmt = "PNG"
        quality = -1
        if ext in (".jpg", ".jpeg"):
            fmt = "JPEG"
            quality = self.settings.jpeg_quality
        elif ext == ".webp":
            fmt = "WEBP"
            quality = self.settings.jpeg_quality

        saved = cropped.save(target_path, fmt, quality)
        if not saved:
            QMessageBox.warning(self, APP_NAME, f"Could not save screenshot to:\n{target_path}")
            return None

        if self.settings.auto_copy_on_save:
            self.backend.copy_to_clipboard(cropped)
        if self.settings.save_to_history:
            self.history_manager.record(cropped, action="save", saved_path=target_path)
        if self.settings.show_notifications:
            self.backend.send_notification(APP_NAME, f"Saved to {target_path}")
        if self.settings.close_after_save:
            self.capture_completed.emit(target_path)
            self.close()
        return target_path

    def upload_selection(self) -> None:
        if self._upload_worker is not None and self._upload_worker.isRunning():
            return
        if not self.has_selection():
            self.set_selection_rect(QRectF(self.rect()))
        cropped = self.render_selected_pixmap()

        self._status_banner = "Uploading screenshot and generating shareable link..."
        self.action_bar.upload_btn.setEnabled(False)
        self.update()

        self._upload_worker = UploadWorker(
            cropped,
            provider=self.settings.upload_provider,
            imgur_client_id=self.settings.imgur_client_id,
            parent=self,
        )
        self._upload_worker.finished_upload.connect(
            lambda res, pix=cropped: self._on_upload_finished(res, pix)
        )
        self._upload_worker.start()

    def _on_upload_finished(self, result: UploadResult, cropped: QPixmap) -> None:
        self.action_bar.upload_btn.setEnabled(True)
        if result.success and result.url:
            self.backend.copy_text_to_clipboard(result.url)
            if self.settings.save_to_history:
                self.history_manager.record(cropped, action="upload", share_url=result.url)
            if self.settings.show_notifications:
                self.backend.send_notification(
                    f"{APP_NAME} Link Copied!",
                    f"Shareable URL copied to clipboard:\n{result.url}",
                )
            self._status_banner = f"Uploaded! Link copied: {result.url}"
            self.update()
            self.capture_completed.emit(result.url)
            self.close()
        else:
            self._status_banner = f"Upload failed: {result.error}"
            self.update()
            QMessageBox.warning(
                self,
                f"{APP_NAME} Upload Error",
                f"Could not upload image:\n{result.error}",
            )

    def cancel_capture(self) -> None:
        self._commit_pending_text()
        self.capture_completed.emit("cancelled")
        self.close()

    # ─── Keyboard Shortcuts ──────────────────────────────────────────────────

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        mods = event.modifiers()

        if key == Qt.Key.Key_Escape:
            if self._text_input is not None:
                self._text_input.clear()
                self._commit_pending_text()
                return
            self.cancel_capture()
            return

        if self._text_input is not None:
            super().keyPressEvent(event)
            return

        # Ctrl+C or Enter/Return -> Copy to Clipboard
        if (mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_C) or key in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
        ):
            self.copy_selection()
            return

        # Ctrl+S -> Save
        if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_S:
            self.save_selection()
            return

        # Ctrl+U -> Upload
        if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_U:
            self.upload_selection()
            return

        # Ctrl+A -> Select Fullscreen
        if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_A:
            self.set_selection_rect(QRectF(self.rect()))
            return

        # Ctrl+Z -> Undo
        if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_Z:
            if mods & Qt.KeyboardModifier.ShiftModifier:
                self.redo_annotation()
            else:
                self.undo_annotation()
            return

        # Ctrl+Y -> Redo
        if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_Y:
            self.redo_annotation()
            return

        # Single-key tool hotkeys
        if not mods:
            tool_map = {
                Qt.Key.Key_V: "select",
                Qt.Key.Key_P: "pen",
                Qt.Key.Key_L: "line",
                Qt.Key.Key_A: "arrow",
                Qt.Key.Key_R: "rect",
                Qt.Key.Key_M: "marker",
                Qt.Key.Key_T: "text",
            }
            if key in tool_map:
                self.annotation_bar.set_active_tool(tool_map[key])
                return
            if key == Qt.Key.Key_BracketLeft:
                self.annotation_bar.set_thickness(self.current_thickness - 1)
                return
            if key == Qt.Key.Key_BracketRight:
                self.annotation_bar.set_thickness(self.current_thickness + 1)
                return

        super().keyPressEvent(event)
