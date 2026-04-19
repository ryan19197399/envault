"""Tests for envault.env_inject."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

from envault.env_inject import build_env, run_with_vault


@pytest.fixture
def vault_data():
    return {
        "vars": {
            "API_KEY": "secret123",
            "DB_HOST": "localhost",
            "DEBUG": "true",
        }
    }


def test_build_env_adds_vars(vault_data):
    env = build_env(vault_data, base_env={})
    assert env["API_KEY"] == "secret123"
    assert env["DB_HOST"] == "localhost"


def test_build_env_merges_with_base(vault_data):
    base = {"EXISTING": "yes"}
    env = build_env(vault_data, base_env=base)
    assert env["EXISTING"] == "yes"
    assert env["API_KEY"] == "secret123"


def test_build_env_overwrite_true(vault_data):
    base = {"API_KEY": "old_value"}
    env = build_env(vault_data, base_env=base, overwrite=True)
    assert env["API_KEY"] == "secret123"


def test_build_env_overwrite_false(vault_data):
    base = {"API_KEY": "old_value"}
    env = build_env(vault_data, base_env=base, overwrite=False)
    assert env["API_KEY"] == "old_value"


def test_build_env_skips_expired(vault_data):
    past = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
    vault_data["ttl"] = {"API_KEY": past}
    env = build_env(vault_data, base_env={}, skip_expired=True)
    assert "API_KEY" not in env


def test_build_env_includes_expired_when_flag_false(vault_data):
    past = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
    vault_data["ttl"] = {"API_KEY": past}
    env = build_env(vault_data, base_env={}, skip_expired=False)
    assert env["API_KEY"] == "secret123"


def test_build_env_empty_vars():
    env = build_env({"vars": {}}, base_env={"FOO": "bar"})
    assert env == {"FOO": "bar"}


def test_run_with_vault_calls_subprocess(vault_data):
    with patch("envault.env_inject.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = run_with_vault(vault_data, ["echo", "hello"], overwrite=True)
        assert mock_run.called
        call_kwargs = mock_run.call_args
        env_passed = call_kwargs[1]["env"]
        assert env_passed["API_KEY"] == "secret123"
