from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "uk_sync.py"
    spec = importlib.util.spec_from_file_location("uk_sync", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


uk_sync = _load_module()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _init_repo(repo_root: Path) -> None:
    _git(repo_root, "init")
    _git(repo_root, "config", "user.email", "test@example.com")
    _git(repo_root, "config", "user.name", "Test User")


def test_detect_sync_commit_mismatch_is_warning_by_default_but_stale_in_strict_mode(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path
    _init_repo(repo_root)

    content_root = repo_root / "src" / "content" / "docs"
    uk_root = content_root / "uk"
    en_path = content_root / "prerequisites/zero-to-terminal/module-0.1-alpha.md"
    uk_path = uk_root / "prerequisites/zero-to-terminal/module-0.1-alpha.md"

    _write(en_path, "---\ntitle: EN\n---\n\nbody\n")
    _git(repo_root, "add", ".")
    _git(repo_root, "commit", "-m", "add english")
    first_commit = _git(repo_root, "log", "-1", "--format=%H", "--", str(en_path))

    _write(
        uk_path,
        "\n".join(
            [
                "---",
                f'en_commit: "{first_commit}"',
                f'en_file: "{en_path.relative_to(repo_root).as_posix()}"',
                "---",
                "",
                "body",
            ]
        ),
    )

    _write(en_path, "---\ntitle: EN\n---\n\nupdated body\n")
    _git(repo_root, "add", str(en_path))
    _git(repo_root, "commit", "-m", "update english")

    monkeypatch.setattr(uk_sync, "REPO_ROOT", repo_root)
    monkeypatch.setattr(uk_sync, "CONTENT_ROOT", content_root)
    monkeypatch.setattr(uk_sync, "UK_ROOT", uk_root)

    default_report = uk_sync.detect_sync(uk_path)
    strict_report = uk_sync.detect_sync(uk_path, strict_commit=True)

    assert default_report is not None
    assert strict_report is not None
    assert default_report.status == "synced"
    assert strict_report.status == "stale"
    assert any(issue.issue_type == "STALE_COMMIT" for issue in strict_report.issues)
