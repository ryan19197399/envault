import pytest
from envault.env_check import check_missing, check_extra, check_mismatched, check_env

VAULT = {"DB_URL": "postgres://localhost", "SECRET": "abc", "PORT": "5432"}
ENV = {"DB_URL": "postgres://localhost", "PORT": "9999", "EXTRA_VAR": "hello"}


def test_check_missing_returns_absent_keys():
    result = check_missing(VAULT, ENV)
    assert "SECRET" in result
    assert "DB_URL" not in result


def test_check_missing_empty_when_all_present():
    assert check_missing({"A": "1"}, {"A": "1", "B": "2"}) == []


def test_check_extra_returns_env_only_keys():
    result = check_extra(VAULT, ENV)
    assert "EXTRA_VAR" in result
    assert "DB_URL" not in result


def test_check_extra_empty_when_env_subset():
    assert check_extra({"A": "1", "B": "2"}, {"A": "1"}) == []


def test_check_mismatched_returns_differing_keys():
    result = check_mismatched(VAULT, ENV)
    assert "PORT" in result
    assert "DB_URL" not in result


def test_check_mismatched_empty_when_all_match():
    assert check_mismatched({"A": "1"}, {"A": "1"}) == []


def test_check_env_returns_all_categories():
    report = check_env(VAULT, ENV)
    assert "missing" in report
    assert "extra" in report
    assert "mismatched" in report
    assert "SECRET" in report["missing"]
    assert "EXTRA_VAR" in report["extra"]
    assert "PORT" in report["mismatched"]


def test_check_env_empty_vault():
    report = check_env({}, {"A": "1"})
    assert report["missing"] == []
    assert "A" in report["extra"]
    assert report["mismatched"] == []


def test_check_env_empty_env():
    report = check_env({"A": "1"}, {})
    assert "A" in report["missing"]
    assert report["extra"] == []
    assert report["mismatched"] == []
