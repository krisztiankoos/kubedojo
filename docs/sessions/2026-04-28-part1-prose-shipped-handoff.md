# Session handoff — 2026-04-28 — Part 1 prose merged + dispatch_prose_review shipped

Audience: the next session that picks up the AI History book (Epic #394).

This continues `2026-04-29-part1-prose-and-pipeline-pivot-handoff.md`. Big results:

1. **Part 1 (Ch01-05) prose merged to main** — all 5 PRs (#477, #479, #480, #481, #483) shipped under the dual-review pipeline.
2. **`scripts/dispatch_prose_review.py` shipped** — generalized cross-family prose-review dispatcher (Claude source-fidelity / Codex prose-quality / Gemini, mirrors `dispatch_research_verdict.py`).
3. **Strict-source rule reinforced**: Ch04 review caught the orchestrator-Claude's "45-year-old Markov" inline fix as a contract-violation even though it was arithmetically correct (the contract literally says 49). Resolution: strike the age.
4. **Build clean** at `0e57fa25` (1881 pages, 41.79s).
5. **#429 closed** as superseded.
6. **Git hygiene**: primary tree pinned to `main` (was parked on stale `pr-484`); 27 merged worktrees + 29 prunable branches reaped; orphan `pr-484` + detached `codex-interactive` worktree removed.

Nothing destructive landed.

## What this session shipped

### Part 1 prose pipeline closeout

Each of Ch01-05 got the two-review treatment and surgical fix-pass:

| Ch | PR | Codex review | Claude review | Final words | Merge SHA |
|---|---|---|---|---:|---|
| 01 | [#477](https://github.com/kube-dojo/kube-dojo.github.io/pull/477) | 4 fixes applied prior session | 4 source-fidelity fixes applied | 3766 | `47b4b176` |
| 02 | [#479](https://github.com/kube-dojo/kube-dojo.github.io/pull/479) | 3 deferred fixes applied | (n/a — Codex-only path) | 3991 | `3115cc98` |
| 03 | [#480](https://github.com/kube-dojo/kube-dojo.github.io/pull/480) | 5 fixes applied prior session | 4 source-fidelity fixes applied | 3150 | `8d79a948` |
| 04 | [#481](https://github.com/kube-dojo/kube-dojo.github.io/pull/481) | 5 fixes applied + posted to PR | 3 source-fidelity fixes applied | 3172 | `d7c516cf` |
| 05 | [#483](https://github.com/kube-dojo/kube-dojo.github.io/pull/483) | 8 fixes applied | 4 source-fidelity fixes applied | 3911 | `058a9d01` |

Notable mid-pipeline events:

- **Ch04 source-fidelity tension**: Codex review caught "forty-nine-year-old Markov" as arithmetically wrong (Markov b.1856 → 45/46 in 1902). Orchestrator-Claude inline-fixed to "forty-five-year-old". Independent Claude source-fidelity review then flagged "45" as a strict-source violation — the contract literally says 49. Resolution per the strict-source rule: **strike the age entirely**. The reviewer-vs-historicity tension is a feature of the dual-pass pipeline, not a bug.
- **Ch05 meta-leak from orchestrator's Codex-fix pass**: orchestrator-Claude's prior fix introduced "the contract leaves open" / "the contract leaves to a later chapter" — research-apparatus vocabulary that must not surface in finished prose. Independent Claude review caught both. Replaced with "is beyond this chapter's scope" / "a thread later chapters will pick up".
- **Lesson**: orchestrator-Claude's inline-edit fixes MUST go through the same cross-family review gate as dispatched-agent edits. Self-applied Codex-flagged fixes can introduce their own strict-source violations.

### `scripts/dispatch_prose_review.py`

Generalized cross-family prose-review dispatcher. Reads prose from the prose branch + the approved research contract from the chapter's research branch, fires headless Claude / Codex / Gemini with the appropriate review prompt, posts the result as a PR comment.

```bash
.venv/bin/python scripts/dispatch_prose_review.py 480 --reviewer claude  # source-fidelity
.venv/bin/python scripts/dispatch_prose_review.py 483 --reviewer codex   # prose-quality
```

Defaults:

- `--reviewer claude` → `mode="read-only"` on `claude-opus-4-7`, ~10-12 min, posts source-fidelity review with `<!-- prose review claude -->` header
- `--reviewer codex` → `mode="read-only"` on `gpt-5.5` (reasoning=high pinned in `~/.codex/config.toml`), ~5-10 min, posts prose-quality review with `<!-- prose review codex -->` header
- `--reviewer gemini` → reuses Codex's prose-quality prompt format with Gemini lane discipline (no URL hallucinations per Issue #421)

Smoke-verified end-to-end on Ch03, Ch04, Ch05 (3 successful headless dispatches this session). Anchored at commit `571e75be`.

### Git hygiene

Resolved the stale-state mess at session start:

- **Primary tree** was parked on local-only `pr-484` (3 unique commits, all duplicate-content of already-merged PRs). Switched primary back to `main`, deleted `pr-484`.
- **Local main was 5 ahead / 2 behind origin/main** at session start. Rebased + pushed (`277214fe..77c13441`).
- **`codex-interactive` worktree** in detached-HEAD state — removed (its commit was already on main and several research branches).
- **27 merged-and-upstream-gone worktrees** + **29 corresponding branches** removed via the API's `/api/git/cleanup` list with a per-branch upstream-gone check.
- **5 Part 1 prose worktrees + branches** removed after merge.

End state: 29 worktrees, 47 local branches (was ~60+ / ~76+ at session start).

## In flight at handoff

Nothing currently dispatched. No background tasks. Bridge clean.

## Cold-start function — the next session should run this

```bash
# 1. Where are we on AI History?
curl -s 'http://127.0.0.1:8768/api/briefing/session?compact=1' | head -50
source ~/.bash_secrets && gh pr list --search "is:open 394 in:title" --json number,title --limit 30

# 2. Verify Part 1 actually merged + chapters present on main
git log --oneline -15 | grep -i 'prose/394-ch'
ls src/content/docs/ai-history/ch-{01,02,03,04,05}-*.md

# 3. Verify the prose review dispatcher is on main
ls scripts/dispatch_prose_review.py

# 4. Is gpt-5.5 still healthy?
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

### Priority 1 — Part 2 prose pipeline (Ch06-10)

All 5 verdicts already cleared `READY_TO_DRAFT_WITH_CAP` from the prior session. Fire `dispatch_chapter_prose.py` with the new Codex-default pipeline (default `--phases gemini,codex` — no flag needed).

Per-chapter caps come from the Codex/Gemini verdict comments on each PR — read via `gh pr view <pr> --json comments`. The verdict PRs are #467 (Ch06), #466 (Ch07), #468 (Ch08), #469 (Ch09), #470 (Ch10).

```bash
.venv/bin/python scripts/dispatch_chapter_prose.py 6 \
    --slug ch-06-the-cybernetics-movement \
    --research-branch claude/394-ch06-research \
    --cap-words <from verdict> \
    --verdict-notes-pr 467
```

Then dispatch the two-review gate:

```bash
.venv/bin/python scripts/dispatch_prose_review.py <pr_num> --reviewer codex
.venv/bin/python scripts/dispatch_prose_review.py <pr_num> --reviewer claude
```

Apply fixes inline (orchestrator) or via dispatched Codex (`feedback_codex_default_prose_expander.md` recipe), push, **rebase to drop the 2 dispatcher infra commits if they're still in the prose branch** (see Reusable patterns), merge.

Wall: ~80-100 min/chapter end-to-end. ~7-8 hours for all 5 sequential.

### Priority 2 — Part 3 prose work (Ch11-14 reviews; Ch15 draft; Ch16 research)

- **Ch11-14 prose PRs (#451, #452, #454, #455)** are Codex-drafted and still need cross-family review (Claude or Gemini, not Codex). Fire `dispatch_prose_review.py --reviewer claude` then a prose-quality review.
- **Ch15 research** verdict cleared (PR #457). Fire `dispatch_chapter_prose.py 15 --slug ch-15-the-gradient-descent-concept --research-branch claude/394-ch15-research --cap-words <from-verdict> --verdict-notes-pr 457`.
- **Ch16 research** is still `status: researching` (stub on main). Claude is research lead for Part 3; build the contract via `dispatch_chapter_research.py 16 --slug ch-16-the-cold-war-blank-check`.

### Priority 3 — resume Part 6/7 research queue (after Parts 2-3 ship)

14 chapters still need Claude-owned research contracts: Ch38, 39, 40 (Part 6 remainder), Ch41–49 (Part 7). Pattern is `dispatch_chapter_research.py N --slug ch-NN-...`. The prior `2026-04-28-claude-research-queue-cap-handoff.md` has the full slug list.

### Priority 4 — close superseded research PRs as their replacements merge

Replacement PRs #456, #467, #468, #459, #460, #462, #463, #470, #469, #466 are still open. The corresponding superseded PRs (#425, #426, #427, #431, #433, #435, #436, #437, #438, #439) are mostly already CLOSED. The lone OPEN supersede was #429 (Ch01 prose), now closed this session.

## Reusable patterns confirmed this session

### Cross-family review applies to orchestrator inline edits, not just dispatched-agent edits

Two cases this session:
1. Ch04: orchestrator changed "49-year-old" → "45-year-old" per Codex catch; Claude review then flagged "45" as a strict-source violation. Resolution: strike the age.
2. Ch05: orchestrator's prior Codex-fix pass introduced "the contract leaves open" — research-vocabulary leak. Claude review caught it.

If the orchestrator applies fixes inline (faster than dispatching headless Codex/Claude for surgical edits), the result still needs a cross-family review pass before merge. The post-fix Claude source-fidelity review is the safety net.

### Rebase-and-drop for stale infrastructure commits in PR branches

The 5 prose branches each carried 2 dispatcher commits (`e964b3c9` cross-family verdict-pass dispatcher, `2c0644b7` Gemini→Claude prose pipeline dispatcher) that had landed on main as different SHAs through the pivot. Direct merge conflicts on `scripts/dispatch_chapter_prose.py` and `scripts/dispatch_research_verdict.py` because main rewrote those files post-pivot.

Fix: `git rebase --onto origin/main 2c0644b7 prose/394-chNN` cleanly drops the 2 infra commits and replays only the chapter prose commits. Force-push, then merge.

If Ch06+ branches inherit the same 2-commit infra base, reuse this pattern.

### `git pr-done` alias has a worktree-cwd bug

When invoked from inside a worktree subdirectory, `git -C ""` in the alias body resolves to the current worktree's HEAD, not the arg's worktree. Symptom: every prune attempt errors with `cannot delete branch '<current-worktree-branch>'`. Don't use the alias from a worktree; either inline the logic or `cd` to the kubedojo root first.

The alias still removes the worktree successfully (the `git worktree remove --force "$wt"` inside the alias DOES get the right `$wt`); only the branch-deletion side misfires. So a botched run leaves orphan branches but cleans up worktrees. Recover via:

```bash
curl -s http://127.0.0.1:8768/api/git/cleanup \
    | jq -r '.prunable_branches[].name' \
    | xargs -I{} git branch -D {}
```

## Memories used / created this session

Used: `feedback_dispatch_to_headless_claude.md`, `reference_agent_runtime_dispatch_pattern.md`, `feedback_codex_dispatch_sequential.md`, `feedback_codex_default_prose_expander.md`, `reference_codex_models.md`, `feedback_advisory_vs_enforced_constraints.md`, `feedback_no_detached_head.md`, `feedback_execute_without_nagging.md`, `feedback_review_policy.md`, `feedback_no_staging_scaffolding.md`.

Memory worth recording (do this in the next session if the patterns stick):

- `feedback_orchestrator_inline_fixes_need_review.md` — capturing the Ch04 "45 vs 49" tension and the Ch05 "the contract leaves open" leak. Orchestrator-Claude's inline fixes need the same cross-family review gate as dispatched-agent fixes.
- `reference_dispatch_prose_review.md` — capturing the new dispatcher's interface and the two review lanes (Claude source-fidelity / Codex prose-quality).
- `feedback_git_pr_done_worktree_bug.md` — capturing the alias's cwd misbehavior and the recovery recipe.

## State at handoff — git tree

- Primary branch: `main` at `0e57fa25` (changelog + STATUS.md). Pushed; clean working tree.
- Worktrees: 29 (was ~60 at session start; pruned 27 merged + 5 Part 1 prose + `codex-interactive`).
- Local branches: 47 (was ~76; pruned 29 prunable + 5 Part 1 prose + `pr-484`).
- Open PRs from this session: none — all 5 Part 1 prose PRs merged.
