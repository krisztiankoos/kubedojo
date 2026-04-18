#!/usr/bin/env bash
# Cold-start ritual for a fresh KubeDojo agent session.
# Brings up services (idempotent) and prints the compact briefing.
# Handoffs reference this script instead of duplicating the curl ritual.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

scripts/services-up >&2

API="${KUBEDOJO_API:-http://127.0.0.1:8768}"
BRIEFING_URL="${API}/api/briefing/session?compact=1"

TMP="/tmp/kubedojo_briefing.$$"
trap 'rm -f "$TMP"' EXIT

for _ in 1 2 3 4 5; do
  if curl -sf "$BRIEFING_URL" >"$TMP"; then
    cat "$TMP"
    exit 0
  fi
  sleep 1
done

echo "ERROR: briefing API did not respond at $BRIEFING_URL — falling back to STATUS.md" >&2
exit 1
