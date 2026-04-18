"""Tests for envault/cli_ttl.py"""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from envault.cli_ttl import ttl
from datetime import datetime, timedelta


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(exists=True, data=None):
    v = MagicMock()
    v.exists.return_value = exists
    v.data = data or {"vars": {"API_KEY": "secret"}, "__ttl__": {}}
    return v


def test_set_ttl_success(runner):
    v = _mock_vault()
    with patch("envault.cli_ttl.Vault", return_value=v):
        result = runner.invoke(ttl, ["set", "myvault", "API_KEY", "300", "--password", "pass"])
    assert result.exit_code == 0
    assert "300s" in result.output
    v.save.assert_called_once()


def test_set_ttl_vault_missing(runner):
    v = _mock_vault(exists=False)
    with patch("envault.cli_ttl.Vault", return_value=v):
        result = runner.invoke(ttl, ["set", "ghost", "API_KEY", "60", "--password", "pass"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_set_ttl_key_missing(runner):
    v = _mock_vault(data={"vars": {}})
    with patch("envault.cli_ttl.Vault", return_value=v):
        result = runner.invoke(ttl, ["set", "myvault", "MISSING", "60", "--password", "pass"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_remove_ttl_existing(runner):
    past = (datetime.utcnow() + timedelta(seconds=100)).isoformat()
    v = _mock_vault(data={"vars": {"API_KEY": "s"}, "__ttl__": {"API_KEY": past}})
    with patch("envault.cli_ttl.Vault", return_value=v):
        result = runner.invoke(ttl, ["remove", "myvault", "API_KEY", "--password", "pass"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_ttl_not_set(runner):
    v = _mock_vault()
    with patch("envault.cli_ttl.Vault", return_value=v):
        result = runner.invoke(ttl, ["remove", "myvault", "API_KEY", "--password", "pass"])
    assert "No TTL" in result.output


def test_purge_no_expired(runner):
    v = _mock_vault()
    with patch("envault.cli_ttl.Vault", return_value=v):
        result = runner.invoke(ttl, ["purge", "myvault", "--password", "pass"])
    assert "No expired" in result.output


def test_purge_with_expired(runner):
    past = (datetime.utcnow() - timedelta(seconds=10)).isoformat()
    v = _mock_vault(data={"vars": {"API_KEY": "s"}, "__ttl__": {"API_KEY": past}})
    with patch("envault.cli_ttl.Vault", return_value=v):
        result = runner.invoke(ttl, ["purge", "myvault", "--password", "pass"])
    assert "Purged" in result.output
    assert "API_KEY" in result.output
