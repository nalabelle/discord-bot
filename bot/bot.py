import glob
from pathlib import Path
import logging
import os
import sys
from datafile import DataFile
from file_secrets import secret
from dataclasses import dataclass, field
from discord.ext import commands
from typing import List, Dict

log = logging.getLogger('DiscordBot')

@dataclass
class BotConfig(DataFile):
    command_prefix: str = os.getenv('COMMAND_PREFIX', '!')
    discord_log_level: str = os.getenv('DISCORD_LOG_LEVEL', 'ERROR')
    extension_filters: List[str] = field(default_factory=lambda: ['.git'])
    extensions: List[str] = field(default_factory=list)
    log_level: str = os.getenv('LOG_LEVEL', 'ERROR')

class DiscordBot(commands.Bot):
    data_path = None
    loaded_extensions = []
    config = None

    def __init__(self, config_path: str, data_path: str):
        self.data_path = data_path
        self.configure(config_path)
        prefix = self.config.command_prefix
        prefix = commands.when_mentioned_or(prefix)
        super(commands.Bot, self).__init__(command_prefix=prefix)
        for extension in self.config.extensions:
            try:
                super(commands.Bot, self).load_extension(extension)
            except Exception as e:
                log.error("Could not load {}: {}".format(extension, e))
            else:
                log.info("Loaded extension: {}".format(extension))

    def configure(self, path: str):
        self.config = BotConfig.from_yaml(path=path)
        if not os.path.exists(path):
            self.config.save()
        logging.getLogger().setLevel(self.config.log_level.upper())
        logging.getLogger('discord').setLevel(self.config.discord_log_level.upper())

    def run(self):
        token = secret('discord_api_token')
        if token:
            super(commands.Bot, self).run(token)
        else:
            log.fatal("Discord API token not set")
            sys.exit(1)

