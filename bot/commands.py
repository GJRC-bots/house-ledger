from __future__ import annotations
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.config import ConfigManager
from bot.scoring import ScoreManager
from utils.helpers import is_admin_or_mod_check, embed_kv, title_case_house

def setup_commands(
    *,
    tree: app_commands.CommandTree,
    bot: commands.Bot,
    config_mgr: ConfigManager,
    score_mgr: ScoreManager,
    dev_guild_id: Optional[str]
):
    guild_kw = {}
    if dev_guild_id and dev_guild_id.isdigit():
        guild_kw = {"guild": discord.Object(id=int(dev_guild_id))}

    # Basic
    @tree.command(name="ping", description="Check if House Ledger is awake.", **guild_kw)
    async def ping(interaction: discord.Interaction):
        await interaction.response.send_message("House Ledger is awake. ✅", ephemeral=True)

    @tree.command(name="diag", description="Diagnostics.", **guild_kw)
    @app_commands.describe(show_members="If true, show house role member counts.")
    async def diag(interaction: discord.Interaction, show_members: bool = True):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("Run this inside a server.", ephemeral=True)
            return

        # member counts
        vr_count = fh_count = 0
        if show_members:
            house_ids = config_mgr.get_house_role_ids()
            vr = guild.get_role(int(house_ids.get("house_veridian") or 0)) if house_ids.get("house_veridian") else None
            fh = guild.get_role(int(house_ids.get("feathered_host") or 0)) if house_ids.get("feathered_host") else None
            vr_count = len(vr.members) if vr else 0
            fh_count = len(fh.members) if fh else 0

        weighting = config_mgr.data.get("weighting", {})
        houses = score_mgr.get_house_totals()

        embed = discord.Embed(title="HOUSE LEDGER — DIAGNOSTICS", color=0x0E171B)
        embed.add_field(name="Guild", value=f"{guild.name} ({guild.id})", inline=False)
        embed.add_field(name="Weighting", value=embed_kv({
            "enabled": str(weighting.get("enabled", False)),
            "rounding": weighting.get("rounding", "round")
        }), inline=False)
        if show_members:
            embed.add_field(name="Member Counts", value=embed_kv({
                "House Veridian": vr_count,
                "Feathered Host": fh_count
            }), inline=False)
        embed.add_field(name="House Totals", value=embed_kv({
            "House Veridian": houses.get("house_veridian", 0),
            "Feathered Host": houses.get("feathered_host", 0)
        }), inline=False)
        embed.set_footer(text="All Offerings are recorded. Balance will be kept.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    #  Config: weighting
    @tree.command(name="config_weighting", description="Enable/disable weighting + rounding.", **guild_kw)
    @is_admin_or_mod_check(config_mgr)
    @app_commands.describe(
        enabled="Turn house-size weighting on or off.",
        rounding="How to round weighted house points."
    )
    @app_commands.choices(rounding=[
        app_commands.Choice(name="round", value="round"),
        app_commands.Choice(name="floor", value="floor"),
        app_commands.Choice(name="ceil", value="ceil")
    ])
    async def config_weighting(interaction: discord.Interaction, enabled: bool, rounding: app_commands.Choice[str]):
        config_mgr.set_weighting(enabled=enabled, rounding=rounding.value)
        await interaction.response.send_message(
            f"Weighting **{ 'ENABLED' if enabled else 'DISABLED' }**, rounding = **{rounding.value}**.",
            ephemeral=True
        )

    #  Standings
    @tree.command(name="standings_house", description="Show current house leaderboard.", **guild_kw)
    async def standings_house(interaction: discord.Interaction):
        houses = score_mgr.get_house_totals()
        ordered = sorted(houses.items(), key=lambda kv: kv[1], reverse=True)
        lines = [f"**{title_case_house(name)}** — {pts} pts" for name, pts in ordered]
        embed = discord.Embed(title="HOUSE LEDGER — STANDINGS", description="\n".join(lines), color=0xB0A77C)
        await interaction.response.send_message(embed=embed)

    #  Scoring
    @tree.command(name="score_add", description="Add points to a house or player.", **guild_kw)
    @is_admin_or_mod_check(config_mgr)
    @app_commands.describe(
        house="House to add points to (house_veridian/feathered_host) OR leave blank if you target a user.",
        user="Player to add points to",
        points="Points to add (integer).",
        reason="Reason (shown in audit log).",
        weighted="Apply house-size weighting (default false)."
    )
    async def score_add(
        interaction: discord.Interaction,
        points: int,
        reason: str,
        weighted: bool = False,
        house: Optional[str] = None,
        user: Optional[discord.Member] = None
    ):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("Run this inside a server.", ephemeral=True)
            return

        if (house is None) == (user is None):
            await interaction.response.send_message(
                "Pick exactly one target: `house` **or** `user`.", ephemeral=True
            )
            return

        if user:
            target = "player"
            target_id = str(user.id)
        else:
            hk = (house or "").strip().lower()
            if hk not in ("veridian", "feathered_host"):
                await interaction.response.send_message("House must be `veridian` or `feathered_host`.", ephemeral=True)
                return
            target = "house"
            target_id = hk

        player_award, house_award = await score_mgr.add_points(
            guild=guild,
            actor_id=interaction.user.id,
            target=target,
            target_id=target_id,
            base_points=points,
            reason=reason,
            weighted=weighted
        )
        msg = f"Added **{points}** base points. House applied: **{house_award}**, Player applied: **{player_award}**."
        await interaction.response.send_message(msg)

    @tree.command(name="score_remove", description="Remove points from a house or player.", **guild_kw)
    @is_admin_or_mod_check(config_mgr)
    @app_commands.describe(
        house="House to remove points from (house_veridian/feathered_host) OR leave blank if you target a user.",
        user="Player to remove points from",
        points="Points to remove (integer).",
        reason="Reason (shown in audit log).",
        weighted="Apply house-size weighting (default false)."
    )
    async def score_remove(
        interaction: discord.Interaction,
        points: int,
        reason: str,
        weighted: bool = False,
        house: Optional[str] = None,
        user: Optional[discord.Member] = None
    ):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("Run this inside a server.", ephemeral=True)
            return

        if (house is None) == (user is None):
            await interaction.response.send_message(
                "Pick exactly one target: `house` **or** `user`.", ephemeral=True
            )
            return

        if user:
            target = "player"
            target_id = str(user.id)
        else:
            hk = (house or "").strip().lower()
            if hk not in ("house_veridian", "feathered_host"):
                await interaction.response.send_message("House must be `house_veridian` or `feathered_host`.", ephemeral=True)
                return
            target = "house"
            target_id = hk

        player_award, house_award = await score_mgr.remove_points(
            guild=guild,
            actor_id=interaction.user.id,
            target=target,
            target_id=target_id,
            base_points=points,
            reason=reason,
            weighted=weighted
        )
        msg = f"Removed **{points}** base points. House applied: **{house_award}**, Player applied: **{player_award}**."
        await interaction.response.send_message(msg)
