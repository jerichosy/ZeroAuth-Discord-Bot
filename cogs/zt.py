import discord
from discord import app_commands
from discord.ext import commands

import config


class ZT(commands.GroupCog, name="zt"):
    def __init__(self, bot):
        self.bot = bot

    # TODO: Make sure this cog is only usable in guilds

    @app_commands.command()
    async def listnetworks(self, interaction: discord.Interaction):
        """Show the joinable ZeroTier networks"""
        joinable_networks = [f"- {network['name']} (ID: `{network['id']}`)" for network in config.joinable_networks]
        await interaction.response.send_message("Joinable ZeroTier networks:\n" + "\n".join(joinable_networks))


async def setup(bot):
    await bot.add_cog(ZT(bot))
