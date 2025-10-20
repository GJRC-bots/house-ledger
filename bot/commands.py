from __future__ import annotations
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.config import ConfigManager
from bot.scoring import ScoreManager
from bot.seasons import SeasonManager
from utils.helpers import is_admin_or_mod_check, title_case_house
from utils.embeds import create_diag_embed, create_standings_embed, create_main_standings_embed, create_overall_leaderboard_embed, create_house_leaderboard_embed
from utils.display import update_display_message

def setup_commands(
    *,
    tree: app_commands.CommandTree,
    bot: commands.Bot,
    config_mgr: ConfigManager,
    score_mgr: ScoreManager,
    season_mgr: SeasonManager,
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
        top_players = score_mgr.get_top_players(50)
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
                role_ids = config_mgr.get_house_role_ids()
                for house, role_id_list in role_ids.items():
                    for role_id in role_id_list:
                        if role_id and role_id.isdigit():
                            try:
                                role = guild.get_role(int(role_id))
                                if role and role in member.roles:
                                    house_key = house
                                    break
                            except ValueError:
                                continue
                    if house_key:
                        break
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
                role_ids = config_mgr.get_house_role_ids()
                for house, role_id_list in role_ids.items():
                    for role_id in role_id_list:
                        if role_id and role_id.isdigit():
                            try:
                                role = guild.get_role(int(role_id))
                                if role and role in member.roles:
                                    house_key = house
                                    break
                            except ValueError:
                                continue
                    if house_key:
                        break
            house_name = title_case_house(house_key) if house_key else "No House"
            msg = f"Removed **{points}** base points from **{user_name}** (**{house_name}**). House applied: **{house_award}**, Player applied: **{player_award}**."
        else:
            house_name = title_case_house(target_id)
            msg = f"Removed **{points}** base points from **{house_name}**. House applied: **{house_award}**."

        await interaction.response.send_message(msg)
        await update_display_message(guild, config_mgr, score_mgr)

    # Seasons
    @tree.command(name="season", description="Show current season information.", **guild_kw)
    async def season(interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("Run this inside a server.", ephemeral=True)
            return

        season_stats = season_mgr.get_season_stats()
        stage_stats = season_mgr.get_stage_stats()

        embed = discord.Embed(
            title=f"🏆 {season_stats['season_name']}",
            color=0x3498db
        )

        embed.add_field(
            name="📊 Season Stats",
            value=f"**Total Submissions:** {season_stats['total_submissions']}\n"
                  f"**Stages:** {season_stats['current_stage']}/{season_stats['total_stages']}",
            inline=True
        )

        embed.add_field(
            name="🎯 Current Stage",
            value=f"**{stage_stats['stage_name']}**\n"
                  f"**Submissions:** {stage_stats['total_submissions']}\n"
                  f"**Correct:** {stage_stats['correct_submissions']}\n"
                  f"**Has Solution:** {'✅' if stage_stats['has_solution'] else '❌'}",
            inline=True
        )

        await interaction.response.send_message(embed=embed)

    @tree.command(name="stage", description="Show current stage information.", **guild_kw)
    async def stage(interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("Run this inside a server.", ephemeral=True)
            return

        stage_stats = season_mgr.get_stage_stats()

        embed = discord.Embed(
            title=f"🎯 {stage_stats['stage_name']}",
            color=0x2ecc71 if stage_stats['has_solution'] else 0xe74c3c
        )

        embed.add_field(
            name="📈 Stats",
            value=f"**Total Submissions:** {stage_stats['total_submissions']}\n"
                  f"**Correct Answers:** {stage_stats['correct_submissions']}\n"
                  f"**Solved:** {'✅' if stage_stats['completed'] else '❌'}",
            inline=False
        )

        if stage_stats['has_solution']:
            if stage_stats['completed']:
                embed.add_field(
                    name="✅ Status",
                    value="Stage has been solved! Submissions are closed.",
                    inline=False
                )
            else:
                embed.add_field(
                    name="💡 Status",
                    value="Solution has been set. Submissions are being accepted!",
                    inline=False
                )
        else:
            embed.add_field(
                name="⏳ Status",
                value="Waiting for solution to be set by admin.",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @tree.command(name="submit", description="Submit an answer for the current stage.", **guild_kw)
    @app_commands.describe(answer="Your answer for the current stage")
    async def submit(interaction: discord.Interaction, answer: str):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("Run this inside a server.", ephemeral=True)
            return

        result, was_correct = season_mgr.submit_answer(str(interaction.user.id), answer)
        
        if was_correct:
            await score_mgr.add_points(
                guild=guild,
                actor_id=interaction.user.id,
                target="player",
                target_id=str(interaction.user.id),
                base_points=10,
                reason=f"Solved {season_mgr.get_current_stage().get('name', 'Stage')}",
                weighted=True
            )
        
        log_channel_id = config_mgr.get_log_channel_id()
        if log_channel_id and was_correct:
            try:
                log_channel = guild.get_channel(int(log_channel_id))
                if log_channel:
                    member = guild.get_member(interaction.user.id)
                    user_name = member.display_name if member else f"User {interaction.user.id}"
                    
                    house_name = "No House"
                    if member:
                        role_ids = config_mgr.get_house_role_ids()
                        for house_key, role_id_list in role_ids.items():
                            for role_id in role_id_list:
                                if role_id and role_id.isdigit():
                                    role = guild.get_role(int(role_id))
                                    if role and role in member.roles:
                                        house_name = title_case_house(house_key)
                                        break
                            if house_name != "No House":
                                break
                    
                    stage_name = season_mgr.get_current_stage().get('name', 'Unknown Stage')
                    embed = discord.Embed(
                        title="🎉 Stage Solved!",
                        description=f"**{user_name}** from **{house_name}** has solved **{stage_name}**!",
                        color=0x27ae60,
                        timestamp=interaction.created_at
                    )
                    embed.add_field(name="Points Awarded", value="10 points (weighted)", inline=False)
                    
                    await log_channel.send(embed=embed)
            except Exception:
                pass
        
        if was_correct:
            await update_display_message(guild, config_mgr, score_mgr)
        
        await interaction.response.send_message(result, ephemeral=True)

    @tree.command(name="advance_season", description="Advance to the next season (Admin only).", **guild_kw)
    @is_admin_or_mod_check(config_mgr)
    async def advance_season(interaction: discord.Interaction):
        result = season_mgr.advance_season()
        await interaction.response.send_message(f"✅ {result}", ephemeral=True)

    @tree.command(name="advance_stage", description="Advance to the next stage (Admin only).", **guild_kw)
    @is_admin_or_mod_check(config_mgr)
    async def advance_stage(interaction: discord.Interaction):
        result = season_mgr.advance_stage()
        await interaction.response.send_message(f"✅ {result}", ephemeral=True)

    @tree.command(name="set_solution", description="Set the solution for the current stage (Admin only).", **guild_kw)
    @is_admin_or_mod_check(config_mgr)
    @app_commands.describe(solution="The correct answer for the current stage")
    async def set_solution(interaction: discord.Interaction, solution: str):
        result = season_mgr.set_stage_solution(solution)
        await interaction.response.send_message(f"✅ {result}", ephemeral=True)
