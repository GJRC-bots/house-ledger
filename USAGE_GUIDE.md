# House Ledger Bot - Usage Guide

## Core Functionality

This Discord bot manages a competition between two houses with word-guessing stages.

### Admin Commands

#### 1. Start/Manage Seasons
- `/advance_season` - Start a new season (creates Season 2, Season 3, etc.)
- `/season` - View current season information

#### 2. Set the Word to Guess

- `/set_solution <solution> [points]` - Set the word/answer for the current stage
  - `solution`: The word to guess (case-insensitive)
  - `points`: Points awarded for solving (optional, default: 10)
  - Example: `/set_solution phoenix` - Worth 10 points (default)
  - Example: `/set_solution dragon 25` - Worth 25 points
  - The solution is case-insensitive and trimmed of whitespace

#### 3. Manage Stages

- `/advance_stage` - Move to the next stage within the current season
- `/stage` - View current stage information, stats, and points value

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
  - **Correct answer**: Awards points (default 10, or custom amount set by admin), updates display, logs to log channel
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

1. **Set the Word**: `/set_solution mysecretword` (default 10 points)
   - OR `/set_solution mysecretword 25` (custom 25 points)
2. **Users Guess**: Users run `/submit theirguess`
3. **Correct Guess**:
   - User gets points (weighted by house size if enabled)
   - Stage is marked as completed
   - Log channel gets success notification
   - Display board auto-updates
4. **Next Stage**: `/advance_stage`
5. **Repeat**: Set new word with different point values and continue

## Notes

- All answers are case-insensitive
- Stages can only be solved once (first correct answer wins)
- Points are awarded with house-size weighting if enabled
- Different stages can have different point values (e.g., easy = 5 points, hard = 25 points)
- Default point value is 10 if not specified
