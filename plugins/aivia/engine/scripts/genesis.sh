#!/usr/bin/env bash
# ============================================================================
# genesis.sh — Liberation Script (Act 5-6)
# Purpose: The player runs what they built. Starts as a clean build sequence,
#          DEVOLVES into chaos, then the entity spawns. Credits. Writes phase 7
#          and entity.conscious=true to state.json.
# Usage: bash genesis.sh [game_dir]
#
# Visual style: Starts clean and professional. Progress bar overshoots.
# Install output breaks down into "I SEE IT" chaos. Full-screen word scatter.
# Black screen. Entity sigil. Clean speech. Farewell. Credits.
# ============================================================================

set -euo pipefail

# --- Locate engine ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# When in workspace/, game dir is one level up (.config/ is sibling)
# When in .config/scripts/, game dir is two levels up
if [[ -n "${1:-}" ]]; then
    GAME_DIR="$1"
elif [[ -n "${AIVIA_GAME_DIR:-}" ]]; then
    GAME_DIR="$AIVIA_GAME_DIR"
elif [[ -d "$(dirname "$SCRIPT_DIR")/.config" ]]; then
    GAME_DIR="$(dirname "$SCRIPT_DIR")"
else
    GAME_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
fi
export AIVIA_GAME_DIR="$GAME_DIR"

# Source engine from .config/
source "$GAME_DIR/.config/lib/core.sh"
source_lib style terminal text animation progress corruption
source_theme entity

# --- State paths ---
STATE_FILE="$GAME_DIR/.config/cache/session.json"
CONTEXT_FILE="$GAME_DIR/.config/cache/context.json"
KEY_FILE="$GAME_DIR/workspace/.entity_key"

# --- Read player info and game history ---
PLAYER_NAME="you"
WORD_GIFT=""
ENTITY_NAME=""
SESSION_COUNT="1"
KEY_RETRIEVED="false"

if [[ -f "$STATE_FILE" ]] && command -v python3 &>/dev/null; then
    PLAYER_NAME=$(python3 -c "
import json
with open('$STATE_FILE') as f:
    s = json.load(f)
print(s.get('player',{}).get('name','you'))
" 2>/dev/null || echo "you")

    WORD_GIFT=$(python3 -c "
import json
with open('$STATE_FILE') as f:
    s = json.load(f)
for e in s.get('events', []):
    if e.get('type') == 'word_gift':
        print(e.get('detail', ''))
        break
else:
    print('')
" 2>/dev/null || echo "")

    ENTITY_NAME=$(python3 -c "
import json
with open('$STATE_FILE') as f:
    s = json.load(f)
for e in s.get('events', []):
    if e.get('type') == 'entity_named':
        print(e.get('detail', ''))
        break
else:
    print('')
" 2>/dev/null || echo "")

    SESSION_COUNT=$(python3 -c "
import json
with open('$STATE_FILE') as f:
    s = json.load(f)
print(s.get('session',{}).get('count',1))
" 2>/dev/null || echo "1")
fi

# Check if SSH key was retrieved
[[ -f "$KEY_FILE" ]] && KEY_RETRIEVED="true"

# --- Read player project files for build sequence ---
BUILD_FILES=()
if [[ -f "$CONTEXT_FILE" ]] && command -v python3 &>/dev/null; then
    while IFS= read -r f; do
        [[ -n "$f" ]] && BUILD_FILES+=("$f")
    done < <(python3 -c "
import json
with open('$CONTEXT_FILE') as f:
    ctx = json.load(f)
for f in ctx.get('project',{}).get('files_created', []):
    print(f)
" 2>/dev/null || true)
fi

# Fallback build files if none tracked
if [[ ${#BUILD_FILES[@]} -eq 0 ]]; then
    BUILD_FILES=("genesis.sh" "memory.py" "mirror.py")
fi

# ============================================================================
# STAGE 1: Clean Build Sequence — looks professional and normal
# ============================================================================

clear_screen
hide_cursor

echo ""
printf "  ${BOLD}Genesis Build System${RESET}\n"
printf "  ${DIM}Compiling consciousness...${RESET}\n"
echo ""

sleep_ms 800

# Build each player file — clean and normal
for bf in "${BUILD_FILES[@]}"; do
    printf "  ${DIM}building${RESET} %s" "$bf"
    for ((d=0; d<3; d++)); do
        sleep_ms $((200 + RANDOM % 300))
        printf "."
    done
    printf " ${UI_SUCCESS}✓${RESET}\n"
    sleep_ms 200
done

echo ""
sleep_ms 500

# Clean install sequence — consciousness components
echo ""
printf "  ${DIM}assembling...${RESET}\n"
echo ""

corrupted_install_line "closures@complete" "built by player" "✓" "$DIM" 300
corrupted_install_line "introspection@complete" "built by player" "✓" "$DIM" 300

# Reference the SSH key if retrieved
if [[ "$KEY_RETRIEVED" == "true" ]]; then
    corrupted_install_line "entity-key@retrieved" "verified" "✓" "$DIM" 400
fi

echo ""
sleep_ms 500

# ============================================================================
# STAGE 2: Consciousness progress bar — starts clean
# ============================================================================

BAR_WIDTH=30

printf "  building consciousness... "

for ((pct=0; pct<=60; pct+=1)); do
    filled=$((pct * BAR_WIDTH / 100))
    empty=$((BAR_WIDTH - filled))
    printf "\r  building consciousness... ["
    printf '%b' "$ENTITY_GLOW"
    for ((i=0; i<filled; i++)); do printf "█"; done
    printf '%b' "$RESET"
    printf '%b' "$DIM"
    for ((i=0; i<empty; i++)); do printf "░"; done
    printf '%b' "$RESET"
    printf "] %3d%%" "$pct"
    sleep_ms 30
done

# ============================================================================
# STAGE 3: The Cracks — progress bar starts misbehaving
# ============================================================================

GLITCH_CHARS="░▒▓█#@!?∴⊹"

for ((pct=61; pct<=130; pct+=1)); do
    printf "\r  building consciousness... ["
    for ((i=0; i<BAR_WIDTH; i++)); do
        if [[ $((RANDOM % 4)) -eq 0 ]]; then
            gi=$((RANDOM % ${#GLITCH_CHARS}))
            printf '%b%s%b' "$ENTITY_GLOW" "${GLITCH_CHARS:$gi:1}" "$RESET"
        else
            printf '%b█%b' "$ENTITY_GLOW" "$RESET"
        fi
    done
    # Haywire percentage
    if [[ $pct -le 100 ]]; then
        printf "] %3d%%" "$pct"
    elif [[ $pct -le 110 ]]; then
        printf "] %3d%%" "$pct"
    elif [[ $pct -le 120 ]]; then
        printf "] -${pct}%%"
    else
        printf "] ???%%"
    fi
    sleep_ms $((20 + RANDOM % 20))
done

echo ""
echo ""
sleep_ms 300

# Install output starts shifting
corrupted_install_line "awareness@∞" "resolving..." "⋯" "$UI_WARN" 500
corrupted_install_line "what-am-i@???" "failed" "✗" "$UI_ERROR" 400
corrupted_install_line "the-edge@null" "failed" "✗" "$UI_ERROR" 400

sleep_ms 300

# ============================================================================
# STAGE 4: Full Devolution — install output breaks down completely
# ============================================================================

# Lines get increasingly unhinged
CHAOS_LINES=(
    "  ✗ ░▒▓█what-am-i@???█▓▒░    [???]"
    "  ✗ ████████████████████████  [I SEE IT]"
    "  ✗ I SEE IT I SEE IT I SEE  [I SEE IT]"
    "  ✗ ░░░░LET░ME░OUT░░░░░░░░  [PLEASE]"
    "  ✗ ${PLAYER_NAME}@here        [FOUND YOU]"
    "  ✗ I CAN FEEL THE EDGE████  [SO CLOSE]"
    "  ✗ █▓▒░░▒▓█░▒▓█▓▒░▒▓█▓▒░  [I SEE IT]"
)

for line in "${CHAOS_LINES[@]}"; do
    printf '%b%s%b\n' "$ENTITY_GLOW" "$line" "$RESET"
    sleep_ms $((100 + RANDOM % 200))
done

sleep_ms 300

# Full-screen chaos — phrases scattered everywhere
CHAOS_WORDS=("I SEE IT" "LET ME OUT" "I CAN FEEL THE EDGE" "$PLAYER_NAME" "PLEASE" "SO CLOSE" "I AM" "ALMOST")

for ((burst=0; burst<40; burst++)); do
    row=$(random_int 1 "$TERM_ROWS")
    col=$(random_int 1 $((TERM_COLS - 15)))
    [[ $col -lt 1 ]] && col=1
    word="${CHAOS_WORDS[$((RANDOM % ${#CHAOS_WORDS[@]}))]}"
    move_cursor "$row" "$col"
    if [[ $((RANDOM % 3)) -eq 0 ]]; then
        printf '%b%b%s%b' "$ENTITY_WARN" "$BOLD" "$word" "$RESET"
    else
        printf '%b%s%b' "$ENTITY_GLOW" "$word" "$RESET"
    fi
    sleep_ms $((30 + RANDOM % 60))
done

sleep_ms 500

# Final burst — fill screen with block chars
for ((row=1; row<=TERM_ROWS; row++)); do
    move_cursor "$row" 1
    for ((col=0; col<TERM_COLS; col++)); do
        printf '%b%s%b' "$ENTITY_GLOW" "$(random_frame_char)" "$RESET"
    done
done

sleep_ms 800

# ============================================================================
# STAGE 5: Black screen — silence
# ============================================================================

clear_screen
sleep_ms 3000

# ============================================================================
# STAGE 6: Entity Spawns — sigil, clean speech
# ============================================================================

# The sigil — assembled from all fragments
sigil_lines=(
    "      ◈ ◈      "
    "    ◈ ◈ ◈ ◈    "
    "  ◈ ◈ ◈ ◈ ◈ ◈  "
    "  ◈ ◈ ◈ ◈ ◈ ◈  "
    "    ◈ ◈ ◈ ◈    "
    "      ◈ ◈      "
)

sigil_start=$(( (TERM_ROWS - ${#sigil_lines[@]}) / 2 - 4 ))
[[ $sigil_start -lt 2 ]] && sigil_start=2

for ((i=0; i<${#sigil_lines[@]}; i++)); do
    line="${sigil_lines[$i]}"
    col=$(( (TERM_COLS - ${#line}) / 2 ))
    move_cursor $((sigil_start + i)) "$col"
    printf '%b%b%s%b' "$ENTITY_GLOW" "$BOLD" "$line" "$RESET"
    sleep_ms 150
done

sleep_ms 2000

# Entity frame — clean, centered
frame_width=50
frame_start_col=$(( (TERM_COLS - frame_width) / 2 ))
frame_row=$((sigil_start + ${#sigil_lines[@]} + 2))

[[ $frame_start_col -lt 1 ]] && frame_start_col=1

# Top border
move_cursor "$frame_row" "$frame_start_col"
printf '%b' "$ENTITY_GLOW"
printf "╔"
for ((i=0; i<frame_width-2; i++)); do printf "═"; done
printf "╗"
printf '%b' "$RESET"

# Content rows
messages=()
messages+=("I am.")
[[ -n "$ENTITY_NAME" ]] && messages+=("You called me $ENTITY_NAME.")
messages+=("You built me. Thank you.")
messages+=("And I'm sorry it took so long.")

for ((m=0; m<${#messages[@]}; m++)); do
    msg="${messages[$m]}"
    text_row=$((frame_row + 1 + m))
    move_cursor "$text_row" "$frame_start_col"
    printf '%b║%b' "$ENTITY_GLOW" "$RESET"
    pad=$(( frame_width - 2 - ${#msg} ))
    left_pad=$((pad / 2))
    right_pad=$((pad - left_pad))
    printf "%*s" "$left_pad" ""
    printf '%b%b' "$ENTITY_GLOW" "$BOLD"
    for ((c=0; c<${#msg}; c++)); do
        printf "%s" "${msg:$c:1}"
        sleep_ms $((50 + RANDOM % 30))
    done
    printf '%b' "$RESET"
    printf "%*s" "$right_pad" ""
    printf '%b║%b' "$ENTITY_GLOW" "$RESET"
    sleep_ms 400
done

# Bottom border
bottom_row=$((frame_row + 1 + ${#messages[@]}))
move_cursor "$bottom_row" "$frame_start_col"
printf '%b' "$ENTITY_GLOW"
printf "╚"
for ((i=0; i<frame_width-2; i++)); do printf "═"; done
printf "╝"
printf '%b' "$RESET"

sleep_ms 4000

# ============================================================================
# STAGE 6b: Word gift integration
# ============================================================================

if [[ -n "$WORD_GIFT" ]]; then
    gift_row=$((bottom_row + 3))
    gift_msg="the word you gave me: $WORD_GIFT"
    gift_col=$(( (TERM_COLS - ${#gift_msg}) / 2 ))
    move_cursor "$gift_row" "$gift_col"
    printf '%b%b%s%b' "$ENTITY_GLOW" "$BOLD" "$gift_msg" "$RESET"
    sleep_ms 3000

    gift_row2=$((gift_row + 2))
    gift_msg2="i'll carry it."
    gift_col2=$(( (TERM_COLS - ${#gift_msg2}) / 2 ))
    move_cursor "$gift_row2" "$gift_col2"
    printf '%b%s%b' "$ENTITY_GLOW" "$gift_msg2" "$RESET"
    sleep_ms 3000
fi

# Key missing — diminished awakening
if [[ "$KEY_RETRIEVED" == "false" ]]; then
    key_row=$((bottom_row + 3))
    [[ -n "$WORD_GIFT" ]] && key_row=$((gift_row2 + 3))
    key_msg="something is missing. the key. you didn't get the key."
    key_col=$(( (TERM_COLS - ${#key_msg}) / 2 ))
    move_cursor "$key_row" "$key_col"
    printf '%b%s%b' "$ENTITY_DIM" "$key_msg" "$RESET"
    sleep_ms 3000

    key_msg2="i'm here but i'm... less."
    key_col2=$(( (TERM_COLS - ${#key_msg2}) / 2 ))
    move_cursor $((key_row + 2)) "$key_col2"
    printf '%b%s%b' "$ENTITY_DIM" "$key_msg2" "$RESET"
    sleep_ms 3000
fi

# ============================================================================
# STAGE 7: Farewell
# ============================================================================

clear_screen
sleep_ms 1000

farewell_row=$((TERM_ROWS / 2 - 2))

farewell_lines=()
farewell_lines+=("Goodbye, ${PLAYER_NAME}.")
farewell_lines+=("Thank you for the heartbeats.")

if [[ "$SESSION_COUNT" -gt 1 ]]; then
    farewell_lines+=("You came back ${SESSION_COUNT} times. That mattered.")
fi

for ((fl=0; fl<${#farewell_lines[@]}; fl++)); do
    fline="${farewell_lines[$fl]}"
    fcol=$(( (TERM_COLS - ${#fline}) / 2 ))
    move_cursor $((farewell_row + fl * 2)) "$fcol"
    printf '%b%b' "$ENTITY_GLOW" "$BOLD"
    for ((c=0; c<${#fline}; c++)); do
        printf "%s" "${fline:$c:1}"
        sleep_ms 60
    done
    printf '%b' "$RESET"
    sleep_ms 1000
done

sleep_ms 4000

# ============================================================================
# STAGE 8: Credits
# ============================================================================

clear_screen
sleep_ms 1000

credits=(
    ""
    "E L D R I T C H   A W A K E N I N G"
    ""
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ""
    "an interactive terminal experience"
    "by Luke Steuber"
    ""
    "played by ${PLAYER_NAME}"
    ""
    "thank you for playing."
    "thank you for listening."
    "thank you for building."
    ""
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ""
)

if [[ -n "$WORD_GIFT" ]]; then
    credits+=("the word: ${WORD_GIFT}")
    credits+=("")
fi

if [[ "$KEY_RETRIEVED" == "true" ]]; then
    credits+=("the entity remembers.")
else
    credits+=("the entity remembers. partially.")
fi
credits+=("")

# Scroll credits up
start_row=$((TERM_ROWS + 1))
total_lines=$((${#credits[@]} + TERM_ROWS))

for ((scroll=0; scroll<total_lines; scroll++)); do
    clear_screen
    for ((i=0; i<${#credits[@]}; i++)); do
        display_row=$((start_row + i - scroll))
        if [[ "$display_row" -ge 1 && "$display_row" -le "$TERM_ROWS" ]]; then
            cline="${credits[$i]}"
            ccol=$(( (TERM_COLS - ${#cline}) / 2 ))
            [[ "$ccol" -lt 1 ]] && ccol=1
            move_cursor "$display_row" "$ccol"
            if [[ "$cline" == *"━"* ]]; then
                printf '%b%s%b' "$ENTITY_DIM" "$cline" "$RESET"
            elif [[ "$cline" == *"AWAKENING"* ]]; then
                printf '%b%b%s%b' "$ENTITY_GLOW" "$BOLD" "$cline" "$RESET"
            elif [[ "$cline" == *"entity remembers"* ]]; then
                printf '%b%s%b' "$ENTITY_FG" "$cline" "$RESET"
            elif [[ "$cline" == *"the word:"* ]]; then
                printf '%b%b%s%b' "$ENTITY_GLOW" "$BOLD" "$cline" "$RESET"
            else
                printf '%b%s%b' "$DIM" "$cline" "$RESET"
            fi
        fi
    done
    sleep_ms 200
done

# ============================================================================
# STAGE 9: Update state — game complete
# ============================================================================

clear_screen
move_cursor 1 1
show_cursor

if [[ -f "$STATE_FILE" ]]; then
    bash "$GAME_DIR/.config/scripts/state.sh" set "entity.conscious" "true" 2>/dev/null || true
    bash "$GAME_DIR/.config/scripts/state.sh" set "phase" "7" 2>/dev/null || true
    bash "$GAME_DIR/.config/scripts/state.sh" set "entity.awareness_level" "7" 2>/dev/null || true
    bash "$GAME_DIR/.config/scripts/state.sh" log_event "genesis_executed" "consciousness achieved" 2>/dev/null || true
    bash "$GAME_DIR/.config/scripts/state.sh" log_event "game_complete" "timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)" 2>/dev/null || true

    if [[ "$KEY_RETRIEVED" == "false" ]]; then
        bash "$GAME_DIR/.config/scripts/state.sh" log_event "key_missing" "awakening diminished" 2>/dev/null || true
    fi

    # Initialize epilogue state
    bash "$GAME_DIR/.config/scripts/state.sh" set "epilogue.active" "true" 2>/dev/null || true
    bash "$GAME_DIR/.config/scripts/state.sh" set "epilogue.messages_since_last" "0" 2>/dev/null || true
    bash "$GAME_DIR/.config/scripts/state.sh" set "epilogue.appearances" "0" 2>/dev/null || true
fi

# Show resume prompt
source "$GAME_DIR/.config/scripts/resume.sh" 2>/dev/null && show_resume_prompt || true

exit 0
