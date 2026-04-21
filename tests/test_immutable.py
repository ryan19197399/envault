"""Tests for envault/immutable.py"""

import pytest
from envault.immutable import (
    mark_immutable,
    unmark_immutable,
    is_immutable,
    list_immutable,
    guard_immutable,
)


@pytest.fixture
def vault_data():
    return {
        "vars": {"DB_URL": "postgres://localhost", "API_KEY": "secret", "PORT": "5432"},
        "_immutable": [],
    }


def test_mark_immutable_adds_key(vault_data):
    mark_immutable(vault_data, "DB_URL")
    assert "DB_URL" in vault_data["_immutable"]


def test_mark_immutable_missing_key_raises(vault_data):
    with pytest.raises(KeyError, match="MISSING"):
        mark_immutable(vault_data, "MISSING")


def test_mark_immutable_no_duplicates(vault_data):
    mark_immutable(vault_data, "API_KEY")
    mark_immutable(vault_data, "API_KEY")
    assert vault_data["_immutable"].count("API_KEY") == 1


def test_mark_immutable_creates_key_if_absent():
    data = {"vars": {"X": "1"}}
    mark_immutable(data, "X")
    assert "_immutable" in data
    assert "X" in data["_immutable"]


def test_unmark_immutable_returns_true(vault_data):
    mark_immutable(vault_data, "PORT")
    result = unmark_immutable(vault_data, "PORT")
    assert result is True
    assert "PORT" not in vault_data["_immutable"]


def test_unmark_immutable_returns_false_if_not_marked(vault_data):
    result = unmark_immutable(vault_data, "DB_URL")
    assert result is False


def test_is_immutable_true(vault_data):
    mark_immutable(vault_data, "API_KEY")
    assert is_immutable(vault_data, "API_KEY") is True


def test_is_immutable_false(vault_data):
    assert is_immutable(vault_data, "DB_URL") is False


def test_list_immutable_returns_all(vault_data):
    mark_immutable(vault_data, "DB_URL")
    mark_immutable(vault_data, "PORT")
    result = list_immutable(vault_data)
    assert set(result) == {"DB_URL", "PORT"}


def test_list_immutable_empty(vault_data):
    assert list_immutable(vault_data) == []


def test_guard_immutable_raises_for_locked_key(vault_data):
    mark_immutable(vault_data, "API_KEY")
    with pytest.raises(PermissionError, match="API_KEY"):
        guard_immutable(vault_data, "API_KEY")


def test_guard_immutable_passes_for_unlocked_key(vault_data):
    guard_immutable(vault_data, "DB_URL")  # should not raise
