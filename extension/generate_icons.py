"""
Generate valid standalone PNG icons for IT'S MY AI Browser Extension.
Uses pure Python standard library (struct, zlib) with zero external dependencies.
"""

import os
import zlib
import struct
from pathlib import Path

def create_png(width, height, color_fn):
    """Creates a PNG image with width and height using color_fn(x, y) -> (r, g, b, a)."""
    raw_bytes = bytearray()
    for y in range(height):
        raw_bytes.append(0)  # Filter type 0 (None)
        for x in range(width):
            r, g, b, a = color_fn(x, y, width, height)
            raw_bytes.extend([r, g, b, a])

    # PNG Signature
    png = b"\x89PNG\r\n\x1a\n"

    # IHDR Chunk
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data) & 0xffffffff
    png += struct.pack(">I", len(ihdr_data)) + b"IHDR" + ihdr_data + struct.pack(">I", ihdr_crc)

    # IDAT Chunk (compressed data)
    compressed = zlib.compress(raw_bytes, 9)
    idat_crc = zlib.crc32(b"IDAT" + compressed) & 0xffffffff
    png += struct.pack(">I", len(compressed)) + b"IDAT" + compressed + struct.pack(">I", idat_crc)

    # IEND Chunk
    iend_crc = zlib.crc32(b"IEND") & 0xffffffff
    png += struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc)

    return png

def ai_core_pixel(x, y, width, height):
    """Generates a futuristic cyan orb on a dark cyber circular base."""
    cx = width / 2.0
    cy = height / 2.0
    dx = (x + 0.5 - cx) / (cx)
    dy = (y + 0.5 - cy) / (cy)
    r_dist = (dx * dx + dy * dy) ** 0.5

    if r_dist > 1.0:
        return (0, 0, 0, 0)  # transparent outside

    # Outer border ring
    if r_dist > 0.82:
        alpha = int(255 * (1.0 - (r_dist - 0.82) / 0.18))
        return (0, 240, 255, max(0, min(255, alpha)))

    # Dark cyber background
    if r_dist > 0.55:
        return (7, 13, 24, 240)

    # Inner glowing cyan core
    core_intensity = 1.0 - (r_dist / 0.55)
    cr = int(0 + 200 * (core_intensity ** 2))
    cg = int(240 + 15 * core_intensity)
    cb = 255
    alpha = int(255 * (0.8 + 0.2 * core_intensity))
    return (min(255, cr), min(255, cg), min(255, cb), min(255, alpha))

def main():
    icons_dir = Path(__file__).resolve().parent / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)

    sizes = [16, 48, 128]
    for size in sizes:
        png_data = create_png(size, size, ai_core_pixel)
        file_path = icons_dir / f"icon{size}.png"
        with open(file_path, "wb") as f:
            f.write(png_data)
        print(f"Generated {file_path} ({len(png_data)} bytes)")

if __name__ == "__main__":
    main()
