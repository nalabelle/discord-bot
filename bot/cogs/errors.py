import logging
import discord
from discord.ext import commands

class Errors(commands.Cog):
    """ Error handling """

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('ErrorsCog')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.channel.send('Cannot use {} in private!'.format(ctx.command))
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            await ctx.channel.send('I broke! 😭 {}'.format(str(error)))
            # log these so we can catch them
            self.logger.exception(error)

