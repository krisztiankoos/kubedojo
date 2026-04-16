from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from unittest.mock import Mock

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from pipeline_v2.control_plane import ControlPlane
from pipeline_v2.review_worker import REVIEW_MODEL
from pipeline_v2.write_worker import WRITE_MODEL, WriteWorker


STUB_MODULE = """---
title: Write Worker Test
slug: /write-worker-test
sidebar:
  order: 1
learning_outcomes:
  - Explain write worker behavior.
  - Distinguish initial writes from rewrites.
---

# Write Worker Test

TODO: replace this stub with real content.
"""

REWRITE_SOURCE = """---
title: Rewrite Worker Test
slug: /rewrite-worker-test
sidebar:
  order: 1
learning_outcomes:
  - Preserve valid content.
  - Repair severe review failures.
---

# Rewrite Worker Test

## Learning Outcomes

- Preserve valid content.
- Repair severe review failures.

## Content

This paragraph has useful context that must be preserved in a rewrite plan.
"""

FINAL_DRAFT = """---
title: Final Draft
slug: /final-draft
sidebar:
  order: 1
---

# Final Draft

## Learning Outcomes

- Explain write worker behavior in production.
- Distinguish initial writes from severe rewrites.

## Content

This final draft is intentionally long enough to look like a real module for the worker tests.
It replaces the stub text with complete teaching content and preserves the expected markdown layout.
"""


def _write_budgets(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            {
                "models": {
                    WRITE_MODEL: {
                        "max_concurrent": 2,
                        "weekly_calls": 200,
                        "hourly_calls": 50,
                        "weekly_budget_usd": 40.0,
                        "cooldown_after_rate_limit": 300,
                    },
                    REVIEW_MODEL: {
                        "max_concurrent": 2,
                        "weekly_calls": 200,
                        "hourly_calls": 50,
                        "weekly_budget_usd": 40.0,
                        "cooldown_after_rate_limit": 300,
                    }
                },
                "defaults": {
                    "max_concurrent": 1,
                    "weekly_calls": 25,
                    "hourly_calls": 10,
                    "weekly_budget_usd": 5.0,
                    "cooldown_after_rate_limit": 300,
                    "weekly_window": "rolling_7d",
                },
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def _make_control_plane(tmp_path: Path) -> ControlPlane:
    budgets_path = tmp_path / ".pipeline" / "budgets.yaml"
    db_path = tmp_path / ".pipeline" / "v2.db"
    _write_budgets(budgets_path)
    return ControlPlane(repo_root=tmp_path, db_path=db_path, budgets_path=budgets_path)


def _write_module(tmp_path: Path, content: str, name: str = "docs/module-1.1-write-worker.md") -> Path:
    module_path = tmp_path / name
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text(content, encoding="utf-8")
    return module_path


def _fetch_rows(db_path: Path, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def test_initial_write_of_stub_module_enqueues_review(tmp_path):
    control_plane = _make_control_plane(tmp_path)
    module_path = _write_module(tmp_path, STUB_MODULE)
    module_key = str(module_path.relative_to(tmp_path))
    control_plane.enqueue(module_key, phase="write", model=WRITE_MODEL)
    write_fn = Mock(return_value=FINAL_DRAFT)
    worker = WriteWorker(control_plane, write_fn=write_fn)

    outcome = worker.run_once()

    assert outcome.status == "written"
    assert module_path.read_text(encoding="utf-8") == FINAL_DRAFT
    queued_review = _fetch_rows(
        control_plane.db_path,
        "SELECT phase, model, queue_state FROM jobs WHERE phase = 'review' AND queue_state = 'pending'",
    )
    assert len(queued_review) == 1
    assert queued_review[0]["model"] == REVIEW_MODEL
    assert write_fn.call_args.kwargs["rewrite"] is False


def test_severe_rewrite_preserves_existing_content_in_prompt_context(tmp_path):
    control_plane = _make_control_plane(tmp_path)
    module_path = _write_module(tmp_path, REWRITE_SOURCE)
    module_key = str(module_path.relative_to(tmp_path))
    control_plane.emit_event(
        "check_failed",
        module_key=module_key,
        payload={
            "verdict": "REJECT",
            "failed_checks": [{"id": "DEPTH", "passed": False, "evidence": "depth gap"}],
            "feedback": "Needs a severe rewrite.",
        },
    )
    control_plane.emit_event(
        "rewrite_escalated",
        module_key=module_key,
        payload={
            "failed_checks": [{"id": "DEPTH", "passed": False, "evidence": "depth gap"}],
            "feedback": "Severe rewrite required.",
            "reasons": ["integrity_failure"],
        },
    )
    control_plane.enqueue(module_key, phase="write", model=WRITE_MODEL)
    write_fn = Mock(return_value=FINAL_DRAFT)
    worker = WriteWorker(control_plane, write_fn=write_fn)

    outcome = worker.run_once()

    assert outcome.status == "written"
    assert write_fn.call_args.kwargs["rewrite"] is True
    assert write_fn.call_args.kwargs["previous_output"] == REWRITE_SOURCE
    assert "Failure history" in write_fn.call_args.args[1]
    assert "integrity_failure" in write_fn.call_args.args[1]


def test_empty_module_file_uses_initial_write_plan(tmp_path):
    control_plane = _make_control_plane(tmp_path)
    module_path = _write_module(tmp_path, "", name="docs/module-1.2-empty.md")
    module_key = str(module_path.relative_to(tmp_path))
    control_plane.enqueue(module_key, phase="write", model=WRITE_MODEL)
    write_fn = Mock(return_value=FINAL_DRAFT)
    worker = WriteWorker(control_plane, write_fn=write_fn)

    outcome = worker.run_once()

    assert outcome.status == "written"
    assert write_fn.call_args.kwargs["rewrite"] is False
    assert "Initial module write" in write_fn.call_args.args[1]
    assert "(empty module body)" in write_fn.call_args.args[1]


def test_write_failure_releases_lease_for_retry(tmp_path):
    control_plane = _make_control_plane(tmp_path)
    module_path = _write_module(tmp_path, STUB_MODULE, name="docs/module-1.3-retry.md")
    module_key = str(module_path.relative_to(tmp_path))
    control_plane.enqueue(module_key, phase="write", model=WRITE_MODEL)
    worker = WriteWorker(control_plane, write_fn=Mock(return_value=None))

    outcome = worker.run_once()

    assert outcome.status == "retry_scheduled"
    assert control_plane.fetch_value(
        "SELECT queue_state FROM jobs WHERE module_key = ? ORDER BY id ASC LIMIT 1",
        (module_key,),
    ) == "pending"
    released = control_plane.iter_events("job_released")[-1]
    payload = json.loads(released["payload_json"])
    assert payload["reason"] == "write_failed"
    assert control_plane.fetch_value(
        "SELECT COUNT(*) FROM jobs WHERE phase = 'review'",
    ) == 0
