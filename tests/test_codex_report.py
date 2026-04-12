from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ai_agent_bridge._codex_report import (
    CodexReport,
    parse_codex_report,
    validate_codex_report,
)


def test_parse_codex_report_success_block():
    text = """
prefix text
=== CODEX REPORT BEGIN ===
TASK_ID: issue-1192-c5c6
STATUS: success
COMMIT_SHA: abc123def456
FILES_TOUCHED:
  - scripts/ai_agent_bridge/_worktree_brief.py
  - scripts/ai_agent_bridge/_codex_report.py
NOTES:
  - Kept adapter wiring out of scope.
  - Added focused parser tests.
RUFF: pass
NEW_TESTS_COUNT: 4
=== CODEX REPORT END ===
suffix text
"""

    report = parse_codex_report(text)

    assert report == CodexReport(
        task_id="issue-1192-c5c6",
        status="success",
        commit_sha="abc123def456",
        files_touched=[
            "scripts/ai_agent_bridge/_worktree_brief.py",
            "scripts/ai_agent_bridge/_codex_report.py",
        ],
        notes=[
            "Kept adapter wiring out of scope.",
            "Added focused parser tests.",
        ],
        extra={
            "RUFF": "pass",
            "NEW_TESTS_COUNT": "4",
        },
    )


def test_parse_codex_report_partial_block_with_missing_optional_fields():
    text = """
=== CODEX REPORT BEGIN ===
TASK_ID: issue-1192-c5c6
STATUS: partial
FILES_TOUCHED: ["tests/test_codex_report.py"]
NOTES: ["Tests added; adapter wiring deferred."]
=== CODEX REPORT END ===
"""

    report = parse_codex_report(text)

    assert report is not None
    assert report.task_id == "issue-1192-c5c6"
    assert report.status == "partial"
    assert report.commit_sha is None
    assert report.files_touched == ["tests/test_codex_report.py"]
    assert report.notes == ["Tests added; adapter wiring deferred."]
    assert report.extra == {}


def test_parse_codex_report_returns_none_when_block_missing():
    assert parse_codex_report("no structured report here") is None


def test_validate_codex_report_catches_missing_required_fields():
    report = CodexReport(
        task_id="",
        status="",
        commit_sha=None,
        files_touched=[],
        notes=[],
        extra={},
    )

    assert validate_codex_report(report) == [
        "TASK_ID is required",
        "STATUS is required",
    ]
