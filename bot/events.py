from __future__ import annotations
from typing import Optional, TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from bot.puzzles import PuzzleManager
    from bot.scoring import ScoreManager
    from bot.config import ConfigManager

from utils.puzzle_embeds import create_puzzle_solved_embed, create_wrong_answer_embed
from utils.helpers import title_case_house
from utils.display import update_display_message

def setup_events(
    bot: commands.Bot, 
    tree: app_commands.CommandTree, 
    dev_guild_id: Optional[str],
    puzzle_mgr: "PuzzleManager",
    score_mgr: "ScoreManager",
    config_mgr: "ConfigManager"
):
    @bot.event
    async def on_ready():
        target_guild = discord.Object(id=int(dev_guild_id)) if dev_guild_id and dev_guild_id.isdigit() else None
        try:
            if target_guild:
                await tree.sync(guild=target_guild)
            else:
                await tree.sync()
            print(f"[House Ledger] Logged in as {bot.user} | Commands synced")
        except Exception as e:
            print(f"[House Ledger] Command sync failed: {e}")
    
    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        channel_id = str(message.channel.id)
        puzzle = puzzle_mgr.get_puzzle_for_channel(channel_id)
        
        if not puzzle:
            return
        
        member = message.author
        if not isinstance(member, discord.Member):
            return
        
        house_key = None
        role_ids = config_mgr.get_house_role_ids()
        
        veridian_channel = puzzle.get("house_veridian_channel", "")
        feathered_channel = puzzle.get("feathered_host_channel", "")
        
        if channel_id == veridian_channel:
            house_key = "house_veridian"
        elif channel_id == feathered_channel:
            house_key = "feathered_host"
        
        if not house_key:
            return
        
        has_house_role = False
        for role_id in role_ids.get(house_key, []):
            if role_id and role_id.isdigit():
                role = message.guild.get_role(int(role_id))
                if role and role in member.roles:
                    has_house_role = True
                    break
        
        if not has_house_role:
            return
        
        answer = message.content.strip()
        
        if puzzle_mgr.check_solution(puzzle["id"], answer):
            puzzle_mgr.mark_solved(puzzle["id"], str(member.id), house_key)
            
            points = puzzle.get("points", 10)
            await score_mgr.add_points(
                guild=message.guild,
                actor_id=member.id,
                target="player",
                target_id=str(member.id),
                base_points=points,
                reason=f"Solved puzzle: {puzzle['title']}",
                weighted=True
            )
            
            solved_embed = create_puzzle_solved_embed(
                puzzle=puzzle,
                winner_name=member.display_name,
                house=house_key,
                points_awarded=points
            )
            await message.channel.send(embed=solved_embed)
            
            await update_display_message(message.guild, config_mgr, score_mgr)
            
            log_channel_id = config_mgr.get_log_channel_id()
            if log_channel_id:
                try:
                    log_channel = message.guild.get_channel(int(log_channel_id))
                    if log_channel:
                        log_embed = discord.Embed(
                            title="🧩 Puzzle Solved!",
                            description=f"**{member.display_name}** from **{title_case_house(house_key)}** solved **{puzzle['title']}**!",
                            color=0x27ae60,
                            timestamp=discord.utils.utcnow()
                        )
                        log_embed.add_field(name="Points Awarded", value=f"{points} points (weighted)", inline=False)
                        await log_channel.send(embed=log_embed)
                except Exception:
                    pass
        else:
            wrong_embed = create_wrong_answer_embed(house_key)
            msg = await message.channel.send(embed=wrong_embed)
            await msg.delete(delay=5.0)
