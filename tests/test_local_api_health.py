"""Regression tests for the local-API health split."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "local_api.py"
    spec = importlib.util.spec_from_file_location("local_api_health", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


local_api = _load_module()


def _html(tmp_path: Path, path: str) -> str:
    status, body, content_type = local_api.route_request(tmp_path, path)
    assert status == 200
    assert "text/html" in content_type
    return body


def test_health_route_renders_operational_panels(tmp_path: Path) -> None:
    html = _html(tmp_path, "/health")

    assert '<a class="navlink active" href="/health"' in html
    assert 'id="health-services-panel"' in html
    assert 'id="health-worktrees-panel"' in html
    assert 'id="health-missing-panel"' in html
    assert "Runtime Services" in html
    assert "Worktrees" in html
    assert "Missing / Dead Letters" in html


def test_dashboard_drops_health_panel_ids(tmp_path: Path) -> None:
    html = _html(tmp_path, "/")

    assert 'id="health-services-panel"' not in html
    assert 'id="health-worktrees-panel"' not in html
    assert 'id="health-missing-panel"' not in html
    assert 'id="services"' not in html
    assert 'id="worktree"' not in html
    assert 'id="missing"' not in html


def test_dashboard_keeps_health_summary_card(tmp_path: Path) -> None:
    html = _html(tmp_path, "/")

    assert 'class="op-summary-card health-summary-card" href="/health"' in html
    assert "Services: 0 running / 0 total" in html
    assert "Worktrees: 0" in html
    assert "Missing: 0" in html


def test_schema_lists_health_route() -> None:
    schema = local_api.build_api_schema()
    paths = {e["path"] for e in schema["endpoints"]}

    assert "/health" in paths
