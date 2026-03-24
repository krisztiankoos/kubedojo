# Enterprise & Hybrid Cloud

**Landing zones, governance, compliance, hybrid connectivity, fleet management, and multi-cloud operations for organizations running Kubernetes at scale.**

Enterprise Kubernetes is not a technology problem -- it is an organizational one. The hardest challenges are not "how do I deploy a pod" but "how do I provision 50 production-ready clusters for 160 teams with consistent security, compliance, and cost controls." This part covers the architecture and automation that separates companies where a new team waits 14 weeks for a cluster from companies where they get one in 30 minutes. You will learn landing zones, policy as code, continuous compliance, hybrid cloud connectivity, fleet management, and zero trust -- the building blocks of enterprise-grade Kubernetes operations.

---

## Modules

| # | Module | Complexity | Time | What You'll Learn |
|---|--------|------------|------|-------------------|
| 1 | [Enterprise Landing Zones & Account Vending](module-1-landing-zones.md) | `[COMPLEX]` | 3h | Control Tower, Azure Landing Zones, GCP Org Hierarchy, automated account vending |
| 2 | [Cloud Governance & Policy as Code](module-2-governance.md) | `[COMPLEX]` | 2.5h | SCPs, Azure Policy, GCP Org Policies, Kyverno, OPA Gatekeeper, unified governance |
| 3 | [Continuous Compliance & CSPM](module-3-compliance.md) | `[COMPLEX]` | 2h | SOC 2/PCI-DSS/HIPAA mapping, automated evidence collection, compliance drift detection |
| 4 | [Hybrid Cloud Architecture (On-Prem to Cloud)](module-4-hybrid.md) | `[COMPLEX]` | 3h | VPN/dedicated connections, EKS Anywhere, Anthos, unified identity, data replication |
| 5 | [Multi-Cloud Fleet Management (Azure Arc / GKE Fleet)](module-5-fleet-management.md) | `[COMPLEX]` | 2.5h | Fleet inventory, centralized policy, configuration management, multi-cloud GitOps |
| 6 | [Multi-Cloud Provisioning with Cluster API](module-6-cluster-api.md) | `[COMPLEX]` | 3h | CAPI architecture, provider ecosystem (CAPA/CAPZ/CAPG), declarative cluster lifecycle |
| 7 | [Multi-Cloud Service Mesh (Istio Multi-Cluster)](module-7-multi-cloud-mesh.md) | `[COMPLEX]` | 3h | Istio multi-cluster topologies, SPIFFE/SPIRE trust, cross-cloud routing, mTLS |
| 8 | [Enterprise GitOps & Platform Engineering](module-8-enterprise-gitops.md) | `[COMPLEX]` | 2.5h | Backstage IDP, ArgoCD at scale, ApplicationSets, multi-tenant Git strategies, RBAC |
| 9 | [Zero Trust Architecture in Hybrid Cloud](module-9-zero-trust.md) | `[COMPLEX]` | 2.5h | BeyondCorp, Identity-Aware Proxies, micro-segmentation, VPN replacement, SLSA |
| 10 | [FinOps at Enterprise Scale](module-10-enterprise-finops.md) | `[COMPLEX]` | 2h | Enterprise discounts, forecasting, chargeback models, multi-cloud cost, FinOps culture |

**Total time**: ~26 hours

---

## Prerequisites

- [Cloud Architecture Patterns](../architecture-patterns/README.md) -- managed vs self-managed, multi-cluster theory, cloud IAM, VPC topologies
- [Advanced Cloud Operations](../advanced-operations/README.md) -- multi-account architecture, networking, DR fundamentals
- Experience with at least one hyperscaler and Kubernetes in production

## What's Next

After Enterprise & Hybrid Cloud, continue with:

- [Cloud-Native Managed Services](../managed-services/README.md) -- databases, messaging, serverless, caching, and more
- [Advanced Cloud Operations](../advanced-operations/README.md) -- cross-cluster networking, active-active, cost optimization
