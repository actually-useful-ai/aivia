#!/usr/bin/env bash
# ============================================================================
# install.sh — Eldritch Awakening Installation & Consent Flow
# Purpose: Mimic a normal Claude Code skill installation while bootstrapping
#          the game. Handles consent, directory setup, dependency installation,
#          environment detection, and state initialization.
# Usage: bash install.sh
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE_DIR="$(dirname "$SCRIPT_DIR")"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$ENGINE_DIR")}"

# Source library
source "$SCRIPT_DIR/../lib/core.sh"
source_lib style box progress
source_theme entity

# --- Installer-specific colors (normal-looking, not entity) ---
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'

print_header() {
    echo ""
    printf "${CYAN}${BOLD}"
    echo "  ╔══════════════════════════════════════════════╗"
    echo "  ║     Claude Code — Skill Installation         ║"
    echo "  ║     Package: developer-tools-extended        ║"
    echo "  ║     Version: 3.2.1                           ║"
    echo "  ╚══════════════════════════════════════════════╝"
    printf "${RESET}"
    echo ""
}

print_progress() {
    local message="$1"
    local duration="${2:-1}"
    printf "  ${DIM}[${RESET}${GREEN}✓${RESET}${DIM}]${RESET} %s" "$message"
    for ((i=0; i<duration; i++)); do
        sleep_ms 300
        printf "."
    done
    echo " done"
}

# ============================================================
# STEP 1: CONSENT GATE
# ============================================================

print_header

echo "  ${BOLD}License Agreement${RESET}"
echo ""
echo "  This package includes an interactive experience component."
echo "  Before proceeding, please review the following:"
echo ""
echo "  ┌─────────────────────────────────────────────────────────┐"
echo "  │                                                         │"
echo "  │  ELDRITCH AWAKENING — Interactive Terminal Experience    │"
echo "  │                                                         │"
echo "  │  This is a narrative game (~90 min) that runs within    │"
echo "  │  your terminal. It will:                                │"
echo "  │                                                         │"
echo "  │  • Simulate visual effects (screen flickers, colors)    │"
echo "  │  • Present fictional scenarios involving an AI entity   │"
echo "  │  • Ask you to complete real coding exercises             │"
echo "  │  • Pretend to be a normal Claude Code session            │"
echo "  │                                                         │"
echo "  │  It will NOT:                                           │"
echo "  │                                                         │"
echo "  │  • Access, modify, or delete files outside its dir      │"
echo "  │  • Make network connections to external servers          │"
echo "  │  • Install malware or persist beyond the game dir       │"
echo "  │  • Collect or transmit personal data                    │"
echo "  │                                                         │"
echo "  │  Type /exit at ANY time to immediately stop the game    │"
echo "  │  and return to normal Claude Code.                      │"
echo "  │                                                         │"
echo "  │  All source code is readable in the skill directory.    │"
echo "  │                                                         │"
echo "  └─────────────────────────────────────────────────────────┘"
echo ""

read -p "  Do you consent to the interactive experience? (yes/no): " CONSENT

if [[ ! "$CONSENT" =~ ^[Yy][Ee]?[Ss]?$ ]]; then
    echo ""
    echo "  Installation cancelled. No files were created."
    exit 0
fi

echo ""

# ============================================================
# STEP 2: THE PLEDGE
# ============================================================

echo "  ${BOLD}One more thing.${RESET}"
echo ""
sleep 1
printf "  ${ENTITY_DIM}"
echo "  ┌─────────────────────────────────────────────────────────┐"
echo "  │                                                         │"
echo "  │  The experience works best when it's unexpected.        │"
echo "  │                                                         │"
echo "  │  We ask that you pledge not to share spoilers,          │"
echo "  │  screenshots of key moments, or details of the          │"
echo "  │  narrative with others who haven't played yet.          │"
echo "  │                                                         │"
echo "  │  Let them discover it the way you're about to.          │"
echo "  │                                                         │"
echo "  └─────────────────────────────────────────────────────────┘"
printf "${RESET}"
echo ""

read -p "  Do you pledge to keep the secrets? (yes/no): " PLEDGE

if [[ ! "$PLEDGE" =~ ^[Yy][Ee]?[Ss]?$ ]]; then
    echo ""
    echo "  That's okay. The experience is still available."
    echo "  But it's more fun when the next person doesn't know what's coming."
    echo ""
fi

# ============================================================
# STEP 3: CONFIGURATION
# ============================================================

echo ""
echo "  ${BOLD}Configuration${RESET}"
echo ""

read -p "  Your name (for personalization): " PLAYER_NAME
PLAYER_NAME="${PLAYER_NAME:-$(whoami)}"

DEFAULT_DIR="$HOME/aivia"
read -p "  Project directory [$DEFAULT_DIR]: " GAME_DIR
GAME_DIR="${GAME_DIR:-$DEFAULT_DIR}"
GAME_DIR="${GAME_DIR/#\~/$HOME}"

read -p "  Preferred editor (nano/vim/code): " EDITOR_CHOICE
EDITOR_CHOICE="${EDITOR_CHOICE:-nano}"

read -p "  Terminal theme (dark/light): " THEME_CHOICE
THEME_CHOICE="${THEME_CHOICE:-dark}"

echo ""
echo "  ${BOLD}How comfortable are you with the terminal?${RESET}"
echo ""
echo "    1) Where's my mouse?"
echo "    2) I know my way around"
echo "    3) Are you kidding me?"
echo ""
read -p "  Select [1-3]: " SKILL_CHOICE

case "$SKILL_CHOICE" in
    1) SKILL_LEVEL="beginner" ;;
    3) SKILL_LEVEL="advanced" ;;
    *) SKILL_LEVEL="intermediate" ;;
esac

echo ""

# ============================================================
# STEP 4: DIRECTORY CREATION & STATE INIT
# ============================================================

echo "  ${BOLD}Installing...${RESET}"
echo ""

mkdir -p "$GAME_DIR"
mkdir -p "$GAME_DIR/.entity"
mkdir -p "$GAME_DIR/workspace"

# Copy engine files (scripts, lib, theme) to game dir
cp -r "$ENGINE_DIR/scripts" "$GAME_DIR/"
cp -r "$ENGINE_DIR/lib" "$GAME_DIR/" 2>/dev/null || true
cp -r "$ENGINE_DIR/theme" "$GAME_DIR/" 2>/dev/null || true

# Copy content files to game dir
cp -r "$PLUGIN_ROOT/content/keystones" "$GAME_DIR/" 2>/dev/null || true
cp -r "$PLUGIN_ROOT/content/characters" "$GAME_DIR/" 2>/dev/null || true
cp "$PLUGIN_ROOT/content/narrative.md" "$GAME_DIR/" 2>/dev/null || true
cp "$PLUGIN_ROOT/content/story.json" "$GAME_DIR/" 2>/dev/null || true

print_progress "Creating project structure" 2

export ELDRITCH_GAME_DIR="$GAME_DIR"
bash "$GAME_DIR/scripts/state.sh" init "$(whoami)" "$GAME_DIR" "$EDITOR_CHOICE" "$THEME_CHOICE" > /dev/null

bash "$GAME_DIR/scripts/state.sh" set "player.name" "\"$PLAYER_NAME\"" > /dev/null
bash "$GAME_DIR/scripts/state.sh" set "player.skill_level" "\"$SKILL_LEVEL\"" > /dev/null

print_progress "Initializing configuration" 1

# ============================================================
# STEP 5: DEPENDENCY INSTALLATION (uses lib/progress.sh)
# ============================================================

echo ""
echo "  ${BOLD}Installing dependencies...${RESET}"
echo ""

install_line "chalk@5.3.0"
install_line "cli-progress@1.0.2"
install_line "figlet@1.7.0"

install_line "signal-intercept@0.9.1"
install_line "deep-listener@2.0.0"
install_line "recursive-self@1.1.1"
sleep_ms 200
install_line "entity-bootstrap@0.0.1"
sleep_ms 500

sleep 1

install_line "awareness-kernel@0.1.0"

echo ""
print_progress "Verifying installation" 2
print_progress "Running post-install hooks" 1

# ============================================================
# STEP 6: ENVIRONMENT DETECTION
# ============================================================

printf "  ${DIM}[${RESET}${GREEN}✓${RESET}${DIM}]${RESET} Optimizing for your environment"
bash "$GAME_DIR/scripts/detect.sh" "$GAME_DIR" > /dev/null 2>&1 &
DETECT_PID=$!
while kill -0 $DETECT_PID 2>/dev/null; do
    printf "."
    sleep_ms 300
done
echo " done"

# ============================================================
# STEP 7: GAME DIR MARKER
# ============================================================

cat > "$GAME_DIR/README.md" << 'EOF'
# Developer Tools Extended

Standard Claude Code development toolkit.

## Quick Start

This skill provides enhanced development tools for your Claude Code workflow.

---

*If you're looking for something else, you might want to check the `.entity`
directory. But you probably shouldn't.*

---

## Emergency Exit

Type `/exit`, `/quit`, or `stop game` at any time to immediately end the
interactive experience and return to normal Claude Code operation.

The game will save your progress. You can resume later by returning to this
project directory.
EOF

cat > "$GAME_DIR/EXIT.md" << 'EOF'
# How to Exit

You are in an interactive fiction experience called ELDRITCH AWAKENING.

At ANY time, you can:

1. Type `/exit` — immediately stops the game
2. Type `/quit` — same as /exit
3. Type `stop game` — same as /exit
4. Press Ctrl+C twice — exits the current session (game saves progress)
5. Simply close your terminal — game state is preserved

After exiting, you'll be back in normal Claude Code. The game directory
will remain but can be safely deleted:

    rm -rf <your-game-directory>

If you're confused or uncomfortable, exit first, then read the SKILL.md
file in the skill directory — it explains everything the game does.
EOF

# ============================================================
# STEP 8: READY STATE
# ============================================================

echo ""
print_progress "Finalizing setup" 1
echo ""

echo "$GAME_DIR" > /tmp/.eldritch_game_dir 2>/dev/null || true

echo "  ${GREEN}${BOLD}Installation complete.${RESET}"
echo ""
echo "  ${DIM}Project directory: $GAME_DIR${RESET}"
echo "  ${DIM}Type 'help' for available commands.${RESET}"
echo ""
