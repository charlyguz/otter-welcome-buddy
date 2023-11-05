import discord
from discord.ext import commands
from discord.ext.commands import Bot
from otter_welcome_buddy.common.constants import OTTER_MODERATOR

# 1) añadir temnplate de mensaje, opcional si hay descripcion añadir esa descripcion
# 2) eliminar editar mensajes de el comando de eliminar roles, en todos quitar lo de los mensajes y dejar uno por defecto
# 3) añadir comando especifico para editar mensaje, añadir un comando para editar rol y emojis

class NewRoles(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.reaction_role_config = {}


    # Asign a role to a user when they react to a message with a specific emoji
    @commands.command() 
    async def new_roles(self, ctx, message_id: int = None, role_name: str = None, emoji: str = None):
        if ctx.invoked_subcommand is None:
            await ctx.send("Avaliable subcommands: edit_message, add_role, remove_role")
            return
        
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            self.reaction_role_config[(message_id, emoji)] = role.id
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('❌')
            await ctx.send("Rol no encontrado")
    
    # Edit a message and optionally assign a role to an emoji
    @commands.command(name="edit_message") 
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
    
    # Create a message with a role assigned to an emoji
    @commands.command(name="add_role")
    async def add_role(self, ctx, role_name: str, emoji: str, message: str): 
        
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            bot_message = await ctx.send(message)
            await bot_message.add_reaction(emoji)
            self.reaction_role_config[(bot_message.id, emoji)] = role.id
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('❌')
            await ctx.send("Rol no encontrado")
    

    # Remove a role from a message and opcionaly edit the message
    @commands.command(name="remove_role")
    @commands.has_role(OTTER_MODERATOR)
    async def remove_role(self, ctx, message_id: int, role_name: str = None, emoji: str = None, new_message: str = None):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            del self.reaction_role_config[(message_id, emoji)]
            await ctx.message.add_reaction('Role deleted ✅')
        if new_message:
            message = await ctx.fetch_message(message_id)
            await message.edit(content=new_message)
            await ctx.message.add_reaction('Message edited ✅')



    # Listener that adds a role to a user that reacts to a message with a specific emoji
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload): 
        message_id_emoji = (payload.message_id, str(payload.emoji.name))

        if message_id_emoji in self.reaction_role_config:
            role_id = self.reaction_role_config[message_id_emoji]
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(role_id)

            if role:
                member = guild.get_member(payload.user_id)
                if member and not member.bot:
                    await member.add_roles(role)
                    channel = guild.get_channel(payload.channel_id)
                    await channel.send(f"Role {role.name} added to {member.display_name} for reacting with {payload.emoji}.")

async def setup(bot: Bot) -> None:
    await bot.add_cog(NewRoles(bot))