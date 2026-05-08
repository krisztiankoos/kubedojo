from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_local_api():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "local_api.py"
    spec = importlib.util.spec_from_file_location("local_api_channel_cadence", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


local_api = _load_local_api()


def test_channel_shell_contains_auto_tightening_poll_cadence(
    tmp_path: Path,
) -> None:
    status, body, _ = local_api.route_request(tmp_path, "/channels/shared")

    assert status == 200
    assert "const DEFAULT_POLL_MS = 5000;" in body
    assert "const TIGHT_POLL_MS = 1000;" in body
    assert "const QUIET_RESET_MS = 30000;" in body
    assert "function computePollDelayMs" in body
    assert 'lastEventType==="reply_started"||lastEventType==="heartbeat"' in body
    assert "return TIGHT_POLL_MS" in body
    assert "return DEFAULT_POLL_MS" in body
    assert 'ev.event==="reply_complete"' in body


def test_channel_shell_contains_stale_fetch_protection(tmp_path: Path) -> None:
    _, body, _ = local_api.route_request(tmp_path, "/channels/shared")

    assert "let currentFetchId = 0;" in body
    assert "const myFetchId=++currentFetchId" in body
    assert "myFetchId!==currentFetchId" in body
