from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import call, patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ai_agent_bridge._worktree_brief import write_worktree_brief


def test_write_worktree_brief_writes_expected_yaml(tmp_path):
    fixed_now = datetime(2026, 4, 12, 9, 30, 0, tzinfo=UTC)

    with patch("ai_agent_bridge._worktree_brief._run_git") as run_git_mock, patch(
        "ai_agent_bridge._worktree_brief._utcnow", return_value=fixed_now
    ):
        run_git_mock.side_effect = [
            "abc123def456",
            "2 5",
        ]
        output_path = write_worktree_brief(tmp_path, "issue-1192-c5c6")

    assert output_path == tmp_path / ".codex-worktree-brief.yaml"
    loaded = yaml.safe_load(output_path.read_text(encoding="utf-8"))
    assert loaded == {
        "worktree_path": str(tmp_path),
        "main_branch": "main",
        "main_head_sha": "abc123def456",
        "divergence": {
            "main_ahead": 2,
            "worktree_ahead": 5,
        },
        "task_id": "issue-1192-c5c6",
        "generated_at": "2026-04-12T09:30:00Z",
    }


def test_write_worktree_brief_calculates_divergence_from_git_commands(tmp_path):
    with patch("ai_agent_bridge._worktree_brief._run_git") as run_git_mock:
        run_git_mock.side_effect = [
            "deadbeef",
            "7 3",
        ]
        write_worktree_brief(tmp_path, "task-123")

    assert run_git_mock.call_args_list == [
        call(tmp_path, "rev-parse", "main"),
        call(tmp_path, "rev-list", "--left-right", "--count", "main...HEAD"),
    ]
