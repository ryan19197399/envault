"""Tests for envault.compare_env."""
import pytest
from envault.compare_env import compare_with_env, format_compare_report


@pytest.fixture
def vault_data():
    return {
        "vars": {
            "DATABASE_URL": "postgres://localhost/dev",
            "SECRET_KEY": "abc123",
            "API_KEY": "vault-api-key",
        }
    }


def test_only_in_vault(vault_data):
    env = {"DATABASE_URL": "postgres://localhost/dev"}
    report = compare_with_env(vault_data, env)
    assert "SECRET_KEY" in report["only_in_vault"]
    assert "API_KEY" in report["only_in_vault"]


def test_only_in_env(vault_data):
    env = {
        "DATABASE_URL": "postgres://localhost/dev",
        "SECRET_KEY": "abc123",
        "API_KEY": "vault-api-key",
        "EXTRA_VAR": "something",
    }
    report = compare_with_env(vault_data, env)
    assert "EXTRA_VAR" in report["only_in_env"]


def test_matching(vault_data):
    env = {
        "DATABASE_URL": "postgres://localhost/dev",
        "SECRET_KEY": "abc123",
        "API_KEY": "vault-api-key",
    }
    report = compare_with_env(vault_data, env)
    assert set(report["matching"]) == {"DATABASE_URL", "SECRET_KEY", "API_KEY"}
    assert report["differing"] == []


def test_differing(vault_data):
    env = {
        "DATABASE_URL": "postgres://localhost/dev",
        "SECRET_KEY": "different-secret",
        "API_KEY": "vault-api-key",
    }
    report = compare_with_env(vault_data, env)
    assert "SECRET_KEY" in report["differing"]
    assert "DATABASE_URL" in report["matching"]


def test_lowercase_env_keys_ignored(vault_data):
    env = {"database_url": "something", "DATABASE_URL": "postgres://localhost/dev"}
    report = compare_with_env(vault_data, env)
    assert "database_url" not in report["only_in_env"]


def test_empty_vault():
    env = {"FOO": "bar"}
    report = compare_with_env({"vars": {}}, env)
    assert "FOO" in report["only_in_env"]
    assert report["only_in_vault"] == []


def test_format_report_in_sync():
    report = {"only_in_vault": [], "only_in_env": [], "matching": ["A"], "differing": []}
    out = format_compare_report(report)
    assert "in sync" in out


def test_format_report_shows_sections(vault_data):
    env = {"EXTRA": "x"}
    report = compare_with_env(vault_data, env)
    out = format_compare_report(report)
    assert "Only in vault" in out
    assert "Only in environment" in out
