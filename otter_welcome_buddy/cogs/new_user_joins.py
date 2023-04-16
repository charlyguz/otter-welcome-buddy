import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context

from otter_welcome_buddy.formatters import messages


class Greetings(commands.Cog):
    """When a user joins, sends reactionable message"""

    def __init__(
        self,
        bot: Bot,
        messages_dependency: type[messages.Formatter],
    ) -> None:
        self.bot: Bot = bot
        self.messages_formatter: type[messages.Formatter] = messages_dependency

    def _command_message(self) -> str:
        return self.messages_formatter.welcome_message()

    @commands.command()
    async def hello(self, ctx: Context) -> None:
        """Sends welcome message with !hello"""
        await ctx.send(self._command_message())


async def setup(bot: Bot) -> None:
    """Required setup method"""
    await bot.add_cog(Greetings(bot, messages.Formatter))
