---
title: Session 9 handoff — PR #324 section source pool ready for Codex review + merge
date: 2026-04-21
---

# TL;DR

Session 9 turned the session 8 citation-pipeline work into a shipping
feature: [#324](https://github.com/kube-dojo/kube-dojo.github.io/pull/324)
implements the **section source pool** design that issue #323 specified.

**The PR is open, pushed, dogfooded clean on 4 modules, and has 3
post-review code fixes pushed on top.** Next session's first job: have
Codex do an independent PR review and merge it if clean.

# What landed this session

## The design consultation

Asked Codex for an opinionated critique of the "section-batched
research" idea before writing code. Codex answered with a hybrid
recommendation that pivoted the design: **section-level source
discovery, per-module research constrained to the pool**. Rationale
and concrete answers to 7 design questions saved in the conversation
log and now canonicalized in PR #324's description. Codex's opinion
mattered here — the naive 5-10-modules-batched approach would have
reduced truthfulness. Using a shared-source-pool + per-module-research
preserves verify-per-claim correctness while still eliminating
redundant URL discovery across related modules.

## Issue #323 — filed

[#323](https://github.com/kube-dojo/kube-dojo.github.io/issues/323)
captures the design with strict acceptance criteria, non-goals, and
risk list.

## PR #324 — shipped on feat/section-source-pool

Branch: `feat/section-source-pool` (pushed to origin).

Commits on the branch:
- `9e184080` — Codex's draft (460 + 128 + 166 LOC across 3 new scripts
  + patches to `citation_backfill.py`, `pipeline_v3.py`,
  `verify_citations.py`, `fetch_citation.py`; tests pass)
- `5a50b2b2` — schema-prune helper + readthedocs.io allowlist + gitops
  dogfood (my patches after Codex timed out mid-implementation)
- `3c46c1b8` — 3 code-review fixes (disposition filter on Sources,
  prune reports actual claim count on non-claim issues, bare-URL title
  derived from host+path)

## Dogfood evidence

Section `platform/toolkits/cicd-delivery/gitops-deployments/` (4
modules): 4/4 success. Pool at
`docs/citation-pools/platform-toolkits-cicd-delivery-gitops-deployments.json`
has 6 validated sources; 3 are reused across modules 2.1 and 2.2 —
the pool-sharing design is empirically confirmed.

## Code review (self-done via skill)

Ran the `code-review:code-review` skill against #324. Five parallel
reviewers flagged 8 candidate issues; scoring filtered 7 of them below
the 80 threshold, so the official comment on the PR is "No issues
found." **But four of those sub-threshold issues were real**, and I
fixed 3 of them on the branch in `3c46c1b8` anyway:
- `_build_sources_section_from_seed` leaked `needs_allowlist_expansion`
  URLs into Sources — now gated on `CITED_DISPOSITIONS`.
- `_prune_schema_failed_claims` aborted modules on non-claim-only
  schema issues (e.g. `missing_section_pool:`) — now preserves actual
  `remaining_claims` count so the caller's abort check fires only on
  genuinely empty seeds.
- Bare URLs as link titles (`[url](url) — note`) — added
  `_derive_title_from_url` helper producing `host: last-path-segment`
  titles; fixed-up 16 already-committed bullets across the 4 dogfood
  modules.

Process items I did NOT address (noted in the PR comment thread):
- STATUS.md update (CLAUDE.md Session Workflow rule #4)
- Gemini review on issue #323 before closing (gemini-workflow.md rule)

# Next session's first task — Codex review + merge of PR #324

Exact recipe:

1. Verify PR is still open:
   ```bash
   gh pr view 324 --repo kube-dojo/kube-dojo.github.io --json state
   ```

2. Ask Codex to review the PR. Use the `/code-review` skill OR a
   direct dispatch. The dispatch prompt should include:
   - PR URL
   - The specific files to review (`scripts/section_source_discovery.py`,
     `scripts/pipeline_v3_section.py`, the patches to `citation_backfill.py`
     and `pipeline_v3.py`, `tests/test_section_source_discovery.py`)
   - The context that **Claude has already done a code review** (find
     it in the comments) — Codex is the second opinion, not the first
   - The 3 fixes landed on top of Codex's draft (`3c46c1b8`) — Codex
     should specifically confirm those fixes look right
   - Hard constraint: Codex must NOT push to main; it reviews and
     reports, the user merges

3. If Codex raises concrete issues, address them on the branch and
   re-request review.

4. If Codex approves or raises only nits, merge the PR:
   ```bash
   gh pr merge 324 --repo kube-dojo/kube-dojo.github.io --squash --delete-branch
   ```

5. Delete the local worktree after merge:
   ```bash
   cd /Users/krisztiankoos/projects/kubedojo
   git worktree remove .worktrees/section-source-pool
   ```

6. After merge, the section pipeline is the preferred path for the
   remaining ~500 structurally-complete uncited modules. Run it on
   the next small section (suggest `platform/toolkits/cicd-delivery/source-control/`
   or `k8s/cka/part3-services-networking/`) to validate at scale.

# Remaining scope after PR #324 merges

## Citation pipeline — the big queue

At the end of session 8, 42 modules were at ≥4.0 (up from 13).
Session 9 added 4 more via the dogfood → ~46 at ≥4.0. The scorer's
filter `(lines >= 300, has_quiz, has_exercise, has_diagram, no citations)`
matched 597 candidates at session start; subtract whatever the
section-pool pipeline has cleared since.

The remaining queue is still 500+ modules. At section-pool wall times
(5 modules × ~10-12 min per module = 50-60 min per section), this is
~100 sections × ~1 hour = 100 wall hours. Not a one-session job.
Sustain sessions of 6-8 hours each across several work days, one
section at a time.

Priority order the user confirmed earlier in session 8:
1. ZTT — already done session 6-7
2. AI (`src/content/docs/ai/`) — mostly cited in session 7 but some thin
3. Prereqs (42 modules) — untouched
4. Linux — untouched
5. Cloud — partially touched in session 8
6. AI/ML Engineering (`ai-ml-engineering/`) — mostly session 8
7. Platform — mostly session 8
8. On-prem — untouched
9. Certifications — partially session 8

## pipeline_v4 for genuinely thin modules

~46 modules are in the "thin, no quiz" / "thin, no citations" bucket.
Those cannot be rescued by citation-only passes; they need body
expansion (narrative teaching, not appended sections). Issue #322
still carries the design. Memory note:
`feedback_teaching_not_listicles.md` captures the quality bar.

Do NOT start v4 until the v3 section-pool queue is drained, unless
you hit a hard blocker on the pipeline side.

# Known gotchas — revisited

- **Codex sandbox blocks outbound HTTP**: pool discovery MUST be
  invoked from a net-enabled session (main session or a danger-mode
  dispatch). Symptom: every URL falls through to `network_failure`
  in the pool's `rejected_urls` array.
- **PyYAML required**: use `.venv/bin/python`, never the homebrew
  `python3` shim. Pipeline fails fast now if yaml is missing (fixed
  in session 8 commit `5bce66b8`).
- **900s Codex dispatch hard-timeout**: large implementation tasks
  may need to be broken into phases. Codex's #324 draft hit the
  timeout mid-dogfood — the skeleton was done, the dogfood was not.
- **Worktree vs main mismatch**: pool files are written to
  `docs/citation-pools/` relative to CWD. If you invoke from a
  worktree, the file lands in the worktree. If from main, in main.
  No global path canonicalization yet.

# References

- [PR #324](https://github.com/kube-dojo/kube-dojo.github.io/pull/324)
- [Issue #323](https://github.com/kube-dojo/kube-dojo.github.io/issues/323)
- [Issue #322](https://github.com/kube-dojo/kube-dojo.github.io/issues/322) — v4 design
- Session 8 handoff: `docs/sessions/2026-04-20-session-8-handoff.md`
- Key new files: `scripts/section_source_discovery.py`,
  `scripts/pipeline_v3_section.py`, `docs/citation-pools/`
- Worktree: `.worktrees/section-source-pool` (delete after merge)
