# Independent Gap Analysis – KubeDojo (Restarted, May 2026)

**Status**: Fresh start incorporating all verified corrections and current connector state.
**Date**: May 16, 2026
**Conducted by**: Grok (via active GitHub connector)
**Previous attempt**: Superseded (old #1231 closed in favor of this clean version).

## Executive Summary

KubeDojo has a strong theory-first foundation with confirmed coverage in key areas such as FinOps and major cloud providers (EKS, GKE, AKS, etc.). The project now includes a dedicated labs repository (`kube-dojo/kubedojo-labs`) containing interactive scenarios (user reports >150 labs). 

The main curriculum is well-structured but remains intentionally light on embedded hands-on content. The primary opportunities lie in tighter integration between the main modules and the labs repo, deeper coverage of emerging 2026 topics (AI/MLOps, advanced observability, policy evolution), improved learner progression/assessment, and automation/quality infrastructure.

This restarted analysis is model-agnostic regarding effort levels (previous benchmarks were not run on Grok 4.3).

## Verified Current State

- **Main repo**: `kube-dojo/kube-dojo.github.io` — ~295+ modules, theory-first, prerequisites complete, certifications strong, Platform Engineering substantial.
- **Labs repo**: `kube-dojo/kubedojo-labs` — Interactive Killercoda-powered scenarios. Significant practical complement (claimed >150 labs). CI/testing infrastructure in progress.
- **Learn Ukrainian**: Visible and connected via Hermes.
- **FinOps & Cloud**: Confirmed present in main curriculum.
- **Effort-level context**: No assumptions from prior tests; recommendations focus on output characteristics.

## Strengths

- Excellent theory-first philosophy and searchable, version-controlled content.
- Strong prerequisite and certification tracks.
- Confirmed FinOps and major cloud provider coverage.
- Dedicated Ukrainian IT engineers tribute and bilingual potential.
- Separate labs repo shows commitment to practical application.
- Active development and connector integration for AI assistance.

## Gaps & Opportunities

### 1. Integration Between Main Curriculum and Labs Repo (High Priority)
- Limited visible mapping between modules and specific lab scenarios.
- Opportunity to create “lab companion” sections or metadata linking theory modules to hands-on exercises.
- CI/testing for labs is emerging (see open issue in labs repo) — needs expansion to full K8s scenarios.

### 2. Emerging & Advanced Topics (2026 Relevance)
- AI/MLOps on Kubernetes (GPU scheduling, inference serving, operators) — neural-dojo migration is positive but needs deeper integration.
- Advanced observability (OpenTelemetry, eBPF tooling at scale).
- Policy-as-Code evolution and runtime security patterns.
- Inner dev loop, progressive delivery, and chaos engineering depth.

### 3. Learner Experience & Assessment
- No explicit persona-based learning paths with milestones.
- Assessment remains relatively light compared to theory depth.
- Opportunity for self-validation rubrics and end-to-end project scenarios.

### 4. Automation, Quality & Maintainability
- Strong pre-commit and pipeline foundation in main repo.
- Labs repo CI is a good start but needs broader coverage and status badges.
- Cross-track consistency checks and automated link/validation could be strengthened.

### 5. Cross-Project Synergies
- Potential for technical Ukrainian vocabulary tracks or bilingual lab instructions linking to Learn Ukrainian project.

## Prioritized Recommendations

**Phase 1 (Quick Wins – 1-2 weeks)**
- Create mapping between main modules and labs scenarios.
- Enhance labs repo CI and add status visibility.
- Add persona-based learning path documents.

**Phase 2 (High-Value Expansion)**
- Accelerate AI/MLOps track integration.
- Expand observability, policy, and progressive delivery depth.
- Build end-to-end practitioner project scenarios.

**Phase 3 (Polish & Scale)**
- Living glossary and bilingual support.
- Automated quality gates across both repos.
- Contributor-friendly templates and good-first-issue curation.

## Notes on AI Assistance & Workflow

- Effort-level guidance should be validated against actual output quality on curriculum tasks rather than assumed from prior tests.
- Medium effort often provides good balance for technical accuracy + pedagogical clarity; high effort can introduce unnecessary complexity.
- Recommend periodic re-evaluation as models evolve.

## Next Steps

1. Full inventory and categorization of `kubedojo-labs` scenarios.
2. Detailed mapping exercise between modules and labs.
3. Implementation of Phase 1 recommendations.

---

*This restarted analysis supersedes all previous versions. All statements are based on currently verified connector state and user corrections.*