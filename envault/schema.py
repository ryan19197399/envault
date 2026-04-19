"""Schema validation for vault variables."""

from typing import Any

VALID_TYPES = {"string", "integer", "boolean", "float"}


def define_schema(vault_data: dict, key: str, type_: str, required: bool = False) -> None:
    """Define a schema rule for a key."""
    if type_ not in VALID_TYPES:
        raise ValueError(f"Invalid type '{type_}'. Must be one of: {', '.join(VALID_TYPES)}")
    vault_data.setdefault("_schema", {})
    vault_data["_schema"][key] = {"type": type_, "required": required}


def remove_schema(vault_data: dict, key: str) -> bool:
    """Remove schema rule for a key. Returns True if removed."""
    schema = vault_data.get("_schema", {})
    if key in schema:
        del schema[key]
        return True
    return False


def get_schema(vault_data: dict, key: str) -> dict | None:
    """Get schema rule for a key."""
    return vault_data.get("_schema", {}).get(key)


def list_schema(vault_data: dict) -> dict:
    """Return all schema rules."""
    return dict(vault_data.get("_schema", {}))


def _coerce(value: str, type_: str) -> Any:
    try:
        if type_ == "integer":
            return int(value)
        if type_ == "float":
            return float(value)
        if type_ == "boolean":
            if value.lower() in ("true", "1", "yes"):
                return True
            if value.lower() in ("false", "0", "no"):
                return False
            raise ValueError
        return value
    except (ValueError, AttributeError):
        raise TypeError(f"Cannot coerce '{value}' to {type_}")


def validate_vault(vault_data: dict) -> list[str]:
    """Validate all vars against schema. Returns list of error messages."""
    errors = []
    schema = vault_data.get("_schema", {})
    vars_ = vault_data.get("vars", {})
    for key, rule in schema.items():
        if rule.get("required") and key not in vars_:
            errors.append(f"{key}: required but missing")
            continue
        if key in vars_:
            try:
                _coerce(vars_[key], rule["type"])
            except TypeError as e:
                errors.append(f"{key}: {e}")
    return errors
