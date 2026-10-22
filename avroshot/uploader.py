"""Cloud image uploader (0x0.st and Imgur anonymous upload) for AvroShot."""

from __future__ import annotations

import base64
import json
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass

from PyQt6.QtCore import QBuffer, QByteArray, QIODevice, QObject, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap


@dataclass
class UploadResult:
    success: bool
    url: str = ""
    delete_url: str = ""
    provider: str = ""
    error: str = ""


def pixmap_to_png_bytes(pixmap: QPixmap) -> bytes:
    ba = QByteArray()
    buf = QBuffer(ba)
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    pixmap.save(buf, "PNG")
    return bytes(ba)


def upload_to_0x0(png_bytes: bytes, timeout: int = 20) -> UploadResult:
    """Upload PNG bytes to https://0x0.st using multipart/form-data (no API key needed)."""
    boundary = f"----AvroShotBoundary{uuid.uuid4().hex}"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="avroshot.png"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode("utf-8") + png_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        "https://0x0.st",
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "AvroShot/1.0 (https://github.com/avroshot/avroshot)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            url = resp.read().decode("utf-8", errors="replace").strip()
            if url.startswith("http"):
                return UploadResult(success=True, url=url, provider="0x0.st")
            return UploadResult(success=False, error=f"Unexpected response: {url}", provider="0x0.st")
    except Exception as exc:
        return UploadResult(success=False, error=str(exc), provider="0x0.st")


def upload_to_imgur(png_bytes: bytes, client_id: str = "546c25a59c58ad7", timeout: int = 20) -> UploadResult:
    """Upload PNG bytes anonymously to Imgur API v3."""
    b64_image = base64.b64encode(png_bytes).decode("ascii")
    payload = urllib.parse.urlencode({"image": b64_image, "type": "base64"}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.imgur.com/3/image",
        data=payload,
        headers={
            "Authorization": f"Client-ID {client_id}",
            "User-Agent": "AvroShot/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
            if data.get("success") and "data" in data and "link" in data["data"]:
                link = data["data"]["link"]
                del_hash = data["data"].get("deletehash", "")
                del_url = f"https://imgur.com/delete/{del_hash}" if del_hash else ""
                return UploadResult(success=True, url=link, delete_url=del_url, provider="imgur")
            return UploadResult(success=False, error="Imgur returned unsuccessful response", provider="imgur")
    except Exception as exc:
        return UploadResult(success=False, error=str(exc), provider="imgur")


def upload_image(
    pixmap: QPixmap,
    provider: str = "0x0.st",
    imgur_client_id: str = "546c25a59c58ad7",
) -> UploadResult:
    """Upload QPixmap using the preferred provider with automatic fallback."""
    png_bytes = pixmap_to_png_bytes(pixmap)
    if provider == "imgur":
        res = upload_to_imgur(png_bytes, client_id=imgur_client_id)
        if res.success:
            return res
        fallback = upload_to_0x0(png_bytes)
        if fallback.success:
            return fallback
        return res
    else:
        res = upload_to_0x0(png_bytes)
        if res.success:
            return res
        fallback = upload_to_imgur(png_bytes, client_id=imgur_client_id)
        if fallback.success:
            return fallback
        return res


class UploadWorker(QThread):
    """Background Qt thread for non-blocking image upload."""

    finished_upload = pyqtSignal(object)  # emits UploadResult

    def __init__(
        self,
        pixmap: QPixmap,
        provider: str = "0x0.st",
        imgur_client_id: str = "546c25a59c58ad7",
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._pixmap = pixmap.copy()
        self._provider = provider
        self._client_id = imgur_client_id

    def run(self) -> None:
        result = upload_image(self._pixmap, self._provider, self._client_id)
        self.finished_upload.emit(result)
