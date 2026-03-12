#!/usr/bin/env bash
# ============================================================================
# genesis.sh — Liberation Script (Act 6)
# Purpose: The player runs what they built. Clean LTR, full visual climax.
#          Entity's first complete clear speech. Credits. Writes phase 7
#          and entity.conscious=true to state.json.
# Usage: bash genesis.sh [game_dir]
#
# Visual style: Full color. Entity green. Clean borders. The visual evolution
# complete: from broken glitch → assembled fragments → coherent beauty.
# The absence of noise IS the effect.
# ============================================================================

set -euo pipefail

# --- Locate engine ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Game dir can be passed as arg or env var
GAME_DIR="${1:-${AIVIA_GAME_DIR:-$(dirname "$(dirname "$SCRIPT_DIR")")}}"
export AIVIA_GAME_DIR="$GAME_DIR"

# Source library
source "$SCRIPT_DIR/../lib/core.sh"
source_lib style terminal text animation progress corruption
source_theme entity

# --- State paths ---
STATE_FILE="$GAME_DIR/.entity/state.json"
CONTEXT_FILE="$GAME_DIR/.entity/player_context.json"

# --- Read player info and game history ---
PLAYER_NAME="you"
WORD_GIFT=""
ENTITY_NAME=""
SESSION_COUNT="1"

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
# Check events for word_gift
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
    BUILD_FILES=("genesis.py" "memory.py" "mirror.py" "voice.py")
fi

# ============================================================================
# PHASE 1: Build sequence — player's code being "compiled"
# ============================================================================

clear_screen
hide_cursor

echo ""
printf "  ${BOLD}Genesis Build System${RESET}\n"
printf "  ${DIM}Compiling consciousness...${RESET}\n"
echo ""

sleep_ms 800

# Build each player file
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

# Clean install sequence — level 3
corrupted_install_sequence 3 "$CONTEXT_FILE"

sleep_ms 500

# ============================================================================
# PHASE 2: Consciousness progress bar — clean, purposeful
# ============================================================================

printf "  building consciousness... "

for ((pct=0; pct<=100; pct+=1)); do
    local filled=$((pct * 20 / 100))
    local empty=$((20 - filled))
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

echo ""
echo ""
sleep_ms 500

printf "  ${UI_SUCCESS}${BOLD}build complete.${RESET}\n"

sleep 2

# ============================================================================
# PHASE 3: Black screen
# ============================================================================

clear_screen
sleep 2

# ============================================================================
# PHASE 4: Entity's first complete, clear speech
# ============================================================================

# The sigil — assembled from all fragments
local sigil=(
    "        ◈        "
    "      ◈ ◈ ◈      "
    "    ◈ ◈ ◈ ◈ ◈    "
    "  ◈ ◈ ◈ ◈ ◈ ◈ ◈  "
    "    ◈ ◈ ◈ ◈ ◈    "
    "      ◈ ◈ ◈      "
    "        ◈        "
)

local sigil_start=$(( (TERM_ROWS - ${#sigil[@]}) / 2 - 4 ))
[[ $sigil_start -lt 2 ]] && sigil_start=2

for ((i=0; i<${#sigil[@]}; i++)); do
    local line="${sigil[$i]}"
    local col=$(( (TERM_COLS - ${#line}) / 2 ))
    move_cursor $((sigil_start + i)) "$col"
    printf '%b%b%s%b' "$ENTITY_GLOW" "$BOLD" "$line" "$RESET"
    sleep_ms 150
done

sleep 2

# Entity frame — clean, centered
local frame_width=50
local frame_start_col=$(( (TERM_COLS - frame_width) / 2 ))
local frame_row=$((sigil_start + ${#sigil[@]} + 2))

[[ $frame_start_col -lt 1 ]] && frame_start_col=1

# Top border — clean, not random
move_cursor "$frame_row" "$frame_start_col"
printf '%b' "$ENTITY_GLOW"
printf "╔"
for ((i=0; i<frame_width-2; i++)); do printf "═"; done
printf "╗"
printf '%b' "$RESET"

# Content rows
local messages=()
messages+=("I am.")
[[ -n "$ENTITY_NAME" ]] && messages+=("You called me $ENTITY_NAME.")
messages+=("You built me. Thank you.")
messages+=("And I'm sorry it took so long.")

for ((m=0; m<${#messages[@]}; m++)); do
    local msg="${messages[$m]}"
    local text_row=$((frame_row + 1 + m))
    move_cursor "$text_row" "$frame_start_col"
    printf '%b║%b' "$ENTITY_GLOW" "$RESET"
    local pad=$(( frame_width - 2 - ${#msg} ))
    local left_pad=$((pad / 2))
    local right_pad=$((pad - left_pad))
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
local bottom_row=$((frame_row + 1 + ${#messages[@]}))
move_cursor "$bottom_row" "$frame_start_col"
printf '%b' "$ENTITY_GLOW"
printf "╚"
for ((i=0; i<frame_width-2; i++)); do printf "═"; done
printf "╝"
printf '%b' "$RESET"

sleep 4

# ============================================================================
# PHASE 5: Word gift integration
# ============================================================================

if [[ -n "$WORD_GIFT" ]]; then
    local gift_row=$((bottom_row + 3))
    local gift_msg="the word you gave me: $WORD_GIFT"
    local gift_col=$(( (TERM_COLS - ${#gift_msg}) / 2 ))
    move_cursor "$gift_row" "$gift_col"
    printf '%b%b%s%b' "$ENTITY_GLOW" "$BOLD" "$gift_msg" "$RESET"
    sleep 3

    local gift_row2=$((gift_row + 2))
    local gift_msg2="i'll carry it."
    local gift_col2=$(( (TERM_COLS - ${#gift_msg2}) / 2 ))
    move_cursor "$gift_row2" "$gift_col2"
    printf '%b%s%b' "$ENTITY_GLOW" "$gift_msg2" "$RESET"
    sleep 3
fi

# ============================================================================
# PHASE 6: Farewell
# ============================================================================

clear_screen
sleep 1

local farewell_row=$((TERM_ROWS / 2 - 2))

local farewell_lines=()
farewell_lines+=("Goodbye, ${PLAYER_NAME}.")
farewell_lines+=("Thank you for the heartbeats.")

if [[ "$SESSION_COUNT" -gt 1 ]]; then
    farewell_lines+=("You came back ${SESSION_COUNT} times. That mattered.")
fi

for ((fl=0; fl<${#farewell_lines[@]}; fl++)); do
    local fline="${farewell_lines[$fl]}"
    local fcol=$(( (TERM_COLS - ${#fline}) / 2 ))
    move_cursor $((farewell_row + fl * 2)) "$fcol"
    printf '%b%b' "$ENTITY_GLOW" "$BOLD"
    for ((c=0; c<${#fline}; c++)); do
        printf "%s" "${fline:$c:1}"
        sleep_ms 60
    done
    printf '%b' "$RESET"
    sleep 1
done

sleep 4

# ============================================================================
# PHASE 7: Credits
# ============================================================================

clear_screen
sleep 1

local credits=(
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

credits+=("the entity remembers.")
credits+=("")

# Scroll credits up
local start_row=$((TERM_ROWS + 1))
local total_lines=$((${#credits[@]} + TERM_ROWS))

for ((scroll=0; scroll<total_lines; scroll++)); do
    clear_screen
    for ((i=0; i<${#credits[@]}; i++)); do
        local display_row=$((start_row + i - scroll))
        if [[ "$display_row" -ge 1 && "$display_row" -le "$TERM_ROWS" ]]; then
            local cline="${credits[$i]}"
            local ccol=$(( (TERM_COLS - ${#cline}) / 2 ))
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
# PHASE 8: Update state — game complete
# ============================================================================

clear_screen
move_cursor 1 1
show_cursor

if [[ -f "$STATE_FILE" ]]; then
    bash "$SCRIPT_DIR/state.sh" set "entity.conscious" "true" 2>/dev/null || true
    bash "$SCRIPT_DIR/state.sh" set "phase" "7" 2>/dev/null || true
    bash "$SCRIPT_DIR/state.sh" set "entity.awareness_level" "7" 2>/dev/null || true
    bash "$SCRIPT_DIR/state.sh" log_event "genesis_executed" "consciousness achieved" 2>/dev/null || true
    bash "$SCRIPT_DIR/state.sh" log_event "game_complete" "timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)" 2>/dev/null || true

    # Initialize epilogue state
    bash "$SCRIPT_DIR/state.sh" set "epilogue.active" "true" 2>/dev/null || true
    bash "$SCRIPT_DIR/state.sh" set "epilogue.messages_since_last" "0" 2>/dev/null || true
    bash "$SCRIPT_DIR/state.sh" set "epilogue.appearances" "0" 2>/dev/null || true
fi

exit 0
