import os
from dotenv import load_dotenv

import discord
from discord.ext import commands, tasks

from storage.json_storage import JsonStorage
from bot.config import ConfigManager
from bot.scoring import ScoreManager
from bot.seasons import SeasonManager
from bot.puzzles import PuzzleManager
from bot.events import setup_events
from bot.commands import setup_commands
from utils.puzzle_embeds import create_puzzle_embed, HOUSE_THEMES

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
DEV_GUILD_ID = os.getenv("GUILD_ID")

if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN in .env")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# STORAGE
storage = JsonStorage(
        config_path="houseledger_config.json",
        scores_path="houseledger_scores.json",
        season_path="houseledger_season.json"
    )


# MANAGERS
config_mgr = ConfigManager(storage=storage)
score_mgr = ScoreManager(storage=storage, config_mgr=config_mgr)
season_mgr = SeasonManager(storage=storage)
puzzle_mgr = PuzzleManager(puzzle_file="puzzles.json")

# BACKGROUND TASKS
@tasks.loop(minutes=1)
async def check_timed_puzzles():
    """Check for expired timed puzzles and update countdowns"""
    try:
        # Check and expire puzzles
        expired = puzzle_mgr.check_and_expire_timed_puzzles()
        
        # Update countdown embeds for active timed puzzles
        for puzzle in puzzle_mgr.get_active_puzzles():
            if not puzzle.get("timed"):
                continue
            
            timed_config = puzzle.get("timed_config", {})
            
            for house_key in ["house_veridian", "feathered_host"]:
                house_config = timed_config.get(house_key, {})
                
                # Skip if already solved
                if house_config.get("solved"):
                    continue
                
                # Get message ID and channel ID
                msg_id = house_config.get("message_id")
                channel_id = puzzle.get(f"{house_key}_channel")
                
                if not msg_id or not channel_id:
                    continue
                
                try:
                    # Get channel and message
                    for guild in bot.guilds:
                        channel = guild.get_channel(int(channel_id))
                        if channel:
                            try:
                                message = await channel.fetch_message(int(msg_id))
                                
                                # Check if expired
                                if puzzle_mgr.is_puzzle_expired_for_house(puzzle["id"], house_key):
                                    # Update embed to show time's up
                                    theme = HOUSE_THEMES.get(house_key, HOUSE_THEMES["house_veridian"])
                                    expired_embed = discord.Embed(
                                        title=f"⏰ TIME'S UP! ⏰",
                                        description=f"{theme['glow']}\n\n**{puzzle['title']}** has expired for {theme['name']}!\n\nBetter luck next time!\n\n{theme['banner']}",
                                        color=0xFF0000,
                                        timestamp=discord.utils.utcnow()
                                    )
                                    expired_embed.set_footer(text=f"{theme['name']} • The challenge has closed")
                                    await message.edit(embed=expired_embed)
                                else:
                                    # Update countdown
                                    time_str = puzzle_mgr.get_time_remaining_str(puzzle["id"], house_key)
                                    current_points = puzzle_mgr.get_timed_points(puzzle["id"], house_key)
                                    
                                    # Create updated embed
                                    updated_embed = create_puzzle_embed(puzzle, house_key, timed=True)
                                    
                                    # Add dynamic countdown field
                                    updated_embed.add_field(
                                        name="⏱️ Current Status",
                                        value=f"{time_str}\n💎 Current Value: **{current_points} points**",
                                        inline=False
                                    )
                                    
                                    await message.edit(embed=updated_embed)
                                    
                            except discord.NotFound:
                                pass  # Message deleted
                            except discord.Forbidden:
                                pass  # No permission
                            break
                            
                except Exception as e:
                    print(f"Error updating timed puzzle {puzzle['id']}: {e}")
                    
    except Exception as e:
        print(f"Error in check_timed_puzzles task: {e}")

@check_timed_puzzles.before_loop
async def before_check_timed_puzzles():
    await bot.wait_until_ready()

# REGISTER
setup_events(bot=bot, tree=tree, dev_guild_id=DEV_GUILD_ID, puzzle_mgr=puzzle_mgr, score_mgr=score_mgr, config_mgr=config_mgr, timed_task=check_timed_puzzles)
setup_commands(tree=tree, bot=bot, config_mgr=config_mgr, score_mgr=score_mgr, season_mgr=season_mgr, puzzle_mgr=puzzle_mgr, dev_guild_id=DEV_GUILD_ID)

# RUN
def main():
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
