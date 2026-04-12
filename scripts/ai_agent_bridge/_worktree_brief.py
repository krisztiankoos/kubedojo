"""Helpers for writing Codex worktree status briefs.

This module is intentionally standalone so the runtime adapter can wire it in
later without pulling bridge-specific behavior into the runtime package.
"""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path

import yaml

_BRIEF_FILENAME = ".codex-worktree-brief.yaml"


def _utcnow() -> datetime:
    """Return the current UTC time as an aware datetime."""
    return datetime.now(UTC)


def _run_git(worktree_path: Path, *args: str) -> str:
    """Run a git command scoped to the given worktree."""
    completed = subprocess.run(
        ["git", "-C", str(worktree_path), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def write_worktree_brief(worktree_path: Path, task_id: str) -> Path:
    """Write ``.codex-worktree-brief.yaml`` at the worktree root."""
    main_head_sha = _run_git(worktree_path, "rev-parse", "main")
    divergence_counts = _run_git(
        worktree_path, "rev-list", "--left-right", "--count", "main...HEAD"
    )
    main_ahead_raw, worktree_ahead_raw = divergence_counts.split()

    payload = {
        "worktree_path": str(worktree_path),
        "main_branch": "main",
        "main_head_sha": main_head_sha,
        "divergence": {
            "main_ahead": int(main_ahead_raw),
            "worktree_ahead": int(worktree_ahead_raw),
        },
        "task_id": task_id,
        "generated_at": _utcnow().isoformat().replace("+00:00", "Z"),
    }

    output_path = worktree_path / _BRIEF_FILENAME
    output_path.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )
    return output_path
