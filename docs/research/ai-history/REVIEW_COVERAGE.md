# AI History Review Coverage

`review_coverage` is the per-chapter audit block used to track whether AI
History research and prose reviews satisfy the cross-family rule for Issue #559.
It lives in each chapter status file:

`docs/research/ai-history/chapters/ch-NN-slug/status.yaml`

## Schema

```yaml
review_coverage:
  research:
    claude_anchor: done | pending | n/a
    gemini_gap: done | pending | n/a
    codex_anchor: done | pending | n/a
  prose:
    claude_source_fidelity: done | pending | n/a
    gemini_prose_quality: done | pending | n/a
    codex_prose_quality: done | pending | n/a
  cross_family_satisfied:
    research: true | false
    prose: true | false
    overall: true | false
  backfill_pending: true | false
  last_audited: 2026-04-29
```

Field values:

- `done`: the audit found the expected review marker.
- `pending`: the marker is expected but has not been found yet.
- `n/a`: that reviewer is not expected for this chapter or lane.
- `cross_family_satisfied.research`: true when the research lane has the two
  non-author reviewer families required by the chapter ownership model.
- `cross_family_satisfied.prose`: true when the prose lane has the two
  non-author reviewer families required by the chapter ownership model.
- `cross_family_satisfied.overall`: true only when both lanes are satisfied.
- `backfill_pending`: true exactly when `cross_family_satisfied.overall` is
  false.
- `last_audited`: date the block was last written by the audit script.

## Cross-Family Rule

Each lane needs at least one reviewer from each non-author model family.

Author mapping for this audit:

| Chapters | Author family | Required research markers | Required prose markers |
|---|---|---|---|
| Ch01-Ch15 | Claude | `codex_anchor`, `gemini_gap` | `codex_prose_quality`, `gemini_prose_quality` |
| Ch16-Ch72 | Codex | `claude_anchor`, `gemini_gap` | `claude_source_fidelity`, `gemini_prose_quality` |

Self-review markers may still be recorded as `done` when present, but they do
not satisfy the cross-family rule.

## Running The Audit

Run from the repository root:

```bash
.venv/bin/python scripts/audit_review_coverage.py
```

The script fetches merged PRs with `gh pr list`, reads PR comments with
`gh api`, detects marker tags, computes `review_coverage`, and prints a
summary table. It does not write files unless `--write` is passed.

To update chapter status files:

```bash
.venv/bin/python scripts/audit_review_coverage.py --write
```

Use strict mode when you want the command to fail instead of using the offline
fallback:

```bash
.venv/bin/python scripts/audit_review_coverage.py --strict-gh
```

This worktree could not reach `api.github.com` on 2026-04-29, so the initial
schema application used the script's conservative local fallback. Rerun with
GitHub access before relying on the audit as marker-authoritative.

## Generated Updates

This document defines the schema and audit workflow only. Do not hand-maintain
coverage tables here. Generated `review_coverage` blocks belong in chapter
`status.yaml` files and should be committed in a separate PR after running a
fresh audit from current `main` with `--write`.
