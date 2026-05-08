from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_local_api():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "local_api.py"
    spec = importlib.util.spec_from_file_location("local_api_channel_delta", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


local_api = _load_local_api()


def test_channel_shell_contains_delta_append_markers(tmp_path: Path) -> None:
    status, body, content_type = local_api.route_request(tmp_path, "/channels/shared")

    assert status == 200
    assert "text/html" in content_type
    assert 'class="channels-sidebar"' in body
    assert 'class="channel-main"' in body
    assert 'class="messages" id="messageList"' in body
    assert "const renderedMsgIds = new Set();" in body
    assert "row.dataset.messageId" in body
    assert "data-message-id" in body
    assert "messageList.appendChild(row)" in body
    assert "messageList.replaceChildren(emptyState)" in body
    assert "messageList.innerHTML" not in body


def test_channel_shell_contains_unread_localstorage_markers(tmp_path: Path) -> None:
    _, body, _ = local_api.route_request(tmp_path, "/channels")

    assert "kdjo_channel_lastvisited_" in body
    assert "unread-badge" in body
    assert "since_ts=" in body
    assert "/channels/+encodeURIComponent" not in body
    assert 'a.href="/channels/"+encodeURIComponent(ch.name)' in body
