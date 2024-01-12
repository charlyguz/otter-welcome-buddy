import logging

import discord
from discord.ext import commands
from discord.ext.commands import Bot

from otter_welcome_buddy.database.handlers.db_guild_handler import DbGuildHandler
from otter_welcome_buddy.database.models.external.guild_model import GuildModel
from otter_welcome_buddy.formatters import debug
from otter_welcome_buddy.startup.database import init_guild_table


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
        init_guild_table(self.bot)

        logger.info(self.debug_formatter.bot_is_ready())

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Event fired when a guild is either created or the bot join into"""
        if DbGuildHandler.get_guild(guild_id=guild.id) is None:
            guild_model: GuildModel = GuildModel(guild_id=guild.id)
            DbGuildHandler.insert_guild(guild_model=guild_model)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Event fired when a guild is deleted or the bot is removed from it"""
        DbGuildHandler.delete_guild(guild_id=guild.id)


async def setup(bot: Bot) -> None:
    """Required setup method"""
    await bot.add_cog(BotEvents(bot, debug.Formatter))
