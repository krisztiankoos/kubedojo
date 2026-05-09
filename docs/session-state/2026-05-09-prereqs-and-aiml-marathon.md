# 2026-05-09 — Prereqs + AI/ML rubric-critical marathon (13 modules)

## TL;DR

Cleared **13 of the rubric-critical-1.5 backlog** in one session via the `run_388_batch.py` pipeline: 1 Prereqs (kubectl-basics), 6 on-premises AI/ML Infrastructure (modules 9.1–9.6), 6 Platform data-ai/ai-infrastructure (modules 1.1–1.6). User-override on the order: Prereqs → on-prem AI/ML → platform AI/ML, ahead of the briefing's CKA/CKAD-first action queue. Plus PR #1061 (`/artifacts` HTML+MD browser, codex-authored) merged at session start. Hygiene pass at session start: 14 stale remote branches deleted, codex worktree leftover removed, 7 untracked PR-residual files cleared.

Session math: 14 PRs merged on main (`8b4d69cd → ba944502`), 13 codex writer dispatches, 13 cross-family reviews (gemini failed 13/13 → claude-sonnet-4-6 fallback worked 13/13), 3 codex re-spins, 7 inline orchestrator fixes, 3 direct merges. ~3h05m wall.

## Key decisions

**Re-spin vs inline-fix C3 routing — empirical pattern locked.**
- `NEEDS CHANGES` with **structural pedagogical regressions** (missing callouts, flattened hooks, semicolon-walls, missing war stories, missing Key Takeaways, merged LO bullets) → re-dispatch codex on the existing branch with the review excerpt as the brief. 3 cases this session: PR #1062, #1066, #1072.
- `NEEDS CHANGES` with **single-line text restorations** (CEL predicate, version mention, broken URL, dead reference) → orchestrator inline-fix per pre-edit self-check (single-line + pre-validated). 2 cases: PR #1064, #1070.
- `APPROVE_WITH_NITS` with **mechanical fixes** (URL pin, var substitution, hyperlink restoration, paragraph break, version clarification) → orchestrator inline-fix + merge. 5 cases: PR #1065, #1067, #1069, #1071, #1073.
- `APPROVE_WITH_NITS` with **content additions** (Key Takeaways bullets, war story creation, Q-explanation polish) → reviewer marks "no block, address before/after merge" → just merge. 3 cases: PR #1063, #1068, #1074.

**Codex spark cap → gpt-5.5 escalation, not auto-fallback.** `dispatch_smart.py edit --agent codex` defaults to `gpt-5.3-codex-spark`. After ~7 codex dispatches in a batch the spark variant began returning `OK: False, elapsed: 5–9s, resp_chars: 0` (silent rejection at session-init, not classic rate-limit error). Smoke-test on default codex model still passed → confirmed the cap is spark-specific. Escalation: `dispatch_smart edit --agent codex --model gpt-5.5 --mode danger` succeeded on PR #1066 (330s) and PR #1072 (150s). Confirms `feedback_spark_rate_limit_fallback_ladder.md` (heavier task → gpt-5.5).

**Gemini reviewer effectively dead today.** 13/13 `gemini_review_start` events ended in `ok: False, elapsed: ~15s, response_excerpt: ''`. 100% fallback rate. The `dispatch_388_pilot.py:342` `dispatch_claude_review` fallback path (added in PR #919 per the 2026-05-06 session) was the only thing that kept the marathon moving. Memory `feedback_headless_claude_gemini_fallback.md` reaffirmed.

**Verify deterministically — both LLMs hallucinate review nits.** Both codex (writer) and claude-sonnet (reviewer) hallucinated URL/fact "issues" that didn't exist on disk:
- PR #1062: claude review claimed `debug-running-pod` was a 404 needing fix; the URL was already correct (200) before AND after the respin.
- PR #1063: claude flagged AMD `instinct.docs.amd.com` as suspect; confirmed 200 with curl, the suggested `rocm.docs.amd.com` alternative was the actual 404.
- PR #1066: in respin output codex claimed v0.4.2 → "200 redirect"; v0.4.2 actually returns plain 200 (no redirect).
- PR #1068: claude flagged Evidently 0.7.21 / ZenML 0.94.2 as "potentially hallucinated, should be 0.4-0.5 era"; PyPI confirmed both numbers correct (latest 0.7.21 / 0.94.3).
- Pattern: **always curl/PyPI-verify before applying any URL/version "fix" the reviewer asserts**, even when the reviewer is confident. `feedback_deterministic_over_hallucination.md` confirmed as TOP-PRIORITY for review-nit triage.

**Codex re-spin regression class — bulk regex/find-replace introduces collateral corruption.** PR #1066's gpt-5.5 respin (commit `e75d759c`) restored the 4 requested fixes correctly but introduced 3 separate new regressions: filename `ollama-network-policy.yaml` → `ollama-network-policy; yaml`, next-module link `module-9.6-edge-inference` → `module-9. 6-edge-inference` (literal space), 26 `<p>...</p>` HTML tags + 1 `<ul>/<li>` block instead of markdown paragraphs/bullets. Looked like an over-eager bulk-substitution pass (period→semicolon in unintended places, html generated where markdown wanted). Required a 2nd orchestrator-inline cleanup commit (`9bb4771a`) using a Python one-shot for HTML-stripping + targeted replacement. **Lesson**: when codex returns from a "broad mechanical edit" task, scan the diff for collateral substitutions before declaring victory — not just the requested fixes.

## Contract observations (no changes shipped this session)

- `dispatch_388_pilot.py:271` `gh pr comment` subprocess inherits parent shell env, which carries the stale `~/.bash_secrets` `GITHUB_TOKEN` → 401 → review never posts to the PR. The dispatcher truncated review excerpt (last 1500 chars in `claude_review_done` event's `response_excerpt`) is the only persisted artifact. Already documented in the standing blockers (`reference_gh_token_from_envrc.md`); fix not in scope this session.
- Batch summary at `pilot_done` lists held PRs from hold-time and never reconciles against post-hold orchestrator merges. After my inline-fix-and-merge passes, the dispatcher's "BATCH SUMMARY → 2 PR(s) held with NEEDS CHANGES" listed PRs that were already merged. Misleading but harmless. If future automation depends on the summary, would need a `git log` reconciliation step before listing.
- `dispatch_smart.py` does not accept `--agent gemini` (only claude + codex). For gemini-fallback work outside the dispatcher, use `scripts/dispatch.py gemini` or `scripts/agent_runtime/runner.py:invoke("gemini", ...)`.

## Cold-start smoketests

```bash
# Tree state — should be clean on main
git status --short && git rev-list --count origin/main..HEAD HEAD..origin/main
#   → "" / "0 0"

# Briefing (canonical)
curl -s http://127.0.0.1:8768/api/briefing/session?compact=1 | jq '.recent_commits[0:3]'
#   top of main is ba944502 ai-storage > d39de3fa ai-cost > 16bc2282 llm-serving

# Critical-rubric remaining (was 261; cleared 13 this session → expect ~248)
curl -s http://127.0.0.1:8768/api/quality/scores | jq '.critical_count'

# Recent PR run (this session)
source ./.envrc && unset GITHUB_TOKEN && \
  gh pr list --state merged --limit 14 --json number,title --jq '.[] | "\(.number) \(.title)"'
#   #1062..#1074 + #1061
```

## Outstanding / next session

**User's stated track is exhausted.** The Prereqs (1 critical) + on-prem AI/ML (6) + platform data-ai/ai-infra (6) buckets are all cleared. The `ai/` track-aliases (11 modules at avg 4.20+) are NOT rubric-critical and the user explicitly noted they're a separate "polish pass" decision, not a 388 density rewrite.

**Backlog still 1.5-critical** (per `/api/quality/upgrade-plan` track grouping):
- Platform Disciplines: 65 (was 71; 6 cleared this session)
- Platform Toolkits: 52
- Platform Foundations: 31
- CKS: 29
- CKAD: 23
- On-Premises (other sub-sections): ~30
- Linux Foundations + Operations: 9

**Don't auto-resume on a default track.** User should pick the next bucket explicitly — they bypassed the briefing's CKA/CKAD ordering this morning, so don't assume CKA is the right next step either.

**Standing blockers unchanged from morning briefing:**
- Branch protection UI flag for "Incident dedup gate" still pending (UI action, can't be done from orchestrator's PAT).
- GH_TOKEN value rotation deferred (operational hygiene).
- The dispatcher → `gh pr comment` 401 issue is a known minor bug; review excerpts are recoverable from the JSONL even if not posted to PRs.

## Memory: no new entries this session

The patterns hit today are all already captured. Reaffirmed (no edits needed):
- `feedback_deterministic_over_hallucination.md` (TOP) — 4 hallucinated nits caught by curl/PyPI verification.
- `feedback_headless_claude_gemini_fallback.md` (TOP) — 13/13 gemini failures, 13/13 claude fallbacks.
- `feedback_spark_rate_limit_fallback_ladder.md` (TOP) — confirmed gpt-5.5 escalation works for heavier edit tasks when spark caps mid-session.
- `feedback_dispatch_codex_for_code_changes.md` (TOP) — orchestrator stayed in inline-fix-only territory for content; structural rewrites went to codex.
- `feedback_codex_review_danger_mode.md` — all codex respins used `--mode danger`.
- `feedback_no_dilemma_framing.md` — 1 decision card surfaced (PR #1062 verdict A/B/C); user picked A.
- `feedback_user_reassigns_overrides_bridge.md` — user verbally redirected from briefing's `actions.next` to Prereqs+AI/ML order.

## Predecessor

Previous session ended with `/api/state/manifest` cold-start path and the codex-desktop UI brief at `docs/briefs/2026-05-09-codex-desktop-artifacts-ui-brief.md` ready for execution. PR #1061 (codex-authored unified `/artifacts` browser) was the realization of that brief; it was merged at the start of this session. The codex-desktop dispatch is therefore complete.
