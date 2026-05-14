from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.quality import pipeline  # noqa: E402
from scripts.quality.pipeline import _backfill_one  # noqa: E402


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def test_inject_failure_restores_seed_json_for_1212(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression for #1212: inject failure must not leave research seed JSON dirty."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")

    module_rel = "src/content/docs/cloud/test/module-test.md"
    module_path = repo / module_rel
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text(
        "---\n"
        "title: Module Test\n"
        "sidebar:\n"
        "  order: 1\n"
        "---\n\n"
        "Original body.\n",
        encoding="utf-8",
    )
    _git(repo, "add", module_rel)
    _git(repo, "commit", "-m", "seed module")

    monkeypatch.setattr(pipeline, "_REPO_ROOT", repo)
    monkeypatch.setattr(pipeline, "_CONTENT_ROOT", repo / "src" / "content" / "docs")

    module_key = "cloud/test/module-test"
    seed_rel = f"docs/citation-seeds/{module_key.replace('/', '-')}.json"
    seed_path = repo / seed_rel

    def fake_subcommand(
        module_key_arg: str,
        sub: str,
        *,
        agent: str | None = None,
    ) -> dict[str, Any]:
        del agent
        assert module_key_arg == module_key
        if sub == "research":
            seed_path.parent.mkdir(parents=True, exist_ok=True)
            seed_path.write_text(
                '{"module_key": "cloud/test/module-test", "claims": []}\n',
                encoding="utf-8",
            )
            return {"ok": True, "stderr": "", "stdout": "", "returncode": 0}
        if sub == "inject":
            return {
                "ok": False,
                "stderr": "inject failed before writing module",
                "stdout": "",
                "returncode": 1,
            }
        raise AssertionError(f"unexpected subcommand: {sub}")

    monkeypatch.setattr(pipeline, "_run_citation_subcommand", fake_subcommand)

    outcome = _backfill_one({"slug": "module-test", "module_path": module_rel}, agent=None)

    assert outcome["done"] is False
    assert outcome["ok"] is False
    assert outcome["stage_failed"] == "inject"
    assert _git(repo, "status", "--porcelain") == ""


def test_research_failure_after_seed_write_restores_seed_for_1212(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression for #1212: failed research may still leave a seed JSON behind."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")

    module_rel = "src/content/docs/cloud/test/module-test.md"
    module_path = repo / module_rel
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text(
        "---\n"
        "title: Module Test\n"
        "sidebar:\n"
        "  order: 1\n"
        "---\n\n"
        "Original body.\n",
        encoding="utf-8",
    )
    _git(repo, "add", module_rel)
    _git(repo, "commit", "-m", "seed module")

    monkeypatch.setattr(pipeline, "_REPO_ROOT", repo)
    monkeypatch.setattr(pipeline, "_CONTENT_ROOT", repo / "src" / "content" / "docs")

    module_key = "cloud/test/module-test"
    seed_rel = f"docs/citation-seeds/{module_key.replace('/', '-')}.json"
    seed_path = repo / seed_rel

    def fake_subcommand(
        module_key_arg: str,
        sub: str,
        *,
        agent: str | None = None,
    ) -> dict[str, Any]:
        del agent
        assert module_key_arg == module_key
        if sub == "research":
            # #1212: simulate citation_backfill writing the seed, then crashing.
            seed_path.parent.mkdir(parents=True, exist_ok=True)
            seed_path.write_text(
                '{"module_key": "cloud/test/module-test", "claims": []}\n',
                encoding="utf-8",
            )
            return {
                "ok": False,
                "stderr": "research crashed after seed write",
                "stdout": "",
                "returncode": 1,
            }
        raise AssertionError(f"unexpected subcommand: {sub}")

    monkeypatch.setattr(pipeline, "_run_citation_subcommand", fake_subcommand)

    outcome = _backfill_one({"slug": "module-test", "module_path": module_rel}, agent=None)

    assert outcome["done"] is False
    assert outcome["ok"] is False
    assert outcome["stage_failed"] == "research"
    assert _git(repo, "status", "--porcelain") == ""
