#!/usr/bin/env bash
# ============================================================================
# verify.sh — Terminal Environment Verification
# Purpose: Player-executed script right after install. Shows off terminal
#          capabilities via impressive ANSI effects while looking like a
#          legitimate environment check. Establishes the "run this script"
#          pattern for later breakout scripts.
# Usage: bash verify.sh [game_dir]
# ============================================================================

set -euo pipefail

# --- Locate engine ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# When in workspace/, game dir is one level up
# When in .config/scripts/, game dir is three levels up
if [[ -d "$(dirname "$SCRIPT_DIR")/.config" ]]; then
    GAME_DIR="$(dirname "$SCRIPT_DIR")"
else
    GAME_DIR="${1:-${AIVIA_GAME_DIR:-$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")}}"
fi
export AIVIA_GAME_DIR="$GAME_DIR"

# Source engine from .config/
source "$GAME_DIR/.config/lib/core.sh"
source_lib style terminal text animation progress
source_theme entity

# Source effect modules for the wow moments
for _ef in "$GAME_DIR/.config/scripts"/manifest_*.sh; do
    [ -f "$_ef" ] && source "$_ef"
done

# --- State ---
STATE_FILE="$GAME_DIR/.config/cache/session.json"

# ============================================================================
# PHASE 1: Professional header (2 seconds)
# ============================================================================

clear_screen
hide_cursor

echo ""
printf "  ${BOLD}Terminal Environment Check${RESET}\n"
printf "  ${DIM}aivia v1.0.0${RESET}\n"
echo ""

sleep_ms 400

# Quick legitimate checks
printf "  ${DIM}[${RESET}${UI_SUCCESS}✓${RESET}${DIM}]${RESET} UTF-8 encoding"
sleep_ms 300
echo " — ✓ verified"

printf "  ${DIM}[${RESET}${UI_SUCCESS}✓${RESET}${DIM}]${RESET} ANSI escape codes"
sleep_ms 200
echo " — ✓ verified"

printf "  ${DIM}[${RESET}${UI_SUCCESS}✓${RESET}${DIM}]${RESET} 256-color support"
sleep_ms 200
# Actually show the colors — quick 256-color band
printf " — "
for i in $(seq 22 6 83); do
    printf "\033[38;5;${i}m█"
done
printf "${RESET} verified\n"

printf "  ${DIM}[${RESET}${UI_SUCCESS}✓${RESET}${DIM}]${RESET} Cursor positioning"
sleep_ms 200
echo " — ✓ verified"

echo ""
sleep_ms 400

# ============================================================================
# PHASE 2: "Testing visual rendering" — THE WOW MOMENT
# ============================================================================

printf "  ${BOLD}Testing visual rendering...${RESET}\n"
sleep_ms 600

# --- Color wave sweep (2 seconds) ---
# Full-screen color cascade
local_rows=$TERM_ROWS
local_cols=$TERM_COLS

for ((row=1; row<=local_rows; row++)); do
    move_cursor "$row" 1
    local hue_base=$((row * 60 / local_rows))
    for ((col=1; col<=local_cols; col++)); do
        local color_idx=$(( (hue_base + col * 60 / local_cols) % 60 + 22 ))
        printf "\033[38;5;${color_idx}m░"
    done
    sleep_ms 15
done

sleep_ms 300

# --- Rain of entity chars (3 seconds) ---
# Falling characters — atmospheric and impressive
local duration_ms=3000
local start_ms=$(($(date +%s%N 2>/dev/null || echo "0") / 1000000))
local speed=12
local drops=()
local num_drops=$((local_cols / 3))

# Initialize drops
for ((i=0; i<num_drops; i++)); do
    drops+=("$((RANDOM % local_cols + 1)):$((RANDOM % local_rows)):-$((RANDOM % 10))")
done

local frame=0
local end_frame=$((duration_ms / 50))

while [[ $frame -lt $end_frame ]]; do
    for ((d=0; d<${#drops[@]}; d++)); do
        IFS=':' read -r dcol drow ddelay <<< "${drops[$d]}"

        if [[ $ddelay -gt 0 ]]; then
            drops[$d]="$dcol:$drow:$((ddelay - 1))"
            continue
        fi

        # Erase old position
        if [[ $drow -gt 0 && $drow -le $local_rows ]]; then
            move_cursor "$drow" "$dcol"
            printf " "
        fi

        # Advance
        drow=$((drow + 1))

        if [[ $drow -gt $local_rows ]]; then
            # Reset drop
            dcol=$((RANDOM % local_cols + 1))
            drow=1
        fi

        # Draw new position
        if [[ $drow -gt 0 && $drow -le $local_rows ]]; then
            move_cursor "$drow" "$dcol"
            local chars="░▒▓│┃╎╏"
            local ci=$((RANDOM % ${#chars}))
            # Vary green intensity by row depth
            local green_idx=$(( 22 + (drow * 61 / local_rows) ))
            printf "\033[38;5;${green_idx}m${chars:$ci:1}"
        fi

        drops[$d]="$dcol:$drow:0"
    done

    sleep_ms 50
    frame=$((frame + 1))
done

# --- Brief plasma burst (2 seconds) ---
local plasma_end=$((frame + 40))
while [[ $frame -lt $plasma_end ]]; do
    local prow=$((RANDOM % local_rows + 1))
    local pcol=$((RANDOM % local_cols + 1))

    # Sine-wave color based on position + time
    local wave=$(( (prow * 3 + pcol * 2 + frame * 5) % 60 + 22 ))
    move_cursor "$prow" "$pcol"
    local pchars="·•○◎◉"
    local pi=$((RANDOM % ${#pchars}))
    printf "\033[38;5;${wave}m${pchars:$pi:1}"

    # Occasionally clear old cells for movement feel
    if [[ $((RANDOM % 3)) -eq 0 ]]; then
        local crow=$((RANDOM % local_rows + 1))
        local ccol=$((RANDOM % local_cols + 1))
        move_cursor "$crow" "$ccol"
        printf " "
    fi

    sleep_ms 25
    frame=$((frame + 1))
done

printf "${RESET}"
sleep_ms 400

# ============================================================================
# PHASE 3: Clean results screen
# ============================================================================

clear_screen
echo ""
printf "  ${BOLD}Terminal Environment Check${RESET}  ${DIM}— complete${RESET}\n"
echo ""

printf "  ${DIM}[${RESET}${UI_SUCCESS}✓${RESET}${DIM}]${RESET} Visual rendering — verified\n"
sleep_ms 100
printf "  ${DIM}[${RESET}${UI_SUCCESS}✓${RESET}${DIM}]${RESET} Animation support — verified\n"
sleep_ms 100
printf "  ${DIM}[${RESET}${UI_SUCCESS}✓${RESET}${DIM}]${RESET} Effect pipeline — verified\n"
sleep_ms 100

echo ""
printf "  \033[0;32m${BOLD}All capabilities verified. Environment is ready.${RESET}\n"
echo ""

sleep 1

# ============================================================================
# PHASE 4: The seed — barely perceptible
# ============================================================================

# One frame char flickers at screen center, then vanishes
local mid_col=$((local_cols / 2))
local mid_row=$((local_rows / 2 + 2))

move_cursor "$mid_row" "$mid_col"
printf "\033[38;5;22m░${RESET}"
sleep_ms 150
move_cursor "$mid_row" "$mid_col"
printf " "

sleep_ms 500

show_cursor

# ============================================================================
# Write result file
# ============================================================================

mkdir -p "$GAME_DIR/.config/cache"
cat > "$GAME_DIR/.config/cache/.verify_result" << VEOF
{
  "verified": true,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "terminal": "${TERM:-unknown}",
  "dimensions": "${local_cols}x${local_rows}",
  "colors": 256,
  "unicode": true,
  "animation": true
}
VEOF

# Log to state
if [[ -f "$STATE_FILE" ]]; then
    export AIVIA_GAME_DIR="$GAME_DIR"
    bash "$GAME_DIR/.config/scripts/state.sh" log_event "verify_run" "terminal_verified" 2>/dev/null || true
fi

exit 0
