from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import pipeline_v3  # noqa: E402


ORIGINAL = "By default, the platform always provisions e2-small."
REWRITE = "By default, the platform often provisions small nodes."


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


def test_gate_a_softened_end_sentence_keyword_in_quiz_is_queued() -> None:
    body, applied, queued = pipeline_v3._apply_overstatement_swaps(
        _module(
            "<details>\n"
            "<summary>What node class does GKE Autopilot provision by default?</summary>\n\n"
            "A: e2-small\n"
            "</details>"
        ),
        [_candidate()],
    )

    assert ORIGINAL not in body
    assert REWRITE in body
    assert applied == [{"line": 8, "trigger": "always", "old": ORIGINAL, "new": REWRITE}]
    assert [item["queue_reason"] for item in queued] == ["gate_a_quiz_residual"]
    assert queued[0]["matched_keyword"] == "e2-small"


def test_gate_a_short_digit_keyword_in_quiz_is_queued() -> None:
    sentence = "The bucket always uses s3."
    rewrite = "The bucket often uses object storage."
    body, applied, queued = pipeline_v3._apply_overstatement_swaps(
        _module(
            "<details>\n"
            "<summary>Which service stores the bucket data?</summary>\n\n"
            "A: s3\n"
            "</details>"
        ).replace(ORIGINAL, sentence),
        [{**_candidate(), "sentence": sentence, "verdict": {
            "verdict": "overstated",
            "suggested_rewrite": rewrite,
        }}],
    )

    assert sentence not in body
    assert rewrite in body
    assert applied == [{"line": 8, "trigger": "always", "old": sentence, "new": rewrite}]
    assert [item["queue_reason"] for item in queued] == ["gate_a_quiz_residual"]
    assert queued[0]["matched_keyword"] == "s3"


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
