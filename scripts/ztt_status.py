#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

import yaml


MODULE_RE = re.compile(r"module-(\d+)\.(\d+)-(.+)\.md$")


def _extract_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    _, _, rest = text.partition("---\n")
    frontmatter, _, _ = rest.partition("\n---\n")
    try:
        data = yaml.safe_load(frontmatter) or {}
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def _module_lab_id(frontmatter: dict) -> str | None:
    lab = frontmatter.get("lab")
    if isinstance(lab, str) and lab.strip():
        return lab.strip()
    if isinstance(lab, dict):
        for key in ("id", "name", "slug"):
            value = lab.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _module_sort_key(path: Path) -> tuple[int, int, str]:
    match = MODULE_RE.fullmatch(path.name)
    if not match:
        return (999, 999, path.name)
    return (int(match.group(1)), int(match.group(2)), match.group(3))


def _module_label(path: Path) -> str:
    match = MODULE_RE.fullmatch(path.name)
    if not match:
        return path.stem
    return f"{match.group(1)}.{match.group(2)} {match.group(3)}"


def _module_key(path: Path, docs_root: Path) -> str:
    rel = path.relative_to(docs_root).as_posix()
    return rel[:-3] if rel.endswith(".md") else rel


def _git_head_for_file(repo_root: Path, path: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", str(path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def build_status(repo_root: Path) -> dict:
    docs_root = repo_root / "src" / "content" / "docs"
    en_dir = docs_root / "prerequisites" / "zero-to-terminal"
    uk_dir = docs_root / "uk" / "prerequisites" / "zero-to-terminal"
    fact_ledger_dir = repo_root / ".pipeline" / "fact-ledgers"
    lab_state = _load_yaml(repo_root / ".pipeline" / "lab-state.yaml").get("labs", {})

    en_modules = sorted(
        [p for p in en_dir.glob("module-*.md") if p.is_file()],
        key=_module_sort_key,
    )

    theory_modules: list[dict] = []
    labs: list[dict] = []
    uk_modules: list[dict] = []

    for module_path in en_modules:
        frontmatter = _extract_frontmatter(module_path)
        module_key = _module_key(module_path, docs_root)
        ledger_name = module_key.replace("/", "__") + ".json"
        ledger_path = fact_ledger_dir / ledger_name
        audited = ledger_path.exists()

        theory_modules.append(
            {
                "label": _module_label(module_path),
                "module_key": module_key,
                "path": module_path.as_posix(),
                "audited": audited,
                "status": "audited" if audited else "pending",
            }
        )

        lab_id = _module_lab_id(frontmatter)
        if lab_id:
            lab_entry = lab_state.get(lab_id, {})
            phase = str(lab_entry.get("phase", "pending"))
            severity = str(lab_entry.get("severity", "-"))
            clean = phase == "done" and severity == "clean"
            labs.append(
                {
                    "lab_id": lab_id,
                    "module_key": module_key,
                    "phase": phase,
                    "severity": severity,
                    "status": "clean" if clean else "pending",
                }
            )

        uk_path = uk_dir / module_path.name
        if not uk_path.exists():
            uk_modules.append(
                {
                    "label": _module_label(module_path),
                    "module_key": module_key,
                    "status": "missing",
                    "uk_path": uk_path.as_posix(),
                }
            )
            continue

        uk_frontmatter = _extract_frontmatter(uk_path)
        tracked_en_file = uk_frontmatter.get("en_file")
        tracked_en_commit = str(uk_frontmatter.get("en_commit", "")).strip().strip('"')
        en_head = _git_head_for_file(repo_root, module_path)

        if tracked_en_file != module_path.relative_to(repo_root).as_posix():
            uk_status = "stale"
        elif tracked_en_commit and en_head and tracked_en_commit == en_head:
            uk_status = "synced"
        elif not tracked_en_commit or not en_head:
            uk_status = "unknown"
        else:
            uk_status = "stale"

        uk_modules.append(
            {
                "label": _module_label(module_path),
                "module_key": module_key,
                "status": uk_status,
                "uk_path": uk_path.as_posix(),
                "en_commit": en_head,
                "uk_en_commit": tracked_en_commit,
            }
        )

    theory_present = len(theory_modules)
    theory_audited = sum(1 for item in theory_modules if item["audited"])
    lab_total = len(labs)
    lab_clean = sum(1 for item in labs if item["status"] == "clean")
    uk_total = len(uk_modules)
    uk_synced = sum(1 for item in uk_modules if item["status"] == "synced")
    uk_missing = sum(1 for item in uk_modules if item["status"] == "missing")
    uk_stale = sum(1 for item in uk_modules if item["status"] == "stale")
    uk_unknown = sum(1 for item in uk_modules if item["status"] == "unknown")

    return {
        "track": "zero-to-terminal",
        "theory": {
            "present": theory_present,
            "audited": theory_audited,
            "ready": theory_present > 0 and theory_present == theory_audited,
            "modules": theory_modules,
        },
        "labs": {
            "total": lab_total,
            "clean": lab_clean,
            "ready": lab_total == lab_clean,
            "items": labs,
        },
        "ukrainian": {
            "total": uk_total,
            "synced": uk_synced,
            "missing": uk_missing,
            "stale": uk_stale,
            "unknown": uk_unknown,
            "sync_clean": uk_missing == 0 and uk_stale == 0 and uk_unknown == 0,
            "modules": uk_modules,
        },
        "ready": {
            "english_production_bar": theory_present > 0 and theory_present == theory_audited and lab_total == lab_clean,
            "ukrainian_sync_clean": uk_missing == 0 and uk_stale == 0 and uk_unknown == 0,
        },
    }


def _print_status(data: dict) -> None:
    theory = data["theory"]
    labs = data["labs"]
    ukrainian = data["ukrainian"]
    ready = data["ready"]

    print("Zero to Terminal Status")
    print()
    print(
        f"English theory: {theory['audited']}/{theory['present']} audited"
    )
    print(f"Labs: {labs['clean']}/{labs['total']} clean")
    print(
        f"Ukrainian sync: {ukrainian['synced']}/{ukrainian['total']} synced"
        f" | missing={ukrainian['missing']} stale={ukrainian['stale']} unknown={ukrainian['unknown']}"
    )
    print()
    print(
        f"English production bar: {'YES' if ready['english_production_bar'] else 'NO'}"
    )
    print(
        f"Ukrainian sync clean: {'YES' if ready['ukrainian_sync_clean'] else 'NO'}"
    )
    print()

    print("Theory")
    for item in theory["modules"]:
        print(f"  {item['label']:<28} {item['status']}")
    print()

    print("Labs")
    for item in labs["items"]:
        print(f"  {item['lab_id']:<28} {item['status']}")
    print()

    print("Ukrainian")
    for item in ukrainian["modules"]:
        print(f"  {item['label']:<28} {item['status']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Show Zero to Terminal readiness status")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of human output")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args(argv)

    data = build_status(args.repo_root.resolve())
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        _print_status(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
