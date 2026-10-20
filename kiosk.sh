#!/usr/bin/env bash
set -euo pipefail
browser=$(command -v chromium || command -v chromium-browser || true)
if [[ -z "$browser" ]]; then echo 'Install Chromium to launch kiosk mode.' >&2; exit 1; fi
kiosk_url="${1:-http://127.0.0.1:8080}"
if [[ "$kiosk_url" == *\?* ]]; then kiosk_url="${kiosk_url}&kiosk=1"; else kiosk_url="${kiosk_url}?kiosk=1"; fi
exec "$browser" --password-store=basic --kiosk --no-first-run --user-data-dir="${XDG_DATA_HOME:-$HOME/.local/share}/HalloweenHub/chromium" "$kiosk_url"
