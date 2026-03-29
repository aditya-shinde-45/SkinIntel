"""
ImagePreprocessorService — validates, fetches, and normalizes images for CNN inference.
"""
import ipaddress
import logging
import socket
import time
from io import BytesIO

import numpy as np
import requests
from PIL import Image, UnidentifiedImageError
from werkzeug.datastructures import FileStorage

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
TARGET_SIZE = (224, 224)


class ImagePreprocessorError(Exception):
    def __init__(self, message: str, status_code: int, error_code: str):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code


class ImagePreprocessorService:
    def __init__(self, max_size_mb: int = 10):
        self.max_size_bytes = max_size_mb * 1024 * 1024

    def preprocess_file(self, file: FileStorage) -> np.ndarray:
        self._validate_mime(file)
        raw = file.read()
        self._validate_size_bytes(len(raw))
        return self._decode_and_normalize(raw)

    def preprocess_url(self, url: str) -> np.ndarray:
        self._ssrf_guard(url)
        raw = self._fetch_with_retry(url)
        return self._decode_and_normalize(raw)

    # ── private helpers ──────────────────────────────────────────────────────

    def _validate_mime(self, file: FileStorage) -> None:
        mime = file.mimetype or ""
        if mime not in ALLOWED_MIME_TYPES:
            raise ImagePreprocessorError(
                f"Unsupported image type '{mime}'. Accepted: jpeg, png, webp.",
                415,
                "unsupported_media_type",
            )

    def _validate_size_bytes(self, size: int) -> None:
        if size > self.max_size_bytes:
            raise ImagePreprocessorError(
                f"Image exceeds maximum allowed size of {self.max_size_bytes // (1024*1024)} MB.",
                413,
                "image_too_large",
            )

    def _ssrf_guard(self, url: str) -> None:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ImagePreprocessorError(
                "image_url must use http or https scheme.",
                400,
                "invalid_image_url",
            )

        hostname = parsed.hostname or ""
        try:
            ip = ipaddress.ip_address(socket.gethostbyname(hostname))
        except (socket.gaierror, ValueError):
            raise ImagePreprocessorError(
                f"Cannot resolve hostname: {hostname}",
                400,
                "invalid_image_url",
            )

        if ip.is_private or ip.is_loopback or ip.is_link_local:
            raise ImagePreprocessorError(
                "image_url must not point to a private or loopback address.",
                400,
                "invalid_image_url",
            )

    def _fetch_with_retry(self, url: str, max_retries: int = 3) -> bytes:
        last_error = None
        for attempt in range(max_retries):
            try:
                resp = requests.get(url, timeout=(5, 10), stream=True)
                if resp.status_code == 200:
                    return resp.content
                last_error = f"HTTP {resp.status_code}"
            except requests.RequestException as e:
                last_error = str(e)

            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)

        raise ImagePreprocessorError(
            f"Failed to fetch image after {max_retries} attempts: {last_error}",
            502,
            "image_fetch_failed",
        )

    def _decode_and_normalize(self, image_bytes: bytes) -> np.ndarray:
        try:
            img = Image.open(BytesIO(image_bytes)).convert("RGB")
        except (UnidentifiedImageError, Exception) as e:
            raise ImagePreprocessorError(
                f"Could not decode image: {e}",
                422,
                "image_decode_error",
            )

        img = img.resize(TARGET_SIZE, Image.LANCZOS)
        arr = np.array(img, dtype=np.float32) / 255.0
        return np.expand_dims(arr, axis=0)  # shape (1, 224, 224, 3)
