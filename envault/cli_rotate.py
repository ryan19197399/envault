"""CLI commands for password and key rotation."""

import click
from envault.rotate import rotate_password, rotate_key
from envault.storage import vault_exists


@click.group()
def rotate():
    """Rotate vault password or individual keys."""
    pass


@rotate.command("password")
@click.argument("vault_name")
@click.option("--old-password", prompt=True, hide_input=True, help="Current password")
@click.option("--new-password", prompt=True, hide_input=True,
              confirmation_prompt=True, help="New password")
def rotate_password_cmd(vault_name, old_password, new_password):
    """Re-encrypt VAULT_NAME with a new password."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    try:
        rotate_password(vault_name, old_password, new_password)
        click.echo(f"Password rotated for vault '{vault_name}'.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@rotate.command("key")
@click.argument("vault_name")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
def rotate_key_cmd(vault_name, key, password):
    """Re-encrypt KEY inside VAULT_NAME (refreshes ciphertext at rest)."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    try:
        rotate_key(vault_name, password, key)
        click.echo(f"Key '{key}' rotated in vault '{vault_name}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
