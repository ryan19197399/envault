import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envault.cli_profiles import profile


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(data=None):
    v = MagicMock()
    v.data = data or {"vars": {"DB_HOST": "localhost", "API_KEY": "secret"}}
    return v


def test_save_profile(runner):
    v = _mock_vault()
    with patch("envault.cli_profiles.Vault", return_value=v):
        result = runner.invoke(
            profile, ["save", "dev", "DB_HOST", "--password", "pass", "--password", "pass"]
        )
    assert result.exit_code == 0
    assert "dev" in result.output


def test_delete_profile_existing(runner):
    v = _mock_vault(data={"vars": {}, "__profiles__": {"dev": ["DB_HOST"]}})
    with patch("envault.cli_profiles.Vault", return_value=v):
        result = runner.invoke(
            profile, ["delete", "dev", "--password", "pass", "--password", "pass"]
        )
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_delete_profile_missing(runner):
    v = _mock_vault()
    with patch("envault.cli_profiles.Vault", return_value=v):
        result = runner.invoke(
            profile, ["delete", "ghost", "--password", "pass", "--password", "pass"]
        )
    assert "not found" in result.output


def test_list_profiles_empty(runner):
    v = _mock_vault()
    with patch("envault.cli_profiles.Vault", return_value=v):
        result = runner.invoke(profile, ["list", "--password", "pass", "--password", "pass"])
    assert "No profiles" in result.output


def test_list_profiles_with_entries(runner):
    v = _mock_vault(data={"vars": {}, "__profiles__": {"prod": ["API_KEY"]}})
    with patch("envault.cli_profiles.Vault", return_value=v):
        result = runner.invoke(profile, ["list", "--password", "pass", "--password", "pass"])
    assert "prod" in result.output
    assert "API_KEY" in result.output


def test_apply_profile_export(runner):
    v = _mock_vault(data={"vars": {"DB_HOST": "localhost"}, "__profiles__": {"dev": ["DB_HOST"]}})
    with patch("envault.cli_profiles.Vault", return_value=v):
        result = runner.invoke(
            profile, ["apply", "dev", "--password", "pass", "--password", "pass"]
        )
    assert "DB_HOST" in result.output


def test_apply_profile_not_found(runner):
    v = _mock_vault()
    with patch("envault.cli_profiles.Vault", return_value=v):
        result = runner.invoke(
            profile, ["apply", "missing", "--password", "pass", "--password", "pass"]
        )
    assert "not found" in result.output
