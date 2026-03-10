#!/usr/bin/env bash
set -e

SCRIPT_NAME="start-ifbcat.sh"
SCRIPT_PATH="$(pwd)/${SCRIPT_NAME}"
LINK_PATH="/usr/local/bin/start-ifbcat.sh"
SERVICE_FILE="/etc/systemd/system/ifbcat.service"

if [[ ! -f "$SCRIPT_PATH" ]]; then
    echo "Error: ${SCRIPT_NAME} not found in current directory"
    exit 1
fi

echo "Creating symlink: $LINK_PATH -> $SCRIPT_PATH"
sudo ln -sf "$SCRIPT_PATH" "$LINK_PATH"

echo "Installing systemd service file"
sudo cp ifbcat.service "$SERVICE_FILE"

echo "Reloading systemd daemon"
sudo systemctl daemon-reload

echo "Enabling ifbcat service"
sudo systemctl enable ifbcat.service

echo "Setup complete! To start the service:"
echo "  sudo systemctl start ifbcat.service"
echo "To check status:"
echo "  systemctl status ifbcat.service"