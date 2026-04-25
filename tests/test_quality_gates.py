"""Tests for ``scripts.quality.gates`` — visual-aid diff, sampling, ledger."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.quality import gates  # noqa: E402


# ---- visual-aid counting ------------------------------------------------


def test_visual_aid_count_mermaid() -> None:
    text = """\
intro

```mermaid
graph TD
  A --> B
```

middle

```mermaid
sequenceDiagram
  X->>Y: hi
```
"""
    assert gates.visual_aid_count(text)["mermaid"] == 2


def test_visual_aid_count_table() -> None:
    text = """\
| col | col |
|-----|-----|
| a   | b   |

prose

| x | y | z |
|---|---|---|
| 1 | 2 | 3 |
"""
    assert gates.visual_aid_count(text)["table"] == 2


def test_visual_aid_count_ascii_diagram_box_drawing() -> None:
    text = """\
prose

```text
┌──────┐
│ pod  │
└──────┘
```
"""
    assert gates.visual_aid_count(text)["ascii_diagram"] == 1


def test_visual_aid_count_ascii_diagram_pipe_art() -> None:
    text = """\
```
+--------+
| node   |
+--------+
| pod    |
+--------+
```
"""
    assert gates.visual_aid_count(text)["ascii_diagram"] == 1


def test_visual_aid_count_ignores_code_with_language() -> None:
    """Real code (yaml/python/etc.) must NOT count as ASCII diagram even
    if it incidentally has pipe characters or a few box-drawing chars."""
    text = """\
```yaml
spec:
  containers:
    - name: web
      image: nginx
```

```python
def f():
    return "x"
```
"""
    assert gates.visual_aid_count(text)["ascii_diagram"] == 0


def test_visual_aid_diff_pass_when_unchanged() -> None:
    text = "```mermaid\nA-->B\n```\n"
    diff = gates.visual_aid_diff(text, text)
    assert gates.regressed_metrics(diff) == []


def test_visual_aid_diff_pass_when_increased() -> None:
    before = "```mermaid\nA-->B\n```\n"
    after = before + "\n| x | y |\n|---|---|\n| 1 | 2 |\n"
    diff = gates.visual_aid_diff(before, after)
    assert gates.regressed_metrics(diff) == []
    assert diff["table"]["delta"] == 1


def test_visual_aid_diff_fail_when_mermaid_dropped() -> None:
    before = "```mermaid\nA-->B\n```\n\n```mermaid\nC-->D\n```\n"
    after = "```mermaid\nA-->B\n```\n"
    diff = gates.visual_aid_diff(before, after)
    assert "mermaid" in gates.regressed_metrics(diff)
    assert diff["mermaid"]["delta"] == -1


def test_visual_aid_diff_fail_when_table_dropped() -> None:
    before = "| a | b |\n|---|---|\n| 1 | 2 |\n"
    after = "(table replaced with prose)\n"
    diff = gates.visual_aid_diff(before, after)
    assert "table" in gates.regressed_metrics(diff)


# ---- visual-aid diff via git --------------------------------------------


@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    """Real git repo with a module on main and a quality/<slug> branch
    representing the writer's rewrite."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    for k, v in [("user.email", "t@t"), ("user.name", "t"), ("commit.gpgsign", "false")]:
        subprocess.run(["git", "config", k, v], cwd=repo, check=True)
    return repo


def _commit(repo: Path, path: str, content: str, message: str) -> None:
    p = repo / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    subprocess.run(["git", "add", path], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=repo, check=True, capture_output=True)


def _branch(repo: Path, slug: str) -> str:
    name = f"quality/{slug}"
    subprocess.run(["git", "checkout", "-b", name], cwd=repo, check=True, capture_output=True)
    return name


def test_visual_aid_diff_for_module_pass(fake_repo: Path) -> None:
    rel = "src/content/docs/foo/module-1.1-bar.md"
    before = "# title\n\n```mermaid\nA-->B\n```\n"
    after = before + "\n| a | b |\n|---|---|\n| 1 | 2 |\n"

    _commit(fake_repo, rel, before, "seed")
    _branch(fake_repo, "foo-module-1.1-bar")
    _commit(fake_repo, rel, after, "rewrite")

    result = gates.visual_aid_diff_for_module(fake_repo, "foo-module-1.1-bar", rel)
    assert result["ok"] is True
    assert result["regressed"] == []
    assert result["diff"]["table"]["delta"] == 1


def test_visual_aid_diff_for_module_fail(fake_repo: Path) -> None:
    rel = "src/content/docs/foo/module-1.2-baz.md"
    before = "# title\n\n```mermaid\nA-->B\n```\n\n```mermaid\nC-->D\n```\n"
    after = "# title\n\n```mermaid\nA-->B\n```\n"  # dropped one mermaid

    _commit(fake_repo, rel, before, "seed")
    _branch(fake_repo, "foo-module-1.2-baz")
    _commit(fake_repo, rel, after, "rewrite-strips-mermaid")

    result = gates.visual_aid_diff_for_module(fake_repo, "foo-module-1.2-baz", rel)
    assert result["ok"] is False
    assert "mermaid" in result["regressed"]


def test_visual_aid_diff_for_module_returns_error_on_bad_base_ref(fake_repo: Path) -> None:
    """A bad ``base_ref`` is a real git error — must be reported as
    ``ok=False`` with an error, NOT silently treated as greenfield. This
    is the regression guard for codex review finding #2."""
    rel = "src/content/docs/foo/module-1.5-x.md"
    _commit(fake_repo, rel, "x\n", "seed")
    _branch(fake_repo, "foo-module-1.5-x")
    _commit(fake_repo, rel, "y\n", "rewrite")

    result = gates.visual_aid_diff_for_module(
        fake_repo, "foo-module-1.5-x", rel, base_ref="nonexistent-ref",
    )
    assert result["ok"] is False
    assert "error" in result
    # Critical: the error must NOT pretend everything's fine — no diff
    # key, regressed key, or greenfield-pass should be present.
    assert "diff" not in result


def test_visual_aid_diff_for_module_greenfield_passes(fake_repo: Path) -> None:
    """A new module that doesn't exist on main passes trivially —
    nothing to regress against."""
    _commit(fake_repo, "README.md", "seed\n", "seed")
    rel = "src/content/docs/foo/module-1.3-new.md"
    _branch(fake_repo, "foo-module-1.3-new")
    _commit(fake_repo, rel, "# new module\n\n```mermaid\nA-->B\n```\n", "greenfield")

    result = gates.visual_aid_diff_for_module(fake_repo, "foo-module-1.3-new", rel)
    assert result["ok"] is True
    assert result["diff"]["mermaid"]["before"] == 0
    assert result["diff"]["mermaid"]["after"] == 1


def test_assert_visual_aids_preserved_raises_on_regression(fake_repo: Path) -> None:
    rel = "src/content/docs/foo/module-1.4-x.md"
    before = "```mermaid\nA-->B\n```\n\n```mermaid\nC-->D\n```\n"
    after = "```mermaid\nA-->B\n```\n"

    _commit(fake_repo, rel, before, "seed")
    _branch(fake_repo, "foo-module-1.4-x")
    _commit(fake_repo, rel, after, "rewrite")

    with pytest.raises(gates.GateError, match="visual-aid regression"):
        gates.assert_visual_aids_preserved(fake_repo, "foo-module-1.4-x", rel)


# ---- sampling -----------------------------------------------------------


def test_should_sample_zero_rate_always_false() -> None:
    assert gates.should_sample("any-slug", 0.0) is False


def test_should_sample_full_rate_always_true() -> None:
    assert gates.should_sample("any-slug", 1.0) is True


def test_should_sample_deterministic_per_slug() -> None:
    """Same slug + rate must return the same answer across calls."""
    rate = 0.20
    for slug in ("a", "b", "ai-mlops-foo", "k8s-cka-module-1.1"):
        first = gates.should_sample(slug, rate)
        second = gates.should_sample(slug, rate)
        assert first == second, slug


def test_should_sample_distribution_roughly_matches_rate() -> None:
    """Hash buckets should produce approximately ``rate`` fraction of trues
    over many slugs. Generous tolerance — this is a smoke-test, not a
    statistical assertion."""
    slugs = [f"slug-{i:04d}" for i in range(1000)]
    sampled = sum(1 for s in slugs if gates.should_sample(s, 0.20))
    assert 150 < sampled < 250, sampled  # 20 % ± 5 % over 1000 = [150, 250]


def test_should_sample_env_var_override(monkeypatch) -> None:
    monkeypatch.setenv("KUBEDOJO_GATES_SAMPLE_RATE", "1.0")
    assert gates.should_sample("anything", None) is True
    monkeypatch.setenv("KUBEDOJO_GATES_SAMPLE_RATE", "0.0")
    assert gates.should_sample("anything", None) is False


def test_should_sample_explicit_rate_overrides_env(monkeypatch) -> None:
    monkeypatch.setenv("KUBEDOJO_GATES_SAMPLE_RATE", "0.0")
    assert gates.should_sample("anything", 1.0) is True


# ---- ledger -------------------------------------------------------------


def test_build_ledger_row_with_sampled_pass() -> None:
    state_payload = {
        "slug": "foo-bar",
        "audit": {"teaching_score": 2.5},
        "review": {"verdict": "approve"},
        "writer": "codex",
        "reviewer": "claude",
    }
    real_llm = {
        "ok": True,
        "passed": True,
        "teaching_score": 4.3,
        "verdict": "strong",
        "model": "gemini-3-flash-preview",
    }
    row = gates.build_ledger_row(slug="foo-bar", state_payload=state_payload, real_llm_result=real_llm)
    assert row.slug == "foo-bar"
    assert row.heuristic_before == 2.5
    assert row.real_llm_sampled is True
    assert row.real_llm_teaching_score == 4.3
    assert row.real_llm_verdict == "strong"
    assert row.writer == "codex"
    assert row.reviewer == "claude"
    assert row.review_verdict == "approve"


def test_build_ledger_row_below_threshold_marks_verdict() -> None:
    state_payload = {
        "audit": {"teaching_score": 2.0},
        "review": {"verdict": "approve"},
        "writer": "codex",
        "reviewer": "claude",
    }
    real_llm = {
        "ok": True,
        "passed": False,
        "teaching_score": 3.2,
        "verdict": "adequate",
    }
    row = gates.build_ledger_row(slug="x", state_payload=state_payload, real_llm_result=real_llm)
    assert row.real_llm_verdict.endswith("below_threshold")


def test_build_ledger_row_no_sample() -> None:
    row = gates.build_ledger_row(
        slug="x",
        state_payload={"audit": {"teaching_score": 4.0}, "writer": "codex", "reviewer": "claude"},
        real_llm_result=None,
    )
    assert row.real_llm_sampled is False
    assert row.real_llm_teaching_score is None
    assert row.real_llm_verdict is None


def test_append_ledger_creates_file_with_header(tmp_path: Path) -> None:
    path = tmp_path / "ledger.tsv"
    row = gates.LedgerRow(
        ts_utc="2026-04-25T12:00:00Z",
        slug="foo-bar",
        heuristic_before=2.5,
        heuristic_after=None,
        real_llm_sampled=True,
        real_llm_teaching_score=4.3,
        real_llm_verdict="strong",
        writer="codex",
        reviewer="claude",
        review_verdict="approve",
        notes="phase-A.1",
    )
    gates.append_ledger(row, path)
    text = path.read_text()
    assert text.startswith("ts_utc\tslug\t")
    assert "foo-bar" in text
    assert "4.30" in text
    assert "phase-A.1" in text


def test_append_ledger_appends_without_duplicating_header(tmp_path: Path) -> None:
    path = tmp_path / "ledger.tsv"
    row = gates.LedgerRow(
        ts_utc="2026-04-25T12:00:00Z",
        slug="a", heuristic_before=2.0, heuristic_after=None,
        real_llm_sampled=False, real_llm_teaching_score=None, real_llm_verdict=None,
        writer="codex", reviewer="claude", review_verdict="approve",
    )
    gates.append_ledger(row, path)
    gates.append_ledger(row, path)
    lines = path.read_text().splitlines()
    assert lines[0].startswith("ts_utc")
    assert lines.count(lines[0]) == 1  # header exactly once
    assert len(lines) == 3  # header + 2 data rows


def test_append_ledger_concurrent_writers_single_header(tmp_path: Path) -> None:
    """Two concurrent first-writers must NOT duplicate the header.

    Regression guard for codex review finding #1: the v1 outside-the-
    lock existence check raced; with a lock + size recheck, exactly one
    worker writes the header even if both observe the file as missing
    on entry.
    """
    import threading

    path = tmp_path / "ledger.tsv"
    rows = [
        gates.LedgerRow(
            ts_utc=f"2026-04-25T12:00:0{i}Z",
            slug=f"slug-{i}",
            heuristic_before=2.0, heuristic_after=None,
            real_llm_sampled=False, real_llm_teaching_score=None, real_llm_verdict=None,
            writer="codex", reviewer="claude", review_verdict="approve",
        )
        for i in range(8)
    ]
    barrier = threading.Barrier(len(rows))

    def worker(r: gates.LedgerRow) -> None:
        barrier.wait()  # release all threads simultaneously
        gates.append_ledger(r, path)

    threads = [threading.Thread(target=worker, args=(r,)) for r in rows]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    lines = path.read_text().splitlines()
    header_count = sum(1 for line in lines if line.startswith("ts_utc\tslug"))
    assert header_count == 1, f"expected 1 header, got {header_count}: {lines}"
    data_lines = [line for line in lines if not line.startswith("ts_utc\tslug")]
    assert len(data_lines) == len(rows)
    # Every row's slug appears exactly once.
    for r in rows:
        assert sum(1 for line in data_lines if r.slug in line) == 1, r.slug


def test_run_real_llm_rubric_returns_error_dict_on_malformed_json(
    tmp_path: Path, monkeypatch
) -> None:
    """Malformed audit JSON must surface as ``ok=False`` with an error,
    NOT raise a ``JSONDecodeError`` past the function boundary.

    Regression guard for codex review finding #3: the v1 ``json.loads``
    call escaped to the caller, which crashed the worker mid-merge.
    """
    # Point the module at a tmp content root so slug-resolution succeeds.
    fake_root = tmp_path
    fake_content = fake_root / "src" / "content" / "docs" / "foo"
    fake_content.mkdir(parents=True)
    module_path = fake_content / "module-1.6-x.md"
    module_path.write_text("# x\n")
    fake_audit_dir = fake_root / ".pipeline" / "teaching-audit"
    fake_audit_dir.mkdir(parents=True)
    audit_json = fake_audit_dir / "foo-module-1.6-x.json"
    audit_json.write_text("{ broken json")

    monkeypatch.setattr(gates, "_REPO_ROOT", fake_root)
    monkeypatch.setattr(gates, "_AUDIT_DIR", fake_audit_dir)
    # Stub out the subprocess so we don't actually call gemini —
    # we want to land at the json-parse step with the malformed file.

    class FakeProc:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: FakeProc())

    result = gates.run_real_llm_rubric(module_path, model="x", timeout=5)
    assert result["ok"] is False
    assert "unreadable" in result["error"].lower() or "json" in result["error"].lower()


def test_ledger_row_to_tsv_escapes_tabs_and_newlines() -> None:
    row = gates.LedgerRow(
        ts_utc="2026-04-25T12:00:00Z",
        slug="x", heuristic_before=None, heuristic_after=None,
        real_llm_sampled=False, real_llm_teaching_score=None, real_llm_verdict=None,
        writer=None, reviewer=None, review_verdict=None,
        notes="multi\nline\twith\ttabs",
    )
    tsv = row.to_tsv()
    assert "\nline" not in tsv.rstrip("\n")  # no embedded newline
    assert tsv.count("\t") == 10  # 11 fields => 10 separators
