"""Screenshot history manager storing recent captures and metadata."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from PyQt6.QtGui import QPixmap

from avroshot.config import get_data_dir


@dataclass
class HistoryEntry:
    id: str
    timestamp: str
    file_path: str
    width: int
    height: int
    action: str  # "copy", "save", "upload"
    share_url: str = ""


class HistoryManager:
    """Persists screenshot history images and index.json on disk."""

    def __init__(self, max_items: int = 50) -> None:
        self.max_items = max_items
        self.history_dir = get_data_dir() / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.history_dir / "index.json"

    def list_entries(self) -> list[HistoryEntry]:
        if not self.index_file.exists():
            return []
        try:
            raw = json.loads(self.index_file.read_text(encoding="utf-8"))
            entries: list[HistoryEntry] = []
            for item in raw:
                if Path(item.get("file_path", "")).exists():
                    entries.append(HistoryEntry(**item))
            return entries
        except Exception:
            return []

    def record(
        self,
        pixmap: QPixmap,
        action: str,
        saved_path: str | None = None,
        share_url: str = "",
    ) -> HistoryEntry:
        now = datetime.now()
        entry_id = now.strftime("%Y%m%d_%H%M%S_%f")
        if saved_path and Path(saved_path).exists():
            target_path = saved_path
        else:
            file_path = self.history_dir / f"shot_{entry_id}.png"
            pixmap.save(str(file_path), "PNG")
            target_path = str(file_path)

        entry = HistoryEntry(
            id=entry_id,
            timestamp=now.strftime("%Y-%m-%d %H:%M:%S"),
            file_path=target_path,
            width=pixmap.width(),
            height=pixmap.height(),
            action=action,
            share_url=share_url,
        )

        entries = self.list_entries()
        entries.insert(0, entry)

        while len(entries) > self.max_items:
            removed = entries.pop()
            try:
                p = Path(removed.file_path)
                if p.parent == self.history_dir and p.exists():
                    p.unlink()
            except OSError:
                pass

        self._save_entries(entries)
        return entry

    def delete_entry(self, entry_id: str) -> None:
        entries = self.list_entries()
        remaining: list[HistoryEntry] = []
        for item in entries:
            if item.id == entry_id:
                try:
                    p = Path(item.file_path)
                    if p.parent == self.history_dir and p.exists():
                        p.unlink()
                except OSError:
                    pass
            else:
                remaining.append(item)
        self._save_entries(remaining)

    def clear_all(self) -> None:
        for item in self.list_entries():
            try:
                p = Path(item.file_path)
                if p.parent == self.history_dir and p.exists():
                    p.unlink()
            except OSError:
                pass
        self._save_entries([])

    def _save_entries(self, entries: list[HistoryEntry]) -> None:
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.index_file.write_text(
            json.dumps([asdict(e) for e in entries], indent=2),
            encoding="utf-8",
        )
