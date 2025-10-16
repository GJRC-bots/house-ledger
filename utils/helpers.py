from __future__ import annotations
from typing import Dict, Any, Callable
import math

import discord
from discord import app_commands

from bot.config import ConfigManager

def is_admin_or_mod_check(config_mgr: ConfigManager) -> Callable:
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user is None or not isinstance(interaction.user, discord.Member):
            return False
        member: discord.Member = interaction.user

        if member.guild_permissions.manage_guild:
            return True

        mod_role_id = config_mgr.get_mod_role_id()
        if mod_role_id and discord.utils.get(member.roles, id=int(mod_role_id)):
            return True

        await interaction.response.send_message("You do not have permission to run this command.", ephemeral=True)
        return False
    return app_commands.check(predicate)

def embed_kv(d: Dict[str, Any]) -> str:
    return "\n".join([f"**{k}**: {v}" for k, v in d.items()])

def title_case_house(key: str) -> str:
    if key.lower() == "feathered_host":
        return "Feathered Host"
    if key.lower() == "house_veridian":
        return "House Veridian"
    return key.title()

def apply_rounding(value: float, mode: str) -> int:
    if mode == "floor":
        return math.floor(value)
    if mode == "ceil":
        return math.ceil(value)
    return round(value)
