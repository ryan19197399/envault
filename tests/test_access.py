"""Tests for envault/access.py"""

import pytest
from envault import access as ac


@pytest.fixture
def vault_data():
    return {"vars": {"API_KEY": "secret", "DB_URL": "postgres://localhost/db"}}


def test_set_permission_creates_access_key(vault_data):
    ac.set_permission(vault_data, "API_KEY", "read", "alice")
    assert ac.ACCESS_KEY in vault_data


def test_set_permission_grants_read(vault_data):
    ac.set_permission(vault_data, "API_KEY", "read", "alice")
    assert "alice" in vault_data[ac.ACCESS_KEY]["API_KEY"]["read"]


def test_set_permission_grants_write(vault_data):
    ac.set_permission(vault_data, "API_KEY", "write", "bob")
    assert "bob" in vault_data[ac.ACCESS_KEY]["API_KEY"]["write"]


def test_set_permission_no_duplicates(vault_data):
    ac.set_permission(vault_data, "API_KEY", "read", "alice")
    ac.set_permission(vault_data, "API_KEY", "read", "alice")
    assert vault_data[ac.ACCESS_KEY]["API_KEY"]["read"].count("alice") == 1


def test_set_permission_invalid_perm_raises(vault_data):
    with pytest.raises(ValueError):
        ac.set_permission(vault_data, "API_KEY", "admin", "alice")


def test_remove_permission_returns_true(vault_data):
    ac.set_permission(vault_data, "API_KEY", "read", "alice")
    result = ac.remove_permission(vault_data, "API_KEY", "read", "alice")
    assert result is True


def test_remove_permission_removes_principal(vault_data):
    ac.set_permission(vault_data, "API_KEY", "read", "alice")
    ac.remove_permission(vault_data, "API_KEY", "read", "alice")
    assert "alice" not in vault_data[ac.ACCESS_KEY]["API_KEY"]["read"]


def test_remove_permission_returns_false_if_missing(vault_data):
    result = ac.remove_permission(vault_data, "API_KEY", "read", "ghost")
    assert result is False


def test_has_permission_true(vault_data):
    ac.set_permission(vault_data, "DB_URL", "write", "carol")
    assert ac.has_permission(vault_data, "DB_URL", "write", "carol") is True


def test_has_permission_false(vault_data):
    assert ac.has_permission(vault_data, "DB_URL", "read", "carol") is False


def test_get_permissions_returns_empty_structure(vault_data):
    perms = ac.get_permissions(vault_data, "MISSING_KEY")
    assert perms == {"read": [], "write": []}


def test_list_access_returns_all(vault_data):
    ac.set_permission(vault_data, "API_KEY", "read", "alice")
    ac.set_permission(vault_data, "DB_URL", "write", "bob")
    result = ac.list_access(vault_data)
    assert "API_KEY" in result
    assert "DB_URL" in result


def test_clear_permissions_returns_true(vault_data):
    ac.set_permission(vault_data, "API_KEY", "read", "alice")
    result = ac.clear_permissions(vault_data, "API_KEY")
    assert result is True
    assert "API_KEY" not in vault_data.get(ac.ACCESS_KEY, {})


def test_clear_permissions_returns_false_if_absent(vault_data):
    result = ac.clear_permissions(vault_data, "NONEXISTENT")
    assert result is False
