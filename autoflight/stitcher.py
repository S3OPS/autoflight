"""Image stitching utilities for creating panoramic orthomosaics."""

from __future__ import annotations

import logging
from typing import Callable, Optional, Sequence

import cv2
import numpy as np

from autoflight.exceptions import StitchingError, ValidationError

logger = logging.getLogger(__name__)

# Export public API
__all__ = ["stitch_images"]


def stitch_images(
    images: Sequence[np.ndarray],
    mode: str = "panorama",
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> np.ndarray:
    """Stitch multiple images into a single panoramic image.
    
    Args:
        images: List of images to stitch
        mode: Stitching mode ("panorama" or "scans")
        progress_callback: Optional callback for progress reporting (progress, message)
        
    Returns:
        Stitched panoramic image
        
    Raises:
        StitchingError: If stitching fails
        ValidationError: If invalid mode or no images provided
    """
    if not images:
        raise ValidationError("No images provided for stitching")
    
    if len(images) == 1:
        logger.warning("Only one image provided, returning without stitching")
        if progress_callback:
            progress_callback(1.0, "Single image - no stitching needed")
        return images[0]
    
    logger.info(f"Stitching {len(images)} images in {mode} mode")
    
    if progress_callback:
        progress_callback(0.5, f"Stitching {len(images)} images...")
    
    # Select stitcher mode
    if mode == "panorama":
        stitcher_mode = cv2.STITCHER_PANORAMA
    elif mode == "scans":
        stitcher_mode = cv2.STITCHER_SCANS
    else:
        raise ValidationError(f"Invalid stitching mode: {mode}. Use 'panorama' or 'scans'")
    
    # Create stitcher and perform stitching
    stitcher = cv2.Stitcher_create(stitcher_mode)
    
    if progress_callback:
        progress_callback(0.6, "Feature detection and matching...")
    
    status, stitched = stitcher.stitch(images)
    
    # Check result
    if status != cv2.Stitcher_OK:
        error_messages = {
            cv2.Stitcher_ERR_NEED_MORE_IMGS: "Need more images with sufficient overlap",
            cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL: "Homography estimation failed - images may not overlap sufficiently",
            cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL: "Camera parameter adjustment failed",
        }
        error_msg = error_messages.get(status, f"Unknown error (status {status})")
        raise StitchingError(f"Stitching failed: {error_msg}")
    
    if stitched is None:
        raise StitchingError("Stitching produced no output")
    
    if progress_callback:
        progress_callback(0.95, "Stitching complete")
    
    logger.info(f"Successfully stitched images into {stitched.shape[1]}x{stitched.shape[0]} panorama")
    return stitched
