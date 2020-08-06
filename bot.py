#!/usr/bin/env python3
import argparse
import glob
import os
import sys
import logging

app_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(os.path.join(app_path,'shared'))

from bot.bot import DiscordBot

logging.basicConfig()
log = logging.getLogger('__main__')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', dest="config", help="Path to config file")
    parser.add_argument('--data', dest="data", help="Path to data directory")
    args = parser.parse_args()
    data_path = args.data or os.getenv('BOT_DATA') or os.path.join(app_path, 'data')
    config_path = args.config or os.getenv('BOT_CONFIG') or os.path.join(data_path, "config.yml")
    bot = DiscordBot(config_path=config_path,data_path=data_path)
    bot.run()

if __name__ == "__main__":
    main()

