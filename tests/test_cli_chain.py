"""Tests for envault/cli_chain.py"""
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envault.cli_chain import chain


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(exists=True, data=None):
    if data is None:
        data = {"vars": {"KEY_A": "alpha", "KEY_B": "beta"}}
    v = MagicMock()
    v.exists.return_value = exists
    v.data = data
    return v


def test_add_chain_success(runner):
    v = _mock_vault()
    with patch("envault.cli_chain.Vault", return_value=v):
        result = runner.invoke(chain, ["add", "myvault", "mychain", "KEY_A", "KEY_B", "--password", "pass"])
    assert result.exit_code == 0
    assert "mychain" in result.output


def test_add_chain_vault_missing(runner):
    v = _mock_vault(exists=False)
    with patch("envault.cli_chain.Vault", return_value=v):
        result = runner.invoke(chain, ["add", "myvault", "mychain", "KEY_A", "--password", "pass"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_remove_chain_success(runner):
    data = {"vars": {"KEY_A": "alpha"}, "_chains": {"mychain": {"steps": ["KEY_A"]}}}
    v = _mock_vault(data=data)
    with patch("envault.cli_chain.Vault", return_value=v):
        result = runner.invoke(chain, ["remove", "myvault", "mychain", "--password", "pass"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_chain_missing(runner):
    v = _mock_vault()
    with patch("envault.cli_chain.Vault", return_value=v):
        result = runner.invoke(chain, ["remove", "myvault", "ghost", "--password", "pass"])
    assert result.exit_code != 0


def test_list_chains_empty(runner):
    v = _mock_vault()
    with patch("envault.cli_chain.Vault", return_value=v):
        result = runner.invoke(chain, ["list", "myvault", "--password", "pass"])
    assert result.exit_code == 0
    assert "No chains" in result.output


def test_run_chain_success(runner):
    data = {"vars": {"KEY_A": "alpha", "KEY_B": "beta"}, "_chains": {"mychain": {"steps": ["KEY_A", "KEY_B"]}}}
    v = _mock_vault(data=data)
    with patch("envault.cli_chain.Vault", return_value=v):
        result = runner.invoke(chain, ["run", "myvault", "mychain", "--password", "pass"])
    assert result.exit_code == 0
    assert "KEY_A=alpha" in result.output
    assert "KEY_B=beta" in result.output
