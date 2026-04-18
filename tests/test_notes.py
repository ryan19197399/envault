"""Tests for envault/notes.py"""

import pytest
from envault import notes as notes_mod


@pytest.fixture
def vault_data():
    return {"vars": {"DB_URL": "postgres://localhost", "API_KEY": "secret"}}


def test_set_note_creates_notes_key(vault_data):
    notes_mod.set_note(vault_data, "DB_URL", "Primary database")
    assert notes_mod.NOTES_KEY in vault_data


def test_set_note_stores_value(vault_data):
    notes_mod.set_note(vault_data, "DB_URL", "Primary database")
    assert vault_data[notes_mod.NOTES_KEY]["DB_URL"] == "Primary database"


def test_set_note_overwrites_existing(vault_data):
    notes_mod.set_note(vault_data, "DB_URL", "old note")
    notes_mod.set_note(vault_data, "DB_URL", "new note")
    assert vault_data[notes_mod.NOTES_KEY]["DB_URL"] == "new note"


def test_get_note_returns_value(vault_data):
    notes_mod.set_note(vault_data, "API_KEY", "Third-party API key")
    assert notes_mod.get_note(vault_data, "API_KEY") == "Third-party API key"


def test_get_note_missing_key_returns_none(vault_data):
    assert notes_mod.get_note(vault_data, "NONEXISTENT") is None


def test_get_note_no_notes_section_returns_none(vault_data):
    assert notes_mod.get_note(vault_data, "DB_URL") is None


def test_remove_note_returns_true(vault_data):
    notes_mod.set_note(vault_data, "DB_URL", "some note")
    result = notes_mod.remove_note(vault_data, "DB_URL")
    assert result is True


def test_remove_note_deletes_entry(vault_data):
    notes_mod.set_note(vault_data, "DB_URL", "some note")
    notes_mod.remove_note(vault_data, "DB_URL")
    assert "DB_URL" not in vault_data.get(notes_mod.NOTES_KEY, {})


def test_remove_note_missing_returns_false(vault_data):
    result = notes_mod.remove_note(vault_data, "MISSING")
    assert result is False


def test_list_notes_returns_all(vault_data):
    notes_mod.set_note(vault_data, "DB_URL", "db note")
    notes_mod.set_note(vault_data, "API_KEY", "api note")
    result = notes_mod.list_notes(vault_data)
    assert result == {"DB_URL": "db note", "API_KEY": "api note"}


def test_list_notes_empty(vault_data):
    assert notes_mod.list_notes(vault_data) == {}


def test_clear_notes_removes_section(vault_data):
    notes_mod.set_note(vault_data, "DB_URL", "note")
    notes_mod.clear_notes(vault_data)
    assert notes_mod.NOTES_KEY not in vault_data
