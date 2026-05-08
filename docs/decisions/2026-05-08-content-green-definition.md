# 2026-05-08 — Content "Green" Definition

**Status**: ACCEPTED
**Decided by**: User (krisztian.koos), session 4
**Scope**: All EN content rewrite work post-2026-05-08; gates the master priority "all EN content green before UK translation or expansion"

## Context

The user committed to a single master goal: drive all EN content to "green" (reviewed) before resuming UK translation or content expansion. The briefing API reports 276 modules at critical rubric score (`< 2.0`), distributed primarily across Platform Disciplines (71), Toolkits (52), Foundations (31), CKS (29), CKAD (23), CKA (17), and On-Premises sections (~30). The intuitive read of "green" was ambiguous.

The `/api/quality/scores` heuristic and the actual pedagogical rubric measure different things:

- **Heuristic scorer** (`/api/quality/scores`, regex-based per `reference_rubric_heuristic_structural.md`): scans for required sections (Sources, quiz, exercise, diagram presence) and prose density gates (mean wpp ≥ 30, median wpp ≥ 28, short-rate ≤ 20%). Reports a binary-ish score: 1.5 (any structural element missing) or ≥ 4.0 (all present). Zero modules score in the 2.0-4.0 middle.
- **Pedagogical rubric** (`docs/quality-rubric.md`): 8 dimensions (Learning Outcomes, Scaffolding & Structure, Active Learning, Real-World Connection, Assessment Alignment, Cognitive Load Management, Engagement & Motivation, Practitioner Depth) on a 1-5 scale. Threshold: **every dimension ≥ 4**. A score of 3 in ANY dimension is automatic fail.

The #388 engine (`scripts/quality/dispatch_388_pilot.py` + `scripts/prompts/module-rewriter-388.md`) targets the heuristic scorer. It is density-first — it ensures sections exist and prose hits the wpp gates. It does NOT measure Bloom's L3+ verbs, constructive alignment, scaffolding progression, scenario-based quiz construction, or cognitive load management. Per memory `feedback_teaching_not_listicles.md`: "Modules must TEACH (beginner→senior). Dry fact-dumps fail even when rubric passes. Rewrite > append."

Declaring victory at heuristic-green would ship 276 structurally-correct modules that may still teach badly.

## Decision

A module is **green** when both gates pass:

### Gate 1 — Structural (heuristic)

`/api/quality/scores` reports the module at `≥ 3.0`. In practice the scorer is bipolar so this means `≥ 4.0` (all required sections present + density gates pass). The `## Sources` section is in place even if backfill is deferred (per the v2 pipeline note in `docs/quality-rubric.md` — citation gate is owned by `citation_backfill.py`).

### Gate 2 — Pedagogical (rubric ≥ 4 per dimension)

A cross-family review (claude-sonnet via `dispatch_smart.py review`) scores the module against `docs/quality-rubric.md`'s 8 dimensions. **Every** dimension must be `≥ 4`. Verdicts allowed for green:

- `APPROVE` — all dimensions ≥ 4, sum ≥ 32, no findings worth a follow-up
- `APPROVE-WITH-NITS` — all dimensions ≥ 4, sum ≥ 32, surface-level cosmetic issues that don't change scoring; nits filed as a single follow-up issue per section, not per-module

Verdicts that DO NOT meet green:

- `NEEDS-CHANGES` — any dimension `< 4`. Module returns to the rewrite queue for a targeted fix-pass.

## Pipeline shape

For each critical-score module:

1. **Structural pass** — `dispatch_388_pilot.py` (or equivalent codex dispatch with `module-rewriter-388.md` brief) produces a density-first rewrite. Codex `gpt-5.5`, danger mode. Internal gemini cross-family structural review handles APPROVE / APPROVE-WITH-NITS / NEEDS-CHANGES per existing dispatcher logic.
2. **Pedagogical pass** — after structural lands on main (or holds for triage), dispatch `claude-sonnet-4-6` via `dispatch_smart.py review` against `docs/quality-rubric.md`. Outcome posted as a PR/commit comment OR opened as a follow-up issue if the module already merged.
3. **Disposition**:
   - Both pass → module marked green in our running ledger.
   - Structural pass + pedagogical NEEDS-CHANGES → re-dispatch codex with the pedagogical findings as the brief addendum. Sequential, not in parallel with structural rewrite of other modules (per `feedback_no_parallel_agent_fanout.md`).
   - Structural NEEDS-CHANGES → existing dispatcher hold lane. Triage manually.

## Canary

CKA 0.1 (`src/content/docs/k8s/cka/part0-environment/module-0.1-cluster-setup.md`) is the canary. Current state: 713 lines, 2132 body words, median wpp 9, short-rate 66.3%, scored 1.5. Canary outcome will tell us:

1. **Engine alive?** — does `dispatch_388_pilot.py` still produce a clean structural rewrite end-to-end after 2 days idle (last run 2026-05-07 with 2 exit=5 failures at end of day)?
2. **Gap size?** — once structural lands, does pedagogical-rubric review find the module green, or does it surface specific deltas (e.g., quiz needs scenario rewrite, Learning Outcomes missing Bloom L3+ verbs)?

If gap is small, structural-only suffices for many modules with light pedagogical touch-up. If gap is large, the pipeline shape above (two passes per module) holds and the marathon takes proportionally longer.

## What this decision does NOT cover

- **Velocity** — sequential vs P-series within-pipeline parallelism is a separate decision deferred to post-canary. See STATUS.md TODO.
- **Section ordering** — which sections go first (CKA, CKS, CKAD, Platform-*, On-Premises) is a separate planning decision once the per-module cost is empirically known.
- **UK retranslation** — UK pauses entirely until EN green is declared. UK detection cron remains shipped-but-dormant (PR #1007).

## References

- `docs/quality-rubric.md` — the 8-dimension scorer
- `scripts/prompts/module-rewriter-388.md` — the structural brief
- `scripts/quality/dispatch_388_pilot.py` — the structural-pass dispatcher
- `reference_rubric_heuristic_structural.md` (memory) — why heuristic ≠ pedagogical
- `feedback_teaching_not_listicles.md` (memory) — modules must teach, not list
- `feedback_dispatch_codex_for_code_changes.md` (memory) — claude orchestrates only
- STATUS.md "Priority lock" section — green-content master goal
