"""Tests for envault/schema.py."""

import pytest
from envault import schema as sch


@pytest.fixture
def vault_data():
    return {"vars": {"PORT": "8080", "DEBUG": "true", "NAME": "app"}}


def test_define_schema_creates_key(vault_data):
    sch.define_schema(vault_data, "PORT", "integer")
    assert "_schema" in vault_data
    assert "PORT" in vault_data["_schema"]


def test_define_schema_stores_type(vault_data):
    sch.define_schema(vault_data, "PORT", "integer", required=True)
    assert vault_data["_schema"]["PORT"]["type"] == "integer"
    assert vault_data["_schema"]["PORT"]["required"] is True


def test_define_schema_invalid_type_raises(vault_data):
    with pytest.raises(ValueError, match="Invalid type"):
        sch.define_schema(vault_data, "PORT", "number")


def test_remove_schema_returns_true(vault_data):
    sch.define_schema(vault_data, "PORT", "integer")
    result = sch.remove_schema(vault_data, "PORT")
    assert result is True
    assert "PORT" not in vault_data["_schema"]


def test_remove_schema_missing_returns_false(vault_data):
    result = sch.remove_schema(vault_data, "MISSING")
    assert result is False


def test_get_schema_returns_rule(vault_data):
    sch.define_schema(vault_data, "PORT", "integer")
    rule = sch.get_schema(vault_data, "PORT")
    assert rule["type"] == "integer"


def test_get_schema_missing_returns_none(vault_data):
    assert sch.get_schema(vault_data, "NOPE") is None


def test_list_schema_returns_all(vault_data):
    sch.define_schema(vault_data, "PORT", "integer")
    sch.define_schema(vault_data, "DEBUG", "boolean")
    rules = sch.list_schema(vault_data)
    assert set(rules.keys()) == {"PORT", "DEBUG"}


def test_validate_vault_passes(vault_data):
    sch.define_schema(vault_data, "PORT", "integer")
    sch.define_schema(vault_data, "DEBUG", "boolean")
    errors = sch.validate_vault(vault_data)
    assert errors == []


def test_validate_vault_wrong_type(vault_data):
    vault_data["vars"]["PORT"] = "not_a_number"
    sch.define_schema(vault_data, "PORT", "integer")
    errors = sch.validate_vault(vault_data)
    assert any("PORT" in e for e in errors)


def test_validate_vault_required_missing(vault_data):
    sch.define_schema(vault_data, "SECRET", "string", required=True)
    errors = sch.validate_vault(vault_data)
    assert any("SECRET" in e and "required" in e for e in errors)


def test_validate_vault_no_schema(vault_data):
    errors = sch.validate_vault(vault_data)
    assert errors == []
