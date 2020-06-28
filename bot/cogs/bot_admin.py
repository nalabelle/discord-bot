import discord
import glob
from discord.ext import commands
from discord.ext.commands import ExtensionNotFound, ExtensionAlreadyLoaded, ExtensionNotLoaded, NoEntryPointError, ExtensionFailed

class BotAdmin(commands.Cog):
    """ Bot Admin Commands """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def get_config(self, ctx):
        await ctx.message.channel.send('```{}```'.format(self.bot.config.dump()))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def save_config(self, ctx):
        self.bot.config.save_config()
        await ctx.message.channel.send('Saved')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, extension : str):
        try:
            self.bot.load_extension(extension)
            self.bot.config.get('extensions').append(extension)
            await ctx.message.channel.send('Extension loaded: {}'.format(extension))
        except ExtensionNotFound:
            await ctx.message.channel.send('Extension not found: {}'.format(extension))
        except ExtensionAlreadyLoaded:
            await ctx.message.channel.send('Extension already loaded: {}'.format(extension))
        except NoEntryPointError:
            await ctx.message.channel.send('Exension has no setup function: {}'.format(extension))
        except ExtensionFailed as e:
            await ctx.message.channel.send('Extension failed: {}, {}'.format(extension, e))


    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, extension : str):
        try:
            self.bot.unload_extension(extension)
            await ctx.message.channel.send('Extension unloaded: {}'.format(extension))
        except ExtensionNotLoaded:
            await ctx.message.channel.send('Extension not loaded: {}'.format(extension))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, extension : str):
        try:
            self.bot.reload_extension(extension)
            await ctx.message.channel.send('Extension reloaded: {}'.format(extension))
        except ExtensionNotLoaded:
            await ctx.message.channel.send('Extension not loaded: {}'.format(extension))
        except ExtensionNotFound:
            await ctx.message.channel.send('Extension not found: {}'.format(extension))
        except NoEntryPointError:
            await ctx.message.channel.send('Exension has no setup function: {}'.format(extension))
        except ExtensionFailed as e:
            await ctx.message.channel.send('Extension failed: {}'.format(extension))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def available(self, ctx):
        files = ["- {}".format(f.replace('.py','').replace('/','.')) for f in glob.glob('cogs/*.py')]
        if files:
            files.sort()
            await ctx.message.channel.send('Extensions:\n```{}```'.format("\n".join(files)))
        else:
            await ctx.message.channel.send('No extensions found')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def loaded(self, ctx):
        files = ["- {}".format(f) for f in self.bot.extensions.keys()]
        if files:
            files.sort()
            await ctx.message.channel.send('Extensions:\n```{}```'.format("\n".join(files)))
        else:
            await ctx.message.channel.send('No extensions found')


def setup(bot):
    bot.add_cog(BotAdmin(bot))

def teardown(bot):
    bot.remove_cog('BotAdmin')

