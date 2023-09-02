import discord
from discord.ext import commands

class Ayuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ayuda(self, ctx):

      embed = discord.Embed(title="Lista de comandos", description="Lista de comandos disponibles, su sintaxis y función de cada uno", color=0x00ff00)
      embed.add_field(name=f"!wikibuscar `nombre de la wiki`", value=f"_alias: \t wiki, wb_ \n Este comando te mostrará la primera wiki que coincida con tu búsqueda.", inline=False)
      embed.add_field(name=f"!construir `tipo` `producto` `nivel` `estado`", value=f"_alias: \t cons, fabri, fabrica_ \n Este comando es para inicar la construcción de una fábrica, granja o mina. Deberás poner el producto que producirá, el nivel y el estado donde se ubicará", inline=False)

      await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Ayuda(bot))