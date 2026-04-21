---
title: Session 13 handoff — quality-campaign corrections, pipeline_v4 filter bugfix, Phase C pilot running
date: 2026-04-21
---

# TL;DR

Driver on the 4/5 quality campaign (#180) flipped from Codex to Claude this
session; codex reorganized #180 into eight per-track slice issues
(#331-#338). Session 12's Phase A plan was WRONG — Stage 2 `--skip-citation`
does not lift ai-ml-engineering modules past 4/5 because the scorer caps
non-cited modules at 1.5. PR #326's AI foundations lifts only worked
because those modules were pre-cited in commit `868fcf7a`. Fixed a
filter bug codex shipped (`56b0f998`) that silenced `--skip-citation`
batches on mixed-gap modules. Killed a wasted PA2 run. Launched a
3-module full-pipeline pilot (Phase C) in background to measure real
wall clock + citation_v3 success rate before committing to bulk.

**Next session's first move:** read `.worktrees/phase-a-stage2/.pipeline/v4/runs/pc-pilot.log`
and the three per-module logs (`pc-*.log` in the same dir) to see how
the pilot finished. Use that data to choose between Route A (full
pipeline overnight), Route B (citation_v3 then Stage 2, two sessions),
or abandon ai-ml-engineering tranche for now and pivot to another
slice.

# What landed this session (commits on main)

| Commit | Scope |
|---|---|
| `b0a914a7` | docs(sessions): fix session 11 handoff — dogfood was already merged as 7dc2917e |
| `7ed19057` | fix(pipeline-v4): retry with rescore-refreshed gap list, not original |
| `fb9f9fc4` | feat(pipeline-v4): add `scripts/pipeline_v4_batch.py` — concurrent batch runner + 14 tests |
| `2f460a0e` | fix(pipeline-v4): skip Stage 2 when only Stage-4 gaps remain |
| `c675cfb1` | docs(sessions): session 12 handoff — batch wrapper + bug fixes |
| `61d2ee60` | fix(pipeline-v4-batch): default workers=1, hard cap 3, clamp-and-warn above |
| `c77aa71e` | feat(dispatch): `KUBEDOJO_GEMINI_SUBSCRIPTION=1` forces OAuth auth path |
| `5fec5c20` | fix(pipeline-v4): residuals_queued is needs_human, not failed |
| `56b0f998` | **fix(pipeline-v4-batch): select_candidates skip_citation filter was too strict** |

Plus codex's PRs (#326 content batch, #327 batch wrapper, #328 hygiene,
#329 skip-citation mode) — all merged before 18:44 CEST. 15 AI content
modules crossed 4.0 via PR #326 Stage 2 expansion.

# Critical strategic finding (corrects session 12 handoff)

**Stage 2 expansion without Stage 4 citation does NOT lift modules
past 4/5 for modules lacking a `## Sources` section.** The scorer in
`scripts/local_api.py:build_quality_scores` has an unconditional
`if not has_citations: score = min(score, 1.5)` cap.

- **AI foundations modules** (ai/foundations/*, ai/ai-native-work/*, etc.)
  succeeded in PR #326 because they were pre-cited in
  `868fcf7a "apply v3 pipeline to foundations"`. Stage 2 just added
  thin/quiz/exercise on top and they cleared the gate.
- **ai-ml-engineering modules** have NOT been through citation_v3.
  Tested `ai-ml-engineering/ai-infrastructure/module-1.4` live: Stage 2
  filled the quiz gap, rescore surfaced no_exercise, second attempt
  filled exercise — score stayed 1.5 throughout because no Sources
  section was added.

Memory updated in `~/.claude/projects/-Users-krisztiankoos-projects-kubedojo/memory/project_stage2_track_coverage.md`.

# Per-slice state (fresh computation, not stale HTTP API)

Current below-4.0 count: **619** (HTTP API shows 630, it's serving stale
cache from before today's merges — force a fresh compute via
`local_api.build_quality_scores(Path.cwd())` in Python, don't trust
the HTTP endpoint's count until the API process is restarted).

| Slice | Below 4.0 | Strategy |
|------:|----------:|:---------|
| #337 AI learner | 11 → **0 fresh** | All 11 already at 4.3 fresh — stale API hides this |
| #338 AI/ML eng | 55 | 25 mixed need full pipeline (Stage 2+4); 30 cite-only need Stage 4 + seed gen |
| #334 K8s certs | 184 | Needs citation seed generation pass first |
| #335 Platform Eng | 178 | Same |
| #333 Cloud | 81 | Same |
| #336 On-Prem | 51 | Same (also overlaps #197 Phase 1) |
| #332 Linux | 37 | Same |
| #331 Prerequisites | 33 | Same |

Total: 630 (stale) / 619 (fresh).

# Phase A execution summary

## PA1 — #337 AI learner

Dropped. Fresh `build_quality_scores` shows all 11 targets already at
4.3. HTTP API cache is stale. Next session can either force-refresh
the API or leave it to eventually re-cache.

## PA2 — #338 AI/ML eng mixed — KILLED

Launched `--track ai-ml-engineering --workers 1 --skip-citation` in
background, watched first 3 modules. Stage 2 filled quiz/exercise
correctly but modules stayed at 1.5 (citation cap). Killed before
wasting 6 h of overnight compute.

Killed processes: worktree python (pid 43618), tee (43619), shell
(43499), plus 4 orphan Gemini nodes (pkill by name). DB lease state
cleaned: 1 active lease removed by direct sqlite update on
`.worktrees/phase-a-stage2/.pipeline/v2.db` table `v4_batch_leases`.

## PC — pilot completed 22:57 CEST, FAILED on an infrastructure bug

All 3 pilot modules completed in ~25 sec each (total pilot wall: 97 sec)
with identical failure:

```
CITATION_V3 start {}
outcome: failed
reason: FileNotFoundError: [Errno 2] No such file or directory: '.venv/bin/python'
```

Root cause: `pipeline_v4._invoke_citation_pipeline` launches
`pipeline_v3` via `subprocess.run([".venv/bin/python", "scripts/pipeline_v3.py", ...], cwd=REPO_ROOT)`.
REPO_ROOT here is the worktree (`.worktrees/phase-a-stage2/`), which
doesn't have a `.venv` — only the primary repo does. So Stage 4 dies
before invoking citation_v3.

**This is a real bug, not a test artifact.** Any worktree-based
pipeline_v4 run hits it. Fix candidates:
- Absolute path: `sys.executable` (the Python that launched pipeline_v4
  is the right one to invoke subprocesses with).
- Search up: if `.venv/bin/python` doesn't exist relative to REPO_ROOT,
  walk up to find the primary repo's venv.
- Per-worktree venv: create a `.venv` symlink into the worktree before
  running — operator burden.

`sys.executable` is the cleanest. Single line change in
`scripts/pipeline_v4.py:_invoke_citation_pipeline`.

**Useful signal salvaged from the broken pilot:**
- Stage 2 correctly filled `no_quiz` on all 3 modules (provenance_blocks_added: 1 each).
- Stage 3 rescore confirmed the 1.5 citation cap: `score: 1.5, gaps: ["no_citations"]` after no_quiz filled. So even with the fix, these 3 modules still hit the cap until Stage 4 actually runs AND either injects a Sources section or falls back to the seed's further_reading.
- Wall clock for Stages 1-3 on these modules was 25-26 sec each. Not the 7-10 min session 12 assumed. Module sizes were 1749-1960 lines starting (much larger than the module-1.2 dogfood's 199 lines).

**Targets attempted (all at 1.5, no Sources section, `loc_before` → `loc_after` in bytes):**

1. `ai-ml-engineering/ai-native-development/module-1.10-anthropic-agent-sdk-and-runtime-patterns` — see `.worktrees/phase-a-stage2/.pipeline/v4/runs/pc-ai-ml-engineering_ai-native-development_module-1.10-*.log`
2. `ai-ml-engineering/classical-ml/module-1.3-time-series-forecasting` — 1960 → 2028 lines
3. `ai-ml-engineering/deep-learning/module-1.1-neural-network-fundamentals` — 1749 → 1803 lines

**On-disk state**: the worktree's 3 modules have Stage-2 quiz additions
applied (provenance-wrapped). NOT committed. Next session decides
whether to keep them (commit to the batch branch) or discard
(`git checkout` the files). They're real content, won't lift scores,
but are genuinely net-positive content if kept.

**Next session's first move on the pilot:**

1. Fix the venv path bug in `pipeline_v4._invoke_citation_pipeline`
   (swap `.venv/bin/python` for `sys.executable`). Add a test that
   runs pipeline_v4 from a path where `.venv/` doesn't exist.
2. Re-run pilot (same 3 modules). Expected: Stage 4 actually runs,
   emits `clean` / `residuals_queued` / `failed`, tells us whether
   citation_v3 can close the gate on ai-ml-engineering content.
3. Based on re-pilot results, choose Route A vs Route B vs pivot.

# Filter bug fix (committed `56b0f998`)

Codex's `select_candidates` in `scripts/pipeline_v4_batch.py` had:
```python
if skip_citation and "no_citations" in gaps:
    continue
if skip_citation and gaps and not pipeline_v4.expand_module.can_expand(gaps):
    continue
```

The first branch excluded ANY module whose gap list contained
`no_citations` — even mixed modules where another gap was Stage-2
fillable. This silenced all 24-26 mixed candidates in
ai-ml-engineering. The `can_expand` check on the second line already
handles the correct "at least one gap is expand-handlable" rule.
Removed the redundant stricter line. Test
`test_select_candidates_skip_citation_filters_stage4_only_modules`
previously asserted the buggy behavior; updated to assert correct
behavior (mixed `no citations, no exercise` is INCLUDED because
Stage 2 handles no_exercise).

This bug explains why codex's later cleanup commits (`d61f6356` "skip
citation-blocked modules in batch mode", `1651cd10` "quiet batch runs
and skip blocked candidates") produced apparently-clean batch runs —
they weren't; the batches were just silently selecting nothing.

# Corrections that need posting

## Wrong claim on #180 driver-update (comment 4290944797)

The 2026-04-21 14:45 UTC comment I posted on #180 claimed Phase A
would lift ~41 modules past 4/5 via Stage 2. That was wrong — Stage 2
alone does NOT lift non-pre-cited modules. Post a follow-up comment
with the corrected understanding, linking to this handoff.

## #337 AI learner is actually done (per fresh scoring)

Worth a closer look: all 11 `ai/ai-building` + `ai/open-models-local-inference`
modules report 4.3 fresh. Either confirm via the API cache
refresh, or re-run the scoring by force. If confirmed, close #337
or at least post an update.

# Process notes worth keeping

## HTTP API quality-scores cache is persistent and stale

The running API server on port 8768 is serving a cached signature
from before today's merges. Direct `build_quality_scores(Path.cwd())`
from a fresh Python process reads current file state. The gap
between the two is ~11 modules (630 vs 619). Don't trust
`curl /api/quality/scores` for near-real-time numbers until the API
process is cycled.

## Gemini auth switch

`KUBEDOJO_GEMINI_SUBSCRIPTION=1` must prefix any pipeline run while
the API key is on cooldown. Memory:
`reference_gemini_subscription_switch.md`. The pilot driver script
`/tmp/pc-pilot-driver.sh` sets this at the top.

## Worker cap

`pipeline_v4_batch` clamps `--workers > 3` down to 3 with a stderr
warning. Default is 1. Memory: `feedback_batch_worker_cap.md`.

## Bridge delegation to Codex for long jobs: don't

I tried dispatching Phase A to Codex via `scripts/ab ask-codex`. Codex
correctly pushed back — the bridge path is for coordination, not
multi-hour content batches. For long batches, set up the worktree
from Claude and kick off the background process directly. Use the
bridge for follow-up tasks (PR drafting, issue comments) after.

# Known issues / gotchas

- **Stash entry still present**: `stash@{0}: pre-vuln-fix stash` on
  main has uncommitted changes to `docs/migration-decisions.md` and
  `src/content/docs/uk/prerequisites/zero-to-terminal/index.md`.
  Accidentally popped this session, restored cleanly; entry remains.
- **`generate_module.py` and `reproduce_bug.py`** in the primary
  checkout's untracked pool — not mine, not touched this session.
- **Pyright errors in `scripts/pipeline_v4.py`** lines 192, 219, 311,
  332 — all `float(entry.get("score"))` patterns. Pre-existing, wrapped
  in try/except at runtime. Six errors total. Not fixed this session.

# Repo state at handoff

- **Primary `main` is 1 commit ahead of `origin/main`**: `56b0f998`
  (the filter-fix commit) is local-only. Push it so the next session
  / other operators see the corrected filter behavior.
- **Worktree `.worktrees/phase-a-stage2/` is dirty** with:
  - `scripts/pipeline_v4_batch.py` — my hand-copied filter-fix
    (already on main in `56b0f998`; can be discarded).
  - 6 content modules under `src/content/docs/ai-ml-engineering/*`
    with Stage 2 `no_quiz` expansions applied — 4 from the killed PA2
    run and 3 from the PC pilot (one overlap). These are real content
    additions (provenance-wrapped), **won't lift the score past 1.5
    until citations are added**, but are net-positive content on
    their own. Next session's call: commit to `batch/phase-a-stage2`
    for later citation pass, or discard and re-run cleanly after the
    venv-path bug is fixed.

# Files / paths referenced

- Pilot driver: `/tmp/pc-pilot-driver.sh`
- Pilot log dir: `.worktrees/phase-a-stage2/.pipeline/v4/runs/`
- Worktree: `.worktrees/phase-a-stage2/` (branch `batch/phase-a-stage2`)
- Session 12 handoff: `docs/sessions/2026-04-21-session-12-handoff.md`
- Slice issues: #331-#338 (see `gh issue list --search "Quality Epic"`)
- Parent epic: #180 (with driver-update comment 4290944797 needing correction)

# Memory updates this session

- New: `feedback_batch_worker_cap.md`
- New: `reference_gemini_subscription_switch.md`
- New: `project_stage2_track_coverage.md` (extensively updated after
  the Stage-2-doesn't-lift-uncited-modules finding)

# Next session opening move

```bash
# 1. Check pilot outcome
tail -50 .worktrees/phase-a-stage2/.pipeline/v4/runs/pc-pilot.log
for f in .worktrees/phase-a-stage2/.pipeline/v4/runs/pc-*.log; do
    echo "=== $f ==="
    grep -E "outcome|score_after|stage_reached|citation_v3_exit" "$f" | tail -5
done

# 2. Fresh quality state
.venv/bin/python -c "
import sys; sys.path.insert(0, 'scripts')
import local_api
from pathlib import Path
p = local_api.build_quality_scores(Path.cwd())
below = [m for m in p['modules'] if float(m['score']) < 4.0]
print(f'below 4.0: {len(below)} of {len(p[\"modules\"])}')
"

# 3. Decide Route A (bulk) vs Route B (two-phase) vs pivot based on pilot results
```
