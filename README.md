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

- **`/ping`**: Check if the bot is online. (Everyone)
- **`/diag`**: Show diagnostics (guild info, weighting, house roles, member counts, totals). (Everyone; `show_members` defaults to true)
- **`/config_weighting`**: Enable/disable weighting and set rounding (round/floor/ceil). (Admins/Mods)
- **`/standings_house`**: Display all standings embeds (main, overall, house-specific). (Everyone)
- **`/standings_main`**: Display main house standings with progress bars. (Everyone)
- **`/standings_overall`**: Display overall player leaderboard. (Everyone)
- **`/standings_veridian`**: Display House Veridian leaderboard. (Everyone)
- **`/standings_feathered`**: Display Feathered Host leaderboard. (Everyone)
- **`/set_display_channel`**: Set the channel for auto-updating scoreboard display. (Admins/Mods)
- **`/score_add`**: Add points to a house or player. Specify house (veridian/feathered_host), user, points, reason, and optional weighting. (Admins/Mods)
- **`/score_remove`**: Remove points from a house or player. Same as add but subtracts. (Admins/Mods)

### Command Reference

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

### Scoring Logic

- Adding to a player: Adds base points to their score and (if they have a house role) weighted points to their house.
- Adding to a house: Adds weighted points directly to the house total.
- Weighting: If enabled, multiplies points by (largest house member count / target house member count), then rounds.

### Viewing Logs

Audit logs are in `houseledger_scores.json` under the "events" array. Each entry includes timestamp, actor, target, points, etc. No console logs by default.

### Auto-Updating Display

Use `/set_display_channel` to set up a pinned scoreboard in a channel that updates automatically whenever scores change via `/score_add` or `/score_remove`. The display shows all standings embeds and refreshes in real-time.
