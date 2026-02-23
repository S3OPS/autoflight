# Autoflight

A professional-grade Python application for generating orthomosaic images from a folder of overlapping aerial photos. Built with OpenCV and designed for ease of use.

## Features

- 🚀 **One-Command Setup** - Install, configure, and run with a single command
- ⚡ **Performance Optimized** - Parallel image loading for faster processing
- 🔄 **Automatic Image Stitching** - Seamlessly combines overlapping images into panoramic orthomosaics
- 📸 **Multiple Format Support** - Works with `.jpg`, `.jpeg`, `.png`, `.tif`, and `.tiff` files
- 🧪 **Tested & Reliable** - Comprehensive test coverage with 22+ tests
- 🛠️ **Developer Friendly** - Modern Python packaging with type hints and code quality tools
- 🔒 **Security Focused** - Input validation and secure dependency management
- 🎯 **Modular Architecture** - Clean separation of concerns for maintainability

## 📁 Image Input Guide: Where to Put Your Images

This section explains **exactly** where to place your images and how to organize them for processing.

### Step 1 — Choose an Input Directory

You have two options:

**Option A: Use the included `sample_images/` directory** *(great for testing)*

The repository already ships with three overlapping aerial sample images ready to use:

```
autoflight/
└── sample_images/          ← Drop your images here for quick testing
    ├── sample_01.jpg       (included — 3 overlapping samples)
    ├── sample_02.jpg       (included)
    └── sample_03.jpg       (included)
```

Simply copy your own `.jpg`, `.jpeg`, `.png`, `.tif`, or `.tiff` files into `sample_images/` alongside the existing samples (or replace them), then run:

```bash
autoflight sample_images output/orthomosaic.jpg
```

**Option B: Create a dedicated directory anywhere on your system** *(recommended for real projects)*

```bash
# Create a folder for your drone photos
mkdir my_drone_photos

# Copy your images into it
cp /path/to/drone/downloads/*.jpg my_drone_photos/

# Run autoflight, pointing at your folder
autoflight my_drone_photos output/orthomosaic.jpg
```

### Step 2 — Supported File Formats

Place any of the following file types in your input directory:

| Format | Extension(s) | Notes |
|--------|-------------|-------|
| JPEG | `.jpg`, `.jpeg` | ✅ Recommended — most common drone format |
| PNG | `.png` | Lossless, but larger file size |
| TIFF | `.tif`, `.tiff` | Professional format, supports georeferencing |

> **Tip:** All other file types (`.txt`, `.xml`, `.log`, GPS logs, etc.) in the same folder are **automatically ignored** — no need to move them.

### Step 3 — Image Requirements for Best Results

For successful stitching your images must:

- **Overlap by 30–70%** — Each photo should share content with the photos next to it. Drone survey missions typically use 60–80% front overlap and 30–60% side overlap.
- **Cover the same scene** — All images should be of the same geographic area taken in one flight session.
- **Have consistent exposure** — Avoid mixing heavily over-exposed or under-exposed shots with normal ones. Bright overcast days produce the best results.
- **Be in focus** — Blurry or motion-blurred images will cause stitching failures.
- **Have at least 2 images** — A single image is returned unchanged; you need at least 2 overlapping images to generate a mosaic.

### Recommended Project Layout

```
my_project/
├── input_images/           ← All source aerial photos go here
│   ├── DJI_0001.jpg
│   ├── DJI_0002.jpg
│   ├── DJI_0003.jpg
│   └── ...                 (any mix of .jpg/.png/.tif is fine)
└── output/                 ← Created automatically by autoflight
    └── orthomosaic.jpg     ← Final stitched result
```

```bash
# Process your images
autoflight input_images output/orthomosaic.jpg
```

### Quick Validation (Dry Run)

Before committing to a long stitching job, check that autoflight can see your images:

```bash
# Validate your input directory without processing
autoflight input_images output/orthomosaic.jpg --dry-run
```

This prints the number of images found and the output path that would be used, without doing any actual stitching.

---

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
# Basic usage
autoflight /path/to/input_images /path/to/output/orthomosaic.jpg

# With options
autoflight /path/to/images output.jpg --verbose --mode panorama

# Disable parallel loading (lower memory usage)
autoflight /path/to/images output.jpg --no-parallel

# Quiet mode (only show errors)
autoflight /path/to/images output.jpg --quiet
```

Or use the Python module directly:

```bash
python -m autoflight.orthomosaic /path/to/input_images /path/to/output/orthomosaic.jpg
```

**CLI Options:**
- `--mode {panorama,scans}` - Stitching mode (default: panorama)
- `--no-parallel` - Disable parallel image loading (slower but uses less memory)
- `-v, --verbose` - Enable verbose output with detailed logging
- `-q, --quiet` - Suppress all output except errors
- `-h, --help` - Show help message

### Python API

You can also use autoflight as a library in your Python code:

```python
from autoflight import create_orthomosaic

# Basic usage
result = create_orthomosaic(
    input_dir="path/to/images",
    output_path="path/to/output.jpg"
)

# With options for performance and logging
result = create_orthomosaic(
    input_dir="path/to/images",
    output_path="path/to/output.jpg",
    parallel=True,      # Enable parallel image loading (default)
    verbose=True,       # Enable detailed logging
    mode="panorama"     # Stitching mode: "panorama" or "scans"
)

print(f"✓ Created orthomosaic: {result.output_path}")
print(f"  Images used: {result.image_count}")
print(f"  Size: {result.size[0]}x{result.size[1]} pixels")
```

**API Parameters:**
- `input_dir` - Directory containing input images (str or Path)
- `output_path` - Path where to save the orthomosaic (str or Path)
- `parallel` - Enable parallel image loading for better performance (default: True)
- `verbose` - Enable verbose logging (default: False)
- `mode` - Stitching mode: "panorama" for standard panoramas or "scans" for scanned images (default: "panorama")

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
│   ├── __init__.py       # Package initialization and exports
│   ├── _ensure_deps.py   # Auto-dependency installation
│   ├── orthomosaic.py    # Main orchestration and CLI
│   ├── image_loader.py   # Image loading with parallel support
│   ├── stitcher.py       # Image stitching algorithms
│   └── output.py         # Output file handling
├── tests/                # Test suite
│   ├── test_orthomosaic.py    # Integration tests
│   ├── test_auto_install.py   # Auto-install tests
│   └── test_modules.py        # Unit tests for modules
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

**Note:** Autoflight now supports NumPy 2.x for improved performance and security.

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

1. **Image Loading**: Loads all supported image formats from the input directory
   - Supports parallel loading for improved performance
   - Validates image paths for security
   - Filters supported formats (.jpg, .jpeg, .png, .tif, .tiff)
2. **Feature Detection**: OpenCV identifies matching features across overlapping images
3. **Image Alignment**: Images are warped and aligned based on detected features
4. **Blending**: Seamlessly blends overlapping regions to create a smooth panorama
5. **Output**: Saves the final orthomosaic to the specified output path

## Performance

- **Parallel Image Loading**: By default, images are loaded in parallel using multiple threads
- **Memory Efficient**: Use `--no-parallel` flag for sequential loading in memory-constrained environments
- **Optimized Processing**: Efficient image stitching with OpenCV's panorama algorithms
- **Scalable**: Handles large image sets with configurable worker pools

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

## Roadmap

See [THE_ONE_RING.md](THE_ONE_RING.md) for the comprehensive development roadmap covering:
- 🚀 **Optimization** - Performance improvements
- 🏕️ **Refactoring** - Code organization
- 🧝 **Modularization** - Component separation
- 🔍 **Security Audit** - Vulnerability assessment
- ⚔️ **Enhancements** - Feature upgrades

## Contributing

Contributions are welcome! Please ensure:
- Tests pass: `make test`
- Code is formatted: `make format`
- Linting passes: `make lint`

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please visit the project repository.
