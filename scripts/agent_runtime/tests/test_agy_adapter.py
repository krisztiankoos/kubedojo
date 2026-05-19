"""Unit tests for the ``AgyAdapter`` Antigravity CLI integration."""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agent_runtime.adapters.agy import AgyAdapter


def _build(mode: str) -> list[str]:
    adapter = AgyAdapter()
    plan = adapter.build_invocation(
        prompt="p",
        mode=mode,
        cwd=Path("/tmp"),
        model="gemini-3.5-flash-high",
        task_id=None,
        session_id=None,
        tool_config=None,
    )
    return plan.cmd


def test_build_invocation_read_only(monkeypatch) -> None:
    monkeypatch.setattr("agent_runtime.adapters.agy.shutil.which", lambda _: "agy")

    cmd = _build("read-only")

    assert cmd == ["agy", "-p", "p"]
    assert "--dangerously-skip-permissions" not in cmd


def test_build_invocation_workspace_write(monkeypatch) -> None:
    monkeypatch.setattr("agent_runtime.adapters.agy.shutil.which", lambda _: "agy")

    cmd = _build("workspace-write")

    assert cmd == ["agy", "-p", "p", "--dangerously-skip-permissions"]


def test_build_invocation_danger(monkeypatch) -> None:
    monkeypatch.setattr("agent_runtime.adapters.agy.shutil.which", lambda _: "agy")

    cmd = _build("danger")

    assert cmd == ["agy", "-p", "p", "--dangerously-skip-permissions"]


def test_build_invocation_with_session_id(monkeypatch) -> None:
    monkeypatch.setattr("agent_runtime.adapters.agy.shutil.which", lambda _: "agy")
    adapter = AgyAdapter()
    session_id = "123e4567-e89b-12d3-a456-426614174000"

    plan = adapter.build_invocation(
        prompt="p",
        mode="read-only",
        cwd=Path("/tmp"),
        model="gemini-3.5-flash-high",
        task_id=None,
        session_id=session_id,
        tool_config=None,
    )

    assert f"--conversation={session_id}" in plan.cmd


def test_build_invocation_uses_home_fallback(monkeypatch) -> None:
    monkeypatch.setattr("agent_runtime.adapters.agy.shutil.which", lambda _: None)
    adapter = AgyAdapter()

    plan = adapter.build_invocation(
        prompt="p",
        mode="read-only",
        cwd=Path("/tmp"),
        model=None,
        task_id=None,
        session_id=None,
        tool_config=None,
    )

    assert plan.cmd[0].endswith("/.local/bin/agy")
    assert plan.stdin_payload == ""


def test_parse_response_happy_path() -> None:
    adapter = AgyAdapter()
    result = adapter.parse_response(
        stdout="Answer\n",
        stderr="",
        returncode=0,
        output_file=None,
    )

    assert result.ok is True
    assert result.response == "Answer"
    assert result.rate_limited is False
    assert result.session_id is None
    assert result.tokens is None
    assert "model" in (result.stderr_excerpt or "")


def test_parse_response_detects_rate_limit() -> None:
    adapter = AgyAdapter()
    result = adapter.parse_response(
        stdout="",
        stderr="RESOURCE_EXHAUSTED: quota exceeded",
        returncode=1,
        output_file=None,
    )

    assert result.rate_limited is True
    assert result.ok is False
    assert result.response == ""
