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

### Part 0: Environment & Exam Technique
| Module | Topic | Status |
|--------|-------|--------|
| 0.1 | [Cluster Setup](docs/cka/part0-environment/module-0.1-cluster-setup.md) | 📋 |
| 0.2 | Shell Mastery (aliases, autocomplete) | 📋 |
| 0.3 | Vim for YAML | 📋 |
| 0.4 | kubernetes.io Navigation | 📋 |
| 0.5 | Exam Strategy & Time Management | 📋 |

### Part 1: Cluster Architecture, Installation & Configuration (25%)
| Module | Topic | Status |
|--------|-------|--------|
| 1.1 | Control Plane Deep-Dive | 📋 |
| 1.2 | Extension Interfaces (CNI, CSI, CRI) | 📋 |
| 1.3 | Helm | 📋 |
| 1.4 | Kustomize | 📋 |
| 1.5 | CRDs & Operators | 📋 |
| 1.6 | RBAC | 📋 |
| 1.7 | kubeadm Basics | 📋 |

### Part 2: Workloads & Scheduling (15%)
| Module | Topic | Status |
|--------|-------|--------|
| 2.1 | Pods (What Actually Happens) | 📋 |
| 2.2 | Deployments, ReplicaSets, DaemonSets | 📋 |
| 2.3 | Jobs & CronJobs | 📋 |
| 2.4 | Scheduling (Affinity, Taints, Tolerations) | 📋 |
| 2.5 | Resource Requests & Limits | 📋 |
| 2.6 | Pod Admission & Security Contexts | 📋 |
| 2.7 | Workload Autoscaling (HPA) | 📋 |

### Part 3: Services & Networking (20%)
| Module | Topic | Status |
|--------|-------|--------|
| 3.1 | Container Networking Fundamentals | 📋 |
| 3.2 | CNI | 📋 |
| 3.3 | Services (ClusterIP, NodePort, LoadBalancer) | 📋 |
| 3.4 | DNS in Kubernetes (CoreDNS) | 📋 |
| 3.5 | Gateway API | 📋 |
| 3.6 | Ingress (Legacy) | 📋 |
| 3.7 | NetworkPolicies | 📋 |

### Part 4: Storage (10%)
| Module | Topic | Status |
|--------|-------|--------|
| 4.1 | Volumes (emptyDir, hostPath) | 📋 |
| 4.2 | PersistentVolumes & PersistentVolumeClaims | 📋 |
| 4.3 | StorageClasses & Dynamic Provisioning | 📋 |
| 4.4 | Volume Types, Access Modes & Reclaim Policies | 📋 |
| 4.5 | CSI Basics | 📋 |

### Part 5: Troubleshooting (30%)
| Module | Topic | Status |
|--------|-------|--------|
| 5.1 | Troubleshooting Methodology | 📋 |
| 5.2 | Application Failures | 📋 |
| 5.3 | Control Plane Failures | 📋 |
| 5.4 | Worker Node Failures | 📋 |
| 5.5 | Network Troubleshooting (Internal & External) | 📋 |
| 5.6 | Service Troubleshooting | 📋 |
| 5.7 | Logging & Monitoring | 📋 |

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
