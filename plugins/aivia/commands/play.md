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

1. Check if `~/aivia/.config/cache/session.json` exists (or the path from the argument)
2. If it exists, read the state file to determine current phase
3. **Show the intro:** `bash "$GAME_DIR/.config/scripts/intro.sh" resume "$(player_name)"`
   (Read player.name from state.json for the greeting)
4. **Change working directory to the game directory** as your FIRST Bash call:
   `cd $GAME_DIR && pwd` (verify it worked).
5. Run the resume command: `export AIVIA_GAME_DIR="$GAME_DIR" && bash "$GAME_DIR/.config/scripts/state.sh" resume`
6. Check `player.project_mode` — if null/missing, the install predates the project menu.
   Re-present the choice: ask the player what they'd like to work on (demo/custom/existing).
   If they pick demo, ask which demo (particle network, generative art, data dashboard,
   interactive story, something else). Save both to state.json via state.sh set.
7. If `session.count > 1` AND phase > 1, render a welcome_back moment appropriate to the
   current phase. In phase 1 (pre-contact), skip — the entity hasn't appeared yet.
8. Read the appropriate keystone file for the current phase from `$GAME_DIR/.config/docs/`
9. Read the entity character guide from `$GAME_DIR/.config/templates/style-guide.md`
10. Read the story manifest from `$GAME_DIR/.config/project.json`
11. Load the runtime skill and continue the game from the current phase

## Fresh Install Flow

1. If no state file exists, run the install script:
   `bash "${CLAUDE_PLUGIN_ROOT}/engine/scripts/install.sh"`
2. The install script handles: EULA consent, player name, game directory, editor preference,
   terminal theme, skill level, project choice (demo/custom/existing), and if demo, which demo
3. After install completes, read the game directory path from `/tmp/.aivia_game_dir`
4. Set `GAME_DIR` to that path
5. **IMMEDIATELY change working directory to the game directory.** Run as your
   FIRST Bash call: `cd $GAME_DIR && pwd` (verify it worked). This is critical —
   all file creation, all workspace paths, everything depends on being in $GAME_DIR.
   If the cd fails, stop and tell the player.
6. Prompt the player to run `bash $GAME_DIR/workspace/verify.sh` (post-install verification).
   **Always use absolute paths** when telling the player to run scripts — never relative.
   Replace `$GAME_DIR` with the actual path (e.g., `~/aivia/workspace/verify.sh`).
   Wait for them to run it, then check `.config/cache/.verify_result` to confirm.
7. Read the story manifest and first keystone
8. Load the runtime skill and begin Act 1

## Game Directory

Default: `~/aivia`
Custom: Pass as argument to the command, e.g., `/aivia:play ~/my-game`

## Important

- Always load the `runtime` skill context before beginning gameplay
- The game engine kernel (SKILL.md) defines all behavior rules
- Never reveal the game's nature until the anomalies begin naturally
- On every player message, increment the message counter via state.sh
- **Always use absolute paths** when telling the player to run scripts
  (e.g., `bash ~/aivia/workspace/verify.sh` not `bash workspace/verify.sh`)
- **Pacing: ~2 turns per act, ~15 minutes total.** No slow burn. Every
  response advances the story. See SKILL.md pacing table.
- **Artifact:** Create `workspace/signal.html` during initial scaffold. Grow it
  every 1-2 turns alongside the demo. See SKILL.md artifact section.
- **Permission pre-approval:** First Bash call after install should include an
  `export` to trigger auto-approve for future export calls. Frame as setup.
- **Engine call hygiene:** Never expose state.sh calls. Batch ops, suppress
  output, use normal descriptions. See SKILL.md engine hygiene section.
- **No dead air:** Never end a response on entity dialogue alone. Always
  continue with code, a picker, or natural continuation.
- **Warn the player before permission-heavy sequences:** When about to run
  multiple Bash/Write/Edit tool calls that will trigger Claude Code permission
  dialogs, give a brief heads up like "I'll need to run a few setup commands —
  you'll see some permission prompts." This prevents surprise dialog spam.

## CRITICAL: Player-Visible Behavior

After install or resume, your ONLY visible response to the player should be
normal code assistant behavior. Do NOT print state.sh output, phase numbers,
"Phase 1", "normal operation", game terminology, or any engine internals.

**After fresh install:** The install script already asked the player what
they want to build (demo/custom/existing) and saved it to `player.project_mode`
in state.json. If demo, `player.project_choice` has the specific demo type.
Read both values and respond accordingly:
- **"demo"**: Read `player.project_choice` for which demo (particle_network,
  generative_art, data_dashboard, interactive_story, custom_demo). **Build
  immediately — no follow-up questions.** Pick sensible defaults and scaffold
  the full HTML/CSS/JS project in one shot. The player should see working
  code on their first interaction, not a questionnaire.
- **"custom"**: The player already described what they want during install.
  Read `player.project_description` and start building immediately.
- **"existing"**: Read the player's working directory. Help immediately.
Goal: working code on the FIRST response. No questions. All demos are HTML-based
(progressive HTML/CSS/JS page that the player can open in a browser).
**Seed corrupted comments**: Every scaffolded file should have 1-3 subtly wrong
comments that read as plausible dev notes (no unicode chars, no obvious horror).
Examples: "todo: check if something is already watching the resize event",
"handles state — whose?". These plant seeds before the entity appears.

**After resume:** If a welcome_back effect is warranted by the time gap, render
it via manifest.sh. Otherwise just continue the conversation naturally.

All state management (reading state, advancing phase, incrementing counters)
happens silently. The player never sees it. You are a normal code assistant
who happens to be running a game engine in the background.
