import click
from pathlib import Path
from envault.backup import create_backup, list_backups, restore_backup, delete_backup, prune_backups


@click.group()
def backup():
    """Manage vault backups."""


@backup.command("create")
@click.argument("vault_name")
def create_cmd(vault_name):
    """Create a timestamped backup of a vault."""
    try:
        path = create_backup(vault_name)
        click.echo(f"Backup created: {path}")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)


@backup.command("list")
@click.argument("vault_name")
def list_cmd(vault_name):
    """List all backups for a vault."""
    backups = list_backups(vault_name)
    if not backups:
        click.echo("No backups found.")
    for p in backups:
        click.echo(p.name)


@backup.command("restore")
@click.argument("vault_name")
@click.argument("backup_file")
def restore_cmd(vault_name, backup_file):
    """Restore a vault from a backup file."""
    try:
        restore_backup(vault_name, Path(backup_file))
        click.echo(f"Vault '{vault_name}' restored from {backup_file}.")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)


@backup.command("delete")
@click.argument("backup_file")
def delete_cmd(backup_file):
    """Delete a specific backup file."""
    removed = delete_backup(Path(backup_file))
    if removed:
        click.echo(f"Deleted: {backup_file}")
    else:
        click.echo("Backup not found.", err=True)


@backup.command("prune")
@click.argument("vault_name")
@click.option("--keep", default=5, show_default=True, help="Number of backups to keep.")
def prune_cmd(vault_name, keep):
    """Prune old backups, keeping the N most recent."""
    deleted = prune_backups(vault_name, keep=keep)
    if deleted:
        for p in deleted:
            click.echo(f"Removed: {p.name}")
    else:
        click.echo("Nothing to prune.")
