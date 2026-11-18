"""Write the committed news illustration using Python's standard library."""
import os
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parent
artwork = (ROOT / "entry.png").read_bytes()
if len(artwork) > 1_048_576 or artwork[:8] != b"\x89PNG\r\n\x1a\n":
    raise ValueError("entry.png must be a PNG no larger than 1 MiB")

# Validate every chunk and its checksum before publishing the asset.
offset = 8
header = None
data_seen = False
ended = False
while offset < len(artwork):
    if offset + 12 > len(artwork):
        raise ValueError("Truncated PNG chunk")
    length = struct.unpack_from(">I", artwork, offset)[0]
    end = offset + 12 + length
    if end > len(artwork):
        raise ValueError("Truncated PNG data")
    kind = artwork[offset + 4:offset + 8]
    payload = artwork[offset + 8:offset + 8 + length]
    checksum = struct.unpack_from(">I", artwork, offset + 8 + length)[0]
    if zlib.crc32(kind + payload) & 0xFFFFFFFF != checksum:
        raise ValueError("PNG checksum mismatch")
    if offset == 8:
        if kind != b"IHDR" or length != 13:
            raise ValueError("PNG must begin with IHDR")
        header = struct.unpack(">IIBBBBB", payload)
        if not (1 <= header[0] <= 1024 and 1 <= header[1] <= 1024):
            raise ValueError("PNG dimensions exceed 1024 × 1024")
    data_seen |= kind == b"IDAT"
    offset = end
    if kind == b"IEND":
        ended = length == 0 and offset == len(artwork)
        break
if not (header and data_seen and ended):
    raise ValueError("PNG is incomplete")

destination = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
destination.mkdir(parents=True, exist_ok=True)
(destination / "entry.png").write_bytes(artwork)
