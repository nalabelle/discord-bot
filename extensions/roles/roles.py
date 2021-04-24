"""
Cog for Role Command
"""

from discord import Forbidden
from discord.ext import commands


class Roles(commands.Cog):
    """ Role commands """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="role", invoke_without_command=False)
    async def role(self, ctx):
        """Manages assignable roles"""

    @role.command()
    @commands.guild_only()
    async def list(self, ctx):
        """List Roles"""
        roles_list = []
        async with ctx.typing():
            roles_list = self.get_roles_list(ctx.guild)
            if len(roles_list) > 0:
                await ctx.send("```{}```".format("\n".join([role.name for role in roles_list])))
                return
            await ctx.send("I couldn't find any roles!")

    @role.command()
    @commands.guild_only()
    async def add(self, ctx, *, roles: str):
        """Add a role to your account"""
        async with ctx.typing():
            role_list = self.role_inflator(ctx.guild, roles)
            if len(role_list) > 0:
                try:
                    await ctx.user.add_roles(*role_list)
                except Forbidden:
                    await ctx.send("I'm not allowed to add that role!")
                    return
                await ctx.send(
                    "I added {} to {}!".format(
                        ctx.user.name, ",".join([role.name for role in role_list])
                    )
                )
                return
            await ctx.send("I don't know what you mean!")

    @role.command(description="Remove yourself from a role")
    @commands.guild_only()
    async def remove(self, ctx, *, roles: str):
        """Remove a role from your account"""
        async with ctx.typing():
            role_list = self.role_inflator(ctx.guild, roles)
            if len(role_list) > 0:
                try:
                    await ctx.user.remove_roles(*role_list)
                except Forbidden:
                    await ctx.send("I'm not allowed to remove that role!")
                    return
                await ctx.send(
                    "I removed {} from {}!".format(
                        ctx.user.name, ",".join([role.name for role in role_list])
                    )
                )
                return
            await ctx.send("I don't know what you mean!")

    def get_roles_list(self, guild):
        """Gets the list of roles the bot is allowed to operate on"""
        everyone = guild.default_role.id
        bot = guild.me.top_role

        roles = [r for r in guild.roles if r != everyone and r < bot]
        roles.reverse()
        return roles

    def role_inflator(self, guild, roles_string):
        """Takes a list of roles as a string and returns a list of Role objects"""
        guild_roles = self.get_roles_list(guild)
        results = []
        roles = map(str.strip, roles_string.split(","))
        for role in roles:
            for guild_role in guild_roles:
                if guild_role.id == guild.default_role.id:
                    continue
                if role.casefold() == guild_role.name.casefold():
                    results.append(guild_role)
        return results
