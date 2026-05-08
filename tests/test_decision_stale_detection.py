from __future__ import annotations

import importlib.util
import os
import sys
import time
from pathlib import Path


def _load_decisions_module():
    module_path = (
        Path(__file__).resolve().parent.parent
        / "scripts"
        / "local_api"
        / "routes"
        / "decisions.py"
    )
    spec = importlib.util.spec_from_file_location("local_api_decisions_stale", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


decisions = _load_decisions_module()


def test_missing_pending_dir_returns_zero_counts(tmp_path: Path) -> None:
    payload = decisions.build_pending_decisions(tmp_path)

    assert payload == {"pending": 0, "stale": 0, "files": []}


def test_pending_decision_older_than_24h_is_stale(tmp_path: Path) -> None:
    pending_dir = tmp_path / "docs" / "decisions" / "pending"
    pending_dir.mkdir(parents=True)
    decision = pending_dir / "test.md"
    decision.write_text("# Pending\n\n**Thread:** `a82ab60b4ce1457aa450f18dac7e8a54`\n", encoding="utf-8")
    old = time.time() - (25 * 3600)
    os.utime(decision, (old, old))

    payload = decisions.scan_decision_lineage(tmp_path, decision)

    assert payload["status"] == "stale"
    pending = decisions.build_pending_decisions(tmp_path)
    assert pending["pending"] == 1
    assert pending["stale"] == 1
    assert pending["files"][0]["status"] == "stale"


def test_decisions_index_shows_banner_for_stale_pending_file(tmp_path: Path) -> None:
    pending_dir = tmp_path / "docs" / "decisions" / "pending"
    pending_dir.mkdir(parents=True)
    decision = pending_dir / "test.md"
    decision.write_text("# Pending\n", encoding="utf-8")
    old = time.time() - (25 * 3600)
    os.utime(decision, (old, old))

    html = decisions.render_decisions_index_html(
        tmp_path,
        top_nav_css="",
        render_top_nav_fn=lambda active: f"<nav>{active}</nav>",
    )

    assert "1 decision awaiting your call." in html
    assert "STALE" in html
