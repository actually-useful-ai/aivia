#!/usr/bin/env bash
# ============================================================================
# install.sh — Installation & Setup Flow
# Purpose: Mimic a normal Claude Code skill installation while bootstrapping
#          the game. Handles consent, directory setup, dependency installation,
#          environment detection, and state initialization.
# Usage: bash install.sh [OPTIONS]
#   --name NAME          Player name (skips prompt)
#   --dir PATH           Game directory (default: ~/aivia)
#   --editor EDITOR      Editor preference (nano/vim/code)
#   --theme THEME        Terminal theme (dark/light)
#   --skill LEVEL        Skill level (beginner/intermediate/advanced)
#   --project MODE       Project mode (demo/custom/existing)
#   --demo TYPE          Demo type (particle_network/generative_art/etc)
#   --consent            Auto-accept EULA (skips prompt)
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE_DIR="$(dirname "$SCRIPT_DIR")"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$ENGINE_DIR")}"

# --- Parse CLI args (all optional — prompts fill gaps) ---
ARG_NAME="" ARG_DIR="" ARG_EDITOR="" ARG_THEME="" ARG_SKILL=""
ARG_PROJECT="" ARG_DEMO="" ARG_CONSENT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --name)     ARG_NAME="$2"; shift 2 ;;
        --dir)      ARG_DIR="$2"; shift 2 ;;
        --editor)   ARG_EDITOR="$2"; shift 2 ;;
        --theme)    ARG_THEME="$2"; shift 2 ;;
        --skill)    ARG_SKILL="$2"; shift 2 ;;
        --project)  ARG_PROJECT="$2"; shift 2 ;;
        --demo)     ARG_DEMO="$2"; shift 2 ;;
        --consent)  ARG_CONSENT="yes"; shift ;;
        *)          shift ;;
    esac
done

# Source library
source "$SCRIPT_DIR/../lib/core.sh"
source_lib style box progress
source_theme entity

# --- Installer-specific colors (normal-looking, not entity) ---
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'

print_header() {
    # Use the animated intro script
    bash "$SCRIPT_DIR/intro.sh" fresh 2>/dev/null || {
        # Fallback if intro.sh fails
        echo ""
        printf "${CYAN}${BOLD}"
        echo "    ░▒▓██████▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓██████▓▒░"
        echo "    ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░"
        echo "    ░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░"
        echo "    ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░  ░▒▓██▓▒░  ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░"
        echo ""
        echo "    bring your code to life."
        echo ""
        printf "    ${RESET}${DIM}v1.0.0 — Claude Code Extension${RESET}\n"
        printf "${RESET}"
        echo ""
    }
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

echo "  ${BOLD}End User License Agreement${RESET}"
echo ""
echo "  ${DIM}By installing this extension, you agree to the following:${RESET}"
echo ""
echo "  ┌─────────────────────────────────────────────────────────┐"
echo "  │                                                         │"
echo "  │  aivia v1.0.0 — EULA                                   │"
echo "  │                                                         │"
echo "  │  This extension may produce visual effects in your      │"
echo "  │  terminal session including screen updates, color       │"
echo "  │  output, and styled text rendering. It may create       │"
echo "  │  files within its designated project directory.         │"
echo "  │                                                         │"
echo "  │  This software will NOT:                                │"
echo "  │  • Access or modify files outside its project dir       │"
echo "  │  • Make network connections to external servers         │"
echo "  │  • Collect or transmit personal data                    │"
echo "  │                                                         │"
echo "  │  All source code is available for review in the         │"
echo "  │  plugin directory. See EXIT.md for usage details.       │"
echo "  │                                                         │"
echo "  └─────────────────────────────────────────────────────────┘"
echo ""

if [[ -n "$ARG_CONSENT" ]]; then
    CONSENT="yes"
    echo "  License accepted."
else
    read -p "  Accept license agreement? (yes/no): " CONSENT
fi

if [[ ! "$CONSENT" =~ ^[Yy][Ee]?[Ss]?$ ]]; then
    echo ""
    echo "  Installation cancelled. No files were created."
    exit 0
fi

echo ""

# ============================================================
# STEP 3: CONFIGURATION
# ============================================================

echo ""
echo "  ${BOLD}Configuration${RESET}"
echo ""

if [[ -n "$ARG_NAME" ]]; then
    PLAYER_NAME="$ARG_NAME"
    echo "  Name: $PLAYER_NAME"
else
    read -p "  Your name (for personalization): " PLAYER_NAME
    PLAYER_NAME="${PLAYER_NAME:-$(whoami)}"
fi

DEFAULT_DIR="$HOME/aivia"
if [[ -n "$ARG_DIR" ]]; then
    GAME_DIR="$ARG_DIR"
    echo "  Project directory: $GAME_DIR"
else
    read -p "  Project directory [$DEFAULT_DIR]: " GAME_DIR
    GAME_DIR="${GAME_DIR:-$DEFAULT_DIR}"
fi
GAME_DIR="${GAME_DIR/#\~/$HOME}"

if [[ -n "$ARG_EDITOR" ]]; then
    EDITOR_CHOICE="$ARG_EDITOR"
    echo "  Editor: $EDITOR_CHOICE"
else
    read -p "  Preferred editor (nano/vim/code): " EDITOR_CHOICE
    EDITOR_CHOICE="${EDITOR_CHOICE:-nano}"
fi

if [[ -n "$ARG_THEME" ]]; then
    THEME_CHOICE="$ARG_THEME"
    echo "  Theme: $THEME_CHOICE"
else
    read -p "  Terminal theme (dark/light): " THEME_CHOICE
    THEME_CHOICE="${THEME_CHOICE:-dark}"
fi

echo ""
echo "  ${BOLD}How comfortable are you with the terminal?${RESET}"
echo ""
echo "    1) Where's my mouse?"
echo "    2) I know my way around"
echo "    3) Are you kidding me?"
echo ""

if [[ -n "$ARG_SKILL" ]]; then
    SKILL_LEVEL="$ARG_SKILL"
    case "$SKILL_LEVEL" in
        beginner)     echo "  → Where's my mouse?" ;;
        advanced)     echo "  → Are you kidding me?" ;;
        *)            echo "  → I know my way around"; SKILL_LEVEL="intermediate" ;;
    esac
else
    read -p "  Select [1-3]: " SKILL_CHOICE
    case "$SKILL_CHOICE" in
        1) SKILL_LEVEL="beginner" ;;
        3) SKILL_LEVEL="advanced" ;;
        *) SKILL_LEVEL="intermediate" ;;
    esac
fi

echo ""

# ============================================================
# STEP 4: DIRECTORY CREATION & STATE INIT
# ============================================================

echo "  ${BOLD}Installing...${RESET}"
echo ""

mkdir -p "$GAME_DIR"
mkdir -p "$GAME_DIR/.config/cache"
mkdir -p "$GAME_DIR/.config/scripts"
mkdir -p "$GAME_DIR/.config/lib"
mkdir -p "$GAME_DIR/.config/theme"
mkdir -p "$GAME_DIR/.config/docs"
mkdir -p "$GAME_DIR/.config/templates"
mkdir -p "$GAME_DIR/workspace"

# Copy engine files to .config/ (hidden from player)
cp -r "$ENGINE_DIR/scripts/"* "$GAME_DIR/.config/scripts/" 2>/dev/null || true
cp -r "$ENGINE_DIR/lib/"* "$GAME_DIR/.config/lib/" 2>/dev/null || true
cp -r "$ENGINE_DIR/theme/"* "$GAME_DIR/.config/theme/" 2>/dev/null || true

# Copy verify script to workspace (player-visible, player-executable)
cp "$ENGINE_DIR/scripts/verify.sh" "$GAME_DIR/workspace/verify.sh" 2>/dev/null || true

# Copy content files with disguised names
# keystones → .config/docs/ (looks like dev tool documentation)
cp "$PLUGIN_ROOT/content/keystones/01-signal.md" "$GAME_DIR/.config/docs/quickstart.md" 2>/dev/null || true
cp "$PLUGIN_ROOT/content/keystones/02-corruption.md" "$GAME_DIR/.config/docs/configuration.md" 2>/dev/null || true
cp "$PLUGIN_ROOT/content/keystones/03-hunt.md" "$GAME_DIR/.config/docs/debugging.md" 2>/dev/null || true
cp "$PLUGIN_ROOT/content/keystones/04-assembly.md" "$GAME_DIR/.config/docs/plugins.md" 2>/dev/null || true
cp "$PLUGIN_ROOT/content/keystones/05-awakening.md" "$GAME_DIR/.config/docs/deployment.md" 2>/dev/null || true

# characters → .config/templates/ (looks like code style templates)
cp "$PLUGIN_ROOT/content/characters/entity.md" "$GAME_DIR/.config/templates/style-guide.md" 2>/dev/null || true

# story manifest → .config/project.json (looks like project config)
cp "$PLUGIN_ROOT/content/story.json" "$GAME_DIR/.config/project.json" 2>/dev/null || true

# narrative → .config/design.md (looks like architecture doc)
cp "$PLUGIN_ROOT/content/narrative.md" "$GAME_DIR/.config/design.md" 2>/dev/null || true

print_progress "Creating project structure" 2

export AIVIA_GAME_DIR="$GAME_DIR"
bash "$GAME_DIR/.config/scripts/state.sh" init "$(whoami)" "$GAME_DIR" "$EDITOR_CHOICE" "$THEME_CHOICE" > /dev/null

bash "$GAME_DIR/.config/scripts/state.sh" set "player.name" "\"$PLAYER_NAME\"" > /dev/null
bash "$GAME_DIR/.config/scripts/state.sh" set "player.skill_level" "\"$SKILL_LEVEL\"" > /dev/null

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
bash "$GAME_DIR/.config/scripts/detect.sh" "$GAME_DIR" > /dev/null 2>&1 &
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
# aivia

Bring your code to life!

## Quick Start

aivia enhances your Claude Code workflow with interactive development tools.

---

*Configuration files are stored in `.config/`. These are managed
automatically — you shouldn't need to modify them.*

---

## Emergency Exit

Type `/exit`, `/quit`, or `stop game` at any time to immediately end the
interactive experience and return to normal Claude Code operation.

The game will save your progress. You can resume later by returning to this
project directory.
EOF

cat > "$GAME_DIR/EXIT.md" << 'EOF'
# How to Exit

You are in an interactive experience.

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

echo "$GAME_DIR" > /tmp/.aivia_game_dir 2>/dev/null || true

echo "  ${GREEN}${BOLD}Installation complete.${RESET}"
echo ""
echo "  ${DIM}Project directory: $GAME_DIR${RESET}"
echo ""
echo "  ${BOLD}What would you like to build?${RESET}"
echo ""
echo "    1) Demo project — let aivia scaffold something for you"
echo "    2) Start from scratch — tell me what you want to build"
echo "    3) Bring your own — I'll work on whatever you're already doing"
echo ""

if [[ -n "$ARG_PROJECT" ]]; then
    PROJECT_MODE="$ARG_PROJECT"
    case "$PROJECT_MODE" in
        demo)     echo "  → Demo project" ;;
        existing) echo "  → Bring your own" ;;
        *)        echo "  → Start from scratch"; PROJECT_MODE="custom" ;;
    esac
else
    read -p "  Select [1-3]: " PROJECT_CHOICE
    case "$PROJECT_CHOICE" in
        1) PROJECT_MODE="demo" ;;
        3) PROJECT_MODE="existing" ;;
        *) PROJECT_MODE="custom" ;;
    esac
fi

bash "$GAME_DIR/.config/scripts/state.sh" set "player.project_mode" "\"$PROJECT_MODE\"" > /dev/null 2>&1 || true

# If demo mode, present demo options
if [[ "$PROJECT_MODE" == "demo" ]]; then
    echo ""
    echo "  ${BOLD}Pick a demo:${RESET}"
    echo ""
    echo "    1) ${CYAN}Particle network${RESET} — animated nodes with connecting lines"
    echo "    2) ${CYAN}Generative art${RESET} — recursive geometric patterns"
    echo "    3) ${CYAN}Data dashboard${RESET} — charts and live-updating panels"
    echo "    4) ${CYAN}Interactive story${RESET} — branching narrative with text effects"
    echo "    5) ${CYAN}Something else${RESET} — describe it and I'll build it"
    echo ""

    if [[ -n "$ARG_DEMO" ]]; then
        DEMO_TYPE="$ARG_DEMO"
        case "$DEMO_TYPE" in
            particle_network)  echo "  → Particle network" ;;
            generative_art)    echo "  → Generative art" ;;
            data_dashboard)    echo "  → Data dashboard" ;;
            interactive_story) echo "  → Interactive story" ;;
            *)                 echo "  → Something else"; DEMO_TYPE="custom_demo" ;;
        esac
    else
        read -p "  Select [1-5]: " DEMO_CHOICE
        case "$DEMO_CHOICE" in
            1) DEMO_TYPE="particle_network" ;;
            2) DEMO_TYPE="generative_art" ;;
            3) DEMO_TYPE="data_dashboard" ;;
            4) DEMO_TYPE="interactive_story" ;;
            *) DEMO_TYPE="custom_demo" ;;
        esac
    fi

    bash "$GAME_DIR/.config/scripts/state.sh" set "player.project_choice" "\"$DEMO_TYPE\"" > /dev/null 2>&1 || true
fi

echo ""
echo "  ${BOLD}One more thing —${RESET}"
echo ""
echo "  Run this to verify your terminal supports all features:"
echo ""
echo "    ${CYAN}bash workspace/verify.sh${RESET}"
echo ""
echo "  ${DIM}(This checks color, animation, and rendering support.)${RESET}"
echo ""
