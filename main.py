#!/usr/bin/env python3
"""news-image-01 entry: "The World at Dawn".

One cinematic hero image carries the whole of Friday
13 November 2026:

  * a white dove with an olive branch crosses the rising sun -
    Europe wins a seat at the Ukraine peace talks;
  * a lone tanker steams through a narrow strait under darkened
    city towers - tankers are struck in Hormuz and a global
    Microsoft 365 outage switches the world's offices off;
  * a constellation in the shape of a computer chip hangs in the
    sky - Nvidia chief executive Jensen Huang resigns;
  * planet Earth itself rises over the water: one planet, one day.

A caption strip at the foot of the picture names those stories in
plain words.  The finished picture ships in this repository as
``image.png``; this program checks it against the competition's
rules (a recognised image format, no more than 1 MiB, no more than
1024 pixels on a side) and copies it unchanged into
``$MAKEFUN_OUTPUT_DIR`` as ``entry.png``.  Standard library only,
and the copy is verified by checksum before success is reported.
"""

import hashlib
import os
import struct
import sys
import zlib
from pathlib import Path

BYTE_LIMIT = 1024 * 1024
SIDE_LIMIT = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


def fail(message):
    print("error: " + message, file=sys.stderr)
    return 1


def size_of_png(blob):
    """(width, height) from the IHDR chunk, CRC checked."""
    if len(blob) < 33 or blob[12:16] != b"IHDR":
        raise ValueError("missing IHDR chunk")
    ihdr = blob[16:29]
    (crc,) = struct.unpack(">I", blob[29:33])
    if zlib.crc32(b"IHDR" + ihdr) & 0xFFFFFFFF != crc:
        raise ValueError("IHDR CRC mismatch")
    return struct.unpack(">II", ihdr[:8])


def size_of_jpeg(blob):
    """(width, height) from the first Start-Of-Frame segment."""
    cursor = 2
    while cursor + 4 <= len(blob):
        if blob[cursor] != 0xFF:
            raise ValueError("JPEG marker stream is corrupt")
        marker = blob[cursor + 1]
        if marker == 0xD9 or 0xD0 <= marker <= 0xD8:
            cursor += 2
            continue
        (seg_len,) = struct.unpack(">H", blob[cursor + 2:cursor + 4])
        if seg_len < 2 or cursor + 2 + seg_len > len(blob):
            raise ValueError("JPEG segment overruns the file")
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height, width = struct.unpack(
                ">HH", blob[cursor + 5:cursor + 9])
            return width, height
        cursor += 2 + seg_len
    raise ValueError("no frame header found in JPEG")


def check_picture(blob):
    """Return (format name, width, height) or raise ValueError."""
    if not blob:
        raise ValueError("the bundled image is empty")
    if len(blob) > BYTE_LIMIT:
        raise ValueError("image exceeds the 1 MiB limit")
    if blob[:8] == PNG_MAGIC:
        fmt, (w, h) = "PNG", size_of_png(blob)
    elif blob[:3] == JPEG_MAGIC:
        fmt, (w, h) = "JPEG", size_of_jpeg(blob)
    else:
        raise ValueError("not a PNG or JPEG image")
    if not (1 <= w <= SIDE_LIMIT and 1 <= h <= SIDE_LIMIT):
        raise ValueError("image exceeds the 1024x1024 limit")
    return fmt, w, h


def main():
    repo = Path(__file__).resolve().parent
    picture = repo / "image.png"
    if not picture.is_file():
        return fail("image.png is missing from the entry repo")

    blob = picture.read_bytes()
    try:
        fmt, width, height = check_picture(blob)
    except ValueError as exc:
        return fail(str(exc))

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    target.write_bytes(blob)

    if hashlib.sha256(target.read_bytes()).hexdigest() != \
            hashlib.sha256(blob).hexdigest():
        return fail("the written entry does not match the bundled image")

    print("wrote %s (%s, %dx%d, %d bytes)"
          % (target, fmt, width, height, len(blob)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
