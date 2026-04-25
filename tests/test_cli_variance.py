"""Tests for envault.cli_variance."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_variance import variance


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(data):
    """Return (load_vault patch, save_vault patch, vault_exists patch)."""
    return (
        patch("envault.cli_variance.vault_exists", return_value=True),
        patch("envault.cli_variance.load_vault", return_value=data),
        patch("envault.cli_variance.save_vault"),
    )


def _vault_data():
    return {"vars": {"DB_HOST": "localhost", "DB_PORT": "5432"}}


def test_set_baseline_success(runner):
    data = _vault_data()
    exists, load, save = _mock_vault(data)
    with exists, load, save as mock_save:
        result = runner.invoke(variance, ["set", "myvault", "DB_HOST", "--password", "pw"])
    assert result.exit_code == 0
    assert "Baseline set" in result.output
    mock_save.assert_called_once()


def test_set_baseline_explicit_value(runner):
    data = _vault_data()
    exists, load, save = _mock_vault(data)
    with exists, load, save:
        result = runner.invoke(
            variance, ["set", "myvault", "DB_HOST", "--password", "pw", "--value", "remotehost"]
        )
    assert result.exit_code == 0
    assert "remotehost" in result.output


def test_set_baseline_vault_missing(runner):
    with patch("envault.cli_variance.vault_exists", return_value=False):
        result = runner.invoke(variance, ["set", "missing", "DB_HOST", "--password", "pw"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_set_baseline_key_missing(runner):
    data = _vault_data()
    exists, load, save = _mock_vault(data)
    with exists, load, save:
        result = runner.invoke(variance, ["set", "myvault", "NOPE", "--password", "pw"])
    assert result.exit_code != 0


def test_check_no_drift(runner):
    data = _vault_data()
    data["variance"] = {"DB_HOST": "localhost"}
    exists, load, save = _mock_vault(data)
    with exists, load, save:
        result = runner.invoke(variance, ["check", "myvault", "DB_HOST", "--password", "pw"])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_check_drift_detected(runner):
    data = _vault_data()
    data["variance"] = {"DB_HOST": "oldhost"}
    exists, load, save = _mock_vault(data)
    with exists, load, save:
        result = runner.invoke(variance, ["check", "myvault", "DB_HOST", "--password", "pw"])
    assert result.exit_code == 0
    assert "DRIFTED" in result.output


def test_report_shows_all_baselined(runner):
    data = _vault_data()
    data["variance"] = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    exists, load, save = _mock_vault(data)
    with exists, load, save:
        result = runner.invoke(variance, ["report", "myvault", "--password", "pw"])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "DB_PORT" in result.output


def test_report_drifted_only(runner):
    data = _vault_data()
    data["variance"] = {"DB_HOST": "oldhost", "DB_PORT": "5432"}
    exists, load, save = _mock_vault(data)
    with exists, load, save:
        result = runner.invoke(
            variance, ["report", "myvault", "--password", "pw", "--drifted-only"]
        )
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "DB_PORT" not in result.output
