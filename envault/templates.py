"""Template support for envault: save and apply variable templates."""

from typing import Optional

TEMPLATES_KEY = "__templates__"


def save_template(vault_data: dict, template_name: str, keys: list[str]) -> dict:
    """Save a named template as a list of variable keys."""
    if TEMPLATES_KEY not in vault_data:
        vault_data[TEMPLATES_KEY] = {}
    vault_data[TEMPLATES_KEY][template_name] = list(keys)
    return vault_data


def delete_template(vault_data: dict, template_name: str) -> bool:
    """Remove a template by name. Returns True if removed, False if not found."""
    templates = vault_data.get(TEMPLATES_KEY, {})
    if template_name in templates:
        del templates[template_name]
        return True
    return False


def get_template(vault_data: dict, template_name: str) -> Optional[list[str]]:
    """Return the list of keys for a template, or None if not found."""
    return vault_data.get(TEMPLATES_KEY, {}).get(template_name)


def list_templates(vault_data: dict) -> dict[str, list[str]]:
    """Return all templates as a dict of name -> [keys]."""
    return dict(vault_data.get(TEMPLATES_KEY, {}))


def apply_template(vault_data: dict, template_name: str) -> Optional[dict[str, str]]:
    """Return a dict of key->value for all keys in the template that exist in vault."""
    keys = get_template(vault_data, template_name)
    if keys is None:
        return None
    vars_ = vault_data.get("vars", {})
    return {k: vars_[k] for k in keys if k in vars_}
