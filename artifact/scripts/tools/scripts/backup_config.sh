#!/bin/bash

# Configuration backup script

# Set backup directory
BACKUP_DIR="$HOME/backups/config_backups/$(date +%Y-%m)"
mkdir -p "$BACKUP_DIR"

# Backup .config directory
echo "Backing up .config directory..."
tar -czf "$BACKUP_DIR/config_backup.tar.gz" -C "$HOME" .config/

# Backup shell configurations
echo "Backing up shell configurations..."
cp "$HOME/.bash_profile" "$HOME/.bashrc" "$BACKUP_DIR/" 2>/dev/null

# Backup git configurations
echo "Backing up git configurations..."
cp "$HOME/.config/git/"* "$BACKUP_DIR/" 2>/dev/null

# Backup editor configurations
echo "Backing up editor configurations..."
cp "$HOME/.config/editors/"* "$BACKUP_DIR/" 2>/dev/null

# Set proper permissions
chmod 600 "$BACKUP_DIR"/*

echo "Configuration backup complete!"
echo "Backup stored in: $BACKUP_DIR" 