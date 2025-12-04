# KCNA Curriculum

> **Kubernetes and Cloud Native Associate** - Entry-level certification for cloud native fundamentals

## About KCNA

The KCNA is a **multiple-choice exam** (not hands-on) that validates foundational knowledge of Kubernetes and cloud native technologies. It's ideal for those new to cloud native or as preparation for CKA/CKAD.

| Aspect | Details |
|--------|---------|
| **Format** | Multiple choice |
| **Duration** | 90 minutes |
| **Questions** | ~60 questions |
| **Passing Score** | 75% |
| **Validity** | 3 years |

## Curriculum Structure

| Part | Topic | Weight | Modules |
|------|-------|--------|---------|
| [Part 0](part0-introduction/) | Introduction | - | 2 |
| [Part 1](part1-kubernetes-fundamentals/) | Kubernetes Fundamentals | 46% | 8 |
| [Part 2](part2-container-orchestration/) | Container Orchestration | 22% | 4 |
| [Part 3](part3-cloud-native-architecture/) | Cloud Native Architecture | 16% | 3 |
| [Part 4](part4-cloud-native-observability/) | Cloud Native Observability | 8% | 2 |
| [Part 5](part5-application-delivery/) | Application Delivery | 8% | 2 |
| **Total** | | **100%** | **21** |

## Module Overview

### Part 0: Introduction (2 modules)
- [0.1 KCNA Overview](part0-introduction/module-0.1-kcna-overview.md) - Exam format and domains
- [0.2 Study Strategy](part0-introduction/module-0.2-study-strategy.md) - Multiple-choice exam techniques

### Part 1: Kubernetes Fundamentals (8 modules)
- [1.1 What is Kubernetes](part1-kubernetes-fundamentals/module-1.1-what-is-kubernetes.md) - Purpose and architecture
- [1.2 Container Fundamentals](part1-kubernetes-fundamentals/module-1.2-container-fundamentals.md) - Container concepts
- [1.3 Control Plane](part1-kubernetes-fundamentals/module-1.3-control-plane.md) - API server, etcd, scheduler
- [1.4 Node Components](part1-kubernetes-fundamentals/module-1.4-node-components.md) - kubelet, kube-proxy
- [1.5 Pods](part1-kubernetes-fundamentals/module-1.5-pods.md) - Basic workload unit
- [1.6 Workload Resources](part1-kubernetes-fundamentals/module-1.6-workload-resources.md) - Deployments, StatefulSets
- [1.7 Services](part1-kubernetes-fundamentals/module-1.7-services.md) - Service types and discovery
- [1.8 Namespaces and Labels](part1-kubernetes-fundamentals/module-1.8-namespaces-labels.md) - Organization

### Part 2: Container Orchestration (4 modules)
- [2.1 Scheduling](part2-container-orchestration/module-2.1-scheduling.md) - How pods get assigned
- [2.2 Scaling](part2-container-orchestration/module-2.2-scaling.md) - HPA, VPA, Cluster Autoscaler
- [2.3 Storage](part2-container-orchestration/module-2.3-storage.md) - PV, PVC, StorageClass
- [2.4 Configuration](part2-container-orchestration/module-2.4-configuration.md) - ConfigMaps and Secrets

### Part 3: Cloud Native Architecture (3 modules)
- [3.1 Cloud Native Principles](part3-cloud-native-architecture/module-3.1-cloud-native-principles.md) - 12-factor apps
- [3.2 CNCF Ecosystem](part3-cloud-native-architecture/module-3.2-cncf-ecosystem.md) - Projects and landscape
- [3.3 Cloud Native Patterns](part3-cloud-native-architecture/module-3.3-patterns.md) - Service mesh, GitOps

### Part 4: Cloud Native Observability (2 modules)
- [4.1 Observability Fundamentals](part4-cloud-native-observability/module-4.1-observability-fundamentals.md) - Metrics, logs, traces
- [4.2 Observability Tools](part4-cloud-native-observability/module-4.2-observability-tools.md) - Prometheus, Grafana, Jaeger

### Part 5: Application Delivery (2 modules)
- [5.1 CI/CD Fundamentals](part5-application-delivery/module-5.1-ci-cd.md) - Pipelines and deployment
- [5.2 Application Packaging](part5-application-delivery/module-5.2-application-packaging.md) - Helm and Kustomize

## How to Use This Curriculum

1. **Follow the order** - Modules build on each other
2. **Read actively** - Don't just skim, understand concepts
3. **Take quizzes** - Each module has quiz questions
4. **Review diagrams** - Visual learning is key for multiple-choice
5. **Focus on "why"** - KCNA tests understanding, not commands

## Key Differences from CKA/CKAD

| Aspect | KCNA | CKA/CKAD |
|--------|------|----------|
| Format | Multiple choice | Hands-on lab |
| Focus | Concepts | Commands |
| Difficulty | Entry-level | Professional |
| Kubernetes access | None | Full cluster |

## Study Tips

- **Understand, don't memorize** - The exam tests concepts
- **Know CNCF projects** - Especially graduated ones
- **Focus on Part 1** - It's 46% of the exam
- **Review diagrams** - Visuals help with multiple-choice
- **Take practice tests** - Get comfortable with the format

## Start Learning

Begin with [Part 0: Introduction](part0-introduction/module-0.1-kcna-overview.md) to understand the exam format, then proceed through each part in order.

Good luck on your KCNA journey!
