"""CLI commands for diffing vaults."""
import click
from envault.vault import Vault
from envault.diff import diff_vaults, format_diff


@click.group()
def diff():
    """Diff vault contents."""
    pass


@diff.command("compare")
@click.argument("vault_a")
@click.argument("vault_b")
@click.option("--password-a", prompt="Password for vault A", hide_input=True)
@click.option("--password-b", prompt="Password for vault B", hide_input=True, default=None)
@click.option("--show-unchanged", is_flag=True, default=False, help="Also show unchanged keys.")
def compare_cmd(vault_a, vault_b, password_a, password_b, show_unchanged):
    """Compare two vaults and show differences."""
    if password_b is None:
        password_b = password_a

    try:
        va = Vault.load(vault_a, password_a)
    except Exception as e:
        raise click.ClickException(f"Could not load vault '{vault_a}': {e}")

    try:
        vb = Vault.load(vault_b, password_b)
    except Exception as e:
        raise click.ClickException(f"Could not load vault '{vault_b}': {e}")

    result = diff_vaults(va.data, vb.data)
    output = format_diff(result, show_unchanged=show_unchanged)
    click.echo(output)


@diff.command("summary")
@click.argument("vault_a")
@click.argument("vault_b")
@click.option("--password-a", prompt="Password for vault A", hide_input=True)
@click.option("--password-b", prompt="Password for vault B", hide_input=True, default=None)
def summary_cmd(vault_a, vault_b, password_a, password_b):
    """Show a summary count of differences between two vaults."""
    if password_b is None:
        password_b = password_a

    try:
        va = Vault.load(vault_a, password_a)
        vb = Vault.load(vault_b, password_b)
    except Exception as e:
        raise click.ClickException(str(e))

    result = diff_vaults(va.data, vb.data)
    click.echo(f"Added:     {len(result['added'])}")
    click.echo(f"Removed:   {len(result['removed'])}")
    click.echo(f"Changed:   {len(result['changed'])}")
    click.echo(f"Unchanged: {len(result['unchanged'])}")
