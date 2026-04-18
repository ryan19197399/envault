"""Tests for envault.tags module."""
import pytest
from envault.tags import (
    set_tag, remove_tag, get_tags, list_by_tag, all_tags, TAGS_KEY
)


@pytest.fixture
def vault_data():
    return {"DB_URL": "postgres://localhost", "API_KEY": "secret"}


def test_set_tag_creates_tags_key(vault_data):
    set_tag(vault_data, "DB_URL", "database")
    assert TAGS_KEY in vault_data
    assert "database" in vault_data[TAGS_KEY]["DB_URL"]


def test_set_tag_no_duplicates(vault_data):
    set_tag(vault_data, "DB_URL", "database")
    set_tag(vault_data, "DB_URL", "database")
    assert vault_data[TAGS_KEY]["DB_URL"].count("database") == 1


def test_set_multiple_tags(vault_data):
    set_tag(vault_data, "DB_URL", "database")
    set_tag(vault_data, "DB_URL", "production")
    assert "database" in get_tags(vault_data, "DB_URL")
    assert "production" in get_tags(vault_data, "DB_URL")


def test_remove_tag_returns_true(vault_data):
    set_tag(vault_data, "API_KEY", "auth")
    result = remove_tag(vault_data, "API_KEY", "auth")
    assert result is True
    assert get_tags(vault_data, "API_KEY") == []


def test_remove_tag_cleans_empty_key(vault_data):
    set_tag(vault_data, "API_KEY", "auth")
    remove_tag(vault_data, "API_KEY", "auth")
    assert "API_KEY" not in vault_data.get(TAGS_KEY, {})


def test_remove_nonexistent_tag_returns_false(vault_data):
    result = remove_tag(vault_data, "API_KEY", "nonexistent")
    assert result is False


def test_get_tags_empty(vault_data):
    assert get_tags(vault_data, "API_KEY") == []


def test_list_by_tag(vault_data):
    set_tag(vault_data, "DB_URL", "production")
    set_tag(vault_data, "API_KEY", "production")
    keys = list_by_tag(vault_data, "production")
    assert set(keys) == {"DB_URL", "API_KEY"}


def test_list_by_tag_no_match(vault_data):
    assert list_by_tag(vault_data, "staging") == []


def test_all_tags(vault_data):
    set_tag(vault_data, "DB_URL", "database")
    set_tag(vault_data, "DB_URL", "production")
    set_tag(vault_data, "API_KEY", "auth")
    result = all_tags(vault_data)
    assert result == sorted(["database", "production", "auth"])


def test_all_tags_empty(vault_data):
    assert all_tags(vault_data) == []
