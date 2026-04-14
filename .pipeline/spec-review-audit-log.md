# Spec v2: Per-Module Review Audit Log

*Revised after design review by Codex and Gemini (2026-04-14).*

## Problem

The v1 pipeline runs multiple review passes per module (REVIEW, integrity gate, CHECK, fact ledger) but the feedback is scattered across:
- `.pipeline/logs/run_*.log` — time-ordered, not indexed by module
- `state.yaml` — stores `severity`, `checks_failed`, `reviewer` but not full feedback text
- Staging files — short-lived, deleted on success

Result: no way to audit a module's quality history. "Why did module X get rewritten 4 times?" requires grepping 300MB of logs across multiple runs.

## Goal

For every module, produce a persistent, human-readable audit trail of every pipeline pass — who reviewed it, what they said, what failed, what changed.

## Design

### Storage: per-module markdown files

Path: `.pipeline/reviews/{module_key_sanitized}.md`

- `module_key_sanitized` = same sanitization as fact ledger (`/` → `__`)
- One file per module, prepended on each pipeline pass (reverse-chronological)
- Committed to git alongside module changes on successful pass (so review history is versioned with content)

### Event taxonomy (single canonical model)

**One entry per significant phase transition**, not per step. Emission responsibility lives in `run_module` orchestration, not in `step_write`/`step_review`/`step_check` helpers (those return payloads for the orchestrator to log).

| Event | When emitted | Phase transition |
|-------|--------------|------------------|
| `WRITE` | After `step_write` returns successfully | pending/audit → write, or write retry |
| `REVIEW` | After `step_review` returns a verdict (includes `verdict` field: APPROVE or REJECT) | review → check / write |
| `INTEGRITY_FAIL` | Only if integrity gate fails (passes are not logged) | review → write (severe) |
| `CHECK_FAIL` | Only if deterministic checks fail | check → write |
| `CHECK_PASS` | After successful deterministic checks | check → score |
| `DONE` | After successful SCORE + commit | score → done |
| `RESET` | When `cmd_reset_stuck` clears errors | varies → pending/write |
| `MANUAL_OVERRIDE` | Reserved for future human override CLI | any → specified |

Note: `APPROVE`/`REJECT` is a field on `REVIEW`, not a separate event (resolves Codex's taxonomy concern).

### Skipped cases (no audit entry)

- `dry_run=True` — no audit writes
- `write_only=True` — log WRITE only (no REVIEW/CHECK)
- Reviewer rate-limited and fallback succeeds — log REVIEW with `reviewer_fallback_used: true`
- Reviewer rate-limited and all tiers fail — log REVIEW with `verdict: FAILED`

### File format

```markdown
# Review Audit: {module_key}

**Path**: `src/content/docs/{path}`
**First pass**: 2026-04-14T09:00:00Z
**Last pass**: 2026-04-14T18:45:00Z
**Total passes**: 5
**Current phase**: done
**Current reviewer**: gemini-3.1-pro-preview
**Current severity**: clean

---

## 2026-04-14T18:45:00Z — `DONE`

Module passed all gates and committed.

**Pass sum**: 40/40 (binary gate: clean)
**Reviewer**: gemini-3.1-pro-preview
**Duration (phase)**: 2s

---

## 2026-04-14T18:45:00Z — `CHECK_PASS`

Deterministic checks passed after review APPROVE.

**Duration**: 1s
**Warnings**: 2 (LINE_COUNT, CODE_LANG)

---

## 2026-04-14T18:44:55Z — `REVIEW` — `APPROVE`

**Reviewer**: gemini-3.1-pro-preview
**Attempt**: 3/5
**Severity**: clean
**Duration**: 45s

**Checks**: 7/7 passed (COV QUIZ EXAM DEPTH WHY PRES LAB)

**Feedback**:
> The module is now well-structured with clear learning outcomes, excellent LAB execution steps, and robust quiz scenarios. All prior concerns addressed.

---

## 2026-04-14T18:30:00Z — `REVIEW` — `REJECT`

**Reviewer**: gemini-3.1-pro-preview
**Attempt**: 2/5
**Severity**: targeted
**Duration**: 38s

**Checks**: 6/7 passed (COV QUIZ EXAM DEPTH WHY PRES) | **Failed**: LAB

**Failed check evidence**:
- **LAB**: The 'STOP: Time to Practice!' section lacks step-by-step execution commands, environment setup, and checkpoint verifications.

**Feedback**:
> The theoretical content and scenario-based quizzes are excellent. However, the LAB section needs concrete commands rather than open-ended references to external scripts.

**Edits applied**: 1/1 structured edits landed (deterministic, no LLM writer call)

---

## 2026-04-14T09:00:00Z — `WRITE`

**Writer**: gemini-3.1-pro-preview
**Mode**: initial write
**Plan**: Standard module structure (initial write plan, 120 chars)
**Output**: 34988 chars
**Duration**: 4m 33s
```

### Header update rules

- Header is **always** rewritten to reflect current state (atomic read-prepend-write)
- Header fields mirror `ms["phase"]`, `ms["reviewer"]`, `ms["severity"]` from state.yaml
- `Total passes` = count of all entries below the `---` divider
- `First pass` = earliest timestamp; `Last pass` = newest

### Ordering

**Reverse-chronological** (newest first, like a changelog). Header on top, then most recent entry, then older entries below.

### Concurrency

- **Per-file OS-level lock** via `fcntl.flock` on a sibling `.lock` file (same pattern as `save_state`)
- Works across processes (parallel mode + multiple pipeline instances)
- In-process `threading.Lock` NOT sufficient (per Codex)

### Atomic writes

Use existing `_atomic_write_text` helper. Read-prepend-write pattern:
1. Acquire `fcntl.flock` on `.lock` file
2. Read existing `.md` file (if exists)
3. Build new content: header + new_entry + existing_body
4. Write to `.tmp` file
5. `tmp.replace(target)` (atomic on POSIX)
6. Release flock

### Integration points in v1_pipeline.py

New helper: `append_review_audit(module_path, event, **fields)` in `v1_pipeline.py`.

Called ONLY from `run_module` orchestration and `cmd_reset_stuck`:
- After `step_write` succeeds → `append_review_audit(path, "WRITE", writer=..., duration=..., plan=...)`
- After `step_review` returns → `append_review_audit(path, "REVIEW", verdict=..., reviewer=..., ...)`
- After integrity gate fails → `append_review_audit(path, "INTEGRITY_FAIL", errors=...)`
- After CHECK fails → `append_review_audit(path, "CHECK_FAIL", failed_checks=...)`
- After CHECK passes → `append_review_audit(path, "CHECK_PASS", warnings=...)`
- After SCORE commits → `append_review_audit(path, "DONE", reviewer=..., pass_sum=...)`
- In `cmd_reset_stuck` → `append_review_audit(path, "RESET", cleared_errors=..., new_phase=...)`

### Git behavior

- Audit file is staged in the **same commit** as the module change on DONE
- On intermediate phases (rejects, retries), audit file is updated but NOT committed separately (will be committed with next successful pass or with a manual flush)
- On `cmd_reset_stuck` → commit `"chore(pipeline): reset stuck modules [audit log]"` with all updated audit files

### Gitignore

Do NOT ignore `.pipeline/reviews/`. Commit review history alongside content changes.

### Size management

- Estimate: 816 modules × avg 5 passes × ~1.5 KB per entry = ~6 MB total. Acceptable for git.
- No rotation needed for v1.
- Future: `--prune-reviews N` flag to keep last N entries per file.

## Acceptance Criteria

### Functional
- [ ] Every WRITE, REVIEW, INTEGRITY_FAIL, CHECK_FAIL, CHECK_PASS, DONE, RESET event creates an audit entry in `.pipeline/reviews/{module_key_sanitized}.md`
- [ ] Entries are reverse-chronological (newest first)
- [ ] File header shows: path, first/last pass timestamps, total passes, current phase, current reviewer, current severity
- [ ] Full reviewer feedback text is captured verbatim (not truncated)
- [ ] Failed check IDs + evidence captured
- [ ] Audit files committed with module changes on DONE
- [ ] `dry_run=True` produces NO audit entries
- [ ] `write_only=True` produces WRITE entries only

### Quality
- [ ] `append_review_audit()` uses `fcntl.flock` for cross-process safety
- [ ] `_atomic_write_text` used for all writes
- [ ] Reading-prepending-writing the file doesn't corrupt existing entries under concurrent access
- [ ] UTF-8 safe for all reviewer content
- [ ] No duplicate entries across resume/retry paths (emission is idempotent per phase transition)

### Testing
- [ ] Unit test: `append_review_audit()` creates new file with correct header + entry
- [ ] Unit test: second call prepends entry, preserves existing entries
- [ ] Unit test: header is updated with each append (current phase, timestamps, count)
- [ ] Unit test: concurrent writes from 5 threads don't corrupt file
- [ ] Unit test: `dry_run=True` doesn't create any file
- [ ] Integration test: full pipeline run (write → review → check → done) produces complete audit for one module with 4 entries
- [ ] Integration test: reset-stuck produces RESET entries with cleared errors

### Backwards compatibility
- [ ] No migration needed — existing modules without audit files are fine, files created on next pipeline run
- [ ] Old state.yaml entries work unchanged

## Non-Goals (v1)

- Not a replacement for `.pipeline/logs/run_*.log` (still needed for time-ordered debugging)
- Not for real-time monitoring (static files, not a dashboard)
- Not structured data (markdown only, no JSON/YAML variant)
- No LLM cost tracking (unreliable per Codex; duration per entry is sufficient)
- No git commit SHA per entry (SHA doesn't exist at audit-write time; add later if needed for DONE events)

## Decisions (was Open Questions)

1. **Prompt text logging**: Log plan (first 500 chars + "..." if longer). Do NOT log full writer prompt.
2. **RESET event content**: Include full cleared error list + resulting phase.
3. **LLM time tracking**: Per-entry `Duration` field only. No cumulative header field.
4. **Commit SHA**: Not included in v1 (not available at write time). Reconsider for DONE events in v2.
5. **MANUAL_OVERRIDE**: Reserved event type, not implemented in v1. Added when human override CLI lands.

## Design Review Sign-Off

- [x] Codex reviewed design (2026-04-14) — flagged event taxonomy, emission point, locking scope. All addressed in v2.
- [x] Gemini reviewed design (2026-04-14) — suggested commit SHA, MANUAL_OVERRIDE, LLM cost. Taxonomy unchanged. Gemini's MANUAL_OVERRIDE added to event list; commit SHA and LLM cost deferred per Codex rationale.
