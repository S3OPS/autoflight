"""Simple HTTP server for the autoflight web interface.

This module provides a lightweight web server (using only Python's standard
library) that serves the single-page HTML application and exposes a JSON API
for image stitching so the entire application can be used from a browser.

Usage::

    from autoflight.server import run_server

    run_server(port=8080)          # blocks; opens browser automatically

Or via the CLI::

    autoflight serve [--port 8080] [--host localhost] [--no-open]
"""

from __future__ import annotations

import base64
import json
import logging
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import cv2
import numpy as np

from autoflight.exceptions import AutoflightError
from autoflight.stitcher import stitch_images

logger = logging.getLogger(__name__)

_WEB_DIR = Path(__file__).parent / "web"

__all__ = ["run_server"]


class _AutoflightHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the autoflight web interface."""

    # ── Logging ──────────────────────────────────────────────────────────────

    def log_message(self, format: str, *args: object) -> None:  # type: ignore[override]
        logger.debug(format, *args)

    # ── Response helpers ──────────────────────────────────────────────────────

    def _send_bytes(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, obj: dict, status: int = 200) -> None:
        self._send_bytes(
            json.dumps(obj).encode("utf-8"),
            "application/json; charset=utf-8",
            status,
        )

    # ── CORS pre-flight ───────────────────────────────────────────────────────

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ── GET: serve the web app ────────────────────────────────────────────────

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            html_path = _WEB_DIR / "index.html"
            if html_path.exists():
                self._send_bytes(html_path.read_bytes(), "text/html; charset=utf-8")
            else:
                self._send_json({"error": "Web interface not found"}, 404)
        else:
            self._send_json({"error": "Not found"}, 404)

    # ── POST: API ─────────────────────────────────────────────────────────────

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/stitch":
            self._handle_stitch()
        else:
            self._send_json({"error": "Not found"}, 404)

    def _handle_stitch(self) -> None:
        """Decode uploaded images, stitch them, and return a base64 PNG."""
        # Parse JSON body
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            payload = json.loads(body)
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json({"success": False, "error": f"Invalid request body: {exc}"}, 400)
            return

        images_b64: list = payload.get("images", [])
        mode: str = str(payload.get("mode", "panorama"))

        if not images_b64:
            self._send_json({"success": False, "error": "No images provided"}, 400)
            return

        # Decode images from base64 data URLs / raw base64
        images: list = []
        for i, b64 in enumerate(images_b64):
            # Strip optional "data:<mime>;base64," prefix
            if "," in b64:
                b64 = b64.split(",", 1)[1]
            try:
                raw = base64.b64decode(b64)
                arr = np.frombuffer(raw, dtype=np.uint8)
                img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            except Exception as exc:
                self._send_json(
                    {"success": False, "error": f"Failed to decode image {i + 1}: {exc}"},
                    400,
                )
                return
            if img is None:
                self._send_json(
                    {"success": False, "error": f"Could not read image {i + 1}"},
                    400,
                )
                return
            images.append(img)

        # Stitch
        try:
            stitched = stitch_images(images, mode=mode)
        except AutoflightError as exc:
            self._send_json({"success": False, "error": str(exc)}, 422)
            return
        except Exception as exc:
            logger.exception("Unexpected error during stitching")
            self._send_json({"success": False, "error": f"Stitching error: {exc}"}, 500)
            return

        # Encode result as PNG
        ok, buf = cv2.imencode(".png", stitched, [cv2.IMWRITE_PNG_COMPRESSION, 3])
        if not ok:
            self._send_json({"success": False, "error": "Failed to encode result image"}, 500)
            return

        result_b64 = base64.b64encode(buf).decode("ascii")
        height, width = stitched.shape[:2]
        self._send_json(
            {
                "success": True,
                "image": result_b64,
                "width": width,
                "height": height,
                "image_count": len(images),
            }
        )


def run_server(
    host: str = "localhost",
    port: int = 8080,
    open_browser: bool = True,
) -> None:
    """Start the autoflight web interface server.

    The server serves the built-in single-page HTML application at ``/`` and
    exposes a JSON API at ``/api/stitch`` for image stitching.

    Args:
        host: Hostname to bind to (default: ``"localhost"``).
        port: TCP port to listen on (default: ``8080``).
        open_browser: If ``True``, open the default browser automatically after
            the server starts (default: ``True``).
    """
    server = HTTPServer((host, port), _AutoflightHandler)
    url = f"http://{host}:{port}"
    print(f"🚀 Autoflight web interface running at {url}")
    print("   Open the URL above in your browser, or press Ctrl+C to stop.")
    if open_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()
