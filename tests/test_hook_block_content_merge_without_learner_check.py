"""Tests for `.claude/hooks/block-content-merge-without-learner-check.sh`.

The hook fires on `gh pr merge` Bash commands. For content PRs (any file
under ``src/content/docs/**``), it requires the PR body to contain a
``## Learner check`` section with a markdown blockquote of >= 30 chars
whose text appears verbatim in at least one touched module file.

These tests bypass the live `gh` CLI via two env overrides:

- ``KUBEDOJO_HOOK_GH_JSON`` — path to a JSON file used in place of
  ``gh pr view --json …`` output.
- ``KUBEDOJO_HOOK_FILE_FIXTURE_DIR`` — directory holding the touched
  files' contents at the same relative paths, used in place of
  ``git show <oid>:<path>``.
"""
import json
import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK = REPO_ROOT / ".claude" / "hooks" / "block-content-merge-without-learner-check.sh"
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


MODULE_BODY = (
    "---\ntitle: Intro to Pods\n---\n\n"
    "A Pod is the smallest deployable compute unit in Kubernetes. "
    "Pods host one or more tightly coupled containers that share network "
    "and storage. Most workloads run inside a single-container Pod managed "
    "by a Deployment.\n\n"
    "## Why beginners stumble\n\n"
    "The biggest source of confusion is that a Pod is not a container — "
    "the container runs inside the Pod, and Kubernetes never schedules a "
    "container directly.\n"
)


def test_non_bash_tool_is_ignored(tmp_path: Path) -> None:
    payload = {
        "tool_name": "Read",
        "tool_input": {"file_path": "/etc/hosts"},
    }
    result = subprocess.run(
        [BASH, str(HOOK)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        cwd=tmp_path,
    )
    assert result.returncode == 0
    assert result.stderr == ""


def test_command_without_pr_merge_is_ignored(tmp_path: Path) -> None:
    result = run_hook(
        "git status",
        pr_json=None,
        fixture_files=None,
        tmp_path=tmp_path,
    )
    assert result.returncode == 0


def test_non_content_pr_is_allowed(tmp_path: Path) -> None:
    pr = {
        "body": "Refactors the auth helper.",
        "files": [{"path": "scripts/auth.py"}],
        "headRefOid": "abc123",
        "title": "feat: extract auth helper",
        "number": 9001,
    }
    result = run_hook(
        "gh pr merge 9001 --squash",
        pr_json=pr,
        fixture_files=None,
        tmp_path=tmp_path,
    )
    assert result.returncode == 0, result.stderr


def test_content_pr_without_learner_check_is_denied(tmp_path: Path) -> None:
    pr = {
        "body": "## Summary\n\nRewrites the Pod intro.\n",
        "files": [{"path": "src/content/docs/k8s/cka/module-intro-pods.md"}],
        "headRefOid": "abc123",
        "title": "content: rewrite pod intro",
        "number": 9002,
    }
    result = run_hook(
        "gh pr merge 9002 --squash",
        pr_json=pr,
        fixture_files={
            "src/content/docs/k8s/cka/module-intro-pods.md": MODULE_BODY,
        },
        tmp_path=tmp_path,
    )
    assert result.returncode == 2
    assert "missing a '## Learner check' section" in result.stderr


def test_learner_check_too_short_is_denied(tmp_path: Path) -> None:
    pr = {
        "body": (
            "## Summary\n\nRewrites the Pod intro.\n\n"
            "## Learner check\n\n"
            "> too short\n\n"
            "Beginners get this.\n"
        ),
        "files": [{"path": "src/content/docs/k8s/cka/module-intro-pods.md"}],
        "headRefOid": "abc123",
        "title": "content: rewrite pod intro",
        "number": 9003,
    }
    result = run_hook(
        "gh pr merge 9003 --squash",
        pr_json=pr,
        fixture_files={
            "src/content/docs/k8s/cka/module-intro-pods.md": MODULE_BODY,
        },
        tmp_path=tmp_path,
    )
    assert result.returncode == 2
    assert ">= 30 chars" in result.stderr


def test_learner_check_quote_not_in_file_is_denied(tmp_path: Path) -> None:
    fake_quote = "Pods are wrappers around the kubelet daemon's runtime API."
    pr = {
        "body": (
            "## Summary\n\nRewrites the Pod intro.\n\n"
            "## Learner check\n\n"
            f"> {fake_quote}\n\n"
            "Beginners think this is wrong.\n"
        ),
        "files": [{"path": "src/content/docs/k8s/cka/module-intro-pods.md"}],
        "headRefOid": "abc123",
        "title": "content: rewrite pod intro",
        "number": 9004,
    }
    result = run_hook(
        "gh pr merge 9004 --squash",
        pr_json=pr,
        fixture_files={
            "src/content/docs/k8s/cka/module-intro-pods.md": MODULE_BODY,
        },
        tmp_path=tmp_path,
    )
    assert result.returncode == 2
    assert "No quote in '## Learner check' was found verbatim" in result.stderr


def test_learner_check_quote_in_file_is_allowed(tmp_path: Path) -> None:
    real_quote = (
        "A Pod is the smallest deployable compute unit in Kubernetes."
    )
    pr = {
        "body": (
            "## Summary\n\nRewrites the Pod intro.\n\n"
            "## Learner check\n\n"
            f"> {real_quote}\n\n"
            "A first-time reader needs to know this line frames the "
            "rest of the module.\n"
        ),
        "files": [{"path": "src/content/docs/k8s/cka/module-intro-pods.md"}],
        "headRefOid": "abc123",
        "title": "content: rewrite pod intro",
        "number": 9005,
    }
    result = run_hook(
        "gh pr merge 9005 --squash",
        pr_json=pr,
        fixture_files={
            "src/content/docs/k8s/cka/module-intro-pods.md": MODULE_BODY,
        },
        tmp_path=tmp_path,
    )
    assert result.returncode == 0, result.stderr


def test_learner_check_quote_in_one_of_many_files_is_allowed(tmp_path: Path) -> None:
    real_quote = (
        "The biggest source of confusion is that a Pod is not a container"
    )
    pr = {
        "body": (
            "## Learner check\n\n"
            f"> {real_quote}\n"
        ),
        "files": [
            {"path": "src/content/docs/k8s/cka/module-intro-pods.md"},
            {"path": "src/content/docs/k8s/cka/module-pod-lifecycle.md"},
        ],
        "headRefOid": "abc123",
        "title": "content: rewrite pod intro + lifecycle",
        "number": 9006,
    }
    result = run_hook(
        "gh pr merge 9006 --squash",
        pr_json=pr,
        fixture_files={
            "src/content/docs/k8s/cka/module-intro-pods.md": MODULE_BODY,
            "src/content/docs/k8s/cka/module-pod-lifecycle.md": "lifecycle module body\n",
        },
        tmp_path=tmp_path,
    )
    assert result.returncode == 0, result.stderr


def test_gh_failure_fails_open(tmp_path: Path) -> None:
    # When `gh pr view` itself fails (auth, network, no PR on branch), the
    # hook must fail open — a quality gate should not trap the orchestrator
    # behind transient infra. We simulate the failure by passing a stub PR
    # JSON file that doesn't parse, which the hook treats as "couldn't
    # resolve PR" → PASS.
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
