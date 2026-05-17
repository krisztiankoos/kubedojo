# quality/pipeline 4-fix bundle (#1281-#1284)

**Owner**: codex (gpt-5.5, danger mode)
**Worktree**: `.worktrees/quality-pipeline-fixes`
**Branch**: `fix-quality-pipeline-1281-1284`
**Source**: clawpatch run `20260517T160324-644010` slice `scripts/quality#2`, 4/4 spot-verified real by claude on 2026-05-17.

## Goal

Ship ONE PR that closes all four issues atomically. They are tightly coupled (all in `scripts/quality/*.py`, all pipeline-correctness, all surfaced by the same review run). Single PR, single review cycle.

PR title: `fix(quality): 4 clawpatch-found correctness bugs in pipeline / stages / batch (#1281-#1284)`
PR body: `Closes #1281. Closes #1282. Closes #1283. Closes #1284.`

## The four bugs

Read each issue's `## Suggested fix` + `## Suggested regression test` sections — they are precise and you can lift them with light adjustment. Quick map:

| # | File | Function | Bug | Fix shape |
|---|---|---|---|---|
| 1281 | `scripts/quality/pipeline.py` | `cmd_cleanup_banners` (lines ~995-1013) | Holds `state.state_lease(slug)` across nested `record_completion` call that re-acquires the same lock; on inner lock-fail the helper swallows the exception and the cleanup counter increments anyway | Load state under lease → release → call helper. Helper returns explicit success flag; only increment counter on success. |
| 1282 | `scripts/quality/run_388_batch.py` | `fetch_active_leases` + `select_modules` (lines ~98-107 + 223-240) | Lease lookup compares `api_path` / `repo_path` only; bare `module_key` form (no `.md`, no `src/content/docs/` prefix) is silently ignored → double-dispatch risk | Normalize all leases at fetch time into canonical form (no prefix, no `.md`); normalize the candidate before lookup. Single helper used both sites. |
| 1283 | `scripts/quality/stages.py` | `_post_merge_gates` + `_commit_ledger_row` (lines ~1441-1473) | `gates.append_ledger` + `_commit_ledger_row` run OUTSIDE `_merge_lock`; if `git commit` raises after `git add` succeeds, the ledger row stays staged → primary dirty → next `merge_one` sees "foreign edit" | Hold `_merge_lock` across the ledger append+commit. On exception, `git restore --staged docs/quality-progress.tsv` + `git restore docs/quality-progress.tsv` in a `finally:` clause. |
| 1284 | `scripts/quality/pipeline.py` | `_process_batch` + `cmd_audit` / `cmd_route` (lines ~351-384) | Module docstring promises exit code 3 on `DispatcherUnavailable`; actual return is 0 (silent CI success on dispatcher outage) | `_process_batch` returns `(ok, fail, aborted: bool)`. `cmd_audit` / `cmd_route` map `aborted=True` → return 3 regardless of `fail` count. |

## Tests

Each issue body has a `## Suggested regression test` block with concrete pytest code — use those verbatim where they apply. Add the four tests to `tests/test_quality_pipeline.py` (extend the existing file if present; create it if not — check first). Use `monkeypatch` over real-filesystem fixtures where the issue body uses `monkeypatch`.

Run before commit:

```bash
.venv/bin/pytest tests/test_quality_pipeline.py tests/test_quality_dispatchers.py tests/test_quality_stages.py -q
```

0 failures required. If any pre-existing test file doesn't exist, just run the ones that do plus the new one.

## Constraints

- **Single commit per fix, four commits total, one PR.** Commit titles:
  - `fix(quality/pipeline): release lease before nested record_completion call (#1281)`
  - `fix(quality/run_388_batch): normalize module_key-form leases (#1282)`
  - `fix(quality/stages): hold merge lock across ledger append+commit (#1283)`
  - `fix(quality/pipeline): propagate dispatcher-abort to exit code 3 (#1284)`
- **Mode**: danger (need git push + gh pr create).
- **Base**: `main`.
- **Three-way rule** (per `feedback_three_way_rule_agreement.md`): writer prompt + dispatcher + verifier must agree where applicable. For #1282 specifically — if the normalization helper is reused elsewhere, find and update all sites (`grep -rn 'leases\[' scripts/`).
- **No `--no-verify`** on commits. If pre-commit hooks fail, fix the root cause.
- **No memory writes** (orchestrator-only).
- **Push and open PR.** End run with the PR URL.

## Reference

- Clawpatch findings (gitignored): `.clawpatch/findings/` (run `20260517T160324-644010`).
- Triage memory: filed last session as confirmed-bug medium.
- Session-21 handoff: `docs/session-state/2026-05-17-session-21-clawpatch-adoption.html`.

## Out of scope

- Other clawpatch findings (none open beyond these 4).
- Pipeline architecture changes (e.g., switch lease registry to redis). These are fixes for known bugs, not redesign.
- Adding new clawpatch findings during this run.
