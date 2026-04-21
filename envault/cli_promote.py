"""CLI commands for promoting environment variables between environments."""

import click
from envault.vault import Vault
from envault.promote import promote_key, promote_all, next_env, get_env_chain


@click.group()
def promote():
    """Promote variables between environments."""


@promote.command("key")
@click.argument("src_vault")
@click.argument("dst_vault")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing key.")
def promote_key_cmd(src_vault, dst_vault, key, password, overwrite):
    """Promote a single KEY from SRC_VAULT to DST_VAULT."""
    try:
        src = Vault.load(src_vault, password)
        dst = Vault.load(dst_vault, password)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    try:
        moved = promote_key(src.data, dst.data, key, overwrite=overwrite)
    except KeyError as e:
        raise click.ClickException(str(e))
    if moved:
        dst.save()
        click.echo(f"Promoted '{key}' from '{src_vault}' to '{dst_vault}'.")
    else:
        click.echo(f"Skipped '{key}': already exists in '{dst_vault}' (use --overwrite to force).")


@promote.command("all")
@click.argument("src_vault")
@click.argument("dst_vault")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--overwrite", is_flag=True, default=False)
def promote_all_cmd(src_vault, dst_vault, password, overwrite):
    """Promote ALL variables from SRC_VAULT to DST_VAULT."""
    try:
        src = Vault.load(src_vault, password)
        dst = Vault.load(dst_vault, password)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    summary = promote_all(src.data, dst.data, overwrite=overwrite)
    dst.save()
    click.echo(f"Promoted: {summary['promoted']}")
    click.echo(f"Skipped:  {summary['skipped']}")


@promote.command("chain")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True)
def show_chain_cmd(vault_name, password):
    """Show the promotion chain configured for VAULT_NAME."""
    try:
        v = Vault.load(vault_name, password)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    chain = get_env_chain(v.data)
    click.echo(" -> ".join(chain))


@promote.command("next")
@click.argument("vault_name")
@click.argument("current_env")
@click.option("--password", prompt=True, hide_input=True)
def next_cmd(vault_name, current_env, password):
    """Show the next environment after CURRENT_ENV in the chain."""
    try:
        v = Vault.load(vault_name, password)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    nxt = next_env(v.data, current_env)
    if nxt:
        click.echo(nxt)
    else:
        click.echo(f"'{current_env}' is the last environment in the chain.")
