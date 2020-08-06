import discord
from discord.ext import commands
from services.giphy import Giphy as GiphyLib

class Giphy(commands.Cog):
    """ Giphy commands """

    def __init__(self, bot):
        self.bot = bot
        self.giphy = GiphyLib()

    @commands.command(description='Give me a phrase, get a giphy')
    async def giphy(self, ctx, *, phrase : str):
        channel = ctx.message.channel
        async with channel.typing():
            giphy_content = self.get_giphy(phrase)
        await channel.send(content=giphy_content)

    def get_giphy(self, phrase):
        giphy = self.giphy.get(phrase)
        return giphy

def setup(bot):
    cog = Giphy(bot)
    bot.add_cog(cog)

def teardown(bot):
    bot.remove_cog('Giphy')

