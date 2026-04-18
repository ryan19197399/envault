import pytest
from envault.profiles import (
    save_profile,
    delete_profile,
    get_profile,
    list_profiles,
    apply_profile,
    PROFILES_KEY,
)


@pytest.fixture
def vault_data():
    return {
        "vars": {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "API_KEY": "secret",
            "DEBUG": "true",
        }
    }


def test_save_profile_creates_key(vault_data):
    result = save_profile(vault_data, "dev", ["DB_HOST", "DB_PORT"])
    assert PROFILES_KEY in result


def test_save_profile_stores_keys(vault_data):
    save_profile(vault_data, "dev", ["DB_HOST", "DB_PORT"])
    assert set(vault_data[PROFILES_KEY]["dev"]) == {"DB_HOST", "DB_PORT"}


def test_save_profile_no_duplicates(vault_data):
    save_profile(vault_data, "dev", ["DB_HOST", "DB_HOST", "DB_PORT"])
    assert vault_data[PROFILES_KEY]["dev"].count("DB_HOST") == 1


def test_save_profile_overwrites(vault_data):
    save_profile(vault_data, "dev", ["DB_HOST"])
    save_profile(vault_data, "dev", ["API_KEY"])
    assert vault_data[PROFILES_KEY]["dev"] == ["API_KEY"]


def test_get_profile_returns_keys(vault_data):
    save_profile(vault_data, "prod", ["API_KEY", "DB_HOST"])
    keys = get_profile(vault_data, "prod")
    assert set(keys) == {"API_KEY", "DB_HOST"}


def test_get_profile_missing_returns_none(vault_data):
    assert get_profile(vault_data, "nonexistent") is None


def test_delete_profile_returns_true(vault_data):
    save_profile(vault_data, "staging", ["DEBUG"])
    assert delete_profile(vault_data, "staging") is True
    assert "staging" not in vault_data[PROFILES_KEY]


def test_delete_profile_missing_returns_false(vault_data):
    assert delete_profile(vault_data, "ghost") is False


def test_list_profiles(vault_data):
    save_profile(vault_data, "dev", ["DEBUG"])
    save_profile(vault_data, "prod", ["API_KEY"])
    profiles = list_profiles(vault_data)
    assert "dev" in profiles
    assert "prod" in profiles


def test_apply_profile_returns_vars(vault_data):
    save_profile(vault_data, "dev", ["DB_HOST", "DB_PORT"])
    result = apply_profile(vault_data, "dev")
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_apply_profile_skips_missing_vars(vault_data):
    save_profile(vault_data, "dev", ["DB_HOST", "MISSING_KEY"])
    result = apply_profile(vault_data, "dev")
    assert "MISSING_KEY" not in result


def test_apply_profile_not_found_returns_none(vault_data):
    assert apply_profile(vault_data, "unknown") is None
