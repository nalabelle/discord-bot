import logging
import sys
from pathlib import Path

import discord
from discord.ext import commands
from file_secrets import secret

import discord_bot.config
from discord_bot.config import BotConfig, ExtensionConfig

log = logging.getLogger("DiscordBot")


class DiscordBot(commands.Bot):
    data = None
    data_path = None
    loaded_extensions = []
    config = None
    # guilds needs to be set by default for state
    registered_intents: set = {"guilds"}

    def register_intents(self) -> None:
        for ext in self.config.extensions:
            if ext.intents:
                self.registered_intents.update(ext.intents)

    def extension_name(self, ext: ExtensionConfig) -> str:
        path = Path(ext.path_override or self.config.extension_path)
        path = path / ext.name
        return str(path).replace("/", ".")

    async def load_extensions(self) -> None:
        for ext in self.config.extensions:
            package = self.extension_name(ext)
            try:
                await super(commands.Bot, self).load_extension(name=package)
            except Exception as e:
                log.exception("Could not load %s: %s", ext.name, e)
            else:
                log.info("Loaded extension: %s", ext.name)

    def __init__(self, config: BotConfig):
        self.config = discord_bot.config.load(config_path=config)
        logging.getLogger().setLevel(self.config.log_level.value)
        log.setLevel(self.config.log_level.value)
        log.debug("Logging at %s", logging.getLevelName(log.level))
        log.debug("Configuration: %s", self.config.json())
        discord.utils.setup_logging(level=self.config.discord_log_level.value, root=False)

        self.data = Path(self.config.data_path)
        self.data_path = self.config.data_path
        self.register_intents()
        prefix = commands.when_mentioned_or(self.config.command_prefix)
        if self.registered_intents:
            intents_dict = dict.fromkeys(self.registered_intents, True)
            log.debug(intents_dict)
            intents = discord.Intents(**intents_dict)
        else:
            intents = discord.Intents.default()
        super(commands.Bot, self).__init__(command_prefix=prefix, intents=intents)

    async def setup_hook(self):
        await self.load_extensions()

    async def run(self):
        token = secret("discord_api_token")
        if token:
            async with self:
                await super(commands.Bot, self).start(token)
        else:
            log.fatal("Discord API token not set")
            sys.exit(1)
