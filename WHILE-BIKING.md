---
title: Session 6 progress — Path B landed, ZTT 0.1–0.5 stagings clean
date: 2026-04-19
author: Claude (session 6)
---

# TL;DR

Path B schema v2 (anchor_text) shipped. Orchestrator now applies
prose rewrites deterministically from the seed's verbatim anchor;
Codex no longer participates in rewrites. All five seeded ZTT
stagings (0.1–0.5) are clean: 27 inline wraps + 14 rewrites +
4 fallback phrase-matches, 0 rejections, 0 diff-lint issues,
`check_citations.py` PASS on every staging.

Nothing pushed to origin. Nothing promoted from staging → real.

# Commits landed this session

| SHA | What |
|---|---|
| `e32dba68` | Path B schema v2 + orchestrator rewrite loop + order flip |
| (pending) | URL paren percent-encoding + phrase-uniqueness fallback for inline validation |

# What the refactor changed

1. **Schema v2**: every `soften_to_illustration` or
   `cannot_be_salvaged` claim carries an `anchor_text` field — a
   VERBATIM single-line substring of the module body. Research
   prompt has a dedicated section enforcing the rules.
2. **Inject contract**: Codex is explicitly told NOT to emit
   `prose_rewrites`. The orchestrator iterates authorized
   rewrites from the seed and substring-swaps anchor_text →
   suggested_rewrite.
3. **Application order**: inline insertions FIRST, rewrites
   SECOND. Inlines don't mutate anchor sentences, so anchor
   substring matching still works after wraps are applied.
4. **URL paren encoding**: Wikipedia disambiguator URLs
   (`/wiki/Shebang_(Unix)`, `/wiki/Ed_(text_editor)`) broke the
   `[phrase](url)` markdown syntax because the regex stopped at
   the first `)`. The orchestrator now percent-encodes parens
   in URLs at insert time (inline wraps + sources section).
5. **Phrase-uniqueness fallback**: when Codex's `target_line`
   has been mutated by an earlier inline on the same line and
   the `phrase` is still unique in the body, the orchestrator
   wraps it directly instead of rejecting. Validation no
   longer requires target-in-body — only shape.
6. **Fail-fast**: `run_inject` validates anchor_text against
   body BEFORE dispatching Codex, saving quota on broken seeds.

# Results on ZTT 0.1–0.5

| Module | Claims | Inline | Rewrite | Fallback | Sources |
|---|---|---|---|---|---|
| 0.1 what-is-a-computer    | 10 | 4 | 5 | 0 | 11 |
| 0.2 what-is-a-terminal    |  9 | 8 | 1 | 1 |  9 |
| 0.3 first-commands        | 10 | 3 | 3 | 1 |  6 |
| 0.4 files-and-directories | 10 | 8 | 2 | 2 | 10 |
| 0.5 editing-files         |  7 | 4 | 3 | 0 |  5 |
| **Totals**                | **46** | **27** | **14** | **4** | **41** |

All five staging files pass `check_citations.py` and all five
coverage gates come back green.

# What's NOT done

- The 65-module batch is still stalled. Not touched in this
  session — the seeds it would produce would all be schema v1
  (no anchor_text); they'd need re-research anyway.
- No stagings promoted to real. Still your call — and the
  logical moment is after a Gemini adversary pass.
- Verify step (Gate B, 2-LLM semantic-agreement check) still
  doesn't exist.
- The statistic-vs-benchmark boundary in the research prompt
  still trips 3 false-positive `hard_cite_class_cannot_soften`
  schema warnings across 0.1/0.3/0.4. Not blocking inject; the
  claim still applies correctly.

# Suggested next moves (your call)

1. Gemini adversary review on ZTT 0.1 staging (and/or 0.2–0.5)
   — independent eyes before promotion.
2. Promote stagings → real for the 5 ZTT modules if Gemini
   approves, then push.
3. Kick the 65-module batch with schema v2 — probably via a
   small orchestrator script that dispatches research
   sequentially and stops on parse failure.
4. Pave over the statistic-vs-benchmark prompt edge.
