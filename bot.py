import logging

import discord
from discord.ext import commands

import config

log = logging.getLogger(__name__)

initial_extensions = ("cogs.meta",)


class ZeroAuth(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.dm_messages = False  # ! TODO: Make sure to disable interactions in DMs as well.
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)

        self.client_id: str = config.client_id

    async def setup_hook(self) -> None:
        log.info("--SETUP HOOK--")

        # self.session = aiohttp.ClientSession()

        self.invite_url = discord.utils.oauth_url(self.client_id)
        log.info(f"Invite URL: {self.invite_url}")

        for extension in initial_extensions:
            try:
                await self.load_extension(extension)
            except Exception as e:
                log.exception("Failed to load extension %s.", extension)

    async def on_ready(self):
        log.info(f"Logged in as {self.user} (ID: {self.user.id})")
        log.info("------")


bot = ZeroAuth()


if config.debug:

    @bot.event
    async def on_message(message: discord.Message) -> None:
        if message.author.bot or message.author == bot.user:
            return

        print(f"{message.author}: {message.content}")

        await bot.process_commands(message)


bot.run(config.token, root_logger=True)