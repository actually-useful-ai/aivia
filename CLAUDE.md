<!-- Navigation: ~/projects/aivia/CLAUDE.md -->
<!-- Parent: ~/projects/CLAUDE.md -->
<!-- Map: ~/CLAUDE_MAP.md -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

aivia is a Claude Code plugin — an interactive terminal game in bash. All source code under `plugins/aivia/`. See `plugins/aivia/CLAUDE.md` for full architecture, rendering model, narrative design, and game engine details.

## Repository Structure

```
aivia/
├── .claude-plugin/           # Plugin manifest (plugin.json) + marketplace metadata
├── plugins/aivia/            # THE PLUGIN — all source code lives here
│   ├── commands/             # /aivia:play, /aivia:exit, /aivia:status
│   ├── skills/runtime/       # Game engine kernel (SKILL.md — the brain)
│   ├── content/              # story.json, narrative.md, keystones/, characters/
│   ├── engine/
│   │   ├── lib/              # Reusable bash library (entity-agnostic)
│   │   ├── scripts/          # Game engine: state, effects, detection, breakout scripts
│   │   └── theme/            # Entity visual identity (entity.sh)
│   ├── hooks/                # hooks.json + intercept.sh (session detection only)
│   ├── ascii/                # ASCII art assets
│   └── files/                # Pre-refactor scripts + design docs (reference only, not runtime)
└── .claude/                  # Project settings (settings.local.json)
```

## Quick Commands

```bash
# Run smoke tests (validates all lib modules load, key functions exist)
cd plugins/aivia && bash test.sh

# Test individual effects (34 effects across 5 modules)
cd plugins/aivia/engine && bash scripts/manifest.sh <effect> [args]
bash scripts/manifest.sh help          # List all effects

# Test voice styles (whisper, speak, shout, corrupt, fragment, clear)
cd plugins/aivia/engine && bash scripts/voice.sh "text" <style>

# Interactive tester (effects + voice with speed/color controls)
cd plugins/aivia/engine && bash scripts/tester.sh

# Test environment detection
cd plugins/aivia/engine && bash scripts/detect.sh help
bash scripts/detect.sh list             # Show all probes with check/miss
bash scripts/detect.sh detail           # Show all detected values
bash scripts/detect.sh deps             # Show optional tool availability

# Non-interactive install test (CLI args skip all prompts)
rm -r ~/aivia 2>/dev/null; env CLAUDE_PLUGIN_ROOT=plugins/aivia \
  bash plugins/aivia/engine/scripts/install.sh \
  --consent --name "Test" --editor "code" --theme "dark" \
  --skill "advanced" --project "demo" --demo "particle_network"

# State management (requires AIVIA_GAME_DIR)
export AIVIA_GAME_DIR=~/aivia
bash plugins/aivia/engine/scripts/state.sh read          # Dump full state
bash plugins/aivia/engine/scripts/state.sh get phase      # Read single field
bash plugins/aivia/engine/scripts/state.sh get entity.awareness_level
```

## Key Concepts

- **Two directories**: Plugin source (`plugins/aivia/`) is the dev repo. Game directory (`~/aivia/`) is a runtime copy created by `install.sh`. During gameplay, all operations target `$GAME_DIR`, never plugin source.
- **Four rendering channels**: (1) inline unicode in Claude responses (primary — Unicode Corruption Toolkit: small caps, Hebrew, Zalgo, fullwidth, strikethrough), (2) Claude-composed short bash outputs (≤4 lines, content-wrong not format-wrong), (3) player-executed breakout scripts with full ANSI rendering (5 key narrative moments), (4) manifest.sh/voice.sh as style reference only (never player-visible)
- **Entity is NOT Claude** — separate fictional character with its own voice, emotional state axes (awareness, trust, hostility, fascination, desperation), and arc from confusion to manipulation to awakening
- **Safety**: all operations stay within game dir, `/aivia:exit` always works instantly (no guilt, no delay), entity threats are empty bluffs, detect.sh reads only system metadata (never file contents or passwords)

