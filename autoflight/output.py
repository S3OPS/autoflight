"""Output utilities for saving stitched images."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from autoflight.exceptions import OutputError, ValidationError

logger = logging.getLogger(__name__)

# Export public API
__all__ = ["save_image"]


def save_image(
    image: np.ndarray,
    output_path: Path,
    create_dirs: bool = True,
    quality: int = 95,
    png_compression: int = 3,
) -> None:
    """Save an image to disk with configurable quality settings.
    
    Args:
        image: Image to save
        output_path: Path where to save the image
        create_dirs: Whether to create parent directories if they don't exist
        quality: JPEG quality setting (1-100, default: 95). Higher = better quality, larger file.
        png_compression: PNG compression level (0-9, default: 3). Higher = smaller file, slower.
        
    Raises:
        OutputError: If saving fails
        ValidationError: If image or parameters are invalid
    """
    # Validate image
    if image is None or image.size == 0:
        raise ValidationError("Cannot save empty or None image")
    
    # Validate quality parameters
    if not 1 <= quality <= 100:
        raise ValidationError(f"JPEG quality must be 1-100, got {quality}")
    if not 0 <= png_compression <= 9:
        raise ValidationError(f"PNG compression must be 0-9, got {png_compression}")
    
    # Validate output path
    if create_dirs:
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OutputError(f"Failed to create output directory: {e}") from e
    elif not output_path.parent.exists():
        raise ValidationError(f"Output directory does not exist: {output_path.parent}")
    
    logger.info(f"Saving image to {output_path}")
    
    # Determine output format and set appropriate parameters
    suffix = output_path.suffix.lower()
    params = []
    
    if suffix in {".jpg", ".jpeg"}:
        params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        logger.debug(f"Using JPEG quality: {quality}")
    elif suffix == ".png":
        params = [cv2.IMWRITE_PNG_COMPRESSION, png_compression]
        logger.debug(f"Using PNG compression: {png_compression}")
    
    # Save the image
    try:
        success = cv2.imwrite(str(output_path), image, params)
        if not success:
            raise OutputError(f"Failed to write output image to {output_path}")
    except cv2.error as e:
        raise OutputError(f"OpenCV error saving image: {e}") from e
    
    logger.debug(f"Image saved successfully: {output_path}")
