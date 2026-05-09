from __future__ import annotations

import os
import shlex
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def _drop_bridge_modules() -> None:
    for name in list(sys.modules):
        if name == "ai_agent_bridge" or name.startswith("ai_agent_bridge."):
            del sys.modules[name]


def _load_bridge(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("AB_DB_PATH", str(tmp_path / "messages.db"))
    monkeypatch.setenv("AB_REPO_ROOT", str(REPO_ROOT))
    _drop_bridge_modules()

    from ai_agent_bridge import _channels, _channels_cli

    _channels.create_channel("test-discuss")
    return _channels, _channels_cli


def _discuss_args(agent: str) -> SimpleNamespace:
    return SimpleNamespace(
        channel="test-discuss",
        body="test",
        with_agents=agent,
        max_rounds=1,
        resume_thread=None,
    )


def _root_delivery_statuses(db_path: Path) -> list[str]:
    db = sqlite3.connect(db_path)
    try:
        rows = db.execute(
            """
            SELECT d.status
            FROM deliveries d
            JOIN channel_messages cm ON cm.message_id = d.message_id
            WHERE cm.parent_id IS NULL
            ORDER BY d.to_agent
            """
        ).fetchall()
    finally:
        db.close()
    return [row[0] for row in rows]


def test_discuss_gemini_retries_quota_failure_without_api_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _channels, channels_cli = _load_bridge(monkeypatch, tmp_path)
    _ = _channels

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    count_file = tmp_path / "gemini-count"
    env_log = tmp_path / "gemini-env.log"
    gemini = fake_bin / "gemini"
    gemini.write_text(
        "\n".join(
            [
                "#!/bin/sh",
                f"count_file={shlex.quote(str(count_file))}",
                f"env_log={shlex.quote(str(env_log))}",
                'count="$(cat "$count_file" 2>/dev/null || printf 0)"',
                'count=$((count + 1))',
                'printf "%s" "$count" > "$count_file"',
                'api_key="${GEMINI_API_KEY-<unset>}"',
                'printf "%s:GEMINI_API_KEY=%s\\n" "$count" "$api_key" >> "$env_log"',
                "cat >/dev/null",
                'if [ "$count" -eq 1 ]; then',
                '  echo "TerminalQuotaError: You have exhausted your capacity on this model. Your quota will reset after 1h." >&2',
                "  exit 1",
                "fi",
                'echo "Gemini retry succeeded. [AGREE]"',
            ]
        ),
        encoding="utf-8",
    )
    gemini.chmod(0o755)

    monkeypatch.setenv("PATH", f"{fake_bin}:{SCRIPTS_DIR}:{os.environ.get('PATH', '')}")
    monkeypatch.setenv("GEMINI_API_KEY", "api-key-from-test")
    monkeypatch.delenv("KUBEDOJO_GEMINI_SUBSCRIPTION", raising=False)

    import agent_runtime.runner as runner

    monkeypatch.setattr(runner, "has_headroom", lambda _agent, _model: (True, ""))
    monkeypatch.setattr(runner, "write_record", lambda _record: None)

    assert channels_cli._handle_discuss(_discuss_args("gemini")) == 0

    env_lines = env_log.read_text(encoding="utf-8").splitlines()
    assert env_lines[0] == "1:GEMINI_API_KEY=api-key-from-test"
    assert env_lines[1] == "2:GEMINI_API_KEY=<unset>"
    assert env_lines[2] == "3:GEMINI_API_KEY=<unset>"


def test_discuss_marks_root_delivery_delivered(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _channels, channels_cli = _load_bridge(monkeypatch, tmp_path)
    _ = _channels

    import agent_runtime.runner as runner

    def fake_invoke(*_args, **_kwargs):
        return SimpleNamespace(
            ok=True,
            response="Claude response. [AGREE]",
            stderr_excerpt=None,
            session_id="claude-session",
        )

    monkeypatch.setattr(runner, "invoke", fake_invoke)

    assert channels_cli._handle_discuss(_discuss_args("claude")) == 0
    assert _root_delivery_statuses(tmp_path / "messages.db") == ["delivered"]
