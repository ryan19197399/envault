import pytest
from envault.templates import (
    save_template,
    delete_template,
    get_template,
    list_templates,
    apply_template,
    TEMPLATES_KEY,
)


@pytest.fixture
def vault_data():
    return {
        "vars": {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "API_KEY": "secret",
        }
    }


def test_save_template_creates_key(vault_data):
    save_template(vault_data, "db", ["DB_HOST", "DB_PORT"])
    assert TEMPLATES_KEY in vault_data
    assert "db" in vault_data[TEMPLATES_KEY]


def test_save_template_stores_keys(vault_data):
    save_template(vault_data, "db", ["DB_HOST", "DB_PORT"])
    assert vault_data[TEMPLATES_KEY]["db"] == ["DB_HOST", "DB_PORT"]


def test_save_template_overwrites_existing(vault_data):
    save_template(vault_data, "db", ["DB_HOST"])
    save_template(vault_data, "db", ["DB_HOST", "DB_PORT"])
    assert vault_data[TEMPLATES_KEY]["db"] == ["DB_HOST", "DB_PORT"]


def test_get_template_returns_keys(vault_data):
    save_template(vault_data, "db", ["DB_HOST", "DB_PORT"])
    assert get_template(vault_data, "db") == ["DB_HOST", "DB_PORT"]


def test_get_template_missing_returns_none(vault_data):
    assert get_template(vault_data, "nonexistent") is None


def test_delete_template_returns_true(vault_data):
    save_template(vault_data, "db", ["DB_HOST"])
    assert delete_template(vault_data, "db") is True
    assert "db" not in vault_data.get(TEMPLATES_KEY, {})


def test_delete_template_missing_returns_false(vault_data):
    assert delete_template(vault_data, "ghost") is False


def test_list_templates_empty(vault_data):
    assert list_templates(vault_data) == {}


def test_list_templates_multiple(vault_data):
    save_template(vault_data, "db", ["DB_HOST", "DB_PORT"])
    save_template(vault_data, "api", ["API_KEY"])
    result = list_templates(vault_data)
    assert set(result.keys()) == {"db", "api"}


def test_apply_template_returns_matching_vars(vault_data):
    save_template(vault_data, "db", ["DB_HOST", "DB_PORT"])
    result = apply_template(vault_data, "db")
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_apply_template_skips_missing_vars(vault_data):
    save_template(vault_data, "mixed", ["DB_HOST", "MISSING_VAR"])
    result = apply_template(vault_data, "mixed")
    assert result == {"DB_HOST": "localhost"}


def test_apply_template_not_found_returns_none(vault_data):
    assert apply_template(vault_data, "nope") is None
