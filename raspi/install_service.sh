#!/bin/bash
set -e

SERVICE_NAME="beachsniffer.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"

echo "Installing $SERVICE_NAME ..."

# Copy service file
sudo cp "$(dirname "$0")/$SERVICE_NAME" "$SERVICE_PATH"

# Reload systemd to pick up changes
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Enable service (start at boot)
echo "Enabling service..."
sudo systemctl enable "$SERVICE_NAME"

# Restart service (or start if new)
echo "Restarting service..."
sudo systemctl restart "$SERVICE_NAME"

echo "Done! Use 'journalctl -u $SERVICE_NAME -f' to view logs."

