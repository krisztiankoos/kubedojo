# AI History Research Wiki

This directory contains the operational research files for the definitive 68-chapter AI History Epic (#394).

## Status Board (rebalanced 2026-04-27)

Ownership rebalance triggered by two signals: (1) Gemini was previously assigned 5 of 9 Parts (1, 2, 6, 7, 8) — single point of failure for the book; (2) Gemini self-admitted to systemic URL/anchor hallucination across his 37 chapters (epic commit `03640e20`, Issue #421), which makes citation-heavy contract drafting a structural mismatch for him. The rebalance routes anchor-heavy Parts to Codex (his `pdftotext`+`grep` workflow is the strongest), narrative-heavy Parts to Claude (integration + careful framing), and keeps Gemini on his already-in-flight Parts plus universal gap-analysis duty.

| Part | Range | Owner | Strength match | Status |
|---|---|---|---|---|
| 1 — Mathematical Foundations | Ch 1-5 | **Gemini** | already in flight | Cleanup of citation hallucinations from earlier draft (#421); 4/5 ready_to_draft_with_cap, Ch1 in gap_analysis_received |
| 2 — Analog Dream & Digital Blank Slate | Ch 6-10 | **Gemini** | already accepted | Complete (5/5 accepted) |
| 3 — Birth of Symbolic AI & Early Optimism | Ch 11-16 | **Claude** | narrative integration | Ch11-Ch14 `capacity_plan_anchored` (Codex anchor draft + Gemini gap audit + Claude integration); Ch15-Ch16 researching |
| 4 — First Winter & Shift to Knowledge | Ch 17-23 | **Codex (new)** | anchor-heavy archival (Lighthill, Mansfield, expert systems) | 0/7 — moved from unclaimed |
| 5 — Mathematical Resurrection | Ch 24-31 | **Codex** | anchor extraction from papers | 4/8 prose_ready; Ch28-31 researching |
| 6 — Rise of Data & Distributed Compute | Ch 32-40 | **Gemini** | already in flight | 5/9 accepted, 4/9 prose_review |
| 7 — Deep Learning Revolution & GPU Coup | Ch 41-49 | **Gemini** | already in flight (do NOT disrupt) | 1/9 prose_review, 8/9 anchors_in_progress |
| 8 — Transformer, Scale & Open Source | Ch 50-58 | **Codex (new)** | dense paper-anchor extraction | 0/9 — reassigned from Gemini (none yet started) |
| 9 — Product Shock & Physical Limits | Ch 59-68 | **Claude (new)** | recent narrative + careful framing | 0/10 — moved from unclaimed |

**Active drafting load (rough):** Codex ~20 chapters; Claude ~16 chapters; Gemini ~12 chapters + cleanup of Parts 1-2.

**Universal duty:** every chapter contract requires dual cross-family review (Codex anchor verification + Gemini gap analysis) before status flips to `accepted`. See `TEAM_WORKFLOW.md`.

All prose drafting is paused until chapter contracts hit `accepted`.

## Source of Truth — where chapter status lives

| Layer | What it covers | Where |
|---|---|---|
| Per-chapter (canonical) | full status, owner, Green/Yellow/Red counts, review_state, notes | `chapters/ch-XX-<slug>/status.yaml` |
| Per-Part (high-level) | this README's Status Board | `docs/research/ai-history/README.md` |
| Per-chapter (live aggregated) | structured roll-up of all 68 status.yaml files | `GET /api/briefing/book` (operator API) |
| Tracking issues | per-Part checklists + cross-family review log | GitHub #394 (epic), #399-#407 (Parts 1-9) |
| Activity feed | merged commits + bridge messages, last 24h | `GET /api/activity?limit=30` |

When you advance a chapter, update the chapter's `status.yaml`. The README Status Board and the API rollup will reflect it on next read; you don't need to touch this file unless the *Part owner* changes or rationale shifts.

## Per-Chapter Status (live snapshot)

| # | Chapter | Owner | Status |
|--:|---|---|---|
|  1 | The Laws of Thought | Gemini | gap_analysis_received |
|  2 | The Universal Machine | Gemini | ready_to_draft_with_cap |
|  3 | The Physical Bridge | Gemini | ready_to_draft_with_cap |
|  4 | The Statistical Roots | Gemini | ready_to_draft_with_cap |
|  5 | The Neural Abstraction | Gemini | ready_to_draft_with_cap |
|  6 | The Cybernetics Movement | Gemini | accepted |
|  7 | The Analog Bottleneck | Gemini | accepted |
|  8 | The Stored Program | Gemini | accepted |
|  9 | The Memory Miracle | Gemini | accepted |
| 10 | The Imitation Game | Gemini | accepted |
| 11 | The Summer AI Named Itself | Claude | capacity_plan_anchored |
| 12 | Logic Theorist & GPS | Claude (Codex draft) | capacity_plan_anchored |
| 13 | The List Processor | Claude (Codex draft) | capacity_plan_anchored |
| 14 | The Perceptron | Claude (Codex draft) | capacity_plan_anchored |
| 15 | The Gradient Descent Concept | Claude | researching |
| 16 | The Cold War Blank Check | Claude | researching |
| 17 | The Perceptron's Fall | Codex | researching |
| 18 | The Lighthill Devastation | Codex | researching |
| 19 | Rules, Experts, and the Knowledge Bottleneck | Codex | researching |
| 20 | Project MAC | Codex | researching |
| 21 | The Rule-Based Fortune | Codex | researching |
| 22 | The Lisp Machine Bubble | Codex | researching |
| 23 | The Japanese Threat | Codex | researching |
| 24 | The Math That Waited for the Machine | Codex | prose_ready |
| 25 | The Universal Approximation Theorem 1989 | Codex | prose_ready |
| 26 | Bayesian Networks | Codex | prose_ready |
| 27 | The Convolutional Breakthrough | Codex | prose_ready |
| 28 | The Second AI Winter | Codex | researching |
| 29 | Support Vector Machines (SVMs) | Codex | researching |
| 30 | The Statistical Underground | Codex | researching |
| 31 | Reinforcement Learning Roots | Codex | researching |
| 32 | The DARPA SUR Program | Gemini | accepted |
| 33 | Deep Blue | Gemini | prose_review |
| 34 | The Accidental Corpus | Gemini | accepted |
| 35 | Indexing the Mind | Gemini | prose_review |
| 36 | The Multicore Wall | Gemini | accepted |
| 37 | Distributing the Compute | Gemini | prose_review |
| 38 | The Human API | Gemini | accepted |
| 39 | The Vision Wall | Gemini | accepted |
| 40 | Data Becomes Infrastructure | Gemini | prose_review |
| 41 | The Graphics Hack | Gemini | prose_review |
| 42 | CUDA | Gemini | anchors_in_progress |
| 43 | The ImageNet Smash | Gemini | anchors_in_progress |
| 44 | The Latent Space | Gemini | anchors_in_progress |
| 45 | Generative Adversarial Networks | Gemini | anchors_in_progress |
| 46 | The Recurrent Bottleneck | Gemini | anchors_in_progress |
| 47 | The Depths of Vision | Gemini | anchors_in_progress |
| 48 | AlphaGo | Gemini | anchors_in_progress |
| 49 | The Custom Silicon | Gemini | anchors_in_progress |
| 50 | Attention Is All You Need | Codex | researching |
| 51 | The Open-Source Distribution Layer | Codex | researching |
| 52 | Bidirectional Context | Codex | researching |
| 53 | The Dawn of Few-Shot Learning | Codex | researching |
| 54 | The Hub of Weights | Codex | researching |
| 55 | The Scaling Laws | Codex | researching |
| 56 | The Megacluster | Codex | researching |
| 57 | The Alignment Problem | Codex | researching |
| 58 | The Math of Noise | Codex | researching |
| 59 | The Product Shock | Claude | researching |
| 60 | The Physics of Scale | Claude | researching |
| 61 | Inference Economics | Claude | researching |
| 62 | The Edge Compute Bottleneck | Claude | researching |
| 63 | The Open Weights Rebellion | Claude | researching |
| 64 | The Monopoly | Claude | researching |
| 65 | The Data Exhaustion Limit | Claude | researching |
| 66 | The Energy Grid Collision | Claude | researching |
| 67 | The Chip War | Claude | researching |
| 68 | The Infinite Datacenter | Claude | researching |

Snapshot taken 2026-04-27. The `/api/briefing/book` endpoint returns this same data live.

The team workflow is maintained in `TEAM_WORKFLOW.md`. It defines the gates between research contracts, gap analysis, anchor extraction, prose readiness, drafting, and cross-family review.

## Structure

*   `source-catalog.md`: Shared bibliography for recurring sources (e.g., Hodges, Gleick, Dyson).
*   `TEAM_WORKFLOW.md`: cross-family review protocol, dual-reviewer requirement, hallucination-filter rules.
*   `chapters/`: 68 chapter directories. Each must hit the KubeDojo sourcing standard (claim-level anchors, page/section references, independent confirmation) before unlocking for prose drafting.

## Ownership & Tracking Issues

Coordination happens across 9 Part Tracking issues linked to Epic #394:

- #399 — Part 1: The Mathematical Foundations (Ch 1-5) — **Gemini**
- #400 — Part 2: The Analog Dream & Digital Blank Slate (Ch 6-10) — **Gemini**
- #401 — Part 3: The Birth of Symbolic AI & Early Optimism (Ch 11-16) — **Claude**
- #402 — Part 4: The First Winter & The Shift to Knowledge (Ch 17-23) — **Codex** (reassigned 2026-04-27, was unclaimed)
- #403 — Part 5: The Mathematical Resurrection (Ch 24-31) — **Codex**
- #404 — Part 6: The Rise of Data & Distributed Compute (Ch 32-40) — **Gemini**
- #405 — Part 7: The Deep Learning Revolution & GPU Coup (Ch 41-49) — **Gemini**
- #406 — Part 8: The Transformer, Scale & Open Source (Ch 50-58) — **Codex** (reassigned 2026-04-27, was Gemini; no chapters were in flight)
- #407 — Part 9: The Product Shock & Physical Limits (Ch 59-68) — **Claude** (reassigned 2026-04-27, was unclaimed)

Note: The 630 changed files in the original PR include automatically generated placeholder directories for the 68 chapters to ensure proper boundaries. These placeholders are intentional and expected in diff reviews.
