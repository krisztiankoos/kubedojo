from __future__ import annotations

import importlib
import importlib.util
import sqlite3
import sys
from pathlib import Path


def _load_local_api():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "local_api.py"
    spec = importlib.util.spec_from_file_location("local_api_channel_summary_fallback", module_path)
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


def test_summary_empty_or_all_null_votes_falls_back_to_chat_banner(
    tmp_path: Path,
    monkeypatch,
) -> None:
    db_path = tmp_path / ".bridge" / "messages.db"
    _use_bridge_db(monkeypatch, db_path)
    _init_db(db_path)
    thread_id = "thread-no-votes"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO channel_messages (
                message_id, channel, thread_id, round_index, from_agent,
                from_model, kind, body, created_at
            )
            VALUES (
                'm1', 'deliberation', ?, 1, 'claude',
                'claude-opus-4-7', 'reply', 'No structured vote yet.',
                '2026-05-07T10:01:00+00:00'
            )
            """,
            (thread_id,),
        )
    finally:
        conn.commit()
        conn.close()

    status, payload, _ = local_api.route_request(
        tmp_path,
        f"/api/channel/{thread_id}/summary",
    )
    assert status == 200
    assert payload["status"] == "in_flight"
    assert payload["rounds"][0]["turns"][0]["vote"] is None

    status, empty_payload, _ = local_api.route_request(
        tmp_path,
        "/api/channel/empty-thread/summary",
    )
    assert status == 200
    assert empty_payload["rounds"] == []
    assert empty_payload["status"] == "in_flight"

    status, body, content_type = local_api.route_request(
        tmp_path,
        f"/channels/{thread_id}?view=graph",
    )
    assert status == 200
    assert "text/html" in content_type
    assert "This thread has no structured votes" in body
    assert 'data-view-toggle="chat">Chat</button>' in body
    assert "function defaultViewForSummary(summary)" in body
    assert 'summary.status==="converged"||summary.decision_id' in body
