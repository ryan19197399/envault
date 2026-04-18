"""Tests for envault/cli_diff.py"""
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envault.cli_diff import diff


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(vars_dict):
    v = MagicMock()
    v.data = {"vars": vars_dict}
    return v


def test_compare_shows_diff(runner):
    va = _mock_vault({"A": "1", "B": "old"})
    vb = _mock_vault({"A": "1", "B": "new", "C": "3"})
    with patch("envault.cli_diff.Vault") as MockVault:
        MockVault.load.side_effect = [va, vb]
        result = runner.invoke(diff, ["compare", "v1", "v2", "--password-a", "pw", "--password-b", "pw"])
    assert result.exit_code == 0
    assert "+ C=3" in result.output
    assert "~ B" in result.output


def test_compare_vault_a_missing(runner):
    with patch("envault.cli_diff.Vault") as MockVault:
        MockVault.load.side_effect = FileNotFoundError("not found")
        result = runner.invoke(diff, ["compare", "v1", "v2", "--password-a", "pw", "--password-b", "pw"])
    assert result.exit_code != 0
    assert "Could not load vault" in result.output


def test_summary_counts(runner):
    va = _mock_vault({"A": "1", "B": "old"})
    vb = _mock_vault({"A": "1", "C": "new"})
    with patch("envault.cli_diff.Vault") as MockVault:
        MockVault.load.side_effect = [va, vb]
        result = runner.invoke(diff, ["summary", "v1", "v2", "--password-a", "pw", "--password-b", "pw"])
    assert result.exit_code == 0
    assert "Added:" in result.output
    assert "Removed:" in result.output
    assert "Unchanged:" in result.output


def test_compare_no_differences(runner):
    va = _mock_vault({"X": "same"})
    vb = _mock_vault({"X": "same"})
    with patch("envault.cli_diff.Vault") as MockVault:
        MockVault.load.side_effect = [va, vb]
        result = runner.invoke(diff, ["compare", "v1", "v2", "--password-a", "pw", "--password-b", "pw"])
    assert result.exit_code == 0
    assert "(no differences)" in result.output
