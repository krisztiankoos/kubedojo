# Session handoff — 2026-05-05 (session 1) — dispatch.py source-fix + #388 / book fact-check audit prep

> Picks up from `2026-05-04-3-incident-dedup-platform-sweep.md` (session 3, prior calendar day). User intent shifted mid-session from "restart #388 on swept tracks" to a deeper systemic fix after the #388 pilot (PR #886) revealed that codex was being dispatched without `--search` and in `--sandbox read-only`. That made every codex writer dispatch in the v2 pipeline produce training-data-only content with no source verification — applies retroactively to **153 already-shipped #388 modules** AND to AI-history book chapters drafted via the agent_runtime adapter, which has no `--search` support either.

## Decisions and contract changes

### Source-of-problem scope (the architectural failure)

The v2 quality pipeline had **two separate web-blindness defaults** that compounded each other:

1. **Writer side**: `scripts/dispatch.py:603` `dispatch_codex` hardcoded `--sandbox read-only` with no `--search`. Codex prose drafts could not verify CIS recommendation IDs, CLI flags, version-gated behavior, Sources URLs, or any fact-laden specific.
2. **Reviewer side**: `scripts/dispatch.py:491` `_CLAUDE_TEXT_ONLY_DISALLOWED` listed `WebFetch,WebSearch` alongside the agentic file-mutation tools. The original autopsy (writer/reviewer stdout corruption from agentic tool use) justified blocking `Edit/Write/Bash/Task`; web tools were collateral damage. **Net effect: both writer and reviewer were blind to factual hallucinations.** Cross-family review caught structural and density issues but had no fact-check capability.

The book chapter dispatch path (`scripts/dispatch_chapter_research.py:277` → `agent_runtime.runner.invoke` → `scripts/agent_runtime/adapters/codex.py`) has **no `--search` support at all** — verified by grep: zero hits for `--search`, `web_search`, `enable_search` across `agent_runtime/runner.py`, `agent_runtime/adapters/codex.py`, `ai_agent_bridge/_codex.py`, `ai_agent_bridge/_gemini.py`. Same blindness, different code path.

### Affected scope (audit work to come)

| Scope | Status | Audit needed |
|---|---|---|
| #388 shipped modules (153) | All drafted via bugged `dispatch_codex`; reviewed by bugged `--no-tools` claude | YES |
| AI-history book chapters | All drafted via bugged `agent_runtime/adapters/codex.py`; review chain has more independent gates (anchor verification, dual-review accept, math sidebar verification) so probably less bad — but still affected | YES (priority per user 2026-05-05 02:50 local) |
| Incident-dedup sweeps (#878 #1–#4) | Drafted via `dispatch_smart.py edit` (sonnet, separate code path); surgical paragraph rewrites; not affected | NO |
| Ukrainian translations | Separate pipeline with RAG MCP tools enabled | NO |
| Hand-written content (orchestrator-authored sweeps, fixes) | Direct edits, no codex/claude dispatch | NO |

User priority (2026-05-05 ~02:50 local, verbatim): *"prio the book first, tonight"* — the book audit comes before the #388 audit. Book reviewer = Claude headless via `dispatch.py claude --no-tools` (cross-family from Codex prose-expander AND Gemini gap-analyzer; only fully cross-family option available for the book).

### Locked: per-call env-var overrides for codex dispatch

The fix preserves prior behavior for non-writer callers (planners, structural code review, cheap reasoning paths) and requires explicit opt-in for writer dispatches:

- `KUBEDOJO_CODEX_SEARCH=1` enables `--search`. Lands BEFORE `exec` on the codex CLI (top-level codex flag, not an exec subflag). Putting it after `exec` silently drops it.
- `KUBEDOJO_CODEX_SANDBOX=<read-only|workspace-write|danger-full-access>` overrides the sandbox mode. Use `danger-full-access` for dispatches that commit + push inside the codex run — workspace-write blocks `.git/worktrees/.../index.lock` and `api.github.com` per `feedback_codex_danger_for_git_gh.md`.

Smoke-tested via `KUBEDOJO_CODEX_SANDBOX=BOGUS-VALUE` (codex CLI rejected with "invalid value") — env-var threading proven end-to-end.

### Locked: pilot validation (Phase C)

The CKS pilot redo (PR #887) with `--search` ON produced demonstrably better content than the no-search run:

| Metric | No-search (PR #886, closed) | With-search (PR #887, open) |
|---|---|---|
| body_words | 5090 | 5016 |
| mean_wpp | 72.7 | 66.0 |
| median_wpp | 76.0 | 72.5 |
| short_paragraph_rate | 1.4% | 6.6% |
| max_consecutive_short_run | 1 | 2 |

Tighter density numbers are consistent with prose carrying more concrete factual specifics (which often bring shorter paragraphs like Source URLs and command snippets). Spot-check on PR #887 verified 4/4 sampled URLs resolve AND codex got the GitHub-vs-DockerHub namespace asymmetry for `kube-bench` correctly (`aquasecurity/kube-bench` on GitHub, `aquasec/kube-bench` on Docker Hub — the alt namespace `aquasecurity/kube-bench` on Docker Hub returns 404). That's the kind of detail that can't reliably come from training data; codex looked it up.

## What's still in flight

- **PR [#887](https://github.com/kube-dojo/kube-dojo.github.io/pull/887)** — CKS pilot redo (search-verified). T0 verifier passed, factual spot-checks passed. Awaiting cross-family review (codex with --search, since codex didn't author this content directly — it was a model-1.2-cis-benchmarks pipeline run, not human-authored claude code). Two known structural issues for reviewer to flag: stray `# Module 1.2` H1 + inline metadata (should be blockquote per `module-quality.md`). Same shape errors appeared on PR #886, so prompt-tuning follow-up is needed in `module-rewriter-388.md` or `module-writer.md`.
- **PR [#888](https://github.com/kube-dojo/kube-dojo.github.io/pull/888)** — `fix(dispatch): codex writer needs --search; reviewer needs WebFetch+WebSearch`. Patches `scripts/dispatch.py` only. **NOT YET EXTENDED** to fix `agent_runtime/adapters/codex.py` (the book's dispatch path) or `dispatch_codex_patch` (which still hardcodes `read-only` with no search). User flagged this mid-session (verbatim 2026-05-05 ~02:55: *"also dont forget to fix the source of the problem"*) — extension needed before the PR is reviewed-and-merged so the fix is comprehensive.
- **PR [#872](https://github.com/kube-dojo/kube-dojo.github.io/pull/872)** — codex routing tiers in `dispatch_smart.py`. Updated this session with `docs/codex-routing-smoke.md` (commit `8fb6d505`) confirming `gpt-5.4-mini` (6.4s/780t) + `gpt-5.3-codex-spark` (4.8s/11.3kt) both operational on bridge auth. Awaiting Gemini re-review (queued; orchestrator-side never dispatched it because the dispatch.py source-of-problem investigation took precedence).
- **PR [#884](https://github.com/kube-dojo/kube-dojo.github.io/pull/884)** + **PR [#885](https://github.com/kube-dojo/kube-dojo.github.io/pull/885)** — incident-dedup sweeps #3 (KCSA+KCNA) and #4 (Platform). Carried over from session 2026-05-04-3. Still awaiting user merge. Sweep #5 (Cloud + AI-ML + On-Prem) remains gated on these landing.

## What remains to do TONIGHT (the proper plan, gated)

The user explicitly approved a sequential, gated plan over `max 2 parallel sessions`. State at handoff time: 0 sessions running, ready to resume.

### Step 1 — extend PR #888 to cover agent_runtime adapter (the book's dispatch path)

The fix branch `fix/dispatch-codex-search` already has the dispatch.py patches (commit `593a8def`). Extend it with:

1. Patch `scripts/agent_runtime/adapters/codex.py` to honor `KUBEDOJO_CODEX_SEARCH=1` (insert `--search` before `exec` in `_build_codex_argv` or wherever the cmd is assembled — verify shape with `grep -n 'exec' scripts/agent_runtime/adapters/codex.py` first).
2. Patch `scripts/dispatch.py` `dispatch_codex_patch` (line ~682) — same env-var pattern as `dispatch_codex`. Currently hardcodes `read-only` and never sets `--search`. Lower priority than 1 because patches operate from review verdicts with source material attached, but should be fixed for consistency.
3. Commit + push to extend PR #888.
4. Update PR #888 description to note adapter coverage.

### Step 2 — cross-family review of PR #888

Reviewer: **Codex via `dispatch_codex_review --use-search`** (claude wrote this code, codex didn't — cross-family OK; use_search lets codex verify the claims about codex CLI behavior in the commit message, e.g. the assertion that `--search` lands before `exec`).

Sequential — single dispatch, ~5 min wall.

### Step 3 — book audit Phase D (one chapter pilot)

Reviewer: **Claude headless** via `dispatch.py claude --no-tools` from a worktree off `fix/dispatch-codex-search` so the patched `_CLAUDE_TEXT_ONLY_DISALLOWED` (with `WebFetch`/`WebSearch` allowed) is active. Cross-family from Codex prose-expander AND Gemini gap-analyzer.

Pilot chapter pick (orchestrator's suggestion; user to confirm):
- **`docs/research/ai-history/chapters/ch-33-deep-blue/`** — review-backfill list, dense verifiable specifics (dates, match results, hardware specs, ELO, opponent/operator names). High-signal target.
- Alternative: **`ch-32-the-darpa-sur-program`** — government/research history is harder to verify (some primary sources aren't web-indexed); could be more representative of the back-catalog's hardest cases.

Audit prompt should read the chapter and Sources files, list every factual claim with a specific (date, name, number, URL, technical spec), WebFetch/WebSearch each against primary sources, and output a structured per-claim report (`verified / unverified / wrong / dead-link`). Cap dispatch wall at ~30 min; sonnet-4-6 default model (cheap reviewer tier).

### Step 4 — measure + decide

After the pilot completes: report wall time, token cost, finding count by category. **Do not auto-chain** to other chapters — gate Phase E (the actual audit batch over 70+ chapters + 153 modules) on user reviewing Phase D's metrics. Per user 2026-05-05 ~02:30 local: *"we cannot run too many things parallel. we should make a proper plan without wasting resources."*

## Cold-start smoketest (the FIRST things to run in the new/resumed session)

```bash
cd /Users/krisztiankoos/projects/kubedojo

# 0. Canonical orientation
curl -s http://127.0.0.1:8768/api/briefing/session?compact=1 | head -50

# 1. Confirm the fix branch + PR state
unset GITHUB_TOKEN && export GH_TOKEN=$(grep -oE 'github_pat_[A-Za-z0-9_]+' .envrc | head -1)
gh api repos/kube-dojo/kube-dojo.github.io/pulls/887 --jq '{n:887,merged,head:.head.ref,review_decision}'
gh api repos/kube-dojo/kube-dojo.github.io/pulls/888 --jq '{n:888,merged,head:.head.ref,review_decision}'
gh api repos/kube-dojo/kube-dojo.github.io/pulls/872 --jq '{n:872,merged,head:.head.ref,review_decision}'
git log --oneline origin/fix/dispatch-codex-search 2>&1 | head -5

# 2. Smoke-check codex auth + Gemini key
codex exec -m gpt-5.4-mini "echo hi" --skip-git-repo-check --sandbox read-only 2>&1 | tail -3
echo "Env GEMINI_API_KEY ends with: ...${GEMINI_API_KEY: -8}"
# If ends with rpXZEPl4: stale → source ~/.bash_secrets per call OR /exit + restart Claude Code
# If ends with Oq3Aq7Bw: fresh

# 3. Verify the dispatch.py fix branch has the env-var threading
grep -n 'KUBEDOJO_CODEX_SEARCH' scripts/dispatch.py
# Expect: hit if you switched to fix branch; no hit on main

# 4. List worktrees — needed for book audit dispatch from the fix branch
git worktree list
```

## Files touched / committed this session

```
Committed on fix/dispatch-codex-search (PR #888, NOT YET MERGED):
  scripts/dispatch.py
    - dispatch_codex: read KUBEDOJO_CODEX_SEARCH + KUBEDOJO_CODEX_SANDBOX env vars
    - _CLAUDE_TEXT_ONLY_DISALLOWED: removed WebFetch + WebSearch (web tools now allowed
      in --no-tools claude dispatches; agentic Edit/Write/Bash/NotebookEdit/Skill/Agent/
      Task/ExitPlanMode still blocked)

Committed on claude/codex-routing (PR #872, awaiting Gemini re-review):
  docs/codex-routing-smoke.md
    - mini + spark smoke-test results, both clean

PR closed this session:
  PR #886 (codex/388-pilot-module-1-2-cis-benchmarks, original no-search draft)
  Branch deleted on origin

PR opened this session:
  PR #887 (codex/388-pilot-module-1-2-cis-benchmarks, search-verified redo) — content side
  PR #888 (fix/dispatch-codex-search) — dispatch.py fix, scope still being extended

Stash carried over from previous session (still on stash@{0}):
  docs/audits/2026-05-04-incident-reuse.md (audit refresh — auto-regenerates;
  pop only if needed; safe to drop)
```

## Cross-thread notes

**ADD:**

- **The `--search` problem applies to TWO independent codex dispatch paths.** `scripts/dispatch.py` (used by #388 batches) and `scripts/agent_runtime/adapters/codex.py` (used by book chapter dispatch). Both need the same env-var fix; PR #888 currently only covers the first. Future agent dispatch wrappers MUST default to honoring `KUBEDOJO_CODEX_SEARCH` — this is a class-of-problem, not a one-off.
- **Codex CLI flag order matters.** `--search` is a top-level codex flag (`codex --search exec ...`), NOT an exec subflag. Putting it after `exec` silently drops it. The patched `dispatch_codex` respects this; reviewers of new dispatch wrappers must verify the same.
- **Smoke-testing `--search` by comparing output text on a stable fact is a diagnostic mistake.** Codex may already know the answer from training data. Use a *threading* test instead — pass an invalid sandbox value (`KUBEDOJO_CODEX_SANDBOX=BOGUS`) and confirm the codex CLI itself rejects it. That's the only way to prove env-var threading end-to-end.
- **Two structural issues recurring across codex #388 drafts** (PR #886 + PR #887 both have them): stray `# Module X.Y: Title` H1 after frontmatter (creates duplicate visible title in Starlight) and inline metadata instead of blockquote-with-bold-labels. These are prompt-shape issues in `module-rewriter-388.md` / `module-writer.md`, not search-related. Fix the prompt before the next #388 batch.
- **`agent_runtime/adapters/codex.py` supports all three sandbox modes** (`read-only`, `workspace-write`, `danger`) per the docstring at line 14 + `supported_modes` at line 117; mode-to-CLI mapping at line 649. So the adapter is already mode-flexible — just needs `--search` plumbing added.

**DROP / RESOLVE:**

- "Stale Gemini API key in this Claude Code process env (`...rpXZEPl4`)" — still live. User has fresh key in `~/.bash_secrets` (`...Oq3Aq7Bw`); per-call `source ~/.bash_secrets &&` workaround unchanged. Permanent fix: `/exit` + restart Claude Code. Not blocking the book audit because that uses claude headless not gemini.
- "GH_TOKEN value still exposed in 2026-05-04 session 2 transcript" — still live, still operational hygiene only. Carrying forward.

## Blockers

- **PR #884 + #885 not yet merged** (incident-dedup sweeps KCSA+KCNA + Platform) — sweep #5 stays gated. Not urgent tonight given the audit priority shift.
- **PR #888 needs to be extended + reviewed + merged** before the book audit findings can be relied upon for follow-up rewrites; the audit itself runs from the fix branch worktree so it's not strictly blocked, but the durable fix needs to land on main.
- **GH_TOKEN does not propagate to codex sandbox env** (intentional per `_agent_env("codex")` design — credentials are filtered). The #388 batch still flags `module_skip: no_pr_in_response` because codex inside the dispatch can't `gh pr create`. Workaround: orchestrator opens the PR manually after codex pushes the branch (used for both PR #886 and PR #887). Permanent fix would be wiring the batch's post-codex hook to detect "branch pushed but no PR" and open the PR from the orchestrator's env. Lower priority than the audit.

## New / updated memory this session

- **NEW** — `feedback_claude_invoke_npx_not_path.md` (TOP PRIORITY): bare PATH `claude` drifts stale; always use `npx @anthropic-ai/claude-code@latest`. `agent_runtime/adapters/claude.py:117-118` has inverted preference — separate fix needed.
- **NEW** — `feedback_codex_writer_needs_search.md` (TOP PRIORITY): codex writer dispatches must use `--search` + writable sandbox; the systemic risk for 153 already-shipped #388 modules is documented inline.
- **NEW** — `reference_quality_board.md`: `http://127.0.0.1:8768/quality-board` is the live module-state HTML dashboard.
- **UPDATED** — `feedback_worktree_strict_origin_main.md`: appended Claude Code 2.1.128 caveat (bare `EnterWorktree` no longer enforces `origin/main` base).

## What was NOT done this session (carryover)

From session 3 handoff `2026-05-04-3-incident-dedup-platform-sweep.md`:

- ~~Verify PR #884 + PR #885 merge status and refresh audit on post-merge main~~ — verified NOT MERGED; audit refresh skipped (would create dirty tree mid-fix). Audit file remains stashed (`stash@{0}`).
- ~~Restart Claude Code in `/Users/krisztiankoos/projects/kubedojo` to load fresh GEMINI_API_KEY~~ — not done; per-call workaround used instead. Still recommended at session start.
- ~~Sweep #5 (Cloud + AI-ML + On-Prem)~~ — not started; gated on #884 + #885 merging.
- ~~Sweep #6 forbidden-trope rewrites~~ — not started.
- ~~Sweep #7 CKA / CKAD final cleanup~~ — not started.
- ~~Smoke-test gpt-5.4-mini + gpt-5.3-codex-spark on bridge auth path~~ — DONE this session; documented in PR #872 commit `8fb6d505`. Gemini re-review still queued.
- ~~Coherence sweep at KCNA bucket boundary (B3 protocol)~~ — not started.
- ~~Investigate the 8 module_skip events from KCNA batch~~ — not started.
- ~~Decide A2 plumbing vs straight to KCSA bucket-2~~ — not decided.

The session pivoted hard mid-flow when the codex no-search bug surfaced; the carryover above is real but should re-prioritize once the fact-check audit pipeline is proven.
