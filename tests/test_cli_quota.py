"""Tests for envault/cli_quota.py"""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch

from envault.cli_quota import quota


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(data=None):
    if data is None:
        data = {"vars": {"FOO": "bar"}}
    v = MagicMock()
    v.data = data
    return v


def test_set_quota_success(runner):
    v = _mock_vault()
    with patch("envault.cli_quota.Vault.load", return_value=v):
        result = runner.invoke(quota, ["set", "myvault", "--password", "pw", "--max-keys", "50"])
    assert result.exit_code == 0
    assert "Quota updated" in result.output
    v.save.assert_called_once_with("pw")


def test_set_quota_vault_missing(runner):
    with patch("envault.cli_quota.Vault.load", side_effect=FileNotFoundError):
        result = runner.invoke(quota, ["set", "missing", "--password", "pw", "--max-keys", "10"])
    assert "not found" in result.output


def test_set_quota_no_options_raises(runner):
    result = runner.invoke(quota, ["set", "myvault", "--password", "pw"])
    assert result.exit_code != 0


def test_show_quota_success(runner):
    v = _mock_vault({"vars": {"A": "1"}, "__quota__": {"max_keys": 20, "max_value_bytes": 512}})
    with patch("envault.cli_quota.Vault.load", return_value=v):
        result = runner.invoke(quota, ["show", "myvault", "--password", "pw"])
    assert result.exit_code == 0
    assert "Max keys" in result.output
    assert "20" in result.output


def test_show_quota_vault_missing(runner):
    with patch("envault.cli_quota.Vault.load", side_effect=FileNotFoundError):
        result = runner.invoke(quota, ["show", "missing", "--password", "pw"])
    assert "not found" in result.output


def test_remove_quota_success(runner):
    v = _mock_vault({"vars": {}, "__quota__": {"max_keys": 10}})
    with patch("envault.cli_quota.Vault.load", return_value=v):
        result = runner.invoke(quota, ["remove", "myvault", "--password", "pw"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_quota_not_found(runner):
    v = _mock_vault({"vars": {}})
    with patch("envault.cli_quota.Vault.load", return_value=v):
        result = runner.invoke(quota, ["remove", "myvault", "--password", "pw"])
    assert "No quota" in result.output
