"""Configuration management for autoflight package.

This module provides centralized configuration management for all
autoflight settings, including performance tuning, security limits,
and output options.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from autoflight.security import SecurityLimits


@dataclass
class PerformanceConfig:
    """Performance-related configuration settings.
    
    Attributes:
        parallel_loading: Whether to load images in parallel
        max_workers: Maximum number of parallel workers for image loading
        memory_limit_mb: Optional memory limit in megabytes
    """
    parallel_loading: bool = True
    max_workers: int = 4
    memory_limit_mb: Optional[int] = None


@dataclass
class OutputConfig:
    """Output-related configuration settings.
    
    Attributes:
        jpeg_quality: JPEG quality setting (1-100, default: 95)
        png_compression: PNG compression level (0-9, default: 3)
        create_dirs: Whether to create parent directories for output
    """
    jpeg_quality: int = 95
    png_compression: int = 3
    create_dirs: bool = True
    
    def __post_init__(self) -> None:
        """Validate configuration values."""
        if not 1 <= self.jpeg_quality <= 100:
            raise ValueError(f"jpeg_quality must be 1-100, got {self.jpeg_quality}")
        if not 0 <= self.png_compression <= 9:
            raise ValueError(f"png_compression must be 0-9, got {self.png_compression}")


@dataclass
class StitchingConfig:
    """Stitching-related configuration settings.
    
    Attributes:
        mode: Stitching mode ("panorama" or "scans")
        try_use_gpu: Whether to attempt GPU acceleration if available
    """
    mode: str = "panorama"
    try_use_gpu: bool = False
    
    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.mode not in {"panorama", "scans"}:
            raise ValueError(f"mode must be 'panorama' or 'scans', got {self.mode}")


# Type alias for progress callbacks
ProgressCallback = Callable[[float, str], None]


@dataclass
class AutoflightConfig:
    """Main configuration class for autoflight.
    
    This class combines all configuration settings and provides
    a centralized way to configure the autoflight package.
    
    Attributes:
        performance: Performance-related settings
        output: Output-related settings
        stitching: Stitching-related settings
        security: Security limits
        verbose: Whether to enable verbose logging
        progress_callback: Optional callback for progress reporting
    """
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    stitching: StitchingConfig = field(default_factory=StitchingConfig)
    security: SecurityLimits = field(default_factory=SecurityLimits)
    verbose: bool = False
    progress_callback: Optional[ProgressCallback] = None
    
    @classmethod
    def from_env(cls) -> "AutoflightConfig":
        """Create configuration from environment variables.
        
        Supported environment variables:
        - AUTOFLIGHT_PARALLEL: Enable/disable parallel loading (1/0)
        - AUTOFLIGHT_MAX_WORKERS: Maximum parallel workers
        - AUTOFLIGHT_JPEG_QUALITY: JPEG output quality
        - AUTOFLIGHT_MODE: Stitching mode
        - AUTOFLIGHT_VERBOSE: Enable verbose logging (1/0)
        
        Returns:
            AutoflightConfig instance configured from environment
        """
        config = cls()
        
        # Performance settings
        if "AUTOFLIGHT_PARALLEL" in os.environ:
            config.performance.parallel_loading = os.environ["AUTOFLIGHT_PARALLEL"] == "1"
        if "AUTOFLIGHT_MAX_WORKERS" in os.environ:
            config.performance.max_workers = int(os.environ["AUTOFLIGHT_MAX_WORKERS"])
        
        # Output settings
        if "AUTOFLIGHT_JPEG_QUALITY" in os.environ:
            config.output.jpeg_quality = int(os.environ["AUTOFLIGHT_JPEG_QUALITY"])
        
        # Stitching settings
        if "AUTOFLIGHT_MODE" in os.environ:
            config.stitching.mode = os.environ["AUTOFLIGHT_MODE"]
        
        # General settings
        if "AUTOFLIGHT_VERBOSE" in os.environ:
            config.verbose = os.environ["AUTOFLIGHT_VERBOSE"] == "1"
        
        return config
    
    def with_progress(self, callback: ProgressCallback) -> "AutoflightConfig":
        """Return a new config with a progress callback set.
        
        Args:
            callback: Progress callback function(progress: float, message: str)
            
        Returns:
            New AutoflightConfig with the callback set
        """
        return AutoflightConfig(
            performance=self.performance,
            output=self.output,
            stitching=self.stitching,
            security=self.security,
            verbose=self.verbose,
            progress_callback=callback,
        )


# Global default configuration
_default_config: Optional[AutoflightConfig] = None


def get_default_config() -> AutoflightConfig:
    """Get the global default configuration.
    
    Returns:
        Default AutoflightConfig instance
    """
    global _default_config
    if _default_config is None:
        _default_config = AutoflightConfig.from_env()
    return _default_config


def set_default_config(config: AutoflightConfig) -> None:
    """Set the global default configuration.
    
    Args:
        config: Configuration to set as default
    """
    global _default_config
    _default_config = config
