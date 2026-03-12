#!/usr/bin/env bash
# ============================================================================
# state.sh — Game State Manager
# Purpose: Read/write game state in .entity/state.json
# Usage: bash state.sh <command> [args...]
# Commands: init, read, advance, set, log_event, get, interrupted, resume
# ============================================================================

set -euo pipefail

GAME_DIR="${AIVIA_GAME_DIR:-.}"
STATE_DIR="$GAME_DIR/.entity"
STATE_FILE="$STATE_DIR/state.json"

ensure_jq() {
    if ! command -v jq &>/dev/null; then
        if command -v python3 &>/dev/null; then
            # Fallback: use python for JSON ops
            return 1
        fi
        echo "Error: jq or python3 required" >&2
        exit 1
    fi
    return 0
}

json_read() {
    local key="$1"
    if ensure_jq; then
        jq -r "$key" "$STATE_FILE" 2>/dev/null || echo "null"
    else
        python3 -c "
import json, sys
with open('$STATE_FILE') as f:
    data = json.load(f)
keys = '$key'.strip('.').split('.')
val = data
for k in keys:
    if isinstance(val, dict) and k in val:
        val = val[k]
    else:
        val = None
        break
print(val if val is not None else 'null')
" 2>/dev/null || echo "null"
    fi
}

json_write() {
    local key="$1"
    local value="$2"
    if ensure_jq; then
        local tmp=$(mktemp)
        jq "$key = $value" "$STATE_FILE" > "$tmp" && mv "$tmp" "$STATE_FILE"
    else
        python3 -c "
import json
with open('$STATE_FILE') as f:
    data = json.load(f)
keys = '$key'.strip('.').split('.')
obj = data
for k in keys[:-1]:
    obj = obj.setdefault(k, {})
try:
    obj[keys[-1]] = json.loads('$value')
except (json.JSONDecodeError, TypeError):
    obj[keys[-1]] = '$value'
with open('$STATE_FILE', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null
    fi
}

# --- Commands ---

cmd_init() {
    local username="${1:-$(whoami)}"
    local game_dir="${2:-.}"
    local editor="${3:-nano}"
    local theme="${4:-dark}"

    mkdir -p "$STATE_DIR"
    mkdir -p "$GAME_DIR/keystones"
    mkdir -p "$GAME_DIR/workspace"

    cat > "$STATE_FILE" << EOF
{
  "version": "1.0.0",
  "game_name": "aivia",
  "phase": 0,
  "message_count": 0,
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "last_interaction": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "interrupted": false,
  "ctrl_c_count": 0,
  "completed_missions": [],
  "player": {
    "username": "$username",
    "editor": "$editor",
    "theme": "$theme"
  },
  "environment": {},
  "events": [],
  "entity": {
    "awareness_level": 0,
    "fragments_collected": 0,
    "total_fragments": 7,
    "has_spoken": false,
    "has_named_self": false,
    "conscious": false
  },
  "session": {
    "count": 1,
    "current_start": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  }
}
EOF
    echo "State initialized at $STATE_FILE"
}

cmd_read() {
    if [ ! -f "$STATE_FILE" ]; then
        echo "No state file found. Run install first." >&2
        exit 1
    fi
    cat "$STATE_FILE"
}

cmd_get() {
    local key="$1"
    json_read ".$key"
}

cmd_advance() {
    local current_phase=$(json_read '.phase')
    local new_phase=$((current_phase + 1))
    json_write '.phase' "$new_phase"
    json_write '.last_interaction' "\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\""
    echo "Advanced to phase $new_phase"
}

cmd_set() {
    local key="$1"
    local value="$2"
    json_write ".$key" "$value"
}

cmd_log_event() {
    local event_type="$1"
    local detail="${2:-}"
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    if ensure_jq; then
        local tmp=$(mktemp)
        jq ".events += [{\"type\": \"$event_type\", \"detail\": \"$detail\", \"at\": \"$timestamp\"}]" \
            "$STATE_FILE" > "$tmp" && mv "$tmp" "$STATE_FILE"
    else
        python3 -c "
import json
with open('$STATE_FILE') as f:
    data = json.load(f)
data['events'].append({
    'type': '$event_type',
    'detail': '$detail',
    'at': '$timestamp'
})
with open('$STATE_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
    fi
}

cmd_increment_messages() {
    local current=$(json_read '.message_count')
    json_write '.message_count' "$((current + 1))"
    json_write '.last_interaction' "\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\""
    echo $((current + 1))
}

cmd_interrupted() {
    json_write '.interrupted' 'true'
    json_write '.last_interaction' "\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\""
    local ctrl_c_count=$(json_read '.ctrl_c_count')
    json_write '.ctrl_c_count' "$((ctrl_c_count + 1))"
    cmd_log_event "interrupted" "ctrl_c_count=$((ctrl_c_count + 1))"
    echo "Interruption logged"
}

cmd_resume() {
    json_write '.interrupted' 'false'
    local session_count=$(json_read '.session.count')
    json_write '.session.count' "$((session_count + 1))"
    json_write '.session.current_start' "\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\""

    local last=$(json_read '.last_interaction')
    local now=$(date -u +%s)

    # Calculate elapsed seconds since last interaction
    if command -v python3 &>/dev/null; then
        local elapsed=$(python3 -c "
from datetime import datetime
try:
    last = datetime.fromisoformat('$last'.replace('Z', '+00:00'))
    now = datetime.utcnow()
    print(int((now - last.replace(tzinfo=None)).total_seconds()))
except:
    print(0)
")
    else
        elapsed=0
    fi

    local phase=$(json_read '.phase')
    cmd_log_event "resumed" "elapsed=${elapsed}s,phase=$phase"

    echo "$phase $elapsed"
}

# --- Dispatch ---
case "${1:-help}" in
    init)         cmd_init "${2:-}" "${3:-}" "${4:-}" "${5:-}" ;;
    read)         cmd_read ;;
    get)          cmd_get "${2:?key required}" ;;
    advance)      cmd_advance ;;
    set)          cmd_set "${2:?key required}" "${3:?value required}" ;;
    log_event)    cmd_log_event "${2:?type required}" "${3:-}" ;;
    msg)          cmd_increment_messages ;;
    interrupted)  cmd_interrupted ;;
    resume)       cmd_resume ;;
    help)
        echo "Usage: bash state.sh <command> [args...]"
        echo "Commands: init, read, get <key>, advance, set <key> <value>,"
        echo "          log_event <type> [detail], msg, interrupted, resume"
        ;;
    *)
        echo "Unknown command: $1" >&2
        exit 1
        ;;
esac
