# quality 2-HIGH bundle (#1296 + #1297)

**Owner**: codex (gpt-5.5, danger mode)
**Worktree**: `.worktrees/quality-high-2fix`
**Branch**: `fix-quality-high-1296-1297`
**Source**: clawpatch run `20260517T201555-cc8fa3` on `scripts/quality#1`; both findings spot-verified real by claude on 2026-05-17.

## Goal

Single PR closing both HIGH-severity findings atomically. They're tightly coupled (same package, same clawpatch run, both production-correctness risks). One review cycle.

- PR title: `fix(quality): 2 HIGH clawpatch findings — slug collision + duplicate-URL citation keep (#1296, #1297)`
- PR body: `Closes #1296. Closes #1297.`

## The two bugs

### #1296 — Pilot worktree slugs collide across same-basename modules

- **File · function**: `scripts/quality/dispatch_388_pilot.py::slugify` (~lines 148-155) + `main` (~lines 536-550).
- **Bug**: `Path(path).stem` strips the directory, so `cks/module-5.1-image-security.md` and `cka/module-5.1-image-security.md` both slug to `module-5-1-image-security`. The second dispatch reuses the first's `.worktrees/codex-388-pilot-<slug>` and branch `codex/388-pilot-<slug>` → overwrites or steals the first PR's head.
- **Repo state**: 7 same-basename pairs verified today (find output in issue body).
- **Fix shape**: build slugs from the repo-relative module path. There's a precedent helper — search for `module_slug_for_pipeline` in `scripts/quality/` (likely `state.py` or `pipeline.py`). REUSE that helper. If it doesn't exist there, write a single helper at module-scope in `dispatch_388_pilot.py` and use it everywhere. Also add a guard in `make_worktree`: if a worktree exists, verify it was created for the same module path (e.g. read a tiny `.module_path` marker dropped at creation) before reusing; raise if mismatched.

### #1297 — Rejected duplicate-URL citation claims are kept

- **File · function**: `scripts/quality/citations.py::rebuild_section` (~lines 338-348); also `process_module_citations` (~lines 393-401).
- **Bug**: verification is per-`SourceEntry` (URL + claim pair), but rebuild keeps lines keyed only by URL (`kept_urls: set[str]`). If the same URL appears twice with different claims and only one gets `supports`, BOTH bullets survive.
- **Policy violation**: this silently lets unverified claims survive — direct contradiction of the TOP-PRIORITY memory rule `feedback_citation_verify_or_remove.md`: "STRICT: burden of proof on keeping. supports → keep. Anything else → remove. Unverified = lie."
- **Fix shape**: track kept entries by occurrence — either the exact raw source line (line text as the dedup key) or a multiset of `(url, claim)` tuples. Carry the per-entry verdicts into reconstruction and append only the exact kept occurrence.

## Tests

Use the regression-test snippets from each issue body. Verify (in branch):

```bash
PYTHONPATH=/Users/krisztiankoos/projects/kubedojo/scripts \
  /Users/krisztiankoos/projects/kubedojo/.venv/bin/pytest \
  tests/test_dispatch_388_pilot.py tests/test_citations*.py tests/test_quality_*.py -q
```

0 failures required. Add the new tests in the appropriate existing files (find `tests/test_dispatch_388_pilot.py` for #1296; `tests/test_citations*.py` for #1297 — create if missing).

## Constraints

- **Two commits, one PR**:
  - `fix(quality/dispatch_388_pilot): build slug from repo-relative path; guard worktree reuse (#1296)`
  - `fix(quality/citations): track kept citations by raw line / SourceEntry, not URL set (#1297)`
- **Mode**: danger (git push + gh pr create).
- **Base**: `main`.
- **No `--no-verify`** on commits.
- **No memory writes** (orchestrator-only).
- **Three-way rule** (`feedback_three_way_rule_agreement.md`): for #1296, if `slugify` is referenced elsewhere (`grep -rn 'slugify' scripts/ tests/`), update all callers to use the new disambiguated slug; for #1297, if `kept_urls` pattern repeats elsewhere in `citations.py`, fix all sites.
- **Push and open PR.** End with PR URL.

## Out of scope

- Medium-severity findings (#1290-#1295). Separate PR(s) if greenlit.
- Architectural overhaul of `slugify` or `citations.py`. These are surgical correctness fixes.
- Migration of existing pilot worktrees on disk (none active right now per `git worktree list`).
