import discord
from discord.ext import commands
import datetime
import sqlite3
from cogs.datos.fabricas import *
from cogs.datos.provincia import *

conn = sqlite3.connect('economy.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS fabricas
            (usuario TEXT, fecha TEXT, tipo TEXT, producto TEXT, nivel INTEGER, lugar INTEGER)''')

allowed_channels = [1088862096344748054, 1016070337802289180]


def calcular_costo_total(nivel, precio_base, nivel_factor, cemento, cemento_factor, vigas, vigas_factor, precio_hectarea):
    costo_total = ((int(precio_base) + (int(cemento) * int(cemento_factor)) +
                    (int(nivel_factor) * (int(vigas) * int(vigas_factor)))) +
                   (int(nivel_factor) * int(precio_hectarea)))
    return costo_total


class Construir(commands.Cog):
    def __init__(self, bot, c):
        self.bot = bot
        self.c = c

    @commands.command()
    async def asignar_registro_construcciones(self, ctx, canal: discord.TextChannel):
        self.canal = canal
        # Aquí se asigna el canal para el registro de construcciones
        # El canal debe ser un objeto de la clase discord.TextChannel
        await ctx.send(f"El canal {canal.mention} ha sido asignado para el registro de construcciones.")

    @commands.command(name = "calcular_costo", aliases = ["costo"] )
    async def calcular_costo(self, ctx, niveles):
      # Aquí se obtiene el costo total de la construcción según el nivel proporcionado por el usuario
        nivel_factor = int(niveles) / 6
        costo = calcular_costo_total(niveles, precio_base, nivel_factor, cemento, cemento_factor, vigas, vigas_factor, precio_hectarea)
        costo_formateado = "{:,.0f}".format(costo).replace(",", ".") 
        await ctx.send(f"El costo de una fábrica de nivel {niveles} sería {costo_formateado}")

    @commands.command(name = "codigo_de_provincias", aliases = ["cdp", "provincias"])
    async def codigo_de_provincias(self, ctx):
        embed = discord.Embed(
            title="Estados y municipios de la República Federal de Miztlán.",
            description="Acá se muestra una lista con todos los estados y el número de sus municipios.",
            color=0x68c200
        )
        
        for estado, municipios in estados:
            municipios_str = ', '.join(str(m) for m in municipios)
            embed.add_field(name=estado, value=municipios_str, inline=False)

        embed.set_image(url= "https://media.discordapp.net/attachments/1090005406648127610/1094069965730095184/codigos_postales_municipios.png")
                        
        await ctx.send(embed=embed)
      

    @commands.command(name = "construir", aliases = ['cons', 'fabri', 'fabrica'])
    async def construir(self, ctx, tipo, producto, nivel, estado):
          autor = ctx.author
          user_id = ctx.author.id
          self.c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
          result = self.c.fetchone()
          if ctx.channel.id not in allowed_channels:
            await ctx.send(f"El comando no está disponible en este canal")
            return
          conn.commit()

      # Manejo de las fechas
          dia_actual = datetime.datetime.now().weekday() 
          if not dia_actual >= 0 or  not dia_actual <= 5:
            await ctx.send("Lo siento, este comando solo puede ejecutarse de lunes a jueves.")
            return
            
          fecha_actual = datetime.datetime.now()
          dias_faltantes = 13 - fecha_actual.weekday()
          fecha_futura = fecha_actual + datetime.timedelta(days=dias_faltantes)

          # Convertir el estado
          num_estado = estado.split()[-1] # obtenemos el número del estado
          lista_numeros = [] # lista vacía para guardar los números de los estados
          nombre_estado = "" # cadena vacía para guardar el nombre del estado

      
          # Iterar por la lista de estados para buscar el número y nombre del estado
          for nombre, numeros in estados:
              if int(num_estado) in numeros:
                  nombre_estado = nombre
                  lista_numeros = numeros
      
          # Verificar si se encontró el estado
          if not nombre_estado:
              await ctx.send("Colocaste mal el estado")
              return
          imagen_url = imagenes_provincias[num_estado]

        # Aquí se obtiene el costo total de la construcción según el nivel proporcionado por el usuario
          nivel_factor = int(nivel) / 6
          costo = calcular_costo_total(nivel, precio_base, nivel_factor, cemento, cemento_factor, vigas, vigas_factor, precio_hectarea)
          costo_formateado = "{:,.0f}".format(costo).replace(",", ".") 

          if result is None:
              await ctx.send("Aún no tienes una cuenta en el sistema de economía.")
          else:
              balance = result[0]
  
              if balance < costo:
                  await ctx.send("No tienes suficientes monedas para realizar esta operación.")  
                  return

        # Aquí se envía el mensaje al canal donde se ejecutó el comando
          embed = discord.Embed(
              title=f"Construcción de la {tipo} de {producto} nivel {nivel}",
              description=f"Se ha iniciado la construcción y producción de {producto}.",
              color=0x68c200
          )
          embed.set_thumbnail(url=imagen_url)
          embed.add_field(name="Costo total", value=f"{costo_formateado}", inline=False)
          embed.add_field(name="Usuario propietario", value=f"{autor.mention}", inline=False)
          embed.add_field(name="Ubicación", value=f"{nombre_estado} {num_estado}", inline=False)

      # Para comparar el tipo y el producto
          if tipo == 'fábrica' and producto in fabrica_producto:
              await ctx.send(embed=embed)
    
              fecha_final = f"La {tipo} concluirá su construcción el {fecha_futura.strftime('%d de %B')}."
    
            # Aquí se envía el mensaje al canal especificado en "!asignar_registro_construcciones"
              canal_registro = ctx.guild.get_channel(1016070338058129509) # Reemplaza 'id_del_canal' por la ID del canal a enviar el mensaje.
    # 1093409463463063622
              if canal_registro is not None:
                await canal_registro.send(embed=embed)
                await canal_registro.send(f"{fecha_final}")
              else:
                await ctx.send(
                    "No se encontró el canal de registro especificado. Por favor, verifica el nombre y vuelve a intentarlo."
                )        
          elif tipo == 'granja' and producto in granja_producto:
              await ctx.send(embed=embed)
    
              fecha_final = f"La {tipo} concluirá su construcción el {fecha_futura.strftime('%d de %B')}."
    
            # Aquí se envía el mensaje al canal especificado en "!asignar_registro_construcciones"
              canal_registro = ctx.guild.get_channel(1016070338058129509) # Reemplaza 'id_del_canal' por la ID del canal a enviar el mensaje.
    
              if canal_registro is not None:
                await canal_registro.send(embed=embed)
                await canal_registro.send(f"{fecha_final}")
              else:
                await ctx.send(
                    "No se encontró el canal de registro especificado. Por favor, verifica el nombre y vuelve a intentarlo."
                ) 
              
          elif tipo == 'mina' and producto in mina_producto:
              await ctx.send(embed=embed)
    
              fecha_final = f"La {tipo} concluirá su construcción el {fecha_futura.strftime('%d de %B')}."
    
            # Aquí se envía el mensaje al canal especificado en "!asignar_registro_construcciones"
              canal_registro = ctx.guild.get_channel(1016070338058129509) # Reemplaza 'id_del_canal' por la ID del canal a enviar el mensaje.
    
              if canal_registro is not None:
                await canal_registro.send(embed=embed)
                await canal_registro.send(f"{fecha_final}")
              else:
                await ctx.send(
                    "No se encontró el canal de registro especificado. Por favor, verifica el nombre y vuelve a intentarlo."
                )  
          else:
              await ctx.send("`Colocaste un tipo o producto errado.`")

          
                
          new_balance = balance - costo
          self.c.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
          self.c.execute("SELECT usuario, fecha, tipo, producto, nivel, lugar FROM transacciones WHERE fecha=?", (fecha_final,))
          resoles = self.c.fetchall()
          for resole in resoles:
              user_id = resole[0]
              tipo = resole[1]
              producto = resole[2]
              nivel = resole[3]
              estado = resole[4]
          self.conn.commit()

    @commands.command(name = "productos", aliases = ['produ'])
    async def productos(self, ctx):
        embed = discord.Embed(
            title= "Lista de productos",
            description="Acá se muestra todos los productos y a que tipo de construcción pertenecen",
            color=0x68c200
        )
        produ_fabrica_str = ', '.join(fabrica_producto)
        embed.add_field(name= "Fábrica", value=discord.utils.escape_markdown(produ_fabrica_str), inline=False)
        produ_granja_str = ', '.join(granja_producto)
        embed.add_field(name= "Granja", value=discord.utils.escape_markdown(produ_granja_str), inline=False)
        produ_mina_str = ', '.join(mina_producto)
        embed.add_field(name= "Mina", value=discord.utils.escape_markdown(produ_mina_str), inline=False)

        embed.set_image(url= "https://media.discordapp.net/attachments/1090005406648127610/1096642613303578715/recursos.png")
                        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Construir(bot, c))
