# Session handoff — 2026-04-29 — Part 1 prose drafted + prose pipeline pivot to Codex

Audience: the next session that picks up the AI History book (Epic #394).

This continues `2026-04-28-claude-research-queue-cap-handoff.md`. Big results:

1. **Verdict pass on 15 research PRs (Ch01-10, Ch15, Ch32-35) — all cleared `READY_TO_DRAFT_WITH_CAP`.**
2. **Part 1 prose drafted + expanded for all 5 chapters (Ch01-05) — ~17.3k words across 5 PRs (#477, #479, #480, #481, #483).**
3. **Prose pipeline pivot: Codex (gpt-5.5) replaces Claude opus as the default expander.** Workflow + dispatcher updated.
4. **Part 9 (Ch 59-68) ownership transferred from Claude to Codex** for both research and prose. Claude now owns research on Parts 1, 2, 3, 6, 7; Codex now owns research on Parts 4, 5, 8, 9.
5. **Two new helper scripts shipped:** `dispatch_research_verdict.py` (codex+gemini cross-family verdict on research PRs) and `dispatch_chapter_prose.py` (Gemini draft → Codex/Claude expand).
6. **Ch36/Ch37 research dispatches that were in flight at the prior handoff completed; PRs #475/#476 opened (paused per Part-priority).**

Nothing destructive landed.

## What this session shipped

### Cross-family verdict pass — 15 research PRs, all cleared

Built `scripts/dispatch_research_verdict.py` — Codex anchor verification + Gemini lane-disciplined gap audit (no URLs from Gemini per Issue #421). Ran against the 15 chapter-research PRs from the prior session.

**All 15 returned `READY_TO_DRAFT_WITH_CAP`** from BOTH cross-family reviewers. Per-chapter verdict caps:

| PR | Ch | Cap | Caveats |
|---|---|---:|---|
| #456 | 01 | 5000 | page-anchor cleanup; biographical Yellows |
| #459 | 02 | 5000 | Hilbert-Ackermann edition / Davis lineage / Church-1937 hedges |
| #460 | 03 | 4000–5000 | no leaning on unfetched MIT thesis signature/supervisor anchors |
| #462 | 04 | ~4500 | hedge Nekrasov/Chuprov; fix Shannon approximation labels |
| #463 | 05 | ~4500 | cap at verified Green technical layers; biographical Yellows thin |
| #466 | 07 | n/a | (verdict OK; not yet drafted) |
| #467 | 06 | n/a | (verdict OK; not yet drafted) |
| #468 | 08 | n/a | |
| #469 | 09 | n/a | |
| #470 | 10 | n/a | |
| #457 | 15 | n/a | (Part 3 — research done) |
| #471–474 | 32–35 | n/a | (Part 6 — research done, prose paused per directive) |

### Part 1 prose pipeline (Ch01-05) — drafted + expanded

Built `scripts/dispatch_chapter_prose.py`. The prior pipeline:

```
Gemini first draft (~3k) → Claude opus expansion to cap
                         → Codex prose review
                         → Claude prose review (independent)
```

| Ch | PR | Branch | Final words | Codex review | Claude review | Fixes applied |
|---|---|---|---:|---|---|---|
| 01 | [#477](https://github.com/kube-dojo/kube-dojo.github.io/pull/477) | `prose/394-ch01` | 3766 | NEEDS_FIX_AND_MERGE — done | NEEDS_FIX_AND_MERGE — done | Codex (2/2) ✅ · Claude (4) **pending** |
| 02 | [#479](https://github.com/kube-dojo/kube-dojo.github.io/pull/479) | `prose/394-ch02` | 3991 | NEEDS_FIX_AND_MERGE — done | — | Codex (5/8) ✅ · Codex (3 left) + Claude pending |
| 03 | [#480](https://github.com/kube-dojo/kube-dojo.github.io/pull/480) | `prose/394-ch03` | 3168 | NEEDS_FIX_AND_MERGE — done | — | Codex (5/5) ✅ · Claude pending |
| 04 | [#481](https://github.com/kube-dojo/kube-dojo.github.io/pull/481) | `prose/394-ch04` | 3186 | NEEDS_FIX_AND_MERGE — done | — | pending · Claude pending |
| 05 | [#483](https://github.com/kube-dojo/kube-dojo.github.io/pull/483) | `prose/394-ch05` | 3959 | — | — | Codex review pending · Claude pending |

Notable mid-pipeline events:

- **Ch01 Gemini hit 429 mid-draft** (committed 1917 words) on the API-key Gemini path while the verdict batch was also using Gemini. Switched Ch01 retry to subscription/OAuth path (`KUBEDOJO_GEMINI_SUBSCRIPTION=1`) — Claude opus expansion read the partial Gemini draft and completed all 5 scenes to 3794 words. **The cutoff did not leave Ch01 incomplete.**
- **Codex prose reviews caught real factual errors.** Ch02 had "Half a decade before any engineer had wired together a physical stored-program machine" — wrong, stored-program machines arrived 1948 (12+ years after 1936). Fixed to "More than a decade before". Other fixes: `one-way-extending tape` → `one-dimensional tape divided into squares`; tighter Princeton/Procter hedge; replaced over-evocative "fortnights / steam" paragraph; replaced "Church didn't capture engineers/physicists" with the contract-supported Church-1937 review point.
- **Independent Claude review on Ch01 caught the De Morgan letter mis-located** (the letter was to W.R. Hamilton, not Boole-De Morgan correspondence as the prose implied), the SEP "preserved through" framing slip, an unmarked elision in the trichotomy quote, and a small Trinity/Maynooth aside scope drift. **All four still pending application** — they are surgical (~5-10 min inline).

### Part 6/7 research — sunk-cost work

The prior session's Ch36/Ch37 dispatches were still running at the start of this session. They completed cleanly:

- **Ch36 — The Multicore Wall** (PR #475, 17 Green / 6 Yellow / 3 Red). Thesis: May 7, 2004 Tejas cancellation as the moment mainstream desktop CPUs stopped being single fast scalar processors.
- **Ch37 — Distributing the Compute** (PR #476, 19/3/3). Thesis: AI inherited a compute substrate (Hadoop) built for web search, not commissioned for AI.

Per user 2026-04-29 directive ("focus on Part 1 then Part 2 then Part 3"), **Ch38–49 research dispatches were NOT fired**. The 14-chapter Part 6/7 research queue from the prior handoff is still pending; resume after Parts 1-3 ship.

### Prose pipeline pivot — Codex default expander (the headline change)

Codex proposed a better pipeline mid-session, the user adopted it. The 2026-04-29 pivot:

```
Approved contract → Gemini first draft (~3k)
    → Codex (gpt-5.5, reasoning=high) expansion to cap   [DEFAULT]
      Claude opus expansion to cap                       [FALLBACK when Codex bandwidth exhausted]
    → Claude source-fidelity review (independent fresh session)
    → Gemini OR Claude prose-quality review
    → merge
```

**Why Codex is the default expander:**

- gpt-5.5 has wider weekly bandwidth than Claude opus
- Codex's source-discipline instinct is the strongest of the three families
- Expansion task ("shape, tighten, enforce source discipline") is Codex's strength
- Saves Claude opus quota for source-fidelity review where independence matters

**The strict-source rule applies to BOTH expanders** (Codex default, Claude fallback): use only the provided contract and claim matrix; if evidence is missing for a scene, leave the scene thin rather than filling it. Concretely — no source additions, no new page anchors, no Yellow→Green upgrades, no invented examples or institutional motives, no expansion beyond the approved Prose Capacity Plan.

Updated artifacts:

- `docs/research/ai-history/TEAM_WORKFLOW.md` — § 5 split into 5a (Gemini draft) + 5b (Codex/Claude expansion); § 6 = Claude source-fidelity review; § 7 = Gemini-or-Claude prose-quality review. Strict-source rule pulled out as load-bearing.
- `docs/research/ai-history/README.md` — role-split section rewritten with the prose-pipeline diagram.
- `scripts/dispatch_chapter_prose.py` — adds `codex` phase, defaults `--phases` to `gemini,codex`, shares the strict-source expansion prompt across Codex and Claude.

Commit: `e75a5722`.

**Part 1 (Ch01-05) used the prior Claude-default pipeline and is in-flight at review/merge — no rework. Part 2 forward uses the new pipeline.**

## In flight at handoff

Nothing currently dispatched. Monitor `b6acqjuwl` timed out earlier in the session; not re-armed at handoff.

## Last-mile changes after the prose pivot commit (`e75a5722`)

Three additional changes landed after the pivot commit:

1. **Codex Ch03 fix-applier** ran (task `b3pplb6bd`, workspace-write on `.worktrees/prose-394-ch03`). Codex applied all 5 surgical fixes from his own review of PR #480 (Shannon's day-to-day MIT work hedged, Bell System oxidation overclaim removed, Turing duality paragraph compressed, Bell Labs uptake / MIT curriculum claim removed, Gardner Yellow quote removed). Word count 3377 → 3168. Codex could NOT commit because workspace-write blocked `.git/worktrees/<name>/index.lock` — orchestrator committed on Codex's behalf (commit `c7c3dfd2`).
2. **Part 9 ownership transfer.** Per user 2026-04-29, Part 9 (The Product Shock & Physical Limits, Ch 59-68) moved from Claude to Codex for both research and prose. Updated TEAM_WORKFLOW.md Roles section and README.md ownership table. Claude now leads research on Parts 1, 2, 3, 6, 7; Codex now leads research on Parts 4, 5, 8, 9.
3. **Codex expansion now uses `danger` mode.** Per the Ch03 fix-applier observation above, `dispatch_chapter_prose.py` was patched to dispatch Codex in `mode="danger"` instead of `workspace-write`. Gemini and Claude stay on workspace-write (no .git/worktrees lock contention from those clients). This matches the documented pattern in `feedback_codex_workspace_write_default.md` and the prior session's "always use mode=danger for codex prose worktrees" lesson.

Commit landing all three: `e35107cf`.

## Cold-start function — the next session should run this

```bash
# 1. Where are we on AI History?
curl -s 'http://127.0.0.1:8768/api/briefing/session?compact=1' | head -50
source ~/.bash_secrets && gh pr list --search "is:open author:@me" --json number,title --limit 30

# 2. Did Codex's Ch03 fix-applier land cleanly?
gh pr view 480 --json commits --jq '.commits[].messageHeadline'
# Expected: a "docs(ch-03): apply Codex prose review fixes" commit on prose/394-ch03

# 3. What's the current state of the 5 Part 1 prose PRs?
for pr in 477 479 480 481 483; do
  gh pr view $pr --json state,mergedAt,reviewDecision \
    --jq "\"#$pr: \(.state) merged=\(.mergedAt // \"no\") review=\(.reviewDecision // \"none\")\""
done

# 4. Is gpt-5.5 cap healthy? (for Codex expansion + fix work)
.venv/bin/python - <<'EOF'
import sys; sys.path.insert(0, "/Users/krisztiankoos/projects/kubedojo/scripts")
from agent_runtime.runner import invoke
try:
    r = invoke("codex", "Reply with 'ok' and nothing else.",
               mode="read-only", model="gpt-5.5",
               task_id="cap-probe-codex", entrypoint="consult",
               hard_timeout=120)
    print("codex gpt-5.5 ok:", r.ok, repr(r.response[:40]))
except Exception as e:
    print("codex still capped:", type(e).__name__, str(e)[:200])
EOF
```

## Pending action items at handoff (priority order)

### Priority 1 — close the loop on Part 1 (Claude-pipeline cohort)

1. **Ch01 (PR #477):** apply the 4 Claude review fixes inline — De Morgan letter recipient (was to W.R. Hamilton, not Boole-De Morgan correspondence), "seventy years later" → ~63, SEP "preserved through" → "as cited in", unmark trichotomy elision. ~10 min surgical work.
2. **Ch02 (PR #479):** apply 3 deferred Codex fixes — ω-consistency vs consistency in the Gödel paragraph, "Hastily drafted" tempo, "Until 1936, computation had assumed..." sweeping framing. ~10 min OR dispatch Codex on the remaining 3.
3. **Ch03 (PR #480):** Codex fixes landed (commit `c7c3dfd2`, 3168 words). Fire Claude source-fidelity review.
4. **Ch04 (PR #481):** dispatch Codex to apply the ~5 review fixes (mirror the Ch03 pattern in `/tmp/ch03-codex-fix-prompt.md`). Then Claude review.
5. **Ch05 (PR #483):** dispatch Codex prose review (cross-family, gpt-5.5 read-only). After fixes, dispatch Claude review.
6. **Merge each PR** when both reviews come back READY.

### Priority 2 — Part 2 prose pipeline (Ch06-10, the new Codex-default pipeline)

All 5 verdicts are in (READY_TO_DRAFT_WITH_CAP). Fire `dispatch_chapter_prose.py` with default `--phases gemini,codex`. Ch06 → Ch10 sequentially, ~25-40 min/chapter (10 min Gemini + 15-30 min Codex). Per-chapter caps come from the Codex/Gemini verdict comments on each PR — read them via `gh pr view <pr> --json comments`.

```bash
.venv/bin/python scripts/dispatch_chapter_prose.py 6 \
  --slug ch-06-the-cybernetics-movement \
  --research-branch claude/394-ch06-research \
  --cap-words <from verdict> \
  --verdict-notes-pr 467
# (default --phases is now gemini,codex — no flag needed)
```

After all 5 expansions, fire cross-family reviews (Codex was the expander → reviewer must be Claude or Gemini). Pattern: `dispatch_research_verdict.py`-shaped prose review with `--only claude` or inline runner.invoke calls.

### Priority 3 — Part 3 prose work (Ch11-16)

- **Ch11–14 prose PRs (#451, #452, #454, #455)** are Codex-drafted and still need cross-family review (must be Claude or Gemini, not Codex). Per the new pipeline, Claude source-fidelity then Gemini prose-quality.
- **Ch15 research PR (#457)** verdict cleared. Fire `dispatch_chapter_prose.py 15 --slug ch-15-the-gradient-descent-concept --research-branch claude/394-ch15-research --cap-words <from-verdict> --verdict-notes-pr 457` with default Codex pipeline.
- **Ch16 research is still `status: researching`** (stub on main). Claude is research lead for Part 3; build the contract via `dispatch_chapter_research.py 16 --slug ch-16-the-cold-war-blank-check`.

### Priority 4 — resume Part 6/7 research queue (after Parts 1-3 ship)

14 chapters still need Claude-owned research contracts: Ch38, 39, 40 (Part 6 remainder), Ch41–49 (Part 7). Pattern is `dispatch_chapter_research.py N --slug ch-NN-...`. The prior handoff's table (`2026-04-28-claude-research-queue-cap-handoff.md`) has the full slug list.

### Priority 5 — close superseded Gemini PRs

#425, #426, #427, #431, #433, #435, #436, #437, #438, #439 are all open and superseded by the Claude-rebuilt research PRs (#456, #467, #468, #459, #460, #462, #463, #470, #469, #466 respectively). Close after replacements merge.

PR #429 (the old Gemini-only Ch01 prose draft) is also open. Close after #477 merges.

## Memories used / created this session

Used: `feedback_dispatch_to_headless_claude.md`, `reference_agent_runtime_dispatch_pattern.md`, `feedback_overnight_autonomous_codex_chain.md`, `feedback_codex_dispatch_sequential.md`, `feedback_claude_weekly_cred_limit.md`, `feedback_gemini_hallucinates_anchors.md`, `feedback_team_over_solo_for_book.md`, `project_ai_history_research_split_2026-04-28.md`, `reference_codex_models.md`, `reference_gemini_subscription_switch.md`, `feedback_advisory_vs_enforced_constraints.md`.

Memory worth recording (do this in the next session if the pivot sticks): a `feedback_codex_default_prose_expander.md` capturing why Codex (gpt-5.5) became the default expander 2026-04-29, what the strict-source rule is, and the load-bearing point that BOTH Codex AND Claude expansion paths obey the same rule.

## State at handoff — git tree

- Primary branch: `main` at `e75a5722` (pivot commit). Clean except 9 untracked files from prior sessions (none ours).
- Open PRs from this session: #475 (Ch36 research), #476 (Ch37 research), #477 (Ch01 prose), #479 (Ch02), #480 (Ch03), #481 (Ch04), #483 (Ch05).
- One Codex dispatch in flight (`b3pplb6bd`, Ch03 fix-applier).
