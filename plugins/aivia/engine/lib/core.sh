#!/usr/bin/env bash
# ============================================================================
# core.sh — Bootstrap & Constants
# Purpose: Foundation for all aivia lib files. Source this first.
# Usage: source "path/to/lib/core.sh"
# ============================================================================

# Guard against double-sourcing
[[ -n "${_AIVIA_CORE_LOADED:-}" ]] && return 0
_AIVIA_CORE_LOADED=1

# --- LIB_DIR detection ---
# Find the lib directory relative to wherever this file is sourced from
if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
    _AIVIA_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    _AIVIA_LIB_DIR="${_AIVIA_LIB_DIR:-$(pwd)/lib}"
fi
readonly AIVIA_LIB_DIR="$_AIVIA_LIB_DIR"
readonly AIVIA_ROOT_DIR="$(dirname "$AIVIA_LIB_DIR")"

# --- Terminal dimensions ---
# Safe for non-TTY environments (piped, CI, headless)
_aivia_refresh_dimensions() {
    if [ -t 1 ]; then
        TERM_COLS=$(tput cols 2>/dev/null || echo 80)
        TERM_ROWS=$(tput lines 2>/dev/null || echo 24)
    else
        TERM_COLS=${COLUMNS:-80}
        TERM_ROWS=${LINES:-24}
    fi
}
_aivia_refresh_dimensions

# --- Dimension constants ---
readonly MIN_WIDTH=40
readonly MAX_WIDTH=120
readonly STANDARD_WIDTH=80

# CONTENT_WIDTH: dynamically computed as min(TERM_COLS, MAX_WIDTH)
_aivia_compute_content_width() {
    if [ "$TERM_COLS" -le "$MAX_WIDTH" ]; then
        CONTENT_WIDTH=$TERM_COLS
    else
        CONTENT_WIDTH=$MAX_WIDTH
    fi
}
_aivia_compute_content_width

# --- Cross-platform millisecond sleep ---
# Honors AIVIA_SPEED_MULT env var (percentage: 50=2x faster, 200=2x slower)
sleep_ms() {
    local ms=$1
    if [[ -n "${AIVIA_SPEED_MULT:-}" ]] && [[ "$AIVIA_SPEED_MULT" -ne 100 ]]; then
        ms=$(( ms * AIVIA_SPEED_MULT / 100 ))
        [[ "$ms" -lt 1 ]] && ms=1
    fi
    if command -v python3 &>/dev/null; then
        python3 -c "import time; time.sleep($ms/1000.0)"
    else
        sleep "0.$(printf '%03d' "$ms")"
    fi
}

# --- Source other lib files ---
# Usage: source_lib style terminal text
source_lib() {
    local mod
    for mod in "$@"; do
        local path="$AIVIA_LIB_DIR/${mod}.sh"
        if [[ -f "$path" ]]; then
            # shellcheck disable=SC1090
            source "$path"
        else
            echo "aivia: lib module not found: $mod ($path)" >&2
            return 1
        fi
    done
}

# --- Source theme files ---
# Usage: source_theme entity
source_theme() {
    local mod
    for mod in "$@"; do
        local path="$AIVIA_ROOT_DIR/theme/${mod}.sh"
        if [[ -f "$path" ]]; then
            # shellcheck disable=SC1090
            source "$path"
        else
            echo "aivia: theme not found: $mod ($path)" >&2
            return 1
        fi
    done
}

# --- Random number utility ---
random_int() {
    local min=$1 max=$2
    echo $(( RANDOM % (max - min + 1) + min ))
}

# --- Random choice from array ---
# Usage: random_choice "${array[@]}"
random_choice() {
    local arr=("$@")
    echo "${arr[$((RANDOM % ${#arr[@]}))]}"
}
