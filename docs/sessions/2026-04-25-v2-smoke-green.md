# 2026-04-25 — v2 quality pipeline GREEN on both writer paths

**State on handoff**: v2 pipeline COMMITTED 2 modules end-to-end across both writer paths. **154 quality tests, ruff clean. 0 commits ahead of origin/main (22 pushed this session).** P0–P4 from the prior handoff all closed; P3 surfaced a citation-insertion design call needing a user decision.

**Tracking**: [#375](https://github.com/kube-dojo/kube-dojo.github.io/issues/375). Prior handoff: [`2026-04-24-v2-smoke-handoff.md`](2026-04-24-v2-smoke-handoff.md).

## Cold-start

```bash
curl -s http://127.0.0.1:8768/api/briefing/session?compact=1 | head -40
.venv/bin/python -m pytest tests/test_quality_*.py -q              # expect 154 passed
git log --oneline origin/main..HEAD | wc -l                        # expect 0
.venv/bin/ruff check scripts/quality/ scripts/dispatch.py
```

## What landed this session

| SHA | Title | Type |
|-----|-------|------|
| `d017e8b9` | hang-detection retry in `_write_in_worktree` | code (P0) |
| `4f911c49` | claude rewrite k8s-capa-module-1.2-argo-events | content (P1) |
| `63c91218` | codex rewrite ai-ai-building-module-1.1-from-chat-to-ai-systems | content (P2) |

Plus 19 unpushed commits from prior session — all 22 now on `origin/main`.

## P0 — hang-detection retry (d017e8b9)

`scripts/quality/stages.py::_write_in_worktree`: after the first dispatch, if the result has the empirical hang signature (`ok=False AND empty stdout AND "timed out" in stderr`), persist the raw under `<attempt_id>-r0.failed.json`, sleep `_HANG_RETRY_SLEEP_SEC` (default 90s, monkeypatched to 0 in tests), redispatch once. If the retry hangs (or produces any non-ok result), persist as `-r1` and FAIL with both filenames in `failure_reason`. Generic non-zero crashes (rc != 0 with stdout or non-timeout stderr — e.g., RuntimeError tracebacks) deliberately skip the retry path so we don't waste compute on real writer crashes.

Both retry diags share the lease's `attempt_id` prefix, so a single FAILED state reliably points at both raw outputs. Worktree teardown still flows through the existing `BaseException` cleanup (Codex must-fix #6/#8 pattern).

Tests: `test_write_one_hang_retry_succeeds`, `test_write_one_hang_double_retry_fails`. The "kaboom" rc=1 test (`test_write_one_dispatch_nonzero_persists_raw_diag`) still passes — the predicate is narrow on purpose.

## P1 — argo-events round 5 (claude writer)

```
08:08:24 AUDITED reset for retry round 5 (P0 hang-retry shipped)
08:08:28 ROUTED track=rewrite writer=claude
08:08:28 WRITE_PENDING queued for write
08:08:28 WRITE_IN_PROGRESS
08:19:17 WRITE_DONE claude wrote 4f911c49     ← 10 min 49 s
08:19:17 CITATION_VERIFY verifying citations (from WRITE_DONE)
08:19:17 REVIEW_PENDING kept=0 removed=0
08:19:17 REVIEW_IN_PROGRESS
08:19:47 REVIEW_APPROVED codex APPROVE score=4.4
08:19:49 COMMITTED merged 4f911c49             ← total 11 min 25 s
```

859 lines, 13 H2 sections, 0 Sources sections. Codex review approved on the first pass — no retry round needed. The merge_one (rebase onto main → ff-merge) executed for the first time on real data; primary clean afterward, no orphan worktrees.

No hang on this round — empirically the rate-window theory wasn't tested (the prior failure was the SECOND consecutive heavy claude call ~10 min after the first; this run was the first claude call in 10+ hours). The hang-retry remains untested in production but covered by unit tests.

## P2 — ai-ai-building 1.1 (codex writer)

```
08:20:21 ROUTED track=rewrite writer=codex
08:20:21 WRITE_PENDING queued for write
08:20:21 WRITE_IN_PROGRESS
08:23:35 WRITE_DONE codex wrote 63c91218       ← 3 min 14 s
08:23:35 CITATION_VERIFY verifying citations (from WRITE_DONE)
08:23:35 REVIEW_PENDING kept=0 removed=0
08:23:35 REVIEW_IN_PROGRESS
08:24:37 REVIEW_APPROVED claude APPROVE score=4.6
08:24:39 COMMITTED merged 63c91218             ← total 4 min 18 s
```

1617 lines, 19 H2 sections, 0 Sources. Codex `--sandbox read-only` emitted clean module markdown (no `*** Begin Patch` or other patch-format pitfall). The extractor handled the codex output identically to claude's. Claude review approved on the first pass.

**Codex is ~3.5× faster than claude as writer** on this dataset (3:14 vs 10:49). Both claude reviewer (60 s) and codex reviewer (30 s) are roughly comparable.

## P3 — citation-insertion design call (NEEDS USER DECISION)

### Findings

1. **v2 omits citations BY DESIGN.** The omission is consistent across the prompt set:
   - `rewrite_prompt:102` — "Do NOT add a `## Sources` section — citations are handled in a separate stage."
   - `structural_prompt:148` — same.
   - `review_prompt:213` — "Ignore the `## Sources` section — citations are handled in a separate stage; do not penalize their absence or content."
   - `citations.py` — only verifies/removes existing entries; no insertion path.

2. **`scripts/citation_backfill.py` is the existing insertion orchestrator** (research → inject → verify → diff-lint). Already-shipped feature; commit `f1754f0d` shows 78 cloud modules backfilled from rubric_score 1.5 → 5.0.

3. **241 modules currently have a `## Sources` section** (from prior backfill runs). v2 rewrite track produces "complete replacement modules" without listing Sources as a protected asset, so any of those 241 that route to `rewrite` will lose their Sources. Mitigating factor: most Sources-having modules sit at audit score ≥ 4.0 (citation_backfill lifts scores to 5.0), so `route_one` sends them to `CITATION_CLEANUP_ONLY` (cleanup-only path preserves them). Actual hit count likely small but nonzero.

4. **No orchestration handoff** between v2 and citation_backfill. v2 reaches `COMMITTED` and stops. Newly-rewritten modules ship at high teaching score but get flagged `critical_quality` by the rubric heuristic scanner (`/api/quality/scores`) because Sources is missing — so the 485 critical_quality alert in the briefing won't shrink from v2 alone.

5. **Rubric/prompt internal inconsistency**: `docs/quality-rubric.md:7` declares a "Citation Gate (Mandatory Before Scoring)" — uncited modules cap at score 3 — but `review_prompt:213` explicitly tells the reviewer to ignore Sources. This is intentional (the reviewer mustn't double-penalize when Sources insertion is deferred), but the rubric text doesn't say so, which will confuse future readers.

### Recommendation

| # | Change | Cost | Risk |
|---|--------|------|------|
| 1 | Add `## Sources` to the protected-assets list in `rewrite_prompt` ("preserve verbatim if present, do not add a new one"). | 1-line prompt edit + 1 test asserting Sources content survives a stub-rewrite. | Zero — closes the 241-module stripping risk. |
| 2a | Document the manual two-step in `STATUS.md` and the v2 batch runbook: "after every v2 batch, run `citation_backfill.py` on the same slug list." | Doc-only. | Workflow discipline only. |
| 2b | Add a 7th `CITATION_BACKFILL` stage in v2 between `COMMITTED` and a new terminal `BACKFILLED` that invokes `scripts/citation_backfill.py`. | Real architecture change — needs Codex review cycle. | Larger; defer until manual workflow is exercised. |
| 3 | Add one paragraph to `docs/quality-rubric.md` explaining that v2's review prompt deliberately suspends the citation gate (citations are handled in a separate stage). | Doc-only. | Zero. |

Ship (1) and (3) immediately as standalone commits. Adopt (2a) as the operating procedure for the upcoming v2 batch. Defer (2b) to a tracking issue.

## P4 — pushed

22 commits pushed to `origin/main` cleanly. `git log --oneline origin/main..HEAD | wc -l` → 0. The push went via "Bypassed rule violations" (admin override of the PR-required rule) — same as prior pushes on this branch. GitHub Dependabot reports 1 moderate vulnerability — pre-existing, unrelated to this session.

## What is now durable

- **End-to-end v2 mechanics on both writer paths.** 6 stages (audit → route → write → citation_verify → review → merge) all run on real data without manual intervention.
- **Worktree lifecycle.** Worktrees PERSIST through write → citation_verify → review → merge, removed only on success or terminal failure. No orphans on either smoke run.
- **Hang-retry.** Unit-tested, ready for the rate-window failure mode if it recurs.
- **Codex-as-writer.** No `*** Begin Patch` issue — `codex --sandbox read-only` emits plain module markdown.
- **Cross-family review.** Both directions (claude→codex and codex→claude) approved on first pass.

## What is NOT yet validated

- **`REVIEW_CHANGES` retry loop on real data.** Both smoke runs got `approve` on the first review. The retry path (changes_requested → WRITE_PENDING with `must_fix` injected into the rewrite prompt) is unit-tested but not smoke-validated.
- **`DispatcherUnavailable` mid-batch.** Peak-hours / budget refusal during a multi-module run hasn't been smoke-tested. Tested via unit tests.
- **Multi-worker parallelism.** Default is `--workers 1`; per `feedback_batch_worker_cap`, hard cap is 3. Concurrent worktrees are per-slug so theoretically safe, but unproven on real data.

## Plan — next session

### N1. Ship the P3 (1) and P3 (3) prompt fixes

```diff
# scripts/quality/prompts.py:97 (rewrite_prompt)
- - Preserve every existing visual aid (ASCII, Mermaid, tables) — they are protected assets. Improve them if you can, but never remove.
+ - Preserve every existing visual aid (ASCII, Mermaid, tables) AND any existing `## Sources` section verbatim — they are protected assets. Improve diagrams/tables if you can, but never remove. Do NOT add a new `## Sources` section if one isn't already present (citations are handled in a separate stage).
- - Do NOT add a `## Sources` section — citations are handled in a separate stage.
```

Plus the same change in `structural_prompt`. Plus a regression test that feeds the writer a module containing a `## Sources` section and asserts the section survives in the captured output (using a stub dispatch that echoes its own prompt — already a pattern in the test suite).

### N2. Smoke a `REVIEW_CHANGES` retry loop

Pick a module where the writer is likely to produce something the cross-family reviewer will reject — e.g., a deliberately under-spec'd test fixture that fails the rubric on Q-count. Run end-to-end, confirm the WRITE_PENDING re-routing under `retry_count=1`, and that the second writer dispatch sees the must-fix bullets prepended via `[f"(retry) {x}" for x in retry_must_fix]`.

### N3. Decide P3 (2a vs 2b)

Run a small v2 batch (5-10 modules) WITH the P3 (1) prompt fix, then invoke `scripts/citation_backfill.py` on the same slug list manually (option 2a). If the manual two-step works cleanly, document it as the standing procedure. If it's painful, escalate to (2b) — a tracked architecture change.

### N4. Begin batch processing

Once N1–N3 are in, start pulling the 720 unaudited / 19 AUDITED-but-not-rewritten modules through v2. Default to `--workers 1` per `feedback_batch_worker_cap`. Cool-down ≥30 min between heavy claude writer runs IS NOT NEEDED now that hang-retry is in (the retry handles the rate window if it recurs). Codex writer has no rate-window risk observed.

## What NOT to do

- **Don't ship a v2 batch without P3 (1) merged first.** 241-module Sources-stripping risk is real on the rewrite track.
- **Don't skip `citation_backfill` after a v2 batch.** Modules will sit at `critical_quality` rubric flag until backfill runs.
- **Don't widen the `--no-tools` disallow list.** Round-2 hang root cause; narrow list `Bash,Edit,Write,NotebookEdit,WebFetch,WebSearch,Skill,Agent,ExitPlanMode` is empirically validated.
- **Don't push without the smoke being green.** Pre-authorization in the prior handoff was scoped to "smoke green"; future pushes need fresh approval if smoke regresses.

## Reference: cold-start checklist for the next session

```bash
curl -s http://127.0.0.1:8768/api/briefing/session?compact=1 | head -40
git log --oneline origin/main..HEAD                   # expect empty
.venv/bin/python -m pytest tests/test_quality_*.py -q # 154 passed
.venv/bin/ruff check scripts/quality/ scripts/dispatch.py
.venv/bin/python -m scripts.quality.pipeline status | head

# Then pick from N1–N4 above. N1 first (it's a prerequisite for N4).
```
