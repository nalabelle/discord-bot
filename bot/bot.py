#!/usr/bin/env python3
import sys,os
import logging
import asyncio
import discord
from discord.ext import commands
from cogs.weather import Weather
from cogs.giphy import Giphy
from cogs.status import Status
from cogs.roles import Roles
from cogs.errors import Errors
from cogs.drawing_contest import DrawingContest

try:
  token = os.environ['DISCORD_TOKEN']
except KeyError:
  print("Please set the DISCORD_TOKEN env variable before running")
  sys.exit(1)

bot_prefix = os.getenv('BOT_PREFIX', '!')

logging.basicConfig(level=logging.DEBUG)

client = commands.Bot(command_prefix=commands.when_mentioned_or(bot_prefix), description="Testing")
client.add_cog(Errors(client))
client.add_cog(Weather(client))
client.add_cog(Giphy(client))
client.add_cog(Status(client))
client.add_cog(Roles(client))
client.add_cog(DrawingContest(client))

client.run(token)
