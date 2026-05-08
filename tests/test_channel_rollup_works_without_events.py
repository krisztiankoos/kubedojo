from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


def _load_local_api():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "local_api.py"
    spec = importlib.util.spec_from_file_location(
        "local_api_channel_rollup_without_events",
        module_path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


local_api = _load_local_api()


def test_channel_rollup_works_without_events(tmp_path: Path, monkeypatch) -> None:
    import ai_agent_bridge._db as bridge_db

    db_path = tmp_path / "messages.db"
    monkeypatch.setenv("AB_DB_PATH", str(db_path))
    monkeypatch.setattr(bridge_db, "DB_PATH", db_path)
    bridge_db.init_db().close()

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO channels (name, created_at, description)
            VALUES ('pipeline', '2026-05-07T12:00:00+00:00', 'Pipeline')
            """
        )
        conn.execute(
            """
            INSERT INTO channel_messages (
                message_id, channel, thread_id, round_index, from_agent, kind, body, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "m-root",
                "pipeline",
                "thread-1",
                0,
                "user",
                "post",
                "This is the thread subject that should be exposed without events.",
                "2026-05-07T12:01:00+00:00",
            ),
        )
        conn.execute(
            """
            INSERT INTO channel_messages (
                message_id, channel, thread_id, parent_id, round_index,
                from_agent, kind, body, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "m-reply",
                "pipeline",
                "thread-1",
                "m-root",
                1,
                "codex",
                "reply",
                "Reply body",
                "2026-05-07T12:03:00+00:00",
            ),
        )
        conn.commit()
    finally:
        conn.close()

    status_code, payload, _ = local_api.route_request(tmp_path, "/api/channels")

    assert status_code == 200
    channels = {channel["name"]: channel for channel in payload["channels"]}
    assert len(channels["pipeline"]["threads"]) == 1
    thread = channels["pipeline"]["threads"][0]
    assert thread["thread_id"] == "thread-1"
    assert thread["subject"] == (
        "This is the thread subject that should be exposed without events."
    )
    assert thread["thread_started_at"] == "2026-05-07T12:01:00+00:00"
    assert thread["thread_last_at"] == "2026-05-07T12:03:00+00:00"
    assert thread["message_count"] == 2
    assert thread["event_count"] == 0
