"""CLI commands for searching vault variables."""

import click
from envault.vault import Vault
from envault.search import search_combined


@click.group()
def search():
    """Search variables in a vault."""
    pass


@search.command("query")
@click.argument("vault_name")
@click.password_option("--password", prompt=True, confirmation_prompt=False)
@click.option("--key", default=None, help="Glob pattern to match variable keys.")
@click.option("--value", default=None, help="Substring to match in variable values.")
@click.option("--tag", default=None, help="Filter variables by tag.")
def query_cmd(vault_name, password, key, value, tag):
    """Search variables in VAULT_NAME by key, value, or tag."""
    vault = Vault(vault_name, password)
    if not vault.exists():
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault.load()

    if not key and not value and not tag:
        click.echo("Provide at least one of --key, --value, or --tag.", err=True)
        raise SystemExit(1)

    results = search_combined(vault.data, key_pattern=key, value_substr=value, tag=tag)

    if not results:
        click.echo("No matching variables found.")
        return

    for k, v in sorted(results.items()):
        click.echo(f"{k}={v}")
