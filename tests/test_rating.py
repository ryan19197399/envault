"""Tests for envault.rating."""

from __future__ import annotations

import pytest

from envault.rating import rate_key, rate_all, rating_summary


@pytest.fixture()
def vault_data() -> dict:
    return {
        "vars": {
            "API_KEY": "secret123",
            "DB_HOST": "localhost",
            "bad_name": "value",
            "EMPTY_VAR": "",
        },
        "notes": {"API_KEY": "Primary API credential"},
        "tags": {"API_KEY": ["production"], "DB_HOST": ["infra"]},
        "schema": {"API_KEY": {"type": "str"}},
        "ttl": {},
        "immutable": [],
    }


def test_rate_key_perfect_score(vault_data):
    # API_KEY has note, tag, schema, good name, non-empty, no TTL (not expired)
    result = rate_key(vault_data, "API_KEY")
    assert result["key"] == "API_KEY"
    assert result["score"] == 100
    assert result["max"] == 100


def test_rate_key_missing_key_raises(vault_data):
    with pytest.raises(KeyError, match="MISSING"):
        rate_key(vault_data, "MISSING")


def test_rate_key_bad_name_loses_points(vault_data):
    result = rate_key(vault_data, "bad_name")
    assert not result["breakdown"]["naming"]["passed"]
    assert result["score"] <= 75


def test_rate_key_empty_value_loses_points(vault_data):
    result = rate_key(vault_data, "EMPTY_VAR")
    assert not result["breakdown"]["non_empty"]["passed"]


def test_rate_key_no_note_loses_points(vault_data):
    result = rate_key(vault_data, "DB_HOST")
    assert not result["breakdown"]["has_note"]["passed"]
    assert result["breakdown"]["has_note"]["weight"] == 15


def test_rate_key_no_schema_loses_points(vault_data):
    result = rate_key(vault_data, "DB_HOST")
    assert not result["breakdown"]["has_schema"]["passed"]


def test_rate_key_immutable_flag(vault_data):
    vault_data["immutable"] = ["API_KEY"]
    result = rate_key(vault_data, "API_KEY")
    assert result["immutable"] is True


def test_rate_all_returns_all_keys(vault_data):
    results = rate_all(vault_data)
    assert len(results) == len(vault_data["vars"])


def test_rate_all_sorted_descending(vault_data):
    results = rate_all(vault_data)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_rating_summary_basic(vault_data):
    stats = rating_summary(vault_data)
    assert stats["count"] == 4
    assert 0 <= stats["average"] <= 100
    assert stats["min"] <= stats["max"]


def test_rating_summary_empty_vault():
    stats = rating_summary({"vars": {}})
    assert stats == {"count": 0, "average": 0, "min": 0, "max": 0}
