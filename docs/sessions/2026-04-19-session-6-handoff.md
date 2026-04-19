---
title: Session 6 handoff — four content gates + ZTT 0.1–0.5 promoted; v3 e2e pipeline next
date: 2026-04-19
---

# TL;DR

Session 6 delivered four independent content-quality gates (overstatement,
semantic-verify, unsourced-assertion, topical-coherence), promoted ZTT 0.1–0.5
from staging to main, applied 27 user-audited fixes, and confirmed the
citation pipeline is trustworthy at the URL↔claim level (Gate B: 28/28
SUPPORTED). Next session: build **pipeline_v3.py** — the full e2e
orchestrator with auto-apply — and run ZTT 0.6–0.11 through it.

Nothing pushed. User explicitly wants commit + push **after** ZTT 0.6–0.11
is ready.

# Session 6 commits landed (main, NOT pushed)

Path B + gates branch, in order:
1. `e32dba68` feat(citations): Path B — anchor_text v2 schema, orchestrator-driven rewrites
2. `d9b88421` fix(citations): URL paren encoding + phrase-uniqueness fallback
3. `1eade06d` content(ztt): promote cited stagings to main + user-reviewed content fixes
4. `843b3b53` feat(gates): overstatement-detection gate (deterministic + LLM)
5. `7e353362` feat(gates): Gate B — semantic verification of citation seeds
6. `c0658ce2` feat(gates): Gate C — unsourced-assertion detector
7. `de3a80e0` feat(gates): Gate D — topical-coherence auditor
8. `11953285` content(ztt): apply gate audit fixes to ZTT 0.1-0.5

# Key user decisions baked in

- **No staging scaffolding.** Inject writes to `module.md` directly. The
  `.staging.md` pattern from session 5 is deprecated. Git diff is the review
  surface. (See: memory file `feedback_no_staging_scaffolding.md`.)
- **E2E automation is the goal.** Don't propose "faster but less ambitious"
  alternatives. Target best-possible-without-overengineering.
- **Schema v2 (anchor_text)** is the seed contract. Research step emits
  verbatim substring anchors; orchestrator substring-swaps deterministically.
- **Delegation**: inline-fix iteration edits <50 LOC; delegate bulk to Codex.
  Run heavy pipelines so raw output never streams through Claude context —
  pipe to files, only read summaries.

# What's built (scripts/)

- `citation_backfill.py` — research + inject (schema v2, anchor_text). **Will
  need refactor** in session 7 to drop staging-file write path and land
  edits in place.
- `fetch_citation.py` — allowlisted URL fetcher with on-disk cache.
- `verify_citations.py` — Gate B, 2-LLM semantic verification.
- `check_overstatement.py` — Gate A, 22 trigger patterns + Codex triage.
- `check_unsourced.py` — Gate C, factual-signal patterns + Codex triage.
- `check_coherence.py` — Gate D, section-batched Gemini audit.
- `check_citations.py` — pre-existing deterministic citation presence check.

# What's left to build (pipeline_v3)

A single orchestrator script `scripts/pipeline_v3.py <module-key>`:

```
research (Codex)
  → verify / Gate B (Gemini) — fail if any UNSUPPORTED/CONTRADICTED
  → inject (orchestrator + Codex) — writes module.md IN PLACE
  → audit: A (pattern + Codex triage), C (pattern + Codex triage),
           D (Gemini per section)
  → auto-apply:
      - Gate A overstated + suggested_rewrite → substring swap
      - Gate D off_topic + delete → paragraph/row removal
      - Gate D off_topic + rewrite_to_fit → Codex rewrite pass
      - Gate C needs_citation → secondary research for the claim
  → re-audit (idempotence check) — if clean, done; else queue to
    .pipeline/v3/human-review/<module>.json
  → emit compact summary line to .pipeline/v3/summary.jsonl
```

Plus `scripts/pipeline_v3_batch.py` for module lists. Output-to-file so raw
content never hits the orchestrator's context.

**Estimated auto-apply coverage**: ~75% of gate findings are deterministically
auto-applicable; ~25% queue for human review. At scale: 525/700 auto-fixed,
175 queued — far better than today's all-manual.

# What's left to remove (cleanup inline with v3 build)

- `src/content.config.ts` line 9: the `!**/*.staging.{md,mdx,…}` exclusion
  pattern. Now orphaned.
- `citation_backfill.py run_inject`: the `staging_path.write_text(...)` call;
  inject should write to `module_path` directly.
- Any `.staging.md` file left anywhere (grep the tree — there are none after
  the promotion commit, but verify before deleting the glob exclusion).

# State of ZTT (track)

| Module | Stage | Notes |
|---|---|---|
| 0.1 what-is-a-computer | ✅ promoted + audited + 7 fixes | clean |
| 0.2 what-is-a-terminal | ✅ promoted + audited + 4 fixes | clean |
| 0.3 first-commands | ✅ promoted + audited + 10 fixes | clean; Pixar war story intentionally uncited (no reliable primary URL) |
| 0.4 files-and-directories | ✅ promoted + audited + 2 fixes | clean |
| 0.5 editing-files | ✅ promoted + audited + 4 fixes | clean |
| 0.6 git-basics | 🔜 seed exists (just researched); needs v3 pipeline | do NOT manually inject with current pipeline — wait for v3 |
| 0.7 what-is-networking | 🔜 unseeded | — |
| 0.8 servers-and-ssh | 🔜 unseeded | — |
| 0.9 software-and-packages | ✅ mermaid quoted; otherwise original content | — |
| 0.10 what-is-the-cloud | 🔜 unseeded | — |
| 0.11 your-first-server | 🔜 unseeded | — |

Ukrainian translations: not touched in session 6. Need a separate UK-drift
gate once v3 is stable.

# Cold-start playbook for session 7

1. Read this doc + `docs/reviews/ztt-0.1-0.5-gate-audit.md`.
2. `git --no-pager log --oneline origin/main..HEAD` — see the 8 unpushed session-6 commits.
3. Confirm no pending work: `git status -s` should only show
   `.cache/`, `.pipeline/`, and maybe `start-claude.sh` (all pre-session).
4. Start session 7 by building `scripts/pipeline_v3.py`:
   - Import existing stages from citation_backfill, verify_citations,
     check_overstatement, check_unsourced, check_coherence.
   - Orchestrate in one function `run_pipeline(module_key, *, auto_apply=True)`.
   - First dogfood target: ZTT 0.6 (already has a seed from this session).
5. Delete staging scaffolding from `content.config.ts` and
   `citation_backfill.py run_inject` in the same commit as v3 lands.
6. Run 0.6–0.11 through `pipeline_v3_batch.py`.
7. `git push` only after all six land clean + build passes + at least one
   module has been spot-checked visually.

# Budget and env

- Codex 10× quota runs to 2026-05-17 (per memory). Session 6 burned ~15 codex
  dispatches (research + inject + Gate A triage). Plenty of runway.
- Gemini: Pro default. 900s per dispatch. Gate B used ~28 dispatches, Gate D
  used ~14. Plenty of runway.
- Bridge: sequential. For 6 modules × ~15 dispatches each = 90 dispatches in
  v3 batch. Expect ~45-60 min wall-clock.

# Known issues / punch list

1. **Statistic-vs-benchmark boundary** still trips research-prompt schema
   validation in ~10% of modules. Not blocking inject. Prompt iteration
   backlog.
2. **Pixar war story uncited** in ZTT 0.3 L342. Story is real, but I refused
   to fabricate a URL. A proper verified primary source would be ideal.
3. **UK translation drift** on modules that change under the enhanced
   pipeline. No automated sync check yet.
4. **Gate A false-positive on intentional wrong-statement rows** (e.g., ZTT
   0.1 "4 GHz CPU is always better" — inside a Common Mistakes row that
   describes the mistake). LLM triage catches most, but the gate could also
   suppress via a "Common Mistakes" table-row context check.

# References

- `WHILE-BIKING.md` — session 6 interim doc, still accurate.
- `docs/reviews/ztt-0.1-0.5-gate-audit.md` — consolidated audit report.
- `.pipeline/audit-ztt-0.1-0.5/` — per-module raw gate outputs.
- `.pipeline/citation-verdicts/` — Gate B verdicts.
- `docs/citation-seeds/` — research seeds (schema v2, anchor_text).
