from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_decisions_module():
    module_path = (
        Path(__file__).resolve().parent.parent
        / "scripts"
        / "local_api"
        / "routes"
        / "decisions.py"
    )
    spec = importlib.util.spec_from_file_location("local_api_decisions_resolves", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


decisions = _load_decisions_module()


def test_deliberation_roadmap_lineage_resolves_pr_994() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    payload = decisions.scan_decision_lineage(
        repo_root,
        "docs/decisions/2026-05-07-deliberation-ui-roadmap.md",
    )

    pr_numbers = {
        item["number"]
        for item in payload["lineage"]["prs"]
        if isinstance(item.get("number"), str)
    }
    assert {"994", "995", "997", "998"}.issubset(pr_numbers)
    assert payload["thread_id"] == "a82ab60b4ce1457aa450f18dac7e8a54"
    assert payload["status"] == "decided"
