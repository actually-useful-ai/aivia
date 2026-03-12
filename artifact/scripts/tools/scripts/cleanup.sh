#!/bin/bash

# Cleanup script for maintaining directory organization

# Clean temporary directory
echo "Cleaning temporary files..."
find ~/temp -type f -mtime +7 -exec rm {} \;

# Archive old backups
echo "Archiving old backups..."
current_month=$(date +%Y-%m)
if [ -d ~/backups/2024 ]; then
    find ~/backups/2024 -type f -mtime +30 -exec mv {} ~/backups/archives/$current_month/ \;
fi

# Clean cache directories
echo "Cleaning cache..."
find ~/.cache -type f -mtime +30 -delete 2>/dev/null

# Trim history files
echo "Trimming history files..."
if [ -f ~/.cache/history/.bash_history ]; then
    tail -n 1000 ~/.cache/history/.bash_history > ~/.cache/history/.bash_history.tmp
    mv ~/.cache/history/.bash_history.tmp ~/.cache/history/.bash_history
fi

# Remove empty directories
echo "Removing empty directories..."
find ~/ -type d -empty -delete 2>/dev/null

# Ensure proper permissions
echo "Setting proper permissions..."
chmod 700 ~/.ssh ~/.config/ssl ~/.cache/history 2>/dev/null
chmod 600 ~/.config/ssl/* ~/.cache/history/* 2>/dev/null

echo "Cleanup complete!" 