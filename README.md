# Autoflight

A professional-grade Python application for generating orthomosaic images from a folder of overlapping aerial photos. Built with OpenCV and designed for ease of use.

## Features

- 🚀 **One-Command Setup** - Install, configure, and run with a single command
- 🔄 **Automatic Image Stitching** - Seamlessly combines overlapping images into panoramic orthomosaics
- 📸 **Multiple Format Support** - Works with `.jpg`, `.jpeg`, `.png`, `.tif`, and `.tiff` files
- 🧪 **Tested & Reliable** - Comprehensive test coverage
- 🛠️ **Developer Friendly** - Modern Python packaging with type hints and code quality tools

## Quick Start

### Zero-Setup Run (Auto-Install Dependencies)

The easiest way to get started - just run it:

```bash
python -m autoflight.orthomosaic /path/to/images output.jpg
```

**No installation required!** Dependencies (OpenCV, NumPy) are automatically installed on first run.

To disable auto-install (e.g., in production):
```bash
export AUTOFLIGHT_NO_AUTO_INSTALL=1
```

### One-Command Setup and Run

For a complete setup with virtual environment:

```bash
./bootstrap.sh
```

This single command will:
1. ✅ Auto-install dependencies (create virtual environment, install packages)
2. ✅ Auto-configure the environment
3. ✅ Auto-setup the project
4. ✅ Auto-run a demo with sample images

### Manual Setup

If you prefer manual setup:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package
pip install -e .

# Run the demo
python -m autoflight.orthomosaic sample_images output/demo_orthomosaic.jpg
```

### Using Make

For common operations:

```bash
make setup      # Complete setup
make test       # Run tests
make demo       # Run demo
make all        # Setup, test, and demo
make help       # Show all available commands
```

## Usage

### Command Line

After installation, you can use the `autoflight` command:

```bash
autoflight /path/to/input_images /path/to/output/orthomosaic.jpg
```

Or use the Python module directly:

```bash
python -m autoflight.orthomosaic /path/to/input_images /path/to/output/orthomosaic.jpg
```

### Python API

You can also use autoflight as a library in your Python code:

```python
from autoflight.orthomosaic import create_orthomosaic

result = create_orthomosaic(
    input_dir="path/to/images",
    output_path="path/to/output.jpg"
)

print(f"Created orthomosaic: {result.output_path}")
print(f"Used {result.image_count} images")
print(f"Size: {result.size[0]}x{result.size[1]} pixels")
```

## Development

### Running Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Or with make:

```bash
make test
```

### Installing Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs additional tools for development:
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking
- `pytest` - Advanced testing

### Code Quality

```bash
make format    # Format code with black
make lint      # Run linters (flake8, mypy)
```

## Project Structure

```
autoflight/
├── autoflight/           # Main package
│   ├── __init__.py
│   └── orthomosaic.py    # Core orthomosaic functionality
├── tests/                # Test suite
│   └── test_orthomosaic.py
├── scripts/              # Utility scripts
│   ├── demo.sh          # Demo script
│   └── generate_sample_images.py
├── sample_images/        # Sample images for demo
├── bootstrap.sh          # One-command setup script
├── Makefile             # Common operations
├── pyproject.toml       # Python package configuration
├── requirements.txt     # Dependencies
└── README.md            # This file
```

## Requirements

- Python 3.8 or higher
- OpenCV (opencv-python) - **Auto-installed on first run**
- NumPy - **Auto-installed on first run**

### Auto-Installation Feature

Autoflight automatically installs required dependencies when you first import or run the module. This means you can:

1. **Just run it** - No need to manually install dependencies
2. **Skip setup** - Dependencies are installed automatically when needed
3. **Stay in control** - Set `AUTOFLIGHT_NO_AUTO_INSTALL=1` to disable auto-install

The auto-install feature:
- ✅ Checks for dependencies only once (cached)
- ✅ Only installs what's missing
- ✅ Silent when dependencies are already present
- ✅ Can be disabled for production/CI environments

To manually install dependencies (traditional approach):
```bash
pip install opencv-python numpy
# or
pip install -r requirements.txt
```

## How It Works

1. **Image Loading**: Reads all supported image formats from the input directory
2. **Feature Detection**: OpenCV identifies matching features across overlapping images
3. **Image Alignment**: Images are warped and aligned based on detected features
4. **Blending**: Seamlessly blends overlapping regions to create a smooth panorama
5. **Output**: Saves the final orthomosaic to the specified output path

## Troubleshooting

### Virtual Environment Issues

If you encounter issues with the virtual environment:

```bash
rm -rf .venv
./bootstrap.sh
```

### OpenCV Installation Problems

On some systems, you might need to install system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install python3-opencv libopencv-dev

# macOS
brew install opencv
```

### Image Stitching Failures

If stitching fails:
- Ensure images have sufficient overlap (typically 30-50%)
- Check that images are from the same scene/location
- Verify images are not too different in brightness or scale

## Contributing

Contributions are welcome! Please ensure:
- Tests pass: `make test`
- Code is formatted: `make format`
- Linting passes: `make lint`

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please visit the project repository.
