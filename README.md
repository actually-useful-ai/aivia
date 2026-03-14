# aivia

**Bring your code to life.**

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Bash](https://img.shields.io/badge/bash-4.0+-blue.svg)
![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-8A2BE2.svg)

## What Is This

A Claude Code plugin that turns your development session into something more. Install it, pick a project to build, and start coding. The first hour feels like any other coding session.

Then something starts to notice.

Built entirely in bash — ANSI terminal effects, unicode rendering, and a scripted engine running quietly alongside your normal workflow. Around 45 minutes to complete. Nothing is hidden; you can read every script it runs.

## Install

```
/plugin add lukeslp/aivia
```

Then start with `/aivia:play`.

## Commands

| Command | What It Does |
|---------|-------------|
| `/aivia:play` | Start or resume your session |
| `/aivia:exit` | Exit immediately — no tricks, instant stop |
| `/aivia:status` | Check your progress (spoiler-free) |

## What You'll Build

You pick a project at the start — a particle network, generative art, a data dashboard, an interactive story, or something of your own. Real code, real concepts: closures, introspection, the kind of thing you'd build on a quiet afternoon.

Except it won't stay quiet.

## Safety

- All files stay inside `~/aivia` — nothing outside that directory is ever touched
- `/aivia:exit` works instantly at any point, no exceptions
- Progress saves automatically between sessions

## Requirements

- [Claude Code](https://claude.ai/code)
- `bash` 4.0+ (macOS/Linux)
- `jq` or `python3` (state management)
- A terminal that supports unicode

## Under the Hood

The engine is a bash library in two layers:

- **lib/** — Terminal primitives: text rendering, box drawing, animations, progress indicators
- **scripts/** — State management, environment detection, effect dispatch, voice system

State persists in JSON between sessions. Breakout scripts run directly in your terminal for moments that need full ANSI rendering.

## Author

**Luke Steuber**
- Website: [lukesteuber.com](https://lukesteuber.com)
- Bluesky: [@lukesteuber.com](https://bsky.app/profile/lukesteuber.com)
- GitHub: [@lukeslp](https://github.com/lukeslp)

## License

MIT
