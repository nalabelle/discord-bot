import sys
from discord.ext import commands

class ConfigReload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def get_config(self, ctx):
        await ctx.message.channel.send('```{}```'.format(self.bot.config.to_yaml()))

    @commands.command()
    @commands.is_owner()
    async def reload_config(self, ctx):
        self.bot.config.__dict__.update(self.bot.config.__class__.from_yaml(path=self.bot.config.path).__dict__)
        await ctx.message.channel.send('Config reloaded: ```{}```'.format(self.bot.config.to_yaml()))

    @commands.command()
    @commands.is_owner()
    async def exit(self, ctx):
        await ctx.message.channel.send('Logging out, bye!')
        sys.exit(0)
