# Spec v2: Decoupled Lab Pipeline

*Revised after parallel design review by Codex and Gemini (2026-04-14).*

## Problem

The module pipeline (v1_pipeline.py) currently reviews modules' inline "Hands-On Exercise" sections via a `LAB` check. This causes two distinct failures:

1. **Convergence churn**: Modules get rejected for LAB issues, triggering severe rewrites that don't fix the actual problem (because the actual lab lives elsewhere)
2. **Phantom validation**: The reviewer evaluates lab summaries in markdown, never the actual lab implementation in `/Users/krisztiankoos/projects/kubedojo-labs/{lab}/` (Killercoda scenarios with `index.json`, `setup.sh`, `step*/verify.sh`)

Real labs are at `~/projects/kubedojo-labs/{track-section}-{module-id}-{name}/` with deterministic shell verification scripts. The module pipeline has no awareness of them.

## Goal

1. **Decouple LAB validation from the module pipeline** — module reviewer no longer evaluates LAB
2. **Create a separate lab pipeline** — operates on `kubedojo-labs/{lab}/`, module-aware (knows what the module teaches)
3. **Persistent audit trail per lab** — same audit-log pattern as #236
4. **Independent quality gates** — lab failures don't block module passes (and vice-versa)

## Design

### Module pipeline changes (v1_pipeline.py)

**Remove LAB from `CHECK_IDS`**:
```python
CHECK_IDS = ["COV", "QUIZ", "EXAM", "DEPTH", "WHY", "PRES"]  # was: ["LAB", "COV", ...]
```

**Update reviewer prompt** (line ~1032 + 1045-1050):
- Remove LAB from "Your job is to grade the module on STRUCTURE only" list
- Remove "1. LAB — Can a student reach the end state..." mandatory check
- Renumber subsequent checks (COV becomes 1, etc.)
- Add note: "Lab quality is evaluated by a separate pipeline (lab_pipeline.py) — do not grade hands-on sections here."

**Keep PRES check working**: PRES still requires hands-on sections to be present (preservation), but doesn't grade their executability.

### New lab pipeline (scripts/lab_pipeline.py)

Separate script, separate state file, separate audit log. Same architectural patterns as v1_pipeline.py.

#### Lab discovery

`KUBEDOJO_LABS_DIR = Path("~/projects/kubedojo-labs").expanduser()` (configurable via env var)

A lab is a directory containing `index.json`. Lab key = directory name (e.g., `cka-1.1-control-plane`).

#### Module ↔ Lab mapping (bi-directional, explicit metadata first)

**Primary mapping** (per Codex + Gemini consensus): explicit metadata.

- **Module → Lab**: optional `lab: <lab-id>` frontmatter field in module .md
  ```yaml
  ---
  title: "Control Plane Components"
  lab: cka-1.1-control-plane
  ---
  ```
- **Lab → Module**: `module` field in lab's `index.json`
  ```json
  {
    "title": "...",
    "module": "k8s/cka/part1/module-1.1-control-plane",
    "details": { ... }
  }
  ```

**Fallback mapping** (only if metadata missing): pattern-based discovery
- Convention: `{track}-{N.M}-{slug}` lab name → walk `src/content/docs/{track}/**/module-{N.M}-{slug}.md`
- Helper: `find_module_for_lab(lab_dir)` tries metadata first, falls back to pattern walk

**Lab pipeline behavior on missing link**:
- Default: WARNING (lab still reviewable, COVERAGE uses generic outcomes)
- With `--require-lab-meta` flag: ERROR (mandatory bi-directional link)

V2 will flip the default to ERROR after backfill is complete.

#### State file

`.pipeline/lab-state.yaml` (separate from `.pipeline/state.yaml`).

```yaml
labs:
  cka-1.1-control-plane:
    phase: done
    last_run: 2026-04-14T08:30:00Z
    severity: clean
    reviewer: gemini-3.1-pro-preview
    module: k8s/cka/part1/module-1.1-control-plane
    checks_failed: []
    errors: []
```

#### Phases

Same shape as module pipeline:
- `pending` → `review` → `check` → `done`
- (No WRITE phase — humans/Gemini author labs separately. Pipeline only reviews + verifies.)

Future v2 could add WRITE for auto-generating labs from modules, but v1 is review-only.

#### LAB_CHECK_IDS

```python
LAB_CHECK_IDS = ["STRUCTURE", "DOCS", "COVERAGE", "CALIBRATION", "VERIFY", "EXEC", "DETERM"]
```

| Check | Tier | What it validates |
|-------|------|-------------------|
| `STRUCTURE` | static | All required files present; valid `index.json` schema (title, description, difficulty, time, steps, backend.imageid) |
| `DOCS` | static | `intro.md` sets context; `step*/text.md` clear; `finish.md` summarizes; hints in `<details>` blocks where appropriate |
| `COVERAGE` | static | Lab steps practice every Learning Outcome from linked module (passed via prompt) |
| `CALIBRATION` | static | Multi-factor difficulty match: step count + scaffolding density + hint quantity + state complexity + declared `time` matches reasonable expectation. Replaces simple step-count check (per Codex). |
| `VERIFY` | static | `verify.sh` scripts check exact state (e.g., `kubectl get -o jsonpath`) not stdout patterns. Flag `grep`/`wc -l`/`sleep` (per Gemini — `sleep` is a juniors' anti-pattern instead of `kubectl wait`) |
| `EXEC` | exec | `setup.sh` runs without errors in fresh container; required tools available; each step's `solution.sh` runs cleanly |
| `DETERM` | exec | After `solution.sh`: `verify.sh` exits 0. After fresh `setup.sh` only: `verify.sh` exits 1. Run twice — same result both times (no flakiness) |

#### Tiered execution (single script, capability-detected)

Per Codex: keep one script with internal layered tiers, not two scripts.

- **`--static`** (default): runs STRUCTURE, DOCS, COVERAGE, CALIBRATION, VERIFY (no Docker needed)
- **`--exec`**: runs static tier PLUS EXEC, DETERM (Docker required). `check_docker_daemon()` guard at start of exec tier — if Docker unavailable:
  - In CI (env `CI=true`): ERROR ("EXEC tier required in CI but Docker unavailable")
  - In dev: WARNING ("EXEC tier skipped — Docker not available") + report as "not run"

#### EXEC isolation (per Gemini — mandatory)

For each lab in `--exec` mode:
1. Spin up fresh container from `index.json.backend.imageid` (e.g., `kubernetes-kubeadm-1node`)
2. Copy lab files in
3. Run `setup.sh`
4. For each step: run `solution.sh`, then `verify.sh` (must exit 0)
5. Reset container (or fresh container), run `setup.sh` only, run `verify.sh` without solution (must exit 1 — negative test)
6. **Mandatory teardown**: `docker rm -f` the container, even on error path

No shared cluster across labs. Each lab gets its own ephemeral container. Stderr of `verify.sh` is captured and included in audit log entry.

Pass via reviewer prompt:
- Module's learning outcomes (extracted from frontmatter)
- Module's topic coverage section
- Module's existing inline "Hands-On Exercise" summary
- Lab's `index.json` + `intro.md` + each step's `text.md` + `verify.sh`

Reviewer model: `gemini-3.1-pro-preview` (matches module reviewer).

#### Reviewer prompt template

```
You are reviewing a hands-on lab for KubeDojo.

The lab practices the concepts taught in this module:
- Learning outcomes: {module_outcomes}
- Topics covered: {module_topics}

Your job is to grade the LAB ONLY on these dimensions:

1. COVERAGE — Do the lab steps practice every Learning Outcome from the module?
   A FAIL must list specific outcomes the lab doesn't exercise.

2. DIFFICULTY — Does the step count match the calibration:
   - Beginner: 3-4 steps with generous hints
   - Intermediate: 4-5 steps with concept hints
   - Advanced: 5-6 steps with minimal guidance

3. STRUCTURE — Required files present? Valid index.json schema?
   - index.json (with title, description, difficulty, time, steps)
   - intro.md, setup.sh
   - step{N}/text.md and step{N}/verify.sh for each declared step
   - finish.md

4. VERIFY — Are verify.sh scripts deterministic? They must check exact state
   (kubectl get pod X -o jsonpath='{.status.phase}' = Running), not stdout patterns.
   Flag any verify.sh that uses `grep`, `wc -l`, or output format checks.

5. DOCS — Are step instructions clear? Does intro set context? Does finish summarize?

Output JSON:
{
  "verdict": "APPROVE" | "REJECT",
  "checks": [
    {"id": "COVERAGE", "passed": bool, "evidence": "..."},
    ...
  ],
  "feedback": "narrative summary"
}
```

### Per-lab audit log

Path: `.pipeline/lab-reviews/{lab_key}.md` (mirrors module audit at `.pipeline/reviews/`).

Same `append_review_audit` mechanics — fcntl lock, atomic writes, reverse-chronological, header refresh from `lab-state.yaml`.

Events:
- `LAB_REVIEW` (with `verdict`, `severity`, checks list)
- `LAB_EXEC` (only in `--exec` mode — duration, pass/fail per step)
- `LAB_DONE` (final pass)
- `LAB_RESET` (mirrors module RESET)

### CLI

```
python scripts/lab_pipeline.py status                           # Status across all labs
python scripts/lab_pipeline.py review {lab_name}                # Review one lab (--static default)
python scripts/lab_pipeline.py review {lab_name} --exec         # Full execution mode
python scripts/lab_pipeline.py e2e [tracks...]                  # All labs (default: all tracks)
python scripts/lab_pipeline.py e2e cka --static                 # Static-only review of CKA labs
python scripts/lab_pipeline.py reset-stuck                      # Reset stuck labs
```

### Storage layout

```
.pipeline/
├── state.yaml               # module pipeline state (existing)
├── lab-state.yaml           # NEW: lab pipeline state
├── reviews/                 # module audit logs (existing, from #236)
└── lab-reviews/             # NEW: lab audit logs
```

### Cross-references

- **Module → Lab**: Module's frontmatter gets new optional field `lab: {lab-name}` (e.g., `lab: cka-1.1-control-plane`). Module reviewer prompt skips LAB but PRES check verifies a `## Hands-On Exercise` section exists with a link to the lab.
- **Lab → Module**: Stored in `lab-state.yaml.module` field (resolved by `find_module_for_lab`).

This keeps modules and labs coupled in narrative/intent, but decoupled in quality gates.

## Acceptance Criteria

### Module pipeline changes
- [ ] `CHECK_IDS` no longer contains "LAB"
- [ ] Reviewer prompt removes LAB check; renumbers remaining checks; adds note about lab pipeline
- [ ] Existing modules previously failing on LAB now pass (if other checks pass)
- [ ] PRES check still flags missing "Hands-On Exercise" sections (preservation, not quality)
- [ ] All 133 existing tests still pass

### Lab pipeline (new)
- [ ] `scripts/lab_pipeline.py` exists with `status`, `review`, `e2e`, `reset-stuck` subcommands
- [ ] `--static` mode runs without Docker
- [ ] `--exec` mode runs `setup.sh` + each step's `solution.sh`/`verify.sh` in Docker container from `index.json.backend.imageid`
- [ ] `find_module_for_lab` resolves lab → module via naming convention
- [ ] Lab review prompt includes module's learning outcomes + topics
- [ ] State persists in `.pipeline/lab-state.yaml`
- [ ] Per-lab audit logs in `.pipeline/lab-reviews/{lab_key}.md` with same pattern as #236

### Quality
- [ ] Lab pipeline uses `_atomic_write_text` and `fcntl.flock` (cross-process safe)
- [ ] **Per-lab locking** (not global): each lab has its own `.lock` file (per Codex)
- [ ] `--exec` mode failures don't crash pipeline (catch + log per-lab)
- [ ] **EXEC isolation mandatory**: each lab runs in its own ephemeral container with mandatory teardown (per Gemini)
- [ ] **Docker capability detection**: `check_docker_daemon()` at start of EXEC tier; ERROR in CI (`CI=true`), WARNING in dev
- [ ] No coupling between module state and lab state (independent reset/resume)
- [ ] Bi-directional metadata link: `lab:` in module frontmatter + `module:` in lab `index.json`
- [ ] `--require-lab-meta` flag enforces both metadata fields present

### Testing
- [ ] Unit test: `find_module_for_lab` correctly maps `cka-1.1-control-plane` → `k8s/cka/part1/module-1.1-control-plane.md`
- [ ] Unit test: lab pipeline state load/save roundtrip
- [ ] Unit test: `--static` mode runs all 4 static checks (STRUCTURE, DOCS, COVERAGE, DIFFICULTY)
- [ ] Unit test: lab audit log writes with correct events
- [ ] Integration test: review one real lab (e.g., `prereq-1.1-shell-mastery`) in `--static` mode
- [ ] Integration test: pick one failing lab from current state, fix it, prove it passes
  - Expected fix demonstrates value: a lab that was being "fixed" by module rewrites can now be properly reviewed and corrected

### Backwards compatibility
- [ ] Existing `state.yaml` and `reviews/` unchanged
- [ ] Modules can ship without a `lab:` frontmatter field (lab pipeline just won't have a module ref for that lab — uses generic outcome list)
- [ ] Reset-stuck on module pipeline doesn't touch lab state and vice-versa

### Demonstration (per user requirement)
- [ ] One lab is fixed end-to-end through this pipeline
- [ ] The fix passes adversary review (Gemini reviews fixed lab → APPROVE)
- [ ] Audit log of the lab shows: initial REVIEW (REJECT), the fix, final REVIEW (APPROVE), DONE

## Non-Goals (v1)

- No auto-generation of labs from modules (review-only, not write)
- No Killercoda integration testing (`--exec` runs locally in Docker, not via Killercoda)
- No fact-grounding for labs (deferred — labs reference module facts which are already grounded)
- No translation of lab content to Ukrainian (deferred)

## Open Questions

1. Should lab `--exec` failures fail the lab pipeline pass, or should they be warnings (since Docker is environment-dependent)? Proposal: WARNING in dev, ERROR in CI.
2. Should the module pipeline's PRES check enforce a frontmatter `lab:` field exists when a "Hands-On Exercise" section is present? Proposal: WARNING for v1, ERROR for v2.
3. Should we backfill `lab:` frontmatter into all 816 modules now or incrementally? Proposal: incremental — let lab pipeline emit suggestions.
4. Does Killercoda support multi-image labs (one container per step)? If so, do we need to handle that? Proposal: no, stick to single-image labs for v1.

## Workflow

1. [x] Spec v1 written
2. [x] Codex + Gemini design review (parallel)
3. [x] Spec revised to v2 incorporating feedback
4. [ ] Codex implements (in worktree)
5. [ ] Gemini reviews implementation
6. [ ] Claude reviews
7. [ ] Pick one currently-failing lab, fix it through the new pipeline
8. [ ] Gemini adversary-reviews the fix
9. [ ] Close issue

## Design Review Sign-Off

- [x] **Codex** (2026-04-14): Approved with revisions — fragile naming convention, single script with tiered exec, refine DIFFICULTY → CALIBRATION, per-lab locking, bi-directional metadata. All addressed in v2.
- [x] **Gemini** (2026-04-14): APPROVE with 2 required changes — mandatory `lab:` frontmatter, EXEC isolation + cleanup. Addressed in v2 (frontmatter optional v1 with WARNING + `--require-lab-meta` flag, EXEC isolation per-container with mandatory teardown).
