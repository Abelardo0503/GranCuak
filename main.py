import discord
import os
from discord.ext import commands
import requests
import asyncio

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(
    command_prefix="!",  # Change to desired prefix
    case_insensitive=True  # Commands aren't case-sensitive
    intents=intents
)

@bot.event 
async def on_ready():  # When the bot is ready
    print("Bot iniciado")
    print(bot.user)  # Prints the bot's username and identifier
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="desarrollo"))

    # Configura el intervalo de tiempo en segundos para hacer la petición
    intervalo = 270  # 5 minutos (puedes ajustar este valor)

    while True:
        # Realiza una petición a tu bot para mantenerlo activo
        url = f"https://replit.com/{os.environ['REPL_SLUG']}.{os.environ['REPL_OWNER']}"
        response = requests.get(url)
        print("Ping enviado para mantener el bot activo")
        await asyncio.sleep(intervalo)

extensions = [
    # 'cogs.cogs_basicos',
    'cogs.wiki',
    'cogs.industria',
    'cogs.ayuda',
    'cogs.economía'
]

if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(extension)


    try:
        bot.run(os.getenv("TOKEN"))
    except discord.HTTPException as e:
        # Manejo de errores
        pass  # Agrega aquí tu manejo de errores específico si es necesario

