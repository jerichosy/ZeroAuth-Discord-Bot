import logging
import traceback
from datetime import datetime
from pprint import pformat
from typing import List, NamedTuple

import discord
from discord import app_commands
from discord.ext import commands

import config

log = logging.getLogger(__name__)


class JoinableNetwork(NamedTuple):
    name: str
    network_id: str

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.network_id})"

    @property
    def markdown(self) -> str:
        return f"{self.name} (ID: `{self.network_id}`)"


class ZT(commands.GroupCog, name="zt"):
    def __init__(self, bot):
        self.bot = bot
        self.joinable_networks = [JoinableNetwork(**network) for network in config.joinable_networks]

    def get_network_by_id(self, id_to_find):
        return next((network for network in self.joinable_networks if network.network_id == id_to_find), None)

    @app_commands.command()
    async def listnetworks(self, interaction: discord.Interaction):
        """Show the joinable ZeroTier networks"""
        joinable_networks_formatted = [f"- {network.markdown}" for network in self.joinable_networks]
        await interaction.response.send_message("Joinable ZeroTier networks:\n" + "\n".join(joinable_networks_formatted))

    async def network_id_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=str(network), value=network.network_id)
            for network in self.joinable_networks
            if current.lower() in str(network).lower()
        ]

    @app_commands.command()
    @app_commands.autocomplete(network_id=network_id_autocomplete)
    @app_commands.describe(
        network_id="The ZeroTier network you joined",
        member_id='Your ZeroTier address. You can find this in System Tray ➔ ZeroTier ➔ "My Address"',
    )
    async def auth(
        self,
        interaction: discord.Interaction,
        network_id: app_commands.Range[str, 16, 16],
        member_id: app_commands.Range[str, 10, 10],
    ):
        """Authorize yourself on the ZeroTier network"""
        # NOTE: This does leak memberIds to other members in the Discord server. We can avoid this by using a modal.
        # ? If we allow admins to auth members through here instead of the ZT Ctrl, add a name arg to the coommand.
        #   We must also maintain a list of admins's Discord IDs in the config file.
        # * Test for invalid inputs (if possible) if changing input strategy

        # https://docs.zerotier.com/api/central/v1/#tag/network-member/operation/getNetworkMember

        log.info(
            f"Received auth req from {interaction.user.name} ({interaction.user.id}) on network {network_id} with {member_id}"
        )

        if not self.get_network_by_id(network_id):
            log.error("User-specified network ID is not in list of joinable networks")
            return await interaction.response.send_message(
                "🛑 Please enter a network ID from the list of joinable ZeroTier networks."
            )

        await interaction.response.defer()

        api_url = config.zt_ctrl_api_url
        # The format of the auth headers is seen here: https://docs.zerotier.com/api/central/examples/
        headers = {"Authorization": f"token {config.zt_ctrl_api_token}"}
        payload = {
            "name": f"{interaction.user.name}-{member_id}",
            "config": {
                "authorized": True,
            },
        }
        async with self.bot.session.post(
            f"{api_url}/network/{network_id}/member/{member_id}", headers=headers, json=payload
        ) as resp:
            log.info(f"Status: {resp.status} {resp.reason}")

            resp_json = await resp.json()

            # Important that we log for audit purposes
            pformat(resp_json)
            log.info(pformat(resp_json, sort_dicts=False))

            if resp.status == 200:  # ✅ checked and tested
                await interaction.followup.send("🟢 You have been authorized on the ZeroTier network.")
                await self.post_auth_webhook(
                    resp_json["name"],
                    member_id,
                    self.get_network_by_id(network_id),
                    interaction.user,
                    (await interaction.original_response()).jump_url,
                )
            elif resp.status == 401:  # ✅ checked and tested (triggers on invalid input)
                await interaction.followup.send(f"🔴 {resp_json["error"]}")
            elif resp.status == 429:  # ✅ checked
                # await interaction.followup.send("🔴 Too many requests. Please try again later.")
                await interaction.followup.send(f"🔴 {resp_json["error"]}")
            elif resp.status == 500:  # ✅ checked
                # await interaction.followup.send("🔴 Internal server error. Please try again later.")
                await interaction.followup.send(f"🔴 {resp_json["error"]}")
            else:  # ✅ checked and tested (triggers when payload is NOT passed as JSON)
                webhookmsg = await interaction.followup.send(
                    f"🔴 Unexpected error. **Please inform the admin of the following:**\n```\n{resp.status} {resp.reason}\n{resp_json["error"]}\n```"
                )
                await webhookmsg.delete(delay=10)

    async def post_auth_webhook(self, name, address, network, member: discord.Member, url):
        try:
            # Set up Webhook
            webhook = discord.Webhook.from_url(config.webhook_url, client=self.bot)

            # Create embed
            embed = discord.Embed(
                title="Self Member Authorization",
                description=f"{member.mention} has authorized **{name}** on the **{network}** network using this bot.",
                color=0x00FF00,
                timestamp=datetime.now(),
            )

            # Add fields
            embed.add_field(name="Name", value=name, inline=True)
            embed.add_field(name="ID/Address", value=address, inline=True)
            embed.add_field(name="Network", value=network, inline=True)

            embed.set_author(name=member.name, icon_url=member.avatar.url, url=url)

            # Send the embed using the webhook
            await webhook.send(embed=embed)
        except BaseException:
            log.error(f"Failed to send audit log webhook for self-auth of {name} ({address})")
            log.error(traceback.format_exc())
        else:
            log.info(f"Sent audit log webhook for self-auth of {name} ({address})")


async def setup(bot):
    await bot.add_cog(ZT(bot))
