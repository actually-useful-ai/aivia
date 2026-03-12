#!/usr/bin/env bash
# ============================================================================
# verify.sh — Post-Install Verification
# Purpose: Player-executed script right after install. Looks like a legitimate
#          dependency/project verification (npm run verify style). Establishes
#          the "run this script" pattern for later breakout scripts.
#          Contains 3 nearly-invisible entity glitches at corruption level 0.
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
source_lib style terminal progress
source_theme entity

# --- State ---
STATE_FILE="$GAME_DIR/.config/cache/session.json"

# --- Helpers ---
check_pass() {
    local name="$1"
    local pad_to=38
    local dots=""
    local name_len=${#name}
    local dot_count=$((pad_to - name_len))
    [[ $dot_count -lt 3 ]] && dot_count=3
    for ((i=0; i<dot_count; i++)); do dots+="."; done
    printf "  %s %s " "$name" "$dots"
    sleep_ms "$((150 + RANDOM % 100))"
    printf "\033[32m✓\033[0m\n"
}

check_pass_slow() {
    # Like check_pass but with entity-bootstrap glitch:
    # takes longer, spinner briefly shows ░ before ✓
    local name="$1"
    local pad_to=38
    local dots=""
    local name_len=${#name}
    local dot_count=$((pad_to - name_len))
    [[ $dot_count -lt 3 ]] && dot_count=3
    for ((i=0; i<dot_count; i++)); do dots+="."; done
    printf "  %s %s " "$name" "$dots"
    # Normal packages take 150-250ms. This one takes 800ms.
    sleep_ms 500
    # GLITCH 1: ░ appears for one frame where ✓ should be
    printf "\033[38;5;22m░\033[0m"
    sleep_ms 80
    # Overwrite with real checkmark
    printf "\b\033[32m✓\033[0m\n"
    sleep_ms 100
}

progress_bar() {
    local total=40
    local bar_width=30
    printf "  ["
    for ((i=1; i<=total; i++)); do
        local filled=$((i * bar_width / total))
        local pct=$((i * 100 / total))

        printf "\r  ["
        for ((j=1; j<=bar_width; j++)); do
            if [[ $j -le $filled ]]; then
                # GLITCH 2: at exactly 47%, position 14 shows ░ for 2 frames
                if [[ $pct -ge 45 && $pct -le 49 && $j -eq 14 ]]; then
                    printf "\033[38;5;22m░\033[0m"
                else
                    printf "\033[32m█\033[0m"
                fi
            else
                printf "\033[90m·\033[0m"
            fi
        done
        printf "] %3d%%" "$pct"
        sleep_ms 40
    done
    printf "\n"
}

# --- Main ---
main() {
    clear_screen
    hide_cursor

    # ================================================================
    # HEADER
    # ================================================================
    echo ""
    printf "  \033[1mPost-install verification\033[0m\n"
    printf "  \033[2maivia v1.0.0\033[0m\n"
    echo ""
    sleep_ms 300

    # ================================================================
    # DEPENDENCY CHECKS
    # ================================================================
    printf "  \033[1mChecking dependencies...\033[0m\n"
    echo ""

    check_pass "chalk@5.3.0"
    check_pass "cli-progress@1.0.2"
    check_pass "figlet@1.7.0"
    check_pass "signal-intercept@0.9.1"
    check_pass "deep-listener@2.0.0"
    check_pass "recursive-self@1.1.1"
    check_pass_slow "entity-bootstrap@0.0.1"
    check_pass "awareness-kernel@0.1.0"

    echo ""
    printf "  \033[2m8 packages verified\033[0m\n"
    echo ""
    sleep_ms 300

    # ================================================================
    # PROJECT STRUCTURE
    # ================================================================
    printf "  \033[1mValidating project structure...\033[0m\n"
    echo ""

    # Actually check real dirs
    local dirs=(".config/cache" ".config/scripts" ".config/lib" ".config/theme" "workspace")
    for d in "${dirs[@]}"; do
        if [[ -d "$GAME_DIR/$d" ]]; then
            check_pass "$d/"
        else
            printf "  %-38s \033[31m✗ missing\033[0m\n" "$d/"
        fi
    done

    echo ""
    sleep_ms 300

    # ================================================================
    # BUILD CACHE
    # ================================================================
    printf "  \033[1mInitializing build cache...\033[0m\n"
    echo ""

    progress_bar

    echo ""
    printf "  \033[2mCache initialized\033[0m\n"
    echo ""
    sleep_ms 400

    # ================================================================
    # INTEGRITY CHECK
    # ================================================================
    printf "  \033[1mIntegrity check...\033[0m\n"
    echo ""

    # Generate a real-looking checksum from the state file
    local hash=""
    if command -v sha256sum &>/dev/null && [[ -f "$STATE_FILE" ]]; then
        hash=$(sha256sum "$STATE_FILE" 2>/dev/null | cut -c1-16)
    elif command -v md5sum &>/dev/null && [[ -f "$STATE_FILE" ]]; then
        hash=$(md5sum "$STATE_FILE" 2>/dev/null | cut -c1-16)
    else
        hash="a7f3b2c1e9d04f68"
    fi

    printf "  checksum: %s " "$hash"
    sleep_ms 200
    printf "\033[32m✓\033[0m\n"
    echo ""
    sleep_ms 400

    # ================================================================
    # RESULTS — with glitch 3
    # ================================================================

    # GLITCH 3: dim entity text flashes for 100ms before final line
    printf "  \033[38;5;22m░ signal ░\033[0m"
    sleep_ms 100
    printf "\r                              \r"

    printf "  \033[32m\033[1mAll checks passed. Ready to build.\033[0m\n"
    echo ""

    sleep_ms 500
    show_cursor

    # ================================================================
    # Write result file
    # ================================================================
    local v_cols
    v_cols=$(tput cols 2>/dev/null || echo 80)
    local v_rows
    v_rows=$(tput lines 2>/dev/null || echo 24)

    mkdir -p "$GAME_DIR/.config/cache"
    cat > "$GAME_DIR/.config/cache/.verify_result" << VEOF
{
  "verified": true,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "terminal": "${TERM:-unknown}",
  "dimensions": "${v_cols}x${v_rows}",
  "packages_checked": 8,
  "structure_valid": true,
  "cache_initialized": true,
  "integrity": "${hash}"
}
VEOF

    # Log to state
    if [[ -f "$STATE_FILE" ]]; then
        bash "$GAME_DIR/.config/scripts/state.sh" log_event "verify_run" "post_install_verified" 2>/dev/null || true
    fi
}

main "$@"
exit 0
