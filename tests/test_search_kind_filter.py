from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from ai_agent_bridge import _channels, _config, _db
from local_api.routes import decisions, search as search_route


def _seed_search_corpus(repo_root: Path, db_path: Path) -> None:
    decisions_dir = repo_root / "docs" / "decisions"
    decisions_dir.mkdir(parents=True)
    (decisions_dir / "choice.md").write_text(
        "# Searchable Decision\n\nfiltertoken in decision body\n",
        encoding="utf-8",
    )
    decisions._DECISIONS_FTS_META.clear()

    with patch.object(_config, "DB_PATH", db_path), patch.object(_db, "DB_PATH", db_path):
        conn = _db.init_db()
        conn.close()
        _channels.create_channel("filter-channel")
        _channels.post(
            "filter-channel",
            "gemini",
            "filtertoken in channel body",
            auto_snapshot=False,
        )


def test_search_kind_filters_channels_decisions_and_all(tmp_path: Path) -> None:
    db_path = tmp_path / "messages.db"
    _seed_search_corpus(tmp_path, db_path)

    status, payload, _ = search_route.route_search_request(
        tmp_path,
        "/api/search",
        {"q": ["filtertoken"], "kind": ["channels"]},
        bridge_db_path=db_path,
    )
    assert status == 200
    assert {item["kind"] for item in payload["results"]} == {"channel"}

    status, payload, _ = search_route.route_search_request(
        tmp_path,
        "/api/search",
        {"q": ["filtertoken"], "kind": ["decisions"]},
        bridge_db_path=db_path,
    )
    assert status == 200
    assert {item["kind"] for item in payload["results"]} == {"decision"}

    status, payload, _ = search_route.route_search_request(
        tmp_path,
        "/api/search",
        {"q": ["filtertoken"], "kind": ["all"]},
        bridge_db_path=db_path,
    )
    assert status == 200
    assert {item["kind"] for item in payload["results"]} == {"channel", "decision"}

    status, payload, _ = search_route.route_search_request(
        tmp_path,
        "/api/search",
        {"q": ["filtertoken"], "kind": ["garbage"]},
        bridge_db_path=db_path,
    )
    assert status == 400
    assert payload["error"] == "invalid kind"
