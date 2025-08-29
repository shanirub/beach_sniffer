#!/bin/bash
set -e
SERVICE_NAME="beachsniffer.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"
echo "Installing $SERVICE_NAME ..."
sudo cp "$(dirname "$0")/$SERVICE_NAME" "$SERVICE_PATH"
echo "Reloading systemd..."
sudo systemctl daemon-reload
echo "Enabling service..."
sudo systemctl enable "$SERVICE_NAME"
echo "Restarting service..."
sudo systemctl restart "$SERVICE_NAME"
echo "Done! Use 'journalctl -u $SERVICE_NAME -f' to view logs."