# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-27

### Added - Optimization & Modularization
- **Parallel Image Loading** - Significantly faster processing with multi-threaded image loading
  - Configurable worker pool with `max_workers` parameter
  - Automatic parallel processing for multiple images
  - Falls back to sequential loading when appropriate
- **Modular Architecture** - Clean separation of concerns
  - `image_loader.py` - Image loading with parallel support and validation
  - `stitcher.py` - Image stitching algorithms with better error messages
  - `output.py` - Output file handling with directory creation
- **Enhanced CLI Options**
  - `--mode {panorama,scans}` - Choose stitching algorithm
  - `--no-parallel` - Disable parallel loading for memory-constrained systems
  - `-v, --verbose` - Enable detailed logging
  - `-q, --quiet` - Suppress non-error output
- **Logging Support** - Comprehensive logging throughout the application
- **Python API Enhancements** - New parameters for `create_orthomosaic()`
  - `parallel` - Enable/disable parallel loading
  - `verbose` - Control logging level
  - `mode` - Select stitching mode

### Security
- **Updated NumPy Support** - Now supports NumPy 2.x (removed upper bound constraint)
  - Fixes compatibility issues with latest OpenCV
  - Improved security with latest NumPy versions
- **Input Validation** - Path traversal protection and validation
  - `validate_path()` function for secure path handling
  - Comprehensive path existence and type checking
- **Secure Subprocess Usage** - Confirmed safe with hardcoded dependencies only

### Improved
- **Better Error Messages** - Detailed, context-aware error messages
  - Specific stitching failure reasons (homography, camera params, etc.)
  - Clear validation error messages
  - Helpful suggestions for common issues
- **Type Hints** - Comprehensive type annotations throughout codebase
- **Code Quality** - Improved organization and maintainability
  - Better separation of concerns
  - Consistent naming conventions
  - Comprehensive docstrings
- **Performance** - Optimized image loading and format detection
  - Path-based format filtering before loading
  - Efficient parallel processing
  - Reduced memory footprint options

### Testing
- **Expanded Test Coverage** - 22+ tests covering all modules
  - `test_modules.py` - Comprehensive unit tests for new modules
  - Tests for parallel and sequential loading
  - Input validation tests
  - Error handling tests
- **Better Test Organization** - Separate test classes for each module

### Documentation
- **Updated README.md** - Enhanced with new features and examples
  - CLI options documentation
  - API parameters reference
  - Performance tips
  - Modular architecture overview
- **API Documentation** - Comprehensive docstrings for all public functions
- **This CHANGELOG** - Detailed documentation of changes

## [1.0.0] - 2024-01-27

### Added
- **One-command setup and run** via `bootstrap.sh` script
  - Auto-installs dependencies (creates venv, installs packages)
  - Auto-configures environment
  - Auto-sets up project
  - Auto-runs demo with sample images
- Modern Python packaging with `pyproject.toml`
- Comprehensive `Makefile` with common operations:
  - `make setup` - Complete project setup
  - `make test` - Run tests
  - `make demo` - Run demo
  - `make all` - Setup, test, and demo
  - `make help` - Show all available commands
- Command-line interface via `autoflight` command
- Sample image generation for demos
- Development dependencies (black, flake8, mypy, pytest)
- Code quality tool configurations
- Comprehensive documentation:
  - Enhanced README.md with quick start guide
  - CONTRIBUTING.md with development guidelines
  - LICENSE (MIT)
  - CHANGELOG.md

### Improved
- Project structure and organization
- `.gitignore` with comprehensive exclusions
- Documentation with better examples and usage instructions
- Developer experience with automated setup

### Technical Enhancements
- Package discovery configuration to exclude non-package directories
- Proper console script entry point
- Support for both CLI and Python API usage
- Better error handling and user feedback

## [0.1.0] - Initial Release

### Features
- Basic orthomosaic generation from overlapping images
- Support for multiple image formats (.jpg, .jpeg, .png, .tif, .tiff)
- OpenCV-based image stitching
- Basic test coverage
