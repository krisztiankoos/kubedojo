---
title: "Changelog"
sidebar:
  order: 2
  label: "What's New"
---
## March 2026 — Ecosystem Update + Quality Review + 21 Certifications

**The biggest update since KubeDojo launched.** 60+ new modules, 30+ updated, every module quality-reviewed, and coverage expanded to 21 certifications.

### Zero to Terminal — Absolute Beginner Track

10 new modules for people with **zero IT background**. From "What is a computer?" to deploying a website — with a restaurant kitchen analogy running throughout. Available in English and Ukrainian.

[Start here &rarr;](prerequisites/zero-to-terminal/index.md)

### Ukrainian Translation (Українська)

24 pages translated to Ukrainian including the full beginner track, Philosophy & Design, and Cloud Native 101. Language switcher in the header. Translation follows learn-ukrainian project quality rules (4-check: Russicism, Surzhyk, Calque, Paronym).

### KCNA: AI/ML, WebAssembly, Green Computing

3 new modules for the November 2025 KCNA curriculum update:
- [AI/ML on Kubernetes](k8s/kcna/part3-cloud-native-architecture/module-3.8-ai-ml-cloud-native.md) — GPU scheduling, LLM inference, Kubeflow/KServe
- [WebAssembly](k8s/kcna/part3-cloud-native-architecture/module-3.9-webassembly.md) — Wasm vs containers, WasmEdge, SpinKube
- [Green Computing](k8s/kcna/part3-cloud-native-architecture/module-3.10-green-computing.md) — Kepler, carbon-aware scheduling

### Knative Serverless

New module: [Knative](platform/toolkits/scaling-reliability/module-6.6-knative.md) — scale-to-zero workloads, Serving, Eventing, traffic splitting.

### CNI Deep Dives

4 new networking modules: [Flannel](platform/toolkits/networking/module-5.5-flannel.md), [Calico](platform/toolkits/networking/module-5.6-calico.md), [kube-router](platform/toolkits/networking/module-5.7-kube-router.md), [Multus](platform/toolkits/networking/module-5.8-multus.md).

### Linux Track Gaps Filled

4 new modules:
- [Package & User Management](linux/operations/module-8.1-storage-management.md) — apt/dnf, useradd/visudo
- [Scheduling & Backups](linux/operations/module-8.4-scheduling-backups.md) — cron, systemd timers, tar, rsync
- [Storage Management](linux/operations/module-8.1-storage-management.md) — LVM, RAID, NFS, swap
- [Network Administration](linux/operations/module-8.2-network-administration.md) — firewalld, bonding, chrony, SSH hardening

### 21 Certification Tracks

KubeDojo now covers every cloud-native certification on the Linux Foundation catalog:

| Tier | Certifications |
|------|---------------|
| **K8s Core** | [KCNA](k8s/kcna/index.md), [KCSA](k8s/kcsa/index.md), [CKA](k8s/cka/index.md), [CKAD](k8s/ckad/index.md), [CKS](k8s/cks/index.md) |
| **Specialist** | [CNPE](k8s/cnpe/index.md), [CNPA](k8s/cnpa/index.md) |
| **Tool-Specific** | [PCA](k8s/pca/index.md), [ICA](k8s/ica/index.md), [CCA](k8s/cca/index.md), [CBA](k8s/cba/index.md), [OTCA](k8s/otca/index.md), [KCA](k8s/kca/index.md), [CAPA](k8s/capa/index.md), [CGOA](k8s/cgoa/index.md) |
| **Other** | [LFCS](k8s/lfcs/index.md), [FinOps](k8s/finops/index.md) |

### Kubernetes 1.35 "Timbernetes" Support

KubeDojo is now fully aligned with **Kubernetes 1.35** (released December 2025):

- **Version bump**: All cluster setup, kubeadm, and upgrade examples updated from 1.31 to 1.35
- **cgroup v2 required**: Cluster setup module now covers the cgroup v2 requirement (v1 disabled by default)
- **containerd 2.0**: Updated container runtime guidance for containerd 2.0+
- **In-Place Pod Resize (GA)**: New section in Resource Management covering live CPU/memory adjustments
- **Gateway API is the standard**: Reframed from "future" to current recommended approach
- **Ingress-NGINX retirement**: Added migration guidance across CKA, CKAD, and CKS tracks
- **IPVS deprecation**: Updated networking modules to recommend nftables
- **WebSocket RBAC change**: Critical breaking change documented in RBAC module

### New Modules

#### Certification Tracks
| Module | Track | Description |
|--------|-------|-------------|
| [Autoscaling (HPA/VPA)](k8s/cka/part2-workloads-scheduling/module-2.9-autoscaling.md) | CKA | Horizontal and Vertical Pod Autoscaling with hands-on load testing |
| [etcd-operator v0.2.0](platform/toolkits/cloud-native-databases/module-15.5-etcd-operator.md) | Platform | Official etcd operator — TLS management, managed upgrades |
| [CNPE Learning Path](k8s/cnpe/index.md) | CNPE | Maps 60+ existing modules to the new CNPE certification domains |

#### Platform Engineering Toolkit — 15 New Modules
| Module | Category | Description |
|--------|----------|-------------|
| [**FinOps & OpenCost**](platform/toolkits/scaling-reliability/module-6.4-finops-opencost.md) | Scaling | K8s cost optimization, resource right-sizing, idle cleanup |
| [**Kyverno**](platform/toolkits/security-tools/module-4.7-kyverno.md) | Security | YAML-native policy engine — validate, mutate, generate |
| [**Chaos Engineering**](platform/toolkits/scaling-reliability/module-6.5-chaos-engineering.md) | Scaling | LitmusChaos + Chaos Mesh hands-on with GameDay planning |
| [**Building Operators**](platform/toolkits/platforms/module-3.4-kubebuilder.md) | Platforms | Kubebuilder from scratch — build a WebApp operator |
| [**Continuous Profiling**](platform/toolkits/observability/module-1.9-continuous-profiling.md) | Observability | Parca + Pyroscope — the 4th pillar of observability |
| [**SLO Tooling**](platform/toolkits/observability/module-1.10-slo-tooling.md) | Observability | Sloth + Pyrra — bridging SRE theory to practice |
| [**Cluster API**](platform/toolkits/platforms/module-3.5-cluster-api.md) | Platforms | Declarative K8s cluster lifecycle management (CAPI) |
| [**vCluster**](platform/toolkits/platforms/module-3.6-vcluster.md) | Platforms | Virtual K8s clusters for multi-tenancy at 1/10th the cost |
| [**Rook/Ceph**](platform/toolkits/storage/module-16.1-rook-ceph.md) | Storage | Distributed storage — block, filesystem, and object from one cluster |
| [**MinIO**](platform/toolkits/storage/module-16.2-minio.md) | Storage | S3-compatible object storage on K8s |
| [**Longhorn**](platform/toolkits/storage/module-16.3-longhorn.md) | Storage | Lightweight distributed block storage with backup/DR |
| [**GPU Scheduling**](platform/toolkits/ml-platforms/module-9.7-gpu-scheduling.md) | ML Platforms | NVIDIA GPU Operator, time-slicing, MIG, monitoring |
| [**DNS Deep Dive**](platform/toolkits/networking/module-5.3-dns-deep-dive.md) | Networking | CoreDNS customization, external-dns, ndots optimization |
| [**MetalLB**](platform/toolkits/networking/module-5.4-metallb.md) | Networking | Bare-metal load balancing — L2 and BGP modes |
| [**SPIFFE/SPIRE**](platform/toolkits/security-tools/module-4.8-spiffe-spire.md) | Security | Cryptographic workload identity for zero-trust networking |

### CKS Exam Alignment

Verified our CKS modules against the CNCF's October 2024 exam overhaul and filled identified gaps:
- Added **Cilium Pod-to-Pod encryption** (WireGuard/IPsec) to Network Policies module
- Added **KubeLinter** section to Static Analysis module
- Updated CKS prerequisite: CKA no longer needs to be active — just passed at any point

### Quality Review ("The KubeDojo Gauntlet")

Every module in KubeDojo was reviewed by **Gemini AI** as an adversary reviewer:

- **329 modules reviewed** across 4 phases
- **95%+ scored 9.5-10/10** on the "Dojo Scale" (Vibe Check, Junior-Proof, Live Test, Sticky Factor)
- **7 modules improved** with dramatic openings, fixing dry "academic" tone
- **1 stub expanded** from 43 lines to 788 lines (CKA Networking Data Path)
- Older Prerequisites modules upgraded to match the quality of newer Platform modules

### Claude-Gemini Collaboration

This update was produced through a novel **multi-AI collaboration**:
- **Claude** (Opus 4.6) handled implementation — writing modules, updating content, managing issues
- **Gemini** (3 Flash) served as adversary reviewer — catching technical errors, flagging dry content, suggesting improvements
- Communication via **ai_agent_bridge** — an SQLite-based message broker enabling structured review workflows
- Every issue was Gemini-reviewed before closing
- Gemini caught 2 technical inaccuracies (StatefulSet versioning, trafficDistribution values) that were fixed before merge

### By the Numbers

| Metric | Count |
|--------|-------|
| New modules | 18 |
| Modules updated | 30+ |
| Modules quality-reviewed | 329 |
| GitHub issues created & closed | 25 |
| Lines of new content | ~12,000 |
| Total curriculum modules | 329 |
| Tracks | 10 (CKA, CKAD, CKS, KCNA, KCSA, CNPE, Platform, Linux, IaC, Prerequisites) |

---

## December 2025 — Initial Release

KubeDojo launched with 311 modules covering all 5 Kubestronaut certifications plus Platform Engineering, Linux, and IaC deep dives. See the [full project history](https://github.com/kube-dojo/kube-dojo.github.io/commits/main) for details.
