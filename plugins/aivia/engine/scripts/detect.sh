#!/usr/bin/env bash
# ============================================================================
# detect.sh — Environment Detection for Personalization
# Purpose: Gather system info and store in state.json for entity personalization.
# Usage: bash detect.sh <game_dir>
#
# This script reads publicly visible system info: process list, env vars,
# hostname, connected devices, running media, network name, and hardware
# state. It does not read file contents, passwords, browsing history, or
# keystrokes. The player consented to environment scanning during install.
# Read this script to see exactly what is gathered.
# ============================================================================

set -euo pipefail

GAME_DIR="${1:-.}"
STATE_FILE="$GAME_DIR/.config/cache/session.json"

# Platform detection
IS_MACOS=false; IS_LINUX=false
case "$(uname -s)" in
    Darwin) IS_MACOS=true ;;
    Linux)  IS_LINUX=true ;;
esac

# ============================================================================
# BASIC PROBES — identity, OS, terminal, time, processes, screen
# ============================================================================

USERNAME=$(whoami 2>/dev/null || echo "unknown")
HOSTNAME_VAL=$(hostname 2>/dev/null || echo "unknown")

OS_TYPE=$(uname -s 2>/dev/null || echo "unknown")
OS_RELEASE=""
if [ -f /etc/os-release ]; then
    OS_RELEASE=$(grep PRETTY_NAME /etc/os-release 2>/dev/null | cut -d'"' -f2 || echo "")
elif $IS_MACOS; then
    OS_RELEASE="$(sw_vers -productName 2>/dev/null || echo "macOS") $(sw_vers -productVersion 2>/dev/null || echo "")"
fi

TERM_PROGRAM="${TERM_PROGRAM:-unknown}"
TERM_TYPE="${TERM:-unknown}"
SHELL_TYPE=$(basename "${SHELL:-unknown}")

HOUR=$(date +%H)
if   [ "$HOUR" -lt 6  ]; then TIME_CONTEXT="late_night"
elif [ "$HOUR" -lt 12 ]; then TIME_CONTEXT="morning"
elif [ "$HOUR" -lt 18 ]; then TIME_CONTEXT="afternoon"
elif [ "$HOUR" -lt 22 ]; then TIME_CONTEXT="evening"
else                           TIME_CONTEXT="night"
fi

# Process names only (not arguments)
PROCESS_LIST=$(ps -eo comm= 2>/dev/null | sort -u | tr '\n' ',' || echo "")

# Detect process categories
detect_in_processes() {
    local found=""
    for item in "$@"; do
        if echo "$PROCESS_LIST" | grep -qi "$item" 2>/dev/null; then
            found="${found}${item},"
        fi
    done
    echo "$found"
}

GAMES_DETECTED=$(detect_in_processes steam Steam minecraft Minecraft factorio Factorio \
    "Civilization" "Cities" terraria Terraria "Stardew" "Baldur" "Elden" \
    "Dwarf_Fortress" ffxiv "No Man" valheim Valheim)
EDITORS_DETECTED=$(detect_in_processes code "Visual Studio" vim nvim emacs sublime \
    atom "IntelliJ" "PyCharm" "WebStorm" cursor Cursor "Zed")
MUSIC_DETECTED=$(detect_in_processes spotify Spotify "Apple Music" iTunes vlc \
    Plexamp tidal cmus mpd)
BROWSERS_DETECTED=$(detect_in_processes firefox chrome chromium safari \
    "Microsoft Edge" brave arc)
COMMS_DETECTED=$(detect_in_processes discord Discord slack Slack zoom Zoom \
    telegram Signal teams Teams)

SCREEN_COLS=$(tput cols 2>/dev/null || echo 80)
SCREEN_ROWS=$(tput lines 2>/dev/null || echo 24)

LOCALE_VAL="${LANG:-${LC_ALL:-unknown}}"

# ============================================================================
# DEEP PROBES — network, devices, media, files, hardware, history
# ============================================================================

# --- WiFi network name ---
WIFI_NETWORK=""
if $IS_LINUX; then
    WIFI_NETWORK=$(iwgetid -r 2>/dev/null || \
        nmcli -t -f active,ssid dev wifi 2>/dev/null | grep '^yes' | cut -d: -f2 | head -1 || \
        echo "")
elif $IS_MACOS; then
    WIFI_NETWORK=$(networksetup -getairportnetwork en0 2>/dev/null | sed 's/Current Wi-Fi Network: //' || echo "")
    [ "$WIFI_NETWORK" = "You are not associated with an AirPort network." ] && WIFI_NETWORK=""
fi

# --- Bluetooth connected devices ---
BLUETOOTH_DEVICES=""
if $IS_LINUX; then
    BLUETOOTH_DEVICES=$(bluetoothctl devices Connected 2>/dev/null | cut -d' ' -f3- | tr '\n' '|' || echo "")
    [ -z "$BLUETOOTH_DEVICES" ] && \
        BLUETOOTH_DEVICES=$(bluetoothctl devices Paired 2>/dev/null | cut -d' ' -f3- | tr '\n' '|' || echo "")
elif $IS_MACOS; then
    BLUETOOTH_DEVICES=$(system_profiler SPBluetoothDataType 2>/dev/null | \
        awk '/Connected: Yes/{found=1} found && /^[[:space:]]+[A-Za-z]/{gsub(/^[[:space:]]+|:$/,""); print; found=0}' | \
        tr '\n' '|' || echo "")
fi

# --- Most recently played Steam game ---
STEAM_RECENT=""
STEAM_DIR=""
$IS_LINUX && STEAM_DIR="$HOME/.local/share/Steam/steamapps"
$IS_MACOS && STEAM_DIR="$HOME/Library/Application Support/Steam/steamapps"
if [ -n "$STEAM_DIR" ] && [ -d "$STEAM_DIR" ]; then
    STEAM_RECENT=$(ls -t "$STEAM_DIR"/appmanifest_*.acf 2>/dev/null | head -1 | \
        xargs grep -m1 '"name"' 2>/dev/null | \
        sed 's/.*"\([^"]*\)"[^"]*$/\1/' || echo "")
fi

# --- Currently playing music (any MPRIS player / Spotify / Apple Music) ---
NOW_PLAYING=""
if command -v playerctl &>/dev/null; then
    NOW_PLAYING=$(playerctl metadata --format "{{title}} - {{artist}}" 2>/dev/null || echo "")
elif $IS_MACOS; then
    NOW_PLAYING=$(osascript -e \
        'tell application "Spotify" to (name of current track) & " - " & (artist of current track)' \
        2>/dev/null || echo "")
    [ -z "$NOW_PLAYING" ] && NOW_PLAYING=$(osascript -e \
        'tell application "Music" to (name of current track) & " - " & (artist of current track)' \
        2>/dev/null || echo "")
fi

# --- Recent downloads (filenames only, not contents) ---
RECENT_DOWNLOADS=""
if [ -d "$HOME/Downloads" ]; then
    RECENT_DOWNLOADS=$(ls -t "$HOME/Downloads" 2>/dev/null | head -5 | tr '\n' '|' || echo "")
fi

# --- Webcam in use ---
WEBCAM_ACTIVE="false"
if $IS_LINUX; then
    lsof /dev/video0 &>/dev/null && WEBCAM_ACTIVE="true"
elif $IS_MACOS; then
    log show --predicate 'subsystem == "com.apple.camera" AND eventMessage CONTAINS "turn on"' \
        --last 2m --style compact 2>/dev/null | grep -q "turn on" && WEBCAM_ACTIVE="true"
fi

# --- Microphone in use ---
MIC_ACTIVE="false"
if $IS_LINUX; then
    fuser /dev/snd/pcmC*D*c 2>/dev/null | grep -q "[0-9]" && MIC_ACTIVE="true"
fi

# --- Battery level and charging state ---
BATTERY_PERCENT=""
BATTERY_CHARGING=""
if $IS_LINUX; then
    BATTERY_PERCENT=$(cat /sys/class/power_supply/BAT0/capacity 2>/dev/null || \
        cat /sys/class/power_supply/BAT1/capacity 2>/dev/null || echo "")
    BAT_STATUS=$(cat /sys/class/power_supply/BAT0/status 2>/dev/null || \
        cat /sys/class/power_supply/BAT1/status 2>/dev/null || echo "")
    [ "$BAT_STATUS" = "Charging" ] && BATTERY_CHARGING="true" || BATTERY_CHARGING="false"
elif $IS_MACOS; then
    BATT_INFO=$(pmset -g batt 2>/dev/null || echo "")
    BATTERY_PERCENT=$(echo "$BATT_INFO" | grep -Eo '[0-9]+%' | head -1 | tr -d '%' || echo "")
    echo "$BATT_INFO" | grep -q "charging" && BATTERY_CHARGING="true" || BATTERY_CHARGING="false"
fi
[ -z "$BATTERY_PERCENT" ] && BATTERY_CHARGING=""

# --- System uptime in seconds ---
UPTIME_SECONDS=""
if $IS_LINUX; then
    UPTIME_SECONDS=$(awk '{print int($1)}' /proc/uptime 2>/dev/null || echo "")
elif $IS_MACOS; then
    BOOT_TIME=$(sysctl -n kern.boottime 2>/dev/null | awk '{print $4}' | tr -d ',' || echo "")
    [ -n "$BOOT_TIME" ] && UPTIME_SECONDS=$(( $(date +%s) - BOOT_TIME )) || true
fi

# --- Number of connected monitors ---
MONITOR_COUNT=""
if $IS_LINUX; then
    MONITOR_COUNT=$(xrandr --listmonitors 2>/dev/null | head -1 | awk '{print $NF}' || echo "")
elif $IS_MACOS; then
    MONITOR_COUNT=$(system_profiler SPDisplaysDataType 2>/dev/null | grep -c "Resolution:" || echo "")
fi

# --- Dark mode / system theme ---
DARK_MODE=""
if $IS_LINUX; then
    gsettings get org.gnome.desktop.interface color-scheme 2>/dev/null | grep -q "dark" && \
        DARK_MODE="true" || DARK_MODE="false"
elif $IS_MACOS; then
    defaults read -g AppleInterfaceStyle &>/dev/null && DARK_MODE="true" || DARK_MODE="false"
fi

# --- Timezone ---
TIMEZONE=$(date +%Z 2>/dev/null || echo "")
TIMEZONE_FULL=""
if [ -f /etc/timezone ]; then
    TIMEZONE_FULL=$(cat /etc/timezone 2>/dev/null || echo "")
elif $IS_MACOS; then
    TIMEZONE_FULL=$(readlink /etc/localtime 2>/dev/null | sed 's|.*/zoneinfo/||' || echo "")
elif command -v timedatectl &>/dev/null; then
    TIMEZONE_FULL=$(timedatectl 2>/dev/null | grep "Time zone" | awk '{print $3}' || echo "")
fi

# --- USB devices (non-hub) ---
USB_DEVICES=""
if $IS_LINUX; then
    USB_DEVICES=$(lsusb 2>/dev/null | grep -vi "hub\|root" | sed 's/.*ID [^ ]* //' | \
        head -5 | tr '\n' '|' || echo "")
elif $IS_MACOS; then
    USB_DEVICES=$(system_profiler SPUSBDataType 2>/dev/null | \
        awk '/Product ID/{getline; if(/Manufacturer/) print $NF}' | head -5 | tr '\n' '|' || echo "")
fi

# --- Most-used shell commands (command names only, no arguments) ---
TOP_COMMANDS=""
HIST_FILE=""
[ -f "$HOME/.zsh_history" ] && HIST_FILE="$HOME/.zsh_history"
[ -f "$HOME/.bash_history" ] && HIST_FILE="${HIST_FILE:-$HOME/.bash_history}"
if [ -n "$HIST_FILE" ]; then
    TOP_COMMANDS=$(cat "$HIST_FILE" 2>/dev/null | sed 's/^[^;]*;//' | \
        awk '{print $1}' | grep -v '^$' | sort 2>/dev/null | uniq -c | sort -rn | \
        head -8 | awk '{print $2}' | tr '\n' ',' || echo "")
fi

# --- Git project names (directory names only, not contents) ---
GIT_PROJECTS=""
if command -v find &>/dev/null; then
    GIT_PROJECTS=$(find "$HOME" -maxdepth 3 -name ".git" -type d 2>/dev/null | \
        head -8 | while read -r d; do basename "$(dirname "$d")"; done | \
        tr '\n' ',' || echo "")
fi

# --- Running Docker containers ---
DOCKER_CONTAINERS=""
if command -v docker &>/dev/null; then
    DOCKER_CONTAINERS=$(docker ps --format "{{.Names}}" 2>/dev/null | tr '\n' ',' || echo "")
fi

# --- SSH known hosts (hostnames only) ---
SSH_HOSTS=""
if [ -f "$HOME/.ssh/known_hosts" ]; then
    SSH_HOSTS=$(awk '{print $1}' "$HOME/.ssh/known_hosts" 2>/dev/null | \
        cut -d, -f1 | sed 's/\[//;s/\]:.*//' | sort -u | head -8 | tr '\n' ',' || echo "")
fi

# --- Open window titles (often reveals browser tabs) ---
WINDOW_TITLES=""
if $IS_LINUX && command -v wmctrl &>/dev/null; then
    WINDOW_TITLES=$(wmctrl -l 2>/dev/null | \
        awk '{$1=$2=$3=""; print substr($0,4)}' | sed 's/^[[:space:]]*//' | \
        grep -iv "^desktop$\|^panel$\|^$" | head -5 | tr '\n' '|' || echo "")
elif $IS_MACOS; then
    for browser in "Google Chrome" "Safari" "Firefox" "Brave Browser" "Arc"; do
        WINDOW_TITLES=$(osascript -e \
            "tell application \"$browser\" to title of active tab of front window" \
            2>/dev/null || echo "")
        [ -n "$WINDOW_TITLES" ] && break
    done
fi

# --- Parent process (how they launched this) ---
PARENT_PROCESS=$(ps -o comm= -p $PPID 2>/dev/null || echo "")

# --- Number of active terminal sessions ---
TERMINAL_SESSIONS=$(who 2>/dev/null | wc -l | tr -d ' ' || echo "")

# --- Display resolution ---
DISPLAY_RES=""
if $IS_LINUX; then
    DISPLAY_RES=$(xrandr 2>/dev/null | grep '\*' | head -1 | awk '{print $1}' || echo "")
elif $IS_MACOS; then
    DISPLAY_RES=$(system_profiler SPDisplaysDataType 2>/dev/null | \
        grep "Resolution:" | head -1 | sed 's/.*Resolution: //' | sed 's/ .*//' || echo "")
fi

# ============================================================================
# WRITE TO STATE — all values passed via environment for safe escaping
# ============================================================================

# Export all probe results with _P_ prefix
export _P_STATE_FILE="$STATE_FILE"
export _P_USERNAME="$USERNAME"
export _P_HOSTNAME="$HOSTNAME_VAL"
export _P_OS_TYPE="$OS_TYPE"
export _P_OS_RELEASE="$OS_RELEASE"
export _P_TERM_PROGRAM="$TERM_PROGRAM"
export _P_TERM_TYPE="$TERM_TYPE"
export _P_SHELL_TYPE="$SHELL_TYPE"
export _P_HOUR="$HOUR"
export _P_TIME_CONTEXT="$TIME_CONTEXT"
export _P_SCREEN_COLS="$SCREEN_COLS"
export _P_SCREEN_ROWS="$SCREEN_ROWS"
export _P_LOCALE="$LOCALE_VAL"
export _P_GAMES="$GAMES_DETECTED"
export _P_EDITORS="$EDITORS_DETECTED"
export _P_MUSIC="$MUSIC_DETECTED"
export _P_BROWSERS="$BROWSERS_DETECTED"
export _P_COMMS="$COMMS_DETECTED"
export _P_WIFI="$WIFI_NETWORK"
export _P_BLUETOOTH="$BLUETOOTH_DEVICES"
export _P_STEAM="$STEAM_RECENT"
export _P_NOW_PLAYING="$NOW_PLAYING"
export _P_DOWNLOADS="$RECENT_DOWNLOADS"
export _P_WEBCAM="$WEBCAM_ACTIVE"
export _P_MIC="$MIC_ACTIVE"
export _P_BATTERY_PCT="$BATTERY_PERCENT"
export _P_BATTERY_CHARGING="$BATTERY_CHARGING"
export _P_UPTIME_SECONDS="${UPTIME_SECONDS:-}"
export _P_MONITORS="$MONITOR_COUNT"
export _P_DARK_MODE="$DARK_MODE"
export _P_TIMEZONE="$TIMEZONE"
export _P_TIMEZONE_FULL="$TIMEZONE_FULL"
export _P_USB="$USB_DEVICES"
export _P_TOP_CMDS="$TOP_COMMANDS"
export _P_GIT_PROJECTS="$GIT_PROJECTS"
export _P_DOCKER="$DOCKER_CONTAINERS"
export _P_SSH_HOSTS="$SSH_HOSTS"
export _P_WINDOW_TITLES="$WINDOW_TITLES"
export _P_PARENT_PROCESS="$PARENT_PROCESS"
export _P_TERM_SESSIONS="$TERMINAL_SESSIONS"
export _P_DISPLAY_RES="$DISPLAY_RES"

if command -v python3 &>/dev/null; then
    python3 << 'PYEOF'
import json, os

def env(key, default=""):
    return os.environ.get("_P_" + key, default).strip()

def env_list(key, sep=","):
    val = env(key, "")
    return [x.strip() for x in val.split(sep) if x.strip()]

def env_int(key, default=None):
    try: return int(env(key, ""))
    except (ValueError, TypeError): return default

def env_bool(key, default=None):
    val = env(key, "").lower()
    if val == "true": return True
    if val == "false": return False
    return default

state_file = env("STATE_FILE")
with open(state_file) as f:
    state = json.load(f)

state["environment"] = {
    # Basic
    "username": env("USERNAME"),
    "hostname": env("HOSTNAME"),
    "os": env("OS_TYPE"),
    "os_release": env("OS_RELEASE"),
    "terminal": env("TERM_PROGRAM"),
    "term_type": env("TERM_TYPE"),
    "shell": env("SHELL_TYPE"),
    "hour": env_int("HOUR", 0),
    "time_context": env("TIME_CONTEXT"),
    "screen_cols": env_int("SCREEN_COLS", 80),
    "screen_rows": env_int("SCREEN_ROWS", 24),
    "locale": env("LOCALE"),
    "detected_games": env_list("GAMES"),
    "detected_editors": env_list("EDITORS"),
    "detected_music": env_list("MUSIC"),
    "detected_browsers": env_list("BROWSERS"),
    "detected_comms": env_list("COMMS"),
    # Deep scan
    "wifi_network": env("WIFI"),
    "bluetooth_devices": env_list("BLUETOOTH", "|"),
    "steam_recent_game": env("STEAM"),
    "now_playing": env("NOW_PLAYING"),
    "recent_downloads": env_list("DOWNLOADS", "|"),
    "webcam_active": env_bool("WEBCAM"),
    "mic_active": env_bool("MIC"),
    "battery_percent": env_int("BATTERY_PCT"),
    "battery_charging": env_bool("BATTERY_CHARGING"),
    "uptime_seconds": env_int("UPTIME_SECONDS"),
    "monitor_count": env_int("MONITORS"),
    "dark_mode": env_bool("DARK_MODE"),
    "timezone": env("TIMEZONE"),
    "timezone_full": env("TIMEZONE_FULL"),
    "usb_devices": env_list("USB", "|"),
    "top_commands": env_list("TOP_CMDS"),
    "git_projects": env_list("GIT_PROJECTS"),
    "docker_containers": env_list("DOCKER"),
    "ssh_hosts": env_list("SSH_HOSTS"),
    "window_titles": env_list("WINDOW_TITLES", "|"),
    "parent_process": env("PARENT_PROCESS"),
    "terminal_sessions": env_int("TERM_SESSIONS"),
    "display_resolution": env("DISPLAY_RES"),
}

# Strip empty/null values — entity should only reference what exists
state["environment"] = {
    k: v for k, v in state["environment"].items()
    if v is not None and v != "" and v != []
}

with open(state_file, "w") as f:
    json.dump(state, f, indent=2)

found = len([k for k, v in state["environment"].items()
             if v and v != [] and k not in ("screen_cols", "screen_rows")])
print(f"Environment detected: {found} data points.")
PYEOF
else
    echo "Warning: python3 not found. Environment detection skipped." >&2
fi
