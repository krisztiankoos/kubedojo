from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from migrate_v1_to_v2 import migrate_v1_to_v2
from pipeline_v2.control_plane import ControlPlane
from pipeline_v2.review_worker import PRO_MODEL


def _write_budgets(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            {
                "models": {
                    PRO_MODEL: {
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


def _write_state(path: Path, modules: dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"modules": modules}, sort_keys=True), encoding="utf-8")


def _resolver(tmp_path: Path):
    def resolve(raw_key: str) -> Path | None:
        candidate = tmp_path / "src" / "content" / "docs" / f"{raw_key}.md"
        candidate.parent.mkdir(parents=True, exist_ok=True)
        if not candidate.exists():
            candidate.write_text("---\ntitle: Test\n---\n", encoding="utf-8")
        return candidate

    return resolve


def _fetch_rows(db_path: Path, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def test_v1_done_module_emits_done_event_and_no_job(tmp_path):
    control_plane = _make_control_plane(tmp_path)
    state_path = tmp_path / ".pipeline" / "state.yaml"
    raw_key = "k8s/cka/module-1.1-done"
    _write_state(state_path, {raw_key: {"phase": "done", "passes": True}})

    summary = migrate_v1_to_v2(
        control_plane,
        state_path=state_path,
        module_resolver=_resolver(tmp_path),
    )

    assert summary.migrated_done == 1
    events = control_plane.iter_events("done")
    assert len(events) == 1
    assert control_plane.fetch_value("SELECT COUNT(*) FROM jobs") == 0


def test_v1_review_module_enqueues_review_job(tmp_path):
    control_plane = _make_control_plane(tmp_path)
    state_path = tmp_path / ".pipeline" / "state.yaml"
    raw_key = "k8s/cka/module-1.2-review"
    _write_state(state_path, {raw_key: {"phase": "review"}})

    summary = migrate_v1_to_v2(
        control_plane,
        state_path=state_path,
        module_resolver=_resolver(tmp_path),
    )

    assert summary.enqueued_review == 1
    queued = _fetch_rows(
        control_plane.db_path,
        "SELECT phase, model, queue_state FROM jobs WHERE phase = 'review'",
    )
    assert len(queued) == 1
    assert queued[0]["queue_state"] == "pending"
    attempt = control_plane.iter_events("attempt_succeeded")[-1]
    payload = json.loads(attempt["payload_json"])
    assert payload["phase"] == "write"


def test_v1_pending_module_enqueues_write_job(tmp_path):
    control_plane = _make_control_plane(tmp_path)
    state_path = tmp_path / ".pipeline" / "state.yaml"
    raw_key = "k8s/cka/module-1.3-pending"
    _write_state(state_path, {raw_key: {"phase": "pending"}})

    summary = migrate_v1_to_v2(
        control_plane,
        state_path=state_path,
        module_resolver=_resolver(tmp_path),
    )

    assert summary.enqueued_write == 1
    queued = _fetch_rows(
        control_plane.db_path,
        "SELECT phase, model, queue_state FROM jobs WHERE phase = 'write'",
    )
    assert len(queued) == 1
    assert queued[0]["queue_state"] == "pending"


def test_v1_data_conflict_marks_needs_human_intervention(tmp_path):
    control_plane = _make_control_plane(tmp_path)
    state_path = tmp_path / ".pipeline" / "state.yaml"
    raw_key = "k8s/cka/module-1.4-conflict"
    _write_state(state_path, {raw_key: {"phase": "data_conflict"}})

    summary = migrate_v1_to_v2(
        control_plane,
        state_path=state_path,
        module_resolver=_resolver(tmp_path),
    )

    assert summary.marked_manual_triage == 1
    failed_jobs = _fetch_rows(
        control_plane.db_path,
        "SELECT phase, queue_state FROM jobs WHERE queue_state = 'failed'",
    )
    assert len(failed_jobs) == 1
    event = control_plane.iter_events("needs_human_intervention")[-1]
    payload = json.loads(event["payload_json"])
    assert payload["reason"] == "data_conflict"


def test_migration_is_idempotent_on_rerun(tmp_path):
    control_plane = _make_control_plane(tmp_path)
    state_path = tmp_path / ".pipeline" / "state.yaml"
    raw_key = "k8s/cka/module-1.5-idempotent"
    _write_state(state_path, {raw_key: {"phase": "review"}})

    first = migrate_v1_to_v2(
        control_plane,
        state_path=state_path,
        module_resolver=_resolver(tmp_path),
    )
    second = migrate_v1_to_v2(
        control_plane,
        state_path=state_path,
        module_resolver=_resolver(tmp_path),
    )

    assert first.enqueued_review == 1
    assert second.skipped_existing == 1
    assert control_plane.fetch_value("SELECT COUNT(*) FROM jobs") == 1
    assert control_plane.fetch_value("SELECT COUNT(*) FROM events WHERE type = 'job_enqueued'") == 1
