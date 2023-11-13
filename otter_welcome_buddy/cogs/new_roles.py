import discord
from discord import TextChannel
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context

from otter_welcome_buddy.common.constants import OTTER_ADMIN
from otter_welcome_buddy.common.constants import OTTER_MODERATOR

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
    """
    Newroles commands who assigns roles for the users that reacts a messages
    Commands:
        roles add_role:     Create new message and assign roles to an emoji
        roles edit_message: Edit a message and optionally assign a role to an emoji
        roles edit_role:    Edit rol or emoji
        roles new_role:     Create a message with a role assigned to an emoji
        roles remove_role:  Remove a role from a message
    """

    _DEFAULT_MESSAGE: str = (
        "Hola {role}, si quieres un nuevo rol para {role_name}, "
        "reacciona a este mensaje con {emoji}."
    )

    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.reaction_role_config: dict[tuple[int, str], int] = {}

    @commands.group(name="roles")
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def roles(self, ctx: Context) -> None:
        """Principal command"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
            return

    @roles.command(name="add_role")  # type: ignore
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def add_role(
        self,
        ctx: Context,
        message_id: int | None = None,
        role_name: str | None = None,
        emoji: str | None = None,
    ) -> None:
        """Asign a role to a user when they react to a message with a specific emoji"""
        if ctx.guild is None:
            return
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role and emoji and message_id:
            self.reaction_role_config[(message_id, emoji)] = role.id
            await ctx.message.add_reaction("✅")
        else:
            await ctx.message.add_reaction("❌")
            await ctx.send("Rol no encontrado")

    @roles.command(name="edit_message")  # type: ignore
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def edit_message(
        self,
        ctx: Context,
        message_id: int,
        new_message: str,
        role_name: str | None = None,
        emoji: str | None = None,
    ) -> None:
        """Edit a message and optionally assign a role to an emoji"""
        message = await ctx.fetch_message(message_id)
        await message.edit(content=new_message)
        if emoji and ctx.guild:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role:
                self.reaction_role_config[(message_id, emoji)] = role.id
                await ctx.message.add_reaction("✅")
            else:
                await ctx.message.add_reaction("❌")
                await ctx.send("Rol no encontrado")

    @roles.command(name="edit_role")  # type: ignore
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def edit_role(
        self,
        ctx: Context,
        message_id: int,
        role_name: str | None = None,
        emoji: str | None = None,
    ) -> None:
        """Edit rol or emoji"""
        if ctx.guild is None:
            return
        if role_name and emoji:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role:
                del self.reaction_role_config[(message_id, emoji)]
                self.reaction_role_config[(message_id, emoji)] = role.id
                await ctx.message.add_reaction("✅")
                await ctx.send("Rol y emoji editado")
            else:
                await ctx.message.add_reaction("❌")
                await ctx.send("Rol no encontrado")
        elif role_name:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role and emoji:
                self.reaction_role_config[(message_id, emoji)] = role.id
                await ctx.message.add_reaction("✅")
                await ctx.send("Rol editado")
            else:
                await ctx.message.add_reaction("❌")
                await ctx.send("Rol no encontrado")
        elif emoji:
            role_id = self.reaction_role_config[(message_id, emoji)]
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            if role:
                del self.reaction_role_config[(message_id, emoji)]
                self.reaction_role_config[(message_id, emoji)] = role.id
                await ctx.message.add_reaction("✅")
                await ctx.send("Emoji editado")
            else:
                await ctx.message.add_reaction("❌")
                await ctx.send("Emoji no encontrado")
        else:
            await ctx.message.add_reaction("❌")
            await ctx.send("No se ha editado nada, pruba a poner un rol o un emoji")

    @roles.command(name="new_role")  # type: ignore
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def new_role(
        self,
        ctx: Context,
        channel: TextChannel,
        role_name: str,
        emoji: str,
        description: str | None = None,
    ) -> None:
        """Create a message with a role assigned to an emoji"""
        if ctx.guild is None:
            return
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        if role:
            role_member = discord.utils.get(ctx.guild.roles, name="interviewee")
            default_message = self._DEFAULT_MESSAGE.format(
                role=role_member.mention if role_member else "",
                role_name=role_name,
                emoji=emoji,
            )
            message = default_message + f" {description}" if description else default_message
            bot_message = await channel.send(message)
            await bot_message.add_reaction(emoji)
            self.reaction_role_config[(bot_message.id, emoji)] = role.id
            await ctx.message.add_reaction("✅")
        else:
            await ctx.message.add_reaction("❌")
            await ctx.send("Rol no encontrado")

    @roles.command(name="remove_role")  # type: ignore
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def remove_role(
        self,
        ctx: Context,
        message_id: int,
        role_name: str | None = None,
        emoji: str | None = None,
    ) -> None:
        """Remove a role from a message"""
        if ctx.guild:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role and emoji:
            del self.reaction_role_config[(message_id, emoji)]
            await ctx.message.add_reaction("Role deleted ✅")
        else:
            await ctx.message.add_reaction("❌")
            await ctx.send("Rol no encontrado")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        """
        Listener that adds a role to a user that
        reacts to a message with a specific emoji
        """
        message_id_emoji = (payload.message_id, str(payload.emoji.name))
        if message_id_emoji in self.reaction_role_config and payload.guild_id:
            guild = self.bot.get_guild(payload.guild_id)
            if guild is None:
                return
            role_id = self.reaction_role_config[message_id_emoji]
            role = guild.get_role(role_id)
            if role and payload.member:
                await discord.Member.add_roles(payload.member, role)
        elif payload.member:
            error_message: str = (
                "Role not found. Please contact an admin if you think this is an error."
            )
            await payload.member.send(
                error_message,
            )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        """
        Listener that removes a role from a user that removes
        a reaction from a message with a specific emoji
        """
        message_id_emoji = (payload.message_id, str(payload.emoji.name))
        if message_id_emoji in self.reaction_role_config and payload.guild_id:
            guild = self.bot.get_guild(payload.guild_id)
            if guild is None:
                return
            role_id = self.reaction_role_config[message_id_emoji]
            role = guild.get_role(role_id)
            if role and payload.member:
                await discord.Member.remove_roles(payload.member, role)
        elif payload.member:
            await payload.member.send(
                "Role not found. Please contact an admin if you think this is an error.",
            )


async def setup(bot: Bot) -> None:
    """Required setup method"""
    await bot.add_cog(NewRoles(bot))
