# Bubble Extractor

A lightweight Python tool to extract clean FAT16 filesystem images from OPPO Bubble firmware.

## Features

- Scans and locates the compressed LZ4 payload within the firmware.
- Streams and decompresses multi-frame LZ4 data streams.
- Identifies the FAT16 boot sector (`mkfs.fat` signature) and strips away container overhead.
- Outputs a clean, standard raw disk image (`.img`).

## Prerequisites

This tool requires Python 3.6 or higher and the `lz4` compression library.

### Installation

Install the required dependencies using pip:

```bash
pip install -r requirements.txt

```
## Usage
Run the script from your terminal by providing the path to the firmware file:
```bash
python3 bubble_extractor.py <path_to_firmware> [-o output_image.img]

```
### Arguments
 * firmware: **(Required)** Path to the input firmware file.
 * -o, --output: **(Optional)** Name of the output FAT image file (Default: fat_image.img).
### Example
```bash
python3 bubble_extractor.py firmware.bin -o my_extracted_filesystem.img

```
## Next Steps
Once the .img file is successfully generated, you can access and extract the internal files using either of the following methods:
 * **Archive Utility (Recommended):** Open the output image directly using standard archive manager software such as **7-Zip, WinRAR, or PeaZip**.
