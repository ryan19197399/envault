"""Tests for envault.audit module."""

import pytest
from envault.audit import log_event, read_log, clear_log


@pytest.fixture
def tmp_audit_dir(tmp_path):
    return str(tmp_path)


def test_log_event_creates_file(tmp_audit_dir):
    log_event("myproject", "init", base_dir=tmp_audit_dir)
    events = read_log("myproject", base_dir=tmp_audit_dir)
    assert len(events) == 1
    assert events[0]["action"] == "init"
    assert events[0]["vault"] == "myproject"


def test_log_event_with_key(tmp_audit_dir):
    log_event("myproject", "set", key="API_KEY", base_dir=tmp_audit_dir)
    events = read_log("myproject", base_dir=tmp_audit_dir)
    assert events[0]["key"] == "API_KEY"


def test_log_event_without_key(tmp_audit_dir):
    log_event("myproject", "list", base_dir=tmp_audit_dir)
    events = read_log("myproject", base_dir=tmp_audit_dir)
    assert "key" not in events[0]


def test_multiple_events_appended(tmp_audit_dir):
    log_event("proj", "set", key="FOO", base_dir=tmp_audit_dir)
    log_event("proj", "get", key="FOO", base_dir=tmp_audit_dir)
    log_event("proj", "delete", key="FOO", base_dir=tmp_audit_dir)
    events = read_log("proj", base_dir=tmp_audit_dir)
    assert len(events) == 3
    assert [e["action"] for e in events] == ["set", "get", "delete"]


def test_read_log_empty_if_no_file(tmp_audit_dir):
    events = read_log("nonexistent", base_dir=tmp_audit_dir)
    assert events == []


def test_clear_log(tmp_audit_dir):
    log_event("proj", "init", base_dir=tmp_audit_dir)
    clear_log("proj", base_dir=tmp_audit_dir)
    events = read_log("proj", base_dir=tmp_audit_dir)
    assert events == []


def test_clear_log_no_file_is_safe(tmp_audit_dir):
    clear_log("nope", base_dir=tmp_audit_dir)  # should not raise


def test_timestamp_format(tmp_audit_dir):
    log_event("proj", "init", base_dir=tmp_audit_dir)
    events = read_log("proj", base_dir=tmp_audit_dir)
    ts = events[0]["timestamp"]
    assert ts.endswith("Z")
    assert "T" in ts
