from discord.ext import commands

class PinMessages(commands.Cog):
    """ Pins and Unpins messages based on emoji """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if reaction.user_id == self.bot.user.id:
            return
        channel = self.bot.get_channel(int(reaction.channel_id))
        message = await channel.fetch_message(reaction.message_id)
        user = channel.guild.get_member(reaction.user_id)
        emoji = reaction.emoji
        if emoji is None:
            return
        if str(emoji) == '📌':
            if message.pinned:
                return
            reason = "📌 emoji added by {}".format(user)
            message.pin(reason=reason)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction):
        if reaction.user_id == self.bot.user.id:
            return
        channel = self.bot.get_channel(int(reaction.channel_id))
        message = await channel.fetch_message(reaction.message_id)
        user = channel.guild.get_member(reaction.user_id)
        emoji = reaction.emoji
        if emoji is None:
            return
        if str(emoji) == '📌':
            if not message.pinned:
                return
            reactions = [str(x) for x in message.reactions]
            if '📌' in reactions:
                return
            reason = "📌 emoji removed by {}".format(user)
            message.unpin(reason=reason)

def setup(bot):
    cog = PinMessages(bot)
    bot.add_cog(cog)

def teardown(bot):
    bot.remove_cog('PinMessages')
