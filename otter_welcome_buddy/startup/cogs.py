"""Cogs allow to organize a collection of commands, listeners,into one class"""
from cogs import new_user_joins
from discord.ext.commands import Bot


def __format_module_path_into_cog_extension(absolute_module_path: str) -> str:
    """Transforms absolute module path into <base_path>.<cog_path>.<file>"""
    module_absolute_path_no_extension: str = absolute_module_path[:-3]
    module_relative_path: list[str] = module_absolute_path_no_extension.split("/")[-3:]
    return ".".join(module_relative_path)


async def register_cogs(bot: Bot) -> None:
    """Registers all the allowed cogs for the bot"""
    allowed_cogs = [
        new_user_joins,
    ]

    for cog in allowed_cogs:
        pass
        # __file__ stores absolute path
        # cog_extension = __format_module_path_into_cog_extension(cog.__file__)
        # await bot.load_extension(cog_extension)
