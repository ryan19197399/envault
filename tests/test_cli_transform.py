"""Tests for envault.cli_transform."""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envault.cli_transform import transform


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(vars_=None, transforms_=None, exists=True):
    v = MagicMock()
    v.exists.return_value = exists
    v.data = {
        "vars": vars_ or {"MY_KEY": "hello"},
        "transforms": transforms_ or {},
    }
    return v


def test_list_transforms(runner):
    result = runner.invoke(transform, ["list"])
    assert result.exit_code == 0
    assert "upper" in result.output
    assert "lower" in result.output


def test_set_pipeline_success(runner):
    mock_v = _mock_vault()
    with patch("envault.cli_transform.Vault", return_value=mock_v):
        result = runner.invoke(
            transform, ["set", "myvault", "MY_KEY", "upper", "strip"],
            input="password\n"
        )
    assert result.exit_code == 0
    assert "MY_KEY" in result.output
    assert "upper" in result.output


def test_set_pipeline_vault_missing(runner):
    mock_v = _mock_vault(exists=False)
    with patch("envault.cli_transform.Vault", return_value=mock_v):
        result = runner.invoke(
            transform, ["set", "myvault", "MY_KEY", "upper"],
            input="password\n"
        )
    assert result.exit_code != 0
    assert "not found" in result.output


def test_set_pipeline_unknown_transform(runner):
    mock_v = _mock_vault()
    with patch("envault.cli_transform.Vault", return_value=mock_v):
        result = runner.invoke(
            transform, ["set", "myvault", "MY_KEY", "bogus"],
            input="password\n"
        )
    assert result.exit_code != 0


def test_remove_pipeline_success(runner):
    mock_v = _mock_vault(transforms_={"MY_KEY": ["upper"]})
    with patch("envault.cli_transform.Vault", return_value=mock_v):
        result = runner.invoke(
            transform, ["remove", "myvault", "MY_KEY"],
            input="password\n"
        )
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_pipeline_not_set(runner):
    mock_v = _mock_vault()
    with patch("envault.cli_transform.Vault", return_value=mock_v):
        result = runner.invoke(
            transform, ["remove", "myvault", "MY_KEY"],
            input="password\n"
        )
    assert result.exit_code == 0
    assert "No pipeline" in result.output


def test_show_pipeline_with_pipeline(runner):
    mock_v = _mock_vault(transforms_={"MY_KEY": ["upper"]})
    with patch("envault.cli_transform.Vault", return_value=mock_v):
        result = runner.invoke(
            transform, ["show", "myvault", "MY_KEY"],
            input="password\n"
        )
    assert result.exit_code == 0
    assert "upper" in result.output
    assert "HELLO" in result.output
