import discord
from discord.ext import commands
from discord.ext.commands import MemberConverter
import sqlite3
import math
import json
import time
import random
import asyncio
from random import randint
from datetime import datetime, timedelta
from cogs.datos.fabricas import *
from cogs.datos.provincia import *
from cogs.datos.funciones import *

con = sqlite3.connect('economy.db')
cur = con.cursor()

### ID's y ente
# 1096469222147756112 = Ministerio Central
#
#


# Crea la tabla 'users' si no existe
cur.execute('''CREATE TABLE IF NOT EXISTS users (
               user_id INTEGER PRIMARY KEY,
               balance INTEGER DEFAULT 0
            )''')

class Economía(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.page_size = 10  # Cantidad de usuarios a mostrar por página
        self.conn = sqlite3.connect("economia.db", timeout=5.0)
        self.conn.execute("PRAGMA busy_timeout = 5000")
      
    # Comando para consultar el saldo actual
    #@bot.tree.command(name="cartera")
    @commands.command(name="cartera", aliases=["dinero", "banco", "cuenta", "bolsa", "bal", "bol"])
    async def cartera(self, ctx, usuario: discord.Member=None):
        if usuario is None:
            usuario = ctx.author
    
        embed = discord.Embed()
        embed.set_author(name=usuario.name, icon_url=usuario.avatar_url_as(size=32))
    
        cur.execute("SELECT balance FROM users WHERE user_id = ?", (usuario.id,))
        result = cur.fetchone()
    
        if result is None:
            await ctx.send(f"{usuario.mention}, aún no tienes una cuenta en el sistema de economía.")
        else:
            balance = result[0]
            embed.add_field(name="Saldo actual", value=str(balance))
            await ctx.send(embed=embed)
    

    # Comando para agregar dinero al saldo
    @commands.has_any_role('✧ Gran Administrador', '✧ Moderador Potente', 'Admin')
    @commands.command(name = "añadir_dinero", aliases = ["ad", "dard", "dar_dinero"])
    async def añadir_dinero(self, ctx, amount: int, usuario):
        if usuario is None:
          user_id = ctx.author.id
        user_id = usuario
        mención = f"<@{user_id}>"
        user = ctx.guild.get_member(user_id)
        if user is not None:
            await ctx.send("No se encontró ningún usuario con esa ID.")
            return
      
        cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = cur.fetchone()

        if result is None:
            cur.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, amount))
        else:
            balance = result[0]
            new_balance = balance + amount
            cur.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))

        con.commit()
        embed = discord.Embed()
        embed.add_field(name=f'Se ha dado dinero a {mención}.', value=f'Se ha añadido {amount} a la cuenta de {mención}.', inline=False)
        
        await ctx.send(embed = embed)

    # Comando para retirar dinero del saldo
    @commands.has_any_role('✧ Gran Administrador', '✧ Moderador Potente', 'Admin')
    @commands.command(name = "quitar_dinero", aliases = ["qd", "quitar_d"])
    async def quitar_dinero(self, ctx, amount: int, usuario):
        if usuario is None:
          user_id = ctx.author.id
        user_id = usuario
        cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = cur.fetchone()

        if result is None:
            await ctx.send("Aún no tienes una cuenta en el sistema de economía.")
        else:
            balance = result[0]

            if balance < amount:
                await ctx.send("No tienes suficientes monedas para realizar esta operación.")
            else:
                new_balance = balance - amount
                cur.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
                con.commit()
                await ctx.send(f"{amount} monedas han sido retiradas de tu cuenta.")
              
    @commands.command(name="top", aliases=["rango", "tabla", "tabla_de_líderes", "tl"])
    async def top(self, ctx, page=1):
        cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC")
        results = cur.fetchall()
    
        total_pages = math.ceil(len(results) / self.page_size)
        if page > total_pages or page < 1:
            await ctx.send(f"Página inválida. Introduce un número entre 1 y {total_pages}.")
            return
    
        start_index = (page - 1) * self.page_size
        end_index = start_index + self.page_size
        results = results[start_index:end_index]
    
        embed = discord.Embed(title="Tabla de ricos", description = "Lista completa con las personas más ricas del servidor", color=discord.Color.green())
        embed.set_thumbnail(url= "https://media.discordapp.net/attachments/1090005406648127610/1096632432662429708/pngtree-ppt-element-illustration-decoration-report-image_1256040.png")
        rank = (page - 1) * self.page_size + 1
        for result in results:
            user_id = result[0]
            balance = result[1]
            user = await self.bot.fetch_user(user_id)
            embed.add_field(name=f"", value=f"`{rank}`. {user.name} - {balance} dadarios", inline=False)
            rank += 1
    
        embed.set_footer(text=f"Página {page}/{total_pages}")
    
        message = await ctx.send(embed=embed)
        if total_pages > 1:
            await message.add_reaction("◀️")
            await message.add_reaction("▶️")
    
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
    
            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=300.0, check=check)
                except asyncio.TimeoutError:
                    await message.clear_reactions()
                    break
    
                if str(reaction.emoji) == "▶️" and page < total_pages:
                    page += 1
                    start_index = (page - 1) * self.page_size
                    end_index = start_index + self.page_size
                    results = results[start_index:end_index]
    
                elif str(reaction.emoji) == "◀️" and page > 1:
                    page -= 1
                    start_index = (page - 1) * self.page_size
                    end_index = start_index + self.page_size
                    results = results[start_index:end_index]
    
                embed.clear_fields()
                rank = (page - 1) * self.page_size + 1
                for result in results:
                    user_id = result[0]
                    balance = result[1]
                    user = await self.bot.fetch_user(user_id)
                    embed.add_field(name=f"", value=f"`{rank}`. {user.name} - {balance} dadarios", inline=False)
                    rank += 1
    
                embed.set_footer(text=f"Página {page}/{total_pages}")
                await message.edit(embed=embed)
                await message.remove_reaction(reaction, user)
    
    @commands.command(name = "trabajar", aliases = ["laburar", "trabajo", "tbj"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def trabajar(self, ctx):
        user_id = ctx.author.id
        mención = f"<@{user_id}>"

        # Asignando variables
        tipo = ['fábrica', 'granja', 'mina']
        dinero = randint(40, 70)
        trabajo = tipo[randint(0, len(tipo) - 1)]
        lugar_trabajo = estados[randint(0, len(estados) - 1)]
        estados_url = imagenes_estados[lugar_trabajo[0]]
        roles_valores = {"✧ Clase Baja-Baja": 1.05, "✧ Clase Baja-Alta": 1.1, "✧ Clase Media-Baja": 1.2, "✧ Clase Media-Alta": 1.3, "✧ Clase Alta-Baja": 1.45, "✧ Clase Alta-Alta": 1.7, "✧ Millonario": 2}

        # Multiplicador por nivel de rol
        multiplicador = 1
        for rol in ctx.author.roles:
            if rol.name in roles_valores:
                multiplicador = roles_valores[rol.name]
                break
        
        dinero *= multiplicador
        dinero = int(dinero)
    
        # Acá dará el dinero
        cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = cur.fetchone()
    
        if result is None:
            cur.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, dinero))
        else:
            balance = result[0]
            new_balance = balance + dinero
            cur.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    
        con.commit()

        # Mensaje de que trabajó el pibe
        embed = discord.Embed()
        embed.set_thumbnail(url=estados_url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url_as(size=32))
        embed.add_field(name = "", value = f"Trabajaste horario completo en una {trabajo} en **{lugar_trabajo[0]}**. Has ganado {dinero} dadarios.")
        await ctx.send(embed=embed)

    @commands.command(name="pagar", aliases=["dar", "regalar"])
    async def pagar(self, ctx, usuario: discord.Member, cantidad: int):
      user_id1 = ctx.author.id
      user_id2 = usuario.id
      cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id1,))
      result1 = cur.fetchone()
      cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id2,))
      result2 = cur.fetchone()
      cur.execute("SELECT balance FROM users WHERE user_id = ?", (1096469222147756112,))
      result3 = cur.fetchone()
  
      if result1 is None:
          await ctx.send("Aún no tienes una cuenta en el sistema de economía.")
      else:
          balance1 = result1[0]
  
          if balance1 < cantidad:
              await ctx.send("No tienes suficientes monedas para realizar esta operación.")
          else:
              impuesto = cantidad * 0.1
              new_balance1 = balance1 - cantidad
              new_balance2 = result2[0] + (cantidad - int(impuesto))
              new_balance3 = result3[0] + int(impuesto)
              cur.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance1, user_id1))
              cur.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance2, user_id2))
              cur.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance3, 'Ministerio Central'))
              con.commit()
              await ctx.send(f"Has pagado {cantidad} monedas a {usuario.mention}. El Ministerio Central ha cobrado un impuesto del 10% ({int(impuesto)} monedas).")


    @commands.command()
    async def purga_de_la_totalidad(self, ctx):
        async def purga_final(ctx):
            try:
                cur.execute("DELETE FROM users")
                conn.commit()
                await ctx.send("¡Todos los usuarios han sido eliminados de la base de datos!")
            except Exception as e:
                await ctx.send(f"No se pudo eliminar a todos los usuarios: {e}")
        
        await confirmación_de_comando(ctx, '¿Está seguro de que desea eliminar toda la economía?', purga_final)

    

class ChatDinero(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}
        self.reward = 100
        self.cooldown_time = 5
        self.database_file = "database.json"
        self.load_database()

    def load_database(self):
        try:
            with open(self.database_file, "r") as f:
                self.database = json.load(f)
        except FileNotFoundError:
            self.database = {}

    def save_database(self):
        with open(self.database_file, "w") as f:
            json.dump(self.database, f)

    def add_balance(self, user_id, amount):
        if user_id not in self.database:
            self.database[user_id] = {"balance": 0}
        self.database[user_id]["balance"] += amount

    def get_balance(self, user_id):
        if user_id not in self.database:
            self.database[user_id] = {"balance": 0}
        return self.database[user_id]["balance"]

    def is_on_cooldown(self, user_id):
        return user_id in self.cooldowns and time.time() < self.cooldowns[user_id]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        author_id = str(message.author.id)
        if self.is_on_cooldown(author_id):
            return

        self.add_balance(author_id, self.reward)
        self.save_database()

        self.cooldowns[author_id] = time.time() + self.cooldown_time

    @commands.has_any_role('Admin')
    @commands.command()
    async def crear_cuentas(self, ctx):
      # Obtiene la lista de usuarios del servidor
      users = ctx.guild.members
      
      # Recorre la lista de usuarios y les asigna una cuenta con 50 de dinero
      for user in users:
          # Comprueba que el usuario no sea un bot
          if not user.bot:
              # Verifica si el usuario ya tiene una cuenta
              cur.execute("SELECT balance FROM users WHERE user_id=?", (user.id,))
              result = cur.fetchone()
              if result is None:
                  # Si el usuario no tiene cuenta, se crea una nueva
                  cur.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user.id, 50))
      
      # Guarda los cambios en la base de datos
      con.commit()
      
      await ctx.send("¡Cuentas creadas con éxito para todos los usuarios del servidor!")


def setup(bot):
    bot.add_cog(Economía(bot))
    bot.add_cog(ChatDinero(bot))