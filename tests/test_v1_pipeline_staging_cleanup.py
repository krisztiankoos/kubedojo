from __future__ import annotations

import builtins
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import v1_pipeline

builtins.print = v1_pipeline._original_print


def test_run_module_drops_orphan_staging_before_write_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    docs_root = tmp_path / "src" / "content" / "docs"
    module_path = docs_root / "platform" / "foundations" / "module-1.1-test.md"
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text("# Module\n", encoding="utf-8")

    staging_path = module_path.with_suffix(".staging.md")
    staging_path.write_text("stale staged draft", encoding="utf-8")

    module_key = "platform/foundations/module-1.1-test"
    state = {"modules": {module_key: {"phase": "write", "errors": []}}}
    observed: dict[str, bool] = {}

    def fake_step_write(*args, **kwargs):
        observed["staging_exists_during_write"] = staging_path.exists()
        return None

    monkeypatch.setattr(v1_pipeline, "CONTENT_ROOT", docs_root)
    monkeypatch.setattr(v1_pipeline, "load_rubric_profile_for_module", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(v1_pipeline, "module_key_from_path", lambda _path: module_key)
    monkeypatch.setattr(v1_pipeline, "save_state", lambda _state: None)
    monkeypatch.setattr(v1_pipeline, "step_write", fake_step_write)

    ok = v1_pipeline.run_module(module_path, state, max_retries=0, write_only=True)

    assert not ok
    assert observed["staging_exists_during_write"] is False
    assert not staging_path.exists()
