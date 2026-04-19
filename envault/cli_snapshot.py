"""CLI commands for vault snapshots."""
import click
from envault.vault import Vault
from envault.env_snapshot import (
    create_snapshot, restore_snapshot, delete_snapshot,
    list_snapshots, get_snapshot
)


@click.group()
def snapshot():
    """Manage vault snapshots."""


@snapshot.command("create")
@click.argument("vault_name")
@click.option("--name", default=None, help="Snapshot name (default: timestamp)")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def create_cmd(vault_name, name, password):
    """Create a snapshot of current vault variables."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    snap_name = create_snapshot(v.data, name)
    v.save()
    click.echo(f"Snapshot '{snap_name}' created.")


@snapshot.command("restore")
@click.argument("vault_name")
@click.argument("snap_name")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def restore_cmd(vault_name, snap_name, password):
    """Restore vault variables from a snapshot."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    if not restore_snapshot(v.data, snap_name):
        click.echo(f"Snapshot '{snap_name}' not found.", err=True)
        raise SystemExit(1)
    v.save()
    click.echo(f"Restored from snapshot '{snap_name}'.")


@snapshot.command("list")
@click.argument("vault_name")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def list_cmd(vault_name, password):
    """List all snapshots."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    snaps = list_snapshots(v.data)
    if not snaps:
        click.echo("No snapshots found.")
    for name, created_at in snaps:
        click.echo(f"{name}  (created: {created_at})")


@snapshot.command("delete")
@click.argument("vault_name")
@click.argument("snap_name")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def delete_cmd(vault_name, snap_name, password):
    """Delete a snapshot."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    if not delete_snapshot(v.data, snap_name):
        click.echo(f"Snapshot '{snap_name}' not found.", err=True)
        raise SystemExit(1)
    v.save()
    click.echo(f"Snapshot '{snap_name}' deleted.")
