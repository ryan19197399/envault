"""Tests for envault.redact module."""

import re
import pytest
from envault.redact import (
    is_sensitive,
    redact_value,
    redact_dict,
    redact_vault_vars,
    REDACT_PLACEHOLDER,
)


# ---------------------------------------------------------------------------
# is_sensitive
# ---------------------------------------------------------------------------

def test_is_sensitive_password():
    assert is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_token():
    assert is_sensitive("GITHUB_TOKEN") is True


def test_is_sensitive_api_key():
    assert is_sensitive("STRIPE_API_KEY") is True


def test_is_sensitive_safe_key():
    assert is_sensitive("APP_PORT") is False


def test_is_sensitive_custom_pattern():
    pattern = [re.compile(r"custom", re.IGNORECASE)]
    assert is_sensitive("MY_CUSTOM_VAR", patterns=pattern) is True
    assert is_sensitive("APP_PORT", patterns=pattern) is False


# ---------------------------------------------------------------------------
# redact_value
# ---------------------------------------------------------------------------

def test_redact_value_sensitive_returns_placeholder():
    result = redact_value("DB_SECRET", "super-secret-123")
    assert result == REDACT_PLACEHOLDER


def test_redact_value_safe_returns_original():
    result = redact_value("APP_HOST", "localhost")
    assert result == "localhost"


# ---------------------------------------------------------------------------
# redact_dict
# ---------------------------------------------------------------------------

def test_redact_dict_masks_sensitive_keys():
    data = {"DB_PASSWORD": "s3cr3t", "APP_PORT": "5432", "API_TOKEN": "abc"}
    result = redact_dict(data)
    assert result["DB_PASSWORD"] == REDACT_PLACEHOLDER
    assert result["API_TOKEN"] == REDACT_PLACEHOLDER
    assert result["APP_PORT"] == "5432"


def test_redact_dict_keys_only_overrides_patterns():
    data = {"DB_PASSWORD": "s3cr3t", "APP_PORT": "5432"}
    result = redact_dict(data, keys_only=["APP_PORT"])
    # APP_PORT is in keys_only → redacted; DB_PASSWORD is NOT in keys_only → kept
    assert result["APP_PORT"] == REDACT_PLACEHOLDER
    assert result["DB_PASSWORD"] == "s3cr3t"


def test_redact_dict_empty():
    assert redact_dict({}) == {}


# ---------------------------------------------------------------------------
# redact_vault_vars
# ---------------------------------------------------------------------------

def test_redact_vault_vars_uses_vars_section():
    vault = {"vars": {"SECRET_KEY": "abc", "HOST": "localhost"}}
    result = redact_vault_vars(vault)
    assert result["SECRET_KEY"] == REDACT_PLACEHOLDER
    assert result["HOST"] == "localhost"


def test_redact_vault_vars_missing_vars_returns_empty():
    result = redact_vault_vars({})
    assert result == {}
