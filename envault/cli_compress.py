"""CLI commands for compressing and decompressing vault exports."""

import click

from envault.compress import compress_vault, decompress_vault, compression_ratio
from envault.storage import load_vault, save_vault, vault_exists


@click.group()
def compress():
    """Compress or decompress vault data."""


@compress.command("pack")
@click.argument("vault_name")
@click.argument("dest")
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
@click.option("--ratio", is_flag=True, default=False, help="Print compression ratio")
def pack_cmd(vault_name: str, dest: str, password: str, ratio: bool):
    """Compress VAULT_NAME to a gzip file at DEST."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    try:
        data = load_vault(vault_name, password)
    except Exception as exc:
        click.echo(f"Failed to load vault: {exc}", err=True)
        raise SystemExit(1)

    size = compress_vault(data, dest)
    click.echo(f"Compressed to '{dest}' ({size} bytes).")

    if ratio:
        r = compression_ratio(data, dest)
        click.echo(f"Compression ratio: {r:.2f}x")


@compress.command("unpack")
@click.argument("src")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing vault")
def unpack_cmd(src: str, vault_name: str, password: str, overwrite: bool):
    """Decompress SRC and save as VAULT_NAME."""
    if vault_exists(vault_name) and not overwrite:
        click.echo(
            f"Vault '{vault_name}' already exists. Use --overwrite to replace it.",
            err=True,
        )
        raise SystemExit(1)
    try:
        data = decompress_vault(src)
    except (FileNotFoundError, ValueError) as exc:
        click.echo(f"Failed to decompress: {exc}", err=True)
        raise SystemExit(1)

    save_vault(vault_name, data, password)
    click.echo(f"Vault '{vault_name}' restored from '{src}'.")
