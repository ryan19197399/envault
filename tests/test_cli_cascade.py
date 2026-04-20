"""Tests for envault/cli_cascade.py"""
import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from envault.cli_cascade import cascade


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(exists=True, data=None):
    v = MagicMock()
    v.exists.return_value = exists
    v.data = data or {
        "vars": {"SRC": "hello", "DST": ""},
        "cascade": {},
    }
    return v


def test_add_cascade_success(runner):
    v = _mock_vault()
    with patch("envault.cli_cascade.Vault", return_value=v):
        result = runner.invoke(cascade, ["add", "myvault", "SRC", "DST", "--password", "pw"])
    assert result.exit_code == 0
    assert "SRC -> DST" in result.output


def test_add_cascade_with_transform(runner):
    v = _mock_vault()
    with patch("envault.cli_cascade.Vault", return_value=v):
        result = runner.invoke(
            cascade, ["add", "myvault", "SRC", "DST", "--transform", "upper", "--password", "pw"]
        )
    assert result.exit_code == 0
    assert "upper" in result.output


def test_add_cascade_vault_missing(runner):
    v = _mock_vault(exists=False)
    with patch("envault.cli_cascade.Vault", return_value=v):
        result = runner.invoke(cascade, ["add", "myvault", "SRC", "DST", "--password", "pw"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_remove_cascade_success(runner):
    v = _mock_vault(data={
        "vars": {"SRC": "hello", "DST": ""},
        "cascade": {"SRC": {"target": "DST", "transform": None}},
    })
    with patch("envault.cli_cascade.Vault", return_value=v):
        result = runner.invoke(cascade, ["remove", "myvault", "SRC", "--password", "pw"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_cascade_not_found(runner):
    v = _mock_vault()
    with patch("envault.cli_cascade.Vault", return_value=v):
        result = runner.invoke(cascade, ["remove", "myvault", "SRC", "--password", "pw"])
    assert result.exit_code == 0
    assert "No cascade rule" in result.output


def test_list_cascades_empty(runner):
    v = _mock_vault()
    with patch("envault.cli_cascade.Vault", return_value=v):
        result = runner.invoke(cascade, ["list", "myvault", "--password", "pw"])
    assert result.exit_code == 0
    assert "No cascade rules" in result.output


def test_list_cascades_with_entries(runner):
    v = _mock_vault(data={
        "vars": {"SRC": "hello", "DST": ""},
        "cascade": {"SRC": {"target": "DST", "transform": "upper"}},
    })
    with patch("envault.cli_cascade.Vault", return_value=v):
        result = runner.invoke(cascade, ["list", "myvault", "--password", "pw"])
    assert result.exit_code == 0
    assert "SRC -> DST" in result.output
    assert "upper" in result.output


def test_apply_cascade_success(runner):
    v = _mock_vault(data={
        "vars": {"SRC": "hello", "DST": ""},
        "cascade": {"SRC": {"target": "DST", "transform": "upper"}},
    })
    with patch("envault.cli_cascade.Vault", return_value=v):
        result = runner.invoke(cascade, ["apply", "myvault", "SRC", "--password", "pw"])
    assert result.exit_code == 0
    assert "DST" in result.output
