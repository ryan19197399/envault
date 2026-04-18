"""Tests for envault/search.py"""

import pytest
from envault.search import search_keys, search_values, search_by_tag, search_combined


@pytest.fixture
def vault_data():
    return {
        "vars": {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "APP_SECRET": "s3cr3t",
            "APP_DEBUG": "true",
        },
        "tags": {
            "DB_HOST": ["db", "infra"],
            "DB_PORT": ["db"],
            "APP_SECRET": ["app", "sensitive"],
        },
    }


def test_search_keys_glob(vault_data):
    result = search_keys(vault_data, "DB_*")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_search_keys_exact(vault_data):
    result = search_keys(vault_data, "APP_DEBUG")
    assert result == {"APP_DEBUG": "true"}


def test_search_keys_no_match(vault_data):
    result = search_keys(vault_data, "MISSING_*")
    assert result == {}


def test_search_values_substring(vault_data):
    result = search_values(vault_data, "local")
    assert result == {"DB_HOST": "localhost"}


def test_search_values_no_match(vault_data):
    result = search_values(vault_data, "zzz")
    assert result == {}


def test_search_by_tag(vault_data):
    result = search_by_tag(vault_data, "db")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_search_by_tag_no_match(vault_data):
    result = search_by_tag(vault_data, "nonexistent")
    assert result == {}


def test_search_combined_key_and_tag(vault_data):
    result = search_combined(vault_data, key_pattern="DB_*", tag="infra")
    assert result == {"DB_HOST": "localhost"}


def test_search_combined_all_filters(vault_data):
    result = search_combined(vault_data, key_pattern="APP_*", value_substr="s3cr3t", tag="sensitive")
    assert result == {"APP_SECRET": "s3cr3t"}


def test_search_combined_no_filters_returns_all(vault_data):
    result = search_combined(vault_data)
    assert result == vault_data["vars"]
