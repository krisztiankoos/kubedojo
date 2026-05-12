import json
import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK = REPO_ROOT / ".claude" / "hooks" / "block-branch-create-in-primary.sh"


def run_hook(command: str, cwd: Path, primary: Path) -> subprocess.CompletedProcess[str]:
    payload = {
        "tool_name": "Bash",
        "tool_input": {
            "command": command,
            "cwd": str(cwd),
        },
    }
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(primary)
    return subprocess.run(
        ["bash", str(HOOK)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        env=env,
        cwd=primary,
    )


def test_primary_checkout_b_denied(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    primary.mkdir()

    result = run_hook("git checkout -b foo", primary, primary)

    assert result.returncode != 0
    assert "branch creation in the primary repo dir is blocked" in result.stderr


def test_worktree_checkout_b_allowed(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    worktree = primary / ".worktrees" / "whatever"
    worktree.mkdir(parents=True)

    result = run_hook("git checkout -b foo", worktree, primary)

    assert result.returncode == 0
    assert result.stderr == ""


def test_primary_checkout_existing_branch_allowed(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    primary.mkdir()

    result = run_hook("git checkout main", primary, primary)

    assert result.returncode == 0
    assert result.stderr == ""


def test_primary_branch_create_without_switch_allowed(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    primary.mkdir()

    result = run_hook("git branch foo", primary, primary)

    assert result.returncode == 0
    assert result.stderr == ""


def test_primary_switch_c_denied(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    primary.mkdir()

    result = run_hook("git switch -c foo", primary, primary)

    assert result.returncode != 0
    assert "branch creation in the primary repo dir is blocked" in result.stderr


def test_primary_switch_existing_branch_allowed(tmp_path: Path) -> None:
    primary = tmp_path / "kubedojo"
    primary.mkdir()

    result = run_hook("git switch main", primary, primary)

    assert result.returncode == 0
    assert result.stderr == ""
