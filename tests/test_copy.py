"""Tests for envault/copy.py"""

import pytest
from envault.copy import copy_key, copy_keys, clone_vault


@pytest.fixture
def src():
    return {"env": {"DB_URL": "postgres://localhost", "SECRET": "abc123", "PORT": "5432"}}


@pytest.fixture
def dst():
    return {"env": {"PORT": "8080"}}


def test_copy_key_success(src, dst):
    result = copy_key(src, dst, "DB_URL")
    assert result is True
    assert dst["env"]["DB_URL"] == "postgres://localhost"


def test_copy_key_skips_existing_without_overwrite(src, dst):
    result = copy_key(src, dst, "PORT")
    assert result is False
    assert dst["env"]["PORT"] == "8080"


def test_copy_key_overwrites_when_flag_set(src, dst):
    result = copy_key(src, dst, "PORT", overwrite=True)
    assert result is True
    assert dst["env"]["PORT"] == "5432"


def test_copy_key_missing_raises(src, dst):
    with pytest.raises(KeyError, match="MISSING_KEY"):
        copy_key(src, dst, "MISSING_KEY")


def test_copy_keys_mixed(src, dst):
    results = copy_keys(src, dst, ["DB_URL", "PORT", "NOPE"])
    assert results["DB_URL"] == "copied"
    assert results["PORT"] == "skipped"
    assert results["NOPE"] == "missing"


def test_copy_keys_with_overwrite(src, dst):
    results = copy_keys(src, dst, ["PORT"], overwrite=True)
    assert results["PORT"] == "copied"
    assert dst["env"]["PORT"] == "5432"


def test_clone_vault_copies_all(src):
    dst = {}
    results = clone_vault(src, dst)
    assert all(v == "copied" for v in results.values())
    assert dst["env"] == src["env"]


def test_clone_vault_skips_existing(src, dst):
    results = clone_vault(src, dst)
    assert results["PORT"] == "skipped"
    assert dst["env"]["PORT"] == "8080"


def test_clone_vault_empty_src():
    src = {"env": {}}
    dst = {"env": {"X": "1"}}
    results = clone_vault(src, dst)
    assert results == {}
