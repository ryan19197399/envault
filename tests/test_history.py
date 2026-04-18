"""Tests for envault/history.py"""

import pytest
from envault.history import (
    record_change,
    get_history,
    clear_history,
    HISTORY_KEY,
    MAX_HISTORY,
)


@pytest.fixture
def vault_data():
    return {"vars": {"FOO": "bar"}}


def test_record_change_creates_history_key(vault_data):
    record_change(vault_data, "FOO", "set", new_value="bar")
    assert HISTORY_KEY in vault_data


def test_record_change_stores_entry(vault_data):
    record_change(vault_data, "FOO", "set", new_value="bar")
    entries = vault_data[HISTORY_KEY]
    assert len(entries) == 1
    assert entries[0]["key"] == "FOO"
    assert entries[0]["action"] == "set"
    assert entries[0]["new_value"] == "bar"
    assert "timestamp" in entries[0]


def test_record_change_with_old_and_new(vault_data):
    record_change(vault_data, "FOO", "update", old_value="old", new_value="new")
    entry = vault_data[HISTORY_KEY][0]
    assert entry["old_value"] == "old"
    assert entry["new_value"] == "new"


def test_record_change_no_old_value_omitted(vault_data):
    record_change(vault_data, "FOO", "set", new_value="bar")
    assert "old_value" not in vault_data[HISTORY_KEY][0]


def test_history_capped_at_max(vault_data):
    for i in range(MAX_HISTORY + 10):
        record_change(vault_data, f"KEY{i}", "set", new_value=str(i))
    assert len(vault_data[HISTORY_KEY]) == MAX_HISTORY


def test_get_history_all(vault_data):
    record_change(vault_data, "A", "set", new_value="1")
    record_change(vault_data, "B", "set", new_value="2")
    assert len(get_history(vault_data)) == 2


def test_get_history_filtered_by_key(vault_data):
    record_change(vault_data, "A", "set", new_value="1")
    record_change(vault_data, "B", "set", new_value="2")
    result = get_history(vault_data, key="A")
    assert len(result) == 1
    assert result[0]["key"] == "A"


def test_get_history_empty(vault_data):
    assert get_history(vault_data) == []


def test_clear_history_all(vault_data):
    record_change(vault_data, "A", "set", new_value="1")
    record_change(vault_data, "B", "set", new_value="2")
    clear_history(vault_data)
    assert vault_data[HISTORY_KEY] == []


def test_clear_history_by_key(vault_data):
    record_change(vault_data, "A", "set", new_value="1")
    record_change(vault_data, "B", "set", new_value="2")
    clear_history(vault_data, key="A")
    remaining = get_history(vault_data)
    assert all(e["key"] != "A" for e in remaining)
    assert any(e["key"] == "B" for e in remaining)
