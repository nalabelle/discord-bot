"""
Sync Commands
"""

import logging
from typing import Literal, Optional

import discord
from discord.ext import commands
from discord.ext.commands import Greedy

log = logging.getLogger("Sync")


class SyncCommand(commands.Cog, name="Sync"):
    """sync commands"""

    def __init__(self, bot):
        self.bot = bot

    # https://gist.github.com/AbstractUmbra/a9c188797ae194e592efe05fa129c57f?permalink_comment_id=4121434#gistcomment-4121434
    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
        self,
        ctx: commands.Context,
        guilds: Greedy[discord.Guild],
        flag: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        """
        Syncs Discord AppCommands with Guilds. No arg will sync globally

        Args:
          guilds:
            The guilds to sync, when called explicitly
          flag:
            ~ to sync the current guild
            * to copy global app commands to this guild and sync
            ^ clear all commands from the guild and sync
        """
        synced = []
        log.debug("Commands: %s", ", ".join([c.name for c in ctx.bot.tree.walk_commands()]))
        if not guilds:
            match flag:
                case "~":
                    synced = await ctx.bot.tree.sync(guild=ctx.guild)
                case "*":
                    ctx.bot.tree.copy_global_to(guild=ctx.guild)
                    synced = await ctx.bot.tree.sync(guild=ctx.guild)
                case "^":
                    ctx.bot.tree.clear_commands(guild=ctx.guild)
                    await ctx.bot.tree.sync(guild=ctx.guild)
                case _:
                    synced = await ctx.bot.tree.sync()
            await ctx.send(
                f"Synced {len(synced)} commands "
                f"{'globally' if flag is None else 'to the current guild.'}",
            )
            return
        for guild in guilds:
            await ctx.bot.tree.sync(guild=guild)
        await ctx.send(f"Synced the tree to {len(guilds)} guilds.")


async def setup(bot):
    """Cog creation"""
    await bot.add_cog(SyncCommand(bot))


async def teardown(bot):
    """Cog teardown"""
    await bot.remove_cog("Sync")
