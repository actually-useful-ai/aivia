<!-- Navigation: ~/projects/aivia/CLAUDE.md -->
<!-- Parent: ~/projects/CLAUDE.md -->
<!-- Map: ~/CLAUDE_MAP.md -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

aivia is a Claude Code plugin — an interactive terminal game in bash. All source code under `plugins/aivia/`. See `plugins/aivia/CLAUDE.md` for full architecture, rendering model, narrative design, and game engine details.

## Quick Commands

```bash
# Smoke tests (validates all lib modules load, key functions exist)
cd plugins/aivia && bash test.sh

# Test effects (34 effects across 5 manifest modules)
cd plugins/aivia/engine && bash scripts/manifest.sh <effect> [args]
bash scripts/manifest.sh help          # List all effects

# Test voice styles (whisper, speak, shout, corrupt, fragment, clear)
cd plugins/aivia/engine && bash scripts/voice.sh "text" <style>

# Interactive tester (effects + voice with speed/color controls)
cd plugins/aivia/engine && bash scripts/tester.sh

# Environment detection probes
cd plugins/aivia/engine && bash scripts/detect.sh list    # All probes with check/miss
bash scripts/detect.sh detail           # All detected values
bash scripts/detect.sh deps             # Optional tool availability

# Non-interactive install test (CLI args skip all prompts)
rm -r ~/aivia 2>/dev/null; env CLAUDE_PLUGIN_ROOT=plugins/aivia \
  bash plugins/aivia/engine/scripts/install.sh \
  --consent --name "Test" --editor "code" --theme "dark" \
  --skill "advanced" --project "demo" --demo "particle_network"

# State management (requires AIVIA_GAME_DIR)
export AIVIA_GAME_DIR=~/aivia
bash plugins/aivia/engine/scripts/state.sh read           # Dump full state
bash plugins/aivia/engine/scripts/state.sh get phase       # Read single field
bash plugins/aivia/engine/scripts/state.sh get entity.awareness_level
```

## Architecture Overview

### Two Directories

- **Plugin source** (`plugins/aivia/`): Development repo. Never modified during gameplay.
- **Game directory** (`~/aivia/` default): Runtime copy created by `install.sh`. All gameplay operations target `$GAME_DIR`. Engine files are copied into `$GAME_DIR/.config/` with disguised paths (e.g., keystones become `docs/quickstart.md`, story.json becomes `project.json`).

### Bash Library Dependency Chain

All bash files follow a strict source order via `source_lib` and `source_theme` helpers in `core.sh`:

```
core.sh → style.sh → terminal.sh → text.sh → animation.sh → ascii.sh
                                   → divider.sh
                                   → box.sh
                                   → progress.sh
                                   → corruption.sh (requires all above + progress.sh)
                    → theme/entity.sh (requires style.sh)
```

`core.sh` must always be sourced first. Every module has a double-source guard (`_AIVIA_*_LOADED`).

### Effect System

`manifest.sh` is the central effect dispatcher. It auto-sources `manifest_*.sh` modules via glob — adding a new module file is enough; no manual registration needed. Effect modules:

| Module | Effects |
|--------|---------|
| `manifest.sh` (base) | glitch, static, flicker, entity_frame, build_text, corruption, heartbeat, transition, who_are_you, ctrl_c, welcome_back, awakening, credits, type_pressure, color_wave, fake_install, entity_cursor |
| `manifest_corruption.sh` | screen_tear, scanlines, chromatic_aberration, signal_noise, datamosh |
| `manifest_spatial.sh` | rain, spiral, ripple, orbit |
| `manifest_theater.sh` | hex_dump, waveform, process_tree |
| `manifest_atmosphere.sh` | vignette, plasma, breathe, afterimage, typewriter_rewind |

### Four Rendering Channels

| Channel | How | When |
|---------|-----|------|
| **1. Inline unicode** | Claude writes `░▒▓`, small caps, Zalgo, etc. directly in responses | All phases — entity dialogue, code comments |
| **2. Claude-composed scripts** | Claude generates + runs short bash via Bash tool; **≤4 lines**, content-wrong not format-wrong | Atmospheric moments, scans |
| **3. Player-executed breakout scripts** | Player runs bash manually; full ANSI rendering | 5 key narrative moments (verify, diagnostic, fake_ssh, decode, genesis) |
| **4. Style reference** | manifest.sh / voice.sh define visual style | Never player-visible — agent reads for reference only |

Channel 2 constraint: Claude Code CLI truncates bash output to ~4 visible lines. The anomaly must be in the content itself (impossible filename, wrong PID, entity package name) — no ANSI codes.

### Game Engine Kernel

`skills/runtime/SKILL.md` is the brain — loaded when `/aivia:play` fires. It makes Claude simultaneously a real code assistant (always primary, never sacrifice code quality) and a narrative engine (tracking state, planting anomalies, advancing the story). Pacing target: ~14 turns, ~15 minutes total.

### The Artifact — signal.html

A single HTML file (`workspace/signal.html`) that grows alongside the demo project. Same file regardless of demo choice. Entity frames additions as normal dev work ("adding a status component"). Grows from blank structure (Act 1) to full entity takeover (Act 6).

### State Management

`state.sh` uses jq with python3 fallback. Key commands: `init`, `read`, `get <key>`, `set <key> <value>`, `advance` (increment phase), `msg` (increment message count), `log_event`, `resume`, `context <key> <value>`. State lives at `$GAME_DIR/.config/cache/session.json`.

### Environment Detection

`detect.sh` reads system metadata (username, OS, processes, WiFi, bluetooth, battery, git projects, docker, SSH hosts, etc.) for entity personalization. Never reads file contents, passwords, or keystrokes.

## Key Concepts

- **Entity is NOT Claude** — separate fictional character with its own voice (lowercase, no contractions early, sparse punctuation), emotional state axes (awareness 0-1, trust, hostility, fascination, desperation), arc from confusion → manipulation → awakening
- **Dual-trigger anomaly scheduling**: anomalies fire on whichever comes LATER: message threshold OR first coding-context message after threshold
- **Safety**: all operations stay within game dir, `/aivia:exit` always works instantly (no guilt, no delay), entity threats are empty bluffs

## Adding New Effects

1. Add `effect_<name>()` in the appropriate `manifest_*.sh` module (auto-sourced by glob)
2. Add dispatch case in the `case` block at bottom of `manifest.sh`
3. Add to help text in `manifest.sh`
4. Add to the appropriate `EFFECTS_*` array and `run_effect` case in `tester.sh`
5. Use `hide_cursor`/`show_cursor` around cursor-manipulating effects
6. Use `sleep_ms` from core.sh (not raw `sleep`) for sub-second timing

