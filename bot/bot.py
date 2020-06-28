#!/usr/bin/env python3
import argparse
import os
import sys
import logging
from services.config import Config
from discord.ext import commands

logging.basicConfig()
log = logging.getLogger('DiscordBot')

class DiscordBot(commands.Bot):
    pwd = os.path.dirname(os.path.realpath(__file__))
    default_config_path = os.path.join(pwd, 'config.yml')
    default_storage_path = os.path.join(pwd, 'data')

    def __init__(self, config_path=None):
        self.initialize_config(config_path)
        self.configure_logging()
        prefix = self.config.get('command_prefix', '!')
        prefix = commands.when_mentioned_or(prefix)
        return super(commands.Bot, self).__init__(command_prefix=prefix)

    def initialize_config(self, config_path=None):
        if not config_path:
            config_path = self.default_config_path
        self.config = Config(path=config_path, allow_env=True)

    def configure_logging(self):
        logging_level = self.config.get('log_level', 'ERROR').upper();
        log.setLevel(logging_level)
        log.info(log.level)

    def run(self):
        self.load_extensions()
        token = self.config.get('discord_api_token', check_file=True)
        if token:
            super(commands.Bot, self).run(token)
        else:
            log.fatal("Discord API token not set")
            sys.exit(1)

    def load_extensions(self):
        extensions = self.config.get('extensions')
        if not extensions:
            return
        for extension in extensions:
            self.load_extension(extension)

    def get_storage_path(self, module):
        path = self.config.get('data_path', self.default_storage_path)
        return os.path.join(path, module)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', dest="config", help="Path to config file")
    args = parser.parse_args()
    config_path = args.config or os.getenv('BOT_CONFIG')

    bot = DiscordBot(config_path=config_path)
    bot.run()

if __name__ == "__main__":
    main()

