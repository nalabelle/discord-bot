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
    extension_filters: List[str] = field(default_factory=lambda: ['.git'])
    extensions: List[str] = field(default_factory=list)
    log_level: str = os.getenv('LOG_LEVEL', 'ERROR')
    discord_log_level: str = os.getenv('DISCORD_LOG_LEVEL', 'ERROR')

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
            self.load_extension(extension)

    def extension_path(self, ext: str) -> Path:
        path = Path(self.data_path, 'extensions', ext)
        path = path.relative_to(Path('.').resolve())
        return path

    def extension_import(self, ext: str):
        path = self.extension_path(ext)
        return str(path).replace('/','.')

    def configure(self, path: str):
        self.config = BotConfig.from_yaml(path=path)
        if not os.path.exists(path):
            self.config.save()
        logging.getLogger().setLevel(self.config.log_level.upper())
        logging.getLogger('discord').setLevel(self.config.discord_log_level.upper())

    def load_extension(self, ext: str) -> None:
        super().load_extension(self.extension_import(ext))
        if ext not in self.config.extensions:
            self.config.extensions.append(ext)
            self.config.save()

    def unload_extension(self, ext: str) -> None:
        super().unload_extension(self.extension_import(ext))
        if ext in self.config.extensions:
            self.config.extensions.remove(ext)
            self.config.save()

    def reload_extension(self, ext: str) -> None:
        extension = self.extension_import(ext)
        log.debug('Reloading {} ({})'.format(ext, extension))
        super(commands.Bot, self).reload_extension(extension)

    def loaded_extensions(self) -> List[str]:
        return [f.replace(self.extension_import(''),'') for f in super().extensions]

    def available_extensions(self) -> List[str]:
        for root, dirs, files in os.walk(self.extension_path('').resolve()):
            return [d.replace('/', '.') for d in dirs if d not in self.config.extension_filters]

    def run(self):
        token = secret('discord_api_token')
        if token:
            super(commands.Bot, self).run(token)
        else:
            log.fatal("Discord API token not set")
            sys.exit(1)

