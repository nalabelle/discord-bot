"""
Cog for Role Command
"""

from __future__ import annotations

import logging

import discord
from discord import Forbidden, app_commands, ui

log = logging.getLogger("Role")


def allowed_roles(guild: discord.Guild):
    """Common Role List"""
    top_bot_role = guild.me.top_role
    roles = [
        r
        for r in guild.roles
        if r != guild.default_role and r != guild.premium_subscriber_role and r < top_bot_role
    ]
    roles.sort(key=lambda r: r.name)
    return roles


class RoleAddSelect(ui.Select):
    """Role Add Selection UI Component"""

    def __init__(self, options):
        super().__init__(
            placeholder="Select a role", custom_id="role_add_select", options=options, max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        role_id = self.values[0]
        role = interaction.guild.get_role(int(role_id))
        try:
            await interaction.user.add_roles(role)
        except Forbidden:
            await interaction.response.send_message(
                "I'm not allowed to add that role!", ephemeral=True
            )
            return
        await interaction.response.send_message(
            f"I added {interaction.user.nick} to {role.name}!", ephemeral=True
        )


class RoleRemoveSelect(ui.Select):
    """Role Remove Selection UI Component"""

    def __init__(self, options):
        super().__init__(
            placeholder="Select a role",
            custom_id="role_remove_select",
            options=options,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        role_id = self.values[0]
        role = interaction.guild.get_role(int(role_id))
        try:
            await interaction.user.remove_roles(role)
        except Forbidden:
            await interaction.response.send_message(
                "I'm not allowed to remove that role!", ephemeral=True
            )
            return
        await interaction.response.send_message(
            f"I removed {interaction.user.nick} from {role.name}!", ephemeral=True
        )


class RoleView(ui.View):
    """View Component for Role Selection"""

    def __init__(self):
        super().__init__()

    @classmethod
    def role_add(cls, interaction: discord.Interaction) -> ui.View:
        """Menu for selecting roles to add"""
        roles = [r for r in allowed_roles(interaction.guild) if r not in interaction.user.roles]
        if not roles:
            raise ValueError("I couldn't find any roles to add")
        options = [discord.SelectOption(label=role.name, value=role.id) for role in roles]
        select = RoleAddSelect(options=options)
        view = cls()
        view.add_item(select)
        return view

    @classmethod
    def role_remove(cls, interaction: discord.Interaction) -> ui.View:
        """Menu for selecting roles to remove"""
        roles = [r for r in allowed_roles(interaction.guild) if r in interaction.user.roles]
        if not roles:
            raise ValueError("I couldn't find any roles to remove")
        options = [discord.SelectOption(label=role.name, value=role.id) for role in roles]
        select = RoleRemoveSelect(options=options)
        view = cls()
        view.add_item(select)
        return view


@app_commands.guild_only()
class RoleCommand(app_commands.Group, name="role"):
    """Role commands"""

    @app_commands.command()
    async def list(self, interaction: discord.Interaction) -> None:
        """List Roles"""
        roles = allowed_roles(interaction.guild)
        if roles:
            await interaction.response.send_message(
                "```{}```".format("\n".join([r.name for r in roles]))
            )
        else:
            await interaction.response.send_message("I couldn't find any roles!")

    @app_commands.command()
    async def add(self, interaction: discord.Interaction) -> None:
        """Add a role to your account"""
        try:
            await interaction.response.send_message(
                view=RoleView.role_add(interaction), ephemeral=True
            )
        except ValueError as err:
            await interaction.response.send_message(content=str(err), ephemeral=True)

    @app_commands.command()
    async def remove(self, interaction: discord.Interaction) -> None:
        """Remove a role from your account"""
        try:
            await interaction.response.send_message(
                view=RoleView.role_remove(interaction), ephemeral=True
            )
        except ValueError as err:
            await interaction.response.send_message(content=str(err), ephemeral=True)


async def setup(bot):
    """Cog creation"""
    bot.tree.add_command(RoleCommand())


async def teardown(bot):
    """Cog teardown"""
    bot.tree.remove_command("role")
