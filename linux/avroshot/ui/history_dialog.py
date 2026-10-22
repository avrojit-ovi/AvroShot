"""Screenshot History Viewer dialog for AvroShot."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from avroshot import APP_NAME
from avroshot.config import AppSettings
from avroshot.history import HistoryEntry, HistoryManager
from avroshot.platforms import get_platform_backend
from avroshot.ui import create_app_icon
from avroshot.uploader import UploadResult, UploadWorker


DIALOG_STYLE = """
QDialog {
    background-color: #0f172a;
    color: #f1f5f9;
}
QListWidget {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 6px;
    color: #f8fafc;
}
QListWidget::item {
    padding: 8px;
    border-radius: 6px;
    margin-bottom: 4px;
}
QListWidget::item:selected {
    background-color: #e11d48;
    color: #ffffff;
}
QLabel {
    color: #e2e8f0;
}
QPushButton {
    background-color: #334155;
    color: #f8fafc;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #475569;
}
QPushButton#PrimaryBtn {
    background-color: #e11d48;
    border-color: #fb7185;
    color: #ffffff;
}
QPushButton#PrimaryBtn:hover {
    background-color: #f43f5e;
}
"""


class HistoryDialog(QDialog):
    """Browse, preview, copy, upload, or delete past screenshots."""

    def __init__(
        self,
        history_manager: HistoryManager | None = None,
        settings: AppSettings | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.settings = settings or AppSettings.load()
        self.history_manager = history_manager or HistoryManager(self.settings.max_history_items)
        self.backend = get_platform_backend()
        self._upload_worker: UploadWorker | None = None

        self.setWindowTitle(f"{APP_NAME} — Screenshot History")
        self.setWindowIcon(create_app_icon(64))
        self.resize(860, 540)
        self.setStyleSheet(DIALOG_STYLE)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # Left column: list of history entries
        left_col = QVBoxLayout()
        title_lbl = QLabel("Recent Captures")
        title_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #f8fafc;")
        left_col.addWidget(title_lbl)

        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(72, 48))
        self.list_widget.currentItemChanged.connect(self._on_selection_changed)
        left_col.addWidget(self.list_widget, stretch=1)

        clear_btn = QPushButton("Clear All History")
        clear_btn.clicked.connect(self._clear_all)
        left_col.addWidget(clear_btn)
        main_layout.addLayout(left_col, stretch=2)

        # Right column: large preview + metadata + action buttons
        right_col = QVBoxLayout()
        self.preview_label = QLabel("Select a screenshot to preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(440, 320)
        self.preview_label.setStyleSheet(
            "background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 8px;"
        )
        right_col.addWidget(self.preview_label, stretch=1)

        self.meta_label = QLabel("")
        self.meta_label.setWordWrap(True)
        self.meta_label.setStyleSheet("font-size: 12px; color: #94a3b8; padding: 4px 0;")
        right_col.addWidget(self.meta_label)

        btn_row = QHBoxLayout()
        self.copy_img_btn = QPushButton("Copy Image")
        self.copy_img_btn.setObjectName("PrimaryBtn")
        self.copy_img_btn.clicked.connect(self._copy_selected_image)

        self.save_as_btn = QPushButton("Save As...")
        self.save_as_btn.clicked.connect(self._save_selected_as)

        self.upload_btn = QPushButton("Upload / Copy Link")
        self.upload_btn.clicked.connect(self._upload_selected)

        self.open_folder_btn = QPushButton("Open Folder")
        self.open_folder_btn.clicked.connect(self._open_containing_folder)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._delete_selected)

        for b in (
            self.copy_img_btn,
            self.save_as_btn,
            self.upload_btn,
            self.open_folder_btn,
            self.delete_btn,
        ):
            btn_row.addWidget(b)

        right_col.addLayout(btn_row)
        main_layout.addLayout(right_col, stretch=3)

        self.refresh_entries()

    def refresh_entries(self) -> None:
        self.list_widget.clear()
        entries = self.history_manager.list_entries()
        for entry in entries:
            pix = QPixmap(entry.file_path)
            icon = QIcon(
                pix.scaled(
                    72,
                    48,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            caption = f"{entry.timestamp}\n{entry.width}×{entry.height}  •  {entry.action.upper()}"
            if entry.share_url:
                caption += "  🔗"
            item = QListWidgetItem(icon, caption)
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.list_widget.addItem(item)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
        else:
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("No screenshots in history yet.")
            self.meta_label.setText("")
            self._set_actions_enabled(False)

    def _current_entry(self) -> HistoryEntry | None:
        item = self.list_widget.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def _set_actions_enabled(self, enabled: bool) -> None:
        for b in (
            self.copy_img_btn,
            self.save_as_btn,
            self.upload_btn,
            self.open_folder_btn,
            self.delete_btn,
        ):
            b.setEnabled(enabled)

    def _on_selection_changed(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        if current is None:
            self._set_actions_enabled(False)
            return
        entry: HistoryEntry = current.data(Qt.ItemDataRole.UserRole)
        self._set_actions_enabled(True)
        pix = QPixmap(entry.file_path)
        if not pix.isNull():
            scaled = pix.scaled(
                self.preview_label.size() - QSize(20, 20),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.preview_label.setPixmap(scaled)
        info = f"File: {entry.file_path}\nSize: {entry.width}×{entry.height} px   |   Captured: {entry.timestamp}"
        if entry.share_url:
            info += f"\nShare URL: {entry.share_url}"
        self.meta_label.setText(info)

    def _copy_selected_image(self) -> None:
        entry = self._current_entry()
        if not entry:
            return
        pix = QPixmap(entry.file_path)
        if not pix.isNull():
            self.backend.copy_to_clipboard(pix)
            self.backend.send_notification(APP_NAME, "Copied screenshot from history to clipboard")

    def _save_selected_as(self) -> None:
        entry = self._current_entry()
        if not entry:
            return
        pix = QPixmap(entry.file_path)
        if pix.isNull():
            return
        default_dir = str(Path(self.settings.save_directory) / Path(entry.file_path).name)
        dest, _ = QFileDialog.getSaveFileName(
            self,
            "Save Screenshot As",
            default_dir,
            "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;All Files (*)",
        )
        if dest:
            pix.save(dest)
            self.backend.send_notification(APP_NAME, f"Saved to {dest}")

    def _upload_selected(self) -> None:
        entry = self._current_entry()
        if not entry:
            return
        if entry.share_url:
            self.backend.copy_text_to_clipboard(entry.share_url)
            self.backend.send_notification(APP_NAME, f"Copied existing link:\n{entry.share_url}")
            return

        pix = QPixmap(entry.file_path)
        if pix.isNull():
            return
        self.upload_btn.setEnabled(False)
        self.upload_btn.setText("Uploading...")
        self._upload_worker = UploadWorker(
            pix,
            provider=self.settings.upload_provider,
            imgur_client_id=self.settings.imgur_client_id,
            parent=self,
        )
        self._upload_worker.finished_upload.connect(self._on_upload_done)
        self._upload_worker.start()

    def _on_upload_done(self, res: UploadResult) -> None:
        self.upload_btn.setEnabled(True)
        self.upload_btn.setText("Upload / Copy Link")
        if res.success and res.url:
            self.backend.copy_text_to_clipboard(res.url)
            self.backend.send_notification(APP_NAME, f"Uploaded! Link copied:\n{res.url}")
            entry = self._current_entry()
            if entry:
                entry.share_url = res.url
                self.meta_label.setText(self.meta_label.text() + f"\nShare URL: {res.url}")
        else:
            QMessageBox.warning(self, APP_NAME, f"Upload failed:\n{res.error}")

    def _open_containing_folder(self) -> None:
        entry = self._current_entry()
        if not entry:
            return
        folder = str(Path(entry.file_path).parent)
        if sys.platform == "win32":
            os.startfile(folder)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _delete_selected(self) -> None:
        entry = self._current_entry()
        if not entry:
            return
        self.history_manager.delete_entry(entry.id)
        self.refresh_entries()

    def _clear_all(self) -> None:
        ans = QMessageBox.question(
            self,
            f"Clear {APP_NAME} History",
            "Are you sure you want to delete all history entries?",
        )
        if ans == QMessageBox.StandardButton.Yes:
            self.history_manager.clear_all()
            self.refresh_entries()
