import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from collections import Counter
from typing import Optional
import json
import config
guild = discord.Object(id=config.guild)

def load_config():
    with open('data/config.json','r') as f:
        return json.load(f)

class Encuentas(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_channel_ecn(self):
        return self.bot.get_channel(config.channel_anuncio)

    @commands.has_permissions(administrator=True)
    @app_commands.command(name="encuesta",description="das una encuesta al server")
    @app_commands.guilds(guild)
    @app_commands.describe(tiempo="arriba de 0",pregunta="text",options="option1,option2,...",image="url de imagen")
    async def encuesta(self,interaction:discord.Interaction,tiempo:int,pregunta:str,options:str,image:Optional[str]):
        opciones = [op.strip() for op in options.split(',') if op.strip()]
        channel = self.get_channel_ecn()
        if tiempo <= 0:
            await interaction.response.send_message("El tiempo debe ser mayor que cero.")
            return

        if len(opciones) > 10:
            await interaction.response.send_message("No puedes tener más de 10 opciones.")
            return
    
        if len(opciones) < 2:
            await interaction.response.send_message("Debes proporcionar al menos dos opciones.")
            return
    
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        if len(opciones) > len(emojis):
            await interaction.response.send_message("No hay suficientes emojis definidos para tantas opciones.")
            return

        descripcion = f"**{pregunta}**\n\n"
        for i, opcion in enumerate(opciones):
            descripcion += f"{emojis[i]}: {opcion}\n"
        descripcion += f"\n*La encuesta finalizará en {tiempo} minutos.*"

        embed = discord.Embed(title="📊 votacion del server", description=descripcion, color=discord.Color.purple())
        if image:
            embed.set_image(image)
        mensaje_encuesta = await channel.send(embed=embed)

        for i in range(len(opciones)):
            await mensaje_encuesta.add_reaction(emojis[i])
        
        await asyncio.sleep(tiempo * 60)
        mensaje_actualizado = await channel.fetch_message(mensaje_encuesta.id)
        votos = Counter()
        for reaccion in mensaje_actualizado.reactions:
            if str(reaccion.emoji) in emojis[:len(opciones)]:
                # Contar votos, restando el voto del bot si es necesario
                votos[str(reaccion.emoji)] = reaccion.count - 1 

        # Determinar el resultado
        if votos:
            ganador_emoji = max(votos, key=votos.get)
            ganador_opcion = opciones[emojis.index(ganador_emoji)]
            resultados_desc = "Resultados:\n"
            for emoji, count in votos.items():
                opcion_texto = opciones[emojis.index(emoji)]
                resultados_desc += f"{emoji} {opcion_texto}: {count} votos\n"
            
            embed_resultados = discord.Embed(title="votacion cerrada", description=resultados_desc, color=discord.Color.green())
            embed_resultados.add_field(name="voto ganador", value=f"{ganador_emoji} {ganador_opcion} con {votos[ganador_emoji]} votos.")
        else:
            embed_resultados = discord.Embed(title="Encuesta Finalizada", description="No se emitieron votos.", color=discord.Color.orange())

        await channel.send(embed=embed_resultados)




async def setup(bot: commands.Bot):
    await bot.add_cog(Encuentas(bot))