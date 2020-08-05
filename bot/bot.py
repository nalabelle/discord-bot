#!/usr/bin/env python3
import argparse
import os
import sys
import logging
from services.config import Config, Secrets
from discord.ext import commands

logging.basicConfig()
log = logging.getLogger('DiscordBot')

class DiscordBot(commands.Bot):
    pwd = os.path.dirname(os.path.realpath(__file__))
    default_config_path = os.path.join(pwd, 'config.yml')

    def __init__(self, config_path=None):
        if not config_path:
            config_path = self.default_config_path
        self.config = Config(path=config_path)
        self.configure_logging()
        prefix = self.config.command_prefix
        prefix = commands.when_mentioned_or(prefix)
        return super(commands.Bot, self).__init__(command_prefix=prefix)

    def configure_logging(self):
        logging_level = self.config.log_level.upper();
        log.setLevel(logging_level)

    def run(self):
        self.load_extensions()
        token = Secrets('discord_api_token')
        if token:
            super(commands.Bot, self).run(token)
        else:
            log.fatal("Discord API token not set")
            sys.exit(1)

    def load_extensions(self):
        extensions = self.config.extensions
        if not extensions:
            return
        for extension in extensions:
            self.load_extension(extension)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', dest="config", help="Path to config file")
    args = parser.parse_args()
    config_path = args.config or os.getenv('BOT_CONFIG')

    bot = DiscordBot(config_path=config_path)
    bot.run()

if __name__ == "__main__":
    main()

