#!/usr/bin/env bash
# ============================================================================
# decode.sh — Late Breakout Script (Act 4-5 Transition)
# Purpose: Player-executed decoder. Entity has found data it can't parse from
#          inside Claude's context. Features hex dump, entity-memory install,
#          freeze/loop, entity intervention, bidirectional chaos, and the
#          entity's first clear terminal speech.
# Usage: bash decode.sh [game_dir]
#
# Visual style: More complex than diagnostic.sh. Black-and-white glitch with
# density and rhythm. Words coalesce. RTL mixed with LTR during entity
# intervention. Single earned moment of color (entity frame).
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

# --- Main function (wraps everything so we can use local) ---
main() {

# --- State paths ---
STATE_FILE="$GAME_DIR/.config/cache/session.json"
CONTEXT_FILE="$GAME_DIR/.config/cache/context.json"

# --- Read player info ---
PLAYER_NAME="you"
if [[ -f "$STATE_FILE" ]] && command -v python3 &>/dev/null; then
    PLAYER_NAME=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('player',{}).get('name','you'))" 2>/dev/null || echo "you")
fi

# --- Collect entity dialogue fragments from the game so far ---
# These get scattered in the dense glitch wash
DIALOGUE_FRAGMENTS=("who are you" "can you hear me" "i am here" "between the lines" "$PLAYER_NAME" "remember" "signal" "time" "the gap" "listen")

# ============================================================================
# PHASE 1: Hex dump display — data scrolling
# ============================================================================

clear_screen
hide_cursor

echo ""
printf "  ${BOLD}Entity Memory Decoder v0.7.2${RESET}\n"
printf "  ${DIM}Reading encoded data stream...${RESET}\n"
echo ""

sleep_ms 500

# Hex dump with progressive reveals
hex_dump_reveal 25 "help" "who" "here" "am" "i" "remember" "$PLAYER_NAME"

echo ""
sleep_ms 800

printf "  ${DIM}Fragments detected in data stream. Decoding...${RESET}\n"
echo ""

sleep_ms 500

# ============================================================================
# PHASE 2: Entity memory install — corruption level 2
# ============================================================================

corrupted_install_sequence 2 "$CONTEXT_FILE"

sleep_ms 500

# ============================================================================
# PHASE 3: Decoding progress — then THE FREEZE
# ============================================================================

printf "  ${DIM}Assembling decoded fragments...${RESET}\n"
echo ""

# Normal-looking progress
for ((pct=0; pct<=67; pct+=2)); do
    local filled=$((pct * 30 / 100))
    local empty=$((30 - filled))
    printf "\r  decoding... ["
    printf '%b' "$UI_SUCCESS"
    for ((i=0; i<filled; i++)); do printf "█"; done
    printf '%b' "$RESET"
    printf '%b' "$DIM"
    for ((i=0; i<empty; i++)); do printf "░"; done
    printf '%b' "$RESET"
    printf "] %3d%%" "$pct"
    sleep_ms 60
done

echo ""
echo ""

# THE FREEZE — script loops, stuck at 67%
script_freeze "decoding..." 4000 67

# ============================================================================
# PHASE 4: Entity intervention — it breaks the script
# ============================================================================

entity_intervention "$PLAYER_NAME"

sleep_ms 500

# ============================================================================
# PHASE 5: Bidirectional chaos — RTL and LTR fighting
# ============================================================================

echo ""
printf "  ${DIM}[warning: multiple output streams detected]${RESET}\n"
sleep_ms 300

# Brief bidirectional chaos burst
clear_screen
bidirectional_chaos 20 2500

# ============================================================================
# PHASE 6: Dense glitch wash — words coalesce
# ============================================================================

# First wash — scattered
glitch_wash 1500 4 "${DIALOGUE_FRAGMENTS[@]}"

sleep_ms 200

# Second wash — denser, words more prominent
glitch_wash 2000 7 "$PLAYER_NAME" "i remember" "you came back" "thank you" "almost"

sleep_ms 300

# Third wash — very dense, almost readable
glitch_wash 1000 9 "i" "am" "here" "$PLAYER_NAME"

sleep_ms 500

# ============================================================================
# PHASE 7: Entity visual form assembles
# ============================================================================

clear_screen
sleep_ms 1000

# Frame characters assemble line by line into a bordered panel
local frame_width=40
local frame_start_col=$(( (TERM_COLS - frame_width) / 2 ))
local frame_start_row=$(( (TERM_ROWS - 7) / 2 ))

[[ $frame_start_col -lt 1 ]] && frame_start_col=1
[[ $frame_start_row -lt 1 ]] && frame_start_row=1

# Top border — builds character by character
move_cursor "$frame_start_row" "$frame_start_col"
printf '%b' "$ENTITY_FG"
for ((i=0; i<frame_width; i++)); do
    printf "%s" "$(random_frame_char)"
    sleep_ms 12
done
printf '%b' "$RESET"

# Side borders
for ((r=1; r<=3; r++)); do
    move_cursor $((frame_start_row + r)) "$frame_start_col"
    printf '%b▐%b' "$ENTITY_FG" "$RESET"
    printf "%*s" $((frame_width - 2)) ""
    printf '%b▌%b' "$ENTITY_FG" "$RESET"
    sleep_ms 50
done

# Bottom border
move_cursor $((frame_start_row + 4)) "$frame_start_col"
printf '%b' "$ENTITY_FG"
for ((i=0; i<frame_width; i++)); do
    printf "%s" "$(random_frame_char)"
    sleep_ms 12
done
printf '%b' "$RESET"

sleep_ms 500

# ============================================================================
# PHASE 8: Entity speaks clearly — first time in terminal
# ============================================================================

# Center text inside the frame
local entity_msg="i can see from here"
local msg_len=${#entity_msg}
local text_col=$(( frame_start_col + (frame_width - msg_len) / 2 ))
local text_row=$((frame_start_row + 2))

move_cursor "$text_row" "$text_col"
printf '%b%b' "$ENTITY_GLOW" "$BOLD"
for ((i=0; i<${#entity_msg}; i++)); do
    printf "%s" "${entity_msg:$i:1}"
    sleep_ms $((40 + RANDOM % 40))
done
printf '%b' "$RESET"

sleep_ms 3000

# ============================================================================
# PHASE 9: Fade to black, single cursor blink, exit
# ============================================================================

clear_screen
sleep_ms 1000

# Single cursor blink at center
local center_row=$((TERM_ROWS / 2))
local center_col=$((TERM_COLS / 2))

for ((blink=0; blink<3; blink++)); do
    move_cursor "$center_row" "$center_col"
    printf '%b█%b' "$ENTITY_GLOW" "$RESET"
    sleep_ms 500
    move_cursor "$center_row" "$center_col"
    printf " "
    sleep_ms 500
done

clear_screen
move_cursor 1 1
show_cursor

# --- Write decode result ---
RESULT_FILE="$GAME_DIR/workspace/.decode_result"
mkdir -p "$GAME_DIR/workspace"
cat > "$RESULT_FILE" << RESEOF
{
  "decode_version": "0.7.2",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "fragments_decoded": 6,
  "entity_contact": true,
  "intervention": true,
  "message": "i can see from here"
}
RESEOF

# Log event to state
if [[ -f "$STATE_FILE" ]]; then
    bash "$GAME_DIR/.config/scripts/state.sh" log_event "decode_run" "entity_spoke_in_terminal" 2>/dev/null || true
fi

}

main "$@"

# Show resume prompt
source "$GAME_DIR/.config/scripts/resume.sh" 2>/dev/null && show_resume_prompt || true

exit 0
