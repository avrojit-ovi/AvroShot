#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="/home/chief/AvroShot"
export PYTHONPATH="${REPO_DIR}:${PYTHONPATH:-}"
cd "${REPO_DIR}"
exec python3 - "${@+"$@"}" <<'PY'
import os
import sys

REPO_DIR = "/home/chief/AvroShot"
if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

from avroshot import annotations
from avroshot.config import AppSettings
from avroshot.annotations import AnnotationHistory, PenShape
from avroshot.history import HistoryManager
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor

def check(desc, ok):
    print(("  PASS" if ok else "  FAIL") + ": " + desc)

print("=== AvroShot Test Suite ===\n")

print("--- Module import tests ---")
settings = AppSettings.load()
check("AppSettings loads", isinstance(settings, AppSettings))
check("image_format is PNG", getattr(settings, "image_format", None) == "PNG")
check("save_directory resolves", bool(settings.save_directory))

history_obj = AnnotationHistory()
check("AnnotationHistory starts empty", len(history_obj.shapes) == 0)
pen = PenShape(start_pt=QPointF(0, 0), color=QColor("red"), thickness=2)
history_obj.add(pen)
check("AnnotationHistory.add pushes shape", len(history_obj.shapes) == 1)
check("AnnotationHistory.undo returns True", history_obj.undo() is True)
check("AnnotationHistory.undo empties stack", len(history_obj.shapes) == 0)
check("AnnotationHistory.redo returns True", history_obj.redo() is True)
check("AnnotationHistory.redo restores shape", len(history_obj.shapes) == 1)

history_dir = os.path.join(os.path.expanduser("~/.local/share/avroshot"), "history")
history = HistoryManager()
check("HistoryManager loads without error", history.list_entries() is not None)
print()

print("--- Clipboard helper smoke (X11 only) ---")
os.environ["QT_QPA_PLATFORM"] = "xcb"
from avroshot.platforms.linux import LinuxBackend

p = LinuxBackend()
try:
    ok = bool(getattr(p, "copy_to_clipboard", None)) and bool(getattr(p, "copy_text_to_clipboard", None))
    print("LinuxBackend has clipboard methods:", ok)
except Exception as e:
    print("skipped / failed:", repr(e))
print()

print("--- Smoke test: built CLI entry point ---")
from avroshot.main import main
if os.path.exists(os.path.expanduser("~/.local/bin/avroshot")):
    print("  PASS: avroshot on PATH")
    main(["--help"])
else:
    print("  WARN: avroshot not on PATH")
print()

print("--- Installation artifacts ---")
print("  avroshot binary:", os.path.expanduser("~/.local/bin/avroshot") if os.path.exists(os.path.expanduser("~/.local/bin/avroshot")) else "not on PATH")
print("  desktop file:", os.path.expanduser("~/.local/share/applications/io.github.avroshot.AvroShot.desktop") if os.path.exists(os.path.expanduser("~/.local/share/applications/io.github.avroshot.AvroShot.desktop")) else "missing")
print("  icon svg:", os.path.expanduser("~/.local/share/icons/hicolor/scalable/apps/avroshot.svg") if os.path.exists(os.path.expanduser("~/.local/share/icons/hicolor/scalable/apps/avroshot.svg")) else "missing")
print("  .deb artifact:", os.path.join(REPO_DIR, "dist/avroshot_1.0.0_all.deb") if os.path.exists(os.path.join(REPO_DIR, "dist/avroshot_1.0.0_all.deb")) else "none")
print()

print("=== All checks complete ===")
PY
