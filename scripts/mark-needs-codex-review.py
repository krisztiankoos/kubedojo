#!/usr/bin/env python3
"""Mark every passed module in .pipeline/state.yaml as needing Codex re-review.

Run this after switching the official reviewer from Gemini to Codex. All modules
previously passed by Gemini get a `needs_codex_review=True` flag and their
`reviewer` field is set to their original reviewer (inferred as "gemini" if
absent, since the historical MODELS["review"] was gemini-3.1-pro-preview).

The modules are NOT reset to an earlier phase — the content on disk is still
considered usable. Only the official reviewer stamp is flagged as missing, so
operators can prioritize re-reviewing with Codex when quota is available.

Usage:
    python scripts/mark-needs-codex-review.py --dry-run    # show what would change
    python scripts/mark-needs-codex-review.py --apply      # persist changes

The script is idempotent: running it twice is a no-op on already-marked modules.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
STATE_FILE = REPO_ROOT / ".pipeline" / "state.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    group.add_argument("--apply", action="store_true", help="Persist changes to state.yaml")
    args = parser.parse_args()

    if not STATE_FILE.exists():
        print(f"State file not found: {STATE_FILE}", file=sys.stderr)
        return 1

    state = yaml.safe_load(STATE_FILE.read_text()) or {}
    modules = state.get("modules") or {}

    total = 0
    would_mark = 0
    already_marked = 0
    not_done = 0

    for ms in modules.values():
        total += 1
        phase = ms.get("phase")
        if phase != "done":
            not_done += 1
            continue
        reviewer = ms.get("reviewer")
        if reviewer == "codex" and not ms.get("needs_codex_review", False):
            already_marked += 1
            continue
        # Flag for re-review. Preserve original reviewer if known; else assume
        # gemini (historical default).
        if not reviewer:
            ms["reviewer"] = "gemini"
        ms["needs_codex_review"] = True
        would_mark += 1

    print(f"Total modules in state: {total}")
    print(f"  phase=done: {total - not_done}")
    print(f"  phase!=done (skipped): {not_done}")
    print(f"  already codex-reviewed: {already_marked}")
    print(f"  to flag needs_codex_review=True: {would_mark}")

    if args.apply and would_mark > 0:
        STATE_FILE.write_text(yaml.safe_dump(state, sort_keys=False))
        print(f"\n✓ Applied. {would_mark} modules flagged in {STATE_FILE}")
    elif args.dry_run:
        print("\n(dry-run — no changes written)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
