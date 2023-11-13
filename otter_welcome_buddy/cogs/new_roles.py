import discord
from discord import TextChannel
from discord.ext import commands
from discord.ext.commands import Bot
from otter_welcome_buddy.common.constants import OTTER_MODERATOR, OTTER_ADMIN

# 1) añadir temnplate de mensaje, opcional si hay descripcion añadir esa descripcion ✅
# 2) eliminar editar mensajes de el comando de eliminar roles  ✅
# 3) en todos los comandos quitar lo de los mensajes y dejar uno por defecto  ✅ revisado 

# pasos para correr el bot
# python -m venv env    1) crear entorno virtual
# source ./env/Scripts/activate 2) activar entorno virtual
# pip install poetry   3) instalar poetry
# poetry install        4) instalar dependencias
# poetry run python otter_welcome_buddy 5) correr el bot
# pre-commit run -a    6) correr pre-commit

# cosas por revisar 
# 1) por que no estan funcionando los grupos de comandos ✅
# 2) por que no puedo correr el bot con poetry run python otter_welcome_buddy 
# 3) mientras no pueda correr poetry no puedo ejecutar prec-commit
# 4) esta demas el comando de editar mensaje?

class NewRoles(commands.Cog):

    _DEFAULT_MESSAGE = "Hola {role}, si quieres un nuevo rol para {role_name}, reacciona a este mensaje con {emoji}."

    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.reaction_role_config = {}


    # Principal command
    @commands.group(name="roles") 
    @commands.has_any_role(OTTER_ADMIN,OTTER_MODERATOR)
    async def roles(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
            return
    
    # Asign a role to a user when they react to a message with a specific emoji
    @roles.command(name="add_role") 
    @commands.has_any_role(OTTER_ADMIN,OTTER_MODERATOR)
    async def add_role(self, ctx, message_id: int = None, role_name: str = None, emoji: str = None):  
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            self.reaction_role_config[(message_id, emoji)] = role.id
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('❌')
            await ctx.send("Rol no encontrado")


    # Edit a message and optionally assign a role to an emoji
    @roles.command(name="edit_message") 
    @commands.has_any_role(OTTER_ADMIN,OTTER_MODERATOR)
    async def edit_message(self, ctx, message_id: int, new_message: str, role_name: str = None, emoji: str = None):
        message = await ctx.fetch_message(message_id)
        await message.edit(content=new_message)
        if role and emoji:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role:
                self.reaction_role_config[(message_id, emoji)] = role.id
                await ctx.message.add_reaction('✅')
            else:
                await ctx.message.add_reaction('❌')
                await ctx.send("Rol no encontrado")
    

    # Edit rol or emoji
    @roles.command(name="edit_role")
    @commands.has_any_role(OTTER_ADMIN,OTTER_MODERATOR)
    async def edit_role(self, ctx, message_id: int, role_name: str = None, emoji: str = None):	
        if role_name and emoji:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role:
                del self.reaction_role_config[(message_id, emoji)]
                self.reaction_role_config[(message_id, emoji)] = role.id
                await ctx.message.add_reaction('✅')
                await ctx.send("Rol y emoji editado")
            else:
                await ctx.message.add_reaction('❌')
                await ctx.send("Rol no encontrado")
        elif role_name:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role:
                self.reaction_role_config[(message_id, emoji)] = role.id
                await ctx.message.add_reaction('✅')
                await ctx.send("Rol editado")
            else:
                await ctx.message.add_reaction('❌')
                await ctx.send("Rol no encontrado")
        elif emoji:
            role_id = self.reaction_role_config[(message_id, emoji)]
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            if role:
                del self.reaction_role_config[(message_id, emoji)]
                self.reaction_role_config[(message_id, emoji)] = role.id
                await ctx.message.add_reaction('✅')
                await ctx.send("Emoji editado")
            else:
                await ctx.message.add_reaction('❌')
                await ctx.send("Emoji no encontrado")
        else:
            await ctx.message.add_reaction('❌')
            await ctx.send("No se ha editado nada, pruba a poner un rol o un emoji")



    # Create a message with a role assigned to an emoji
    @roles.command(name="new_role")
    @commands.has_any_role(OTTER_ADMIN,OTTER_MODERATOR)
    async def new_role(self, ctx, channel: TextChannel, role_name: str, emoji: str, description: str = None ): 
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        if role:
            role = discord.utils.get(ctx.guild.roles, name="interviewee")
            default_message = self._DEFAULT_MESSAGE.format(role=role.mention, role_name=role_name, emoji=emoji)
            message = default_message + f" {description}" if description else default_message
            bot_message = await channel.send(message)
            await bot_message.add_reaction(emoji)
            self.reaction_role_config[(bot_message.id, emoji)] = role.id
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('❌')
            await ctx.send("Rol no encontrado")

    

    # Remove a role from a message 
    @roles.command(name="remove_role")
    @commands.has_any_role(OTTER_ADMIN,OTTER_MODERATOR)
    async def remove_role(self, ctx, message_id: int, role_name: str = None, emoji: str = None):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            del self.reaction_role_config[(message_id, emoji)]
            await ctx.message.add_reaction('Role deleted ✅')
        else:
            await ctx.message.add_reaction('❌')
            await ctx.send("Rol no encontrado")



    # Listener that adds a role to a user that reacts to a message with a specific emoji
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload): 
        message_id_emoji = (payload.message_id, str(payload.emoji.name))

        if message_id_emoji in self.reaction_role_config:
            guild = await self.get_guild(payload)
            role = await self.get_rol(guild, message_id_emoji)

            if role:
                member = await self.get_member(payload, guild)
                if member and not member.bot:
                    await member.add_roles(role)
                    channel = guild.get_channel(payload.channel_id)
                    await channel.send(f"Role {role.name} added to {member.display_name} for reacting with {payload.emoji}.")


    # Listener that removes a role from a user that removes a reaction from a message with a specific emoji
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        message_id_emoji = (payload.message_id, str(payload.emoji.name))

        if message_id_emoji in self.reaction_role_config:
            guild = await self.get_guild(payload)
            role = await self.get_rol(guild, message_id_emoji)
            member = await self.get_member(payload, guild)
            
            await self.remove_role(member, role)
        else:
            channel = guild.get_channel(payload.channel_id)
            await channel.send("Role not found. Please contact an admin if you think this is an error.")

async def setup(bot: Bot) -> None:
    await bot.add_cog(NewRoles(bot))