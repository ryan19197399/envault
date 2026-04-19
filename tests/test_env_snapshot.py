"""Tests for envault.env_snapshot."""
import pytest
from envault.env_snapshot import (
    create_snapshot, restore_snapshot, delete_snapshot,
    list_snapshots, get_snapshot, SNAPSHOTS_KEY
)


@pytest.fixture
def vault_data():
    return {"vars": {"DB_HOST": "localhost", "DB_PORT": "5432"}}


def test_create_snapshot_creates_key(vault_data):
    create_snapshot(vault_data, "snap1")
    assert SNAPSHOTS_KEY in vault_data


def test_create_snapshot_stores_vars(vault_data):
    create_snapshot(vault_data, "snap1")
    assert vault_data[SNAPSHOTS_KEY]["snap1"]["vars"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_create_snapshot_default_name(vault_data):
    name = create_snapshot(vault_data)
    assert name in vault_data[SNAPSHOTS_KEY]


def test_create_snapshot_stores_created_at(vault_data):
    create_snapshot(vault_data, "snap1")
    assert "created_at" in vault_data[SNAPSHOTS_KEY]["snap1"]


def test_create_snapshot_is_copy(vault_data):
    create_snapshot(vault_data, "snap1")
    vault_data["vars"]["DB_HOST"] = "changed"
    assert vault_data[SNAPSHOTS_KEY]["snap1"]["vars"]["DB_HOST"] == "localhost"


def test_restore_snapshot_restores_vars(vault_data):
    create_snapshot(vault_data, "snap1")
    vault_data["vars"]["DB_HOST"] = "changed"
    result = restore_snapshot(vault_data, "snap1")
    assert result is True
    assert vault_data["vars"]["DB_HOST"] == "localhost"


def test_restore_snapshot_missing_returns_false(vault_data):
    assert restore_snapshot(vault_data, "nonexistent") is False


def test_delete_snapshot_removes_entry(vault_data):
    create_snapshot(vault_data, "snap1")
    result = delete_snapshot(vault_data, "snap1")
    assert result is True
    assert "snap1" not in vault_data[SNAPSHOTS_KEY]


def test_delete_snapshot_missing_returns_false(vault_data):
    assert delete_snapshot(vault_data, "ghost") is False


def test_list_snapshots_empty(vault_data):
    assert list_snapshots(vault_data) == []


def test_list_snapshots_returns_names_and_dates(vault_data):
    create_snapshot(vault_data, "s1")
    create_snapshot(vault_data, "s2")
    snaps = list_snapshots(vault_data)
    names = [n for n, _ in snaps]
    assert "s1" in names and "s2" in names


def test_get_snapshot_returns_vars(vault_data):
    create_snapshot(vault_data, "snap1")
    result = get_snapshot(vault_data, "snap1")
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_get_snapshot_missing_returns_none(vault_data):
    assert get_snapshot(vault_data, "nope") is None
