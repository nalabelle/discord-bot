#!/usr/bin/env python3
import sys,os
import logging
import asyncio
import discord
from discord.ext import commands
from actions.weather.weather import Weather
from actions.giphy.giphy import Giphy
from actions.status.status import Status

try:
  token = os.environ['DISCORD_TOKEN']
except KeyError:
  print("Please set the DISCORD_TOKEN env variable before running")
  sys.exit(1)

logging.basicConfig(level=logging.DEBUG)

client = commands.Bot(command_prefix=commands.when_mentioned_or('!'), description="Testing")
client.add_cog(Weather(client))
client.add_cog(Giphy(client))
client.add_cog(Status(client))

@client.event
@asyncio.coroutine
def on_ready():
  yield from client.change_presence(game=discord.Game(name="with gear oil"))

client.run(token)
