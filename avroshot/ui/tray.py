"""System Tray controller and application coordinator for AvroShot."""

from __future__ import annotations

from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon

from avroshot import APP_NAME, DESCRIPTION, VERSION
from avroshot.config import AppSettings
from avroshot.history import HistoryManager
from avroshot.platforms import get_platform_backend
from avroshot.ui import create_app_icon
from avroshot.ui.history_dialog import HistoryDialog
from avroshot.ui.overlay import CaptureOverlay
from avroshot.ui.settings_dialog import SettingsDialog


class AvroShotController(QObject):
    """Coordinates instant capture, delayed capture, tray icon menu, history, and settings."""

    def __init__(self, exit_on_capture_done: bool = False) -> None:
        super().__init__()
        self.settings = AppSettings.load()
        self.history_manager = HistoryManager(self.settings.max_history_items)
        self.backend = get_platform_backend()
        self.exit_on_capture_done = exit_on_capture_done

        self.overlay: CaptureOverlay | None = None
        self.history_dialog: HistoryDialog | None = None
        self.settings_dialog: SettingsDialog | None = None
        self.tray_icon: QSystemTrayIcon | None = None

    def init_tray(self) -> bool:
        """Initialize system tray icon with menu for instant/delayed capture, history, and settings."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return False

        QApplication.setQuitOnLastWindowClosed(False)
        self.tray_icon = QSystemTrayIcon(create_app_icon(64), self)
        self.tray_icon.setToolTip(f"{APP_NAME} v{VERSION} — Click to capture screen")

        menu = QMenu()
        capture_now_act = QAction("Capture Screen Now", menu)
        capture_now_act.triggered.connect(lambda: self.start_capture(delay_seconds=0))
        menu.addAction(capture_now_act)

        delay_act = QAction(f"Capture with {self.settings.delay_seconds}s Delay", menu)
        delay_act.triggered.connect(lambda: self.start_capture(delay_seconds=self.settings.delay_seconds))
        menu.addAction(delay_act)

        menu.addSeparator()

        history_act = QAction("Screenshot History...", menu)
        history_act.triggered.connect(self.open_history)
        menu.addAction(history_act)

        settings_act = QAction("Settings...", menu)
        settings_act.triggered.connect(self.open_settings)
        menu.addAction(settings_act)

        about_act = QAction(f"About {APP_NAME}", menu)
        about_act.triggered.connect(self.show_about)
        menu.addAction(about_act)

        menu.addSeparator()

        quit_act = QAction("Quit", menu)
        quit_act.triggered.connect(QApplication.instance().quit)  # type: ignore[arg-type]
        menu.addAction(quit_act)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()
        return True

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.start_capture(delay_seconds=0)

    def start_capture(self, delay_seconds: int = 0) -> None:
        if delay_seconds > 0:
            if self.settings.show_notifications:
                self.backend.send_notification(
                    APP_NAME,
                    f"Taking screenshot in {delay_seconds} seconds...",
                )
            QTimer.singleShot(int(delay_seconds * 1000), self._execute_capture)
        else:
            # Brief 80ms delay if launched from tray menu so menu closes cleanly
            if self.tray_icon is not None and not self.exit_on_capture_done:
                QTimer.singleShot(120, self._execute_capture)
            else:
                self._execute_capture()

    def _execute_capture(self) -> None:
        if self.overlay is not None:
            try:
                self.overlay.close()
            except Exception:
                pass
            self.overlay = None

        screenshot = self.backend.capture_fullscreen()
        if screenshot is None or screenshot.isNull():
            msg = "Unable to capture screen. Please check display permissions."
            self.backend.send_notification(f"{APP_NAME} Error", msg)
            if self.exit_on_capture_done:
                QApplication.instance().quit()  # type: ignore[union-attr]
            return

        self.settings = AppSettings.load()
        self.overlay = CaptureOverlay(
            screenshot=screenshot,
            settings=self.settings,
            history_manager=self.history_manager,
        )
        self.overlay.capture_completed.connect(self._on_overlay_finished)
        self.overlay.show_fullscreen_overlay()

    def _on_overlay_finished(self, _status: str) -> None:
        self.overlay = None
        if self.exit_on_capture_done:
            # Give clipboard/notification subprocesses 250ms to flush before exiting
            QTimer.singleShot(250, QApplication.instance().quit)  # type: ignore[arg-type]

    def open_history(self) -> None:
        if self.history_dialog is not None and self.history_dialog.isVisible():
            self.history_dialog.refresh_entries()
            self.history_dialog.raise_()
            self.history_dialog.activateWindow()
            return
        self.history_dialog = HistoryDialog(
            history_manager=self.history_manager,
            settings=self.settings,
        )
        self.history_dialog.show()
        self.history_dialog.raise_()
        self.history_dialog.activateWindow()

    def open_settings(self) -> None:
        self.settings = AppSettings.load()
        dlg = SettingsDialog(settings=self.settings)
        if dlg.exec():
            self.settings = AppSettings.load()

    def show_about(self) -> None:
        QMessageBox.about(
            None,
            f"About {APP_NAME}",
            f"<h3>{APP_NAME} v{VERSION}</h3>"
            f"<p>{DESCRIPTION}</p>"
            f"<p><b>Shortcuts during capture:</b><br>"
            f"• Drag mouse: Select region &amp; resize via 8 handles<br>"
            f"• P / L / A / R / M / T / V: Pen, Line, Arrow, Rectangle, Marker, Text, Move<br>"
            f"• Ctrl+Z / Ctrl+Y: Undo / Redo<br>"
            f"• Ctrl+C or Enter: Copy to Clipboard<br>"
            f"• Ctrl+S: Save to Disk<br>"
            f"• Ctrl+U: Upload &amp; Copy Shareable Link<br>"
            f"• Esc: Cancel</p>",
        )
