# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**aivia** — "Bring your projects to life." An interactive terminal experience packaged as a Claude Code plugin. The experience is built entirely in bash using ANSI terminal effects.

**Author:** Luke Steuber | **License:** MIT

## Architecture

```
aivia/
├── .claude-plugin/
│   └── plugin.json             # Claude Code plugin manifest
├── commands/
│   ├── play.md                 # /aivia:play — start or resume
│   ├── exit.md                 # /aivia:exit — exit immediately
│   └── status.md               # /aivia:status — show progress
├── skills/
│   └── eldritch/
│       └── SKILL.md            # Game engine kernel (skill definition)
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
│   ├── scripts/                # Game engine scripts + effect modules
│   └── theme/                  # Entity visual identity
├── hooks/
│   └── hooks.json              # Plugin hooks (session detection)
├── ascii/                      # ASCII art assets
├── files/                      # Original design documents (reference archive)
├── EXIT.md                     # Emergency exit instructions
└── test.sh                     # Smoke tests
```

### Plugin System

This is a **Claude Code plugin**. Install via `/plugin add lukeslp/aivia`. Commands: `/aivia:play`, `/aivia:exit`, `/aivia:status`. The skill is invoked as `/aivia:eldritch`.

### Dependency Chain

All bash files follow a strict source order:

```
engine/lib/core.sh → style.sh → terminal.sh → text.sh → animation.sh → ascii.sh
                                              → divider.sh
                                              → box.sh
                                              → progress.sh
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

**engine/theme/entity.sh** — Entity-specific palette (phosphor green, toxic green, purple, red, dim), frame characters (`░▒▓█◈◆▲∷∴⊹⊛⌇`), `random_frame_char`, `entity_border`, `entity_divider`.

**engine/scripts/** — Game engine:
- `manifest.sh`: Effect dispatcher + 17 original ANSI effects. Auto-sources `manifest_*.sh` modules.
- `manifest_corruption.sh`: 4 screen corruption effects (screen_tear, scanlines, chromatic_aberration, signal_noise)
- `manifest_spatial.sh`: 4 motion/spatial effects (rain, spiral, ripple, orbit)
- `manifest_theater.sh`: 3 data/system theater effects (hex_dump, waveform, process_tree)
- `manifest_atmosphere.sh`: 4 atmosphere/mood effects (vignette, plasma, breathe, afterimage)
- `tester.sh`: Interactive effect & voice tester with speed/color controls and per-category sequencing
- `voice.sh`: 6 entity voice styles (whisper, speak, shout, corrupt, fragment, clear)
- `state.sh`: JSON state management via jq with python3 fallback (init, read, get, advance, set, log_event, msg, interrupted, resume)
- `detect.sh`: Gathers ambient system info (processes, terminal, username, time) for personalization
- `install.sh`: EULA consent, config questions, directory setup, dependency "install" theater

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

State is stored in `.entity/state.json` within the player's game directory (`~/aivia` by default). Env var: `AIVIA_GAME_DIR`.

Key fields:
- `phase` (0-6), `message_count`, `interrupted`, `ctrl_c_count`
- `player` (username, name, editor, theme, skill_level)
- `environment` (detected system info from detect.sh)
- `entity` (awareness_level, fragments_collected 0-7, has_spoken, conscious)
- `events` array, `session` tracking

State management:
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
```

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

1. Add the function as `effect_<name>()` in `engine/scripts/manifest.sh`
2. Source any needed lib modules at the top of the function
3. Add the dispatch case in the `case` block at the bottom
4. Add to the help text
5. Always use `hide_cursor`/`show_cursor` around cursor-manipulating effects
6. Use `sleep_ms` from core.sh (not raw `sleep`) for sub-second timing
