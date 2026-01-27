#!/bin/bash
#
# Demo script for autoflight
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Autoflight Demo${NC}"
echo "================"
echo ""

# Generate sample images if needed
if [ ! -d "sample_images" ] || [ -z "$(ls -A sample_images/*.jpg 2>/dev/null)" ]; then
    echo "Generating sample images..."
    python3 scripts/generate_sample_images.py
fi

# Create output directory
mkdir -p output

# Run the orthomosaic generation
echo ""
echo "Running orthomosaic generation..."
echo "Input: sample_images/"
echo "Output: output/demo_orthomosaic.jpg"
echo ""

python -m autoflight.orthomosaic sample_images output/demo_orthomosaic.jpg

echo ""
echo -e "${GREEN}Demo complete!${NC}"
echo "Output saved to: output/demo_orthomosaic.jpg"
echo ""
