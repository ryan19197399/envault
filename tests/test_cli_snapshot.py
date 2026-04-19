"""Tests for envault.cli_snapshot."""
import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from envault.cli_snapshot import snapshot


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(data=None, exists=True):
    v = MagicMock()
    v.exists.return_value = exists
    v.data = data or {"vars": {"KEY": "val"}}
    return v


def test_create_snapshot_success(runner):
    v = _mock_vault()
    with patch("envault.cli_snapshot.Vault", return_value=v):
        result = runner.invoke(snapshot, ["create", "myvault", "--name", "snap1", "--password", "secret"])
    assert result.exit_code == 0
    assert "snap1" in result.output
    v.save.assert_called_once()


def test_create_snapshot_vault_missing(runner):
    v = _mock_vault(exists=False)
    with patch("envault.cli_snapshot.Vault", return_value=v):
        result = runner.invoke(snapshot, ["create", "myvault", "--password", "secret"])
    assert result.exit_code != 0


def test_restore_snapshot_success(runner):
    v = _mock_vault()
    with patch("envault.cli_snapshot.Vault", return_value=v), \
         patch("envault.cli_snapshot.restore_snapshot", return_value=True) as mock_restore:
        result = runner.invoke(snapshot, ["restore", "myvault", "snap1", "--password", "secret"])
    assert result.exit_code == 0
    assert "snap1" in result.output
    v.save.assert_called_once()


def test_restore_snapshot_missing(runner):
    v = _mock_vault()
    with patch("envault.cli_snapshot.Vault", return_value=v), \
         patch("envault.cli_snapshot.restore_snapshot", return_value=False):
        result = runner.invoke(snapshot, ["restore", "myvault", "ghost", "--password", "secret"])
    assert result.exit_code != 0


def test_list_snapshots_empty(runner):
    v = _mock_vault()
    with patch("envault.cli_snapshot.Vault", return_value=v), \
         patch("envault.cli_snapshot.list_snapshots", return_value=[]):
        result = runner.invoke(snapshot, ["list", "myvault", "--password", "secret"])
    assert result.exit_code == 0
    assert "No snapshots" in result.output


def test_delete_snapshot_success(runner):
    v = _mock_vault()
    with patch("envault.cli_snapshot.Vault", return_value=v), \
         patch("envault.cli_snapshot.delete_snapshot", return_value=True):
        result = runner.invoke(snapshot, ["delete", "myvault", "snap1", "--password", "secret"])
    assert result.exit_code == 0
    assert "deleted" in result.output
