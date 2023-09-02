import discord
from discord.ext import commands
import sqlite3
import math
import json
import time

conn = sqlite3.connect('economy.db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS apuestas (id INTEGER PRIMARY KEY, titulo TEXT, descripcion TEXT, opciones TEXT, estado INTEGER DEFAULT 0)')

def obtener_monedas(usuario):
    cur.execute("SELECT balance FROM users WHERE user_id = ?", (usuario,))
    monedas_obtenidas = cur.fetchone()
    balance = monedas_obtenidas[0]
    monedas_obtenidas = balance
    return monedas_obtenidas
    

def guardar_monedas(usuario, moneditas, apuesta, opcion, cantidad):
    cur.execute("UPDATE users SET balance = ? WHERE user_id = ?", (moneditas, usuario))
    conn.commit()


class Apuestas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.apuestas = {}
    
    # comando para crear una nueva apuesta
    @commands.command()
    async def crear_apuesta(self, ctx, titulo, descripcion, *opciones):
        opciones = list(opciones)
        if len(opciones) < 2 or len(opciones) > 20:
            await ctx.send("Debe haber entre 2 y 20 opciones.")
            return
        self.apuestas[ctx.channel.id] = {"titulo": titulo, "descripcion": descripcion, "opciones": opciones, "apuestas": {}}
        mensaje = f"Se ha creado una nueva apuesta: **{titulo}**\n{descripcion}\n\nOpciones:\n"
        for i, opcion in enumerate(opciones):
            mensaje += f"{i+1}. {opcion}\n"
        mensaje += "\nPara apostar, usa el comando !apostar."
        await ctx.send(mensaje)
    
    # comando para mostrar la apuesta actual
    @commands.command()
    async def apuesta_actual(self, ctx):
        if ctx.channel.id not in self.apuestas:
            await ctx.send("No hay ninguna apuesta en curso.")
            return
        apuesta = self.apuestas[ctx.channel.id]
        mensaje = f"Apuesta actual: **{apuesta['titulo']}**\n{apuesta['descripcion']}\n\nOpciones:\n"
        for i, opcion in enumerate(apuesta['opciones']):
          mensaje += f"{i+1}. {opcion}: {apuesta['apuestas'].get(i, 0)} monedas\n"
        mensaje += "\nPara apostar, usa el comando !apostar."
        await ctx.send(mensaje)

    
    # comando para hacer una apuesta
    @commands.command()
    async def apostar(self, ctx, opcion: int, cantidad: int):
        if ctx.channel.id not in self.apuestas:
            await ctx.send("No hay ninguna apuesta en curso.")
            return

        apuesta = self.apuestas[ctx.channel.id]

        if opcion < 1 or opcion > len(apuesta["opciones"]):
            await ctx.send("La opción seleccionada no es válida.")
            return
        opcion = opcion - 1

        if cantidad < 1:
            await ctx.send("La cantidad apostada debe ser mayor a 0.")
            return
        usuario = str(ctx.author.id)
        monedas = obtener_monedas(usuario) # función que devuelve las monedas del usuario
        if cantidad > monedas:
            await ctx.send("No tienes suficientes monedas.")
            return
        apuesta['apuestas'][opcion] = cantidad
        moneditas = monedas - cantidad
        guardar_monedas(usuario, moneditas, apuesta, opcion, cantidad) # función que guarda las monedas del usuario

        #self.apuestas[ctx.channel.id] = apuesta['apuestas'].get(opcion, cantidad)
      
        await ctx.send(f"Has apostado {cantidad} monedas a la opción **{apuesta['opciones'][opcion]}**.")

    
    @commands.command(name="fin_apuesta")
    async def fin_apuesta(self, ctx, opcion):
        apuesta = self.apuestas[ctx.channel.id]
        if apuesta is None:
          await ctx.send("No hay una apuesta activa en este canal.")
          return
    
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("Solo un administrador puede finalizar una apuesta.")
            return
    
        if opcion not in apuesta["opciones"]:
            await ctx.send("La opción especificada no es válida para esta apuesta.")
            return
    
        # Obtener el total de dinero apostado en la apuesta
        total_apostado = sum(apuesta["opciones"][opcion]["apostado"] for opcion in apuesta["opciones"])
    
        # Obtener el total apostado en la opción ganadora
        total_ganadora = apuesta["opciones"][ganadora]["apostado"]
    
        # Calcular el porcentaje de la casa (5%)
        porcentaje_casa = int(total_apostado * 0.05)
    
        # Calcular el total a repartir entre los ganadores
        total_premio = total_apostado - porcentaje_casa
    
        # Calcular la proporción para repartir entre los ganadores
        if total_ganadora == 0:
            proporciones = {opcion: 0 for opcion in apuesta["opciones"]}
        else:
            proporciones = {opcion: apuesta["opciones"][opcion]["apostado"] / total_ganadora for opcion in apuesta["opciones"]}
    
        # Calcular el dinero a repartir entre los ganadores
        premios = {opcion: int(proporciones[opcion] * total_premio) for opcion in apuesta["opciones"]}
    
        # Añadir el porcentaje de la casa al bot
        self.dinero_bot += porcentaje_casa
    
        # Repartir el dinero a los ganadores
        for opcion, premio in premios.items():
            if opcion == ganadora:
                for usuario, dinero in apuesta["opciones"][opcion]["apostadores"].items():
                    self.dinero_usuarios[usuario] += dinero + premio
            else:
                for usuario, dinero in apuesta["opciones"][opcion]["apostadores"].items():
                    self.dinero_usuarios[usuario] += dinero
    
        # Eliminar la apuesta activa
        del self.apuestas_activas[ctx.channel.id]
    
        await ctx.send(f"La opción ganadora ha sido {ganadora}. Se han repartido {total_premio} {self.nombre_moneda} entre los ganadores.")

    @commands.command(name="borrar_apuesta")
    async def borrar_apuesta(self, ctx):
        cur.execute("SELECT id FROM apuestas WHERE estado = 0")
        result = cur.fetchone()
        if result is None:
            await ctx.send("No hay ninguna apuesta en curso.")
        else:
            id = result[0]
            cur.execute("DELETE FROM apuestas WHERE id = ?", (id,))
            cur.execute("DELETE FROM apuestas_usuarios WHERE apuesta_id = ?", (id,))
            conn.commit()
            await ctx.send("La apuesta en curso ha sido eliminada.")
    
def setup(bot):
    bot.add_cog(Apuestas(bot))