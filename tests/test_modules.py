"""Tests for the modular components."""

import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from autoflight.image_loader import (
    load_images,
    load_single_image,
    is_supported_image,
    validate_path,
)
from autoflight.stitcher import stitch_images
from autoflight.output import save_image
from autoflight.exceptions import (
    ImageLoadError,
    ValidationError,
    StitchingError,
)


def _write_image(path: Path, image: np.ndarray) -> None:
    """Helper to write test images."""
    cv2.imwrite(str(path), image)


def _create_test_image(size=(100, 100), seed=0) -> np.ndarray:
    """Create a test image."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, 255, size=(*size, 3), dtype=np.uint8)


class TestImageLoader(unittest.TestCase):
    """Tests for image_loader module."""
    
    def test_is_supported_image(self) -> None:
        """Test image format detection."""
        self.assertTrue(is_supported_image(Path("test.jpg")))
        self.assertTrue(is_supported_image(Path("test.JPG")))
        self.assertTrue(is_supported_image(Path("test.jpeg")))
        self.assertTrue(is_supported_image(Path("test.png")))
        self.assertTrue(is_supported_image(Path("test.tif")))
        self.assertTrue(is_supported_image(Path("test.tiff")))
        self.assertFalse(is_supported_image(Path("test.txt")))
        self.assertFalse(is_supported_image(Path("test.pdf")))
    
    def test_validate_path_exists(self) -> None:
        """Test path validation for existing paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            # Should not raise for existing directory
            validate_path(temp_path, must_exist=True, must_be_dir=True)
            
            # Should raise ValidationError for non-existent path
            with self.assertRaises(ValidationError):
                validate_path(temp_path / "nonexistent", must_exist=True)
    
    def test_load_single_image(self) -> None:
        """Test loading a single image."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            image_path = temp_path / "test.jpg"
            test_image = _create_test_image()
            _write_image(image_path, test_image)
            
            loaded = load_single_image(image_path)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.shape, test_image.shape)
    
    def test_load_single_image_failure(self) -> None:
        """Test loading non-existent image fails."""
        with self.assertRaises((ImageLoadError, ValidationError)):
            load_single_image(Path("/nonexistent/image.jpg"))
    
    def test_load_images_sequential(self) -> None:
        """Test loading multiple images sequentially."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            _write_image(temp_path / "img1.jpg", _create_test_image(seed=1))
            _write_image(temp_path / "img2.jpg", _create_test_image(seed=2))
            
            images = load_images(temp_path, parallel=False)
            self.assertEqual(len(images), 2)
    
    def test_load_images_parallel(self) -> None:
        """Test loading multiple images in parallel."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            image_one = _create_test_image(seed=1)
            image_two = _create_test_image(seed=2)
            image_three = _create_test_image(seed=3)
            _write_image(temp_path / "img1.png", image_one)
            _write_image(temp_path / "img2.png", image_two)
            _write_image(temp_path / "img3.png", image_three)
            
            images = load_images(temp_path, parallel=True)
            self.assertEqual(len(images), 3)
            np.testing.assert_array_equal(images[0], image_one)
            np.testing.assert_array_equal(images[1], image_two)
            np.testing.assert_array_equal(images[2], image_three)
    
    def test_load_images_no_images(self) -> None:
        """Test loading from empty directory fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            with self.assertRaises(ImageLoadError):
                load_images(temp_path)
    
    def test_load_images_filters_non_images(self) -> None:
        """Test that non-image files are filtered out."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            _write_image(temp_path / "img1.jpg", _create_test_image(seed=1))
            (temp_path / "readme.txt").write_text("test")
            
            images = load_images(temp_path)
            self.assertEqual(len(images), 1)


class TestStitcher(unittest.TestCase):
    """Tests for stitcher module."""
    
    def test_stitch_images_single(self) -> None:
        """Test stitching with a single image returns the image."""
        image = _create_test_image()
        result = stitch_images([image])
        self.assertIsNotNone(result)
        np.testing.assert_array_equal(result, image)
    
    def test_stitch_images_empty(self) -> None:
        """Test stitching with no images fails."""
        with self.assertRaises(ValidationError):
            stitch_images([])
    
    def test_stitch_images_multiple(self) -> None:
        """Test stitching multiple overlapping images."""
        rng = np.random.default_rng(0)
        base = rng.integers(0, 255, size=(300, 300, 3), dtype=np.uint8)
        shift_matrix = np.float32([[1, 0, -50], [0, 1, 0]])
        shifted = cv2.warpAffine(base, shift_matrix, (300, 300))
        
        result = stitch_images([base, shifted])
        self.assertIsNotNone(result)
        self.assertGreater(result.shape[0], 0)
        self.assertGreater(result.shape[1], 0)
    
    def test_stitch_images_invalid_mode(self) -> None:
        """Test stitching with invalid mode fails."""
        image = _create_test_image()
        with self.assertRaises(ValidationError):
            stitch_images([image, image], mode="invalid")


class TestOutput(unittest.TestCase):
    """Tests for output module."""
    
    def test_save_image(self) -> None:
        """Test saving an image."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_path = temp_path / "output.jpg"
            image = _create_test_image()
            
            save_image(image, output_path)
            self.assertTrue(output_path.exists())
    
    def test_save_image_creates_dirs(self) -> None:
        """Test saving an image creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_path = temp_path / "subdir" / "output.jpg"
            image = _create_test_image()
            
            save_image(image, output_path, create_dirs=True)
            self.assertTrue(output_path.exists())
    
    def test_save_image_no_create_dirs_fails(self) -> None:
        """Test saving fails when parent directory doesn't exist and create_dirs is False."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_path = temp_path / "nonexistent" / "output.jpg"
            image = _create_test_image()
            
            with self.assertRaises(ValidationError):
                save_image(image, output_path, create_dirs=False)
    
    def test_save_image_empty_fails(self) -> None:
        """Test saving empty image fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_path = temp_path / "output.jpg"
            
            with self.assertRaises(ValidationError):
                save_image(None, output_path)
    
    def test_save_image_with_quality(self) -> None:
        """Test saving an image with custom quality settings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_path = temp_path / "output.jpg"
            image = _create_test_image()
            
            # Test with custom quality
            save_image(image, output_path, quality=50)
            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
