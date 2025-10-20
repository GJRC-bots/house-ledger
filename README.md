# House Ledger

## Configuration

Configuration is stored in `houseledger_config.json`. Default settings are created on first run. Key options:

- **Guild ID**: Server ID (auto-detected).
- **Mod Role ID**: Role ID for moderators (users with this role can use admin commands).
- **House Roles**: Role IDs for "veridian" and "feathered_host" houses. Users with these roles are assigned to houses automatically.
- **Channels**: Optional channel IDs for scoreboard, review_queue, and log (not currently used in commands).
- **Weighting**: Enable/disable house-size weighting and set rounding mode.
- **Display**: Channel ID and message ID for auto-updating scoreboard (set via `/set_display_channel`).

To edit manually, stop the bot, modify the JSON, and restart. Use `/config_weighting` for weighting settings.

## Usage

### Commands

#### Basic Commands

| Command | Description |
|---------|-------------|
| `/ping` | Check if the bot is online. |
| `/diag [show_members:true\|false]` | Show diagnostics (guild info, weighting, house roles, member counts, totals). |

#### Configuration Commands

| Command | Description |
|---------|-------------|
| `/config_weighting enabled:true\|false rounding:round\|floor\|ceil` | Enable/disable weighting and set rounding. (Admins/Mods) |
| `/set_display_channel` | Set the channel for auto-updating scoreboard display. (Admins/Mods) |

#### Standings Commands

| Command | Description |
|---------|-------------|
| `/standings_house` | Display all standings embeds (main, overall, house-specific). |
| `/standings_main` | Display main house standings with progress bars. |
| `/standings_overall` | Display overall player leaderboard. |
| `/standings_veridian` | Display House Veridian leaderboard. |
| `/standings_feathered` | Display Feathered Host leaderboard. |

#### Scoring Commands

| Command | Description |
|---------|-------------|
| `/score_add points reason [weighted:true\|false] [house:veridian\|feathered_host \| user:@user]` | Add points to a house or player. (Admins/Mods) |
| `/score_remove points reason [weighted:true\|false] [house:veridian\|feathered_host \| user:@user]` | Remove points from a house or player. (Admins/Mods) |

#### Season Commands

| Command | Description |
|---------|-------------|
| `/season` | Show current season information and stats. |
| `/stage` | Show current stage information, submission stats, and points value. |
| `/submit answer` | Submit an answer for the current stage. Awards points on correct answer. |
| `/advance_season` | Advance to the next season. (Admins/Mods) |
| `/advance_stage` | Advance to the next stage within the current season. (Admins/Mods) |
| `/set_solution solution [points:number]` | Set the correct answer and point value (default: 10) for the current stage. (Admins/Mods) |

#### Puzzle Commands

| Command | Description |
|---------|-------------|
| `/puzzle_list` | View all available puzzles and their status. |
| `/puzzle_activate puzzle_id veridian_channel feathered_channel` | Activate a puzzle in specified house channels. (Admins/Mods) |
| `/puzzle_deactivate puzzle_id` | Deactivate an active puzzle. (Admins/Mods) |
| *Just type your answer* | In puzzle channels, simply type your answer - no command needed! |

### Scoring Logic

- Adding to a player: Adds base points to their score and (if they have a house role) weighted points to their house.
- Adding to a house: Adds weighted points directly to the house total.
- Weighting: If enabled, multiplies points by (largest house member count / target house member count), then rounds.

### Viewing Logs

Audit logs are in `houseledger_scores.json` under the "events" array. Each entry includes timestamp, actor, target, points, etc. No console logs by default.

### Auto-Updating Display

Use `/set_display_channel` to set up a pinned scoreboard in a channel that updates automatically whenever scores change via `/score_add` or `/score_remove`. The display shows all standings embeds and refreshes in real-time.

### Season System

The bot includes a season system for running competitive word-guessing games between houses. Each season contains multiple stages, and users compete to solve them first.

**Key Features:**
- **Seasons**: Long-term competitions with multiple stages
- **Stages**: Individual word-guessing challenges within a season
- **Custom Points**: Each stage can have different point values (default: 10)
- **Submissions**: Users can submit multiple attempts until someone gets it right
- **First Correct Wins**: Once a stage is solved, submissions close automatically
- **No Wrong Answer Logging**: Only correct answers are logged to maintain privacy
- **Weighted Scoring**: Points are weighted by house size if enabled
- **Auto-Updates**: Display board updates automatically when stages are solved

**Typical Workflow:**
1. Admin sets a word: `/set_solution phoenix 25` (25 points for this stage)
2. Users guess: `/submit eagle` (wrong - can try again)
3. User guesses: `/submit phoenix` (correct - wins 25 points, stage closes)
4. Admin advances: `/advance_stage`
5. Admin sets new word: `/set_solution dragon 10` (10 points for this stage)
6. Repeat...

Season data is stored in `houseledger_season.json`. Use `/season` and `/stage` to view current progress, `/submit` to participate, and admin commands to manage the competition.

### Puzzle System

The bot includes an independent puzzle system that runs parallel to seasons/stages. Puzzles are special challenges that can be activated at any time for bonus points.

**Key Features:**
- **Independent System**: Puzzles don't affect season/stage progression
- **JSON Configuration**: All puzzles defined in `puzzles.json`
- **House-Specific Channels**: Each puzzle displays in dedicated channels for both houses
- **Beautiful Embeds**: Themed embeds with house colors and emojis (⚔️ for Veridian, 🪶 for Feathered Host)
- **Natural Submission**: Users just type their answer in the channel - no command needed
- **First Correct Wins**: Only one house can solve each puzzle
- **Custom Points**: Each puzzle has its own point value
- **Auto-Close**: Puzzles deactivate automatically when solved

**How It Works:**
1. Admin activates puzzle: `/puzzle_activate puzzle_1 #veridian-puzzles #feathered-puzzles`
2. Beautiful embed appears in both house channels with the challenge
3. House members type their answers directly in the channel
4. First correct answer wins the points for their house
5. Celebration embed appears, puzzle closes automatically

**Puzzle Submission:**
- No slash command required - just type your answer
- Case-insensitive matching
- Wrong answers show brief "not quite" message (auto-deletes after 5s)
- Correct answer triggers celebration, awards points, updates scoreboard

**Strategic Uses:**
- Bonus challenges during seasons
- Tie-breakers when houses are close
- Special events or themed puzzles
- Multi-day challenges
- Mix of difficulty levels for variety

Puzzle configuration is stored in `puzzles.json`. See `example.puzzles.json` for sample puzzle structure.
