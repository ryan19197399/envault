"""Register the quota command group with the main CLI."""

from envault.cli_quota import quota


def register(main_cli):
    """Attach the quota command group to the root CLI."""
    main_cli.add_command(quota)
