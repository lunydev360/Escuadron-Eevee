import logging
import os
import random
from pathlib import Path

import webserver
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import config

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("COMMAND_PREFIX", "!")
GUILD = discord.Object(id=config.guild)

if not TOKEN:
    raise RuntimeError("Falta DISCORD_TOKEN en el archivo .env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=commands.DefaultHelpCommand(no_category="Comandos"),
        )

    async def setup_hook(self) -> None:
        cogs_path = Path(__file__).parent / "cogs"

        for file in cogs_path.glob("*.py"):
            if file.name.startswith("_"):
                continue

            extension = f"cogs.{file.stem}"
            await self.load_extension(extension)
            logging.info("Cog cargado: %s", extension)

        self.tree.copy_global_to(guild=GUILD)
        synced_commands = await self.tree.sync(guild=GUILD)
        logging.info(
            "Comandos sincronizados en el guild %s: %s",
            config.guild,
            len(synced_commands),
        )

    async def on_ready(self) -> None:
        if self.user is not None:
            logging.info("Conectado como %s (ID: %s)", self.user, self.user.id)

        if not self.status_task.is_running():
            self.status_task.start()

    @tasks.loop(minutes=0.15)
    async def status_task(self) -> None:
        await self.change_presence(
            activity=discord.Game(name=random.choice(config.activity))
        )

    @status_task.before_loop
    async def before_status_task(self) -> None:
        await self.wait_until_ready()


bot = DiscordBot()
webserver.keep_alive()
bot.run(TOKEN, reconnect=True)
