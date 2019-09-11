from discord.ext import commands

def is_owner_or_admin():
    async def predicate(ctx):
        # if it's the owner, let it do whatever
        if await ctx.bot.is_owner(ctx.author):
            return True
        # otherwise, let's check guild permissions
        if not isinstance(ctx.channel, discord.abc.GuildChannel):
            raise NoPrivateMessage()
        permissions = ch.permissions_for(ctx.channel.author)
        if 'manage_webhooks' not in permissions:
            raise MissingRole('ManageWebhooks')
        return True
    return commands.check(predicate)


