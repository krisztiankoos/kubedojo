from __future__ import annotations

import importlib.util
import json
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
    spec = importlib.util.spec_from_file_location("local_api_decisions_cache", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


decisions = _load_decisions_module()


def test_decision_lineage_cache_invalidates_on_mtime_change(tmp_path: Path) -> None:
    decisions_dir = tmp_path / "docs" / "decisions"
    decisions_dir.mkdir(parents=True)
    decision = decisions_dir / "demo.md"
    decision.write_text("# Demo\n\n**Thread:** `a82ab60b4ce1457aa450f18dac7e8a54`\n", encoding="utf-8")

    first = decisions.scan_decision_lineage(tmp_path, decision)
    rel = "docs/decisions/demo.md"
    cache_path = tmp_path / ".pipeline" / "decision-lineage-cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    assert cache[rel]["mtime"] == decision.stat().st_mtime

    cache[rel]["lineage"]["lineage"]["commits"] = [
        {"sha": "sentinel", "subject": "cached", "ts": "cached"}
    ]
    cache_path.write_text(json.dumps(cache), encoding="utf-8")
    cached = decisions.scan_decision_lineage(tmp_path, decision)
    assert cached["lineage"]["commits"][0]["sha"] == "sentinel"

    new_mtime = time.time() + 5
    os.utime(decision, (new_mtime, new_mtime))
    rebuilt = decisions.scan_decision_lineage(tmp_path, decision)
    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    assert cache[rel]["mtime"] == decision.stat().st_mtime
    assert rebuilt["lineage"]["commits"] == first["lineage"]["commits"]
    assert all(commit["sha"] != "sentinel" for commit in rebuilt["lineage"]["commits"])
