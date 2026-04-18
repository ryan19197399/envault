"""CLI commands for audit log inspection."""

import click
from envault.audit import read_log, clear_log


@click.group()
def audit():
    """View and manage vault audit logs."""
    pass


@audit.command("log")
@click.argument("vault_name")
@click.option("--limit", default=20, show_default=True, help="Max entries to show.")
def show_log(vault_name: str, limit: int):
    """Show recent audit events for a vault."""
    events = read_log(vault_name)
    if not events:
        click.echo(f"No audit log found for vault '{vault_name}'.")
        return
    recent = events[-limit:]
    for e in recent:
        key_part = f"  key={e['key']}" if "key" in e else ""
        click.echo(f"{e['timestamp']}  {e['action']}{key_part}")


@audit.command("clear")
@click.argument("vault_name")
@click.confirmation_option(prompt="Clear audit log? This cannot be undone.")
def clear(vault_name: str):
    """Clear the audit log for a vault."""
    clear_log(vault_name)
    click.echo(f"Audit log cleared for vault '{vault_name}'.")
