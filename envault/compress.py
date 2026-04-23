"""Vault compression utilities — gzip-based compression for exported vault data."""

import gzip
import json
import os
from pathlib import Path


def compress_vault(data: dict, dest_path: str) -> int:
    """Serialize vault data to JSON and write as a gzip-compressed file.

    Returns the number of bytes written.
    """
    raw = json.dumps(data, indent=2).encode("utf-8")
    dest = Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(dest, "wb") as fh:
        fh.write(raw)
    return dest.stat().st_size


def decompress_vault(src_path: str) -> dict:
    """Read a gzip-compressed file and deserialize vault data from JSON.

    Raises FileNotFoundError if the file does not exist.
    Raises ValueError if the content is not valid JSON.
    """
    src = Path(src_path)
    if not src.exists():
        raise FileNotFoundError(f"Compressed vault not found: {src_path}")
    with gzip.open(src, "rb") as fh:
        raw = fh.read()
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid compressed vault content: {exc}") from exc


def compression_ratio(original: dict, compressed_path: str) -> float:
    """Return the compression ratio (original bytes / compressed bytes).

    A ratio > 1 means the compressed file is smaller than the original JSON.
    """
    original_size = len(json.dumps(original, indent=2).encode("utf-8"))
    compressed_size = Path(compressed_path).stat().st_size
    if compressed_size == 0:
        return float("inf")
    return original_size / compressed_size
