"""CLI commands for observable variables."""

import click
from envault.vault import Vault
from envault import observable as obs


@click.group()
def observe():
    """Manage observable variable triggers."""
    pass


@observe.command("add")
@click.argument("vault_name")
@click.argument("key")
@click.option("--action", required=True, type=click.Choice(["log", "copy", "notify"]), help="Action to trigger.")
@click.option("--target", default=None, help="Target key for 'copy' action.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def add_observer(vault_name, key, action, target, password):
    """Add an observer to KEY in VAULT_NAME."""
    try:
        vault = Vault.load(vault_name, password)
        obs.set_observer(vault.data, key, action, target)
        vault.save(password)
        click.echo(f"Observer added: {key} -> {action}" + (f" (target: {target})" if target else ""))
    except (KeyError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@observe.command("remove")
@click.argument("vault_name")
@click.argument("key")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def remove_observer(vault_name, key, password):
    """Remove observer from KEY in VAULT_NAME."""
    try:
        vault = Vault.load(vault_name, password)
        removed = obs.remove_observer(vault.data, key)
        if removed:
            vault.save(password)
            click.echo(f"Observer removed for '{key}'.")
        else:
            click.echo(f"No observer found for '{key}'.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@observe.command("list")
@click.argument("vault_name")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def list_observers(vault_name, password):
    """List all observers in VAULT_NAME."""
    try:
        vault = Vault.load(vault_name, password)
        entries = obs.list_observers(vault.data)
        if not entries:
            click.echo("No observers defined.")
            return
        for entry in entries:
            target_str = f" -> {entry['target']}" if "target" in entry else ""
            click.echo(f"  {entry['key']}: {entry['action']}{target_str}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


def register(main_cli):
    main_cli.add_command(observe)
