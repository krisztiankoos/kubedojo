# Session handoff — 2026-05-08 (session 1) — issue #983 fully shipped (Tier-3 ADR + Tier-2 PR + --resume-thread); codex runtime locked to danger + task-class --search

> Picks up from `2026-05-07-5-l-series-launch-and-active-active-prep.md`. **3 PRs merged** (#984 Tier-3 ADR `f27cd876`, #985 Tier-2 + `--resume-thread` `5a9794bc`, #986 codex runtime locked `46d8b00b`), **1 new memory**, **0 PRs dangling.** Autopilot v3 still alive. Closes the explicit next-session item from session-5: the active-active-comms deliberation has shipped end to end. The autonomous shift continues with the L-series queue (L2 → L6) per `docs/decisions/2026-05-07-local-api-ui-split.md`.

## Headline outcomes

1. **Issue #983 deliberation converged at round 3 with full [AGREE]** — `ab discuss persistent-agent-listeners --with claude,codex,gemini --max-rounds 3` (thread `3b760b6b643c40039bac280e3544964d`). Key corrections caught:
   - **Tier-2 is Claude-only resume in practice, not 2-of-3.** Codex caught: `scripts/agent_runtime/adapters/gemini.py:141` literally drops `session_id` with `_ = session_id`. Gemini CLI has no `--resume` equivalent. The session-5 framing's "2-3× cache hits for 2 of 3 agents" was overstated.
   - **LOC was inflated.** Real Tier-2 change is ~10 LOC + tests, not 50-100. Gemini caught.
   - **D1 storage**: reuse the existing `sessions` table at `scripts/ai_agent_bridge/_db.py:40-50, :283-339` keyed `discuss:{correlation_id}`. NOT in-memory dict, NOT new column on `channel_messages`. Codex caught the pre-existing schema; Gemini and Claude both verified and conceded.
   - **D2**: write our own ADR (PR #984) before any Tier-3 daemon work. Cross-project Multi-UI ADR exists in learn-ukrainian only — Gemini verified it's not in this repo.
   - **D3**: accept Codex `resume_policy="never"` ceiling. Enforced at `runner.py:158-164` (raises ValueError, not silent ignore).

2. **PR #984 Tier-3 ADR merged (`f27cd876`)** — `docs/decisions/2026-05-07-persistent-listeners-architecture.md`, 196 lines. Codex authored (gpt-5.5, danger, architect class), claude-sonnet reviewed (APPROVE with one NIT addressed inline before merge — line 12 imprecision about Gemini "storing" a bridge-side id when in practice the adapter drops the input and `parse_response` returns None). Q1/Q3/Q6/Q11 framework imported from cross-project Multi-UI ADR. Status remains `Draft` — Tier-3 daemon implementation deferred.

3. **PR #985 Tier-2 + `--resume-thread` merged (`5a9794bc`)** — `closes #983`. Two-round codex authorship on the same branch:
   - **Round 1 (`b345087e`)**: switches `_handle_discuss` from `entrypoint="delegate"` to `"bridge"`; per-agent session_id load/store via `get_session`/`set_session`; defense-in-depth gate so codex NEVER reads `codex_session_id` even if a stale row exists; new `session_mode=new|resume|none` field on usage records (per codex's reviewer note).
   - **Round 2 (`ce69c569`)**: `--resume-thread <thread_id>` CLI flag with trace-required guard. Selectivity rule (user instruction): "we don't want to resume everything, just those which had trace [in Tier-2 storage]." Flag rejects threads with no `claude_session_id` or `gemini_session_id` (codex sessions intentionally don't qualify — never-policy means no warmable trace). New `_channels.thread_exists()` helper.
   - Claude-sonnet reviewed APPROVE-with-nits (N1: failure-path `session_mode` misreporting as "resume" → fixed inline; N2: error message conflated typo and no-trace → reorder so `thread_exists` runs first → fixed inline; N3-N5 deferred). Three deferred nits below.
   - 18/18 tests passing. +556 LOC.

4. **PR #986 codex always danger + task-class `--search` merged (`46d8b00b`)** — codex's invocation contract locked. Three rounds: claude-sonnet authored round-1 (`2c885dee`), codex reviewed NEEDS CHANGES with 6 raw `codex exec` call sites missed in the audit, codex amended round-2 (`ed696209`) with the corrected `--search` policy + missed-site fixes. Claude-sonnet round-2 review caught one real conflict (`run_section_v3.py` had both `--full-auto` AND `--dangerously-bypass-approvals-and-sandbox` — undefined CLI behavior); single-line fix (`628c8609`) committed inline before merge.
   - **`supported_modes = frozenset({"danger"})`** at the adapter (`scripts/agent_runtime/adapters/codex.py:120`). `workspace-write` rejected with `ValueError`. `read-only` was already rejected per PR #981.
   - **`--search` policy** (corrected from initial always-on after user pushback): env-gated via `KUBEDOJO_CODEX_SEARCH`; `dispatch_smart` sets per-class — `draft` and `architect` ON; `search`, `edit`, `review` OFF. Legacy `dispatch.py` helpers hardcode per role: `dispatch_codex` + `dispatch_codex_patch` ON (writers); `dispatch_codex_review` OFF (preserves load-bearing default).
   - **6 raw `codex exec` call sites fixed** (Path D — direct subprocess that bypassed both the adapter and `dispatch.py`):
     - `scripts/run_section_v3.py:73-75`
     - `scripts/on-prem/phase2-write-only.py:353-355` (was `--sandbox read-only` — silently broken since PR #981)
     - `scripts/on-prem/phase2-write-only.py:392-394` (same)
     - `scripts/research/writer-calibration-rigorous.py:256-260` (same)
     - `scripts/research/writer-calibration-rigorous.py:307-311` (same)
     - `scripts/quality_pipeline.py:602-606`
   - **`scripts/ab` shell wrapper** pins `CODEX_BRIDGE_MODE=danger` (no `:=` override). Stderr warning fires if caller had set a different value.
   - **`scripts/ops/smoketest_ab_workspace_write.sh`** renamed/rewritten as `smoketest_ab_codex_danger.sh` — asserts the new invariant. The old one was broken on main since PR #981.
   - 15/15 tests pass; ruff clean.

5. **Codex invocation audit completed** — surfaced three flag-assembly paths (canonical adapter, `dispatch.py` legacy with three helpers, raw subprocess in 6 sites) and four orchestration layers (`dispatch_smart`, bridge `_codex.py`, `ab discuss` `_invoke_one`, 388 pilot). PR #986 locks all of them to a single contract. Memory entry `reference_session_resume_per_agent.md` (NEW) captures the per-agent resume capability matrix and the existing `sessions` table reuse pattern so future cold-starts don't re-derive the discovery.

## Decisions and contract changes

### Codex runtime contract (PR #986, locked once merged)

**Sandbox**: `--dangerously-bypass-approvals-and-sandbox` always. No `read-only`, no `workspace-write`, no env override. The adapter rejects anything else with `ValueError`. The `scripts/ab` wrapper hard-pins. Legacy `dispatch.py` helpers hardcode the flag.

**Search**: env-gated via `KUBEDOJO_CODEX_SEARCH` (default off at the adapter). Policy lives in the dispatch layer:
- `dispatch_smart` task classes: `draft` ON, `architect` ON, others OFF.
- `dispatch.py` legacy helpers: `dispatch_codex` ON, `dispatch_codex_patch` ON, `dispatch_codex_review` OFF.
- Bridge layer (`ab inbox run`, `ab ask-codex`): OFF (no env set).
- `ab discuss`: OFF (no env set).

**Why task-class instead of always-on**: latency + tokens + non-determinism + review-task contamination. A reviewer pulling external context from the live web during PR review biases the verdict. Original `use_search=False` default on `dispatch_codex_review` was load-bearing.

### Issue #983 Tier-2 contract (PR #985, merged)

`ab discuss` claude/gemini participants now warm-resume across rounds via the existing `sessions` table; codex stays fresh per `resume_policy="never"`. `--resume-thread <id>` flag attaches a new `ab discuss` invocation to an existing thread, but only when there's a "trace" (claude or gemini session_id stored). Trace requirement is selectivity: codex-only threads, pre-Tier-2 threads, and typo'd thread ids all reject with crisp error messages.

### `_handle_discuss` invocation shape (post-PR #985)

```python
# claude/gemini: load+store via sessions table; runner emits --resume <uuid>
session_id = get_session(f"discuss:{correlation_id}")[f"{agent}_session_id"] if agent in ("claude", "gemini") else None
result = runtime_invoke(agent, prompt, mode=("danger" if agent == "codex" else "read-only"),
                       cwd=(REPO_ROOT if agent == "codex" else None),
                       entrypoint="bridge", session_id=session_id, hard_timeout=900)
if agent == "claude" and result.ok and result.session_id:
    set_session(f"discuss:{correlation_id}", claude_session_id=result.session_id)
```

`--resume-thread <id>` reuses `correlation_id` instead of generating new + posts a continuation message in the existing thread.

### Reviewer protocol (locked across L-series, D-series, agent-runtime PRs)

Two checks on top of `docs/review-protocol.md`:
1. **Stale-content sweep** — verify content removed from one site is genuinely gone (no `// removed` comments, no orphaned helpers, no dead CSS).
2. **Live continuity check** — for routes/CLI flags, curl/exec the new behavior and confirm 200 / correct output.

For agent-runtime PRs specifically, add:
3. **Per-agent ceiling check** — codex must not receive a `session_id`; gemini may receive bridge-side context but must not be described as CLI-resumed.

## What's still in flight

- **Autopilot v3 PID 27331** — still alive at handoff. Continued shipping module-citation commits direct to main throughout this session.
- **Local API process** — still serving on `:8768` from a stale binary (started pre-L0/L1 merges from session 5). User opted to handle the restart themselves; carry over.
- **Autonomous L-series chain in progress** — L2 next, then L3-L6 sequentially. Each: codex author + claude-sonnet review + merge.

## What was NOT done (carryover)

### Three deferred review nits from PR #985

These were called APPROVE-with-nits and intentionally deferred to keep PR #985 scoped:

- **N3** — `get_session` returns both legacy short keys (`claude`, `gemini`, `codex`) and new long keys (`claude_session_id`, etc.). Backward-compat correct but accumulates stale shape. Clean up when `_inbox.py` migrates off the short keys.
- **N4** — integration test for `session_mode` end-to-end through `_handle_discuss`. Unit coverage at `_build_usage_record` exists; integration assertion is missing. Sufficient to ship; nice to add.
- **N5** — `@overload` decorators on `set_session` to satisfy Pyright. Runtime works; type-stub mismatch only. Tests show "No parameter named X" warnings on calls like `set_session("...", claude_session_id=...)`.

Worth opening a single follow-up issue grouping all three so they don't get lost.

### L-series continuation (next session, the autonomous-shift queue)

Per `docs/decisions/2026-05-07-local-api-ui-split.md`, sequential dispatch:

- **L2 #975** — Quality Board → `/quality` and `/quality/{module-key}`. Retire `/quality-board` URL alias to `/quality` (HTTP 301). ~250 LOC. Largest L-step. Touches `qb-*` filters + detail drawer + JSON-loading JS in `local_api.py`.
- **L3 #976** — V2 pipeline + autopilot v3 health → `/pipeline`. ~150 LOC.
- **L4 #977** — Activity feed → `/activity` with track/agent filters. ~120 LOC.
- **L5 #978** — Services + Worktrees + Missing/dead-letters → `/health`. ~120 LOC.
- **L6 #979** — slim `/` to overview cards only. Target under 20KB. ~200 LOC.

Pattern: codex authors with `dispatch_smart edit --agent codex --new-branch <branch> --worktree .worktrees/<branch>`, claude-sonnet reviews via `dispatch_smart review --agent claude`, address any nits inline if pre-validated single-line, merge with direct `gh pr merge --squash` (NOT `--auto`).

### D-series continuation (held since session 4)

- **D1 #964** — extract `routes/channels.py` only. Pre-D1 work has stale-content concerns now that L-series is in flight; double-check before dispatch.
- **D2 #965** — chat shell + post form.
- **D3 #966** — Decision Graph + body-diff modal.
- **D4 #967** — lineage scanner.
- **D4.5 #968** — keyboard nav.
- **D5 #969** — AFK-notify.
- **D6 #970** — FTS5 search.

Sequence per `docs/decisions/2026-05-07-deliberation-ui-roadmap.md`.

### From session 4 (still open)

- Wire cron for `detect_uk_divergence.py` (PR #960 shipped script; no schedule).
- Wire cron for `translation_v2.py worker loop` (PR #958 shipped `--max-calls`; no schedule).
- UK pipeline E2E smoke.
- Branch protection UI flag for `Incident dedup gate` (UI click only; CLI cannot).
- Open follow-up issues per autopilot section for #388 density-rewrite pass.
- Autopilot perf (P-series) — within-pipeline parallelism.

## Worktree state at handoff write-time

```
/Users/krisztiankoos/projects/kubedojo                              <main, 46d8b00b>
```

All session-1 worktrees pruned (codex-tier3-listeners-adr, codex-tier2-discuss-resume, claude-codex-danger-search). Clean.

## Cold-start smoketest

```bash
cd /Users/krisztiankoos/projects/kubedojo

# 1. Recent merges since session-5 handoff
git log --oneline --since="2026-05-07 21:30" | head -20
# Expect: ed696209 (round-2), 2c885dee (round-1), 5a9794bc (#985 squash),
#   1caea065 (N1+N2 fixes), 13364d8d (assertion fix), ce69c569 (resume-thread),
#   b345087e (Tier-2 base), f27cd876 (#984 squash), cb5ac023 (ADR nit),
#   c4807461 (ADR initial)

# 2. PR #986 status
source ./.envrc && unset GITHUB_TOKEN
gh pr view 986 --json state,mergedAt,latestReviews

# 3. Adapter contract: workspace-write is rejected
.venv/bin/python -c '
import sys
sys.path.insert(0, "scripts")
from agent_runtime.runner import invoke
try:
    invoke("codex", "x", mode="workspace-write", entrypoint="delegate")
    print("FAIL: workspace-write was accepted")
except ValueError as e:
    print("OK invariant fires:", e)
'

# 4. Tier-2 session resume tests still green
.venv/bin/pytest tests/test_bridge_inbox_cli.py tests/test_agent_runtime_runner.py tests/test_codex_always_danger.py tests/test_dispatch_codex_routing.py -q

# 5. ab discuss --resume-thread is wired
scripts/ab discuss --help | grep -E "resume-thread|max-rounds"

# 6. Memory entries
cat ~/.claude/projects/-Users-krisztiankoos-projects-kubedojo/memory/MEMORY.md | grep -E "session_resume_per_agent"

# 7. Autopilot v3 still alive?
cat .pipeline/v3/autopilot/heartbeat.json
ps -p 27331 -o command= | head -1
```

## Files touched / commits this session

```
PRs merged this session:
  #984  docs(decisions): Tier-3 persistent-listeners architecture        → f27cd876
  #985  feat(ab-discuss): Tier-2 session resume (closes #983)            → 5a9794bc
  #986  feat(agent-runtime): codex always runs danger + task-class --search → 46d8b00b

GH issues closed: #983 (via PR #985 close-link).

Memory added:
  reference_session_resume_per_agent.md — per-agent resume capability matrix.

Memory unchanged but reaffirmed:
  feedback_dispatch_codex_for_code_changes.md — TOP RULE held; everything substantial dispatched.
  feedback_codex_dispatch_sequential.md — sequential codex dispatches throughout.
  feedback_review_policy.md — every PR cross-family reviewed before merge.
  feedback_codex_push_silent_failure.md — caught + manually pushed once on PR #985 round-2.
  feedback_no_yes_man.md — pushed back on my own always-on --search recommendation when user asked "are you sure".
  feedback_gh_pr_merge_auto_squash_race.md — direct --squash, never --auto.
```

## Cross-thread notes

**ADD:**

- **Codex runtime contract is locked** (post-PR #986 merge): `supported_modes = {"danger"}`; `--search` task-class-driven; no env override for sandbox; bridge wrapper hard-pins. Adapter rejects `workspace-write` with ValueError; smoketest at `scripts/ops/smoketest_ab_codex_danger.sh` is the regression guard.
- **Tier-2 ab discuss session resume** is live. Claude warms across rounds via `sessions` table at `_db.py:40-50`; gemini's CLI silently drops `session_id` so no warm cache despite the adapter API; codex stays fresh per `resume_policy="never"`. `--resume-thread <id>` flag with trace-required guard. Issue #983 closed.
- **Six raw `codex exec` call sites** discovered during PR #986 audit — they bypassed both the adapter and `dispatch.py` helpers entirely (Path D in the audit). Four were silently on `--sandbox read-only` since PR #981. PR #986 fixes all six. Future audits should check `grep -rn "codex exec" scripts/` periodically — Path D may grow back if not vigilant.
- **Cross-project deliberation worked end-to-end**: framing emerged from learn-ukrainian → kubedojo session-5 captured it as issue #983 → kubedojo session-6 (this session) ran the deliberation, shipped the design doc, and shipped the implementation. The "out-ship learn-ukrainian's design" framing produced concrete code shipped within ~5 hours of starting the deliberation.

**DROP / RESOLVE:**

- "Run `ab discuss persistent-agent-listeners`" (carryover from session 5) → **RESOLVED** by the deliberation in this session.
- "Tier-2 PR scope ready to dispatch" (carryover from session 5) → **RESOLVED** by PR #985.
- "Tier-3 design doc drafted" (carryover from session 5) → **RESOLVED** by PR #984.
- "/operator 404 + 0 channel-links" (raised this session) → user opted to restart local-api themselves; carry over but no longer my action.

## Blockers

(unchanged from session 5)

- **Branch protection UI flag** for `Incident dedup gate` — UI click pending.
- **GH_TOKEN value still exposed in 2026-05-04 session 2 transcript** — operational hygiene only.
- **Stale `GITHUB_TOKEN` env var in shell** — encountered again this session, briefly broke `gh` calls. Fix: `source ./.envrc && unset GITHUB_TOKEN` at session start.

## New / updated memory this session

- `reference_session_resume_per_agent.md` (NEW) — per-agent session resume capability matrix. Claude warms; Gemini drops at adapter; Codex forbidden by registry. Existing `sessions` table is the reuse path; no new schema needed for thread-scoped session reuse. MEMORY.md index updated.

## Final tally

- **3 PRs merged** (#984 ADR, #985 Tier-2 implementation, #986 codex runtime contract).
- **3 codex dispatch rounds** on PR #985 (base + amendment + N1+N2 fix). **3 author rounds** on PR #986 (round-1 claude-sonnet, round-2 codex amendment, round-3 single-line nit fix). **2 cross-family reviews** on PR #986 (codex caught 6 missed sites round-1; claude-sonnet caught conflicting flag round-2).
- **1 deliberation** (`ab discuss persistent-agent-listeners`, 3 rounds, full [AGREE]).
- **0 PRs dangling** at session end.
- **1 memory added** + 1 memory updated (MEMORY.md index).
- **The explicit next-session item from session 5 is closed.** Active-active comms architecture deliberated, designed, and shipped end-to-end.
- **Autonomous shift begins**: L-series queue (#975 L2 → #979 L6) sequential, codex-author + claude-sonnet review per PR.
