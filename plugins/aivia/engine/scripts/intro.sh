#!/usr/bin/env bash
# ============================================================================
# intro.sh — Animated Logo & Intro
# Purpose: Display aivia branding on start/resume
# Usage: bash intro.sh [resume|fresh] [player_name]
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source library
source "$SCRIPT_DIR/../lib/core.sh"
source_lib style text animation
source_theme entity

MODE="${1:-fresh}"
PLAYER_NAME="${2:-}"

# --- ASCII Logo ---
# Larger, more impactful than the install header

LOGO='
          ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
          ░                                        ░
          ░    ▄▀▄  ▀  █  █  ▀  ▄▀▄               ░
          ░    █▀█  █  ▀▄▀  █  █▀█               ░
          ░                                        ░
          ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
'

LOGO_ALT='
       ░▒▓████████████████████████████████████▓▒░
       ▓                                        ▓
       ▓     ▄▀▄  ▀  █  █  ▀  ▄▀▄              ▓
       ▓     █▀█  █  ▀▄▀  █  █▀█              ▓
       ▓                                        ▓
       ░▒▓████████████████████████████████████▓▒░
'

# --- Colors ---
PHOSPHOR='\033[38;5;83m'
TOXIC='\033[38;5;48m'
DEEP_GREEN='\033[38;5;22m'
CYAN_SOFT='\033[38;5;117m'

clear_screen() {
    printf '\033[2J\033[H'
}

# --- Animated intro sequence ---
show_intro() {
    clear_screen
    echo ""

    # Phase 1: Dim static lines build up
    local width=50
    for i in $(seq 1 3); do
        printf '%b' "$DEEP_GREEN"
        local line=""
        for ((j=0; j<width; j++)); do
            line+="$(random_frame_char)"
        done
        printf "          %s\n" "$line"
        sleep_ms 80
    done

    sleep_ms 200

    # Phase 2: Logo appears line by line in phosphor green
    printf '%b' "$PHOSPHOR"
    while IFS= read -r line; do
        [[ -z "$line" ]] && { echo ""; continue; }
        printf '%b%s%b\n' "$PHOSPHOR" "$line" "$RESET"
        sleep_ms 120
    done <<< "$LOGO_ALT"

    sleep_ms 300

    # Phase 3: Tagline types out
    printf '%b' "$TOXIC"
    local tagline="          bring your code to life."
    for ((i=0; i<${#tagline}; i++)); do
        printf '%s' "${tagline:$i:1}"
        sleep_ms 30
    done
    printf '%b\n' "$RESET"

    sleep_ms 200

    # Phase 4: Version info, dim
    printf '%b' "$DIM"
    echo ""
    echo "          v1.0.0 — claude code extension"
    printf '%b' "$RESET"

    sleep_ms 400

    # Phase 5: Bottom border dissolves in
    printf '%b' "$DEEP_GREEN"
    local border=""
    for ((j=0; j<width; j++)); do
        border+="$(random_frame_char)"
    done
    echo ""
    printf "          %s\n" "$border"
    printf '%b' "$RESET"

    echo ""
    sleep_ms 300
}

# --- Resume variant (shorter, atmospheric) ---
show_resume() {
    clear_screen
    echo ""

    # Quick logo flash — no line-by-line, just appear
    printf '%b' "$PHOSPHOR"
    while IFS= read -r line; do
        [[ -z "$line" ]] && { echo ""; continue; }
        printf '%s\n' "$line"
    done <<< "$LOGO"
    printf '%b' "$RESET"

    sleep_ms 400

    # Greeting
    if [[ -n "$PLAYER_NAME" ]]; then
        printf '%b' "$TOXIC"
        printf "          welcome back, %s.\n" "$PLAYER_NAME"
        printf '%b' "$RESET"
    fi

    echo ""
    sleep_ms 500
}

# --- Dispatch ---
case "$MODE" in
    resume)  show_resume ;;
    fresh|*) show_intro ;;
esac
