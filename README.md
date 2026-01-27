# autoflight

Generate orthomosaic images from a folder of overlapping photos.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python -m autoflight.orthomosaic /path/to/input_images /path/to/output/orthomosaic.jpg
```

The command will read all supported image formats (`.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff`) from the input folder,
stitch them into a single orthomosaic, and write the output image.

## Testing

```bash
python -m unittest
```
