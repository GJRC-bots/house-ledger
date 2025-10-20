from __future__ import annotations
from typing import Dict, Any, Optional
import discord

HOUSE_THEMES = {
    "house_veridian": {
        "color": 0x00FF88,
        "emoji": "⚔️",
        "name": "House Veridian",
        "accent": "✦",
        "banner": "═══════════════════════════════",
        "glow": "⋆｡‧˚ʚ ⚔️ ɞ˚‧｡⋆"
    },
    "feathered_host": {
        "color": 0xFFD700,
        "emoji": "🪶",
        "name": "Feathered Host",
        "accent": "✧",
        "banner": "═══════════════════════════════",
        "glow": "⋆｡‧˚ʚ 🪶 ɞ˚‧｡⋆"
    }
}

def create_puzzle_embed(puzzle: Dict[str, Any], house: str) -> discord.Embed:
    """Create a beautiful puzzle embed for a specific house"""
    theme = HOUSE_THEMES.get(house, HOUSE_THEMES["house_veridian"])
    
    embed = discord.Embed(
        title=f"{theme['emoji']} {puzzle['title']} {theme['emoji']}",
        description=f"{theme['glow']}\n\n{puzzle['description']}\n\n{theme['banner']}",
        color=theme['color'],
        timestamp=discord.utils.utcnow()
    )
    
    # Puzzle content
    embed.add_field(
        name=f"{theme['accent']} The Challenge {theme['accent']}",
        value=puzzle['puzzle_content'],
        inline=False
    )
    
    # Points value
    embed.add_field(
        name="💎 Reward",
        value=f"**{puzzle['points']} Points**",
        inline=True
    )
    
    # Hint (if available)
    if puzzle.get('hint'):
        embed.add_field(
            name="💡 Hint",
            value=f"||{puzzle['hint']}||",
            inline=True
        )
    
    # Image (if available)
    if puzzle.get('image_url'):
        embed.set_image(url=puzzle['image_url'])
    
    # Footer
    footer_text = puzzle.get('footer_text', 'Submit your answer in this channel')
    embed.set_footer(
        text=f"{theme['name']} • {footer_text}",
        icon_url=None
    )
    
    embed.add_field(
        name="\u200b",
        value=f"{theme['banner']}\n*Submit your answer by typing it in this channel*\n{theme['banner']}",
        inline=False
    )
    
    return embed


def create_puzzle_solved_embed(puzzle: Dict[str, Any], winner_name: str, house: str, points_awarded: int) -> discord.Embed:
    """Create a celebration embed when puzzle is solved"""
    theme = HOUSE_THEMES.get(house, HOUSE_THEMES["house_veridian"])
    
    embed = discord.Embed(
        title=f"🎉 PUZZLE SOLVED! 🎉",
        description=f"{theme['glow']}\n\n**{winner_name}** from **{theme['name']}** has cracked the code!\n\n{theme['banner']}",
        color=theme['color'],
        timestamp=discord.utils.utcnow()
    )
    
    embed.add_field(
        name=f"{theme['emoji']} Puzzle",
        value=puzzle['title'],
        inline=True
    )
    
    embed.add_field(
        name="💎 Points Awarded",
        value=f"**{points_awarded}** points",
        inline=True
    )
    
    embed.add_field(
        name="✨ Solution",
        value=f"||{puzzle['solution']}||",
        inline=False
    )
    
    embed.set_footer(
        text=f"{theme['name']} • Glory to the house!",
        icon_url=None
    )
    
    return embed


def create_puzzle_list_embed(puzzles: list, house: str = "house_veridian") -> discord.Embed:
    """Create an embed showing all available puzzles"""
    theme = HOUSE_THEMES.get(house, HOUSE_THEMES["house_veridian"])
    
    embed = discord.Embed(
        title=f"{theme['emoji']} Available Puzzles {theme['emoji']}",
        description=f"{theme['glow']}\n\n{theme['banner']}",
        color=theme['color'],
        timestamp=discord.utils.utcnow()
    )
    
    for puzzle in puzzles:
        status = "🟢 Active" if puzzle.get('active') else "⚫ Inactive"
        solved = "✅ Solved" if puzzle.get('solved_by') else "❌ Unsolved"
        
        value = f"**Status:** {status}\n"
        value += f"**Progress:** {solved}\n"
        value += f"**Points:** {puzzle.get('points', 10)}\n"
        value += f"**ID:** `{puzzle['id']}`"
        
        embed.add_field(
            name=f"{theme['accent']} {puzzle['title']}",
            value=value,
            inline=True
        )
    
    embed.set_footer(
        text=f"{theme['name']} • Use /puzzle_activate to start a puzzle",
        icon_url=None
    )
    
    return embed


def create_wrong_answer_embed(house: str) -> discord.Embed:
    """Create an embed for wrong answers"""
    theme = HOUSE_THEMES.get(house, HOUSE_THEMES["house_veridian"])
    
    embed = discord.Embed(
        title=f"{theme['accent']} Not Quite... {theme['accent']}",
        description=f"That's not the correct answer. Keep trying!\n\n*The puzzle awaits your wisdom...*",
        color=theme['color']
    )
    
    embed.set_footer(text=f"{theme['name']} • Persistence brings glory")
    
    return embed


def create_puzzle_activated_embed(puzzle: Dict[str, Any], house: str) -> discord.Embed:
    """Create an announcement embed when puzzle is activated"""
    theme = HOUSE_THEMES.get(house, HOUSE_THEMES["house_veridian"])
    
    embed = discord.Embed(
        title=f"🔔 NEW PUZZLE ACTIVATED! 🔔",
        description=f"{theme['glow']}\n\n**{puzzle['title']}** is now live!\n\nHead to your house's puzzle channel to participate!\n\n{theme['banner']}",
        color=theme['color'],
        timestamp=discord.utils.utcnow()
    )
    
    embed.add_field(
        name="💎 Points at Stake",
        value=f"**{puzzle['points']} Points**",
        inline=True
    )
    
    embed.add_field(
        name="🏆 Be the First",
        value="First correct answer wins!",
        inline=True
    )
    
    embed.set_footer(
        text=f"{theme['name']} • Glory awaits!",
        icon_url=None
    )
    
    return embed
