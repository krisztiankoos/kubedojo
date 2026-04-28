# Session handoff — 2026-04-28 — Part 2 prose pipeline + dispatcher hardening

Audience: the next session that picks up the AI History book (Epic #394).

This continues `2026-04-28-part1-prose-shipped-handoff.md`. Big results:

1. **Part 1 supersede research merged** (#456, #459, #460, #462, #463). Verified anchor-level research now on main alongside the already-merged Part 1 prose.
2. **Part 2 Ch06–Ch09 fully shipped** — prose + supersede research both on main. Ch10 prose dispatch fired and running in background at handoff.
3. **Dispatcher hardening** — three commits worth keeping in mind:
   - `7bca1e7a` / `ababdddd` — stage contract to disk + reference paths instead of inlining (drops prompt 10× from ~40k to ~5k chars; fixed Gemini per-window 429s).
   - `a12a3ef3` — stage inside the worktree (`.dispatch-context/`) instead of `/tmp/` so Gemini's workspace-write sandbox accepts the paths even on retry.
   - `e915534d` — `fire_phase` catches `RateLimitedError`/`AgentTimeoutError` and probes the worktree for a commit on `prose_path`; if the commit is there, treat the phase as success and continue. Recovers from Gemini's "tool work succeeded but final-summary 429ed" pattern.
4. **`scripts/dispatch_smart.py` shipped** — task-class headless-Claude wrapper. `search`→haiku, `edit`/`draft`→sonnet, `architect`→opus. JSONL audit log at `logs/smart_dispatch.jsonl`. Built specifically to stop the orchestrator burning opus on cheap work.
5. **`scripts/dispatch_chapter_research.py` generalized** — accepts `--agent {claude,codex}` so Codex can be a research target. Default still Claude.
6. **`src/content/docs/ai-history/index.md` refreshed** — lifecycle column corrected for everything that's actually on main (P1 → accepted, P5 Ch29-31 → accepted, Ch11-14 → prose_review, Ch15 → prose_ready, Ch50-52 → prose_ready), role split section reflects the 2026-04-28 evening policy.

## What this session shipped

### Part 1 supersede research closeout

Each of Ch01-05 had a verified-anchor supersede research PR open from prior sessions; all five had cleared both cross-family verdicts but never been merged (mergeable=UNKNOWN because the branches were ~85-106 commits behind main on unrelated files). The fix is a clean rebase that drops the "behind" baggage:

```bash
git -C .worktrees/claude-394-ch{NN}-research rebase origin/main
git -C .worktrees/claude-394-ch{NN}-research push --force-with-lease origin claude/394-ch{NN}-research
gh pr merge {PR#} --merge --repo kube-dojo/kube-dojo.github.io
```

Each commit is scoped to one chapter's 8 research files — no overlap with main's progress. PR #467 (Ch06) had its remote branch deleted at some point, so the local branch had to be re-pushed before merge.

| Ch | Research PR | Merge SHA |
|---|---|---|
| 01 | #456 | `d493372f` |
| 02 | #459 | `3faf8ad2` |
| 03 | #460 | `bb5c7099` |
| 04 | #462 | `2150b4de` |
| 05 | #463 | `0526d339` |

Same dance applies to remaining open research PRs (Ch10 #470 + the 6 Part 6 ones #471-#476 that landed earlier in the session series).

### Part 2 Ch06-09 prose pipeline

Each chapter ran the full `gemini → codex` pipeline against the verified research from `claude/394-ch{NN}-research`, then went through the dual cross-family review gate (`dispatch_prose_review.py --reviewer codex` + `--reviewer claude`), with all flagged strict-source nudges applied as inline orchestrator fixes before merge. Codex slot is sequential so reviews and prose dispatches are interleaved; Claude reviews can run in parallel with codex work.

| Ch | Prose PR | Review fixes (Codex / Claude) | Final words | Prose merge | Research merge |
|---|---|---|---:|---|---|
| 06 | [#496](https://github.com/kube-dojo/kube-dojo.github.io/pull/496) | 2 / 1 (drop "deliberate", reword Macy "demonstration", drop "acoustic") | 4180 | `a188efa4` | `db828dff` (#467) |
| 07 | [#497](https://github.com/kube-dojo/kube-dojo.github.io/pull/497) | 3 / 2 (motor speeds, hedge "brittle", drop meta-leak / drop "newly", "modes"→"mode") | 4473 | `242ccaac` | `93688ae5` (#466) |
| 08 | [#498](https://github.com/kube-dojo/kube-dojo.github.io/pull/498) | 5 / 3 (reattribute flag-bit to *First Draft*, hedge March 1946, "stored order code", "modern code paradigm", drop Ch9 boundary creep / trim Eckert quote, recast Bartik paraphrase) | 4036 | `ac5fa170` | `abee7eb4` (#468) |
| 09 | [#499](https://github.com/kube-dojo/kube-dojo.github.io/pull/499) | 4 / 1 (myriabit anchor, soften "deadlock broke", AN/FSQ-7 hedge, scope load-bearing / Valley as "associate professor") | 4079 | `a56a3d75` | `2c05a82b` (#469) |

Notable: Ch08 was the first chapter to exercise the `e915534d` resilience path. The dispatch log shows `[fire] gemini runner classified failure but commit ... is present — treating as success` followed by codex expansion succeeding on the same dispatch. Ch09 ran cleanly on first try.

### Dispatcher hardening — root causes and fixes

**`7bca1e7a` + `ababdddd` — staged-files instead of inlined contract.** The Gemini 429s on Ch06's first attempts traced to per-window input-token quota, not auth. The contract embedding was ~10-15k tokens. Staging the 8 files to disk and referencing paths drops the prompt to ~1-2k tokens; Gemini reads via its file-read tool which doesn't count against the streaming-input window.

**`a12a3ef3` — stage inside the worktree.** Ch07's first retry showed a second failure mode: Gemini's workspace-write sandbox rejects `/tmp/...` paths with "Path not in workspace" once a 429 forces an internal retry. Ch06 worked only because the first attempt happened to succeed. Move staging to `<worktree>/.dispatch-context/` and the sandbox accepts every path on every retry. Prompts now warn explicitly not to `git add .dispatch-context/`.

**`e915534d` — commit-presence recovery.** Ch07 hit a third pattern: Gemini reads contract, drafts prose, runs `git add` + `git commit` successfully, then 429s on its final streaming summary message. Stdout is empty, the runner classifies `rate_limited`, raises `RateLimitedError`, and `main()` crashes before the codex expansion phase can fire. The work is on disk; only the runner can't see it. `fire_phase` now catches `RateLimitedError`/`AgentTimeoutError`, probes `git log main..HEAD -- prose_path` in the worktree, and treats the phase as success if a commit landed. Confirmed working on Ch08, Ch09, Ch10.

### `scripts/dispatch_smart.py`

Single-CLI headless-Claude dispatcher with task-class model selection:

| `--task-class` | Model | Default mode | Default timeout | Use for |
|---|---|---|---|---|
| `search` | claude-haiku-4-5-20251001 | read-only | 600s | codebase scans, file lookups, factual Q&A |
| `edit` | claude-sonnet-4-6 | workspace-write | 1800s | small/medium code edits |
| `draft` | claude-sonnet-4-6 | workspace-write | 3600s | prose drafting / expansion |
| `architect` | claude-opus-4-7 | workspace-write | 3600s | deep reasoning, multi-file refactors |

Logs every call to `logs/smart_dispatch.jsonl`. Smoke-tested haiku echo round-trip in 10s. Reference memory: `reference_dispatch_smart.md`. Built so the orchestrator stops burning opus on cheap work.

### Role split (memory: `project_ai_history_research_split_2026-04-28.md`)

Final 2026-04-28 evening policy after one mid-session walk-back:

- **Claude** — research for Parts 1, 2, 3 ONLY. After Parts 1/2/3 close, Claude monitors but does not drive new research.
- **Codex** — research for Parts 4, 5, 6, 7, 8, 9 (he had 4/5/8; user added 6/7/9 to off-load Claude's weekly cap which had hit ~30 % in a day on the initial Ch32-37 push).
- **Gemini** — gap audit on every chapter; first-draft prose for Parts 1 and 2 (Codex expands).

`docs/research/ai-history/README.md` and `TEAM_WORKFLOW.md` may still show the older split — flag for whoever next touches research-docs.

## In flight at handoff

**`bwjlbwi3e`** — Ch10 prose pipeline (`gemini → codex` against `claude/394-ch10-research`, cap 5,000, verdict-notes PR #470). Worktree: `.worktrees/prose-394-ch10`. Background task; harness will notify on completion.

When it lands:

1. Push `prose/394-ch10`, open PR.
2. Fire dual review (`dispatch_prose_review.py {PR} --reviewer codex` + `--reviewer claude`).
3. Apply combined strict-source nudges as inline orchestrator fix-pass.
4. Merge prose PR.
5. Rebase + push + merge research PR #470 (last open Part 2 research PR).
6. Cleanup worktrees + branches.
7. Part 2 fully shipped — update `STATUS.md` and `index.md` to mark Ch10 accepted.

Other open #394 PRs at handoff:

- **Part 3 prose PRs awaiting cross-family review**: #451 (Ch11), #452 (Ch12), #454 (Ch13), #455 (Ch14). All Codex-drafted; need Claude source-fidelity + a prose-quality reviewer (Codex is conflicted as author — use Gemini for the prose-quality lane).
- **Part 3 research**: #457 (Ch15) — verdict cleared, prose pending. Ch16 stub still `status: researching`.
- **Part 6 research**: #471-#476 (Ch32-37) — open from earlier sessions; verdicts may need to be checked before the rebase+merge dance.

Codex is now driving Parts 6/7/8/9 research per the policy update. Don't push fresh contracts there from Claude.

## Cold-start function — the next session should run this

```bash
# 1. Where are we on AI History?
curl -s 'http://127.0.0.1:8768/api/briefing/session?compact=1' | head -50
source ~/.bash_secrets && gh pr list --search "is:open 394 in:title" --json number,title --limit 30

# 2. Is Ch10 prose pipeline still alive or did it land?
pgrep -fl "dispatch_chapter_prose.*10"
git -C .worktrees/prose-394-ch10 log --oneline main..HEAD
ls .worktrees/prose-394-ch10/.dispatch-context/ 2>/dev/null

# 3. Verify the Part 2 closure on main
git log --oneline -20 origin/main | grep -E "ch-(06|07|08|09|10)"
ls src/content/docs/ai-history/ch-{06,07,08,09,10}-*.md

# 4. Smoke-check dispatchers still work
.venv/bin/python scripts/dispatch_chapter_prose.py --help | head -5
.venv/bin/python scripts/dispatch_smart.py search "Reply with literal OK" 2>&1 | tail -5

# 5. Codex auth probe
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

### Priority 1 — finish Ch10 (Part 2 closeout)

When Ch10 prose dispatch completes (notification): push branch, open PR, dual review, fix-pass, merge prose, rebase+merge research #470, cleanup. ~30-45 min wall after dispatch lands.

### Priority 2 — Part 3 review backlog

The 4 codex-drafted prose PRs (#451-#455) need cross-family review. They predate the staged-files refactor, so the prose itself is fine — only the review dispatch matters. Review pattern:

```bash
.venv/bin/python scripts/dispatch_prose_review.py 451 --reviewer claude    # source-fidelity
.venv/bin/python scripts/dispatch_prose_review.py 451 --reviewer gemini    # prose-quality (codex is the author here, so gemini takes the prose-quality lane)
```

Per `docs/review-protocol.md`, codex-authored work cannot be reviewed by codex. Use Gemini for the prose-quality lane.

### Priority 3 — Ch15 prose + Ch16 research

- **Ch15 prose**: research verdict on PR #457 cleared (last session). Read the cap from the brief's Prose Capacity Plan total then `dispatch_chapter_prose.py 15 --slug ch-15-the-gradient-descent-concept --research-branch claude/394-ch15-research --cap-words {N} --verdict-notes-pr 457`.
- **Ch16 research**: Claude-owned (Part 3 = Claude). `dispatch_chapter_research.py 16 --slug ch-16-the-cold-war-blank-check`. Honest cap if anchored evidence runs out.

### Priority 4 — Codex's progress on Parts 4-9

Per the role split, Codex now drives 4/5/6/7/8/9 research. He's already done with Parts 4 and 5 (15 chapters all `accepted` on main, verified earlier this session). Part 8: Ch50-52 `prose_ready`, Ch53-58 `researching`. Parts 6/7/9: not yet driven by Codex.

When checking what to do next here, **don't dispatch fresh research from Claude** — Codex is the lead. Claude only monitors.

### Priority 5 — close the Part 6 research PRs (Ch32-37 #471-#476)

These were Claude's pre-policy-flip research contracts. They need verdict checks (probably already cleared from prior sessions) and the same rebase+merge dance as Part 1.

### Priority 6 — `dispatch_chapter_prose.py` is now scaffolding

Per `feedback_no_staging_scaffolding.md`: when Epic #394 ships, `dispatch_chapter_prose.py`, `dispatch_chapter_research.py`, `dispatch_research_verdict.py`, `dispatch_prose_review.py` are all reapable. The reusable bits (`stage_contract_locally`, `_prose_committed_on_branch` recovery pattern) could be lifted into `agent_runtime/` as a generic `delegate-with-contract` helper. Not urgent.

## Reusable patterns confirmed this session

### Stage contract files to `<worktree>/.dispatch-context/` for any agent

Save input bytes by writing once to disk and pointing the agent at paths. Inside the worktree (not `/tmp/`) so workspace-write sandboxes accept the paths on retry. Agent prompts must explicitly forbid `git add .dispatch-context/`. Validated on gemini, codex, claude.

### Commit-presence recovery from runner false-failures

`fire_phase` catching `RateLimitedError`/`AgentTimeoutError` and probing `git log main..HEAD -- prose_path` is the right shape. The agent's tool work happens out-of-band from its streaming response; if the commit is there, the work is done regardless of how the runner classified the call. Same probe shape can rescue any "tool work succeeded but final response failed" failure mode.

### Rebase-and-merge for stale supersede research PRs

Branches that are 1 commit ahead of main and 80-100+ commits behind on unrelated files merge cleanly via `git rebase origin/main` (drops the behind baggage), `git push --force-with-lease`, `gh pr merge --merge`. Confirmed on 9 PRs this session (5 Part 1 + 4 Part 2). Each commit is scoped to one chapter's 8 research files; no collateral on main.

### Cross-family review on orchestrator inline edits

The fix-pass after a dual review is an orchestrator inline edit, not a dispatched-agent edit. Per the prior handoff's lesson, those need the same cross-family safety net as agent edits. This session relied on the previous-session lesson and didn't introduce new strict-source violations in the fix passes — but the review log on each PR is the audit trail (every fix is keyed to a specific reviewer comment).

## State at handoff — git tree

- Primary branch: `main` at `2c05a82b` (Ch09 research merge). Pushed; clean working tree.
- Worktrees: 27 (was 31 at session start). Reaped: prose-394-ch06, prose-394-ch07, prose-394-ch08, prose-394-ch09 + their corresponding `claude-394-ch{NN}-research` worktrees. `prose-394-ch10` and `claude-394-ch10-research` still present (in-flight).
- Open PRs from this session: 0 from this session merged + still open. 1 will open shortly when Ch10 prose dispatch lands.

## Memories used / created this session

Used:
- `feedback_dispatch_to_headless_claude.md`
- `reference_agent_runtime_dispatch_pattern.md`
- `feedback_codex_dispatch_sequential.md`
- `feedback_codex_default_prose_expander.md`
- `reference_codex_models.md`
- `feedback_advisory_vs_enforced_constraints.md`
- `feedback_execute_without_nagging.md`
- `feedback_review_policy.md`
- `feedback_no_staging_scaffolding.md`
- `feedback_no_yes_man.md`
- `reference_gemini_subscription_switch.md`
- `feedback_test_before_run.md`

Created/updated:
- `reference_dispatch_smart.md` — task-class headless wrapper docs
- `project_ai_history_research_split_2026-04-28.md` — updated twice (initial flip, walk-back, then final policy)

Worth recording in the next session if patterns stick:
- `feedback_stage_contract_inside_worktree.md` — Gemini sandbox rejects `/tmp/...` on retry; always stage inside the workspace.
- `feedback_runner_false_failure_recovery.md` — when tool work commits but the runner classifies failure, probe the worktree before propagating.
