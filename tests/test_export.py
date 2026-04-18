import pytest
from envault.export import to_shell_exports, to_dotenv, from_dotenv


def test_to_shell_exports_basic():
    result = to_shell_exports({"FOO": "bar", "BAZ": "qux"})
    assert "export BAZ='qux'" in result
    assert "export FOO='bar'" in result


def test_to_shell_exports_escapes_single_quotes():
    result = to_shell_exports({"KEY": "it's alive"})
    assert "KEY" in result
    assert "'\\''" in result


def test_to_dotenv_basic():
    result = to_dotenv({"FOO": "bar"})
    assert 'FOO="bar"' in result


def test_to_dotenv_escapes_double_quotes():
    result = to_dotenv({"KEY": 'say "hello"'})
    assert '\\"' in result


def test_from_dotenv_basic():
    content = 'FOO="bar"\nBAZ="qux"'
    result = from_dotenv(content)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_from_dotenv_ignores_comments():
    content = "# comment\nFOO=bar"
    result = from_dotenv(content)
    assert "FOO" in result
    assert len(result) == 1


def test_from_dotenv_ignores_blank_lines():
    content = "\nFOO=bar\n\nBAZ=qux\n"
    result = from_dotenv(content)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_from_dotenv_single_quotes():
    content = "FOO='hello world'"
    result = from_dotenv(content)
    assert result["FOO"] == "hello world"


def test_from_dotenv_unquoted_value():
    content = "FOO=simplevalue"
    result = from_dotenv(content)
    assert result["FOO"] == "simplevalue"


def test_from_dotenv_empty_value():
    content = 'FOO=""'
    result = from_dotenv(content)
    assert result["FOO"] == ""


def test_roundtrip_dotenv():
    original = {"API_KEY": "secret123", "DEBUG": "true"}
    content = to_dotenv(original)
    parsed = from_dotenv(content)
    assert parsed == original


def test_roundtrip_shell_exports_special_chars():
    original = {"MSG": "it's a test"}
    result = to_shell_exports(original)
    assert "MSG" in result
