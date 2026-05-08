#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME="${HOME:?HOME must be set}"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

for tmpl in "$SCRIPT_DIR"/*.plist.tmpl; do
	plist_name="$(basename "${tmpl%.tmpl}")"
	label="${plist_name%.plist}"
	target="$LAUNCH_AGENTS_DIR/$plist_name"

	launchctl unload "$target" >/dev/null 2>&1 || true
	rm -f "$target"
done

echo "Uninstalled."
