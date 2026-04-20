"""Tests for envault/cascade.py"""
import pytest
from envault.cascade import (
    set_cascade, remove_cascade, get_cascade, list_cascades, apply_cascades
)


@pytest.fixture
def vault_data():
    return {
        "vars": {
            "DB_HOST": "localhost",
            "DB_HOST_UPPER": "",
            "APP_URL": "http://example.com",
            "APP_URL_CLEAN": "",
        }
    }


def test_set_cascade_creates_key(vault_data):
    set_cascade(vault_data, "DB_HOST", "DB_HOST_UPPER", transform="upper")
    assert "cascade" in vault_data
    assert "DB_HOST" in vault_data["cascade"]


def test_set_cascade_stores_target_and_transform(vault_data):
    set_cascade(vault_data, "DB_HOST", "DB_HOST_UPPER", transform="upper")
    rule = vault_data["cascade"]["DB_HOST"]
    assert rule["target"] == "DB_HOST_UPPER"
    assert rule["transform"] == "upper"


def test_set_cascade_no_transform(vault_data):
    set_cascade(vault_data, "DB_HOST", "DB_HOST_UPPER")
    assert vault_data["cascade"]["DB_HOST"]["transform"] is None


def test_set_cascade_missing_source_raises(vault_data):
    with pytest.raises(KeyError, match="MISSING"):
        set_cascade(vault_data, "MISSING", "DB_HOST_UPPER")


def test_set_cascade_missing_target_raises(vault_data):
    with pytest.raises(KeyError, match="MISSING"):
        set_cascade(vault_data, "DB_HOST", "MISSING")


def test_set_cascade_invalid_transform_raises(vault_data):
    with pytest.raises(ValueError, match="Unknown transform"):
        set_cascade(vault_data, "DB_HOST", "DB_HOST_UPPER", transform="base64")


def test_remove_cascade_returns_true(vault_data):
    set_cascade(vault_data, "DB_HOST", "DB_HOST_UPPER")
    result = remove_cascade(vault_data, "DB_HOST")
    assert result is True
    assert "DB_HOST" not in vault_data.get("cascade", {})


def test_remove_cascade_missing_returns_false(vault_data):
    result = remove_cascade(vault_data, "DB_HOST")
    assert result is False


def test_get_cascade_returns_rule(vault_data):
    set_cascade(vault_data, "DB_HOST", "DB_HOST_UPPER", transform="upper")
    rule = get_cascade(vault_data, "DB_HOST")
    assert rule is not None
    assert rule["target"] == "DB_HOST_UPPER"


def test_get_cascade_missing_returns_none(vault_data):
    assert get_cascade(vault_data, "DB_HOST") is None


def test_list_cascades_returns_all(vault_data):
    set_cascade(vault_data, "DB_HOST", "DB_HOST_UPPER", transform="upper")
    set_cascade(vault_data, "APP_URL", "APP_URL_CLEAN", transform="strip")
    rules = list_cascades(vault_data)
    assert len(rules) == 2
    sources = {r["source"] for r in rules}
    assert sources == {"DB_HOST", "APP_URL"}


def test_list_cascades_empty(vault_data):
    assert list_cascades(vault_data) == []


def test_apply_cascades_upper_transform(vault_data):
    vault_data["vars"]["DB_HOST"] = "localhost"
    set_cascade(vault_data, "DB_HOST", "DB_HOST_UPPER", transform="upper")
    updated = apply_cascades(vault_data, "DB_HOST")
    assert updated == ["DB_HOST_UPPER"]
    assert vault_data["vars"]["DB_HOST_UPPER"] == "LOCALHOST"


def test_apply_cascades_no_transform_copies_value(vault_data):
    vault_data["vars"]["DB_HOST"] = "myhost"
    set_cascade(vault_data, "DB_HOST", "DB_HOST_UPPER")
    apply_cascades(vault_data, "DB_HOST")
    assert vault_data["vars"]["DB_HOST_UPPER"] == "myhost"


def test_apply_cascades_no_rule_returns_empty(vault_data):
    result = apply_cascades(vault_data, "DB_HOST")
    assert result == []
