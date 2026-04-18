"""Tests for audit CLI commands."""

import pytest
from click.testing import CliRunner
from envault.cli_audit import audit
from envault.audit import log_event


@pytest.fixture
def runner():
    return CliRunner()


def test_show_log_no_entries(runner, tmp_path, monkeypatch):
    monkeypatch.setattr("envault.audit.Path.home", lambda: tmp_path)
    result = runner.invoke(audit, ["log", "myproject"])
    assert result.exit_code == 0
    assert "No audit log" in result.output


def test_show_log_with_entries(runner, tmp_path, monkeypatch):
    monkeypatch.setattr("envault.audit._audit_path",
                        lambda name, base_dir=None: tmp_path / f"{name}.audit.jsonl")
    log_event("myproject", "set", key="DB_URL", base_dir=str(tmp_path))
    log_event("myproject", "get", key="DB_URL", base_dir=str(tmp_path))

    from envault import audit as audit_mod
    original = audit_mod._audit_path
    audit_mod._audit_path = lambda name, base_dir=None: tmp_path / f"{name}.audit.jsonl"

    result = runner.invoke(audit, ["log", "myproject"])
    audit_mod._audit_path = original

    assert result.exit_code == 0
    assert "set" in result.output
    assert "get" in result.output
    assert "DB_URL" in result.output


def test_clear_log_confirmed(runner, tmp_path, monkeypatch):
    from envault import audit as audit_mod
    original = audit_mod._audit_path
    audit_mod._audit_path = lambda name, base_dir=None: tmp_path / f"{name}.audit.jsonl"

    log_event("proj", "init", base_dir=str(tmp_path))
    result = runner.invoke(audit, ["clear", "proj"], input="y\n")
    audit_mod._audit_path = original

    assert result.exit_code == 0
    assert "cleared" in result.output


def test_clear_log_aborted(runner):
    result = runner.invoke(audit, ["clear", "proj"], input="n\n")
    assert result.exit_code != 0 or "Aborted" in result.output
