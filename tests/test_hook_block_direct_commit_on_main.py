import json
import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK = REPO_ROOT / ".claude" / "hooks" / "block-direct-commit-on-main.sh"
BASH = "/bin/bash"


def init_git_main(primary: Path) -> None:
    subprocess.run(["git", "init", "-b", "main", str(primary)], check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "agent@example.test"],
        cwd=primary,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Agent"],
        cwd=primary,
        check=True,
        capture_output=True,
    )
    (primary / "README.md").write_text("test repo\n")
    subprocess.run(["git", "add", "README.md"], cwd=primary, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=primary,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "checkout", "main"], cwd=primary, check=True, capture_output=True)


def run_hook_payload(
    payload: dict[str, object],
    primary: Path,
    *,
    cwd: Path | None = None,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(primary)
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [BASH, str(HOOK)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        env=env,
        cwd=cwd or primary,
    )


def run_hook(command: str, cwd: Path, primary: Path) -> subprocess.CompletedProcess[str]:
    payload = {
        "tool_name": "Bash",
        "tool_input": {
            "command": command,
            "cwd": str(cwd),
        },
    }
    return run_hook_payload(payload, primary, cwd=cwd)


def test_main_commit_no_ref_denied(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    init_git_main(primary)

    result = run_hook('git commit -m "fix: thing"', primary, primary)

    assert result.returncode == 2
    assert "direct commit to main without PR ref is blocked" in result.stderr
    assert "feedback_no_direct_push_to_main.md" in result.stderr


def test_main_commit_pr_ref_allowed(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    init_git_main(primary)

    result = run_hook('git commit -m "feat(x): blah (#1234)"', primary, primary)

    assert result.returncode == 0


def test_main_commit_docs_status_allowed(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    init_git_main(primary)

    result = run_hook('git commit -m "docs(status): handoff"', primary, primary)

    assert result.returncode == 0


def test_main_commit_handoff_prefix_allowed(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    init_git_main(primary)

    result = run_hook('git commit -m "handoff: session-N"', primary, primary)

    assert result.returncode == 0


def test_main_commit_backfill_prefix_allowed(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    init_git_main(primary)

    result = run_hook('git commit -m "backfill citations"', primary, primary)

    assert result.returncode == 0


def test_main_commit_backfill_false_positive_denied(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    init_git_main(primary)

    result = run_hook('git commit -m "backfilling: not a pipeline commit"', primary, primary)

    assert result.returncode == 2
    assert "direct commit to main without PR ref is blocked" in result.stderr


def test_main_commit_short_flag_cluster_am_denied(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    init_git_main(primary)

    result = run_hook('git commit -am "fix: thing"', primary, primary)

    assert result.returncode == 2
    assert "direct commit to main without PR ref is blocked" in result.stderr


def test_main_commit_backfill_prefix_allowed_with_colon(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    init_git_main(primary)

    result = run_hook('git commit -m "backfill: real pipeline commit"', primary, primary)

    assert result.returncode == 0


def test_main_commit_short_flag_cluster_am_with_pr_ref_allowed(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    init_git_main(primary)

    result = run_hook('git commit -am "fix: thing (#123)"', primary, primary)

    assert result.returncode == 0


def test_feature_branch_commit_allowed(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    init_git_main(primary)
    subprocess.run(["git", "checkout", "-b", "feature"], cwd=primary, check=True, capture_output=True)

    result = run_hook('git commit -m "fix: thing"', primary, primary)

    assert result.returncode == 0
    assert result.stderr == ""


def test_commit_amend_no_message_allowed(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    init_git_main(primary)

    result = run_hook("git commit --amend --no-edit", primary, primary)

    assert result.returncode == 0
    assert "not introspected" in result.stderr


def test_commit_F_file_allowed(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    init_git_main(primary)
    message = tmp_path / "msg.txt"
    message.write_text("fix: thing\n")

    result = run_hook(f"git commit -F {message}", primary, primary)

    assert result.returncode == 0
    assert "not introspected" in result.stderr


def test_commit_no_m_flag_allowed(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    init_git_main(primary)

    result = run_hook("git commit", primary, primary)

    assert result.returncode == 0
    assert "not introspected" in result.stderr


def test_non_commit_bash_command_allowed(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    init_git_main(primary)

    result = run_hook("git log -3", primary, primary)

    assert result.returncode == 0
    assert result.stderr == ""


def test_detached_head_allowed(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    init_git_main(primary)
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=primary,
        text=True,
        check=True,
        capture_output=True,
    ).stdout.strip()
    subprocess.run(["git", "checkout", commit], cwd=primary, check=True, capture_output=True)

    result = run_hook('git commit -m "fix: thing"', primary, primary)

    assert result.returncode == 0
    assert result.stderr == ""
