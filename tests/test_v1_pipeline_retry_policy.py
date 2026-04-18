from __future__ import annotations

import argparse
import builtins
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import v1_pipeline

builtins.print = v1_pipeline._original_print


def _write_section(tmp_path: Path) -> tuple[Path, list[Path]]:
    docs_root = tmp_path / "docs"
    section_path = docs_root / "test-track" / "part1"
    section_path.mkdir(parents=True, exist_ok=True)
    modules = [
        section_path / "module-1.1-one.md",
        section_path / "module-1.2-two.md",
    ]
    for module_path in modules:
        module_path.write_text("# Test module\n", encoding="utf-8")
    return docs_root, modules


def _run_section_args(*, workers: int) -> argparse.Namespace:
    return argparse.Namespace(
        section="test-track/part1",
        track="test",
        skip_gaps=True,
        write_model=None,
        review_model=None,
        workers=workers,
        dry_run=False,
        write_only=False,
        refresh_fact_ledger=False,
        verbose=True,
    )


def test_run_section_serial_uses_shared_retry_cap(tmp_path, monkeypatch):
    docs_root, modules = _write_section(tmp_path)
    observed: list[int | None] = []

    def fake_run_module(module_path: Path, state: dict, max_retries: int | None = None, **kwargs) -> bool:
        assert module_path in modules
        observed.append(max_retries)
        return True

    monkeypatch.setattr(v1_pipeline, "CONTENT_ROOT", docs_root)
    monkeypatch.setattr(v1_pipeline, "load_state", lambda: {"modules": {}})
    monkeypatch.setattr(v1_pipeline.gaps, "run_track_gap_analysis", lambda *args, **kwargs: [])
    monkeypatch.setattr(v1_pipeline, "run_module", fake_run_module)

    with pytest.raises(SystemExit) as exc:
        v1_pipeline.cmd_run_section(_run_section_args(workers=1))

    assert exc.value.code == 0
    assert observed == [v1_pipeline.MAX_RETRIES, v1_pipeline.MAX_RETRIES]


def test_run_section_parallel_uses_shared_retry_cap(tmp_path, monkeypatch):
    docs_root, modules = _write_section(tmp_path)
    observed: list[int | None] = []

    def fake_run_module(module_path: Path, state: dict, max_retries: int | None = None, **kwargs) -> bool:
        assert module_path in modules
        observed.append(max_retries)
        return True

    monkeypatch.setattr(v1_pipeline, "CONTENT_ROOT", docs_root)
    monkeypatch.setattr(v1_pipeline, "load_state", lambda: {"modules": {}})
    monkeypatch.setattr(v1_pipeline.gaps, "run_track_gap_analysis", lambda *args, **kwargs: [])
    monkeypatch.setattr(v1_pipeline, "run_module", fake_run_module)

    with pytest.raises(SystemExit) as exc:
        v1_pipeline.cmd_run_section(_run_section_args(workers=2))

    assert exc.value.code == 0
    assert sorted(observed) == [v1_pipeline.MAX_RETRIES, v1_pipeline.MAX_RETRIES]


def test_reset_stuck_recovers_rejection_below_shared_retry_cap(tmp_path, monkeypatch):
    docs_root, modules = _write_section(tmp_path)
    module_path = modules[0]
    module_key = "test-track/part1/module-1.1-one"
    rejection_count = v1_pipeline.MAX_RETRIES - 1
    state = {
        "modules": {
            module_key: {
                "phase": "write",
                "errors": [f"Review rejected {rejection_count} times"],
            }
        }
    }
    save_state = Mock()

    monkeypatch.setattr(v1_pipeline, "CONTENT_ROOT", docs_root)
    monkeypatch.setattr(v1_pipeline, "load_state", lambda: state)
    monkeypatch.setattr(v1_pipeline, "save_state", save_state)
    monkeypatch.setattr(v1_pipeline, "find_module_path", lambda key: module_path if key == module_key else None)
    monkeypatch.setattr(v1_pipeline, "append_review_audit", lambda *args, **kwargs: tmp_path / "reset-audit.json")
    monkeypatch.setattr(
        v1_pipeline,
        "_git_stage_and_commit",
        lambda *args, **kwargs: (
            SimpleNamespace(returncode=0, stderr=""),
            SimpleNamespace(returncode=0, stderr=""),
        ),
    )

    v1_pipeline.cmd_reset_stuck(argparse.Namespace())

    assert state["modules"][module_key]["phase"] == "pending"
    assert state["modules"][module_key]["errors"] == []
    save_state.assert_called_once_with(state)
