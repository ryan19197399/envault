"""Tests for envault/group.py"""

import pytest
from envault import group as grp


@pytest.fixture
def vault_data():
    return {"vars": {"DB_URL": "postgres://", "API_KEY": "secret", "TIMEOUT": "30"}}


def test_create_group_creates_key(vault_data):
    grp.create_group(vault_data, "backend")
    assert "groups" in vault_data
    assert "backend" in vault_data["groups"]


def test_create_group_initializes_empty(vault_data):
    grp.create_group(vault_data, "backend")
    assert vault_data["groups"]["backend"] == []


def test_create_group_does_not_overwrite_existing(vault_data):
    vault_data["groups"] = {"backend": ["DB_URL"]}
    grp.create_group(vault_data, "backend")
    assert vault_data["groups"]["backend"] == ["DB_URL"]


def test_delete_group_returns_true(vault_data):
    vault_data["groups"] = {"backend": []}
    assert grp.delete_group(vault_data, "backend") is True


def test_delete_group_removes_entry(vault_data):
    vault_data["groups"] = {"backend": [], "frontend": []}
    grp.delete_group(vault_data, "backend")
    assert "backend" not in vault_data["groups"]
    assert "frontend" in vault_data["groups"]


def test_delete_group_missing_returns_false(vault_data):
    assert grp.delete_group(vault_data, "nonexistent") is False


def test_add_to_group_success(vault_data):
    grp.add_to_group(vault_data, "backend", "DB_URL")
    assert "DB_URL" in vault_data["groups"]["backend"]


def test_add_to_group_no_duplicates(vault_data):
    grp.add_to_group(vault_data, "backend", "DB_URL")
    grp.add_to_group(vault_data, "backend", "DB_URL")
    assert vault_data["groups"]["backend"].count("DB_URL") == 1


def test_add_to_group_missing_key_raises(vault_data):
    with pytest.raises(KeyError):
        grp.add_to_group(vault_data, "backend", "MISSING_KEY")


def test_remove_from_group_returns_true(vault_data):
    vault_data["groups"] = {"backend": ["DB_URL"]}
    assert grp.remove_from_group(vault_data, "backend", "DB_URL") is True


def test_remove_from_group_removes_key(vault_data):
    vault_data["groups"] = {"backend": ["DB_URL", "API_KEY"]}
    grp.remove_from_group(vault_data, "backend", "DB_URL")
    assert "DB_URL" not in vault_data["groups"]["backend"]
    assert "API_KEY" in vault_data["groups"]["backend"]


def test_remove_from_group_missing_returns_false(vault_data):
    vault_data["groups"] = {"backend": []}
    assert grp.remove_from_group(vault_data, "backend", "DB_URL") is False


def test_get_group_returns_keys(vault_data):
    vault_data["groups"] = {"backend": ["DB_URL"]}
    assert grp.get_group(vault_data, "backend") == ["DB_URL"]


def test_get_group_missing_returns_none(vault_data):
    assert grp.get_group(vault_data, "nonexistent") is None


def test_list_groups_returns_all(vault_data):
    vault_data["groups"] = {"backend": ["DB_URL"], "frontend": ["API_KEY"]}
    result = grp.list_groups(vault_data)
    assert set(result.keys()) == {"backend", "frontend"}


def test_list_groups_empty(vault_data):
    assert grp.list_groups(vault_data) == {}


def test_key_groups_returns_containing_groups(vault_data):
    vault_data["groups"] = {"backend": ["DB_URL", "API_KEY"], "infra": ["DB_URL"]}
    result = grp.key_groups(vault_data, "DB_URL")
    assert set(result) == {"backend", "infra"}


def test_key_groups_not_in_any(vault_data):
    vault_data["groups"] = {"backend": ["API_KEY"]}
    assert grp.key_groups(vault_data, "DB_URL") == []
