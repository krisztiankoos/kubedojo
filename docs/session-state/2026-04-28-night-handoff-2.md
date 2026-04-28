# Session handoff — 2026-04-28 night #2

> Extracted from STATUS.md during the 2026-04-28 index migration. The original "## Active Work" section starts below verbatim.

## Active Work (2026-04-28 night handoff #2 — Parts 3/6/7 finish queue, in that order)

**User directive received ~8:00 PM CEST (verbatim)**: *"focus on finishing part 3 then part 6 and part 7 but first a session handoff"*

This re-prioritizes the cold-start function. Authoritative ordering:
1. Part 3 finish (Ch15 cosmetic + Ch16 full pipeline)
2. Part 6 finish (Ch38, Ch39, Ch40 full pipeline — replace stub prose)
3. Part 7 (Ch41-49 full pipeline — replace stubs where present, draft where not)

**Branch at handoff**: `main` at `5603ed04` (clean apart from `scripts/local_api.py` user-side dashboard panel edits and orphan `test_rendering.js`; both pre-existing, leave alone).

### STEP 0 — PRECONDITION before ANY verdict pass on Codex-authored research

`scripts/dispatch_research_verdict.py` currently hardcodes only Codex (anchor verification) + Gemini (gap audit) reviewers. For Codex-authored research (Ch16, Ch38-40, Ch41-49 — all upcoming), default invocation = Codex reviewing itself = violates the cross-family rule in `docs/review-protocol.md`. `--only gemini` falls back without anchor verification (the exact gap that got Gemini banned per #421).

**Fix needed (~30-60 min, untestable end-to-end until the first Codex Part 7 PR exists)**:
1. Add `claude_anchor_prompt(slug, contract)` in `scripts/dispatch_research_verdict.py` mirroring `codex_prompt` (Claude has the same shell tooling: curl, pdftotext, pdfgrep).
2. Add `fire(agent="claude", ...)` branch using `claude-opus-4-7`, timeout 1500.
3. In `process_one()`, auto-detect from `meta["headRefName"]` prefix:
   - `claude/394-chNN-research` → use Codex for anchors (current behavior, unchanged)
   - `codex/394-chNN-research` → use Claude for anchors (new path)
   - Gemini gap audit runs unchanged in both branches (always cross-family to both authors).
4. Add `"claude"` to `--only` choices so manual override is available.
5. Smoke-validate: `--help` parse + ruff/AST + dry-fire on the first Part 7 PR with `--no-post` (or wrap the dispatch and inspect the would-be comment body before letting it post). DO NOT ship a half-tested verdict pass into the overnight Part 7 chain.

**If time is tight**: run `--only gemini` for Codex-authored verdict passes and accept no anchor verification. This is a regression. Don't ship Part 7 prose without anchor verification.

### 1. Part 3 finish (~5 min cosmetic + ~1.5 h Ch16)

**Quick wins (cosmetic index fixups, direct push to main)**:
- Flip Ch15 Drafted column in `src/content/docs/ai-history/index.md`: `| 15 | The Gradient Descent Concept | accepted | no |` → `| 15 | The Gradient Descent Concept | accepted | [yes](./ch-15-the-gradient-descent-concept/) |`. Prose was deployed today as PR #506; tonight's roll-up regex only touched the Lifecycle column.
- Flip Ch17–23 Drafted column from bare `yes` → `[yes](./ch-NN-slug/)`. Verified this session: prose files exist on disk (`src/content/docs/ai-history/ch-17-the-perceptron-s-fall.md` etc., all 26-28KB, dated 2026-04-28 morning). Index just lacks the markdown link syntax — Parts 1/2/3/5/6 all use `[yes](link)` form. Same direct-push pattern as `df95b0f9`.

**Ch16 — full research → prose pipeline (~1.5 h)**:
- Status: `researching`, no contract on disk. Per the 2026-04-29 split Codex was research lead for Parts 3/6/7 (Claude orchestrates) — user's "finish part 3" directive authorizes Claude to dispatch Codex via `dispatch_chapter_research.py`.
- Dispatch: `.venv/bin/python scripts/dispatch_chapter_research.py 16 --slug ch-16-the-cold-war-blank-check --agent codex`. Builds contract on `codex/394-ch16-research` branch + opens PR.
- Verdict: requires STEP 0 done. Then `dispatch_research_verdict.py PR_NUM` (auto-routes Claude for anchors, Gemini for gap).
- Merge research → `prose_ready` → `dispatch_chapter_prose.py 16 --slug ch-16-the-cold-war-blank-check --research-branch main --cap-words <from verdict notes>` → dual prose review → fix-pass → merge → roll-up.

### 2. Part 6 finish (Ch38, 39, 40 — ~3-4 h total)

Same end-to-end pipeline as Ch16, three times. Each chapter starts at `status: researching` with NO contract on disk.

**Important — existing stub prose**: Ch38-40 have 743w / 801w / 957w prose files on disk dated 2026-04-27 (pre-anchored-pipeline drafts, ~5x shorter than proper Part 6 chapters which average 4,000 words). The dispatcher's prompt is explicit about replacing legacy prose on main, so these will be overwritten cleanly when the new pipeline runs.

For each Ch in 38, 39, 40 (sequential, NOT parallel — codex dispatches must be sequential per `feedback_codex_dispatch_sequential.md`):
1. `dispatch_chapter_research.py NN --slug ch-NN-... --agent codex` → contract PR on `codex/394-chNN-research`
2. `dispatch_research_verdict.py PR_NUM` → posts Claude (anchor) + Gemini (gap) reviews
3. Apply any verdict fix-passes; merge research PR
4. `dispatch_chapter_prose.py NN --slug ... --research-branch main --cap-words N --verdict-notes-pr PR_NUM` → Gemini draft + Codex expand
5. Push prose branch, open PR, fire `dispatch_prose_review.py PR --reviewer claude` and `--reviewer gemini` in parallel
6. Apply inline fix-pass, merge

After all three: one Part 6 supplemental roll-up commit (Ch38-40 → `accepted` in index.md).

### 3. Part 7 (Ch41-49 — 9 chapters, ~12-15 h overnight chain)

Run end-to-end per `feedback_overnight_autonomous_codex_chain.md`. Same per-chapter recipe as Part 6.

**Ch41 stub (699w) and Ch43 stub (695w)** exist on disk; same pre-anchored vintage. Will be replaced.

Order: Ch41 → 42 → 43 → 44 → 45 → 46 → 47 → 48 → 49 sequential. After all nine: Part 7 roll-up.

### Pro-preview model availability

`gemini-3.1-pro-preview` was hung on both API key and OAuth/subscription paths around 6:00 PM CEST tonight. Smoke-test before each session-fresh batch:

```bash
timeout 30 gemini -m gemini-3.1-pro-preview -p "Reply with the single word: pong"
```

If pro is healthy → drop the env vars, use defaults.
If pro still hangs → use the env overrides as during tonight's Ch33-37 batch:
```bash
export KUBEDOJO_GEMINI_DRAFT_MODEL=gemini-3-flash-preview
export KUBEDOJO_GEMINI_REVIEW_MODEL=gemini-3-flash-preview
```

The override is now committed in `dispatch_chapter_prose.py:436-441` (mirrors `dispatch_prose_review.py:298`).

### Ownership question to flag (do not block — proceed unless user objects)

The 2026-04-29 Part split (memory `project_ai_history_research_split_2026-04-28.md`) had Ch16 explicitly Codex-owned with "Claude orchestrates" framing. User's "finish part 3" directive doesn't change ownership — Codex still does the writing via dispatch — but means Claude takes orchestrator responsibility for Ch16 instead of waiting on Codex's own schedule. Same logic applies to Ch38-40 (Part 6) and Ch41-49 (Part 7). If user wanted Claude to author the research himself, they would say so; otherwise dispatch to Codex per the existing split.

---
