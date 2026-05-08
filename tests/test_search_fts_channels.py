from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from ai_agent_bridge import _channels, _config, _db
from local_api.routes import search as search_route


def _init_bridge_db(db_path: Path) -> None:
    with patch.object(_config, "DB_PATH", db_path), patch.object(_db, "DB_PATH", db_path):
        conn = _db.init_db()
        conn.close()


def test_channel_messages_fts_triggers_insert_and_rank_results(tmp_path: Path) -> None:
    db_path = tmp_path / "messages.db"
    _init_bridge_db(db_path)

    with patch.object(_config, "DB_PATH", db_path), patch.object(_db, "DB_PATH", db_path):
        _channels.create_channel("search-topic")
        weaker = _channels.post(
            "search-topic",
            "claude",
            "needle appears once",
            auto_snapshot=False,
        )
        stronger = _channels.post(
            "search-topic",
            "codex",
            "needle needle needle appears more often",
            auto_snapshot=False,
        )

        conn = _db.get_db()
        try:
            unique_token = "uniquetokenfts"
            conn.execute(
                """
                INSERT INTO channel_messages(
                    message_id, channel, thread_id, round_index,
                    from_agent, body, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "directftsmessage",
                    "search-topic",
                    "directftsthread",
                    0,
                    "user",
                    f"direct insert {unique_token}",
                    "2026-01-01T00:00:00+00:00",
                ),
            )
            conn.commit()
            rows = conn.execute(
                "SELECT message_id FROM channel_messages_fts WHERE channel_messages_fts MATCH ?",
                (f'"{unique_token}"',),
            ).fetchall()
            assert [row["message_id"] for row in rows] == ["directftsmessage"]
        finally:
            conn.close()

    status, payload, _ = search_route.build_search_payload(
        tmp_path,
        {"q": ["needle"], "kind": ["channels"], "limit": ["10"]},
        bridge_db_path=db_path,
    )
    assert status == 200
    result_ids = [item["message_id"] for item in payload["results"]]
    assert result_ids.index(stronger["message_id"]) < result_ids.index(weaker["message_id"])
    assert payload["results"][0]["rank"] <= payload["results"][1]["rank"]
