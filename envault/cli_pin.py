"""CLI commands for PIN management."""

import click
from envault.vault import Vault
from envault.pin import set_pin, verify_pin, remove_pin, is_pin_expired, pin_expires_at
import datetime


@click.group()
def pin():
    """Manage vault PIN shortcuts."""
    pass


@pin.command("set")
@click.argument("vault_name")
@click.password_option("--pin", prompt="PIN", help="PIN to set")
@click.option("--ttl", default=3600, show_default=True, help="TTL in seconds")
def set_cmd(vault_name, pin, ttl):
    """Set a PIN for quick vault access."""
    try:
        v = Vault.load(vault_name, click.prompt("Master password", hide_input=True))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    set_pin(v.data, pin, ttl_seconds=ttl)
    v.save()
    click.echo(f"PIN set for vault '{vault_name}' (TTL: {ttl}s).")


@pin.command("verify")
@click.argument("vault_name")
@click.password_option("--pin", prompt="PIN", confirmation_prompt=False, help="PIN to verify")
def verify_cmd(vault_name, pin):
    """Verify a PIN against the stored hash."""
    try:
        v = Vault.load(vault_name, click.prompt("Master password", hide_input=True))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    if verify_pin(v.data, pin):
        click.echo("PIN verified successfully.")
    else:
        click.echo("Invalid or expired PIN.", err=True)
        raise SystemExit(1)


@pin.command("remove")
@click.argument("vault_name")
def remove_cmd(vault_name):
    """Remove the PIN from a vault."""
    try:
        v = Vault.load(vault_name, click.prompt("Master password", hide_input=True))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    remove_pin(v.data)
    v.save()
    click.echo(f"PIN removed from vault '{vault_name}'.")


@pin.command("status")
@click.argument("vault_name")
def status_cmd(vault_name):
    """Show PIN expiry status."""
    try:
        v = Vault.load(vault_name, click.prompt("Master password", hide_input=True))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    if is_pin_expired(v.data):
        click.echo("No active PIN or PIN has expired.")
    else:
        ts = pin_expires_at(v.data)
        dt = datetime.datetime.fromtimestamp(ts).isoformat()
        click.echo(f"PIN active, expires at: {dt}")
