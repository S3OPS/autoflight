"""Command-line interface for autoflight.

This module provides the CLI for the autoflight orthomosaic generation tool.
It separates CLI concerns from the core API, allowing for clean programmatic usage.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Iterable, Optional

from autoflight.config import AutoflightConfig, PerformanceConfig, OutputConfig, StitchingConfig


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Generate an orthomosaic from overlapping aerial images",
        epilog="Example: %(prog)s /path/to/images output.jpg",
        prog="autoflight",
    )
    
    # Required arguments
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing input images (jpg, jpeg, png, tif, tiff)"
    )
    parser.add_argument(
        "output_path",
        type=Path,
        help="Path where to save the orthomosaic image (supports .jpg, .jpeg, .png, .tif, .tiff, .html)"
    )
    
    # Stitching options
    parser.add_argument(
        "--mode",
        choices=["panorama", "scans"],
        default="panorama",
        help="Stitching mode: 'panorama' for standard panoramas, 'scans' for scanned images (default: panorama)"
    )
    
    # Performance options
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel image loading (slower but uses less memory)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        metavar="N",
        help="Number of parallel workers for image loading (default: 4)"
    )
    
    # Output options
    parser.add_argument(
        "--quality",
        type=int,
        default=95,
        metavar="Q",
        help="JPEG quality setting, 1-100 (default: 95)"
    )
    
    # Logging options
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
    
    # Advanced options
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Show progress bar during processing"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs without processing"
    )
    
    return parser


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure logging based on CLI options.
    
    Args:
        verbose: Enable debug-level logging
        quiet: Only show errors
    """
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    
    # Only configure if not already configured
    if not logging.getLogger().handlers:
        logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    else:
        logging.getLogger().setLevel(level)


def config_from_args(args: argparse.Namespace) -> AutoflightConfig:
    """Create an AutoflightConfig from parsed arguments.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        AutoflightConfig configured from arguments
    """
    performance = PerformanceConfig(
        parallel_loading=not args.no_parallel,
        max_workers=args.workers,
    )
    
    output = OutputConfig(
        jpeg_quality=args.quality,
    )
    
    stitching = StitchingConfig(
        mode=args.mode,
    )
    
    return AutoflightConfig(
        performance=performance,
        output=output,
        stitching=stitching,
        verbose=args.verbose,
    )


def print_progress(progress: float, message: str) -> None:
    """Print progress to stdout.
    
    Args:
        progress: Progress value from 0.0 to 1.0
        message: Status message
    """
    bar_width = 40
    filled = int(bar_width * progress)
    bar = "█" * filled + "░" * (bar_width - filled)
    percent = int(progress * 100)
    print(f"\r[{bar}] {percent}% - {message}", end="", flush=True)
    if progress >= 1.0:
        print()  # Newline at completion


def run(args: Iterable[str] | None = None) -> int:
    """Run the CLI.
    
    Args:
        args: Command-line arguments (defaults to sys.argv)
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = create_parser()
    parsed = parser.parse_args(list(args) if args is not None else None)
    
    # Setup logging
    setup_logging(parsed.verbose, parsed.quiet)
    
    # Handle dry-run mode
    if parsed.dry_run:
        # Just validate inputs
        if not parsed.input_dir.exists():
            print(f"Error: Input directory does not exist: {parsed.input_dir}", file=sys.stderr)
            return 1
        if not parsed.input_dir.is_dir():
            print(f"Error: Input path is not a directory: {parsed.input_dir}", file=sys.stderr)
            return 1
        print(f"Dry run: Would process images from {parsed.input_dir}")
        print(f"         Output would be saved to {parsed.output_path}")
        return 0
    
    # Create config from args
    config = config_from_args(parsed)
    
    # Add progress callback if requested
    if parsed.progress:
        config = config.with_progress(print_progress)
    
    try:
        # Import here to avoid circular imports
        from autoflight.orthomosaic import create_orthomosaic
        
        result = create_orthomosaic(
            parsed.input_dir,
            parsed.output_path,
            parallel=config.performance.parallel_loading,
            verbose=config.verbose,
            mode=config.stitching.mode,
            quality=config.output.jpeg_quality,
            progress_callback=config.progress_callback,
        )
        
        if not parsed.quiet:
            print(
                f"✓ Orthomosaic created: {result.output_path}\n"
                f"  Images used: {result.image_count}\n"
                f"  Size: {result.size[0]}x{result.size[1]} pixels"
            )
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if parsed.verbose:
            import traceback
            traceback.print_exc()
        return 1


def run_serve(args: Iterable[str] | None = None) -> int:
    """Run the web interface server.

    Args:
        args: Arguments for the serve subcommand (defaults to sys.argv after 'serve')

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    from autoflight.server import run_server

    parser = argparse.ArgumentParser(
        description="Start the autoflight web interface server",
        prog="autoflight serve",
        epilog="Example: %(prog)s --port 8080",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        metavar="HOST",
        help="Hostname to bind to (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        metavar="PORT",
        help="TCP port to listen on (default: 8080)",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not automatically open a browser window",
    )

    parsed = parser.parse_args(list(args) if args is not None else [])
    try:
        run_server(host=parsed.host, port=parsed.port, open_browser=not parsed.no_open)
        return 0
    except OSError as e:
        print(f"Error: Could not start server: {e}", file=sys.stderr)
        return 1


def main(args: Iterable[str] | None = None) -> int:
    """Main entry point for the CLI.

    Dispatches to the ``serve`` subcommand when the first argument is
    ``"serve"``; otherwise runs the standard stitching pipeline.

    Args:
        args: Command-line arguments (defaults to sys.argv)

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    argv = list(args) if args is not None else sys.argv[1:]
    if argv and argv[0] == "serve":
        return run_serve(argv[1:])
    # Pass None so argparse uses sys.argv when args was not supplied explicitly
    return run(args if args is not None else None)


if __name__ == "__main__":
    raise SystemExit(main())
