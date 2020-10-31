""" Dice commands """
from dataclasses import dataclass, InitVar
from rolldice import DiceBag
from discord.ext import commands

@dataclass
class Roll:
    phrase: InitVar[str]
    score: int = None
    explain: str = None
    details: str = None

    def __post_init__(self, phrase) -> None:
        bag = DiceBag()
        bag.roll = phrase
        bag.roll_dice()
        self.explain = bag.last_explanation
        # Some dice libraries give a third level of info, this one does not.
        self.details = self.explain
        self.score = bag.last_roll

class Dice(commands.Cog):
    """ Dice commands """

    def __init__(self, bot):
        self.bot = bot

    def _roll(self, phrase : str) -> str:
        result = Roll(phrase)
        text = "Result: {} `{}`".format(result.score, result.explain)
        return text

    @commands.command()
    async def roll(self, ctx, *, phrase : str):
        """Roll some dice"""
        channel = ctx.message.channel
        async with channel.typing():
            text = self._roll(phrase)
        await channel.send(content=text)

def setup(bot):
    cog = Dice(bot)
    bot.add_cog(cog)

def teardown(bot):
    bot.remove_cog('Dice')
