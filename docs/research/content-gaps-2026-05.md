# KubeDojo content gap inventory — 2026-05-12

> **Status**: Stage 0 in the gap-planning workflow. Captures candidate gaps;
> per-gap research briefs (Stage 1) live as separate files in
> `docs/research/gap-*.md`. Gap unlocks for drafting only after Stage 2
> (`ab discuss` pressure-test), Stage 3 (parent epic + child issues),
> Stage 4 (sidebar placement branch), and Stage 5 (critical-rubric drops
> below threshold).

## How to use this doc

This is an inventory, not a roadmap. Each row captures a candidate gap with a
leverage tier and current status. New module drafts MUST NOT start from this
file — they must go through Stage 1 (per-gap research brief), Stage 2
(`ab discuss` pressure-test), Stage 3 (GH epic + child issues), Stage 4
(sidebar placement on a tracking branch), then Stage 5 (schedule unlock).

**Anti-rot guard**: gap unlock criterion is dependency-bound, not
calendar-bound. A gap unlocks for drafting when:

- Its per-gap brief has been written and `ab discuss`-validated,
- The relevant track's critical-rubric module count is below ~50,
- A parent epic + child GH issues exist for the track, AND
- A sidebar placement branch has been merged with stub pages.

## Tier 1 — High-leverage, complements existing audience

| Gap | Description | Status | Brief |
|---|---|---|---|
| **AI-native engineering work** | Harness engineering, agent legibility, in-repo system-of-record, eval-driven dev, feedback-loop design. The layered-harness mental model is the core teaching point. | **Researched** (Stage 1 complete) | [`harness-symphony-gap.md`](harness-symphony-gap.md) |
| **Software engineering craft** | Reading code (not writing), debugging as discipline, code review practice, writing RFCs/ADRs, technical writing for engineers. KubeDojo teaches Kubernetes *operations* but not the *engineering judgment* used around it. | Unresearched | — |
| **LLM-native application engineering** | RAG depth, agents in production, evals as production gate, vLLM/serving on K8s, GPU scheduling reality. Pieces exist in `ai/ai-ml-engineering` but no "build a real LLM app on K8s" arc. | Partially covered; needs gap brief | — |

## Tier 2 — Foundational mental models

| Gap | Description | Status | Brief |
|---|---|---|---|
| **Engineer mental models** | Partial failure, time/clocks, idempotency, eventual consistency *as practiced*. Distributed-systems intuition gap — CKA track teaches `kubectl`, not why the world is async. | Unresearched | — |
| **Cost lens as cross-cutting thread** | "Everything has a cost" appearing in every module's "operate in prod" content, not just one FinOps section. | Unresearched | — |

## Tier 3 — Niche but real audience

| Gap | Description | Status | Brief |
|---|---|---|---|
| **Compliance-aware platform engineering** | HIPAA, PCI-DSS, SOC 2, FedRAMP, GDPR, air-gapped deployments. Niche but the entire regulated-industry market needs it. | Unresearched | — |
| **Hardware + facilities awareness** | PXE/BMC/IPMI, switches, racks, power/cooling — bare-metal companion track. Adjacent to the on-prem vision. | Captured in `memory/project_onprem_vision.md`, unshipped | — |

## Tier 4 — Topical gaps (carried from 2026-04-25 analysis)

Source: `memory/project_topical_gap_analysis.md`. Verify counts against live
`/api/quality/scores` before acting — quality state decays as backfill/rewrite
lands.

- **KServe** — no standalone deep-dive
- **Seldon Core / BentoML** — no dedicated coverage
- **Prefect** — no module (Airflow IS covered at `data-engineering/module-1.5-airflow.md`)
- **Bare-metal MLOps end-to-end recipe** — pieces exist (RKE2, GPU operator, Kubeflow) but no walkthrough tying them
- **Vector DBs** (Milvus, Weaviate, Qdrant) — increasingly important for LLMOps
- **Multi-cluster depth** (Karmada, Liqo, ClusterNet — beyond CAPI)
- **Workload identity mechanics** across the three clouds (IRSA, Workload Identity, Azure AD WI)
- **Service mesh internals** (xDS, envoy filters, sidecar-less mesh)
- **Release Engineering** (5 modules from 2026-03-24 expansion plan: progressive delivery, OpenFeature, ephemeral envs, rollback, release pipelines at scale)
- **Chaos Engineering** (5 modules: principles, LitmusChaos/Chaos Mesh, game days, failure sim, chaos in prod)
- **FinOps expansion** (Kubecost/OpenCost, showback/chargeback, cost-aware architecture, FinOps culture)
- **Engineering Leadership** (incident command, blameless postmortems, on-call, ADRs/RFCs, stakeholder management)
- **Advanced Networking** (DNS at scale, CDN/edge, WAF/DDoS, BGP, IPv6/dual-stack)
- **Data Engineering on K8s** (Kafka/Strimzi, Spark operator, Flink operator, lakehouse, real-time ML)
- **Extending K8s expansion** (Kubebuilder controllers, controller testing, admission webhooks, API aggregation, scheduler plugins, multi-cluster CAPI/Karmada)
- **eBPF foundation module**
- **Edge K8s module**

## What's deliberately NOT on this list

- Anything driven by personal-life framing (interview prep, role transitions) — per `feedback_no_personal_framing.md`
- "Coverage for coverage's sake" — every gap must have a teaching outcome that doesn't already exist
- Modules whose primary value is keyword/SEO bait — content quality > traffic
- Embedded / firmware / microcontroller content — outside the cloud-native scope

## Critical context — quality is the dominant gap, not coverage

Per `memory/project_topical_gap_analysis.md` (2026-04-25) and verified by
current `/api/quality/scores`: **~250 modules sit at critical rubric score
(<2.0)**. Most "missing" content is present-but-shallow or present-but-uncited.
The #388 chain is the right tool for the dominant gap.

**Implication for new content**: every gap-filling module added before the
critical-rubric count drops increases the average pain, not the quality. The
sequencing rule (gap unlock criterion above) exists for this reason.

Restated bluntly: the standing brief is **5 excellent beats 55 mediocre**
(`feedback_teaching_not_listicles.md`). Adding 30 stub-quality "coming soon"
modules across the gap list defeats this. Each gap unlock should produce
modules at the upper end of the rubric.

## Workflow reference

1. **Stage 0 — Gap inventory** (this doc)
2. **Stage 1 — Per-gap research brief** — `docs/research/gap-<name>.md`, modeled on `harness-symphony-gap.md`
3. **Stage 2 — Pressure-test** — `ab discuss --with claude,codex,gemini` per gap
4. **Stage 3 — GH epic + child issues** — parent per gap, child per module, with brief attached
5. **Stage 4 — Sidebar placement** — `placement/<gap>` branch with substantive stub pages (not content-free placeholders)
6. **Stage 5 — Schedule unlock** — critical-rubric threshold + dependency-bound
7. **Stage 6 — Write** via codex writer + cross-family reviewer + density verifier

## Related artifacts

- [`harness-symphony-gap.md`](harness-symphony-gap.md) — Stage 1 brief for AI-native engineering work
- `memory/project_topical_gap_analysis.md` — 2026-04-25 topical gap snapshot
- `memory/project_onprem_vision.md` — on-prem expansion vision
- `memory/project_expansion_plan.md` — 2026-03-24 expansion plan items
- `docs/quality-rubric.md` — the rubric every gap-filling module must satisfy
- `docs/review-protocol.md` — cross-family review requirement
