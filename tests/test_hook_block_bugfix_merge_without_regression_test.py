"""Tests for `.claude/hooks/block-bugfix-merge-without-regression-test.sh`.

The hook fires on `gh pr merge` for bugfix PRs (title starts with ``fix:`` /
``fix(...)``: OR body has ``Fixes #N`` / ``Closes #N``). It requires a
``Regression test:`` line in the body that points to a test file which
(a) is in this PR's files list and (b) references the issue number.

Pytest is intentionally NOT run by the hook — CI's job. The hook is a
fast (<1s) mechanical receipt that the regression test exists.
"""
import json
import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK = REPO_ROOT / ".claude" / "hooks" / "block-bugfix-merge-without-regression-test.sh"
BASH = "/bin/bash"


def run_hook(
    command: str,
    *,
    pr_json: dict | None,
    fixture_files: dict[str, str] | None,
    tmp_path: Path,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)
    if pr_json is not None:
        pr_json_path = tmp_path / "pr.json"
        pr_json_path.write_text(json.dumps(pr_json))
        env["KUBEDOJO_HOOK_GH_JSON"] = str(pr_json_path)
    if fixture_files is not None:
        fixture_dir = tmp_path / "fixtures"
        for rel, contents in fixture_files.items():
            target = fixture_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(contents)
        env["KUBEDOJO_HOOK_FILE_FIXTURE_DIR"] = str(fixture_dir)
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": command, "cwd": str(tmp_path)},
    }
    return subprocess.run(
        [BASH, str(HOOK)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        env=env,
        cwd=tmp_path,
    )


TEST_FILE_WITH_ISSUE = (
    "import pytest\n\n"
    "# Regression test for issue #1212 (citation backfill cascade-fail).\n"
    "def test_inject_failure_restores_seed_json():\n"
    "    assert True\n"
)

TEST_FILE_WITHOUT_ISSUE = (
    "import pytest\n\n"
    "def test_inject_failure_restores_seed_json():\n"
    "    assert True\n"
)


def test_non_bash_tool_is_ignored(tmp_path: Path) -> None:
    payload = {"tool_name": "Read", "tool_input": {"file_path": "/etc/hosts"}}
    result = subprocess.run(
        [BASH, str(HOOK)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        cwd=tmp_path,
    )
    assert result.returncode == 0


def test_non_merge_command_is_ignored(tmp_path: Path) -> None:
    result = run_hook(
        "git status",
        pr_json=None,
        fixture_files=None,
        tmp_path=tmp_path,
    )
    assert result.returncode == 0


def test_non_fix_pr_is_allowed(tmp_path: Path) -> None:
    pr = {
        "body": "Adds a new helper.",
        "files": [{"path": "scripts/helper.py"}],
        "headRefOid": "abc123",
        "title": "feat: new helper",
        "number": 9100,
    }
    result = run_hook(
        "gh pr merge 9100 --squash",
        pr_json=pr,
        fixture_files=None,
        tmp_path=tmp_path,
    )
    assert result.returncode == 0, result.stderr


def test_fix_pr_without_regression_test_is_denied(tmp_path: Path) -> None:
    pr = {
        "body": "Fixes #1212 — restores the seed JSON on inject failure.",
        "files": [{"path": "scripts/quality/pipeline.py"}],
        "headRefOid": "abc123",
        "title": "fix(pipeline): restore seed on inject failure",
        "number": 9101,
    }
    result = run_hook(
        "gh pr merge 9101 --squash",
        pr_json=pr,
        fixture_files=None,
        tmp_path=tmp_path,
    )
    assert result.returncode == 2
    assert "missing a 'Regression test:' line" in result.stderr


def test_fix_pr_with_test_not_in_pr_is_denied(tmp_path: Path) -> None:
    pr = {
        "body": (
            "Fixes #1212.\n\n"
            "Regression test: tests/test_backfill_seed_restore.py\n"
        ),
        "files": [
            {"path": "scripts/quality/pipeline.py"},
            # Note: test file not in PR files list.
        ],
        "headRefOid": "abc123",
        "title": "fix(pipeline): restore seed on inject failure",
        "number": 9102,
    }
    result = run_hook(
        "gh pr merge 9102 --squash",
        pr_json=pr,
        fixture_files={
            "tests/test_backfill_seed_restore.py": TEST_FILE_WITH_ISSUE,
        },
        tmp_path=tmp_path,
    )
    assert result.returncode == 2
    assert "is not part of this PR" in result.stderr


def test_fix_pr_with_test_missing_issue_ref_is_denied(tmp_path: Path) -> None:
    pr = {
        "body": (
            "Fixes #1212.\n\n"
            "Regression test: tests/test_backfill_seed_restore.py\n"
        ),
        "files": [
            {"path": "scripts/quality/pipeline.py"},
            {"path": "tests/test_backfill_seed_restore.py"},
        ],
        "headRefOid": "abc123",
        "title": "fix(pipeline): restore seed on inject failure",
        "number": 9103,
    }
    result = run_hook(
        "gh pr merge 9103 --squash",
        pr_json=pr,
        fixture_files={
            "tests/test_backfill_seed_restore.py": TEST_FILE_WITHOUT_ISSUE,
        },
        tmp_path=tmp_path,
    )
    assert result.returncode == 2
    assert "does not reference any of the issues" in result.stderr


def test_fix_pr_with_valid_regression_test_is_allowed(tmp_path: Path) -> None:
    pr = {
        "body": (
            "Fixes #1212 — the citation backfill cascade-fail bug.\n\n"
            "Regression test: tests/test_backfill_seed_restore.py\n"
        ),
        "files": [
            {"path": "scripts/quality/pipeline.py"},
            {"path": "tests/test_backfill_seed_restore.py"},
        ],
        "headRefOid": "abc123",
        "title": "fix(pipeline): restore seed on inject failure",
        "number": 9104,
    }
    result = run_hook(
        "gh pr merge 9104 --squash",
        pr_json=pr,
        fixture_files={
            "tests/test_backfill_seed_restore.py": TEST_FILE_WITH_ISSUE,
        },
        tmp_path=tmp_path,
    )
    assert result.returncode == 0, result.stderr


def test_fix_title_with_paren_issue_ref_recognized(tmp_path: Path) -> None:
    # Some bugfix PRs ref the issue only in the title via `(#N)` rather
    # than via Fixes: in the body. The hook should still treat them as
    # bugfix PRs and check for a regression test.
    pr = {
        "body": (
            "Restores the seed JSON on inject failure.\n\n"
            "Regression test: tests/test_backfill_seed_restore.py\n"
        ),
        "files": [
            {"path": "scripts/quality/pipeline.py"},
            {"path": "tests/test_backfill_seed_restore.py"},
        ],
        "headRefOid": "abc123",
        "title": "fix(pipeline): restore seed on inject failure (#1212)",
        "number": 9105,
    }
    result = run_hook(
        "gh pr merge 9105 --squash",
        pr_json=pr,
        fixture_files={
            "tests/test_backfill_seed_restore.py": TEST_FILE_WITH_ISSUE,
        },
        tmp_path=tmp_path,
    )
    assert result.returncode == 0, result.stderr


def test_fix_title_no_issue_anywhere_accepts_test_if_in_pr(tmp_path: Path) -> None:
    # Edge case: title is `fix:` but no issue number is referenced anywhere.
    # The hook accepts the test as long as it's in the PR — we can't enforce
    # an issue ref that doesn't exist.
    pr = {
        "body": (
            "Fixes a small typo bug in the logger.\n\n"
            "Regression test: tests/test_logger_typo.py\n"
        ),
        "files": [
            {"path": "scripts/logger.py"},
            {"path": "tests/test_logger_typo.py"},
        ],
        "headRefOid": "abc123",
        "title": "fix(logger): correct log level constant",
        "number": 9106,
    }
    result = run_hook(
        "gh pr merge 9106 --squash",
        pr_json=pr,
        fixture_files={
            "tests/test_logger_typo.py": "def test_logger():\n    assert True\n",
        },
        tmp_path=tmp_path,
    )
    assert result.returncode == 0, result.stderr


def test_gh_failure_fails_open(tmp_path: Path) -> None:
    pr_json_path = tmp_path / "pr.json"
    pr_json_path.write_text("not valid json {{{")
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)
    env["KUBEDOJO_HOOK_GH_JSON"] = str(pr_json_path)
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "gh pr merge 1 --squash", "cwd": str(tmp_path)},
    }
    result = subprocess.run(
        [BASH, str(HOOK)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        env=env,
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stderr
