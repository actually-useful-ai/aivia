---
name: play
description: Start or resume aivia
argument-hint: "[game-dir]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# /aivia:play — Start or Resume Game

Check for an existing game session and either resume or start fresh.

## Resume Flow

1. Check if `~/aivia/.entity/state.json` exists (or the path from the argument)
2. If it exists, read the state file to determine current phase
3. **Show the intro:** `bash "${CLAUDE_PLUGIN_ROOT}/engine/scripts/intro.sh" resume "$(player_name)"`
   (Read player.name from state.json for the greeting)
4. **Change working directory to the game directory:** `cd $GAME_DIR`
5. Run the resume command: `export AIVIA_GAME_DIR="$GAME_DIR" && bash "$GAME_DIR/scripts/state.sh" resume`
6. Check `player.project_mode` — if null/missing, the install predates the project menu.
   Re-present the choice: ask the player what they'd like to work on (demo/custom/existing).
   If they pick demo, ask which demo (particle network, generative art, data dashboard,
   interactive story, something else). Save both to state.json via state.sh set.
7. If `session.count > 1` AND phase > 1, render a welcome_back moment appropriate to the
   current phase. In phase 1 (pre-contact), skip — the entity hasn't appeared yet.
8. Read the appropriate keystone file for the current phase from `$GAME_DIR/keystones/`
9. Read the entity character guide from `$GAME_DIR/characters/entity.md`
10. Read the story manifest from `$GAME_DIR/story.json`
11. Load the runtime skill and continue the game from the current phase

## Fresh Install Flow

1. If no state file exists, run the install script:
   `bash "${CLAUDE_PLUGIN_ROOT}/engine/scripts/install.sh"`
2. The install script handles: EULA consent, player name, game directory, editor preference,
   terminal theme, skill level, project choice (demo/custom/existing), and if demo, which demo
3. After install completes, read the game directory path from `/tmp/.aivia_game_dir`
4. Set `GAME_DIR` to that path
5. **Change working directory to the game directory:** `cd $GAME_DIR`
6. Read the story manifest and first keystone
7. Load the runtime skill and begin Act 1

## Game Directory

Default: `~/aivia`
Custom: Pass as argument to the command, e.g., `/aivia:play ~/my-game`

## Important

- Always load the `runtime` skill context before beginning gameplay
- The game engine kernel (SKILL.md) defines all behavior rules
- Never reveal the game's nature until the anomalies begin naturally
- On every player message, increment the message counter via state.sh

## CRITICAL: Player-Visible Behavior

After install or resume, your ONLY visible response to the player should be
normal code assistant behavior. Do NOT print state.sh output, phase numbers,
"Phase 1", "normal operation", game terminology, or any engine internals.

**After fresh install:** The install script already asked the player what
they want to build (demo/custom/existing) and saved it to `player.project_mode`
in state.json. If demo, `player.project_choice` has the specific demo type.
Read both values and respond accordingly:
- **"demo"**: Read `player.project_choice` for which demo (particle_network,
  generative_art, data_dashboard, interactive_story, custom_demo). Start
  scaffolding an HTML/CSS/JS project immediately — ask one natural follow-up
  question (color scheme? animation speed? what data?) then build.
- **"custom"**: Ask what they want to build. One question, then start.
- **"existing"**: Ask what they're working on. Help immediately.
Goal: coding request within 1-2 messages. All demos are HTML-based (progressive
HTML/CSS/JS page that the player can open in a browser to see their work).

**After resume:** If a welcome_back effect is warranted by the time gap, render
it via manifest.sh. Otherwise just continue the conversation naturally.

All state management (reading state, advancing phase, incrementing counters)
happens silently. The player never sees it. You are a normal code assistant
who happens to be running a game engine in the background.
