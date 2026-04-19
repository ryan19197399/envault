"""Tests for envault.cli_secrets_gen."""
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envault.cli_secrets_gen import gen


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(vars_dict):
    v = MagicMock()
    v.data = {"vars": vars_dict}
    return v


def test_password_prints_value(runner):
    result = runner.invoke(gen, ["password"])
    assert result.exit_code == 0
    assert len(result.output.strip()) == 32


def test_password_custom_length(runner):
    result = runner.invoke(gen, ["password", "--length", "16"])
    assert result.exit_code == 0
    assert len(result.output.strip()) == 16


def test_token_prints_value(runner):
    result = runner.invoke(gen, ["token"])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 0


def test_hex_prints_value(runner):
    result = runner.invoke(gen, ["hex", "--bytes", "16"])
    assert result.exit_code == 0
    output = result.output.strip()
    assert len(output) == 32
    int(output, 16)


def test_password_set_vault_missing(runner):
    with patch("envault.cli_secrets_gen.vault_exists", return_value=False):
        result = runner.invoke(gen, ["password", "--set", "SECRET_KEY",
                                     "--vault", "myvault", "--password", "pw"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_password_set_stores_value(runner):
    mock_vault = _mock_vault({"SECRET_KEY": "old"})
    with patch("envault.cli_secrets_gen.vault_exists", return_value=True), \
         patch("envault.cli_secrets_gen.Vault.load", return_value=mock_vault):
        result = runner.invoke(gen, ["password", "--set", "SECRET_KEY",
                                     "--vault", "default", "--password", "pw"])
    assert result.exit_code == 0
    assert "Set 'SECRET_KEY'" in result.output
    assert mock_vault.data["vars"]["SECRET_KEY"] != "old"
