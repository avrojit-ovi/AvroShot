"""Automated test suite for AvroShot core components."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication

from avroshot.annotations import (
    AnnotationHistory,
    ArrowShape,
    LineShape,
    MarkerShape,
    PenShape,
    RectShape,
    TextShape,
)
from avroshot.config import AppSettings
from avroshot.history import HistoryManager
from avroshot.ui.overlay import CaptureOverlay


app = QApplication.instance() or QApplication([])


class TestAvroShot(unittest.TestCase):
    def test_annotations_and_undo_redo(self) -> None:
        history = AnnotationHistory()
        self.assertFalse(history.can_undo())
        self.assertFalse(history.can_redo())

        pen = PenShape(QPointF(10, 10), QColor("#ff0000"), 3)
        pen.update_end(QPointF(30, 30))
        pen.update_end(QPointF(60, 40))
        history.add(pen)

        arrow = ArrowShape(QPointF(20, 20), QPointF(120, 90), QColor("#00ff00"), 4)
        history.add(arrow)

        rect = RectShape(QPointF(50, 50), QPointF(150, 120), QColor("#0000ff"), 2)
        history.add(rect)

        line = LineShape(QPointF(0, 0), QPointF(100, 100), QColor("#ffff00"), 3)
        history.add(line)

        marker = MarkerShape(QPointF(15, 15), QColor("#ff00ff"), 5)
        marker.update_end(QPointF(80, 15))
        history.add(marker)

        txt = TextShape(QPointF(40, 60), "Hello AvroShot", QColor("#ffffff"), 16)
        history.add(txt)

        self.assertEqual(len(history.shapes), 6)
        self.assertTrue(history.can_undo())

        # Undo twice
        self.assertTrue(history.undo())
        self.assertTrue(history.undo())
        self.assertEqual(len(history.shapes), 4)
        self.assertTrue(history.can_redo())

        # Redo once
        self.assertTrue(history.redo())
        self.assertEqual(len(history.shapes), 5)

        # Render all shapes onto a QImage to verify no exceptions and pixels change
        canvas = QImage(200, 200, QImage.Format.Format_ARGB32)
        canvas.fill(Qt.GlobalColor.black)
        painter = QPainter(canvas)
        for s in history.shapes:
            s.draw(painter)
        painter.end()

        # Verify some non-black pixels were drawn
        non_black = sum(
            1
            for x in range(0, 200, 5)
            for y in range(0, 200, 5)
            if (canvas.pixel(x, y) & 0x00FFFFFF) != 0
        )
        self.assertGreater(non_black, 0)

    def test_overlay_selection_crop_and_handles(self) -> None:
        base_pix = QPixmap(800, 600)
        base_pix.fill(QColor("#1e293b"))

        settings = AppSettings(
            save_to_history=False,
            show_notifications=False,
            close_after_copy=False,
            close_after_save=False,
        )
        overlay = CaptureOverlay(screenshot=base_pix, settings=settings)
        overlay.resize(800, 600)

        # Select 320x240 region
        overlay.set_selection_rect(QRectF(100, 120, 320, 240))
        self.assertTrue(overlay.has_selection())

        # Verify all 8 resize handles are positioned accurately
        handles = overlay._handle_points()
        self.assertEqual(set(handles.keys()), {"tl", "tc", "tr", "rc", "br", "bc", "bl", "lc"})
        self.assertEqual(overlay._hit_test_handle(QPointF(100, 120)), "tl")
        self.assertEqual(overlay._hit_test_handle(QPointF(420, 360)), "br")

        # Add an annotation inside selection and render cropped output
        overlay.annotations.add(RectShape(QPointF(120, 140), QPointF(250, 250), QColor("#ff2e55"), 4))
        cropped = overlay.render_selected_pixmap()
        self.assertEqual(cropped.width(), 320)
        self.assertEqual(cropped.height(), 240)

        # Save selection to temp file
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = str(Path(tmpdir) / "cropped_test.png")
            saved_path = overlay.save_selection(target_path=out_file)
            self.assertEqual(saved_path, out_file)
            self.assertTrue(Path(out_file).exists())
            loaded = QPixmap(out_file)
            self.assertEqual(loaded.width(), 320)
            self.assertEqual(loaded.height(), 240)

        overlay.close()

    def test_history_manager(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = HistoryManager(max_items=3)
            mgr.history_dir = Path(tmpdir)
            mgr.index_file = mgr.history_dir / "index.json"

            pix = QPixmap(120, 80)
            pix.fill(QColor("#38bdf8"))

            e1 = mgr.record(pix, action="copy")
            e2 = mgr.record(pix, action="save")
            entries = mgr.list_entries()
            self.assertEqual(len(entries), 2)
            self.assertEqual(entries[0].id, e2.id)

            mgr.delete_entry(e1.id)
            self.assertEqual(len(mgr.list_entries()), 1)

            mgr.clear_all()
            self.assertEqual(len(mgr.list_entries()), 0)


if __name__ == "__main__":
    unittest.main()
