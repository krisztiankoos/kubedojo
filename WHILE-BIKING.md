---
title: While-biking report — inject rewrite-emission bug is a schema issue, not an emission bug
date: 2026-04-19
author: Claude (session 6 cold start)
---

# TL;DR

The `9bc4a722` markdown-normalization fix got inline-wraps landing
(5/5 in ZTT 0.1), but prose_rewrites are still 0/7. Root cause
found, verified by direct inspection of message_id 356 (last
Codex inject response) and the seed/body pair. It is **not** an
emission-layer bug. Codex honestly emits `prose_rewrites: []`
because the seed's `claim_text` is a paraphrase of the module
text, not a verbatim substring. The orchestrator's
`_find_claim_span_in_line` normalizer handles markdown noise
(\`\`, \*\*, \_) but not paraphrase differences ("Thirty" vs "30",
"at 60.8%" vs "StatCounter: 60.8% worldwide", etc.).

**No further inject runs should dispatch until this is fixed.**
I did not run inject on ZTT 0.2–0.5 after confirming the
diagnosis — it would burn Codex quota reproducing the same
failure mode.

# Evidence

Seed (ZTT 0.1, C002):
```
claim_text: "Thirty browser tabs alone can eat 4-6 GB of RAM."
```
Body (line 99):
```
...Each program needs counter space, and 30 browser tabs alone
 can eat 4-6 GB. The OS starts shuffling...
```

Seed (ZTT 0.1, C003):
```
claim_text: "Windows is the most common desktop OS worldwide at 60.8% in March 2026."
```
Body (line 143):
```
Windows  → The most common desktop OS (StatCounter: 60.8% worldwide, March 2026)
```

`_normalize_for_match` strips \`\*\_\\\\\s — after normalization
both sides still differ in word order and in numerals ("Thirty"
vs "30"). No substring match ⇒ Codex reports
`claim_text_not_found` or emits `prose_rewrites: []`.

Inject prompt line 828 actively tells Codex: "If `claim_text`
does not appear in `target_line` you picked the wrong line —
revise." Codex is obeying exactly. The bug is in the prompt
contract, not in Codex's output.

# Scope across the 5 seeded ZTT modules

| Module | Cited | Rewrite | Deferred | Total |
|---|---|---|---|---|
| 0.1 what-is-a-computer | 7 | 7 | 0 | 14 |
| 0.2 what-is-a-terminal | 5 | 2 | 0 | 7 |
| 0.3 first-commands    | 6 | 1 | 3 | 10 |
| 0.4 files-and-dirs    | 5 | 2 | 0 | 7 |
| 0.5 editing-files     | 7 | 4 | 0 | 11 |
| **Totals**            | **30** | **16** | **3** | **49** |

16 rewrites across 5 modules are currently blocked. 30 inline
wraps should still land cleanly (confirmed on 0.1; strongly
expected on 0.2–0.5).

# Two fix paths — user call

## Path A (smallest surface, orchestrator-only)

Change `apply_inject_plan` so the orchestrator auto-discovers
target_line for every authorized rewrite the plan did not
emit. Use token-set overlap (≥75% of claim_text tokens present
in a single line; tiebreak by `span_hint` section header).
Replacement text still comes from the seed — Codex has no new
trust. Drop the "Codex must emit prose_rewrites" expectation
from the prompt entirely; keep it as a pure anchor finder for
inline wraps + sources.

- **Pros**: no seed re-research; no schema change; works on
  existing seeds including the ZTT batch-in-flight.
- **Cons**: token-overlap heuristic can mis-target if a
  paraphrase matches two lines; needs a confidence threshold
  and a reject path. Adds ~80 LOC to `citation_backfill.py`.

## Path B (seed schema evolution)

Add `anchor_text` to every rewrite-disposition claim — a
VERBATIM substring from the module body that the orchestrator
can substring-swap for `suggested_rewrite`. Update the research
prompt to emit it; update the orchestrator to use it. Re-run
research on the 5 seeds (ZTT 0.1–0.5).

- **Pros**: deterministic; no heuristic; clearest audit trail.
- **Cons**: re-research cost (5 Codex dispatches @ ~30s each =
  cheap); re-invalidates the in-flight 65-module batch's
  rewrite-disposition claims (all would need `anchor_text`
  added).

# My recommendation

Path A. The orchestrator already has `_find_claim_span_in_line`
and `_authorized_replacement_lines` — extending with fuzzy
target-line discovery is a natural evolution. It rescues seeds
already paid for (the 5 ZTT seeds; whatever comes out of the
65-module batch) without a schema-break. If token-overlap proves
unreliable at scale, Path B becomes a graceful follow-up (add
`anchor_text`, keep Path A as fallback for legacy seeds).

# What I did NOT do

- Did not promote any staging → real.
- Did not run inject on ZTT 0.2/0.3/0.4/0.5 — would burn quota
  confirming a bug already diagnosed.
- Did not push commits.
- Did not modify `citation_backfill.py` — the fix is
  structural enough that you flagged such calls as yours.

# What I will do when you confirm

If Path A: implement `_auto_discover_rewrite_target` in
citation_backfill.py, extend `apply_inject_plan` to auto-populate
missing rewrites, re-run inject on ZTT 0.1 to validate
end-to-end, then scale to 0.2–0.5.

If Path B: draft the research-prompt update + seed-schema v2 +
orchestrator changes as a single diff; wait for another
confirmation before re-dispatching research.

# Known-unknowns worth flagging

- The 65-module research batch is **stalled**. Last bridge
  message is 09:14:51 UTC (~2h before this write), a research
  dispatch for ZTT 0.6 `git-basics` that never produced a seed
  (no response row, no `docs/citation-seeds/...-0.6-git-basics.json`).
  Only ZTT 0.1–0.5 made it through. No orchestrator process is
  running (`ps` clean; no citation pid). "65 modules in flight"
  in the session 5 handoff was optimistic — the pipeline is
  sequential-by-design and simply stopped after 5.
- The `statistic` vs `benchmark` boundary note from session 5
  is still unresolved. Not a blocker for Path A.
