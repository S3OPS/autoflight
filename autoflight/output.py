"""Output utilities for saving stitched images."""

from __future__ import annotations

import base64
import html
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from autoflight.exceptions import OutputError, ValidationError

logger = logging.getLogger(__name__)

# Export public API
__all__ = ["save_image", "save_html"]


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
    
    # Delegate to HTML output when the output extension is .html
    if output_path.suffix.lower() == ".html":
        save_html(image, output_path, create_dirs=create_dirs)
        return

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


def save_html(
    image: np.ndarray,
    output_path: Path,
    create_dirs: bool = True,
    title: str = "Orthomosaic",
) -> None:
    """Save an image as an HTML document with the image embedded as base64.

    The generated HTML file is self-contained: the orthomosaic is encoded as a
    base64 PNG data URL so the file can be opened in any browser without
    additional assets.

    Args:
        image: Image to embed
        output_path: Path where to save the HTML file (should end with .html)
        create_dirs: Whether to create parent directories if they don't exist
        title: Title displayed in the HTML document

    Raises:
        OutputError: If saving fails
        ValidationError: If image is invalid
    """
    if image is None or image.size == 0:
        raise ValidationError("Cannot save empty or None image")

    if create_dirs:
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OutputError(f"Failed to create output directory: {e}") from e
    elif not output_path.parent.exists():
        raise ValidationError(f"Output directory does not exist: {output_path.parent}")

    logger.info(f"Saving HTML report to {output_path}")

    # Encode image as PNG into memory, then base64-encode it
    try:
        success, buffer = cv2.imencode(".png", image)
        if not success:
            raise OutputError("Failed to encode image for HTML output")
        img_b64 = base64.b64encode(buffer).decode("ascii")
    except cv2.error as e:
        raise OutputError(f"OpenCV error encoding image: {e}") from e

    height, width = image.shape[:2]
    safe_title = html.escape(title)
    timestamp = html.escape(datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    safe_width = html.escape(str(width))
    safe_height = html.escape(str(height))

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{safe_title}</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background: #f5f5f5;
    }}
    h1 {{
      color: #333;
    }}
    .meta {{
      color: #666;
      margin-bottom: 16px;
      font-size: 0.9em;
    }}
    .image-container {{
      max-width: 100%;
      overflow: auto;
    }}
    img {{
      max-width: 100%;
      height: auto;
      border: 1px solid #ccc;
      border-radius: 4px;
    }}
  </style>
</head>
<body>
  <h1>{safe_title}</h1>
  <p class="meta">
    Size: {safe_width}&times;{safe_height} pixels &bull; Generated: {timestamp}
  </p>
  <div class="image-container">
    <img src="data:image/png;base64,{img_b64}" alt="{safe_title}">
  </div>
</body>
</html>
"""

    try:
        output_path.write_text(html_content, encoding="utf-8")
    except OSError as e:
        raise OutputError(f"Failed to write HTML file: {e}") from e

    logger.debug(f"HTML report saved successfully: {output_path}")
