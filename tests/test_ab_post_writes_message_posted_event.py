from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from ai_agent_bridge import _channels, _cli, _db


@pytest.fixture(autouse=True)
def isolate_db(tmp_path):
    db_file = tmp_path / "messages.db"
    with patch("ai_agent_bridge._config.DB_PATH", db_file), \
         patch("ai_agent_bridge._db.DB_PATH", db_file):
        _db.init_db().close()
        yield db_file


def _run_cli(argv: list[str]) -> int:
    with patch.object(sys, "argv", ["ab", *argv]):
        try:
            _cli.main()
        except SystemExit as exc:
            return exc.code if isinstance(exc.code, int) else 0
    return 0


def test_ab_post_writes_message_posted_event(isolate_db: Path, capsys) -> None:
    _channels.create_channel("pipeline")

    exit_code = _run_cli(
        ["post", "pipeline", "hello from ab post", "--no-snapshot"]
    )

    assert exit_code == 0
    assert "posted to #pipeline" in capsys.readouterr().out

    conn = sqlite3.connect(isolate_db)
    conn.row_factory = sqlite3.Row
    try:
        message = conn.execute(
            """
            SELECT message_id, thread_id, from_agent, round_index
            FROM channel_messages
            WHERE channel = 'pipeline'
            """
        ).fetchone()
        assert message is not None
        events = conn.execute(
            """
            SELECT thread_id, event, payload_json, ts
            FROM channel_events
            WHERE thread_id = ? AND event = 'message_posted'
            """,
            (message["thread_id"],),
        ).fetchall()
    finally:
        conn.close()

    assert len(events) == 1
    event = events[0]
    assert event["thread_id"] == message["thread_id"]
    payload = json.loads(event["payload_json"])
    assert payload == {
        "message_id": message["message_id"],
        "from_agent": message["from_agent"],
        "round_index": message["round_index"],
    }


def test_channel_backfill_events_is_idempotent(isolate_db: Path, capsys) -> None:
    _channels.create_channel("pipeline")
    conn = sqlite3.connect(isolate_db)
    try:
        conn.execute(
            """
            INSERT INTO channel_messages (
                message_id, channel, thread_id, round_index, from_agent, kind, body, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "legacy-message",
                "pipeline",
                "legacy-thread",
                0,
                "user",
                "post",
                "historical post",
                "2026-05-07T12:00:00+00:00",
            ),
        )
        conn.commit()
    finally:
        conn.close()

    assert _run_cli(["channel", "backfill-events"]) == 0
    assert "inserted 1 message_posted" in capsys.readouterr().out
    assert _run_cli(["channel", "backfill-events"]) == 0
    assert "inserted 0 message_posted" in capsys.readouterr().out

    conn = sqlite3.connect(isolate_db)
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM channel_events WHERE event = 'message_posted'"
        ).fetchone()[0]
    finally:
        conn.close()

    assert count == 1


def test_message_posted_unique_index_blocks_duplicate_payload(
    isolate_db: Path,
) -> None:
    conn = sqlite3.connect(isolate_db)
    payload = json.dumps({"message_id": "dup-message"}, sort_keys=True)
    try:
        conn.execute(
            """
            INSERT INTO channel_events (delivery_id, thread_id, event, payload_json, ts)
            VALUES (?, ?, ?, ?, ?)
            """,
            (None, "thread-a", "message_posted", payload, "2026-05-07T12:00:00+00:00"),
        )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO channel_events (delivery_id, thread_id, event, payload_json, ts)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    None,
                    "thread-b",
                    "message_posted",
                    payload,
                    "2026-05-07T12:01:00+00:00",
                ),
            )
    finally:
        conn.close()
