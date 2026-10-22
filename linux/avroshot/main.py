"""CLI entrypoint for AvroShot (`avroshot`)."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from avroshot import APP_ID, APP_NAME, DESCRIPTION, VERSION
from avroshot.config import AppSettings
from avroshot.history import HistoryManager
from avroshot.platforms import get_platform_backend
from avroshot.ui import create_app_icon
from avroshot.ui.tray import AvroShotController


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="avroshot",
        description=f"{APP_NAME} v{VERSION} — {DESCRIPTION}",
    )
    parser.add_argument(
        "-c",
        "--capture",
        action="store_true",
        help="Capture the screen immediately and open the Lightshot-style annotation overlay (default action).",
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=int,
        default=0,
        metavar="SECONDS",
        help="Wait SECONDS before capturing the screen (e.g., --delay 3).",
    )
    parser.add_argument(
        "-t",
        "--tray",
        action="store_true",
        help="Run AvroShot in the system tray.",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Open the Screenshot History viewer.",
    )
    parser.add_argument(
        "--settings",
        action="store_true",
        help="Open the AvroShot Settings dialog.",
    )
    parser.add_argument(
        "--fullscreen-save",
        metavar="PATH",
        help="Capture full screen non-interactively and save directly to PATH.",
    )
    parser.add_argument(
        "--fullscreen-copy",
        action="store_true",
        help="Capture full screen non-interactively and copy directly to clipboard.",
    )
    parser.add_argument(
        "--register-shortcut",
        nargs="?",
        const="<Super><Shift>s",
        metavar="BINDING",
        help="Register global keyboard shortcut on Ubuntu/GNOME (default: <Super><Shift>s).",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{APP_NAME} {VERSION}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    app = QApplication(sys.argv if argv is None else [sys.argv[0], *argv])
    app.setApplicationName(APP_NAME)
    app.setDesktopFileName(APP_ID)
    app.setApplicationVersion(VERSION)
    app.setWindowIcon(create_app_icon(64))

    backend = get_platform_backend()
    settings = AppSettings.load()

    if args.register_shortcut:
        import shutil

        cmd_bin = shutil.which("avroshot") or "avroshot"
        ok, msg = backend.register_global_shortcut(f"{cmd_bin} --capture", args.register_shortcut)
        print(msg)
        return 0 if ok else 1

    if args.fullscreen_save:
        pix = backend.capture_fullscreen()
        if pix is None or pix.isNull():
            print("Error: Failed to capture screen.", file=sys.stderr)
            return 1
        out_path = Path(args.fullscreen_save).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if not pix.save(str(out_path), "PNG"):
            print(f"Error: Could not save to {out_path}", file=sys.stderr)
            return 1
        if settings.save_to_history:
            HistoryManager(settings.max_history_items).record(pix, action="save", saved_path=str(out_path))
        print(f"Saved fullscreen screenshot ({pix.width()}x{pix.height()}) to {out_path}")
        return 0

    if args.fullscreen_copy:
        pix = backend.capture_fullscreen()
        if pix is None or pix.isNull():
            print("Error: Failed to capture screen.", file=sys.stderr)
            return 1
        backend.copy_to_clipboard(pix)
        if settings.save_to_history:
            HistoryManager(settings.max_history_items).record(pix, action="copy")
        print(f"Copied fullscreen screenshot ({pix.width()}x{pix.height()}) to clipboard")
        return 0

    if args.history:
        ctrl = AvroShotController(exit_on_capture_done=False)
        ctrl.open_history()
        return app.exec()

    if args.settings:
        ctrl = AvroShotController(exit_on_capture_done=False)
        ctrl.open_settings()
        return 0

    if args.tray:
        ctrl = AvroShotController(exit_on_capture_done=False)
        if not ctrl.init_tray():
            print("Warning: System tray not available; opening capture overlay instead.", file=sys.stderr)
            ctrl.exit_on_capture_done = True
            ctrl.start_capture(delay_seconds=args.delay)
        return app.exec()

    # Default or --capture: launch interactive Lightshot overlay
    ctrl = AvroShotController(exit_on_capture_done=True)
    ctrl.start_capture(delay_seconds=max(0, args.delay))
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
