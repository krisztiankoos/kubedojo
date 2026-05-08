from __future__ import annotations

import importlib
import importlib.util
import sqlite3
import sys
from pathlib import Path


def _load_local_api():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "local_api.py"
    spec = importlib.util.spec_from_file_location("local_api_channel_summary_rounds", module_path)
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


def _insert_message(
    db_path: Path,
    message_id: str,
    *,
    thread_id: str,
    round_index: int,
    from_agent: str,
    body: str,
    created_at: str,
) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO channel_messages (
                message_id, channel, thread_id, round_index, from_agent,
                from_model, kind, body, created_at
            )
            VALUES (?, 'deliberation', ?, ?, ?, 'model-x', 'reply', ?, ?)
            """,
            (message_id, thread_id, round_index, from_agent, body, created_at),
        )
    finally:
        conn.commit()
        conn.close()


def test_summary_groups_messages_by_round_index_and_created_at(
    tmp_path: Path,
    monkeypatch,
) -> None:
    db_path = tmp_path / ".bridge" / "messages.db"
    _use_bridge_db(monkeypatch, db_path)
    _init_db(db_path)
    thread_id = "thread-rounds"

    _insert_message(
        db_path,
        "m0",
        thread_id=thread_id,
        round_index=0,
        from_agent="user",
        body="Should we pick option A or B?",
        created_at="2026-05-07T10:00:00+00:00",
    )
    _insert_message(
        db_path,
        "m2",
        thread_id=thread_id,
        round_index=1,
        from_agent="codex",
        body="Later turn [OPTION B]",
        created_at="2026-05-07T10:02:00+00:00",
    )
    _insert_message(
        db_path,
        "m1",
        thread_id=thread_id,
        round_index=1,
        from_agent="claude",
        body="Earlier turn [OPTION A]",
        created_at="2026-05-07T10:01:00+00:00",
    )
    _insert_message(
        db_path,
        "m3",
        thread_id=thread_id,
        round_index=2,
        from_agent="gemini",
        body="Final turn [AGREE]",
        created_at="2026-05-07T10:03:00+00:00",
    )

    status, payload, _ = local_api.route_request(
        tmp_path,
        f"/api/channel/{thread_id}/summary",
    )

    assert status == 200
    assert payload["subject"] == "Should we pick option A or B?"
    assert [round_["round_idx"] for round_ in payload["rounds"]] == [1, 2]
    assert [turn["agent"] for turn in payload["rounds"][0]["turns"]] == [
        "claude",
        "codex",
    ]
    assert payload["rounds"][0]["turns"][0]["message_id"] == "m1"
