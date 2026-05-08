from __future__ import annotations

import os
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
    first = decisions_dir / "first.md"
    second = pending_dir / "second.md"
    first.write_text("# First Decision\n\nsharedterm alpha\n", encoding="utf-8")
    second.write_text("# Second Decision\n\nsharedterm beta\n", encoding="utf-8")

    decisions._DECISIONS_FTS_META.clear()
    refreshed = decisions._refresh_decisions_fts(tmp_path, db_path=db_path)
    assert refreshed["scanned"] == 2
    assert set(refreshed["updated"]) == {"first.md", "second.md"}

    status, payload, _ = search_route.build_search_payload(
        tmp_path,
        {"q": ["sharedterm"], "kind": ["decisions"], "limit": ["10"]},
        bridge_db_path=db_path,
    )
    assert status == 200
    assert {item["filename"] for item in payload["results"]} == {"first.md", "second.md"}

    first.write_text("# First Decision Updated\n\nsharedterm updatedunique\n", encoding="utf-8")
    new_mtime = time.time() + 10
    os.utime(first, (new_mtime, new_mtime))
    refreshed = decisions._refresh_decisions_fts(tmp_path, db_path=db_path)
    assert refreshed["updated"] == ["first.md"]
    assert refreshed["deleted"] == []

    status, payload, _ = search_route.build_search_payload(
        tmp_path,
        {"q": ["updatedunique"], "kind": ["decisions"], "limit": ["10"]},
        bridge_db_path=db_path,
    )
    assert status == 200
    assert [item["filename"] for item in payload["results"]] == ["first.md"]
    assert payload["results"][0]["title"] == "First Decision Updated"
