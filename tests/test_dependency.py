"""Tests for envault.dependency module."""

import pytest
from envault import dependency as dep


@pytest.fixture
def vault_data():
    return {
        "vars": {"DB_URL": "postgres://", "DB_PASS": "secret", "API_KEY": "abc"},
        "dependencies": {},
    }


def test_add_dependency_creates_entry(vault_data):
    dep.add_dependency(vault_data, "DB_URL", "DB_PASS")
    assert "DB_PASS" in vault_data["dependencies"]["DB_URL"]


def test_add_dependency_no_duplicates(vault_data):
    dep.add_dependency(vault_data, "DB_URL", "DB_PASS")
    dep.add_dependency(vault_data, "DB_URL", "DB_PASS")
    assert vault_data["dependencies"]["DB_URL"].count("DB_PASS") == 1


def test_add_dependency_missing_key_raises(vault_data):
    with pytest.raises(KeyError):
        dep.add_dependency(vault_data, "MISSING", "DB_PASS")


def test_add_dependency_missing_depends_on_raises(vault_data):
    with pytest.raises(KeyError):
        dep.add_dependency(vault_data, "DB_URL", "MISSING")


def test_remove_dependency_returns_true(vault_data):
    dep.add_dependency(vault_data, "DB_URL", "DB_PASS")
    result = dep.remove_dependency(vault_data, "DB_URL", "DB_PASS")
    assert result is True
    assert "DB_URL" not in vault_data["dependencies"]


def test_remove_dependency_returns_false_when_absent(vault_data):
    result = dep.remove_dependency(vault_data, "DB_URL", "DB_PASS")
    assert result is False


def test_get_dependencies_returns_list(vault_data):
    dep.add_dependency(vault_data, "DB_URL", "DB_PASS")
    result = dep.get_dependencies(vault_data, "DB_URL")
    assert result == ["DB_PASS"]


def test_get_dependencies_empty_for_unknown(vault_data):
    assert dep.get_dependencies(vault_data, "API_KEY") == []


def test_get_dependents(vault_data):
    dep.add_dependency(vault_data, "DB_URL", "DB_PASS")
    dep.add_dependency(vault_data, "API_KEY", "DB_PASS")
    result = dep.get_dependents(vault_data, "DB_PASS")
    assert set(result) == {"DB_URL", "API_KEY"}


def test_list_all_dependencies(vault_data):
    dep.add_dependency(vault_data, "DB_URL", "DB_PASS")
    result = dep.list_all_dependencies(vault_data)
    assert result == {"DB_URL": ["DB_PASS"]}


def test_check_missing_dependencies_none(vault_data):
    dep.add_dependency(vault_data, "DB_URL", "DB_PASS")
    assert dep.check_missing_dependencies(vault_data) == {}


def test_check_missing_dependencies_detects_missing(vault_data):
    vault_data["dependencies"]["DB_URL"] = ["GHOST_KEY"]
    result = dep.check_missing_dependencies(vault_data)
    assert "DB_URL" in result
    assert "GHOST_KEY" in result["DB_URL"]
