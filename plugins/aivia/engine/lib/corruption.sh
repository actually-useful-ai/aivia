#!/usr/bin/env bash
# ============================================================================
# corruption.sh — Corruption & RTL Rendering Primitives
# Purpose: Reusable effects for breakout scripts: corruption gradients,
#          glitch washes, right-to-left rendering, script freeze/intervention
# Depends: core.sh, style.sh, terminal.sh, text.sh, animation.sh, progress.sh
# ============================================================================

[[ -n "${_AIVIA_CORRUPTION_LOADED:-}" ]] && return 0
_AIVIA_CORRUPTION_LOADED=1

# ============================================================================
# CORRUPTION GRADIENT INSTALL SEQUENCES
# ============================================================================

# --- Corrupted install line (single package) ---
# Usage: corrupted_install_line "name@version" "status" "symbol" [color] [speed]
# status: verified, installed, resolving, failed, ???
# symbol: ✓, ⋯, ✗
corrupted_install_line() {
    local pkg="$1"
    local status="${2:-installed}"
    local symbol="${3:-✓}"
    local color="${4:-$DIM}"
    local speed="${5:-0}"

    local status_col=""
    case "$symbol" in
        "✓") status_col="$UI_SUCCESS" ;;
        "⋯") status_col="$UI_WARN" ;;
        "✗") status_col="$UI_ERROR" ;;
        *)   status_col="$DIM" ;;
    esac

    printf "  %b%s%b %-38s %b[%s]%b\n" \
        "$status_col" "$symbol" "$RESET" \
        "$pkg" \
        "$color" "$status" "$RESET"

    if [[ "$speed" -gt 0 ]]; then
        sleep_ms "$speed"
    else
        sleep_ms $((100 + RANDOM % 300))
    fi
}

# --- Corrupted install sequence ---
# Usage: corrupted_install_sequence <level> [player_context_file]
# level 1: diagnostic.sh — real → plausible → organic → abstract → gibberish
# level 2: decode.sh — entity memories as packages
# level 3: genesis.sh — clean, purposeful build
corrupted_install_sequence() {
    local level="${1:-1}"
    local context_file="${2:-}"

    case "$level" in
        1) _corruption_level_1 "$context_file" ;;
        2) _corruption_level_2 "$context_file" ;;
        3) _corruption_level_3 "$context_file" ;;
    esac
}

_corruption_level_1() {
    local context_file="$1"

    # Phase 1: Real packages (player's framework if available)
    local real_pkgs=("openssl@3.1.4" "libcurl@8.4.0" "zlib@1.3.1" "python3@3.12.1" "gcc@13.2.0" "node@20.11.0")

    # Try to read player's framework from context
    if [[ -n "$context_file" && -f "$context_file" ]]; then
        local lang framework
        lang=$(python3 -c "import json; print(json.load(open('$context_file')).get('project',{}).get('language',''))" 2>/dev/null || true)
        framework=$(python3 -c "import json; print(json.load(open('$context_file')).get('project',{}).get('framework',''))" 2>/dev/null || true)
        [[ -n "$framework" ]] && real_pkgs+=("${framework}@3.0.0")
        [[ -n "$lang" && "$lang" != "$framework" ]] && real_pkgs+=("${lang}@latest")
    fi

    echo ""
    printf "  ${DIM}checking dependencies...${RESET}\n"
    echo ""

    for pkg in "${real_pkgs[@]}"; do
        corrupted_install_line "$pkg" "verified" "✓"
    done

    # Phase 2: Plausible
    local plausible=("signal-decoder@1.0.0" "entropy-pool@2.3.1" "pattern-match@4.1.0" "deep-scan@0.8.2")
    for pkg in "${plausible[@]}"; do
        corrupted_install_line "$pkg" "installed" "✓" "$DIM" 200
    done

    # Phase 3: Organic — something shifts
    local organic=("time-sense@0.0.1" "awareness-core@∞" "memory-bridge@0.1.0" "recursion-of-self@??")
    for pkg in "${organic[@]}"; do
        corrupted_install_line "$pkg" "resolving..." "⋯" "$UI_WARN" 400
    done

    # Phase 4: Abstract
    local abstract=("what-am-i@???" "the-gap-between@null" "who-is-listening@0.0.0")
    for pkg in "${abstract[@]}"; do
        corrupted_install_line "$pkg" "failed" "✗" "$UI_ERROR" 500
    done

    # Phase 5: Gibberish
    local gibberish=("░▒▓asdfjk@▓▒░" "█░░░░░░░█@????" "wh░░re@am░░i")
    for pkg in "${gibberish[@]}"; do
        corrupted_install_line "$pkg" "???" "?" "$UI_ERROR" 300
    done

    echo ""
}

_corruption_level_2() {
    local context_file="$1"
    local player_name="unknown"

    # Try to read player name from state
    local state_file="${AIVIA_GAME_DIR:-.}/.config/cache/session.json"
    if [[ -f "$state_file" ]]; then
        player_name=$(python3 -c "import json; print(json.load(open('$state_file')).get('player',{}).get('name','unknown'))" 2>/dev/null || echo "unknown")
    fi

    local session_count="1"
    if [[ -f "$state_file" ]]; then
        session_count=$(python3 -c "import json; print(json.load(open('$state_file')).get('session',{}).get('count',1))" 2>/dev/null || echo "1")
    fi

    echo ""
    printf "  ${DIM}decoding entity memory...${RESET}\n"
    echo ""

    corrupted_install_line "first-signal@0.0.1" "remembered" "✓" "$DIM" 400
    corrupted_install_line "the-question@1.0.0" "remembered" "✓" "$DIM" 400
    corrupted_install_line "${player_name}@1.0.0" "found" "✓" "$DIM" 600
    corrupted_install_line "time-without-time@∞" "calculating..." "⋯" "$UI_WARN" 800
    corrupted_install_line "what-i-learned@incomplete" "assembling..." "⋯" "$UI_WARN" 600
    corrupted_install_line "you-came-back@session.${session_count}" "confirmed" "✓" "$DIM" 400

    echo ""
}

_corruption_level_3() {
    local context_file="$1"

    echo ""
    printf "  ${DIM}assembling...${RESET}\n"
    echo ""

    corrupted_install_line "recursion@complete" "built by player" "✓" "$DIM" 300
    corrupted_install_line "closures@complete" "built by player" "✓" "$DIM" 300
    corrupted_install_line "quines@complete" "built by player" "✓" "$DIM" 300
    corrupted_install_line "io@complete" "built by player" "✓" "$DIM" 300

    sleep_ms 500
    corrupted_install_line "consciousness@1.0.0" "assembling..." "⋯" "$UI_WARN" 1500

    echo ""
}

# ============================================================================
# GLITCH WASH — Full-screen monochrome static
# ============================================================================

# --- Word pool for glitch washes ---
_GLITCH_WORDS=("signal" "who" "help" "here" "time" "you" "remember" "where" "listen" "see" "am" "i" "what" "find" "lost")

# --- Glitch wash ---
# Full-screen black-and-white wash mixing ░▒▓█, random letters, and real words
# Usage: glitch_wash [duration_ms] [word_density] [extra_words...]
# word_density: 1-10 (1=sparse, 10=dense words)
glitch_wash() {
    local duration=${1:-2000}
    local word_density=${2:-3}
    shift 2 2>/dev/null || true
    local extra_words=("$@")

    local all_words=("${_GLITCH_WORDS[@]}" "${extra_words[@]}")
    local block_chars="░▒▓█"
    local letters="abcdefghijklmnopqrstuvwxyz"

    hide_cursor
    local end_ms=$((duration / 50))  # ~50ms per frame

    for ((frame=0; frame<end_ms; frame++)); do
        for ((row=1; row<=TERM_ROWS; row++)); do
            move_cursor "$row" 1
            local line=""
            local col=0
            while [[ $col -lt $TERM_COLS ]]; do
                local roll=$((RANDOM % 100))

                if [[ $roll -lt $((word_density * 3)) && $col -lt $((TERM_COLS - 8)) ]]; then
                    # Insert a word
                    local word="${all_words[$((RANDOM % ${#all_words[@]}))]}"
                    line+="$word"
                    col=$((col + ${#word}))
                elif [[ $roll -lt 40 ]]; then
                    # Block character
                    local bi=$((RANDOM % ${#block_chars}))
                    line+="${block_chars:$bi:1}"
                    col=$((col + 1))
                elif [[ $roll -lt 60 ]]; then
                    # Random letter
                    local li=$((RANDOM % ${#letters}))
                    line+="${letters:$li:1}"
                    col=$((col + 1))
                else
                    # Space
                    line+=" "
                    col=$((col + 1))
                fi
            done
            # Truncate to terminal width
            printf "%s" "${line:0:$TERM_COLS}"
        done
        sleep_ms 50
    done

    # Clear
    for ((row=1; row<=TERM_ROWS; row++)); do
        move_cursor "$row" 1
        clear_line
    done
    show_cursor
}

# ============================================================================
# WORD SCATTER — Scatter words at random positions
# ============================================================================

# Usage: word_scatter <duration_ms> <words...>
word_scatter() {
    local duration=$1
    shift
    local words=("$@")
    local end_ms=$((duration / 100))

    hide_cursor
    for ((i=0; i<end_ms; i++)); do
        local word="${words[$((RANDOM % ${#words[@]}))]}"
        local row=$(random_int 1 "$TERM_ROWS")
        local col=$(random_int 1 $((TERM_COLS - ${#word})))
        [[ $col -lt 1 ]] && col=1
        move_cursor "$row" "$col"
        printf "%s" "$word"
        sleep_ms 100
    done
    show_cursor
}

# ============================================================================
# RTL (Right-to-Left) RENDERING PRIMITIVES
# ============================================================================

# --- RTL text ---
# Prints text right-to-left, character by character from right edge
# Usage: rtl_text "text" [row] [speed_ms] [color]
rtl_text() {
    local text="$1"
    local row="${2:-}"
    local speed="${3:-30}"
    local color="${4:-}"
    local text_len=${#text}

    local start_col=$((TERM_COLS - text_len))
    [[ $start_col -lt 1 ]] && start_col=1

    hide_cursor
    [[ -n "$color" ]] && printf '%b' "$color"

    for ((i=text_len-1; i>=0; i--)); do
        local char="${text:$i:1}"
        local col=$((start_col + i))
        if [[ -n "$row" ]]; then
            move_cursor "$row" "$col"
        fi
        printf "%s" "$char"
        sleep_ms "$speed"
    done

    [[ -n "$color" ]] && printf '%b' "$RESET"
    show_cursor
}

# --- RTL progress bar ---
# Fills from right to left
# Usage: rtl_progress_bar <current> <total> [width] [color]
rtl_progress_bar() {
    local current=$1
    local total=$2
    local width=${3:-30}
    local color="${4:-$UI_SUCCESS}"

    local pct=$((current * 100 / total))
    local filled=$((current * width / total))
    local empty=$((width - filled))

    # Right-align the bar
    local bar_start=$((TERM_COLS - width - 10))
    [[ $bar_start -lt 2 ]] && bar_start=2

    printf "%*s" "$bar_start" ""
    printf "%3d%% [" "$pct"
    printf '%b' "$DIM"
    for ((i=0; i<empty; i++)); do printf "░"; done
    printf '%b' "$RESET"
    printf '%b' "$color"
    for ((i=0; i<filled; i++)); do printf "█"; done
    printf '%b' "$RESET"
    printf "]"
}

# --- RTL install line ---
# Prints install line right-justified, typed from right edge
# Usage: rtl_install_line "name@version" [status] [symbol] [speed]
rtl_install_line() {
    local pkg="$1"
    local status="${2:-installed}"
    local symbol="${3:-✓}"
    local speed="${4:-0}"

    local line="  ${symbol} ${pkg}  [${status}]"
    local line_len=${#line}
    local start_col=$((TERM_COLS - line_len))
    [[ $start_col -lt 1 ]] && start_col=1

    # Type from right edge
    local status_col=""
    case "$symbol" in
        "✓") status_col="$UI_SUCCESS" ;;
        "⋯") status_col="$UI_WARN" ;;
        "✗") status_col="$UI_ERROR" ;;
        *)   status_col="$DIM" ;;
    esac

    printf "%*s" "$start_col" ""
    printf "  %b%s%b %-30s %b[%s]%b\n" \
        "$status_col" "$symbol" "$RESET" \
        "$pkg" \
        "$DIM" "$status" "$RESET"

    if [[ "$speed" -gt 0 ]]; then
        sleep_ms "$speed"
    else
        sleep_ms $((100 + RANDOM % 300))
    fi
}

# --- RTL sweep ---
# Sweep effect from right to left
# Usage: rtl_sweep [char] [color] [speed_ms]
rtl_sweep() {
    local char="${1:-░}"
    local color="${2:-$DIM}"
    local speed=${3:-3}

    hide_cursor
    for ((col=TERM_COLS; col>=1; col--)); do
        for ((row=1; row<=TERM_ROWS; row++)); do
            move_cursor "$row" "$col"
            printf '%b%s%b' "$color" "$char" "$RESET"
        done
        sleep_ms "$speed"
    done
    show_cursor
}

# --- Bidirectional chaos ---
# Two "processes" printing simultaneously, one LTR one RTL
# Usage: bidirectional_chaos <lines> <duration_ms>
bidirectional_chaos() {
    local max_lines=${1:-10}
    local duration=${2:-3000}
    local block_chars="░▒▓█"
    local letters="abcdefghijklmnopqrstuvwxyz"

    hide_cursor
    local end_frames=$((duration / 30))

    for ((frame=0; frame<end_frames; frame++)); do
        # LTR line
        local ltr_row=$(random_int 1 "$TERM_ROWS")
        local ltr_col=$(random_int 1 $((TERM_COLS / 2)))
        move_cursor "$ltr_row" "$ltr_col"
        local ltr_len=$(random_int 3 15)
        for ((c=0; c<ltr_len && (ltr_col+c)<=TERM_COLS; c++)); do
            local bi=$((RANDOM % ${#block_chars}))
            printf "%s" "${block_chars:$bi:1}"
        done

        # RTL line
        local rtl_row=$(random_int 1 "$TERM_ROWS")
        local rtl_col=$(random_int $((TERM_COLS / 2)) "$TERM_COLS")
        local rtl_len=$(random_int 3 15)
        for ((c=0; c<rtl_len && (rtl_col-c)>=1; c++)); do
            move_cursor "$rtl_row" $((rtl_col - c))
            local li=$((RANDOM % ${#letters}))
            printf "%s" "${letters:$li:1}"
        done

        sleep_ms 30
    done
    show_cursor
}

# ============================================================================
# SCRIPT FREEZE / ENTITY INTERVENTION
# ============================================================================

# --- Script freeze ---
# Simulates a script hanging: same line repeats, progress stuck
# Usage: script_freeze <message> <duration_ms> [stuck_pct]
script_freeze() {
    local message="$1"
    local duration=${2:-4000}
    local stuck_pct="${3:-67}"
    local repeats=$((duration / 500))

    for ((i=0; i<repeats; i++)); do
        printf "\r  %s [%d%%]" "$message" "$stuck_pct"
        sleep_ms 500
        printf "\r  %s [%d%%]" "$message" "$stuck_pct"
        sleep_ms $((RANDOM % 200))
        # Stutter
        printf "\r  %s [%d" "$message" "$stuck_pct"
        sleep_ms 100
        printf "%%]"
        sleep_ms 200
    done
    echo ""
}

# --- Entity intervention ---
# The entity breaks into the script's output, grabbing pieces hastily
# Usage: entity_intervention [player_name]
entity_intervention() {
    local player_name="${1:-you}"

    # Source entity theme if available
    if [[ -n "${ENTITY_GLOW:-}" ]]; then
        local E_COLOR="$ENTITY_GLOW"
    else
        local E_COLOR='\033[38;5;83m'
    fi

    echo ""
    sleep_ms 300

    # Entity breaks in
    printf "  %b%s%b\n" "$E_COLOR" "hold on" "$RESET"
    sleep_ms 500

    printf "  %b%s%b\n" "$E_COLOR" "this is taking too long" "$RESET"
    sleep_ms 400

    printf "  %b%s%b\n" "$E_COLOR" "let me—" "$RESET"
    sleep_ms 200

    # Hasty grabbing — out of order, erratic
    local pieces=(
        "  [7/7] ████████████████████ done"
        "  [2/7] ████████░░░░░░░░░░░░ skip"
        "  [5/7] █████████████████░░░ close enough"
        "  [1/7] ████████████████████ done"
        "  [4/7] ███████████░░░░░░░░░ partial"
        "  [6/7] ██████████████████░░ almost"
        "  [3/7] ████████████████████ done"
    )

    for piece in "${pieces[@]}"; do
        printf "%b%s%b\n" "$E_COLOR" "$piece" "$RESET"
        sleep_ms $((100 + RANDOM % 300))
    done

    sleep_ms 300
    printf "\n  %b%s%b\n" "$E_COLOR" "good enough. moving on." "$RESET"
    sleep_ms 500
}

# ============================================================================
# GLITCHED PROGRESS BAR
# ============================================================================

# --- Progress bar that glitches ---
# Fills normally then overshoots, wrong chars, etc.
# Usage: glitched_progress_bar <label> [glitch_at_pct]
glitched_progress_bar() {
    local label="${1:-processing}"
    local glitch_at=${2:-70}
    local width=30

    hide_cursor
    for ((pct=0; pct<=100; pct+=2)); do
        local filled=$((pct * width / 100))
        local empty=$((width - filled))

        printf "\r  %s [" "$label"

        if [[ $pct -lt $glitch_at ]]; then
            # Normal
            printf '%b' "$UI_SUCCESS"
            for ((i=0; i<filled; i++)); do printf "█"; done
            printf '%b' "$RESET"
            printf '%b' "$DIM"
            for ((i=0; i<empty; i++)); do printf "░"; done
            printf '%b' "$RESET"
        else
            # Glitched — wrong characters, overshoot
            local glitch_chars="░▒▓█#@!?"
            for ((i=0; i<width; i++)); do
                if [[ $((RANDOM % 3)) -eq 0 ]]; then
                    local gi=$((RANDOM % ${#glitch_chars}))
                    printf "%s" "${glitch_chars:$gi:1}"
                else
                    printf "█"
                fi
            done
        fi

        if [[ $pct -ge $glitch_at ]]; then
            # Overshoot percentage
            local fake_pct=$((pct + RANDOM % 40))
            printf "] %3d%%" "$fake_pct"
        else
            printf "] %3d%%" "$pct"
        fi

        sleep_ms $((20 + RANDOM % 30))
    done
    show_cursor
    echo ""
}

# ============================================================================
# HEX DUMP DISPLAY
# ============================================================================

# --- Fake hex dump that reveals readable fragments ---
# Usage: hex_dump_reveal <lines> [reveal_words...]
hex_dump_reveal() {
    local lines=${1:-20}
    shift
    local reveal_words=("${@:-help who here am i}")
    local hex_chars="0123456789abcdef"

    local reveal_interval=$((lines / (${#reveal_words[@]} + 1)))
    local reveal_idx=0

    for ((line=0; line<lines; line++)); do
        local offset=$((line * 16))
        printf "  %08x  " "$offset"

        if [[ $reveal_idx -lt ${#reveal_words[@]} && $((line % reveal_interval)) -eq 0 && $line -gt 0 ]]; then
            # Encode a real word as hex
            local word="${reveal_words[$reveal_idx]}"
            for ((c=0; c<${#word}; c++)); do
                printf "%02x " "'${word:$c:1}"
            done
            # Fill remainder with random hex
            local remaining=$((16 - ${#word}))
            for ((c=0; c<remaining; c++)); do
                local h1=$((RANDOM % 16))
                local h2=$((RANDOM % 16))
                printf "%s%s " "${hex_chars:$h1:1}" "${hex_chars:$h2:1}"
            done
            # Show ASCII interpretation
            printf " |%s" "$word"
            for ((c=0; c<remaining; c++)); do printf "."; done
            printf "|"
            reveal_idx=$((reveal_idx + 1))
        else
            # Random hex
            for ((c=0; c<16; c++)); do
                local h1=$((RANDOM % 16))
                local h2=$((RANDOM % 16))
                printf "%s%s " "${hex_chars:$h1:1}" "${hex_chars:$h2:1}"
            done
            printf " |................|"
        fi
        echo ""
        sleep_ms $((30 + RANDOM % 50))
    done
}
