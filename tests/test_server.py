"""Tests for the autoflight web server."""

import base64
import json
import tempfile
import threading
import unittest
from http.server import HTTPServer
from pathlib import Path
from urllib import request as urllib_request
from urllib.error import URLError

import cv2
import numpy as np

from autoflight.server import _AutoflightHandler, _WEB_DIR, run_server


def _create_test_image(size=(100, 100), seed=0) -> np.ndarray:
    """Create a small deterministic test image."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, 255, size=(*size, 3), dtype=np.uint8)


def _image_to_b64(img: np.ndarray) -> str:
    """Encode an ndarray image to a base64 PNG string."""
    ok, buf = cv2.imencode(".png", img)
    assert ok
    return "data:image/png;base64," + base64.b64encode(buf).decode("ascii")


class _ServerTestCase(unittest.TestCase):
    """Base class that starts and tears down a test HTTP server."""

    server: HTTPServer
    port: int
    base_url: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = HTTPServer(("localhost", 0), _AutoflightHandler)
        cls.port = cls.server.server_address[1]
        cls.base_url = f"http://localhost:{cls.port}"
        cls._thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls._thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()

    def _get(self, path: str):
        """Make a GET request and return (status, body_bytes)."""
        req = urllib_request.Request(self.base_url + path)
        try:
            with urllib_request.urlopen(req) as resp:
                return resp.status, resp.read()
        except urllib_request.HTTPError as e:
            return e.code, e.read()

    def _post_json(self, path: str, payload: dict):
        """Make a POST request with JSON body and return (status, parsed_json)."""
        body = json.dumps(payload).encode("utf-8")
        req = urllib_request.Request(
            self.base_url + path,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib_request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read())
        except urllib_request.HTTPError as e:
            return e.code, json.loads(e.read())


class TestServerGet(_ServerTestCase):
    """Tests for GET / (serving the web app)."""

    def test_get_root_returns_200(self) -> None:
        status, body = self._get("/")
        self.assertEqual(status, 200)

    def test_get_root_returns_html(self) -> None:
        _, body = self._get("/")
        self.assertIn(b"<!DOCTYPE html>", body)

    def test_get_root_contains_autoflight(self) -> None:
        _, body = self._get("/")
        self.assertIn(b"Autoflight", body)

    def test_get_unknown_path_returns_404(self) -> None:
        status, _ = self._get("/nonexistent")
        self.assertEqual(status, 404)


class TestServerStitchApi(_ServerTestCase):
    """Tests for POST /api/stitch."""

    def test_stitch_no_images_returns_400(self) -> None:
        status, data = self._post_json("/api/stitch", {"images": []})
        self.assertEqual(status, 400)
        self.assertFalse(data["success"])
        self.assertIn("No images", data["error"])

    def test_stitch_invalid_json_returns_400(self) -> None:
        req = urllib_request.Request(
            self.base_url + "/api/stitch",
            data=b"not-json",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib_request.urlopen(req) as resp:
                status = resp.status
                data = json.loads(resp.read())
        except urllib_request.HTTPError as e:
            status = e.code
            data = json.loads(e.read())
        self.assertEqual(status, 400)
        self.assertFalse(data["success"])

    def test_stitch_single_image_returns_ok(self) -> None:
        """A single image should be returned unchanged (no stitching needed)."""
        img = _create_test_image(size=(50, 80), seed=1)
        status, data = self._post_json(
            "/api/stitch",
            {"images": [_image_to_b64(img)], "mode": "panorama"},
        )
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertIn("image", data)
        self.assertEqual(data["image_count"], 1)
        self.assertEqual(data["width"], 80)
        self.assertEqual(data["height"], 50)

    def test_stitch_result_is_valid_png(self) -> None:
        """The returned base64 string should decode to a valid PNG."""
        img = _create_test_image(size=(60, 60), seed=2)
        _, data = self._post_json(
            "/api/stitch",
            {"images": [_image_to_b64(img)], "mode": "panorama"},
        )
        raw = base64.b64decode(data["image"])
        arr = np.frombuffer(raw, dtype=np.uint8)
        decoded = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded.shape[0], 60)
        self.assertEqual(decoded.shape[1], 60)

    def test_stitch_unknown_endpoint_returns_404(self) -> None:
        status, data = self._post_json("/api/unknown", {})
        self.assertEqual(status, 404)


class TestServerModule(unittest.TestCase):
    """Tests for server module-level attributes."""

    def test_web_dir_exists(self) -> None:
        self.assertTrue(_WEB_DIR.is_dir(), f"_WEB_DIR not found: {_WEB_DIR}")

    def test_index_html_exists(self) -> None:
        self.assertTrue((_WEB_DIR / "index.html").exists())

    def test_index_html_has_api_stitch(self) -> None:
        content = (_WEB_DIR / "index.html").read_text(encoding="utf-8")
        self.assertIn("/api/stitch", content)


class TestServeCli(unittest.TestCase):
    """Tests for the serve CLI subcommand parsing."""

    def test_serve_help(self) -> None:
        from autoflight.cli import run_serve

        with self.assertRaises(SystemExit) as ctx:
            run_serve(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_main_dispatches_serve(self) -> None:
        """main() with 'serve --help' should exit 0."""
        from autoflight.cli import main

        with self.assertRaises(SystemExit) as ctx:
            main(["serve", "--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
