import logging

import discord
from discord.ext import commands
from discord.ext.commands import Bot

from otter_welcome_buddy.common.constants import OTTER_ROLE
from otter_welcome_buddy.database.handlers.db_guild_handler import DbGuildHandler
from otter_welcome_buddy.database.models.external.guild_model import GuildModel
from otter_welcome_buddy.formatters import debug
from otter_welcome_buddy.settings import WELCOME_MESSAGES


logger = logging.getLogger(__name__)


class BotEvents(commands.Cog):
    """Actions related to the events emitted by discord"""

    def __init__(
        self,
        bot: Bot,
        debug_dependency: type[debug.Formatter],
    ) -> None:
        self.bot: Bot = bot
        self.debug_formatter: type[debug.Formatter] = debug_dependency

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Ready Event"""
        # Verify that all the guilds that the bot is part of are in the database
        for guild in self.bot.guilds:
            if DbGuildHandler.get_guild(guild_id=guild.id) is None:
                guild_model: GuildModel = GuildModel(id=guild.id)
                DbGuildHandler.insert_guild(guild_model=guild_model)

        logger.info(self.debug_formatter.bot_is_ready())

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        """Event fired when a user react to the welcome message, giving the entry role to him"""
        # Check if the user to add the role is valid
        if payload.member is None:
            logger.warning("Missing member to add role in %s", __name__)
            return
        if not WELCOME_MESSAGES or str(payload.message_id) in WELCOME_MESSAGES:
            try:
                guild = next(guild for guild in self.bot.guilds if guild.id == payload.guild_id)
                member_role = discord.utils.get(guild.roles, name=OTTER_ROLE)
                if member_role is None:
                    logger.warning("Not role found in %s for guild %s", __name__, guild.name)
                    return
                await discord.Member.add_roles(payload.member, member_role)
            except StopIteration:
                logger.warning("Not guild found in %s", __name__)
            except discord.Forbidden:
                logger.error("Not permissions to add the role in %s", __name__)
            except discord.HTTPException:
                logger.error("Adding roles failed in %s", __name__)
            except Exception:
                logger.error("Exception in %s", __name__)


async def setup(bot: Bot) -> None:
    """Required setup method"""
    await bot.add_cog(BotEvents(bot, debug.Formatter))
