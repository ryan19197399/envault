"""Tests for envault/cli_history.py"""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envault.cli_history import history


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(exists=True, data=None):
    vault = MagicMock()
    vault.exists.return_value = exists
    vault.data = data or {}
    return vault


def test_show_history_no_entries(runner):
    vault = _mock_vault(data={})
    with patch("envault.cli_history.Vault", return_value=vault):
        result = runner.invoke(history, ["show", "myvault", "--password", "pass"])
    assert result.exit_code == 0
    assert "No history found" in result.output


def test_show_history_with_entries(runner):
    from envault.history import record_change
    data = {}
    record_change(data, "FOO", "set", new_value="bar")
    vault = _mock_vault(data=data)
    with patch("envault.cli_history.Vault", return_value=vault):
        result = runner.invoke(history, ["show", "myvault", "--password", "pass"])
    assert result.exit_code == 0
    assert "FOO" in result.output
    assert "SET" in result.output


def test_show_history_vault_missing(runner):
    vault = _mock_vault(exists=False)
    with patch("envault.cli_history.Vault", return_value=vault):
        result = runner.invoke(history, ["show", "myvault", "--password", "pass"])
    assert result.exit_code != 0


def test_show_history_filtered_by_key(runner):
    from envault.history import record_change
    data = {}
    record_change(data, "FOO", "set", new_value="1")
    record_change(data, "BAR", "set", new_value="2")
    vault = _mock_vault(data=data)
    with patch("envault.cli_history.Vault", return_value=vault):
        result = runner.invoke(history, ["show", "myvault", "--key", "FOO", "--password", "pass"])
    assert "FOO" in result.output
    assert "BAR" not in result.output


def test_clear_history_confirmed(runner):
    from envault.history import record_change
    data = {}
    record_change(data, "FOO", "set", new_value="1")
    vault = _mock_vault(data=data)
    with patch("envault.cli_history.Vault", return_value=vault):
        result = runner.invoke(
            history, ["clear", "myvault", "--password", "pass", "--yes"]
        )
    assert result.exit_code == 0
    assert "cleared" in result.output
    vault.save.assert_called_once()
