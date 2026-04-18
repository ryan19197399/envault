"""Tests for import_export_dotenv module."""
import pytest
from unittest.mock import patch, MagicMock
from envault.import_export_dotenv import export_to_dotenv, import_from_dotenv


def _make_vault(vars_dict):
    v = MagicMock()
    v.data = {"vars": dict(vars_dict)}
    v.save = MagicMock()
    return v


@patch("envault.import_export_dotenv.log_event")
@patch("envault.import_export_dotenv.Vault.load")
def test_export_writes_file(mock_load, mock_log, tmp_path):
    mock_load.return_value = _make_vault({"KEY": "val", "FOO": "bar"})
    out = str(tmp_path / ".env")
    count = export_to_dotenv("myvault", "pass", out)
    assert count == 2
    content = (tmp_path / ".env").read_text()
    assert "KEY=" in content
    assert "FOO=" in content
    mock_log.assert_called_once()


@patch("envault.import_export_dotenv.log_event")
@patch("envault.import_export_dotenv.Vault.load")
def test_import_adds_new_keys(mock_load, mock_log, tmp_path):
    vault = _make_vault({})
    mock_load.return_value = vault
    env_file = tmp_path / ".env"
    env_file.write_text('NEW_KEY="hello"\nANOTHER="world"\n')
    result = import_from_dotenv("myvault", "pass", str(env_file))
    assert set(result["added"]) == {"NEW_KEY", "ANOTHER"}
    assert result["skipped"] == []
    assert result["overwritten"] == []
    vault.save.assert_called_once_with("pass")


@patch("envault.import_export_dotenv.log_event")
@patch("envault.import_export_dotenv.Vault.load")
def test_import_skips_existing_without_overwrite(mock_load, mock_log, tmp_path):
    vault = _make_vault({"EXISTING": "old"})
    mock_load.return_value = vault
    env_file = tmp_path / ".env"
    env_file.write_text('EXISTING="new"\n')
    result = import_from_dotenv("myvault", "pass", str(env_file), overwrite=False)
    assert result["skipped"] == ["EXISTING"]
    assert vault.data["vars"]["EXISTING"] == "old"


@patch("envault.import_export_dotenv.log_event")
@patch("envault.import_export_dotenv.Vault.load")
def test_import_overwrites_when_flag_set(mock_load, mock_log, tmp_path):
    vault = _make_vault({"EXISTING": "old"})
    mock_load.return_value = vault
    env_file = tmp_path / ".env"
    env_file.write_text('EXISTING="new"\n')
    result = import_from_dotenv("myvault", "pass", str(env_file), overwrite=True)
    assert result["overwritten"] == ["EXISTING"]
    assert vault.data["vars"]["EXISTING"] == "new"
