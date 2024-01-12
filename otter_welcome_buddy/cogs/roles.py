import logging

from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context

from otter_welcome_buddy.common.constants import OTTER_ADMIN
from otter_welcome_buddy.common.constants import OTTER_MODERATOR
from otter_welcome_buddy.common.constants import OTTER_ROLE
from otter_welcome_buddy.common.constants import WELCOME_MESSAGES
from otter_welcome_buddy.common.utils.discord_ import send_plain_message
from otter_welcome_buddy.database.handlers.db_role_config_handler import DbRoleConfigHandler
from otter_welcome_buddy.database.models.external.role_config_model import BaseRoleConfigModel


logger = logging.getLogger(__name__)


class Roles(commands.Cog):
    """
    Refer to this template when adding a new command for the bot,
    once done, call it on the cogs.py file
    Commands:
        roles welcome add
        roles welcome remove
    """

    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @commands.group(
        brief="Commands related to give roles to the users",
        invoke_without_command=True,
    )
    async def roles(self, ctx: Context) -> None:
        """
        Roles will send the help when no final command is invoked
        """
        await ctx.send_help(ctx.command)

    @staticmethod
    def init_welcome_messages() -> None:
        """
        Initialize the welcome messages from the database
        """
        base_role_config_models: list[
            BaseRoleConfigModel
        ] = DbRoleConfigHandler.get_all_base_role_configs()
        for base_role_config_model in base_role_config_models:
            WELCOME_MESSAGES[base_role_config_model.guild.id] = base_role_config_model.message_ids

    @staticmethod
    def _update_welcome_messages(guild_id: int, message_ids: list[int]) -> None:
        """
        Update the welcome messages for a guild
        """
        WELCOME_MESSAGES[guild_id] = message_ids

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

    @welcome.command(usage="<message_ids>")  # type: ignore
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
            await send_plain_message(
                ctx,
                f"**Welcome message** saved! React to it to give the role **{OTTER_ROLE}**",
            )
        except Exception:
            logger.exception("Error while inserting into database")

    @welcome.command()  # type: ignore
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def remove(self, ctx: Context, message_id: int | None = None) -> None:
        """
        Remove messages from the database to be used as welcome messages.
        If no message_id is provided, all messages will be removed
        """
        if ctx.guild is None:
            logger.warning("No guild on context to save the messages")
            return

        try:
            base_role_config_model = DbRoleConfigHandler.get_base_role_config(
                guild_id=ctx.guild.id,
            )
            if base_role_config_model is not None:
                if message_id is None:
                    DbRoleConfigHandler.delete_base_role_config(guild_id=ctx.guild.id)
                    msg = "**Welcome messages** removed!"
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
                    msg = "**Welcome message** deleted!"
                self._update_welcome_messages(
                    guild_id=ctx.guild.id,
                    message_ids=message_ids,
                )
            else:
                msg = "No welcome messages set! 😱"
            await send_plain_message(ctx, msg)
        except Exception:
            logger.exception("Error while inserting into database")


async def setup(bot: Bot) -> None:
    """Required setup method"""
    await bot.add_cog(Roles(bot))
