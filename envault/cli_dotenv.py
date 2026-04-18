"""CLI commands for dotenv import/export."""
import click
from envault.import_export_dotenv import export_to_dotenv, import_from_dotenv


@click.group()
def dotenv():
    """Import and export variables using .env files."""


@dotenv.command("export")
@click.argument("vault_name")
@click.argument("output", default=".env")
@click.password_option("--password", "-p", prompt=True, help="Vault password")
def export_cmd(vault_name, output, password):
    """Export VAULT_NAME variables to a .env file."""
    try:
        count = export_to_dotenv(vault_name, password, output)
        click.echo(f"Exported {count} variable(s) to {output}")
    except FileNotFoundError:
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@dotenv.command("import")
@click.argument("vault_name")
@click.argument("input", default=".env")
@click.password_option("--password", "-p", prompt=True, help="Vault password")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys")
def import_cmd(vault_name, input, password, overwrite):
    """Import variables from a .env file into VAULT_NAME."""
    try:
        result = import_from_dotenv(vault_name, password, input, overwrite=overwrite)
        click.echo(f"Added: {len(result['added'])}, Overwritten: {len(result['overwritten'])}, Skipped: {len(result['skipped'])}")
        if result["skipped"]:
            click.echo(f"Skipped keys (use --overwrite to replace): {', '.join(result['skipped'])}")
    except FileNotFoundError as e:
        click.echo(f"File not found: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
