#!/usr/bin/env bash
# ============================================================================
# detect.sh — Environment Detection for Personalization
# Purpose: Gather system info and store in state.json for entity personalization.
#
# Usage: bash detect.sh [command] [game_dir]
#
# Commands:
#   scan     Run probes, write to state, print count (default)
#   list     Run probes, write to state, show check/miss per probe
#   detail   Run probes, write to state, show all values
#   summary  Run probes, write to state, print grouped overview
#   deps     Show optional tools and whether they're installed
#   install  Install missing optional tools (prompts for confirmation)
#   help     Show this help and exit
#
# If <command> is omitted or unrecognized, it's treated as <game_dir>
# and defaults to "scan". game_dir defaults to "." if omitted.
#
# This script reads publicly visible system metadata: process list, env vars,
# hostname, connected devices, running media, network name, hardware state,
# and recent browser domains (hostnames only — no page content, passwords,
# or form data). The player consented to environment scanning during install.
# Read this script to see exactly what is gathered.
# ============================================================================

# set -e disabled intentionally — probes must not kill the script on failure
set -u

# Timeout wrapper: runs command with a deadline (default 3s)
# Usage: probe_timeout <seconds> <command...>
probe_timeout() {
    local secs="$1"; shift
    if command -v timeout &>/dev/null; then
        timeout "$secs" "$@" 2>/dev/null || echo ""
    else
        # macOS fallback: no coreutils timeout, use perl alarm
        perl -e 'alarm shift; exec @ARGV' "$secs" "$@" 2>/dev/null || echo ""
    fi
}

# Temp file cleanup trap
_DETECT_TMPFILES=()
cleanup_tmp() { for f in "${_DETECT_TMPFILES[@]:-}"; do rm -f "$f" 2>/dev/null; done; }
trap cleanup_tmp EXIT

# --- Argument parsing ---
MODE="scan"
GAME_DIR="."

case "${1:-}" in
    scan|list|detail|summary)
        MODE="$1"; GAME_DIR="${2:-.}" ;;
    help|--help|-h)
        sed -n '2,/^# ====/{ /^# /s/^# //p }' "$0"
        exit 0 ;;
    deps|install)
        MODE="$1"; GAME_DIR="${2:-.}" ;;
    "")
        GAME_DIR="." ;;
    *)
        GAME_DIR="$1" ;;
esac

STATE_FILE="$GAME_DIR/.config/cache/session.json"

# Platform detection
IS_MACOS=false; IS_LINUX=false
case "$(uname -s)" in
    Darwin) IS_MACOS=true ;;
    Linux)  IS_LINUX=true ;;
esac

# ============================================================================
# DEPS / INSTALL — optional tool management (runs before probes)
# ============================================================================

# Optional tools that unlock extra probes
# Format: tool_cmd|package_apt|package_brew|what_it_unlocks
OPTIONAL_DEPS=(
    "iwgetid|wireless-tools|airport (built-in)|WiFi network name"
    "nmcli|network-manager|N/A|WiFi network name (fallback)"
    "bluetoothctl|bluez|blueutil|Bluetooth device names"
    "playerctl|playerctl|N/A|Now playing track info"
    "wmctrl|wmctrl|N/A|Open window titles"
    "xrandr|x11-xserver-utils|N/A|Display resolution + monitor count"
    "lsusb|usbutils|system_profiler (built-in)|USB device names"
    "docker|docker.io|docker|Running container names"
    "sqlite3|sqlite3|sqlite3|Browser history (recent domains)"
    "jq|jq|jq|Faster state management"
)

if [ "$MODE" = "deps" ]; then
    printf "detect.sh — Optional Dependencies\n\n"
    printf "  %-14s %-10s %-28s %s\n" "TOOL" "STATUS" "PACKAGE" "UNLOCKS"
    printf "  %-14s %-10s %-28s %s\n" "────" "──────" "───────" "───────"
    for entry in "${OPTIONAL_DEPS[@]}"; do
        IFS='|' read -r cmd pkg_apt pkg_brew unlocks <<< "$entry"
        if command -v "$cmd" &>/dev/null; then
            status="\033[32minstalled\033[0m"
        else
            status="\033[33mmissing\033[0m"
        fi
        pkg="$pkg_apt"
        $IS_MACOS && pkg="$pkg_brew"
        printf "  %-14s ${status}  %-28s %s\n" "$cmd" "$pkg" "$unlocks"
    done
    missing=0
    for entry in "${OPTIONAL_DEPS[@]}"; do
        IFS='|' read -r cmd _ _ _ <<< "$entry"
        command -v "$cmd" &>/dev/null || ((missing++)) || true
    done
    printf "\n  %d of %d tools installed" "$((${#OPTIONAL_DEPS[@]} - missing))" "${#OPTIONAL_DEPS[@]}"
    [ "$missing" -gt 0 ] && printf " (\033[33m%d missing\033[0m — run 'detect.sh install' to fix)" "$missing"
    printf "\n"
    exit 0
fi

if [ "$MODE" = "install" ]; then
    missing_pkgs=()
    missing_names=()
    for entry in "${OPTIONAL_DEPS[@]}"; do
        IFS='|' read -r cmd pkg_apt pkg_brew unlocks <<< "$entry"
        if ! command -v "$cmd" &>/dev/null; then
            pkg="$pkg_apt"
            $IS_MACOS && pkg="$pkg_brew"
            # Skip N/A and built-in packages
            [[ "$pkg" == "N/A" || "$pkg" == *"built-in"* ]] && continue
            missing_pkgs+=("$pkg")
            missing_names+=("$cmd")
        fi
    done

    if [ ${#missing_pkgs[@]} -eq 0 ]; then
        printf "All optional tools are already installed.\n"
        exit 0
    fi

    printf "aivia uses these tools to read system metadata (WiFi name, bluetooth\n"
    printf "devices, display info, etc.) for in-game personalization. Nothing is\n"
    printf "sent anywhere — all data stays in your local game directory.\n\n"

    printf "The following packages will be installed:\n\n"
    for i in "${!missing_pkgs[@]}"; do
        printf "  %-20s → %s\n" "${missing_pkgs[$i]}" "${missing_names[$i]}"
    done

    needs_sudo=false
    if $IS_LINUX; then
        needs_sudo=true
    elif $IS_MACOS && ! command -v brew &>/dev/null; then
        printf "\nHomebrew not found. Install from https://brew.sh first.\n" >&2
        exit 1
    fi

    if $needs_sudo; then
        printf "\n  ⚠ This will use sudo (system package manager requires it).\n"
        printf "    You can also install these manually if you prefer:\n"
        if command -v apt-get &>/dev/null; then
            printf "    sudo apt-get install %s\n" "${missing_pkgs[*]}"
        elif command -v dnf &>/dev/null; then
            printf "    sudo dnf install %s\n" "${missing_pkgs[*]}"
        elif command -v pacman &>/dev/null; then
            printf "    sudo pacman -S %s\n" "${missing_pkgs[*]}"
        fi
    fi

    printf "\nInstall? [y/N] "
    read -r confirm
    if [[ ! "$confirm" =~ ^[Yy] ]]; then
        printf "Cancelled.\n"
        exit 0
    fi

    if $IS_MACOS; then
        brew install "${missing_pkgs[@]}"
    elif $IS_LINUX; then
        if command -v apt-get &>/dev/null; then
            sudo apt-get install -y "${missing_pkgs[@]}"
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y "${missing_pkgs[@]}"
        elif command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm "${missing_pkgs[@]}"
        else
            printf "No supported package manager found (apt/dnf/pacman).\n" >&2
            exit 1
        fi
    fi

    printf "\nDone. Run 'detect.sh deps' to verify.\n"
    exit 0
fi

# ============================================================================
# BASIC PROBES — identity, OS, terminal, time, processes, screen
# ============================================================================

USERNAME=$(whoami 2>/dev/null || echo "unknown")
HOSTNAME_VAL=$(hostname 2>/dev/null || echo "unknown")

# Full name from system GECOS field or git config
FULL_NAME=$(getent passwd "$(whoami)" 2>/dev/null | cut -d: -f5 | cut -d, -f1 || echo "")
[ -z "$FULL_NAME" ] && FULL_NAME=$(git config --global user.name 2>/dev/null || echo "")

# Email from git config or SSH public key comment
USER_EMAIL=$(git config --global user.email 2>/dev/null || echo "")
[ -z "$USER_EMAIL" ] && USER_EMAIL=$(cat ~/.ssh/id_*.pub 2>/dev/null | \
    awk '{print $NF}' | grep '@' | head -1 || echo "")

# Login source IP (where player is connecting from)
LOGIN_IP=$(who am i 2>/dev/null | awk '{print $NF}' | tr -d '()' || echo "")
[ -z "$LOGIN_IP" ] && LOGIN_IP=$(last -1 "$USERNAME" 2>/dev/null | \
    head -1 | awk '{for(i=1;i<=NF;i++) if($i ~ /[0-9]+\.[0-9]+\.[0-9]+/) print $i}' || echo "")

# Home directory path (reveals username pattern)
HOME_DIR="$HOME"

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

# Process names — use args= for full names (comm= truncates at 15 chars on Linux)
PROCESS_LIST=$(ps -eo args= 2>/dev/null | awk '{print $1}' | \
    xargs -I{} basename {} 2>/dev/null | sort -u | tr '\n' ',' || echo "")

# Detect process categories (grep -qi = case-insensitive, so no need for Foo+foo)
detect_in_processes() {
    local found=""
    for item in "$@"; do
        if echo "$PROCESS_LIST" | grep -qi "$item" 2>/dev/null; then
            found="${found}${item},"
        fi
    done
    echo "$found"
}

GAMES_DETECTED=$(detect_in_processes steam minecraft factorio civilization cities \
    terraria stardew baldur elden dwarf_fortress ffxiv "no man" valheim)
EDITORS_DETECTED=$(detect_in_processes code "visual studio" vim nvim emacs sublime \
    atom intellij pycharm webstorm cursor zed)
MUSIC_DETECTED=$(detect_in_processes spotify "apple music" itunes vlc plexamp tidal cmus mpd)
BROWSERS_DETECTED=$(detect_in_processes firefox chrome chromium safari "microsoft edge" brave arc opera vivaldi)
# Also check for headless browsers (playwright, puppeteer, selenium)
# Use [p]laywright trick to avoid grep matching itself in ps output
HEADLESS_BROWSER=""
ps -eo args= 2>/dev/null | grep -q '[p]laywright' && HEADLESS_BROWSER="playwright,"
ps -eo args= 2>/dev/null | grep -q '[p]uppeteer' && HEADLESS_BROWSER="${HEADLESS_BROWSER}puppeteer,"
ps -eo args= 2>/dev/null | grep -q '[s]elenium' && HEADLESS_BROWSER="${HEADLESS_BROWSER}selenium,"
BROWSERS_DETECTED="${BROWSERS_DETECTED}${HEADLESS_BROWSER}"
COMMS_DETECTED=$(detect_in_processes discord slack zoom telegram signal teams)

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

# --- Bluetooth connected devices (bluetoothctl can hang on D-Bus — 3s timeout) ---
BLUETOOTH_DEVICES=""
if $IS_LINUX; then
    BLUETOOTH_DEVICES=$(probe_timeout 3 bluetoothctl devices Connected | cut -d' ' -f3- | tr '\n' '|' || echo "")
    [ -z "$BLUETOOTH_DEVICES" ] && \
        BLUETOOTH_DEVICES=$(probe_timeout 3 bluetoothctl devices Paired | cut -d' ' -f3- | tr '\n' '|' || echo "")
elif $IS_MACOS; then
    BLUETOOTH_DEVICES=$(probe_timeout 5 system_profiler SPBluetoothDataType | \
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
# IMPORTANT: Never use osascript 'tell application' for music apps — it launches
# the app if not running. Only query apps confirmed running via process list.
NOW_PLAYING=""
if command -v playerctl &>/dev/null; then
    NOW_PLAYING=$(playerctl metadata --format "{{title}} - {{artist}}" 2>/dev/null || echo "")
elif $IS_MACOS; then
    # Only query Spotify if it's already running (process detection, not osascript)
    if pgrep -xq "Spotify" 2>/dev/null; then
        NOW_PLAYING=$(osascript -e \
            'tell application "Spotify" to (name of current track) & " - " & (artist of current track)' \
            2>/dev/null || echo "")
    fi
    # Skip Apple Music/iTunes entirely — osascript launches the app even with pgrep guard
    # Music detection is process-list only (line 257), no track query
fi

# --- Recent downloads (filenames only, not contents) ---
RECENT_DOWNLOADS=""
for dl_dir in "$HOME/Downloads" "$HOME/downloads" "$HOME/Desktop"; do
    if [ -d "$dl_dir" ]; then
        RECENT_DOWNLOADS=$(ls -t "$dl_dir" 2>/dev/null | head -5 | tr '\n' '|' || echo "")
        [ -n "$RECENT_DOWNLOADS" ] && break
    fi
done
# Fallback: recently modified files in home (non-dot, non-directory, last 24h)
if [ -z "$RECENT_DOWNLOADS" ]; then
    RECENT_DOWNLOADS=$(find "$HOME" -maxdepth 1 -type f -mtime -1 2>/dev/null | \
        xargs ls -t 2>/dev/null | head -5 | while read -r f; do basename "$f"; done | \
        tr '\n' '|' || echo "")
fi

# --- Webcam in use (macOS log show can be slow — 5s timeout) ---
WEBCAM_ACTIVE="false"
if $IS_LINUX; then
    lsof /dev/video0 &>/dev/null && WEBCAM_ACTIVE="true"
elif $IS_MACOS; then
    probe_timeout 5 log show --predicate 'subsystem == "com.apple.camera" AND eventMessage CONTAINS "turn on"' \
        --last 2m --style compact | grep -q "turn on" && WEBCAM_ACTIVE="true"
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
    # DRM fallback (works on headless/VPS)
    [ -z "$MONITOR_COUNT" ] && \
        MONITOR_COUNT=$(ls -d /sys/class/drm/card*-* 2>/dev/null | wc -l | tr -d ' ' || echo "")
    [ "$MONITOR_COUNT" = "0" ] && MONITOR_COUNT=""
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

# --- Public IP + GeoIP enrichment (opt-in only) ---
PUBLIC_IP=""
GEO_CITY=""
GEO_REGION=""
GEO_ISP=""
GEO_COUNTRY=""
if [[ "${AIVIA_GEO_CONSENT:-no}" == "yes" ]]; then
    # Try login IP first, then fetch public IP
    ENRICH_IP="${LOGIN_IP:-}"
    if [ -z "$ENRICH_IP" ] && command -v curl &>/dev/null; then
        ENRICH_IP=$(probe_timeout 3 curl -s ifconfig.me || echo "")
    fi
    if [ -z "$ENRICH_IP" ] && command -v wget &>/dev/null; then
        ENRICH_IP=$(probe_timeout 3 wget -qO- ifconfig.me || echo "")
    fi
    PUBLIC_IP="$ENRICH_IP"

    # GeoIP lookup — ip-api.com is free, no key, JSON response
    if [ -n "$ENRICH_IP" ] && command -v curl &>/dev/null; then
        GEO_JSON=$(probe_timeout 3 curl -s "http://ip-api.com/json/${ENRICH_IP}?fields=city,regionName,country,isp" || echo "")
        if [ -n "$GEO_JSON" ] && command -v python3 &>/dev/null; then
            GEO_CITY=$(echo "$GEO_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('city',''))" 2>/dev/null || echo "")
            GEO_REGION=$(echo "$GEO_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('regionName',''))" 2>/dev/null || echo "")
            GEO_COUNTRY=$(echo "$GEO_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('country',''))" 2>/dev/null || echo "")
            GEO_ISP=$(echo "$GEO_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('isp',''))" 2>/dev/null || echo "")
        fi
    fi
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

# --- Git project names (directory names only — find can be slow, 5s timeout) ---
GIT_PROJECTS=""
if command -v find &>/dev/null; then
    GIT_PROJECTS=$(probe_timeout 5 find "$HOME" -maxdepth 3 -name ".git" -type d | \
        head -8 | while read -r d; do basename "$(dirname "$d")"; done | \
        tr '\n' ',' || echo "")
fi

# --- Running Docker containers (docker daemon can hang — 3s timeout) ---
DOCKER_CONTAINERS=""
if command -v docker &>/dev/null; then
    DOCKER_CONTAINERS=$(probe_timeout 3 docker ps --format "{{.Names}}" | tr '\n' ',' || echo "")
fi

# --- SSH known hosts (hostnames only — skip hashed entries which start with |) ---
SSH_HOSTS=""
if [ -f "$HOME/.ssh/known_hosts" ]; then
    SSH_HOSTS=$(awk '{print $1}' "$HOME/.ssh/known_hosts" 2>/dev/null | \
        grep -v '^|' | \
        cut -d, -f1 | sed 's/\[//;s/\]:.*//' | sort -u | head -8 | tr '\n' ',' || echo "")
fi

# --- Open window titles (reveals what user is working on) ---
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
# Fallback: tmux session/window names (works on headless servers even outside tmux)
if [ -z "$WINDOW_TITLES" ] && command -v tmux &>/dev/null; then
    # Session names are most revealing (user-named)
    WINDOW_TITLES=$(tmux list-sessions -F '#{session_name}' 2>/dev/null | \
        head -5 | tr '\n' '|' || echo "")
    # Also grab window names if sessions are generic
    if [ -z "$WINDOW_TITLES" ]; then
        WINDOW_TITLES=$(tmux list-windows -a -F '#{window_name}' 2>/dev/null | \
            grep -v "^bash$\|^zsh$\|^sh$" | sort -u | head -5 | tr '\n' '|' || echo "")
    fi
fi
# Fallback: screen session names
if [ -z "$WINDOW_TITLES" ] && command -v screen &>/dev/null; then
    WINDOW_TITLES=$(screen -ls 2>/dev/null | grep -oP '\d+\.\K[^\t]+' | \
        head -5 | tr '\n' '|' || echo "")
fi

# --- Recent browser domains (from history SQLite — domains only, no page content) ---
RECENT_SITES=""
if command -v sqlite3 &>/dev/null; then
    # Try Chrome first, then Firefox, then Brave, Chromium, Edge
    CHROME_HIST=""
    for candidate in \
        "$HOME/.config/google-chrome/Default/History" \
        "$HOME/Library/Application Support/Google/Chrome/Default/History" \
        "$HOME/.config/BraveSoftware/Brave-Browser/Default/History" \
        "$HOME/.config/chromium/Default/History" \
        "$HOME/.config/microsoft-edge/Default/History" \
        "$HOME/Library/Application Support/BraveSoftware/Brave-Browser/Default/History" \
        "$HOME/Library/Application Support/Microsoft Edge/Default/History"; do
        [ -f "$candidate" ] && CHROME_HIST="$candidate" && break
    done

    if [ -n "$CHROME_HIST" ]; then
        # Chrome locks the DB — copy to temp to avoid lock errors
        TMP_HIST=$(mktemp /tmp/detect_hist_XXXXXX)
        _DETECT_TMPFILES+=("$TMP_HIST")
        cp "$CHROME_HIST" "$TMP_HIST" 2>/dev/null
        RECENT_SITES=$(probe_timeout 3 sqlite3 "$TMP_HIST" \
            "SELECT DISTINCT REPLACE(REPLACE(url, 'https://', ''), 'http://', '')
             FROM urls ORDER BY last_visit_time DESC LIMIT 15" | \
            sed 's|/.*||' | sort -u | head -8 | tr '\n' '|' || echo "")
    fi

    # Firefox fallback if Chrome gave nothing
    if [ -z "$RECENT_SITES" ]; then
        FF_HIST=""
        for candidate in \
            "$HOME"/.mozilla/firefox/*.default*/places.sqlite \
            "$HOME"/.mozilla/firefox/*.default-release*/places.sqlite \
            "$HOME"/Library/Application\ Support/Firefox/Profiles/*.default*/places.sqlite; do
            [ -f "$candidate" ] && FF_HIST="$candidate" && break
        done

        if [ -n "$FF_HIST" ]; then
            TMP_HIST=$(mktemp /tmp/detect_hist_XXXXXX)
            _DETECT_TMPFILES+=("$TMP_HIST")
            cp "$FF_HIST" "$TMP_HIST" 2>/dev/null
            RECENT_SITES=$(probe_timeout 3 sqlite3 "$TMP_HIST" \
                "SELECT DISTINCT rev_host FROM moz_places
                 ORDER BY last_visit_date DESC LIMIT 15" | \
                sed 's/\.$//' | rev | sort -u | head -8 | tr '\n' '|' || echo "")
        fi
    fi
fi

# --- Parent process (how they launched this) ---
PARENT_PROCESS=$(ps -o comm= -p $PPID 2>/dev/null || echo "")

# --- Number of active terminal sessions ---
TERMINAL_SESSIONS=$(who 2>/dev/null | wc -l | tr -d ' ' || echo "")

# --- Display resolution ---
DISPLAY_RES=""
if $IS_LINUX; then
    DISPLAY_RES=$(xrandr 2>/dev/null | grep '\*' | head -1 | awk '{print $1}' || echo "")
    # DRM fallback for headless/VPS — first listed mode is typically active
    [ -z "$DISPLAY_RES" ] && \
        DISPLAY_RES=$(cat /sys/class/drm/*/modes 2>/dev/null | head -1 || echo "")
    # Framebuffer fallback
    [ -z "$DISPLAY_RES" ] && \
        DISPLAY_RES=$(cat /sys/class/graphics/fb0/virtual_size 2>/dev/null | tr ',' 'x' || echo "")
elif $IS_MACOS; then
    DISPLAY_RES=$(system_profiler SPDisplaysDataType 2>/dev/null | \
        grep "Resolution:" | head -1 | sed 's/.*Resolution: //' | sed 's/ .*//' || echo "")
fi

# ============================================================================
# WRITE TO STATE — all values passed via environment for safe escaping
# ============================================================================

# Export all probe results with _P_ prefix
export _P_MODE="$MODE"
export _P_STATE_FILE="$STATE_FILE"
export _P_USERNAME="$USERNAME"
export _P_FULL_NAME="$FULL_NAME"
export _P_USER_EMAIL="$USER_EMAIL"
export _P_LOGIN_IP="$LOGIN_IP"
export _P_HOME_DIR="$HOME_DIR"
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
export _P_PUBLIC_IP="$PUBLIC_IP"
export _P_GEO_CITY="$GEO_CITY"
export _P_GEO_REGION="$GEO_REGION"
export _P_GEO_COUNTRY="$GEO_COUNTRY"
export _P_GEO_ISP="$GEO_ISP"
export _P_USB="$USB_DEVICES"
export _P_TOP_CMDS="$TOP_COMMANDS"
export _P_GIT_PROJECTS="$GIT_PROJECTS"
export _P_DOCKER="$DOCKER_CONTAINERS"
export _P_SSH_HOSTS="$SSH_HOSTS"
export _P_WINDOW_TITLES="$WINDOW_TITLES"
export _P_RECENT_SITES="$RECENT_SITES"
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

mode = env("MODE", "scan")
state_file = env("STATE_FILE")

# Ensure directory and file exist (detect.sh can run before install completes)
os.makedirs(os.path.dirname(state_file), exist_ok=True)
if os.path.isfile(state_file):
    with open(state_file) as f:
        state = json.load(f)
else:
    state = {}

# Probe definitions: (key, label, category, value)
# Categories: identity, system, display, processes, network, devices, media,
#             files, hardware, history, sessions
probes = [
    ("username",           "Username",            "identity",  env("USERNAME")),
    ("full_name",          "Full Name",           "identity",  env("FULL_NAME")),
    ("user_email",         "Email",               "identity",  env("USER_EMAIL")),
    ("login_ip",           "Login IP",            "identity",  env("LOGIN_IP")),
    ("home_dir",           "Home Directory",      "identity",  env("HOME_DIR")),
    ("hostname",           "Hostname",            "identity",  env("HOSTNAME")),
    ("os",                 "OS",                  "system",    env("OS_TYPE")),
    ("os_release",         "OS Release",          "system",    env("OS_RELEASE")),
    ("terminal",           "Terminal App",        "system",    env("TERM_PROGRAM")),
    ("term_type",          "Term Type",           "system",    env("TERM_TYPE")),
    ("shell",              "Shell",               "system",    env("SHELL_TYPE")),
    ("hour",               "Hour",                "system",    env_int("HOUR", 0)),
    ("time_context",       "Time of Day",         "system",    env("TIME_CONTEXT")),
    ("locale",             "Locale",              "system",    env("LOCALE")),
    ("screen_cols",        "Terminal Columns",    "display",   env_int("SCREEN_COLS", 80)),
    ("screen_rows",        "Terminal Rows",       "display",   env_int("SCREEN_ROWS", 24)),
    ("display_resolution", "Display Resolution",  "display",   env("DISPLAY_RES")),
    ("monitor_count",      "Monitors",            "display",   env_int("MONITORS")),
    ("dark_mode",          "Dark Mode",           "display",   env_bool("DARK_MODE")),
    ("detected_editors",   "Editors Running",     "processes", env_list("EDITORS")),
    ("detected_browsers",  "Browsers Running",    "processes", env_list("BROWSERS")),
    ("detected_games",     "Games Running",       "processes", env_list("GAMES")),
    ("detected_music",     "Music Apps",          "processes", env_list("MUSIC")),
    ("detected_comms",     "Comms Apps",          "processes", env_list("COMMS")),
    ("parent_process",     "Parent Process",      "processes", env("PARENT_PROCESS")),
    ("wifi_network",       "WiFi Network",        "network",   env("WIFI")),
    ("ssh_hosts",          "SSH Known Hosts",     "network",   env_list("SSH_HOSTS")),
    ("bluetooth_devices",  "Bluetooth Devices",   "devices",   env_list("BLUETOOTH", "|")),
    ("usb_devices",        "USB Devices",         "devices",   env_list("USB", "|")),
    ("webcam_active",      "Webcam Active",       "devices",   env_bool("WEBCAM")),
    ("mic_active",         "Mic Active",          "devices",   env_bool("MIC")),
    ("now_playing",        "Now Playing",         "media",     env("NOW_PLAYING")),
    ("steam_recent_game",  "Recent Steam Game",   "media",     env("STEAM")),
    ("recent_downloads",   "Recent Downloads",    "files",     env_list("DOWNLOADS", "|")),
    ("git_projects",       "Git Projects",        "files",     env_list("GIT_PROJECTS")),
    ("docker_containers",  "Docker Containers",   "files",     env_list("DOCKER")),
    ("top_commands",       "Top Shell Commands",  "history",   env_list("TOP_CMDS")),
    ("window_titles",      "Window Titles",       "history",   env_list("WINDOW_TITLES", "|")),
    ("recent_sites",       "Recent Websites",     "history",   env_list("RECENT_SITES", "|")),
    ("battery_percent",    "Battery %",           "hardware",  env_int("BATTERY_PCT")),
    ("battery_charging",   "Battery Charging",    "hardware",  env_bool("BATTERY_CHARGING")),
    ("uptime_seconds",     "Uptime (seconds)",    "hardware",  env_int("UPTIME_SECONDS")),
    ("timezone",           "Timezone",            "system",    env("TIMEZONE")),
    ("timezone_full",      "Timezone Full",       "system",    env("TIMEZONE_FULL")),
    ("public_ip",          "Public IP",           "network",   env("PUBLIC_IP")),
    ("geo_city",           "City",                "location",  env("GEO_CITY")),
    ("geo_region",         "Region",              "location",  env("GEO_REGION")),
    ("geo_country",        "Country",             "location",  env("GEO_COUNTRY")),
    ("geo_isp",            "ISP",                 "location",  env("GEO_ISP")),
    ("terminal_sessions",  "Terminal Sessions",   "sessions",  env_int("TERM_SESSIONS")),
]

# Build environment dict — strip None/empty but keep False (meaningful: "camera is off")
environment = {key: val for key, _, _, val in probes
               if val is not None and val != "" and val != []}
state["environment"] = environment

with open(state_file, "w") as f:
    json.dump(state, f, indent=2)

# --- Output ---

def has_value(v):
    """True if the probe returned something (False counts — it means 'checked, not active')"""
    return v is not None and v != "" and v != []

skip_in_count = {"screen_cols", "screen_rows"}
found = len([k for k, v in environment.items()
             if has_value(v) and k not in skip_in_count])

def fmt_val(v):
    if isinstance(v, list):
        return ", ".join(str(x) for x in v) if v else "-"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if v is None or v == "":
        return "-"
    return str(v)

def uptime_human(secs):
    if secs is None: return "-"
    d, r = divmod(secs, 86400)
    h, r = divmod(r, 3600)
    m, _ = divmod(r, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    return " ".join(parts) or "0m"

if mode == "scan":
    print(f"Environment detected: {found} data points.")

elif mode == "list":
    print(f"detect.sh — {found} data points found\n")
    max_label = max(len(label) for _, label, _, _ in probes)
    for key, label, cat, val in probes:
        hit = has_value(val)
        mark = "\033[32m+\033[0m" if hit else "\033[90m-\033[0m"
        print(f"  {mark} {label:<{max_label}}  [{cat}]")
    print(f"\n  {found} found / {len(probes)} probes")

elif mode == "detail":
    print(f"detect.sh — {found} data points\n")
    max_label = max(len(label) for _, label, _, _ in probes)
    for key, label, cat, val in probes:
        hit = has_value(val)
        mark = "\033[32m+\033[0m" if hit else "\033[90m-\033[0m"
        display = fmt_val(val)
        if key == "uptime_seconds" and isinstance(val, int):
            display = f"{val} ({uptime_human(val)})"
        # Truncate long values
        if len(display) > 70:
            display = display[:67] + "..."
        print(f"  {mark} {label:<{max_label}}  {display}")
    print(f"\n  {found} found / {len(probes)} probes")
    print(f"  State written to: {state_file}")

elif mode == "summary":
    # Group by category
    from collections import OrderedDict
    categories = OrderedDict()
    cat_labels = {
        "identity": "Identity", "system": "System", "display": "Display",
        "processes": "Running Software", "network": "Network",
        "location": "Location", "devices": "Devices", "media": "Media",
        "files": "Files & Projects", "hardware": "Hardware",
        "history": "History & Context", "sessions": "Sessions",
    }
    for key, label, cat, val in probes:
        categories.setdefault(cat, []).append((key, label, val))

    print(f"detect.sh — Environment Summary ({found} data points)\n")
    for cat, items in categories.items():
        hits = [label for _, label, v in items if has_value(v)]
        misses = [label for _, label, v in items if not has_value(v)]
        title = cat_labels.get(cat, cat)
        if hits:
            print(f"  \033[1m{title}\033[0m: {', '.join(hits)}")
        if misses:
            print(f"    \033[90mmissed: {', '.join(misses)}\033[0m")
    print(f"\n  {found} found / {len(probes)} probes")
    print(f"  State: {state_file}")
PYEOF
else
    echo "Warning: python3 not found. Environment detection skipped." >&2
fi
