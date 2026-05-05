# Session Status — index

> **Read this first every session. Update before ending.**
>
> This file is an **index**, not a log. Per-session handoffs live in
> [`docs/session-state/`](./docs/session-state/) as dated files; this file
> just points at them. When you finish a session, **add a row to "Latest
> handoff" and shift the previous Latest into "Predecessor chain" — do
> NOT replace this whole file**.

## Cold-start protocol

1. Hit `curl -s http://127.0.0.1:8768/api/briefing/session?compact=1` (the API parses the `## TODO` and `## Blockers` sections of this file).
2. Read the row in **Latest handoff** below — that's the only file you need for current state.
3. Skim **Cross-thread notes (still active)** for stuff that spans sessions.
4. If picking up a long-running thread, click into the relevant **Predecessor chain** row.
5. Pre-2026-04-28 sessions (29 of them, going back to session 1) live in [`docs/session-state/archive-pre-2026-04-28.md`](./docs/session-state/archive-pre-2026-04-28.md) — kept for spelunking only, not actively maintained.

## Latest handoff

| Date | Thread | File | Status |
|------|--------|------|--------|
| 2026-05-05 (session 2) | **Phase D pilots (3) shipped + Phase E sweep Part 1 merged + Parts 2-9 plumbing.** PR #888 extended (covers `dispatch_codex_patch` + `agent_runtime/adapters/codex.py` adapter), codex APPROVE w/ `--search`, squash-merged (`733cfff0`). Carry-over PRs #884 / #885 / #887 all merged this session; structural fix `c9c45c45` cleaned PR #887's stray H1 + missing separator. Three Phase D book-audit pilots completed via `dispatch.py claude --no-tools` (now WebFetch/WebSearch enabled): ch-33 Deep Blue (74 claims, 88% R:supported, 1 R:contradicted in glossary fixed `d0201191`), ch-34 The Accidental Corpus (108 claims, 88%, 1 R:wrong in cast + 1 body drift fixed `065e4fd8`), ch-58 The Math of Noise (63 claims, 86%, 1 W:wrong in matters + 1 architecture drift fixed `6e1ba040`). Section-by-section risk profile locked in `docs/decisions/2026-05-05-phase-e-scope.md` (`cfb5b278`): cast / glossary / `:::note[Why this still matters today]` are sweep-scope; timeline / math (Tier 2) clean; body / architecture spot-check only. Sweep driver `scripts/sweep_ai_history_aids.py` cross-family-reviewed pre-launch (codex gpt-5.5 + gemini), both NEEDS CHANGES integrated: `fcntl` per-chapter lock, `tempfile.mkstemp`, sha256 concurrent-modification check, byte-for-byte frontmatter preservation, structural-block count preservation, JSON `before→after` fix-list output (NOT full markdown regeneration — gemini's voice-preservation guard), `:::note` no-"as-of-{year}" boilerplate, metaphor/rhetorical-flourish guard. Driver is dispatch-then-apply-from-audit-JSON (apply re-uses dry-run JSONs, no second dispatch). Phase E Part 1 (ch-01..ch-08) shipped (`0a6cb725`): 8 chapters audited, 4 clean, 4 with 6 wrong-specifics fixed (ch-02 Manchester Baby date span; ch-05 Lettvin "Univ. Chicago" → "Univ. Illinois" + 1959 frog's-eye paper authorship order; ch-07 W. Grey Walter tortoise Behaviour N motor speed; ch-08 flag-bit memory tagging attribution). Build clean each commit. Part 2 dry-run launched at handoff time (background bash task `bmdolfkpn`, ETA ~11:30 local). Incidental fix `a385f81f`: `dispatch.py gemini` CLI branch was missing `print(output)` for non-`--github` invocations — discovered when stylistic review came back empty; two-line fix on trunk. | [`docs/session-state/2026-05-05-2-phase-d-pilots-and-phase-e-sweep.md`](./docs/session-state/2026-05-05-2-phase-d-pilots-and-phase-e-sweep.md) | **Next session: (1) check on Part 2 dry-run if still in-flight; (2) inspect Part 2 diffs, apply audited fixes, build, commit, push; (3) repeat for Parts 3-9 (Part 5 skips ch-33/34, Part 8 skips ch-58); (4) re-request Gemini review on PR #872 + sweep #5 / #6 / #7 in parallel as bandwidth allows.** |

## Predecessor chain (most-recent first)

| Date | Thread | Where to find it |
|------|--------|------------------|
| 2026-05-05 (session 1) | **dispatch.py source-of-problem fix uncovered + book / #388 fact-check audit prep.** `dispatch_codex` (line 603) hardcoded `--sandbox read-only` + no `--search`; `_CLAUDE_TEXT_ONLY_DISALLOWED` (line 491) banned WebFetch+WebSearch. Closed PR #886 (no-search draft); shipped CKS pilot redo PR #887 with `KUBEDOJO_CODEX_SEARCH=1` + `KUBEDOJO_CODEX_SANDBOX=danger-full-access` env-var threading. Patches landed on PR #888 (later extended + merged in session 2). | [`docs/session-state/2026-05-05-1-dispatch-fix-and-book-audit-prep.md`](./docs/session-state/2026-05-05-1-dispatch-fix-and-book-audit-prep.md) |
| 2026-05-04 (session 3) | **Incident-dedup sweeps #3 + #4 shipped (PRs awaiting merge); 3 regex tightenings; delegation discipline lesson.** Sweep #3 PR [#884](https://github.com/kube-dojo/kube-dojo.github.io/pull/884) — 14 KCSA+KCNA modules + Facebook 2021 BGP regex word-boundary fix + 2 catalog claims (Siloscape 2021 + XZ Utils CVE-2024-3094). Sweep #4 PR [#885](https://github.com/kube-dojo/kube-dojo.github.io/pull/885) — 25 Platform modules dispatched correctly via `scripts/dispatch_smart.py edit` (sonnet-4.6, ~$1.50-3, JSONL audit `task_id=smart-edit-1777933078`). Gemini caught 7 Must-Fix + 1 Nit on #885; all addressed in `180c122c` along with 3 regex tightenings (Cloudflare 2019, Cloudflare 2020 BGP, Target 2013). **Guardrail count: 85 → 33 curriculum-wide.** Locked: `dispatch_smart.py edit` is the per-file sweep drafter from #5+; `Agent`-tool subagent retired for content sweeps. | [`docs/session-state/2026-05-04-3-incident-dedup-platform-sweep.md`](./docs/session-state/2026-05-04-3-incident-dedup-platform-sweep.md) |
| 2026-05-04 (session 2) | **Curriculum-wide incident-anecdote de-duplication sweep launched.** Phase 1 (audit + 15 canonicals + 41-incident catalog + guardrail) + Phase 2 sweep #1 (PR #880 — 10 prerequisites modules) + sweep #2 (PR #882 — 13 CKS modules) shipped. Hard rule: every named real-world incident appears in at most ONE module across the curriculum. Gemini cross-family review caught 4 substantive issues on infrastructure PR #879 + 1 grammar nit on #880; 5 issues on #882 (regex false positives + diagram-label euphemism). Guardrail: 121 → 85 violations. Token leak: GH_TOKEN exposed in transcript. | [`docs/session-state/2026-05-04-2-incident-dedup-sweep.md`](./docs/session-state/2026-05-04-2-incident-dedup-sweep.md) |
| 2026-05-04 (session 1) | **Codex-out window cleanup, quality-board status-split, 4 PRs merged + 1 holding.** Shipped #874 (blocker note) · #875 (pipeline-v4 tech-debt) · #873 (quality-board status-split: `done=78, needs_rewrite=424, needs_review=59, shipped_unreviewed=192, both=1`) · #876 (citation-residuals resolver phase 2, closes #344). Holding #872 (codex routing tiers) — NEEDS CHANGES, blocked on codex smoke-test. 3 new memories. | [`docs/session-state/2026-05-04-1-codex-out-cleanup-and-status-split.md`](./docs/session-state/2026-05-04-1-codex-out-cleanup-and-status-split.md) |
| 2026-05-02 (session 5) | **#388 Day 3 KCNA batch COMPLETE (6h 6m wall) + `/api/388/batches` endpoint pending review-fix + GitHub-token rotation.** 28 modules, 13 merged + 5 APPROVE_WITH_NITS + 1 NEEDS CHANGES + 1 ERROR + 8 module_skip + 1 gemini_error. The 8 module_skip events (28%) are a regression from Day 2 (0%). Headless Claude added `/api/388/batches` endpoint (+143 LOC); codex review NEEDS CHANGES on dual-pilot_start handling (fix shipped between sessions). Token rotation: per-project `.envrc` PATs (kubedojo gets fresh fine-grained token). | [`docs/session-state/2026-05-02-5-388-day3-kcna-running-token-rotation.md`](./docs/session-state/2026-05-02-5-388-day3-kcna-running-token-rotation.md) |
| 2026-05-02 (session 4) | **#388 Day 3 KCNA proving batch LAUNCHED + dispatcher hardened per ab-discuss.** `ab discuss day3-388 --with claude,codex,gemini --max-rounds 3` converged at round 2 on **A2+B3+C3+D1**; two load-bearing dispatcher fixes shipped (commit `a63cdad3`): portable REPO path + APPROVE_WITH_NITS verdict collapse fix. `run_388_batch.py` E2E entry shipped (commit `82e50f52`). Built `scripts/quality/day3-bucket1-kcna.txt` (28 KCNA modules) + `day3-bucket2-kcsa.txt` (26 KCSA modules). Batch launched 14:48 UTC, single-lane. | [`docs/session-state/2026-05-02-4-388-day3-bucket1-launched.md`](./docs/session-state/2026-05-02-4-388-day3-bucket1-launched.md) |
| 2026-05-02 (session 3) | **#388 Day 2 pilot COMPLETE — 9/9 merged in ~90 min wall time.** All 9 pilot modules cleared every #388 verifier gate (T0 on main, body_words 5014-5758, mwpp 67-89). Codex on gpt-5.5 + danger mode is ~10x faster than the 9-13 hour pre-pilot estimate (avg 11.6 min/module). Cross-family gemini review caught 2 real issues that codex's own checks missed (1 dead URL, 1 redundant code line). Threshold-freeze: density gates don't constrain codex; body_words_5000 is the only binding gate. | [`docs/session-state/2026-05-02-3-388-day-2-pilot-complete.md`](./docs/session-state/2026-05-02-3-388-day-2-pilot-complete.md) |
| 2026-05-02 (session 2) | **#388 Day 2 pilot launched (autonomous).** 9 pilot modules selected, sequential dispatcher (`scripts/quality/dispatch_388_pilot.py`) running on PID 52373. Pattern: codex (gpt-5.5, danger) → gemini cross-family review → auto-merge. Expected wall-clock 9-13 hours (turned out to be ~90 min). | [`docs/session-state/2026-05-02-2-388-day-2-pilot-launched.md`](./docs/session-state/2026-05-02-2-388-day-2-pilot-launched.md) |
| 2026-05-02 (session 1) | **#388 Day 1 complete — verifier shipped + 6 density fix-passes merged + first audit ran.** `scripts/quality/verify_module.py` (849 LOC, 13 tests) merged via PR #724. Audit on `audit-2026-05-02-v2.jsonl` shows 235/235 → T3 (real — body_words_5000 floor binding on 234/235 modules). All 6 session-5 fix-pass modules (5.6, 5.7, 5.8, 5.9, 9.10, 9.11) re-fixed via Codex 2x parallel and merged (#725-730), each cross-family Gemini-reviewed. | [`docs/session-state/2026-05-02-1-388-day-1-verifier-and-fix-pass.md`](./docs/session-state/2026-05-02-1-388-day-1-verifier-and-fix-pass.md) |
| 2026-05-01 (session 5) | **#379 Phase A.2 (KServe / Seldon / BentoML / bare-metal MLOps) + #385 Phase E.2 (Gardener / multi-cluster on-prem / OpenStack on K8s / VMware Tanzu) — all 8 modules shipped as 8 PRs, both issues closed.** 4 density fix-pass PRs (#720-723) followed after user flagged choppy prose. Codex consulted twice on #388 architecture (bridge #3384 + #3386): verifier-first, pilot-then-volume, density-first brief. Canonical brief addendum at `scripts/prompts/module-rewriter-388.md`. | [`docs/session-state/2026-05-01-5-greenfield-shipped-388-prep.md`](./docs/session-state/2026-05-01-5-greenfield-shipped-388-prep.md) |
| 2026-05-01 (session 4) | **Issue tracker triage: 40 → 14 open (26 closures) + greenfield-before-#388 sequencing locked + KServe dispatch brief staged.** Closed 16 #388-subsumed, 4 completed, 5 stale, 1 substantially shipped. Locked routing: no Gemini, Codex drafts, Claude reviews. REWRITE-tier first within #388. | [`docs/session-state/2026-05-01-4-issue-triage-greenfield-prep.md`](./docs/session-state/2026-05-01-4-issue-triage-greenfield-prep.md) |
| 2026-05-01 (session 3) | **#559 review-coverage closeout (option c hybrid) + #394 epic closure + `context-monitor.sh` Block A fix + issue closeout audit.** Audit-script `_expected_lane_fields` + `_lane_satisfied` relaxed to "any two distinct cross-family markers" for prose lane. `audit_review_coverage.py --write` populated `review_coverage:` blocks across 72 chapter `status.yaml` files. Backfill reviews on Ch02 (PR #479) + Ch03 (PR #480). | [`docs/session-state/2026-05-01-3-559-evidence-prep.md`](./docs/session-state/2026-05-01-3-559-evidence-prep.md) |
| 2026-05-01 (session 2) | **#677 closeout (3 PRs merged) + Dependabot psutil + deep git hygiene + dashboard panels finished.** ML 2.7 (#708, Codex APPROVE 36/40) + RL 2.1 (#709, 847 lines, 11 arxiv IDs verified) + DL 1.7 cleanup (#710, filename/slug/forward-link aligned). Dependabot psutil >=7.2.2 merged (#542). Worktrees 50→3, branches 87→4, 8 dead PIDs + 1 detached HEAD + 2 stashes resolved. Stash@{1} popped + finished: dashboard panels (Book Progress + Module Distribution). | [`docs/session-state/2026-05-01-2-677-closeout-hygiene-dashboard.md`](./docs/session-state/2026-05-01-2-677-closeout-hygiene-dashboard.md) |
| 2026-05-01 | **ML curriculum expansion (#677) — 19 of 22 modules merged in one session.** Phase 0 foundation + 11 Tier-1 (machine-learning/) + RL 1.1 + DL 1.8/1.9 + 6 Tier-2 ML (2.1-2.6). ML 2.7 in flight at session-end; RL 2.1 + DL 1.7 cleanup pending. Locked the dispatch-and-fallback pattern, pinned-slug discipline, plain-text Next-Module convention, no-skill / no-cold-start preamble. | [`docs/session-state/2026-05-01-ml-expansion-batch.md`](./docs/session-state/2026-05-01-ml-expansion-batch.md) |
| 2026-04-30 (night-7) | **Post-Ch59-72 followups** — reader-aid lint script (`check_reader_aids.py`), 9-Part sidebar grouping for AI history, deep-link bridge from AI/ML history module to the book; surfaced classical-ml curriculum gap (only 3 modules) needing dedicated next-session plan | [`docs/session-state/2026-04-30-night-7-followups.md`](./docs/session-state/2026-04-30-night-7-followups.md) |
| 2026-04-30 (night-6) | **Ch59–Ch72 shipped — entire 72-chapter AI history book reader-aid rollout (#562) complete.** 14 chapters end-to-end; Tier 3 yield 14/26 (~54%, Codex source-fetch REVIVEs); caps verification + worktree-write discipline tightened mid-session | [`docs/session-state/2026-04-30-part8-9-ch59-72-shipped.md`](./docs/session-state/2026-04-30-part8-9-ch59-72-shipped.md) |
| 2026-04-30 (night-5) | Part 8 reader-aids Ch50–Ch58 shipped — 9 PRs merged-as-you-go; all Tier 2 (math/architecture) chapters in the entire book landed; Codex caught 2 math errors + 1 verbatim hallucination | [`docs/session-state/2026-04-30-part8-9-ch50-58-shipped.md`](./docs/session-state/2026-04-30-part8-9-ch50-58-shipped.md) |
| 2026-04-30 (night-4) | Part 7 reader-aids (Ch41–Ch49) RELEASED + 26-PR merge sweep + lifecycle bookkeeping migration — Parts 1–7 fully on main (49 chapters); arch-sketch form-lock confirmed (LR for sequential, TD for hierarchies) | [`docs/session-state/2026-04-30-part7-reader-aids-shipped.md`](./docs/session-state/2026-04-30-part7-reader-aids-shipped.md) |
| 2026-04-30 (night-3) | Part 6 reader-aids (Ch32–Ch40) PR-complete — 9 PRs open; inline-sequential single-Agent-dispatch pattern validated at 9-chapter scale; first orchestrator-override of a Codex Tier 3 verdict (Ch38) | [`docs/session-state/2026-04-30-part6-reader-aids-prs.md`](./docs/session-state/2026-04-30-part6-reader-aids-prs.md) |
| 2026-04-30 (night-2) | Part 5 reader-aids (Ch24–Ch31) PR-complete — 8 PRs open; Agent worktree fan-out retired after 5/8 race incident; Tier 3 ran sequential | [`docs/session-state/2026-04-30-part5-reader-aids-prs.md`](./docs/session-state/2026-04-30-part5-reader-aids-prs.md) |
| 2026-04-30 | Part 4 reader-aids (Ch17–Ch23) RELEASED — 7 PRs #600–#606 merged via squash; parallel headless-Claude + parallel Codex Tier 3 dispatch | [`docs/session-state/2026-04-30-part4-reader-aids-prs.md`](./docs/session-state/2026-04-30-part4-reader-aids-prs.md) |
| 2026-04-29 (night-2) | Parts 2 & 3 reader-aids RELEASED — Ch10 closes Part 2; Ch11–Ch16 close Part 3; Mermaid click-to-enlarge modal shipped | [`docs/session-state/2026-04-29-parts-2-3-closed.md`](./docs/session-state/2026-04-29-parts-2-3-closed.md) |
| 2026-04-29 (night) | Part 1 RELEASED — section-header fix on Ch01–Ch09 + 9 PRs merged; right-nav now works | [`docs/session-state/2026-04-29-part1-released.md`](./docs/session-state/2026-04-29-part1-released.md) |
| 2026-04-29 (evening) | Part 1 reader-aids PR-complete — Ch07/Ch08/Ch09 shipped (3 PRs); all 8 Part 1 PRs open | [`docs/session-state/2026-04-29-part1-reader-aids-complete.md`](./docs/session-state/2026-04-29-part1-reader-aids-complete.md) |
| 2026-04-29 (afternoon) | Part 1 reader-aids rollout — Ch02–Ch06 shipped (5 PRs); PR-hygiene gotchas memorised | [`docs/session-state/2026-04-29-part1-reader-aids-rollout.md`](./docs/session-state/2026-04-29-part1-reader-aids-rollout.md) |
| 2026-04-29 (morning) | Ch01 reader-aid prototype (Tier 1+2+3) + math rendering fix + 6 sub-issues for rollout | [`docs/session-state/2026-04-29-reader-aids-ch01-prototype.md`](./docs/session-state/2026-04-29-reader-aids-ch01-prototype.md) |
| 2026-04-29 (overnight) | Parts 3/6/7 shipped (13 chapters) + STATUS.md index migration + STEP 0 routing | [`docs/session-state/2026-04-29-parts-3-6-7-shipped.md`](./docs/session-state/2026-04-29-parts-3-6-7-shipped.md) |
| 2026-04-28 night | Parts 3/6/7 finish queue setup (Ch16 + Ch38-40 + Ch41-49 plan) | [`docs/session-state/2026-04-28-night-handoff-2.md`](./docs/session-state/2026-04-28-night-handoff-2.md) |
| 2026-04-28 night | Part 6 fully closed (Ch32-37 + roll-up) | archive § "2026-04-28 night — Part 6 fully closed" |
| 2026-04-28 evening | Smart-router wrapper shipped; Claude resumes Parts 2/3 | archive § "2026-04-28 evening — smart-router wrapper" |
| 2026-04-28 | AI History Part 1 prose shipped | archive § "2026-04-28 — AI History Part 1 prose shipped" |
| 2026-04-27 evening | Part 3 dual-reviewed pipeline + ownership rebalance | archive § "2026-04-27 evening" |
| 2026-04-26 night | v4 handoff: bridges + drain-fix + What's New | archive § "2026-04-26 ~20:15 local — v4 handoff" |
| 2026-04-26 | #388 deferred-review batch under `KUBEDOJO_SKIP_REVIEW` | archive § "2026-04-26 ~10:55 local" |
| 2026-04-26 morning | #388 single-batch mode after concurrency-race compounding | archive § "2026-04-26 ~06:40 local" |
| 2026-04-26 ~03:35 | #388 batch resumed under hardened rewrite prompt | archive § "2026-04-26 ~03:35 local" |
| 2026-04-26 ~02:45 | #388 Phase 0 + #8 done; prioritized rewrite batch | archive § "2026-04-26 ~02:45 local" |
| 2026-04-25 night | #378 12-module recovery; 11/12 green | archive § "2026-04-25 ~22:00 local" |
| 2026-04-24 morning | 4 PRs merged, phase-2 pilot unblocked | archive § "2026-04-24 morning" |
| 2026-04-23 night | 6 PRs merged; cross-family reviewer rule codified | archive § "2026-04-23 night" |
| 2026-04-21 | pipeline_v4 built end-to-end, dogfood validated | archive § "Session 11 (2026-04-21)" |
| ≤2026-04-18 | Sessions 1–3 (citation-first infra, role-swap) | archive § "Prior session archive (sessions 1–3)" |

## Cross-thread notes (still active)

These are state items that span individual sessions. Prune entries as threads close.

- **Curriculum-wide incident-anecdote de-duplication sweep (#878) — 4 of 7 sweep PRs landed.** Hard rule: every named real-world incident appears in at most ONE module across the EN curriculum. Lock-tables: 15 canonicals (`docs/audits/2026-05-04-incident-canonicals.md`) + 41-incident replacement catalog (`docs/audits/2026-05-04-incident-replacement-catalog.md`). Sweep series: prereqs ✓ (#880 merged) → CKS ✓ (#882 merged) → KCSA+KCNA ⏳ (#884 awaiting merge) → Platform ⏳ (#885 awaiting merge) → Cloud+AI-ML+On-Prem (next) → forbidden-trope rewrites → CKA+CKAD final. Guardrail count: 121 → 33 curriculum-wide. Final sweep promotes the guardrail to a CI-required check.
- **`scripts/dispatch_smart.py edit` is the LOCKED drafter for sweep #5+** (decision 2026-05-04 session 3). Per-file content sweeps go through sonnet-4.6 via `agent_runtime.runner.invoke` (CLI subprocess, JSONL audit at `logs/smart_dispatch.jsonl`), NEVER through `Agent` tool with `subagent_type=general-purpose` (~5x cost difference per `code-editing-safety.md` measured "2-3M token reload, 1000:1 overhead-to-output ratio"). The `Agent` tool is retired for content sweeps and probably for most fresh-implementation per-file edit batches.
- **Phase E book-audit sweep — three-pilot section-by-section risk profile and driver locked.** Decision: `docs/decisions/2026-05-05-phase-e-scope.md`. Sweep targets: cast / glossary / `:::note[Why this still matters today]`. Skip: timeline (template-derived from `timeline.md`, clean across 3 pilots), math sidebars in Tier 2 chapters (separate codex math-review effective). Spot-check only: architecture sketches, body prose. Driver: `scripts/sweep_ai_history_aids.py` — cross-family-reviewed by codex+gemini pre-launch; both NEEDS CHANGES integrated (fcntl per-chapter lock, sha256 concurrent-modification check, byte-for-byte frontmatter preservation, structural-block count preservation, JSON `before→after` fix-list output, no "as-of-{year}" boilerplate, metaphor/rhetorical-flourish guard). Mechanism is dispatch-then-apply-from-audit-JSON (apply re-uses dry-run JSONs, no second dispatch). Per-Part gating with `--part N`; default `--halt-on-rate-limit`. Part 1 shipped (`0a6cb725`, 6 fixes / 8 chapters). Parts 2-9 remaining (~8 hr wall total).
- **Catalog claims update three places** (sweep #3 onward): `[CLAIMED]` annotation in `docs/audits/2026-05-04-incident-replacement-catalog.md`, entry in `CANONICALS` dict in `scripts/check_incident_reuse.py`, regex in `INCIDENTS` dict in `scripts/audit_incident_reuse.py`. Sweep #3 claimed Siloscape 2021 + XZ Utils CVE-2024-3094.
- **Regex catalog tightenings landed across sweeps #1–#4** for false positives that surface at curriculum scale. Pattern: `Name.{0,N}(generic-word|year|broad-term)` consistently catches unrelated content. Confirmed fixes: Uber `\bUber\b` (kUBERnetes), SolarWinds + Codecov (require incident signals not just product names), Facebook 2021 `\bMeta\b`+`\blocked out\b` word boundaries, Cloudflare 2019 (drop bare year/July), Cloudflare 2020 (drop bare BGP/year), Target 2013 (drop bare "breach"). Future regex catalog work: prefer pinned signals (HVAC, Fazio, 40 million cards) over broad word lists.
- **GH_TOKEN value was printed to stdout once during 2026-05-04 session 2** (mishandled `.envrc` cat). The kube-dojo fine-grained PAT is exposed in that session's transcript. Recommend rotating when convenient. Functional impact: none (token still works); operational: minor.
- **Stale `GEMINI_API_KEY` env in this Claude Code process** — user rotated key 2026-05-04 (new value in `~/.bash_secrets`, ends `Oq3Aq7Bw`); Claude Code's env still has the pre-rotation value (ends `rpXZEPl4`). Per-call workaround: `source ~/.bash_secrets &&`. Permanent fix: `/exit` and restart Claude Code so it inherits fresh env from the parent shell.
- **Gemini-3.1-pro-preview cross-family review quality** has been high-signal across 4 sweep PRs: caught regex false positives + bridge-integrity violations + wrong-incident xref mappings + xref-proximity bugs + duplicate floating xrefs. Same-family-priors caveat doesn't appear to degrade verdict quality on this kind of structured-rule review work.
- **#388 Day 3 KCNA proving batch LAUNCHED 2026-05-02 14:48 UTC (28 modules, single-lane, ~5-6 hr wall).** Logs: `logs/388_day3_bucket1_2026-05-02.jsonl`. New dispatcher behavior: APPROVE_WITH_NITS held for orchestrator triage (no auto-merge), REPO portable across worktrees, `--input/--max/--log` flags. Triage held PRs after `pilot_done`; cleanup script needs `--input` generalization next session.
- **`ab discuss` deliberation pattern proven** — `ab discuss day3-388` converged at round 2 (A2+B3+C3+D1) in ~2 min wall. Codex flagged 2 dispatcher bugs in r1 that gemini+claude ratified; protocol surfaces disagreement through `[OPTION X-N]`/`[AGREE]`/`[DEFER]` instead of burying it in prose. Full transcript: `ab channel tail day3-388 -n 20`. Convergence ⇒ no Decision Card per rule.
- **A2 (two-lane) plumbing deferred** until single-lane proving batch validates the hardened dispatcher. Two reasons: `feedback_codex_dispatch_sequential.md` (concurrent codex dispatches die silently), and `npm run build` is a serialized shared resource per AGENTS.md. Half-day of plumbing once we commit (split input file 2 ways, 2 background processes, shared cleanup).
- **#388 Day 2 pilot COMPLETE 2026-05-02 (~90 min wall time).** All 9 pilot modules merged (#731-#739), all T0 on main with body_words 5014-5758. Cross-family gemini review caught 2 real issues codex missed (1 dead URL, 1 redundant code line). Threshold-freeze: keep all gates; density gates don't constrain codex (mwpp 67-89 observed vs floor 30); body_words_5000 is the binding constraint.
- **All 6 session-5 density fix-pass modules merged this session** (#725 5.7, #726 5.6, #727 5.8, #728 5.9, #729 9.10, #730 9.11). Each Codex-authored, Gemini-approved cross-family. 5.7 was the worst (max_run=19→2); 9.11 needed +1134 words to clear the body_words_5000 floor (3867→5001). Now all 14 of 14 session-5 modules (8 greenfield + 6 fix-passes) on main.
- **`scripts/quality/verify_module.py` is the canonical #388 contract on main** (PR #724 merged 2026-05-02). 849 LOC, 13 tests passing. Density+structure+sources+anti-leak+alignment gates → JSONL with tier classification (T0/T1/T2/T3). Section-name synonym detection (4 LO variants, 5 Quiz variants, 5 Hands-On variants, etc.). CLI: `--all-revision-pending --skip-source-check --out PATH.jsonl --summary --tier-only`.
- **First #388 audit complete: `scripts/quality/audit-2026-05-02-v2.jsonl`** — 235/235 modules → T3. The 100% T3 is real, not a verifier bug: 234/235 fail body_words_5000 (most modules are 1000-4500 words, well under the new 5000-word #388 floor); 233/235 fail sources_min_10. Codex's consult predicted 45-60% T3; empirical answer is 100%. Implication: every `revision_pending: true` module needs a full rewrite, not a structural patch.
- **Section-heading variants exist across the curriculum** (4 LO conventions: 457 "What You'll Be Able to Do", 261 "Learning Outcomes", 104 "What You'll Learn", 2 "Learning Objectives"; plus `## Did You Know?`, `## Further Reading`, `## Quiz: <topic>` patterns). Verifier handles all of them. **Low-priority cosmetic drift, not a real problem** — "What You'll Be Able to Do" is arguably better pedagogically. Only annoying if a future section-aware tool wants to skip the synonym table.
- **`scripts/prompts/module-rewriter-388.md` is the canonical brief addendum for all #388 dispatches** (committed 2026-05-01 session 5). Layered on top of `module-writer.md`. Codex's 5 prose-discipline fragments verbatim plus 5,000-7,000 word target replacing 600+ lines. Density gates (mean_wpp >= 30, median_wpp >= 28, short_rate <= 20%, max_run <= 2) are hard gates; verifier enforces them.
- **Codex 2x parallel confirmed under load** — 8 concurrent dispatches across this session (verifier MVP, verifier-v2, 6 fix-passes) with zero silent failures. Stale memory `feedback_codex_dispatch_sequential.md` fully superseded.
- **Codex sandbox limitation: workspace-write blocks `.git/worktrees/.../index.lock`.** Every Codex dispatch this session reported "Commit was blocked by sandbox permissions" — recovery pattern is for the orchestrator to manually `cd <worktree>` + `git add` + `git commit` from primary tree. Worked 8/8 times. For Day 2+, switch to `mode="danger"` so Codex can commit directly (saves orchestrator a step per dispatch).
- **Worktree cwd-persistence trap.** When creating worktrees in long sessions, the bash cwd may have drifted into a sibling worktree from a prior `cd`. Always pass absolute paths to `git worktree add` to avoid creating nested worktrees (caught once this session — verifier-v2 was nested under verifier).
- **Build is ~38s for 1,999-2,011 pages.** CLAUDE.md updated 2026-05-01 from stale 1,297 value.
- **#394 AI History — all 72 chapters of prose are on main.** Codex's autonomous Part 9 chain shipped through Ch72 (verified by file existence and word counts ≥4k each).
- **All 72 AI history chapters carry full reader aids on main (#562 complete, 2026-04-30 night-6).** Every chapter has Tier 1 (TL;DR + cast + timeline + glossary + Why-still-matters); 15 chapters carry selective Tier 2 (math sidebars on Ch01/04/15/24/25/27/29/44/50/55/58 + architecture sketches on Ch41/42/49/50/52/58); 51+ Tier 3 elements landed across the book under cross-family Codex review. Tier 3 yield averaged ~22% on Parts 5–8 and ~54% on Parts 8–9 (Ch59–Ch72) — the higher rate is driven by Codex REVIVEs from concept-only proposals.
- **AI history sidebar grouped into 9 Parts** (commit `5ba5871e`, 2026-04-30 night-7). URLs unchanged — only render hierarchy. Implementation: explicit `items[]` in `astro.config.mjs` instead of flat `autogenerate`. Future chapter additions/renames now require a sidebar update (autogenerate convenience traded for grouping).
- **Reader-aid lint script `scripts/check_reader_aids.py`** (commit `f56e87a6`, 2026-04-30 night-7). Manual-run validator for Tier 1 caps + structural presence across all 72 chapters. Surfaces 14 pre-existing cap violations (Ch07/08/09/14/18/21/22/23/27/33/35/37/50/58) — left for Codex's dedup pass to trim naturally.
- **AI/ML history module bridges into the AI history book** (commit `7cd6291f`, 2026-04-30 night-7). 11 Part-level *Go deeper* asides + a top-level pointer in `src/content/docs/ai-ml-engineering/history/module-1.1-history-of-ai-machine-learning.md`. The module body is unchanged — survey + exercises preserved as the 30-min on-ramp.
- **Codex 0.128.0 + gpt-5.5 (reasoning=high) is the working dispatch tier** as of 2026-05-01 session 2. Both `codex exec` direct and `scripts/ab ask-codex` wrapper round-trip cleanly (12.2s + 10.4s on a tiny smoke). Yesterday's "wrapper drops stdin silently" issue did NOT reproduce on a single test — wait for more data points before retiring that note.
- **Dashboard book panel reflects deployment-state truth, not research-phase status.** `/api/briefing/book` now returns `published_count` + `aids_landed_count` at top + per-Part. Sourced from `prose_state` / `reader_aids` lifecycle fields in chapter `status.yaml` (commit `ab801bf7`). Existing `total_status_rollup` field unchanged for back-compat.
- **`/api/status/summary` track schema added `uk_module_count`.** Frontend dashboard renders per-track UK coverage. AI track properly named (added to `TRACK_ORDER` in `scripts/status.py`); the "Other" bucket is empty for current curriculum.
- **`_parse_status_yaml` now strips trailing ` # comment` from unquoted scalar values.** Lifecycle fields had inline state-machine comments which the prior parser was reading as part of the value.
- **Pre-existing test flake**: `tests/test_local_api.py::test_cli_starts_server_and_reports_host_port` hangs on Python 3.14 because `print(...)` in `serve()` is fully-buffered when piped to `subprocess.PIPE`. Confirmed pre-existing on pristine main. Fix is `print(..., flush=True)` in `local_api.py:serve()` or `PYTHONUNBUFFERED=1` in the test's subprocess env.
- **Stale `--host 0.0.0.0` API process** found and killed during this session's hygiene sweep. Future hygiene checks should scan `ps` for `--host 0.0.0.0 ` on `local_api.py` alongside the worktree sweep — the localhost-only rule per memory `feedback_localhost_only.md` is easy to violate accidentally on long sessions.
- **`context-monitor.sh` hook handoff target is stale.** Hook hard-codes `.pipeline/session-handoff.md` (last touched 2026-04-17, 3 weeks old); actual practice writes to `docs/session-state/`. If the hook ever fires near the 95% emergency tier it'll point next session at the wrong file. Fix queued for next session.
- **Caps verification is mandatory in Tier 1 dispatch prompts.** Ch65 shipped Why-still at 121 words (1 over the 120 cap) without it; from Ch66 onward, dispatches included a pre-commit `awk + wc -w` block on TL;DR and Why-still and zero further chapters shipped over-cap.
- **Worktree-write discipline must be explicit in dispatch prompts.** Ch63's agent wrote contract files (`tier3-proposal.md` / `tier3-review.md`) to the primary tree path instead of the worktree path, causing an untracked-file conflict on `git pull`. From Ch64 onward, prompts banned primary-tree writes outright (`DO NOT write to /.../docs/research/...`) and zero further violations occurred.
- **Architecture-sketch form-lock confirmed: `flowchart LR` for sequential dataflow, `flowchart TD` only when topology is genuinely hierarchical.** Three data points: Ch41 LR-lock, Ch42 LR→TD-deviation (CUDA grid → block → thread is hierarchical), Ch49 LR-reuse (TPU systolic array is linear). For Ch50/Ch52/Ch58, default to LR with explicit deviation justification only.
- **Lifecycle fields added to all 72 chapter status.yaml** (commit `ab801bf7`, addressing Codex bookkeeping note forwarded by user). New top-level fields: `prose_state` (`research_only | published_on_main`), `reader_aids` (`none | pr_open | landed`), `lifecycle_updated`. Existing `status` field untouched (keeps research-phase semantics). Per-chapter agents now flip `reader_aids` directly in their reader-aid commit.
- **Merge-as-you-go discipline reset.** Per-Part PR accumulation became debt at 24 open PRs. Going forward: squash-merge each reader-aid PR immediately after Codex Tier 3 review, do not let the queue accumulate.
- **Verbatim COMPLETE sentence rule for codex revives.** When codex revives an Element 9 pull-quote, the review must include the COMPLETE verbatim sentence in `>`-blockquote form, not a fragment. Ch43 Russakovsky revive needed a follow-up dispatch to extract the full sentence.
- **Inline-sequential single-Agent-dispatch pattern (no `isolation=worktree`) validated through 9 + 9 + 9 = 27 chapters (Parts 6/7).** Pre-create per-chapter worktree → dispatch one headless sonnet Agent (no isolation flag) with explicit `cd <worktree>` discipline → codex Tier 3 review → apply verdicts inline → push + PR → squash-merge → next chapter. Zero worktree GC races across the full sweep. ~9–15 min per chapter (Tier 2 chapters longer).
- **Agent worktree fan-out is RETIRED for chapter batches.** 5 of 8 agents missed their worktrees on Part 5 despite `touch .worktree-sentinel` mitigation (vs. 1 of 7 on Part 4). The race is unfixable from the prompt side; `Agent(isolation="worktree")` for parallel chapter work commits to primary main instead of the worktree branch. Future Part 6+ batches must be **inline / sequential** in the orchestrator. Recovery procedure documented at memory `reference_agent_worktree_recovery.md` (cherry-pick + reset).
- **Codex parallel `codex exec` still works** under `--dangerously-bypass-approvals-and-sandbox` direct invocation (6 in parallel Part 4 = ~5 min). The fan-out retirement is specific to `Agent(isolation="worktree")`, not all parallelism. Part 5 ran codex sequentially anyway (~16 min for 8) under the no-fan-out instruction; either pattern is acceptable for codex-only review batches.
- **Tier 1 dispatch prompt must require Green primary source for Tier 3 pull-quotes.** Every Part 5 author proposal cited "Chapter XX prose" as source, which fails Tier 3 source-discipline. Add to next dispatch prompt: "for the pull-quote, cite a Green primary source and confirm verbatim before proposing."
- **Concurrent `npm run build` in N worktrees corrupts the shared vite/astro cache** — all Part 4 agents flagged a false-alarm CSS build error from parallel-build interleaving. Mitigation: skip build verify; rely on CI post-merge.
- **Mermaid click-to-enlarge modal shipped** (`00ce1f1b`). Inline diagrams stay column-fit with a small "Click to enlarge" hint; click opens a fullscreen modal that clones the SVG, sizes it from its viewBox, and renders both-axis-scrollable at fullscreen. Light + dark themes verified. Close via X / Escape / backdrop click; focus restores; body scroll locks.
- **`scripts/ab ask-codex` wrapper "drops stdin silently" data point may be stale.** 2026-04-30 incident report says two dispatches died with zero-byte output. 2026-05-01 session 2 ran two clean stdin-via-`-` dispatches (smoke + PR #708 review) without reproduction. Could be 0.128.0 fix, could be transient. Don't retire the note yet, but stop preemptively bypassing the wrapper.
- **Headless-Claude delegation rule reinforced** (memory `feedback_dispatch_to_headless_claude.md`). Tier 1 reader-aid design is exactly the kind of clean text-writing job that should go to `Agent(subagent_type="general-purpose")` so the orchestrator's context survives the batch. Plan locked in for Part 4.
- **Reader-aid layout pattern frozen** — Tier 1 + 2 + 3, non-invasive on bit-identical prose. Canonical doc: `docs/research/ai-history/READER_AIDS.md`. Ch01 prototype on `main` as `49e8e299` (PR #566). Tier 3 coeditor: Claude proposes / Codex reviews adversarially / Gemini for tie-breaks (Issue #564, memory `feedback_tier3_coeditor_pattern.md`).
- **Math rendering live** — `remark-math` + `rehype-katex` + KaTeX CSS in `astro.config.mjs` (commit `8c93d8db`). `$inline$` and `$$display$$` LaTeX both render. Fixes inline math across the entire AI history book retroactively.
- **STEP 0 routing shipped** (`scripts/dispatch_research_verdict.py`): branch-prefix routing puts Claude on anchor verification for `codex/394-...` research PRs and Codex for `claude/394-...` PRs.
- **`gemini-3.1-pro-preview` capacity flap intermittent under combined load.** When two chains run in parallel, pro-preview can return 429 "No capacity available". Fix: `KUBEDOJO_GEMINI_REVIEW_MODEL=gemini-3-flash-preview` env override.
- **Codex `mode="danger"` rule** for end-to-end dispatches that include `git push` + `gh pr create` (memory `feedback_codex_danger_for_git_gh.md`). Workspace-write silently fails on `.git/worktrees/.../index.lock` and `api.github.com`.
- **PR #558 (Ch51) and PR #565 (Ch52)** — both stale, content already on main. Close or rebase the index.md changes before next prose chain ships.
- **`shipped_unreviewed` is a distinct status on the quality board** (PR #873 merged 2026-05-04). 192 modules are stage=UNAUDITED + score≥4 + no banner — i.e. ad-hoc shipments that never went through the pipeline state machine. They are NOT bookkeeping artifacts that can be backfilled with synthetic verdicts (`feedback_citation_verify_or_remove.md` honesty rule applies to provenance too). They genuinely need cross-family review when bandwidth allows. Live counts: `done=78, needs_rewrite=424, needs_review=59, shipped_unreviewed=192, both=1`.
- **Codex-out window protocol** (memory `feedback_codex_offline_contingency.md`) — when all Codex tiers are out of weekly quota, Gemini OAuth is sole cross-family reviewer; Claude can write *or* review (not the same PR); `ab discuss` runs 2-way with explicit note in any Decision Card. Pre-window checklist: open all pending PRs and dispatch reviews early before Gemini OAuth burns. Window 2026-05-04 → ~11:00 2026-05-05.
- **`scripts/dispatch_smart.py` extended with `--agent {claude,codex}`** (PR #872 — open, NEEDS CHANGES holding for smoke-test). Mirrors PR #870 economical-multi-agent tiering for cross-agent dispatches: search→haiku/mini, edit/draft→sonnet/spark, review/architect→sonnet/gpt-5.5. Once codex is back: smoke-test the new model strings, document, re-request review, merge.
- **User-side dirty files to leave alone**: `test_rendering.js` (orphan). The dashboard-panels stash was popped + finished + merged (`c70b6f2d`) in 2026-05-01 session 2 — both panels live at `http://127.0.0.1:8768/`.
- **PR-hygiene gotchas memorised this session** (memory `feedback_verify_aids_after_branch.md`): (1) `git checkout -b` on a chapter file lacking a trailing newline silently drops working-tree edits — defensive habit `printf '\n' >> ch-XX-*.md` before any branch op + `git show --stat HEAD` after every commit; (2) PRs branched from main while Codex's Part 9 chain advances can pick up unrelated chapter commits in their diff — recreate from current main + cherry-pick.
- **🚨 SOURCE-OF-PROBLEM: web-blindness in v2 quality dispatch — RESOLVED 2026-05-05 session 2.** PR #888 squash-merged (`733cfff0`). All three codex code paths now honor `KUBEDOJO_CODEX_SEARCH=1`: `dispatch_codex` (writer), `dispatch_codex_patch` (review-driven edit applier), `CodexAdapter.build_invocation` (book chapter dispatch). The `_CLAUDE_TEXT_ONLY_DISALLOWED` set no longer blocks `WebFetch`+`WebSearch`. Cross-family verified by codex gpt-5.5 with `--search`. Three Phase D book-audit pilots (ch-33 / ch-34 / ch-58) in session 2 found ~88% R:supported each with wrong-specifics localized to peripheral sections (cast, glossary, `:::note[matters]`) — all fixed inline. Phase E sweep Part 1 shipped; Parts 2-9 in progress.
- **`--search` is a TOP-LEVEL codex flag, not an exec subflag.** Order matters: `codex --search exec --skip-git-repo-check --sandbox <mode>`. Putting it after `exec` silently drops it. Patched `dispatch_codex` respects this; new dispatch wrappers must too.
- **Smoke-testing `--search` by output comparison is a diagnostic mistake.** Codex may already know the answer from training data on stable facts. Use a *threading* test — pass an invalid sandbox value (`KUBEDOJO_CODEX_SANDBOX=BOGUS`) and confirm the codex CLI itself rejects it. That's the only way to prove env-var threading end-to-end.
- **GH_TOKEN does not propagate to codex sandbox** (intentional per `_agent_env("codex")` in `dispatch.py`). The #388 batch flags `module_skip: no_pr_in_response` whenever codex tries `gh pr create` from inside its dispatch. Workaround: orchestrator opens the PR manually after codex pushes the branch (used for both PR #886 and PR #887). Permanent fix would wire the batch's post-codex hook to detect "branch pushed but no PR" and open it from the orchestrator's env.
- **Two structural issues recurring across codex #388 drafts** (PR #886 + PR #887 both have them): stray `# Module X.Y: Title` H1 after frontmatter (creates duplicate visible title in Starlight) and inline metadata instead of blockquote-with-bold-labels per `module-quality.md`. Prompt-shape issue in `module-rewriter-388.md` / `module-writer.md`, not search-related. Fix the prompt before the next #388 batch.

## End-of-session ritual

1. Write today's full handoff to `docs/session-state/YYYY-MM-DD-<topic>.md` (or `YYYY-MM-DD-<topic>-N.md` if multiple in a day).
2. Edit this file:
   - Promote the new file to **Latest handoff** (overwrite the row).
   - Move the previous Latest into **Predecessor chain** (newest at top).
   - Update **Cross-thread notes** — add new long-running items, prune resolved ones.
3. Update **TODO** + **Blockers** below with current state (briefing API depends on these headings).
4. Commit with `docs(status): handoff <date> — <topic>` style message.

The pre-2026-04-28 archive is intentionally append-only; don't edit it. If a stale entry needs correction, do it in this index instead.

## Current State

**746 English modules** across 8 published tracks. **312 Ukrainian translations** (~42% — Prereqs 98%, Linux 100%, K8s 77%, Cloud 92%, Platform 1%, On-Prem/AI/AI-ML 0%). Counts surface live via the new "Module Distribution" dashboard panel at `http://127.0.0.1:8768/`.

**Website:** https://kube-dojo.github.io/ (Starlight/Astro, ~1,350 pages, ~30-40s build)

**Site tabs:** Home | Fundamentals | Linux | Cloud | Certifications | Platform | On-Premises | AI | AI/ML Engineering

## Curriculum Summary

| Track | Modules | Status |
|-------|---------|--------|
| Fundamentals | 44 | Complete |
| Linux Deep Dive | 37 | Complete |
| Cloud | 85 | Complete |
| Certifications (CKA/CKAD/CKS/KCNA/KCSA/Extending + 12 learning paths) | 195 | Complete |
| Platform Engineering | 210 | Complete |
| On-Premises Kubernetes | 51 | Complete (needs Gemini review) |
| AI | 25 | Expanded bridge track; needs production-quality upgrades |
| AI/ML Engineering | 99 | Complete (expanded with #677 ML/RL/DL batch 2026-05-01: 12 Tier-1 ML + 7 Tier-2 ML + 2 RL + 2 new DL + 1 DL fix) |
| **Total** | **746** | **Complete** |

Per-track breakdowns (Cert / Cloud / On-Prem / Platform / AI/ML / AI / UK translations) live in the curriculum directories themselves; they were trimmed from this file 2026-04-28 because they were stable reference material that didn't belong in a session index.

## Quality Standard

**Rubric-based quality system** (`docs/quality-rubric.md`): 7 dimensions scored 1-5. Pass = avg ≥ 3.5, no dimension at 1.

**Audit results** (`docs/quality-audit-results.md`, 2026-04-03): 31 modules scored. Overall avg 3.3/5. Gold standard: Systems Thinking (4.6), On-Prem Case (4.4). 5 critical stubs fixed, 3 high-priority modules improved. 8 medium + 11 low priority remain.

**Systemic issues addressed**: formal learning outcomes added to all rewritten modules + writer prompt; inline active-learning prompts added (was back-loaded in 87% of modules); scenario-based quizzes replace recall-only.

## Open GitHub Issues

Issue tracker shrunk 40 → 14 open via batch triage 2026-05-01 (session 4); then 14 → 12 open via #379 + #385 closures (session 5). 28 total closures since session 4.

| # | Issue | Status |
|---|-------|--------|
| #14 | Curriculum Monitoring & Official Sources | Open — permanent tracker |
| #143 | Ukrainian Translation — Full Site Coverage | Open (~40%) |
| #186 | Ukrainian Translations sync with quality improvements | Open |
| #197 | On-Premises Track expansion | Open — strategic per `project_onprem_vision.md` |
| #341 | Citation residuals auto-resolver epic | Open — tooling, separate from #388 |
| #342 | pipeline-v4 rename `needs_human` → `residuals_filed` | Open — 5-min mechanical task |
| #344 | Citation-residuals: extend resolver | Open — in flight per worktree `codex/issue-344` |
| #373 | Liveness probes for LLM-dispatch subprocesses | Open — stalled but coherent infra-reliability scope |
| #386 | Phase F: Lab quality audit | Open — labs ≠ modules; distinct from #388 |
| **#388** | **Site-wide module quality rewrite** | **Active — Day 3 KCNA proving batch in flight (28 modules, single-lane). Day 2 pilot complete (9/9 in 90 min). Verifier + brief addendum + dispatcher hardened. Remaining: KCNA bucket → KCSA bucket → 226 critical-rubric modules.** |
| #391 | Public-facing status page | Open — borderline-stale; coherent product idea |
| #393 | Post-#388 ML/AI history depth pass | Open — explicitly post-#388 |

## TODO

**Next session — Phase E sweep continuation is the active workstream:**

- [ ] **Check on Part 2 dry-run (background bash task `bmdolfkpn`)** — launched at session-2 handoff (~10:35 local), ETA ~11:30. If still running on session resume, wait for notification. If completed, inspect `.tmp/sweep-logs/ch-{09..16}-{audit,diff}.*` and `.tmp/sweep-logs/summary.jsonl`.
- [ ] **Phase E sweep Part 2 (ch-09..ch-16)** — apply audited fixes (re-using dry-run audit JSONs, no re-dispatch), build verify, commit + push. Apply script in `docs/session-state/2026-05-05-2-phase-d-pilots-and-phase-e-sweep.md` "What remains to do" section; same shape as Part 1 commit `0a6cb725`.
- [ ] **Phase E sweep Parts 3-9** — repeat-cycle: dispatch dry-run via `.venv/bin/python scripts/sweep_ai_history_aids.py --part N --dry-run` → inspect → apply → build → commit. ~1 hr dry-run + 5 min apply per Part. **Part 5 skips ch-33+ch-34; Part 8 skips ch-58.** Total ~8 Parts × ~1 hr = ~8 hr wall remaining.
- [ ] **Re-request Gemini review on PR #872** (codex routing tiers + smoke results). Queued from session 1+2.
- [ ] **Sweep #5 (Cloud + AI-ML + On-Prem)** — incident-dedup. PR #884 + #885 ARE NOW MERGED this session. Refresh audit on post-merge main and dispatch sweep #5 via `dispatch_smart.py edit` (per locked pattern).
- [ ] **Sweep #6 forbidden-trope rewrite** — `ai-ml-engineering/mlops/module-1.3-cicd-for-ml.md` (1 file). Inline orchestrator work, no agent dispatch.
- [ ] **Sweep #7 — CKA / CKAD final cleanup.** Confirm via fresh audit after sweep #5 lands; expect 1–3 files.
- [ ] **Promote `scripts/check_incident_reuse.py` to CI-required** once curriculum-wide count reaches 0.
- [ ] **Update `module-rewriter-388.md` / `module-writer.md` prompts** to ban stray `# Module X.Y: Title` H1 + inline metadata before next #388 batch (recurring shape error in PR #886 + PR #887 codex drafts; would otherwise come back).
- [ ] **Restart Claude Code** so fresh `GEMINI_API_KEY` from `~/.bash_secrets` (`...Oq3Aq7Bw`) flows into env. Without restart, every Gemini dispatch needs `source ~/.bash_secrets &&` prefix (workaround works; not blocking).
- [ ] **Coherence sweep at KCNA bucket boundary** (B3 protocol, carryover): one fresh codex+gemini pair reads the cumulative diff across the 28 KCNA modules merged 2026-05-02.
- [ ] **Investigate the 8 module_skip events from KCNA batch** (carryover, codex now back).
- [ ] **Decide A2 plumbing vs straight to KCSA bucket-2** (carryover).
- [ ] **Optional — rotate the leaked GH_TOKEN** (carryover; functional impact none).

**Routing locked (still active):**
- **No Gemini in writer routing.**
- **Codex drafts** all #388 rewrites (gpt-5.5, danger mode, reasoning=high).
- **Gemini reviews** cross-family (~22% real-issue intervention rate in Day 2 pilot). APPROVE_WITH_NITS now correctly routes to C3 fix-up lane (was silently auto-merging in Day 2; fixed this session in `dispatch_388_pilot.py`).
- **Within #388: REWRITE-tier first** (~165 modules at <18 wpp), REVIEW-tier waits.

**Carryover residuals from prior handoffs:**
- [ ] **Ch02 line-119 fix** — "five years before" → "more than a decade before". One-line fix; low priority.
- [ ] **Ch32–Ch37 research-pending** under strict-gh audit (out of #559 scope; could spin a fresh sub-issue).

**Review-coverage rollup matrix (Ch02–Ch15, scope of #559 — COMPLETE):**

| Ch | Prose PR | Markers present | Audit verdict |
|----|----------|-----------------|---------------|
| Ch02 | #479 | claude + codex | OK (claude marker backfilled 2026-05-01) |
| Ch03 | #480 | claude + codex | OK (codex marker backfilled 2026-05-01) |
| Ch04 | #481 | claude + codex | OK (post-#421 standard) |
| Ch05 | #483 | claude + codex | OK (post-#421 standard) |
| Ch06 | #496 | claude + codex | OK (post-#421 standard) |
| Ch07 | #497 | claude + codex | OK (post-#421 standard) |
| Ch08 | #498 | claude + codex | OK (post-#421 standard) |
| Ch09 | #499 | claude + codex | OK (post-#421 standard) |
| Ch10 | #500 | claude + gemini | OK (pre-#421 standard, valid evidence) |
| Ch11 | #451 | claude + gemini | OK (pre-#421 standard) |
| Ch12 | #452 | claude + gemini | OK (pre-#421 standard) |
| Ch13 | #454 | claude + gemini | OK (pre-#421 standard) |
| Ch14 | #455 | claude + gemini | OK (pre-#421 standard) |
| Ch15 | #506 | claude + gemini | OK (pre-#421 standard) |

**Background / lower priority:**
- [ ] Google Search Console verification — user will paste the meta-tag token (or HTML file). Then submit `https://kube-dojo.github.io/sitemap-index.xml` to GSC.
- [ ] PR #558 + PR #565 stale-prose cleanup (content already on main)
- [ ] **387 modules at critical rubric score (<2.0)** — content-debt workstream, codex-blocked, separate from #388.

## Blockers

- **Phase E sweep Parts 2-9 still pending** — Part 2 dry-run in flight at handoff time (background bash task `bmdolfkpn`); Parts 3-9 not started. Total ~8 hr wall remaining. Active workstream, not urgent.
- **PR #872 still open + NEEDS CHANGES** — Gemini re-review queued. Carry-over from session 1+2.
- **Stale `GEMINI_API_KEY` in this Claude Code process** — user rotated 2026-05-04 session 3; new key in `~/.bash_secrets` (ends `Oq3Aq7Bw`); current process still has old `...rpXZEPl4`. Per-call workaround: `source ~/.bash_secrets &&` before any `dispatch.py gemini` invocation. Permanent fix: `/exit` and restart Claude Code.
- **GH_TOKEN does not propagate to codex sandbox env** (intentional design in `_agent_env`, not a bug). #388 batches keep flagging `module_skip: no_pr_in_response` whenever codex tries `gh pr create` from inside the dispatch. Workaround: orchestrator opens PR manually after codex pushes the branch.
- **GH_TOKEN value still exposed in 2026-05-04 session 2 transcript.** Functional impact none, operational hygiene only. Rotate when convenient.

## Key Decisions

- Migrated from MkDocs Material to Starlight (Astro) — faster builds, proper i18n, modern stack
- `scripts/dispatch.py` replaces `ai_agent_bridge/` — direct CLI dispatch, no SQLite broker
- GH Actions pinned to commit SHA, requirements locked with hashes, Dependabot enabled
- Pinned `zod@3.25.76` (zod v4 breaks Starlight schema validation)
- `defaultLocale: 'root'` for Starlight i18n — English at root URLs, Ukrainian at `/uk/`
- On-prem modules written by parallel agents (~500 lines each), need Gemini adversary review
- 2026-04-28: STATUS.md migrated to **index pattern** (was a 1623-line forever-growing log). Per-session handoffs now live in `docs/session-state/`; this file just points at them.

---
**Maintenance Rule**: Claude updates this file at session end or after completing modules. Per-session detail goes into a new `docs/session-state/YYYY-MM-DD-*.md` file, not inline.
