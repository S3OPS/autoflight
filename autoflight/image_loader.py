"""Image loading utilities with parallel support and validation."""

from __future__ import annotations

import concurrent.futures
import logging
from pathlib import Path
from typing import List, Optional, Callable, cast

import cv2
import numpy as np

from autoflight.exceptions import ImageLoadError, ValidationError
from autoflight.security import (
    SecurityLimits,
    validate_file_size,
    validate_file_count,
    validate_path_security,
    get_default_limits,
)

logger = logging.getLogger(__name__)

# Export public API
__all__ = [
    "load_images",
    "load_single_image",
    "is_supported_image",
    "validate_path",
    "SUPPORTED_EXTENSIONS",
]

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}


def validate_path(path: Path, must_exist: bool = True, must_be_dir: bool = False) -> None:
    """Validate a file system path.
    
    Args:
        path: Path to validate
        must_exist: Whether the path must exist
        must_be_dir: Whether the path must be a directory
        
    Raises:
        ValidationError: If validation fails
    """
    if must_exist and not path.exists():
        raise ValidationError(f"Path does not exist: {path}")
    
    if must_be_dir and must_exist and not path.is_dir():
        raise ValidationError(f"Path is not a directory: {path}")
    
    # Security: Check for path traversal attempts
    try:
        validate_path_security(path)
    except Exception as e:
        raise ValidationError(f"Invalid path: {path}") from e


def is_supported_image(path: Path) -> bool:
    """Check if a file is a supported image format.
    
    Args:
        path: Path to check
        
    Returns:
        True if the file has a supported extension
    """
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def load_single_image(
    path: Path,
    validate_security: bool = True,
    limits: Optional[SecurityLimits] = None,
) -> np.ndarray:
    """Load a single image from disk with security validation.
    
    Args:
        path: Path to the image file
        validate_security: Whether to perform security validation
        limits: Optional security limits (uses defaults if not provided)
        
    Returns:
        Loaded image as numpy array
        
    Raises:
        ImageLoadError: If the image cannot be loaded
        SecurityError: If security validation fails
    """
    logger.debug(f"Loading image: {path}")
    
    # Security validation
    if validate_security:
        if limits is None:
            limits = get_default_limits()
        validate_file_size(path, limits=limits)
    
    # Load the image
    image = cv2.imread(str(path))
    if image is None:
        raise ImageLoadError(f"Failed to load image: {path}")
    
    return image


def load_images(
    input_dir: Path,
    parallel: bool = True,
    max_workers: int = 4,
    validate_security: bool = True,
    limits: Optional[SecurityLimits] = None,
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> List[np.ndarray]:
    """Load all supported images from a directory.
    
    Args:
        input_dir: Directory containing images
        parallel: Whether to load images in parallel
        max_workers: Maximum number of parallel workers
        validate_security: Whether to perform security validation
        limits: Optional security limits (uses defaults if not provided)
        progress_callback: Optional callback for progress reporting (progress, message)
        
    Returns:
        List of loaded images
        
    Raises:
        ValidationError: If directory is invalid
        ImageLoadError: If no images are found or loading fails
        SecurityError: If security validation fails
    """
    validate_path(input_dir, must_exist=True, must_be_dir=True)
    
    # Get all supported image paths
    image_paths = sorted([
        path for path in input_dir.iterdir()
        if path.is_file() and is_supported_image(path)
    ])
    
    if not image_paths:
        raise ImageLoadError(f"No supported images found in {input_dir}")
    
    # Security: Validate file count
    if validate_security:
        if limits is None:
            limits = get_default_limits()
        validate_file_count(len(image_paths), limits=limits)
    
    logger.info(f"Found {len(image_paths)} images in {input_dir}")
    
    if progress_callback:
        progress_callback(0.0, f"Loading {len(image_paths)} images...")
    
    if parallel and len(image_paths) > 1:
        logger.debug(f"Loading images in parallel with {max_workers} workers")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(load_single_image, path, validate_security, limits): i
                for i, path in enumerate(image_paths)
            }
            images_by_index: List[Optional[np.ndarray]] = [None] * len(image_paths)
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                try:
                    image = future.result()
                    index = futures[future]
                    images_by_index[index] = image
                    completed += 1
                    if progress_callback:
                        progress = completed / len(image_paths)
                        progress_callback(progress * 0.5, f"Loaded {completed}/{len(image_paths)} images")
                except Exception as e:
                    index = futures[future]
                    failed_path = image_paths[index]
                    logger.error(f"Failed to load image {failed_path}: {e}")
                    raise
            images = cast(List[np.ndarray], images_by_index)
    else:
        logger.debug("Loading images sequentially")
        images = []
        for i, path in enumerate(image_paths):
            image = load_single_image(path, validate_security, limits)
            images.append(image)
            if progress_callback:
                progress = (i + 1) / len(image_paths)
                progress_callback(progress * 0.5, f"Loaded {i + 1}/{len(image_paths)} images")
    
    logger.info(f"Loaded {len(images)} images successfully")
    return images
