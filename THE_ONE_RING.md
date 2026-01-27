# The One Ring 💍

> *"One Ring to rule them all, One Ring to find them,*  
> *One Ring to bring them all, and in the darkness bind them."*

A comprehensive roadmap for Autoflight's journey to excellence. This document examines the entire repository and proposes the next steps for optimization, refactoring, modularization, security auditing, and enhancement.

---

## Table of Contents

1. [Optimize: Make the Journey Faster](#1-optimize-make-the-journey-faster)
2. [Refactor: Clean Up the Camp](#2-refactor-clean-up-the-camp)
3. [Modularize: Break Up the Fellowship](#3-modularize-break-up-the-fellowship)
4. [Audit: Inspect the Ranks](#4-audit-inspect-the-ranks)
5. [Enhance and Upgrade](#5-enhance-and-upgrade)
6. [Next Steps Summary](#6-next-steps-summary)

---

## 1. Optimize: Make the Journey Faster 🚀

> *"Don't take the long way around the mountain; use the Great Eagles."*

### Current State
The project already implements parallel image loading with configurable worker pools. However, there are opportunities for further optimization.

### Recommendations

#### 1.1 Image Loading Optimizations (Priority: High)
- [ ] **Implement lazy loading** - Load images on-demand rather than all at once
- [ ] **Add image caching** - Cache processed images to avoid redundant I/O operations
- [ ] **Memory-mapped file access** - Use `numpy.memmap` for large image files to reduce memory footprint
- [ ] **Progressive loading** - Load thumbnails first for preview, then full resolution

#### 1.2 Processing Pipeline Optimizations (Priority: High)
- [ ] **GPU acceleration** - Integrate CUDA support via OpenCV's GPU module for faster stitching
- [ ] **Multi-scale processing** - Process at lower resolution first, then refine
- [ ] **Streaming architecture** - Process images as they load rather than waiting for all

#### 1.3 I/O Optimizations (Priority: Medium)
- [ ] **Async file I/O** - Use `aiofiles` for non-blocking file operations
- [ ] **Output format optimization** - Allow JPEG quality settings to balance size vs speed
- [ ] **Batch output writing** - Write tiles in parallel for large orthomosaics

#### 1.4 Memory Management (Priority: Medium)
- [ ] **Configurable memory limits** - Allow users to set maximum memory usage
- [ ] **Automatic image downscaling** - Reduce resolution when memory is constrained
- [ ] **Garbage collection optimization** - Explicit cleanup after processing large images

### Quick Wins
```python
# Example: Add JPEG quality parameter to output.py
def save_image(
    image: np.ndarray,
    output_path: Path,
    quality: int = 95,
    create_dirs: bool = True,
) -> None:
    """Save with configurable quality for JPEG files."""
    if output_path.suffix.lower() in {'.jpg', '.jpeg'}:
        cv2.imwrite(str(output_path), image, [cv2.IMWRITE_JPEG_QUALITY, quality])
```

---

## 2. Refactor: Clean Up the Camp 🏕️

> *"Keep the same mission, but organize the supplies so they aren't a mess."*

### Current State
The codebase is well-organized with clear separation into modules. However, some areas could benefit from cleanup.

### Recommendations

#### 2.1 Code Style Consistency (Priority: Medium)
- [ ] **Standardize logging** - Some modules use `logger.info()`, others use `print()`. Standardize to logging
- [ ] **Consistent error handling** - Create custom exception classes for better error categorization
- [ ] **Type hint completeness** - Add missing type hints (e.g., return types for some functions)

#### 2.2 Configuration Management (Priority: Medium)
- [ ] **Centralize configuration** - Create a `config.py` module for all configurable parameters
- [ ] **Environment variable support** - Expand beyond `AUTOFLIGHT_NO_AUTO_INSTALL`
- [ ] **Configuration file support** - Allow `.autoflightrc` or `autoflight.toml` for project settings

#### 2.3 Error Handling Improvements (Priority: High)
```python
# Proposed: autoflight/exceptions.py
class AutoflightError(Exception):
    """Base exception for all autoflight errors."""
    pass

class ImageLoadError(AutoflightError):
    """Raised when image loading fails."""
    pass

class StitchingError(AutoflightError):
    """Raised when image stitching fails."""
    pass

class OutputError(AutoflightError):
    """Raised when output operations fail."""
    pass
```

#### 2.4 Logging Improvements (Priority: Medium)
- [ ] **Structured logging** - Add JSON logging option for production environments
- [ ] **Progress callbacks** - Allow external progress tracking for GUI integration
- [ ] **Timing metrics** - Add performance timing to logs for optimization tracking

### Quick Wins
- Add `__all__` exports to all modules for explicit public API
- Add `py.typed` marker file for PEP 561 compliance
- Standardize docstring format (Google style consistently)

---

## 3. Modularize: Break Up the Fellowship 🧝

> *"Instead of one giant group, give Aragorn, Legolas, and Gimli their own specific tasks."*

### Current State
The project has a good modular structure with:
- `image_loader.py` - Image loading operations
- `stitcher.py` - Image stitching algorithms
- `output.py` - Output file handling
- `orthomosaic.py` - Main orchestration

### Recommendations

#### 3.1 Feature Detection Module (Priority: High)
Extract feature detection into a separate module for flexibility:
```
autoflight/
├── features/
│   ├── __init__.py
│   ├── sift.py      # SIFT feature detection
│   ├── orb.py       # ORB feature detection (free alternative)
│   └── surf.py      # SURF feature detection
```

#### 3.2 Blending Strategies Module (Priority: Medium)
```
autoflight/
├── blending/
│   ├── __init__.py
│   ├── multiband.py   # Multi-band blending
│   ├── feather.py     # Feather blending
│   └── linear.py      # Linear blending
```

#### 3.3 Input/Output Abstraction (Priority: Medium)
```
autoflight/
├── io/
│   ├── __init__.py
│   ├── readers/
│   │   ├── local.py   # Local filesystem
│   │   ├── s3.py      # AWS S3 support
│   │   └── gcs.py     # Google Cloud Storage
│   └── writers/
│       ├── local.py
│       ├── s3.py
│       └── tiles.py   # Tile output (TMS/XYZ)
```

#### 3.4 CLI and API Separation (Priority: High)
- [ ] **Move CLI to separate module** - `autoflight/cli.py` for command-line interface
- [ ] **Keep `orthomosaic.py` as pure API** - No argparse or CLI concerns
- [ ] **Add entry point flexibility** - Support both `autoflight` and `autoflight-cli` commands

#### 3.5 Plugin Architecture (Priority: Low)
Consider a plugin system for extensibility:
```python
# Example plugin interface
class AutoflightPlugin:
    """Base class for autoflight plugins."""
    
    def on_image_loaded(self, image, path):
        """Called after each image is loaded."""
        pass
    
    def on_stitch_complete(self, result):
        """Called after stitching completes."""
        pass
```

---

## 4. Audit: Inspect the Ranks 🔍

> *"Look through the code to find any hidden Orcs (security flaws) or traitors."*

### Security Assessment

#### 4.1 Current Security Strengths ✅
- **Input validation** - `validate_path()` checks for path traversal attacks
- **Secure dependency installation** - Hardcoded package specifications prevent injection
- **No shell injection** - Uses `subprocess.check_call()` with list arguments
- **Type safety** - Type hints help prevent type confusion bugs

#### 4.2 Potential Vulnerabilities 🔴

##### 4.2.1 Image Processing Vulnerabilities (Medium Risk)
```python
# Current: Directly passes user-provided paths to cv2.imread()
image = cv2.imread(str(path))

# Recommendation: Add additional validation
def load_single_image(path: Path) -> np.ndarray:
    # Validate path is within expected directory
    resolved = path.resolve()
    if not str(resolved).startswith(str(expected_base.resolve())):
        raise ValueError(f"Path traversal detected: {path}")
    
    # Check file magic bytes, not just extension
    if not _is_valid_image_file(path):
        raise ValueError(f"Invalid image file: {path}")
```

##### 4.2.2 Denial of Service Concerns (Medium Risk)
- [ ] **Add image size limits** - Prevent memory exhaustion from huge images
- [ ] **Add file count limits** - Prevent processing millions of files
- [ ] **Add timeout handling** - Prevent infinite processing loops

##### 4.2.3 Dependency Security (Low Risk)
- [ ] **Pin exact versions** - Currently uses version ranges
- [ ] **Add integrity hashes** - Use `pip install --require-hashes`
- [ ] **Regular dependency audits** - Add `pip-audit` to CI pipeline

#### 4.3 Recommended Security Additions

```python
# autoflight/security.py (proposed)

MAX_IMAGE_SIZE = 100_000_000  # 100 megapixels
MAX_FILE_SIZE = 500_000_000   # 500 MB
MAX_FILES = 1000

def validate_image_safety(path: Path) -> None:
    """Validate image file for security concerns."""
    # Check file size
    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {path}")
    
    # Check image dimensions (after loading)
    image = cv2.imread(str(path))
    if image is not None:
        pixels = image.shape[0] * image.shape[1]
        if pixels > MAX_IMAGE_SIZE:
            raise ValueError(f"Image too large: {pixels} pixels")
```

#### 4.4 Security Checklist
- [ ] Add file size limits before processing
- [ ] Add image dimension limits
- [ ] Implement file count limits
- [ ] Add magic byte validation for image formats
- [ ] Pin dependency versions exactly
- [ ] Add `pip-audit` to CI
- [ ] Add SECURITY.md with vulnerability reporting process
- [ ] Consider sandboxing image processing

---

## 5. Enhance and Upgrade ⚔️

### 5.1 Feature Enhancements (Priority: High)

#### 5.1.1 GeoTIFF Support
```python
# Add support for georeferenced output
def create_orthomosaic(
    input_dir: Path,
    output_path: Path,
    georeference: bool = False,  # NEW
    crs: str = "EPSG:4326",      # NEW
) -> OrthomosaicResult:
```

#### 5.1.2 Tile Output
- [ ] Generate XYZ/TMS tiles for web mapping
- [ ] Support multiple zoom levels
- [ ] Add tile server compatibility (Leaflet, MapLibre)

#### 5.1.3 Preview Mode
- [ ] Generate low-resolution preview quickly
- [ ] Allow parameter tuning before full processing
- [ ] Interactive boundary adjustment

### 5.2 API Enhancements (Priority: Medium)

#### 5.2.1 Async API
```python
async def create_orthomosaic_async(
    input_dir: Path,
    output_path: Path,
    progress_callback: Callable[[float], None] = None,
) -> OrthomosaicResult:
    """Async version with progress reporting."""
```

#### 5.2.2 Streaming API
```python
def create_orthomosaic_streaming(
    image_iterator: Iterator[np.ndarray],
    output_path: Path,
) -> OrthomosaicResult:
    """Process images from a stream/generator."""
```

### 5.3 CLI Enhancements (Priority: Medium)
- [ ] Add progress bar (`--progress`)
- [ ] Add dry-run mode (`--dry-run`)
- [ ] Add configuration file support (`--config`)
- [ ] Add JSON output (`--json`)
- [ ] Add batch processing (`--batch`)

### 5.4 Integration Enhancements (Priority: Low)
- [ ] REST API wrapper for web services
- [ ] Docker image for containerized deployment
- [ ] AWS Lambda support for serverless processing
- [ ] Kubernetes job templates

### 5.5 Quality Improvements (Priority: Medium)
- [ ] Color correction across images
- [ ] Exposure balancing
- [ ] Vignette removal
- [ ] Lens distortion correction

---

## 6. Next Steps Summary 📋

### Immediate Actions (This Sprint)

| Priority | Task | Category | Effort |
|----------|------|----------|--------|
| 🔴 High | Add file size/dimension limits | Security | 2h |
| 🔴 High | Create custom exceptions | Refactor | 2h |
| 🔴 High | Separate CLI from API | Modularize | 4h |
| 🟡 Medium | Add JPEG quality parameter | Optimize | 1h |
| 🟡 Medium | Standardize logging | Refactor | 2h |

### Short-term Goals (Next Month)

| Priority | Task | Category | Effort |
|----------|------|----------|--------|
| 🔴 High | GPU acceleration support | Optimize | 1 week |
| 🔴 High | Add progress callbacks | Enhance | 2 days |
| 🟡 Medium | Create configuration module | Refactor | 3 days |
| 🟡 Medium | Add tile output support | Enhance | 1 week |
| 🟢 Low | Plugin architecture | Modularize | 1 week |

### Long-term Vision (Next Quarter)

1. **Cloud Integration** - S3/GCS input/output support
2. **Web API** - REST service for orthomosaic generation
3. **Distributed Processing** - Support for processing across multiple nodes
4. **Machine Learning** - Automatic image sorting and quality assessment
5. **Real-time Preview** - Live stitching preview during capture

---

## Progress Tracking

### Checklist Dashboard

```
OPTIMIZE    [██████░░░░] 60% - Parallel loading done, GPU pending
REFACTOR    [████░░░░░░] 40% - Good structure, needs standardization  
MODULARIZE  [████████░░] 80% - Well modularized, minor improvements
AUDIT       [██████░░░░] 60% - Basic security, needs hardening
ENHANCE     [████░░░░░░] 40% - Core features done, advanced pending
```

### Version Milestones

| Version | Focus | Target |
|---------|-------|--------|
| v1.2.0 | Security hardening + CLI separation | Next sprint |
| v1.3.0 | GPU acceleration + progress callbacks | Short-term |
| v2.0.0 | Cloud integration + REST API | Long-term |

---

## How to Use This Document

1. **Review regularly** - Check progress at sprint reviews
2. **Update status** - Mark completed items with ✅
3. **Reprioritize** - Adjust based on user feedback
4. **Track metrics** - Monitor performance improvements
5. **Document decisions** - Add notes on why certain paths were chosen

---

> *"The road goes ever on and on, down from the door where it began."*  
> — J.R.R. Tolkien

*Document maintained by: Autoflight Contributors*
