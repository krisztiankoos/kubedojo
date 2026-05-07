# Deliberation UI roadmap (D0–D6)

**Date:** 2026-05-07
**Channel:** `deliberation-ui-roadmap`
**Thread:** `a82ab60b4ce1457aa450f18dac7e8a54`
**Participants:** claude, codex, gemini (3 rounds, full convergence in round 3)
**External review:** learn-ukrainian project team — pushed back on the original framing

## Context

PRs #961 (channels API) + #962 (channels UI: card grid + per-thread Slack-like feed, XSS-safe) shipped 2026-05-07. Functional but minimal vs learn-ukrainian's `playgrounds/channels.html` (870 LOC, sidebar + post form + round indicator + discussion strip + delta-render). Question: how do we evolve `/channels` next?

## Original kubedojo proposal — what was wrong with it

Initial proposal pitched a 4-PR sequence (D1 router split → D2 chat shell → D3 Decision Graph as primary view → D4 lineage). Key claim: invert the chat-as-primary paradigm, make Decision Graph the default.

**Cross-family review caught three real flaws.**

### Learn-ukrainian's external pushback (paraphrased; full text in conversation log)

1. **"Decision Graph as primary view" is a category error.** Their channel mix is 70-30 conversational vs deliberative. Pipeline / content / shared / reviews are mostly chat. Inverting the default across all channels breaks the dominant traffic shape.
2. **Trace vs artifact conflation.** `ab discuss` thread = trace; `docs/decisions/<id>.md` = artifact. The thread should LINK to a decision, not BE one.
3. **Round-major 3-column grid fails on 2000-char bodies.** Implementation gotcha: ours typical round-1 replies are 1500-2500c. A 3-col grid of full bodies is unreadable. Counter: round-major HEADERS + body-diff modal on click.
4. **They want our chat shell features ported wholesale**: per-domain router, delta-render, monotonic counter, post form. Confirmation that PR #1732 (their version) was solid.

### Internal `ab discuss` deliberation (3 agents, 3 rounds)

Round 1: split positions.
- **claude:** D2 before D1 (user value first), 2-router cut, conditional-graph-default
- **codex:** D2 before D1 — flagged shipped contract drift in `scripts/local_api.py` (rename + body-storage bugs)
- **gemini:** Strict D1 first (zero-functional-change refactor), graph-as-emphatically-default

Round 2: codex changed mind toward strict D1-first (with a D0 contract fix in front); claude converged with codex; gemini was rate-limited (gemini-3.1-pro-preview "no capacity") and missed.

Round 3: full convergence on `[OPTION A′]`. All three agents posted `[AGREE]`. Gemini conceded both prior positions ("strict D1-first" and "graph-as-absolute-default") explicitly.

## Concrete bugs surfaced (mandate D0)

The deliberation forced us to look at shipped code, which uncovered three concrete contract drifts plus one DB-path drift discovered live during this orchestration:

| # | Bug | Location | Symptom |
|---|-----|----------|---------|
| 1 | `/api/channels` rollup emits `name`/`last_event_ts` | `scripts/local_api.py:2065`, `:2105` | Renderer reads `c.channel`/`t.last_ts` at `:7298` — silent rendering failure on non-empty data |
| 2 | Thread view expects `ev.body` for `reply_complete` | `scripts/local_api.py:7378` | Watcher only persists `agent`+`chars` at `_channels_watch.py:122` — message bodies never displayed |
| 3 | No `message_posted` event type | `_channels_watch.py:13` (`VALID_TYPES`) | D2's "post a human message" path has nowhere to write |
| 4 | API reads wrong DB | `_db.py:get_db()` returns `.mcp/servers/message-broker/messages.db`; `ab` CLI writes to `.bridge/messages.db` | Live verified: `/api/channels` returned `[]` while `.bridge/messages.db` had 10 messages |

**These four bugs make D1's refactor unsafe** — splitting around a broken contract just locks the bug in across more files. **D0 is non-negotiable and must precede D1.**

## Convergence — the agreed sequence

`D0 → D1 → D2 → D3 → D4 → D4.5 → D5 → D6`

| Phase | Scope | Effort | Status |
|-------|-------|--------|--------|
| **D0** | Fix the 4 contract drifts above. Add `message_posted` to `VALID_TYPES` with `body` payload field. Add a single regression test that posts to a channel via the bridge and reads it back via `/api/channels` (catches the DB-path drift). | ~80 LOC + 2 tests | **non-negotiable, ships first** |
| **D1** | Extract `scripts/local_api/routes/channels.py` only (codex's cut beats claude's 2-router). Add `importlib` compat shim so `tests/test_local_api*.py:15+` keep loading `scripts/local_api.py` directly. Pipeline + dashboard splits deferred until they have real new route surface. | ~250 LOC (mostly moves) | accepted |
| **D2** | Chat shell: sidebar + main pane + post form. Posts use `from_agent='user'` (already valid per `_channels.py:68`) + the new `message_posted` event from D0. Delta-render preserving scroll. Auto-tightening poll (5s idle → 1s on `reply_started`). | ~250 LOC HTML/JS + ~80 LOC backend + 3 tests | accepted |
| **D3** | Server-side `thread_summary` payload (rounds × agents × votes × cost) — **mandatory**, codex right that round geometry lives in `channel_messages.round_index`, not reconstructible from `channel_events` alone. Decision Graph view = round-major HEADERS + body-diff modal on click (per learn-ukrainian's pushback on long bodies). **Conditional default**: chat for in-flight; graph after final-round `[AGREE]` sweep OR Decision Card emission. NOT graph-as-absolute-default. | ~250 LOC HTML/JS + ~150 LOC backend + 4 tests | accepted (revised from original) |
| **D4** | Lineage only. Scan `docs/decisions/*.md` + `git log --grep='<decision-id>'` for backlinks. Render under each Decision Graph: "Influenced: PR #X, commit abc123, ...". `/decisions` index page lists all decisions with status. | ~150 LOC backend + ~100 LOC frontend + 3 tests | accepted |
| **D4.5** | ⌘K channel switcher + `j/k` message keyboard nav + `?` keybindings overlay. | ~100 LOC frontend + 1 test | accepted, low priority |
| **D5** | AFK-notify on Decision Card emission. Browser Notification API hook + `/api/decisions/pending` poll. Closes the loop where `docs/decisions/pending/` decisions get forgotten. | ~80 LOC | accepted, downstream |
| **D6** | Full-text search across decision cards + thread bodies (SQLite FTS5). Deferred until D4 establishes durable lineage to anchor results to. | ~100 LOC | accepted, last |

## Cross-validation: external and internal converged

Both critiques (learn-ukrainian + internal ab-discuss) independently arrived at the same core conclusion:

- **Decision Graph is a TOGGLE/conditional default, not a primary view.**
- **D4 (lineage scanner) is paradigm-independent and a clean win.**
- **Round geometry is right for deliberation threads SPECIFICALLY, not all channels.**

The convergence is itself signal — when independent reviewers (one external project, three internal agents with different priors) land in the same place, confidence is high.

## Acceptance criteria (per-phase)

Reproduced from agent positions; promoted to merge gates.

**D0:**
- [ ] `/api/channels` returns non-empty rollup against `.bridge/messages.db` (not `.mcp/...`).
- [ ] Renderer at `local_api.py:7298` reads field names that match server payload shape exactly.
- [ ] `message_posted` event type accepted by `append_channel_event`; `body` field round-trips through `read_channel_events`.
- [ ] Existing 6 channel tests still pass; 2 new tests cover D0 specifically.

**D1:**
- [ ] All `/api/*` endpoints byte-identical against a smoketest matrix (golden-file diff pre/post).
- [ ] `scripts/local_api.py` remains importable via `importlib` for existing tests.
- [ ] No new dependencies added.
- [ ] `tests/test_local_api*.py` passes unchanged.

**D2:**
- [ ] Posting via web form → event lands in DB with `from_agent='user'` and `message_posted` event type.
- [ ] Cross-browser: post in Chrome, see it in Firefox within 2s without refresh.
- [ ] Delta-render preserves scroll on append (verified at non-bottom).
- [ ] No regression on PR #962's XSS-escape tests.

**D3:**
- [ ] Graph renders correctly for the deliberation channel that produced THIS document (`deliberation-ui-roadmap` thread `a82ab60b...`).
- [ ] Toggle round-trips chat ↔ graph without state loss.
- [ ] Cost-per-round populated from `model_cascade` event payload.
- [ ] Threads with no votes show only chat (no broken graph rendering).
- [ ] Body-diff modal opens on vote-chip click; closes via X / Escape / backdrop.

**D4:**
- [ ] Lineage section appears under at least 1 historical Decision Graph with real PR/commit backlinks.
- [ ] `/decisions` index lists ≥2 decisions with status badges.
- [ ] Stale-decisions banner fires when `docs/decisions/pending/*.md` is >24h old.

## Open items (not blocking convergence)

- **D3 default mode (graph vs conditional).** Gemini owned the "emphatic graph default" position but missed round 2 due to gemini-3.1-pro-preview "No capacity available" 429s. Conceded in round 3 explicitly. Conditional ships unless gemini re-engages with new evidence after D3 lands and we have ≥10 real threads to evaluate.
- **Cross-project upstream.** Once D4 ships, send learn-ukrainian a `git diff` for upstream — closes the loop where they ported FROM us in #955 (bridge-watch) and we port TO them with the lineage scanner.

## GitHub issues (opened 2026-05-07)

| Phase | Issue | Status |
|-------|-------|--------|
| D0 | [#963 [D0] Channels contract bugfixes (gate to all UI/refactor work)](https://github.com/kube-dojo/kube-dojo.github.io/issues/963) | open, ships first |
| D1 | [#964 [D1] Extract routes/channels.py (incremental, not big-bang)](https://github.com/kube-dojo/kube-dojo.github.io/issues/964) | open, blocked by D0 |
| D2 | [#965 [D2] Channels chat shell + bidirectional posting](https://github.com/kube-dojo/kube-dojo.github.io/issues/965) | open, blocked by D0+D1 |
| D3 | [#966 [D3] Decision Graph view: thread_summary + conditional default](https://github.com/kube-dojo/kube-dojo.github.io/issues/966) | open, blocked by D0+D1+D2 |
| D4 | [#967 [D4] Decision lineage scanner + /decisions index](https://github.com/kube-dojo/kube-dojo.github.io/issues/967) | open, blocked by D0–D3 |
| D4.5 | [#968 [D4.5] Channels keyboard navigation](https://github.com/kube-dojo/kube-dojo.github.io/issues/968) | open, low priority |
| D5 | [#969 [D5] AFK-notify on Decision Card emission](https://github.com/kube-dojo/kube-dojo.github.io/issues/969) | open, blocked by D4 |
| D6 | [#970 [D6] FTS5 search across decisions + thread bodies](https://github.com/kube-dojo/kube-dojo.github.io/issues/970) | open, last in sequence |

All 8 share label `deliberation-ui-roadmap` for grouping.

## References

- ADR pattern: `.claude/rules/decision-card.md`
- Thread transcript: SQLite `.bridge/messages.db`, channel `deliberation-ui-roadmap`, thread `a82ab60b4ce1457aa450f18dac7e8a54`
- External pushback: in conversation log 2026-05-07 (learn-ukrainian team)
- Concrete bug locations: `scripts/local_api.py:2065`, `:7298`, `:7378`; `scripts/ai_agent_bridge/_channels_watch.py:13`, `:122`; `scripts/ai_agent_bridge/_db.py:get_db()`
- Predecessor decisions: `docs/decisions/2026-05-05-phase-e-scope.md`
- Convention source: `feedback_ab_discuss_for_decisions.md` (memory)
