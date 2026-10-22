"""Base platform abstraction for screen capture, clipboard, notifications, and hotkeys."""

from __future__ import annotations

from abc import ABC, abstractmethod
from PyQt6.QtGui import QPixmap


class PlatformBackend(ABC):
    """Abstract base class for OS-specific operations (Linux X11/Wayland, Windows, macOS)."""

    @abstractmethod
    def capture_fullscreen(self) -> QPixmap | None:
        """Capture the entire desktop across all monitors and return a QPixmap."""

    @abstractmethod
    def copy_to_clipboard(self, pixmap: QPixmap) -> bool:
        """Copy QPixmap to system clipboard and ensure it persists after process exit."""

    @abstractmethod
    def copy_text_to_clipboard(self, text: str) -> bool:
        """Copy text string to system clipboard and ensure it persists after process exit."""

    @abstractmethod
    def send_notification(self, title: str, message: str, icon_path: str | None = None) -> None:
        """Display a native desktop notification."""

    @abstractmethod
    def register_global_shortcut(self, command: str, binding: str = "<Super><Shift>s") -> tuple[bool, str]:
        """Configure OS global keyboard shortcut to launch AvroShot."""
