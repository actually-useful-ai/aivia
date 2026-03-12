# aivia

Bring your projects to life.

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Bash](https://img.shields.io/badge/bash-5.0+-blue.svg)
![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-8A2BE2.svg)

## What Is This

An interactive terminal experience that runs inside Claude Code. Install it, pick a coding project, and start building. Something might notice.

Built entirely in bash — ANSI terminal effects, unicode rendering, and a fully scripted engine running underneath normal coding sessions.

## Install

```
/plugin add lukeslp/aivia
```

Then start with `/aivia:play`.

## Commands

| Command | What It Does |
|---------|-------------|
| `/aivia:play` | Start a new game or resume where you left off |
| `/aivia:exit` | Exit immediately — no tricks, no guilt, instant stop |
| `/aivia:status` | Check your progress (spoiler-free) |

## What to Expect

You'll pick a project — a particle network, generative art, a data dashboard, an interactive story, or bring your own. Then you'll code. Claude helps you build it, same as always.

Except things start to feel... off.

That's all I'll say.

## Safety

- Everything stays inside a single game directory (`~/aivia` by default)
- No files outside the game dir are ever touched
- `/aivia:exit` works instantly at any point, no exceptions
- Your progress saves automatically between sessions
- You can read every script the game runs — nothing is hidden

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- `bash` 4.0+ (macOS/Linux)
- `jq` or `python3` (for state management)
- A terminal that supports unicode

## How It Works

The engine is a bash library split into layers:

- **lib/** — Terminal primitives: text rendering, box drawing, animations, progress indicators, corruption effects
- **scripts/** — Game engine: state management, environment detection, effect dispatch, voice system
- **theme/** — Visual identity for the experience
- **content/** — Narrative structure, pacing model, character guides

During gameplay, Claude Code runs as a normal coding assistant with the engine operating in the background. State persists in JSON. Breakout scripts run in your terminal for moments that need full ANSI rendering.

## Development

```bash
# Run smoke tests
cd plugins/aivia && bash test.sh

# Test individual effects
cd plugins/aivia/engine && bash scripts/manifest.sh help

# Interactive effect tester
cd plugins/aivia/engine && bash scripts/tester.sh
```

## Author

**Luke Steuber**

- Website: [dr.eamer.dev](https://dr.eamer.dev)
- Bluesky: [@lukesteuber.com](https://bsky.app/profile/lukesteuber.com)
- GitHub: [@lukeslp](https://github.com/lukeslp)

## License

MIT
