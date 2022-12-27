from discord.ext import commands

from otter_welcome_buddy.formatters import debug, messages


class Greetings(commands.Cog):
    """When a user joins, sends reactionable message"""

    def __init__(self, bot, messages_dependency, debug_dependency):
        self.bot = bot
        self.messages_formatter = messages_dependency
        self.debug_formatter = debug_dependency

    def _command_message(self):
        return self.messages_formatter.welcome_message()

    @commands.Cog.listener()
    async def on_ready(self):
        """Ready Event"""
        print(self.debug_formatter.bot_is_ready())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Send Welcome message to new member"""
        await member.send(self.messages_formatter.welcome_message())

    @commands.command()
    async def hello(self, ctx, *, member=None):
        """Sends welcome message with !hello"""
        member = member or ctx.author
        await ctx.send(self._command_message())


async def setup(bot):
    """Required setup method"""
    await bot.add_cog(Greetings(bot, messages.Formatter, debug.Formatter))
