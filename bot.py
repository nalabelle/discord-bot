#!/usr/bin/env python3
import sys,os
import signal
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

def interrupt(signal, frame):
  print("Exiting")
  sys.exit(0)

signal.signal(signal.SIGINT, interrupt)

client = commands.Bot(command_prefix=commands.when_mentioned_or('!'), description="Testing")
client.add_cog(Weather(client))
client.add_cog(Giphy(client))
client.add_cog(Status(client))

@client.event
@asyncio.coroutine
def on_ready():
  yield from client.change_presence(game=discord.Game(name="with gear oil"))

while True:
  try:
    client.run(token)
  except KeyboardInterrupt as e:
    print("Exiting")
    sys.exit(0)
  except ConnectionResetError as e:
    print("Connection Reset: {}".format(e))
    pass
  except Exception as e:
    print("Exception: {}".format(e))
    pass
