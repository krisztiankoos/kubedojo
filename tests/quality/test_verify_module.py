"""Tests for `_check_url` lightpanda fallback behavior."""
from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.quality import verify_module


class FakeResponse:
    def __init__(self, status_code: int, history: list[Any] | None = None):
        self.status_code = status_code
        self.history = history if history is not None else []

    def close(self) -> None:
        return None


def _install_fake_requests(monkeypatch: Any) -> None:
    class FakeSession:
        def __init__(self) -> None:
            self.max_redirects: int | None = None

        def head(self, *_args: Any, **_kwargs: Any) -> FakeResponse:
            return FakeResponse(403)

        def get(self, *_args: Any, **_kwargs: Any) -> FakeResponse:
            return FakeResponse(404)

    monkeypatch.setitem(sys.modules, "requests", types.SimpleNamespace(Session=FakeSession))


def test_check_url_falls_back_to_lightpanda(monkeypatch: Any) -> None:
    _install_fake_requests(monkeypatch)

    def fake_run(cmd: list[str], capture_output: bool = True, text: bool = True, timeout: int = 15) -> Any:
        assert cmd == ["lightpanda", "fetch", "--dump", "markdown", "https://openai.com/index/harness-engineering/"]
        return types.SimpleNamespace(returncode=0, stdout="# Title\n")

    monkeypatch.setattr("subprocess.run", fake_run)
    assert (
        verify_module._check_url("https://openai.com/index/harness-engineering/")
        == "200"
    )
