import discord
from discord.ext import commands
import requests

class Wiki(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
      

    @commands.command(
      name = 'wikibuscar',
      aliases = ['wiki','wb']
    )
    async def wikibuscar(self, ctx, query):
        # Establecer los parámetros para la búsqueda
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srprop": "size",
            "utf8": 1,
            "formatversion": 2,
            "origin": "*"
        }

        # Hacer una petición GET a la API de Fandom con los parámetros de búsqueda
        response = requests.get("https://miztlan.fandom.com/es/api.php?action=query&format=json&list=search&utf8=1&srsearch=" + query.replace(" ", "_"), params=params)

        # Verificar si la respuesta es exitosa
        if response.status_code == 200:
            # Obtener los resultados de la búsqueda en formato JSON
            data = response.json()

            # Extraer el título del primer resultado de búsqueda
            title = data["query"]["search"][0]["title"]

            # Construir la URL de la página de la wiki
            wiki_url = f"https://miztlan.fandom.com/es/wiki/{title.replace(' ', '_')}"

            # Enviar la URL de la página de la wiki al canal de Discord
            await ctx.send(wiki_url)
        else:
            # Si la respuesta no es exitosa, enviar un mensaje de error al canal de Discord
            await ctx.send('Error en la búsqueda.')

def setup(bot):
    bot.add_cog(Wiki(bot))
