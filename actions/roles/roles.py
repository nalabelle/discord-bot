import sys,os,traceback
import asyncio
import discord
from discord.ext import commands
from discord import Forbidden

class Roles:
    """ Role commands """

    def __init__(self, bot):
        self.bot = bot
        self.top_roles = dict()

    @asyncio.coroutine
    def on_ready(self):
        for server in self.bot.servers:
            self.update_top_role(server)

    @asyncio.coroutine
    def on_server_role_create(self, role):
        self.update_top_role(role.server)

    @asyncio.coroutine
    def on_server_role_delete(self, role):
        self.update_top_role(role.server)

    @asyncio.coroutine
    def on_server_role_update(self, role_before, role_after):
        self.update_top_role(role_after.server)

    @asyncio.coroutine
    def on_member_update(self, member_before, member_after):
        if(member_after.id == self.bot.user.id):
            self.update_top_role(member_after.server)

    def update_top_role(self, server):
        """Updates the bot's top role for a server"""
        self.top_roles[server.id] = server.me.top_role

    def role_inflator(self, server, roles_string):
        """Takes a list of roles as a string and returns a list of Role objects"""
        server_roles = server.roles
        results = []
        roles = map(str.strip, roles_string.split(','))
        for role in roles:
            for server_role in server_roles:
                if server_role.is_everyone:
                    continue
                if(role.casefold() == server_role.name.casefold()):
                    results.append(server_role)
        return results

    @commands.group(name="role",invoke_without_command=False)
    @asyncio.coroutine
    def role(self):
        """Manages assignable roles"""
    
    @role.command(pass_context=True,description='List roles')
    @asyncio.coroutine
    def list(self, ctx):
        user = ctx.message.author
        server = ctx.message.server
        channel = ctx.message.channel
        try:
            if server is None or user is None:
                return
            yield from self.bot.send_typing(channel)
            roles_list = []
            for role in server.roles:
                if role.is_everyone:
                    continue
                if(role <= self.top_roles[server.id]):
                    roles_list.append(role)
            if len(roles_list):
                yield from self.bot.say('```{}```'.format('\n'.join([role.name for role in roles_list])))
        except Exception as e:
            yield from self.bot.say('I broke! 😭 {}'.format(str(e)))
            pass

    @role.command(pass_context=True,description='Add yourself to a role')
    @asyncio.coroutine
    def add(self, ctx, *, roles : str):
        user = ctx.message.author
        server = ctx.message.server
        channel = ctx.message.channel
        try:
            if server is None or user is None:
                return
            role_list = self.role_inflator(server, roles)
            if len(role_list):
                yield from self.bot.send_typing(channel)
                yield from self.bot.add_roles(user, *role_list)
                yield from self.bot.say('I added {} to {}!'.format(user.name, ','.join([role.name for role in role_list])))
            else:
                yield from self.bot.say('i don\'t know what you mean!')
        except Forbidden as e:
            yield from self.bot.say('I\'m not allowed to add that role!')
            pass
        except Exception as e:
            yield from self.bot.say('I broke! 😭 {}'.format(str(e)))
            pass

    @role.command(pass_context=True,description='Remove yourself from a role')
    @asyncio.coroutine
    def remove(self, ctx, *, roles : str):
        user = ctx.message.author
        server = ctx.message.server
        channel = ctx.message.channel
        try:
            if server is None or user is None:
                return
            role_list = self.role_inflator(server, roles)
            if len(role_list):
                yield from self.bot.send_typing(channel)
                yield from self.bot.remove_roles(user, *role_list)
                yield from self.bot.say('I removed {} from {}!'.format(user.name, ','.join([role.name for role in role_list])))
            else:
                yield from self.bot.say('i don\'t know what you mean!')
        except Forbidden as e:
            yield from self.bot.say('I\'m not allowed to remove that role!')
            pass
        except Exception as e:
            yield from self.bot.say('I broke! 😭 {}'.format(str(e)))
            pass

