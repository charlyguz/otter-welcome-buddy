import logging

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context

from otter_welcome_buddy.common.constants import OTTER_ADMIN
from otter_welcome_buddy.common.constants import OTTER_MODERATOR
from otter_welcome_buddy.common.constants import OTTER_ROLE
from otter_welcome_buddy.common.utils.discord_ import convert_str_to_partial_emoji
from otter_welcome_buddy.common.utils.discord_ import find_message_in_guild
from otter_welcome_buddy.common.utils.discord_ import get_basic_embed
from otter_welcome_buddy.common.utils.discord_ import get_guild_by_id
from otter_welcome_buddy.common.utils.discord_ import get_member_by_id
from otter_welcome_buddy.common.utils.discord_ import send_plain_message
from otter_welcome_buddy.database.handlers.db_role_config_handler import DbRoleConfigHandler
from otter_welcome_buddy.database.models.external.role_config_model import BaseRoleConfigModel


logger = logging.getLogger(__name__)


class Roles(commands.Cog):
    """
    Roles related commands who assigns roles for the users that reacts a messages
    Commands:
        roles welcome add:              Add one or more message ids separated by whitespaces
        roles welcome remove:           Remove messages to be used as welcome messages
        roles reaction create:          Create a new message that the users can react to
        roles reaction convert:         Convert message to give roles when user reacts to it
        roles reaction add_role:        Add role to message
        roles reaction edit_message:    Edit message description
        roles reaction edit_role:       Edit role that the user will get when reacts to the message
        roles reaction edit_emoji:      Edit emoji that the user will react to get the role
        roles reaction remove_role:     Remove message completely or role from message
    """

    # guild_id: [message_id]
    _WELCOME_MESSAGES_CONFIG: dict[int, list[int]] = {}
    # message_id: {emoji: role_id}
    _REACTION_ROLES_CONFIG: dict[int, dict[str, int]] = {}

    _DEFAULT_MESSAGE: str = "React here with the corresponding emoji to get more roles!"

    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self._init_welcome_messages()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        """
        Listener that process when a user add a reaction to a message
        """
        # Check if the user and guild to add the role is valid
        if payload.guild_id is None:
            logger.warning("Missing data to add role in %s", __name__)
            return

        try:
            await self._check_welcome_message_reaction(
                payload.guild_id,
                payload.member,
                payload.user_id,
                payload.message_id,
            )
            await self._check_roles_reaction(
                payload.guild_id,
                payload.member,
                payload.user_id,
                payload.message_id,
                payload.emoji,
            )
        except discord.Forbidden:
            logger.error("Not permissions to add the roles")
        except discord.HTTPException:
            logger.error("Adding roles failed")
        except Exception:
            logger.exception("Exception while adding the role on reaction")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        """
        Listener that process when a user remove a reaction from a message
        """
        # Check if the user and guild to remove the role is valid
        if payload.guild_id is None:
            logger.warning("Missing data to remove role in %s", __name__)
            return

        try:
            await self._check_roles_reaction(
                payload.guild_id,
                payload.member,
                payload.user_id,
                payload.message_id,
                payload.emoji,
                False,
            )
        except discord.Forbidden:
            logger.error("Not permissions to remove the roles")
        except discord.HTTPException:
            logger.error("Removing roles failed")
        except Exception:
            logger.exception("Exception while removing the role on reaction")

    @commands.group(
        brief="Commands related to give roles to the users",
        invoke_without_command=True,
    )
    async def roles(self, ctx: Context) -> None:
        """
        Roles will send the help when no final command is invoked
        """
        await ctx.send_help(ctx.command)

    def _init_welcome_messages(self) -> None:
        """
        Initialize the welcome messages from the database
        """
        base_role_config_models: list[
            BaseRoleConfigModel
        ] = DbRoleConfigHandler.get_all_base_role_configs()
        for base_role_config_model in base_role_config_models:
            self._WELCOME_MESSAGES_CONFIG.update(
                {base_role_config_model.guild.id: base_role_config_model.message_ids},
            )

    def _update_welcome_messages(self, guild_id: int, message_ids: list[int]) -> None:
        """
        Update the welcome messages for a guild
        """
        self._WELCOME_MESSAGES_CONFIG[guild_id] = message_ids

    @roles.group(  # type: ignore
        brief="Commands related to give the otter role to the users "
        "when reacting to the welcome messages",
        invoke_without_command=True,
    )
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def welcome(self, ctx: Context) -> None:
        """
        Roles will send the help when no final command is invoked
        """
        await ctx.send_help(ctx.command)

    @welcome.command(  # type: ignore
        brief="Add message_ids separated by whitespaces to be used as welcome messages",
        usage="<message_ids>",
    )
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def add(self, ctx: Context, input_message_ids: commands.Greedy[int]) -> None:
        """
        Add one or more message ids separated by whitespaces
        to the database to be used as welcome messages
        """
        if len(input_message_ids) == 0:
            return
        # Remove duplicates
        message_ids: list[int] = list(set(input_message_ids))
        if ctx.guild is None:
            logger.warning("No guild on context to save the messages")
            return

        try:
            base_role_config_model = DbRoleConfigHandler.get_base_role_config(
                guild_id=ctx.guild.id,
            )
            if base_role_config_model is not None:
                message_ids.extend(base_role_config_model.message_ids)
                base_role_config_model.message_ids = list(set(message_ids))
            else:
                base_role_config_model = BaseRoleConfigModel(
                    guild=ctx.guild.id,
                    message_ids=message_ids,
                )

            base_role_config_model = DbRoleConfigHandler.insert_base_role_config(
                base_role_config_model=base_role_config_model,
            )

            self._update_welcome_messages(
                guild_id=base_role_config_model.guild.id,
                message_ids=base_role_config_model.message_ids,
            )
            await ctx.message.add_reaction("✅")
        except Exception:
            logger.exception("Error while inserting into database")

    @welcome.command(  # type: ignore
        brief="Remove messages to be used as welcome messages. "
        "If no message_id is provided, all messages will be removed",
        usage="[message_id]",
    )
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def remove(self, ctx: Context, message_id: int | None = None) -> None:
        """
        Remove messages from the database to be used as welcome messages.
        If no message_id is provided, all messages will be removed
        """
        if ctx.guild is None:
            logger.warning("No guild on context to remove the messages")
            return

        try:
            base_role_config_model = DbRoleConfigHandler.get_base_role_config(
                guild_id=ctx.guild.id,
            )
            if base_role_config_model is not None:
                if message_id is None:
                    DbRoleConfigHandler.delete_base_role_config(guild_id=ctx.guild.id)
                    message_ids = []
                else:
                    base_role_config_model = (
                        DbRoleConfigHandler.delete_message_from_base_role_config(
                            guild_id=ctx.guild.id,
                            input_message_id=message_id,
                        )
                    )
                    message_ids = (
                        base_role_config_model.message_ids if base_role_config_model else []
                    )
                self._update_welcome_messages(
                    guild_id=ctx.guild.id,
                    message_ids=message_ids,
                )
            await ctx.message.add_reaction("✅")
        except Exception:
            logger.exception("Error while inserting into database")

    async def _check_welcome_message_reaction(
        self,
        guild_id: int,
        member: discord.Member | None,
        user_id: int,
        message_id: int,
    ) -> None:
        """
        Check if the reaction is on a welcome message
        """
        if message_id in self._WELCOME_MESSAGES_CONFIG.get(guild_id, []):
            guild = await get_guild_by_id(self.bot, guild_id)
            if guild is None:
                logger.warning("Not guild found in %s with id %s", __name__, guild_id)
                return
            member = await get_member_by_id(guild, user_id) if member is None else member
            if member is None:
                logger.warning("Not member found in guild %s with id %s", guild_id, user_id)
                return
            member_role = discord.utils.get(guild.roles, name=OTTER_ROLE)
            if member_role is None:
                logger.warning("Not role found in %s for guild %s", __name__, guild.name)
                return
            await discord.Member.add_roles(member, member_role)

    @roles.group(  # type: ignore
        brief="Commands related to give the otter role to the users "
        "when reacting to the assigned messages",
        invoke_without_command=True,
    )
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def reaction(self, ctx: Context) -> None:
        """
        Roles will send the help when no final command is invoked
        """
        await ctx.send_help(ctx.command)

    def _format_roles_in_message(self, guild: discord.Guild, message_id: int) -> str:
        """
        Format the roles in the message
        """
        message_rows: list[str] = []
        for emoji, role_id in self._REACTION_ROLES_CONFIG.get(message_id, {}).items():
            guild_role: discord.Role | None = discord.utils.get(guild.roles, id=role_id)
            if guild_role is None:
                logger.error(
                    "Role %s not found in guild %s, removing it from the list",
                    role_id,
                    guild.id,
                )
                del self._REACTION_ROLES_CONFIG[message_id][emoji]
                continue
            message_rows.append(f"{emoji}: {guild_role.mention}")
        return "\n".join(message_rows)

    async def _update_roles_message(self, ctx: Context, message_id: int) -> None:
        try:
            if ctx.guild is None:
                logger.warning("No guild on context to add the role to the message")
                return

            message: discord.Message | None = await find_message_in_guild(ctx.guild, message_id)
            if message is None or len(message.embeds) != 1:
                logger.warning(
                    "The message %s was not correctly configured in %s",
                    message_id,
                    __name__,
                )
                await send_plain_message(ctx, "Message not correctly configured in guild")
                return

            title: str | None = message.embeds[0].title
            description: str = self._format_roles_in_message(ctx.guild, message_id)
            await message.edit(embed=get_basic_embed(title=title, description=description))
            await ctx.message.add_reaction("✅")
        except discord.Forbidden:
            logger.exception("Not enough permissions to edit the message")
        except discord.HTTPException:
            logger.exception("Editing the message failed")
        except Exception:
            logger.exception("Exception while adding the role to the message")

    def _is_emoji_configured(self, message_id: int, emoji: discord.PartialEmoji) -> bool:
        """
        Check if the emoji is in the message
        """
        return self._REACTION_ROLES_CONFIG.get(message_id, {}).get(emoji.name) is not None

    def _is_role_configured(self, message_id: int, role: discord.Role) -> bool:
        """
        Check if the role is in the message
        """
        return role.id in self._REACTION_ROLES_CONFIG.get(message_id, {}).values()

    def _get_emoji_from_role(self, message_id: int, role: discord.Role) -> str | None:
        """
        Get the emoji from the role
        """
        for emoji, role_id in self._REACTION_ROLES_CONFIG.get(message_id, {}).items():
            if role_id == role.id:
                return emoji
        return None

    @reaction.command(  # type: ignore
        brief="Create a new message that the users can react to",
        usage="<text_channel> [content]",
    )
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def create(
        self,
        ctx: Context,
        channel: discord.TextChannel,
        *,
        content: str | None = None,
    ) -> None:
        """
        Create a new message that the users can react to. If no content
        is provided, the default template will be used
        """
        try:
            if content is None:
                content = self._DEFAULT_MESSAGE
            message: discord.Message = await channel.send(embed=get_basic_embed(title=content))
            self._REACTION_ROLES_CONFIG[message.id] = {}
            await send_plain_message(
                ctx,
                f"Message `{message.id}` created! Start adding roles to it.",
            )
        except discord.Forbidden:
            logger.error("Not enough permissions to send or react to the message in %s", __name__)
        except discord.HTTPException:
            logger.error("Sending or reacting to the message failed in %s", __name__)
        except Exception:
            logger.exception("Exception in %s", __name__)

    @reaction.command(  # type: ignore
        brief="Convert a message that the users can react to",
        usage="<message_id>",
    )
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def convert(self, ctx: Context, message_id: int) -> None:
        """
        Convert an existing message that the users can react to.
        """
        if self._REACTION_ROLES_CONFIG.get(message_id) is not None:
            await send_plain_message(ctx, "Message already exists in the configuration")
            return

        self._REACTION_ROLES_CONFIG[message_id] = {}
        await ctx.message.add_reaction("✅")

    @reaction.command(  # type: ignore
        brief="Add role to message with its corresponding emoji",
        usage="<message_id> <role> <emoji>",
    )
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def add_role(self, ctx: Context, message_id: int, role: discord.Role, emoji: str) -> None:
        """
        Add role to message with its corresponding emoji
        """
        if ctx.guild is None:
            logger.warning("No guild on context to add the roles")
            return

        try:
            if self._REACTION_ROLES_CONFIG.get(message_id) is None:
                await send_plain_message(
                    ctx,
                    "Message is not configured to be used, use `convert` first",
                )
                return

            partial_emoji: discord.PartialEmoji | None = convert_str_to_partial_emoji(
                emoji,
                ctx.guild,
            )
            if partial_emoji is None:
                await send_plain_message(ctx, "Not valid emoji")
                return

            if self._is_emoji_configured(message_id, partial_emoji) or self._is_role_configured(
                message_id,
                role,
            ):
                await send_plain_message(
                    ctx,
                    "Emoji or Role already exists in the configuration for this message",
                )
                return

            self._REACTION_ROLES_CONFIG[message_id][partial_emoji.name] = role.id
            await self._update_roles_message(ctx, message_id)
        except Exception:
            logger.exception("Exception in %s", __name__)

    @reaction.command(  # type: ignore
        brief="Edit message description",
        usage="<message_id> [content]",
    )
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def edit_message(
        self,
        ctx: Context,
        message_id: int,
        *,
        content: str,
    ) -> None:
        """
        Edit message description
        """
        if ctx.guild is None:
            logger.warning("No guild on context to edit the message")
            return

        try:
            if self._REACTION_ROLES_CONFIG.get(message_id) is None:
                await send_plain_message(ctx, "Message is not configured to be used")
                return

            message: discord.Message | None = await find_message_in_guild(ctx.guild, message_id)
            if message is None:
                logger.warning("The message %s was not found in %s", message_id, __name__)
                await send_plain_message(ctx, "Message not found in guild")
                return

            description: str = self._format_roles_in_message(ctx.guild, message_id)
            await message.edit(embed=get_basic_embed(title=content, description=description))
            await ctx.message.add_reaction("✅")
        except discord.Forbidden:
            logger.error("Not enough permissions to edit the message in %s", __name__)
        except discord.HTTPException:
            logger.error("Editing the message failed in %s", __name__)
        except Exception:
            logger.exception("Exception in %s", __name__)

    @reaction.command(  # type: ignore
        brief="Edit role that the user will get when reacting to the message",
        usage="<message_id> <emoji> <new_role>",
    )
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def edit_role(
        self,
        ctx: Context,
        message_id: int,
        emoji: str,
        role: discord.Role,
    ) -> None:
        """
        Edit role that the user will get when reacting to the message. If the emoji
        is not configured, it will be added to the message
        """
        if ctx.guild is None:
            logger.warning("No guild on context to edit the role")
            return

        try:
            if self._REACTION_ROLES_CONFIG.get(message_id) is None:
                await send_plain_message(
                    ctx,
                    "Message is not configured to be used, use `convert` first",
                )
                return

            partial_emoji: discord.PartialEmoji | None = convert_str_to_partial_emoji(
                emoji,
                ctx.guild,
            )
            if partial_emoji is None:
                await send_plain_message(ctx, "Not valid emoji")
                return

            if self._is_role_configured(message_id, role):
                await send_plain_message(ctx, "Role already configured")
                return

            self._REACTION_ROLES_CONFIG[message_id][partial_emoji.name] = role.id
            await self._update_roles_message(ctx, message_id)
        except Exception:
            logger.exception("Exception in %s", __name__)

    @reaction.command(  # type: ignore
        brief="Edit emoji that the user will react to get the role",
        usage="<message_id> <role> <new_emoji>",
    )
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def edit_emoji(
        self,
        ctx: Context,
        message_id: int,
        role: discord.Role,
        emoji: str,
    ) -> None:
        """
        Edit emoji that the user will react to get the role. If the role
        is not configured, it will be added to the message
        """
        if ctx.guild is None:
            logger.warning("No guild on context to edit the role")
            return

        try:
            if self._REACTION_ROLES_CONFIG.get(message_id) is None:
                await send_plain_message(
                    ctx,
                    "Message is not configured to be used, use `convert` first",
                )
                return

            partial_emoji: discord.PartialEmoji | None = convert_str_to_partial_emoji(
                emoji,
                ctx.guild,
            )
            if partial_emoji is None:
                await send_plain_message(ctx, "Not valid emoji")
                return

            if self._is_emoji_configured(message_id, partial_emoji):
                await send_plain_message(ctx, "Emoji already configured")
                return

            emoji_role: str | None = self._get_emoji_from_role(message_id, role)
            if emoji_role is not None:
                del self._REACTION_ROLES_CONFIG[message_id][emoji_role]

            self._REACTION_ROLES_CONFIG[message_id][partial_emoji.name] = role.id
            await self._update_roles_message(ctx, message_id)
        except Exception:
            logger.exception("Exception in %s", __name__)

    @reaction.command(  # type: ignore
        brief="Remove message completely or role from message",
        usage="<message_id> [role]",
    )
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def remove_role(
        self,
        ctx: Context,
        message_id: int,
        role: discord.Role | None = None,
    ) -> None:
        """
        Remove message completely or role from message. If no role is provided,
        the message will be removed completely
        """
        if ctx.guild is None:
            logger.warning("No guild on context to edit the role")
            return

        try:
            if role is not None:
                emoji_role: str | None = self._get_emoji_from_role(message_id, role)
                if emoji_role is not None:
                    del self._REACTION_ROLES_CONFIG[message_id][emoji_role]
                    await self._update_roles_message(ctx, message_id)
                    return

            try:
                message: discord.Message | None = await find_message_in_guild(
                    ctx.guild,
                    message_id,
                )
                if message is not None:
                    await message.delete()
                del self._REACTION_ROLES_CONFIG[message_id]
                await ctx.message.add_reaction("✅")
            except Exception:
                logger.exception("Exception while deleting the message")

        except Exception:
            logger.exception("Exception in %s", __name__)

    async def _check_roles_reaction(  # pylint: disable=too-many-arguments
        self,
        guild_id: int,
        member: discord.Member | None,
        user_id: int,
        message_id: int,
        emoji: discord.PartialEmoji,
        is_add_reaction: bool = True,
    ) -> None:
        """
        Check if the reaction has a corresponding role to assign
        """
        role_id = self._REACTION_ROLES_CONFIG.get(message_id, {}).get(emoji.name)
        if role_id is not None:
            guild = await get_guild_by_id(self.bot, guild_id)
            if guild is None:
                logger.warning("Not guild found in %s with id %s", __name__, guild_id)
                return
            member = await get_member_by_id(guild, user_id) if member is None else member
            if member is None:
                logger.warning("Not member found in guild %s with id %s", guild_id, user_id)
                return
            member_role = discord.utils.get(guild.roles, id=role_id)
            if member_role is None:
                logger.warning(
                    "Not role found in %s for guild %s with id %s",
                    __name__,
                    guild.name,
                    role_id,
                )
                return
            if is_add_reaction:
                await discord.Member.add_roles(member, member_role)
            else:
                await discord.Member.remove_roles(member, member_role)


async def setup(bot: Bot) -> None:
    """Required setup method"""
    await bot.add_cog(Roles(bot))
