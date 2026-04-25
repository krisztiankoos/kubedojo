# Session Handoff — 2026-04-25 — #378 batch failure + recovery plan

## Decisions made this session (sticky)

- **Codex always writes content; claude codes + reviews; gemini audits/cites/tiebreaks.** Even/odd alternation retired. Commit `b0103abe`. Memory: `feedback_writer_reviewer_split.md`.
- **Claude owns pipeline mutations end-to-end.** Default `--workers 1`. Stream progress. Recover SIGINT-killed modules. Memory: `feedback_claude_owns_pipeline.md` (supersedes the older "user runs pipeline mutations" rule for pipelines specifically).
- **No personal-life framing in plans/tickets/commits.** Memory: `feedback_no_personal_framing.md`. Epic #376 + tickets #378/#379 already scrubbed.

## Contract changes shipped this session

| Change | Commit | Purpose |
|---|---|---|
| `writer_for_index` returns `("codex","claude")` for every index | `b0103abe` | Retire alternation — claude lands ~440-line modules vs codex's 1500-2000+ |
| `scripts/quality/gates.py` — visual-aid hard gate, deterministic 20% gemini sampler, fcntl-locked TSV ledger | `7f4ff4d4` | #377 prerequisite. Hard gate wired into `merge_one` before ff-merge. |
| Post-merge sampler + ledger wired into `merge_one` | `4ef2274f` | Auto-fires on every COMMITTED transition. |
| `audit_teaching_quality.py` prompt template moved from `/tmp/kd_audit_prompt.md` to `scripts/prompts/audit_teaching.md` | `4abd1f80` | Survive reboots; in-repo, version-controlled. |
| `docs/quality-progress.tsv.lock` gitignored | (see commit chain at handoff time) | Stop the ledger lock from dirtying primary mid-batch (root cause of 9.3 merge fail). |

## What just failed and why

User triggered `pipeline run --workers 3 --only <12 MLOps slugs>` from a command I prepared. Outcome:

| Status | Count | Modules |
|---|---|---|
| FAILED — merge blocked because primary dirty | 1 | 9.3 (write+review APPROVED 4.8 — ready to merge, blocked by `docs/quality-progress.tsv` being untracked) |
| FAILED — SIGINT mid-dispatch (rc=-2 KeyboardInterrupt) | 5 | 5.1, 9.1, 9.2, 9.4, 9.5, 9.6 |
| Worktree standing — CITATION_VERIFY | 2 | 5.2, 5.3 |
| Worktree standing — WRITE_IN_PROGRESS | 1 | 5.4 |
| UNAUDITED (never picked up by the run) | 2 | 5.5, 5.6 |

Diagnostics: `.pipeline/quality-pipeline/diagnostics/<slug>.write.*.failed.json`. Confirmed rc=-2 = `KeyboardInterrupt` from user signal.

**Root causes (both mine, now fixed):**

1. The `_post_merge_gates` ledger creates `docs/quality-progress.tsv` + `.tsv.lock` on first merge. Both were untracked → `has_uncommitted(primary)` returned true → next merge in the batch was refused. Fixed by gitignoring the `.lock`; the `.tsv` itself is committed as the audit trail.
2. Handed the user a `--workers 3` command and walked away with no progress monitoring. Memory `feedback_batch_worker_cap.md` says default 1, ramp to 3 only after a clean batch. I should not have offered 3 cold. New rule (`feedback_claude_owns_pipeline.md`) closes that gap.

## Current state on disk

- Branch: `main`, ahead of origin by ~14 commits.
- Worktrees still standing (3): `quality-platform-disciplines-data-ai-mlops-module-5.{2,3,4}-*` — these still hold the in-flight rewrites; not abandoned, can be resumed.
- `.pipeline/teaching-audit/` has all 12 MLOps audit JSONs (gemini, real-LLM scores).
- `docs/quality-progress.tsv` exists with one row from 9.4 (the cleanup-only that completed before 9.3 broke merge).

## Smoketests (cold start verification)

```bash
# 1. Repo is clean.
git status --short
# Expected: empty after handoff commit.

# 2. Quality test suite green.
.venv/bin/pytest tests/test_quality_gates.py tests/test_quality_dispatchers.py tests/test_quality_stages.py -q
# Expected: 85 passed.

# 3. Audit prompt template resolves from repo, not /tmp.
.venv/bin/python -c "from scripts.audit_teaching_quality import PROMPT_TEMPLATE; assert PROMPT_TEMPLATE.exists(), PROMPT_TEMPLATE; print('ok:', PROMPT_TEMPLATE)"

# 4. Gates CLI works.
.venv/bin/python -m scripts.quality.gates should-sample --slug test-1 --sample-rate 0.5

# 5. Visual-aid count on a real module.
.venv/bin/python -c "from pathlib import Path; from scripts.quality.gates import visual_aid_count; print(visual_aid_count(Path('src/content/docs/ai-ml-engineering/mlops/module-1.1-ml-devops-foundations.md').read_text()))"
```

## Recovery plan (next concrete actions)

1. **Tear down the 3 standing worktrees** so the recovery starts from a clean primary:
   ```bash
   for slug in platform-disciplines-data-ai-mlops-module-5.2-feature-stores \
               platform-disciplines-data-ai-mlops-module-5.3-model-training \
               platform-disciplines-data-ai-mlops-module-5.4-model-serving; do
     git worktree remove --force ".worktrees/quality-${slug}" 2>/dev/null
     git branch -D "quality/${slug}" 2>/dev/null
   done
   ```

2. **Reset the 6 FAILED state files** back to a non-terminal stage so the run picks them up. SIGINT-killed modules go to `WRITE_PENDING`; the merge-blocked 9.3 (write done, review approved) goes to `REVIEW_APPROVED`:
   ```python
   # claude does this inline in next session — see scripts/quality/state.py:transition()
   ```
   Specific resets:
   - 5.1, 9.1, 9.2, 9.4, 9.5, 9.6 → `WRITE_PENDING` (SIGINT during write/review/citation)
   - 9.3 → `REVIEW_APPROVED` (work done; only merge needs to retry — and the gitignore fix unblocks it)

3. **Pre-flight checks** (per `feedback_claude_owns_pipeline.md`):
   ```bash
   git status --short                                   # must be empty
   .venv/bin/python scripts/dispatch.py codex "say hi" --timeout 30
   git worktree list                                    # only primary expected
   ```

4. **Re-run the 12 with workers=1, streaming to a log AND visible in the chat:**
   ```bash
   .venv/bin/python -m scripts.quality.pipeline run --workers 1 --only \
     platform-disciplines-data-ai-mlops-module-5.1-mlops-fundamentals \
     platform-disciplines-data-ai-mlops-module-5.2-feature-stores \
     platform-disciplines-data-ai-mlops-module-5.3-model-training \
     platform-disciplines-data-ai-mlops-module-5.4-model-serving \
     platform-disciplines-data-ai-mlops-module-5.5-model-monitoring \
     platform-disciplines-data-ai-mlops-module-5.6-ml-pipelines \
     on-premises-ai-ml-infrastructure-module-9.1-gpu-nodes-accelerated \
     on-premises-ai-ml-infrastructure-module-9.2-private-ai-training \
     on-premises-ai-ml-infrastructure-module-9.3-private-llm-serving \
     on-premises-ai-ml-infrastructure-module-9.4-private-mlops-platform \
     on-premises-ai-ml-infrastructure-module-9.5-private-aiops \
     on-premises-ai-ml-infrastructure-module-9.6-high-performance-storage-ai \
     2>&1 | tee .pipeline/runs/$(date +%Y%m%d-%H%M%S)-378-batch.log
   ```
   At workers=1 sequential, ~1.5–2 hours wall-time for 8 rewrites + 4 cleanup-only. Claude monitors stage transitions every ~60s and surfaces every `[ok]`/`[fail]` to the operator.

5. **After the batch lands**: verify `docs/quality-progress.tsv` got 12 rows; sample 2-3 modules from the rewritten 8 to spot-check the codex output stayed within the visual-aid gate; close ticket #378 with the audit-score deltas.

## Open epic-level decisions (still unresolved from the original plan)

- Budget cap per phase (codex 10x window ends 2026-05-17).
- Lab audit start date (#386 / Phase F).

## Memory pointers added/updated this session

- `feedback_writer_reviewer_split.md` (new)
- `feedback_no_personal_framing.md` (new)
- `feedback_claude_owns_pipeline.md` (new — partially supersedes `feedback_no_run_scripts.md` for pipeline mutations)
- `project_topical_gap_analysis.md` (scrubbed for personal framing)

## Cold-start one-liner

> Read `MEMORY.md` → read `STATUS.md` → read this handoff (`docs/sessions/2026-04-25-handoff-378-failed-batch.md`) → run smoketests above → execute recovery plan steps 1–5.
