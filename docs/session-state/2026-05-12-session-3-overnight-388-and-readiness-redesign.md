# Session handoff — 2026-05-12 session 3

**Overnight #388 chain ran prereqs (44→merged ~45) + AI phase 15/25. Stopped
cleanly at module boundary at 11:34. Readiness API redesign decided (A⁴
2-bit, frontmatter-canonical), but PRE-REQUISITE work surfaced: backfill
pipeline must (a) write `citations_verified` to frontmatter, and (b)
become part of the per-module chain pipeline. Two GH issues filed.
Auto-merge enabled on repo. Major harness-engineering/Symphony curriculum
gap captured for follow-up.**

## TL;DR for cold-start

1. Hit `curl -s http://127.0.0.1:8768/api/briefing/session?compact=1` first.
2. Chain is stopped cleanly — `module-1.2-what-are-llms` was the last
   completed module. `module-1.3-prompting-basics` and onward are not done.
3. Decision Card at `docs/decisions/pending/2026-05-12-readiness-signal-redesign.md`
   — accepted (A⁴ 2-bit), but user wants **option #2** from the citation
   discussion: integrate `backfill-pending` into the per-module pipeline,
   not just retrofit the readiness API. This is bigger work than A⁴ alone.
4. PR queue: 9 open #388-pilot PRs. 4 from AI phase already merged. Held
   bucket is mix of APPROVE_WITH_NITS (auto-merge candidate when chain
   resumes) and NEEDS_CHANGES (need re-dispatch or fix).
5. Three issues open: #1143 (codex bridge stability), #1144 (branch
   protection hardening), and the pending decision card.

## What shipped this session

### Commits on `main`

| SHA | Subject |
|---|---|
| `8f4f2ca7` | `chore(hygiene): drop phantom Pipeline Supervisor service + archive cleanup` — removed `local_api.py:106` entry that referenced `.pids/pipeline.pid` with no producer. Killed perpetual "Pipeline Supervisor stopped" alert. |
| `53a322c0` | `docs(research): capture Harness Engineering + Symphony gap` — `docs/research/harness-symphony-gap.md`. Curriculum module spec + self-application analysis. Critical caveat: education ≠ Symphony's bad-output-is-cheap regime; 5 excellent beats 55 mediocre. |
| `c3ca83e2` | `chore(388): chain runner + queue files for prereqs → ai → ai/ml-eng` — `scripts/quality/run_388_chain.sh` + 3 queue files (44+25+99=168 modules). |
| `ed7b67bc` (approx, current main) | All NITS PRs from prereqs phase batch-merged in this session. |

Plus **45 module-rewrite merges** from the overnight chain (mostly via
`gh pr merge --squash --delete-branch` direct calls; the chain's
`merge_failed` log entries were almost all actual successes with local
branch-cleanup errors only).

### Artifacts created

- `docs/research/harness-symphony-gap.md` — Lopopolo's harness engineering
  + Symphony post + KubeDojo-specific mapping. Section C is the concrete
  self-application audit; Section C.D codifies "what's NOT adoptable" (no
  auto-merge on module content without cross-family review).
- `docs/decisions/pending/2026-05-12-readiness-signal-redesign.md` — full
  Decision Card with codex audit findings. A⁴ recommended.
- `scripts/quality/{queue-prereqs.txt, queue-ai.txt, queue-ai-ml.txt}` —
  the three chain queues (44 + 25 + 99 modules).
- `scripts/quality/run_388_chain.sh` — sequential phase chainer.
- `scripts/quality/kill_chain_at_boundary.sh` — boundary-kill watcher.
  Fires SIGTERM when current module's verdict event lands AND next
  module's `module_start` is seen. Used 11:34 to stop the chain
  cleanly between AI-phase modules 1.2 and 1.3.
- `~/.claude/projects/.../memory/feedback_ai_gate_is_the_gate.md` — new
  feedback memory. Reflexively asking for "spot-check 2-3 PRs before
  merging" is wrong. AI gate IS the gate; human gate is post-deploy on
  live site.

### GH issues filed

- **#1143 — Codex bridge: skip push-verify when local HEAD didn't move
  during dispatch.** Root cause for codex failing all 3 rounds of the
  readiness `ab discuss`. `scripts/agent_runtime/runner.py:619-626` runs
  `verify_current_branch_pushed` after every danger-mode codex dispatch
  with `parse.ok=True`. Wrong for `ab discuss` consultations where codex
  doesn't commit. ~15 LOC fix.
- **#1144 — Harden branch protection on `main` — required CI + reviews.**
  Companion to auto-merge being enabled. The "AI gate is the gate"
  policy needs to be enforced at the branch level, not just in the
  chain's policy code. Open question: can `gh pr review --approve` from
  a bot identity satisfy required-review rules?

### Repo settings changed

- **Auto-merge enabled** at the repo level (user toggled via UI).
  `allow_auto_merge: true`. Required check + review rules are NOT yet
  configured — that's #1144's scope.

## Where the chain stopped

```
phase=prereqs:   44/44 dispatched, ~30 merged (13 overnight + 32 nits-batch)
                 Some retries inflate the count beyond 44.
                 0 NITS open. 8 NEEDS_CHANGES still open from this phase.

phase=ai:        15/25 dispatched, codex_done 14/15
                 Last completed module: module-1.2-what-are-llms (slug
                 module-1-2-what-are-llms)
                 module-1.3-prompting-basics through module-1.4-trust-boundaries
                 NOT done.
                 4 merged (the "merge_failed" misclassifications).
                 8 NITS-held open.
                 5 NEEDS_CHANGES-held open.
                 (Some events fire multiple times per module; exact module
                 count is in logs/388_chain_2026-05-12_ai.jsonl.)

phase=ai-ml:     NOT STARTED. 99 modules remain in queue-ai-ml.txt.
```

Current `origin/main`: `ed7b67bc` (will move as remaining PRs auto-merge).

## Open PR queue (9 total)

| PR | Module | Verdict |
|---|---|---|
| #1091 | module-1.4-cloud-native-ecosystem (prereqs) | NEEDS CHANGES |
| #1093 | module-1-git-internals (prereqs) | NEEDS CHANGES |
| #1098 | module-5-worktrees-stashing (prereqs) | NEEDS CHANGES |
| #1113 | module-1.3-cicd-pipelines (prereqs) | NEEDS CHANGES |
| #1114 | module-1.4-observability (prereqs) | NEEDS CHANGES |
| #1124 | module-0.2-what-is-a-terminal (prereqs) | NEEDS CHANGES |
| #1125 | module-0.3-first-commands (prereqs) | NEEDS CHANGES |
| #1133 | module-1.2-models-apis-context-structured-output (ai) | NEEDS CHANGES |
| #1142 | module-1.4-human-in-the-loop-habits (ai) | NITS or NEEDS — verify |

All have CI=SUCCESS. None have human spot-checks because **per
`feedback_ai_gate_is_the_gate.md`, spot-checking is not part of the
workflow** — human gate happens on the live site post-deploy.

## Key decisions made

### D1 — Readiness signal redesign (A⁴, with caveat #2 modification)

**Architecture:** `/api/tracks/readiness` becomes FS-derived from
frontmatter on `main`. Drops `.pipeline/v2.db` dependency.

**Predicate (final, after user accepted option #2 from the citation
discussion):**

```python
cleared := fm.get("revision_pending") is not True \
        AND fm.get("citations_verified") is True
```

**The implementation order matters** because A⁴ as designed requires
prerequisite patches:

1. **`backfill-pending` must write `citations_verified: true` to module
   frontmatter** (currently writes to `.pipeline/quality-pipeline/<slug>.json`
   sidecar only). Add `set_citations_verified_frontmatter()` helper in
   `scripts/quality/queue.py` parallel to `set_qa_pending_frontmatter` at
   `:362`. Call from `_backfill_one` after successful `inject`.
2. **Make `backfill-pending` part of the per-module chain pipeline.**
   `dispatch_388_pilot.py` currently runs codex write → review → merge,
   then moves to next module. Add a backfill step before "next module"
   so each merged module has its citations actually verified before
   counting as done.
3. **Run backfill on the 45 already-merged historical modules.** They
   currently have `revision_pending: false` but no `citations_verified`
   field. They'd show as uncleared under A⁴. One-time catchup batch.
4. **Then implement the readiness API change.** `~80-120 LOC` if
   prerequisites are done.

**Codex audit findings (file:line citations preserved):**
- `cmd_backfill_pending` entry: `scripts/quality/pipeline.py:500` →
  `_backfill_one` ~`:422-477`.
- `citation_backfill.py inject` explicitly never modifies frontmatter
  (`:1251`); mechanical write at `:1853` is `module_path.write_text(new_body)`.
- Cleanup path REMOVES `revision_pending` rather than setting false
  (`scripts/quality/queue.py:381`). **Predicate must use `is not True`,
  NOT `== False`.**
- Replacement handler: reuse `_iter_en_modules`, `_track_for_key`,
  `_section_for_key`. Parse frontmatter with `status._extract_frontmatter`
  (`scripts/status.py:172`).
- Cache version pattern from `_v_quality_board` (`local_api.py:8534`)
  applies to `_v_docs_frontmatter`.
- Tests: current `tests/test_local_api.py:3001-3134` are v2.db-shaped
  and need full rewrite around frontmatter combos.

### D2 — AI gate is the gate

User correction this session, durable rule. The AI-driven review chain
(codex writer + cross-family reviewer + density verifier) IS the
production gate. No reflexive "spot-check 2-3 first" before batch-merging.
Human gate happens post-deploy on the live site. Filed as
`feedback_ai_gate_is_the_gate.md`.

### D3 — Single cross-family reviewer per #388 PR

User confirmation: one reviewer is enough for #388. Dual review is
reserved for #394 AI history chapters per `feedback_dual_review_required.md`.
Gemini primary (when quota), Claude fallback (when Gemini 503s/quota).

### D4 — Auto-merge enabled on repo

User toggled via UI. Companion hardening (#1144) needs follow-up but is
not blocking.

## Critical context — citation gate gap

This is the meatiest finding of the session and the most important to
absorb in the next session.

**Tonight's 45 merged modules have NEVER had citation backfill run on
them.** The pre-merge review checks URL shape only ("eyeball it, flag
obvious dead URLs"). The Citation Gate (fetch URL, parse content, verify
support) is explicitly DEFERRED to `scripts.quality.pipeline backfill-pending`
per `docs/quality-rubric.md:17`. It hasn't run.

This means:
- If codex hallucinated a URL (a known failure mode for both Codex and
  Gemini per `feedback_gemini_hallucinates_anchors.md`), it's live on
  `main`.
- The dashboard, once A⁴ ships, will correctly show these as **uncleared**
  until backfill runs.
- "5 excellent beats 55 mediocre" — currently we have 45 modules whose
  citation quality is unverified. They are NOT "excellent" by the
  rubric's own standard.

The user's choice: **option #2** — make backfill part of the per-module
pipeline going forward, and run a one-time catchup on the 45 historical
merges. This is the meat of next session.

## Plan for next session, in priority order

1. **Triage the 9 open NEEDS_CHANGES PRs.** Some are likely
   re-dispatchable (reviewer feedback gives concrete fixes). Others may
   be process-level issues (e.g., gemini hallucination). Decide:
   re-dispatch via codex with the review feedback as input, or close +
   manually fix.
2. **Implement the prereq patches for A⁴:**
   - `set_citations_verified_frontmatter()` helper in `scripts/quality/queue.py`
   - Call from `_backfill_one` in `scripts/quality/pipeline.py`
   - **Decision needed:** if `inject` returns `nothing_to_do`, is that
     "verified" or "not run"? Codex flagged this at `:469`.
3. **Add backfill step to `dispatch_388_pilot.py` per-module loop.**
   After successful merge, dispatch backfill for that module before
   moving to next. Estimate +2-5 min/module to chain throughput.
4. **Run backfill on 45 already-merged modules.** One-time catchup.
   Could be a separate script or part of pipeline restart.
5. **Implement A⁴ readiness API** in `scripts/local_api.py` (replace
   `build_tracks_readiness` and drop the v2.db reducer glue). Estimate
   60-90 LOC + cache version + tests.
6. **Filter queue files** to drop modules where `revision_pending` is
   already absent on main. Avoids re-dispatching done work when chain
   restarts.
7. **Restart chain** on the filtered queues (AI phase remainder + AI/ML
   Engineering full).
8. **#1143 — fix codex bridge push-verify gate.** 15 LOC. Important for
   future `ab discuss` reliability.
9. **#1144 — branch protection hardening.** Open question: can AI
   reviews satisfy required-review rule? Investigate.
10. **Harness/Symphony curriculum** — modules in `ai/ai-native-work` for
    harness engineering + Symphony (B in `harness-symphony-gap.md`).
    After all the above.
11. **Self-application audit** — KubeDojo's harness-engineering current
    state vs the seven principles (C in `harness-symphony-gap.md`). `ab
    discuss` first per the gap doc.

## What NOT to do next session

- **Don't reflexively spot-check PRs before merging.** AI gate is the
  gate (`feedback_ai_gate_is_the_gate.md`).
- **Don't run `ab discuss` while the chain is pushing PRs.** Codex's
  push-verify check races against concurrent `origin/main` movement
  (this is #1143). Workaround until #1143 lands: dispatch codex via
  `dispatch_smart.py architect --agent codex --worktree <path>` directly,
  bypassing the bridge's `discuss` mechanism.
- **Don't ship A⁵ single-bit** (just `revision_pending`). It would lie
  about the gate — modules without verified citations would show as
  cleared. User explicitly chose option #2 (full gate, backfill in
  pipeline).
- **Don't auto-merge module-content PRs without cross-family review.**
  Even with repo auto-merge enabled. The chain's policy is
  `dispatch_388_pilot.py` decides verdicts — the chain still gates
  merges by verdict.

## Open environmental questions

- **Pipeline_v2 status (GH #375).** This session didn't touch it.
  Readiness redesign decouples from v2.db; v2 itself still needs the
  rebuild-or-retire decision. `ab discuss` first per the issue.
- **Gemini account rotation.** User downgraded to AI Pro tier; rotates
  3 family accounts manually. Tonight: gemini failed reviews → claude
  fallback throughout. Rotation didn't help once the daily quota hit.
  Possible follow-up: a `⚠ ROTATE GEMINI` console marker that pauses
  the chain on 3 consecutive Gemini failures. Lower priority than the
  citation-gate work.
- **Pipeline supervisor reference removed but `dispatch_388_pilot.py`
  doesn't yet write to `.pipeline/v2.db`.** When A⁴ lands and the
  readiness API stops reading v2.db, the v2 workers (write/review/patch)
  become disconnected from the dashboard. This is fine — those workers
  are batch-driven, started only when running pipeline_v2 explicitly.
  Just be aware.

## File path quick reference

- Chain logs: `logs/388_chain_2026-05-12.log` (phase markers),
  `logs/388_chain_2026-05-12_{prereqs,ai,ai-ml}.jsonl` (per-module events).
- Watcher log: `logs/kill_watcher_2026-05-12.log`.
- Chain artifacts: `scripts/quality/{run_388_chain.sh, kill_chain_at_boundary.sh, queue-*.txt}`.
- Pilot dispatcher: `scripts/quality/dispatch_388_pilot.py`.
- Rewriter prompt: `scripts/prompts/module-rewriter-388.md`.
- Readiness handler (current, soon replaced): `scripts/local_api.py:4026-4135` + v2 glue `:3546-3680`.
- Backfill: `scripts/quality/pipeline.py:500` (`cmd_backfill_pending`).
- Frontmatter helpers: `scripts/quality/queue.py:362` (`set_qa_pending_frontmatter` — model for the new helper).
- Decision Card: `docs/decisions/pending/2026-05-12-readiness-signal-redesign.md`.
- Harness/Symphony gap: `docs/research/harness-symphony-gap.md`.

## Predecessor context

Previous handoff:
`docs/session-state/2026-05-12-codex-resume-output-flags.md` — covers PR
#1087 (codex resume cmd flags fix, merged `d6118c80`). That work is done;
the remaining smoketest is folded into #1143's scope (separate but
related codex bridge work).
