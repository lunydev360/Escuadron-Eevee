import io
import json
import random
from pathlib import Path

import discord
from discord.ext import commands
from easy_pil import Editor, Font, load_image_async

import config

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
WELCOME_FILE = DATA_DIR / "welcome.json"


def load_welcome_images_from_file() -> list[str]:
    try:
        with WELCOME_FILE.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    if isinstance(data, dict):
        return [value for value in data.values() if isinstance(value, str)]
    return []


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_welcome_channel(self) -> discord.TextChannel | None:
        channel = self.bot.get_channel(config.channel_welcome)
        return channel if isinstance(channel, discord.TextChannel) else None

    async def get_welcome_images(self) -> list[str]:
        post_id = getattr(config, "channel_welcome_forum_post", None)
        if post_id:
            try:
                post = self.bot.get_channel(post_id)
                if post is None:
                    post = await self.bot.fetch_channel(post_id)

                images: list[str] = []
                if isinstance(post, discord.Thread):
                    history = post.history(limit=50)
                    async for message in history:
                        for attachment in message.attachments:
                            if attachment.content_type and "image" in attachment.content_type:
                                images.append(attachment.url)
                elif isinstance(post, discord.abc.Messageable):
                    history = post.history(limit=50)
                    async for message in history:
                        for attachment in message.attachments:
                            if attachment.content_type and "image" in attachment.content_type:
                                images.append(attachment.url)

                if images:
                    return images
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass

        return load_welcome_images_from_file()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        channel = self.get_welcome_channel()
        if channel is None:
            return

        images = await self.get_welcome_images()
        imagen_url = random.choice(images) if images else "https://images.unsplash.com/photo-1517849845537-4d257902454a"

        try:
            background_image = await load_image_async(imagen_url)
        except Exception:
            background_image = await load_image_async("https://images.unsplash.com/photo-1517849845537-4d257902454a")

        background = Editor(background_image).resize((800, 400))
        profile_imagen = await load_image_async(str(member.avatar.url if member.avatar else member.default_avatar.url))

        profile = Editor(profile_imagen).resize((150, 150)).circle_image()
        poppins = Font.poppins(size=50, variant="bold")
        poppins_small = Font.poppins(size=20, variant="light")

        background.paste(profile, (325, 90))
        background.ellipse((325, 90), 150, 150, outline="black", stroke_width=5)

        background.text(
            (400, 260),
            f"BIENVENIDO a {member.guild.name}",
            color="black",
            font=poppins,
            align="center",
            stroke_width=2,
            stroke_fill="white",
        )
        background.text(
            (400, 325),
            "que alegria verte por aca",
            color="black",
            font=poppins_small,
            align="center",
            stroke_width=2,
            stroke_fill="white",
        )

        file = discord.File(background.image_bytes, filename="welcome2.jpg")
        await channel.send(f"hola {member.mention} recuerda visitar <#{config.channel_rule}>")
        await channel.send(file=file)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Welcome(bot))
