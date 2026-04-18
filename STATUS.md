# Session Status

> **Read this first every session. Update before ending.**

## Active Work (2026-04-18, session 2)

Lead: Claude. Citation-first infra for automated pipeline (Gemini 3.1 Pro writes → Codex reviews/fact-checks/applies). Full handoff: [`docs/sessions/2026-04-18-lead-dev-citation-infra.md`](./docs/sessions/2026-04-18-lead-dev-citation-infra.md).

**Session 2 progress (autonomous run):**
- Pushed 4 citation-infra commits to `origin/main` (build verified green, 1797 pages, 0 errors).
- Read V3 proposal #217 in full — most already shipped via #219/#224/#226. Remaining: pin Gemini, per-track rubric, sampling.
- Drafted 4 infra GH issues: **#276** (local API GH endpoints), **#277** (local API build endpoints), **#278** (pipeline v3 remaining — 3 PRs), **#279** (automated citation pipeline wiring).
- Opened **PR #280** — citation-aware module page design proposal (3-tab Theory/Practice/Citations via Starlight `<Tabs syncKey>`; resolves design scope of #273).
- Delegated all 5 to Codex via agent bridge (task-ids infra-276..279, review-280). Build-report-in-PR-body convention included in each delegation to avoid future Claude-side build hops.

**Role-swap decision:** picked Codex adversarial on every PR (role-swap per PR) — consistent with Codex-as-reviewer memory and #235 queue ownership pattern. Gemini stays as fallback only if Codex is unavailable.

**Session 2 — autonomous run additions (while user AFK):**

API stability (committed d19a1016):
- Killed runaway API instance (stale port 8768 lock); restarted on 127.0.0.1:8768 (per `localhost_only` rule).
- Added `timeout=5` to two unbounded `subprocess.run` calls in `scripts/local_api.py` (`build_worktree_status`, `list_worktrees`) — they can hang the briefing endpoint when git hits lock contention.
- Wrapped `do_GET` response-send in `BrokenPipeError`/`ConnectionResetError` handler — client disconnects no longer noisy.
- Explicit `ThreadingHTTPServer.daemon_threads = True` and `allow_reuse_address = True` — eliminates "port in use" startup loops.

Pipeline running (foreground now; survives session end):
- Killed 4 stale PID files (patch/review/write/pipeline).
- Started 3 v2 workers via Bash background: patch-worker (PID 87463), review-worker (PID 87941), write-worker (PID 88084). All orphaned from parent shell.
- Sleep interval: 30s. Workers are live and picking up work — pipeline moved 1 pending_patch job through patch → review since start.
- Current state: `pending_review: 1, pending_write: 0, pending_patch: 0, done: 566, dead_letter: 0, in_progress: 0`. Convergence 99.8%. flapping_count: 12 (up 1; minor).

Codex delegation (with `CODEX_BRIDGE_MODE=danger` since prior `safe` mode blocked writes + network):
- `infra-277-v2` (rerun of #277 build API endpoints) — running in background task `b6n7sz9tq`.
- `infra-235-race` (CRITICAL parallel race condition from #235, lines 3049-3063 / 190-201 / 2848-2864 of v1_pipeline.py) — running in background task `b7u81pwe3`.
- Earlier `review-280` completed successfully: substantive adversarial review (5 concrete findings, corpus-scan evidence). Posted as PR comment since Codex has no network to `gh`.

Issue triage / comments posted:
- **#217** — status audit posted; remaining work tracked in #278; recommended close once PR 1 lands.
- **#274** — ACs 1-3 marked done with commit references; AC4 handled; AC5 deferred to #279.
- **#180** — AI Foundations batch reset announced per #274.

Uncommitted in tree:
- `src/content/docs/k8s/lfcs/module-1.4-storage-services-and-users-practice.md` — **worker WIP**, don't touch.
- `docs/sessions/` — untracked session handoff docs.

**PRs opened by Codex, reviewed by Claude (role-swap convention). All OPEN, waiting for user merge:**

#235 HIGH-severity bug fixes (14 of 14 closed):
- #281 serialize parallel worker state mutations (CRITICAL)
- #284 defer data_conflict check until after draft
- #285 malformed review JSON fails closed
- #287 _merge_fact_ledgers is pure and idempotent
- #288 needs_independent_review revived for last-resort approvals
- #289 content-aware ledger covers late sections (40k windowing)
- #290 check_failures tracks consecutive, not lifetime
- #291 last-attempt edit success triggers re-review, not reject
- #292 write-only preserves draft for review (regression test lock-in)
- #293 fresh restart clears stale resume metadata
- #294 review fallback chain continues to last-resort
- #295 severe rewrite clears stale targeted_fix, uses full rewrite model
- #296 CHECK retries in-function, shields outer circuit breaker
- #297 rewrite retries extract knowledge packet from baseline
- #298 unify retry policy across serial/parallel/reset-stuck modes

#277/#278 infra (pipeline v3 remaining + build API):
- #282 feat: /api/build/run + /api/build/status (#277) — **note: re-run ruff + npm run build from main before merge**, worktree build-path bug was environmental
- #283 refactor: pin Gemini writer model via single constant (#278 PR 1, narrow)
- #286 refactor: pin Gemini constant across remaining workers (#278 PR 1b, full)

#273 design:
- #280 citation-aware module page design proposal

**Codex queue state (max 2 concurrent):**
- `infra-276` (GH API endpoints — /api/gh/issues + /api/gh/prs) — running in background task `bfg1f3zn8`.
- `infra-278-pr2` (per-track rubric profiles with default.yaml reproducing current behavior) — running in background task `bmvx43o2c`.
- Queued for next invocation: `infra-278-pr3` (second-reviewer 10-20% sampling), `infra-279` (citation pipeline wiring), plus #235 MEDIUM-severity items.

**Service state at handoff:**
- API: 127.0.0.1:8768, PID 82871, uptime 20 min
- v2 patch/review/write workers: PIDs 87463 / 87941 / 88084, all 19 min uptime
- dev server: unchanged (existing)
- Pipeline convergence: 99.8%, 566 done, 1 pending_review (flapping on LFCS module-1.4, known issue being tracked in #235)
- 0 stale pid files, 1 stopped (pipeline supervisor, intentional — workers are direct-run, no supervisor layer active)

## Current State

**726 modules** across 8 published tracks. **115 Ukrainian translations** (~16% — certs + prereqs; AI/ML and AI not yet translated).

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
| AI | 21 | Expanded bridge track; needs production-quality upgrades |
| AI/ML Engineering | 79 | Complete (expanded beyond Phase 4b; needs ongoing quality upgrades) |
| **Total** | **726** | **Complete** |

### Certifications Breakdown
| Cert | Modules |
|------|---------|
| CKA | 47 |
| CKAD | 30 |
| CKS | 30 |
| KCNA | 28 |
| KCSA | 26 |
| Extending K8s | 8 |

### Cloud Breakdown
| Section | Modules |
|---------|---------|
| Hyperscaler Rosetta Stone | 1 |
| AWS Essentials | 12 |
| GCP Essentials | 12 |
| Azure Essentials | 12 |
| Architecture Patterns | 4 |
| EKS Deep Dive | 5 |
| GKE Deep Dive | 5 |
| AKS Deep Dive | 4 |
| Advanced Operations | 10 |
| Managed Services | 10 |
| Enterprise & Hybrid | 10 |

### On-Premises Breakdown
| Section | Modules |
|---------|---------|
| Planning & Economics | 4 |
| Bare Metal Provisioning | 4 |
| Networking | 4 |
| Storage | 3 |
| Multi-Cluster | 3 |
| Security | 4 |
| Operations | 5 |
| Resilience | 3 |

### Platform Engineering Breakdown
| Section | Modules |
|---------|---------|
| Foundations | 32 |
| Disciplines (SRE, Platform Eng, GitOps, DevSecOps, MLOps, AIOps + Release Eng, Chaos Eng, FinOps, Data Eng, Networking, AI/GPU Infra, Leadership) | 71 |
| Toolkits (17 categories) | 96 |
| Supply Chain Defense Guide | 1 |
| CNPE Learning Path | 1 |

### AI/ML Engineering Breakdown
Migrated from neural-dojo + modernized with 8 new 2026 modules (#199, Phase 4b). All modules passed the v1 quality pipeline at 38–40/40.

| Section | Modules |
|---------|---------|
| Prerequisites | 4 |
| AI-Native Development | 10 |
| Generative AI | 6 |
| Vector DBs & RAG | 6 |
| Frameworks & Agents | 10 |
| AI Infrastructure | 5 |
| Advanced GenAI | 11 |
| Multimodal AI | 4 |
| Deep Learning | 7 |
| MLOps | 12 |
| Classical ML | 3 |
| History | 1 |

### AI Breakdown
Top-level learner-first AI track designed as the bridge from AI literacy into real AI building and then into AI/ML Engineering.

| Section | Modules |
|---------|---------|
| Foundations | 6 |
| AI-Native Work | 4 |
| AI Building | 4 |
| Open Models & Local Inference | 7 |
| AI for Kubernetes & Platform Work | 4 |

### Ukrainian Translations
| Track | Translated | Total |
|-------|-----------|-------|
| Prerequisites | 35 | 33 |
| CKA | 47 | 47 |
| CKAD | 30 | 30 |
| CKS | 0 | 30 |
| KCNA | 0 | 28 |
| KCSA | 0 | 26 |
| AI/ML Engineering | 0 | 68 |
| **Total** | **115** | **626** |

## Quality Standard

**Rubric-based quality system** (docs/quality-rubric.md): 7 dimensions scored 1-5. Pass = avg >= 3.5, no dimension at 1.

**Audit results** (docs/quality-audit-results.md, 2026-04-03): 31 modules scored.
- Overall avg: 3.3/5 (GOOD)
- Gold standard: Systems Thinking (4.6), On-Prem Case (4.4)
- 5 critical stubs fixed (expanded from 49-74 lines to 266-918 lines)
- 3 high-priority modules improved (API Deprecations, etcd-operator, Deployments)
- Remaining: 8 medium, 11 low priority modules need improvements

**Systemic issues found & being addressed**:
1. No modules had formal learning outcomes → added to all rewritten modules + codified in writer prompt
2. Active learning back-loaded to end in 87% of modules → inline prompts added to rewrites
3. Quiz questions tested recall not understanding → scenario-based quizzes in all rewrites

## Open GitHub Issues

| # | Issue | Status |
|---|-------|--------|
| #14 | Curriculum Monitoring & Official Sources | Open |
| #143 | Ukrainian Translation — Full Coverage | Open (~40%) |
| #157 | Supabase Auth + Progress Migration | Open |
| #156 | CKA Parts 3-5 Labs | Open |
| #165 | Epic: Pedagogical Quality Review | Open (Phases 1-3,5 done; Phase 4: CKA/CKAD/On-Prem complete) |
| #180 | Elevate All Modules to 4/5 | Open (CKA/CKAD/On-Prem done; CKS/KCNA/KCSA/Cloud/Platform pending) |
| #177 | Improve Lowest-Quality Modules | Open (8 critical/high done, ~19 remaining) |
| #179 | Improve Lowest-Quality Labs | Open (blocked on Phase 3 lab audit) |
| #199 | AI/ML Engineering track migration + modernization | Open (Phase 4b done; Phase 7 cross-link + Phase 8 UK translate remain) |
| #200 | AI/ML local per-section module numbering (filename rename) | Open (delegated to Codex in worktree) |

## Recently Closed (Session 3)
| # | Issue | Status |
|---|-------|--------|
| #174 | Phase 1: Research Educational Frameworks | Closed — docs/pedagogical-framework.md |
| #175 | Phase 2: Create Quality Rubric | Closed — docs/quality-rubric.md |
| #176 | Phase 3: Audit Modules Against Rubric | Closed — 31 modules scored |
| #178 | Phase 5: Codify Quality Standards | Closed — writer prompt, rules, skill updated |
| #170-173 | Gemini's buzzword issues | Closed — replaced by concrete sub-tickets |

## TODO

- [x] Prerequisites: all 33 modules improved (outcomes, inline prompts, quiz upgrades, emoji fixes) — EN + UK complete
- [x] Linux: all 37 modules improved (outcomes added) — EN + UK complete
- [x] CKA: all 41 modules — outcomes + inline prompts + scenario quizzes (Parts 0-5 complete) — EN complete, UK outcomes synced
- [x] CKAD: all 24 modules — outcomes + inline prompts + scenario quizzes — EN complete, UK outcomes synced
- [x] CKS: 30 modules — outcomes + inline prompts + scenario quizzes — EN complete, UK outcomes synced
- [x] KCNA: 28 modules — outcomes + inline prompts + scenario quizzes — EN complete, UK outcomes synced
- [x] KCSA: 26 modules — outcomes + inline prompts + scenario quizzes — EN complete, UK outcomes synced
- [x] On-Premises: all 30 modules — inline prompts + narrative between code blocks + quiz improvements
- [x] Fundamentals track reorder: Zero to Terminal → Everyday Linux → Cloud Native 101 → K8s Basics → Philosophy & Design → Modern DevOps
- [x] Zero to Terminal: Next Module link fixes (0.1→0.2, UK 0.2→0.3)
- [x] Git Deep Dive course: 10 modules + Git Basics in ZTT — #190
- [x] v1 quality pipeline built: AUDIT→WRITE→REVIEW→CHECK→SCORE — #188
- [x] Gap detection (within-track + cross-track) — #188
- [x] Zero to Terminal: 10/10 modules pass pipeline (29+/35)
- [x] All prerequisites pass pipeline (43/44 done, 29+/35) — #180
- [x] 6 rejected prereq modules rewritten by Gemini + passed pipeline (35/35, 34/35)
- [x] ZTT module numbering collision fixed (0.6 git-basics + 0.6 networking → renumbered 0.7-0.11)
- [x] Pipeline v2: Gemini defaults, e2e command, track aliases, safety hardening
- [x] uk_sync.py consolidated: status/detect/fix/translate/e2e with track aliases
- [x] Certs pipeline: 150/164 pass, 3 fail, 8 WIP — #180
- [x] Cloud pipeline: 80/86 pass — #180
- [x] Linux pipeline: 34/38 pass — #180
- [x] Pipeline v3: knowledge packets, block-level rewrite, ASCII→Mermaid — #192
- [x] Pipeline: section index.md rewrite (EN) + auto-translate (UK) after section completes
- [x] Pipeline: 41 integration tests (test_pipeline.py)
- [x] Pipeline: subsection aliases (ztt, cka, aws, etc.) + auto-discover from any dir path
- [x] Nav fix: all 156 index.md files (EN+UK) set to sidebar.order: 0
- [x] Nav fix: slug corrections for ZTT module-0.6, git-deep-dive modules 1 and 9
- [x] K8S_API check: demoted to WARNING, strips code blocks + inline code (false positives)
- [x] .staging file glob bug fixed (was creating bogus state entries)
- [x] Token analysis: subagents are 74% of volume but mostly cheap cache reads. Not the cost monster claimed.
- [x] AI/ML Engineering track migrated from neural-dojo (60 existing + 8 new 2026 modules, #199 Phase 4b). All 8 new pass v1 pipeline at 40/40.
- [x] v1 pipeline fixes: 300s→900s timeouts, targeted-fix / nitpick / previous_output scaffolding, short-output guard (enables quality-rubric retries to converge)
- [ ] AI/ML Engineering #199 remaining: Phase 7 cross-link (run), Phase 8 UK translate (skipped for now)
- [ ] AI/ML Engineering #200: local per-section module numbering (delegated to Codex)
- [ ] Remaining pipeline: On-Premises (30), Platform (209), Specialty (18) — #180
- [ ] Stuck modules: ~11 at WRITE (Gemini rejection loop), need knowledge packet retry
- [ ] ASCII→Mermaid conversion pass for all 587 modules — #193 (after #180)
- [ ] UK prereqs translation: re-sync after pipeline rewrites
- [ ] Lab quality audit and improvements — #179

## Blockers
- Gemini CLI output inconsistency: sometimes writes to files, sometimes returns to stdout — handled but fragile

## Key Decisions
- Migrated from MkDocs Material to Starlight (Astro) — faster builds, proper i18n, modern stack
- `scripts/dispatch.py` replaces `ai_agent_bridge/` — direct CLI dispatch, no SQLite broker
- GH Actions pinned to commit SHA, requirements locked with hashes, Dependabot enabled
- Pinned zod@3.25.76 (zod v4 breaks Starlight schema validation)
- `defaultLocale: 'root'` for Starlight i18n — English at root URLs, Ukrainian at `/uk/`
- On-prem modules written by parallel agents (~500 lines each), need Gemini adversary review

---
**Maintenance Rule**: Claude updates this file at session end or after completing modules.
