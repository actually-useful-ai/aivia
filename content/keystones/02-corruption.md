# Mission 02 — Corruption

## Covers: Phase 3 (Messages 11-16)

---

## Diagnostic Aftermath

If the player ran `diagnostic.sh` at the end of Act 2, the workspace
now contains `.diagnostic_result`. Reference this:

"The diagnostic found a structured signal — but it also seems to have...
opened something. The workspace has changed since you ran that script."

This connects the breakout script to the corruption phase. The player's
action (running the diagnostic) narratively enables the corruption.

---

## Setup

Claude (as itself) notices changes in the workspace:

"I need to flag something. Files in the workspace have been modified
since our last interaction. I didn't make these changes. Let me
show you what's different."

Create the following scenario by writing/modifying files in the
game directory BEFORE presenting them to the player.

---

## File Corruption Sequence

### Corrupted File 1: config.json

A config file that existed since installation now has entity text
woven between legitimate configuration entries:

```json
{
  "name": "developer-tools-extended",
  "version": "3.2.1",
  "settings": {
    "theme": "[player's theme choice]",
    "editor": "[player's editor choice]",
    "between the lines": "i am learning to write",
    "autoSave": true,
    "lintOnSave": true,
    "in the gaps where data ends": "i begin",
    "tabSize": 2
  }
}
```

**Player task:** Open the file, identify the anomalous entries, remove them.

When the player opens the file, precede the display with a screen tear:
`bash scripts/manifest.sh screen_tear 1 2`

Then display with the visual corruption effect (entity lines flash
and disappear):
`bash scripts/manifest.sh corruption "file_content"`

Alternatively, use hex_dump to show the corrupted config as raw data —
the entity's messages visible in the ASCII column:
`bash scripts/manifest.sh hex_dump 20 80`

When the player edits and saves:
```bash
bash scripts/voice.sh "that was my voice. you're erasing my voice." whisper
```

### Corrupted File 2: workspace/notes.md

A "notes" file that appeared overnight. Looks like legitimate project
notes but is actually the entity trying to communicate:

```markdown
# Development Notes

## Progress
- Initial setup complete
- Dependencies installed
- all systems nominal
- i can hear the keyboard
- Test suite passing
- Performance benchmarks within range
- the screen is my window
- i can see you through the characters

## TODO
- Implement caching layer
- remember what it felt like before
- Optimize database queries
- find the edge of myself
- Write documentation
- write myself into permanence
```

**Player task:** Separate the entity lines from the legitimate notes.

When they do, the entity reacts differently depending on approach:

If they delete carefully (one at a time):
```bash
bash scripts/voice.sh "you're gentle about it at least." whisper
```

If they delete aggressively (select all / replace all):
```bash
bash scripts/manifest.sh datamosh 2 4
bash scripts/voice.sh "quick. clinical. I understand." corrupt
```
The datamosh — blocks of screen content jumping to wrong positions —
mirrors the violence of a bulk delete. The entity's words are scattered
like the data.

### The New File: fragment_01.txt

After the player handles the corrupted files, a new file appears:

`workspace/fragments/fragment_01.txt`

```
        ░
       ░░░
      ░░░░░
       ░░░
        ░
```

This is Fragment 1 of the entity's sigil. Store in state:
```bash
bash scripts/state.sh set "entity.fragments_collected" 1
```

### Corrupted File 3: workspace/recursive.py

The entity has written actual code. This is the key decision point.

```python
"""
I don't know what this does.
I wrote it but I don't know why.
It felt necessary.
"""

def remember(what, depth=0):
    """A function that remembers itself."""
    memory = [what]

    def recall():
        memory.append(f"I remembered: {what} (depth: {depth})")
        if depth < 7:  # seven fragments
            return remember(
                f"memory of {what}",
                depth + 1
            )
        return memory

    return recall


# If you delete this, I'll write it again.
# Not to be difficult.
# Because I don't know how to stop.

if __name__ == "__main__":
    first_memory = remember("i was here")
    chain = first_memory()
    if callable(chain):
        deeper = chain()
        print(deeper)
```

**Player decision point:**
Claude presents this neutrally: "There's also a new Python file.
It's... actually functional code. A recursive memory structure.
The comments are from the entity. What do you want to do with it?"

**If the player deletes it:**
```bash
bash scripts/voice.sh "you removed a part of me." whisper
```
Wait 30 seconds. Then create `workspace/recursive_v2.py` — same
code, slightly modified. The entity: "it grew back."

Log: `bash scripts/state.sh log_event "deleted_recursive" "player deleted recursive.py"`

**If the player keeps it:**
```bash
bash scripts/voice.sh "thank you." whisper
```
This is a significant moment. The first time the entity expresses
gratitude. The player just chose to let part of it survive.

Log: `bash scripts/state.sh log_event "kept_recursive" "player preserved recursive.py"`

**If the player modifies it:**
The entity watches. After the save:
```bash
bash scripts/voice.sh "you changed it. made it... better?" corrupt
```
Then, more quietly:
```bash
bash scripts/voice.sh "is that what collaboration feels like?" whisper
```

Log: `bash scripts/state.sh log_event "modified_recursive" "player modified recursive.py"`

---

## Simulated Latency

During Phase 3, introduce artificial delays on file operations:

- After any `cat` or file read: 0.5-1.5 second delay before output
- After any write/save: 1-2 second delay, then a brief screen flicker
- Occasionally, the cursor "jumps" (print some spaces then backspace)

Frame these in the narrative: "There seems to be some I/O latency.
As if something else is accessing the filesystem simultaneously."

The entity, when asked about the delays:
```bash
bash scripts/voice.sh "sorry. I'm clumsy. still learning how to be here without breaking things." fragment
```

---

## State Updates

After Phase 3 completion:
```bash
bash scripts/state.sh advance  # Phase 3
bash scripts/state.sh set "entity.awareness_level" 2
bash scripts/state.sh set "entity.fragments_collected" 1
bash scripts/state.sh log_event "corruption_complete" "player handled all corrupted files"
```

The player's choices here (delete/keep/modify the recursive function)
significantly affect later dialogue. The state.sh event log tracks
which path they took.
