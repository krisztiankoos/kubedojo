# Brief — Make `/artifacts` UI a unified HTML + Markdown browser

**Date:** 2026-05-09
**Author:** Claude (orchestrator) on behalf of user
**Target agent:** codex-desktop (UI/UX revamp owner per project convention — see memory `reference_codex_desktop_web_ui_tools.md`)
**Repo root:** `/Users/krisztiankoos/projects/kubedojo`
**Local API:** `http://127.0.0.1:8768/` (single-file Python: `scripts/local_api.py`, stdlib `BaseHTTP`)

> **Format note:** Markdown is the correct format for this brief per the consumer-direction lens in `feedback_html_over_markdown_for_artifacts.md` — dispatch briefs are AI→AI artifacts (consumed by the target agent, not by the user), so Markdown wins on parse cost with no readability loss for the consumer.

## Context (what exists now)

PR #1023 shipped the `/artifacts` route — it lists HTML files under `audit/` + `docs/migrations/` + `docs/session-state/` + `docs/references/` and serves them statically at `/artifacts/<path>`. It does NOT render Markdown artifacts at all. We are mid-migration to HTML-first orchestrator artifacts (see `docs/migrations/html-first/plan.html` for the locked policy and matrix), but ~95 % of `docs/**/*.md` will stay Markdown indefinitely (STATUS.md, decision cards, research notes, session handoffs that didn't merit HTML, etc.). Per-file triage is happening separately in [#1058](https://github.com/kube-dojo/kube-dojo.github.io/issues/1058) with a Gemini-led audit.

So the UI needs to serve **both** artifact families from one place, not just the HTML side. Right now the user has to `cat` markdown files in a terminal — that's the gap.

## Concrete goal (acceptance criteria)

A user opens `http://127.0.0.1:8768/artifacts` and:

1. **Sees a unified, categorized index of every HTML and Markdown artifact** under `audit/`, `docs/migrations/`, `docs/session-state/`, `docs/decisions/`, `docs/sessions/`, `docs/research/`, `docs/audits/`, `docs/references/`, `docs/briefs/`, and top-level `docs/*.md`. Categorized by directory; per-category collapsible if it improves scan-ability.
2. **Click an HTML artifact** → renders as HTML in the browser (current behavior, preserved).
3. **Click a Markdown artifact** → renders as styled HTML server-side (use Python `markdown` lib if available, or a vendored single-file renderer — no npm/build step). Code blocks syntax-highlighted (pygments is fine; already a transitive dep). Keep the dashboard's dark theme.
4. **Lightpanda renders cleanly** — `lightpanda fetch --dump markdown http://127.0.0.1:8768/artifacts/<path>` returns sensible markdown for cross-family review (per memory `reference_lightpanda_html_rendering.md`).
5. **No regression** on existing dashboard routes: `/`, `/quality`, `/pipeline`, `/activity`, `/health`, `/channels`, `/decisions`, `/api/*` — all must respond with the same body bytes (modulo unrelated changes).

## In scope

- Edits to `scripts/local_api.py` (single-file Python — keep it that way).
- Server-side Markdown → HTML render (with a small per-render cache keyed on file mtime).
- Sidebar nav, breadcrumbs, search-within-file (only if ≤ 50 LOC; skip otherwise).
- CSS — inline-copy from `docs/migrations/html-first/_design-system.html` (canonical variables). Match the topnav from existing dashboard pages.
- Update `/api/schema` entry for `/artifacts` to mention markdown rendering.

## Out of scope (do NOT do)

- No build system, no npm/yarn, no JS bundler. Vanilla JS + inline CSS only.
- No migration of markdown files to HTML — that's [#1058](https://github.com/kube-dojo/kube-dojo.github.io/issues/1058)'s job, not this one.
- No changes to the JSON API schema or any `/api/*` endpoint shape.
- No new dependencies in `requirements.txt` beyond what's already imported elsewhere in the repo (check first: `grep -rn "^import\|^from" scripts/`).
- No restart-required behavior beyond what we have today — the existing API process model is "edit + restart"; don't introduce hot-reload.

## Files to read first

| File | Why |
|---|---|
| `scripts/local_api.py` | Existing `/artifacts` impl (`build_artifacts_index`, `render_artifacts_index_html`, route table near `_render_top_nav`); the topnav helper to reuse |
| `docs/migrations/html-first/plan.html` | Locked migration matrix — what artifact classes exist |
| `docs/migrations/html-first/_design-system.html` | CSS variables to inline (canonical source) |
| `audit/388-cka-part1-batch/index.html` | Style reference for what HTML artifacts look like |
| `audit/388-cka-part2-batch/index.html` | Just-shipped second exemplar |
| `STATUS.md` | A representative Markdown artifact you'll need to render well |
| `docs/decisions/` | Markdown decision cards — also need to render well |

## Smoke tests (run before declaring done)

```bash
# 1. Server starts and /artifacts responds 200
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8768/artifacts

# 2. An HTML artifact still renders
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8768/artifacts/audit/388-cka-part2-batch/index.html

# 3. A Markdown artifact renders as HTML (Content-Type: text/html)
curl -sI http://127.0.0.1:8768/artifacts/STATUS.md | grep -i content-type

# 4. Lightpanda renders the index cleanly
lightpanda fetch --dump markdown http://127.0.0.1:8768/artifacts | head -20

# 5. No dashboard regression — these must all return 200
for p in / /quality /pipeline /activity /health /channels /decisions /api/schema /api/briefing/session; do
  printf "%-30s %s\n" "$p" "$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8768$p)"
done
```

## Deliverable

- One PR titled `feat(local-api): /artifacts unified HTML + Markdown browser (HTML-first migration #5)`.
- PR body: link this brief, list the 5 acceptance criteria with check-marks, paste the smoke-test transcript.
- Cross-family review: dispatch to gemini-3-flash-preview via `lightpanda` rendering of changed routes (per project convention) — do NOT dispatch claude headless for this review (claude budget is for orchestration).

## Notes on existing rules to honor

- `feedback_html_artifacts_via_local_api.md` — local API is the canonical serving path; this PR formalizes that for both formats.
- `reference_lightpanda_html_rendering.md` — your reviewer reads via lightpanda; design with that in mind.
- `feedback_deterministic_over_hallucination.md` — any counts, sizes, file lists in the new UI must come from `os.scandir` / `os.stat` at request time, not be cached or hand-curated.
- `feedback_codex_budget_prefer_gemini.md` — codex weekly is thin; pick gemini-3-flash-preview for the cross-family review pass, not codex.
