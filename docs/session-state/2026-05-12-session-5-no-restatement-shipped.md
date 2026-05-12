# Session handoff — 2026-05-12 session 5

**NO RESTATEMENT contract shipped + 4 chain-failure modules rewritten clean. 10 PRs merged + 1 issue tracked. `ab discuss` converged on Option C; codex+gemini both rejected the deterministic anti-repetition gate (Option D) after codex measured Jaccard overlap clusters at ~0.40 for both clean and padded modules. Backfill batch restarted at session end (limit 50, 742 modules total) and running autonomously on the codex lane.**

## TL;DR for cold-start

1. Hit `curl -s http://127.0.0.1:8768/api/briefing/session?compact=1` first.
2. **NO RESTATEMENT contract is now in main**: `scripts/prompts/module-rewriter-388.md` carries a new `## NO RESTATEMENT ACROSS H2 SECTIONS` section (PR #1165 / commit `78e7a9df`). Each core H2 must contribute net-new mechanism/example/comparison/decision rule; later sections may not restate the same thesis in different prose; synthesis closing sections (`Senior Judgment`, `Patterns & Anti-Patterns`, `Decision Framework`) are allowed only if they introduce net-new criteria.
3. **4 #388 modules rewrote successfully under the new contract** (all merged): #1166 (prompting-basics, took +1 fix iter), #1167 (privacy-safety-trust, clean), #1168 (mlx-on-apple-silicon, clean — the hardest 5800w-padding case is solved), #1169 (ai-coding-tools-landscape, -2563/+235 lines).
4. **queue-ai-ml.txt is now empty of `revision_pending: true` modules.** Filter PR #1163 dropped 123 of 124 entries; the final 1 (#1169) is merged.
5. **Bridge push-verify race fixed** (PR #1164 / commit `7a787c6c`): `runner.py` now captures HEAD before danger-mode dispatch and skips `verify_current_branch_pushed` when HEAD didn't move. Unblocks `ab discuss` reliability — codex no-op rounds no longer trip false `origin stale` errors.
6. **Backfill batch is RUNNING at session end** (started 19:20 UTC, limit 50, default codex agent). Logs at `logs/backfill_pending_20260512_1923.log`. First action next session: check `/api/briefing/session` to see if it's still running or how many cleared.
7. **A⁴ Decision Card cleanup done** (PR #1162): moved `docs/decisions/pending/2026-05-12-readiness-signal-redesign.md` → `docs/decisions/...` with Resolution footer citing the 3 implementation PRs.
8. **New memory rule**: `feedback_never_branch_in_primary_dir.md` — primary dir stays on `main`, all branching → worktrees. User correction 2026-05-12. The harness has 60 worktrees configured precisely so branching is free.

## What shipped this session

### 10 PRs merged on `main`

| PR | Module / Change |
|---|---|
| #1162 | docs(decisions): resolve readiness-signal redesign — A⁴ shipped |
| #1154 | feat(388): density+structure rewrite of Quantization and Model Formats (APPROVE_WITH_NITS, chain leftover) |
| #1163 | chore(388): filter chain queues — 123 of 124 entries cleared |
| #1164 | fix(runner): skip push-verify when danger-mode dispatch is a no-op (#1143) |
| #1165 | feat(388): add NO RESTATEMENT rule to writer contract (Option C) |
| #1166 | feat(388): rewrite module-1.3-prompting-basics under NO RESTATEMENT contract |
| #1167 | feat(388): rewrite module-1.5-privacy-safety-and-trust under NO RESTATEMENT contract |
| #1168 | feat(388): rewrite module-1.4-mlx-on-apple-silicon under NO RESTATEMENT contract |
| #1169 | feat(388): rewrite module-1.1-ai-coding-tools-landscape under NO RESTATEMENT contract |

### 3 PRs closed (re-rewritten as fresh dispatches)

| PR | Module | Reason closed |
|---|---|---|
| #1147 | module-1.3-prompting-basics | Worked Example tail (~700w) circular + non-canonical `developers.openai.com` URLs. Reborn as #1166. |
| #1149 | module-1.5-privacy-safety-and-trust | One 404 CNCF whitepaper URL (otherwise content was excellent). Reborn as #1167. |
| #1156 | module-1.4-mlx-on-apple-silicon | 5800w endemic philosophical rehashing + 404 mlx-lm/docs URL. Reborn as #1168. |

### 1 issue opened

- **#1170** — Option F (Prose Capacity Plans) tracking issue. Records the deferred F decision + design questions for implementation + calibration question (sample 20 already-shipped modules for natural body_words distribution). Not blocking; revisit before next bulk #388 sweep.

### ab discuss channel

- **`padding-constraint-tightening-2026-05-12`** — 3 rounds, codex + gemini. Full transcript in `.bridge/messages.db`. Converged on C+A; D rejected (Jaccard ~0.40 cluster); F deferred.

## Key durable decisions

### D1 — Option C (NO RESTATEMENT) is the immediate fix; Option F (capacity plans) is deferred

Codex argued and gemini conceded: the verifier path at `verify_module.py` has no per-module budget input today; shipping F now means touching dispatch/research/verifier plumbing + calibration + tests, which is materially broader than a prompt contract change. The padding failure mode is **contract-shaped** (the contract had no anti-restatement language), not floor-shaped. Floor stays at 5000 globally.

### D2 — Option D (deterministic anti-repetition gate) is REJECTED, not deferred

Codex empirically measured Jaccard / section-pair overlap on a clean module (#1154 `quantization-and-model-formats`, ~0.41-0.45) and a rejected module (#1156 `mlx-on-apple-silicon`, ~0.38-0.43). They cluster too closely — D as a hard gate would false-positive on legitimate conceptual build-up. Both agents agreed. Do NOT revisit D as a hard gate; advisory-flag-only might be acceptable but only after recalibration on 20+ accepted modules.

### D3 — When body_words falls under floor after content removal, add NET-NEW substance (not floor lowering)

Empirical from PR #1166: deleting the synthesis tail (~63w) dropped body_words to 4937, below the 5000 floor. Solution adopted: dispatch codex to add ~80-120w of substantive net-new content (one Worked Example variant, one comparison row, one anti-pattern with code) — NOT to lower the floor or restore the synthesis tail. This is the contract working as designed: floor enforces depth, NO RESTATEMENT enforces substance.

### D4 — Cross-family review on rerun-rounds must explicitly say "read the diff, not the description"

Per existing memory `feedback_gemini_hallucinates_round2_approvals.md`. Confirmed useful — PR #1166 round-2 gemini correctly read the diff and approved the actual fix.

## Lessons learned (worth saving)

### L1 — Codex sometimes leaks scratch files into primary dir

PR #1156 rerun left `pr_content.md` (the module content as scratch) in the primary repo dir. Codex's own output flagged this. The brief said "stay in the worktree" but codex `cd`'d to primary for `npm run build` and dropped a scratch file there. Not destructive (untracked, deleted at session end), but a pattern worth catching. **Action for next time**: explicit brief language: "do not write any file outside the worktree, even scratch."

### L2 — Codex `cd`s to primary for `npm run build` from worktrees

Both PR #1168 and #1156 reruns ran `npm run build` from primary because `.worktrees/*/node_modules` resolution doesn't work. Codex reports the workaround openly. **Mid-term action**: investigate why `node_modules` doesn't symlink correctly into worktrees, fix once. The build needs to be runnable from worktrees so the rule "stay in worktree" can be enforced.

### L3 — Monitor's startup-race guard needs `[ "$prev_head" != "?" ]`

My first Monitor for codex commits emitted a false "commit landed" event because `git rev-parse HEAD` returns "?" (my `|| echo "?"` fallback) when the worktree doesn't yet exist between dispatch and codex starting. The "?" gets stored as `prev_head`, then the next real HEAD reading triggers the echo. Fix: `[ "$prev_head" != "?" ]` in the guard. Already applied in the ai-coding-tools and backfill Monitors.

## Cold-start contract changes

If a future agent needs to dispatch a #388 rewrite:

1. Use `scripts/dispatch_smart.py architect --agent codex --mode danger --new-branch ... --worktree .worktrees/...` for fresh rewrites (gpt-5.5).
2. Use `scripts/dispatch_smart.py edit --agent codex --mode danger --worktree <existing>` for follow-up fixes on the SAME branch (spark, faster).
3. Brief must reference `scripts/prompts/module-rewriter-388.md` (now includes NO RESTATEMENT).
4. Per-module addenda for sensitive cases: `body_words` cap (5500 default, 5300 for already-padded modules), forbid synthesis sections, curl-verify URLs.
5. After codex done: dispatch gemini review with explicit "read the diff via `gh pr diff <N>`, not the brief description" guard.
6. APPROVE → merge + cleanup worktree + pull main; NEEDS_CHANGES → dispatch a focused fix via `edit` on the same worktree.

## Open items / next session priorities

1. **Backfill batch progress** — running at session end. Check first thing.
2. **#1170** — Option F tracking; calibration step (sample 20 modules for natural body_words) before next 100+ module sweep.
3. **#1143 follow-up** — fix landed (#1164); confirm `ab discuss` is more reliable on next use.
4. **#1144** — branch protection hardening on `main` (not started this session).
5. **Section C harness hardening (focus task #12)** — `pre-tool-use` hooks. Not started; would catch today's branch-in-primary lapse (saved as memory).
6. **Stale git hygiene** — 55 prunable upstream-gone branches + 53 prunable worktrees flagged by `/api/git/cleanup`. Deferred because `git cleanup-merged` alias is `branch -D` based — destructive across worktrees. Cleanup probably wants explicit per-worktree removal.

## Executable smoketests for cold-start

```bash
# Briefing first (canonical)
curl -s http://127.0.0.1:8768/api/briefing/session?compact=1

# Verify NO RESTATEMENT shipped to main
.venv/bin/python -c "from pathlib import Path; t = Path('scripts/prompts/module-rewriter-388.md').read_text(); assert 'NO RESTATEMENT ACROSS H2 SECTIONS' in t; assert 'depth budget, not a quota' in t; print('NO RESTATEMENT contract OK')"

# Verify bridge push-verify fix shipped
grep -A3 "head_before is not None" scripts/agent_runtime/runner.py | head -5

# Check whether backfill batch is still running
/bin/ps aux | grep -E "backfill-pending" | grep -v grep | head -3

# Cold-start safety ritual (per session 4 handoff)
/bin/ps aux | grep -E "dispatch_388_pilot" | grep -v grep | head -3   # should be empty
```

## Cross-references

- Previous handoff: `docs/session-state/2026-05-12-session-4-a4-shipped-and-catchup-bugs.md` (A⁴ shipped, catchup bugs)
- `ab discuss` transcript: `.bridge/messages.db`, channel `padding-constraint-tightening-2026-05-12`, thread `7cd8109a735444c18848bf144d8048e9`
- Issue: #1170 (Option F deferred)
- Decision Card (resolved): `docs/decisions/2026-05-12-readiness-signal-redesign.md` (no longer pending)
