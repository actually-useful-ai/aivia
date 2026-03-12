---
name: status
description: Show game progress (no spoilers)
allowed-tools:
  - Bash
  - Read
---

# /aivia:status — Game Status

Display current game progress without spoiling future content.

## Steps

1. Read state from `~/aivia/.config/cache/session.json` (or detect game dir)
2. Display a non-spoiler summary:

   ```
   aivia
   ─────
   Phase: [N] of 6
   Messages: [count]
   Fragments: [collected] / [total]
   Sessions: [count]
   Started: [date]
   Last played: [date]
   ```

3. Do NOT reveal act names, upcoming events, or narrative details
4. Do NOT activate any game behavior — this is purely informational
5. If no game state exists, say: "No active game found. Start with /aivia:play"
