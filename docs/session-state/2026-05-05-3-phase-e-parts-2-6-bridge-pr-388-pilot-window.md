# Session handoff — 2026-05-05 (session 3) — Phase E Parts 2-6 shipped + bridge round-1 fix ported + #388 ai-ml-engineering pilot

> Picks up from `2026-05-05-2-phase-d-pilots-and-phase-e-sweep.md`. Inherited Part 2 dry-run in flight (background bash `bmdolfkpn`) and Parts 3-9 plumbing. This session shipped Phase E Parts 2 through 6 (19 fixes / 18 chapters changed across 48 audited), merged two carry-over PRs (#889 round-1 fix, #872 codex routing tiers) via cross-family review with no claude burn on the review side, and ran a #388 ai-ml-engineering pilot during the 14-20 CET 2x window — 2 modules rewritten cleanly by codex but PRs #891 + #892 still pending gemini review at session end (gemini API on REST 503 → OAuth fallback ladder, slow but designed path).

## Decisions and contract changes

### Phase E sweep — Parts 2 through 6 shipped (19 fixes / 18 chapters across 48 audited)

Per-Part flow locked from session 2 ran cleanly. Each Part: dispatch dry-run → inspect diffs → apply audited fixes from JSON → build verify → commit + push → next.

| Part | Range | Audited | With fixes | Total fixes | Commit |
|---|---|---|---|---|---|
| 2 | ch-09..ch-16 | 8 | 6 | 8 | `ac992e21` |
| 3 | ch-17..ch-24 | 8 | 4 | 4 | `2848ed68` |
| 4 | ch-25..ch-32 | 8 | 1 | 1 | `b09e9b77` |
| 5 | ch-35..ch-40 (skips ch-33+34) | 6 | 0 | 0 | (no commit, all clean) |
| 6 | ch-41..ch-48 | 8 | 1 | 1 | `1243e7c4` |

Notable findings:

- **Part 2 ch-10 caught a primary-source paraphrase error in the bundle itself.** Mind 1950 §5 reads "64 magnetic tracks each with a capacity of 2560, eight electronic tubes with a capacity of 1280" — but `docs/research/ai-history/chapters/ch-10-the-imitation-game/infrastructure-log.md` and `scene-sketches.md` both paraphrase it as "2560 wheels with 1280-digit capacity each" (track count and per-track capacity inverted, tube capacity misattributed). The chapter inherited that wrong reading from the bundle. Audit cross-checked against the primary PDF, fix shipped (`ac992e21`). **Bundle followup queued (TODO #7)**: correct the two bundle files to match the primary source so future drafts in this chapter don't regress.
- **Part 6 ch-46 audit's "after" string would have duplicated "gating logic — "** in the post-apply prose. The factual finding (LSTM forget+input gates ≠ GRU reset+update gates) was correct; the substitution string was overzealous. Overrode the audit JSON in-place with a surgical minimum edit (gate-name swap only) before applying. Override note added to audit JSON for the record. Pattern to remember: the audit's `before/after` is a starting point; if applying it would produce broken prose, override with a cleaner minimum edit before running the apply step.
- **Part 4 onward dropped sharply** (1 fix in 8 chapters for Part 4, 0 for Part 5, 1 for Part 6). The section-by-section risk profile from the 3-pilot synthesis predicted that the modern AI-history chapters are more bundle-anchored than the early-period chapters (Part 1: 6 fixes, Part 2: 8 fixes). Confirmed in practice. Cumulative: Parts 1-6 = 20 fixes / 19 chapters changed / 48 chapters audited (40% non-clean).

Parts 7, 8 (skips ch-58), 9 NOT started — held at 14:00 CET when the 2x claude window opened. Resume in next session or after 20:00 today.

### PR #889 — bridge round-1 short-circuit fix ported from learn-ukrainian

User asked for the ab-bridge feature port from learn-ukrainian → kubedojo. Scoped into 3 PRs (Tier A correctness fix, Tier B citation_check + review flag, Tier D plumbing). Recommended phased order; user agreed implicitly (kept working).

**PR 1 (Tier A) shipped this session — `4b505d13`:**
- Ports learn-ukrainian commit `872d8376b0` (round-1 short-circuit block + per-round directive split) + `4185c0a33c` (test alignment).
- The bug: kubedojo's `ab discuss` would short-circuit at round 1 if all agents signed `[AGREE]`, but round 1 is parallel fan-out — agents haven't seen each other's replies yet, so [AGREE] is "I'm done with my answer" not cross-agent assent. Surfaced empirically in learn-ukrainian's собака-gender deliberation 2026-05-05: 3 agents disagreed substantively, all signed [AGREE] in round 1, protocol declared consensus on a hallucination.
- Fix: convergence requires `round_idx >= 2`. Round 1 directive explicitly says `[DISAGREE]` is the default. Round 2+ directive tells agents to read prior replies and push back.
- Codex cross-family review (gpt-5.5) returned NEEDS CHANGES with two findings: (1) `min(max(1, args.max_rounds), MAX_ROUNDS_CAP)` allowed `--max-rounds 1` which silently broke the round-1-cannot-converge invariant — round 1 prints "Forcing round 2" then immediately hits `round_idx == max_rounds` break. Fix: `MAX_ROUNDS_FLOOR = 2` clamp + `ℹ️` clamp message. (2) Function docstring described stale convergence semantics. Updated to reflect round-2+ minimum.
- Fixup commit `0c2367ff` addressed both. Added regression test `test_discuss_max_rounds_one_clamps_to_two`. 74/74 bridge tests pass. Codex re-review APPROVE. Squash-merged.

**PR 2 (Tier B — `_citation_check.py` ~744 LOC + 541 LOC tests + 42 LOC channels.py hook + `--review` flag): deferred to next session.** Larger surface area; safer with a fresh context.

**PR 3 (Tier D — bridge plumbing, 9 helper modules): deferred until usage signal demands.** Per `feedback_no_staging_scaffolding.md`, importing 9 helpers ahead of need is the staging-scaffolding antipattern.

### PR #872 — codex routing tiers in dispatch_smart.py finally cleared

Carry-over from session 1+2. Gemini's prior NEEDS CHANGES was "untested model strings introduce runtime risk" — fix `8fb6d505` added `docs/codex-routing-smoke.md` with smoke results (gpt-5.4-mini: 6.4s/780t, gpt-5.3-codex-spark: 4.8s/11.3kt). Re-requested gemini review pre-window (no claude burn on the review side). Gemini APPROVE: "concrete evidence eliminates the runtime failure risk that blocked the previous review." Squash-merged: `a2190f1a`.

`dispatch_smart.py --agent codex` now routes by task class: search→gpt-5.4-mini, edit/draft→gpt-5.3-codex-spark, review/architect→gpt-5.5. Per `feedback_codex_model_routing.md`.

### #388 ai-ml-engineering pilot during 14-20 CET 2x window

User reminded me that 14-20 CET is the 2x claude credit window and asked if they could run #388 there instead. Yes — #388 batches are codex-driven (writer) + gemini (reviewer), no claude in the loop. Pilot dispatched.

**Three batch attempts on the same `--track ai-ml-engineering --max 2` bucket:**

1. **13:36 (pre-window) — codex hung at 0 bytes for 2 hr.** Process alive, low CPU (0.68s of CPU after 2hr wallclock = 99.99% network-wait). Classic codex API/SSE hang, not "slow." Per `feedback_codex_dispatch_sequential.md`. I killed pid 49497 + 49496 around 15:41. The runner was in `T+` state (suspended via Ctrl-Z). My SIGCONT made a queued KeyboardInterrupt fire, runner crashed before logging `module_fail`. Worktree + branch cleaned up. Net: zero shipped from this attempt.

2. **16:10 (mid-window, started by user, I missed it because no Monitor armed) — both modules rewritten cleanly.**
   - `module-1.9-building-with-ai-coding-assistants` → commit `b63e796d`, T0 verified (body_words=6466, mean_wpp=60.4, median_wpp=62, short_rate=0.028)
   - `module-1.9-anomaly-detection-and-novelty-detection` → commit `926c3921`, T0 verified (body_words=8281, mean_wpp=47.1, median_wpp=44.5, short_rate=0.011)
   - **Both `module_skip: no_pr_in_response`** because codex sandbox has no `GH_TOKEN` (intentional `_agent_env` design). Branches pushed to origin, PR-create failed silently, runner advanced. Cleanup ran, worktrees removed.

3. **17:40 (mid-window) — same `--track --max 2` rerun by user.** Codex on both modules redid the rewrites locally (different commits: `501c1cbf` for module 1, similar for module 2) but `git push` was rejected because the remote branches already had session-2's `b63e796d` / `926c3921`. **Codex defensively did NOT force-push.** Both `module_skip: no_pr_in_response`. The redo-codex burn was wasted because the bucket-builder filter only skips merged-to-main modules, not modules with active `codex/388-pilot-*` branches.

**Manual triage shipped this session:**
- PR #891 opened on `b63e796d` (module 1). Gemini review dispatched at 17:48 — REST 503 → API key 429 → OAuth fallback (designed path per `reference_gemini_subscription_switch.md` and `feedback_codex_offline_contingency.md`). Process pid 30090 still running at session end.
- PR #892 opened on `926c3921` (module 2). Gemini review dispatched at 17:53 — same 503/429 → OAuth fallback. Process pid 33153 still running at session end.
- Both PRs `MERGEABLE`, `reviewDecision: ""` (gemini hasn't posted a verdict yet). `headRefOid` matches the codex commits.

**Bug to fix in next session:** bucket-builder for `run_388_batch.py` should also skip modules with an active `codex/388-pilot-<slug>` branch on origin (not just shipped-to-main modules). Otherwise every rerun until the PRs merge wastes ~15 min of codex per module on a duplicate rewrite that defensively can't push. Small enhancement to `scripts/quality/run_388_batch.py` bucket-build phase.

### Window-friendly orchestration pattern locked

User said "thin claude through the 2x window, codex/gemini do the work, but keep me in the loop." Ran the playbook:
- Pre-window: dispatched codex review of PR #889 (cleared in 1 round-trip), dispatched gemini re-review of PR #872 (APPROVE → merged).
- Window opens: held Phase E sweep (claude-driven audits) until 20:00. Ran #388 codex pilot (codex+gemini only). Triaged held PRs #891 + #892 manually (orchestrator-side `gh pr create`, no claude content burn).
- Monitor armed on JSONL events; per-chapter / per-module results stream as `<task-notification>` events without polling.

This is the right shape for future 14-20 windows: claude orchestrator stays thin (commit pushes, PR opens, decision routing); codex + gemini do the heavy work.

## What's still in flight

- **PR #891 (388 module 1, `b63e796d`) — gemini review running on OAuth fallback.** Process pid 30090. Will land within minutes-to-an-hour depending on OAuth account rotation. Once APPROVE, squash-merge.
- **PR #892 (388 module 2, `926c3921`) — gemini review running on OAuth fallback.** Process pid 33153. Same situation.
- **PR #890** — separate gemini review running (pid 26134) dispatched by codex-interactive at 17:44. Reviewing a "premature-closure audit for AI History review coverage." Not opened by me; track but don't block on it.
- **Phase E Part 7 (ch-49..ch-56)** — held at session end, not started. Resume after 20:00 CET or in next session.

## What remains to do

### Immediate (next session)

1. **Merge PR #891 + #892** once gemini reviews land as APPROVE. Standard squash + delete branch. If NEEDS CHANGES, hand-fix the small stuff inline + re-request review.
2. **Resume Phase E Parts 7-9.** Part 8 skips ch-58 (already audited inline session 2). Per-Part: dispatch dry-run → inspect → apply → build → commit → push. Same script + same per-Part flow from session 2's handoff. Each Part ~30-50 min wall + ~5 min apply/commit. ~3 Parts × ~45 min = ~2.25 hr wall.
3. **Continue #388 ai-ml-engineering batch.** With 891+892 merged, bucket-builder will skip them next time → next batch picks up modules 3-4 (likely Decision Trees, Linear Regression, Hyperparameter Optimization, Dimensionality Reduction per the briefing's top-5).

### Bug fixes / enhancements

- **Bucket-builder skip-by-branch enhancement.** `scripts/quality/run_388_batch.py` should also skip modules with an active `codex/388-pilot-<slug>` remote branch, not just shipped-to-main modules. Prevents wasted codex burn on duplicate rewrites that can't push. ~20 LOC.
- **Bundle correction for ch-10 Manchester storage spec.** `docs/research/ai-history/chapters/ch-10-the-imitation-game/{infrastructure-log,scene-sketches}.md` carry the same wrong paraphrase the chapter had pre-fix. Replace with primary-source wording: "64 magnetic tracks each with a capacity of 2560, eight electronic tubes with a capacity of 1280." Low priority — chapter is now correct on origin.
- **Restart Claude Code for fresh `GEMINI_API_KEY`** — still stale in this process; `source ~/.bash_secrets &&` workaround works per-call. Permanent fix: `/exit` and restart. Carry-over from session 1+2.

### Bridge port follow-ups (PR 2, PR 3)

- **PR 2 — port `_citation_check.py` (`c36d159a26`, 744 LOC module + 541 LOC tests + 42 LOC channels.py hook) + `--review` flag for `ab discuss` / `ab post`.** Self-contained feature, tests come with it. ~1.3K LOC PR. Defer to fresh session for context.
- **PR 3 — bridge plumbing (watch --follow, --model/--deadline flags, deliveries-table reply routing, reconciliation job, stuck-queue fix, scope preflight, 9 helper modules).** Defer until kubedojo workflow signals demand. No usage signal yet.

### Other carryover (from session 2)

- **Sweep #5 (Cloud + AI-ML + On-Prem) incident-dedup.** Refresh `docs/audits/2026-05-04-incident-reuse.md` on post-merge main (PRs #884 + #885 are merged), then dispatch sweep #5 via `dispatch_smart.py edit`. Outside the 2x window.
- **Sweep #6 forbidden-trope rewrite** — `ai-ml-engineering/mlops/module-1.3-cicd-for-ml.md` (1 file, inline orchestrator work).
- **Sweep #7 — CKA / CKAD final cleanup.** Confirm via fresh audit after sweep #5.
- **Promote `scripts/check_incident_reuse.py` to CI-required** once curriculum-wide count reaches 0.
- **Update `module-rewriter-388.md` / `module-writer.md` prompts** to ban stray `# Module X.Y: Title` H1 + inline metadata before next #388 batch. Recurring shape error in codex drafts.

## Cold-start smoketest

```bash
cd /Users/krisztiankoos/projects/kubedojo

# 0. Canonical orientation
curl -s http://127.0.0.1:8768/api/briefing/session?compact=1 | head -50

# 1. Confirm trunk state
git log --oneline -10
# Expected most recent: 1243e7c4 (Phase E Part 6) or later

# 2. Check open #388 PRs awaiting gemini review or merge
unset GITHUB_TOKEN && export GH_TOKEN=$(grep -oE 'github_pat_[A-Za-z0-9_]+' .envrc | head -1)
gh pr list --state open --search 'feat(388)' --json number,title,reviewDecision,mergeable,headRefOid

# 3. Worktree state (should be clean except codex-interactive detached)
git worktree list

# 4. Phase E sweep state — any Part 7 process running?
/bin/ps -ef | grep -E 'sweep_ai|run_388' | grep -v grep

# 5. Stale gemini review processes from session 3 (pid 30090, 33153)?
/bin/ps -ef | grep dispatch.py | grep -v grep
# If still alive, check /tmp/gemini-review-89{1,2}-output.md for verdicts

# 6. Briefing's actionable triage
curl -s http://127.0.0.1:8768/api/briefing/session?compact=1 | jq '.actions, .top_modules'
```

## Files touched / committed this session

```
On main (squash-merged or direct commits):
  ac992e21 chore(ai-history): Phase E sweep Part 2 — fix 8 wrong-specifics across ch-09..ch-16
  2848ed68 chore(ai-history): Phase E sweep Part 3 — fix 4 wrong-specifics across ch-17..ch-24
  b09e9b77 chore(ai-history): Phase E sweep Part 4 — fix 1 wrong-specific in ch-26
  1243e7c4 chore(ai-history): Phase E sweep Part 6 — fix 1 wrong-specific in ch-46
  4b505d13 fix(deliberation): block round-1 short-circuit + restructure per-round directive (#889)
  a2190f1a feat(dispatch): mirror PR #870 codex routing tiers in dispatch_smart.py (#872)

PRs merged this session:
  #889 fix/discuss-round1-block → main (squash 4b505d13). Branch deleted.
  #872 claude/codex-routing → main (squash a2190f1a). Branch + worktree deleted.

PRs still open at session end:
  #891 codex/388-pilot-module-1-9-building-with-ai-coding-assistants (b63e796d, gemini review on OAuth fallback)
  #892 codex/388-pilot-module-1-9-anomaly-detection-and-novelty-detection (926c3921, gemini review on OAuth fallback)
  #890 (separate, codex-interactive's review-coverage audit fix; gemini review running pid 26134)

Worktrees still around:
  /Users/krisztiankoos/projects/kubedojo                            (primary, main @ 1243e7c4)
  /Users/krisztiankoos/projects/kubedojo/.worktrees/codex-closed-ac-repair      (codex-interactive's #890 work)
  /Users/krisztiankoos/projects/kubedojo/.worktrees/codex-interactive            (detached HEAD, pre-existing)

Files touched (sweep target chapters):
  src/content/docs/ai-history/ch-09-the-memory-miracle.md
  src/content/docs/ai-history/ch-10-the-imitation-game.md
  src/content/docs/ai-history/ch-11-the-summer-ai-named-itself.md
  src/content/docs/ai-history/ch-13-the-list-processor.md
  src/content/docs/ai-history/ch-15-the-gradient-descent-concept.md
  src/content/docs/ai-history/ch-16-the-cold-war-blank-check.md
  src/content/docs/ai-history/ch-17-the-perceptron-s-fall.md
  src/content/docs/ai-history/ch-18-the-lighthill-devastation.md
  src/content/docs/ai-history/ch-20-project-mac.md
  src/content/docs/ai-history/ch-22-the-lisp-machine-bubble.md
  src/content/docs/ai-history/ch-26-bayesian-networks.md
  src/content/docs/ai-history/ch-46-the-recurrent-bottleneck.md

Bridge port files:
  scripts/ai_agent_bridge/_channels_cli.py (+127 lines net per PR #889)
  tests/test_bridge_inbox_cli.py (+59 lines net per PR #889)
```

## Cross-thread notes

**ADD:**

- **Phase E sweep results so far (Parts 1-6 complete):** 20 fixes / 19 chapters changed / 48 chapters audited. Section-by-section trend: Parts 1-2 (early period, 1850s-1950s) heavy with cast/glossary corrections (8-14 chapters with fixes); Parts 3-6 (1956-1998) drop sharply (1-4 fixes each). Bundle anchoring is stronger for modern AI history. Parts 7-9 (1998-present) likely similar to Parts 4-6.
- **Phase E driver reminder: dispatch-then-apply-from-audit-JSON.** Re-running a Part's `--dry-run` re-dispatches and overwrites the audit JSONs. Don't re-run unless something changed.
- **Phase E ch-10 caught a bundle-paraphrase error in primary-source territory.** When the audit's web citation contradicts the bundle's own paraphrase, the audit is usually right (audit cross-checks against the primary source the bundle paraphrased from). Bundle correction should follow as cleanup.
- **Bridge round-1 short-circuit fix is now active in kubedojo's `ab discuss`** (per `4b505d13`). Future multi-agent deliberations require ≥ 2 rounds; round-1 [AGREE] is informational-only and triggers an `ℹ️` log line. `--max-rounds 1` clamps to 2 with a clamp message.
- **#388 batch sandbox-PR-create gap is structural.** Codex sandbox has no `GH_TOKEN` (intentional `_agent_env` design). Every codex-led `gh pr create` fails with `module_skip: no_pr_in_response`. Workaround: orchestrator opens PR manually after batch identifies pushed branches. Bucket-builder enhancement (skip-by-branch) is the durable fix for the wasted-redo-codex-burn problem.
- **Window-friendly orchestration pattern: claude thin, codex+gemini heavy.** During 14-20 CET 2x window: dispatch codex/gemini for content + reviews; claude only does PR opens, branch cleanup, decision routing, Monitor reads. No Phase E sweep dispatches (claude-driven audits). No `dispatch_smart.py edit/draft` (sonnet). #388 batches are fine (codex+gemini only). Lock this for future windows.
- **Gemini API rate-limit ladder (REST 503 → API key 429 → OAuth) is slow but designed.** `dispatch.py gemini --review` falls through automatically. Plan for 5-30 min reviews when REST is congested, not 1-3 min. Per `reference_gemini_subscription_switch.md`.

**DROP / RESOLVE:**

- "Phase E sweep Parts 2-9 still pending" — partially resolved. Parts 2-6 shipped this session. Parts 7-9 deferred to next session.
- "PR #872 still open + NEEDS CHANGES" — RESOLVED. Merged this session as `a2190f1a`.
- "Re-request Gemini review on PR #872" — RESOLVED.
- "Phase E sweep Part 2 dry-run in flight at handoff time (background bash task `bmdolfkpn`)" — RESOLVED. Part 2 finished + shipped.

## Blockers

- **PR #891 + #892 still awaiting gemini cross-family review at session end.** Reviews dispatched, on OAuth fallback ladder due to gemini REST congestion. Will land in next session likely; if not, re-request fresh review.
- **Phase E Parts 7-9 not started** — held at 14:00 CET window opening. ~3 Parts × ~45 min = ~2.25 hr wall remaining.
- **Bucket-builder doesn't skip-by-branch** — every #388 ai-ml-engineering rerun until 891+892 merge wastes ~30 min of codex on duplicate rewrites. Fix is small (~20 LOC) but not urgent.
- **Stale `GEMINI_API_KEY` in this Claude Code process.** Per-call workaround `source ~/.bash_secrets &&` works. Permanent fix: `/exit` and restart Claude Code.
- **GH_TOKEN does not propagate to codex sandbox env** (intentional). Workaround: orchestrator opens PR manually after codex pushes the branch. Documented; not a bug.

## New / updated memory this session

(No new memories. Patterns hit were extensions of existing memories — `feedback_codex_dispatch_sequential.md`, `reference_gemini_subscription_switch.md`, `feedback_codex_offline_contingency.md`, `feedback_review_policy.md`. Window-friendly orchestration pattern is captured in this handoff's cross-thread notes; if the pattern recurs in 2-3 future sessions, promote to a memory then.)

## What was NOT done this session (carryover)

- Phase E Parts 7-9 — not started (held for window).
- Sweep #5 (Cloud + AI-ML + On-Prem) — not started.
- Sweep #6 forbidden-trope rewrite (1 file inline) — not started.
- Sweep #7 CKA / CKAD final cleanup — not started.
- Bridge sync PR 2 (citation_check + review flag) — not started.
- Bridge sync PR 3 (plumbing) — deferred indefinitely until usage signal.
- Bundle follow-up: ch-10 Manchester storage spec — not started.
- Bucket-builder skip-by-branch enhancement — not started.
- Update `module-rewriter-388.md` / `module-writer.md` prompts to ban stray H1 — not started.
- Coherence sweep at KCNA bucket boundary (B3 protocol) — not started.

The session was deeper than wide on two fronts: Phase E book-audit cleared 5 of 9 Parts (Parts 2-6), and the bridge round-1 fix landed cleanly via cross-family review with no claude burn on the review side. The 2x window used for #388 codex pilot — productive but capped at 2 modules due to the bucket-builder skip-by-branch gap that turned every rerun into a no-op.
