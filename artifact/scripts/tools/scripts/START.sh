#!/bin/bash
set -euo pipefail

# Variables
log_dir="/var/log/startup_scripts"
mkdir -p $log_dir
ports=(5003 5005 5002)
admin_venv="/home/html/admin/admin_venv"
chat_venv="/home/html/admin/venv_chat"
# portal_venv="/home/html/portal/venv_portal"
admin_script="/home/html/admin/server_admin_5003.py"
chat_script="/home/html/admin/server_chat_5002.py"
# backup_script="/home/html/admin/server_chat_backup_5002.py"
# portal_script="/home/html/portal/app.py"

admin_log="$log_dir/admin_server.log"
chat_log="$log_dir/chat_server.log"
# backup_log="$log_dir/backup_server.log"
# portal_log="$log_dir/portal_server.log"

# Stop services if --stop is provided
if [ "${1:-}" == "--stop" ]; then
    echo "Stopping all services..."
    pkill -f "server_admin_5003.py"
    pkill -f "server_chat_5002.py"
    # pkill -f "server_chat_backup_5002.py"
    # pkill -f "chainlit"
    echo "All services stopped."
    exit 0
fi

# Cleanup on exit
trap 'echo "Script interrupted. Cleaning up..."; pkill -P $$; exit' SIGINT SIGTERM

# Kill processes on required ports
for port in "${ports[@]}"; do
    pid=$(sudo lsof -t -i:$port)
    if [ ! -z "$pid" ]; then
        echo "Killing process on port $port..."
        sudo kill -9 $pid
    fi
done

# Start services
source $admin_venv/bin/activate
python3 $admin_script > $admin_log 2>&1 &
deactivate

source $chat_venv/bin/activate
python3 $chat_script > $chat_log 2>&1 &
# python3 $backup_script > $backup_log 2>&1 &
deactivate

# source $portal_venv/bin/activate
# chainlit run $portal_script -wh > $portal_log 2>&1 &
# deactivate

# Health checks
check_service() {
    local name="$1"
    local port="$2"
    if nc -z localhost $port; then
        echo "$name on port $port is running."
    else
        echo "Failed to start $name on port $port. Exiting."
        exit 1
    fi
}

check_service "Admin Server" 5003
# check_service "Chat Server" 5005
check_service "Chat Server" 5002
# check_service "Portal" 8000

echo "All systems go, boss!"