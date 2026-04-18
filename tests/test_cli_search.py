"""Tests for envault/cli_search.py"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envault.cli_search import search


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(exists=True, data=None):
    vault = MagicMock()
    vault.exists.return_value = exists
    vault.data = data or {
        "vars": {"DB_HOST": "localhost", "APP_KEY": "abc"},
        "tags": {"DB_HOST": ["db"]},
    }
    return vault


def test_query_by_key(runner):
    mock = _mock_vault()
    with patch("envault.cli_search.Vault", return_value=mock):
        result = runner.invoke(search, ["query", "myapp", "--password", "pass", "--key", "DB_*"])
    assert result.exit_code == 0
    assert "DB_HOST=localhost" in result.output
    assert "APP_KEY" not in result.output


def test_query_by_value(runner):
    mock = _mock_vault()
    with patch("envault.cli_search.Vault", return_value=mock):
        result = runner.invoke(search, ["query", "myapp", "--password", "pass", "--value", "abc"])
    assert result.exit_code == 0
    assert "APP_KEY=abc" in result.output


def test_query_by_tag(runner):
    mock = _mock_vault()
    with patch("envault.cli_search.Vault", return_value=mock):
        result = runner.invoke(search, ["query", "myapp", "--password", "pass", "--tag", "db"])
    assert result.exit_code == 0
    assert "DB_HOST=localhost" in result.output


def test_query_vault_missing(runner):
    mock = _mock_vault(exists=False)
    with patch("envault.cli_search.Vault", return_value=mock):
        result = runner.invoke(search, ["query", "myapp", "--password", "pass", "--key", "*"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_query_no_filters(runner):
    mock = _mock_vault()
    with patch("envault.cli_search.Vault", return_value=mock):
        result = runner.invoke(search, ["query", "myapp", "--password", "pass"])
    assert result.exit_code != 0
    assert "at least one" in result.output


def test_query_no_results(runner):
    mock = _mock_vault()
    with patch("envault.cli_search.Vault", return_value=mock):
        result = runner.invoke(search, ["query", "myapp", "--password", "pass", "--key", "MISSING_*"])
    assert result.exit_code == 0
    assert "No matching" in result.output
