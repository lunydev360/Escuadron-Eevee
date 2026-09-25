import json
from pathlib import Path
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

import config


guild = discord.Object(id=config.guild)
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RULES_FILE = DATA_DIR / "rules.json"
CONFIG_FILE = DATA_DIR / "config.json"


def load_json(file: Path, default: dict) -> dict:
    try:
        with file.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
    except (FileNotFoundError, json.JSONDecodeError):
        data = default.copy()

    return data if isinstance(data, dict) else default.copy()


def save_json(file: Path, data: dict) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open("w", encoding="utf-8") as stream:
        json.dump(data, stream, indent=4, ensure_ascii=False)


def load_rules() -> dict:
    return load_json(RULES_FILE, {})


def load_config() -> dict:
    return load_json(CONFIG_FILE, {})


def save_config(data: dict) -> None:
    save_json(CONFIG_FILE, data)


def get_rules() -> discord.Embed:
    embed = discord.Embed(
        title="REGLAS DEL SERVER",
        description=" ",
        color=discord.Color.purple(),
    )
    rules = load_rules()

    if not rules:
        embed.description = "Todavía no hay reglas configuradas."

    for number, (rule_id, rule) in enumerate(rules.items(), start=1):
        embed.add_field(
            name=f"{number} # {rule.get('name', 'Sin nombre')}",
            value=f"[{rule_id}] {rule.get('description', 'Sin descripción')}",
            inline=False,
        )

    embed.set_image(url="https://cdn.discordapp.com/attachments/1450712651167436830/1450731531487150265/8_sin_titulo_20251217000854.png?ex=69439a86&is=69424906&hm=8fa783512f4051b29c14f2b07560bb2f76747facc2d65bd5aaea19864d6bae1a&")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1450712651167436830/1450731531772493834/5_sin_titulo_20251217000731.png?ex=69439a86&is=69424906&hm=a7b8a16666dd2d549082205a018d35d2eedb20e099574b417d6a205e3c8c250&")
    return embed


class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_channel_rul(self) -> discord.TextChannel | None:
        channel = self.bot.get_channel(config.channel_rule)
        return channel if isinstance(channel, discord.TextChannel) else None

    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="add_rule", description="Agrega una nueva regla")
    @app_commands.guilds(guild)
    @app_commands.describe(
        id="Identificador",
        name="Nombre de la regla",
        description="Descripción de la regla",
    )
    async def add_rule(
        self,
        interaction: discord.Interaction,
        id: str,
        name: str,
        description: Optional[str] = None,
    ) -> None:
        rules = load_rules()
        file_config = load_config()
        channel = self.get_channel_rul()

        if id in rules:
            await interaction.response.send_message(
                "Esa ID ya pertenece a una regla.", ephemeral=True
            )
            return

        if channel is None:
            await interaction.response.send_message(
                "No se encontró el canal de reglas configurado.", ephemeral=True
            )
            return

        rules[id] = {
            "name": name,
            "description": description or "Sin descripción",
        }
        save_json(RULES_FILE, rules)
        await self._replace_rules_message(channel, file_config)
        await interaction.response.send_message(
            "La regla se añadió correctamente.", ephemeral=True
        )

    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="remove_rule", description="Remueve una regla")
    @app_commands.guilds(guild)
    @app_commands.describe(id="ID de la regla")
    async def remove_rule(self, interaction: discord.Interaction, id: str) -> None:
        rules = load_rules()
        file_config = load_config()
        channel = self.get_channel_rul()

        if id not in rules:
            await interaction.response.send_message(
                "No existe una regla con esa ID.", ephemeral=True
            )
            return

        if channel is None:
            await interaction.response.send_message(
                "No se encontró el canal de reglas configurado.", ephemeral=True
            )
            return

        del rules[id]
        save_json(RULES_FILE, rules)
        await self._replace_rules_message(channel, file_config)
        await interaction.response.send_message(
            "La regla se eliminó correctamente.", ephemeral=True
        )

    async def _replace_rules_message(
        self,
        channel: discord.TextChannel,
        file_config: dict,
    ) -> None:
        message_id = file_config.get("rule_id")
        if message_id:
            try:
                old_message = await channel.fetch_message(message_id)
                await old_message.delete()
            except discord.NotFound:
                pass

        message = await channel.send(embed=get_rules())
        file_config["rule_id"] = message.id
        save_config(file_config)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Rules(bot))