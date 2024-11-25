import logging
from pprint import pformat

import discord
from discord import app_commands
from discord.ext import commands

import config

log = logging.getLogger(__name__)


class ZT(commands.GroupCog, name="zt"):
    def __init__(self, bot):
        self.bot = bot
        self.joinable_networks = config.joinable_networks

    # TODO: Make sure this cog is only usable in guilds

    @app_commands.command()
    async def listnetworks(self, interaction: discord.Interaction):
        """Show the joinable ZeroTier networks"""
        joinable_networks = [f"- {network['name']} (ID: `{network['id']}`)" for network in self.joinable_networks]
        await interaction.response.send_message("Joinable ZeroTier networks:\n" + "\n".join(joinable_networks))

    @app_commands.command()
    @app_commands.describe(
        network_id="The ZeroTier network you joined",
        member_id='Your ZeroTier address. You can find this in System Tray ➔ ZeroTier ➔ "My Address"',
    )
    async def auth(self, interaction: discord.Interaction, network_id: str, member_id: str):
        """Authorize yourself on the ZeroTier network"""
        # NOTE: This does leak memberIds to other members in the Discord server. We can avoid this by using a modal.
        # ? If we allow admins to auth members through here instead of ZTNET, add a name arg to the coommand.
        #   We must also maintain a list of admins's Discord IDs in the config file.
        # TODO: Test for invalid inputs (if possible) after finalizing input strategy

        # https://ztnet.network/Rest%20Api/Organization/Network-Members/modify-a-organization-network-member

        log.info(
            f"Received auth req from {interaction.user.name} ({interaction.user.id}) on network {network_id} with {member_id}"
        )

        await interaction.response.defer()

        api_url = config.ztnet_api_url
        orgid = config.ztnet_orgid
        headers = {"x-ztnet-auth": config.ztnet_api_token}
        payload = {"name": f"{interaction.user.name}-{member_id}", "authorized": True}
        async with self.bot.session.post(
            f"{api_url}/org/{orgid}/network/{network_id}/member/{member_id}", headers=headers, json=payload
        ) as resp:
            log.info(f"Status: {resp.status} {resp.reason}")

            resp_json = await resp.json()

            # Important that we log for audit purposes
            pformat(resp_json)
            log.info(pformat(resp_json, sort_dicts=False))

            if resp.status == 200:  # ✅ checked and tested
                await interaction.followup.send("🟢 You have been authorized on the ZeroTier network.")
            elif resp.status == 401:  # ✅ checked
                await interaction.followup.send(
                    # "🔴 Unauthorized. Your request has not been applied. **Please inform the admin of the error.**"
                    f"🔴 {resp_json["error"]} Your request has not been applied. **Please inform the admin of the error.**"
                )
            elif resp.status == 429:  # ✅ checked
                # await interaction.followup.send("🔴 Too many requests. Please try again later.")
                await interaction.followup.send(f"🔴 {resp_json["error"]}")
            elif resp.status == 500:  # ✅ checked
                await interaction.followup.send("🔴 Internal server error. Please try again later.")
            else:  # ✅ checked and tested
                webhookmsg = await interaction.followup.send(
                    f"🔴 Unexpected error. **Please inform the admin of the following:**\n```\n{resp.status} {resp.reason}\n{resp_json["error"]}\n```"
                )
                await webhookmsg.delete(delay=10)


async def setup(bot):
    await bot.add_cog(ZT(bot))
