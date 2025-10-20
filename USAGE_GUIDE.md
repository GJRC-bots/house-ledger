# House Ledger Bot - Usage Guide

## Core Functionality

This Discord bot manages a competition between two houses with word-guessing stages.

### Admin Commands

#### 1. Start/Manage Seasons
- `/advance_season` - Start a new season (creates Season 2, Season 3, etc.)
- `/season` - View current season information

#### 2. Set the Word to Guess
- `/set_solution <solution>` - Set the word/answer for the current stage
  - Example: `/set_solution phoenix`
  - The solution is case-insensitive and trimmed of whitespace

#### 3. Manage Stages
- `/advance_stage` - Move to the next stage within the current season
- `/stage` - View current stage information and stats

#### 4. Configure Display
- `/set_display_channel` - Set up auto-updating scoreboard in current channel
  - Creates a pinned message that updates when points change

#### 5. Manual Scoring
- `/score_add` - Add points to a house or player
- `/score_remove` - Remove points from a house or player

### User Commands

#### Submit Answers
- `/submit <answer>` - Try to guess the word for the current stage
  - Example: `/submit phoenix`
  - **Correct answer**: Awards 10 points (weighted), updates display, logs to log channel
  - **Incorrect answer**: Shows "Incorrect. Try again!" (no logging of wrong attempts)
  - **Already solved**: Shows message that stage is complete

### View Standings
- `/standings_main` - Main scoreboard with progress bars
- `/standings_overall` - Overall player leaderboard
- `/standings_veridian` - House Veridian specific leaderboard
- `/standings_feathered` - Feathered Host specific leaderboard
- `/standings_house` - Comprehensive standings view

### Other Commands
- `/ping` - Check if bot is online
- `/diag` - Diagnostics (admin only)
- `/config_weighting` - Configure house-size weighting (admin only)

## Typical Workflow

1. **Start a Season**: `/advance_season`
2. **Set the Word**: `/set_solution mysecretword`
3. **Users Guess**: Users run `/submit theirguess`
4. **Correct Guess**: 
   - User gets 10 points (weighted)
   - Stage is marked as completed
   - Log channel gets success notification
   - Display board auto-updates
5. **Next Stage**: `/advance_stage`
6. **Repeat**: Set new word and continue

## Key Features

- ✅ No logging of incorrect attempts (privacy-friendly)
- ✅ Auto-updating display board on correct answers
- ✅ Weighted scoring based on house sizes
- ✅ Multi-embed scoreboard system
- ✅ Stage progression tracking
- ✅ Season management
- ✅ Comprehensive leaderboards

## Configuration

Edit `houseledger_config.json`:
```json
{
  "guild_id": "your_guild_id",
  "mod_role_id": "moderator_role_id",
  "house_roles": {
    "house_veridian": "role_id",
    "feathered_host": "role_id"
  },
  "channels": {
    "log": "channel_id_for_logs"
  },
  "weighting": {
    "enabled": false,
    "rounding": "round"
  }
}
```

## Notes

- Solutions are stored in `houseledger_season.json`
- Scores are stored in `houseledger_scores.json`
- All answers are case-insensitive
- Stages can only be solved once (first correct answer wins)
- Points are awarded with house-size weighting if enabled
