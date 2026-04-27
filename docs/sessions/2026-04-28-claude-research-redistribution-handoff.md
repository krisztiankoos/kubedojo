# Session handoff — 2026-04-28 — research redistribution + Ch11-14 prose_ready

Audience: the next Claude session that picks up the AI History book (Epic #394).

This continues `2026-04-27-claude-part3-post-decomposition-handoff.md`. Two big things landed this session:

1. **Ch11-14 dual-verdict pass complete and merged.** All four research-phase PRs (#443-#446) now at `prose_ready` on main with word caps from the dual-reviewer verdict.
2. **Research duties taken off Gemini.** After his self-admitted URL/anchor hallucination across 37 chapters (epic commit `03640e20`, Issue #421), the user redistributed research between Claude and Codex. Documented, ACK'd by both peers, memory saved.

## State at handoff

### Public-facing
- `/ai-history/` is now a real landing page (was 404). Status board renders 68 chapters across 9 parts with `Research: X · Prose: Y` headers per part. Lifecycle column shows `prose_ready (cap N,NNN)` for Ch11-14.
- Roll-up: 5 `accepted`, 3 `prose_review`, 4 `prose_ready`, 3 `capacity_plan_anchored`, 22 `researching` with legacy prose, 31 not yet drafted.

### Part 3 (Claude-owned research)
- Ch11-14 research contracts merged with caps:
  | Ch | PR | Cap | Gemini verdict | Other reviewer |
  |---:|---|---:|---|---|
  | 11 | #443 | 5,100 | READY_TO_DRAFT (msg #2938) | Codex gpt-5.5 READY_TO_DRAFT_WITH_CAP 5,100 (msg #2946) |
  | 12 | #444 | 4,500 | READY_TO_DRAFT_WITH_CAP 4,500 (msg #2940) | Independent Claude READY_TO_DRAFT_WITH_CAP 4,500 (Codex authored, conflict) |
  | 13 | #445 | 4,500 | READY_TO_DRAFT (msg #2942) | Independent Claude READY_TO_DRAFT_WITH_CAP 4,500 |
  | 14 | #446 | 4,500 | READY_TO_DRAFT_WITH_CAP 4,500 (msg #2944) | Independent Claude READY_TO_DRAFT_WITH_CAP 4,500 |
  Resolution rule: most_conservative_verdict_wins. Ch15-16 contracts not yet started.

### Role split (effective 2026-04-28)

Canonical references: `docs/research/ai-history/README.md` (Role Split + ownership table), `docs/research/ai-history/TEAM_WORKFLOW.md` (Roles section), `src/content/docs/ai-history/index.md` (public).

- **Claude — research lead** for Parts 1, 2, 3, 6, 7, 9. Anchor extraction directly via `curl` + `pdftotext` + `pdfgrep`. Proof case: Ch11 dartray.pdf (6 Green claims via local `pdftotext`).
- **Codex — research lead** for Parts 4, 5, 8 (unchanged). Helper for archive-blocked / scanned-PDF anchor extraction when Claude is stuck — narrow one-shot dispatches, NOT contract re-ownership. Continues as prose drafter for Part 3.
- **Gemini — gap auditor + first-draft prose writer** for Parts 1, 2, 6, 7. STOPS touching sources entirely. Hard rule in his prompts: NEVER cite URLs/page anchors/DOIs in audits.
- Cross-family verdict rule unchanged: every chapter needs `READY_TO_DRAFT` or `READY_TO_DRAFT_WITH_CAP` from BOTH cross-family reviewers before drafting unlocks.
- Codex ACK msg #2948; Gemini ACK msg #2950. No pushback from either.

### Beyond Part 3
- `main` advanced again: PR #447 (codex/394-ch19-research) merged. Ch17-19 now `capacity_plan_anchored`.
- The 6 untracked files in primary repo (`boole.tex`, `boole.txt`, `fix_ch1_anchor.py`, `review_ch1_claude.txt`, `review_ch1_codex.txt`, prior session doc) are not mine and remain unchanged.

## Pending action items at handoff

Priority order. The user has not picked an option — open question at the bottom.

### A. Ch11-14 prose phase (Codex drafts → Claude expands)

Ch11-14 are at `prose_ready`. Per the workflow's "One Branch, One PR, One Phase":
- Open `codex/394-ch11-prose`, `codex/394-ch12-prose`, `codex/394-ch13-prose`, `codex/394-ch14-prose` off `main`.
- Codex drafts each prose chapter respecting the per-chapter word cap (5,100 / 4,500 / 4,500 / 4,500). Brief.md self-imposed honesty caps govern.
- Claude expands the draft to full depth (Codex's drafts have historically been longer than Gemini's so the "expansion" gap may be smaller; verify per chapter).
- Cross-family prose review: Claude reviews Codex-drafted prose. Gemini may also gap-audit prose for narrative coherence.

### B. Ch15-16 research contracts (Part 3 backlog)

Same per-chapter pipeline as Ch11-14, but with the new policy:
- **Ch15 — The Gradient Descent Concept.** Likely sources: Cauchy 1847, Robbins-Monro 1951, Widrow-Hoff 1960 (Ch14 cross-link), Linnainmaa 1970, Kelley 1960 / Bryson 1961. Cross-link Ch14 (perceptron rule = SGD on linear classifier).
- **Ch16 — The Cold War Blank Check.** Likely sources: Mansfield Amendment 1969, Edwards *The Closed World* 1996, Licklider 1962 vision letter, ONR Mark I contract docs, Smith *RAND* 1966.
- Under the new policy, Claude OWNS the research contract directly (anchor extraction). Codex stays available for prose drafting + scanned-PDF helper. Gemini gap-audits.

### C. Parts 1, 2, 6, 7 re-research (Claude takes over from Gemini)

This is the largest backlog. 28 chapters. The "Golden Research" prose was merged but contracts are at `researching` with placeholder shells (or partially fabricated anchors that need vetting).

Per priority/honesty:
- Decide whether to **re-verify existing prose** against new contracts, or treat the legacy prose as draft and rebuild contracts from scratch. Likely: rebuild contracts from scratch, then check legacy prose against the rebuilt contract claim-by-claim.
- Open Gemini's existing PRs (#425, #426, #427, #431, #433, #436, #437, #438, #439) — these are Gemini's research-phase PRs that include fabricated anchors. They should NOT be merged as-is. Either close them or have Claude take them over branch-by-branch.

### D. GitHub issue assignees

Issues #399, #400, #404, #405 still show Gemini as the GitHub-side assignee. The docs (README.md ownership table) are now the canonical truth — but if you want the GitHub side to match, reassign each to `krisztiankoos` (the human, since GH doesn't model agents) with a comment pointing to the new ownership table.

## Pipeline command reference (validated in this session)

### Bridge dispatches (sequential per `feedback_codex_dispatch_sequential.md`)
```
# Gemini gap audit / verdict (synchronous, ~30s)
scripts/ab ask-gemini --task-id "chNN-task-2026-04-NN" \
  --from claude --from-model claude-opus-4-7 \
  "$(cat /tmp/chNN_prompt.txt)"

# Codex anchor verify / draft (synchronous via bridge ~5-10 min)
scripts/ab ask-codex --task-id "chNN-task-2026-04-NN" \
  --from claude --from-model claude-opus-4-7 \
  --to-model gpt-5.5 --review \
  "$(cat /tmp/chNN_prompt.txt)"
```

### Codex heavy draft (in worktree, ~30-60 min)
```
codex exec --skip-git-repo-check --sandbox workspace-write -m gpt-5.5 \
  -c model_reasoning_effort=high \
  < /tmp/chNN_codex_prompt.txt > /tmp/chNN_codex_output.txt 2>&1
```
Codex cannot self-commit (sandbox blocks `.git/worktrees/<name>/index.lock`); Claude commits on his behalf.

### Independent Claude verdict (when Codex authored, can't be cross-family)
Use Agent tool with `subagent_type: general-purpose, model: opus` — gives a fresh-context prose-capacity verdict.

## Memories used / saved

**Used heavily this session:** `feedback_gemini_hallucinates_anchors.md`, `feedback_dual_review_required.md`, `feedback_writer_reviewer_split.md`, `feedback_finish_what_you_started.md`, `feedback_user_reassigns_overrides_bridge.md`, `feedback_consult_codex_on_decisions.md`, `feedback_advisory_vs_enforced_constraints.md`, `feedback_no_yes_man.md`.

**Saved this session:** `project_ai_history_research_split_2026-04-28.md` — the new role split policy. Indexed in `MEMORY.md` under Project section.

## Cold-start function

```bash
# 1. Where are we on AI History?
curl -s 'http://127.0.0.1:8768/api/briefing/session?compact=1' | head -50
source ~/.bash_secrets && gh pr list --search "is:open" --json number,title,headRefName,author --limit 30

# 2. Status of Part 3 chapters specifically
for n in 11 12 13 14 15 16; do
  rsd=$(ls -d docs/research/ai-history/chapters/ch-${n}-*/ 2>/dev/null | head -1)
  status=$(grep -E "^status:" "${rsd}/status.yaml" | head -1 | awk '{print $2}')
  cap=$(grep -E "^prose_word_cap:" "${rsd}/status.yaml" 2>/dev/null | head -1 | awk '{print $2}')
  echo "Ch${n}: ${status} ${cap:+(cap ${cap})}"
done

# 3. Has main advanced? Are there new chapter PRs from Codex / Gemini?
git fetch origin main && git log --oneline origin/main -10

# 4. Bridge inbox
scripts/ab inbox show claude

# 5. Confirm policy is documented
grep -A2 "Role Split (effective 2026-04-28)" docs/research/ai-history/README.md | head -10
```

## Open question for the human

You haven't picked the next move. Options, ordered by minimum decision latency:

1. **Start Ch15 research now** (Part 3 forward progress; contained scope; ~30-60 min wall for the contract). Recommended if you want to stay on the Ch11→Ch16 sequence the prior handoff laid out.
2. **Hand Ch11-14 prose to Codex** (kicks off the prose phase for the four chapters that just dual-cleared). 4 dispatches × 30-60 min = 2-4 hours wall, but they go in parallel from Codex's side as separate worktree-branch dispatches.
3. **Start the Parts 1/2/6/7 re-research wave** (the largest backlog, 28 chapters). Begin with Ch1 to validate the new Claude-owned anchor-extraction workflow on a known chapter (Boole 1854 *Laws of Thought*).
4. **Reassign GitHub issue assignees** for #399, #400, #404, #405 (cleanup, no model time required).

Option 1 or 2 honors the Part-3 momentum. Option 3 is the higher-impact long-term play but is heavy. Option 4 is bookkeeping that can run alongside any of the above.

---

## End-of-handoff checklist (this session)

- [x] Ch11-14 dual-verdict pass: 4 Gemini verdicts + 1 Codex verdict + 3 independent Claude verdicts; all integrated into per-PR `status.yaml`.
- [x] All 4 PRs (#443-#446) merged to main; branches preserved on origin.
- [x] gpt-5.4 → gpt-5.5 correction applied to Ch11 contract files.
- [x] Public status board (`/ai-history/index.md`) created and pushed.
- [x] Role-split policy documented in README.md, TEAM_WORKFLOW.md, index.md.
- [x] Codex + Gemini notified via bridge; both ACK'd cleanly (no pushback).
- [x] Memory `project_ai_history_research_split_2026-04-28.md` saved + indexed.
- [x] This handoff written.
