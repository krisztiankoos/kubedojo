# Independent gap analysis — KubeDojo curriculum (2026-05-17)

> Same brief sent to **grok-4** and **deepseek V4 Pro** so verdicts are directly comparable. **Do not coordinate.** GH umbrella: [#1299](https://github.com/kube-dojo/kube-dojo.github.io/issues/1299).

## Your role

You are an independent curriculum reviewer. Your job is to do a fresh gap analysis of KubeDojo (free open-source cloud-native curriculum, ~757 modules across 8 published tracks) and tell us **what we missed, what we over-scoped, and what we mis-prioritized**. We have an existing gap inventory + roadmap; your goal is to challenge it, not ratify it.

We have access to your work via `scripts/dispatch_smart.py review --agent {grok|deepseek} --mode workspace-write`. You have read access to the entire repo + write access to your output path.

## Repo orientation (read these first)

| What | Where | Why |
|---|---|---|
| Project overview | `CLAUDE.md` | Tracks, sidebar, build, agent recipe |
| Quality rubric | `docs/quality-rubric.md` + `docs/pedagogical-framework.md` | Quality bar every module must meet |
| Module standard | `.claude/rules/module-quality.md` | Required sections, Bloom L3+, ≥4 per dimension |
| Stage-0 gap inventory | `docs/research/content-gaps-2026-05.md` | 4 tiers of candidate gaps, unlock criteria |
| Stage-4 triangulated roadmap | `docs/research/gap-triangulation-roadmap-2026-05.html` | 51 rows: Tier 1=4, Tier 2=20, Tier 3=27 deferred |
| KodeKloud + CNCF + Cert triangulation | `docs/research/kodekloud-gap-analysis-2026-05-12.html` | 67KB master input to the roadmap |
| Stage-1 briefs (already-deep-dived gaps) | `docs/research/gap-engineering-craft.md`, `docs/research/gap-llm-native-app-synthesis.md`, `docs/research/harness-symphony-gap.md`, `docs/research/ai-engineering-foundations-stage0-2026-05-15.html` | Where our thinking is concrete |
| Live quality state | `curl -s http://127.0.0.1:8768/api/quality/scores?summary=1` | Currently 757 modules, avg 4.27, 157 critical |
| Per-track structure | `ls src/content/docs/` | Fundamentals, Linux, Cloud, Certifications (k8s/), Platform, On-Premises, AI, AI/ML Engineering |
| Filled recently | PRs #1220 (Harness Eng 2.1), #1221 (Symphony 2.2), #1226 (Context Engineering Fundamentals) | Don't re-flag these |

## What we've decided so far (challenge or ratify)

**Tier 1 (high-confidence, ≥2 sources):**
1. Azure Application Gateway operator path → 1 module, Cloud/Azure
2. Azure App Service operations → 1 module, Cloud/Azure
3. Streaming ops (NATS + Strimzi + CloudEvents) → 2-3 modules, Platform Disciplines (hard-blocked: Platform Disciplines critical-count was 65, may have dropped)
4. Cloud Custodian policy-as-code governance → 1 module, Cloud/Enterprise-Hybrid

**Tier 2 (single-source, ab-discuss pending) — top entries:**
- Harness engineering + Symphony orchestration (✅ shipped as #1220 + #1221)
- Software engineering craft for operators (4-7 modules)
- LLM-native application engineering on K8s (4-7 modules)
- Engineer mental models for distributed systems (2-3)
- Cost lens as cross-cutting habit (2-3)
- DVC, Great Expectations, GitHub Actions, Ansible operator arc, ML repo hygiene
- Azure Event Hub/Grid, Azure SQL, production model-serving traffic patterns, drift-triggered auto-retraining, CML, Dapr/Buildpacks, gRPC/Envoy, AWS data ingestion, HCP Terraform, Azure Backup/Site Recovery

**Tier 3 (deferred):** Jenkins (excluded by policy), Docker absolute-beginner arc (likely covered), ARM Templates/Bicep migration, CNCF edge/bare-metal control plane, AWS security selector, Azure storage operator tooling, Azure governance mechanics, Azure network troubleshooting, AWS database edge, compliance-aware platform eng, hardware+facilities, KServe deep-dive, Seldon/BentoML, Prefect/Argo Workflows, bare-metal MLOps recipe, vector DBs, multi-cluster beyond CAPI, workload identity across clouds, Release Eng / Chaos Eng / FinOps / Eng Leadership / Advanced Networking / Data Eng / Extending K8s / eBPF / Edge K8s expansions.

## Constraints (hard rules — do not violate)

1. **Jenkins is excluded by policy** — prefer GitHub Actions, GitLab CI, ArgoCD. Don't propose Jenkins coverage.
2. **No personal-life framing** — no interview prep, job-search, role-transition modules. Curriculum is for engineers regardless of life situation.
3. **Quality > coverage.** 5 excellent modules beat 55 mediocre. Don't propose stub-quality "coming soon" entries.
4. **Quality-floor gate is real.** Drafting unlocks per-track when track critical-count < 50. If you propose a module in a rewrite-first track (Platform Disciplines, Platform Toolkits, CKS, CKAD), flag the dependency explicitly.
5. **No teaching listicles.** Modules must teach a mental model + scaffold complexity, not dump bullets. See `feedback_teaching_not_listicles` precedent.
6. **No embedded / firmware / microcontroller / non-cloud-native scope.**
7. **Modern defaults.** No deprecated tooling unless the gap is explicitly about migration paths.

## What we want from you (your output)

Write a structured HTML report to **your assigned output path** (see Dispatch line at bottom). Reports get served via the local API at `http://127.0.0.1:8768/artifacts/`.

Sections required (in order):

### 1. Verdict on existing roadmap (table)

For each row in our existing Tier 1 + Tier 2 (24 rows total — pull them from `docs/research/gap-triangulation-roadmap-2026-05.html`), produce a verdict:

| Existing gap | Your verdict | Rationale | Adjusted priority | Source citation |
|---|---|---|---|---|

**Verdicts** (pick one): `ratify`, `over-scoped` (you'd cut it), `under-scoped` (we should expand), `mis-prioritized` (move to higher/lower tier), `already-covered` (cite existing module path), `wrong-track-placement` (suggest correct), `nuance-needed` (specific change).

**Citation required for every verdict.** Cite either:
- An existing module path in `src/content/docs/...` (for `already-covered`)
- A primary source URL (cncf.io, vendor docs, official cert blueprint) for net-new claims
- A specific section of the kodekloud-gap-analysis or your independent web research

### 2. Net-new gaps (table)

Gaps we **missed**. Provide ≥3, max 15.

| Net-new gap | Why we missed it | Tier suggestion (1/2/3) | Track placement | Estimated module count | Primary source citation |
|---|---|---|---|---|---|

Same citation discipline as section 1. **Do not propose gaps that fail any of the hard constraints above.**

### 3. Over-scoped removals (list)

Items in our roadmap (any tier) you'd cut entirely. Justify each with a source-cited reason. Examples of valid reasons: covered by an existing module, audience too narrow, technology effectively deprecated, deliverable would be a tool catalog not a lesson.

### 4. Priority reordering (numbered list, top 10)

Given everything above + the quality-floor gate, list the 10 highest-leverage **next moves** in order. Each item must specify: track, module key, dependency chain (what must score ≥3 first), estimated codex-call count.

### 5. Confidence + disagreement self-report

End with a short section:
- **High-confidence verdicts** (gaps where your independent reasoning + sources unambiguously agree with our existing inventory)
- **Low-confidence verdicts** (where you'd want a second human reviewer)
- **Things you'd flag in `ab discuss`** (genuinely controversial calls)

This last section is load-bearing — we use it to decide what to surface as a Decision Card.

## Methodology requirements

- **Use deterministic computation where possible** (memory `feedback_deterministic_over_hallucination`). For coverage claims, grep the repo:
  ```bash
  grep -rli "kserve" src/content/docs/ | head
  find src/content/docs -name "*kafka*"
  ```
  Don't recall — measure.
- **For external claims, cite a URL you actually verified.** Don't fabricate. If you can't verify, mark `unverified` and skip the citation. (See memory `feedback_gemini_hallucinates_anchors` for the failure mode.)
- **Do not coordinate with the other reviewer.** Your verdict must be independent. If we find suspicious convergence, we'll route to `ab discuss` for adversarial pressure-test.
- **You can read any file in the repo.** Use `cat`, `grep`, `find`, `curl http://127.0.0.1:8768/api/...` freely.
- **Token discipline:** Don't read whole files when grep + selective read works. Target your report at ~3000-6000 words of substance, not 20000 words of summary.

## Dispatch metadata

- **Output path** (you'll be told which when dispatched):
  - `audit/gap-analysis-2026-05-17/grok-report.html` (if you are grok)
  - `audit/gap-analysis-2026-05-17/deepseek-report.html` (if you are deepseek)
- **Cap**: one dispatch, ~90 min wall clock max.
- **Format**: standalone HTML (self-contained; matches `docs/session-state/*.html` style — see one for reference). Use `<table>`, `<ul>`, semantic HTML; no external CSS.
- **First-line of report**: a 2-3 sentence TL;DR of your verdict ("ratify N/24, cut M, add K net-new, top move is X").

## Why this is happening

We've shipped ~750 modules and our internal gap analysis (Stage-0 inventory + Stage-4 roadmap) has been claude/codex/gemini-driven for 5 weeks. We want fresh adversarial perspectives from grok and deepseek before committing to another wave of writing. Convergent LLM priors are a known risk; your independent verdicts are how we surface real blind spots.

Output is for synthesis into `docs/research/gap-plan-2026-05-17.html`, which then becomes per-module GH issues + codex writer dispatches. Quality > speed.
