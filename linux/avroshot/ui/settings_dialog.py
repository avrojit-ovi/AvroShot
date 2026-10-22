"""Settings Dialog for AvroShot."""

from __future__ import annotations

import shutil

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from avroshot import APP_NAME
from avroshot.config import AppSettings
from avroshot.platforms import get_platform_backend
from avroshot.ui import create_app_icon
from avroshot.ui.history_dialog import DIALOG_STYLE


class SettingsDialog(QDialog):
    """Configure save directory, default tool/color/thickness, upload provider, delay, and system hotkey."""

    def __init__(self, settings: AppSettings | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings or AppSettings.load()
        self.backend = get_platform_backend()
        self._chosen_color = QColor(self.settings.default_color)

        self.setWindowTitle(f"{APP_NAME} — Settings")
        self.setWindowIcon(create_app_icon(64))
        self.setMinimumWidth(520)
        self.setStyleSheet(
            DIALOG_STYLE
            + """
            QLineEdit, QComboBox, QSpinBox {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #475569;
                border-radius: 5px;
                padding: 5px 8px;
            }
            QCheckBox {
                color: #e2e8f0;
                spacing: 8px;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        header = QLabel(f"{APP_NAME} Preferences")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #f8fafc;")
        root.addWidget(header)

        form = QFormLayout()
        form.setSpacing(10)

        # Save directory
        dir_row = QHBoxLayout()
        self.save_dir_edit = QLineEdit(self.settings.save_directory)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_dir)
        dir_row.addWidget(self.save_dir_edit, stretch=1)
        dir_row.addWidget(browse_btn)
        form.addRow("Save Directory:", dir_row)

        # Filename pattern
        self.pattern_edit = QLineEdit(self.settings.filename_pattern)
        form.addRow("Filename Pattern:", self.pattern_edit)

        # Default tool
        self.tool_combo = QComboBox()
        for tid, label in [
            ("pen", "Freehand Pen"),
            ("arrow", "Arrow"),
            ("rect", "Rectangle"),
            ("line", "Line"),
            ("marker", "Marker / Highlighter"),
            ("text", "Text"),
            ("select", "Move / Resize Selection"),
        ]:
            self.tool_combo.addItem(label, tid)
        idx = self.tool_combo.findData(self.settings.default_tool)
        if idx >= 0:
            self.tool_combo.setCurrentIndex(idx)
        form.addRow("Default Tool:", self.tool_combo)

        # Default color & thickness
        color_row = QHBoxLayout()
        self.color_btn = QPushButton(self._chosen_color.name())
        self._update_color_btn_style()
        self.color_btn.clicked.connect(self._pick_color)
        self.thickness_spin = QSpinBox()
        self.thickness_spin.setRange(1, 20)
        self.thickness_spin.setValue(self.settings.default_thickness)
        color_row.addWidget(self.color_btn)
        color_row.addWidget(QLabel("Thickness (px):"))
        color_row.addWidget(self.thickness_spin)
        form.addRow("Default Color:", color_row)

        # Overlay dim opacity
        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(40, 220)
        self.opacity_spin.setValue(self.settings.overlay_dim_opacity)
        form.addRow("Overlay Dimming (40-220):", self.opacity_spin)

        # Delay seconds
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 30)
        self.delay_spin.setSuffix(" sec")
        self.delay_spin.setValue(self.settings.delay_seconds)
        form.addRow("Delayed Capture Timer:", self.delay_spin)

        # Upload provider
        self.upload_combo = QComboBox()
        self.upload_combo.addItem("0x0.st (Instant Shareable Link, No Key Required)", "0x0.st")
        self.upload_combo.addItem("Imgur Anonymous Upload", "imgur")
        up_idx = self.upload_combo.findData(self.settings.upload_provider)
        if up_idx >= 0:
            self.upload_combo.setCurrentIndex(up_idx)
        form.addRow("Upload Service:", self.upload_combo)

        # Global shortcut binding
        hk_row = QHBoxLayout()
        self.shortcut_edit = QLineEdit(self.settings.shortcut_key)
        apply_hk_btn = QPushButton("Bind Shortcut")
        apply_hk_btn.clicked.connect(self._bind_shortcut_now)
        hk_row.addWidget(self.shortcut_edit, stretch=1)
        hk_row.addWidget(apply_hk_btn)
        form.addRow("Global Hotkey:", hk_row)

        root.addLayout(form)

        # Checkboxes
        self.auto_copy_cb = QCheckBox("Automatically copy screenshot to clipboard when saving")
        self.auto_copy_cb.setChecked(self.settings.auto_copy_on_save)
        root.addWidget(self.auto_copy_cb)

        self.history_cb = QCheckBox("Save captures to Screenshot History")
        self.history_cb.setChecked(self.settings.save_to_history)
        root.addWidget(self.history_cb)

        self.notify_cb = QCheckBox("Show desktop notifications after Copy / Save / Upload")
        self.notify_cb.setChecked(self.settings.show_notifications)
        root.addWidget(self.notify_cb)

        # Dialog buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("PrimaryBtn")
        save_btn.clicked.connect(self._save_and_close)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        root.addLayout(btn_row)

    def _browse_dir(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, "Choose Save Directory", self.save_dir_edit.text())
        if chosen:
            self.save_dir_edit.setText(chosen)

    def _pick_color(self) -> None:
        c = QColorDialog.getColor(self._chosen_color, self, "Default Annotation Color")
        if c.isValid():
            self._chosen_color = c
            self.color_btn.setText(c.name())
            self._update_color_btn_style()

    def _update_color_btn_style(self) -> None:
        self.color_btn.setStyleSheet(
            f"background-color: {self._chosen_color.name()}; color: #ffffff; font-weight: bold;"
        )

    def _bind_shortcut_now(self) -> None:
        binding = self.shortcut_edit.text().strip() or "<Super><Shift>s"
        cmd_bin = shutil.which("avroshot") or "avroshot"
        ok, msg = self.backend.register_global_shortcut(f"{cmd_bin} --capture", binding)
        if ok:
            QMessageBox.information(self, APP_NAME, msg)
        else:
            QMessageBox.warning(self, APP_NAME, msg)

    def _save_and_close(self) -> None:
        self.settings.save_directory = self.save_dir_edit.text().strip() or self.settings.save_directory
        self.settings.filename_pattern = self.pattern_edit.text().strip() or "AvroShot_%Y-%m-%d_%H-%M-%S.png"
        self.settings.default_tool = str(self.tool_combo.currentData())
        self.settings.default_color = self._chosen_color.name()
        self.settings.default_thickness = self.thickness_spin.value()
        self.settings.overlay_dim_opacity = self.opacity_spin.value()
        self.settings.delay_seconds = self.delay_spin.value()
        self.settings.upload_provider = str(self.upload_combo.currentData())
        self.settings.shortcut_key = self.shortcut_edit.text().strip() or "<Super><Shift>s"
        self.settings.auto_copy_on_save = self.auto_copy_cb.isChecked()
        self.settings.save_to_history = self.history_cb.isChecked()
        self.settings.show_notifications = self.notify_cb.isChecked()
        self.settings.save()
        self.accept()
