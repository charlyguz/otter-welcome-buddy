from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context


class CommandTemplate(commands.Cog):
    """
    Refer to this template when adding a new command for the bot,
    once done, call it on the cogs.py file
    Commands:
        my_group my_command
        my_group my_group_2 my_command_2
    """

    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @commands.group(invoke_without_command=True)
    async def my_group(self, ctx: Context) -> None:
        """
        CommandTemplate will send the help when no final command is invoked
        """
        await ctx.send_help(ctx.command)

    @my_group.command()  # type: ignore
    async def my_command(self, _: Context) -> None:
        """!my_group my_command"""

    @my_group.group(invoke_without_command=True)  # type: ignore
    async def my_group_2(self, ctx: Context) -> None:
        """
        CommandTemplate will send the help when no final command is invoked
        """
        await ctx.send_help(ctx.command)

    @my_group_2.command()  # type: ignore
    async def my_command_2(self, _: Context) -> None:
        """!my_group my_group_2 my_command_2"""


async def setup(bot: Bot) -> None:
    """Required setup method"""
    await bot.add_cog(CommandTemplate(bot))
