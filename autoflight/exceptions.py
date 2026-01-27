"""Custom exceptions for autoflight package.

This module provides a hierarchy of exceptions for better error handling
and categorization across the autoflight package.
"""

from __future__ import annotations


class AutoflightError(Exception):
    """Base exception for all autoflight errors.
    
    All autoflight-specific exceptions inherit from this class,
    allowing users to catch all autoflight errors with a single handler.
    """
    pass


class ImageLoadError(AutoflightError):
    """Raised when image loading fails.
    
    This can occur due to:
    - File not found
    - Invalid image format
    - Corrupted image data
    - Permission issues
    """
    pass


class StitchingError(AutoflightError):
    """Raised when image stitching fails.
    
    This can occur due to:
    - Insufficient overlap between images
    - Homography estimation failure
    - Camera parameter adjustment failure
    - Not enough images provided
    """
    pass


class OutputError(AutoflightError):
    """Raised when output operations fail.
    
    This can occur due to:
    - Invalid output path
    - Permission denied
    - Disk full
    - Invalid image data
    """
    pass


class ValidationError(AutoflightError):
    """Raised when input validation fails.
    
    This can occur due to:
    - Invalid path
    - Path traversal attempt
    - File size limits exceeded
    - Image dimension limits exceeded
    """
    pass


class SecurityError(AutoflightError):
    """Raised when security validation fails.
    
    This can occur due to:
    - Path traversal attempt
    - File too large
    - Image dimensions exceed limits
    - Malformed image data
    """
    pass
