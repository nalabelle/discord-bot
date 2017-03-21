import sys,os
import asyncio
import discord
from discord.ext import commands
import giphypop

try:
  GIPHY_API_KEY = os.environ['GIPHY_API_KEY']
except KeyError:
  #library will use the public key if available
  pass

class Giphy:
  """ Giphy commands """

  def __init__(self, bot):
        self.bot = bot
        self.giphypop = giphypop.Giphy()

  @commands.command(pass_context=True,description='Give me a phrase, get a giphy')
  @asyncio.coroutine
  def giphy(self, ctx, *, phrase : str):
    channel = ctx.message.channel
    try:
      yield from self.bot.send_typing(channel)
      results = self.giphypop.translate(phrase=phrase)
      if results.url:
        yield from self.bot.say('{}'.format(results.url))
    except Exception as e:
      yield from self.bot.say('I broke! 😭 {}'.format(str(e)))
      pass

