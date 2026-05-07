from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path
from typing import Any

import sys


def _load_local_api():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "local_api.py"
    spec = importlib.util.spec_from_file_location("local_api_channels", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


local_api = _load_local_api()


def _init_channel_events_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS channel_events (
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


def _seed_channel_events(db_path: Path, events: list[dict[str, Any]], *, thread_id: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.executemany(
            """
            INSERT INTO channel_events (delivery_id, thread_id, event, payload_json, ts)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    event.get("delivery_id"),
                    thread_id,
                    event["event"],
                    json.dumps(event["payload"]),
                    event["ts"],
                )
                for event in events
            ],
        )
    finally:
        conn.commit()
        conn.close()


def _use_bridge_db(monkeypatch, db_path: Path) -> None:
    import importlib

    bridge_db = importlib.import_module("ai_agent_bridge._db")
    monkeypatch.setenv("AB_DB_PATH", str(db_path))
    monkeypatch.setattr(bridge_db, "DB_PATH", db_path)


def test_api_channels_returns_empty_shape(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "messages.db"
    _use_bridge_db(monkeypatch, db_path)
    status_code, payload, _ = local_api.route_request(tmp_path, "/api/channels")
    assert status_code == 200
    assert payload == {"channels": []}


def test_api_channel_events_returns_events_in_order(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "messages.db"
    _use_bridge_db(monkeypatch, db_path)
    _init_channel_events_db(db_path)
    thread_id = "thread-123"
    _seed_channel_events(
        db_path,
        [
            {
                "event": "reply_started",
                "payload": {"agent": "codex", "model": "gpt-5.5"},
                "ts": "2026-05-07T15:00:00+00:00",
            },
            {
                "event": "heartbeat",
                "payload": {"delivery_id": "d-1", "elapsed_s": 30},
                "ts": "2026-05-07T15:00:30+00:00",
            },
            {
                "event": "model_cascade",
                "payload": {"agent": "gemini", "model": "gpt-5.5"},
                "ts": "2026-05-07T15:01:00+00:00",
            },
        ],
        thread_id=thread_id,
    )
    status_code, payload, _ = local_api.route_request(tmp_path, f"/api/channel/{thread_id}/events")
    assert status_code == 200
    assert payload["thread_id"] == thread_id
    assert payload["events"] == [
        {
            "event_id": 1,
            "event": "reply_started",
            "ts": "2026-05-07T15:00:00+00:00",
            "agent": "codex",
            "model": "gpt-5.5",
        },
        {
            "event_id": 2,
            "event": "heartbeat",
            "ts": "2026-05-07T15:00:30+00:00",
            "delivery_id": "d-1",
            "elapsed_s": 30,
        },
        {
            "event_id": 3,
            "event": "model_cascade",
            "ts": "2026-05-07T15:01:00+00:00",
            "agent": "gemini",
            "model": "gpt-5.5",
        },
    ]
    assert payload["next_since_event_id"] == 3


def test_api_channel_events_since_event_id_filters(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "messages.db"
    _use_bridge_db(monkeypatch, db_path)
    _init_channel_events_db(db_path)
    thread_id = "thread-123"
    _seed_channel_events(
        db_path,
        [
            {
                "event": "reply_started",
                "payload": {"agent": "codex"},
                "ts": "2026-05-07T15:00:00+00:00",
            },
            {
                "event": "heartbeat",
                "payload": {"delivery_id": "d-1"},
                "ts": "2026-05-07T15:00:30+00:00",
            },
            {
                "event": "reply_complete",
                "payload": {"agent": "gemini"},
                "ts": "2026-05-07T15:01:00+00:00",
            },
        ],
        thread_id=thread_id,
    )
    status_code, payload, _ = local_api.route_request(
        tmp_path,
        f"/api/channel/{thread_id}/events?since_event_id=2",
    )
    assert status_code == 200
    assert payload["events"] == [
        {
            "event_id": 3,
            "event": "reply_complete",
            "ts": "2026-05-07T15:01:00+00:00",
            "agent": "gemini",
        }
    ]
    assert payload["next_since_event_id"] == 3
