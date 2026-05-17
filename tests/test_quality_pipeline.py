"""Regression tests for quality pipeline bugfixes #1281-#1284."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from scripts.quality import pipeline, run_388_batch, stages


def test_cmd_cleanup_banners_releases_state_lease_before_cleanup(monkeypatch, capsys: pytest.CaptureFixture):
    in_lease = {"open": False}
    state = {
        "stage": "COMMITTED",
        "queue": {"completed_at": None},
        "module_path": "src/content/docs/platform/module-1.9-foo.md",
        "history": [],
    }
    calls: list[bool] = []

    class _Lease:
        def __enter__(self):
            in_lease["open"] = True
            return self

        def __exit__(self, exc_type, exc, tb):
            in_lease["open"] = False

        def load(self):
            return state

    def fake_state_lease(slug: str, timeout: float = 5):
        assert slug == "platform-module-1.9-foo"
        return _Lease()

    def fake_clear_banner_and_complete_queue(*_args, **_kwargs):
        calls.append(in_lease["open"])
        raise RuntimeError("cleanup failure")

    monkeypatch.setattr(pipeline.state, "state_lease", fake_state_lease)
    monkeypatch.setattr(pipeline, "iter_all_modules", lambda: [Path("src/content/docs/platform/module-1.9-foo.md")])
    monkeypatch.setattr(pipeline.state, "slug_for", lambda _p: "platform-module-1.9-foo")
    monkeypatch.setattr(stages, "_clear_banner_and_complete_queue", fake_clear_banner_and_complete_queue)

    rc = pipeline.cmd_cleanup_banners(argparse.Namespace(only=None))
    out = capsys.readouterr().out

    assert rc == 1
    assert calls == [False]
    assert "Fixed: 0, Failed: 1" in out
    assert "Failed to clean banner for platform-module-1.9-foo" in out


def test_run_388_batch_normalizes_lease_module_keys(monkeypatch):
    payload = {
        "active": [
            {"path": "src/content/docs/platform/module-1.9-foo.md"},
            {"module_key": "/platform/module-1.9-bar"},
            {"module_path": "k8s/module-1.9-baz.md"},
        ],
    }
    monkeypatch.setattr(run_388_batch, "api_get", lambda _path: payload)
    leases = run_388_batch.fetch_active_leases()
    assert leases == {
        "platform/module-1.9-foo",
        "platform/module-1.9-bar",
        "k8s/module-1.9-baz",
    }

    plan = {
        "tracks": [
            {
                "track": "platform",
                "modules": [
                    {"path": "platform/module-1.9-foo.md"},
                    {"path": "platform/module-1.9-bar.md"},
                ],
            }
        ]
    }
    selected, reasons = run_388_batch.select_modules("platform", plan, {}, leases, {})
    assert selected == []
    assert "  skip [leased]    platform/module-1.9-foo.md" in reasons[0]
    assert "  skip [leased]    platform/module-1.9-bar.md" in reasons[1]


def test_commit_ledger_row_restores_staged_and_worktree_on_commit_error(monkeypatch, tmp_path: Path):
    calls: list[list[str]] = []
    ledger = tmp_path / "docs" / "quality-progress.tsv"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text("slug\tscore\n")

    class _Completed:
        def __init__(self, returncode: int):
            self.returncode = returncode

    def fake_run(cmd, *args, **kwargs):
        calls.append(list(cmd))
        if cmd[:3] == ["git", "diff", "--quiet"]:
            return _Completed(1)
        if cmd[:2] == ["git", "add"]:
            return _Completed(0)
        if cmd[:2] == ["git", "commit"]:
            raise subprocess.CalledProcessError(1, cmd)
        if cmd[:2] == ["git", "restore"]:
            return _Completed(0)
        raise AssertionError(f"unexpected command: {cmd}")

    monkeypatch.setattr(stages, "_primary", lambda: tmp_path)
    monkeypatch.setattr(stages.subprocess, "run", fake_run)

    with pytest.raises(subprocess.CalledProcessError):
        stages._commit_ledger_row("platform-module-1")

    assert ["git", "restore", "--staged", "docs/quality-progress.tsv"] in calls
    assert ["git", "restore", "docs/quality-progress.tsv"] in calls


def test_process_batch_and_cmd_route_audit_map_dispatcher_abort_to_exit_code_3(monkeypatch):
    monkeypatch.setattr(
        pipeline,
        "iter_states",
        lambda only=None: [{"slug": "platform-module-1.9-foo", "stage": "UNAUDITED"}],
    )

    def _fail(_slug: str) -> None:
        raise pipeline.DispatcherUnavailable("dispatcher temporarily unavailable")

    ok, fail, aborted = pipeline._process_batch({"UNAUDITED"}, _fail, limit=None, only=None)
    assert ok == 0
    assert fail == 0
    assert aborted is True

    monkeypatch.setattr(pipeline.stages, "audit_one", _fail)
    assert pipeline.cmd_audit(argparse.Namespace(limit=None, only=None)) == 3

    monkeypatch.setattr(pipeline.stages, "route_one", _fail)
    monkeypatch.setattr(
        pipeline,
        "iter_states",
        lambda only=None: [{"slug": "platform-module-1.9-foo", "stage": "AUDITED"}],
    )
    assert pipeline.cmd_route(argparse.Namespace(limit=None, only=None)) == 3
