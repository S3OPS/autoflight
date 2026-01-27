"""Image loading utilities with parallel support and validation."""

from __future__ import annotations

import concurrent.futures
import logging
from pathlib import Path
from typing import List

import cv2
import numpy as np

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}


def validate_path(path: Path, must_exist: bool = True, must_be_dir: bool = False) -> None:
    """Validate a file system path.
    
    Args:
        path: Path to validate
        must_exist: Whether the path must exist
        must_be_dir: Whether the path must be a directory
        
    Raises:
        ValueError: If validation fails
    """
    if must_exist and not path.exists():
        raise ValueError(f"Path does not exist: {path}")
    
    if must_be_dir and must_exist and not path.is_dir():
        raise ValueError(f"Path is not a directory: {path}")
    
    # Security: Check for path traversal attempts
    try:
        path.resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid path: {path}") from e


def is_supported_image(path: Path) -> bool:
    """Check if a file is a supported image format.
    
    Args:
        path: Path to check
        
    Returns:
        True if the file has a supported extension
    """
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def load_single_image(path: Path) -> np.ndarray:
    """Load a single image from disk.
    
    Args:
        path: Path to the image file
        
    Returns:
        Loaded image as numpy array
        
    Raises:
        ValueError: If the image cannot be loaded
    """
    logger.debug(f"Loading image: {path}")
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"Failed to load image: {path}")
    return image


def load_images(input_dir: Path, parallel: bool = True, max_workers: int = 4) -> List[np.ndarray]:
    """Load all supported images from a directory.
    
    Args:
        input_dir: Directory containing images
        parallel: Whether to load images in parallel
        max_workers: Maximum number of parallel workers
        
    Returns:
        List of loaded images
        
    Raises:
        ValueError: If no images are found or loading fails
    """
    validate_path(input_dir, must_exist=True, must_be_dir=True)
    
    # Get all supported image paths
    image_paths = sorted([
        path for path in input_dir.iterdir()
        if path.is_file() and is_supported_image(path)
    ])
    
    if not image_paths:
        raise ValueError(f"No supported images found in {input_dir}")
    
    logger.info(f"Found {len(image_paths)} images in {input_dir}")
    
    # Load images
    if parallel and len(image_paths) > 1:
        logger.debug(f"Loading images in parallel with {max_workers} workers")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            images = list(executor.map(load_single_image, image_paths))
    else:
        logger.debug("Loading images sequentially")
        images = [load_single_image(path) for path in image_paths]
    
    logger.info(f"Loaded {len(images)} images successfully")
    return images
