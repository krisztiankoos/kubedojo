from __future__ import annotations

import os
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from local_api.routes import decisions, search as search_route


def test_decisions_fts_indexes_and_refreshes_only_touched_file(tmp_path: Path) -> None:
    db_path = tmp_path / "messages.db"
    decisions_dir = tmp_path / "docs" / "decisions"
    pending_dir = decisions_dir / "pending"
    pending_dir.mkdir(parents=True)
    first = decisions_dir / "2026-05-17-first.md"
    second = pending_dir / "2026-05-17-second.md"
    first.write_text("# First Decision\n\nsharedterm alpha\n", encoding="utf-8")
    second.write_text("# Second Decision\n\nsharedterm beta\n", encoding="utf-8")

    decisions._DECISIONS_FTS_META.clear()
    refreshed = decisions._refresh_decisions_fts(tmp_path, db_path=db_path)
    assert refreshed["scanned"] == 2
    assert set(refreshed["updated"]) == {"2026-05-17-first.md", "2026-05-17-second.md"}

    status, payload, _ = search_route.build_search_payload(
        tmp_path,
        {"q": ["sharedterm"], "kind": ["decisions"], "limit": ["10"]},
        bridge_db_path=db_path,
    )
    assert status == 200
    assert {item["filename"] for item in payload["results"]} == {
        "2026-05-17-first.md",
        "2026-05-17-second.md",
    }

    first.write_text("# First Decision Updated\n\nsharedterm updatedunique\n", encoding="utf-8")
    new_mtime = time.time() + 10
    os.utime(first, (new_mtime, new_mtime))
    refreshed = decisions._refresh_decisions_fts(tmp_path, db_path=db_path)
    assert refreshed["updated"] == ["2026-05-17-first.md"]
    assert refreshed["deleted"] == []

    status, payload, _ = search_route.build_search_payload(
        tmp_path,
        {"q": ["updatedunique"], "kind": ["decisions"], "limit": ["10"]},
        bridge_db_path=db_path,
    )
    assert status == 200
    assert [item["filename"] for item in payload["results"]] == ["2026-05-17-first.md"]
    assert payload["results"][0]["title"] == "First Decision Updated"


def test_decision_scanners_ignore_sidecar_readme_and_template(tmp_path: Path, monkeypatch) -> None:
    decisions_dir = tmp_path / "docs" / "decisions"
    pending = decisions_dir / "pending"
    pending.mkdir(parents=True)
    (decisions_dir / "README.md").write_text("sidecartoken not a card", encoding="utf-8")
    (decisions_dir / "_template.md").write_text("sidecartoken not a card", encoding="utf-8")
    (decisions_dir / "2026-05-17-real-card.md").write_text("# real card", encoding="utf-8")
    (pending / "README.md").write_text("sidecartoken not a card", encoding="utf-8")
    (pending / "2026-05-17-pending-card.md").write_text("# pending", encoding="utf-8")

    pending_result = decisions.build_pending_decisions(tmp_path)
    index_result = decisions.build_decisions_index(tmp_path)

    pending_names = {Path(f["decision_path"]).name for f in pending_result["files"]}
    assert "README.md" not in pending_names
    assert "_template.md" not in pending_names
    assert pending_names == {"2026-05-17-pending-card.md"}

    index_names = {item["filename"] for item in index_result["decisions"]}
    assert index_names == {"2026-05-17-real-card.md", "2026-05-17-pending-card.md"}

    db_path = tmp_path / "messages.db"
    decisions._DECISIONS_FTS_META.clear()
    decisions._refresh_decisions_fts(tmp_path, db_path=db_path)
    status, payload, _ = search_route.build_search_payload(
        tmp_path,
        {"q": ["sidecartoken"], "kind": ["decisions"], "limit": ["10"]},
        bridge_db_path=db_path,
    )
    assert status == 200
    assert payload["results"] == []


def test_refresh_decisions_fts_repopulates_after_db_recreated(tmp_path: Path) -> None:
    db_path = tmp_path / "messages.db"
    decisions_dir = tmp_path / "docs" / "decisions"
    decisions_dir.mkdir(parents=True)
    card = decisions_dir / "2026-05-17-cache-card.md"
    card.write_text("# Cache Card\n\ncardtoken survives db recreation\n", encoding="utf-8")

    decisions._DECISIONS_FTS_META.clear()
    decisions._refresh_decisions_fts(tmp_path, db_path=db_path)
    status, payload, _ = search_route.build_search_payload(
        tmp_path,
        {"q": ["cardtoken"], "kind": ["decisions"], "limit": ["10"]},
        bridge_db_path=db_path,
    )
    assert status == 200
    assert payload["results"] != []

    db_path.unlink()
    db_path.touch()
    conn = sqlite3.connect(db_path)
    try:
        decisions.setup_decisions_fts(conn)
        conn.commit()
    finally:
        conn.close()

    decisions._refresh_decisions_fts(tmp_path, db_path=db_path)
    status, payload, _ = search_route.build_search_payload(
        tmp_path,
        {"q": ["cardtoken"], "kind": ["decisions"], "limit": ["10"]},
        bridge_db_path=db_path,
    )
    assert status == 200
    assert payload["results"] != []
