"""Tests for envault.lock session locking."""

import time
import pytest
from pathlib import Path
from unittest.mock import patch

from envault.lock import (
    touch_session,
    is_locked,
    lock,
    unlock,
    get_last_active,
    DEFAULT_TIMEOUT,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


VAULT = "myvault"


def test_is_locked_when_no_session(vault_dir):
    assert is_locked(vault_dir, VAULT) is True


def test_unlock_creates_session(vault_dir):
    unlock(vault_dir, VAULT)
    assert is_locked(vault_dir, VAULT) is False


def test_touch_session_updates_timestamp(vault_dir):
    touch_session(vault_dir, VAULT)
    ts1 = get_last_active(vault_dir, VAULT)
    time.sleep(0.05)
    touch_session(vault_dir, VAULT)
    ts2 = get_last_active(vault_dir, VAULT)
    assert ts2 > ts1


def test_lock_removes_session(vault_dir):
    unlock(vault_dir, VAULT)
    lock(vault_dir, VAULT)
    assert is_locked(vault_dir, VAULT) is True


def test_lock_idempotent_when_already_locked(vault_dir):
    lock(vault_dir, VAULT)  # should not raise
    assert is_locked(vault_dir, VAULT) is True


def test_is_locked_after_timeout(vault_dir):
    touch_session(vault_dir, VAULT)
    with patch("envault.lock.time.time", return_value=time.time() + DEFAULT_TIMEOUT + 1):
        assert is_locked(vault_dir, VAULT) is True


def test_is_locked_within_timeout(vault_dir):
    touch_session(vault_dir, VAULT)
    assert is_locked(vault_dir, VAULT, timeout=DEFAULT_TIMEOUT) is False


def test_get_last_active_none_when_missing(vault_dir):
    assert get_last_active(vault_dir, VAULT) is None


def test_get_last_active_returns_float(vault_dir):
    touch_session(vault_dir, VAULT)
    ts = get_last_active(vault_dir, VAULT)
    assert isinstance(ts, float)
    assert ts <= time.time()
