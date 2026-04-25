# 2026-04-24 — v2 quality pipeline first-real-module smoke handoff

**State on handoff**: v2 pipeline ran end-to-end on `k8s-capa-module-1.2-argo-events` four times. Three real bugs surfaced and were fixed. One issue remains (write-retry hang). 5 of 6 stages validated. **18 commits ahead of `origin/main` on `main`. Primary clean. Not pushed. 152 quality tests, ruff clean.**

**Tracking**: [#375](https://github.com/kube-dojo/kube-dojo.github.io/issues/375). Prior handoff: [`2026-04-24-v2-implementation-handoff.md`](2026-04-24-v2-implementation-handoff.md).

## Cold-start

```bash
# 1. Confirm green
curl -s http://127.0.0.1:8768/api/briefing/session?compact=1 | head -40
.venv/bin/python -m pytest tests/test_quality_*.py -q              # expect 152 passed
git log --oneline origin/main..HEAD | wc -l                        # expect 18

# 2. Read this doc + the autopsy table in STATUS.md.

# 3. Open the diag artifacts to see what's already known about the hang.
ls .pipeline/quality-pipeline/k8s-capa-module-1.2-argo-events.write.*.failed.json
# .write.36654ecb2e86.failed.json — round-4 retry hang (narrow disallow, 0B)
# .write.d42d847f1341.failed.json — round-2 wide-disallow hang (different cause)

# 4. Pick a fix from the plan below.
```

## What works (smoke-validated)

End-to-end mechanics that shipped clean across rounds 3 and 4:

- Audit promotion (cached `.pipeline/teaching-audit/<slug>.json` is reused — bootstrap is idempotent)
- Route (score 3.8 < 4.0 → `track=rewrite`, `writer=claude`, `reviewer=codex`)
- Worktree create, claude writer dispatch with `--no-tools` narrow list
- Module extraction (`extract_module_markdown`) — strips claude's prose preamble and recovers an 80 KB module
- Worktree commit (`07dd4678` in round 4 write 1)
- Citation_verify (writer didn't emit `## Sources` per the rewrite prompt — `had_sources=false`, kept=0/removed=0, clean transition)
- Cross-family review dispatched to codex (CLI + sandbox + verdict-JSON parsing all work)
- Verdict parsing — `changes_requested` with 3 must-fix items captured into state
- `REVIEW_CHANGES` → `WRITE_PENDING` retry routing — `retry_count=1` of cap 2
- Worktree + branch teardown on FAILED — round-5 ownership-invariant fix held under both real failure paths (`from_stage` + `preexisting_worktree`, no flag race)

## What is NOT yet validated

- **Final merge step (`merge_one`)**: pipeline never reached `REVIEW_APPROVED`, so the rebase + ff-merge path on real changes is still untested in production. Tests cover it; live data does not.
- **Codex as writer**: `module_index=193` is odd → claude writes. Half the modules will route to codex. Codex's `--sandbox read-only` should yield text-only output but this path has not been smoke-tested. Risk: codex returns a patch instead of full markdown.
- **Citation insertion**: the rewrite prompt instructs claude to NOT add a `## Sources` section ("citations are handled in a separate stage"). citation_verify only verifies/removes EXISTING citations. **No stage in v2 currently INSERTS citations into rewritten modules.** Either (a) this is intentional and citations land later in a separate batch, or (b) a citation-insertion stage was missed in the v2 design. Needs a design call.

## Open issue: claude write-retry hang

Round 4 retry write hung 900 s with 0 B stdout. Same signature as round 2 (which had a different root cause — wide disallow list). Round 4 retry used the narrow disallow list that succeeded for write 1 of the same run, ~10 min earlier.

Likely cause: Anthropic-side throttling or stall on a second large claude-code call issued within ~10 min of the first. The `_claude_call_count` budget is per-process so each `dispatch_claude` starts fresh, but Anthropic's rate window is independent of our process boundary.

**Diagnostic data preserved**:

- `.pipeline/quality-pipeline/k8s-capa-module-1.2-argo-events.write.36654ecb2e86.failed.json` — round-4 retry hang. `dispatch.ok=False`, `returncode=1`, `duration_sec=900.17`, `stdout_len=0`, `stderr="Claude timed out after 900s"`, `prompt_sha256=3d5a63cae4...`, `prompt_len_chars=91155`.
- `.pipeline/quality-pipeline/k8s-capa-module-1.2-argo-events.write.d42d847f1341.failed.json` — round-2 wide-disallow hang. Same shape. `prompt_len_chars=86882` (no retry must-fix bullets so slightly shorter).

## Plan — next-session task list

### P0. Hang-detection retry inside `_write_in_worktree`

Edit `scripts/quality/stages.py::_write_in_worktree`. After the existing dispatch failure path, detect "looks like a hang" (`result.ok is False` AND `result.stdout` is empty AND `"timed out" in result.stderr.lower()`), sleep N seconds (start with 90), retry the dispatch once with a NEW `attempt_id`. The second `_save_write_diag` call already namespaces by `attempt_id` so both diags survive.

Bound: at most ONE retry. If the retry also hangs, FAIL with both diags on disk.

```
# Sketch — adjust to fit existing structure
if not result.ok and not result.stdout and "timed out" in (result.stderr or "").lower():
    diag = _save_write_diag(..., error="dispatch_hang_attempt1")
    time.sleep(90)
    attempt_id = state.start_in_progress(...)  # new attempt_id; pipeline already tracks these
    result = dispatch(writer, prompt, timeout=timeout, cwd=wt, tools_disabled=True)
    if not result.ok:
        diag = _save_write_diag(..., error="dispatch_hang_attempt2")
        raise StageError(...)
```

Tests:
- `test_write_one_hang_retry_succeeds` — first dispatch returns hang signature, second returns valid markdown → WRITE_DONE.
- `test_write_one_hang_double_retry_fails` — both hang → FAILED with both diags on disk.

### P1. Re-run smoke after P0

```bash
# Reset argo-events to AUDITED (preserves audit + module_index).
.venv/bin/python -c "
import json, pathlib
p = pathlib.Path('.pipeline/quality-pipeline/k8s-capa-module-1.2-argo-events.json')
s = json.loads(p.read_text())
s['stage'] = 'AUDITED'
s['track'] = None; s['write'] = None; s['review'] = None; s['commit'] = None
s['retry_count'] = 0; s.pop('failure_reason', None); s.pop('attempt_id', None)
s['history'].append({'at': '...', 'stage': 'AUDITED', 'note': 'reset for retry round 5 (hang-retry fix)'})
p.write_text(json.dumps(s, indent=2))
"
rm -f .pipeline/quality-pipeline/k8s-capa-module-1.2-argo-events.json.lock

# Smoke. Cool down at least 30 min from any prior claude-code call to
# avoid being on the hang-prone rate window.
.venv/bin/python -m scripts.quality.pipeline run-module k8s-capa-module-1.2-argo-events
# Expect: terminal COMMITTED, .worktrees/ empty, one new commit on main.
```

### P2. Codex-as-writer smoke

Pick an even-index module from the bootstrap's AUDITED set:

```bash
.venv/bin/python -c "
import json, pathlib
for p in sorted(pathlib.Path('.pipeline/quality-pipeline').glob('*.json')):
    if p.name.endswith('.lock') or '.write.' in p.name: continue
    s = json.loads(p.read_text())
    if s.get('stage') == 'AUDITED' and s.get('module_index', 0) % 2 == 0:
        print(s['module_index'], s['slug'], s.get('audit', {}).get('teaching_score'))
" | head
```

Run-module on a candidate. Most likely failure modes:
- Codex returns a `*** Begin Patch` block instead of full markdown → extractor fails. Fix: extend `extract_module_markdown` to handle codex patch format, OR force codex into "plain output" mode via prompt addendum.
- Codex respects `--sandbox read-only` and emits clean markdown → already works.

### P3. Citation-insertion design call

Investigate whether v2 is supposed to insert citations into rewritten modules:

```bash
grep -rn "Sources\|## Sources\|insert_citations\|add_citations" scripts/quality/ docs/
git log --all --oneline | grep -i citation | head
```

If v2 omits citation insertion intentionally, the modules will land without `## Sources` sections, which the rubric flags as a structural gap (487 modules currently at "critical_quality" rubric score == missing Sources). If the design IS to insert citations, locate the missing stage and wire it in.

This is a design question for the user, not a bug to fix solo.

### P4. Push to origin

After P0+P1+P2 land green: `git push origin main`. **18 commits waiting**, none pushed yet. User explicitly approved a single push when the smoke is green.

## What NOT to do

- **Don't run `run-module` against real modules without first cooling down ≥30 min from the last claude-code call.** Two of the four smoke-round failures were claude hangs that I (this session) provoked by chaining heavy calls without spacing. P0 (hang-retry) is the durable fix, but until it lands, manual cool-down is the only protection.
- **Don't push to `origin/main` without explicit user approval.** 18 commits waiting.
- **Don't extend `quality_pipeline.py` (v1).** Dead code, kept only for reference.
- **Don't widen the `--no-tools` disallow list back to include Read/Glob/Grep.** Round-2 hang was caused by exactly that. The narrow list `Bash,Edit,Write,NotebookEdit,WebFetch,WebSearch,Skill,Agent,ExitPlanMode` is empirically validated.
- **Don't raise `--workers` above 1 for batch runs.** Hard cap per `feedback_batch_worker_cap`. Default 1 anyway.
- **Don't rely on the writer's prompt to keep claude in text-only mode** — must pass `--no-tools` (`tools_disabled=True`) at the dispatch call. The prompt alone (round 1) failed.

## Reference: commits this session (6, all unpushed)

| SHA | Title | Why it matters |
|-----|-------|----------------|
| `e240f551` | round-5 post-create-worktree race fix | Codex round-5 must — invariant `we_own_throwaway` predicate replaces flag flipped post-`create_worktree` |
| `3ef9bddf` | STATUS — round-6 APPROVE notation | Documentation only |
| `912f56ee` | persist writer raw stdout/stderr on write failure | Diagnostic — without this every write FAILED is undebuggable without re-dispatch |
| `b488e522` | force text-only output from Claude writer/reviewer | Closes round-1 root cause (agentic claude editing worktree directly) |
| `c8a5f3d1` | narrow `--no-tools` disallow list | Closes round-2 root cause (wide list hangs claude entirely) |
| `2c2a80a5` | add missing `codex` subparser to `dispatch.py` | Closes round-3 root cause (latent — `dispatch_codex` existed but had no CLI route) |
| `cbbbd469` | smoke autopsy in STATUS | Documentation only |

## Reference: cold-start checklist for the next session

```bash
# State of play
curl -s http://127.0.0.1:8768/api/briefing/session?compact=1 | head -40
git log --oneline origin/main..HEAD            # 18 commits, top should be cbbbd469
.venv/bin/python -m pytest tests/test_quality_*.py -q  # 152 passed
.venv/bin/ruff check scripts/quality/ scripts/dispatch.py  # All checks passed!
.venv/bin/python -m scripts.quality.pipeline status | head  # 21 AUDITED, 721 UNAUDITED
ls .pipeline/quality-pipeline/k8s-capa-module-1.2-argo-events.write.*.failed.json

# Then: P0 → P1 → P2 → P3 → P4 above.
```
