import importlib.util
import sys
from pathlib import Path


def _load_check_citations():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "check_citations.py"
    spec = importlib.util.spec_from_file_location("check_citations_test", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_quality_check_citations():
    module_path = (
        Path(__file__).resolve().parent.parent
        / "scripts"
        / "quality"
        / "check_citations.py"
    )
    spec = importlib.util.spec_from_file_location(
        "quality_check_citations_test", module_path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


check_citations = _load_check_citations()
check_file = check_citations.check_file
quality_check_citations = _load_quality_check_citations()


def test_check_citations_passes_with_sources_and_war_story_source(tmp_path: Path) -> None:
    path = tmp_path / "module.md"
    path.write_text(
        """# Demo

## Why This Module Matters

> **War Story: Test Incident**
> Something happened.
> **Source**: [Example](https://example.com/story)

Body citation.[^1]

## Sources

- [Example](https://example.com/story)

[^1]: Supporting note.
""",
        encoding="utf-8",
    )

    result = check_file(path)
    assert result["passes"] is True
    assert result["issues"] == []


def test_check_citations_fails_without_sources_section(tmp_path: Path) -> None:
    path = tmp_path / "module.md"
    path.write_text(
        """# Demo

## Why This Module Matters

> **War Story: Test Incident**
> Something happened.
""",
        encoding="utf-8",
    )

    result = check_file(path)
    assert result["passes"] is False
    assert "missing_sources_section" in result["issues"]
    assert "war_story_missing_source_line" in result["issues"]


def test_quality_check_citations_missing_explicit_path_returns_nonzero(
    tmp_path: Path, capsys
) -> None:
    missing = tmp_path / "does-not-exist.md"

    result = quality_check_citations.main([str(missing)])

    captured = capsys.readouterr()
    assert result == 1
    assert f"warning: {missing.resolve()} does not exist" in captured.err
    assert "No existing files were checked." in captured.err


def test_quality_check_citations_mixed_valid_and_missing_returns_nonzero(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    valid = tmp_path / "module.md"
    missing = tmp_path / "missing.md"
    valid.write_text(
        """# Demo

## Sources

- [Example](https://example.com/story)
""",
        encoding="utf-8",
    )

    def fake_check_url(url: str):
        return quality_check_citations.CitationCheck(
            file="",
            url=url,
            status=200,
            final_url=url,
            final_host="example.com",
            original_host="example.com",
            ok=True,
            error=None,
        )

    monkeypatch.setattr(quality_check_citations, "check_url", fake_check_url)

    result = quality_check_citations.main([str(valid), str(missing)])

    captured = capsys.readouterr()
    assert result == 1
    assert "OK" in captured.out
    assert f"warning: {missing.resolve()} does not exist" in captured.err
    assert "1 provided path(s) were missing." in captured.err
