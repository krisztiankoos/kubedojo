---
title: Session 7 handoff — pipeline_v3 + ZTT/AI citation sweep; v4 is content-first
date: 2026-04-20
---

# TL;DR

Session 7 built `pipeline_v3` (single-module end-to-end: research → Gate B
verify → in-place inject → Gates A/C/D audit → auto-apply → re-audit),
ran it over **6/6 ZTT modules (0.6–0.11)** and **25/25 /ai modules** with
per-module commits, and closed 10 v1/v2-obsoleted GitHub issues.

**Critical lesson surfaced at end**: the /ai modules we cited were at
rubric score 2.0–3.5 with primary issue "thin, no quiz". Citing before
expanding is backwards — anchors and softens will break when modules
are later rewritten for rubric compliance. The ZTT sweep was a valid
second pass (those modules were already at 4/5 from session 6 audit);
the /ai sweep was partially wasted.

Next session builds **pipeline_v4** — content-first: expand to 4/5,
then citation. [Issue #322](https://github.com/kube-dojo/kube-dojo.github.io/issues/322)
carries the full design.

Nothing pushed. 22 commits on main, local only.

# Session 7 commits landed (main, NOT pushed)

In order:

## Foundation (1)
- `d57f52f7` feat(pipeline): v3 orchestrator + batched gate audits

## Bug fixes uncovered during dogfood (7)
- `a07a0080` fix(citations): inject only writes to disk on a clean diff
- `83783bd7` fix(ztt): mermaid 11.x renders bare `<br>` tags as syntax error
- `23ae712e` fix(ztt): mermaid 11.x rejects `<b>` HTML in node labels
- `e6fda55d` fix(citations): research prompt explicit about statistic class options
- `cf31fec8` fix(citations): make cannot_be_salvaged the easier choice for marginal URLs
- `281e055d` fix(mermaid): walk `.ec-line` divs instead of innerText for diagram source
- `69c9059f` fix(citations): orchestrator skips rewrites whose anchor lives in `> "..."` quotes
- `c61a78bc` fix(citations): mark orchestrator-skipped quoted-block rewrites as addressed
- `e0694942` fix(citations): inject prompt forbids edits inside blockquote-quoted strings

## Content — ZTT (6)
- `aa40ba14` 0.6 git-basics
- `b2efc342` 0.8 servers-and-ssh
- `2d30d2a6` 0.9 software-and-packages
- `5201c037` 0.7 what-is-networking  (recovered)
- `6b72b63f` 0.11 your-first-server   (recovered)
- `d51a70b4` 0.10 what-is-the-cloud   (recovered, hallucinated-URL bias fix)

## Content — /ai (6 subsection-batched + 1 recovery)
- `ec20ddef` ai-building (4 modules)
- `8b7e47a4` ai-for-kubernetes-platform-work (2 of 4)
- `b182609f` ai-native-work (4 modules)
- `868fcf7a` foundations (5 of 6)
- `6da7ffae` open-models-local-inference (6 of 7)
- `316f73aa` 3 recovered AI modules (ai-for-k8s 1.3, foundations 1.1, open-models 1.7)
- `883b4056` ai-for-k8s 1.1 (final recovery via quoted-block skip)

# Key design decisions baked in

- **Per-candidate → batched audits.** Gates A/C/D now send ONE LLM
  call per module, not one per candidate. Wall-time per module:
  ~60 min → ~10–15 min.
- **Inject writes only on clean diff.** Previous bug: failed diff lint
  still wrote new_body to disk, polluting subsequent diffs. Now
  `module_path.write_text` is gated on `not diff_issues`.
- **Quoted-block rewrites forbidden.** `> "..."` content is author-
  quoted verbatim material (AI reviewer output, example excerpts).
  Both the inject prompt and the orchestrator skip rewrite-
  disposition claims anchored there.
- **cannot_be_salvaged is the easier path.** Strengthened prompt HARD
  TEST: "can you point at a specific passage in the URL that contains
  THIS claim's facts? If no, don't cite." Kills Codex's URL-fishing
  bias toward marketing homepages.
- **Sentence extraction respects `.git` / `.gitignore` / file
  extensions.** Boundary regex now requires whitespace/EOL after `.`.
- **Post-swap breakage detection.** Pipeline_v3 rejects any
  overstatement swap that introduces `..`, dangling backticks,
  duplicated prefix, or a sentence-count increase.

# Salvaged issues (10 closed via subagent)

All cited `d57f52f7` as the foundational supersession:

- #274, #275, #308, #311, #313, #315, #316, #317, #318, #319

# State of tracks

| Track | Modules | Status |
|---|---|---|
| ZTT 0.1–0.5 | ✅ promoted + audited (session 6) |
| ZTT 0.6–0.11 | ✅ v3-cited (session 7) |
| /ai/ (25 modules) | ⚠️ v3-cited BUT still at 2.0–3.5 rubric score — needs expand pass before citations are durable |
| /prerequisites/ (42 modules excl. ZTT) | ⏸ not touched. Do NOT citation-batch until v4 lands |
| /cloud/, /k8s/, /platform/, /on-premises/, /ai-ml-engineering/ | ⏸ not touched |

# What's left to build (pipeline_v4)

Full design in [#322](https://github.com/kube-dojo/kube-dojo.github.io/issues/322). Skeleton:

```
Stage 1  RUBRIC_SCAN   →  structured gaps (thin, no_quiz, …)
Stage 2  EXPAND         →  additive-only per-gap generation
Stage 3  RUBRIC_RECHECK →  confirm >= 4.0
Stage 4  CITATION_V3    →  existing pipeline_v3
Stage 5  FINAL_RECHECK  →  rubric didn't regress
```

Files to create:
- `scripts/rubric_gaps.py`
- `scripts/expand_module.py`
- `scripts/pipeline_v4.py`
- `scripts/pipeline_v4_batch.py`

First dogfood target: one /ai 2.0 module that already has a citation seed
(e.g. `ai/ai-for-kubernetes-platform-work/module-1.2-*`). End-to-end through
v4 should land rubric >= 4.0 + preserved citations.

# Known punch list

1. **/ai Sources sections may survive expansion, per-sentence anchors
   won't.** When v4 expands /ai modules, citation seeds need re-research.
   Session 7 seed JSON files are reusable as further-reading hints but
   the anchor_text entries won't survive substantial rewrites.
2. **AI ai-for-k8s 1.1 landed clean but empty-ish.** Two rewrite
   claims were correctly skipped (inside `> "..."`). Only the Sources
   section was added. Module still thin.
3. **Statistic-class research sometimes still reaches for the wrong
   URL tier.** Prompt has been tightened twice; remaining cases need
   either in-research substring-check (`option #2` from session 7
   discussion) or stricter allowlist for vendor homepages.
4. **UK translation drift** on modules that changed under v3. No
   automated sync check yet; `feedback_no_yes_man` memory note.
5. **Gate A false-positive on intentional wrong-statement table
   rows** carries over from session 6. Not hit in session 7 sweeps.

# Cold-start playbook for session 8

1. Read this doc + [#322](https://github.com/kube-dojo/kube-dojo.github.io/issues/322).
2. Pull briefing: `curl -s http://127.0.0.1:8768/api/briefing/session?compact=1`.
3. Confirm no dirty tree: `git status -s` should show `.cache/`,
   `.pipeline/`, and maybe `start-claude.sh` — all pre-session.
4. Start session 8 by building `scripts/rubric_gaps.py` and
   `scripts/expand_module.py`. Compose into `scripts/pipeline_v4.py`.
5. Dogfood on one /ai 2.0 module. Verify rubric >= 4.0, citations
   preserved.
6. Batch /ai through v4. Per-module commits as each lands clean.
7. If v4 proves stable across /ai, run prereqs (42 modules).
8. `git push` only after user eyeballs the diffs.

# Budget and env

- Codex 10× quota runs to 2026-05-17. Session 7 burned ~60 codex
  dispatches (research × 31, inject × 31, Gate A/C batched × 31,
  plus recoveries). Plenty of runway.
- Gemini Pro: ~35 dispatches (Gate B × 31 + Gate D × 31). Plenty.
- Bridge stays sequential. Two batches in-flight simultaneously
  interleave through the bridge queue without conflict (verified in
  session 7 ZTT recovery + AI main batch parallel run).

# References

- [#322](https://github.com/kube-dojo/kube-dojo.github.io/issues/322) — pipeline_v4 design + acceptance criteria.
- `docs/sessions/2026-04-19-session-6-handoff.md` — prior handoff.
- `scripts/pipeline_v3.py` + `scripts/pipeline_v3_batch.py` — v3 orchestrator.
- `.pipeline/v3/runs/` — per-module run records.
- `.pipeline/v3/human-review/` — residuals queued for human eye.
- `.pipeline/v3/summary.jsonl` — append-only log of every v3 run.
- `docs/citation-seeds/` — research seeds (schema v2, anchor_text).
