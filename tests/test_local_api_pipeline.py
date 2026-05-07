"""Regression tests for the local-API pipeline page split."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "local_api.py"
    spec = importlib.util.spec_from_file_location("local_api_pipeline", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


local_api = _load_module()


def _route(tmp_path: Path, path: str) -> str:
    status, body, content_type = local_api.route_request(tmp_path, path)
    assert status == 200
    assert "text/html" in content_type
    return body


def test_pipeline_route_returns_real_page(tmp_path: Path) -> None:
    html = _route(tmp_path, "/pipeline")
    assert 'id="v2-body"' in html
    assert 'id="v2-badge"' in html
    assert 'id="autopilot-v3-body"' in html
    assert 'id="autopilot-v3-badge"' in html
    assert '<a class="navlink active" href="/pipeline"' in html
    assert 'href="/channels"' in html


def test_dashboard_drops_v2_pipeline_panel(tmp_path: Path) -> None:
    html = _route(tmp_path, "/")
    assert 'id="v2-body"' not in html
    assert 'id="v2-badge"' not in html


def test_dashboard_keeps_pipeline_summary_link(tmp_path: Path) -> None:
    html = _route(tmp_path, "/")
    assert 'class="pipeline-summary-card"' in html
    assert 'href="/pipeline"' in html


def test_pipeline_recent_events_feed_markup(tmp_path: Path) -> None:
    html = _route(tmp_path, "/pipeline")
    assert "Recent pipeline events" in html
    assert 'id="pipeline-events"' in html
    assert '<div class="empty-state">Loading&hellip;</div>' in html

