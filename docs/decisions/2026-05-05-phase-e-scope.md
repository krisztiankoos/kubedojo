# DECISION REQUIRED — Phase E scope after ch-33 audit returned clean

**Date filed**: 2026-05-05 03:14 CEST  
**Filed by**: claude (orchestrator), session 2  
**Surface**: User active in session — also emitted inline; this file is the durable record

## Context

PR #888 (codex `--search` source-of-problem fix) merged on trunk earlier this session. Phase D pilot — fact-check audit of `src/content/docs/ai-history/ch-33-deep-blue.md` — completed via `dispatch.py claude --no-tools` with `WebFetch`+`WebSearch` enabled (the patched `_CLAUDE_TEXT_ONLY_DISALLOWED`). Audit walltime ~60 min, 18 web ops issued, prompt scoped to compare prose against the per-chapter research bundle (`docs/research/ai-history/chapters/ch-33-deep-blue/`) first, then web-verify only the unsupported set, plus 5 spot-checks of bundle URLs.

**Audit result (full report at `.tmp/ch33-audit-out.md`):**

| Verdict | Count |
|---|---|
| R:supported | 65 / 74 (88%) |
| R:supported-but-drift | 5 (minor paraphrase/qualifier drops) |
| R:unsupported | 1 (Kasparov 1963 birth — verified-correct on web; not in bundle) |
| R:contradicted | 1 (glossary "Fredkin Prize ≥2500" vs body "2650+") |
| W:wrong | 1 (the same glossary entry — fixed inline this session, commit `d0201191`) |
| W:dead-link | 0 |
| Phase-3 spot-checks | SciAm fully verified, Wikipedia fully verified, 3 PDF mirrors content-unverifiable through WebFetch (binary; tool limitation, not gemini hallucination — research-bundle pdftotext extractions are still authoritative) |

**Auditor's narrative verdict** (closing paragraph):
> Approximately 88% of the chapter's 74 factual claims are cleanly anchored in the research bundle, and the research bundle's primary URL set shows no evidence of gemini-class upstream hallucination. The existing review gates (anchor verification + dual-family review) compensated effectively for the no-search dispatch defect: the writer drew correctly from the research bundle on every engineering claim that matters. **A back-catalog audit is not warranted based on this chapter's results, though a targeted sweep of chapter glossary sections across all no-search-dispatched chapters is advisable**, since the glossary appears to be the one section where the writer may have supplemented bundle-anchored content with general knowledge that slipped past the reviewer's engineering-focused checks.

The single contradicted error was localized to a peripheral section (the `<details>` "Plain-words glossary"), internally inconsistent with the body prose (Mermaid timeline + body both correctly say "2650+"; only the glossary said "above 2500"). That's the *signature* of a no-search hallucination — peripheral content the engineering-focused review chain didn't interrogate against the bundle.

## Options

### A. **Targeted glossary sweep across all ~69 remaining no-search-drafted chapters**

Audit only the glossary `<details>` block (and other peripheral reader-aid sections — TL;DR, cast-of-characters, math sidebars where applicable) in each chapter, comparing against the per-chapter research bundle. Skip the body prose audit (which the dual-review gate already covered).

- Wall: ~5 min/chapter (smaller scope than the full ch-33 audit). 69 × 5 = ~6 hr serial; ~1.5 hr if dispatched 3-at-a-time within the user's max-2 cap (which is for content writers; reviewer-class is lighter).
- Cost: ~$0.30/chapter claude headless = ~$20 total
- Risk: minimal — peripheral-section sweep won't disturb body prose; fixes are 1-line edits like the glossary one this session
- Confidence: high. We already saw the failure mode on one chapter; pattern-matching is the right tool.

### B. **One more pilot before scoping** ★ orchestrator recommendation

Audit one more chapter on the review-backfill list (ch-34 *DARPA SUR Program* or ch-35 *Indexing the Mind*) the same way. If it also returns clean with only glossary/peripheral drift, Option A becomes the right follow-up with high confidence. If it surfaces harder errors (e.g., body-prose contradictions, math-sidebar errors that survived dual-review), we re-evaluate the scope upward.

- Wall: ~30 min wall, 1 dispatch
- Cost: ~$1 in audit tokens
- Risk: ~30 min of latency before deciding Option A scope

### C. **Skip Phase E entirely**

Accept residual risk. The dispatch fix is in trunk; all future drafts are clean. The existing review gates were shown to compensate for the bug on the audited chapter. The one error found was minor and fixed.

- Wall: 0
- Cost: 0
- Risk: ~69 chapters retain unaudited peripheral sections that *probably* contain a similar glossary-class error pattern at low rate. If the rate is similar to ch-33 (~1 error / chapter / peripheral section), expect ~10–20 small factual errors site-wide in the AI history book that won't be discovered until a reader catches them.

### D. **Full back-catalog audit** (original Phase E plan)

70+ book chapters + 153 #388 modules, full prose audit each. Conservative-but-expensive.

- Wall: ~30 min/chapter × ~220 = 110 hr serial; weeks at the user's parallelism caps
- Cost: ~$200–$400 in audit tokens
- Risk: low (most thorough); but the audit's own verdict says "not warranted"

## Disagreement

None — single auditor (claude headless), single recommendation; the auditor and orchestrator agree.

## Orchestrator recommendation

**Option B**, then most likely Option A. The ch-33 result is one data point. Spending another 30 min to confirm the failure-mode pattern repeats (peripheral-section drift, body prose clean) before committing to the 6-hr Option A is the right tradeoff between under-investment (Option C) and over-investment (Option D). If pilot #2 returns clean → Option A. If pilot #2 surfaces harder errors → re-evaluate up.

## Decision (2026-05-05 03:18 CEST)

**User chose Option B with extension**: *"do as many pilots as you require to finetune everything so B"*. Orchestrator authorized to run multiple pilots until the failure-mode pattern is well-characterized, then choose Phase E scope (likely Option A) based on findings.

**Pilot plan**:
- Pilot 2: ch-34 *The Accidental Corpus* — different topic class (corpus linguistics / NLP history), tests whether the "peripheral sections are the weak spot" hypothesis holds outside chess history
- Pilot 3 (if needed): ch-35 *Indexing the Mind* (cognitive-science history) or a Tier 2 chapter with math sidebar (e.g., ch-55 / ch-58) to test formula-class drift
- Pilot 4 (if needed): a chapter from Part 5 or Part 7 (deep-learning era) where the *facts* are denser per page than the chess history era

**Stop conditions**:
- Pattern confirmed in 2-3 pilots → commit to glossary-only sweep (Option A) for the remaining chapters
- Body-prose drift surfaces in any pilot → re-evaluate scope upward
- Pilot returns essentially clean (≥95% R:supported, no contradicted) → can lower bar for Option A scope

## Three-pilot results (2026-05-05 ~04:00 CEST)

| Pilot | Chapter | Claims | R:supported | Wrong-specifics found | Section of error |
|---|---|---|---|---|---|
| 1 | ch-33 Deep Blue | 74 | 65 (88%) | 1 R:contradicted | S:glossary (Fredkin Prize threshold "≥2500" vs body's correct "2650+") |
| 2 | ch-34 The Accidental Corpus | 108 | 95 (88%) | 1 R:wrong | S:cast (Berners-Lee "CERN physicist") + body "billions of words" drift |
| 3 | ch-58 The Math of Noise | 63 | 54 (86%) | 1 W:wrong + 3 W:partial | **S:matters** ("DDPM still dominant" — flow matching is, in 2024-2025) + S:architecture "every layer" overclaim |

All three errors fixed inline this session (commits `d0201191`, `065e4fd8`, `6e1ba040`).

### Section-by-section risk profile (3-pilot synthesis)

| Section | Pilot data | Risk | Phase E action |
|---|---|---|---|
| `S:cast` (`<details>` cast table) | 1 wrong / 3 pilots | medium — when adds characterisation beyond people.md | **sweep** — bundle cross-check |
| `S:glossary` (`<details>` plain-words glossary) | 1 contradicted / 3 pilots | medium — when adds numeric specifics not in bundle | **sweep** — bundle cross-check |
| `S:matters` (`:::note[Why this still matters today]`) | 1 W:wrong + several unsup / 1 pilot tested | **HIGH** — bundle ends at chapter writing horizon, can't anchor 2024-2025 frontier-model claims | **sweep + web verify** — most expensive but highest signal |
| `S:timeline` (Mermaid diagram) | clean across all 3 | low — template-derived from timeline.md | **skip** |
| `S:math` (Tier 2 math sidebar) | 6/6 clean in 1 pilot | low — separate codex math review effective | **skip for Tier 2 chapters** that already had codex math review |
| `S:architecture` (Tier 2 only) | 3/7 minor drift in 1 pilot | low — implicit-knowledge drift, not factually wrong | **spot-check** only when novel numeric claims |
| `S:body` (main running prose) | 6% drift average; low severity | low — paraphrasing / rounding, no contradicted claims | **on-request audit only** — not systematic |

## Final Phase E scope

**SWEEP**: cast + glossary + S:matters notes across all 69 remaining no-search-drafted ai-history chapters. Mechanism per memory `feedback_dispatch_smart_for_sweeps.md`: `dispatch.py claude --no-tools` (which has `WebFetch`/`WebSearch` post-PR #888) with a per-chapter prompt that:

1. Reads the prose + the chapter's research bundle
2. Identifies wrong-specifics in S:cast / S:glossary by comparing against `people.md` + `sources.md` + `timeline.md`
3. Identifies wrong-specifics in S:matters by web-verifying any 2024-2025 claim against current state-of-field
4. Outputs the corrected markdown (3-section diff, not whole-file rewrite)

**SKIP**: timeline, math sidebars (Tier 2), body, architecture-sketch (unless novel numeric claims).

**Cost estimate**: ~5 min/chapter × 69 chapters = ~6 hr serial; can run as 3-at-a-time within the user's max-2 cap (claude headless dispatches don't compete with each other on the same subscription tier as long as we stay under rate limits) → ~2 hr wall.

**Order of operations**:
1. Build a sweep driver script: `scripts/sweep_ai_history_aids.py` that iterates chapters, reads bundle, dispatches claude headless with the audit-and-fix prompt, atomic-writes the result
2. Smoke-test on ch-32 (one of the review-backfill list) before scaling
3. Run the batch (~2 hr wall, ~$25-30 in claude tokens)
4. Each chapter's diff committed as a single commit per Part (Part 1: ch-01 to ch-08, Part 2: ch-09 to ch-16, etc.) for clean history

**Stop conditions during sweep**:
- Three consecutive chapters return zero changes → pattern frequency lower than estimated; can stop early
- Any chapter returns body-prose changes (sweep's prompt forbids that) → halt and inspect (over-stepping)
- Rate-limit on claude dispatch → pause and resume

**Awaiting user**: explicit go on the sweep batch. The pilots already produced 3 fixed errors; the sweep is the proper Option A execution.
