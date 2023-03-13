import asyncio
import os

from discord.ext.commands import Bot
from discord.ext.commands import when_mentioned_or
from dotenv import load_dotenv

from otter_welcome_buddy.common.constants import COMMAND_PREFIX
from otter_welcome_buddy.startup import cogs
from otter_welcome_buddy.startup import intents

load_dotenv()


async def main() -> None:
    """Principal function to be called by Docker"""

    bot: Bot = Bot(
        command_prefix=when_mentioned_or(COMMAND_PREFIX),
        intents=intents.get_registered_intents(),
    )

    async with bot:
        await cogs.register_cogs(bot)
        await bot.start(os.environ["DISCORD_TOKEN"])


if __name__ == "__main__":
    asyncio.run(main())
