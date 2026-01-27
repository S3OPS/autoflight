"""Image stitching utilities for creating panoramic orthomosaics."""

from __future__ import annotations

import logging
from typing import Sequence

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def stitch_images(images: Sequence[np.ndarray], mode: str = "panorama") -> np.ndarray:
    """Stitch multiple images into a single panoramic image.
    
    Args:
        images: List of images to stitch
        mode: Stitching mode ("panorama" or "scans")
        
    Returns:
        Stitched panoramic image
        
    Raises:
        RuntimeError: If stitching fails
        ValueError: If invalid mode or no images provided
    """
    if not images:
        raise ValueError("No images provided for stitching")
    
    if len(images) == 1:
        logger.warning("Only one image provided, returning without stitching")
        return images[0]
    
    logger.info(f"Stitching {len(images)} images in {mode} mode")
    
    # Select stitcher mode
    if mode == "panorama":
        stitcher_mode = cv2.STITCHER_PANORAMA
    elif mode == "scans":
        stitcher_mode = cv2.STITCHER_SCANS
    else:
        raise ValueError(f"Invalid stitching mode: {mode}. Use 'panorama' or 'scans'")
    
    # Create stitcher and perform stitching
    stitcher = cv2.Stitcher_create(stitcher_mode)
    status, stitched = stitcher.stitch(list(images))
    
    # Check result
    if status != cv2.Stitcher_OK:
        error_messages = {
            cv2.Stitcher_ERR_NEED_MORE_IMGS: "Need more images",
            cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL: "Homography estimation failed",
            cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL: "Camera parameter adjustment failed",
        }
        error_msg = error_messages.get(status, f"Unknown error (status {status})")
        raise RuntimeError(f"Stitching failed: {error_msg}")
    
    if stitched is None:
        raise RuntimeError("Stitching produced no output")
    
    logger.info(f"Successfully stitched images into {stitched.shape[1]}x{stitched.shape[0]} panorama")
    return stitched
