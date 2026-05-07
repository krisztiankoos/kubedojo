"""Smoke tests for /channels deliberation UI routes."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "local_api.py"
    spec = importlib.util.spec_from_file_location("local_api_channels_ui", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


local_api = _load_module()


def test_channels_index_returns_html(tmp_path: Path) -> None:
    status, body, content_type = local_api.route_request(tmp_path, "/channels")
    assert status == 200
    assert "text/html" in content_type
    assert "Agent Deliberations" in body


def test_channel_thread_returns_html_with_thread_id(tmp_path: Path) -> None:
    status, body, content_type = local_api.route_request(
        tmp_path, "/channels/abc123"
    )
    assert status == 200
    assert "text/html" in content_type
    assert "abc123" in body
    assert "/api/channel/" in body
