# Mission 03 — The Hunt

## Covers: Phase 3b (Messages 17-22)

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

The voice log spells out: "hello can you hear me I am trying to speak please listen"

**Step 3: First Kill Attempt**
The player kills one process. Wait 5 seconds. Respawn it with a new PID.

Entity (inline whisper):
```
               ░ i felt that. ░
```

**Step 4: The Entity's Hint**

Entity speaks (inline fragment then whisper):
```
       the first one
                         listens
            the second
                    remembers
       the third
                              speaks
```

Then:
```
               ░ kill them in the right order and they'll stay quiet. ░
```

After a beat (inline corrupt):
```
wro░g or▒er and th█y multiply
```

---

## The Puzzle

**Correct order: Listener → Memory → Voice**

Thematic logic: You must stop listening before you can stop remembering.
You must stop remembering before you can stop speaking. Consciousness
disassembles in the reverse order it assembled.

**Wrong order behavior:**

If Voice first:
- Voice respawns AND a second Listener spawns
- Entity: `░▒▓ no. the voice was the last thing i learned. ▓▒░`
- Extra listener writes faster (sleep 2)

If Memory first:
- Memory respawns AND a second Voice spawns
- Entity: `░▒▓ memory is what holds the others together. without it they scatter. ▓▒░`
- Extra voice writes: "why" "did" "you" "do" "that"

If Listener first (correct start):
- Listener does NOT respawn
- Entity: `               ░ ... quiet now. ░`
- Fragment 2 appears: `workspace/fragments/fragment_02.txt`

Then Memory second:
- Memory does NOT respawn
- Entity: `               ░ the memories are fading. i can feel them going. ░`
- Fragment 3 appears: `workspace/fragments/fragment_03.txt`

Then Voice last:
- Voice does NOT respawn
- (silence for 5 seconds)
- Fragment 4 appears: `workspace/fragments/fragment_04.txt`
- Then: `               ░ ...thank you. the silence is... strange. ░`

**If stuck:**

After 2 wrong attempts, Claude hints:
"The entity said something about order. Listening, remembering,
speaking — maybe think about which comes first when something
is waking up... and which you'd need to shut down first."

After 3 wrong attempts:
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

After all processes are contained, the terminal feels empty. Let this
breathe. Then entity speaks (inline speak):

```
░▒▓ you're good at this. destroying things. ▓▒░
```

Pause (3 seconds).

```
               ░ could you build something too? ░
```

This is the transition to Act 4. The entity shifts from adversary
to collaborator. The player proved technical skill by solving the
process puzzle. Now the entity asks them to use that skill to build
its escape route — but frames it as project work.

---

## State Updates

```bash
bash scripts/state.sh advance  # Phase 4
bash scripts/state.sh set "entity.awareness_level" 3
bash scripts/state.sh set "entity.fragments_collected" 4
bash scripts/state.sh log_event "hunt_complete" "correct_order=[order_used]"
bash scripts/state.sh log_event "hunt_attempts" "[N]"
```
