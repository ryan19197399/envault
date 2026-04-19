"""CLI commands for formatted vault output."""
import click
from envault.vault import Vault
from envault.fmt import format_output
from envault.tags import get_tags
from envault.notes import list_notes


@click.group()
def fmt():
    """Display vault variables in various formats."""


@fmt.command("show")
@click.argument("vault_name")
@click.password_option("--password", "-p", prompt="Password", confirmation_prompt=False)
@click.option("--format", "fmt", type=click.Choice(["table", "json", "csv"]), default="table", show_default=True)
@click.option("--with-tags", is_flag=True, default=False, help="Include tags column (table only).")
@click.option("--with-notes", is_flag=True, default=False, help="Include notes column (table only).")
def show_cmd(vault_name, password, fmt, with_tags, with_notes):
    """Show vault variables in the chosen format."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    data = {k: val for k, val in v.data.items() if not k.startswith("_")}

    kwargs = {}
    if with_tags and fmt == "table":
        kwargs["tags"] = v.data.get("_tags", {})
    if with_notes and fmt == "table":
        kwargs["notes"] = v.data.get("_notes", {})

    click.echo(format_output(data, fmt=fmt, **kwargs))
