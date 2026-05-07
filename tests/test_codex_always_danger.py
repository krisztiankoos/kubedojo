"""Regression tests: codex always runs in danger mode.

read-only starved Codex of network/filesystem and caused rc=-9 stale-rollout
salvage — three failures in a single session 2026-05-07. These tests ensure
the guard cannot be silently undone.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


def test_codex_adapter_rejects_read_only_mode():
    """runner.invoke('codex', ..., mode='read-only') must raise ValueError.

    CodexAdapter.supported_modes no longer includes 'read-only'. The runner
    validates mode pre-spawn (step 2 of the invoke flow), so no subprocess
    is ever launched.
    """
    from agent_runtime.runner import invoke

    with pytest.raises(ValueError, match="does not support mode"):
        invoke(
            "codex",
            "x",
            mode="read-only",
            cwd=None,
            model=None,
            task_id=None,
        )


def test_dispatch_smart_codex_forces_danger_mode():
    """dispatch_smart.py review --agent codex --dry-run always resolves mode=danger.

    Regardless of the 'review' task class default (read-only), codex
    dispatches must be overridden to danger before any validation runs.
    """
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "dispatch_smart.py"),
            "review",
            "--agent", "codex",
            "--dry-run",
            "-",
        ],
        input="x",
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, (
        f"dispatch_smart.py exited {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "mode=danger" in result.stdout, (
        f"Expected 'mode=danger' in stdout but got:\n{result.stdout}"
    )
