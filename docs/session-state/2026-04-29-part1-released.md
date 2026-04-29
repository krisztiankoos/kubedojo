# Session handoff — 2026-04-29 night — Part 1 released to main

> Picks up after the same-day evening session that PR-completed the Part 1 reader-aid rollout. This night session shipped the right-nav-section-header fix across all of Part 1 (Ch01 + Ch02–Ch09) and **merged all 9 PRs to main**. Part 1 is now publicly readable end-to-end with reader aids + working right-nav table-of-contents.

## What was decided

User caught a structural bug while reviewing Ch01 on the live site: the right-nav showed only "Overview" instead of section headings. Investigation revealed **Ch01, Ch03, Ch04, Ch05, Ch06, Ch07, Ch08, Ch09 all lacked any `##` section headers** in their prose body. Ch02 had 4 already; Ch10–Ch14 and Ch17+ were unaffected because they were drafted via a different prose pipeline that included scene-named headers from the start.

Decisions:
1. **Section headers are not a violation of the bit-identity rule.** The rule applies to prose body unchanged; adding `##` headings between paragraphs at scene boundaries is a structural addition, not a textual edit. The pattern was already established by Ch02, Ch10, Ch11, etc.
2. **Header titles come from `brief.md` scenes outline.** Each chapter's brief lists 4–5 scenes; the opening prose covers Scene 1 and the rest become `##` sections.
3. **Land headers on the existing reader-aid PR branches before merging.** Each open PR (Ch02–Ch09) got a follow-up commit adding scene-section headers. Ch01 got a fresh branch (PR #593) since it was already on main.
4. **Earlier framing — "tier 3 land rate is too low, drop the ceremony" — was a misread.** User clarified: keep the `Ch01 quality` standard (Tier 1 + Tier 2 where applicable + Tier 3 where genuine candidates exist; refusal-default is fine for SKIP cases). Don't lower the bar. The tier3-proposal.md / tier3-review.md cycle stays.

## What shipped on main this session

```
e538df4b Merge pull request #592 from kube-dojo/claude/394-ch09-reader-aids
6c28d0b3 Merge pull request #591 from kube-dojo/claude/394-ch08-reader-aids
e0eb884f Merge pull request #588 from kube-dojo/claude/394-ch07-reader-aids
9bbbc3db Merge pull request #583 from kube-dojo/claude/394-ch06-reader-aids
6c691f30 Merge pull request #581 from kube-dojo/claude/394-ch05-reader-aids-v2
dce1c6a0 Merge pull request #579 from kube-dojo/claude/394-ch04-reader-aids
5736f022 Merge pull request #582 from kube-dojo/claude/394-ch03-reader-aids-v2
164f1153 Merge pull request #577 from kube-dojo/claude/394-ch02-reader-aids
ac50a242 Merge pull request #593 from kube-dojo/claude/394-ch01-section-headers
```

Section-header verification on `main`:

| Chapter | `##` sections |
|---|---|
| Ch01 The Laws of Thought | 3 |
| Ch02 The Universal Machine | 4 |
| Ch03 The Physical Bridge | 4 |
| Ch04 The Statistical Roots | 4 |
| Ch05 The Neural Abstraction | 4 |
| Ch06 The Cybernetics Movement | 4 |
| Ch07 The Analog Bottleneck | 4 |
| Ch08 The Stored Program | 4 |
| Ch09 The Memory Miracle | 4 |

Total: **35 `##` sections across Part 1**, plus reader aids (TL;DR + Cast + Timeline + Glossary + "Why this still matters") on every chapter, plus the Tier 2 math sidebar on Ch04, plus the Tier 3 absorption-law plain-reading on Ch03.

`npm run build` runs clean: 1941 pages built in 38.53s.

Codex's Part 9 chain still past Ch65 (no new chapters landed during this session).

## Cold-start smoketest (executable)

```bash
# 1. Confirm Part 1 chapters all have section headers:
for f in src/content/docs/ai-history/ch-0*-*.md; do printf "%-50s %s\n" "$(basename $f)" "$(grep -c '^## ' $f)"; done

# 2. Confirm we're on main and clean:
git status -sb
git log --oneline -10

# 3. Build verify:
npm run build 2>&1 | tail -3

# 4. Optional — pop dashboard stash:
git stash list
# git stash pop  # only if user asks
```

## What's next (lanes the next session can pick up in any order)

1. **Part 2 reader-aid rollout (Ch10–Ch17).** Same per-chapter playbook but with the `##` section-header step *combined* with the reader-aid commit (don't split into two PRs). Ch10–Ch14 and Ch17 already have scene-named headers from their drafting pipeline — they need only Tier 1 + Tier 2 (Ch15 only) + Tier 3 added on top. Ch15 and Ch16 lack section headers — those need both the headers and reader aids.
2. **Pop the dashboard stash** if the user wants the WIP back: `git stash list` shows `WIP: book progress + module distribution dashboard panels (paused for Part 1 reader-aid rollout)`.
3. **Tier 3 calibration takeaway for Part 2**: refusal is a valid default but propose any genuine candidates rather than reflexively writing 3 SKIPs. Calibration so far: 3 of 26 candidates landed (Ch01 2/5; Ch03 1/3; everything else 0/0–0/4).
4. **Stale cleanup still pending** (not touched this session):
   - PR #558 (Ch51 stale prose), PR #565 (Ch52 stale prose) — content already on main; close-or-rebase the index.md changes.
   - PR #567 (review-coverage schema) — open, ready to review; after merge re-run `scripts/audit_review_coverage.py` with live `gh`.

## Cross-thread updates (for STATUS.md)

- **DROP** from cross-thread notes:
  - "Part 1 reader-aids rollout PR-complete (8 of 8 PRs open, awaiting review/merge)" → replace with **"Part 1 reader-aids RELEASED on main (Ch01 prototype + Ch02–Ch09 + section-header fix on Ch01–Ch09)"**.
- **ADD** to cross-thread notes:
  - **Section-header layout pattern**: chapters lacking `##` sections need them inserted at brief.md scene-boundaries. Ch15, Ch16 in Part 2 are the next candidates.
  - **Combine section-header + reader-aid on a single PR** for Part 2+. Don't split into two operations.
- **Codex Part 9 chain location**: still past Ch65 (no new chapters landed during this session).

## Pace data

- Cold start (briefing + git + handoff read): ~1 min — the playbook was in active context from the previous session
- Per-chapter section-header insertion: 4 Edit calls + commit + push, ~3 min wall-clock per chapter
- Total for 9 chapters (Ch01–Ch09): ~30 min including branch switches
- 9 PRs merged in chapter order: ~30 s wall-clock (`gh pr merge --merge` × 9)
- Build verify on main post-merge: 38.53 s
- Total session: ~75 min from "I found a bug" to "Part 1 released"
