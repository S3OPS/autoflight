"""Orthomosaic generation utilities."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Optional

from autoflight.image_loader import load_images
from autoflight.output import save_image
from autoflight.stitcher import stitch_images
from autoflight.exceptions import AutoflightError

logger = logging.getLogger(__name__)

# Export public API
__all__ = ["create_orthomosaic", "OrthomosaicResult"]

# Type alias for progress callbacks
ProgressCallback = Callable[[float, str], None]


@dataclass
class OrthomosaicResult:
    """Result of orthomosaic creation.
    
    Attributes:
        output_path: Path where the orthomosaic was saved
        image_count: Number of images used in the mosaic
        size: Tuple of (width, height) in pixels
    """
    
    output_path: Path
    image_count: int
    size: tuple[int, int]


def create_orthomosaic(
    input_dir: Path | str,
    output_path: Path | str,
    parallel: bool = True,
    verbose: bool = False,
    mode: str = "panorama",
    quality: int = 95,
    progress_callback: Optional[ProgressCallback] = None,
) -> OrthomosaicResult:
    """Create an orthomosaic from images in input_dir and write to output_path.
    
    This is the main API function for creating orthomosaics. It handles the complete
    pipeline: loading images, stitching them together, and saving the result.
    
    Args:
        input_dir: Directory containing input images
        output_path: Path where to save the orthomosaic
        parallel: Whether to load images in parallel (faster for many images)
        verbose: Whether to enable verbose logging
        mode: Stitching mode ("panorama" or "scans")
        quality: JPEG quality setting (1-100, default: 95)
        progress_callback: Optional callback for progress reporting.
            Called with (progress: float, message: str) where progress is 0.0 to 1.0.
        
    Returns:
        OrthomosaicResult with information about the created orthomosaic
        
    Raises:
        ValidationError: If input is invalid
        ImageLoadError: If image loading fails
        StitchingError: If stitching fails
        OutputError: If saving fails
        
    Example:
        >>> from autoflight import create_orthomosaic
        >>> result = create_orthomosaic("path/to/images", "output.jpg")
        >>> print(f"Created {result.size[0]}x{result.size[1]} mosaic from {result.image_count} images")
    """
    # Configure logging only if not already configured
    if not logging.getLogger().handlers:
        level = logging.DEBUG if verbose else logging.WARNING
        logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    elif verbose:
        # If already configured, just update the level for verbose mode
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Convert to Path objects
    input_path = Path(input_dir)
    output_path_obj = Path(output_path)
    
    logger.info(f"Creating orthomosaic from {input_path}")
    
    if progress_callback:
        progress_callback(0.0, "Starting orthomosaic creation...")
    
    # Load images
    images = load_images(input_path, parallel=parallel, progress_callback=progress_callback)
    
    # Stitch images
    stitched = stitch_images(images, mode=mode, progress_callback=progress_callback)
    
    if progress_callback:
        progress_callback(0.95, "Saving output...")
    
    # Save result
    save_image(stitched, output_path_obj, quality=quality)
    
    if progress_callback:
        progress_callback(1.0, "Complete!")
    
    # Return result
    height, width = stitched.shape[:2]
    result = OrthomosaicResult(
        output_path=output_path_obj,
        image_count=len(images),
        size=(width, height)
    )
    
    logger.info(f"Orthomosaic created successfully: {result.output_path}")
    return result


def main(args: Iterable[str] | None = None) -> int:
    """Command-line interface for orthomosaic generation.
    
    This function provides backward compatibility with the legacy CLI.
    For new code, consider using the autoflight.cli module directly.
    
    Args:
        args: Command-line arguments (defaults to sys.argv)
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Generate an orthomosaic from overlapping aerial images",
        epilog="Example: %(prog)s /path/to/images output.jpg"
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing input images (jpg, jpeg, png, tif, tiff)"
    )
    parser.add_argument(
        "output_path",
        type=Path,
        help="Path where to save the orthomosaic image"
    )
    parser.add_argument(
        "--mode",
        choices=["panorama", "scans"],
        default="panorama",
        help="Stitching mode: 'panorama' for standard panoramas, 'scans' for scanned images (default: panorama)"
    )
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel image loading (slower but uses less memory)"
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=95,
        metavar="Q",
        help="JPEG quality setting, 1-100 (default: 95)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress all output except errors"
    )
    
    parsed = parser.parse_args(list(args) if args is not None else None)
    
    # Handle quiet mode
    if parsed.quiet:
        logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
    
    try:
        result = create_orthomosaic(
            parsed.input_dir,
            parsed.output_path,
            parallel=not parsed.no_parallel,
            verbose=parsed.verbose,
            mode=parsed.mode,
            quality=parsed.quality,
        )
        
        if not parsed.quiet:
            print(
                f"✓ Orthomosaic created: {result.output_path}\n"
                f"  Images used: {result.image_count}\n"
                f"  Size: {result.size[0]}x{result.size[1]} pixels"
            )
        
        return 0
        
    except AutoflightError as e:
        print(f"Error: {e}", file=sys.stderr)
        if parsed.verbose:
            import traceback
            traceback.print_exc()
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if parsed.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
