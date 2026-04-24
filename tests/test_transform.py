"""Tests for envault.transform."""

import pytest
from envault import transform as tf


@pytest.fixture
def vault_data():
    return {
        "vars": {
            "API_KEY": "  hello world  ",
            "SECRET": "mysecret",
            "ENCODED": "aGVsbG8=",
        },
        "transforms": {},
    }


def test_list_transforms_returns_builtins():
    names = tf.list_transforms()
    assert "upper" in names
    assert "lower" in names
    assert "strip" in names
    assert "base64_encode" in names


def test_apply_transform_upper(vault_data):
    assert tf.apply_transform("hello", "upper") == "HELLO"


def test_apply_transform_lower(vault_data):
    assert tf.apply_transform("HELLO", "lower") == "hello"


def test_apply_transform_strip(vault_data):
    assert tf.apply_transform("  hi  ", "strip") == "hi"


def test_apply_transform_reverse():
    assert tf.apply_transform("abc", "reverse") == "cba"


def test_apply_transform_base64_roundtrip():
    encoded = tf.apply_transform("hello", "base64_encode")
    decoded = tf.apply_transform(encoded, "base64_decode")
    assert decoded == "hello"


def test_apply_transform_unknown_raises():
    with pytest.raises(KeyError, match="Unknown transform"):
        tf.apply_transform("value", "nonexistent")


def test_apply_pipeline_multiple_steps():
    result = tf.apply_pipeline("  Hello  ", ["strip", "upper"])
    assert result == "HELLO"


def test_set_pipeline_stores_steps(vault_data):
    tf.set_pipeline(vault_data, "API_KEY", ["strip", "upper"])
    assert vault_data["transforms"]["API_KEY"] == ["strip", "upper"]


def test_set_pipeline_missing_key_raises(vault_data):
    with pytest.raises(KeyError, match="not found"):
        tf.set_pipeline(vault_data, "MISSING", ["upper"])


def test_set_pipeline_invalid_step_raises(vault_data):
    with pytest.raises(KeyError, match="Unknown transform"):
        tf.set_pipeline(vault_data, "API_KEY", ["upper", "bogus"])


def test_remove_pipeline_returns_true(vault_data):
    tf.set_pipeline(vault_data, "API_KEY", ["strip"])
    assert tf.remove_pipeline(vault_data, "API_KEY") is True
    assert "API_KEY" not in vault_data["transforms"]


def test_remove_pipeline_missing_returns_false(vault_data):
    assert tf.remove_pipeline(vault_data, "API_KEY") is False


def test_get_pipeline_returns_none_when_absent(vault_data):
    assert tf.get_pipeline(vault_data, "API_KEY") is None


def test_resolve_value_no_pipeline(vault_data):
    result = tf.resolve_value(vault_data, "SECRET")
    assert result == "mysecret"


def test_resolve_value_with_pipeline(vault_data):
    tf.set_pipeline(vault_data, "API_KEY", ["strip", "upper"])
    result = tf.resolve_value(vault_data, "API_KEY")
    assert result == "HELLO WORLD"


def test_resolve_value_missing_key_returns_none(vault_data):
    assert tf.resolve_value(vault_data, "NOPE") is None
