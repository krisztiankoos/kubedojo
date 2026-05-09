"""Safe GitHub PR merge helpers.

GitHub's auto-merge queue can capture an old squash payload before later
branch commits land. These helpers wait for green checks first, then run a
direct squash merge so GitHub merges the live branch tip.
"""
from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


class PrMergeError(RuntimeError):
    """Raised when a PR cannot be safely merged."""


@dataclass(frozen=True)
class CheckSummary:
    pending: int
    failed: int
    total: int


def _run_gh(args: list[str], repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _check_value(item: dict[str, Any], *names: str) -> str:
    for name in names:
        value = item.get(name)
        if isinstance(value, str) and value:
            return value.upper()
    return ""


def _summarize_checks(status_check_rollup: list[dict[str, Any]]) -> CheckSummary:
    pending = 0
    failed = 0
    total = 0
    for item in status_check_rollup:
        if not isinstance(item, dict):
            continue
        total += 1
        conclusion = _check_value(item, "conclusion", "state")
        status = _check_value(item, "status")
        if conclusion in {"FAILURE", "FAILED", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED"}:
            failed += 1
        elif conclusion in {"SUCCESS", "NEUTRAL", "SKIPPED"} or status == "COMPLETED":
            continue
        else:
            pending += 1
    return CheckSummary(pending=pending, failed=failed, total=total)


def _merge_sha(pr_number: int, repo: Path) -> str:
    view = _run_gh(["pr", "view", str(pr_number), "--json", "mergeCommit"], repo)
    if view.returncode != 0:
        raise PrMergeError(f"merged PR #{pr_number}, but merge SHA lookup failed: {view.stderr.strip()}")
    try:
        payload = json.loads(view.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise PrMergeError(f"merged PR #{pr_number}, but merge SHA JSON was invalid") from exc
    merge_commit = payload.get("mergeCommit") or {}
    sha = merge_commit.get("oid") if isinstance(merge_commit, dict) else None
    if not sha:
        raise PrMergeError(f"merged PR #{pr_number}, but GitHub did not return mergeCommit.oid")
    return sha


def merge_when_green(
    pr_number: int,
    *,
    poll_interval: int = 8,
    timeout: int = 900,
    repo: Path | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> str:
    """Wait for all PR checks to pass, then direct squash-merge the live tip.

    Raises:
        PrMergeError: If any check fails, the PR closes before merge, the
            timeout expires, or the direct merge command fails.

    Returns:
        The merge commit SHA.
    """
    repo_root = repo or Path.cwd()
    deadline = time.monotonic() + timeout
    last_summary = CheckSummary(pending=0, failed=0, total=0)

    while True:
        view = _run_gh(
            ["pr", "view", str(pr_number), "--json", "state,statusCheckRollup"],
            repo_root,
        )
        if view.returncode != 0:
            raise PrMergeError(f"gh pr view failed for PR #{pr_number}: {view.stderr.strip()}")
        try:
            payload = json.loads(view.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise PrMergeError(f"gh pr view returned invalid JSON for PR #{pr_number}") from exc

        state = str(payload.get("state") or "").upper()
        if state and state != "OPEN":
            raise PrMergeError(f"PR #{pr_number} is {state}, not open")

        rollup = payload.get("statusCheckRollup") or []
        if not isinstance(rollup, list):
            raise PrMergeError(f"PR #{pr_number} statusCheckRollup was not a list")
        last_summary = _summarize_checks(rollup)
        if last_summary.failed:
            raise PrMergeError(f"PR #{pr_number} has {last_summary.failed} failing check(s)")
        if last_summary.pending == 0:
            break

        if time.monotonic() >= deadline:
            raise PrMergeError(
                f"timed out waiting for PR #{pr_number} checks: "
                f"{last_summary.pending} pending of {last_summary.total}"
            )
        sleep_fn(poll_interval)

    merge = _run_gh(
        ["pr", "merge", str(pr_number), "--squash", "--delete-branch"],
        repo_root,
    )
    if merge.returncode != 0:
        raise PrMergeError(f"direct squash merge failed for PR #{pr_number}: {merge.stderr.strip()}")
    return _merge_sha(pr_number, repo_root)

