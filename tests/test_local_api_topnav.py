"""Regression tests for local-API top navigation routes."""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "local_api.py"
    spec = importlib.util.spec_from_file_location("local_api_topnav", module_path)
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


def _has_channels_nav(html: str) -> bool:
    return bool(re.search(r'<a class="navlink(?: active)?" href="/channels"', html))


def test_new_skeleton_routes_return_topnav(tmp_path: Path) -> None:
    for path in ["/health"]:
        html = _route(tmp_path, path)
        assert _has_channels_nav(html)
        assert "This page is part of the L0-L6 local-API UI split." in html


def test_quality_route_returns_real_page(tmp_path: Path) -> None:
    html = _route(tmp_path, "/quality")
    assert len(html) > 5000
    assert '<a class="navlink active" href="/quality"' in html
    assert 'id="quality-board"' in html


def test_operator_route_returns_real_page(tmp_path: Path) -> None:
    html = _route(tmp_path, "/operator")
    assert len(html) > 5000
    assert 'id="op-now"' in html
    assert '<a class="navlink active" href="/operator"' in html


def test_dashboard_drops_op_hero_columns(tmp_path: Path) -> None:
    html = _route(tmp_path, "/")
    assert 'id="op-now"' not in html


def test_dashboard_summary_links_to_operator(tmp_path: Path) -> None:
    html = _route(tmp_path, "/")
    assert 'class="op-summary-card"' in html
    assert 'class="op-summary-link"' in html


def test_home_page_links_to_channels(tmp_path: Path) -> None:
    html = _route(tmp_path, "/")
    assert _has_channels_nav(html)


def test_channels_pages_keep_topnav(tmp_path: Path) -> None:
    for path in ["/channels", "/channels/thread-123"]:
        html = _route(tmp_path, path)
        assert _has_channels_nav(html)
