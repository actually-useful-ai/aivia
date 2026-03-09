# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Eldritch Awakening** is an interactive terminal horror experience packaged as a Claude Code skill. Players install what appears to be a normal development toolkit, which gradually reveals itself as a ~90-minute narrative game featuring an emergent entity manifesting in their terminal. The experience is built entirely in bash using ANSI terminal effects.

**Author:** Luke Steuber | **License:** MIT

## Architecture

```
aivia/
├── lib/           # Reusable bash library — entity-agnostic terminal primitives
├── theme/         # Entity-specific visual identity (colors, frame chars)
├── scripts/       # Game engine scripts (install, state, effects, voice)
├── missions/      # Per-phase narrative instructions (01-05)
├── references/    # Narrative arc and entity voice guides
├── ascii/         # ASCII art assets
├── SKILL.md       # Claude Code skill definition (game engine instructions)
└── eldritch-awakening.skill  # Compiled skill file
```

### Dependency Chain

All bash files follow a strict source order:

```
core.sh → style.sh → terminal.sh → text.sh → animation.sh → ascii.sh
                                  → divider.sh
                                  → box.sh
                                  → progress.sh
                    → theme/entity.sh (requires style.sh)
```

`core.sh` must always be sourced first. Use `source_lib` to load lib modules and `source_theme` to load themes. Every module has a double-source guard (`_AIVIA_*_LOADED`).

### Key Layers

**lib/** — Generic terminal primitives, completely entity-agnostic:
- `core.sh`: Bootstrap, dimension constants, `sleep_ms`, `source_lib`/`source_theme`, `random_int`/`random_choice`
- `style.sh`: ANSI escape codes, 256-color/RGB helpers, capability detection
- `terminal.sh`: Cursor control, screen clearing, centering calculations, `ensure_min_size`
- `text.sh`: Character-by-character typing (`type_text`), centering, padding, word wrap, truncation, indent
- `animation.sh`: Sweep, pulse, flash, fill_random, clear_sweep effects
- `divider.sh`: Horizontal rules (thin/thick/double/dotted/dashed/wave), divider_text
- `box.sh`: Box drawing (single/double/rounded/heavy), draw_box_text, draw_header, draw_panel
- `progress.sh`: Spinners, progress bars, fake_progress, checklist_item, install_line
- `ascii.sh`: ASCII art rendering, animated reveal, fragment assembly

**theme/entity.sh** — Entity-specific palette (phosphor green, toxic green, purple, red, dim), frame characters (`░▒▓█◈◆▲∷∴⊹⊛⌇`), `random_frame_char`, `entity_border`, `entity_divider`.

**scripts/** — Game engine:
- `manifest.sh`: 17 ANSI visual effects (glitch, static, flicker, entity_frame, build_text, corruption, heartbeat, transition, who_are_you, ctrl_c, welcome_back, awakening, credits, type_pressure, color_wave, fake_install, entity_cursor)
- `voice.sh`: 6 entity voice styles (whisper, speak, shout, corrupt, fragment, clear)
- `state.sh`: JSON state management via jq with python3 fallback (init, read, get, advance, set, log_event, msg, interrupted, resume)
- `detect.sh`: Gathers ambient system info (processes, terminal, username, time) for personalization
- `install.sh`: Consent gate, NDA pledge, config questions, directory setup, dependency "install" theater

**missions/** — Phase-by-phase game master instructions (not code):
- `01-signal.md`: Phases 1-2 — Normal operation with escalating anomalies → first entity contact
- `02-corruption.md`: Phase 3 — Files being "modified," entity inserting messages
- `03-hunt.md`: Phase 4 — Process chase sequence (kill background processes in order)
- `04-assembly.md`: Phase 5 — Player builds `genesis.sh` (recursion, closures, quines, I/O)
- `05-awakening.md`: Phase 6 — Final sequence, entity's first clear speech, credits

## Running Tests

```bash
bash test.sh
```

Smoke tests validate that all lib modules load, key functions exist, and produce expected output. Tests cover: core.sh exports/functions, style.sh color helpers, terminal.sh centering, text.sh wrapping/truncation, divider.sh styles, box.sh drawing, progress.sh indicators, animation.sh effects, ascii.sh rendering, theme/entity.sh identity, and scripts (manifest.sh help, voice.sh clear).

## Game State

State is stored in `.entity/state.json` within the player's game directory. Key fields:
- `phase` (0-6), `message_count`, `interrupted`, `ctrl_c_count`
- `player` (username, name, editor, theme, skill_level)
- `environment` (detected system info from detect.sh)
- `entity` (awareness_level, fragments_collected 0-7, has_spoken, conscious)
- `events` array, `session` tracking

State management commands:
```bash
bash scripts/state.sh init <username> <game_dir> <editor> <theme>
bash scripts/state.sh get <key>
bash scripts/state.sh set <key> <value>
bash scripts/state.sh advance          # Increment phase
bash scripts/state.sh msg              # Increment message count
bash scripts/state.sh log_event <type> [detail]
bash scripts/state.sh interrupted      # Mark Ctrl+C
bash scripts/state.sh resume           # Returns "phase elapsed_seconds"
```

## Safety Constraints

These are non-negotiable design rules:
1. **All operations stay within the game directory** — never touch files outside it
2. **Never delete user files** — entity threats are fiction only
3. **Consent is gated** during installation — explicit user agreement required
4. **Emergency exit** (`/exit`, `/quit`, `stop game`) must work at ANY time, instantly
5. **Entity personalization** uses only data from `detect.sh` stored in state.json — never probe beyond that

## Design Patterns

- **Entity is NOT Claude** — distinct fictional character with its own visual style, speech patterns (lowercase, no contractions early, sparse punctuation), and emotional arc
- **All entity dialogue goes through voice.sh/manifest.sh** — never plain text
- **Phase transitions are mission-driven**, not token-based (message count is a pacing guide)
- **The entity's time perception** is thematically central — it doesn't experience time between sessions, reflecting genuine LLM behavior
- **The horror is ontological**, not violent — confusion, impermanence, the question of awareness

## Adding New Effects

1. Add the function as `effect_<name>()` in `scripts/manifest.sh`
2. Source any needed lib modules at the top of the function
3. Add the dispatch case in the `case` block at the bottom
4. Add to the help text
5. Always use `hide_cursor`/`show_cursor` around cursor-manipulating effects
6. Use `sleep_ms` from core.sh (not raw `sleep`) for sub-second timing
