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
    spec = importlib.util.spec_from_file_location(
        "local_api_decision_card_anchor",
        module_path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


decisions = _load_decisions_module()


def test_decisions_index_rows_have_card_ids_and_target_css(tmp_path: Path) -> None:
    decisions_dir = tmp_path / "docs" / "decisions"
    pending_dir = decisions_dir / "pending"
    pending_dir.mkdir(parents=True)
    decided = decisions_dir / "2026-05-08-decided.md"
    pending = pending_dir / "2026-05-08-pending.md"
    decided.write_text("# Decided\n", encoding="utf-8")
    pending.write_text("# Pending\n", encoding="utf-8")

    html = decisions.render_decisions_index_html(
        tmp_path,
        top_nav_css="",
        render_top_nav_fn=lambda active: f"<nav>{active}</nav>",
    )

    assert 'id="card-2026-05-08-decided.md"' in html
    assert 'id="card-2026-05-08-pending.md"' in html
    assert "tr.decision-card:target" in html
    assert "@keyframes decision-target-highlight" in html
