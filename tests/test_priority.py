"""Tests for envault.priority."""

import pytest
from envault.priority import (
    DEFAULT_PRIORITY,
    set_priority,
    remove_priority,
    get_priority,
    list_priorities,
    sorted_keys,
)


@pytest.fixture()
def vault_data():
    return {
        "vars": {"API_KEY": "abc", "DB_URL": "postgres://", "SECRET": "s3cr3t"},
        "__priorities__": {},
    }


def test_set_priority_stores_value(vault_data):
    set_priority(vault_data, "API_KEY", 5)
    assert vault_data["__priorities__"]["API_KEY"] == 5


def test_set_priority_creates_key_if_absent(vault_data):
    del vault_data["__priorities__"]
    set_priority(vault_data, "DB_URL", 10)
    assert "__priorities__" in vault_data
    assert vault_data["__priorities__"]["DB_URL"] == 10


def test_set_priority_missing_key_raises(vault_data):
    with pytest.raises(KeyError):
        set_priority(vault_data, "NONEXISTENT", 1)


def test_set_priority_invalid_value_raises(vault_data):
    with pytest.raises(ValueError):
        set_priority(vault_data, "API_KEY", 0)


def test_remove_priority_returns_true(vault_data):
    set_priority(vault_data, "API_KEY", 3)
    result = remove_priority(vault_data, "API_KEY")
    assert result is True
    assert "API_KEY" not in vault_data["__priorities__"]


def test_remove_priority_missing_returns_false(vault_data):
    result = remove_priority(vault_data, "API_KEY")
    assert result is False


def test_get_priority_returns_set_value(vault_data):
    set_priority(vault_data, "SECRET", 2)
    assert get_priority(vault_data, "SECRET") == 2


def test_get_priority_default_when_not_set(vault_data):
    assert get_priority(vault_data, "DB_URL") == DEFAULT_PRIORITY


def test_list_priorities_sorted(vault_data):
    set_priority(vault_data, "SECRET", 10)
    set_priority(vault_data, "API_KEY", 1)
    set_priority(vault_data, "DB_URL", 5)
    result = list_priorities(vault_data)
    assert result == [("API_KEY", 1), ("DB_URL", 5), ("SECRET", 10)]


def test_list_priorities_empty(vault_data):
    assert list_priorities(vault_data) == []


def test_sorted_keys_respects_priority(vault_data):
    set_priority(vault_data, "SECRET", 1)
    set_priority(vault_data, "DB_URL", 2)
    keys = sorted_keys(vault_data)
    assert keys[0] == "SECRET"
    assert keys[1] == "DB_URL"
    # API_KEY has no explicit priority, goes last
    assert keys[2] == "API_KEY"


def test_sorted_keys_all_default(vault_data):
    keys = sorted_keys(vault_data)
    # All have DEFAULT_PRIORITY; order is stable but all present
    assert set(keys) == {"API_KEY", "DB_URL", "SECRET"}
