"""Tests for dispatch_388 backfill integration."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.quality import dispatch_388_pilot as pilot


def _mock_run(returncode: int, stdout: str = "", stderr: str = ""):
    result = MagicMock()
    result.returncode = returncode
    result.stdout = stdout
    result.stderr = stderr
    return result


def test_dispatch_backfill_happy_path_runs_pipeline_and_push(tmp_path):
    module_path = "src/content/docs/k8s/cka/module-1.md"
    module_slug = pilot.module_slug_for_pipeline(module_path)

    with patch("scripts.quality.dispatch_388_pilot.subprocess.run", side_effect=[
        _mock_run(0, stdout="Already up to date."),
        _mock_run(0, stdout=f"[ok]    {module_slug}: deadbeef12"),
        _mock_run(0, stdout="To github.com:repo.git"),
    ]) as mock_run, patch("scripts.quality.dispatch_388_pilot.log") as mock_log:
        assert pilot.dispatch_backfill("my-slug", module_path)

    events = [c.args[0]["event"] for c in mock_log.call_args_list]
    assert "backfill_start" in events
    assert "backfill_done" in events
    done = next(c.args[0] for c in mock_log.call_args_list if c.args[0]["event"] == "backfill_done")
    assert done["slug"] == "my-slug"
    assert done["sha"] == "deadbeef12"
    assert mock_run.call_args_list[1].args[0] == [
        str(pilot.VENV_PYTHON),
        "-m", "scripts.quality.pipeline", "backfill-pending", "--module", module_slug,
    ]
    assert mock_run.call_args_list[2].args[0] == ["git", "push", "origin", "main"]


def test_dispatch_backfill_backfill_failure_logs_and_continues():
    module_path = "src/content/docs/k8s/cka/module-2.md"
    with patch("scripts.quality.dispatch_388_pilot.subprocess.run", side_effect=[
        _mock_run(0, stdout="Already up to date."),
        _mock_run(1, stderr="pipeline failed"),
    ]) as _, patch("scripts.quality.dispatch_388_pilot.log") as mock_log:
        assert pilot.dispatch_backfill("my-slug", module_path) is False

    events = [c.args[0]["event"] for c in mock_log.call_args_list]
    assert "backfill_failed" in events
    failed = next(c.args[0] for c in mock_log.call_args_list if c.args[0]["event"] == "backfill_failed")
    assert failed["slug"] == "my-slug"
    assert "pipeline failed" in failed["reason"]


def test_main_chain_calls_backfill_after_merge_and_continues_on_failure(tmp_path):
    queue = tmp_path / "queue.txt"
    queue.write_text(
        "\n".join(
            [
                "src/content/docs/k8s/cka/module-1.md",
                "src/content/docs/k8s/cka/module-2.md",
            ]
        )
    )
    codex_result = MagicMock(ok=True, response="Opened PR: https://github.com/org/repo/pull/42")

    with patch("scripts.quality.dispatch_388_pilot.make_worktree", return_value=tmp_path), \
         patch("scripts.quality.dispatch_388_pilot.dispatch_codex", return_value=codex_result), \
         patch("scripts.quality.dispatch_388_pilot.dispatch_gemini_review", return_value=("VERDICT: APPROVE", "APPROVE")), \
         patch("scripts.quality.dispatch_388_pilot.merge_pr", return_value="abc123"), \
         patch("scripts.quality.dispatch_388_pilot.dispatch_backfill", side_effect=[False, True]) as mock_backfill, \
         patch("scripts.quality.dispatch_388_pilot.post_review_comment"), \
         patch("scripts.quality.dispatch_388_pilot.time.sleep"), \
         patch("scripts.quality.dispatch_388_pilot.log") as mock_log:
        rc = pilot.main(["--input", str(queue)])

    assert rc == 0
    assert mock_backfill.call_count == 2
    events = [c.args[0]["event"] for c in mock_log.call_args_list]
    assert events.count("merged") == 2


def test_dispatch_backfill_sha_regex_parses_ok_line():
    output = "\n".join(
        [
            "[no-op] k8s-cka-module-9: already clean",
            "[ok]    k8s-cka-module-8: deadbeef12",
            "[ok]    k8s-cka-module-9: c0ffee99",
        ]
    )
    match = re.search(r"^\[ok\]\s+k8s-cka-module-8:\s+([0-9a-f]+)", output, re.MULTILINE)
    assert match is not None
    assert match.group(1) == "deadbeef12"
