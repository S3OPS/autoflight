# Autoflight Quick Reference Guide

## One-Command Setup & Run

```bash
./bootstrap.sh
```

This single command does everything:
- ✓ Creates virtual environment
- ✓ Installs all dependencies
- ✓ Runs tests
- ✓ Generates sample images
- ✓ Creates demo orthomosaic

## Common Commands

### Web Interface

The easiest way to use Autoflight is the built-in browser UI:

```bash
autoflight serve          # opens http://localhost:8080 automatically
# or
make serve
```

Drag & drop your aerial images, choose settings, click **Generate Orthomosaic**, then download the result as PNG or a self-contained HTML report.

### Using Make

```bash
make help          # Show all available commands
make setup         # Complete project setup
make test          # Run all tests
make demo          # Run demo with sample images
make serve         # Start the web interface
make all           # Setup, test, and demo
make clean         # Remove temporary files
```

### Using the CLI

```bash
# Activate virtual environment first
source .venv/bin/activate

# Run with autoflight command
autoflight /path/to/images output.jpg

# Or use Python module
python -m autoflight.orthomosaic /path/to/images output.jpg
```

### Development

```bash
make install-dev   # Install with development tools
make format        # Format code with black
make lint          # Run code linters
```

## Usage Examples

### Basic Usage

```bash
autoflight sample_images output/result.jpg
```

### Custom Images

```bash
autoflight /path/to/drone/photos output/orthomosaic.jpg
```

### Python API

```python
from autoflight.orthomosaic import create_orthomosaic

result = create_orthomosaic(
    input_dir="images/",
    output_path="output/mosaic.jpg"
)

print(f"Created from {result.image_count} images")
print(f"Size: {result.size[0]}x{result.size[1]}")
```

## Supported Formats

Input: `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff`
Output: `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff`, `.html` (self-contained HTML report)

> **Where to put images:** Copy your aerial photos into any local directory, then pass that
> directory path as the first argument. The `sample_images/` folder in the repo is ready to
> use for testing — just drop images there and run `autoflight sample_images output/result.jpg`.

## Requirements

- Python 3.8+
- OpenCV
- NumPy

All dependencies are automatically installed by `bootstrap.sh` or `make setup`.

## Troubleshooting

### Reset Environment

```bash
rm -rf .venv
./bootstrap.sh
```

### Check Installation

```bash
source .venv/bin/activate
python -c "import autoflight; print('OK')"
```

### Run Tests

```bash
make test
```

## Project Structure

```
autoflight/
├── bootstrap.sh              # One-command setup script
├── Makefile                  # Build automation
├── pyproject.toml           # Python package config
├── autoflight/              # Main package
│   ├── __init__.py
│   ├── cli.py               # CLI entry point (incl. `serve` subcommand)
│   ├── orthomosaic.py       # Core stitching API
│   ├── server.py            # Built-in web server
│   └── web/
│       └── index.html       # Browser UI
├── tests/                   # Test suite
├── scripts/                 # Utility scripts
└── sample_images/           # Demo images
```

## Links

- Repository: https://github.com/S3OPS/autoflight
- Issues: https://github.com/S3OPS/autoflight/issues
- Contributing: See CONTRIBUTING.md
