"""Tests for per-module body-word floor sidecar behavior."""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.quality import verify_module


def _make_module(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = " ".join("word" for _ in range(3500))
    text = f"""---
title: "Test Module"
slug: c1/module
sidebar:
  order: 1
---

{body}
"""
    path.write_text(text, encoding="utf-8")
    return path


def _module_slug_for_budgets(root: Path, module_path: Path) -> str:
    return module_path.relative_to(root / "src" / "content" / "docs").as_posix().replace("/", "__")


def test_verify_module_body_word_floor_uses_default_5000(tmp_path, monkeypatch) -> None:
    module = _make_module(tmp_path / "src/content/docs/c1/module.md")
    monkeypatch.setattr(verify_module, "REPO_ROOT", tmp_path)
    result = verify_module.verify(module, skip_source_check=True, max_workers=1)
    assert result["gates"]["body_words_floor_met"] is False


def test_verify_module_body_word_floor_reads_sidecar_3000(tmp_path, monkeypatch) -> None:
    module = _make_module(tmp_path / "src/content/docs/c1/module.md")
    budgets = tmp_path / ".pipeline" / "budgets"
    budgets.mkdir(parents=True, exist_ok=True)
    budget = budgets / f"{_module_slug_for_budgets(tmp_path, module)}.json"
    budget.write_text(
        '{"body_words_min": 3000, "source_module": "src/content/docs/c1/module.md", "set_at": "2026-01-01T00:00:00+00:00"}',
        encoding="utf-8",
    )
    monkeypatch.setattr(verify_module, "REPO_ROOT", tmp_path)
    assert verify_module.verify(module, skip_source_check=True, max_workers=1)["gates"]["body_words_floor_met"] is True


def test_verify_module_body_word_floor_reads_sidecar_4000(tmp_path, monkeypatch) -> None:
    module = _make_module(tmp_path / "src/content/docs/c1/module.md")
    budgets = tmp_path / ".pipeline" / "budgets"
    budgets.mkdir(parents=True, exist_ok=True)
    budget = budgets / f"{_module_slug_for_budgets(tmp_path, module)}.json"
    budget.write_text(
        '{"body_words_min": 4000, "source_module": "src/content/docs/c1/module.md", "set_at": "2026-01-01T00:00:00+00:00"}',
        encoding="utf-8",
    )
    monkeypatch.setattr(verify_module, "REPO_ROOT", tmp_path)
    assert verify_module.verify(module, skip_source_check=True, max_workers=1)["gates"]["body_words_floor_met"] is False
