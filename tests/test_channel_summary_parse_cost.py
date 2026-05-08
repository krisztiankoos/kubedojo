from __future__ import annotations

import importlib
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path


def _load_local_api():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "local_api.py"
    spec = importlib.util.spec_from_file_location("local_api_channel_summary_cost", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


local_api = _load_local_api()


def _use_bridge_db(monkeypatch, db_path: Path) -> None:
    bridge_db = importlib.import_module("ai_agent_bridge._db")
    monkeypatch.setenv("AB_DB_PATH", str(db_path))
    monkeypatch.setattr(bridge_db, "DB_PATH", db_path)


def _init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(
            """
            CREATE TABLE channel_messages (
                message_id TEXT PRIMARY KEY,
                channel TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                parent_id TEXT,
                correlation_id TEXT,
                round_index INTEGER DEFAULT 0,
                from_agent TEXT NOT NULL,
                from_model TEXT,
                kind TEXT DEFAULT 'post',
                body TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE channel_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                delivery_id TEXT,
                thread_id TEXT NOT NULL,
                event TEXT NOT NULL,
                payload_json TEXT,
                ts TEXT NOT NULL
            );
            """
        )
    finally:
        conn.commit()
        conn.close()


def test_summary_aggregates_model_cascade_cost_and_defaults_missing(
    tmp_path: Path,
    monkeypatch,
) -> None:
    db_path = tmp_path / ".bridge" / "messages.db"
    _use_bridge_db(monkeypatch, db_path)
    _init_db(db_path)
    thread_id = "thread-cost"
    conn = sqlite3.connect(db_path)
    try:
        conn.executemany(
            """
            INSERT INTO channel_messages (
                message_id, channel, thread_id, round_index, from_agent,
                from_model, kind, body, created_at
            )
            VALUES (?, 'deliberation', ?, 1, ?, 'model-x', 'reply', ?, ?)
            """,
            [
                ("m1", thread_id, "claude", "First [OPTION A]", "2026-05-07T10:01:00+00:00"),
                ("m2", thread_id, "codex", "Second [OPTION B]", "2026-05-07T10:02:00+00:00"),
            ],
        )
        conn.executemany(
            """
            INSERT INTO channel_events (thread_id, event, payload_json, ts)
            VALUES (?, 'model_cascade', ?, ?)
            """,
            [
                (
                    thread_id,
                    json.dumps({"message_id": "m1", "cost_usd": 0.03, "elapsed_s": 10}),
                    "2026-05-07T10:01:10+00:00",
                ),
                (
                    thread_id,
                    json.dumps({"message_id": "m1", "cost_usd": 0.02, "elapsed_s": 5}),
                    "2026-05-07T10:01:15+00:00",
                ),
            ],
        )
    finally:
        conn.commit()
        conn.close()

    status, payload, _ = local_api.route_request(
        tmp_path,
        f"/api/channel/{thread_id}/summary",
    )

    assert status == 200
    turns = payload["rounds"][0]["turns"]
    assert turns[0]["cost_usd"] == 0.05
    assert turns[0]["elapsed_s"] == 15
    assert turns[1]["cost_usd"] == 0
    assert turns[1]["elapsed_s"] == 0
    assert payload["rounds"][0]["cost_usd"] == 0.05
    assert payload["total_cost_usd"] == 0.05
    assert payload["total_elapsed_s"] == 15
