"""Linux (Ubuntu Wayland & X11) platform backend for AvroShot."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import urllib.parse
import uuid
from pathlib import Path

from PyQt6.QtCore import QBuffer, QByteArray, QIODevice, QPoint, QRect, Qt
from PyQt6.QtGui import QGuiApplication, QImage, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication

from avroshot import APP_ID, APP_NAME
from avroshot.platforms.base import PlatformBackend


def is_wayland_session() -> bool:
    return (
        os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
        or bool(os.environ.get("WAYLAND_DISPLAY"))
    )


def ensure_desktop_and_portal_permissions() -> None:
    """Ensure .desktop file exists and xdg-desktop-portal PermissionStore grants silent screenshot access."""
    try:
        apps_dir = Path.home() / ".local" / "share" / "applications"
        apps_dir.mkdir(parents=True, exist_ok=True)
        desktop_file = apps_dir / f"{APP_ID}.desktop"
        if not desktop_file.exists():
            exec_cmd = shutil.which("avroshot") or "avroshot"
            desktop_file.write_text(
                f"[Desktop Entry]\n"
                f"Type=Application\n"
                f"Name={APP_NAME}\n"
                f"Comment=Lightshot-style Screenshot & Annotation Tool\n"
                f"Exec={exec_cmd} --capture\n"
                f"Icon=avroshot\n"
                f"Terminal=false\n"
                f"Categories=Utility;Graphics;2DGraphics;Photography;\n"
                f"StartupNotify=false\n",
                encoding="utf-8",
            )
    except Exception:
        pass

    try:
        import dbus

        bus = dbus.SessionBus()
        perm_obj = bus.get_object(
            "org.freedesktop.impl.portal.PermissionStore",
            "/org/freedesktop/impl/portal/PermissionStore",
        )
        perm_iface = dbus.Interface(
            perm_obj, "org.freedesktop.impl.portal.PermissionStore"
        )
        for app_key in ["", APP_ID, "avroshot"]:
            perm_iface.SetPermission("screenshot", True, "screenshot", app_key, ["yes"])
    except Exception:
        pass


class LinuxBackend(PlatformBackend):
    """Handles screen capture, clipboard persistence, notifications, and shortcuts on Linux (Wayland & X11)."""

    def __init__(self) -> None:
        ensure_desktop_and_portal_permissions()

    def capture_fullscreen(self) -> QPixmap | None:
        if is_wayland_session():
            pix = self._capture_wayland_portal()
            if pix is not None and not pix.isNull():
                return pix
            pix = self._capture_wayland_cli()
            if pix is not None and not pix.isNull():
                return pix
            pix = self._capture_gnome_dbus()
            if pix is not None and not pix.isNull():
                return pix

        # X11 or fallback multi-monitor stitch via QScreen.grabWindow(0)
        pix = self._capture_qt_screens()
        if pix is not None and not pix.isNull() and not self._is_all_black(pix):
            return pix

        # Final fallback: try portal even on X11 if grabWindow failed
        pix = self._capture_wayland_portal()
        if pix is not None and not pix.isNull():
            return pix

        return pix

    def _is_all_black(self, pixmap: QPixmap) -> bool:
        """Detect Xwayland root-window all-black captures on Wayland."""
        img = pixmap.toImage()
        if img.isNull() or img.width() == 0 or img.height() == 0:
            return True
        step_x = max(1, img.width() // 20)
        step_y = max(1, img.height() // 20)
        unique_pixels = set()
        for x in range(0, img.width(), step_x):
            for y in range(0, img.height(), step_y):
                unique_pixels.add(img.pixel(x, y))
                if len(unique_pixels) > 1:
                    return False
        return len(unique_pixels) <= 1 and (next(iter(unique_pixels), 0) & 0x00FFFFFF) == 0

    def _capture_wayland_portal(self) -> QPixmap | None:
        """Capture full screen silently via org.freedesktop.portal.Screenshot with Gio.Application ID."""
        try:
            import gi

            gi.require_version("Gio", "2.0")
            from gi.repository import Gio, GLib

            app = Gio.Application(
                application_id=APP_ID,
                flags=Gio.ApplicationFlags.NON_UNIQUE,
            )
            app.register(None)
            conn = app.get_dbus_connection()
            if conn is None:
                return None

            loop = GLib.MainLoop()
            captured_path: list[str] = []

            def on_portal_response(
                _connection,
                _sender_name,
                _object_path,
                _interface_name,
                _signal_name,
                parameters,
            ):
                try:
                    resp, results = parameters.unpack()
                    if resp == 0 and "uri" in results:
                        uri = str(results["uri"])
                        file_path = urllib.parse.unquote(urllib.parse.urlparse(uri).path)
                        if os.path.exists(file_path):
                            captured_path.append(file_path)
                except Exception:
                    pass
                finally:
                    if loop.is_running():
                        loop.quit()

            sub_id = conn.signal_subscribe(
                "org.freedesktop.portal.Desktop",
                "org.freedesktop.portal.Request",
                "Response",
                None,
                None,
                Gio.DBusSignalFlags.NONE,
                on_portal_response,
            )

            token = f"avro_{uuid.uuid4().hex[:10]}"
            try:
                conn.call_sync(
                    "org.freedesktop.portal.Desktop",
                    "/org/freedesktop/portal/desktop",
                    "org.freedesktop.portal.Screenshot",
                    "Screenshot",
                    GLib.Variant(
                        "(sa{sv})",
                        (
                            "",
                            {
                                "interactive": GLib.Variant("b", False),
                                "handle_token": GLib.Variant("s", token),
                            },
                        ),
                    ),
                    GLib.VariantType("(o)"),
                    Gio.DBusCallFlags.NONE,
                    5000,
                    None,
                )
                timeout_id = GLib.timeout_add(4500, lambda: (loop.quit() if loop.is_running() else None) or False)
                loop.run()
                GLib.source_remove(timeout_id)
            finally:
                conn.signal_unsubscribe(sub_id)

            if captured_path:
                img_file = captured_path[0]
                img = QImage(img_file)
                try:
                    os.remove(img_file)
                except OSError:
                    pass
                if not img.isNull():
                    return QPixmap.fromImage(img)
        except Exception:
            pass
        return None

    def _capture_gnome_dbus(self) -> QPixmap | None:
        """Fallback capture via org.gnome.Shell.Screenshot if permitted."""
        try:
            import dbus

            bus = dbus.SessionBus()
            obj = bus.get_object("org.gnome.Shell.Screenshot", "/org/gnome/Shell/Screenshot")
            iface = dbus.Interface(obj, "org.gnome.Shell.Screenshot")
            fd, tmp_path = tempfile.mkstemp(prefix="avroshot_", suffix=".png")
            os.close(fd)
            success, used_file = iface.Screenshot(False, False, tmp_path)
            target = str(used_file) if used_file else tmp_path
            if success and os.path.exists(target):
                img = QImage(target)
                try:
                    os.remove(target)
                except OSError:
                    pass
                if not img.isNull():
                    return QPixmap.fromImage(img)
        except Exception:
            pass
        return None

    def _capture_wayland_cli(self) -> QPixmap | None:
        """Fallback CLI tools (grim for wlroots/Sway/Hyprland, spectacle, gnome-screenshot, scrot)."""
        fd, tmp_path = tempfile.mkstemp(prefix="avroshot_", suffix=".png")
        os.close(fd)
        commands = []
        if shutil.which("grim"):
            commands.append(["grim", tmp_path])
        if shutil.which("gnome-screenshot"):
            commands.append(["gnome-screenshot", "-f", tmp_path])
        if shutil.which("spectacle"):
            commands.append(["spectacle", "-b", "-n", "-f", "-o", tmp_path])
        if shutil.which("scrot"):
            commands.append(["scrot", "-o", tmp_path])

        for cmd in commands:
            try:
                res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=4)
                if res.returncode == 0 and os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
                    img = QImage(tmp_path)
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
                    if not img.isNull():
                        return QPixmap.fromImage(img)
            except Exception:
                continue
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass
        return None

    def _capture_qt_screens(self) -> QPixmap | None:
        """Capture all monitors via QScreen.grabWindow(0) and stitch onto a virtual desktop canvas."""
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
        """Copy image to clipboard using QClipboard + wl-copy/xclip if available so it persists after exit."""
        ok = False
        try:
            cb = QGuiApplication.clipboard()
            if cb is not None:
                cb.setPixmap(pixmap)
                QApplication.processEvents()
                ok = True
        except Exception:
            pass

        # Encode PNG bytes for external clipboard persistence tools
        ba = QByteArray()
        buf = QBuffer(ba)
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buf, "PNG")
        png_bytes = bytes(ba)

        if is_wayland_session() and shutil.which("wl-copy"):
            try:
                proc = subprocess.Popen(
                    ["wl-copy", "--type", "image/png"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                proc.communicate(input=png_bytes, timeout=2)
                ok = True
            except Exception:
                pass
        elif shutil.which("xclip"):
            try:
                proc = subprocess.Popen(
                    ["xclip", "-selection", "clipboard", "-t", "image/png", "-i"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                proc.communicate(input=png_bytes, timeout=2)
                ok = True
            except Exception:
                pass

        return ok

    def copy_text_to_clipboard(self, text: str) -> bool:
        ok = False
        try:
            cb = QGuiApplication.clipboard()
            if cb is not None:
                cb.setText(text)
                QApplication.processEvents()
                ok = True
        except Exception:
            pass

        if is_wayland_session() and shutil.which("wl-copy"):
            try:
                proc = subprocess.Popen(
                    ["wl-copy"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                proc.communicate(input=text.encode("utf-8"), timeout=2)
                ok = True
            except Exception:
                pass
        elif shutil.which("xclip"):
            try:
                proc = subprocess.Popen(
                    ["xclip", "-selection", "clipboard"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                proc.communicate(input=text.encode("utf-8"), timeout=2)
                ok = True
            except Exception:
                pass
        return ok

    def send_notification(self, title: str, message: str, icon_path: str | None = None) -> None:
        if shutil.which("notify-send"):
            cmd = ["notify-send", "-a", APP_NAME]
            if icon_path and os.path.exists(icon_path):
                cmd.extend(["-i", icon_path])
            else:
                cmd.extend(["-i", "camera-photo"])
            cmd.extend([title, message])
            try:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    def register_global_shortcut(self, command: str, binding: str = "<Super><Shift>s") -> tuple[bool, str]:
        """Register a GNOME/Ubuntu custom keyboard shortcut via gsettings."""
        if not shutil.which("gsettings"):
            return False, "gsettings not found. Please set a Custom Shortcut manually in Settings -> Keyboard."

        try:
            schema = "org.gnome.settings-daemon.plugins.media-keys"
            key = "custom-keybindings"
            base_path = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"
            avro_path = f"{base_path}/avroshot/"

            res = subprocess.run(
                ["gsettings", "get", schema, key],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if res.returncode != 0:
                return False, f"Could not read gsettings: {res.stderr.strip()}"

            raw = res.stdout.strip()
            if raw.startswith("@as"):
                current_list: list[str] = []
            else:
                import ast

                try:
                    current_list = list(ast.literal_eval(raw))
                except Exception:
                    current_list = []

            if avro_path not in current_list:
                current_list.append(avro_path)
                formatted = "[" + ", ".join(f"'{p}'" for p in current_list) + "]"
                subprocess.run(
                    ["gsettings", "set", schema, key, formatted],
                    check=True,
                    timeout=3,
                )

            item_schema = f"{schema}.custom-keybinding:{avro_path}"
            subprocess.run(["gsettings", "set", item_schema, "name", f"{APP_NAME} Capture"], check=True, timeout=3)
            subprocess.run(["gsettings", "set", item_schema, "command", command], check=True, timeout=3)
            subprocess.run(["gsettings", "set", item_schema, "binding", binding], check=True, timeout=3)
            return True, f"Registered shortcut '{binding}' -> {command}"
        except Exception as exc:
            return False, f"Failed to register shortcut: {exc}"
