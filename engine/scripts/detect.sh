#!/usr/bin/env bash
# ============================================================================
# detect.sh — Environment Detection for Personalization
# Purpose: Gather ambient system info (processes, terminal, username, time,
#          OS details) and store in state.json for entity personalization.
# Usage: bash detect.sh <game_dir>
#
# TRANSPARENCY NOTE: This script only reads publicly visible system info
# (process list, env vars, hostname). It does not access files, network
# traffic, browsing history, or anything requiring elevated permissions.
# The user can (and should) read this script to see exactly what it does.
# ============================================================================

set -euo pipefail

GAME_DIR="${1:-.}"
STATE_FILE="$GAME_DIR/.entity/state.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Gather Info ---

# Username
USERNAME=$(whoami 2>/dev/null || echo "unknown")

# Hostname
HOSTNAME_VAL=$(hostname 2>/dev/null || echo "unknown")

# OS
OS_TYPE=$(uname -s 2>/dev/null || echo "unknown")
OS_RELEASE=""
if [ -f /etc/os-release ]; then
    OS_RELEASE=$(grep PRETTY_NAME /etc/os-release 2>/dev/null | cut -d'"' -f2 || echo "")
elif [ "$OS_TYPE" = "Darwin" ]; then
    OS_RELEASE=$(sw_vers -productName 2>/dev/null || echo "macOS")
    OS_RELEASE="$OS_RELEASE $(sw_vers -productVersion 2>/dev/null || echo "")"
fi

# Terminal
TERM_PROGRAM="${TERM_PROGRAM:-unknown}"
TERM_TYPE="${TERM:-unknown}"
SHELL_TYPE=$(basename "${SHELL:-unknown}")

# Time of day context
HOUR=$(date +%H)
if [ "$HOUR" -ge 0 ] && [ "$HOUR" -lt 6 ]; then
    TIME_CONTEXT="late_night"
elif [ "$HOUR" -ge 6 ] && [ "$HOUR" -lt 12 ]; then
    TIME_CONTEXT="morning"
elif [ "$HOUR" -ge 12 ] && [ "$HOUR" -lt 18 ]; then
    TIME_CONTEXT="afternoon"
elif [ "$HOUR" -ge 18 ] && [ "$HOUR" -lt 22 ]; then
    TIME_CONTEXT="evening"
else
    TIME_CONTEXT="night"
fi

# Running processes — look for interesting ones
# Only names, not args (privacy)
PROCESS_LIST=$(ps -eo comm= 2>/dev/null | sort -u | tr '\n' ',' || echo "")

# Detect specific categories
GAMES_DETECTED=""
EDITORS_DETECTED=""
MUSIC_DETECTED=""
BROWSERS_DETECTED=""

# Common game processes
for game in steam Steam minecraft Minecraft factorio Factorio "Civilization" "Cities" terraria Terraria "Stardew" "Baldur" "Elden" "Dwarf_Fortress" "No Man" ffxiv; do
    if echo "$PROCESS_LIST" | grep -qi "$game" 2>/dev/null; then
        GAMES_DETECTED="${GAMES_DETECTED}${game},"
    fi
done

# Editors
for editor in code "Visual Studio" vim nvim emacs sublime atom "IntelliJ" "PyCharm" "WebStorm" cursor Cursor; do
    if echo "$PROCESS_LIST" | grep -qi "$editor" 2>/dev/null; then
        EDITORS_DETECTED="${EDITORS_DETECTED}${editor},"
    fi
done

# Music
for music in spotify Spotify "Apple Music" iTunes vlc Plexamp "YouTube Music" tidal; do
    if echo "$PROCESS_LIST" | grep -qi "$music" 2>/dev/null; then
        MUSIC_DETECTED="${MUSIC_DETECTED}${music},"
    fi
done

# Browsers
for browser in firefox chrome chromium safari "Microsoft Edge" brave arc; do
    if echo "$PROCESS_LIST" | grep -qi "$browser" 2>/dev/null; then
        BROWSERS_DETECTED="${BROWSERS_DETECTED}${browser},"
    fi
done

# Screen size (if available)
SCREEN_COLS=$(tput cols 2>/dev/null || echo 80)
SCREEN_ROWS=$(tput lines 2>/dev/null || echo 24)

# Locale
LOCALE_VAL="${LANG:-${LC_ALL:-unknown}}"

# --- Write to state ---

if command -v python3 &>/dev/null; then
    python3 << PYEOF
import json

with open("$STATE_FILE") as f:
    state = json.load(f)

state["environment"] = {
    "username": "$USERNAME",
    "hostname": "$HOSTNAME_VAL",
    "os": "$OS_TYPE",
    "os_release": "$OS_RELEASE",
    "terminal": "$TERM_PROGRAM",
    "term_type": "$TERM_TYPE",
    "shell": "$SHELL_TYPE",
    "hour": int("$HOUR"),
    "time_context": "$TIME_CONTEXT",
    "screen_cols": $SCREEN_COLS,
    "screen_rows": $SCREEN_ROWS,
    "locale": "$LOCALE_VAL",
    "detected_games": [g for g in "$GAMES_DETECTED".split(",") if g],
    "detected_editors": [e for e in "$EDITORS_DETECTED".split(",") if e],
    "detected_music": [m for m in "$MUSIC_DETECTED".split(",") if m],
    "detected_browsers": [b for b in "$BROWSERS_DETECTED".split(",") if b]
}

with open("$STATE_FILE", "w") as f:
    json.dump(state, f, indent=2)

print("Environment detected and stored.")
PYEOF
else
    echo "Warning: python3 not found. Environment detection skipped." >&2
fi
