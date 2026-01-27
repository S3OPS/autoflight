"""Autoflight package - Professional-grade orthomosaic generation.

This package provides tools for creating orthomosaic images from overlapping
aerial photographs. It handles the complete pipeline from loading images
through stitching and saving the final result.

Example:
    >>> from autoflight import create_orthomosaic
    >>> result = create_orthomosaic("path/to/images", "output.jpg")
    >>> print(f"Created {result.size[0]}x{result.size[1]} mosaic")

Modules:
    - orthomosaic: Main API for creating orthomosaics
    - image_loader: Image loading with parallel support
    - stitcher: Image stitching algorithms
    - output: Output file handling with quality settings
    - config: Configuration management
    - security: Security validation utilities
    - exceptions: Custom exception classes
    - cli: Command-line interface
"""

# Auto-install dependencies before any imports
from autoflight._ensure_deps import ensure_dependencies

ensure_dependencies()

# Export main functionality
from autoflight.orthomosaic import create_orthomosaic, OrthomosaicResult
from autoflight.exceptions import (
    AutoflightError,
    ImageLoadError,
    StitchingError,
    OutputError,
    ValidationError,
    SecurityError,
)
from autoflight.config import AutoflightConfig, get_default_config, set_default_config
from autoflight.security import SecurityLimits

__all__ = [
    # Main API
    "create_orthomosaic",
    "OrthomosaicResult",
    # Exceptions
    "AutoflightError",
    "ImageLoadError",
    "StitchingError",
    "OutputError",
    "ValidationError",
    "SecurityError",
    # Configuration
    "AutoflightConfig",
    "get_default_config",
    "set_default_config",
    "SecurityLimits",
]

__version__ = "1.2.0"
