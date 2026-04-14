from __future__ import annotations

from dataclasses import dataclass


REWRITE_FEEDBACK_KEYWORDS = (
    "requires reorganization",
    "outline",
)
MAX_DISPERSED_RANGES = 3
MAX_PATCH_ATTEMPTS = 2
MAX_REWRITE_ATTEMPTS = 3


@dataclass(frozen=True)
class EscalationDecision:
    should_escalate: bool
    reasons: list[str]


def count_dispersed_ranges(failed_checks: list[dict]) -> int:
    ranges: set[tuple[int, int]] = set()
    for check in failed_checks:
        if not isinstance(check, dict):
            continue
        line_range = check.get("line_range")
        if (
            isinstance(line_range, list)
            and len(line_range) == 2
            and all(isinstance(value, int) for value in line_range)
        ):
            start, end = int(line_range[0]), int(line_range[1])
            ranges.add((min(start, end), max(start, end)))
    return len(ranges)


def feedback_requires_reorganization(feedback: str) -> bool:
    lowered = feedback.lower()
    return any(keyword in lowered for keyword in REWRITE_FEEDBACK_KEYWORDS)


def should_escalate_patch(
    *,
    failed_checks: list[dict],
    feedback: str,
    patch_attempts: int,
    patch_apply_failed: bool,
    partial_apply: bool,
    patch_degraded: bool,
) -> EscalationDecision:
    reasons: list[str] = []
    dispersed_ranges = count_dispersed_ranges(failed_checks)
    if patch_apply_failed:
        reasons.append("patch_apply_failed")
    if partial_apply:
        reasons.append("patch_partial_apply")
    if dispersed_ranges > MAX_DISPERSED_RANGES:
        reasons.append(f"dispersed_ranges>{MAX_DISPERSED_RANGES}")
    if patch_attempts > MAX_PATCH_ATTEMPTS:
        reasons.append(f"patch_attempts>{MAX_PATCH_ATTEMPTS}")
    if feedback_requires_reorganization(feedback):
        reasons.append("feedback_requires_reorganization")
    if patch_degraded:
        reasons.append("patch_degraded")
    return EscalationDecision(should_escalate=bool(reasons), reasons=reasons)


def should_dead_letter_rewrite(rewrite_attempts: int) -> bool:
    return rewrite_attempts > MAX_REWRITE_ATTEMPTS
