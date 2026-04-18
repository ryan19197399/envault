"""CLI commands for viewing variable change history."""

import click
from envault.vault import Vault
from envault.history import get_history, clear_history


@click.group()
def history():
    """View and manage variable change history."""
    pass


@history.command("show")
@click.argument("vault_name")
@click.option("--key", default=None, help="Filter history by variable name.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def show_history(vault_name, key, password):
    """Show change history for a vault or a specific key."""
    vault = Vault(vault_name, password)
    if not vault.exists():
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault.load()
    entries = get_history(vault.data, key=key)
    if not entries:
        click.echo("No history found.")
        return
    for entry in entries:
        parts = [entry["timestamp"], entry["action"].upper(), entry["key"]]
        if "old_value" in entry:
            parts.append(f"old={entry['old_value']!r}")
        if "new_value" in entry:
            parts.append(f"new={entry['new_value']!r}")
        click.echo("  ".join(parts))


@history.command("clear")
@click.argument("vault_name")
@click.option("--key", default=None, help="Clear history only for this variable.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
@click.confirmation_option(prompt="Are you sure you want to clear history?")
def clear_cmd(vault_name, key, password):
    """Clear history for a vault or a specific key."""
    vault = Vault(vault_name, password)
    if not vault.exists():
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault.load()
    clear_history(vault.data, key=key)
    vault.save()
    target = f"key '{key}'" if key else "all keys"
    click.echo(f"History cleared for {target}.")
