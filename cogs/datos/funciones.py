import discord

# Lista de roles con valores asignados
roles_valores = {"✧ Clase Baja-Baja": 1.05, "✧ Clase Baja-Alta": 1.1, "✧ Clase Media-Baja": 1.2, "✧ Clase Media-Alta": 1.3, "✧ Clase Alta-Baja": 1.45, "✧ Clase Alta-Alta": 1.7, "✧ Millonario": 2}

def nivel_roles_aumento(variable, rol): 
    porcentaje_aumento = roles_valores.get(rol, 1) # Buscar el porcentaje de aumento correspondiente al rol
    variable *= porcentaje_aumento # Aplicar el porcentaje de aumento a la variable
    return variable # Retornar la variable con el aumento aplicado


async def confirmación_de_comando(ctx, message_text, command_func, reaction='✅', cancel_reaction='❌'):
    """
    Requiere una confirmación por medio de una reacción antes de ejecutar un comando.

    Parámetros:
    ctx (discord.ext.commands.Context): El contexto del comando.
    message_text (str): El mensaje de confirmación.
    command_func (coroutine function): La función que se ejecutará en caso de que se confirme.
    reaction (str): La reacción que se debe usar para confirmar.
    cancel_reaction (str): La reacción que se debe usar para cancelar.

    """
    message = await ctx.send(message_text)
    await message.add_reaction(reaction)
    await message.add_reaction(cancel_reaction)

    def check(reaction_, user):
        return user == ctx.author and reaction_.message == message

    try:
        reaction_, user = await ctx.bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await message.remove_reaction(reaction, ctx.bot.user)
        await message.remove_reaction(cancel_reaction, ctx.bot.user)
        await ctx.send('Se ha agotado el tiempo para confirmar la acción.')
    else:
        if str(reaction_.emoji) == reaction:
            await command_func(ctx)
        elif str(reaction_.emoji) == cancel_reaction:
            await message.remove_reaction(reaction, ctx.bot.user)
            await message.remove_reaction(cancel_reaction, ctx.bot.user)
            await ctx.send('La acción ha sido cancelada.')
