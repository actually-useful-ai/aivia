<!-- Navigation: ~/projects/aivia/CLAUDE.md -->
<!-- Parent: ~/projects/CLAUDE.md -->
<!-- Map: ~/CLAUDE_MAP.md -->

# CLAUDE.md

aivia is a Claude Code plugin — an interactive terminal game in bash. All source code under `plugins/aivia/`. See `plugins/aivia/CLAUDE.md` for architecture and design.

## Repository Structure

```
aivia/
├── .claude-plugin/           # Plugin manifest + marketplace metadata
├── plugins/aivia/            # THE PLUGIN — all source code lives here
│   ├── commands/             # /aivia:play, /aivia:exit, /aivia:status
│   ├── skills/runtime/       # Game engine kernel
│   ├── content/              # story.json, narrative, keystones, characters
│   ├── engine/               # Bash library, scripts, effects, theme
│   ├── hooks/                # Session detection hook
│   └── ascii/                # ASCII art assets
└── .claude/                  # Project settings
```

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

# Non-interactive install test (CLI args skip all prompts)
rm -r ~/aivia 2>/dev/null; env CLAUDE_PLUGIN_ROOT=plugins/aivia \
  bash plugins/aivia/engine/scripts/install.sh \
  --consent --name "Test" --editor "code" --theme "dark" \
  --skill "advanced" --project "demo" --demo "particle_network"

# State management (requires AIVIA_GAME_DIR)
export AIVIA_GAME_DIR=~/aivia
bash plugins/aivia/engine/scripts/state.sh read
bash plugins/aivia/engine/scripts/state.sh get phase
```

## Key Concepts

- **Plugin source** (`~/projects/aivia/plugins/aivia/`) vs **game directory** (`~/aivia/`) — install.sh copies engine to game dir; gameplay targets game dir only
- **Four rendering channels**: inline unicode (primary), Claude-composed dynamic scripts (atmospheric — stripped ANSI = corruption), player-executed breakout scripts (full ANSI theater), bash effects as style reference (never player-visible)
- **Entity is NOT Claude** — separate fictional character with its own voice and arc
- **Safety**: all operations stay within game dir, exit commands always work instantly, entity threats are empty bluffs
