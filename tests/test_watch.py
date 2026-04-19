"""Tests for envault/watch.py."""
import os
import time
import pytest
from unittest.mock import patch, MagicMock
from envault.watch import get_vault_mtime, watch_vault


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def test_get_vault_mtime_missing_returns_none(tmp_vault_dir):
    result = get_vault_mtime("nonexistent", base_dir=tmp_vault_dir)
    assert result is None


def test_get_vault_mtime_existing_returns_float(tmp_vault_dir):
    with patch("envault.watch._vault_path", return_value=os.path.join(tmp_vault_dir, "v.json")):
        path = os.path.join(tmp_vault_dir, "v.json")
        with open(path, "w") as f:
            f.write("{}")
        result = get_vault_mtime("v", base_dir=tmp_vault_dir)
        assert isinstance(result, float)


def test_watch_vault_detects_change(tmp_vault_dir):
    vault_file = os.path.join(tmp_vault_dir, "myvault.json")
    with open(vault_file, "w") as f:
        f.write("{}")

    calls = []

    def on_change(name):
        calls.append(name)

    mtimes = [1000.0, 1000.0, 1001.0]
    mtime_iter = iter(mtimes)

    with patch("envault.watch.get_vault_mtime", side_effect=lambda *a, **kw: next(mtime_iter)):
        with patch("envault.watch.time.sleep"):
            watch_vault("myvault", on_change, interval=0.01, max_checks=3, base_dir=tmp_vault_dir)

    assert calls == ["myvault"]


def test_watch_vault_no_change_no_callback(tmp_vault_dir):
    calls = []

    def on_change(name):
        calls.append(name)

    with patch("envault.watch.get_vault_mtime", return_value=999.0):
        with patch("envault.watch.time.sleep"):
            watch_vault("myvault", on_change, interval=0.01, max_checks=3, base_dir=tmp_vault_dir)

    assert calls == []


def test_watch_vault_max_checks_stops(tmp_vault_dir):
    counter = {"n": 0}

    def on_change(name):
        pass

    original_sleep = time.sleep
    sleep_calls = []

    with patch("envault.watch.get_vault_mtime", return_value=1.0):
        with patch("envault.watch.time.sleep", side_effect=lambda s: sleep_calls.append(s)):
            watch_vault("v", on_change, interval=0.1, max_checks=5, base_dir=tmp_vault_dir)

    assert len(sleep_calls) == 5
