#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
  echo "[!] Please run as root (e.g., sudo bash setup_systemd.sh)"
  exit 1
fi

echo "[*] Copying gateway.service to /etc/systemd/system/..."
cp /home/fyp1512/gateway.service /etc/systemd/system/gateway.service

echo "[*] Reloading systemd daemon..."
systemctl daemon-reload

echo "[*] Enabling gateway.service on boot..."
systemctl enable gateway.service

echo "[*] Starting gateway.service now..."
systemctl restart gateway.service

echo "[+] Successfully configured. Service status:"
systemctl status gateway.service --no-pager
