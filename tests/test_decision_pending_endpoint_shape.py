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
    spec = importlib.util.spec_from_file_location(
        "local_api_decision_pending_endpoint_shape",
        module_path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


decisions = _load_decisions_module()


def test_pending_endpoint_returns_mtime_and_is_stale(tmp_path: Path) -> None:
    pending_dir = tmp_path / "docs" / "decisions" / "pending"
    pending_dir.mkdir(parents=True)
    fresh = pending_dir / "2026-05-08-fresh.md"
    old = pending_dir / "2026-05-07-old.md"
    fresh.write_text("# Fresh\n", encoding="utf-8")
    old.write_text("# Old\n", encoding="utf-8")
    old_mtime = time.time() - (25 * 3600)
    os.utime(old, (old_mtime, old_mtime))

    status, payload, content_type = decisions.route_decision_api_request(
        tmp_path,
        "/api/decisions/pending",
    )

    assert status == 200
    assert "application/json" in content_type
    assert payload["pending"] == 1
    assert payload["stale"] == 1
    files = {item["filename"]: item for item in payload["files"]}
    assert set(files) == {"2026-05-08-fresh.md", "2026-05-07-old.md"}
    assert isinstance(files["2026-05-08-fresh.md"]["mtime"], float)
    assert isinstance(files["2026-05-07-old.md"]["mtime"], float)
    assert files["2026-05-08-fresh.md"]["is_stale"] is False
    assert files["2026-05-07-old.md"]["is_stale"] is True
