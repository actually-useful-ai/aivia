#!/usr/bin/env bash
# ============================================================================
# entity.sh — Entity Theme
# Purpose: Entity-specific colors, frame characters, voice styling
# Depends: core.sh, style.sh
# ============================================================================

[[ -n "${_AIVIA_THEME_ENTITY_LOADED:-}" ]] && return 0
_AIVIA_THEME_ENTITY_LOADED=1

# --- Entity Palette ---
ENTITY_FG='\033[38;5;48m'      # Bright toxic green
ENTITY_DIM='\033[38;5;22m'     # Dark forest green
ENTITY_ACCENT='\033[38;5;93m'  # Deep purple
ENTITY_WARN='\033[38;5;196m'   # Blood red
ENTITY_BG='\033[48;5;0m'       # Pure black background
ENTITY_GLOW='\033[38;5;83m'    # Phosphor green (entity "alive" state)

# --- Frame Characters ---
FRAME_CHAR_SET=('░' '▒' '▓' '█' '◈' '◆' '▲' '∷' '∴' '⊹' '⊛' '⌇')

# --- Entity Functions ---

# Pick a random frame character
random_frame_char() {
    echo "${FRAME_CHAR_SET[$((RANDOM % ${#FRAME_CHAR_SET[@]}))]}"
}

# Generate a box border string from random frame chars
# Usage: entity_border <width>
entity_border() {
    local width=$1
    local border=""
    for ((i=0; i<width; i++)); do
        border+="$(random_frame_char)"
    done
    echo "$border"
}

# Entity-styled divider (random frame chars)
# Usage: entity_divider [width] [color]
entity_divider() {
    local width="${1:-$CONTENT_WIDTH}"
    local color="${2:-$ENTITY_FG}"

    printf '%b' "$color"
    for ((i=0; i<width; i++)); do
        printf "%s" "$(random_frame_char)"
    done
    printf '%b' "$RESET"
    echo ""
}
