from __future__ import annotations

from pathlib import Path

import yaml


def _read_frontmatter(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise AssertionError(f"invalid frontmatter for {path}")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise AssertionError(f"invalid frontmatter for {path}") from exc

    return yaml.safe_load("\n".join(lines[1:end])) or {}
