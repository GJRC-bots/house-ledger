from __future__ import annotations
from typing import Dict, Any, List, Tuple
import os

import discord

from utils.helpers import embed_kv, title_case_house

def create_diag_embed(
    guild: discord.Guild,
    weighting: Dict[str, Any],
    vr_count: int,
    fh_count: int,
    houses: Dict[str, int],
    show_members: bool
) -> discord.Embed:
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
    return embed

def create_main_standings_embed(guild: discord.Guild, houses: Dict[str, int], config_mgr) -> Tuple[discord.Embed, List[discord.File]]:
    """Creates the main house standings embed with progress bars."""

    ordered_houses = sorted(houses.items(), key=lambda kv: kv[1], reverse=True)
    leading_house = ordered_houses[0][0] if ordered_houses else None

    house_config = {
        "house_veridian": {"color": 0x00FF00},
        "feathered_host": {"color": 0xFFD700},
    }

    files = []
    color = house_config.get(leading_house, {}).get("color", 0xFFD700)
    embed = discord.Embed(
        title="🏆 HOUSE LEDGER — SCOREBOARD 🏆",
        description="*The grand standings of glory and honor*",
        color=color
    )

    # Set winning house thumbnail
    if leading_house in house_config:
        file_path = os.path.join(os.getcwd(), "assets", f"{leading_house}.png")
        if os.path.exists(file_path):
            files.append(discord.File(file_path, filename=f"{leading_house}.png"))
            embed.set_thumbnail(url=f"attachment://{leading_house}.png")

    # Calculate max points for progress bar scaling
    max_points = ordered_houses[0][1] if ordered_houses else 1

    # House standings with progress bars
    standings_text = ""
    for i, (name, pts) in enumerate(ordered_houses):
        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
        house_name = title_case_house(name)

        # Create visual progress bar
        bar_length = 15
        filled = int((pts / max_points) * bar_length) if max_points > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)

        # Point gap indicator
        gap_text = ""
        if i > 0:
            gap = ordered_houses[i-1][1] - pts
            gap_text = f" (−{gap})"

        standings_text += f"{medal} **{house_name}**\n"
        standings_text += f"┃ `{bar}` {pts} pts{gap_text}\n\n"

    embed.add_field(name="\u200B", value="\u200B", inline=False)

    embed.add_field(name="📊 HOUSE STANDINGS", value=standings_text, inline=False)

    embed.add_field(name="\u200B", value="\u200B", inline=False)

    total_points = sum(pts for _, pts in ordered_houses)
    embed.add_field(
        name="📈 TOTAL COMPETITION POINTS",
        value=f"**{total_points}** pts across all houses",
        inline=False
    )

    embed.add_field(name="\u200B", value="\u200B", inline=False)

    embed.set_footer(text="⚖️ Balance will be kept. Glory to the houses!")
    return embed, files

def create_overall_leaderboard_embed(guild: discord.Guild, top_players: List[Tuple[str, int]], config_mgr) -> Tuple[discord.Embed, List[discord.File]]:
    """Creates the overall player leaderboard embed."""

    embed = discord.Embed(
        title="👥 TOP PLAYERS — OVERALL RANKINGS",
        description="The mightiest warriors across all houses",
        color=0x0080FF
    )

    player_text = ""
    for i, (user_id, pts) in enumerate(top_players[:15]):
        member = guild.get_member(int(user_id))
        name = member.display_name if member else f"User {user_id}"

        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1:2d}"

        # Get house affiliation
        player_house = None
        for house_key, role_id in config_mgr.get_house_role_ids().items():
            role = guild.get_role(int(role_id)) if role_id else None
            if role and member and role in member.roles:
                player_house = house_key
                break

        # Determine if player is top of their house
        leader_marker = ""
        if player_house:
            house_members = set()
            for hk, rid in config_mgr.get_house_role_ids().items():
                if hk == player_house:
                    role = guild.get_role(int(rid)) if rid else None
                    if role:
                        house_members = set(str(m.id) for m in role.members)
                    break
            if house_members:
                house_scores = [p for uid, p in top_players if uid in house_members]
                if house_scores and pts == max(house_scores):
                    leader_marker = "👑"

        # Get house name with bracket notation
        house_display = f"[{title_case_house(player_house)}]" if player_house else "[No House]"

        player_text += f"{medal} **{name}** {house_display} • {pts} pts {leader_marker}\n"

    embed.add_field(name="\u200B", value="\u200B", inline=False)
    embed.add_field(name="🎖️ ELITE COMPETITORS", value=player_text, inline=False)
    embed.add_field(name="\u200B", value="\u200B", inline=False)
    embed.set_footer(text="Ranked by total points across all activities")
    return embed, []

def create_house_leaderboard_embed(guild: discord.Guild, houses: Dict[str, int], top_players: List[Tuple[str, int]], config_mgr, house_key: str) -> Tuple[discord.Embed, List[discord.File]]:
    """Creates a house-specific leaderboard embed."""

    house_roles = config_mgr.get_house_role_ids()
    role_id = house_roles.get(house_key)
    if not role_id:
        return None, []

    role = guild.get_role(int(role_id))
    if not role:
        return None, []

    house_members = set(str(m.id) for m in role.members)
    house_top = [(uid, pts) for uid, pts in top_players if uid in house_members][:12]

    if not house_top:
        return None, []

    house_config = {
        "house_veridian": {"color": 0x00FF00},
        "feathered_host": {"color": 0xFFD700},
    }

    config = house_config.get(house_key, {})
    embed = discord.Embed(
        title=f"🏠 {title_case_house(house_key).upper()}",
        description=f"Elite champions of {title_case_house(house_key)}",
        color=config.get("color", 0x808080)
    )

    files = []
    # Add house PNG as thumbnail
    file_path = os.path.join(os.getcwd(), "assets", f"{house_key}.png")
    if os.path.exists(file_path):
        filename = f"{house_key}_house.png"
        files.append(discord.File(file_path, filename=filename))
        embed.set_thumbnail(url=f"attachment://{filename}")

    house_text = ""
    for i, (user_id, pts) in enumerate(house_top):
        member = guild.get_member(int(user_id))
        name = member.display_name if member else f"User {user_id}"
        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1:2d}"

        # Percentage of house's top player
        if i == 0:
            pct_text = "HOUSE CHAMPION"
        else:
            pct = (pts / house_top[0][1] * 100) if house_top[0][1] > 0 else 0
            pct_text = f"{pct:.0f}% of leader"

        house_text += f"{medal} **{name}** • {pts} pts ({pct_text})\n"

    embed.add_field(name="\u200B", value="\u200B", inline=False)
    embed.add_field(name="🎯 TOP PERFORMERS", value=house_text, inline=False)
    embed.add_field(name="\u200B", value="\u200B", inline=False)
    embed.add_field(
        name="👥 HOUSE MEMBERS",
        value=f"{len(house_members)} total members",
        inline=True
    )
    embed.add_field(
        name="⭐ HOUSE TOTAL",
        value=f"{houses.get(house_key, 0)} pts",
        inline=True
    )
    embed.add_field(name="\u200B", value="\u200B", inline=False)

    ordered_houses = sorted(houses.items(), key=lambda kv: kv[1], reverse=True)
    standing = [h[0] for h in ordered_houses].index(house_key) + 1 if house_key in [h[0] for h in ordered_houses] else "?"
    embed.set_footer(text=f"House standing: {standing}/{len(ordered_houses)}")
    return embed, files

def create_standings_embed(guild: discord.Guild, houses: Dict[str, int], top_players: List[Tuple[str, int]], config_mgr) -> Tuple[List[discord.Embed], List[discord.File]]:
    """Creates an epic multi-embed scoreboard system with visual progress bars and house-specific leaderboards."""

    embeds = []
    files = []

    # Main standings
    embed, f = create_main_standings_embed(guild, houses, config_mgr)
    embeds.append(embed)
    files.extend(f)

    # Overall leaderboard
    embed, f = create_overall_leaderboard_embed(guild, top_players, config_mgr)
    embeds.append(embed)
    files.extend(f)

    # House-specific
    for house_key in ["house_veridian", "feathered_host"]:
        embed, f = create_house_leaderboard_embed(guild, houses, top_players, config_mgr, house_key)
        if embed:
            embeds.append(embed)
            files.extend(f)
    
    return embeds, files