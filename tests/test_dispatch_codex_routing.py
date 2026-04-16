from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from dispatch import dispatch_codex_patch, dispatch_codex_review


def _completed_process(cmd: list[str], *, stdout: str = "ok", stderr: str = ""):
    return subprocess.CompletedProcess(cmd, 0, stdout=stdout, stderr=stderr)


def test_dispatch_codex_review_defaults_to_no_search_and_read_only():
    """Review defaults to no --search; sandbox always read-only."""
    with patch(
        "dispatch._run_with_process_group",
        return_value=_completed_process(["codex"]),
    ) as run_mock, patch("dispatch._log"):
        ok, output = dispatch_codex_review("review prompt", model="gpt-5.3-codex-spark", timeout=123)

    assert ok is True
    assert output == "ok"
    cmd = run_mock.call_args.args[0]
    assert Path(cmd[0]).name == "codex"
    assert "--search" not in cmd
    assert "exec" in cmd
    assert "--sandbox" in cmd
    assert "read-only" in cmd
    assert "--dangerously-bypass-approvals-and-sandbox" not in cmd


def test_dispatch_codex_review_enables_search_when_requested():
    """FACT_CHECK deep reviews opt in via use_search=True."""
    with patch(
        "dispatch._run_with_process_group",
        return_value=_completed_process(["codex"]),
    ) as run_mock, patch("dispatch._log"):
        ok, output = dispatch_codex_review(
            "review prompt",
            model="gpt-5.3-codex-spark",
            timeout=123,
            use_search=True,
        )

    assert ok is True
    assert output == "ok"
    cmd = run_mock.call_args.args[0]
    assert Path(cmd[0]).name == "codex"
    assert "--search" in cmd
    assert cmd.index("--search") < cmd.index("exec")
    assert "--sandbox" in cmd
    assert "read-only" in cmd


def test_dispatch_codex_patch_runs_read_only_sandbox():
    """Patch applies edits via Python; Codex needs no write/exec privilege."""
    with patch(
        "dispatch._run_with_process_group",
        return_value=_completed_process(["codex"]),
    ) as run_mock, patch("dispatch._log"):
        ok, output = dispatch_codex_patch("patch prompt", model="gpt-5.4", timeout=456)

    assert ok is True
    assert output == "ok"
    cmd = run_mock.call_args.args[0]
    assert Path(cmd[0]).name == "codex"
    assert cmd[1] == "exec"
    assert "--sandbox" in cmd
    assert "read-only" in cmd
    assert "--dangerously-bypass-approvals-and-sandbox" not in cmd
    assert "--search" not in cmd
