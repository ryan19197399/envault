"""Tests for envault.variance."""

import pytest

from envault.variance import (
    check_variance,
    get_baseline,
    remove_baseline,
    set_baseline,
    variance_report,
)


@pytest.fixture
def vault_data():
    return {
        "vars": {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "API_KEY": "secret",
        }
    }


def test_set_baseline_creates_variance_key(vault_data):
    set_baseline(vault_data, "DB_HOST")
    assert "variance" in vault_data


def test_set_baseline_stores_current_value(vault_data):
    set_baseline(vault_data, "DB_HOST")
    assert vault_data["variance"]["DB_HOST"] == "localhost"


def test_set_baseline_explicit_value(vault_data):
    set_baseline(vault_data, "DB_HOST", value="remotehost")
    assert vault_data["variance"]["DB_HOST"] == "remotehost"


def test_set_baseline_missing_key_raises(vault_data):
    with pytest.raises(KeyError):
        set_baseline(vault_data, "MISSING_KEY")


def test_get_baseline_returns_value(vault_data):
    set_baseline(vault_data, "DB_PORT")
    assert get_baseline(vault_data, "DB_PORT") == "5432"


def test_get_baseline_missing_returns_none(vault_data):
    assert get_baseline(vault_data, "DB_HOST") is None


def test_remove_baseline_returns_true(vault_data):
    set_baseline(vault_data, "DB_HOST")
    assert remove_baseline(vault_data, "DB_HOST") is True
    assert "DB_HOST" not in vault_data.get("variance", {})


def test_remove_baseline_missing_returns_false(vault_data):
    assert remove_baseline(vault_data, "DB_HOST") is False


def test_check_variance_no_drift(vault_data):
    set_baseline(vault_data, "DB_HOST")
    result = check_variance(vault_data, "DB_HOST")
    assert result["drifted"] is False
    assert result["baseline"] == "localhost"
    assert result["current"] == "localhost"


def test_check_variance_detects_drift(vault_data):
    set_baseline(vault_data, "DB_HOST")
    vault_data["vars"]["DB_HOST"] = "newhost"
    result = check_variance(vault_data, "DB_HOST")
    assert result["drifted"] is True
    assert result["current"] == "newhost"


def test_check_variance_no_baseline_not_drifted(vault_data):
    result = check_variance(vault_data, "DB_HOST")
    assert result["drifted"] is False
    assert result["baseline"] is None


def test_check_variance_missing_key_raises(vault_data):
    with pytest.raises(KeyError):
        check_variance(vault_data, "NOPE")


def test_variance_report_returns_all_baselined(vault_data):
    set_baseline(vault_data, "DB_HOST")
    set_baseline(vault_data, "DB_PORT")
    report = variance_report(vault_data)
    keys = [r["key"] for r in report]
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys


def test_variance_report_sorted_by_key(vault_data):
    set_baseline(vault_data, "DB_PORT")
    set_baseline(vault_data, "API_KEY")
    set_baseline(vault_data, "DB_HOST")
    report = variance_report(vault_data)
    keys = [r["key"] for r in report]
    assert keys == sorted(keys)


def test_variance_report_skips_missing_vars(vault_data):
    set_baseline(vault_data, "DB_HOST")
    vault_data["variance"]["GHOST_KEY"] = "old"
    report = variance_report(vault_data)
    keys = [r["key"] for r in report]
    assert "GHOST_KEY" not in keys
