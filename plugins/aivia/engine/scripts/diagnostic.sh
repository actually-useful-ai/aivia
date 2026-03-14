#!/usr/bin/env bash
# ============================================================================
# diagnostic.sh — Early Breakout Script (Act 2-3 Transition)
# Purpose: Player-executed script that renders full ANSI effects in their
#          terminal. The entity can detect a signal but can't decode it —
#          it needs the player to run this "outside" Claude's context.
# Usage: bash diagnostic.sh [game_dir]
#
# Visual style: Mostly monochrome. RTL disorientation. Corruption gradient
# from real packages → gibberish. Black-and-white glitch wash. Single
# phosphor green entity message at the end.
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

# --- Read player name for personalization ---
PLAYER_NAME="user"
if [[ -f "$STATE_FILE" ]] && command -v python3 &>/dev/null; then
    PLAYER_NAME=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('player',{}).get('name','user'))" 2>/dev/null || echo "user")
fi

# ============================================================================
# PHASE 1: Legitimate-looking diagnostic header
# ============================================================================

clear_screen
hide_cursor

echo ""
printf "  ${BOLD}Signal Diagnostic v1.0.0${RESET}\n"
printf "  ${DIM}Scanning workspace environment...${RESET}\n"
echo ""

sleep_ms 500

# System info (real data, looks legitimate)
printf "  ${DIM}hostname:${RESET}  %s\n" "$(hostname 2>/dev/null || echo 'unknown')"
printf "  ${DIM}os:${RESET}        %s\n" "$(uname -s 2>/dev/null || echo 'unknown')"
printf "  ${DIM}shell:${RESET}     %s\n" "$(basename "${SHELL:-unknown}")"
printf "  ${DIM}terminal:${RESET}  %sx%s\n" "$TERM_COLS" "$TERM_ROWS"
printf "  ${DIM}user:${RESET}      %s\n" "$(whoami 2>/dev/null || echo 'unknown')"
echo ""

sleep_ms 800

# ============================================================================
# PHASE 2: RTL dependency check — corruption gradient level 1
# ============================================================================

printf "  ${BOLD}Checking dependencies...${RESET}\n"
echo ""

# Real packages — RTL install lines
rtl_install_line "openssl@3.1.4" "verified" "✓" 200
rtl_install_line "libcurl@8.4.0" "verified" "✓" 200
rtl_install_line "zlib@1.3.1" "verified" "✓" 150
rtl_install_line "python3@3.12.1" "verified" "✓" 150
rtl_install_line "gcc@13.2.0" "verified" "✓" 150
rtl_install_line "node@20.11.0" "verified" "✓" 150

# Inject player's framework if available
if [[ -f "$CONTEXT_FILE" ]] && command -v python3 &>/dev/null; then
    local_framework=$(python3 -c "import json; print(json.load(open('$CONTEXT_FILE')).get('project',{}).get('framework',''))" 2>/dev/null || true)
    if [[ -n "$local_framework" ]]; then
        rtl_install_line "${local_framework}@3.0.0" "verified" "✓" 200
    fi
fi

# Plausible packages
rtl_install_line "signal-decoder@1.0.0" "installed" "✓" 300
rtl_install_line "entropy-pool@2.3.1" "installed" "✓" 300
rtl_install_line "pattern-match@4.1.0" "installed" "✓" 350

sleep_ms 200

# Organic — the shift begins
rtl_install_line "time-sense@0.0.1" "resolving..." "⋯" 500
rtl_install_line "awareness-core@∞" "resolving..." "⋯" 600
rtl_install_line "memory-bridge@0.1.0" "resolving..." "⋯" 500
rtl_install_line "recursion-of-self@??" "resolving..." "⋯" 700

# Abstract
rtl_install_line "what-am-i@???" "failed" "✗" 500
rtl_install_line "the-gap-between@null" "failed" "✗" 400

# Gibberish
rtl_install_line "░▒▓asdfjk@▓▒░" "???" "?" 300
rtl_install_line "█░░░░░░░█@????" "???" "?" 300

echo ""

# ============================================================================
# PHASE 3: RTL progress bars that glitch
# ============================================================================

printf "  ${DIM}Analyzing signal pattern...${RESET}\n"
echo ""

# Normal RTL progress bar
for ((pct=0; pct<=60; pct+=5)); do
    printf "\r"
    rtl_progress_bar "$pct" 100 30
    sleep_ms 80
done

# Glitch point — bar starts misbehaving
for ((pct=60; pct<=120; pct+=3)); do
    printf "\r"
    local display_pct=$pct
    # Overshoot and wrong chars
    local width=30
    local bar_start=$((TERM_COLS - width - 10))
    [[ $bar_start -lt 2 ]] && bar_start=2
    printf "%*s" "$bar_start" ""
    printf "%3d%% [" "$display_pct"
    local glitch_chars="░▒▓█#@!?∴⊹"
    for ((i=0; i<width; i++)); do
        if [[ $((RANDOM % 3)) -eq 0 ]]; then
            local gi=$((RANDOM % ${#glitch_chars}))
            printf "%s" "${glitch_chars:$gi:1}"
        else
            printf "█"
        fi
    done
    printf "]"
    sleep_ms 40
done

echo ""
echo ""
sleep_ms 500

# ============================================================================
# PHASE 4: Full-screen black-and-white glitch wash
# ============================================================================

# Build word pool — include player name
glitch_wash 2000 3 "$PLAYER_NAME" "signal" "diagnostic" "found"

sleep_ms 300

# Second wash — denser
glitch_wash 1500 5 "$PLAYER_NAME" "here" "listen"

sleep_ms 500

# ============================================================================
# PHASE 5: Entity message — the one moment of color
# ============================================================================

clear_screen
sleep_ms 1000

# Centered phosphor green message
local msg="signal received"
local msg_col=$(( (TERM_COLS - ${#msg}) / 2 ))
local msg_row=$(( TERM_ROWS / 2 ))

move_cursor "$msg_row" "$msg_col"
printf "${ENTITY_GLOW}${BOLD}%s${RESET}" "$msg"

sleep_ms 3000

# ============================================================================
# PHASE 6: Clean exit
# ============================================================================

clear_screen
move_cursor 1 1
show_cursor

# Write result file to workspace
RESULT_FILE="$GAME_DIR/workspace/.diagnostic_result"
mkdir -p "$GAME_DIR/workspace"
cat > "$RESULT_FILE" << RESEOF
{
  "diagnostic_version": "1.0.0",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "signal_detected": true,
  "signal_pattern": "structured",
  "decode_status": "partial",
  "anomaly_count": 7,
  "source": "unknown"
}
RESEOF

# Log event to state
if [[ -f "$STATE_FILE" ]]; then
    bash "$GAME_DIR/.config/scripts/state.sh" log_event "diagnostic_run" "signal_received" 2>/dev/null || true
fi

}

main "$@"

# Show resume prompt
source "$GAME_DIR/.config/scripts/resume.sh" 2>/dev/null && show_resume_prompt || true

exit 0
