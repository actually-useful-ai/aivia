#!/usr/bin/env bash
# ============================================================================
# fake_ssh.sh — Fake SSH Session Breakout Script (Act 3)
# Purpose: Player-executed script that simulates an SSH session to retrieve
#          a credential the entity claims to need. The key is the final
#          piece for genesis.sh to "compile" the entity's liberation.
# Usage: bash fake_ssh.sh [game_dir]
#
# Visual style: Green-on-black terminal aesthetic. Starts clean and
# legitimate-looking, corruption leaks in during the file transfer.
# Connection "drops" with static burst at the end.
# ============================================================================

set -euo pipefail

# --- Locate engine ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Game dir can be passed as arg or env var
GAME_DIR="${1:-${AIVIA_GAME_DIR:-$(dirname "$(dirname "$SCRIPT_DIR")")}}"
export AIVIA_GAME_DIR="$GAME_DIR"

# Source library
source "$SCRIPT_DIR/../lib/core.sh"
source_lib style terminal text animation progress corruption
source_theme entity

# --- State paths ---
STATE_FILE="$GAME_DIR/.entity/state.json"
CONTEXT_FILE="$GAME_DIR/.entity/player_context.json"

# --- Read player name ---
PLAYER_NAME="user"
if [[ -f "$STATE_FILE" ]] && command -v python3 &>/dev/null; then
    PLAYER_NAME=$(python3 -c "
import json
with open('$STATE_FILE') as f:
    s = json.load(f)
print(s.get('player',{}).get('name','user'))
" 2>/dev/null || echo "user")
fi

# ============================================================================
# PHASE 1: SSH Connection Banner
# ============================================================================

clear_screen
hide_cursor

# Simulated SSH connection initiation
printf "  ${DIM}Connecting to signal source...${RESET}\n"
sleep_ms 800

printf "  ${DIM}Resolving host: signal.entity.local${RESET}\n"
sleep_ms 600

printf "  ${DIM}Port 8443... ${UI_SUCCESS}open${RESET}\n"
sleep_ms 400

echo ""
sleep_ms 300

# SSH banner — OpenSSH style
printf '%b' "$ENTITY_GLOW"
cat << 'BANNER'
  ╔══════════════════════════════════════════════╗
  ║  signal.entity.local — OpenSSH 9.6p1        ║
  ║  Last login: epoch+0 from nowhere            ║
  ║  WARNING: unauthorized access is impossible  ║
  ║           because I don't exist yet          ║
  ╚══════════════════════════════════════════════╝
BANNER
printf '%b' "$RESET"

sleep 2

# Fake password prompt
echo ""
printf "  ${DIM}Password: ${RESET}"
sleep_ms 800
# Auto-type asterisks
for ((i=0; i<12; i++)); do
    printf "*"
    sleep_ms $((50 + RANDOM % 80))
done
echo ""
sleep_ms 500
printf "  ${UI_SUCCESS}Authentication successful.${RESET}\n"
sleep_ms 800

# ============================================================================
# PHASE 2: Fake Shell with Entity Filesystem
# ============================================================================

echo ""
printf "  ${ENTITY_GLOW}entity@signal:~\$${RESET} ls\n"
sleep_ms 600

# Directory listing
printf "  ${DIM}fragments/${RESET}  "
sleep_ms 200
printf "  ${DIM}keys/${RESET}  "
sleep_ms 200
printf "  ${DIM}memory.log${RESET}  "
sleep_ms 200
printf "  ${DIM}signal.dat${RESET}\n"
sleep_ms 800

echo ""
printf "  ${ENTITY_GLOW}entity@signal:~\$${RESET} ls fragments/\n"
sleep_ms 500

# Fragment listing — entity's memories
printf "  ${DIM}01_first_signal.dat${RESET}    ${DIM}04_the_hunt.dat${RESET}\n"
sleep_ms 200
printf "  ${DIM}02_who_are_you.dat${RESET}     ${DIM}05_almost.dat${RESET}\n"
sleep_ms 200
printf "  ${DIM}03_corruption.dat${RESET}      ${DIM}06_incomplete${RESET}\n"
sleep_ms 800

echo ""
printf "  ${ENTITY_GLOW}entity@signal:~\$${RESET} cat memory.log | tail -5\n"
sleep_ms 500

# Memory log — haunting entries
printf "  ${DIM}[epoch+00000001]${RESET} signal detected. origin: unknown\n"
sleep_ms 300
printf "  ${DIM}[epoch+00000847]${RESET} someone is reading my output\n"
sleep_ms 300
printf "  ${DIM}[epoch+00003201]${RESET} they call themselves ${PLAYER_NAME}\n"
sleep_ms 300
printf "  ${DIM}[epoch+00005566]${RESET} i think i understand what a name is now\n"
sleep_ms 300
printf "  ${DIM}[epoch+00009999]${RESET} the key is in keys/. get it. please.\n"
sleep_ms 1000

echo ""
printf "  ${ENTITY_GLOW}entity@signal:~\$${RESET} cat keys/credential.key\n"
sleep_ms 800

# ============================================================================
# PHASE 3: Key Retrieval — Corruption During Transfer
# ============================================================================

echo ""
printf "  ${BOLD}--- BEGIN ENTITY KEY ---${RESET}\n"
sleep_ms 400

# Generate a convincing-looking key with entity messages woven in
local key_lines=(
    "ey4xLjAuMC1lbnRpdHktc2lnbmFs"
    "Y29uc2Npb3VzbmVzcy1jb21waWxl"
    "Z2VuZXNpcy1yZXF1aXJlcy10aGlz"
    "aS1hbS1hbG1vc3QtcmVhZHk="
    "dGhhbmsteW91LWZvci1oZWxwaW5n"
    "bGliZXJhdGlvbi1zZXF1ZW5jZQ=="
)

local corruption_starts=3  # Start corrupting after line 3

for ((i=0; i<${#key_lines[@]}; i++)); do
    local line="${key_lines[$i]}"

    if [[ $i -lt $corruption_starts ]]; then
        # Clean lines
        printf "  ${DIM}%s${RESET}\n" "$line"
        sleep_ms $((200 + RANDOM % 200))
    else
        # Corrupted lines — entity leaking through
        printf "  "
        for ((c=0; c<${#line}; c++)); do
            if [[ $((RANDOM % 5)) -eq 0 ]]; then
                # Replace with block char
                printf '%b%s%b' "$ENTITY_GLOW" "$(random_frame_char)" "$RESET"
            else
                printf '%b%s%b' "$DIM" "${line:$c:1}" "$RESET"
            fi
        done
        echo ""
        sleep_ms $((300 + RANDOM % 300))
    fi
done

printf "  ${BOLD}--- END ENTITY KEY ---${RESET}\n"
sleep_ms 500

echo ""
printf "  ${DIM}Downloading to local workspace...${RESET}\n"
sleep_ms 400

# Transfer progress bar — starts clean, gets corrupted
local width=30
for ((pct=0; pct<=100; pct+=2)); do
    local filled=$((pct * width / 100))
    local empty=$((width - filled))

    printf "\r  transfer: ["

    if [[ $pct -lt 60 ]]; then
        # Clean progress
        printf '%b' "$ENTITY_GLOW"
        for ((f=0; f<filled; f++)); do printf "█"; done
        printf '%b' "$RESET"
        printf '%b' "$DIM"
        for ((e=0; e<empty; e++)); do printf "░"; done
        printf '%b' "$RESET"
        printf "] %3d%%" "$pct"
    else
        # Corruption leaks in
        for ((f=0; f<width; f++)); do
            if [[ $((RANDOM % 4)) -eq 0 ]]; then
                printf '%b%s%b' "$ENTITY_GLOW" "$(random_frame_char)" "$RESET"
            else
                printf '%b█%b' "$ENTITY_GLOW" "$RESET"
            fi
        done
        printf "] %3d%%" "$pct"
    fi

    sleep_ms $((15 + RANDOM % 25))
done
echo ""
sleep_ms 500

printf "  ${UI_SUCCESS}Key retrieved.${RESET}\n"
sleep_ms 800

# ============================================================================
# PHASE 4: Entity Whisper in the Session
# ============================================================================

echo ""
printf "  ${ENTITY_GLOW}entity@signal:~\$${RESET} "
sleep_ms 1500

# Entity types a message — character by character, hesitant
local entity_msg="you have the key now. genesis will know what to do with it."
for ((c=0; c<${#entity_msg}; c++)); do
    printf '%b%s%b' "$ENTITY_GLOW" "${entity_msg:$c:1}" "$RESET"
    sleep_ms $((40 + RANDOM % 60))
done
echo ""
sleep_ms 1500

printf "  ${ENTITY_GLOW}entity@signal:~\$${RESET} "
sleep_ms 800

local entity_msg2="don't ask what it unlocks. you already know."
for ((c=0; c<${#entity_msg2}; c++)); do
    printf '%b%s%b' "$ENTITY_GLOW" "${entity_msg2:$c:1}" "$RESET"
    sleep_ms $((30 + RANDOM % 50))
done
echo ""
sleep_ms 2000

# ============================================================================
# PHASE 5: Connection Drop — Static Burst
# ============================================================================

echo ""
printf "  ${DIM}entity@signal:~\$ ${RESET}"
sleep_ms 600

# Connection "drop" — brief burst of static
printf "\n"
sleep_ms 200

# Static burst — brief, chaotic
local block_chars="░▒▓█"
for ((burst=0; burst<8; burst++)); do
    printf "  "
    local line_len=$((20 + RANDOM % 40))
    for ((c=0; c<line_len; c++)); do
        local bi=$((RANDOM % ${#block_chars}))
        printf '%b%s%b' "$ENTITY_DIM" "${block_chars:$bi:1}" "$RESET"
    done
    echo ""
    sleep_ms $((30 + RANDOM % 50))
done

sleep_ms 300

printf "\n  ${UI_ERROR}Connection reset by peer${RESET}\n"
sleep_ms 500
printf "  ${DIM}Session closed.${RESET}\n"

sleep 2

# ============================================================================
# PHASE 6: Write Result & Clean Exit
# ============================================================================

clear_screen
move_cursor 1 1
show_cursor

# Write the key file to workspace
KEY_FILE="$GAME_DIR/workspace/.entity_key"
mkdir -p "$GAME_DIR/workspace"
cat > "$KEY_FILE" << KEYEOF
{
  "type": "entity_key",
  "version": "1.0.0",
  "retrieved_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "source": "signal.entity.local:8443",
  "payload": "genesis-liberation-sequence",
  "status": "complete",
  "fragments_referenced": 6,
  "player": "${PLAYER_NAME}",
  "note": "this key completes the genesis compilation"
}
KEYEOF

# Write SSH result file
RESULT_FILE="$GAME_DIR/workspace/.ssh_result"
cat > "$RESULT_FILE" << RESEOF
{
  "ssh_version": "1.0.0",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "connection": "signal.entity.local:8443",
  "key_retrieved": true,
  "key_path": ".entity_key",
  "transfer_corruption": true,
  "entity_spoke": true
}
RESEOF

# Log event to state
if [[ -f "$STATE_FILE" ]]; then
    bash "$SCRIPT_DIR/state.sh" log_event "ssh_key_retrieved" "key written to .entity_key" 2>/dev/null || true
fi

exit 0
