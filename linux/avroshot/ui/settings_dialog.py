"""Settings Dialog for AvroShot."""

from __future__ import annotations

import shutil

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFocusEvent, QKeyEvent, QMouseEvent
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

DEFAULT_SHORTCUT = "<Super><Shift>s"

_MODIFIER_TOKENS = (
    (Qt.KeyboardModifier.ControlModifier, "<Control>"),
    (Qt.KeyboardModifier.AltModifier, "<Alt>"),
    (Qt.KeyboardModifier.ShiftModifier, "<Shift>"),
    (Qt.KeyboardModifier.MetaModifier, "<Super>"),
)

_KEY_NAMES = {
    Qt.Key.Key_Space: "space",
    Qt.Key.Key_Return: "Return",
    Qt.Key.Key_Enter: "Return",
    Qt.Key.Key_Tab: "Tab",
    Qt.Key.Key_Backspace: "BackSpace",
    Qt.Key.Key_Delete: "Delete",
    Qt.Key.Key_Insert: "Insert",
    Qt.Key.Key_Home: "Home",
    Qt.Key.Key_End: "End",
    Qt.Key.Key_PageUp: "Page_Up",
    Qt.Key.Key_PageDown: "Page_Down",
    Qt.Key.Key_Up: "Up",
    Qt.Key.Key_Down: "Down",
    Qt.Key.Key_Left: "Left",
    Qt.Key.Key_Right: "Right",
    Qt.Key.Key_Print: "Print",
    Qt.Key.Key_Minus: "minus",
    Qt.Key.Key_Equal: "equal",
    Qt.Key.Key_Comma: "comma",
    Qt.Key.Key_Period: "period",
    Qt.Key.Key_Slash: "slash",
    Qt.Key.Key_Semicolon: "semicolon",
    Qt.Key.Key_Apostrophe: "apostrophe",
    Qt.Key.Key_BracketLeft: "bracketleft",
    Qt.Key.Key_BracketRight: "bracketright",
    Qt.Key.Key_Backslash: "backslash",
    Qt.Key.Key_QuoteLeft: "grave",
}


def key_to_accelerator(key: int) -> str | None:
    """Translate a Qt key code into the GTK accelerator syntax gsettings accepts."""
    if int(Qt.Key.Key_A) <= key <= int(Qt.Key.Key_Z):
        return chr(key).lower()
    if int(Qt.Key.Key_0) <= key <= int(Qt.Key.Key_9):
        return chr(key)
    if int(Qt.Key.Key_F1) <= key <= int(Qt.Key.Key_F35):
        return f"F{key - int(Qt.Key.Key_F1) + 1}"
    return _KEY_NAMES.get(Qt.Key(key))


class ShortcutRecorder(QLineEdit):
    """Read-only field that records the next key combination pressed in it.

    Click the field, press e.g. Super+Shift+S, and the field shows
    ``<Super><Shift>s`` - the exact syntax gsettings needs - instead of
    asking the user to type that string by hand.
    """

    def __init__(self, binding: str = "", parent: QWidget | None = None) -> None:
        super().__init__(binding, parent)
        self.setReadOnly(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click here and press the shortcut you want (Esc cancels)")
        self.setPlaceholderText("Click, then press a key combination")
        self._recording = False
        self._previous = binding

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802 (Qt API)
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        self._start_recording()
        event.accept()

    def focusInEvent(self, event: QFocusEvent) -> None:  # noqa: N802 (Qt API)
        super().focusInEvent(event)
        if event.reason() in (Qt.FocusReason.MouseFocusReason, Qt.FocusReason.TabFocusReason):
            self._start_recording()

    def focusOutEvent(self, event: QFocusEvent) -> None:  # noqa: N802 (Qt API)
        self._finish_recording()
        super().focusOutEvent(event)

    def _start_recording(self) -> None:
        if self._recording:
            return
        self._previous = self.text().strip()
        self._recording = True
        self.setText("Press keys…")
        self.selectAll()

    def _finish_recording(self) -> None:
        if not self._recording:
            return
        self._recording = False
        if not self.text().strip() or self.text().startswith("Press"):
            self.setText(self._previous)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802 (Qt API)
        if not self._recording:
            self._start_recording()
            return
        key = event.key()
        if key == int(Qt.Key.Key_Escape):
            self._recording = False
            self.setText(self._previous)
            return
        if key in (
            int(Qt.Key.Key_Control),
            int(Qt.Key.Key_Shift),
            int(Qt.Key.Key_Alt),
            int(Qt.Key.Key_Meta),
            int(Qt.Key.Key_Super_L),
            int(Qt.Key.Key_Super_R),
        ):
            return  # wait for the non-modifier key

        accelerator = key_to_accelerator(key)
        if accelerator is None:
            return
        modifiers = event.modifiers()
        tokens = "".join(token for flag, token in _MODIFIER_TOKENS if modifiers & flag)
        self._recording = False
        self.setText(tokens + accelerator)
        self.selectAll()


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

        # Global shortcut binding - click the field and press the combo
        self.shortcut_edit = ShortcutRecorder(self.settings.shortcut_key or DEFAULT_SHORTCUT)
        self._original_shortcut = self.shortcut_edit.text().strip()
        apply_hk_btn = QPushButton("Apply Shortcut")
        apply_hk_btn.clicked.connect(self._bind_shortcut_now)
        hk_row = QHBoxLayout()
        hk_row.addWidget(self.shortcut_edit, stretch=1)
        hk_row.addWidget(apply_hk_btn)
        form.addRow("Global Hotkey:", hk_row)
        form.addRow(
            "",
            QLabel("Click the box above and press the combination, e.g. Super+Shift+S."),
        )

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

    def _register_shortcut(self, binding: str, notify: bool = True) -> bool:
        """Bind the hotkey system-wide; returns True when the binding was applied."""
        cmd_bin = shutil.which("avroshot") or "avroshot"
        ok, msg = self.backend.register_global_shortcut(f"{cmd_bin} --capture", binding)
        if notify:
            if ok:
                QMessageBox.information(
                    self,
                    APP_NAME,
                    f"Hotkey active: {binding}\n\nPress it anywhere to take a screenshot.",
                )
            else:
                QMessageBox.warning(self, APP_NAME, msg)
        return ok

    def _bind_shortcut_now(self) -> None:
        binding = self.shortcut_edit.text().strip() or DEFAULT_SHORTCUT
        if self._register_shortcut(binding):
            self._original_shortcut = binding

    def _save_and_close(self) -> None:
        self.settings.save_directory = self.save_dir_edit.text().strip() or self.settings.save_directory
        self.settings.filename_pattern = self.pattern_edit.text().strip() or "AvroShot_%Y-%m-%d_%H-%M-%S.png"
        self.settings.default_tool = str(self.tool_combo.currentData())
        self.settings.default_color = self._chosen_color.name()
        self.settings.default_thickness = self.thickness_spin.value()
        self.settings.overlay_dim_opacity = self.opacity_spin.value()
        self.settings.delay_seconds = self.delay_spin.value()
        self.settings.upload_provider = str(self.upload_combo.currentData())
        self.settings.shortcut_key = self.shortcut_edit.text().strip() or DEFAULT_SHORTCUT
        self.settings.auto_copy_on_save = self.auto_copy_cb.isChecked()
        self.settings.save_to_history = self.history_cb.isChecked()
        self.settings.show_notifications = self.notify_cb.isChecked()
        self.settings.save()

        # Saving a changed hotkey should actually bind it - otherwise the new
        # combination would be stored but never registered with the desktop.
        if self.settings.shortcut_key != self._original_shortcut:
            self._register_shortcut(self.settings.shortcut_key)

        self.accept()
