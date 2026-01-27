"""Tests for the new modules: security, config, cli, and exceptions."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np

from autoflight.exceptions import (
    AutoflightError,
    ImageLoadError,
    StitchingError,
    OutputError,
    ValidationError,
    SecurityError,
)
from autoflight.security import (
    SecurityLimits,
    validate_file_size,
    validate_image_dimensions,
    validate_file_count,
    validate_path_security,
    get_default_limits,
)
from autoflight.config import (
    AutoflightConfig,
    PerformanceConfig,
    OutputConfig,
    StitchingConfig,
    get_default_config,
    set_default_config,
)


def _write_image(path: Path, image: np.ndarray) -> None:
    """Helper to write test images."""
    cv2.imwrite(str(path), image)


def _create_test_image(size=(100, 100), seed=0) -> np.ndarray:
    """Create a test image."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, 255, size=(*size, 3), dtype=np.uint8)


class TestExceptions(unittest.TestCase):
    """Tests for custom exceptions."""
    
    def test_exception_hierarchy(self) -> None:
        """Test that all exceptions inherit from AutoflightError."""
        self.assertTrue(issubclass(ImageLoadError, AutoflightError))
        self.assertTrue(issubclass(StitchingError, AutoflightError))
        self.assertTrue(issubclass(OutputError, AutoflightError))
        self.assertTrue(issubclass(ValidationError, AutoflightError))
        self.assertTrue(issubclass(SecurityError, AutoflightError))
    
    def test_exception_messages(self) -> None:
        """Test that exceptions can carry messages."""
        msg = "Test error message"
        
        for exc_class in [ImageLoadError, StitchingError, OutputError, ValidationError, SecurityError]:
            exc = exc_class(msg)
            self.assertEqual(str(exc), msg)


class TestSecurityLimits(unittest.TestCase):
    """Tests for SecurityLimits class."""
    
    def test_default_limits(self) -> None:
        """Test default security limits."""
        limits = SecurityLimits()
        self.assertEqual(limits.max_file_size, 500_000_000)
        self.assertEqual(limits.max_image_pixels, 100_000_000)
        self.assertEqual(limits.max_files, 1000)
    
    def test_custom_limits(self) -> None:
        """Test custom security limits."""
        limits = SecurityLimits(
            max_file_size=1000,
            max_image_pixels=500,
            max_files=10,
        )
        self.assertEqual(limits.max_file_size, 1000)
        self.assertEqual(limits.max_image_pixels, 500)
        self.assertEqual(limits.max_files, 10)


class TestSecurityValidation(unittest.TestCase):
    """Tests for security validation functions."""
    
    def test_validate_file_size_passes(self) -> None:
        """Test file size validation passes for small files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            image_path = temp_path / "test.jpg"
            _write_image(image_path, _create_test_image())
            
            # Should not raise
            validate_file_size(image_path)
    
    def test_validate_file_size_fails(self) -> None:
        """Test file size validation fails for oversized files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            image_path = temp_path / "test.jpg"
            _write_image(image_path, _create_test_image())
            
            # Use very small limit
            limits = SecurityLimits(max_file_size=10)
            with self.assertRaises(SecurityError):
                validate_file_size(image_path, limits=limits)
    
    def test_validate_image_dimensions_passes(self) -> None:
        """Test image dimension validation passes for small images."""
        validate_image_dimensions(100, 100)
    
    def test_validate_image_dimensions_fails(self) -> None:
        """Test image dimension validation fails for oversized images."""
        limits = SecurityLimits(max_image_pixels=100)
        with self.assertRaises(SecurityError):
            validate_image_dimensions(100, 100, limits=limits)  # 10000 pixels
    
    def test_validate_file_count_passes(self) -> None:
        """Test file count validation passes for small counts."""
        validate_file_count(10)
    
    def test_validate_file_count_fails(self) -> None:
        """Test file count validation fails for excessive counts."""
        limits = SecurityLimits(max_files=5)
        with self.assertRaises(SecurityError):
            validate_file_count(10, limits=limits)
    
    def test_validate_path_security_normal_path(self) -> None:
        """Test path security validation passes for normal paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            resolved = validate_path_security(temp_path)
            self.assertEqual(resolved, temp_path.resolve())
    
    def test_validate_path_security_with_base_dir(self) -> None:
        """Test path security validation with base directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            subdir = base_path / "subdir"
            subdir.mkdir()
            
            # Should pass for paths within base
            resolved = validate_path_security(subdir, base_dir=base_path)
            self.assertEqual(resolved, subdir.resolve())
    
    def test_validate_path_security_traversal_detected(self) -> None:
        """Test path security validation detects path traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir) / "base"
            base_path.mkdir()
            
            # Create a path outside base
            outside_path = Path(temp_dir) / "outside"
            outside_path.mkdir()
            
            # Should fail for paths outside base
            with self.assertRaises(SecurityError):
                validate_path_security(outside_path, base_dir=base_path)


class TestConfig(unittest.TestCase):
    """Tests for configuration module."""
    
    def test_performance_config_defaults(self) -> None:
        """Test PerformanceConfig default values."""
        config = PerformanceConfig()
        self.assertTrue(config.parallel_loading)
        self.assertEqual(config.max_workers, 4)
        self.assertIsNone(config.memory_limit_mb)
    
    def test_output_config_defaults(self) -> None:
        """Test OutputConfig default values."""
        config = OutputConfig()
        self.assertEqual(config.jpeg_quality, 95)
        self.assertEqual(config.png_compression, 3)
        self.assertTrue(config.create_dirs)
    
    def test_output_config_validation(self) -> None:
        """Test OutputConfig validates values."""
        with self.assertRaises(ValueError):
            OutputConfig(jpeg_quality=101)
        with self.assertRaises(ValueError):
            OutputConfig(png_compression=10)
    
    def test_stitching_config_defaults(self) -> None:
        """Test StitchingConfig default values."""
        config = StitchingConfig()
        self.assertEqual(config.mode, "panorama")
        self.assertFalse(config.try_use_gpu)
    
    def test_stitching_config_validation(self) -> None:
        """Test StitchingConfig validates mode."""
        with self.assertRaises(ValueError):
            StitchingConfig(mode="invalid")
    
    def test_autoflight_config_defaults(self) -> None:
        """Test AutoflightConfig default values."""
        config = AutoflightConfig()
        self.assertIsInstance(config.performance, PerformanceConfig)
        self.assertIsInstance(config.output, OutputConfig)
        self.assertIsInstance(config.stitching, StitchingConfig)
        self.assertIsInstance(config.security, SecurityLimits)
        self.assertFalse(config.verbose)
        self.assertIsNone(config.progress_callback)
    
    def test_autoflight_config_from_env(self) -> None:
        """Test AutoflightConfig.from_env()."""
        with patch.dict(os.environ, {
            "AUTOFLIGHT_PARALLEL": "0",
            "AUTOFLIGHT_JPEG_QUALITY": "80",
            "AUTOFLIGHT_MODE": "scans",
            "AUTOFLIGHT_VERBOSE": "1",
        }):
            config = AutoflightConfig.from_env()
            self.assertFalse(config.performance.parallel_loading)
            self.assertEqual(config.output.jpeg_quality, 80)
            self.assertEqual(config.stitching.mode, "scans")
            self.assertTrue(config.verbose)
    
    def test_autoflight_config_with_progress(self) -> None:
        """Test AutoflightConfig.with_progress()."""
        config = AutoflightConfig()
        
        def callback(progress, msg):
            pass
        
        new_config = config.with_progress(callback)
        self.assertIsNone(config.progress_callback)
        self.assertEqual(new_config.progress_callback, callback)
    
    def test_get_and_set_default_config(self) -> None:
        """Test getting and setting default config."""
        original = get_default_config()
        
        custom_config = AutoflightConfig(verbose=True)
        set_default_config(custom_config)
        
        self.assertEqual(get_default_config(), custom_config)
        
        # Restore original
        set_default_config(original)


class TestCLI(unittest.TestCase):
    """Tests for CLI module."""
    
    def test_cli_help(self) -> None:
        """Test CLI --help output."""
        from autoflight.cli import create_parser
        
        parser = create_parser()
        # Should not raise
        with self.assertRaises(SystemExit) as ctx:
            parser.parse_args(["--help"])
        self.assertEqual(ctx.exception.code, 0)
    
    def test_cli_dry_run(self) -> None:
        """Test CLI dry-run mode."""
        from autoflight.cli import run
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            result = run([str(temp_path), "output.jpg", "--dry-run"])
            self.assertEqual(result, 0)
    
    def test_cli_dry_run_nonexistent(self) -> None:
        """Test CLI dry-run mode with non-existent directory."""
        from autoflight.cli import run
        
        result = run(["/nonexistent/path", "output.jpg", "--dry-run"])
        self.assertEqual(result, 1)
    
    def test_cli_config_from_args(self) -> None:
        """Test config_from_args creates proper config."""
        from autoflight.cli import create_parser, config_from_args
        
        parser = create_parser()
        args = parser.parse_args([
            "/input", "output.jpg",
            "--mode", "scans",
            "--no-parallel",
            "--quality", "80",
            "--verbose",
        ])
        
        config = config_from_args(args)
        
        self.assertFalse(config.performance.parallel_loading)
        self.assertEqual(config.stitching.mode, "scans")
        self.assertEqual(config.output.jpeg_quality, 80)
        self.assertTrue(config.verbose)


if __name__ == "__main__":
    unittest.main()
