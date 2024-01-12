import logging

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import TextChannel
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context

from otter_welcome_buddy.common.constants import CronExpressions
from otter_welcome_buddy.common.constants import OTTER_ADMIN
from otter_welcome_buddy.common.constants import OTTER_MODERATOR
from otter_welcome_buddy.common.utils.dates import DateUtils
from otter_welcome_buddy.common.utils.discord_ import get_channel_by_id
from otter_welcome_buddy.common.utils.discord_ import send_plain_message
from otter_welcome_buddy.common.utils.types.common import DiscordChannelType
from otter_welcome_buddy.database.handlers.db_announcements_config_handler import (
    DbAnnouncementsConfigHandler,
)
from otter_welcome_buddy.database.models.external.announcements_config_model import (
    AnnouncementsConfigModel,
)
from otter_welcome_buddy.formatters import timeline


logger = logging.getLogger(__name__)


class Timelines(commands.Cog):
    """
    Timelines command events, where notifications about hiring events are sent every month
    Commands:
        timelines start:    Start cronjob for timeline messages
        timelines stop:     Stop cronjob for timeline messages
        timelines run send: Send announcement to configured channel
    """

    def __init__(self, bot: Bot, messages_formatter: type[timeline.Formatter]):
        self.bot: Bot = bot
        self.messages_formatter: type[timeline.Formatter] = messages_formatter
        self.scheduler: AsyncIOScheduler = AsyncIOScheduler()

        self.__configure_scheduler()

    def __configure_scheduler(self) -> None:
        """Configure and start scheduler"""
        self.scheduler.add_job(
            self._send_message_on_channel,
            DateUtils.create_cron_trigger_from(
                CronExpressions.DAY_ONE_OF_EACH_MONTH_CRON.value,
            ),
        )
        self.scheduler.start()

    @commands.group(
        brief="Commands related to Timelines messages",
        invoke_without_command=True,
        pass_context=True,
    )
    async def timelines(self, ctx: Context) -> None:
        """
        Timelines will help to keep track of important events to be announced via cronjobs
        """
        await ctx.send_help(ctx.command)

    @timelines.command(  # type: ignore
        brief="Set the interview season announcements for a server",
        usage="<text_channel>",
    )
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def start(
        self,
        ctx: Context,
        channel: TextChannel,
    ) -> None:
        """Command to interact with the bot and start cron"""
        if ctx.guild is None:
            logger.warning("No guild on context")
            return
        announcements_config_model = AnnouncementsConfigModel(
            guild=ctx.guild.id,
            channel_id=channel.id,
        )

        try:
            DbAnnouncementsConfigHandler.insert_announcements_config(
                announcements_config_model=announcements_config_model,
            )
            await send_plain_message(
                ctx,
                "**Announcement config** updated! Be ready to start receiving more announcements.",
            )
        except Exception:
            logger.exception("Error while inserting into database")

    @timelines.command(  # type: ignore
        brief="Remove the interview season announcements for a server",
    )
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def stop(
        self,
        ctx: Context,
    ) -> None:
        """Command to interact with the bot and start cron"""
        if ctx.guild is None:
            logger.warning("No guild on context")
            return

        try:
            announcements_config = DbAnnouncementsConfigHandler.get_announcements_config(
                guild_id=ctx.guild.id,
            )
            msg: str = ""
            if announcements_config is not None:
                DbAnnouncementsConfigHandler.delete_announcements_config(guild_id=ctx.guild.id)
                msg = "**Announcement config** removed!"
            else:
                msg = "No config set! 😱"
            await send_plain_message(ctx, msg)
        except Exception:
            logger.exception("Error while inserting into database")

    def _get_hiring_events(self) -> str:
        """Get hiring events for current month"""
        return self.messages_formatter.get_hiring_events_for(
            DateUtils.get_current_month(),
        )

    async def _send_message_on_channel(self) -> None:
        """
        Check the database to see which guilds send the message to at the start of the month
        """
        for entry in DbAnnouncementsConfigHandler.get_all_announcements_configs():
            try:
                channel: DiscordChannelType | None = await get_channel_by_id(
                    self.bot,
                    entry.channel_id,
                )
                if channel is None or not isinstance(channel, discord.TextChannel):
                    logger.error("Channel %s invalid to send the hiring message", entry.channel_id)
                    return
                await channel.send(self._get_hiring_events())
            except discord.Forbidden:
                logger.error("Not enough permissions to send the message in %s", __name__)
            except discord.HTTPException:
                logger.error("Sending the message failed in %s", __name__)
            except Exception:
                logger.exception("Error while sending the announcement in %s", __name__)

    @timelines.group(  # type: ignore
        brief="Commands related to trigger manually the timeline announcement",
        invoke_without_command=True,
    )
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def run(self, ctx: Context) -> None:
        """
        Admin commands related to trigger and test the announcement
        """
        await ctx.send_help(ctx.command)

    @run.command(brief="Admin command to trigger the send message on channel")  # type: ignore
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def send(self, _: Context) -> None:
        """
        Admin command that execute the send message on channel method,
        this is executed as usual to all the guilds
        """
        await self._send_message_on_channel()


async def setup(bot: Bot) -> None:
    """Required setup method"""
    await bot.add_cog(Timelines(bot, timeline.Formatter))
