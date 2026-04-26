from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import pipeline_v3  # noqa: E402


ORIGINAL = "GKE Autopilot always provisions e2-small nodes by default."
REWRITE = "GKE Autopilot often provisions small nodes depending on workload."


def _candidate() -> dict[str, object]:
    return {
        "line": 8,
        "trigger": "always",
        "sentence": ORIGINAL,
        "verdict": {
            "verdict": "overstated",
            "suggested_rewrite": REWRITE,
        },
    }


def _module(quiz_body: str | None) -> str:
    quiz_section = "" if quiz_body is None else f"\n## Quiz\n\n{quiz_body}\n"
    return f"""---
title: Gate A Fixture
sidebar:
  order: 1
---

# Gate A Fixture

## Why This Module Matters

{ORIGINAL}
{quiz_section}"""


def test_gate_a_softened_keywords_in_quiz_are_queued() -> None:
    body, applied, queued = pipeline_v3._apply_overstatement_swaps(
        _module(
            "<details>\n"
            "<summary>What node class does GKE Autopilot provision by default?</summary>\n\n"
            "The answer is e2-small.\n"
            "</details>"
        ),
        [_candidate()],
    )

    assert ORIGINAL not in body
    assert REWRITE in body
    assert applied == [{"line": 8, "trigger": "always", "old": ORIGINAL, "new": REWRITE}]
    assert [item["queue_reason"] for item in queued] == ["gate_a_quiz_residual"]


def test_gate_a_softened_keywords_not_in_quiz_are_not_queued() -> None:
    body, applied, queued = pipeline_v3._apply_overstatement_swaps(
        _module(
            "<details>\n"
            "<summary>Which rollout signal should an operator inspect first?</summary>\n\n"
            "Check pending pods and recent events before changing requests.\n"
            "</details>"
        ),
        [_candidate()],
    )

    assert ORIGINAL not in body
    assert applied
    assert queued == []


def test_gate_a_softened_module_without_quiz_is_not_queued() -> None:
    body, applied, queued = pipeline_v3._apply_overstatement_swaps(
        _module(None),
        [_candidate()],
    )

    assert ORIGINAL not in body
    assert applied
    assert queued == []
