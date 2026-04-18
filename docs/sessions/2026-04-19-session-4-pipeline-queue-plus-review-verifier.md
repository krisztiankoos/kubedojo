# Session Handoff — 2026-04-18/19 Session 4 — Pipeline Queue + Universal Review Verifier

## Cold start (next session, read first)

```bash
bash scripts/cold-start.sh                                   # services-up + compact briefing
gh pr list --repo kube-dojo/kube-dojo.github.io --author @me # in-flight PRs (should be 0)
bash scripts/ops/smoketest_ab_workspace_write.sh             # bridge default guard
```

Session 4 ended with a clean main, zero open PRs, and the full review-verifier + anti-hallucination protocol on main. Next session starts from a quiet state.

## Novel info (not derivable from briefing / git / PR list)

1. **Review verifier is now live**: `scripts/verify_review.py` parses FINDING blocks from any reviewer's output and grep-checks every `CURRENT CODE` quote against the branch file. Three outcomes: `verified` / `line_mismatch` / `quote_missing`. Warn-only (exit 1 on quote_missing, never blocks merge). Use it whenever a reviewer's finding looks suspect.
2. **Gemini defaults to Pro for reviews**: `scripts/dispatch.py gemini --review` now auto-picks `gemini-3.1-pro-preview` via `GEMINI_REVIEW_MODEL`. Override with `--model gemini-3-flash-preview` if you explicitly want Flash. Flash hallucinated "missing" code on #309 and #320 (both turned out to be present); Pro's first live test on #321 was clean.
3. **`--review` flag has parity across bridge routes**: `ask-gemini`, `ask-codex`, `ask-claude` all accept `--review`. Each prepends the canonical protocol from `docs/review-protocol.md` via `ai_agent_bridge._prompts.build_review_message()`. Any agent can now review any other agent's work using the same contract.
4. **`CODEX_BRIDGE_MODE=danger` is needed more often than the default suggests**: workspace-write blocks both `.git/refs/*` (worktree creation fails) AND network (`gh` fails). Use `danger` for any dispatch that needs to push or call gh. The #308 first-attempt failure was exactly this.
5. **Codex meta-reply pattern has a reliable fix**: when Codex sends "I would do X" instead of executing, re-dispatch with explicit shell commands and a required response format ("End with: 'PR <url> opened, tests pass.' OR 'Blocked — <reason>'"). Worked first-try on #279c retry.
6. **Codex 900s timeout salvage**: if Codex times out after the code is done but before commit/push/PR, the worktree usually holds finished work. Run tests locally; if green, commit+push+open-PR yourself with Codex co-author. Saved PR #320 that way.
7. **Delegation discipline feedback**: user called out (verbatim: "WHY ARE YOU SO STIUBBBORN") that iteration fixes of ~20 LOC should be done inline, not dispatched through Codex. Bridge stays free for fresh work. Codex for new implementations + audits; Claude for iteration fixes.
8. **Dispatch from primary cwd, not from worktrees**: running `scripts/dispatch.py` from a worktree that later gets deleted crashes log writes. Always `cd` back to primary before backgrounding a dispatch.
9. **The live quality scorer from #304 is reality, the frozen markdown audit is not**: do not trust `docs/quality-audit-results.md` (2026-04-03 snapshot). The four "critical" modules it flagged (CKA 2.8, KCNA 3.6/3.7/4.3) now score 4.2-5.0 live. The real critical list is in `GET /api/quality/scores` — currently 7 modules <2.0 (see "Side lane for user" below).

## Decisions waiting on you

None that block the next session. Queue below is all dispatch-ready.

## PR stack — what landed in session 4

All merged, main clean:

| Issue | PR | Scope |
|-------|----|-------|
| #306 | #307 | FACT_CHECK unverified routes to rejection + API/dashboard surfacing |
| #308 | #309 | v2 audit bridge to `.pipeline/reviews/*.md` (with header-preservation fix) |
| #279a | #310 | WRITE-time citation seed injection (including rewrite branch) |
| #279b | #312 | Citation gate between WRITE and REVIEW with 3-strike rollback |
| #279c | #314 | CITE binary review check (7th gate) |
| #243 | #320 | Translation v2 per-track health + lab metadata parity |
| (infra) | #321 | Universal review protocol + verifier, ask-* `--review` parity, Pro default |

**Issues closed as parents**: #217 (Pipeline v3), #239 (v2 budget queue), #279 (citation pipeline), #303 (old scorer obsolete).

## Queue — session 5 picks up here (in priority order)

1. **#277** — `/api/build/run` + `/api/build/status` endpoints. Spec on issue. Clear, ~100-150 LOC. Prompt drafted at `/tmp/277-prompt.md` (will need re-drafting in session 5 since `/tmp` doesn't survive).
2. **#258** — Local API audit + cold-start cost reduction. Broad scope; first dispatch should ask Codex for a split plan, not implement.
3. **#248** — Review Batch tracking issue. Content already on main; probably closable after quick triage.
4. **#319** — Remove legacy AUDIT compat shims. ~30-50 LOC, LOW priority.
5. **#311** — Finish factoring `append_review_audit` out of `v1_pipeline.py`. Deferred from #309. ~120 LOC.
6. **#313** — Regenerate AI foundations 1.1/1.2/1.3 via citation-aware pipeline. DEPENDS on user enqueueing them; see side-lane below.
7. **#315–#318** — Pipeline v2 follow-ups (check-worker + ledger-worker, rate-limit parity, observability, immutable attempts + routing config). Each is a separate dispatch.

## Side lane — user actions

### Enqueue critical-quality modules

The 7 modules currently <2.0 on `GET /api/quality/scores`. Hold off until #315 lands for cleaner worker separation, OR enqueue now if you want them processing in the background:

```bash
for path in \
  src/content/docs/k8s/cks/part1-cluster-setup/module-1.2-cis-benchmarks.md \
  src/content/docs/k8s/cks/part2-cluster-hardening/module-2.2-serviceaccount-security.md \
  src/content/docs/k8s/cks/part6-runtime-security/module-6.4-immutable-infrastructure.md \
  src/content/docs/k8s/cgoa/module-1.1-exam-strategy-and-blueprint-review.md \
  src/content/docs/k8s/cgoa/module-1.2-gitops-principles-review.md \
  src/content/docs/k8s/cgoa/module-1.3-patterns-and-tooling-review.md \
  src/content/docs/platform/foundations/distributed-systems/module-5.1-what-makes-systems-distributed.md; do
  scripts/pipeline enqueue "$path" --phase write --model gemini-3.1-pro-preview --priority 100
done
scripts/pipeline status
```

Memory rule `feedback_no_run_scripts` says pipeline mutations are user-only; hence this lives in the handoff, not in Claude-automation.

### Triage 2 dead-letter translation modules

From `GET /api/translation/v2/status`:
- `platform/foundations/distributed-systems/module-5.1-what-makes-systems-distributed` → dead-letter
- `platform/foundations/distributed-systems/module-5.3-eventual-consistency` → dead-letter

Inspect the review log for each with `GET /api/reviews?module=<key>` and decide: requeue, manually fix, or accept the dead-letter.

## Incomplete / untouched

- None blocking. The queue above is prioritized but nothing is mid-flight.
- `docs/quality-audit-results.md` is stale (superseded by `/api/quality/scores`). Low priority to add a "superseded" note at the top.
- `.pipeline/spec-v2-pipeline.md` still describes the full pipeline design; #315–#318 are the remaining gaps.
