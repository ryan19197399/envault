import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envault.cli_condvar import condvar


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(data):
    vault = MagicMock()
    vault.data = data
    return vault


def test_add_condvar_success(runner):
    data = {"vars": {"LOG_LEVEL": "info", "ENV": "production"}}
    vault = _mock_vault(data)
    with patch("envault.cli_condvar.vault_exists", return_value=True), \
         patch("envault.cli_condvar.Vault", return_value=vault):
        result = runner.invoke(condvar, [
            "add", "LOG_LEVEL", "ENV",
            "--when", "production:warn",
            "--when", "development:debug",
            "--vault", "myapp",
            "--password", "secret"
        ])
    assert result.exit_code == 0
    assert "Condvar rule added" in result.output
    vault.save.assert_called_once()


def test_add_condvar_vault_missing(runner):
    with patch("envault.cli_condvar.vault_exists", return_value=False):
        result = runner.invoke(condvar, [
            "add", "LOG_LEVEL", "ENV",
            "--when", "production:warn",
            "--vault", "missing",
            "--password", "secret"
        ])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_add_condvar_invalid_condition_format(runner):
    data = {"vars": {"LOG_LEVEL": "info", "ENV": "production"}}
    vault = _mock_vault(data)
    with patch("envault.cli_condvar.vault_exists", return_value=True), \
         patch("envault.cli_condvar.Vault", return_value=vault):
        result = runner.invoke(condvar, [
            "add", "LOG_LEVEL", "ENV",
            "--when", "badformat",
            "--vault", "myapp",
            "--password", "secret"
        ])
    assert result.exit_code != 0
    assert "Invalid condition format" in result.output


def test_remove_condvar_success(runner):
    data = {
        "vars": {"LOG_LEVEL": "info", "ENV": "production"},
        "__condvars__": {"LOG_LEVEL": {"source": "ENV", "conditions": {"production": "warn"}, "default": None}}
    }
    vault = _mock_vault(data)
    with patch("envault.cli_condvar.vault_exists", return_value=True), \
         patch("envault.cli_condvar.Vault", return_value=vault):
        result = runner.invoke(condvar, [
            "remove", "LOG_LEVEL",
            "--vault", "myapp",
            "--password", "secret"
        ])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_condvars_empty(runner):
    data = {"vars": {"ENV": "production"}}
    vault = _mock_vault(data)
    with patch("envault.cli_condvar.vault_exists", return_value=True), \
         patch("envault.cli_condvar.Vault", return_value=vault):
        result = runner.invoke(condvar, [
            "list",
            "--vault", "myapp",
            "--password", "secret"
        ])
    assert result.exit_code == 0
    assert "No condvar rules" in result.output


def test_apply_condvars_success(runner):
    data = {
        "vars": {"LOG_LEVEL": "info", "ENV": "production"},
        "__condvars__": {"LOG_LEVEL": {"source": "ENV", "conditions": {"production": "warn"}, "default": None}}
    }
    vault = _mock_vault(data)
    with patch("envault.cli_condvar.vault_exists", return_value=True), \
         patch("envault.cli_condvar.Vault", return_value=vault):
        result = runner.invoke(condvar, [
            "apply",
            "--vault", "myapp",
            "--password", "secret"
        ])
    assert result.exit_code == 0
    assert "applied" in result.output
    vault.save.assert_called_once()
