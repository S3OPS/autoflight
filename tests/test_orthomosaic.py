import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from autoflight.orthomosaic import create_orthomosaic


def _write_image(path: Path, image: np.ndarray) -> None:
    cv2.imwrite(str(path), image)


class TestOrthomosaic(unittest.TestCase):
    def test_create_orthomosaic_generates_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            rng = np.random.default_rng(0)
            base = rng.integers(0, 255, size=(300, 300, 3), dtype=np.uint8)
            shift_matrix = np.float32([[1, 0, -50], [0, 1, 0]])
            shifted = cv2.warpAffine(base, shift_matrix, (300, 300))

            _write_image(temp_dir / "one.jpg", base)
            _write_image(temp_dir / "two.jpg", shifted)
            output_path = temp_dir / "mosaic.jpg"
            result = create_orthomosaic(temp_dir, output_path)

            self.assertTrue(output_path.exists())
            self.assertEqual(result.image_count, 2)
            self.assertGreater(result.size[0], 0)
            self.assertGreater(result.size[1], 0)
