# Session handoff — 2026-04-29 — Ch01 reader-aid prototype + Tier 1/2/3 pattern frozen

> Picks up after the overnight Parts 3/6/7 handoff. Established the canonical reader-aid layout for the AI history book, shipped the Ch01 prototype, fixed math rendering site-wide. Codex's autonomous chain quietly closed Part 8 (Ch50-58) during the session.

## What was decided

1. **Tier 3 reader-aid coeditor pattern: Claude proposes, Codex reviews adversarially, Gemini for tie-breaks.** Decided after explicit Codex consult (task `394-tier3-coeditor-consult`). Codex pushed back on the "Claude is best at refusal" framing as untested without calibration data; agreed Claude has the strongest literary instinct of the three for "is this sentence quotable" judgment but pairing with adversarial Codex review prevents Claude self-bias and Codex over-systematization. Memory: `feedback_tier3_coeditor_pattern.md`. Issue #564 updated.

2. **Reader-aid layout (Tier 1 + 2 + 3) frozen via Ch01 prototype.** Non-invasive — every existing prose body remains bit-identical; aids live in callouts/accordions/Mermaid blocks before and after the prose. Tier 1 (every chapter): TL;DR `:::tip`, cast `<details>`, timeline `<details><Mermaid>`, glossary `<details>`, "still matters" `:::note`. Tier 2 (math/architecture-heavy chapters): math sidebar `<details>` with `$...$` notation, architecture sketches via Mermaid. Tier 3 (selective): `:::tip[Plain reading]` after dense paragraphs, pull-quote sidebar after source paragraph (only when chapter has *the line*), inline definitions skipped (Starlight has no Tooltip component; HTML `<abbr>` violates bit-identity). Canonical doc: `docs/research/ai-history/READER_AIDS.md`. Memory: `project_ai_history_reader_aids.md`.

3. **Reader-facing book index.** `src/content/docs/ai-history/index.md` no longer carries the internal scaffolding (lifecycle table, role split, agent-collaboration notes, per-part Research/Prose/Orchestrator lines, Drafted/Lifecycle columns, Roll-up table). Now shows: era summary per part, chapter list with links, "(coming soon)" markers for unpublished chapters, single-line completion roll-up.

4. **Codex `mode="danger"` rule** for end-to-end dispatches. When a Codex dispatch ends in `git push` + `gh pr create`, use `mode="danger"`, not `"workspace-write"`. Workspace-write silently fails on `.git/worktrees/.../index.lock` and `api.github.com` — `ok=True` returns but no commit/PR. Memory: `feedback_codex_danger_for_git_gh.md`. Discovered live on the schema dispatch (#567) — recovered by committing manually from outside the sandbox, then patched the rule.

5. **Math rendering enabled site-wide.** `remark-math` + `rehype-katex` wired into Astro markdown plugins, `katex/dist/katex.min.css` added to Starlight `customCss`. Fixes inline `$x$` and display `$x^2 = x$` math across every chapter retroactively, not just the Tier 2 sidebar in Ch01 that surfaced the bug.

## Contract changes (files touched)

| Path | Change |
|---|---|
| `astro.config.mjs` | + remark-math + rehype-katex plugins; + KaTeX CSS to customCss |
| `package.json` / `package-lock.json` | + remark-math, rehype-katex, katex (devDependencies) |
| `scripts/dispatch_prose_review.py` | + dedicated `gemini_prose_quality_prompt()`; + main-fallback when prose branch deleted post-merge |
| `scripts/local_api.py` | + `_count_review_backfill_pending()` (only on the open PR #567 branch — not yet merged) |
| `scripts/audit_review_coverage.py` | NEW — deterministic audit script (only on PR #567 branch) |
| `docs/research/ai-history/READER_AIDS.md` | NEW — canonical reader-aid layout for chapters 2-72 |
| `docs/research/ai-history/REVIEW_COVERAGE.md` | NEW — review-coverage schema docs (only on PR #567 branch) |
| All chapter `status.yaml` files | + `review_coverage` block (only on PR #567 branch — 30 chapters marked `backfill_pending: true` per offline-fallback audit) |
| `src/content/docs/ai-history/index.md` | Reader-facing rewrite |
| `src/content/docs/ai-history/ch-01-the-laws-of-thought.md` | + Tier 1 + 2 + 3 reader aids (prose body bit-identical) |

## What shipped on main this session

```
8c93d8db fix(site): render LaTeX math with remark-math + rehype-katex (#561)
49e8e299 docs(ai-history): Tier 1 + 2 + 3 reader aids — Ch01 prototype (#561, #564) (#566)
610c6072 fix(dispatch): fall back to main when prose branch is gone (#559)
352189d0 docs(ai-history): make book index reader-facing (#394)
c079593c fix(dispatch): dedicated gemini_prose_quality_prompt for prose review (#394)
```

Plus Codex's autonomous chain closed Part 8 entirely:

```
5fb69bd9 docs(ai-history): publish ch58 math of noise (#394)
bdf9be82 docs(ai-history): publish ch57 alignment problem (#394)
9cea0338 docs(ai-history): publish ch56 megacluster (#394)
043bd41e docs(ai-history): publish ch55 scaling laws (#394)
c9d93815 docs(ai-history): publish ch54 hub of weights (#394)
b94cbc6c docs(ai-history): publish ch53 few-shot learning (#394)
c342d343 docs(ai-history): publish ch52 bidirectional context (#394)
90d2b692 docs(ai-history): publish ch51 open-source distribution layer (#394)
```

**58 of 72 chapters now on main.** Part 9 (Ch59-72, 14 chapters) is the only remaining lift on the book.

## Open PRs

| PR | Topic | State | Action needed |
|---|---|---|---|
| **#567** | Review-coverage schema (#559) | OPEN | Merge after a quick review; then re-run `audit_review_coverage.py` with live `gh` access (initial audit ran in offline-fallback mode) |
| #558 | Ch51 prose | STALE | Ch51 already on main as `90d2b692`; close or rebase the index.md change to the reader-facing format |
| #565 | Ch52 prose | STALE | Ch52 already on main; the file content also accidentally landed via `610c6072` then properly via `c342d343`. Close once you confirm no diff |

## Issues opened (sub-issues of #394)

- **#559** — Cross-family review backfill (Ch01-31, 28 chapters)
- **#560** — Review standard for Parts 8-9 forward
- **#561** — Ch01 reader-aid prototype ✅ shipped
- **#562** — Tier 1 rollout (Ch01-72)
- **#563** — Tier 2 math + architecture sidebars (~15 target chapters)
- **#564** — Tier 3 selective passes (Claude proposes / Codex reviews)

## Cold-start smoketest (executable)

```bash
# 1. Briefing API + git state + open PRs in one go:
curl -s http://127.0.0.1:8768/api/briefing/session?compact=1 | python3 -c "import json,sys; b=json.load(sys.stdin); print('alerts:', b['alerts']); print('actions.next:', b['actions']['next'][:3]); print('review_backfill (after #567 merges):', b.get('review_backfill','not yet'))"
git log --oneline -8
gh pr list --state open --search '#394' --limit 10

# 2. Confirm math renders on Ch01 (after the deploy lands):
curl -s 'https://kube-dojo.github.io/ai-history/ch-01-the-laws-of-thought/' | grep -c 'class="katex'
# Expect: 21+

# 3. Confirm reader-aid layout in repo:
ls docs/research/ai-history/READER_AIDS.md
head -1 src/content/docs/ai-history/ch-01-the-laws-of-thought.md
# Expect: ":::tip[In one paragraph]" appears in the body
grep -c ':::tip\|:::note\|<details>\|```mermaid' src/content/docs/ai-history/ch-01-the-laws-of-thought.md
# Expect: 8+ (TL;DR + 4 details + 2 Tier 3 tips + still-matters)
```

## What's next

The work breaks into three parallel lanes that the next session can pick up in any order:

1. **Backfill cross-family reviews on Ch01-31** (#559). Loop:
   ```python
   # After #567 lands:
   .venv/bin/python scripts/audit_review_coverage.py  # refresh with live gh
   # Then for each ch with backfill_pending=true:
   .venv/bin/python scripts/dispatch_prose_review.py <pr_num> --reviewer <missing_family>
   ```
   The fallback-to-main fix already lands; Ch01 was the first one done (Gemini prose-quality posted on PR #477).

2. **Tier 1 batch rollout to Ch02-72** (#562). Per-chapter dispatch (Codex writes from contract, Claude reviews source-fidelity). One-shot per chapter; the template is frozen in `READER_AIDS.md`. Roll out by part.

3. **Tier 2 math + architecture sidebars** on the targeted chapters (#563). Math sidebars: Ch04, Ch15, Ch24, Ch25, Ch27, Ch29, Ch44, Ch50, Ch55, Ch58. Architecture sketches: Ch41, 42, 49, 50, 52, 58.

After 1-3 settle, **Tier 3 selective passes** (#564) using the Claude-proposes / Codex-reviews pattern. Ch01 prototype shows ~40% acceptance rate (2 of 5 candidates landed); expect similar across other chapters.

## Cross-thread updates (for STATUS.md)

- DONE this session, drop from cross-thread notes:
  - Cosmetic backlog (`gemini_prose_quality_prompt` extracted)
  - Stale Gemini worktrees (3 deleted in worktree, 10 deleted as branches local + origin)
  - Codex Part 8 chain (closed — all 9 chapters on main)
- ADD to cross-thread notes:
  - **Reader-aid layout**: canonical pattern in `READER_AIDS.md`. Tier 3 uses Claude-proposes / Codex-reviews coeditor pattern. Bit-identical prose body is a hard rule.
  - **Math rendering live**: `remark-math` + `rehype-katex` + KaTeX CSS. `$inline$` and `$$display$$` LaTeX both work.
  - **Codex Part 9 chain still going** (`codex resume 019dcbc8-...`). Ch59-72, 14 chapters. Don't disturb.

## Cleanup items still pending

- **PR #558 (Ch51) + PR #565 (Ch52)** — both stale, content already on main. Close or rebase before next prose chain ships.
- **Reader-aid component DX** — for the math sidebar specifically, a custom `<MathSidebar>` component would let chapters call `<MathSidebar>...$x^2=x$...</MathSidebar>` instead of the wordy `<details><summary><strong>The math, on demand</strong></summary>...`. Optional polish; not blocking.
- **Tier 3 inline-definition mechanism** — Starlight has no Tooltip component. If the user wants inline definitions later, options are: (a) add a Tooltip component to `src/components/`; (b) accept HTML `<abbr title="...">word</abbr>` and relax the bit-identical-prose rule for that one element. Decided to skip in the prototype; document in #564 that this needs a design call.

## Pace data

- Cold start (briefing + git + state read): ~5 min
- Issue creation + index cleanup + cosmetic dispatch fix + commits: ~20 min
- Tier 1+2 dispatch (headless Claude, claude-opus-4-7, ~40 min hard timeout): ran in ~25 min
- Tier 3 dispatch (Claude proposes + ab ask-codex review + apply): ran in ~25 min
- Codex coverage-schema dispatch (failed sandbox, recovered manually): ~5 min for the dispatch + ~3 min for manual recovery
- Math renderer fix (npm install + config + build verify + commit): ~5 min inline

Total session: ~3h 30min, including the sandbox recovery delay.
