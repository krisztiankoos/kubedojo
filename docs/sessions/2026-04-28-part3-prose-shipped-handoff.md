# Session handoff — 2026-04-28 (PM) — Part 2 closeout + Part 3 prose shipped

Audience: the next session that picks up the AI History book (Epic #394).

This continues `2026-04-28-part2-prose-pipeline-handoff.md`. Big results this run:

1. **Part 2 fully shipped** — Ch10 prose merged (PR #500) and the Ch10 supersede research PR #470 rebased + merged. Ch6–Ch10 prose + research all on `main`.
2. **Part 3 prose backlog cleared** — Ch11–Ch14 (PRs #451, #452, #454, #455) all dual-reviewed, fix-passed inline, and merged. Part 3 is now 4/6 shipped (Ch15 prose pending; Ch16 still researching).
3. **Dispatcher fix on main** — `scripts/dispatch_prose_review.py` now falls back to `main` as the research-source ref when no `claude/394-chNN-research` or `codex/394-chNN-research` branch exists. The Part 3 batch was ValueError-ing because their research already lives on main rather than on a dedicated branch (commit `4f6300b3`).
4. **Roll-up + index refreshed** — Ch6–14 now show `accepted`. Ch53–55 confirmed `prose_ready` per Codex (verified against `status.yaml` on main). Roll-up table updated to 29 accepted / 7 prose_ready / 11 legacy-prose-on-researching / 21 researching-no-prose.
5. **Tree pruned** — 6 merged worktrees + branches removed (claude-394-ch10-research, codex-394-ch11/12/13/14-prose, prose-394-ch10).

## Chapter scoreboard (after this session)

Across the 68-chapter book:

| Status | Count | Chapters |
|---|---:|---|
| **accepted** (merged) | **29** | Part 1 (Ch1–5), Part 2 (Ch6–10), Part 3 (Ch11–14), Part 4 (Ch17–23), Part 5 (Ch24–31) |
| **prose_ready** (verdict cleared, no draft yet) | **7** | Ch15, Ch50, Ch51, Ch52, Ch53, Ch54, Ch55 |
| **researching, legacy prose merged** (rewrite due) | **11** | Part 6 Ch32–40, Part 7 Ch41 + Ch43 |
| **researching, no prose** | **21** | Ch16, Part 7 Ch42 / Ch44–49, Part 8 Ch56–58, Part 9 Ch59–68 |

Per-Part:
- **Parts 1, 2, 4, 5** — fully shipped.
- **Part 3** — 4/6 shipped (Ch15 prose pending; Ch16 still researching).
- **Part 6** — 0/9 verified; legacy prose merged for all 9; supersede research PRs #471–#476 open on Ch32–37.
- **Part 7** — 0/9; Ch41 + Ch43 have legacy prose, the rest are still researching with no draft.
- **Part 8** — 0/9; Ch50–55 prose_ready, Ch56 next-up for research, Ch57/58 pending.
- **Part 9** — 0/10; all researching, no prose anywhere.

## What this session shipped

### Part 2 closeout (Ch10)

Picked up the in-flight `gemini → codex` pipeline from the prior handoff. Both phase commits (`993d276e` gemini draft, `bb0562c3` codex expansion) had landed in `.worktrees/prose-394-ch10/` by session start.

- Pushed branch, opened PR #500 (4,388 words, well under the 5,000 cap).
- Dual review: Claude `NEEDS_FIX_AND_MERGE` (§6.4 solipsism paraphrase + §6.5 disabilities list reproduced Yellow sub-page material; "fair play" 1947 phrase imported into §6.4). Gemini `READY_TO_MERGE`.
- Inline orchestrator fix-pass: rewrote Turing's §6.4 reply structurally without verbatim sub-page text; trimmed disabilities list to abstract category names ("kindness, originality, error-making, sensory pleasure, emotional response, language use"); dropped the "fair play" phrase from the §6.4 paragraph. Commit `4d06b8e7`. Word count 4,384 after fix.
- Merged PR #500. Rebased `claude/394-ch10-research` onto post-prose main, force-pushed, merged PR #470. **Part 2 fully shipped.**

### Part 3 prose backlog (Ch11–Ch14)

The 4 codex-drafted prose PRs had cleared CI but had no review comments at session start. Approach: fire all 4 Claude reviews in parallel (background), Gemini reviews sequentially in a chained background bash. Per-PR fix-pass, then merge.

| Ch | PR | Final words | Claude verdict | Gemini verdict | Fix commit | Merge SHA |
|---|---|---:|---|---|---|---|
| 11 | [#451](https://github.com/kube-dojo/kube-dojo.github.io/pull/451) | 4,911 | NEEDS_FIX_AND_MERGE (JOHNNIAC unhedged) | READY_TO_MERGE | `60877c86` | `8133d77c` |
| 12 | [#452](https://github.com/kube-dojo/kube-dojo.github.io/pull/452) | 4,641 | READY_TO_MERGE (joined-by-correspondence soft) | NEEDS_FIX_AND_MERGE (4 meta leaks + heading) | `32add95f` | `f626a832` |
| 13 | [#454](https://github.com/kube-dojo/kube-dojo.github.io/pull/454) | 4,827 | NEEDS_FIX_AND_MERGE (~50w + meta optional) | NEEDS_FIX_AND_MERGE (5 meta leaks + irony repetition) | `fc8003e2` | `2d418c7e` |
| 14 | [#455](https://github.com/kube-dojo/kube-dojo.github.io/pull/455) | 4,695 | READY_TO_MERGE | NEEDS_FIX_AND_MERGE (3 fourth-wall meta) | `649d615a` | `5f55b3e2` |

Notable: Ch13 hit a transient `RateLimitedError: ... File not found` on the gemini chain (post-tool 429 plus a stale internal path probe). Re-fired alone 2 min later and it succeeded — same shape as `feedback_runner_false_failure_recovery.md`.

### Dispatcher fix — `dispatch_prose_review.py` `main` fallback

The Part 3 batch crashed on first attempt with `ValueError: no research branch found for ch-NN-...`. Root cause: the script tried `claude/394-chNN-research` then `codex/394-chNN-research`, but Ch11-14 research had already merged to main with no dedicated branch.

Patch: probe for `docs/research/ai-history/chapters/<slug>/brief.md` on `origin/main`; if present, return `"main"` as the research_branch. `gather_contract` and `read_branch_file` both work unchanged with `main` as the ref. Commit `4f6300b3`, pushed to main same session.

### Codex prose-expander meta-diction leak — pattern confirmed

A consistent pattern emerged across Ch12, Ch13, Ch14: **both** reviewers independently flagged the same kind of leak — Codex's expander had imported the contract's production-process vocabulary directly into reader-facing prose. Words to watch for: `"the contract"`, `"Yellow"`, `"unsafe"`, `"anchor"`, `"paginated source"`, `"deliberately cautious"`, `"primary-page extraction"`, `"safe claim is enough"`.

Fix shape (one-line edit per leak):
- `"the current chapter contract has it anchored to..."` → `"the strongest available source is..."`
- `"the contract keeps that anecdote Yellow because..."` → `"that anecdote rests on... rather than..."`
- `"the broader priority claim is unsafe"` → `"does not survive scrutiny"`
- `"## Honest Attribution Close"` (scene-sketch artifact heading) → `"## Defining the Achievement"`

Saved as memory `feedback_codex_prose_meta_diction_leak.md`. Worth adding an explicit forbid-list to `dispatch_chapter_prose.py:codex_prompt` next session — would prevent the leak entirely instead of catching it in fix-pass.

### Bash-tool background-timeout gotcha

`run_in_background: true` with `timeout: 600000` (10 min cap, harness max) is still enforced. Fired the 5× sequential Gemini chain (~15 min total) and the bash was killed mid-#454. Re-fired remaining steps as separate background tasks. Saved as memory `feedback_bash_background_timeout.md`. For long sequential chains, fan out to separate background calls.

## In flight at handoff

Nothing in flight. Tree clean, main clean, no background processes running.

## Open #394 PRs

| # | Branch | What it is | Ready? |
|---|---|---|---|
| 457 | `claude/394-ch15-research` | Ch15 verified-anchor research; verdicts cleared a few sessions ago | rebase + merge dance, prose dispatch after |
| 471 | `claude/394-ch32-research` | Part 6 supersede research, pre-policy-flip Claude work | verify verdict, rebase + merge |
| 472 | `claude/394-ch33-research` | Same | Same |
| 473 | `claude/394-ch34-research` | Same | Same |
| 474 | `claude/394-ch35-research` | Same | Same |
| 475 | `claude/394-ch37-research` | Same | Same |
| 476 | `claude/394-ch36-research` | Same | Same |

## Cold-start function — the next session should run this

```bash
# 1. Where are we on AI History?
curl -s 'http://127.0.0.1:8768/api/briefing/session?compact=1' | head -50
source ~/.bash_secrets && gh pr list --search "is:open 394 in:title" --json number,title --limit 30

# 2. Recent main activity
git log --oneline -15 origin/main

# 3. Lifecycle reality on the chapters this session touched
grep -E "^\| (10|11|12|13|14) " src/content/docs/ai-history/index.md
ls src/content/docs/ai-history/ch-1[0-4]-*.md

# 4. Verify Part 8 prose_ready chapters Codex flagged are still aligned
for ch in 53 54 55; do
  echo "=== Ch$ch ===";
  cat docs/research/ai-history/chapters/ch-$ch-*/status.yaml | head -7;
done

# 5. Codex auth probe (for any prose dispatch that may follow)
.venv/bin/python - <<'EOF'
import sys; sys.path.insert(0, "scripts")
from agent_runtime.runner import invoke
r = invoke("codex", "Reply with literal OK and nothing else.",
           mode="read-only", model="gpt-5.5",
           task_id="cap-probe-codex-cold-start", entrypoint="consult",
           hard_timeout=120)
print("codex:", r.ok, repr((r.response or "")[:40]))
EOF
```

## Pending action items at handoff (priority order)

### Priority 1 — Ch15 prose (Part 3 closeout)

PR #457 has the verdicts cleared. Pull the cap from the brief's Prose Capacity Plan, then:

```bash
.venv/bin/python scripts/dispatch_chapter_prose.py 15 \
    --slug ch-15-the-gradient-descent-concept \
    --research-branch claude/394-ch15-research \
    --cap-words <N> \
    --verdict-notes-pr 457
```

Then dual review (`dispatch_prose_review.py 15 --reviewer claude` + `--reviewer gemini`), inline fix-pass, merge prose, then rebase + merge research PR #457. ~80–100 min wall.

### Priority 2 — Ch16 research (Part 3 final)

`status: researching` stub. Claude is still on Parts 1/2/3 per the policy split.

```bash
.venv/bin/python scripts/dispatch_chapter_research.py 16 \
    --slug ch-16-the-cold-war-blank-check
```

When the contract lands, dual-review and bring it to `prose_ready`. After that Part 3 is complete.

### Priority 3 — Close Part 6 supersede research PRs (#471–#476)

These are pre-policy-flip Claude research contracts for Ch32–37. Verdicts may already be on file (check via `gh pr view <N> --json comments`); if cleared, run the same rebase + merge dance that worked on Part 1 and #470:

```bash
git fetch origin main
git -C .worktrees/claude-394-ch{NN}-research rebase origin/main
git -C .worktrees/claude-394-ch{NN}-research push --force-with-lease origin claude/394-ch{NN}-research
gh pr merge {PR#} --merge --repo kube-dojo/kube-dojo.github.io
```

Each commit is scoped to one chapter's 8 research files; no overlap with other chapters' progress. After landing, those Ch32–37 chapters will have verified-anchor research on main and the legacy prose can be re-drafted from the proper contract.

### Priority 4 — Update `dispatch_chapter_prose.py:codex_prompt` to forbid contract-vocabulary

Per `feedback_codex_prose_meta_diction_leak.md`. Add an explicit forbid-list to the codex_prompt: do not use the words `contract`, `Yellow`, `Red`, `unsafe`, `anchor`, `paginated`, or `extraction` in reader-facing prose; convert hedges to natural narrative form. Would have prevented all the meta-narrative fixes this session needed for Ch12/13/14. Small change, high prevention payoff.

### Priority 5 — Codex's own queue (Parts 6/7/8/9 research + drafting)

Per the role split, Codex drives 4/5/6/7/8/9 research and prose. He's done with Parts 4/5 prose, has Ch50–55 at prose_ready in Part 8, and Ch56 is next on his research queue. Part 6 has legacy prose plus open supersede research PRs. Part 7 / Part 9 are mostly still researching.

When checking what to do next here, **don't dispatch fresh research from Claude** for Parts 4–9 — Codex is the lead. Claude only monitors, supports prose review, and does the orchestrator-side merge dance.

### Priority 6 — `dispatch_chapter_*.py` are now scaffolding

Same observation as the prior handoff (`feedback_no_staging_scaffolding.md`). When Epic #394 ships, `dispatch_chapter_prose.py`, `dispatch_chapter_research.py`, `dispatch_research_verdict.py`, `dispatch_prose_review.py` are reapable. The reusable bits (`stage_contract_locally`, the `main` fallback added this session, the `_prose_committed_on_branch` recovery pattern from prior session) could be lifted into `agent_runtime/` as a generic `delegate-with-contract` helper. Not urgent; flag for after the book lands.

## Reusable patterns confirmed this session

### `main` fallback in dispatch_prose_review.py

When the prose was drafted before the supersede-research workflow existed (Ch11–14 fall in this gap), the research is on `main` and there is no dedicated branch. `gather_contract` doesn't care about the ref name — it just calls `git show <ref>:<path>` — so passing `"main"` works unchanged.

### Parallel Claude reviews + sequential Gemini reviews

`dispatch_prose_review.py --reviewer claude` is safe to fan out in parallel because each invocation spawns its own headless session with a unique `task_id`. Gemini and Codex must stay sequential per the existing memories. So the pattern for any N-PR review batch:

- Fan out N Claude reviews concurrently as separate background tasks.
- Chain Gemini reviews in a single sequential bash, OR fire as separate background tasks one at a time. Either works — but watch the 10-min bash-timeout cap (see `feedback_bash_background_timeout.md`).
- For Codex-drafted prose, Codex itself is conflicted as reviewer, so use Gemini for the prose-quality lane.

### Dispatcher word-count is authoritative

Reviewers (especially Claude) sometimes guess word counts by eye and overshoot 20–30%. The dispatcher's `[read] prose: NN words` print is `len(prose.split())` — trust it over reviewer estimates before deciding to trim. On Ch11 the Claude review said "rough count ~6,400 words" but actual was 4,898 — 30% overestimate, no trim needed.

### Cross-family review on orchestrator inline edits

The fix-pass after a dual review is an orchestrator inline edit, not a dispatched-agent edit. Per the prior session's lesson, those need the same cross-family safety net as agent edits — which means small surgical edits keyed to specific reviewer comments, not freeform rewrites. This session every fix-pass commit has a 1:1 mapping from reviewer comment → file edit, captured in the commit message body.

## State at handoff — git tree

- **Primary branch**: `main` at `f302ab5f` (`docs(ai-history): refresh roll-up + Ch53-55 prose_ready (#394)`). Pushed; clean working tree.
- **Worktrees**: 22 (was 27 at session start, 21 after worktree-prune of merged ch10-research + codex-394-ch11/12/13/14-prose + prose-394-ch10; +1 from a Codex-side worktree that appeared during the session).
- **Local branches**: 35 (deleted 6 merged ones).
- **Open PRs from this session**: 0. All 6 prose PRs (Ch10/11/12/13/14 — and Ch10 research) merged in-session.
- **Build**: `npm run build` clean (1891 pages, 35s).

## Memories used / created this session

Used:
- `feedback_dispatch_to_headless_claude.md`
- `reference_agent_runtime_dispatch_pattern.md`
- `feedback_codex_dispatch_sequential.md`
- `feedback_codex_default_prose_expander.md`
- `feedback_review_policy.md`
- `feedback_no_staging_scaffolding.md`
- `feedback_test_before_run.md`
- `feedback_runner_false_failure_recovery.md` (Ch13 gemini 429 pattern)

Created this session:
- `feedback_codex_prose_meta_diction_leak.md` — Codex prose expander leaks contract diction into reader-facing prose. Strip in prompt or fix-pass.
- `feedback_bash_background_timeout.md` — Bash `run_in_background: true` still enforces the per-call timeout (max 600000 ms). Long sequential chains get killed mid-loop. Fan out as separate background tasks.

Worth recording in the next session if the pattern persists:
- A potential `feedback_dispatch_review_main_fallback.md` if the `main`-fallback need recurs on other dispatchers (research_verdict, etc.). For now, the one-liner in `dispatch_prose_review.py` documents itself.
