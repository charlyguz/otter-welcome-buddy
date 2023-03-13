import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context

from otter_welcome_buddy.common.constants import OTTER_ROLE
from otter_welcome_buddy.formatters import debug
from otter_welcome_buddy.formatters import messages
from otter_welcome_buddy.settings import WELCOME_MESSAGES


class Greetings(commands.Cog):
    """When a user joins, sends reactionable message"""

    def __init__(
        self,
        bot: Bot,
        messages_dependency: type[messages.Formatter],
        debug_dependency: type[debug.Formatter],
    ) -> None:
        self.bot: Bot = bot
        self.messages_formatter: type[messages.Formatter] = messages_dependency
        self.debug_formatter: type[debug.Formatter] = debug_dependency

    def _command_message(self) -> str:
        return self.messages_formatter.welcome_message()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Ready Event"""
        print(self.debug_formatter.bot_is_ready())

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        """Event fired when a user react to the welcome message, giving the entry role to him"""
        # Check if the user to add the role is valid
        if payload.member is None:
            print(f"Missing member to add role in {__name__}")
            return
        if not WELCOME_MESSAGES or str(payload.message_id) in WELCOME_MESSAGES:
            try:
                guild = next(guild for guild in self.bot.guilds if guild.id == payload.guild_id)
                member_role = discord.utils.get(guild.roles, name=OTTER_ROLE)
                if member_role is None:
                    print(f"Not role found in {__name__} for guild {guild.name}")
                    return
                await discord.Member.add_roles(payload.member, member_role)
            except StopIteration:
                print(f"Not guild found in {__name__}")
            except discord.Forbidden:
                print(f"Not permissions to add the role in {__name__}")
            except discord.HTTPException:
                print(f"Adding roles failed in {__name__}")
            except Exception:
                print(f"Exception in {__name__}")

    @commands.command()
    async def hello(self, ctx: Context) -> None:
        """Sends welcome message with !hello"""
        await ctx.send(self._command_message())


async def setup(bot: Bot) -> None:
    """Required setup method"""
    await bot.add_cog(Greetings(bot, messages.Formatter, debug.Formatter))
