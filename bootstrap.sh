#!/bin/bash
#
# Autoflight Bootstrap Script
# One-command setup and run: ./bootstrap.sh
#
# This script will:
# 1. Auto-install dependencies (create venv, install packages)
# 2. Auto-configure the environment
# 3. Auto-setup the project
# 4. Auto-run a demo

set -e  # Exit on error

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Print banner
echo "============================================"
echo "  Autoflight - One-Command Setup & Run"
echo "============================================"
echo ""

# Step 1: Check Python installation
info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
info "Found Python $PYTHON_VERSION"

# Step 2: Create virtual environment
if [ ! -d ".venv" ]; then
    info "Creating virtual environment..."
    python3 -m venv .venv
    success "Virtual environment created"
else
    info "Virtual environment already exists"
fi

# Step 3: Activate virtual environment
info "Activating virtual environment..."
source .venv/bin/activate

# Step 4: Upgrade pip
info "Upgrading pip..."
pip install --upgrade pip --quiet

# Step 5: Install package and dependencies
info "Installing autoflight package and dependencies..."
pip install -e . --quiet
success "Dependencies installed"

# Step 6: Run tests
info "Running tests to verify installation..."
if python -m unittest discover -s tests -p "test_*.py" -v; then
    success "All tests passed"
else
    warning "Some tests failed, but continuing..."
fi

# Step 7: Generate sample images if they don't exist
info "Checking for sample images..."
python3 scripts/generate_sample_images.py
success "Sample images ready"

# Step 8: Run demo
info "Running demo orthomosaic generation..."
echo ""
python -m autoflight.orthomosaic sample_images output/demo_orthomosaic.jpg

echo ""
echo "============================================"
success "Autoflight setup and demo complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Activate environment: source .venv/bin/activate"
echo "  2. Run with your images: autoflight /path/to/images output.jpg"
echo "  3. Or use: python -m autoflight.orthomosaic /path/to/images output.jpg"
echo "  4. Validate installation: make validate"
echo ""
echo "For more commands, see: make help"
echo ""
