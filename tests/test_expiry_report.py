"""Tests for envault/expiry_report.py."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from envault.expiry_report import (
    build_report,
    get_already_expired,
    get_due_reminders,
    get_expiring_soon,
)

_NOW = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


@pytest.fixture()
def vault_data():
    future_soon = _iso(_NOW + timedelta(hours=6))
    future_far = _iso(_NOW + timedelta(days=5))
    past = _iso(_NOW - timedelta(hours=1))
    return {
        "vars": {"API_KEY": "secret", "DB_PASS": "pass", "TOKEN": "tok", "OLD": "val"},
        "_ttl": {
            "API_KEY": future_soon,
            "DB_PASS": future_far,
            "TOKEN": past,
        },
        "_reminders": {
            "OLD": {"due": _iso(_NOW - timedelta(minutes=30)), "message": "rotate this"},
            "API_KEY": {"due": _iso(_NOW + timedelta(days=2)), "message": "check expiry"},
        },
    }


def test_get_expiring_soon_returns_within_window(vault_data):
    with patch("envault.expiry_report._now", return_value=_NOW):
        results = get_expiring_soon(vault_data, within_seconds=86400)
    keys = [r["key"] for r in results]
    assert "API_KEY" in keys
    assert "DB_PASS" not in keys
    assert "TOKEN" not in keys  # already expired


def test_get_expiring_soon_sorted_by_seconds_left(vault_data):
    extra_ttl = _iso(_NOW + timedelta(hours=2))
    vault_data["_ttl"]["EXTRA"] = extra_ttl
    with patch("envault.expiry_report._now", return_value=_NOW):
        results = get_expiring_soon(vault_data, within_seconds=86400)
    lefts = [r["seconds_left"] for r in results]
    assert lefts == sorted(lefts)


def test_get_expiring_soon_empty_when_no_ttl():
    with patch("envault.expiry_report._now", return_value=_NOW):
        results = get_expiring_soon({}, within_seconds=86400)
    assert results == []


def test_get_already_expired_returns_past_entries(vault_data):
    with patch("envault.expiry_report._now", return_value=_NOW):
        results = get_already_expired(vault_data)
    keys = [r["key"] for r in results]
    assert "TOKEN" in keys
    assert "API_KEY" not in keys
    assert "DB_PASS" not in keys


def test_get_already_expired_empty_when_none_expired(vault_data):
    vault_data["_ttl"] = {"A": _iso(_NOW + timedelta(days=1))}
    with patch("envault.expiry_report._now", return_value=_NOW):
        results = get_already_expired(vault_data)
    assert results == []


def test_get_due_reminders_returns_past_due(vault_data):
    with patch("envault.expiry_report._now", return_value=_NOW):
        results = get_due_reminders(vault_data)
    keys = [r["key"] for r in results]
    assert "OLD" in keys
    assert "API_KEY" not in keys


def test_get_due_reminders_includes_message(vault_data):
    with patch("envault.expiry_report._now", return_value=_NOW):
        results = get_due_reminders(vault_data)
    old_entry = next(r for r in results if r["key"] == "OLD")
    assert old_entry["message"] == "rotate this"


def test_build_report_structure(vault_data):
    with patch("envault.expiry_report._now", return_value=_NOW):
        report = build_report(vault_data, warn_within_seconds=86400)
    assert "expiring_soon" in report
    assert "already_expired" in report
    assert "due_reminders" in report
    assert isinstance(report["expiring_soon"], list)
    assert isinstance(report["already_expired"], list)
    assert isinstance(report["due_reminders"], list)
