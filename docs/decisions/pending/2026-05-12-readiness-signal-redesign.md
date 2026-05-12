# DECISION REQUIRED — Readiness signal redesign (`/api/tracks/readiness`)

**Date:** 2026-05-12
**Agents:** claude, gemini, codex (3 rounds; codex round-1/2/3 failed environmental — finally got input via direct `dispatch_smart.py architect --agent codex` on a fresh worktree)
**Channel:** `readiness-signal-2026-05-12` thread `23a5358b9daf449e81ed6a3488813e42`

## What converged

All three agents agree on **architecture**:
- FS-derived signal, **frontmatter-canonical** on `main` HEAD.
- Drop `/api/tracks/readiness`'s dependency on `.pipeline/v2.db`.
- v2.db consumers (`/api/pipeline/v2/*`, status CLI, activity feed) are
  independent of readiness and unaffected (codex audit confirmed —
  `scripts/local_api.py:1516/1601/1671/8176/7432/8526` are read-only and
  serve different views).

## What was disputed

Scope of the `cleared` predicate:

- **A‴ (claude):** 2-bit FS predicate. `revision_pending: false AND
  citations_verified: true`. Density + rubric structural become a
  separate `quality_tier` field. Single function in `local_api.py`,
  estimated ~50 LOC.
- **D (gemini):** Decoupled readiness service synthesizing 3-4 async
  signals (revision_pending + density + rubric structural + citations).
  Forward-compatible with whatever replaces pipeline_v2.

Claude conceded the citation-bit point (citations *are* an async
post-merge gate per `docs/quality-rubric.md:17`) → moved from A → A‴ →
adding `citations_verified`. Gemini did not concede the
density/rubric-as-gate point.

## Codex audit — implementation reality check

Codex audited the worktree (`gpt-5.5`, danger mode, `.worktrees/codex-
readiness-audit` off origin/main `351b4f6f`). Verdict: **[CONCERN]** —
A‴ has two real issues:

### Issue 1 — `backfill-pending` does NOT write `citations_verified` to frontmatter

- `cmd_backfill_pending` (`scripts/quality/pipeline.py:500`) → `_backfill_one`
  (~line 422-477) → runs `citation_backfill.py research` + `inject`.
- `citation_backfill.py inject` (`:1251`) explicitly tells the agent
  **never to modify frontmatter**. The mechanical write at `:1853` is
  `module_path.write_text(new_body)` — body only.
- Backfill writes outcome to a **sidecar JSON file** at
  `.pipeline/quality-pipeline/<slug>.json` (`scripts/quality/state.py:3`),
  not to frontmatter.
- Result: there is no `citations_verified` field anywhere in code or
  content today. **A‴ as stated cannot be implemented without a
  prerequisite patch.**

### Issue 2 — Strict `revision_pending == false` conflicts with cleanup

- The normal cleanup path **removes the `revision_pending` field**
  entirely rather than setting it to `false` (`scripts/quality/queue.py:381`).
- A‴'s predicate as written (`== false`) would fail closed for
  already-cleared modules.
- Correct predicate: `fm.get("revision_pending") is not True` (presence-
  of-absence semantics).

## A⁴ — final recommended predicate

```python
cleared := fm.get("revision_pending") is not True \
        AND fm.get("citations_verified") is True
```

Two FS bits. Same architecture as A‴. Predicate corrected to match
existing cleanup-on-absence behavior.

## Patch package (codex's LOC estimate)

| Component | LOC | Where |
|---|---|---|
| New `build_tracks_readiness` handler + cache | 60-90 | `scripts/local_api.py` (replaces `:4026-4135` + drops `:3546-3680` v2 glue) |
| `set_citations_verified_frontmatter()` helper | 25-35 | `scripts/quality/queue.py` (parallel to `set_qa_pending_frontmatter` at `:362`) |
| Call-site in `_backfill_one` after successful `inject` | 10-20 | `scripts/quality/pipeline.py` |
| `_v_docs_frontmatter` cache version (mirrors `_v_quality_board:8534`) | 15 | `scripts/local_api.py` (add to `CACHE_POLICY`) |
| Tests rewrite (current at `tests/test_local_api.py:3001-3134` are v2.db-shaped) | 80-120 | `tests/test_local_api.py` |
| **Total** | **175-260 LOC** | 4 files |

Reusable helpers Codex identified:
- `_iter_en_modules`, `_track_for_key`, `_section_for_key` (already in
  `local_api.py`)
- `status._extract_frontmatter` (`scripts/status.py:172`)
- `_root` mapping for top-level modules (`scripts/local_api.py:3682`)
- Cache version pattern from `_v_quality_board` (`:8534`)

## Carry-forward considerations

1. **Quality_tier field deferred.** A⁴ doesn't add the separate
   `quality_tier` field — only `cleared`. Adding rubric/density as
   triage-priority signals can come later in the same handler if needed.
   Gemini's pedagogical concerns (density + rubric independently
   computed) are addressable as additional response fields, not as
   additional gate bits.
2. **Migration moment.** The instant this lands, the readiness API
   changes its truth. Modules that were "cleared" under the v2.db read
   but lack `citations_verified: true` will flip to "uncleared." That's
   correct behavior (citations are required for clearance), but it will
   show a one-time apparent regression in the dashboard. Document this
   in the PR.
3. **Backfill backlog.** Once the patch lands, every module that has
   `revision_pending` absent but no `citations_verified: true` (i.e.
   most of the existing corpus) becomes "needs backfill." The backfill
   pipeline will need to walk them. Could be a long tail.
4. **Pipeline_v2 untouched.** This change does NOT decide GH #375 (v2
   rebuild). v2 keeps running for its other endpoints; readiness just
   stops listening to it. Decoupling is the whole point.

## Options for the user

- **GO A⁴** — dispatch codex (`architect`, danger mode, fresh worktree)
  with the 4-file patch package. Expected: 60-90 min for codex to land
  + run tests; then standard cross-family review on the PR.
- **DEFER** — accept A⁴ as the architectural decision, but don't
  implement until after the overnight #388 batch finishes (≈12-15h from
  now). Avoids any race between the chain and a structural API change.
- **REOPEN** — if you don't accept A⁴, reopen the discussion with a
  tighter brief (e.g., make the case for D's "decoupled service" given
  codex's concrete LOC reality, or propose A⁵ with different gate bits).

## Orchestrator recommendation

**DEFER + GO A⁴ after the chain finishes.** Reasoning:
- Chain is mid-flight (AI phase 12/25, AI/ML Engineering not started).
- A structural API change while the chain is pushing PRs every ~10 min
  introduces unnecessary timing risk (the same origin-stale race that
  killed codex round-1/2/3 above).
- Codex confirmed the patch is implementable as stated (with A‴ → A⁴
  predicate sharpening). The decision is no longer contested.
- 175-260 LOC across 4 files, with tests, is one focused codex dispatch
  — easier when not racing the chain.

**Awaiting:** user override (D / different scope) or "go A⁴ now" /
"defer A⁴ until chain done".
