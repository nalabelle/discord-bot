import os
from pathlib import Path
from typing import List
from discord.ext import commands
from discord.ext.commands import ExtensionNotFound, ExtensionAlreadyLoaded, ExtensionNotLoaded, NoEntryPointError, ExtensionFailed

class ExtensionAdmin(commands.Cog):
    """ Extension Admin Commands """

    def __init__(self, bot):
        self.bot = bot

    def extension_path(self, ext: str) -> Path:
        path = Path(self.bot.data_path, 'extensions', ext)
        path = path.relative_to(Path('.').resolve())
        return path

    def extension_import(self, ext: str) -> str:
        path = self.extension_path(ext)
        return str(path).replace('/','.')

    def loaded_extensions(self) -> List[str]:
        prefix = self.extension_import('') + "."
        return [f.replace(prefix,'') for f in self.bot.extensions]

    def available_extensions(self) -> List[str]:
        exts = []
        prefix = self.extension_import('') + "."
        loaded_extensions = self.loaded_extensions()
        for child in self.extension_path('').iterdir():
            if str(child) in self.bot.config.extension_filters:
                continue
            if child.is_dir():
                if child.joinpath('__init__.py').exists():
                    ext_module = str(child).replace('/','.').replace(prefix,'')
                    if ext_module not in loaded_extensions:
                        exts.append(ext_module)
        return exts

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, *, extension : str):
        e = self.extension_import(extension)
        try:
            self.bot.load_extension(e)
            if e not in self.bot.config.extensions:
                self.bot.config.extensions.append(e)
                self.bot.config.save()
            await ctx.message.channel.send('Extension loaded: {}'.format(extension))
        except ExtensionNotFound:
            await ctx.message.channel.send('Extension not found: {}'.format(extension))
        except ExtensionAlreadyLoaded:
            await ctx.message.channel.send('Extension already loaded: {}'.format(extension))
        except NoEntryPointError:
            await ctx.message.channel.send('Exension has no setup function: {}'.format(extension))
        except ExtensionFailed as e:
            await ctx.message.channel.send('Extension failed: {}, {}'.format(extension, e))
            raise e

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, *, extension : str):
        e = self.extension_import(extension)
        try:
            self.bot.unload_extension(e)
            await ctx.message.channel.send('Extension unloaded: {}'.format(extension))
        except ExtensionNotLoaded:
            await ctx.message.channel.send('Extension not loaded: {}'.format(extension))
        if e in self.bot.config.extensions:
            self.bot.config.extensions.remove(e)
            self.bot.config.save()

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *, extension : str):
        e = self.extension_import(extension)
        try:
            self.bot.reload_extension(e)
            await ctx.message.channel.send('Extension reloaded: {}'.format(extension))
        except ExtensionNotLoaded:
            await ctx.message.channel.send('Extension not loaded: {}'.format(extension))
        except ExtensionNotFound:
            await ctx.message.channel.send('Extension not found: {}'.format(extension))
        except NoEntryPointError:
            await ctx.message.channel.send('Exension has no setup function: {}'.format(extension))
        except ExtensionFailed as e:
            await ctx.message.channel.send('Extension failed: {}, {}'.format(extension, e))

    @commands.command()
    @commands.is_owner()
    async def available(self, ctx):
        channel = ctx.message.channel
        exts = None
        with channel.typing():
            exts = ["- {}".format(e) for e in self.available_extensions()]
        if exts:
            exts.sort()
            await channel.send('Extensions:\n```{}```'.format("\n".join(exts)))
        else:
            await channel.send('No extensions found')

    @commands.command()
    @commands.is_owner()
    async def loaded(self, ctx):
        channel = ctx.message.channel
        exts = None
        await channel.send('Prefix: {}'.format(self.extension_import('')))
        with channel.typing():
            exts = ["- {}".format(e) for e in self.loaded_extensions()]
        if exts:
            exts.sort()
            await channel.send('Extensions:\n```{}```'.format("\n".join(exts)))
        else:
            await channel.send('No extensions found')


