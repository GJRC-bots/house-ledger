import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

from storage.json_storage import JsonStorage
from bot.config import ConfigManager
from bot.scoring import ScoreManager
from bot.seasons import SeasonManager
from bot.puzzles import PuzzleManager
from bot.events import setup_events
from bot.commands import setup_commands

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

# REGISTER
setup_events(bot=bot, tree=tree, dev_guild_id=DEV_GUILD_ID, puzzle_mgr=puzzle_mgr, score_mgr=score_mgr, config_mgr=config_mgr)
setup_commands(tree=tree, bot=bot, config_mgr=config_mgr, score_mgr=score_mgr, season_mgr=season_mgr, puzzle_mgr=puzzle_mgr, dev_guild_id=DEV_GUILD_ID)

# RUN
def main():
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
