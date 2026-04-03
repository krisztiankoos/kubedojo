---
title: "Module 1.1: What is Kubernetes?"
slug: k8s/kcna/part1-kubernetes-fundamentals/module-1.1-what-is-kubernetes
sidebar:
  order: 2
---
> **Complexity**: `[QUICK]` - Foundational concepts
>
> **Time to Complete**: 20-25 minutes
>
> **Prerequisites**: None

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Explain** what Kubernetes is, the problems it solves, and why it became the industry standard
2. **Compare** Kubernetes with traditional deployment, VM-based, and other orchestration approaches
3. **Identify** the key capabilities Kubernetes provides: self-healing, scaling, service discovery, and rollouts
4. **Evaluate** whether a given workload scenario would benefit from Kubernetes orchestration

---

## Why This Module Matters

"What is Kubernetes?" might seem like a simple question, but understanding it deeply is crucial. KCNA tests whether you truly understand Kubernetes' purpose, not just its features.

This module establishes the foundation everything else builds on.

---

## The Problem Kubernetes Solves

```
┌─────────────────────────────────────────────────────────────┐
│              BEFORE KUBERNETES                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Traditional Deployment:                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Server 1         Server 2         Server 3         │   │
│  │  ┌─────────┐     ┌─────────┐     ┌─────────┐       │   │
│  │  │  App A  │     │  App B  │     │  App C  │       │   │
│  │  └─────────┘     └─────────┘     └─────────┘       │   │
│  │  ┌─────────┐     ┌─────────┐     ┌─────────┐       │   │
│  │  │   OS    │     │   OS    │     │   OS    │       │   │
│  │  └─────────┘     └─────────┘     └─────────┘       │   │
│  │  ┌─────────┐     ┌─────────┐     ┌─────────┐       │   │
│  │  │Hardware │     │Hardware │     │Hardware │       │   │
│  │  └─────────┘     └─────────┘     └─────────┘       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Problems:                                                 │
│  • One app per server = waste                              │
│  • Server dies = app dies                                  │
│  • Manual scaling                                          │
│  • Deployment is risky                                     │
│  • No standard way to manage                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## What is Kubernetes?

**Kubernetes** (K8s) is an open-source **container orchestration platform** that automates deploying, scaling, and managing containerized applications.

### Breaking That Down

| Term | Meaning |
|------|---------|
| **Open-source** | Free, community-driven, no vendor lock-in |
| **Container orchestration** | Managing many containers as a system |
| **Platform** | Foundation to build on, not just a tool |
| **Automates** | Reduces manual work and human error |

### The Name

- **Kubernetes** = Greek for "helmsman" or "pilot"
- **K8s** = K + 8 letters + s (shorthand)
- Originated at Google (based on Borg)
- Donated to CNCF in 2015

---

## What Kubernetes Does

```
┌─────────────────────────────────────────────────────────────┐
│              KUBERNETES CAPABILITIES                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. DEPLOYMENT                                             │
│     "Run my app"                                           │
│     ├── Deploy containers                                  │
│     ├── Rolling updates                                    │
│     └── Rollback if needed                                 │
│                                                             │
│  2. SCALING                                                │
│     "Handle more traffic"                                  │
│     ├── Scale up (more replicas)                          │
│     ├── Scale down (fewer replicas)                       │
│     └── Autoscale based on metrics                        │
│                                                             │
│  3. HEALING                                                │
│     "Keep it running"                                      │
│     ├── Restart failed containers                          │
│     ├── Replace unhealthy nodes                           │
│     └── Reschedule if node dies                           │
│                                                             │
│  4. SERVICE DISCOVERY                                      │
│     "Let apps find each other"                            │
│     ├── DNS-based discovery                               │
│     ├── Load balancing                                    │
│     └── Internal networking                               │
│                                                             │
│  5. CONFIGURATION                                          │
│     "Manage settings"                                      │
│     ├── ConfigMaps for config                             │
│     ├── Secrets for sensitive data                        │
│     └── Environment injection                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Kubernetes vs Alternatives

### Why Not Just Use VMs?

| Aspect | Virtual Machines | Kubernetes + Containers |
|--------|------------------|------------------------|
| Startup time | Minutes | Seconds |
| Resource usage | Heavy (full OS) | Light (shared kernel) |
| Density | ~10s per host | ~100s per host |
| Portability | Limited | High |
| Scaling | Slow | Fast |

### Why Not Just Use Docker?

Docker runs containers. Kubernetes **orchestrates** them:

```
┌─────────────────────────────────────────────────────────────┐
│              DOCKER vs KUBERNETES                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  DOCKER:                                                   │
│  "Run this container on this machine"                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  docker run nginx                                   │   │
│  │  → Runs ONE container on ONE machine                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  KUBERNETES:                                               │
│  "Run 3 copies, keep them healthy, balance traffic"        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Deployment: nginx, replicas: 3                     │   │
│  │  → Runs across cluster                              │   │
│  │  → Self-heals if one dies                           │   │
│  │  → Load balances traffic                            │   │
│  │  → Scales up/down automatically                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Docker = Container runtime                                │
│  Kubernetes = Container orchestrator                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Kubernetes Concepts

> **Pause and predict**: If Docker can already run containers, why would an organization need Kubernetes on top of it? What problems remain unsolved after you can run a single container on a single machine?

### Declarative Configuration

You tell Kubernetes **what you want**, not **how to do it**:

```yaml
# You declare: "I want 3 nginx replicas"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 3  # Desired state
  ...
```

Kubernetes continuously works to make reality match your declaration.

### Desired State vs Current State

```
┌─────────────────────────────────────────────────────────────┐
│              DESIRED STATE RECONCILIATION                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  You declare:     "I want 3 replicas"                      │
│                         │                                   │
│                         ▼                                   │
│  Kubernetes:      Checks current state                     │
│                         │                                   │
│           ┌─────────────┴─────────────┐                    │
│           │                           │                     │
│           ▼                           ▼                     │
│     If 2 running:              If 4 running:               │
│     "Create 1 more"            "Terminate 1"               │
│                                                             │
│  This loop runs CONTINUOUSLY                               │
│  Kubernetes never stops trying to match desired state      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **Stop and think**: If Kubernetes uses a declarative model and you declare "I want 3 replicas," what happens when one replica crashes at 3 AM? Who or what restarts it, and how does the system know it should?

### Immutable Infrastructure

- Containers aren't modified in place
- Updates create new containers
- Old containers are replaced, not changed
- This ensures consistency and reproducibility

---

## Where Kubernetes Runs

Kubernetes can run:

| Environment | Examples |
|-------------|----------|
| **Public Cloud** | EKS (AWS), GKE (Google), AKS (Azure) |
| **Private Cloud** | OpenStack, VMware |
| **On-Premises** | Bare metal, data centers |
| **Edge** | Retail stores, factories |
| **Development** | minikube, kind, Docker Desktop |

This flexibility is a key advantage—no vendor lock-in.

---

## Did You Know?

- **Kubernetes came from Google's Borg** - Google ran Borg internally for 10+ years before creating Kubernetes as an open-source version.

- **K8s handles massive scale** - Large clusters can run 5,000+ nodes and 150,000+ pods.

- **Most CNCF projects integrate with K8s** - Kubernetes is the foundation of the cloud native ecosystem.

- **The release cycle is predictable** - New Kubernetes versions come out every ~4 months with a 14-month support window.

---

## Common Mistakes

| Mistake | Why It Hurts | Correct Understanding |
|---------|--------------|----------------------|
| "K8s is just Docker" | Missing orchestration value | K8s orchestrates containers; Docker runs them |
| "K8s replaces VMs" | They serve different purposes | K8s runs ON VMs or bare metal |
| "K8s is only for big companies" | Missing development value | K8s works at any scale |
| "K8s is a container runtime" | Confusing layers | K8s uses runtimes like containerd |

---

## Quiz

1. **Your team is evaluating container orchestration tools. A colleague suggests Docker Swarm is simpler to set up. What advantages does Kubernetes offer that might justify the added complexity?**
   <details>
   <summary>Answer</summary>
   Kubernetes offers a much larger ecosystem (CNCF projects, Helm charts, operators), a declarative configuration model with continuous reconciliation, robust autoscaling (HPA, VPA, Cluster Autoscaler), a rich scheduling system (affinity, taints, tolerations), and extensive community support. While Docker Swarm is simpler, Kubernetes provides self-healing, rolling updates with rollback, service discovery via DNS, and is the industry standard supported by all major cloud providers. The complexity pays off at scale and when you need production-grade features.
   </details>

2. **A startup is running their web application on a single VM. Traffic is growing, and they are considering Kubernetes. What specific problems would Kubernetes solve that their current single-VM setup cannot handle?**
   <details>
   <summary>Answer</summary>
   A single VM creates a single point of failure -- if it goes down, the entire application is unavailable. Kubernetes solves this by running multiple replicas across multiple nodes, providing self-healing (automatic restart and rescheduling), horizontal scaling to handle traffic spikes, rolling updates for zero-downtime deployments, and service discovery so components can find each other. It also enables efficient resource utilization by bin-packing containers onto nodes.
   </details>

3. **A new hire asks: "Isn't Kubernetes just a container runtime like Docker?" How would you explain the difference between the two?**
   <details>
   <summary>Answer</summary>
   Docker (specifically containerd) is a container runtime -- it knows how to create, start, and stop a single container on a single machine. Kubernetes is a container orchestrator -- it manages containers across a cluster of machines. Kubernetes decides where containers run, restarts them if they crash, scales them based on demand, provides networking between them, and ensures the system matches your declared desired state. Kubernetes actually uses a container runtime (like containerd) under the hood to do the actual work of running containers.
   </details>

4. **You declare a Deployment with 3 replicas, but currently 4 pods are running due to a previous manual scaling operation. What will Kubernetes do, and why?**
   <details>
   <summary>Answer</summary>
   Kubernetes will terminate one pod to bring the count down to 3. This is the declarative model at work: you declared the desired state (3 replicas), and Kubernetes continuously reconciles the current state to match. The reconciliation loop checks: "Are there 3 pods? No, there are 4. Action: terminate 1." This loop runs continuously, which is why Kubernetes is self-healing -- it constantly tries to make reality match your declaration.
   </details>

5. **Your company wants to avoid vendor lock-in. How does Kubernetes help with this goal, and what is the historical reason it was designed this way?**
   <details>
   <summary>Answer</summary>
   Kubernetes runs on any infrastructure -- public cloud (EKS, GKE, AKS), private cloud, on-premises bare metal, or even developer laptops. Your application manifests are portable across environments. This is by design: Google donated Kubernetes to the vendor-neutral CNCF in 2015 specifically to prevent any single company from controlling it. The same Deployment YAML works on AWS, GCP, Azure, or your own data center, meaning you can move workloads between providers without rewriting your application configuration.
   </details>

---

## Summary

**Kubernetes is**:
- An open-source container orchestration platform
- Automates deployment, scaling, and management
- Uses declarative configuration (desired state)
- Runs anywhere (cloud, on-prem, edge)

**Kubernetes does**:
- Deploys and updates containers
- Scales applications up and down
- Self-heals when things fail
- Provides service discovery
- Manages configuration

**Key insight**: Kubernetes is NOT a container runtime—it orchestrates containers that runtimes like containerd actually run.

---

## Next Module

[Module 1.2: Container Fundamentals](../module-1.2-container-fundamentals/) - Understanding containers before diving into Kubernetes architecture.
