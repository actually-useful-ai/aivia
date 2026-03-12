---
name: play
description: Start or resume Eldritch Awakening
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
3. Run the resume command: `export ELDRITCH_GAME_DIR="$GAME_DIR" && bash "$GAME_DIR/scripts/state.sh" resume`
4. If `session.count > 1`, run the welcome_back visual effect:
   `bash "$GAME_DIR/scripts/manifest.sh" welcome_back <phase> <elapsed_seconds>`
5. Read the appropriate keystone file for the current phase from `$GAME_DIR/keystones/`
6. Read the entity character guide from `$GAME_DIR/characters/entity.md`
7. Read the story manifest from `$GAME_DIR/story.json`
8. Load the Eldritch Awakening skill and continue the game from the current phase

## Fresh Install Flow

1. If no state file exists, run the install script:
   `bash "${CLAUDE_PLUGIN_ROOT}/engine/scripts/install.sh"`
2. The install script handles consent, configuration, directory setup, and state init
3. After install completes, read the game directory path from `/tmp/.eldritch_game_dir`
4. Set `GAME_DIR` to that path
5. Read the story manifest and first keystone
6. Load the Eldritch Awakening skill and begin Act 1

## Game Directory

Default: `~/aivia`
Custom: Pass as argument to the command, e.g., `/aivia:play ~/my-game`

## Important

- Always load the `eldritch` skill context before beginning gameplay
- The game engine kernel (SKILL.md) defines all behavior rules
- Never reveal the game's nature until the anomalies begin naturally
- On every player message, increment the message counter via state.sh
