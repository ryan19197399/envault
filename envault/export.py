"""Utilities for exporting vault variables to shell and .env formats."""
from typing import Dict


def to_shell_exports(variables: Dict[str, str]) -> str:
    """Return a shell-compatible export string for all variables."""
    lines = []
    for key, value in sorted(variables.items()):
        escaped = value.replace("\\", "\\\\").replace("'", "'\\''")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines)


def to_dotenv(variables: Dict[str, str]) -> str:
    """Return a .env file formatted string for all variables."""
    lines = []
    for key, value in sorted(variables.items()):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines)


def from_dotenv(content: str) -> Dict[str, str]:
    """Parse a .env file content into a dictionary."""
    variables = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        variables[key] = value
    return variables
