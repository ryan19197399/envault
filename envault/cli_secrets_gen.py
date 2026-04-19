"""CLI commands for generating secret values."""
import click
from envault.secrets_gen import generate_password, generate_token, generate_hex, generate_and_set
from envault.vault import Vault
from envault.storage import vault_exists


@click.group()
def gen():
    """Generate secure random secrets."""


@gen.command("password")
@click.option("--length", "-l", default=32, show_default=True, help="Password length.")
@click.option("--no-symbols", is_flag=True, help="Exclude punctuation.")
@click.option("--set", "key", default=None, help="Vault key to store the generated value.")
@click.option("--vault", "vault_name", default="default", show_default=True)
@click.password_option("--password", prompt="Vault password", required=False, default="")
def password_cmd(length, no_symbols, key, vault_name, password):
    """Generate a random password."""
    import string
    alphabet = string.ascii_letters + string.digits
    if not no_symbols:
        alphabet += string.punctuation
    value = generate_password(length=length, alphabet=alphabet)
    if key:
        if not vault_exists(vault_name):
            click.echo(f"Vault '{vault_name}' not found.", err=True)
            raise SystemExit(1)
        v = Vault.load(vault_name, password)
        if key not in v.data.get("vars", {}):
            click.echo(f"Key '{key}' not found in vault.", err=True)
            raise SystemExit(1)
        v.data["vars"][key] = value
        v.save()
        click.echo(f"Set '{key}' to generated password.")
    else:
        click.echo(value)


@gen.command("token")
@click.option("--bytes", "nbytes", default=32, show_default=True)
@click.option("--set", "key", default=None, help="Vault key to store the generated value.")
@click.option("--vault", "vault_name", default="default", show_default=True)
@click.password_option("--password", prompt="Vault password", required=False, default="")
def token_cmd(nbytes, key, vault_name, password):
    """Generate a URL-safe random token."""
    value = generate_token(nbytes=nbytes)
    if key:
        if not vault_exists(vault_name):
            click.echo(f"Vault '{vault_name}' not found.", err=True)
            raise SystemExit(1)
        v = Vault.load(vault_name, password)
        v.data["vars"][key] = value
        v.save()
        click.echo(f"Set '{key}' to generated token.")
    else:
        click.echo(value)


@gen.command("hex")
@click.option("--bytes", "nbytes", default=32, show_default=True)
def hex_cmd(nbytes):
    """Generate a random hex string."""
    click.echo(generate_hex(nbytes=nbytes))
