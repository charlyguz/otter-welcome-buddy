import logging

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context
from emoji import is_emoji

from otter_welcome_buddy.common.constants import COMMAND_PREFIX
from otter_welcome_buddy.common.utils.types.common import DiscordChannelType


logger = logging.getLogger(__name__)


def get_basic_embed(title: str | None = None, description: str | None = None) -> discord.Embed:
    """Get a basic embed"""
    return discord.Embed(title=title, description=description, color=discord.Color.teal())


def get_warning_embed(description: str | None = None) -> discord.Embed:
    """Get an embed with yellow color to warn the user"""
    return discord.Embed(description=description, color=discord.Color.yellow())


def get_error_embed(description: str | None = None) -> discord.Embed:
    """Get an embed with red color to flag the user"""
    return discord.Embed(description=description, color=discord.Color.red())


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


def convert_str_to_partial_emoji(
    input_emoji: str,
    guild: discord.Guild | None = None,
) -> discord.PartialEmoji | None:
    """Convert a string to a PartialEmoji object if it is a valid emoji"""
    partial_emoji = discord.PartialEmoji.from_str(input_emoji)
    is_valid: bool = False
    if partial_emoji.is_unicode_emoji():
        is_valid = is_emoji(partial_emoji.name)
    elif partial_emoji.is_custom_emoji() and guild is not None:
        is_valid = discord.utils.get(guild.emojis, name=partial_emoji.name) is not None

    return partial_emoji if is_valid else None


async def find_message_in_guild(guild: discord.Guild, message_id: int) -> discord.Message | None:
    """Find a message by its id in a guild"""
    for channel in guild.text_channels:
        try:
            message = await channel.fetch_message(message_id)
            if message:
                return message
        except discord.NotFound:
            continue
        except discord.Forbidden:
            continue
    return None


async def bot_error_handler(ctx: Context, error: Exception) -> None:  # noqa: C901
    """Handler when an error is raised in a command"""
    if isinstance(error, commands.CommandNotFound):
        pass

    if ctx.command is None:
        logger.warning("Command not found when handling error")
        return

    if getattr(error, "handled", False):
        # Errors already handled in cogs should have .handled = True
        return

    if isinstance(
        error,
        (
            commands.BadArgument,
            commands.MissingRequiredArgument,
        ),
    ):
        command = ctx.command
        command.reset_cooldown(ctx)
        usage = f"`{COMMAND_PREFIX}{str(command)} "
        params = []
        for key, value in command.params.items():
            if key not in ["self", "ctx"]:
                is_optional = any(
                    substring in str(value) for substring in ["NoneType", "Optional", "="]
                )
                params.append(f"[{key}]" if is_optional else f"<{key}>")
        usage += " ".join(params)
        usage += "`"
        if command.help:
            usage += f"\n\n{command.help}"
        await ctx.author.send(embed=get_warning_embed(f"The correct usage is: {usage}"))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.author.send(
            embed=get_error_embed("You don't have enough permissions to execute this command"),
        )
    elif isinstance(error, commands.DisabledCommand):
        await ctx.author.send(
            embed=get_warning_embed("Sorry, this command is temporarily disabled"),
        )
    elif isinstance(error, commands.CommandNotFound):
        await ctx.author.send(
            embed=get_warning_embed(
                "Oops! Looks like your command doesn' exist, "
                f"type `{COMMAND_PREFIX}help` to learn more",
            ),
        )
    else:
        msg = f"Ignoring exception in command {ctx.command}:"
        extra = {
            "message_content": ctx.message.content,
            "jump_url": ctx.message.jump_url,
        }
        logger.exception(msg, extra=extra)
