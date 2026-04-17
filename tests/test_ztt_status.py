from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
from pathlib import Path

import yaml


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "ztt_status.py"
    spec = importlib.util.spec_from_file_location("ztt_status", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ztt_status = _load_module()
build_status = ztt_status.build_status


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _module_frontmatter(*, lab_id: str | None = None) -> str:
    lines = [
        "---",
        'title: "Example"',
    ]
    if lab_id:
        lines.extend(
            [
                "lab:",
                f'  id: "{lab_id}"',
                f'  url: "https://killercoda.com/kubedojo/scenario/{lab_id}"',
                '  duration: "20 min"',
                '  difficulty: "beginner"',
                '  environment: "ubuntu"',
            ]
        )
    lines.extend(["---", "", "body"])
    return "\n".join(lines)


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


def test_build_status_reports_ready_english_and_synced_ukrainian(tmp_path: Path) -> None:
    repo_root = tmp_path
    _init_repo(repo_root)

    en_dir = repo_root / "src/content/docs/prerequisites/zero-to-terminal"
    uk_dir = repo_root / "src/content/docs/uk/prerequisites/zero-to-terminal"
    fact_dir = repo_root / ".pipeline/fact-ledgers"

    en_one = en_dir / "module-0.1-alpha.md"
    en_two = en_dir / "module-0.2-beta.md"
    _write(en_one, _module_frontmatter())
    _write(en_two, _module_frontmatter(lab_id="prereq-0.2-beta"))

    _git(repo_root, "add", ".")
    _git(repo_root, "commit", "-m", "add english")

    en_one_commit = _git(repo_root, "log", "-1", "--format=%H", "--", str(en_one))
    en_two_commit = _git(repo_root, "log", "-1", "--format=%H", "--", str(en_two))

    _write(
        uk_dir / en_one.name,
        "\n".join(
            [
                "---",
                f'en_commit: "{en_one_commit}"',
                f'en_file: "{en_one.relative_to(repo_root).as_posix()}"',
                "---",
                "",
                "body",
            ]
        ),
    )
    _write(
        uk_dir / en_two.name,
        "\n".join(
            [
                "---",
                f'en_commit: "{en_two_commit}"',
                f'en_file: "{en_two.relative_to(repo_root).as_posix()}"',
                "---",
                "",
                "body",
            ]
        ),
    )
    _write(fact_dir / "prerequisites__zero-to-terminal__module-0.1-alpha.json", "{}")
    _write(fact_dir / "prerequisites__zero-to-terminal__module-0.2-beta.json", "{}")

    lab_state = {
        "labs": {
            "prereq-0.2-beta": {
                "phase": "done",
                "severity": "clean",
                "module": "prerequisites/zero-to-terminal/module-0.2-beta",
            }
        }
    }
    _write(repo_root / ".pipeline/lab-state.yaml", yaml.dump(lab_state, sort_keys=False))

    status = build_status(repo_root)

    assert status["theory"]["present"] == 2
    assert status["theory"]["audited"] == 2
    assert status["theory"]["ready"] is True
    assert status["labs"]["clean"] == 1
    assert status["labs"]["ready"] is True
    assert status["ukrainian"]["synced"] == 2
    assert status["ukrainian"]["sync_clean"] is True
    assert status["ready"]["english_production_bar"] is True
    assert status["ready"]["ukrainian_sync_clean"] is True


def test_build_status_flags_stale_and_missing_ukrainian_files(tmp_path: Path) -> None:
    repo_root = tmp_path
    _init_repo(repo_root)

    en_dir = repo_root / "src/content/docs/prerequisites/zero-to-terminal"
    uk_dir = repo_root / "src/content/docs/uk/prerequisites/zero-to-terminal"
    fact_dir = repo_root / ".pipeline/fact-ledgers"

    en_one = en_dir / "module-0.1-alpha.md"
    en_two = en_dir / "module-0.2-beta.md"
    _write(en_one, _module_frontmatter())
    _write(en_two, _module_frontmatter())

    _git(repo_root, "add", ".")
    _git(repo_root, "commit", "-m", "add english")

    current_commit = _git(repo_root, "log", "-1", "--format=%H", "--", str(en_one))
    _write(
        uk_dir / en_one.name,
        "\n".join(
            [
                "---",
                'en_commit: "deadbeef"',
                f'en_file: "{en_one.relative_to(repo_root).as_posix()}"',
                "---",
                "",
                "body",
            ]
        ),
    )
    _write(fact_dir / "prerequisites__zero-to-terminal__module-0.1-alpha.json", "{}")
    _write(fact_dir / "prerequisites__zero-to-terminal__module-0.2-beta.json", "{}")

    status = build_status(repo_root)

    assert current_commit
    assert status["ukrainian"]["missing"] == 1
    assert status["ukrainian"]["stale"] == 1
    assert status["ukrainian"]["sync_clean"] is False
    module_statuses = {item["module_key"]: item["status"] for item in status["ukrainian"]["modules"]}
    assert module_statuses["prerequisites/zero-to-terminal/module-0.1-alpha"] == "stale"
    assert module_statuses["prerequisites/zero-to-terminal/module-0.2-beta"] == "missing"


def test_cli_json_output(tmp_path: Path) -> None:
    repo_root = tmp_path
    _init_repo(repo_root)
    en_dir = repo_root / "src/content/docs/prerequisites/zero-to-terminal"
    _write(en_dir / "module-0.1-alpha.md", _module_frontmatter())
    _git(repo_root, "add", ".")
    _git(repo_root, "commit", "-m", "add english")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/ztt_status.py",
            "--json",
            "--repo-root",
            str(repo_root),
        ],
        cwd="/Users/krisztiankoos/projects/kubedojo",
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)
    assert data["track"] == "zero-to-terminal"
    assert data["theory"]["present"] == 1
