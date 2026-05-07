# Session handoff — 2026-05-07 (session 5) — D0 + L0 + L1 + What's New + codex-always-danger merged; L-series launched; active-active comms deliberation queued

> Picks up from `2026-05-07-4-channels-ui-and-deliberation-roadmap.md`. **5 PRs merged** in one session (#971 D0, #972 What's New rewrite, #980 L0 nav, #982 L1 operator, #981 codex-always-danger), **1 new ADR** (local-api UI split L0–L6), **8 GH issues opened** (L0–L6 + the persistent-agent-listeners decision-pending). Autopilot v3 still alive through the whole session, shipping module-citation commits in parallel. Next session is queued: full `ab discuss` on real active-active agent communications.

## Headline outcomes

1. **PR #971 D0 channels contract bugfixes (`2014f916`)** — `closes #963`. Four contract drifts in PR #961+#962 fixed:
   - `/api/channels` payload field shape now matches renderer (`name`/`last_event_ts`).
   - `reply_complete` events persist a `body` field; renderer surfaces it.
   - `message_posted` added to `VALID_CHANNEL_EVENTS` (gate-only; D2 wires the post path).
   - `_config.DB_PATH` resolves `.bridge/messages.db` first then falls back to `.mcp/...` — closes the live-discovered bug where API showed `{"channels":[]}` against real `.bridge/messages.db` data.
   - +130 LOC, 2 new regression tests. Codex authored (gpt-5.5, danger), claude-sonnet reviewed (MINOR NITS — all forward-pointing for D1).

2. **PR #972 What's New rewrite (`17dba4f8`)** — new `/changelog` page is learner-facing now: 45 lines down from 258, no PR numbers / phase codes / AI metadata / self-review status. Original 258-line release log preserved verbatim at `docs/internal-changelog.md` (outside Starlight content path → not rendered). User pushback that drove this: *"the whats new page, it is not good, this is not a proper whats format, we just need to tell users whats new and thts it, not internal stuff they might not understand."* Claude-sonnet authored, codex (danger mode) reviewed and caught a real factual error — the May 2026 ML Tier-1 bullet said "twelve new foundational modules" but two of the twelve are renumbered existing modules (slots 1.6 + 1.12). One-line reword applied (`8a954eb7`), merged.

3. **PR #980 L0 top nav + skeleton routes (`25210104`)** — `closes #973`. Sticky top nav linking `/operator /quality /pipeline /activity /channels /health` now lives at `_render_top_nav()`. Stubbed `/operator /quality /pipeline /activity /health` as placeholder routes (real content lands in L1–L5). **The home → /channels gap closes here** — until this PR, the new chat UI was unreachable except by typing the URL. Codex authored, claude-sonnet reviewed (NEEDS CHANGES round 1 — caught two real bugs: `/quality-board` regression and dual-sticky-header overlap); round-2 fix `9e01ed4f` introduced `--topnav-h: 45px` CSS variable + `top: var(--topnav-h, 45px)` on existing sticky headers; APPROVE round 2.

4. **PR #982 L1 Operator triage to `/operator` (`b79243e6`)** — `closes #974`. The 3-column `op-now/op-blocked/op-next` panel moved off the home monolith into a dedicated `/operator` page; `/` keeps a 1-row summary card showing active+blocked counts and a link to the full page. Stale-content sweep landed: removed `op-col-list/op-hero-empty` CSS from dashboard scope, removed dashboard JS targeting `#op-now/#op-blocked/#op-next`. Codex authored (+285/-135 in `local_api.py`), claude-sonnet reviewed (MINOR NITS — stale "Phase D: Operator" comment + weak summary-card test); both inline-fixed in `5f78e9ed`.

5. **PR #981 codex always runs in danger mode (`93730548`)** — user demand after a third repeat-failure in the same session: *"this cause so much damage to us so far. and yet you keep repeating. add it to the code that codex always runs in fucing danger mode else he cannot fact check etc"*. Read-only is now impossible for codex at the code level:
   - `codex.supported_modes` drops `read-only`; `_mode_flags` raises `ValueError` on it.
   - `dispatch_smart.py --agent codex` forces `mode=danger` regardless of task class (explicit `--mode read-only` errors out).
   - `dispatch.py:dispatch_codex()`, `dispatch_codex_review()`, `dispatch_codex_patch()` all switched to `--dangerously-bypass-approvals-and-sandbox`.
   - `scripts/ab` default `CODEX_BRIDGE_MODE` flipped from `workspace-write` to `danger`.
   - `_codex.py` defaults + legacy `safe` value both map to danger.
   - `tests/test_codex_always_danger.py` (new) plus updates to `test_dispatch_codex_routing.py`.
   - **Plus a downstream fix caught pre-merge**: `_channels_cli.py:_invoke_one` was passing `mode="read-only"` for ALL ab-discuss participants. After this PR landed, codex would crash on every round of `ab discuss --with codex,...`. Per-agent fix: codex → danger + REPO_ROOT cwd; claude/gemini stay read-only.
   - Round 1: claude-sonnet authored. Round 2: codex (gpt-5.5, danger sandbox + worktree) caught 4 real findings — most critically, `dispatch_codex()` main path STILL allowed read-only after round 1, plus `sys.executable` violations of `AGENTS.md`, plus `git diff --check` failure due to behind-main rebase, plus a cosmetic dry-run print bug. Round 3: codex APPROVED after `04a4ac1a` rebased + addressed all four. Round 4: my own catch on `_channels_cli.py` shipped in `6d8d22f0`. CI green; merged clean.

6. **ADR `docs/decisions/2026-05-07-local-api-ui-split.md` (`fd302920`)** — local-API UI split L0–L6 roadmap. User pushback that drove this: *"how can i navigate from the api ui main page to the channel? and why do we stack so many things in one page? should not we do it like learn-ukrainian project done it"*. Imports learn-ukrainian's route-per-concern dashboard pattern (10 dedicated routes vs our 84KB single-page monolith with 226 structural elements and zero static `<a href>` links). 7 GH issues opened with label `local-api-ui-split`: #973 (L0 — done), #974 (L1 — done), #975 (L2 Quality Board), #976 (L3 Pipeline), #977 (L4 Activity), #978 (L5 Health), #979 (L6 slim home). Reviewer protocol additions baked into the ADR per user instruction (*"the agent who reviews it make sure we dont have stale obsolete content"*): every L-PR requires (1) stale-content check (no orphaned content / dead CSS / `// removed` comments) + (2) live nav check (curl each new route, confirm 200 + correct title + nav link from `/`).

7. **GH issue #983 — Persistent agent listeners (decision-pending label, deliberation in thread)**. Cross-project deliberation surfaced an architectural finding worth capturing as durable home for the next big work item. Three-tier framing:
   - **Tier 1 (today, broken)**: cold subprocess + cold prompt cache per round of `ab discuss`. 0 LOC of work, costs every round full Anthropic prompt-cache miss.
   - **Tier 2 (ship-now, ~50–100 LOC)**: switch `_channels_cli.py:964` `entrypoint="delegate"` → `"bridge"` + per-(agent, discussion-correlation-id) session_id store + per-agent gate (claude+gemini only — codex stays fresh per its `resume_policy="never"`). Wins 2-3× cache hits for 2 of 3 agents; likely fixes round-2 root truncation as side effect.
   - **Tier 3 (deferred, weeks)**: API-daemon listeners with claim/lease/keepalive — true active-active continuity. Per the cross-project ADR, Q1/Q3/Q6/Q11 cover the framework. Defer until Tier 2 ships.
   - **Structural ceiling**: codex's `resume_policy="never"` (project policy, quota economics + fresh-context-per-round design intent) means even Tier-3 daemons can't fully warm codex's API cache. They'd save spawn cost (~1-2s) but each call still pays full prompt-cache creation. Real ceiling, not engineerable around.
   - **My initial framing was wrong**: I proposed "thread session_id through `_channels_cli.py:964`, ~50 LOC." Codex caught it: `runner.py:139 _enforce_resume_policy` raises `ValueError` when (a) codex is passed any session_id, OR (b) delegate/dispatch entrypoints pass session_id. Naive threading would crash on every codex round AND on EVERY round of any agent in delegate-mode. Real fix is the entrypoint switch + per-agent gate.

## Decisions and contract changes

### Codex-always-danger is now a code-level invariant

Three failures in a single session (`b0831agg2` review, `bz69nr365` review, plus an earlier dispatch I retried in danger mode) proved that prompt-level / memory-level reminders aren't sufficient. Memory `feedback_codex_review_danger_mode.md` saved earlier in the session, then PR #981 baked it into the code so it can never recur. Going forward:

- `dispatch_smart.py --agent codex` always resolves to `mode="danger"`.
- `runner.invoke("codex", ..., mode="read-only")` raises `ValueError` at the boundary.
- All legacy `dispatch_codex*` helpers in `dispatch.py` use the danger sandbox flag.
- `scripts/ab` and `_codex.py` default to danger for inter-agent bridge messaging.
- Workspace-write override remains valid for callers that explicitly want `--full-auto` (e.g. niche dispatch flows that don't need full network access).

### L-series ADR pattern is locked

Same shape as the D-series ADR from session 4: ADR file → one GH issue per phase → shared per-roadmap label → ADR commit references the issue numbers. Reviewer additions specific to L-series PRs:
1. **Stale-content sweep** — verify no orphaned content / dead CSS rules / `// removed` comments / `# TODO L<N>` markers remain after a panel is moved.
2. **Live nav curl check** — every new route returns 200 with the expected title; the home `/` nav links to it.

This pattern has now been used twice (D-series channels UI roadmap + L-series local-api UI split). Codified as a cross-thread note.

### Persistent-listener architecture decision lives in issue thread

Per `docs/decisions/pending/README.md` convention (multi-week architectural calls go in GH issues with `decision-pending` label, not pending Decision Cards): issue #983 is the home. Three open decision points in the issue body:
- D1: persist session_id in channel_messages payload vs in-memory dict
- D2: extend Multi-UI ADR with daemon spec vs ad-hoc lease/keepalive
- D3: accept codex's `resume_policy="never"` ceiling vs revisit

Cross-validation: same finding emerged independently from a learn-ukrainian deliberation between gemini and codex in the same time window; their codex caught the structural error in the original framing first, my consult of our codebase confirmed it.

## What's still in flight

- **Autopilot v3 PID 27331** — still alive at handoff (uptime ~7h53m at 23:00 local). 9 module-citation commits shipped to main during this session (on-premises/security section completed, now mid-section on `platform/disciplines/core-platform/sre/module-1.1`). Section commits visible in `git log origin/main`.
- **L-series #975–#979** open (L2 Quality Board → L6 slim home). All gated by L0+L1 which are now merged. Ready to dispatch sequentially next session.
- **D-series #964–#970** still open from session 4 (D1 extract `routes/channels.py` → D6 FTS5 search). **Held — user pivoted to L-series mid-session 5.** Resume after L-series settles (or interleave).
- **Local API process** — still running on port 8768 (the autopilot writes to `_db.py`'s default DB path). After PR #981 + the channels_cli fix, codex calls in ab-discuss now go via danger mode + REPO_ROOT cwd.

## What was NOT done (carryover)

### Immediate next session — the user explicitly wants this

**Run `ab discuss` claude+codex+gemini on the persistent-agent-listeners architecture (issue #983).** User instruction (verbatim, profanity-edit OK): *"create a session handoff and in the next session you guys discuss how to do really active communications, and you show those ukranians whos boss, ok ?"*

Cold-start agents next session should:

1. **Read this handoff in full.**
2. **Read issue #983** in full — it captures the three-tier framing, codex's structural finding, the open decision points, and the link to the cross-project Multi-UI ADR.
3. **Read `docs/decisions/2026-05-07-local-api-ui-split.md`** for context on the L-series (the UX layer that this work feeds into).
4. **Optional: skim the cross-project Multi-UI ADR** if accessible (the source agent referenced `docs/decisions/pending/2026-05-06-multi-ui-channel-participation.md` in the learn-ukrainian project — Q1 identity, Q3 participant_scope, Q6 lease+keepalive, Q11 fallback_reason). We should write our equivalent.
5. **Run `scripts/ab discuss persistent-agent-listeners --with claude,codex,gemini --max-rounds 3`** with a brief that asks each agent to argue from its strengths:
   - Claude: orchestration, cross-thread context, what falls out of the user's daily flow.
   - Codex: implementation feasibility, sandbox/auth gotchas, the `resume_policy="never"` ceiling.
   - Gemini: source verification, anti-rubber-stamp.
6. **Convergence target**: a Tier-2 PR scope (~50–100 LOC) ready to dispatch + a Tier-3 design doc (`docs/decisions/2026-05-07-persistent-listeners-architecture.md` or similar — drafted, not implemented). The competitive framing (paraphrased): we want our Tier-2 to ship before learn-ukrainian's, and our Tier-3 ADR to be tighter than theirs.
7. **Emit a Decision Card** if the deliberation surfaces real disagreement on D1/D2/D3 from issue #983. Per `feedback_ab_discuss_for_decisions.md`.

Concrete first action: open the channel + dispatch the brief. Don't pre-decide.

### L-series continuation (also next session, parallel to the deliberation)

- **L2 (#975)** — move Quality Board to `/quality` and `/quality/{module-key}`. Retire `/quality-board` URL alias to `/quality` (HTTP 301). ~250 LOC. Largest L-step; touches `qb-*` filters + detail drawer + the JSON-loading JS.
- **L3 (#976)** — V2 pipeline + autopilot v3 health to `/pipeline`. ~150 LOC.
- **L4 (#977)** — Activity feed to `/activity`. ~120 LOC.
- **L5 (#978)** — Services + Worktrees + Missing/dead-letters to `/health`. ~120 LOC.
- **L6 (#979)** — slim `/` to overview cards only, target under 20KB total. ~200 LOC.

### D-series resumption (from session 4)

- **D1 #964** — extract `routes/channels.py` only (codex's narrower cut from the deliberation). Pre-D1 work has stale-content concerns now that L-series is in flight; double-check before dispatch.
- D2 #965 (chat shell + post form), D3 #966 (Decision Graph + body-diff modal), D4 #967 (lineage scanner), D4.5 #968 (keyboard nav), D5 #969 (AFK-notify), D6 #970 (FTS5 search). Sequence per `docs/decisions/2026-05-07-deliberation-ui-roadmap.md`.

### From session 4 (still open)

- Wire cron for `detect_uk_divergence.py` (PR #960 shipped script; no schedule).
- Wire cron for `translation_v2.py worker loop` (PR #958 shipped `--max-calls`; no schedule).
- UK pipeline E2E smoke.
- Branch protection UI flag for `Incident dedup gate` (UI click only).
- Open follow-up issues per autopilot section for #388 density-rewrite pass.
- Autopilot perf (P-series) — within-pipeline parallelism.

## Worktree state at handoff

```
/Users/krisztiankoos/projects/kubedojo                         <main>
```

All session-5 worktrees pruned (`codex-d0-channels-contract`, `claude-whats-new-rewrite`, `codex-l0-top-nav`, `codex-l1-operator`, `codex-codex-always-danger`). Clean.

## Cold-start smoketest

```bash
cd /Users/krisztiankoos/projects/kubedojo

# 1. Autopilot still alive?
cat .pipeline/v3/autopilot/heartbeat.json
ps -p 27331 -o command= | head -1

# 2. L0+L1 nav live?
curl -s -o /dev/null -w "HTTP %{http_code} %{size_download}b /\n" http://127.0.0.1:8768/
curl -s -o /dev/null -w "HTTP %{http_code} %{size_download}b /operator\n" http://127.0.0.1:8768/operator
curl -s -o /dev/null -w "HTTP %{http_code} %{size_download}b /channels\n" http://127.0.0.1:8768/channels
curl -s http://127.0.0.1:8768/ | grep -c 'href="/channels"'   # should be >= 1 (was 0 before L0)

# 3. Codex danger enforcement live?
PYTHONPATH=$(pwd)/scripts .venv/bin/python -c '
from agent_runtime.runner import invoke
try:
    invoke("codex", "x", mode="read-only", entrypoint="delegate")
except ValueError as e:
    print("OK invariant fires:", e)
'

# 4. ab discuss against the new contract
scripts/ab channel list   # /channels listing should still work
sqlite3 .bridge/messages.db "SELECT message_id, from_agent FROM channel_messages ORDER BY message_id DESC LIMIT 5"

# 5. Recent merges this session — should show #971 #972 #980 #981 #982 + ADR
git log --oneline --since="2026-05-07 18:00" | head -15

# 6. The 7 L-series + 1 decision-pending issue
source ./.envrc && unset GITHUB_TOKEN && gh issue list --label local-api-ui-split --limit 10
gh issue list --label decision-pending --limit 10
```

## Files touched / commits this session

```
Direct-to-main (chronological after session-4 handoff):
  fd302920 docs(decisions): local-api UI split L0-L6 ADR
  + autopilot v3 commits — 9 modules across on-premises/security + start of platform/disciplines/core-platform/sre

PRs merged this session:
  #971  fix(channels): D0 contract bugfixes (closes #963)                 → 2014f916
  #972  docs(whats-new): rewrite for learners; preserve release log       → 17dba4f8
  #980  feat(local-api): L0 top nav + skeleton routes (closes #973)       → 25210104
  #982  feat(local-api): L1 — move Operator triage to /operator (#974)    → b79243e6
  #981  feat(agent-runtime): codex always runs in danger mode             → 93730548

GH issues opened: #973–#979 (L0–L6, label `local-api-ui-split`), #983 (Persistent agent listeners — `decision-pending`).
```

## Cross-thread notes

**ADD:**

- **Codex always runs in danger mode (code-level invariant).** Adapter `supported_modes` drops `read-only`; `dispatch_smart.py --agent codex` forces danger; legacy `dispatch_codex*` use danger sandbox; `scripts/ab` default `CODEX_BRIDGE_MODE=danger`. Workspace-write override remains valid for niche cases. After this, the read-only-induced "rc=-9, garbage from stale rollouts" failure mode (which cost three retries this session alone) cannot recur.
- **L-series ADR + reviewer protocol locked.** ADR `docs/decisions/2026-05-07-local-api-ui-split.md`. Every L-PR requires stale-content sweep + live nav curl. Pattern is now identical to D-series (`docs/decisions/2026-05-07-deliberation-ui-roadmap.md`) — apply to any future user-flagged UI direction.
- **L0 + L1 LIVE on `/`.** Top nav with `/operator /quality /pipeline /activity /channels /health`; Operator triage on its own page. The home → /channels invisibility is fixed.
- **Persistent agent listeners — decision-pending issue #983.** Three-tier framing: Tier 1 (today, broken), Tier 2 (entrypoint switch + per-agent session_id store, ~50-100 LOC, ship-now), Tier 3 (API-daemon listeners, weeks, deferred). Codex caught a structural error in the naive "thread session_id" framing (`runner.py:139 _enforce_resume_policy` blocks delegate entrypoint + codex resume). Cross-validated against learn-ukrainian's parallel deliberation. **Next session is the deliberation that decides Tier-2 PR scope.**
- **`_channels_cli.py:_invoke_one` per-agent mode** — codex → danger + REPO_ROOT cwd, claude/gemini → read-only. Necessary because codex.supported_modes dropped read-only in PR #981 (would have crashed every codex round of `ab discuss`).
- **decision-pending GH label** created this session (yellow `#FBCA04`). Per `docs/decisions/pending/README.md:39-43` convention: multi-week architectural calls live as GH issues with this label, not as Decision Card files.

**DROP / RESOLVE:**

- "Ship D0 (#963)" (carryover from session 4) → **RESOLVED** by PR #971 / commit `2014f916`.
- "What's New page is internal/jargon-heavy" (raised + resolved this session) → **RESOLVED** by PR #972 / commit `17dba4f8`. New page at `/changelog`; old release log preserved at `docs/internal-changelog.md`.
- "/channels invisible from /" (raised + resolved this session) → **RESOLVED** by PR #980 / commit `25210104`. Top nav links it.
- "Codex repeatedly running in read-only and failing" (raised + escalated 3× this session) → **RESOLVED structurally** by PR #981 / commit `93730548`. Code-level invariant.

(Session-4's `/channels` UI cannot show real data is also fully resolved — D0 ships the DB-path fix.)

## Blockers

(unchanged from session 4, plus one update)

- **Branch protection UI flag** for `Incident dedup gate` — UI click pending.
- **GH_TOKEN value still exposed in 2026-05-04 session 2 transcript** — operational hygiene only.
- **Stale `GITHUB_TOKEN` env var in shell** — encountered this session, briefly broke `gh` calls. Fix: `unset GITHUB_TOKEN && source ./.envrc && unset GITHUB_TOKEN` at session start. Already documented in cross-thread notes; mention here for visibility.

## New / updated memory this session

- `feedback_codex_review_danger_mode.md` (NEW) — codex review dispatches must use `--mode danger`; read-only starves codex (rc=-9, garbage from stale rollouts). Saved after the second of three failures; PR #981 then made the rule mechanically enforced.

Existing memory reaffirmed (no edits needed):
- `feedback_dispatch_codex_for_code_changes.md` — TOP RULE held throughout; everything substantial dispatched (D0, What's New, L0, L1, codex-always-danger, all reviews).
- `feedback_codex_dispatch_sequential.md` — sequential codex dispatches enforced (when L1 was in flight, codex-always-danger went to claude-sonnet instead).
- `feedback_headless_claude_gemini_fallback.md` — headless-claude reviews used throughout; gemini not invoked this session.
- `feedback_review_policy.md` — every PR cross-family reviewed before merge.
- `feedback_finish_what_you_started.md` — reviewer findings addressed inline or via dispatch; no dangling NEEDS CHANGES.
- `feedback_no_dilemma_framing.md` + `feedback_execute_without_nagging.md` — `AskUserQuestion` used twice with recommendation + tradeoff (What's New old-content disposition + date range; next-dispatch-priority); user signaled "stop asking, do them parallel" mid-session and I switched modes.
- `feedback_gh_pr_merge_auto_squash_race.md` — merged with direct `gh pr merge --squash`, never `--auto`.

## Final tally

- **5 PRs merged today** (#971, #972, #980, #981, #982) — second-fastest sustained merge cadence this week (session 4 had 6).
- **8 GH issues opened** (#973–#979 L-series, #983 persistent-listeners decision).
- **1 ADR committed** (`docs/decisions/2026-05-07-local-api-ui-split.md`).
- **1 new memory** (`feedback_codex_review_danger_mode.md`).
- **0 PRs dangling** — clean exit.
- **Autopilot v3 still running** at handoff (9 module-citation commits direct to main this session).
- **Next session pre-loaded**: full `ab discuss` deliberation on real active-active comms architecture, with the explicit goal of out-shipping learn-ukrainian's design.
