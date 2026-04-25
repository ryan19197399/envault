"""CLI commands for managing lifecycle hooks on vault keys."""

from __future__ import annotations

import click

from envault.lifecycle import VALID_EVENTS, fire_hook, get_hook, list_hooks, remove_hook, set_hook
from envault.storage import load_vault, save_vault, vault_exists


@click.group()
def lifecycle() -> None:
    """Manage lifecycle hooks for vault keys."""


@lifecycle.command("set")
@click.argument("vault_name")
@click.argument("key")
@click.argument("event", type=click.Choice(list(VALID_EVENTS)))
@click.argument("command")
@click.password_option(prompt="Vault password")
def set_cmd(vault_name: str, key: str, event: str, command: str, password: str) -> None:
    """Register COMMAND to run on EVENT for KEY in VAULT_NAME."""
    if not vault_exists(vault_name):
        raise click.ClickException(f"Vault '{vault_name}' does not exist.")
    vault_data = load_vault(vault_name, password)
    try:
        set_hook(vault_data, key, event, command)
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    save_vault(vault_name, password, vault_data)
    click.echo(f"Hook '{event}' set for key '{key}'.")


@lifecycle.command("remove")
@click.argument("vault_name")
@click.argument("key")
@click.argument("event", type=click.Choice(list(VALID_EVENTS)))
@click.password_option(prompt="Vault password")
def remove_cmd(vault_name: str, key: str, event: str, password: str) -> None:
    """Remove the hook for EVENT on KEY in VAULT_NAME."""
    if not vault_exists(vault_name):
        raise click.ClickException(f"Vault '{vault_name}' does not exist.")
    vault_data = load_vault(vault_name, password)
    removed = remove_hook(vault_data, key, event)
    if not removed:
        raise click.ClickException(f"No '{event}' hook found for key '{key}'.")
    save_vault(vault_name, password, vault_data)
    click.echo(f"Hook '{event}' removed from key '{key}'.")


@lifecycle.command("show")
@click.argument("vault_name")
@click.argument("key")
@click.password_option(prompt="Vault password")
def show_cmd(vault_name: str, key: str, password: str) -> None:
    """Show all hooks registered for KEY in VAULT_NAME."""
    if not vault_exists(vault_name):
        raise click.ClickException(f"Vault '{vault_name}' does not exist.")
    vault_data = load_vault(vault_name, password)
    hooks = list_hooks(vault_data, key)
    if not hooks:
        click.echo(f"No hooks registered for key '{key}'.")
        return
    for event, command in hooks.items():
        click.echo(f"  {event}: {command}")


@lifecycle.command("fire")
@click.argument("vault_name")
@click.argument("key")
@click.argument("event", type=click.Choice(list(VALID_EVENTS)))
@click.password_option(prompt="Vault password")
def fire_cmd(vault_name: str, key: str, event: str, password: str) -> None:
    """Manually fire the hook for EVENT on KEY."""
    if not vault_exists(vault_name):
        raise click.ClickException(f"Vault '{vault_name}' does not exist.")
    vault_data = load_vault(vault_name, password)
    cmd = fire_hook(vault_data, key, event)
    if cmd is None:
        raise click.ClickException(f"No '{event}' hook found for key '{key}'.")
    click.echo(f"Fired: {cmd}")
