from __future__ import annotations
from typing import TYPE_CHECKING

import discord

from utils.embeds import create_standings_embed

if TYPE_CHECKING:
    from bot.config import ConfigManager
    from bot.scoring import ScoreManager


async def update_display_message(guild: discord.Guild, config_mgr: ConfigManager, score_mgr: ScoreManager) -> None:
    """Update the auto-display message with current standings."""
    channel_id = config_mgr.get_display_channel_id()
    message_id = config_mgr.get_display_message_id()

    if not channel_id or not message_id:
        return
    
    try:
        channel = guild.get_channel(int(channel_id))
        if not channel or not isinstance(channel, discord.TextChannel):
            return

        message = await channel.fetch_message(int(message_id))
        houses = score_mgr.get_house_totals()
        top_players = score_mgr.get_top_players(15)
        embeds, files = create_standings_embed(guild, houses, top_players, config_mgr)
        
        await message.edit(embeds=embeds, attachments=files)

    except (discord.NotFound, discord.Forbidden, ValueError, Exception):
        pass