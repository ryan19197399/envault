"""Tests for envault.lifecycle."""

from __future__ import annotations

import pytest

from envault.lifecycle import (
    VALID_EVENTS,
    fire_hook,
    get_hook,
    list_hooks,
    remove_hook,
    set_hook,
)


@pytest.fixture()
def vault_data() -> dict:
    return {"vars": {"API_KEY": "secret", "DB_URL": "postgres://localhost/db"}, "lifecycle": {}}


def test_set_hook_creates_lifecycle_key(vault_data: dict) -> None:
    vault_data.pop("lifecycle")
    set_hook(vault_data, "API_KEY", "pre_set", "echo before")
    assert "lifecycle" in vault_data


def test_set_hook_stores_command(vault_data: dict) -> None:
    set_hook(vault_data, "API_KEY", "post_set", "notify.sh")
    assert vault_data["lifecycle"]["API_KEY"]["post_set"] == "notify.sh"


def test_set_hook_overwrites_existing(vault_data: dict) -> None:
    set_hook(vault_data, "API_KEY", "pre_get", "old_cmd")
    set_hook(vault_data, "API_KEY", "pre_get", "new_cmd")
    assert vault_data["lifecycle"]["API_KEY"]["pre_get"] == "new_cmd"


def test_set_hook_missing_key_raises(vault_data: dict) -> None:
    with pytest.raises(KeyError, match="MISSING"):
        set_hook(vault_data, "MISSING", "pre_set", "echo hi")


def test_set_hook_invalid_event_raises(vault_data: dict) -> None:
    with pytest.raises(ValueError, match="Invalid event"):
        set_hook(vault_data, "API_KEY", "on_explode", "echo boom")


def test_remove_hook_returns_true(vault_data: dict) -> None:
    set_hook(vault_data, "API_KEY", "pre_set", "echo hi")
    assert remove_hook(vault_data, "API_KEY", "pre_set") is True


def test_remove_hook_returns_false_when_absent(vault_data: dict) -> None:
    assert remove_hook(vault_data, "API_KEY", "pre_set") is False


def test_remove_hook_cleans_up_empty_key(vault_data: dict) -> None:
    set_hook(vault_data, "API_KEY", "pre_set", "echo hi")
    remove_hook(vault_data, "API_KEY", "pre_set")
    assert "API_KEY" not in vault_data["lifecycle"]


def test_get_hook_returns_command(vault_data: dict) -> None:
    set_hook(vault_data, "DB_URL", "post_delete", "cleanup.sh")
    assert get_hook(vault_data, "DB_URL", "post_delete") == "cleanup.sh"


def test_get_hook_returns_none_when_absent(vault_data: dict) -> None:
    assert get_hook(vault_data, "API_KEY", "pre_get") is None


def test_list_hooks_returns_all(vault_data: dict) -> None:
    set_hook(vault_data, "API_KEY", "pre_set", "cmd1")
    set_hook(vault_data, "API_KEY", "post_set", "cmd2")
    hooks = list_hooks(vault_data, "API_KEY")
    assert hooks == {"pre_set": "cmd1", "post_set": "cmd2"}


def test_list_hooks_empty_when_none(vault_data: dict) -> None:
    assert list_hooks(vault_data, "API_KEY") == {}


def test_fire_hook_runs_command(vault_data: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_run(cmd: str, **_kwargs: object) -> None:
        calls.append(cmd)

    import subprocess
    monkeypatch.setattr(subprocess, "run", fake_run)
    set_hook(vault_data, "API_KEY", "pre_get", "echo triggered")
    result = fire_hook(vault_data, "API_KEY", "pre_get")
    assert result == "echo triggered"
    assert calls == ["echo triggered"]


def test_fire_hook_returns_none_when_absent(vault_data: dict) -> None:
    assert fire_hook(vault_data, "API_KEY", "pre_get") is None


def test_valid_events_contains_expected() -> None:
    assert "pre_set" in VALID_EVENTS
    assert "post_set" in VALID_EVENTS
    assert "pre_get" in VALID_EVENTS
    assert "post_get" in VALID_EVENTS
    assert "pre_delete" in VALID_EVENTS
    assert "post_delete" in VALID_EVENTS
