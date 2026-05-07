# Local-API UI split — L0–L6 roadmap

**Date:** 2026-05-07
**Decision driver:** user pushback during session 5 — *"how can i navigate from the api ui main page to the channel? and why do we stack so many things in one page? should not we do it like learn-ukrainian project done it"*
**Pattern source:** [learn-ukrainian's dashboard router](https://github.com/anthropics/learn-ukrainian) — `scripts/api/dashboard_router.py` exposes ~10 dedicated routes (`/overview`, `/research`, `/track/{id}`, `/pipeline`, `/comms`, `/comms/conversation/{task_id}`, `/activity-config`, etc.) instead of one monolith.

## Context

Today (`scripts/local_api.py:7414`):

```python
if path in {"/", "/dashboard", "/quality-board"}:
    return 200, render_dashboard_html(), "text/html; charset=utf-8"
```

`/`, `/dashboard`, `/quality-board` ALL return the same `render_dashboard_html()` — 84KB single page, 226 structural elements (h2/h3/div/section), 14+ panels stacked: Operator triage, Readiness, Quality Board, Activity, Tracks, Services, V2 pipeline, Translations, Worktrees, Missing/dead-letters, Book progress, Completion, Reviews, Feedback. **Zero navigation links** — `grep -ciE "channel" /tmp/local-api-home.html` returns 0 hits. The only real second page is `/channels` (and its `/channels/<thread_id>` detail), shipped in PR #962.

Result: `/channels` is invisible from `/`. Discoverability is zero. Agents and humans both have to *know* the route to find it.

## Decision

Adopt learn-ukrainian's **route-per-concern** layout. Split the monolith into ~7 dedicated pages with a shared top nav.

| Phase | Issue | Scope (one-liner) | Effort |
|-------|-------|-------------------|--------|
| **L0** | [#973](https://github.com/kube-dojo/kube-dojo.github.io/issues/973) | Add top nav (sticky header) linking `/operator`, `/quality`, `/pipeline`, `/activity`, `/services`, `/channels`, `/health`. Stub each new route to render a placeholder + the nav. **Foundational gate — ships before L1.** | ~80 LOC |
| **L1** | [#974](https://github.com/kube-dojo/kube-dojo.github.io/issues/974) | Move Operator triage panel (`#op-now`, `#op-blocked`, `#op-next`) to dedicated `/operator` page. `/` keeps a 1-row summary card linking to it. | ~150 LOC |
| **L2** | [#975](https://github.com/kube-dojo/kube-dojo.github.io/issues/975) | Move Quality Board (`#quality-board`, `qb-*` filters, detail drawer) to `/quality` and `/quality/{module-key}`. Retire `/quality-board` URL alias to `/quality` (301). | ~250 LOC |
| **L3** | [#976](https://github.com/kube-dojo/kube-dojo.github.io/issues/976) | Move V2 pipeline + autopilot v3 health panels to `/pipeline`. Add a tail-N events feed. | ~150 LOC |
| **L4** | [#977](https://github.com/kube-dojo/kube-dojo.github.io/issues/977) | Move Activity feed (`/api/activity`) to `/activity` with track/agent filters. | ~120 LOC |
| **L5** | [#978](https://github.com/kube-dojo/kube-dojo.github.io/issues/978) | Move Services + Worktrees + Missing/dead-letters to `/health`. (Operational triage outside the daily flow.) | ~120 LOC |
| **L6** | [#979](https://github.com/kube-dojo/kube-dojo.github.io/issues/979) | Slim `/` to overview cards only. Each card = current state summary + link to its detail page. Drop the giant tables and inline filters. | ~200 LOC |

## Cross-validation

Not deliberated via `ab discuss` — the pattern is imported from learn-ukrainian which has been running it in production for months. The user explicitly asked for that model. ADR captures the import + sequence; if any phase surfaces a real architectural fork during implementation, escalate to `ab discuss`.

## Reviewer protocol — applies to every L-PR

Two additions on top of `docs/review-protocol.md`:

1. **Stale-content check.** Reviewer must verify that content/HTML/JS removed from `render_dashboard_html()` is genuinely no longer needed (or correctly relocated to its new page). No "// removed" comments, no orphaned JS state, no dead CSS rules. *(User instruction 2026-05-07: "make sure we dont have stale obsolote content".)*
2. **Live navigation check.** Reviewer must `curl http://127.0.0.1:8768/<new-route>` and confirm the route returns 200 with the expected page title, AND that the top nav from `/` links to it.

## Acceptance criteria for the roadmap as a whole

- `/` returns under 20KB (down from 84KB).
- Every panel currently on `/` exists at a dedicated route, linked from the top nav.
- `/channels` is reachable from the top nav (no longer invisible).
- All retained routes pass `python scripts/check_site_health.py` if applicable.

## Out of scope (explicit non-goals)

- No design-system migration (Tailwind, Tachyons, etc) — keep the existing CSS variables.
- No client-side router (HTMX, React, SPA) — server-rendered HTML per route.
- No new API endpoints — UI re-skin only; data sources unchanged.

## Pattern to repeat for future high-leverage UI moves

The pair (`docs/decisions/2026-05-07-deliberation-ui-roadmap.md` for `/channels` UI, this ADR for the local-API split) sets the precedent: when the user signals a UI direction, write the ADR + open one issue per phase + tag with a per-roadmap label, then dispatch phase 0 immediately.
