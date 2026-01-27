"""Autoflight package - Professional-grade orthomosaic generation."""

# Auto-install dependencies before any imports
from autoflight._ensure_deps import ensure_dependencies

ensure_dependencies()

# Export main functionality
from autoflight.orthomosaic import create_orthomosaic, OrthomosaicResult

__all__ = ["create_orthomosaic", "OrthomosaicResult"]
__version__ = "1.1.0"
