import logging

import discord
from discord.ext.commands import Context


logger = logging.getLogger(__name__)


async def send_plain_message(ctx: Context, message: str) -> None:
    """Send a message as embed, this allows to use more markdown features"""
    try:
        await ctx.send(embed=discord.Embed(description=message, color=discord.Color.teal()))
    except discord.Forbidden:
        logger.exception("Not enough permissions to send the message")
    except discord.HTTPException:
        logger.exception("Sending the message failed")
