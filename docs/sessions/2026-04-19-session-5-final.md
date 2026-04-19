---
title: Session 5 final handoff — citation pipeline + ZTT-to-prereq batch
date: 2026-04-19
---

# TL;DR

Session 5 built the citation backfill pipeline end-to-end: a scorer
that tells the truth, a deterministic fetcher proven against 20
allowlist tiers, a research step that honestly classifies claims
into 5 dispositions (including `unciteable` and `soften_to_illustration`),
and an inject step that mechanically applies structured edit plans
without touching prose outside authorized rewrites. A 65-module
batch (remaining ZTT + all AI + all non-ZTT prereqs) is running as
of this write. Nothing is pushed to GitHub. Staging files
(`module.staging.md`) stay local (gitignored) — the decision to
promote staging → real is explicitly yours, not the pipeline's.

# Commits landed this session (13 commits on main, not pushed)

| # | SHA | What |
|---|---|---|
| 1 | `c1220cd0` | Scorer citation gate + Pyright cleanup (avg 4.71 → 1.50; 726/726 critical) |
| 2 | `1918d262` | Unify `## Sources` header across v1 pipeline + tests |
| 3 | `6bb8dd54` | Session 5 handoff (first half) |
| 4 | `df4f64bf` | Fetcher + tiered trusted-domain allowlist (20/20 dry-run) |
| 5 | `dc34bf4b` | STATUS refresh |
| 6 | `c0fcf450` | Research step + seed schema + first ZTT 0.1 seed |
| 7 | `786a09d3` | Disposition-aware research (3 dispositions: supported/weak_anchor/unciteable) |
| 8 | `bec88105` | Inject step + revision queue for unciteable claims |
| 9 | `a769aede` | ZTT 0.2 + 0.11 seeds — scale validation |
| 10 | `aaf8afdb` | Session 5 addendum doc |
| 11 | `8966ae32` | 5-disposition schema, hard-cite rule, audience tiers |
| 12 | `9bc4a722` | Markdown-aware claim_text matching in inject step |
| 13 | (this file) | Session 5 final handoff |

# What works, what doesn't

## Works end-to-end (production-grade)

- **Heuristic scorer** (`scripts/local_api.py::build_quality_scores`)
  — fails any module without `## Sources` section, surfaces 726/726
  critical until backfill lands. Real baseline.
- **Fetcher** (`scripts/fetch_citation.py`) — browser UA, text
  extraction via stdlib `html.parser`, on-disk cache gitignored.
  20/20 dry-run against allowlist tiers: NIST, OWASP, AWS, GCP,
  Azure, CISA, Anthropic, GitLab, CERN, Wikipedia — all return real
  text. Off-allowlist correctly rejects.
- **Allowlist** (`docs/citation-trusted-domains.yaml`) — tiered by
  claim class (standards / upstream / vendor / incidents / general)
  with expansion hosts added after ZTT 0.1 calibration:
  about.gitlab.com, home.cern, gs.statcounter.com,
  blog.cloudflare.com.
- **Research step**
  (`scripts/citation_backfill.py research <module-key>`) — disposition
  aware, audience calibrated, hard-cite rule enforced.
  Three iterations made it robust: v1 forced anchors, v2 added 3
  dispositions, v4 expanded to 5 with hard-cite for war stories.
  The ZTT 0.1 v4 seed produces 14 claims: 7 supported, 4 soften,
  3 salvage.

## Works but has rough edges

- **Inject step**
  (`scripts/citation_backfill.py inject <module-key>`) — produces
  a valid staging file with all inline wraps + Sources section.
  Rewrite-emission was silently dropping 5/5 prose rewrites before
  the `9bc4a722` markdown-normalization fix. Post-fix, re-dispatch
  was in flight at handoff time; whether it lands clean is TBD in
  the next session.
- **Diff linter** (`_verify_diff_is_additive`) — strict enough to
  catch prose-change anomalies, permissive enough to allow
  authorized rewrites. The `_find_claim_span_in_line` helper walks
  markdown noise and builds normalized→original index maps.

## Doesn't exist yet

- **Verify step (Gate B).** The 2-LLM semantic-agreement check
  designed during the session-5 Gemini+Codex consult is NOT built.
  Current pipeline trusts Codex's claim→URL pairing and the
  deterministic URL+allowlist gate. Good enough for MVP; a future
  session should add a second LLM reading cached page text and
  emitting SUPPORTED/UNSUPPORTED labels per claim.
- **Merge workflow.** `module.staging.md` files sit alongside
  `module.md`. Nothing auto-promotes them. You explicitly flagged
  "no humans in the loop" but also that big pedagogical decisions
  aren't for the pipeline to make. That tension resolves in a
  follow-up: auto-promote once the verify step is live AND a
  deterministic-only gate signs off.
- **Revision worker.** Modules with `needs_allowlist_expansion`
  claims write a JSON record to `.pipeline/citation-revisions/`
  but nothing acts on it. Same pattern for `cannot_be_salvaged`
  claims after their prose rewrites land. A future pass surfaces
  these as a review queue.

# Calibration findings (ZTT 0.1 over 4 iterations)

| Iter | Dispositions surfaced | Key insight |
|---|---|---|
| v1 | 10 claims, 0 honest flags | Codex forced weak anchors on every claim |
| v2 | 8 claims, 4 unciteable (single bucket) | Added `unciteable` disposition; surfaced hallucinated AWS price |
| v3 | 12 claims, 5 supported / 4 soften / 3 salvage | Expanded allowlist, added 3-way split — found StatCounter+GitLab primaries |
| v4 | 14 claims, 7 supported / 4 soften / 3 salvage | Hard-cite rule for war_story/incident/standard; AWS price correctly cannot_be_salvaged |

Open prompt edge: Codex sometimes labels rough behavior-numbers as
`statistic` (hard-cite class), triggering a schema violation when
it softens them. Next iter: tighten `statistic` vs `benchmark`
definitions in the research prompt.

# Aggregate stats from the biking-time batch

*(to be filled in after batch completes; see
`/tmp/ztt_ai_prereq_batch.sh` output log)*

Target set: 65 modules across remaining ZTT (7), AI (25), non-ZTT
prereqs (33).
As of handoff-write: 4 seeds present (ZTT 0.1, 0.2, 0.3, 0.4),
61 pending.

# Known issues for next session

1. **Inject rewrite-emission confirmation pending.** Re-dispatch
   is running; need to verify post-fix staging has all rewrites
   applied AND diff linter stays clean. If it does, scale inject
   across the batch-produced seeds. If not, there's another
   emission layer bug to chase.

2. **Statistic-vs-benchmark class boundary.** Codex's mental model
   of "statistic" is too broad. Claims like "30 tabs use 4-6 GB"
   (which is really a rough behavior benchmark) get classed as
   `statistic`, tripping the hard-cite rule. Fix: tighten the
   research prompt's class definitions.

3. **Some ZTT modules may have pre-existing off-allowlist
   citations.** ZTT 0.1 original already links StatCounter (now
   allowlisted — no issue) and GitHub (OK). Future modules may
   link blogs/medium/etc. The pipeline currently adds citations
   but doesn't remove or audit existing ones. Worth a separate
   lint pass once the backfill lands.

4. **User-pending tactical decisions:**
   - When to promote staging → real (probably after verify step).
   - Whether to push the 13 commits to origin.
   - How to handle the `needs_allowlist_expansion` queue.
   - Whether to tackle the remaining Pyright issues in
     `v1_pipeline.py` (10 errors, all pre-existing).

# Autonomous work plan (what I'll do while you bike)

1. Monitor the 65-module research batch; resumable if it stalls.
2. Once research is done, run inject on a representative sample
   (3–5 modules across tracks) to confirm the normalization fix
   holds beyond ZTT 0.1.
3. Gemini adversarial review on ZTT 0.1 staging — whatever the
   inject state is at that point, get an independent opinion.
4. Aggregate stats into this handoff (disposition distribution,
   unciteable rate, allowlist-expansion candidates per track).
5. Commit seeds batch. Commit any prompt iteration that comes out
   of Gemini review. Do NOT promote stagings to real.
6. Leave a `WHILE-BIKING.md` summary in the repo root if anything
   unexpected happens — so you see it immediately.

# Budget and env notes

- Codex budget: 10× quota runs to 2026-05-17; session used ~5 of
  it. Plenty of runway.
- Gemini: Pro as reviewer default. 900s timeout per dispatch.
- Bridge concurrency: observed OK at 4 concurrent dispatches
  (inject + 3 research) during this session. Batch runs
  sequentially by default to avoid risk.
- `.pipeline/citation-fetch-cache/` gitignored, grows with every
  URL fetched; safe to delete, will re-fetch.
- `.pipeline/citation-revisions/` gitignored too.

# How a fresh agent picks up this thread

1. Read this doc + STATUS.md.
2. Check the monitor batch output if still running; otherwise
   `ls docs/citation-seeds/` to see what's there.
3. `.venv/bin/python3 scripts/citation_backfill.py inject <module-key>`
   runs inject on any seeded module.
4. Compare `module.md` vs `module.staging.md` with `diff -u` to
   audit a single module before deciding on promotion.
5. `.venv/bin/python3 scripts/check_citations.py <path>` validates
   the deterministic gate on a staging file.
6. Bridge DB at `.bridge/messages.db` has the full Codex/Gemini
   conversation history; query by `task_id LIKE 'citation-%'` to
   inspect raw model responses.
