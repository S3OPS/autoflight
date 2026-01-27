"""Auto-install dependencies before they are needed."""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path


# Cache to avoid checking dependencies multiple times
_deps_checked = False


def _is_installed(module_name: str) -> bool:
    """Check if a module is installed."""
    return importlib.util.find_spec(module_name) is not None


def _install_package(package_name: str) -> None:
    """Install a package using pip.
    
    Args:
        package_name: Package specification (from hardcoded dependencies dict only).
    """
    # Only silence stdout, keep stderr for error messages
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", package_name, "--quiet"],
        stdout=subprocess.DEVNULL,
    )


def ensure_dependencies() -> None:
    """Ensure all required dependencies are installed.
    
    This function checks if required dependencies (opencv-python, numpy) are installed.
    If not, it automatically installs them unless disabled via environment variable.
    
    Environment Variables:
        AUTOFLIGHT_NO_AUTO_INSTALL: Set to any value to disable auto-installation.
    """
    global _deps_checked
    
    # Skip if already checked
    if _deps_checked:
        return
    
    # Skip if auto-install is disabled
    if os.environ.get("AUTOFLIGHT_NO_AUTO_INSTALL"):
        _deps_checked = True
        return
    
    # Define required dependencies (hardcoded for security)
    dependencies = {
        "cv2": "opencv-python>=4.9.0,<5.0",
        "numpy": "numpy>=1.26.0",
    }
    
    missing_deps = []
    for module_name, package_spec in dependencies.items():
        if not _is_installed(module_name):
            missing_deps.append((module_name, package_spec))
    
    if missing_deps:
        print("Auto-installing missing dependencies...", file=sys.stderr)
        print("(Set AUTOFLIGHT_NO_AUTO_INSTALL=1 to disable)", file=sys.stderr)
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
    
    _deps_checked = True
