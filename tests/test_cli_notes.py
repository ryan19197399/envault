"""Tests for envault/cli_notes.py"""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envault.cli_notes import note


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(exists=True, data=None):
    v = MagicMock()
    v.load.return_value = exists
    v.data = data or {"vars": {"DB_URL": "postgres://localhost"}, "__notes__": {}}
    return v


@patch("envault.cli_notes.Vault")
def test_set_note_success(mock_vault_cls, runner):
    v = _mock_vault()
    mock_vault_cls.return_value = v
    result = runner.invoke(note, ["set", "myvault", "DB_URL", "main db", "--password", "pass"])
    assert result.exit_code == 0
    assert "Note set" in result.output
    v.save.assert_called_once()


@patch("envault.cli_notes.Vault")
def test_set_note_vault_missing(mock_vault_cls, runner):
    v = _mock_vault(exists=False)
    mock_vault_cls.return_value = v
    result = runner.invoke(note, ["set", "ghost", "DB_URL", "note", "--password", "pass"])
    assert result.exit_code != 0
    assert "not found" in result.output


@patch("envault.cli_notes.Vault")
def test_set_note_key_missing(mock_vault_cls, runner):
    v = _mock_vault(data={"vars": {}})
    mock_vault_cls.return_value = v
    result = runner.invoke(note, ["set", "myvault", "MISSING", "note", "--password", "pass"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


@patch("envault.cli_notes.Vault")
def test_get_note_found(mock_vault_cls, runner):
    v = _mock_vault(data={"vars": {"DB_URL": "x"}, "__notes__": {"DB_URL": "main db"}})
    mock_vault_cls.return_value = v
    result = runner.invoke(note, ["get", "myvault", "DB_URL", "--password", "pass"])
    assert result.exit_code == 0
    assert "main db" in result.output


@patch("envault.cli_notes.Vault")
def test_get_note_not_found(mock_vault_cls, runner):
    v = _mock_vault()
    mock_vault_cls.return_value = v
    result = runner.invoke(note, ["get", "myvault", "DB_URL", "--password", "pass"])
    assert result.exit_code == 0
    assert "No note" in result.output


@patch("envault.cli_notes.Vault")
def test_list_notes_empty(mock_vault_cls, runner):
    v = _mock_vault()
    mock_vault_cls.return_value = v
    result = runner.invoke(note, ["list", "myvault", "--password", "pass"])
    assert result.exit_code == 0
    assert "No notes" in result.output


@patch("envault.cli_notes.Vault")
def test_remove_note_existing(mock_vault_cls, runner):
    v = _mock_vault(data={"vars": {"DB_URL": "x"}, "__notes__": {"DB_URL": "a note"}})
    mock_vault_cls.return_value = v
    result = runner.invoke(note, ["remove", "myvault", "DB_URL", "--password", "pass"])
    assert result.exit_code == 0
    assert "removed" in result.output
