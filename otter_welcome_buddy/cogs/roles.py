import logging

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context

from otter_welcome_buddy.common.constants import OTTER_ADMIN
from otter_welcome_buddy.common.constants import OTTER_MODERATOR
from otter_welcome_buddy.common.constants import OTTER_ROLE
from otter_welcome_buddy.common.utils.discord_ import get_guild_by_id
from otter_welcome_buddy.common.utils.discord_ import get_member_by_id
from otter_welcome_buddy.database.handlers.db_role_config_handler import DbRoleConfigHandler
from otter_welcome_buddy.database.models.external.role_config_model import BaseRoleConfigModel


logger = logging.getLogger(__name__)


class Roles(commands.Cog):
    """
    Roles related commands who assigns roles for the users that reacts a messages
    Commands:
        roles welcome add:              Add one or more message ids separated by whitespaces
        roles welcome remove:           Remove messages to be used as welcome messages
    """

    # guild_id: [message_id]
    _WELCOME_MESSAGES_CONFIG: dict[int, list[int]] = {}

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
        except discord.Forbidden:
            logger.error("Not permissions to add the roles")
        except discord.HTTPException:
            logger.error("Adding roles failed")
        except Exception:
            logger.exception("Exception while adding the role on reaction")

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


async def setup(bot: Bot) -> None:
    """Required setup method"""
    await bot.add_cog(Roles(bot))
