from __future__ import annotations

from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from agent_runtime import runner
from agent_runtime.adapters.base import InvocationPlan
from agent_runtime.result import ParseResult


@pytest.mark.parametrize(
    ("head_shas", "verify_called"),
    [
        (["same", "same"], False),
        (["before", "after"], True),
        ([None, "after"], True),
    ],
    ids=[
        "noop-danger-dispatch-skips-push-verify",
        "commit-landing-danger-dispatch-runs-push-verify",
        "git-head-failure-falls-back-to-push-verify",
    ],
)
def test_danger_push_verify_depends_on_head_movement(head_shas, verify_called):
    adapter = SimpleNamespace(
        default_model="gpt-test",
        supported_modes=frozenset({"danger"}),
        build_invocation=lambda **kw: InvocationPlan(
            cmd=["fake-agent"],
            cwd=kw["cwd"],
        ),
        liveness_signal_paths=lambda _plan: (),
        parse_response=lambda **_kw: ParseResult(ok=True, response="done"),
    )
    proc = SimpleNamespace(
        returncode=0,
        stdin=None,
        poll=lambda: 0,
        kill=lambda: None,
        wait=lambda timeout=None: 0,
    )
    state = SimpleNamespace(stdout_lines=["done"], stderr_lines=[])

    with (
        patch.object(runner, "_load_adapter", return_value=adapter),
        patch.object(runner, "has_headroom", return_value=(True, "")),
        patch.object(runner, "build_agent_env", return_value={}),
        patch.object(runner.subprocess, "Popen", return_value=proc),
        patch.object(runner, "start_watchdog", return_value=(state, [])),
        patch.object(runner, "stop_watchdog"),
        patch.object(runner, "write_record"),
        patch.object(runner, "_git_head_sha", side_effect=head_shas),
        patch.object(
            runner,
            "verify_current_branch_pushed",
            return_value=(True, None),
        ) as verify_pushed,
    ):
        result = runner.invoke(
            "codex",
            "consult only",
            mode="danger",
            cwd=Path("/tmp"),
            model="gpt-test",
            skip_headroom_check=True,
        )

    assert result.ok
    assert result.usage_record["stderr_excerpt"] is None
    assert verify_pushed.called is verify_called


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


def test_invoke_rejects_codex_resume_from_delegate_entrypoint():
    from agent_runtime.runner import invoke

    with pytest.raises(ValueError, match="resume_policy='bridge_only'"):
        invoke(
            "codex",
            "x",
            mode="danger",
            cwd=Path("/tmp"),
            model=None,
            task_id="task-1",
            session_id="codex-previous",
            entrypoint="delegate",
        )


def test_invoke_rejects_codex_resume_from_dispatch_entrypoint():
    from agent_runtime.runner import invoke

    with pytest.raises(ValueError, match="resume_policy='bridge_only'"):
        invoke(
            "codex",
            "x",
            mode="danger",
            cwd=Path("/tmp"),
            model=None,
            task_id="task-1",
            session_id="codex-previous",
            entrypoint="dispatch",
        )
