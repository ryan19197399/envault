"""Tests for envault.cli_rating."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_rating import rating


@pytest.fixture()
def runner():
    return CliRunner()


_VAULT = {
    "vars": {"API_KEY": "s3cr3t", "DB_HOST": "localhost"},
    "notes": {"API_KEY": "main key"},
    "tags": {"API_KEY": ["prod"]},
    "schema": {"API_KEY": {"type": "str"}},
    "ttl": {},
    "immutable": [],
}


def _mock_vault(exists=True, data=None):
    return (
        patch("envault.cli_rating.vault_exists", return_value=exists),
        patch("envault.cli_rating.load_vault", return_value=data or _VAULT),
    )


def test_show_rating_success(runner):
    with _mock_vault()[0], _mock_vault()[1]:
        result = runner.invoke(rating, ["show", "myvault", "API_KEY"])
    assert result.exit_code == 0
    assert "Score" in result.output
    assert "Breakdown" in result.output


def test_show_rating_vault_missing(runner):
    with patch("envault.cli_rating.vault_exists", return_value=False):
        result = runner.invoke(rating, ["show", "ghost", "KEY"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_show_rating_key_missing(runner):
    with patch("envault.cli_rating.vault_exists", return_value=True), \
         patch("envault.cli_rating.load_vault", return_value=_VAULT):
        result = runner.invoke(rating, ["show", "myvault", "NO_SUCH_KEY"])
    assert result.exit_code != 0


def test_all_cmd_lists_keys(runner):
    with patch("envault.cli_rating.vault_exists", return_value=True), \
         patch("envault.cli_rating.load_vault", return_value=_VAULT):
        result = runner.invoke(rating, ["all", "myvault"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DB_HOST" in result.output


def test_all_cmd_min_score_filter(runner):
    with patch("envault.cli_rating.vault_exists", return_value=True), \
         patch("envault.cli_rating.load_vault", return_value=_VAULT):
        result = runner.invoke(rating, ["all", "myvault", "--min-score", "101"])
    assert result.exit_code == 0
    assert "No keys match" in result.output


def test_summary_cmd(runner):
    with patch("envault.cli_rating.vault_exists", return_value=True), \
         patch("envault.cli_rating.load_vault", return_value=_VAULT):
        result = runner.invoke(rating, ["summary", "myvault"])
    assert result.exit_code == 0
    assert "Average" in result.output
    assert "Keys" in result.output


def test_summary_vault_missing(runner):
    with patch("envault.cli_rating.vault_exists", return_value=False):
        result = runner.invoke(rating, ["summary", "ghost"])
    assert result.exit_code != 0
