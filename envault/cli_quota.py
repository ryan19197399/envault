"""CLI commands for quota management."""

from __future__ import annotations

import click

from envault.vault import Vault
from envault.quota import set_quota, get_quota, remove_quota, quota_report


@click.group()
def quota():
    """Manage per-vault key and value size quotas."""


@quota.command("set")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--max-keys", type=int, default=None, help="Maximum number of keys.")
@click.option("--max-value-bytes", type=int, default=None, help="Maximum bytes per value.")
def set_cmd(vault_name, password, max_keys, max_value_bytes):
    """Set quota limits on a vault."""
    if max_keys is None and max_value_bytes is None:
        raise click.UsageError("Provide at least --max-keys or --max-value-bytes.")
    try:
        v = Vault.load(vault_name, password)
        set_quota(v.data, max_keys=max_keys, max_value_bytes=max_value_bytes)
        v.save(password)
        click.echo("Quota updated.")
    except FileNotFoundError:
        click.echo(f"Vault '{vault_name}' not found.", err=True)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)


@quota.command("show")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True)
def show_cmd(vault_name, password):
    """Show quota settings and current usage."""
    try:
        v = Vault.load(vault_name, password)
        report = quota_report(v.data)
        q = get_quota(v.data)
        click.echo(f"Max keys:          {q['max_keys']}")
        click.echo(f"Max value bytes:   {q['max_value_bytes']}")
        click.echo(f"Keys used:         {report['key_count']} ({report['keys_remaining']} remaining)")
        click.echo(f"Largest value:     {report['largest_value_bytes']} bytes")
    except FileNotFoundError:
        click.echo(f"Vault '{vault_name}' not found.", err=True)


@quota.command("remove")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True)
def remove_cmd(vault_name, password):
    """Remove quota settings (revert to defaults)."""
    try:
        v = Vault.load(vault_name, password)
        removed = remove_quota(v.data)
        if removed:
            v.save(password)
            click.echo("Quota settings removed.")
        else:
            click.echo("No quota settings found.")
    except FileNotFoundError:
        click.echo(f"Vault '{vault_name}' not found.", err=True)


def register(main_cli):
    main_cli.add_command(quota)
