"""CLI commands for expiry and reminder reports."""

import click
from envault.vault import Vault
from envault.expiry_report import build_report


@click.group()
def expiry():
    """View expiry and reminder reports for vault variables."""
    pass


@expiry.command("report")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--days",
    default=7,
    show_default=True,
    help="Window in days for 'expiring soon' entries.",
)
@click.option(
    "--reminder-days",
    default=7,
    show_default=True,
    help="Window in days for due reminders.",
)
def report_cmd(vault_name: str, password: str, days: int, reminder_days: int):
    """Show a full expiry and reminder report for a vault."""
    try:
        vault = Vault(vault_name, password)
        vault.load()
    except FileNotFoundError:
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    except Exception:
        click.echo("Failed to load vault. Check your password.", err=True)
        raise SystemExit(1)

    report = build_report(vault.data, days=days, reminder_days=reminder_days)

    # --- Expiring soon ---
    expiring = report.get("expiring_soon", [])
    click.echo(f"\n{'='*40}")
    click.echo(f"  Expiring within {days} day(s): {len(expiring)} key(s)")
    click.echo(f"{'='*40}")
    if expiring:
        for entry in expiring:
            key = entry["key"]
            expires_at = entry.get("expires_at", "unknown")
            seconds_left = entry.get("seconds_left", 0)
            hours_left = seconds_left / 3600
            click.echo(f"  {key:<30} expires: {expires_at}  ({hours_left:.1f}h left)")
    else:
        click.echo("  No keys expiring soon.")

    # --- Already expired ---
    expired = report.get("already_expired", [])
    click.echo(f"\n{'='*40}")
    click.echo(f"  Already expired: {len(expired)} key(s)")
    click.echo(f"{'='*40}")
    if expired:
        for entry in expired:
            key = entry["key"]
            expires_at = entry.get("expires_at", "unknown")
            click.echo(f"  {key:<30} expired: {expires_at}")
    else:
        click.echo("  No expired keys.")

    # --- Due reminders ---
    reminders = report.get("due_reminders", [])
    click.echo(f"\n{'='*40}")
    click.echo(f"  Reminders due within {reminder_days} day(s): {len(reminders)} key(s)")
    click.echo(f"{'='*40}")
    if reminders:
        for entry in reminders:
            key = entry["key"]
            due = entry.get("due", "unknown")
            message = entry.get("message", "")
            click.echo(f"  {key:<30} due: {due}  — {message}")
    else:
        click.echo("  No reminders due soon.")

    click.echo()


@expiry.command("summary")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--days", default=7, show_default=True, help="Lookahead window in days.")
def summary_cmd(vault_name: str, password: str, days: int):
    """Print a one-line summary of expiry status for a vault."""
    try:
        vault = Vault(vault_name, password)
        vault.load()
    except FileNotFoundError:
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    except Exception:
        click.echo("Failed to load vault. Check your password.", err=True)
        raise SystemExit(1)

    report = build_report(vault.data, days=days, reminder_days=days)

    n_soon = len(report.get("expiring_soon", []))
    n_expired = len(report.get("already_expired", []))
    n_reminders = len(report.get("due_reminders", []))

    click.echo(
        f"Vault '{vault_name}': "
        f"{n_expired} expired, "
        f"{n_soon} expiring within {days}d, "
        f"{n_reminders} reminder(s) due."
    )
