<!-- Navigation: ~/projects/aivia/CLAUDE.md -->
<!-- Parent: ~/projects/CLAUDE.md -->
<!-- Map: ~/CLAUDE_MAP.md -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**aivia** — "Bring your projects to life." An interactive terminal experience packaged as a Claude Code plugin. Built entirely in bash using ANSI terminal effects.

**Author:** Luke Steuber | **License:** MIT

## Repository Structure

```
aivia/
├── .claude-plugin/           # Plugin manifest + marketplace metadata
│   ├── plugin.json
│   └── marketplace.json
├── plugins/aivia/            # THE PLUGIN — all source code lives here
│   ├── CLAUDE.md             # Detailed architecture guide (read this)
│   ├── plugin.json
│   ├── commands/             # /aivia:play, /aivia:exit, /aivia:status
│   ├── skills/runtime/       # Game engine kernel (SKILL.md)
│   ├── content/              # story.json, narrative, keystones, characters
│   ├── engine/               # Bash library, scripts, effects, theme
│   ├── hooks/                # Session detection hook
│   ├── ascii/                # ASCII art assets
│   ├── files/                # Pre-refactor design docs (reference only)
│   ├── EXIT.md               # Emergency exit instructions
│   └── test.sh               # Smoke tests
└── .claude/                  # Project settings
```

All source code is under `plugins/aivia/`. See `plugins/aivia/CLAUDE.md` for full architecture, dependency chains, state management, and design patterns.

## Quick Commands

```bash
# Run smoke tests
cd plugins/aivia && bash test.sh

# Test individual effects
cd plugins/aivia/engine && bash scripts/manifest.sh <effect> [args]
bash scripts/manifest.sh help          # List all effects

# Test voice styles
cd plugins/aivia/engine && bash scripts/voice.sh "text" <style>

# Interactive tester (effects + voice with controls)
cd plugins/aivia/engine && bash scripts/tester.sh

# State management (requires AIVIA_GAME_DIR)
export AIVIA_GAME_DIR=~/aivia
bash plugins/aivia/engine/scripts/state.sh read
bash plugins/aivia/engine/scripts/state.sh get phase
```

## Plugin Installation

Install as a Claude Code plugin: `/plugin add lukeslp/aivia`

Commands: `/aivia:play` (start/resume), `/aivia:exit` (quit), `/aivia:status` (progress)

## Key Concepts

- **Plugin source** (`~/projects/aivia/plugins/aivia/`) vs **game directory** (`~/aivia/`) — install.sh copies engine to game dir; gameplay targets game dir only
- **Three rendering channels**: inline unicode (primary), player-executed breakout scripts (ANSI), bash effects as style reference (never player-visible)
- **Entity is NOT Claude** — separate fictional character with its own voice and arc
- **Safety**: all operations stay within game dir, exit commands always work instantly, entity threats are empty bluffs
