.PHONY: help install install-dev test lint format clean run demo setup all validate

# Default target
help:
	@echo "Autoflight - Orthomosaic Image Generator"
	@echo ""
	@echo "Available targets:"
	@echo "  make setup        - Complete setup: create venv, install deps"
	@echo "  make install      - Install package dependencies"
	@echo "  make install-dev  - Install package with dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make validate     - Validate installation"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code with black"
	@echo "  make demo         - Run demo with sample images"
	@echo "  make run          - Run the application (requires INPUT and OUTPUT env vars)"
	@echo "  make clean        - Clean temporary files and cache"
	@echo "  make all          - Setup, test, and run demo"
	@echo ""

# Complete setup
setup:
	@echo "Setting up autoflight..."
	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv .venv; \
	fi
	@echo "Installing dependencies..."
	@. .venv/bin/activate && pip install --upgrade pip && pip install -e .
	@echo "Setup complete! Activate with: source .venv/bin/activate"

# Install package
install:
	pip install -e .

# Install package with dev dependencies
install-dev:
	pip install -e ".[dev]"

# Run tests
test:
	@if [ -d ".venv" ]; then \
		. .venv/bin/activate && python -m unittest discover -s tests -p "test_*.py"; \
	else \
		python -m unittest discover -s tests -p "test_*.py"; \
	fi

# Run linters (if dev deps installed)
lint:
	@if [ -d ".venv" ]; then \
		. .venv/bin/activate && \
		if command -v flake8 >/dev/null 2>&1; then \
			flake8 autoflight tests --max-line-length=100 --ignore=E203,W503; \
		else \
			echo "flake8 not installed. Run 'make install-dev' first."; \
		fi && \
		if command -v mypy >/dev/null 2>&1; then \
			mypy autoflight; \
		else \
			echo "mypy not installed. Run 'make install-dev' first."; \
		fi; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
	fi

# Format code
format:
	@if [ -d ".venv" ]; then \
		. .venv/bin/activate && \
		if command -v black >/dev/null 2>&1; then \
			black autoflight tests; \
		else \
			echo "black not installed. Run 'make install-dev' first."; \
		fi; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
	fi

# Run demo
demo:
	@echo "Running autoflight demo..."
	@if [ -d ".venv" ]; then \
		. .venv/bin/activate && bash scripts/demo.sh; \
	else \
		bash scripts/demo.sh; \
	fi

# Run with custom input/output
run:
	@if [ -z "$(INPUT)" ] || [ -z "$(OUTPUT)" ]; then \
		echo "Usage: make run INPUT=/path/to/images OUTPUT=/path/to/output.jpg"; \
		exit 1; \
	fi
	@if [ -d ".venv" ]; then \
		. .venv/bin/activate && python -m autoflight.orthomosaic $(INPUT) $(OUTPUT); \
	else \
		python -m autoflight.orthomosaic $(INPUT) $(OUTPUT); \
	fi

# Clean temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/

# Do everything: setup, test, demo
all: setup test demo

# Validate installation
validate:
	@bash scripts/validate.sh
