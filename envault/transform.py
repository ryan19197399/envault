"""Value transformation pipeline for envault."""

from typing import Callable, Dict, List, Optional

_BUILTIN_TRANSFORMS: Dict[str, Callable[[str], str]] = {
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
    "reverse": lambda v: v[::-1],
    "base64_encode": lambda v: __import__("base64").b64encode(v.encode()).decode(),
    "base64_decode": lambda v: __import__("base64").b64decode(v.encode()).decode(),
    "url_encode": lambda v: __import__("urllib.parse", fromlist=["quote"]).quote(v, safe=""),
    "trim_quotes": lambda v: v.strip("'\"``"),
}


def list_transforms() -> List[str]:
    """Return names of all built-in transforms."""
    return sorted(_BUILTIN_TRANSFORMS.keys())


def apply_transform(value: str, transform_name: str) -> str:
    """Apply a named transform to a value.

    Raises KeyError if the transform is unknown.
    """
    if transform_name not in _BUILTIN_TRANSFORMS:
        raise KeyError(f"Unknown transform: '{transform_name}'")
    return _BUILTIN_TRANSFORMS[transform_name](value)


def apply_pipeline(value: str, pipeline: List[str]) -> str:
    """Apply a sequence of transforms to a value in order."""
    for step in pipeline:
        value = apply_transform(value, step)
    return value


def set_pipeline(vault_data: dict, key: str, pipeline: List[str]) -> None:
    """Attach a transform pipeline to a vault key.

    Raises KeyError if the key does not exist in vars.
    Raises KeyError if any step is an unknown transform.
    """
    if key not in vault_data.get("vars", {}):
        raise KeyError(f"Key '{key}' not found in vault")
    for step in pipeline:
        if step not in _BUILTIN_TRANSFORMS:
            raise KeyError(f"Unknown transform: '{step}'")
    vault_data.setdefault("transforms", {})[key] = list(pipeline)


def remove_pipeline(vault_data: dict, key: str) -> bool:
    """Remove the transform pipeline for a key. Returns True if removed."""
    transforms = vault_data.get("transforms", {})
    if key in transforms:
        del transforms[key]
        return True
    return False


def get_pipeline(vault_data: dict, key: str) -> Optional[List[str]]:
    """Return the pipeline for a key, or None if not set."""
    return vault_data.get("transforms", {}).get(key)


def resolve_value(vault_data: dict, key: str) -> Optional[str]:
    """Return the transformed value for a key, applying its pipeline if any."""
    value = vault_data.get("vars", {}).get(key)
    if value is None:
        return None
    pipeline = get_pipeline(vault_data, key)
    if pipeline:
        value = apply_pipeline(value, pipeline)
    return value
