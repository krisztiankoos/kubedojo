# Session 2026-05-09 — HTML-first lens revision + #1058 docs MD audit shipped

> **Format:** Markdown per `feedback_html_over_markdown_for_artifacts.md` consumer-direction lens (handoffs are AI→AI; next-session agent reads via `Read` first). HTML reserved for genuinely user-facing handoffs.

## Cold-start (start here, in this order)

1. `curl -s http://127.0.0.1:8768/api/briefing/session?compact=1` — primary orientation. **Caveat:** local API still on stale PID 18362 (predates overnight PRs); user was asked to restart but it's not confirmed. New endpoints `/artifacts`, `/api/state/manifest`, `/api/session/current` will 404 until restart. Restart command: `kill 18362 && python3 scripts/local_api.py --host 127.0.0.1 --port 8768 &` — or check first with `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8768/artifacts`.
2. Read this handoff (you are doing it now).
3. Open `audit/docs-md-triage/index.html` — the user's landing report for the docs/ MD triage. Has 5 DELETE + 11 MIGRATE_HTML candidates the user will action next session.

## Decisions locked this session

### 1. HTML vs Markdown — consumer-direction lens (memory rewritten)

The original "HTML-first for orchestrator artifacts" rule was refined. New lens:

- **AI → Human** (user reads it) → HTML
- **Human → AI** (user types it) → Markdown
- **AI → AI** (next agent reads it) → Markdown

Two artifact classes flipped from HTML to Markdown:
- **Dispatch briefs** — primary consumer is the dispatched agent; first correctly-classified example: `docs/briefs/2026-05-09-codex-desktop-artifacts-ui-brief.md`
- **Session handoffs** (this file) — primary consumer is the next-session AI

Unchanged HTML: batch reports, PR review explainers, bug autopsies, summary audits.

Memory: `~/.claude/projects/-Users-krisztiankoos-projects-kubedojo/memory/feedback_html_over_markdown_for_artifacts.md` (rewritten).
PR: #1059 merged (commit `44d739b8`) — patched `docs/migrations/html-first/plan.html` to encode the lens. Follow-up nits: #1060.

### 2. Deterministic computation over LLM recall (TOP PRIORITY memory)

New rule: any fact a script can compute exactly, the agent MUST compute exactly. Don't ask LLMs to count what `wc -l` answers. Discovered via Gemini flash calibration (#1057) — flash-preview hallucinated line counts off 20-50 % when not pre-supplied. Inlining verified `wc -l` numbers and forbidding recomputation eliminated the hallucination class entirely (40/40 spot-checks passed across the #1058 audit).

Memory: `feedback_deterministic_over_hallucination.md`. Indexed under TOP PRIORITY.

**Pending propagation:** rule needs to be added to `scripts/prompts/{module-writer,module-rewriter-388,teaching-judge,teaching-rewrite}.md` + `scripts/quality/dispatch_388_pilot.py` review template (per `feedback_three_way_rule_agreement.md`). Defer to codex-spark tomorrow when its cap clears (~2026-05-10 09:32 UTC) — preserves codex weekly counter.

### 3. Spark rate-limit fallback ladder (memory)

When `gpt-5.3-codex-spark` hits its usage cap (currently rate-limited until 2026-05-10 09:32 UTC), do NOT reflex-bump to `gpt-5.5`. Fall laterally by complexity:
- Quick / mechanical → `gpt-5.4-mini` or `gemini-3.1-flash-lite-preview`
- Heavier / multi-file → `gemini-3-flash-preview`

Memory: `feedback_spark_rate_limit_fallback_ladder.md`.

### 4. Codex weekly thin — prefer Gemini for non-judgment work (memory)

User signal: "we slowly running out of codex weekly. keep that in mind." Decision tree before each dispatch — if the task doesn't need gpt-5.5's superior intelligence, route to gemini. Reserve codex for review/architect/judgment.

Memory: `feedback_codex_budget_prefer_gemini.md`.

### 5. Gemini flash calibration — flash-preview wins decisively (#1057 closed)

Same prompt, 33 files, classify into 4 categories:
- `gemini-3-flash-preview`: all 4 categories used; content-aware reasons; identified DELETE + MIGRATE_HTML candidates
- `gemini-3.1-flash-lite-preview`: only 2 categories; rubber-stamped with copy-paste reasons; pattern-matched on date alone

**Use `gemini-3-flash-preview` for any audit/triage requiring file content reading.** flash-lite-preview only for templated transformations.

## Shipped this session

### PRs merged
- **#1059** — `docs(html-first): consumer-direction lens — flip briefs + handoffs to Markdown` — gemini-flash review APPROVE_WITH_NITS, nits filed as #1060
- (cherry-picks to main, no PR ceremony for audit artifacts):
  - `17bdd496` — CKA Part 2 batch report (audit/388-cka-part2-batch/index.html, 562 lines)
  - `4090577e` — research/ MD triage report (audit/docs-md-triage/research.html, 4,443 lines)
  - `b66b1874` — research.csv + raw chunk sidecars
  - `b4f396a8` — phase 1+3+4 raw + all.csv (consolidated 750-row sidecar)
  - `064ac4a6` — consolidated index.html (audit/docs-md-triage/index.html, 5,670 lines)

### Issues
- **#1057** — Gemini flash calibration — closed (verdict: flash-preview wins)
- **#1058** — docs/ MD audit + reorg — closed (all 4 phases complete; action queue in closing comment)
- **#1060** — opened (plan.html nits from #1059 review, deferred)

### Memories created/rewritten
| File | Type | Note |
|---|---|---|
| `feedback_html_over_markdown_for_artifacts.md` | rewritten | now leads with consumer-direction lens |
| `feedback_deterministic_over_hallucination.md` | new (TOP PRIORITY) | counts/dates/SHAs from scripts not LLMs |
| `feedback_spark_rate_limit_fallback_ladder.md` | new | flash-lite vs flash routing |
| `feedback_codex_budget_prefer_gemini.md` | new | routing decision tree |

## Outstanding action queue (for user OR next session)

### Immediate (user-facing, ready to execute)
1. **Restart local API** — kill PID 18362 + relaunch to surface `/artifacts`, `/api/state/manifest`, `/api/session/current` endpoints
2. **Execute #1058 action queue:**
   - DELETE 5 files in `docs/research/ai-history/backup_ch01/` (entire dir is superseded duplicates)
   - Open per-file issues for 11 MIGRATE_HTML candidates (see `audit/docs-md-triage/index.html`)
   - Bulk `git mv` 206 ARCHIVE files into `<dir>/archive/` subfolders

### Soft-deferred (low-priority polish)
3. Patch `docs/migrations/html-first/plan.html` line 228 + 429 (issue #1060 nits)
4. Patch `scripts/prompts/*.md` + `scripts/quality/dispatch_388_pilot.py` to encode the deterministic-computation rule (TOP PRIORITY memory binding tooling-side)
5. **Codex-desktop UI brief** at `docs/briefs/2026-05-09-codex-desktop-artifacts-ui-brief.md` — make `/artifacts` a unified HTML + Markdown browser. Brief is ready to paste; user can hand it off any time.

### Already-deferred (waiting on signal)
6. Phase 2 of HTML-first migration plan — PR review explainers — not yet triggered
7. Phase 3 / 4 of HTML-first migration plan — bug autopsies + dispatch briefs — defer per consumer-direction (briefs now MD by default; autopsies still HTML when next incident hits)

## Smoketest (verify-state-fast)

```bash
# Local API healthy + new endpoints live
curl -s -o /dev/null -w "/artifacts %{http_code}\n" http://127.0.0.1:8768/artifacts
curl -s -o /dev/null -w "/api/state/manifest %{http_code}\n" http://127.0.0.1:8768/api/state/manifest

# Audit artifacts present
ls audit/docs-md-triage/         # → all.csv, index.html, raw/, research.csv, research.html
ls audit/388-cka-part2-batch/    # → index.html (562 lines)

# Memory + index synced
ls ~/.claude/projects/-Users-krisztiankoos-projects-kubedojo/memory/feedback_*.md | wc -l   # should include 4 new from this session

# Tree clean
git status --short && git log --oneline -5
```

## Pre-2026-05-09 chain

Predecessor: `docs/session-state/2026-05-10-overnight-html-migration-complete-and-cka-part2-marathon.html` (the overnight chain that landed PRs #1023/#1025/#1026/#1027 and ran the CKA Part 2-5 marathon 29/29).

This session's job was to close the loop on what overnight produced:
- Close out the marathon with a Part 2 batch report (audit/388-cka-part2-batch/index.html)
- Validate the HTML-first policy on real work, refine the lens, propagate
- Audit docs/ MD per #1058 (Gemini-led — first deliberate non-codex bulk dispatch)
