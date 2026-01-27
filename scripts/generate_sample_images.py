#!/usr/bin/env python3
"""Generate sample images for autoflight demo."""

import sys
from pathlib import Path

import cv2
import numpy as np


def generate_sample_images(output_dir: Path, num_images: int = 3) -> None:
    """Generate sample overlapping images for stitching demo."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a base pattern image
    rng = np.random.default_rng(42)
    base_img = rng.integers(50, 200, size=(400, 600, 3), dtype=np.uint8)
    
    # Add some distinctive patterns
    # Add circles
    cv2.circle(base_img, (150, 150), 50, (255, 100, 100), -1)
    cv2.circle(base_img, (450, 150), 40, (100, 255, 100), -1)
    cv2.circle(base_img, (300, 300), 60, (100, 100, 255), -1)
    
    # Add rectangles
    cv2.rectangle(base_img, (100, 250), (200, 350), (255, 255, 100), -1)
    cv2.rectangle(base_img, (400, 250), (500, 350), (255, 100, 255), -1)
    
    # Add text
    cv2.putText(base_img, "AUTOFLIGHT", (200, 200), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Generate overlapping images by shifting the base image
    shifts = [
        (0, 0),        # Original position
        (-100, 0),     # Shift left
        (100, 0),      # Shift right
    ]
    
    for i, (shift_x, shift_y) in enumerate(shifts[:num_images]):
        # Create transformation matrix for shifting
        shift_matrix = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
        shifted = cv2.warpAffine(base_img, shift_matrix, (base_img.shape[1], base_img.shape[0]))
        
        # Add some variation
        noise = rng.integers(-10, 10, size=shifted.shape, dtype=np.int16)
        shifted = np.clip(shifted.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Save image
        output_path = output_dir / f"sample_{i+1:02d}.jpg"
        cv2.imwrite(str(output_path), shifted)
        print(f"Generated: {output_path}")


if __name__ == "__main__":
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    sample_dir = project_root / "sample_images"
    
    # Check if sample images already exist
    if sample_dir.exists() and list(sample_dir.glob("*.jpg")):
        print(f"Sample images already exist in {sample_dir}")
        sys.exit(0)
    
    print(f"Generating sample images in {sample_dir}...")
    generate_sample_images(sample_dir)
    print("Sample images generated successfully!")
