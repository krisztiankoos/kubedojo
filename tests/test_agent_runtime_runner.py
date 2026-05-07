from __future__ import annotations

from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from agent_runtime import runner


def test_build_usage_record_session_mode_new():
    record = runner._build_usage_record(
        agent="claude",
        entrypoint="bridge",
        model="test-model",
        mode="read-only",
        task_id="discuss-task",
        cwd=Path("/tmp"),
        session_id=None,
        session_id_out="uuid-1",
        duration_s=0.1,
        input_chars=3,
        output_chars=4,
        returncode=0,
        outcome="ok",
        rate_limited=False,
        stalled=False,
        stderr_excerpt=None,
        tokens=10,
    )

    assert record["session_mode"] == "new"


def test_build_usage_record_session_mode_resume():
    record = runner._build_usage_record(
        agent="claude",
        entrypoint="bridge",
        model="test-model",
        mode="read-only",
        task_id="discuss-task",
        cwd=Path("/tmp"),
        session_id="uuid-1",
        session_id_out="uuid-1",
        duration_s=0.1,
        input_chars=3,
        output_chars=4,
        returncode=0,
        outcome="ok",
        rate_limited=False,
        stalled=False,
        stderr_excerpt=None,
        tokens=10,
    )

    assert record["session_mode"] == "resume"


def test_build_usage_record_session_mode_none_drop():
    record = runner._build_usage_record(
        agent="gemini",
        entrypoint="bridge",
        model="test-model",
        mode="read-only",
        task_id="discuss-task",
        cwd=Path("/tmp"),
        session_id="uuid-1",
        session_id_out=None,
        duration_s=0.1,
        input_chars=3,
        output_chars=4,
        returncode=0,
        outcome="ok",
        rate_limited=False,
        stalled=False,
        stderr_excerpt=None,
        tokens=10,
    )

    assert record["session_mode"] == "none"


def test_build_usage_record_session_mode_none_codex():
    record = runner._build_usage_record(
        agent="codex",
        entrypoint="bridge",
        model="test-model",
        mode="danger",
        task_id="discuss-task",
        cwd=Path("/tmp"),
        session_id=None,
        session_id_out=None,
        duration_s=0.1,
        input_chars=3,
        output_chars=4,
        returncode=0,
        outcome="ok",
        rate_limited=False,
        stalled=False,
        stderr_excerpt=None,
        tokens=10,
    )

    assert record["session_mode"] == "none"
