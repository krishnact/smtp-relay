#!/bin/bash

CERT_PATH="/etc/ssl/private/server.pem"

if [ ! -f "$CERT_PATH" ]; then
  echo "[+] Generating self-signed cert at $CERT_PATH"
  mkdir -p "$(dirname "$CERT_PATH")"
  openssl req -new -x509 -days 7305 -nodes \
    -subj "/CN=localhost" \
    -out "$CERT_PATH" -keyout "$CERT_PATH"
  chmod 600 "$CERT_PATH"
else
  echo "[+] Using existing cert at $CERT_PATH"
fi

echo "[+] Starting SMTPS relay server..."
exec python3 /app/email_relay.py
