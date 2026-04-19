"""Tests for envault/cli_access.py"""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envault.cli_access import access


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(exists=True, data=None):
    v = MagicMock()
    v.exists.return_value = exists
    v.data = data or {"vars": {"API_KEY": "secret"}, "_access": {}}
    return v


def test_grant_success(runner):
    v = _mock_vault()
    with patch("envault.cli_access.Vault", return_value=v):
        result = runner.invoke(
            access, ["grant", "myvault", "API_KEY", "read", "alice",
                     "--password", "pass", "--password", "pass"]
        )
    assert result.exit_code == 0
    assert "Granted" in result.output


def test_grant_vault_missing(runner):
    v = _mock_vault(exists=False)
    with patch("envault.cli_access.Vault", return_value=v):
        result = runner.invoke(
            access, ["grant", "myvault", "API_KEY", "read", "alice",
                     "--password", "pass", "--password", "pass"]
        )
    assert result.exit_code != 0
    assert "not found" in result.output


def test_grant_key_missing(runner):
    v = _mock_vault(data={"vars": {}, "_access": {}})
    with patch("envault.cli_access.Vault", return_value=v):
        result = runner.invoke(
            access, ["grant", "myvault", "API_KEY", "read", "alice",
                     "--password", "pass", "--password", "pass"]
        )
    assert result.exit_code != 0
    assert "not found" in result.output


def test_revoke_success(runner):
    from envault import access as ac
    data = {"vars": {"API_KEY": "secret"}, "_access": {}}
    ac.set_permission(data, "API_KEY", "read", "alice")
    v = _mock_vault(data=data)
    with patch("envault.cli_access.Vault", return_value=v):
        result = runner.invoke(
            access, ["revoke", "myvault", "API_KEY", "read", "alice",
                     "--password", "pass", "--password", "pass"]
        )
    assert result.exit_code == 0
    assert "Revoked" in result.output


def test_revoke_not_found(runner):
    v = _mock_vault()
    with patch("envault.cli_access.Vault", return_value=v):
        result = runner.invoke(
            access, ["revoke", "myvault", "API_KEY", "read", "ghost",
                     "--password", "pass", "--password", "pass"]
        )
    assert "not found" in result.output


def test_show_permissions(runner):
    from envault import access as ac
    data = {"vars": {"API_KEY": "secret"}, "_access": {}}
    ac.set_permission(data, "API_KEY", "read", "alice")
    v = _mock_vault(data=data)
    with patch("envault.cli_access.Vault", return_value=v):
        result = runner.invoke(
            access, ["show", "myvault", "API_KEY",
                     "--password", "pass", "--password", "pass"]
        )
    assert "alice" in result.output
