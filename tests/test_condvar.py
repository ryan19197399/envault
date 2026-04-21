import pytest
from envault.condvar import (
    set_condvar,
    remove_condvar,
    get_condvar,
    list_condvars,
    apply_condvars,
)


@pytest.fixture
def vault_data():
    return {
        "vars": {
            "ENV": "production",
            "LOG_LEVEL": "info",
            "DEBUG": "false",
        }
    }


def test_set_condvar_creates_key(vault_data):
    set_condvar(vault_data, "LOG_LEVEL", "ENV", {"production": "warn", "development": "debug"})
    assert "__condvars__" in vault_data
    assert "LOG_LEVEL" in vault_data["__condvars__"]


def test_set_condvar_stores_rule(vault_data):
    set_condvar(vault_data, "LOG_LEVEL", "ENV", {"production": "warn"}, default="info")
    rule = vault_data["__condvars__"]["LOG_LEVEL"]
    assert rule["source"] == "ENV"
    assert rule["conditions"] == {"production": "warn"}
    assert rule["default"] == "info"


def test_set_condvar_missing_key_raises(vault_data):
    with pytest.raises(KeyError, match="MISSING"):
        set_condvar(vault_data, "MISSING", "ENV", {"production": "warn"})


def test_set_condvar_missing_source_raises(vault_data):
    with pytest.raises(KeyError, match="NO_SOURCE"):
        set_condvar(vault_data, "LOG_LEVEL", "NO_SOURCE", {"production": "warn"})


def test_set_condvar_empty_conditions_raises(vault_data):
    with pytest.raises(ValueError, match="conditions"):
        set_condvar(vault_data, "LOG_LEVEL", "ENV", {})


def test_remove_condvar_returns_true(vault_data):
    set_condvar(vault_data, "LOG_LEVEL", "ENV", {"production": "warn"})
    assert remove_condvar(vault_data, "LOG_LEVEL") is True
    assert "LOG_LEVEL" not in vault_data["__condvars__"]


def test_remove_condvar_missing_returns_false(vault_data):
    assert remove_condvar(vault_data, "NONEXISTENT") is False


def test_get_condvar_returns_rule(vault_data):
    set_condvar(vault_data, "LOG_LEVEL", "ENV", {"production": "warn"})
    rule = get_condvar(vault_data, "LOG_LEVEL")
    assert rule is not None
    assert rule["source"] == "ENV"


def test_get_condvar_missing_returns_none(vault_data):
    assert get_condvar(vault_data, "NONEXISTENT") is None


def test_list_condvars_returns_all(vault_data):
    set_condvar(vault_data, "LOG_LEVEL", "ENV", {"production": "warn"})
    set_condvar(vault_data, "DEBUG", "ENV", {"development": "true"})
    result = list_condvars(vault_data)
    assert "LOG_LEVEL" in result
    assert "DEBUG" in result


def test_apply_condvars_updates_matching(vault_data):
    set_condvar(vault_data, "LOG_LEVEL", "ENV", {"production": "warn", "development": "debug"})
    apply_condvars(vault_data)
    assert vault_data["vars"]["LOG_LEVEL"] == "warn"


def test_apply_condvars_uses_default_when_no_match(vault_data):
    vault_data["vars"]["ENV"] = "staging"
    set_condvar(vault_data, "LOG_LEVEL", "ENV", {"production": "warn"}, default="verbose")
    apply_condvars(vault_data)
    assert vault_data["vars"]["LOG_LEVEL"] == "verbose"


def test_apply_condvars_no_default_leaves_value(vault_data):
    vault_data["vars"]["ENV"] = "staging"
    set_condvar(vault_data, "LOG_LEVEL", "ENV", {"production": "warn"})
    apply_condvars(vault_data)
    assert vault_data["vars"]["LOG_LEVEL"] == "info"  # unchanged
