# KubeDojo

**Free, comprehensive training for all 5 Kubernetes certifications.**

No paywalls. No upsells. Just quality education.

---

## Why This Exists

The Kubernetes certification industry charges $300-500+ for courses that often deliver shallow content, outdated material, and "exam dumps" that don't build real understanding.

KubeDojo is different:
- **Free forever** - No paid tiers, no premium content behind paywalls
- **Theory-first** - Understand *why*, not just *what to type*
- **Battle-tested** - Built by practitioners who use K8s daily and have taken these exams
- **Community-driven** - Contributions welcome, knowledge shared

If you can learn for free, you should be able to.

---

## The Kubestronaut Path

KubeDojo prepares you for all 5 core Kubernetes certifications required for [Kubestronaut](https://www.cncf.io/training/kubestronaut/) status:

| Cert | Name | Type | Status |
|------|------|------|--------|
| **CKA** | Certified Kubernetes Administrator | Hands-on lab | 🚧 In Progress |
| **CKAD** | Certified Kubernetes Application Developer | Hands-on lab | 📋 Planned |
| **CKS** | Certified Kubernetes Security Specialist | Hands-on lab | 📋 Planned |
| **KCNA** | Kubernetes & Cloud Native Associate | Multiple choice | 📋 Planned |
| **KCSA** | Kubernetes & Cloud Native Security Associate | Multiple choice | 📋 Planned |

---

## CKA Curriculum (2025)

> **Curriculum Version**: CKA 2025 (effective Feb 18, 2025)
>
> Based on [CNCF Official Curriculum](https://github.com/cncf/curriculum)

The CKA is notoriously difficult after recent changes. 16 hands-on questions in 2 hours. Speed matters as much as knowledge.

### 2025 Changes Summary

| Added | Removed/Deprioritized |
|-------|----------------------|
| Helm | etcd backup/restore |
| Kustomize | Cluster upgrades |
| Gateway API | Infrastructure provisioning |
| CRDs & Operators | |
| Pod Security Admission | |

### Part 0: Environment & Exam Technique ✅
| Module | Topic | Status |
|--------|-------|--------|
| 0.1 | [Cluster Setup](docs/cka/part0-environment/module-0.1-cluster-setup.md) | ✅ |
| 0.2 | [Shell Mastery](docs/cka/part0-environment/module-0.2-shell-mastery.md) | ✅ |
| 0.3 | [Vim for YAML](docs/cka/part0-environment/module-0.3-vim-yaml.md) | ✅ |
| 0.4 | [kubernetes.io Navigation](docs/cka/part0-environment/module-0.4-k8s-docs.md) | ✅ |
| 0.5 | [Exam Strategy - Three-Pass Method](docs/cka/part0-environment/module-0.5-exam-strategy.md) | ✅ |

### Part 1: Cluster Architecture, Installation & Configuration (25%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 1.1 | [Control Plane Deep-Dive](docs/cka/part1-cluster-architecture/module-1.1-control-plane.md) | ✅ |
| 1.2 | [Extension Interfaces (CNI, CSI, CRI)](docs/cka/part1-cluster-architecture/module-1.2-extension-interfaces.md) | ✅ |
| 1.3 | [Helm](docs/cka/part1-cluster-architecture/module-1.3-helm.md) | ✅ |
| 1.4 | [Kustomize](docs/cka/part1-cluster-architecture/module-1.4-kustomize.md) | ✅ |
| 1.5 | [CRDs & Operators](docs/cka/part1-cluster-architecture/module-1.5-crds-operators.md) | ✅ |
| 1.6 | [RBAC](docs/cka/part1-cluster-architecture/module-1.6-rbac.md) | ✅ |
| 1.7 | [kubeadm Basics](docs/cka/part1-cluster-architecture/module-1.7-kubeadm.md) | ✅ |

### Part 2: Workloads & Scheduling (15%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 2.1 | [Pods Deep-Dive](docs/cka/part2-workloads-scheduling/module-2.1-pods.md) | ✅ |
| 2.2 | [Deployments & ReplicaSets](docs/cka/part2-workloads-scheduling/module-2.2-deployments.md) | ✅ |
| 2.3 | [DaemonSets & StatefulSets](docs/cka/part2-workloads-scheduling/module-2.3-daemonsets-statefulsets.md) | ✅ |
| 2.4 | [Jobs & CronJobs](docs/cka/part2-workloads-scheduling/module-2.4-jobs-cronjobs.md) | ✅ |
| 2.5 | [Resource Management](docs/cka/part2-workloads-scheduling/module-2.5-resource-management.md) | ✅ |
| 2.6 | [Scheduling](docs/cka/part2-workloads-scheduling/module-2.6-scheduling.md) | ✅ |
| 2.7 | [ConfigMaps & Secrets](docs/cka/part2-workloads-scheduling/module-2.7-configmaps-secrets.md) | ✅ |

### Part 3: Services & Networking (20%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 3.1 | [Services](docs/cka/part3-services-networking/module-3.1-services.md) | ✅ |
| 3.2 | [Endpoints & EndpointSlices](docs/cka/part3-services-networking/module-3.2-endpoints.md) | ✅ |
| 3.3 | [DNS & CoreDNS](docs/cka/part3-services-networking/module-3.3-dns.md) | ✅ |
| 3.4 | [Ingress](docs/cka/part3-services-networking/module-3.4-ingress.md) | ✅ |
| 3.5 | [Gateway API](docs/cka/part3-services-networking/module-3.5-gateway-api.md) | ✅ |
| 3.6 | [Network Policies](docs/cka/part3-services-networking/module-3.6-network-policies.md) | ✅ |
| 3.7 | [CNI & Cluster Networking](docs/cka/part3-services-networking/module-3.7-cni.md) | ✅ |

### Part 4: Storage (10%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 4.1 | [Volumes](docs/cka/part4-storage/module-4.1-volumes.md) | ✅ |
| 4.2 | [PersistentVolumes & PersistentVolumeClaims](docs/cka/part4-storage/module-4.2-pv-pvc.md) | ✅ |
| 4.3 | [StorageClasses & Dynamic Provisioning](docs/cka/part4-storage/module-4.3-storageclasses.md) | ✅ |
| 4.4 | [Volume Snapshots & Cloning](docs/cka/part4-storage/module-4.4-snapshots.md) | ✅ |
| 4.5 | [Storage Troubleshooting](docs/cka/part4-storage/module-4.5-troubleshooting.md) | ✅ |

### Part 5: Troubleshooting (30%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 5.1 | [Troubleshooting Methodology](docs/cka/part5-troubleshooting/module-5.1-methodology.md) | ✅ |
| 5.2 | [Application Failures](docs/cka/part5-troubleshooting/module-5.2-application-failures.md) | ✅ |
| 5.3 | [Control Plane Failures](docs/cka/part5-troubleshooting/module-5.3-control-plane.md) | ✅ |
| 5.4 | [Worker Node Failures](docs/cka/part5-troubleshooting/module-5.4-worker-nodes.md) | ✅ |
| 5.5 | [Network Troubleshooting](docs/cka/part5-troubleshooting/module-5.5-networking.md) | ✅ |
| 5.6 | [Service Troubleshooting](docs/cka/part5-troubleshooting/module-5.6-services.md) | ✅ |
| 5.7 | [Logging & Monitoring](docs/cka/part5-troubleshooting/module-5.7-logging-monitoring.md) | ✅ |

### Part 6: Speed Drills & Mock Exams
| Module | Topic | Status |
|--------|-------|--------|
| 6.1 | Kubectl Imperative Speedruns | 📋 |
| 6.2 | YAML Generation Patterns | 📋 |
| 6.3 | Helm Speed Drills | 📋 |
| 6.4 | Task Complexity Recognition | 📋 |
| 6.5 | Three-Pass Strategy Practice | 📋 |
| 6.6 | Mock Exam #1 | 📋 |
| 6.7 | Mock Exam #2 | 📋 |
| 6.8 | Mock Exam #3 | 📋 |

---

## Philosophy

### Theory Before Hands-On
You can't troubleshoot what you don't understand. Every module starts with *why* before *how*.

### Speed Is a Skill
Knowing Kubernetes isn't enough. The CKA gives you ~7 minutes per question. We train speed explicitly.

### "Good Enough" Mindset
Perfectionists fail timed exams. We teach when to move on, when 80% is better than 0%.

### No Memorization
Kubernetes docs are available during the exam. We teach you to navigate them fast, not memorize YAML.

### Skills Over Simulation
We teach skills and strategy. For realistic exam simulation, use [killer.sh](https://killer.sh) (included with exam purchase).

---

## Quality Standards

Every module includes:
- **Clear explanations** - No handwaving, explain the "why"
- **Analogies** - Complex concepts made memorable
- **War stories** - Real incidents that illustrate consequences
- **Gotchas** - Common mistakes and how to avoid them
- **"Did You Know?"** - Interesting facts that reinforce learning
- **Hands-on exercises** - Practice with clear deliverables
- **Speed tips** - Exam-specific shortcuts
- **Quiz questions** - Test your understanding

---

## Getting Started

1. Clone this repo
2. Start with [Module 0.1: Cluster Setup](docs/cka/part0-environment/module-0.1-cluster-setup.md)
3. Work through modules in order
4. Track your progress

```bash
git clone https://github.com/krisztiankoos/kubedojo.git
cd kubedojo
```

---

## Curriculum Sources

We track official CNCF curriculum and update when changes occur:

- [CNCF Curriculum Repository](https://github.com/cncf/curriculum)
- [CKA Program Changes](https://training.linuxfoundation.org/certified-kubernetes-administrator-cka-program-changes/)
- [CKS Program Changes](https://training.linuxfoundation.org/cks-program-changes/)

See [Issue #14](https://github.com/krisztiankoos/kubedojo/issues/14) for monitoring and change tracking.

---

## Contributing

This is a community project. Contributions welcome:
- Fix errors or typos
- Add war stories from your experience
- Improve explanations
- Suggest better analogies
- Report issues

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License. Free to use, share, and modify.

---

*"In the dojo, everyone starts as a white belt. What matters is showing up to train."*
