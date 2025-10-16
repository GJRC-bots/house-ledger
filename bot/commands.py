from __future__ import annotations
from importlib.metadata import files
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.config import ConfigManager
from bot.scoring import ScoreManager
from utils.helpers import is_admin_or_mod_check, embed_kv, title_case_house
from utils.embeds import create_diag_embed, create_standings_embed, create_main_standings_embed, create_overall_leaderboard_embed, create_house_leaderboard_embed
from utils.display import update_display_message

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

        embed = create_diag_embed(guild, weighting, vr_count, fh_count, houses, show_members)
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
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("Run this inside a server.", ephemeral=True)
            return

        houses = score_mgr.get_house_totals()
        top_players = score_mgr.get_top_players(10)
        embeds, files = create_standings_embed(guild, houses, top_players, config_mgr)
        await interaction.response.send_message(embeds=embeds, files=files)

    @tree.command(name="standings_main", description="Show main house standings with progress bars.", **guild_kw)
    async def standings_main(interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("Run this inside a server.", ephemeral=True)
            return

        houses = score_mgr.get_house_totals()
        embed, files = create_main_standings_embed(guild, houses, config_mgr)
        await interaction.response.send_message(embed=embed, files=files)

    @tree.command(name="standings_overall", description="Show overall player leaderboard.", **guild_kw)
    async def standings_overall(interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("Run this inside a server.", ephemeral=True)
            return

        top_players = score_mgr.get_top_players(15)
        embed, files = create_overall_leaderboard_embed(guild, top_players, config_mgr)
        await interaction.response.send_message(embed=embed, files=files)

    @tree.command(name="standings_veridian", description="Show House Veridian leaderboard.", **guild_kw)
    async def standings_veridian(interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("Run this inside a server.", ephemeral=True)
            return

        houses = score_mgr.get_house_totals()
        top_players = score_mgr.get_top_players(15)
        embed, files = create_house_leaderboard_embed(guild, houses, top_players, config_mgr, "house_veridian")
        if embed:
            await interaction.response.send_message(embed=embed, files=files)
        else:
            await interaction.response.send_message("House Veridian data not available.", ephemeral=True)

    @tree.command(name="standings_feathered", description="Show Feathered Host leaderboard.", **guild_kw)
    async def standings_feathered(interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("Run this inside a server.", ephemeral=True)
            return

        houses = score_mgr.get_house_totals()
        top_players = score_mgr.get_top_players(15)
        embed, files = create_house_leaderboard_embed(guild, houses, top_players, config_mgr, "feathered_host")
        if embed:
            await interaction.response.send_message(embed=embed, files=files)
        else:
            await interaction.response.send_message("Feathered Host data not available.", ephemeral=True)

    @tree.command(name="set_display_channel", description="Set the channel for auto-updating scoreboard.", **guild_kw)
    @is_admin_or_mod_check(config_mgr)
    async def set_display_channel(interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("Run this inside a server.", ephemeral=True)
            return

        houses = score_mgr.get_house_totals()
        top_players = score_mgr.get_top_players(15)
        embeds, files = create_standings_embed(guild, houses, top_players, config_mgr)

        await interaction.response.send_message(embeds=embeds, files=files)
        message = await interaction.original_response()

        # Pin the message
        try:
            await message.pin()
        except discord.Forbidden:
            await interaction.followup.send("Couldn't pin the message (missing permissions).", ephemeral=True)

        config_mgr.set_display_settings(str(interaction.channel_id), str(message.id))
        await interaction.followup.send(f"Display channel set to {interaction.channel.mention}. The scoreboard will auto-update here.", ephemeral=True)

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
            if hk not in ("house_veridian", "feathered_host"):
                await interaction.response.send_message("House must be `house_veridian` or `feathered_host`.")
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

        if target == "player":
            member = guild.get_member(int(target_id))
            user_name = member.display_name if member else f"User {target_id}"
            house_key = None
            if member:
                ids = config_mgr.get_house_role_ids()
                vr_id = str(ids.get("house_veridian") or "").strip()
                fh_id = str(ids.get("feathered_host") or "").strip()
                if vr_id and any(r.id == int(vr_id) for r in member.roles):
                    house_key = "house_veridian"
                elif fh_id and any(r.id == int(fh_id) for r in member.roles):
                    house_key = "feathered_host"
            house_name = title_case_house(house_key) if house_key else "No House"
            msg = f"Added **{points}** base points to **{user_name}** (**{house_name}**). House applied: **{house_award}**, Player applied: **{player_award}**."
        else:
            house_name = title_case_house(target_id)
            msg = f"Added **{points}** base points to **{house_name}**. House applied: **{house_award}**."

        await interaction.response.send_message(msg)
        await update_display_message(guild, config_mgr, score_mgr)

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

        if target == "player":
            member = guild.get_member(int(target_id))
            user_name = member.display_name if member else f"User {target_id}"
            house_key = None
            if member:
                ids = config_mgr.get_house_role_ids()
                vr_id = str(ids.get("house_veridian") or "").strip()
                fh_id = str(ids.get("feathered_host") or "").strip()
                if vr_id and any(r.id == int(vr_id) for r in member.roles):
                    house_key = "house_veridian"
                elif fh_id and any(r.id == int(fh_id) for r in member.roles):
                    house_key = "feathered_host"
            house_name = title_case_house(house_key) if house_key else "No House"
            msg = f"Removed **{points}** base points from **{user_name}** (**{house_name}**). House applied: **{house_award}**, Player applied: **{player_award}**."
        else:
            house_name = title_case_house(target_id)
            msg = f"Removed **{points}** base points from **{house_name}**. House applied: **{house_award}**."

        await interaction.response.send_message(msg)
        await update_display_message(guild, config_mgr, score_mgr)
