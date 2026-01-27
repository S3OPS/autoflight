# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
