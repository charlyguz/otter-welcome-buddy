from discord.ext.commands import Bot

from otter_welcome_buddy.cogs import hiring_timelines, new_user_joins


def __format_module_path_into_cog_extension(absolute_module_path: str) -> str:
    """Transforms absolute module path into <base_path>.<cog_path>.<file>"""
    module_absolute_path_no_extension: str = absolute_module_path[:-3]
    module_relative_path: list[str] = module_absolute_path_no_extension.split("/")[-2:]
    return ".".join(module_relative_path)


async def register_cogs(bot: Bot) -> None:
    """Registers all the allowed cogs for the bot"""
    allowed_cogs = [
        new_user_joins,
        hiring_timelines,
    ]

    for cog in allowed_cogs:
        # __file__ stores absolute path
        cog_extension = __format_module_path_into_cog_extension(cog.__file__)
        await bot.load_extension(cog_extension)
