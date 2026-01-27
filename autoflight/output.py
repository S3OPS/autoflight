"""Output utilities for saving stitched images."""

from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def save_image(image: np.ndarray, output_path: Path, create_dirs: bool = True) -> None:
    """Save an image to disk.
    
    Args:
        image: Image to save
        output_path: Path where to save the image
        create_dirs: Whether to create parent directories if they don't exist
        
    Raises:
        RuntimeError: If saving fails
        ValueError: If image is invalid
    """
    if image is None or image.size == 0:
        raise ValueError("Cannot save empty or None image")
    
    # Validate output path
    if create_dirs:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    elif not output_path.parent.exists():
        raise ValueError(f"Output directory does not exist: {output_path.parent}")
    
    logger.info(f"Saving image to {output_path}")
    
    # Save the image
    success = cv2.imwrite(str(output_path), image)
    if not success:
        raise RuntimeError(f"Failed to write output image to {output_path}")
    
    logger.debug(f"Image saved successfully: {output_path}")
