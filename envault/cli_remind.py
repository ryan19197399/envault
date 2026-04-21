"""CLI commands for managing key reminders in envault."""

import click
from datetime import datetime, timezone
from envault.vault import Vault
from envault.remind import set_reminder, remove_reminder, get_reminder, list_due, list_reminders


@click.group()
def remind():
    """Manage reminders for vault keys."""
    pass


@remind.command("set")
@click.argument("vault_name")
@click.argument("key")
@click.option("--message", "-m", required=True, help="Reminder message.")
@click.option("--due", "-d", required=True, help="Due date/time in ISO 8601 format (e.g. 2025-12-31T00:00:00).")
@click.password_option("--password", "-p", prompt="Vault password", help="Vault password.")
def set_cmd(vault_name, key, message, due, password):
    """Set a reminder for a vault key."""
    try:
        vault = Vault.load(vault_name, password)
    except FileNotFoundError:
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    except Exception:
        click.echo("Failed to load vault. Check your password.", err=True)
        raise SystemExit(1)

    if key not in vault.data.get("vars", {}):
        click.echo(f"Key '{key}' not found in vault.", err=True)
        raise SystemExit(1)

    try:
        due_dt = datetime.fromisoformat(due)
    except ValueError:
        click.echo(f"Invalid date format: '{due}'. Use ISO 8601 (e.g. 2025-12-31T00:00:00).", err=True)
        raise SystemExit(1)

    set_reminder(vault.data, key, due_dt, message)
    vault.save(vault_name, password)
    click.echo(f"Reminder set for '{key}' due {due_dt.isoformat()}.")


@remind.command("remove")
@click.argument("vault_name")
@click.argument("key")
@click.password_option("--password", "-p", prompt="Vault password", help="Vault password.")
def remove_cmd(vault_name, key, password):
    """Remove a reminder for a vault key."""
    try:
        vault = Vault.load(vault_name, password)
    except FileNotFoundError:
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    except Exception:
        click.echo("Failed to load vault. Check your password.", err=True)
        raise SystemExit(1)

    removed = remove_reminder(vault.data, key)
    if removed:
        vault.save(vault_name, password)
        click.echo(f"Reminder for '{key}' removed.")
    else:
        click.echo(f"No reminder found for '{key}'.")


@remind.command("show")
@click.argument("vault_name")
@click.argument("key")
@click.password_option("--password", "-p", prompt="Vault password", help="Vault password.")
def show_cmd(vault_name, key, password):
    """Show the reminder for a specific key."""
    try:
        vault = Vault.load(vault_name, password)
    except FileNotFoundError:
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    except Exception:
        click.echo("Failed to load vault. Check your password.", err=True)
        raise SystemExit(1)

    reminder = get_reminder(vault.data, key)
    if reminder is None:
        click.echo(f"No reminder set for '{key}'.")
    else:
        click.echo(f"Key:     {key}")
        click.echo(f"Due:     {reminder['due']}")
        click.echo(f"Message: {reminder['message']}")


@remind.command("list")
@click.argument("vault_name")
@click.password_option("--password", "-p", prompt="Vault password", help="Vault password.")
@click.option("--due-only", is_flag=True, default=False, help="Show only reminders that are currently due.")
def list_cmd(vault_name, password, due_only):
    """List all reminders in a vault."""
    try:
        vault = Vault.load(vault_name, password)
    except FileNotFoundError:
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    except Exception:
        click.echo("Failed to load vault. Check your password.", err=True)
        raise SystemExit(1)

    if due_only:
        reminders = list_due(vault.data)
        label = "due reminders"
    else:
        reminders = list_reminders(vault.data)
        label = "reminders"

    if not reminders:
        click.echo(f"No {label} found.")
        return

    click.echo(f"{'KEY':<20} {'DUE':<25} MESSAGE")
    click.echo("-" * 70)
    for entry in reminders:
        click.echo(f"{entry['key']:<20} {entry['due']:<25} {entry['message']}")
