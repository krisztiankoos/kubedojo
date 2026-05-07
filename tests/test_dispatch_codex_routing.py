from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from dispatch import dispatch_codex_patch, dispatch_codex_review


def _completed_process(cmd: list[str], *, stdout: str = "ok", stderr: str = ""):
    return subprocess.CompletedProcess(cmd, 0, stdout=stdout, stderr=stderr)


def test_dispatch_codex_review_always_search_and_danger():
    """Review always includes --search and danger sandbox.

    --search is unconditional; use_search arg was removed in this PR.
    Danger mode is mandatory — read-only starved Codex of network/filesystem
    and caused rc=-9 stale-rollout salvage (three failures 2026-05-07).
    """
    with patch(
        "dispatch._run_with_process_group",
        return_value=_completed_process(["codex"]),
    ) as run_mock, patch("dispatch._log"):
        ok, output = dispatch_codex_review("review prompt", model="gpt-5.3-codex-spark", timeout=123)

    assert ok is True
    assert output == "ok"
    cmd = run_mock.call_args.args[0]
    assert Path(cmd[0]).name == "codex"
    assert "--search" in cmd
    assert cmd.index("--search") < cmd.index("exec")
    assert "exec" in cmd
    assert "--dangerously-bypass-approvals-and-sandbox" in cmd
    assert "--sandbox" not in cmd
    assert "read-only" not in cmd


def test_dispatch_codex_patch_runs_danger_sandbox_with_search():
    """Patch runs in danger mode with --search — Codex needs network to verify facts.

    read-only starved Codex of network/filesystem and caused rc=-9 stale-rollout
    salvage — three failures in a single session 2026-05-07.
    """
    with patch(
        "dispatch._run_with_process_group",
        return_value=_completed_process(["codex"]),
    ) as run_mock, patch("dispatch._log"):
        ok, output = dispatch_codex_patch("patch prompt", model="gpt-5.4", timeout=456)

    assert ok is True
    assert output == "ok"
    cmd = run_mock.call_args.args[0]
    assert Path(cmd[0]).name == "codex"
    assert "--search" in cmd
    assert cmd.index("--search") < cmd.index("exec")
    assert "--dangerously-bypass-approvals-and-sandbox" in cmd
    assert "--sandbox" not in cmd
    assert "read-only" not in cmd
