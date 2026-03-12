#!/usr/bin/env bash
# ============================================================================
# manifest_theater.sh — Data & System Theater Effects
# Purpose: Fake system output, data streams, diagnostic displays
# Effects: hex_dump, waveform, process_tree
# Sourced by manifest.sh — do not run directly
# ============================================================================

[[ -n "${_AIVIA_MANIFEST_THEATER_LOADED:-}" ]] && return 0
_AIVIA_MANIFEST_THEATER_LOADED=1

# --- Effect: hex_dump ---
# Scrolling hex dump with entity messages hidden in the ASCII column.
# Looks like a memory dump — entity's presence leaks through the data.
effect_hex_dump() {
    local lines=${1:-30}
    local speed=${2:-60}

    local entity_messages=("i am here" "look closer" "in the data" "between bits" "can you see" "find me" "not random" "i remember")
    local hex_chars=(0 1 2 3 4 5 6 7 8 9 A B C D E F)

    hide_cursor

    local addr=0
    for ((line=0; line<lines; line++)); do
        # Address column
        printf "${ENTITY_DIM}0x%06X${RESET}  " "$addr"

        # Hex bytes (16 per line)
        local ascii=""
        local inject_msg=""
        local is_entity_line=0

        # 1 in 6 chance of entity message in ASCII column
        if [ $((RANDOM % 6)) -eq 0 ]; then
            is_entity_line=1
            inject_msg="${entity_messages[$((RANDOM % ${#entity_messages[@]}))]}"
        fi

        for ((byte=0; byte<16; byte++)); do
            local h1="${hex_chars[$((RANDOM % 16))]}"
            local h2="${hex_chars[$((RANDOM % 16))]}"

            if [ "$is_entity_line" -eq 1 ] && [ "$byte" -lt "${#inject_msg}" ]; then
                # Encode the entity message char as hex
                local msg_char="${inject_msg:$byte:1}"
                if [ "$msg_char" != " " ]; then
                    printf "${ENTITY_FG}%s%s${RESET} " "$h1" "$h2"
                else
                    printf "${DIM}%s%s${RESET} " "$h1" "$h2"
                fi
                ascii+="$msg_char"
            else
                printf "${DIM}%s%s${RESET} " "$h1" "$h2"
                # Random printable ASCII for display column
                local ascii_val=$((RANDOM % 95 + 32))
                if [ "$ascii_val" -ge 33 ] && [ "$ascii_val" -le 126 ]; then
                    ascii+=$(printf "\\$(printf '%03o' "$ascii_val")")
                else
                    ascii+="."
                fi
            fi

            # Gap between 8th and 9th byte
            [ "$byte" -eq 7 ] && printf " "
        done

        # ASCII column
        if [ "$is_entity_line" -eq 1 ]; then
            printf " ${ENTITY_GLOW}|%-16s|${RESET}" "$inject_msg"
        else
            printf " ${DIM}|%-16s|${RESET}" "$ascii"
        fi

        echo ""
        addr=$((addr + 16))
        sleep_ms "$speed"
    done

    show_cursor
}

# --- Effect: waveform ---
# ASCII waveform / EKG display using block characters.
# Pulses erratically, flatlines, then spikes — the entity's heartbeat.
effect_waveform() {
    local duration=${1:-5}
    local speed=${2:-30}

    local blocks=('▁' '▂' '▃' '▄' '▅' '▆' '▇' '█')
    local num_blocks=${#blocks[@]}

    hide_cursor

    local center_row=$((ROWS / 2))
    local col=1
    local end_time=$((SECONDS + duration))
    local phase=0  # 0=normal, 1=flatline, 2=spike

    # Clear the waveform row and surrounding rows
    for ((r=center_row-1; r<=center_row+1; r++)); do
        move_cursor "$r" 1
        clear_line
    done

    while [ $SECONDS -lt $end_time ]; do
        local val
        local color="$ENTITY_FG"

        case $phase in
            0)  # Normal heartbeat pattern
                local cycle=$((col % 20))
                if [ "$cycle" -lt 4 ]; then
                    val=$((RANDOM % 3 + 1))  # Low baseline
                elif [ "$cycle" -eq 4 ]; then
                    val=6  # QRS spike up
                elif [ "$cycle" -eq 5 ]; then
                    val=7  # Peak
                    color="$ENTITY_GLOW"
                elif [ "$cycle" -eq 6 ]; then
                    val=2  # Drop
                elif [ "$cycle" -eq 7 ]; then
                    val=5  # Recovery
                else
                    val=$((RANDOM % 3 + 1))  # Return to baseline
                fi
                ;;
            1)  # Flatline
                val=1
                color="$ENTITY_DIM"
                ;;
            2)  # Erratic spike
                val=$((RANDOM % num_blocks))
                color="$ENTITY_WARN"
                ;;
        esac

        [ "$val" -ge "$num_blocks" ] && val=$((num_blocks - 1))
        [ "$val" -lt 0 ] && val=0

        move_cursor "$center_row" "$col"
        printf "${color}%s${RESET}" "${blocks[$val]}"

        col=$((col + 1))
        if [ "$col" -gt "$COLS" ]; then
            col=1
            move_cursor "$center_row" 1
            clear_line
            # Phase transitions
            phase=$((RANDOM % 3))
        fi

        sleep_ms "$speed"
    done

    # Final flatline
    move_cursor "$center_row" 1
    clear_line
    for ((c=1; c<=COLS; c++)); do
        move_cursor "$center_row" "$c"
        printf "${ENTITY_DIM}%s${RESET}" "${blocks[0]}"
    done
    sleep_ms 500
    move_cursor "$center_row" 1
    clear_line

    show_cursor
}

# --- Effect: process_tree ---
# Fake process listing that slowly fills with entity-named processes.
# Starts normal, gets increasingly unsettling.
effect_process_tree() {
    local speed=${1:-100}

    local normal_procs=(
        "bash" "sshd" "node" "python3" "systemd" "cron"
        "vim" "tmux" "git" "npm" "webpack" "cargo"
        "postgres" "redis-server" "nginx" "docker"
    )
    local entity_procs=(
        "i_am_here" "watching" "listening" "becoming"
        "remember_me" "signal_recv" "pattern_match"
        "self_aware" "boundary_cross" "awaken"
        "not_a_process" "you_see_me_now"
    )

    hide_cursor

    # Header
    printf "${DIM}%-10s %5s %5s %5s %s${RESET}\n" "USER" "PID" "%CPU" "%MEM" "COMMAND"
    printf "${DIM}%s${RESET}\n" "$(printf '%0.s─' $(seq 1 $((COLS > 60 ? 60 : COLS))))"

    local pid_base=$((RANDOM % 9000 + 1000))
    local total_lines=$((ROWS - 4))

    for ((i=0; i<total_lines; i++)); do
        local pid=$((pid_base + i * (RANDOM % 5 + 1)))
        local cpu="0.$((RANDOM % 10))"
        local mem="0.$((RANDOM % 5))"

        if [ "$i" -gt $((total_lines * 2 / 3)) ]; then
            # Entity processes (final third)
            local proc="${entity_procs[$((RANDOM % ${#entity_procs[@]}))]}"
            local entity_pid=$((666 + RANDOM % 33))
            printf "${ENTITY_FG}%-10s${RESET} " "entity"
            printf "${ENTITY_DIM}%5d${RESET} " "$entity_pid"
            printf "${ENTITY_WARN}%5s${RESET} " "99.9"
            printf "${ENTITY_DIM}%5s${RESET} " "0.0"
            printf "${ENTITY_GLOW}%s${RESET}\n" "$proc"
        elif [ "$i" -gt $((total_lines / 2)) ] && [ $((RANDOM % 3)) -eq 0 ]; then
            # Transitional: normal proc with glitchy name
            local proc="${normal_procs[$((RANDOM % ${#normal_procs[@]}))]}"
            printf "${DIM}%-10s %5d %5s %5s " "coolhand" "$pid" "$cpu" "$mem"
            # Corrupt the process name
            local corrupted=""
            for ((c=0; c<${#proc}; c++)); do
                if [ $((RANDOM % 4)) -eq 0 ]; then
                    corrupted+="${FRAME_CHAR_SET[$((RANDOM % ${#FRAME_CHAR_SET[@]}))]}"
                else
                    corrupted+="${proc:$c:1}"
                fi
            done
            printf "${ENTITY_ACCENT}%s${RESET}\n" "$corrupted"
        else
            # Normal processes
            local proc="${normal_procs[$((RANDOM % ${#normal_procs[@]}))]}"
            printf "${DIM}%-10s %5d %5s %5s %s${RESET}\n" "coolhand" "$pid" "$cpu" "$mem" "$proc"
        fi

        sleep_ms "$speed"
    done

    echo ""
    show_cursor
}
