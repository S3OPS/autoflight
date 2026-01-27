"""Auto-install dependencies before they are needed."""

import importlib.util
import subprocess
import sys
from pathlib import Path


def _is_installed(module_name: str) -> bool:
    """Check if a module is installed."""
    return importlib.util.find_spec(module_name) is not None


def _install_package(package_name: str) -> None:
    """Install a package using pip."""
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", package_name, "--quiet"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def ensure_dependencies() -> None:
    """Ensure all required dependencies are installed."""
    # Define required dependencies
    dependencies = {
        "cv2": "opencv-python>=4.9.0,<5.0",
        "numpy": "numpy>=1.26.0,<2.0",
    }
    
    missing_deps = []
    for module_name, package_spec in dependencies.items():
        if not _is_installed(module_name):
            missing_deps.append((module_name, package_spec))
    
    if missing_deps:
        print("Auto-installing missing dependencies...", file=sys.stderr)
        for module_name, package_spec in missing_deps:
            print(f"  Installing {package_spec}...", file=sys.stderr)
            try:
                _install_package(package_spec)
                print(f"  ✓ {module_name} installed", file=sys.stderr)
            except subprocess.CalledProcessError as e:
                print(
                    f"  ✗ Failed to install {package_spec}: {e}",
                    file=sys.stderr,
                )
                raise RuntimeError(
                    f"Failed to auto-install dependency {package_spec}. "
                    f"Please install manually: pip install {package_spec}"
                ) from e
        print("Dependencies installed successfully!", file=sys.stderr)
