from __future__ import annotations
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

def setup_events(bot: commands.Bot, tree: app_commands.CommandTree, dev_guild_id: Optional[str]):
    @bot.event
    async def on_ready():
        target_guild = discord.Object(id=int(dev_guild_id)) if dev_guild_id and dev_guild_id.isdigit() else None
        try:
            if target_guild:
                await tree.sync(guild=target_guild)
            else:
                await tree.sync()
        except Exception as e:
            print(f"[House Ledger] Command sync failed: {e}")
        print(f"[House Ledger] Logged in as {bot.user} | Commands synced to "
              f"{'guild ' + dev_guild_id if dev_guild_id else 'GLOBAL'}.")
