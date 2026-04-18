"""CLI commands for vault sync/export/import."""

import click
from pathlib import Path

from envault.sync import export_vault, import_vault
from envault.vault import Vault


@click.group()
def sync():
    """Export and import encrypted vault files."""


@sync.command("export")
@click.argument("vault_name")
@click.argument("output", type=click.Path())
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def export_cmd(vault_name: str, output: str, password: str):
    """Export VAULT_NAME to an encrypted file at OUTPUT."""
    try:
        vault = Vault.load(vault_name, password)
    except FileNotFoundError:
        raise click.ClickException(f"Vault '{vault_name}' not found.")
    except Exception:
        raise click.ClickException("Failed to decrypt vault. Check your password.")

    out_path = Path(output)
    export_vault(vault, password, out_path)
    click.echo(f"Vault '{vault_name}' exported to {out_path}")


@sync.command("import")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("vault_name")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing vault.")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def import_cmd(input_file: str, vault_name: str, overwrite: bool, password: str):
    """Import an encrypted vault file into local storage as VAULT_NAME."""
    try:
        import_vault(Path(input_file), password, vault_name, overwrite=overwrite)
        click.echo(f"Vault imported as '{vault_name}'.")
    except FileExistsError as e:
        raise click.ClickException(str(e))
    except Exception:
        raise click.ClickException("Failed to import vault. Check your password or file.")
