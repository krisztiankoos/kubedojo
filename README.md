# KubeDojo

**Free, comprehensive training for Kubernetes certifications and platform engineering.**

No paywalls. No upsells. Just quality education.

---

## 🇺🇦 Присвята

*Цей проєкт присвячується українським ІТ-інженерам, які віддали своє життя, захищаючи Батьківщину.*

*Вони були розробниками, DevOps-інженерами, системними адміністраторами. Вони будували системи, писали код, підтримували інфраструктуру. Коли прийшла війна, вони залишили клавіатури й взяли зброю. Вони стали воїнами.*

*Їхній код живе. Їхня жертва — вічна. Слава Україні.*

---

### Заповіт

*Тарас Шевченко, 1845*

> Як умру, то поховайте
> Мене на могилі,
> Серед степу широкого,
> На Вкраїні милій,
> Щоб лани широкополі,
> І Дніпро, і кручі
> Було видно, було чути,
> Як реве ревучий.
>
> Як понесе з України
> У синєє море
> Кров ворожу... отойді я
> І лани і гори —
> Все покину і полину
> До самого Бога
> Молитися... а до того
> Я не знаю Бога.
>
> Поховайте та вставайте,
> Кайдани порвіте
> І вражою злою кров'ю
> Волю окропіте.
> І мене в сем'ї великій,
> В сем'ї вольній, новій,
> Не забудьте пом'янути
> Незлим тихим словом.

---

## Learning Paths

```
┌─────────────────────────────────────────────────────────────────┐
│                         KUBEDOJO                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BEGINNER                                                       │
│  └── prerequisites/                                             │
│      ├── Philosophy & Design      "Why Kubernetes?"             │
│      ├── Cloud Native 101         "Containers & ecosystem"      │
│      ├── Kubernetes Basics        "Hands-on fundamentals"       │
│      └── Modern DevOps            "IaC, GitOps, CI/CD intro"    │
│                         │                                       │
│                         ▼                                       │
│  CERTIFICATION PATH (Kubestronaut)                              │
│  └── k8s/                                                       │
│      ├── KCNA  ─────► Entry-level (multiple choice)            │
│      ├── CKAD  ─────► Developer (hands-on lab)                 │
│      ├── CKA   ─────► Administrator (hands-on lab)             │
│      ├── KCSA  ─────► Security Associate (multiple choice)     │
│      └── CKS   ─────► Security Specialist (hands-on lab)       │
│                         │                                       │
│                         ▼                                       │
│  PRACTITIONER PATH (Beyond Certifications)                      │
│  └── platform/                                                  │
│      ├── foundations/    "Theory that doesn't change"           │
│      │   ├── Systems Thinking                                   │
│      │   ├── Reliability Engineering                            │
│      │   ├── Observability Theory                               │
│      │   ├── Security Principles                                │
│      │   └── Distributed Systems                                │
│      │                                                          │
│      ├── disciplines/    "Applied practices"                    │
│      │   ├── SRE                                                │
│      │   ├── Platform Engineering                               │
│      │   ├── GitOps                                             │
│      │   ├── DevSecOps                                          │
│      │   └── MLOps                                              │
│      │                                                          │
│      └── toolkits/       "Current tools (evolving)"             │
│          ├── Observability    (Prometheus, OTel, Grafana)       │
│          ├── GitOps Tools     (ArgoCD, Flux)                    │
│          ├── Security Tools   (Vault, OPA, Falco)               │
│          ├── Platforms        (Backstage, Crossplane)           │
│          └── ML Platforms     (Kubeflow, MLflow)                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

| Path | Audience | Modules | Status |
|------|----------|---------|--------|
| **Prerequisites** | Beginners | 23 | ✅ Complete |
| **Kubernetes Certifications** | Cert seekers | 142 | ✅ Complete |
| **Platform Engineering** | Practitioners | ~75 | 🚧 Planned |

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

| Cert | Name | Type | Modules | Status |
|------|------|------|---------|--------|
| **CKA** | Certified Kubernetes Administrator | Hands-on lab | 38 | ✅ Complete |
| **CKAD** | Certified Kubernetes Application Developer | Hands-on lab | 28 | ✅ Complete |
| **CKS** | Certified Kubernetes Security Specialist | Hands-on lab | 30 | ✅ Complete |
| **KCNA** | Kubernetes & Cloud Native Associate | Multiple choice | 21 | ✅ Complete |
| **KCSA** | Kubernetes & Cloud Native Security Associate | Multiple choice | 25 | ✅ Complete |
| | **Prerequisites** | Foundation | 23 | ✅ Complete |
| | **Total** | | **165** | |

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
| 0.1 | [Cluster Setup](docs/k8s/cka/part0-environment/module-0.1-cluster-setup.md) | ✅ |
| 0.2 | [Shell Mastery](docs/k8s/cka/part0-environment/module-0.2-shell-mastery.md) | ✅ |
| 0.3 | [Vim for YAML](docs/k8s/cka/part0-environment/module-0.3-vim-yaml.md) | ✅ |
| 0.4 | [kubernetes.io Navigation](docs/k8s/cka/part0-environment/module-0.4-k8s-docs.md) | ✅ |
| 0.5 | [Exam Strategy - Three-Pass Method](docs/k8s/cka/part0-environment/module-0.5-exam-strategy.md) | ✅ |

### Part 1: Cluster Architecture, Installation & Configuration (25%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 1.1 | [Control Plane Deep-Dive](docs/k8s/cka/part1-cluster-architecture/module-1.1-control-plane.md) | ✅ |
| 1.2 | [Extension Interfaces (CNI, CSI, CRI)](docs/k8s/cka/part1-cluster-architecture/module-1.2-extension-interfaces.md) | ✅ |
| 1.3 | [Helm](docs/k8s/cka/part1-cluster-architecture/module-1.3-helm.md) | ✅ |
| 1.4 | [Kustomize](docs/k8s/cka/part1-cluster-architecture/module-1.4-kustomize.md) | ✅ |
| 1.5 | [CRDs & Operators](docs/k8s/cka/part1-cluster-architecture/module-1.5-crds-operators.md) | ✅ |
| 1.6 | [RBAC](docs/k8s/cka/part1-cluster-architecture/module-1.6-rbac.md) | ✅ |
| 1.7 | [kubeadm Basics](docs/k8s/cka/part1-cluster-architecture/module-1.7-kubeadm.md) | ✅ |

### Part 2: Workloads & Scheduling (15%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 2.1 | [Pods Deep-Dive](docs/k8s/cka/part2-workloads-scheduling/module-2.1-pods.md) | ✅ |
| 2.2 | [Deployments & ReplicaSets](docs/k8s/cka/part2-workloads-scheduling/module-2.2-deployments.md) | ✅ |
| 2.3 | [DaemonSets & StatefulSets](docs/k8s/cka/part2-workloads-scheduling/module-2.3-daemonsets-statefulsets.md) | ✅ |
| 2.4 | [Jobs & CronJobs](docs/k8s/cka/part2-workloads-scheduling/module-2.4-jobs-cronjobs.md) | ✅ |
| 2.5 | [Resource Management](docs/k8s/cka/part2-workloads-scheduling/module-2.5-resource-management.md) | ✅ |
| 2.6 | [Scheduling](docs/k8s/cka/part2-workloads-scheduling/module-2.6-scheduling.md) | ✅ |
| 2.7 | [ConfigMaps & Secrets](docs/k8s/cka/part2-workloads-scheduling/module-2.7-configmaps-secrets.md) | ✅ |

### Part 3: Services & Networking (20%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 3.1 | [Services](docs/k8s/cka/part3-services-networking/module-3.1-services.md) | ✅ |
| 3.2 | [Endpoints & EndpointSlices](docs/k8s/cka/part3-services-networking/module-3.2-endpoints.md) | ✅ |
| 3.3 | [DNS & CoreDNS](docs/k8s/cka/part3-services-networking/module-3.3-dns.md) | ✅ |
| 3.4 | [Ingress](docs/k8s/cka/part3-services-networking/module-3.4-ingress.md) | ✅ |
| 3.5 | [Gateway API](docs/k8s/cka/part3-services-networking/module-3.5-gateway-api.md) | ✅ |
| 3.6 | [Network Policies](docs/k8s/cka/part3-services-networking/module-3.6-network-policies.md) | ✅ |
| 3.7 | [CNI & Cluster Networking](docs/k8s/cka/part3-services-networking/module-3.7-cni.md) | ✅ |

### Part 4: Storage (10%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 4.1 | [Volumes](docs/k8s/cka/part4-storage/module-4.1-volumes.md) | ✅ |
| 4.2 | [PersistentVolumes & PersistentVolumeClaims](docs/k8s/cka/part4-storage/module-4.2-pv-pvc.md) | ✅ |
| 4.3 | [StorageClasses & Dynamic Provisioning](docs/k8s/cka/part4-storage/module-4.3-storageclasses.md) | ✅ |
| 4.4 | [Volume Snapshots & Cloning](docs/k8s/cka/part4-storage/module-4.4-snapshots.md) | ✅ |
| 4.5 | [Storage Troubleshooting](docs/k8s/cka/part4-storage/module-4.5-troubleshooting.md) | ✅ |

### Part 5: Troubleshooting (30%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 5.1 | [Troubleshooting Methodology](docs/k8s/cka/part5-troubleshooting/module-5.1-methodology.md) | ✅ |
| 5.2 | [Application Failures](docs/k8s/cka/part5-troubleshooting/module-5.2-application-failures.md) | ✅ |
| 5.3 | [Control Plane Failures](docs/k8s/cka/part5-troubleshooting/module-5.3-control-plane.md) | ✅ |
| 5.4 | [Worker Node Failures](docs/k8s/cka/part5-troubleshooting/module-5.4-worker-nodes.md) | ✅ |
| 5.5 | [Network Troubleshooting](docs/k8s/cka/part5-troubleshooting/module-5.5-networking.md) | ✅ |
| 5.6 | [Service Troubleshooting](docs/k8s/cka/part5-troubleshooting/module-5.6-services.md) | ✅ |
| 5.7 | [Logging & Monitoring](docs/k8s/cka/part5-troubleshooting/module-5.7-logging-monitoring.md) | ✅ |

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

## CKAD Curriculum (2025) ✅

> **Curriculum Version**: CKAD 2025
>
> Based on [CNCF Official Curriculum](https://github.com/cncf/curriculum)

The CKAD tests your ability to design, build, and deploy cloud-native applications on Kubernetes.

### Part 0: Environment & Exam Technique ✅
| Module | Topic | Status |
|--------|-------|--------|
| 0.1 | [Cluster Setup](docs/k8s/ckad/part0-environment/module-0.1-cluster-setup.md) | ✅ |
| 0.2 | [Shell Mastery](docs/k8s/ckad/part0-environment/module-0.2-shell-mastery.md) | ✅ |
| 0.3 | [Vim for YAML](docs/k8s/ckad/part0-environment/module-0.3-vim-yaml.md) | ✅ |
| 0.4 | [kubernetes.io Navigation](docs/k8s/ckad/part0-environment/module-0.4-k8s-docs.md) | ✅ |
| 0.5 | [Exam Strategy](docs/k8s/ckad/part0-environment/module-0.5-exam-strategy.md) | ✅ |

### Part 1: Application Design and Build (20%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 1.1 | [Pods Deep-Dive](docs/k8s/ckad/part1-app-design/module-1.1-pods.md) | ✅ |
| 1.2 | [Jobs & CronJobs](docs/k8s/ckad/part1-app-design/module-1.2-jobs.md) | ✅ |
| 1.3 | [Multi-Container Patterns](docs/k8s/ckad/part1-app-design/module-1.3-multi-container.md) | ✅ |
| 1.4 | [Init Containers](docs/k8s/ckad/part1-app-design/module-1.4-init-containers.md) | ✅ |
| 1.5 | [Volumes & Storage](docs/k8s/ckad/part1-app-design/module-1.5-volumes.md) | ✅ |

### Part 2: Application Deployment (20%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 2.1 | [Deployments](docs/k8s/ckad/part2-deployment/module-2.1-deployments.md) | ✅ |
| 2.2 | [Rolling Updates & Rollbacks](docs/k8s/ckad/part2-deployment/module-2.2-rolling-updates.md) | ✅ |
| 2.3 | [Helm Package Manager](docs/k8s/ckad/part2-deployment/module-2.3-helm.md) | ✅ |
| 2.4 | [Kustomize](docs/k8s/ckad/part2-deployment/module-2.4-kustomize.md) | ✅ |

### Part 3: Application Observability (15%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 3.1 | [Probes (Liveness, Readiness, Startup)](docs/k8s/ckad/part3-observability/module-3.1-probes.md) | ✅ |
| 3.2 | [Container Logging](docs/k8s/ckad/part3-observability/module-3.2-logging.md) | ✅ |
| 3.3 | [Debugging Pods](docs/k8s/ckad/part3-observability/module-3.3-debugging.md) | ✅ |
| 3.4 | [Resource Monitoring](docs/k8s/ckad/part3-observability/module-3.4-monitoring.md) | ✅ |
| 3.5 | [Application Troubleshooting](docs/k8s/ckad/part3-observability/module-3.5-troubleshooting.md) | ✅ |

### Part 4: Application Environment, Configuration and Security (25%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 4.1 | [ConfigMaps](docs/k8s/ckad/part4-environment/module-4.1-configmaps.md) | ✅ |
| 4.2 | [Secrets](docs/k8s/ckad/part4-environment/module-4.2-secrets.md) | ✅ |
| 4.3 | [Resource Requirements](docs/k8s/ckad/part4-environment/module-4.3-resources.md) | ✅ |
| 4.4 | [SecurityContexts](docs/k8s/ckad/part4-environment/module-4.4-securitycontext.md) | ✅ |
| 4.5 | [ServiceAccounts](docs/k8s/ckad/part4-environment/module-4.5-serviceaccounts.md) | ✅ |
| 4.6 | [Custom Resource Definitions](docs/k8s/ckad/part4-environment/module-4.6-crds.md) | ✅ |

### Part 5: Services and Networking (20%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 5.1 | [Services](docs/k8s/ckad/part5-networking/module-5.1-services.md) | ✅ |
| 5.2 | [Ingress](docs/k8s/ckad/part5-networking/module-5.2-ingress.md) | ✅ |
| 5.3 | [NetworkPolicies](docs/k8s/ckad/part5-networking/module-5.3-networkpolicies.md) | ✅ |

---

## CKS Curriculum (2025) ✅

> **Curriculum Version**: CKS 2025
>
> Based on [CNCF Official Curriculum](https://github.com/cncf/curriculum)
>
> **Prerequisite**: Active CKA certification required

The CKS tests your ability to secure Kubernetes clusters, from infrastructure to runtime.

### Part 0: Environment & Exam Strategy ✅
| Module | Topic | Status |
|--------|-------|--------|
| 0.1 | [CKS Overview](docs/k8s/cks/part0-environment/module-0.1-cks-overview.md) | ✅ |
| 0.2 | [Security Lab Setup](docs/k8s/cks/part0-environment/module-0.2-security-lab.md) | ✅ |
| 0.3 | [Security Tools](docs/k8s/cks/part0-environment/module-0.3-security-tools.md) | ✅ |
| 0.4 | [Exam Strategy](docs/k8s/cks/part0-environment/module-0.4-exam-strategy.md) | ✅ |

### Part 1: Cluster Setup (10%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 1.1 | [Network Policies](docs/k8s/cks/part1-cluster-setup/module-1.1-network-policies.md) | ✅ |
| 1.2 | [CIS Benchmarks](docs/k8s/cks/part1-cluster-setup/module-1.2-cis-benchmarks.md) | ✅ |
| 1.3 | [Ingress Security](docs/k8s/cks/part1-cluster-setup/module-1.3-ingress-security.md) | ✅ |
| 1.4 | [Node Metadata Protection](docs/k8s/cks/part1-cluster-setup/module-1.4-node-metadata.md) | ✅ |
| 1.5 | [GUI Security](docs/k8s/cks/part1-cluster-setup/module-1.5-gui-security.md) | ✅ |

### Part 2: Cluster Hardening (15%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 2.1 | [RBAC Deep-Dive](docs/k8s/cks/part2-cluster-hardening/module-2.1-rbac-deep-dive.md) | ✅ |
| 2.2 | [ServiceAccount Security](docs/k8s/cks/part2-cluster-hardening/module-2.2-serviceaccount-security.md) | ✅ |
| 2.3 | [API Server Security](docs/k8s/cks/part2-cluster-hardening/module-2.3-api-server-security.md) | ✅ |
| 2.4 | [Kubernetes Upgrades](docs/k8s/cks/part2-cluster-hardening/module-2.4-kubernetes-upgrades.md) | ✅ |
| 2.5 | [Restricting API Access](docs/k8s/cks/part2-cluster-hardening/module-2.5-restricting-api-access.md) | ✅ |

### Part 3: System Hardening (15%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 3.1 | [AppArmor](docs/k8s/cks/part3-system-hardening/module-3.1-apparmor.md) | ✅ |
| 3.2 | [Seccomp](docs/k8s/cks/part3-system-hardening/module-3.2-seccomp.md) | ✅ |
| 3.3 | [Kernel Hardening](docs/k8s/cks/part3-system-hardening/module-3.3-kernel-hardening.md) | ✅ |
| 3.4 | [Network Security](docs/k8s/cks/part3-system-hardening/module-3.4-network-security.md) | ✅ |

### Part 4: Minimize Microservice Vulnerabilities (20%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 4.1 | [Security Contexts](docs/k8s/cks/part4-microservice-vulnerabilities/module-4.1-security-contexts.md) | ✅ |
| 4.2 | [Pod Security Admission](docs/k8s/cks/part4-microservice-vulnerabilities/module-4.2-pod-security-admission.md) | ✅ |
| 4.3 | [Secrets Management](docs/k8s/cks/part4-microservice-vulnerabilities/module-4.3-secrets-management.md) | ✅ |
| 4.4 | [Runtime Sandboxing](docs/k8s/cks/part4-microservice-vulnerabilities/module-4.4-runtime-sandboxing.md) | ✅ |

### Part 5: Supply Chain Security (20%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 5.1 | [Image Security](docs/k8s/cks/part5-supply-chain-security/module-5.1-image-security.md) | ✅ |
| 5.2 | [Image Scanning](docs/k8s/cks/part5-supply-chain-security/module-5.2-image-scanning.md) | ✅ |
| 5.3 | [Static Analysis](docs/k8s/cks/part5-supply-chain-security/module-5.3-static-analysis.md) | ✅ |
| 5.4 | [Admission Controllers](docs/k8s/cks/part5-supply-chain-security/module-5.4-admission-controllers.md) | ✅ |

### Part 6: Monitoring, Logging and Runtime Security (20%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 6.1 | [Audit Logging](docs/k8s/cks/part6-runtime-security/module-6.1-audit-logging.md) | ✅ |
| 6.2 | [Falco](docs/k8s/cks/part6-runtime-security/module-6.2-falco.md) | ✅ |
| 6.3 | [Container Investigation](docs/k8s/cks/part6-runtime-security/module-6.3-container-investigation.md) | ✅ |
| 6.4 | [Immutable Infrastructure](docs/k8s/cks/part6-runtime-security/module-6.4-immutable-infrastructure.md) | ✅ |

---

## KCNA Curriculum ✅

> **Kubernetes and Cloud Native Associate** - Entry-level certification
>
> **Format**: Multiple choice (not hands-on), 90 minutes, ~60 questions, 75% to pass

The KCNA tests conceptual understanding of Kubernetes and cloud native technologies.

### Part 0: Introduction ✅
| Module | Topic | Status |
|--------|-------|--------|
| 0.1 | [KCNA Overview](docs/k8s/kcna/part0-introduction/module-0.1-kcna-overview.md) | ✅ |
| 0.2 | [Study Strategy](docs/k8s/kcna/part0-introduction/module-0.2-study-strategy.md) | ✅ |

### Part 1: Kubernetes Fundamentals (46%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 1.1 | [What is Kubernetes](docs/k8s/kcna/part1-kubernetes-fundamentals/module-1.1-what-is-kubernetes.md) | ✅ |
| 1.2 | [Container Fundamentals](docs/k8s/kcna/part1-kubernetes-fundamentals/module-1.2-container-fundamentals.md) | ✅ |
| 1.3 | [Control Plane](docs/k8s/kcna/part1-kubernetes-fundamentals/module-1.3-control-plane.md) | ✅ |
| 1.4 | [Node Components](docs/k8s/kcna/part1-kubernetes-fundamentals/module-1.4-node-components.md) | ✅ |
| 1.5 | [Pods](docs/k8s/kcna/part1-kubernetes-fundamentals/module-1.5-pods.md) | ✅ |
| 1.6 | [Workload Resources](docs/k8s/kcna/part1-kubernetes-fundamentals/module-1.6-workload-resources.md) | ✅ |
| 1.7 | [Services](docs/k8s/kcna/part1-kubernetes-fundamentals/module-1.7-services.md) | ✅ |
| 1.8 | [Namespaces & Labels](docs/k8s/kcna/part1-kubernetes-fundamentals/module-1.8-namespaces-labels.md) | ✅ |

### Part 2: Container Orchestration (22%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 2.1 | [Scheduling](docs/k8s/kcna/part2-container-orchestration/module-2.1-scheduling.md) | ✅ |
| 2.2 | [Scaling](docs/k8s/kcna/part2-container-orchestration/module-2.2-scaling.md) | ✅ |
| 2.3 | [Storage](docs/k8s/kcna/part2-container-orchestration/module-2.3-storage.md) | ✅ |
| 2.4 | [Configuration](docs/k8s/kcna/part2-container-orchestration/module-2.4-configuration.md) | ✅ |

### Part 3: Cloud Native Architecture (16%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 3.1 | [Cloud Native Principles](docs/k8s/kcna/part3-cloud-native-architecture/module-3.1-cloud-native-principles.md) | ✅ |
| 3.2 | [CNCF Ecosystem](docs/k8s/kcna/part3-cloud-native-architecture/module-3.2-cncf-ecosystem.md) | ✅ |
| 3.3 | [Cloud Native Patterns](docs/k8s/kcna/part3-cloud-native-architecture/module-3.3-patterns.md) | ✅ |

### Part 4: Cloud Native Observability (8%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 4.1 | [Observability Fundamentals](docs/k8s/kcna/part4-cloud-native-observability/module-4.1-observability-fundamentals.md) | ✅ |
| 4.2 | [Observability Tools](docs/k8s/kcna/part4-cloud-native-observability/module-4.2-observability-tools.md) | ✅ |

### Part 5: Application Delivery (8%) ✅
| Module | Topic | Status |
|--------|-------|--------|
| 5.1 | [CI/CD Fundamentals](docs/k8s/kcna/part5-application-delivery/module-5.1-ci-cd.md) | ✅ |
| 5.2 | [Application Packaging](docs/k8s/kcna/part5-application-delivery/module-5.2-application-packaging.md) | ✅ |

---

## Prerequisite Tracks ✅

Before diving into certification-specific content, these foundational tracks build the knowledge and context you need.

### Philosophy & Design ✅
| Module | Topic | Status |
|--------|-------|--------|
| 1 | [Why Kubernetes Won](docs/prerequisites/philosophy-design/module-1-why-kubernetes-won.md) | ✅ |
| 2 | [Declarative vs Imperative](docs/prerequisites/philosophy-design/module-2-declarative-vs-imperative.md) | ✅ |
| 3 | [What We Don't Cover](docs/prerequisites/philosophy-design/module-3-what-we-dont-cover.md) | ✅ |
| 4 | [Dead Ends - Technologies to Avoid](docs/prerequisites/philosophy-design/module-4-dead-ends.md) | ✅ |

### Cloud Native 101 ✅
| Module | Topic | Status |
|--------|-------|--------|
| 1 | [What Are Containers?](docs/prerequisites/cloud-native-101/module-1-what-are-containers.md) | ✅ |
| 2 | [Docker Fundamentals](docs/prerequisites/cloud-native-101/module-2-docker-fundamentals.md) | ✅ |
| 3 | [What is Kubernetes?](docs/prerequisites/cloud-native-101/module-3-what-is-kubernetes.md) | ✅ |
| 4 | [Cloud Native Ecosystem](docs/prerequisites/cloud-native-101/module-4-cloud-native-ecosystem.md) | ✅ |
| 5 | [Monolith to Microservices](docs/prerequisites/cloud-native-101/module-5-monolith-to-microservices.md) | ✅ |

### Kubernetes Basics ✅
| Module | Topic | Status |
|--------|-------|--------|
| 1 | [Your First Cluster](docs/prerequisites/kubernetes-basics/module-1-first-cluster.md) | ✅ |
| 2 | [kubectl Basics](docs/prerequisites/kubernetes-basics/module-2-kubectl-basics.md) | ✅ |
| 3 | [Pods - The Atomic Unit](docs/prerequisites/kubernetes-basics/module-3-pods.md) | ✅ |
| 4 | [Deployments - Managing Apps](docs/prerequisites/kubernetes-basics/module-4-deployments.md) | ✅ |
| 5 | [Services - Stable Networking](docs/prerequisites/kubernetes-basics/module-5-services.md) | ✅ |
| 6 | [ConfigMaps & Secrets](docs/prerequisites/kubernetes-basics/module-6-configmaps-secrets.md) | ✅ |
| 7 | [Namespaces & Labels](docs/prerequisites/kubernetes-basics/module-7-namespaces-labels.md) | ✅ |
| 8 | [YAML for Kubernetes](docs/prerequisites/kubernetes-basics/module-8-yaml-kubernetes.md) | ✅ |

### Modern DevOps Practices ✅
| Module | Topic | Status |
|--------|-------|--------|
| 1 | [Infrastructure as Code](docs/prerequisites/modern-devops/module-1-infrastructure-as-code.md) | ✅ |
| 2 | [GitOps](docs/prerequisites/modern-devops/module-2-gitops.md) | ✅ |
| 3 | [CI/CD Pipelines](docs/prerequisites/modern-devops/module-3-cicd-pipelines.md) | ✅ |
| 4 | [Observability Fundamentals](docs/prerequisites/modern-devops/module-4-observability.md) | ✅ |
| 5 | [Platform Engineering](docs/prerequisites/modern-devops/module-5-platform-engineering.md) | ✅ |
| 6 | [Security Practices (DevSecOps)](docs/prerequisites/modern-devops/module-6-devsecops.md) | ✅ |

---

## Platform Engineering Track 🚧

> **Beyond Certifications** - Deep practitioner knowledge for SRE, Platform Engineering, DevSecOps, and MLOps.
>
> This track is for practitioners who want to master the disciplines and tools that run on Kubernetes in production.

### Foundations (Theory That Doesn't Change)

| Track | Modules | Focus | Status |
|-------|---------|-------|--------|
| Systems Thinking | 4 | Complexity, feedback loops, emergence, Cynefin | 📋 |
| Reliability Engineering | 4 | Failure modes, redundancy, MTBF/MTTR, risk | 📋 |
| Observability Theory | 3 | Signals, cardinality, unknown unknowns | 📋 |
| Security Principles | 4 | Zero trust, threat modeling, defense in depth | 📋 |
| Distributed Systems | 4 | CAP theorem, consensus, consistency | 📋 |

### Disciplines (Applied Practices)

| Track | Modules | Focus | Status |
|-------|---------|-------|--------|
| SRE | 8 | SLOs, error budgets, incidents, chaos engineering | 📋 |
| Platform Engineering | 6 | IDPs, golden paths, self-service, developer experience | 📋 |
| GitOps | 5 | Reconciliation, progressive delivery, multi-cluster | 📋 |
| DevSecOps | 6 | Shift-left, supply chain, policy-as-code, compliance | 📋 |
| MLOps | 6 | ML lifecycle, experiment tracking, model serving | 📋 |

### Toolkits (Current Tools - Will Evolve)

| Track | Modules | Tools Covered | Status |
|-------|---------|---------------|--------|
| Observability | 6 | Prometheus, OpenTelemetry, Grafana, Loki, Tempo | 📋 |
| GitOps Tools | 5 | ArgoCD, Flux, Argo Rollouts, Flagger | 📋 |
| Security Tools | 5 | Vault, OPA/Gatekeeper, Kyverno, Falco, Sigstore | 📋 |
| Platforms | 4 | Backstage, Crossplane, Port, Kratix | 📋 |
| ML Platforms | 5 | Kubeflow, MLflow, Seldon/KServe, Feast, vLLM | 📋 |

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

```bash
git clone https://github.com/krisztiankoos/kubedojo.git
cd kubedojo
```

**Choose your path:**

| If you are... | Start here |
|---------------|------------|
| New to Kubernetes | [Prerequisites: Philosophy & Design](docs/prerequisites/philosophy-design/module-1-why-kubernetes-won.md) |
| Know basics, want certs | [KCNA Overview](docs/k8s/kcna/part0-introduction/module-0.1-kcna-overview.md) (entry-level) |
| Already certified | [Platform Track: Foundations](docs/platform/) (coming soon) |
| Experienced, want depth | [Platform Track: SRE](docs/platform/disciplines/sre/) (coming soon) |

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
