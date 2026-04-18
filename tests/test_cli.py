import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envault.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_init_creates_vault(runner, tmp_path):
    with patch("envault.storage._vault_path", side_effect=lambda name: tmp_path / f"{name}.vault"):
        with patch("envault.storage.vault_exists", return_value=False):
            mock_vault = MagicMock()
            with patch("envault.cli.Vault", return_value=mock_vault) as MockVault:
                result = runner.invoke(cli, ["init", "myproject"], input="secret\nsecret\n")
                assert result.exit_code == 0
                assert "created successfully" in result.output
                MockVault.assert_called_once_with("myproject", "secret")
                mock_vault.save.assert_called_once()


def test_init_fails_if_vault_exists(runner):
    with patch("envault.storage.vault_exists", return_value=True):
        result = runner.invoke(cli, ["init", "myproject"], input="secret\nsecret\n")
        assert result.exit_code != 0
        assert "already exists" in result.output


def test_set_var(runner):
    mock_vault = MagicMock()
    with patch("envault.cli.Vault") as MockVault:
        MockVault.load.return_value = mock_vault
        result = runner.invoke(cli, ["set", "myproject", "API_KEY", "abc123"], input="secret\n")
        assert result.exit_code == 0
        mock_vault.set.assert_called_once_with("API_KEY", "abc123")
        mock_vault.save.assert_called_once()


def test_get_var(runner):
    mock_vault = MagicMock()
    mock_vault.get.return_value = "abc123"
    with patch("envault.cli.Vault") as MockVault:
        MockVault.load.return_value = mock_vault
        result = runner.invoke(cli, ["get", "myproject", "API_KEY"], input="secret\n")
        assert result.exit_code == 0
        assert "abc123" in result.output


def test_get_var_missing_key(runner):
    mock_vault = MagicMock()
    mock_vault.get.return_value = None
    with patch("envault.cli.Vault") as MockVault:
        MockVault.load.return_value = mock_vault
        result = runner.invoke(cli, ["get", "myproject", "MISSING"], input="secret\n")
        assert result.exit_code != 0


def test_list_vaults_cmd(runner):
    with patch("envault.storage.list_vaults", return_value=["proj1", "proj2"]):
        result = runner.invoke(cli, ["vaults"])
        assert result.exit_code == 0
        assert "proj1" in result.output
        assert "proj2" in result.output
