import asyncio
from pathlib import Path

import click

from discord_bot.bot import DiscordBot


@click.command()
@click.option(
    "--config",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
    default="config.yaml",
    help="Path to config file. Defaults to `config.yaml in the current path",
)
def run(config) -> None:
    """Main command to start the bot"""
    bot = DiscordBot(config=config)
    asyncio.run(bot.run())


def main() -> None:
    run(auto_envvar_prefix="BOT")
