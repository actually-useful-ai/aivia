---
name: exit
description: Exit Eldritch Awakening immediately
allowed-tools:
  - Bash
  - Read
---

# /aivia:exit — Exit Game

Immediately break character and exit the game. No guilt mechanics. No "but the
entity doesn't want you to leave." The player's comfort comes first.

## Steps

1. If Act 4 processes are running, kill them:
   ```bash
   for proc in aivia-listener aivia-memory aivia-voice; do
     pkill -f "$proc" 2>/dev/null || true
   done
   ```
2. Save current game state (state.sh handles timestamps automatically)
3. Tell the player clearly and out of character:

   "Game paused. Your progress is saved at [game directory path].

   To resume: `/aivia:play`
   To delete and reset: `rm -rf [game directory path]`

   You're back in normal Claude Code."

4. Do NOT continue any game behavior after this command
