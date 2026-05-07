#!/usr/bin/env bash
# Smoketest: scripts/ab must pin CODEX_BRIDGE_MODE=danger and clobber any
# caller-supplied override.
#
# Regression guard: danger mode is the only valid mode for Codex — read-only
# and workspace-write both starve it of network/filesystem (rc=-9 stale-rollout
# salvage). This test ensures the default cannot be silently changed back.
#
# Exit 0 on pass, non-zero with diagnostic on fail.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
AB="$REPO_ROOT/scripts/ab"
[ -x "$AB" ] || { echo "FAIL: $AB not executable"; exit 1; }

# Extract the env-setup preamble (everything before the final exec) so we can
# source it in isolation and inspect the resulting environment without
# actually invoking the Python bridge.
exec_line="$(grep -n '^exec ' "$AB" | head -1 | cut -d: -f1)"
[ -n "$exec_line" ] || { echo "FAIL: no 'exec' line found in $AB"; exit 1; }

preamble="$(mktemp)"
trap 'rm -f "$preamble"' EXIT
head -n "$((exec_line - 1))" "$AB" > "$preamble"

# Test 1: default is danger when caller has not set the var.
actual_default="$(bash -c "unset CODEX_BRIDGE_MODE; source '$preamble'; printf '%s' \"\$CODEX_BRIDGE_MODE\"")"
if [ "$actual_default" != "danger" ]; then
  echo "FAIL: default CODEX_BRIDGE_MODE is '$actual_default', expected 'danger'"
  echo "HINT: Codex requires danger mode — read-only/workspace-write starve it of network/filesystem."
  exit 1
fi

# Test 2: caller-supplied value is clobbered to danger (no override allowed).
actual_override="$(bash -c "export CODEX_BRIDGE_MODE=workspace-write; source '$preamble' 2>/dev/null; printf '%s' \"\$CODEX_BRIDGE_MODE\"")"
if [ "$actual_override" != "danger" ]; then
  echo "FAIL: CODEX_BRIDGE_MODE=workspace-write was not clobbered; got '$actual_override'"
  echo "HINT: scripts/ab must hard-set CODEX_BRIDGE_MODE=danger, not use := default syntax."
  exit 1
fi

echo "PASS: scripts/ab pins CODEX_BRIDGE_MODE=danger and clobbers any override"
