from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from agent_runtime.result import Result
from ai_agent_bridge import _channels, _cli, _db


@pytest.fixture(autouse=True)
def isolate_db(tmp_path):
    db_file = tmp_path / "messages.db"
    with patch("ai_agent_bridge._config.DB_PATH", db_file), \
         patch("ai_agent_bridge._db.DB_PATH", db_file):
        _db.init_db()
        yield db_file


def _run_cli(argv: list[str]) -> int:
    with patch.object(sys, "argv", ["ab", *argv]):
        try:
            _cli.main()
        except SystemExit as exc:
            return exc.code if isinstance(exc.code, int) else 0
    return 0


@patch("agent_runtime.runner.invoke")
def test_discuss_routes_cold_warm_and_fresh_session_modes(
    mock_invoke,
    monkeypatch,
) -> None:
    _channels.create_channel("session-modes")
    monkeypatch.setattr(_channels, "fetch_monitor_state", lambda: None)
    ids = iter(range(1, 1000))
    monkeypatch.setattr(_channels, "_new_id", lambda: f"session-mode-{next(ids):04d}")

    def _result(agent: str, *_args, **_kwargs) -> Result:
        return Result(
            ok=True,
            agent=agent,
            model="test-model",
            mode="danger" if agent == "codex" else "read-only",
            response=f"{agent} reply\n[AGREE]",
            stderr_excerpt=None,
            duration_s=0.1,
            session_id="claude-session" if agent == "claude" else "codex-session",
            rate_limited=False,
            stalled=False,
            returncode=0,
            usage_record={},
        )

    mock_invoke.side_effect = _result

    exit_code = _run_cli(
        [
            "discuss",
            "session-modes",
            "topic",
            "--with",
            "claude,codex",
            "--max-rounds",
            "2",
        ]
    )

    assert exit_code == 0
    claude_calls = [
        call for call in mock_invoke.call_args_list if call.args[0] == "claude"
    ]
    codex_calls = [
        call for call in mock_invoke.call_args_list if call.args[0] == "codex"
    ]
    assert [call.kwargs["session_id"] for call in claude_calls] == [
        None,
        "claude-session",
    ]
    assert all(call.kwargs["session_id"] is None for call in codex_calls)
    assert all(call.kwargs["mode"] == "danger" for call in codex_calls)
    assert (
        _db.get_session("discuss:session-mode-0001")["claude_session_id"]
        == "claude-session"
    )
