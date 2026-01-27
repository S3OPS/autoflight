# Contributing to Autoflight

Thank you for your interest in contributing to Autoflight! This document provides guidelines and instructions for contributing.

## Getting Started

### One-Command Setup

The easiest way to get started:

```bash
./bootstrap.sh
```

This will set up everything you need to start contributing.

### Manual Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/S3OPS/autoflight.git
   cd autoflight
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the package in development mode with dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Running Tests

Always run tests before submitting changes:

```bash
make test
```

Or:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

### Code Quality

We maintain high code quality standards:

1. **Format your code** with Black:
   ```bash
   make format
   ```

2. **Run linters**:
   ```bash
   make lint
   ```

3. **Type checking** with mypy (if installed):
   ```bash
   mypy autoflight
   ```

### Code Style Guidelines

- Follow PEP 8 style guide
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use descriptive variable and function names
- Add docstrings to public functions and classes

## Making Changes

### Pull Request Process

1. Fork the repository
2. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Make your changes following the coding standards
4. Add or update tests for your changes
5. Ensure all tests pass: `make test`
6. Format your code: `make format`
7. Run linters: `make lint`
8. Commit your changes with a clear message:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

9. Push to your fork and submit a pull request

### Commit Message Guidelines

- Use clear, descriptive commit messages
- Start with a verb in the imperative mood (e.g., "Add", "Fix", "Update")
- Keep the first line under 50 characters
- Add a detailed description if necessary

Example:
```
Add support for GeoTIFF format

- Implement GeoTIFF reading functionality
- Add tests for GeoTIFF processing
- Update documentation
```

## Testing

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with the `test_` prefix
- Use `unittest` framework
- Aim for high test coverage

Example test:
```python
import unittest
from autoflight.orthomosaic import create_orthomosaic

class TestNewFeature(unittest.TestCase):
    def test_feature_works(self):
        # Test implementation
        self.assertTrue(True)
```

## Documentation

- Update README.md if you add new features
- Add docstrings to new functions and classes
- Update help messages for CLI changes

## Questions or Problems?

- Open an issue on GitHub
- Provide detailed information about your environment
- Include steps to reproduce any bugs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Autoflight! 🚀
