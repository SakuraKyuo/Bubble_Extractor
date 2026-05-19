#!/usr/bin/env python3
# Bubble Firmware Extractor
# Designed by SakuraKyuo
import sys
import os
import io
import argparse
import lz4.frame

LZ4_MAGIC = b'\x04\x22\x4d\x18'
FAT_SIGNATURE = b'\xEB\x3C\x90mkfs.fat'


def find_all(bytez, pattern):
    off = 0
    positions = []
    while True:
        off = bytez.find(pattern, off)
        if off == -1:
            break
        positions.append(off)
        off += 1
    return positions


def extract_lz4_chunk(firmware):
    lz4_offsets = find_all(firmware, LZ4_MAGIC)

    if lz4_offsets:
        start = lz4_offsets[0]
        print(f"[+] Found LZ4 magic header at offset {start:#x}")
        compressed = firmware[start:]
    else:
        print("[!] LZ4 magic not found, using default fallback offset 0x200")
        if len(firmware) <= 0x200:
            raise RuntimeError("Firmware too short")
        start = 0x200
        compressed = firmware[start:]

    decompressed = bytearray()
    decompressor = lz4.frame.LZ4FrameDecompressor()
    data_stream = io.BytesIO(compressed)
    chunk_size = 4 * 1024 * 1024

    try:
        while True:
            chunk = data_stream.read(chunk_size)
            if not chunk:
                break
            try:
                decompressed.extend(decompressor.decompress(chunk))
            except lz4.frame.LZ4FrameError:
                if decompressor.needs_input and not decompressor.unused_data:
                    break
                else:
                    raise
        if not decompressor.eof:
            print("[!] Warning: Compressed data may be incomplete, partial output saved")
    except Exception as e:
        raise RuntimeError(f"LZ4 streaming decompression failed: {e}")

    if len(decompressed) == 0:
        raise RuntimeError("Decompressed data is empty")
    print(f"[+] Decompression successful. Size: {len(decompressed)} bytes")
    return bytes(decompressed)


def extract_fat(decompressed):
    fat_offsets = find_all(decompressed, FAT_SIGNATURE)
    if not fat_offsets:
        raise RuntimeError("FAT boot sector not found in decompressed data")

    fat_start = fat_offsets[0]
    print(f"[+] Found FAT boot sector at offset {fat_start:#x}")
    return decompressed[fat_start:]


def main():
    parser = argparse.ArgumentParser(description="Extract FAT16 filesystem image from OPPO Bubble firmware")
    parser.add_argument("firmware", help="Path to firmware file")
    parser.add_argument("-o", "--output", default="fat_image.img", help="Output FAT image name")
    args = parser.parse_args()

    if not os.path.exists(args.firmware):
        sys.exit(f"Error: Firmware file {args.firmware} not found")

    try:
        with open(args.firmware, "rb") as f:
            firmware = f.read()
    except Exception as e:
        sys.exit(f"Error reading firmware: {e}")

    print(f"[*] Firmware size: {len(firmware)} bytes")

    decompressed = extract_lz4_chunk(firmware)
    fat_img = extract_fat(decompressed)

    with open(args.output, "wb") as f:
        f.write(fat_img)
    print(f"\n[✓] Success! FAT16 image written to: {args.output}")

    print(f"""
Next steps:
  You can now extract files directly from the output image using 7-Zip, WinRAR, PeaZip, etc.
""")


if __name__ == "__main__":
    main()
