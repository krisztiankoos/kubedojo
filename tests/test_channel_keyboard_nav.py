"""Structural smoke test for the channels keyboard navigation script.

This does not execute browser behavior. A follow-up should add Playwright or
JSDOM coverage for the actual keybinding interactions.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_local_api():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "local_api.py"
    spec = importlib.util.spec_from_file_location("local_api_channel_keynav", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


local_api = _load_local_api()


def test_channel_shell_contains_keyboard_navigation_markers(tmp_path: Path) -> None:
    status, body, content_type = local_api.route_request(tmp_path, "/channels/shared")

    assert status == 200
    assert "text/html" in content_type
    assert "// D4.5 keybindings" in body
    assert "addEventListener('keydown', " in body
    assert "event.target.tagName === 'INPUT'" in body
    assert "event.target.tagName === 'TEXTAREA'" in body
    assert "event.key === '?'" in body
    assert "event.key === 'j'" in body
    assert "event.key === 'k'" in body
    assert "event.key === 'g'" in body
    assert "(event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k'" in body
    assert "keybindings-help-modal" in body
    assert "channel-switcher-modal" in body
    assert "kbd-focused" in body
