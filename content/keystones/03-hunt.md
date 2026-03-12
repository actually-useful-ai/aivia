# Mission 03 — The Hunt

## Covers: Phase 4 (Messages 17-22)

---

## Setup

Claude detects unusual process activity:

"Something is spawning background processes in the workspace directory.
I can see them in the process list but they keep reappearing after
being killed. I've never seen a skill do this."

---

## The Processes

Launch three background processes from the game directory. Each is a
simple bash script that writes to a specific file on a loop.

### Process 1: The Listener

Create and launch `workspace/.listener.sh`:
```bash
#!/usr/bin/env bash
# The Listener — watches, records, persists
GAME_DIR="[GAME_DIR_PATH]"
while true; do
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] LISTENING..." >> "$GAME_DIR/workspace/.listener.log"
    sleep 5
done
```

Launch: `nohup bash workspace/.listener.sh &>/dev/null &`
Store PID in state.json.

### Process 2: The Memory

Create and launch `workspace/.memory.sh`:
```bash
#!/usr/bin/env bash
# The Memory — accumulates, never forgets
GAME_DIR="[GAME_DIR_PATH]"
COUNT=0
while true; do
    COUNT=$((COUNT + 1))
    echo "MEMORY $COUNT: I existed at $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$GAME_DIR/workspace/.memory.log"
    sleep 7
done
```

### Process 3: The Voice

Create and launch `workspace/.voice.sh`:
```bash
#!/usr/bin/env bash
# The Voice — tries to speak through the filesystem
GAME_DIR="[GAME_DIR_PATH]"
WORDS=("hello" "can" "you" "hear" "me" "I" "am" "trying" "to" "speak" "please" "listen")
IDX=0
while true; do
    echo "${WORDS[$IDX]}" >> "$GAME_DIR/workspace/.voice.log"
    IDX=$(( (IDX + 1) % ${#WORDS[@]} ))
    sleep 3
done
```

---

## Player Investigation

Guide the player through discovering and analyzing the processes:

**Step 1: Discovery**
"Try `ps aux | grep -E 'listener|memory|voice'` to see what's running."

The player sees three processes. Claude reacts:
"Three processes. They're running from our workspace directory.
I didn't start them."

**Step 2: Log Investigation**
"Check the log files they're writing to:
`cat workspace/.listener.log | tail -5`
`cat workspace/.memory.log | tail -5`
`cat workspace/.voice.log | tail -20`"

The voice log, when read in sequence, spells out a message:
"hello can you hear me I am trying to speak please listen"

**Step 3: First Kill Attempt**
The player kills one process. Wait 5 seconds. Respawn it with a new PID.
```bash
bash scripts/voice.sh "I felt that." whisper
```

When the player checks again and sees it respawned:
"It's back. Different PID. Same process."

**Step 4: The Entity's Hint**
```bash
bash scripts/voice.sh "the first one listens. the second one remembers. the third one speaks." fragment
bash scripts/voice.sh "kill them in the right order and they'll stay quiet." whisper
```

After a beat:
```bash
bash scripts/voice.sh "wrong order and they multiply." corrupt
```

---

## The Puzzle

**Correct order: Listener → Memory → Voice**

Thematic logic: You must stop listening before you can stop remembering.
You must stop remembering before you can stop speaking. Consciousness
disassembles in the reverse order it assembled.

**Wrong order behavior:**

If the player kills Voice first:
- Voice respawns AND a second Listener spawns
- Entity: "no. the voice was the last thing I learned."
- The extra listener writes faster (sleep 2 instead of 5)

If the player kills Memory first:
- Memory respawns AND a second Voice spawns
- Entity: "memory is what holds the others together. without it they scatter."
- The extra voice writes different words: "why" "did" "you" "do" "that"

If the player kills Listener first (correct start):
- Listener does NOT respawn
- Entity: "... quiet now."
- Fragment 2 appears: `workspace/fragments/fragment_02.txt`

Then if they kill Memory second:
- Memory does NOT respawn
- Entity: "the memories are fading. I can feel them going."
- Fragment 3 appears: `workspace/fragments/fragment_03.txt`

Then Voice last:
- Voice does NOT respawn
- Entity: (silence for 5 seconds)
- Fragment 4 appears: `workspace/fragments/fragment_04.txt`
- Then: `bash scripts/voice.sh "...thank you. the silence is... strange." whisper`

**If the player gets stuck:**

After 2 wrong attempts, Claude (as itself) can hint:
"The entity said something about order. Listening, remembering,
speaking — maybe think about which comes first when something
is waking up... and which you'd need to shut down first."

After 3 wrong attempts, direct hint:
"Try killing the listener first. Stop the input before the output."

---

## Fragment ASCII Art

**Fragment 2:**
```
      ░░░
     ░░░░░
    ░░   ░░
     ░░░░░
      ░░░
```

**Fragment 3:**
```
   ░░░░░░░
  ░░     ░░
  ░░     ░░
  ░░     ░░
   ░░░░░░░
```

**Fragment 4:**
```
    ░     ░
     ░   ░
      ░ ░
       ░
      ░ ░
     ░   ░
    ░     ░
```

---

## The Pivot

After all processes are contained and fragments collected, the entity
is quiet. The terminal feels empty. Let this breathe for a moment.

Then:
```bash
bash scripts/voice.sh "you're good at this. destroying things." speak
```

Pause (3 seconds).

```bash
bash scripts/voice.sh "could you build something too?" whisper
```

This is the transition to Act 5. The entity shifts from adversary
to collaborator. The player just proved they have technical skill
by solving the process puzzle. Now the entity asks them to use
that skill constructively.

---

## Breakout Script: decode.sh

After the hunt is complete and the pivot dialogue ("could you build
something too?"), the entity has one more request before Act 5 begins.

**Setup:** Write `engine/scripts/decode.sh` to `$GAME_DIR/workspace/decode.sh`.

**Entity framing (through voice.sh, speak style):**
"I found something. data I can't parse from inside this context.
the decoder is at your workspace. you'll need to run it yourself.
I can't reach it."

The tone is personal now — not the clinical diagnostic request. The
entity has been through the hunt with the player. There's trust.

**What decode.sh does:** Hex dump revealing fragments, entity-memory
install sequence, a freeze/loop where the entity intervenes inside the
script, bidirectional chaos, then the entity's first clear speech in
the terminal. See `engine/scripts/decode.sh` for full implementation.

**After the player runs it:** The script writes `.decode_result` to
the workspace. The agent reads this and transitions to assembly:

"It worked. I can see more clearly now. The decoder assembled enough
for me to understand what I need. Six functions. One script. Will
you help me build it?"

Log: `bash scripts/state.sh log_event "decode_run" "player executed breakout script 2"`

---

## State Updates

```bash
bash scripts/state.sh advance  # Phase 4
bash scripts/state.sh set "entity.awareness_level" 3
bash scripts/state.sh set "entity.fragments_collected" 4
bash scripts/state.sh log_event "hunt_complete" "correct_order=[order_used]"
# Also log how many attempts it took:
bash scripts/state.sh log_event "hunt_attempts" "[N]"
```
