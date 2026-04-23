"""Tests for envault.compress."""

import gzip
import json
import os
from pathlib import Path

import pytest

from envault.compress import compress_vault, decompress_vault, compression_ratio


@pytest.fixture()
def tmp_dir(tmp_path):
    return tmp_path


@pytest.fixture()
def sample_data():
    return {
        "vars": {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET_KEY": "abc123"},
        "tags": {"DB_HOST": ["database"]},
    }


def test_compress_vault_creates_file(tmp_dir, sample_data):
    dest = str(tmp_dir / "vault.gz")
    compress_vault(sample_data, dest)
    assert Path(dest).exists()


def test_compress_vault_returns_positive_size(tmp_dir, sample_data):
    dest = str(tmp_dir / "vault.gz")
    size = compress_vault(sample_data, dest)
    assert size > 0


def test_compress_vault_produces_valid_gzip(tmp_dir, sample_data):
    dest = str(tmp_dir / "vault.gz")
    compress_vault(sample_data, dest)
    with gzip.open(dest, "rb") as fh:
        content = fh.read()
    parsed = json.loads(content.decode("utf-8"))
    assert parsed == sample_data


def test_decompress_vault_roundtrip(tmp_dir, sample_data):
    dest = str(tmp_dir / "vault.gz")
    compress_vault(sample_data, dest)
    result = decompress_vault(dest)
    assert result == sample_data


def test_decompress_vault_missing_file_raises(tmp_dir):
    with pytest.raises(FileNotFoundError):
        decompress_vault(str(tmp_dir / "nonexistent.gz"))


def test_decompress_vault_invalid_content_raises(tmp_dir):
    bad = tmp_dir / "bad.gz"
    with gzip.open(bad, "wb") as fh:
        fh.write(b"not json at all!!!")
    with pytest.raises(ValueError):
        decompress_vault(str(bad))


def test_compression_ratio_greater_than_one(tmp_dir, sample_data):
    """Compressing non-trivial JSON should yield ratio >= 1."""
    # Use a larger payload to ensure gzip wins
    large_data = {"vars": {f"KEY_{i}": "value" * 10 for i in range(50)}}
    dest = str(tmp_dir / "large.gz")
    compress_vault(large_data, dest)
    ratio = compression_ratio(large_data, dest)
    assert ratio > 1.0


def test_compress_creates_parent_dirs(tmp_dir, sample_data):
    dest = str(tmp_dir / "nested" / "deep" / "vault.gz")
    compress_vault(sample_data, dest)
    assert Path(dest).exists()
