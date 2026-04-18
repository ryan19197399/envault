"""Tests for envault/rename.py"""

import pytest
from envault.rename import rename_key, set_alias, remove_alias, resolve_alias, list_aliases


@pytest.fixture
def vault_data():
    return {
        "env": {"DB_HOST": "localhost", "DB_PORT": "5432"},
        "tags": {"DB_HOST": ["db"]},
        "notes": {"DB_HOST": "primary host"},
        "ttl": {"DB_HOST": 9999999999},
    }


def test_rename_key_success(vault_data):
    rename_key(vault_data, "DB_HOST", "DATABASE_HOST")
    assert "DATABASE_HOST" in vault_data["env"]
    assert "DB_HOST" not in vault_data["env"]
    assert vault_data["env"]["DATABASE_HOST"] == "localhost"


def test_rename_key_migrates_tags(vault_data):
    rename_key(vault_data, "DB_HOST", "DATABASE_HOST")
    assert "DATABASE_HOST" in vault_data["tags"]
    assert "DB_HOST" not in vault_data["tags"]


def test_rename_key_migrates_notes(vault_data):
    rename_key(vault_data, "DB_HOST", "DATABASE_HOST")
    assert vault_data["notes"]["DATABASE_HOST"] == "primary host"


def test_rename_key_migrates_ttl(vault_data):
    rename_key(vault_data, "DB_HOST", "DATABASE_HOST")
    assert "DATABASE_HOST" in vault_data["ttl"]
    assert "DB_HOST" not in vault_data["ttl"]


def test_rename_key_missing_raises(vault_data):
    with pytest.raises(KeyError):
        rename_key(vault_data, "MISSING_KEY", "NEW_KEY")


def test_rename_key_conflict_raises(vault_data):
    with pytest.raises(ValueError):
        rename_key(vault_data, "DB_HOST", "DB_PORT")


def test_rename_key_conflict_overwrite(vault_data):
    rename_key(vault_data, "DB_HOST", "DB_PORT", overwrite=True)
    assert vault_data["env"]["DB_PORT"] == "localhost"


def test_set_alias_success(vault_data):
    set_alias(vault_data, "DB_HOST", "host")
    assert vault_data["aliases"]["host"] == "DB_HOST"


def test_set_alias_missing_key_raises(vault_data):
    with pytest.raises(KeyError):
        set_alias(vault_data, "NONEXISTENT", "alias")


def test_remove_alias_returns_true(vault_data):
    set_alias(vault_data, "DB_HOST", "host")
    result = remove_alias(vault_data, "host")
    assert result is True
    assert "host" not in vault_data.get("aliases", {})


def test_remove_alias_missing_returns_false(vault_data):
    result = remove_alias(vault_data, "nonexistent")
    assert result is False


def test_resolve_alias_direct_key(vault_data):
    assert resolve_alias(vault_data, "DB_HOST") == "localhost"


def test_resolve_alias_via_alias(vault_data):
    set_alias(vault_data, "DB_HOST", "host")
    assert resolve_alias(vault_data, "host") == "localhost"


def test_resolve_alias_missing_returns_none(vault_data):
    assert resolve_alias(vault_data, "UNKNOWN") is None


def test_list_aliases_empty(vault_data):
    assert list_aliases(vault_data) == {}


def test_list_aliases_returns_all(vault_data):
    set_alias(vault_data, "DB_HOST", "host")
    set_alias(vault_data, "DB_PORT", "port")
    aliases = list_aliases(vault_data)
    assert aliases == {"host": "DB_HOST", "port": "DB_PORT"}
