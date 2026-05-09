"""Git remote verification helpers for agent-orchestrated pushes."""
from __future__ import annotations

import subprocess
from pathlib import Path


def verify_pushed_to_remote(
    branch_name: str,
    expected_local_sha: str,
    *,
    repo: Path | None = None,
) -> tuple[bool, str | None, str | None]:
    """Return whether ``origin/<branch_name>`` points at ``expected_local_sha``."""
    cwd = repo or Path.cwd()
    result = subprocess.run(
        ["git", "ls-remote", "origin", branch_name],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return False, None, (result.stderr or result.stdout or "git ls-remote failed").strip()

    remote_sha: str | None = None
    expected_ref = f"refs/heads/{branch_name}"
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        sha, ref = parts[0], parts[1]
        if ref == expected_ref or ref.endswith(f"/{branch_name}"):
            remote_sha = sha
            break

    if remote_sha is None:
        return False, None, f"origin has no branch named {branch_name!r}"
    if remote_sha != expected_local_sha:
        return (
            False,
            remote_sha,
            f"origin/{branch_name} is {remote_sha[:12]}, expected {expected_local_sha[:12]}",
        )
    return True, remote_sha, None


def verify_current_branch_pushed(repo: Path) -> tuple[bool, str | None]:
    """Verify the checked-out branch in ``repo`` is present at the same SHA on origin."""
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if branch.returncode != 0:
        return False, f"could not read current branch: {branch.stderr.strip()}"
    branch_name = branch.stdout.strip()
    if not branch_name or branch_name == "HEAD":
        return False, "worktree is detached; cannot verify remote branch push"

    local = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if local.returncode != 0:
        return False, f"could not read local HEAD: {local.stderr.strip()}"
    local_sha = local.stdout.strip()
    ok, remote_sha, error = verify_pushed_to_remote(branch_name, local_sha, repo=repo)
    if ok:
        return True, None
    if remote_sha is None:
        on_origin_main = subprocess.run(
            ["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        if on_origin_main.returncode == 0:
            return True, None
    remote_label = remote_sha[:12] if remote_sha else "missing"
    return (
        False,
        "Codex danger-mode dispatch left origin stale: "
        f"branch={branch_name} local={local_sha[:12]} remote={remote_label}; {error}",
    )
