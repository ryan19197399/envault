import time
import pytest
from envault.lint import (
    lint_key_naming,
    lint_empty_values,
    lint_duplicate_values,
    lint_expired_ttl,
    run_lint,
)


@pytest.fixture
def vault_data():
    return {
        "vars": {
            "DATABASE_URL": "postgres://localhost/db",
            "api_key": "secret123",
            "PORT": "",
            "REDIS_URL": "postgres://localhost/db",
        },
        "ttl": {
            "DATABASE_URL": time.time() - 100,
            "REDIS_URL": time.time() + 9999,
        },
    }


def test_lint_key_naming_flags_lowercase(vault_data):
    issues = lint_key_naming(vault_data)
    keys = [i["key"] for i in issues]
    assert "api_key" in keys


def test_lint_key_naming_passes_upper_snake(vault_data):
    issues = lint_key_naming(vault_data)
    keys = [i["key"] for i in issues]
    assert "DATABASE_URL" not in keys
    assert "PORT" not in keys


def test_lint_empty_values_flags_empty(vault_data):
    issues = lint_empty_values(vault_data)
    keys = [i["key"] for i in issues]
    assert "PORT" in keys


def test_lint_empty_values_ignores_nonempty(vault_data):
    issues = lint_empty_values(vault_data)
    keys = [i["key"] for i in issues]
    assert "DATABASE_URL" not in keys


def test_lint_duplicate_values_flags_shared(vault_data):
    issues = lint_duplicate_values(vault_data)
    assert len(issues) == 1
    assert "duplicate_value" == issues[0]["issue"]


def test_lint_duplicate_values_no_issue_when_unique():
    data = {"vars": {"A": "1", "B": "2"}}
    assert lint_duplicate_values(data) == []


def test_lint_expired_ttl_flags_expired(vault_data):
    issues = lint_expired_ttl(vault_data)
    keys = [i["key"] for i in issues]
    assert "DATABASE_URL" in keys


def test_lint_expired_ttl_ignores_valid(vault_data):
    issues = lint_expired_ttl(vault_data)
    keys = [i["key"] for i in issues]
    assert "REDIS_URL" not in keys


def test_run_lint_returns_all_issues(vault_data):
    issues = run_lint(vault_data)
    issue_types = {i["issue"] for i in issues}
    assert "naming" in issue_types
    assert "empty_value" in issue_types
    assert "duplicate_value" in issue_types
    assert "expired_ttl" in issue_types


def test_run_lint_selective_checks(vault_data):
    issues = run_lint(vault_data, checks=["naming"])
    issue_types = {i["issue"] for i in issues}
    assert issue_types == {"naming"}


def test_run_lint_empty_vault():
    assert run_lint({}) == []
