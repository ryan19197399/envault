"""CLI commands for group management in envault."""

import click
from envault.vault import Vault
from envault import group as grp


@click.group()
def group():
    """Manage key groups."""


@group.command("create")
@click.argument("vault_name")
@click.argument("group_name")
@click.password_option(prompt="Vault password")
def create_cmd(vault_name, group_name, password):
    """Create a new empty group."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    grp.create_group(v.data, group_name)
    v.save()
    click.echo(f"Group '{group_name}' created.")


@group.command("delete")
@click.argument("vault_name")
@click.argument("group_name")
@click.password_option(prompt="Vault password")
def delete_cmd(vault_name, group_name, password):
    """Delete a group."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    if grp.delete_group(v.data, group_name):
        v.save()
        click.echo(f"Group '{group_name}' deleted.")
    else:
        click.echo(f"Group '{group_name}' not found.", err=True)


@group.command("add")
@click.argument("vault_name")
@click.argument("group_name")
@click.argument("key")
@click.password_option(prompt="Vault password")
def add_cmd(vault_name, group_name, key, password):
    """Add a key to a group."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    try:
        grp.add_to_group(v.data, group_name, key)
        v.save()
        click.echo(f"Key '{key}' added to group '{group_name}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@group.command("remove")
@click.argument("vault_name")
@click.argument("group_name")
@click.argument("key")
@click.password_option(prompt="Vault password")
def remove_cmd(vault_name, group_name, key, password):
    """Remove a key from a group."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    if grp.remove_from_group(v.data, group_name, key):
        v.save()
        click.echo(f"Key '{key}' removed from group '{group_name}'.")
    else:
        click.echo(f"Key '{key}' not in group '{group_name}'.", err=True)


@group.command("list")
@click.argument("vault_name")
@click.option("--group-name", default=None, help="Show keys for a specific group.")
@click.password_option(prompt="Vault password")
def list_cmd(vault_name, group_name, password):
    """List groups or keys in a group."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    if group_name:
        keys = grp.get_group(v.data, group_name)
        if keys is None:
            click.echo(f"Group '{group_name}' not found.", err=True)
            raise SystemExit(1)
        if keys:
            for k in keys:
                click.echo(k)
        else:
            click.echo(f"Group '{group_name}' is empty.")
    else:
        groups = grp.list_groups(v.data)
        if not groups:
            click.echo("No groups defined.")
        else:
            for g, keys in groups.items():
                click.echo(f"{g}: {', '.join(keys) if keys else '(empty)'}")
