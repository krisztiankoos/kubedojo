#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOME="${HOME:?HOME must be set}"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
LOG_DIR="$REPO_ROOT/.pipeline/launchd-logs"

sed_escape() {
	printf '%s' "$1" | sed 's/[&|]/\\&/g'
}

escaped_home="$(sed_escape "$HOME")"
escaped_repo_root="$(sed_escape "$REPO_ROOT")"

mkdir -p "$LOG_DIR"
mkdir -p "$LAUNCH_AGENTS_DIR"

for tmpl in "$SCRIPT_DIR"/*.plist.tmpl; do
	plist_name="$(basename "${tmpl%.tmpl}")"
	target="$LAUNCH_AGENTS_DIR/$plist_name"

	sed \
		-e "s|{{HOME}}|$escaped_home|g" \
		-e "s|{{REPO_ROOT}}|$escaped_repo_root|g" \
		"$tmpl" > "$target"

	launchctl unload "$target" >/dev/null 2>&1 || true
	launchctl load "$target"
done

launchctl list | grep -E 'kubedojo' || echo "(no kubedojo jobs registered yet)"
echo "Installed. Logs at: $LOG_DIR/"
