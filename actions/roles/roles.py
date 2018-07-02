import sys,os,traceback
import asyncio
import discord
from discord.ext import commands
from discord import Forbidden

class Roles:
    """ Role commands """

    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(pass_context=True,description='Add yourself to a role')
    @asyncio.coroutine
    def addme(self, ctx, *, roles : str):
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

    @commands.command(pass_context=True,description='Remove yourself from a role')
    @asyncio.coroutine
    def removeme(self, ctx, *, roles : str):
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

