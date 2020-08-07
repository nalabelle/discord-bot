import discord
from discord.ext import commands
from discord import Forbidden

class Roles(commands.Cog):
    """ Role commands """

    def __init__(self, bot):
        self.bot = bot
        self.top_roles = dict()

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.update_top_role_from_guild(guild)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        self.update_top_role_from_guild(role.guild)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        self.update_top_role_from_guild(role.guild)

    @commands.Cog.listener()
    async def on_guild_role_update(self, role_before, role_after):
        self.update_top_role_from_guild(role_after.guild)

    @commands.Cog.listener()
    async def on_member_update(self, member_before, member_after):
        if(member_after.id == self.bot.user.id):
            self.update_top_role_from_guild(member_after.guild)

    @commands.group(name="role",invoke_without_command=False)
    async def role(self, ctx):
        """Manages assignable roles"""

    @role.command(description='List roles')
    @commands.guild_only()
    async def list(self, ctx):
        guild = ctx.guild
        roles_list = []
        async with ctx.typing():
            roles_list = self.get_roles_list(guild)
        if len(roles_list):
            await ctx.send('```{}```'.format('\n'.join([role.name for role in roles_list])))
        else:
            await ctx.send('I couldn\'t find any roles!')

    @role.command(description='Add yourself to a role')
    @commands.guild_only()
    async def add(self, ctx, *, roles : str):
        guild = ctx.guild
        channel = ctx.channel
        user = ctx.author
        try:
            role_list = []
            changed = False
            async with channel.typing():
                role_list = self.role_inflator(guild, roles)
                if len(role_list):
                    await user.add_roles(*role_list)
                    changed = True
            if changed:
                await channel.send('I added {} to {}!'.format(
                  user.name, ','.join([role.name for role in role_list])
                  ))
            else:
                await channel.send('i don\'t know what you mean!')
        except Forbidden as e:
            await channel.send('I\'m not allowed to add that role!')

    @role.command(description='Remove yourself from a role')
    @commands.guild_only()
    async def remove(self, ctx, *, roles : str):
        guild = ctx.guild
        channel = ctx.channel
        user = ctx.author
        try:
            role_list = []
            changed = False
            async with channel.typing():
                role_list = self.role_inflator(guild, roles)
                if len(role_list):
                    await user.remove_roles(*role_list)
                    changed = True
            if changed:
                await channel.send('I removed {} from {}!'.format(
                  user.name, ','.join([role.name for role in role_list])
                  ))
            else:
                await channel.send('i don\'t know what you mean!')
        except Forbidden as e:
            await channel.send('I\'m not allowed to remove that role!')

    def get_roles_list(self, guild):
        roles_list = []
        if guild.id not in self.top_roles:
            self.update_top_role_from_guild(guild)
        top_role = self.top_roles[guild.id]

        for role in guild.roles:
            if role.id == guild.default_role.id:
                continue
            if(role < top_role):
                roles_list.append(role)
        roles_list.sort()
        return roles_list

    def update_top_role_from_guild(self, guild):
        """Updates the top role for a guild"""
        top_role = guild.me.top_role
        self.top_roles[guild.id] = top_role

    def role_inflator(self, guild, roles_string):
        """Takes a list of roles as a string and returns a list of Role objects"""
        guild_roles = self.get_roles_list(guild)
        results = []
        roles = map(str.strip, roles_string.split(','))
        for role in roles:
            for guild_role in guild_roles:
                if guild_role.id == guild.default_role.id:
                    continue
                if(role.casefold() == guild_role.name.casefold()):
                    results.append(guild_role)
        return results

