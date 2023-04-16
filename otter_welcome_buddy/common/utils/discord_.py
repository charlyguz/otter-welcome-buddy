import discord
from discord.ext.commands import Context


async def send_message(ctx: Context, message: str) -> None:
    """Send a message as embed, this allows to use more markdown features"""
    await ctx.send(embed=discord.Embed(description=message, color=discord.Color.teal()))