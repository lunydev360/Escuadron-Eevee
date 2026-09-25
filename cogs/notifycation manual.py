import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal

import random
import json
import config
guild = discord.Object(id=config.guild)

def load_config():
    with open('data/config.json','r') as f:
        return json.load(f)

class Avisos(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    def get_channel_notf(self):
        return self.bot.get_channel(config.channel_anuncio)

    @commands.has_permissions(administrator=True)
    @app_commands.command(name="anuncio",description="publica un anuncio ala comunidad")
    @app_commands.guilds(guild)
    @app_commands.describe(title="agrega un titulo al anuncio para la comunidad",mensaje="escribe un mensaje de anuncio",options="option1, option2,...")
    async def anuncio(self,interaction: discord.Interaction,mensaje:str,title:Optional[str],options:Optional[str]):
        channel = self.get_channel_notf()
        titulo = " "
        if title:
            titulo = title
        else:
            titulo = random.choice(config.m_info_server)
        emend = discord.Embed(title=titulo,
                              description=mensaje,
                              color=discord.Color.random())
        if options:
            opciones_lista = [op.strip() for op in options.split(',') if op.strip()]
            for i, option in enumerate(opciones_lista):
                emend.add_field(name=f"{int(i)+1}# {option}",value=" ",inline=False)
        emend.set_thumbnail(url= "https://cdn.discordapp.com/attachments/1450712562961481811/1450715169310244914/5_sin_titulo_20251216230402.png?ex=69438b49&is=694239c9&hm=891ab329d6910e395808592073d99ef659393147c4f32477d08f9a3540377391&")
        emend.set_image(url="https://cdn.discordapp.com/attachments/1450712562961481811/1450712820789416047/linea-imagen-animada-0015.gif?ex=69438919&is=69423799&hm=03d0f7b3698c0dbef965438d93efe579b0f50c46d10160ca0d3428a17d9201d5&")
        emend.set_footer(text="opine de la informacion (su opinion nos imnporta mucho para mejorar)")

        get_message = await channel.send(embed=emend)
        reaction = ["✅","🫤","❌"]
        for i in range(len(reaction)):
            await get_message.add_reaction(reaction[i])
        await interaction.response.send_message("la informacion a sido enviada con exito")
    
    
async def setup(bot: commands.Bot):
    await bot.add_cog(Avisos(bot))