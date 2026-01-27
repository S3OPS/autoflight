"""Security utilities for autoflight package.

This module provides security-related validation functions to protect against
common vulnerabilities like path traversal attacks, denial of service via
large files, and malformed input.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from autoflight.exceptions import SecurityError, ValidationError

logger = logging.getLogger(__name__)

# Security limits - configurable via config module
DEFAULT_MAX_FILE_SIZE = 500_000_000  # 500 MB
DEFAULT_MAX_IMAGE_PIXELS = 100_000_000  # 100 megapixels
DEFAULT_MAX_FILES = 1000


class SecurityLimits:
    """Configurable security limits for image processing.
    
    Attributes:
        max_file_size: Maximum file size in bytes (default: 500 MB)
        max_image_pixels: Maximum total pixels in an image (default: 100 megapixels)
        max_files: Maximum number of files to process (default: 1000)
    """
    
    def __init__(
        self,
        max_file_size: int = DEFAULT_MAX_FILE_SIZE,
        max_image_pixels: int = DEFAULT_MAX_IMAGE_PIXELS,
        max_files: int = DEFAULT_MAX_FILES,
    ) -> None:
        self.max_file_size = max_file_size
        self.max_image_pixels = max_image_pixels
        self.max_files = max_files


# Default security limits
_default_limits = SecurityLimits()


def get_default_limits() -> SecurityLimits:
    """Get the default security limits.
    
    Returns:
        Default SecurityLimits instance
    """
    return _default_limits


def validate_file_size(
    path: Path,
    max_size: Optional[int] = None,
    limits: Optional[SecurityLimits] = None,
) -> None:
    """Validate that a file does not exceed size limits.
    
    Args:
        path: Path to the file to validate
        max_size: Maximum allowed file size in bytes (overrides limits)
        limits: SecurityLimits instance (defaults to global limits)
        
    Raises:
        SecurityError: If file size exceeds the limit
        ValidationError: If file cannot be accessed
    """
    if limits is None:
        limits = _default_limits
    
    effective_max = max_size if max_size is not None else limits.max_file_size
    
    try:
        file_size = path.stat().st_size
    except OSError as e:
        raise ValidationError(f"Cannot access file: {path}") from e
    
    if file_size > effective_max:
        raise SecurityError(
            f"File size ({file_size:,} bytes) exceeds limit ({effective_max:,} bytes): {path}"
        )
    
    logger.debug(f"File size validated: {path} ({file_size:,} bytes)")


def validate_image_dimensions(
    width: int,
    height: int,
    max_pixels: Optional[int] = None,
    limits: Optional[SecurityLimits] = None,
) -> None:
    """Validate that image dimensions do not exceed limits.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        max_pixels: Maximum allowed total pixels (overrides limits)
        limits: SecurityLimits instance (defaults to global limits)
        
    Raises:
        SecurityError: If image dimensions exceed the limit
    """
    if limits is None:
        limits = _default_limits
    
    effective_max = max_pixels if max_pixels is not None else limits.max_image_pixels
    
    total_pixels = width * height
    if total_pixels > effective_max:
        raise SecurityError(
            f"Image dimensions ({width}x{height} = {total_pixels:,} pixels) "
            f"exceed limit ({effective_max:,} pixels)"
        )
    
    logger.debug(f"Image dimensions validated: {width}x{height} ({total_pixels:,} pixels)")


def validate_file_count(
    count: int,
    max_files: Optional[int] = None,
    limits: Optional[SecurityLimits] = None,
) -> None:
    """Validate that the number of files does not exceed limits.
    
    Args:
        count: Number of files
        max_files: Maximum allowed file count (overrides limits)
        limits: SecurityLimits instance (defaults to global limits)
        
    Raises:
        SecurityError: If file count exceeds the limit
    """
    if limits is None:
        limits = _default_limits
    
    effective_max = max_files if max_files is not None else limits.max_files
    
    if count > effective_max:
        raise SecurityError(
            f"File count ({count}) exceeds limit ({effective_max})"
        )
    
    logger.debug(f"File count validated: {count} files")


def validate_path_security(path: Path, base_dir: Optional[Path] = None) -> Path:
    """Validate a path for security concerns.
    
    This function checks for:
    - Path traversal attempts (e.g., ../../../etc/passwd)
    - Symbolic link attacks
    - Invalid paths
    
    Args:
        path: Path to validate
        base_dir: Optional base directory - if provided, resolved path must be within it
        
    Returns:
        Resolved, validated path
        
    Raises:
        SecurityError: If path validation fails
    """
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError) as e:
        raise SecurityError(f"Invalid path: {path}") from e
    
    # Check for path traversal if base_dir is provided
    if base_dir is not None:
        try:
            base_resolved = base_dir.resolve()
            # Check that resolved path starts with base directory
            resolved.relative_to(base_resolved)
        except ValueError:
            raise SecurityError(
                f"Path traversal detected: {path} resolves outside of {base_dir}"
            )
    
    logger.debug(f"Path security validated: {path} -> {resolved}")
    return resolved


def validate_image_file(
    path: Path,
    limits: Optional[SecurityLimits] = None,
    check_dimensions: bool = False,
) -> None:
    """Perform comprehensive security validation on an image file.
    
    Args:
        path: Path to the image file
        limits: SecurityLimits instance (defaults to global limits)
        check_dimensions: Whether to load and check image dimensions
        
    Raises:
        SecurityError: If any security validation fails
        ValidationError: If file cannot be accessed
    """
    if limits is None:
        limits = _default_limits
    
    # Validate path security
    validate_path_security(path)
    
    # Validate file size
    validate_file_size(path, limits=limits)
    
    # Optionally check image dimensions (requires loading the image)
    if check_dimensions:
        try:
            import cv2
            image = cv2.imread(str(path))
            if image is not None:
                height, width = image.shape[:2]
                validate_image_dimensions(width, height, limits=limits)
        except ImportError:
            logger.warning("OpenCV not available for dimension check")
        except Exception as e:
            logger.warning(f"Could not check image dimensions: {e}")
    
    logger.debug(f"Image file security validated: {path}")
