"""Tests for envault.resolve — variable interpolation."""

import pytest
from envault.resolve import (
    resolve_value,
    resolve_all,
    has_references,
    list_references,
)


@pytest.fixture
def vars_():
    return {
        "HOST": "localhost",
        "PORT": "5432",
        "DB_URL": "postgres://${HOST}:${PORT}/mydb",
        "GREETING": "hello ${NAME}",
        "PLAIN": "no_refs_here",
    }


def test_resolve_value_simple(vars_):
    result = resolve_value("${HOST}:${PORT}", vars_)
    assert result == "localhost:5432"


def test_resolve_value_nested(vars_):
    result = resolve_value("${DB_URL}", vars_)
    assert result == "postgres://localhost:5432/mydb"


def test_resolve_value_no_refs(vars_):
    assert resolve_value("static_value", vars_) == "static_value"


def test_resolve_value_unresolved_key(vars_):
    with pytest.raises(KeyError, match="NAME"):
        resolve_value("${GREETING}", vars_)


def test_resolve_value_circular_raises():
    circular = {"A": "${B}", "B": "${A}"}
    with pytest.raises(ValueError, match="[Cc]ircular"):
        resolve_value("${A}", circular)


def test_resolve_value_max_depth_exceeded():
    deep = {f"K{i}": f"${{K{i+1}}}" for i in range(15)}
    deep["K15"] = "end"
    with pytest.raises(ValueError, match="depth"):
        resolve_value("${K0}", deep)


def test_resolve_all_basic(vars_):
    extended = {**vars_, "NAME": "world"}
    result = resolve_all(extended)
    assert result["DB_URL"] == "postgres://localhost:5432/mydb"
    assert result["GREETING"] == "hello world"
    assert result["PLAIN"] == "no_refs_here"


def test_resolve_all_skip_errors(vars_):
    # GREETING references NAME which is missing
    result = resolve_all(vars_, skip_errors=True)
    assert result["GREETING"] == "hello ${NAME}"  # left as-is
    assert result["HOST"] == "localhost"


def test_resolve_all_raises_without_skip(vars_):
    with pytest.raises(KeyError):
        resolve_all(vars_, skip_errors=False)


def test_has_references_true():
    assert has_references("prefix_${KEY}_suffix") is True


def test_has_references_false():
    assert has_references("no_placeholders") is False


def test_list_references_multiple():
    refs = list_references("${A} and ${B} and ${A}")
    assert refs == ["A", "B", "A"]


def test_list_references_empty():
    assert list_references("plain value") == []
