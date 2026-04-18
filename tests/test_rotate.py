"""Tests for envault.rotate and envault.cli_rotate."""

import pytest
import json
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from envault.rotate import rotate_password, rotate_key
from envault.cli_rotate import rotate


@pytest.fixture
def vault_data():
    return {"vars": {"DB_URL": "postgres://localhost", "SECRET": "abc123"}, "tags": {}}


def _make_mock_vault(data):
    raw = json.dumps(data)
    mock_load = MagicMock(return_value=raw)
    mock_save = MagicMock()
    return raw, mock_load, mock_save


def test_rotate_password_calls_save(vault_data):
    raw, mock_load, mock_save = _make_mock_vault(vault_data)
    with patch("envault.rotate.load_vault", mock_load), \
         patch("envault.rotate.save_vault", mock_save), \
         patch("envault.rotate.log_event"):
        rotate_password("myapp", "oldpass", "newpass")
    mock_load.assert_called_once_with("myapp", "oldpass")
    mock_save.assert_called_once_with("myapp", raw, "newpass")


def test_rotate_key_returns_value(vault_data):
    raw, mock_load, mock_save = _make_mock_vault(vault_data)
    with patch("envault.rotate.load_vault", mock_load), \
         patch("envault.rotate.save_vault", mock_save), \
         patch("envault.rotate.log_event"), \
         patch("envault.rotate.derive_key", return_value=b"k" * 32), \
         patch("envault.rotate.encrypt", return_value=b"token"):
        value = rotate_key("myapp", "pass", "DB_URL")
    assert value == "postgres://localhost"


def test_rotate_key_missing_key_raises(vault_data):
    raw, mock_load, _ = _make_mock_vault(vault_data)
    with patch("envault.rotate.load_vault", mock_load), \
         patch("envault.rotate.log_event"):
        with pytest.raises(KeyError):
            rotate_key("myapp", "pass", "NONEXISTENT")


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_rotate_password(runner, vault_data):
    raw = json.dumps(vault_data)
    with patch("envault.cli_rotate.vault_exists", return_value=True), \
         patch("envault.cli_rotate.rotate_password") as mock_rp:
        result = runner.invoke(rotate, [
            "password", "myapp",
            "--old-password", "old",
            "--new-password", "new"
        ])
    assert result.exit_code == 0
    assert "rotated" in result.output
    mock_rp.assert_called_once_with("myapp", "old", "new")


def test_cli_rotate_password_vault_missing(runner):
    with patch("envault.cli_rotate.vault_exists", return_value=False):
        result = runner.invoke(rotate, [
            "password", "ghost",
            "--old-password", "x",
            "--new-password", "y"
        ])
    assert result.exit_code == 1


def test_cli_rotate_key(runner, vault_data):
    with patch("envault.cli_rotate.vault_exists", return_value=True), \
         patch("envault.cli_rotate.rotate_key", return_value="val") as mock_rk:
        result = runner.invoke(rotate, [
            "key", "myapp", "SECRET",
            "--password", "pass"
        ])
    assert result.exit_code == 0
    assert "rotated" in result.output
    mock_rk.assert_called_once_with("myapp", "pass", "SECRET")
