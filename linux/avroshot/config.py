"""Cross-platform configuration and paths manager for AvroShot."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def get_config_dir() -> Path:
    """Return OS-appropriate configuration directory."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "AvroShot"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "AvroShot"
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg_config) if xdg_config else (Path.home() / ".config")
    return base / "avroshot"


def get_data_dir() -> Path:
    """Return OS-appropriate data directory (used for screenshot history)."""
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "AvroShot"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "AvroShot"
    xdg_data = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg_data) if xdg_data else (Path.home() / ".local" / "share")
    return base / "avroshot"


def get_default_pictures_dir() -> Path:
    """Return default directory where screenshots are saved."""
    pictures = Path.home() / "Pictures" / "AvroShot"
    return pictures


@dataclass
class AppSettings:
    save_directory: str = field(default_factory=lambda: str(get_default_pictures_dir()))
    filename_pattern: str = "AvroShot_%Y-%m-%d_%H-%M-%S.png"
    image_format: str = "PNG"
    jpeg_quality: int = 95
    overlay_dim_opacity: int = 135  # 0-255 dark overlay alpha
    default_tool: str = "pen"       # select, pen, line, arrow, rect, marker, text
    default_color: str = "#ff2e55"  # Lightshot vibrant crimson-red
    default_thickness: int = 3
    default_font_size: int = 16
    auto_copy_on_save: bool = True
    save_to_history: bool = True
    max_history_items: int = 50
    show_notifications: bool = True
    close_after_copy: bool = True
    close_after_save: bool = True
    upload_provider: str = "0x0.st"  # "0x0.st" or "imgur"
    imgur_client_id: str = "546c25a59c58ad7"
    shortcut_key: str = "<Super><Shift>s"
    delay_seconds: int = 3

    @classmethod
    def load(cls) -> "AppSettings":
        cfg_file = get_config_dir() / "settings.json"
        if cfg_file.exists():
            try:
                data = json.loads(cfg_file.read_text(encoding="utf-8"))
                valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
                filtered: dict[str, Any] = {k: v for k, v in data.items() if k in valid_keys}
                return cls(**filtered)
            except Exception:
                return cls()
        settings = cls()
        settings.save()
        return settings

    def save(self) -> None:
        cfg_dir = get_config_dir()
        cfg_dir.mkdir(parents=True, exist_ok=True)
        cfg_file = cfg_dir / "settings.json"
        cfg_file.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
