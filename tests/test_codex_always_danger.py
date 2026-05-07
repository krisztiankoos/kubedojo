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


def _load_dispatch() -> object:
    import importlib.util
    spec = importlib.util.spec_from_file_location("dispatch", SCRIPTS_DIR / "dispatch.py")
    dispatch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dispatch)  # type: ignore[union-attr]
    return dispatch


def _capture_cmd(dispatch_fn, *args, **kwargs) -> list[str]:
    """Call dispatch_fn, intercept _run_with_process_group, return captured cmd."""
    dispatch = _load_dispatch()

    captured_cmd: list[str] = []

    def fake_run(cmd, *_args, **_kwargs):
        captured_cmd.extend(cmd)
        raise FileNotFoundError("no codex cli in test")

    dispatch._run_with_process_group = fake_run  # type: ignore[attr-defined]
    fn = getattr(dispatch, dispatch_fn)
    fn(*args, **kwargs)
    return captured_cmd


def test_codex_adapter_rejects_workspace_write_mode():
    """runner.invoke('codex', ..., mode='workspace-write') must raise ValueError.

    CodexAdapter.supported_modes now only contains 'danger'. workspace-write
    blocks .git/worktrees index.lock and api.github.com — danger is required.
    """
    from agent_runtime.runner import invoke

    with pytest.raises(ValueError, match="does not support mode"):
        invoke(
            "codex",
            "x",
            mode="workspace-write",
            cwd=None,
            model=None,
            task_id=None,
        )


def test_dispatch_codex_sandbox_env_ignored():
    """KUBEDOJO_CODEX_SANDBOX env var is now ignored; cmd is always danger.

    The env override was removed in this PR — the var no longer affects
    command construction. Verify the flag is still danger even when the
    env var is set to workspace-write.
    """
    import os
    env_backup = os.environ.get("KUBEDOJO_CODEX_SANDBOX")
    try:
        os.environ["KUBEDOJO_CODEX_SANDBOX"] = "workspace-write"
        cmd = _capture_cmd("dispatch_codex", "test prompt")
    finally:
        if env_backup is None:
            os.environ.pop("KUBEDOJO_CODEX_SANDBOX", None)
        else:
            os.environ["KUBEDOJO_CODEX_SANDBOX"] = env_backup

    assert "--dangerously-bypass-approvals-and-sandbox" in cmd, (
        f"Expected danger flag even with KUBEDOJO_CODEX_SANDBOX=workspace-write, got: {cmd}"
    )
    assert "--full-auto" not in cmd, (
        f"--full-auto must not appear when env var is ignored, got: {cmd}"
    )


def test_dispatch_codex_default_is_danger():
    """dispatch_codex() builds a --dangerously-bypass-approvals-and-sandbox command.

    Env var is gone; the flag is unconditional.
    """
    import os
    os.environ.pop("KUBEDOJO_CODEX_SANDBOX", None)
    cmd = _capture_cmd("dispatch_codex", "test prompt")
    assert "--dangerously-bypass-approvals-and-sandbox" in cmd, (
        f"Expected danger flag in cmd but got: {cmd}"
    )
    assert "--sandbox" not in cmd, (
        f"--sandbox should not appear in danger-mode cmd, got: {cmd}"
    )


def test_dispatch_codex_always_includes_search():
    """dispatch_codex() always includes --search regardless of KUBEDOJO_CODEX_SEARCH env."""
    import os
    for val in ("0", "1", None):
        if val is None:
            os.environ.pop("KUBEDOJO_CODEX_SEARCH", None)
        else:
            os.environ["KUBEDOJO_CODEX_SEARCH"] = val
        cmd = _capture_cmd("dispatch_codex", "test prompt")
        assert "--search" in cmd, (
            f"Expected --search in cmd (KUBEDOJO_CODEX_SEARCH={val!r}), got: {cmd}"
        )
    os.environ.pop("KUBEDOJO_CODEX_SEARCH", None)


def test_dispatch_codex_review_always_includes_search():
    """dispatch_codex_review() always includes --search (no use_search arg anymore)."""
    cmd = _capture_cmd("dispatch_codex_review", "test prompt")
    assert "--search" in cmd, f"Expected --search in review cmd, got: {cmd}"
    assert "--dangerously-bypass-approvals-and-sandbox" in cmd, (
        f"Expected danger flag in review cmd, got: {cmd}"
    )


def test_dispatch_codex_patch_always_includes_search():
    """dispatch_codex_patch() always includes --search regardless of KUBEDOJO_CODEX_SEARCH env."""
    import os
    os.environ.pop("KUBEDOJO_CODEX_SEARCH", None)
    cmd = _capture_cmd("dispatch_codex_patch", "test prompt")
    assert "--search" in cmd, f"Expected --search in patch cmd, got: {cmd}"
    assert "--dangerously-bypass-approvals-and-sandbox" in cmd, (
        f"Expected danger flag in patch cmd, got: {cmd}"
    )


def test_codex_bridge_runtime_mode_always_danger():
    """_codex_bridge_runtime_mode() returns 'danger' regardless of CODEX_BRIDGE_MODE env."""
    import importlib.util
    import os

    spec = importlib.util.spec_from_file_location(
        "ai_agent_bridge._codex",
        SCRIPTS_DIR / "ai_agent_bridge" / "_codex.py",
    )
    # Module imports from agent_runtime — guard against import errors in test env.
    try:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    except (ImportError, ModuleNotFoundError):
        pytest.skip("ai_agent_bridge deps not available in this test env")

    for env_val in ("workspace-write", "safe", "full-auto", "danger", None):
        if env_val is None:
            os.environ.pop("CODEX_BRIDGE_MODE", None)
        else:
            os.environ["CODEX_BRIDGE_MODE"] = env_val
        result = mod._codex_bridge_runtime_mode()  # type: ignore[attr-defined]
        assert result == "danger", (
            f"Expected 'danger' for CODEX_BRIDGE_MODE={env_val!r}, got {result!r}"
        )
    os.environ.pop("CODEX_BRIDGE_MODE", None)
