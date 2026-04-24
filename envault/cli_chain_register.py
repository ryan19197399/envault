"""Registration helper to attach the chain command group to the main CLI."""
from envault.cli_chain import chain


def register(cli):
    """Attach the `chain` command group to the given Click group."""
    cli.add_command(chain)
