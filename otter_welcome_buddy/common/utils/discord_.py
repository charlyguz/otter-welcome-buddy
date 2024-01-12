import logging

import discord
from discord.ext.commands import Bot
from discord.ext.commands import Context

from otter_welcome_buddy.common.utils.types.common import DiscordChannelType


logger = logging.getLogger(__name__)


def get_basic_embed(title: str | None = None, description: str | None = None) -> discord.Embed:
    """Get a basic embed"""
    return discord.Embed(title=title, description=description, color=discord.Color.teal())


async def send_plain_message(ctx: Context, message: str) -> None:
    """Send a message as embed, this allows to use more markdown features"""
    try:
        await ctx.send(embed=get_basic_embed(description=message))
    except discord.Forbidden:
        logger.exception("Not enough permissions to send the message")
    except discord.HTTPException:
        logger.exception("Sending the message failed")


async def get_guild_by_id(bot: Bot, guild_id: int) -> discord.Guild | None:
    """Get a guild by its id"""
    # Check if the guild is in bot's cache
    guild: discord.Guild | None = bot.get_guild(guild_id)
    if guild is None:
        try:
            # Fetch the guild from Discord
            guild = await bot.fetch_guild(guild_id)
        except discord.Forbidden:
            logger.error("Not enough permissions to fetch the guild %s", guild_id)
        except discord.HTTPException:
            logger.error("Getting the guild %s failed", guild_id)

    return guild


async def get_channel_by_id(bot: Bot, channel_id: int) -> DiscordChannelType | None:
    """Get a channel by its id"""
    # Check if the channel is in bot's cache
    channel: DiscordChannelType | None = bot.get_channel(channel_id)
    if channel is None:
        try:
            # Fetch the channel from Discord
            channel = await bot.fetch_channel(channel_id)
        except discord.NotFound:
            logger.error("Invalid channel_id %s", channel_id)
        except discord.InvalidData:
            logger.error("Invalid channel type received for channel %s", channel_id)
        except discord.Forbidden:
            logger.error("Not enough permissions to fetch the channel %s", channel_id)
        except discord.HTTPException:
            logger.error("Getting the channel %s failed", channel_id)

    return channel


async def get_message_by_id(
    bot: Bot,
    channel_id: int,
    message_id: int,
) -> tuple[discord.Message, discord.TextChannel] | None:
    """Get a message by its id and its corresponding text channel"""
    channel: DiscordChannelType | None = await get_channel_by_id(bot, channel_id)
    if isinstance(channel, discord.TextChannel):
        try:
            # Fetch the message from Discord
            message: discord.Message = await channel.fetch_message(message_id)
            return (message, channel)
        except discord.NotFound:
            logger.error("Message with id %s not found", message_id)
        except discord.Forbidden:
            logger.error("Not enough permissions to fetch the message %s", message_id)
        except discord.HTTPException:
            logger.error("Getting the message %s failed", message_id)
    else:
        logger.error("Invalid channel %s while retrieving the message %s", channel_id, message_id)

    return None


async def get_member_by_id(guild: discord.Guild, member_id: int) -> discord.Member | None:
    """Get a member by its id"""
    # Check if the member is in guild's cache
    member: discord.Member | None = guild.get_member(member_id)
    if member is None:
        try:
            # Fetch the member from Discord
            member = await guild.fetch_member(member_id)
        except discord.NotFound:
            logger.error("Member with id %s not found", member_id)
        except discord.Forbidden:
            logger.error("Not enough permissions to fetch the member %s", member_id)
        except discord.HTTPException:
            logger.error("Getting the member %s failed", member_id)

    return member
