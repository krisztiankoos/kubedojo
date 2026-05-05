# Session handoff — 2026-05-05 (session 2) — Phase D pilots (3) + Phase E sweep Part 1 shipped + Parts 2-9 plumbing

> Picks up from `2026-05-05-1-dispatch-fix-and-book-audit-prep.md`. Inherited a freshly merged source-of-problem patch (PR #888 covering `scripts/dispatch.py`) but with the agent_runtime adapter and `dispatch_codex_patch` still unfixed, plus a queued book-audit Phase D plan starting at ch-33 Deep Blue. This session extended the patch, ran three Phase D pilots, fixed all surfaced wrong-specifics inline, designed + cross-family-reviewed a Phase E sweep driver, shipped Part 1 (ch-01..ch-08, 6 fixes), and launched Part 2 — which is still running at handoff time.

## Decisions and contract changes

### PR #888 extended + merged + 4 carry-over PRs merged

The session-1 plan called for extending PR #888 to cover the two remaining codex code paths (`dispatch_codex_patch` + `agent_runtime/adapters/codex.py`). Done in commit `76ff38be` on `fix/dispatch-codex-search`:

- `dispatch_codex_patch` honors `KUBEDOJO_CODEX_SEARCH=1` + `KUBEDOJO_CODEX_SANDBOX` (same env-var pattern as `dispatch_codex`).
- `CodexAdapter.build_invocation` honors `KUBEDOJO_CODEX_SEARCH=1` (inserts `--search` before `exec`). Sandbox stays a first-class `mode` parameter (caller controls via the runner; no env-var override there because that would create dual authority — codex agreed in his review).

Threading verified end-to-end via 4-case smoke (no env / env=1 / env=0 / env=1+danger). Cross-family reviewed by codex gpt-5.5 with `KUBEDOJO_CODEX_SEARCH=1` (the very env var the PR introduces — meta-validation that the patch works). Codex returned **APPROVE**, verified both core claims against upstream codex source: `--search` is a top-level flag (`codex --search exec ...`), and valid `--sandbox` values are exactly `read-only` / `workspace-write` / `danger-full-access`. PR #888 squash-merged (`733cfff0`).

Then the user instructed "merge those" for three carry-over PRs:
- PR #884 (incident-dedup KCSA+KCNA sweep) → squash `29cc2863`
- PR #885 (incident-dedup Platform sweep) → squash `e2e11e5b`
- PR #887 (CKS pilot redo, search-verified) → squash `a86b7b9e`

Plus a follow-up structural fix on PR #887's content (`c9c45c45`): dropped stray `# Module 1.2` H1 + added missing `---` separator after blockquote per `module-quality.md`. Build clean, 2015 pages.

### Phase D pilots — 3 chapters audited, all fixed inline

Three pilots (each ~25-60 min wall) drove the section-by-section risk profile:

| Pilot | Chapter | Claims | R:supported | Errors | Section of error |
|---|---|---|---|---|---|
| 1 | ch-33 Deep Blue | 74 | 65 (88%) | 1 R:contradicted | S:glossary (Fredkin Prize "≥2500" vs body's "2650+") |
| 2 | ch-34 The Accidental Corpus | 108 | 95 (88%) | 1 R:wrong + 1 body drift | S:cast (Berners-Lee "CERN physicist") + S:body "billions of words" 1993 |
| 3 | ch-58 The Math of Noise | 63 | 54 (86%) | 1 W:wrong + 3 W:partial | **S:matters** (DDPM "still dominant" / FLUX-SD3 framing) + S:architecture "every layer" |

All fixed inline this session: `d0201191` (ch-33), `065e4fd8` (ch-34), `6e1ba040` (ch-58). Build clean each time.

### Phase E scope locked + cross-family-reviewed driver shipped

Three-pilot synthesis (locked in `docs/decisions/2026-05-05-phase-e-scope.md`, commit `cfb5b278`):

| Section | Pilot data | Phase E action |
|---|---|---|
| `S:cast` | 1 wrong / 3 pilots | sweep — bundle cross-check |
| `S:glossary` | 1 contradicted / 3 pilots | sweep — bundle cross-check |
| `S:matters` | 1 W:wrong + several W:partial / 1 pilot | **sweep** + web verify forward-looking |
| `S:timeline` | clean across all 3 | skip — template-derived |
| `S:math` | 6/6 clean (Tier 2 with codex math review) | skip — codex math review effective |
| `S:architecture` | 3/7 minor drift, 0 contradicted | spot-check only |
| `S:body` | 6% paraphrase drift, low severity | on-request only (NOT systematic) |

User pushed back on "skip" sections: *"address all from high to low, fix ALL errors, dnt you agree?"* — agreed in principle (fix every wrong-specific) with the nuance that "error" = factually-wrong specifics, not paraphrase drift. The driver prompt distinguishes them explicitly.

User also instructed cross-family review pre-launch: *"consult with codex about this and with gemini, so the fix is not causing stylistic errors."* Both reviewers returned NEEDS CHANGES. Their must-fixes integrated into the v2 driver:

**Codex (engineering)**:
- `fcntl` per-chapter lock (no shared `.tmp` race)
- `tempfile.mkstemp` for atomic write (not shared `.tmp` filename)
- `sha256(original)` at audit start, re-verify before write (concurrent-modification detection)
- Byte-for-byte frontmatter preservation (not just title-line check)
- Structural-block count preservation (`<details>`, `:::note`, `## headings`)
- Rate-limit detection at sweep level (halts the sweep)
- Log audit-trail BEFORE atomic-applying (not after)
- `.venv/bin/python` (not `sys.executable`) per project rule
- `--part` flag for natural per-Part gating, default --halt-on-rate-limit
- Robust separator regex (line-anchored)

**Gemini (stylistic)**:
- Output format = JSON `before→after` fix-list, NOT full markdown regeneration (full-rewrite causes silent stylistic drift)
- Forbid metaphor / rhetorical-flourish "corrections"
- Explicit ban on "as of {year}" boilerplate in `:::note[Why this still matters today]` blocks
- Explicit "minimum edit, preserve voice" rule with operational examples

Driver: `scripts/sweep_ai_history_aids.py` (committed in Part 1, `0a6cb725`). 9 Parts (ch-01..ch-08, ch-09..ch-16, ..., ch-65..ch-72). Skips ch-33/34/58 (already audited). Each Part: dispatch dry-run → inspect diffs → apply audited fixes from JSON (re-using dry-run audit output, no re-dispatch) → build verify → commit + push → next Part.

### Phase E Part 1 shipped (ch-01 .. ch-08)

8 chapters audited, 4 returned clean, 4 had a total of 6 wrong-specifics — all bundle-cited or web-cited, all minimum edits. Commit `0a6cb725`:

| Chapter | Fixes | Type |
|---|---|---|
| ch-02 | 1 | Universal Machine: "five years before" → "more than a decade" (Manchester Baby 1948 = 12 yr after Turing 1936; chapter contradicted itself in next paragraph) |
| ch-05 | 3 | Neural Abstraction: Lettvin "Univ. of Chicago" → "Univ. of Illinois" (cast + body); 1959 frog's-eye paper authorship order corrected to canonical |
| ch-07 | 1 | Analog Bottleneck: W. Grey Walter tortoise Behaviour N steering motor "half speed" → "full speed" (was Behaviour E figure mis-applied; Holland 2003 p.2101 anchors it) |
| ch-08 | 1 | Stored Program: flag-bit memory tagging attribution "First Draft" (1945) → "1946 IAS design" (Haigh 2014 p.10 anchor; bundle infrastructure-log explicit) |

Wall: ~1 hr Part 1 dry-run + 5 min apply + commit. Build clean.

### dispatch.py CLI bug fix (incidental)

While dispatching gemini for the stylistic review, the `python scripts/dispatch.py gemini --review --timeout T - < prompt > out.md` command returned EXIT=0 with empty out.md. Root cause: the gemini CLI branch in `dispatch.py main()` only printed output via `post_to_github()` when `--github` was passed; without `--github`, output was silently discarded. The claude and codex branches both had `if ok: print(output)`. Two-line fix in commit `a385f81f` adds the missing `print(output)` to the gemini branch.

## What's still in flight

- **Phase E sweep Part 2 (ch-09..ch-16)** — dry-run launched at 10:35 local, ETA ~11:30. Background bash task ID: `bmdolfkpn`. Output to `.tmp/sweep-logs/part2-dry-run.log` and `summary.jsonl`.
- **PR #872** (codex routing tiers + `dispatch_smart.py` extension) — still open, NEEDS CHANGES. Gemini re-review still queued from session 1.
- **Decision Card promoted to commit** — `docs/decisions/2026-05-05-phase-e-scope.md` (`cfb5b278`); pending dir created at `docs/decisions/pending/` (currently empty).

## What remains to do

### Phase E sweep continuation (Parts 2 through 9)

Per-Part flow is locked. Repeat-cycle for each Part:

```bash
.venv/bin/python scripts/sweep_ai_history_aids.py --part N --dry-run \
  > .tmp/sweep-logs/partN-dry-run.log 2>&1

# Inspect diffs:
ls .tmp/sweep-logs/ch-*-{audit,diff}.* | sort -u

# Apply audited fixes (re-uses the dry-run audit JSONs; no re-dispatch):
.venv/bin/python -c "
import json, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
from sweep_ai_history_aids import (apply_fixes, post_apply_sanity, atomic_write, hash_text, chapter_prose_path)
LOG = Path('.tmp/sweep-logs')
applied = []
for audit_path in sorted(LOG.glob('ch-*-audit.json')):
    audit = json.loads(audit_path.read_text())
    chapter_id = audit['chapter_id']
    if not audit['fixes']: continue
    prose_path = chapter_prose_path(chapter_id)
    original = prose_path.read_text()
    if hash_text(original) != audit['original_hash']:
        print(f'{chapter_id}: SKIP — hash mismatch'); continue
    ok, fixed, errors = apply_fixes(original, audit['fixes'])
    if not ok: print(f'{chapter_id}: FAIL apply — {errors}'); continue
    sane, msg = post_apply_sanity(original, fixed)
    if not sane: print(f'{chapter_id}: FAIL sanity — {msg}'); continue
    atomic_write(prose_path, fixed)
    applied.append((chapter_id, len(audit['fixes'])))
    print(f'{chapter_id}: applied {len(audit[\"fixes\"])} fix(es)')
print('total fixes:', sum(n for _,n in applied))
"

# Verify build:
npm run build 2>&1 | tail -3

# Commit + push (per-Part commit message convention from Part 1):
git add src/content/docs/ai-history/
git commit -m "chore(ai-history): Phase E sweep Part N — fix M wrong-specifics across ch-XX..ch-YY" \
  -m "<per-chapter detail; cite bundle/web sources; same shape as 0a6cb725>"
git push
```

**Important**: re-running a Part's dry-run resets and re-dispatches (model temperature → slightly different fix-lists). Do NOT re-run a Part without a reason. The audit JSONs in `.tmp/sweep-logs/` are the contract; the apply script reads them.

**Per-Part skip rules**:
- Part 5 (ch-33..ch-40): skip ch-33 + ch-34 (already audited inline this session)
- Part 8 (ch-57..ch-64): skip ch-58 (already audited inline this session)
- Default skip set in driver: `ch-33,ch-34,ch-58`

**Estimated cost remaining**: 8 Parts × ~1 hr dry-run + ~5 min apply/commit each = ~8.5 hr wall + ~40 min orchestrator-active. ~$70-100 in claude tokens for the 8 Parts. Likely 30-50 wrong-specifics to fix across the remaining 64 chapters (extrapolating from Part 1's 6 fixes / 8 chapters).

### Other follow-ups

- **Re-request Gemini review on PR #872** (codex routing tiers + smoke results). Once Gemini re-approves, merge.
- **Sweep #5 (Cloud + AI-ML + On-Prem)** — incident-dedup, gated on PR #884 + #885 merging (now done). Refresh `docs/audits/2026-05-04-incident-reuse.md` on post-merge main, then dispatch sweep #5 via `dispatch_smart.py edit`.
- **Sweep #6 trope rewrite** — `ai-ml-engineering/mlops/module-1.3-cicd-for-ml.md` (1 file, inline). Carry-over from session 1.
- **Sweep #7 CKA / CKAD final cleanup** — confirm via fresh audit after sweep #5.
- **Promote `scripts/check_incident_reuse.py` to CI-required** once curriculum-wide count reaches 0.
- **Restart Claude Code** for fresh `GEMINI_API_KEY` (still stale in this process; `source ~/.bash_secrets &&` workaround still required for gemini dispatches).
- **Two structural issues recurring across codex #388 drafts** (also flagged session 1): stray `# Module X.Y: Title` H1 + inline metadata. Update `module-rewriter-388.md` / `module-writer.md` prompts before next #388 batch.

## Cold-start smoketest

```bash
cd /Users/krisztiankoos/projects/kubedojo

# 0. Canonical orientation
curl -s http://127.0.0.1:8768/api/briefing/session?compact=1 | head -50

# 1. Confirm trunk state
git log --oneline -10
# Expected most recent: 0a6cb725 (Phase E Part 1) or later (whatever Part N was last shipped)

# 2. Check if Part 2 dry-run is still alive (orchestrator may have backgrounded it at handoff)
/bin/ps -ef | grep -E 'sweep_ai|dispatch.py.*claude' | grep -v grep

# 3. Inspect any Part 2 results that may have completed
ls -la .tmp/sweep-logs/ | grep -E 'ch-(09|10|11|12|13|14|15|16)|part2'
cat .tmp/sweep-logs/summary.jsonl | tail -20

# 4. Worktree state
git worktree list
# Expected: main + claude-codex-routing (PR #872) + codex-interactive (detached HEAD, pre-existing)

# 5. PRs in flight
unset GITHUB_TOKEN && export GH_TOKEN=$(grep -oE 'github_pat_[A-Za-z0-9_]+' .envrc | head -1)
gh pr view 872 --json state,reviewDecision --jq '{state,reviewDecision}'

# 6. Decision card
ls docs/decisions/
# Expected: 2026-05-05-phase-e-scope.md + pending/ (empty unless user filed something)
```

## Files touched / committed this session

```
On main (squash-merged or direct commits):
  733cfff0 fix(dispatch): codex writer needs --search; reviewer needs WebFetch+WebSearch (#888)
  29cc2863 chore(content): de-dup incident anecdotes — KCSA + KCNA sweep (#878) (#884)
  e2e11e5b chore(content): de-dup incident anecdotes — Platform sweep (#878) (#885)
  a86b7b9e feat(388): density+structure rewrite of CIS Benchmarks and kube-bench (#388 pilot) (#887)
  c9c45c45 fix(cks): drop stray H1 + add separator on CIS Benchmarks module
  d0201191 fix(ai-history): correct ch-33 glossary Fredkin Prize threshold
  065e4fd8 fix(ai-history): correct ch-34 cast title + 1993 corpus-size figure
  6e1ba040 fix(ai-history): correct ch-58 forward-looking matters note + cross-attention scope
  cfb5b278 docs(decisions): finalize Phase E scope after 3-pilot dataset
  a385f81f fix(dispatch): print gemini output to stdout when not posting to GitHub
  0a6cb725 chore(ai-history): Phase E sweep Part 1 — fix 6 wrong-specifics across ch-01..ch-08

PRs merged this session:
  #888 fix/dispatch-codex-search → main (squash 733cfff0). Branch deleted on origin.
  #884 claude/incident-sweep-kcsa-kcna → main (squash 29cc2863). Branch deleted.
  #885 claude/incident-sweep-platform → main (squash e2e11e5b). Branch deleted.
  #887 codex/388-pilot-module-1-2-cis-benchmarks → main (squash a86b7b9e). Branch deleted.

Worktrees cleaned up:
  /Users/krisztiankoos/projects/kubedojo/.worktrees/fix-dispatch-search (after PR #888 merge)
  /Users/krisztiankoos/projects/kubedojo-sweep-kcsa-kcna (after PR #884 merge)
  /Users/krisztiankoos/projects/kubedojo-sweep-platform (after PR #885 merge)

Worktrees still around (intentional):
  /Users/krisztiankoos/projects/kubedojo                                  (primary, main)
  /Users/krisztiankoos/projects/kubedojo/.worktrees/claude-codex-routing  (PR #872, still open)
  /Users/krisztiankoos/projects/kubedojo/.worktrees/codex-interactive     (detached HEAD, pre-existing)

Files added:
  scripts/sweep_ai_history_aids.py             — Phase E sweep driver (cross-family reviewed)
  docs/decisions/2026-05-05-phase-e-scope.md   — Decision card with 3-pilot synthesis
  docs/decisions/pending/                       — empty dir created
  .tmp/sweep-logs/                              — audit + diff artifacts for inspection (NOT committed; .tmp is gitignored)

Still in-flight at handoff:
  Background bash task bmdolfkpn — Part 2 dry-run; ETA ~11:30 local
```

## Cross-thread notes

**ADD**:

- **Phase E sweep mechanism is **dispatch-then-apply-from-audit-JSON** (NOT re-dispatch).** The dry-run produces audit JSONs in `.tmp/sweep-logs/`. The apply step re-uses those JSONs to apply fixes deterministically — no second dispatch needed. This means dry-run is the expensive step; apply is ~1 second per chapter. Don't re-run a Part's dry-run unless something changed (model temperature would produce slightly different fix-lists).
- **Output format is JSON `before→after` fix-list (NOT full markdown regeneration)** — gemini stylistic review caught that full-markdown rewrite causes silent paraphrase drift through sampling variance. The driver enforces: `before` must appear exactly once in the file, `after` is the minimum edit, neither may span structural boundaries (`##`, `<details>`, `:::`).
- **Per-chapter `fcntl` lock + `sha256(original)` concurrent-modification check** are now standard for this style of batch-edit driver. Codex review caught the race-window in the prior shared-`.tmp` design.
- **Section-by-section risk profile (3-pilot synthesis)** locked in `docs/decisions/2026-05-05-phase-e-scope.md`. Cast / glossary / `:::note[Why this still matters today]` are the high-yield sweep targets. Timeline is template-derived from `timeline.md` and clean. Math sidebars in Tier 2 chapters had separate codex math-review and are clean. Architecture sketches drift on implicit knowledge but are not contradicted. Body prose has 6% paraphrase drift but rarely a wrong-specific.
- **`dispatch.py gemini` print bug fixed** (commit `a385f81f`) — the gemini CLI branch was missing `if ok: print(output)`. Now matches claude/codex branches. Workaround note in cross-thread (above) is now stale; can drop.

**DROP / RESOLVE**:

- "PR #888 patch only covers `scripts/dispatch.py`" — RESOLVED. PR #888 was extended to cover the agent_runtime adapter + `dispatch_codex_patch` and merged this session.
- "PR #884 + #885 not yet merged" — RESOLVED. Both merged this session.
- "Cross-family review of PR #888 needed" — RESOLVED. Codex APPROVE; merged.
- "Book audit Phase D pilot" — RESOLVED (3 pilots, all fixed inline).
- "Phase E gating decision" — RESOLVED. Final scope committed; 9-Part sweep launched (Part 1 shipped, Parts 2-9 plumbing).
- "`dispatch.py gemini` doesn't print verdict to stdout without `--github N`" — RESOLVED by commit `a385f81f`. Drop the cross-thread note.

## Blockers

- **Phase E sweep Parts 2-9 still pending** — Part 2 dry-run in flight; Parts 3-9 not started. Each Part is ~1 hr dry-run + 5 min apply/commit. Total ~8.5 hr wall remaining. Not urgent but is the active workstream.
- **PR #872 still open + NEEDS CHANGES** — Gemini re-review queued. Lower priority; carry-over from session 1.
- **Stale `GEMINI_API_KEY` in this Claude Code process** — same as session 1; per-call workaround `source ~/.bash_secrets &&` still works. Permanent fix: `/exit` and restart Claude Code.
- **GH_TOKEN value still exposed in 2026-05-04 session 2 transcript** — operational hygiene only. Rotate when convenient.

## New / updated memory this session

- **UPDATED** — `feedback_codex_writer_needs_search.md`: PR #888 is now on trunk (squash `733cfff0`) and covers all three codex code paths (writer, patcher, book adapter). Adapter intentionally omits `KUBEDOJO_CODEX_SANDBOX` — caller's `mode` parameter is the authority; codex review confirmed this is the right design.

(No new memories in this session — the patterns we hit were extensions of existing memories rather than novel rules.)

## What was NOT done this session (carryover)

- Sweep #5 (Cloud + AI-ML + On-Prem) — not started; gated on PR #884 + #885 merging (now done; can dispatch next session).
- Sweep #6 forbidden-trope rewrite (1 file inline) — not started.
- Sweep #7 CKA / CKAD final cleanup — not started.
- Re-request Gemini review on PR #872 — not done.
- Restart Claude Code for fresh `GEMINI_API_KEY` — not done (per-call workaround used instead).
- Coherence sweep at KCNA bucket boundary (B3 protocol) — not started.
- Investigate the 8 module_skip events from KCNA batch — not started.
- Decide A2 plumbing vs straight to KCSA bucket-2 — not decided.
- Update `module-rewriter-388.md` / `module-writer.md` prompts to ban stray H1 + inline metadata — not done.
- Phase E sweep Parts 2-9 — Part 2 dry-run in flight at handoff; Parts 3-9 not started.

The session was deeper than wide: PR #888 fully landed, three high-quality book-audit pilots, sweep driver designed + cross-family reviewed + Part 1 shipped. The carryover sweep-#5/6/7 work is unblocked but deferred to keep the book-audit thread moving.
