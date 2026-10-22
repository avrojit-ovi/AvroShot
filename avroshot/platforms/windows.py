"""Windows platform backend for AvroShot (future-ready cross-platform support)."""

from __future__ import annotations

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QGuiApplication, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication

from avroshot.platforms.base import PlatformBackend


class WindowsBackend(PlatformBackend):
    """Handles screen capture, clipboard, notifications, and shortcuts on Windows 10/11."""

    def capture_fullscreen(self) -> QPixmap | None:
        screens = QGuiApplication.screens()
        if not screens:
            return None
        if len(screens) == 1:
            return screens[0].grabWindow(0)

        virtual_rect = QRect()
        for scr in screens:
            virtual_rect = virtual_rect.united(scr.geometry())

        canvas = QPixmap(virtual_rect.size())
        canvas.fill(Qt.GlobalColor.black)
        painter = QPainter(canvas)
        for scr in screens:
            geom = scr.geometry()
            shot = scr.grabWindow(0)
            offset = geom.topLeft() - virtual_rect.topLeft()
            painter.drawPixmap(offset, shot)
        painter.end()
        return canvas

    def copy_to_clipboard(self, pixmap: QPixmap) -> bool:
        cb = QGuiApplication.clipboard()
        if cb is not None:
            cb.setPixmap(pixmap)
            QApplication.processEvents()
            return True
        return False

    def copy_text_to_clipboard(self, text: str) -> bool:
        cb = QGuiApplication.clipboard()
        if cb is not None:
            cb.setText(text)
            QApplication.processEvents()
            return True
        return False

    def send_notification(self, title: str, message: str, icon_path: str | None = None) -> None:
        # System tray message is used by tray controller when running on Windows
        pass

    def register_global_shortcut(self, command: str, binding: str = "<Super><Shift>s") -> tuple[bool, str]:
        return True, "On Windows, AvroShot tray registers global hotkeys via Win32 RegisterHotKey."
