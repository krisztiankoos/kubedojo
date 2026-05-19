---
title: "GitOps & Deployments Toolkit"
sidebar:
  order: 0
  label: "GitOps & Deployments"
---
> **Toolkit Track** | 5 Modules | ~4 hours total

## Overview

The GitOps & Deployments Toolkit covers the essential tools for declarative, Git-driven Kubernetes deployments. These tools implement the GitOps methodology—using Git as the single source of truth for infrastructure and application configuration.

This toolkit builds on the concepts from [GitOps Discipline](../../../disciplines/delivery-automation/gitops/) and shows you how to implement those principles with production-grade tools.

## Prerequisites

Before starting this toolkit:
- [GitOps Discipline](../../../disciplines/delivery-automation/gitops/) — GitOps principles and practices
- Basic Kubernetes knowledge (Deployments, Services)
- Git fundamentals
- kubectl experience

## Modules

| # | Module | Complexity | Time |
|---|--------|------------|------|
| 2.1 | [ArgoCD](module-2.1-argocd/) | `[COMPLEX]` | 45-50 min |
| 2.2 | [Argo Rollouts](module-2.2-argo-rollouts/) | `[COMPLEX]` | 45-50 min |
| 2.3 | [Flux](module-2.3-flux/) | `[COMPLEX]` | 40-45 min |
| 2.4 | [Helm & Kustomize](module-2.4-helm-kustomize/) | `[MEDIUM]` | 35-40 min |
| 2.5 | [Dapr and Buildpacks — Application Definition Beyond Helm](module-2.5-dapr-buildpacks/) | `[COMPLEX]` | 60-70 min |

## Learning Outcomes

After completing this toolkit, you will be able to:

1. **Deploy with ArgoCD** — Applications, sync strategies, App of Apps, RBAC
2. **Implement progressive delivery** — Canary, blue-green, automated analysis
3. **Use Flux GitOps Toolkit** — Sources, Kustomizations, image automation
4. **Package with Helm** — Charts, templates, dependencies, releases
5. **Customize with Kustomize** — Bases, overlays, patches, components
6. **Define beyond Helm** — Dapr Components plus Buildpacks-built images, with reproducible builds and runtime building blocks decoupled from Helm templates

## Tool Selection Guide

```
WHICH GITOPS TOOL?
─────────────────────────────────────────────────────────────────

Need a UI?
├── Yes → ArgoCD
│         • Great visualization
│         • Developer-friendly
│         • Easy onboarding
│
└── No → Flux
         • CLI/automation-first
         • Image automation built-in
         • Lower resource usage

Need progressive delivery?
├── Yes → Argo Rollouts
│         • Canary deployments
│         • Blue-green switches
│         • Automated analysis
│
└── No → Standard Deployment
         • Rolling updates
         • Simpler setup

Package management?
├── Third-party apps → Helm
│                      • Chart repositories
│                      • Version management
│                      • Release tracking
│
└── Own apps → Kustomize
               • No templates
               • Pure YAML
               • Environment overlays

Application definition beyond Helm?
├── Standard app image build → Buildpacks
│                             • No Dockerfile
│                             • Curated builders
│                             • Rebase and SBOM discipline
│
└── Runtime building blocks → Dapr Components
                              • State, pub-sub, secrets
                              • Sidecar API contract
                              • Plain manifest review path

BEST PRACTICE: Combine tools!
• Helm for packaging
• Kustomize for environment variants
• Buildpacks for repeatable image builds
• Dapr for shared runtime building blocks
• ArgoCD/Flux for deployment
• Argo Rollouts for progressive delivery
```

## The GitOps Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    GITOPS DEPLOYMENT STACK                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  GIT REPOSITORY (Source of Truth)                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  • Helm charts                                            │   │
│  │  • Kustomize overlays                                     │   │
│  │  • Plain YAML manifests                                   │   │
│  │  • Application configurations                             │   │
│  └────────────────────────────┬─────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              GITOPS CONTROLLER                            │   │
│  │                                                           │   │
│  │  ┌─────────────────┐      ┌─────────────────┐            │   │
│  │  │     ArgoCD      │  OR  │      Flux       │            │   │
│  │  │                 │      │                 │            │   │
│  │  │ • Sync to Git   │      │ • Reconcile     │            │   │
│  │  │ • Detect drift  │      │ • Image update  │            │   │
│  │  │ • Visualize     │      │ • Notifications │            │   │
│  │  └─────────────────┘      └─────────────────┘            │   │
│  └────────────────────────────┬─────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              PROGRESSIVE DELIVERY                         │   │
│  │                                                           │   │
│  │  ┌─────────────────┐                                      │   │
│  │  │  Argo Rollouts  │                                      │   │
│  │  │                 │                                      │   │
│  │  │ • Canary        │                                      │   │
│  │  │ • Blue-Green    │                                      │   │
│  │  │ • Analysis      │                                      │   │
│  │  └─────────────────┘                                      │   │
│  └────────────────────────────┬─────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              KUBERNETES CLUSTER                           │   │
│  │                                                           │   │
│  │  Desired state from Git = Actual state in cluster        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Study Path

```
Module 2.1: ArgoCD
     │
     │  GitOps with UI, sync strategies
     ▼
Module 2.2: Argo Rollouts
     │
     │  Progressive delivery, canary, analysis
     ▼
Module 2.3: Flux
     │
     │  GitOps toolkit, image automation
     ▼
Module 2.4: Helm & Kustomize
     │
     │  Package management, overlays
     ▼
Module 2.5: Dapr and Buildpacks
     │
     │  Application definition beyond Helm
     ▼
[Toolkit Complete] → CI/CD Pipelines Toolkit
```

## Key Concepts

### GitOps Principles in Practice

| Principle | ArgoCD Implementation | Flux Implementation |
|-----------|----------------------|---------------------|
| **Declarative** | Application CRD | Kustomization/HelmRelease |
| **Versioned** | Git repo as source | GitRepository source |
| **Automated** | Auto-sync policy | Reconciliation loop |
| **Auditable** | Git history + UI | Git history + events |

### When to Use What

```
DEPLOYMENT SCENARIO                    TOOL RECOMMENDATION
─────────────────────────────────────────────────────────────────

Installing Prometheus                  → Helm chart
├── Available from chart repo
├── Many configuration options
└── Upstream maintains it

Your microservice to 3 envs           → Kustomize overlays
├── Same base, different configs
├── You control the manifests
└── Simple differences

Microservices share runtime needs     → Dapr + Buildpacks
├── No Dockerfile per repo
├── State/pub-sub/secrets as Components
└── Plain manifests instead of template sprawl

Breaking change in API                → Argo Rollouts canary
├── Need gradual rollout
├── Want automated rollback
└── Have metrics to analyze

100 apps across 10 clusters           → ArgoCD ApplicationSets
├── Template-based generation          OR Flux multi-cluster
├── Consistent patterns
└── Central visibility
```

## Related Tracks

- **Before**: [GitOps Discipline](../../../disciplines/delivery-automation/gitops/) — Why GitOps works
- **Related**: [Observability Toolkit](../../observability-intelligence/observability/) — Monitor deployments
- **Related**: [IaC Tools](../../infrastructure-networking/iac-tools/) — Infrastructure delivery with GitOps
- **After**: [CI/CD Pipelines Toolkit](../ci-cd-pipelines/) — Build before deploy

---

*"GitOps is not about tools—it's about the practice of using Git as source of truth. These tools make that practice operational."*
