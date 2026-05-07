"""Regression tests: codex always runs in danger mode.

read-only starved Codex of network/filesystem and caused rc=-9 stale-rollout
salvage — three failures in a single session 2026-05-07. These tests ensure
the guard cannot be silently undone.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
WORKTREE_ROOT = Path(__file__).resolve().parent.parent
# .venv lives at the primary repo root, not the worktree root — use git common-dir.
_git_common_dir = subprocess.check_output(
    ["git", "-C", str(WORKTREE_ROOT), "rev-parse", "--git-common-dir"],
    text=True,
).strip()
REPO_ROOT = Path(_git_common_dir).parent.resolve()
VENV_PYTHON = str(REPO_ROOT / ".venv/bin/python")


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
            VENV_PYTHON,
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


def test_dispatch_codex_rejects_read_only_sandbox():
    """dispatch_codex() raises ValueError when KUBEDOJO_CODEX_SANDBOX=read-only.

    Confirms the main write-path guard added in round-2 of PR #981.
    """
    import importlib
    import os

    import importlib.util
    spec = importlib.util.spec_from_file_location("dispatch", SCRIPTS_DIR / "dispatch.py")
    dispatch = importlib.util.module_from_spec(spec)
    env_backup = os.environ.get("KUBEDOJO_CODEX_SANDBOX")
    try:
        os.environ["KUBEDOJO_CODEX_SANDBOX"] = "read-only"
        spec.loader.exec_module(dispatch)
        with pytest.raises(ValueError, match="read-only is forbidden"):
            dispatch.dispatch_codex("test prompt")
    finally:
        if env_backup is None:
            os.environ.pop("KUBEDOJO_CODEX_SANDBOX", None)
        else:
            os.environ["KUBEDOJO_CODEX_SANDBOX"] = env_backup


def test_dispatch_codex_default_is_danger():
    """dispatch_codex() builds a --dangerously-bypass-approvals-and-sandbox command by default.

    Verifies the guard added in round-2: no KUBEDOJO_CODEX_SANDBOX set means danger.
    Uses monkeypatching so no real subprocess is spawned.
    """
    import importlib.util
    import os

    os.environ.pop("KUBEDOJO_CODEX_SANDBOX", None)
    spec = importlib.util.spec_from_file_location("dispatch", SCRIPTS_DIR / "dispatch.py")
    dispatch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dispatch)

    captured_cmd: list = []

    def fake_run(cmd, *args, **kwargs):
        captured_cmd.extend(cmd)
        raise FileNotFoundError("no codex cli in test")

    dispatch._run_with_process_group = fake_run
    ok, _ = dispatch.dispatch_codex("test prompt")
    assert not ok
    assert "--dangerously-bypass-approvals-and-sandbox" in captured_cmd, (
        f"Expected danger flag in cmd but got: {captured_cmd}"
    )
    assert "--sandbox" not in captured_cmd, (
        f"--sandbox should not appear in danger-mode cmd, got: {captured_cmd}"
    )
