import sys,os
import asyncio
import discord
from discord.ext import commands

class Status:
  """ Now Playing """

  def __init__(self, bot):
        self.bot = bot

  @commands.command(hidden=True)
  @commands.has_permissions(manage_webhooks=True)
  @asyncio.coroutine
  def status(self, *, status : str):
    try:
      yield from self.bot.change_presence(game=discord.Game(name=status))
    except Exception as e:
      yield from self.bot.say('I broke! 😭 {}'.format(str(e)))
      pass

