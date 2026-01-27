"""Orthomosaic generation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

import cv2
import numpy as np


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}


@dataclass
class OrthomosaicResult:
    output_path: Path
    image_count: int
    size: tuple[int, int]


def _load_images(input_dir: Path) -> List[np.ndarray]:
    images: List[np.ndarray] = []
    for path in sorted(input_dir.iterdir()):
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(f"Failed to load image: {path}")
        images.append(image)
    if not images:
        raise ValueError(f"No supported images found in {input_dir}")
    return images


def _stitch(images: Sequence[np.ndarray]) -> np.ndarray:
    stitcher = cv2.Stitcher_create(cv2.STITCHER_PANORAMA)
    status, stitched = stitcher.stitch(list(images))
    if status != cv2.Stitcher_OK or stitched is None:
        raise RuntimeError(f"Stitching failed with status {status}")
    return stitched


def create_orthomosaic(input_dir: Path | str, output_path: Path | str) -> OrthomosaicResult:
    """Create an orthomosaic from images in input_dir and write to output_path."""
    input_path = Path(input_dir)
    output_path = Path(output_path)
    images = _load_images(input_path)
    stitched = _stitch(images)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output_path), stitched):
        raise RuntimeError(f"Failed to write output image to {output_path}")
    height, width = stitched.shape[:2]
    return OrthomosaicResult(output_path=output_path, image_count=len(images), size=(width, height))


def main(args: Iterable[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Generate an orthomosaic from input images")
    parser.add_argument("input_dir", type=Path, help="Directory containing input images")
    parser.add_argument("output_path", type=Path, help="Path to write the orthomosaic image")
    parsed = parser.parse_args(list(args) if args is not None else None)

    result = create_orthomosaic(parsed.input_dir, parsed.output_path)
    print(
        f"Wrote orthomosaic to {result.output_path} "
        f"using {result.image_count} images ({result.size[0]}x{result.size[1]})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
