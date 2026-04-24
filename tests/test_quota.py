"""Tests for envault/quota.py"""

import pytest
from envault.quota import (
    set_quota,
    get_quota,
    remove_quota,
    check_quota,
    quota_report,
    DEFAULT_MAX_KEYS,
    DEFAULT_MAX_VALUE_BYTES,
)


@pytest.fixture
def vault_data():
    return {"vars": {"FOO": "bar", "BAZ": "qux"}}


def test_set_quota_creates_key(vault_data):
    set_quota(vault_data, max_keys=100)
    assert "__quota__" in vault_data


def test_set_quota_stores_max_keys(vault_data):
    set_quota(vault_data, max_keys=50)
    assert vault_data["__quota__"]["max_keys"] == 50


def test_set_quota_stores_max_value_bytes(vault_data):
    set_quota(vault_data, max_value_bytes=1024)
    assert vault_data["__quota__"]["max_value_bytes"] == 1024


def test_set_quota_invalid_max_keys_raises(vault_data):
    with pytest.raises(ValueError, match="max_keys"):
        set_quota(vault_data, max_keys=0)


def test_set_quota_invalid_max_value_bytes_raises(vault_data):
    with pytest.raises(ValueError, match="max_value_bytes"):
        set_quota(vault_data, max_value_bytes=-1)


def test_get_quota_defaults_when_not_set(vault_data):
    q = get_quota(vault_data)
    assert q["max_keys"] == DEFAULT_MAX_KEYS
    assert q["max_value_bytes"] == DEFAULT_MAX_VALUE_BYTES


def test_get_quota_returns_set_values(vault_data):
    set_quota(vault_data, max_keys=10, max_value_bytes=256)
    q = get_quota(vault_data)
    assert q["max_keys"] == 10
    assert q["max_value_bytes"] == 256


def test_remove_quota_returns_true_when_exists(vault_data):
    set_quota(vault_data, max_keys=10)
    assert remove_quota(vault_data) is True
    assert "__quota__" not in vault_data


def test_remove_quota_returns_false_when_absent(vault_data):
    assert remove_quota(vault_data) is False


def test_check_quota_passes_for_new_key(vault_data):
    set_quota(vault_data, max_keys=10)
    check_quota(vault_data, "NEW_KEY", "value")  # should not raise


def test_check_quota_raises_when_keys_full():
    data = {"vars": {"A": "1", "B": "2"}}
    set_quota(data, max_keys=2)
    with pytest.raises(ValueError, match="Quota exceeded"):
        check_quota(data, "C", "3")


def test_check_quota_allows_update_existing_key():
    data = {"vars": {"A": "1", "B": "2"}}
    set_quota(data, max_keys=2)
    check_quota(data, "A", "new_value")  # update, should not raise


def test_check_quota_raises_when_value_too_large(vault_data):
    set_quota(vault_data, max_value_bytes=5)
    with pytest.raises(ValueError, match="Quota exceeded"):
        check_quota(vault_data, "KEY", "this_is_too_long")


def test_quota_report_returns_counts(vault_data):
    set_quota(vault_data, max_keys=100, max_value_bytes=4096)
    report = quota_report(vault_data)
    assert report["key_count"] == 2
    assert report["max_keys"] == 100
    assert report["keys_remaining"] == 98
    assert report["largest_value_bytes"] == 3  # "qux" or "bar"


def test_quota_report_empty_vars():
    data = {"vars": {}}
    report = quota_report(data)
    assert report["key_count"] == 0
    assert report["largest_value_bytes"] == 0
