"""Platform factory returning the right backend for Linux, Windows, or macOS."""

from __future__ import annotations

import sys

from avroshot.platforms.base import PlatformBackend

_BACKEND_INSTANCE: PlatformBackend | None = None


def get_platform_backend() -> PlatformBackend:
    global _BACKEND_INSTANCE
    if _BACKEND_INSTANCE is not None:
        return _BACKEND_INSTANCE

    if sys.platform == "win32":
        from avroshot.platforms.windows import WindowsBackend

        _BACKEND_INSTANCE = WindowsBackend()
    elif sys.platform == "darwin":
        from avroshot.platforms.macos import MacOSBackend

        _BACKEND_INSTANCE = MacOSBackend()
    else:
        from avroshot.platforms.linux import LinuxBackend

        _BACKEND_INSTANCE = LinuxBackend()

    return _BACKEND_INSTANCE
