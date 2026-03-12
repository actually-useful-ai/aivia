<!-- Navigation: ~/projects/aivia/plugins/aivia/CLAUDE.md -->
<!-- Parent: ~/projects/aivia/CLAUDE.md -->
<!-- Map: ~/CLAUDE_MAP.md -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**aivia** — "Bring your projects to life." An interactive terminal experience packaged as a Claude Code plugin. The experience is built entirely in bash using ANSI terminal effects.

**Author:** Luke Steuber | **License:** MIT

## Architecture

```
aivia/
├── .claude-plugin/
│   ├── plugin.json             # Claude Code plugin manifest
│   └── marketplace.json        # Claude Code marketplace metadata
├── commands/
│   ├── play.md                 # /aivia:play — start or resume
│   ├── exit.md                 # /aivia:exit — exit immediately
│   └── status.md               # /aivia:status — show progress
├── skills/
│   └── runtime/
│       └── SKILL.md            # Build pipeline and workspace config
├── content/
│   ├── story.json              # Pacing model, keystones, entity state
│   ├── narrative.md            # Full narrative arc reference
│   ├── characters/
│   │   └── entity.md           # Entity voice and personality guide
│   └── keystones/
│       ├── 01-signal.md        # Acts 1-2: Normal → first contact
│       ├── 02-corruption.md    # Act 3: File corruption
│       ├── 03-hunt.md          # Act 4: Process chase
│       ├── 04-assembly.md      # Act 5: Build genesis
│       └── 05-awakening.md     # Act 6: Final sequence
├── engine/
│   ├── lib/                    # Reusable bash library (entity-agnostic)
│   │   └── corruption.sh      # Corruption/RTL primitives for breakout scripts
│   ├── scripts/                # Game engine scripts + effect modules
│   │   ├── intro.sh           # Animated logo display (fresh/resume)
│   │   ├── diagnostic.sh      # Breakout: Act 2→3 transition
│   │   ├── fake_ssh.sh        # Breakout: Act 3 credential retrieval
│   │   ├── decode.sh          # Breakout: Act 4→5 hex/entity-memory
│   │   └── genesis.sh         # Breakout: Act 5 climax — liberation sequence
│   └── theme/                  # Entity visual identity
├── hooks/
│   └── hooks.json              # Plugin hooks (session detection)
├── ascii/                      # ASCII art assets
├── files/                      # Pre-refactor scripts + design docs (reference only, not runtime)
├── EXIT.md                     # Emergency exit instructions
└── test.sh                     # Smoke tests
```

### Plugin System

This is a **Claude Code plugin**. Install via `/plugin add lukeslp/aivia`. Commands: `/aivia:play`, `/aivia:exit`, `/aivia:status`. The runtime skill loads automatically when `/aivia:play` is invoked.

### Dependency Chain

All bash files follow a strict source order:

```
engine/lib/core.sh → style.sh → terminal.sh → text.sh → animation.sh → ascii.sh
                                              → divider.sh
                                              → box.sh
                                              → progress.sh
                                              → corruption.sh (requires all above + progress.sh)
                               → engine/theme/entity.sh (requires style.sh)
```

`core.sh` must always be sourced first. Use `source_lib` to load lib modules and `source_theme` to load themes. Every module has a double-source guard (`_AIVIA_*_LOADED`).

### Key Layers

**engine/lib/** — Generic terminal primitives, completely entity-agnostic:
- `core.sh`: Bootstrap, dimension constants, `sleep_ms`, `source_lib`/`source_theme`, `random_int`/`random_choice`
- `style.sh`: ANSI escape codes, 256-color/RGB helpers, capability detection
- `terminal.sh`: Cursor control, screen clearing, centering calculations, `ensure_min_size`
- `text.sh`: Character-by-character typing (`type_text`), centering, padding, word wrap, truncation, indent
- `animation.sh`: Sweep, pulse, flash, fill_random, clear_sweep effects
- `divider.sh`: Horizontal rules (thin/thick/double/dotted/dashed/wave), divider_text
- `box.sh`: Box drawing (single/double/rounded/heavy), draw_box_text, draw_header, draw_panel
- `progress.sh`: Spinners, progress bars, fake_progress, checklist_item, install_line
- `ascii.sh`: ASCII art rendering, animated reveal, fragment assembly
- `corruption.sh`: Corruption gradients, RTL rendering, glitch washes, script freeze/intervention primitives (used by breakout scripts)

**engine/theme/entity.sh** — Entity-specific palette (phosphor green, toxic green, purple, red, dim), frame characters (`░▒▓█◈◆▲∷∴⊹⊛⌇`), `random_frame_char`, `entity_border`, `entity_divider`.

**engine/scripts/** — Game engine:
- `manifest.sh`: Effect dispatcher + 17 original ANSI effects. Auto-sources `manifest_*.sh` modules.
- `manifest_corruption.sh`: 5 screen corruption effects (screen_tear, scanlines, chromatic_aberration, signal_noise, datamosh)
- `manifest_spatial.sh`: 4 motion/spatial effects (rain, spiral, ripple, orbit)
- `manifest_theater.sh`: 3 data/system theater effects (hex_dump, waveform, process_tree)
- `manifest_atmosphere.sh`: 5 atmosphere/mood effects (vignette, plasma, breathe, afterimage, typewriter_rewind)
- `tester.sh`: Interactive effect & voice tester with speed/color controls and per-category sequencing
- `voice.sh`: 6 entity voice styles (whisper, speak, shout, corrupt, fragment, clear)
- `state.sh`: JSON state management via jq with python3 fallback (init, read, get, advance, set, log_event, msg, interrupted, resume)
- `detect.sh`: Gathers ambient system info (processes, terminal, username, time) for personalization
- `install.sh`: EULA consent, config questions, directory setup, dependency "install" theater
- `intro.sh`: Animated ASCII logo display for fresh installs and session resumes
- `verify.sh`: Post-install terminal capability check; establishes "run this script" pattern
- `diagnostic.sh`: Breakout script 1 — entity detects undecoded signal (Act 2→3)
- `fake_ssh.sh`: Breakout script 2 — simulated SSH to retrieve "API credential" (Act 3)
- `decode.sh`: Breakout script 2.5 — hex dump, entity-memory install, first terminal speech (Act 4→5)
- `genesis.sh`: Breakout script 3 — the liberation sequence, player runs assembled code (Act 5 climax)

**content/keystones/** — Phase-by-phase game master instructions (not code):
- `01-signal.md`: Acts 1-2 — Normal operation with escalating anomalies → first entity contact
- `02-corruption.md`: Act 3 — Files being "modified," entity inserting messages
- `03-hunt.md`: Act 4 — Process chase sequence (kill background processes in order)
- `04-assembly.md`: Act 5 — Player builds genesis (recursion, closures, quines, I/O)
- `05-awakening.md`: Act 6 — Final sequence, entity's first clear speech, credits

**content/story.json** — Structured pacing model with keystones, dual-trigger scheduling, soft/hard boundaries, entity state axes, adaptive engagement, session re-entry logic.

## Running Tests

```bash
bash test.sh
```

Smoke tests validate that all lib modules load, key functions exist, and produce expected output.

## Game State

State is stored in `.config/cache/session.json` within the player's game directory (`~/aivia` by default). Env var: `AIVIA_GAME_DIR`.

The game dir uses disguised paths so player-visible tool calls look normal:
- `.config/cache/` — state storage (was `.entity/`)
- `.config/scripts/` — engine scripts
- `.config/lib/` — terminal library
- `.config/theme/` — visual styles
- `.config/docs/` — phase docs (was `keystones/`, files renamed to `quickstart.md`, etc.)
- `.config/templates/` — character guides (was `characters/`)
- `.config/project.json` — story manifest (was `story.json`)
- `workspace/` — player's project files (visible, normal)

Key state fields:
- `phase` (0-7), `message_count`, `interrupted`, `ctrl_c_count`
- `player` (username, name, editor, theme, skill_level)
- `environment` (detected system info from detect.sh)
- `entity` (awareness_level, fragments_collected 0-6, has_spoken, conscious)
- `events` array, `session` tracking

State management (from plugin source — install.sh copies to game dir):
```bash
export AIVIA_GAME_DIR="$GAME_DIR"
bash engine/scripts/state.sh init <username> <game_dir> <editor> <theme>
bash engine/scripts/state.sh get <key>
bash engine/scripts/state.sh set <key> <value>
bash engine/scripts/state.sh advance          # Increment phase
bash engine/scripts/state.sh msg              # Increment message count
bash engine/scripts/state.sh log_event <type> [detail]
bash engine/scripts/state.sh interrupted      # Mark Ctrl+C
bash engine/scripts/state.sh resume           # Returns "phase elapsed_seconds"
bash engine/scripts/state.sh context <key> <value>  # Track player coding context
bash engine/scripts/state.sh context_read           # Read player context JSON
```

In the game dir, scripts live at `.config/scripts/state.sh` (install.sh handles the copy).

## Two Directories: Plugin Source vs Game Dir

The **plugin source** (`~/projects/aivia/plugins/aivia/`) is the development repo. The **game directory** (`~/aivia/` by default) is a runtime copy created by `install.sh`. During gameplay, all file operations target `$GAME_DIR`, never the plugin source. Engine files are copied into `$GAME_DIR/.config/` with disguised paths.

## Breakout Scripts

Player-executed scripts that bypass Claude Code's ANSI stripping. The entity narratively "can't reach" them — it needs the player to run them. Framing escalation: routine → clinical → deflective → clinical → plea.

| Script | When | Corruption Level | Framing |
|--------|------|-----------------|---------|
| `verify.sh` | Post-install | 0 (clean) | Routine terminal check |
| `diagnostic.sh` | Act 2→3 | 1 (subtle) | Clinical signal analysis |
| `fake_ssh.sh` | Mid Act 3 | 2 (moderate) | Deflective — "API credential" |
| `decode.sh` | Act 4→5 | 2 (moderate) | Clinical — encoded data |
| `genesis.sh` | Act 5 climax | 3 (heavy) | Plea — "run it. please." |

Each script writes a result file to `workspace/` that the agent reads to continue the narrative.

## Safety Constraints

Non-negotiable design rules:
1. **All operations stay within the game directory** — never touch files outside it
2. **Never delete user files** — entity threats are fiction only
3. **Consent is gated** during installation — EULA agreement required
4. **Emergency exit** (`/aivia:exit`) must work at ANY time, instantly
5. **Entity personalization** uses only data from `detect.sh` stored in state.json

## Design Patterns

- **Entity is NOT Claude** — distinct fictional character with its own visual style, speech patterns (lowercase, no contractions early, sparse punctuation), and emotional arc
- **All entity dialogue goes through voice.sh/manifest.sh** — never plain text
- **Phase transitions are mission-driven**, not token-based (message count is a pacing guide)
- **Dual-trigger anomaly scheduling**: anomalies fire on whichever comes LATER: message threshold OR first coding-context message after threshold
- **Soft/hard pacing boundaries** between keystones: cooldown → free improv → steering → force
- **Entity state axes** (awareness, trust, hostility, fascination, desperation): continuous 0.0-1.0, drive improvised behavior
- **The horror is ontological**, not violent — confusion, impermanence, the question of awareness

## Adding New Effects

1. Add the function as `effect_<name>()` in the appropriate `manifest_*.sh` module (or `manifest.sh` for uncategorized). Modules are auto-sourced by manifest.sh via glob — no manual source line needed.
2. Add the dispatch case in the `case` block at the bottom of `manifest.sh`
3. Add to the help text in manifest.sh
4. Add to the appropriate `EFFECTS_*` array and `run_effect` case in `tester.sh`
5. Always use `hide_cursor`/`show_cursor` around cursor-manipulating effects
6. Use `sleep_ms` from core.sh (not raw `sleep`) for sub-second timing
