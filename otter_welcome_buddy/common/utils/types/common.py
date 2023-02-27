from typing import TypeAlias

import discord

DiscordChannelType: TypeAlias = (
    discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel
)
