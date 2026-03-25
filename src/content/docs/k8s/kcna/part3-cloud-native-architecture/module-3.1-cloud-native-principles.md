---
title: "Module 3.1: Cloud Native Principles"
slug: k8s/kcna/part3-cloud-native-architecture/module-3.1-cloud-native-principles
sidebar:
  order: 2
  label: "Part 3: Cloud Native Architecture"
---
> **Complexity**: `[MEDIUM]` - Architecture concepts
>
> **Time to Complete**: 30-35 minutes
>
> **Prerequisites**: Part 2 (Container Orchestration)

---

## Why This Module Matters

Cloud native is more than just containers—it's a set of principles for building scalable, resilient applications. The KCNA exam tests your understanding of what makes an application truly "cloud native." This module covers the foundational concepts.

---

## What is Cloud Native?

```
┌─────────────────────────────────────────────────────────────┐
│              CLOUD NATIVE DEFINITION                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CNCF Definition:                                          │
│  ─────────────────────────────────────────────────────────  │
│  "Cloud native technologies empower organizations to       │
│   build and run scalable applications in modern, dynamic  │
│   environments such as public, private, and hybrid clouds."│
│                                                             │
│  Key characteristics:                                      │
│  • Containers                                              │
│  • Service meshes                                          │
│  • Microservices                                           │
│  • Immutable infrastructure                                │
│  • Declarative APIs                                        │
│                                                             │
│  Cloud Native ≠ "Running in the cloud"                    │
│  ─────────────────────────────────────────────────────────  │
│  You can run cloud native apps on-premises                │
│  You can run non-cloud-native apps in the cloud           │
│                                                             │
│  Cloud native = designed for cloud environments           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## The 12-Factor App

The **12-Factor App** methodology is foundational to cloud native:

```
┌─────────────────────────────────────────────────────────────┐
│              THE 12 FACTORS                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. CODEBASE                                               │
│     One codebase tracked in version control                │
│     Many deploys (dev, staging, prod)                     │
│                                                             │
│  2. DEPENDENCIES                                           │
│     Explicitly declare and isolate dependencies            │
│     Never rely on system packages                          │
│                                                             │
│  3. CONFIG                                                 │
│     Store config in the environment                        │
│     Not in code (ConfigMaps/Secrets!)                     │
│                                                             │
│  4. BACKING SERVICES                                       │
│     Treat backing services as attached resources          │
│     Database, cache, queue = URLs, not special cases      │
│                                                             │
│  5. BUILD, RELEASE, RUN                                    │
│     Strictly separate build and run stages                │
│     Build → Release (build + config) → Run                │
│                                                             │
│  6. PROCESSES                                              │
│     Execute app as stateless processes                    │
│     State lives in backing services, not memory           │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              THE 12 FACTORS (continued)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  7. PORT BINDING                                           │
│     Export services via port binding                       │
│     App is self-contained, serves HTTP                    │
│                                                             │
│  8. CONCURRENCY                                            │
│     Scale out via the process model                       │
│     Run multiple instances, not bigger instances          │
│                                                             │
│  9. DISPOSABILITY                                          │
│     Maximize robustness with fast startup/shutdown        │
│     Can be started/stopped at any moment                  │
│                                                             │
│ 10. DEV/PROD PARITY                                        │
│     Keep development, staging, production similar         │
│     Same tools, same dependencies                         │
│                                                             │
│ 11. LOGS                                                   │
│     Treat logs as event streams                           │
│     Write to stdout, let platform handle collection       │
│                                                             │
│ 12. ADMIN PROCESSES                                        │
│     Run admin/management tasks as one-off processes       │
│     Migrations, scripts as separate Jobs                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 12-Factor in Kubernetes Context

| Factor | Kubernetes Implementation |
|--------|--------------------------|
| Codebase | Container images from Git |
| Dependencies | Container images bundle deps |
| Config | ConfigMaps and Secrets |
| Backing services | Services point to databases |
| Build/Release/Run | CI/CD pipelines |
| Processes | Pods are stateless |
| Port binding | Container ports |
| Concurrency | Horizontal scaling (replicas) |
| Disposability | Fast container startup |
| Dev/prod parity | Same images everywhere |
| Logs | Stdout → log aggregation |
| Admin processes | Jobs and CronJobs |

---

## Microservices Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              MONOLITH vs MICROSERVICES                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  MONOLITH:                                                 │
│  ─────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Single Application                      │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │   │
│  │  │   UI    │ │ Orders  │ │ Payment │ │ Shipping│  │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │   │
│  │              Shared Database                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  • One deployment                                          │
│  • Changes affect everything                               │
│  • Scale entire app                                        │
│                                                             │
│  MICROSERVICES:                                            │
│  ─────────────────────────────────────────────────────────  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │   UI    │  │ Orders  │  │ Payment │  │Shipping │       │
│  │ Service │  │ Service │  │ Service │  │ Service │       │
│  │   DB    │  │   DB    │  │   DB    │  │   DB    │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│       ↑            ↑            ↑            ↑             │
│       └────────────┴─────┬──────┴────────────┘             │
│                          │                                  │
│                     API Gateway                            │
│                                                             │
│  • Independent deployments                                 │
│  • Change one service only                                 │
│  • Scale individual services                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Microservices Characteristics

| Characteristic | Description |
|----------------|-------------|
| **Single responsibility** | Each service does one thing well |
| **Independent deployment** | Deploy without affecting others |
| **Decentralized data** | Each service owns its data |
| **Technology agnostic** | Use best tool for each service |
| **Failure isolation** | One failure doesn't crash all |
| **Team ownership** | Small teams own services |

---

## Immutable Infrastructure

```
┌─────────────────────────────────────────────────────────────┐
│              IMMUTABLE INFRASTRUCTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  MUTABLE (Traditional):                                    │
│  ─────────────────────────────────────────────────────────  │
│  Server → SSH in → Update packages → Modify config        │
│                                                             │
│  Problem: Servers diverge over time ("snowflakes")        │
│  "But it works on server A!" doesn't work on server B     │
│                                                             │
│  IMMUTABLE (Cloud Native):                                 │
│  ─────────────────────────────────────────────────────────  │
│  Need change? → Build new image → Deploy new container    │
│                → Delete old container                      │
│                                                             │
│  ┌─────────┐      ┌─────────┐                             │
│  │ v1.0    │  →   │ v1.1    │   (new container)          │
│  │ Running │      │ Running │                             │
│  └─────────┘      └─────────┘                             │
│       ↓                                                    │
│   Deleted                                                  │
│                                                             │
│  Benefits:                                                 │
│  • Reproducible deployments                               │
│  • Easy rollback (just run old version)                   │
│  • No configuration drift                                  │
│  • Better testing (same image everywhere)                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Declarative vs Imperative

```
┌─────────────────────────────────────────────────────────────┐
│              DECLARATIVE vs IMPERATIVE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  IMPERATIVE: "How to do it"                               │
│  ─────────────────────────────────────────────────────────  │
│  kubectl run nginx --image=nginx                          │
│  kubectl scale deployment nginx --replicas=3              │
│  kubectl expose deployment nginx --port=80                │
│                                                             │
│  • Step by step commands                                   │
│  • You specify the actions                                 │
│  • No record of desired state                             │
│                                                             │
│  DECLARATIVE: "What you want"                             │
│  ─────────────────────────────────────────────────────────  │
│  apiVersion: apps/v1                                      │
│  kind: Deployment                                          │
│  spec:                                                     │
│    replicas: 3                                             │
│    template:                                               │
│      spec:                                                 │
│        containers:                                         │
│        - name: nginx                                       │
│          image: nginx                                      │
│                                                             │
│  kubectl apply -f deployment.yaml                         │
│                                                             │
│  • Describe desired state                                  │
│  • Kubernetes figures out how                             │
│  • Version controlled (GitOps!)                           │
│                                                             │
│  Cloud native = Declarative                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Design for Failure

```
┌─────────────────────────────────────────────────────────────┐
│              DESIGN FOR FAILURE                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Cloud native assumption:                                  │
│  ─────────────────────────────────────────────────────────  │
│  "Everything will fail. Plan for it."                     │
│                                                             │
│  Patterns:                                                 │
│                                                             │
│  1. REDUNDANCY                                             │
│     Run multiple replicas                                  │
│     If one fails, others handle traffic                   │
│                                                             │
│  2. HEALTH CHECKS                                          │
│     Liveness: "Is the container alive?"                   │
│     Readiness: "Can it receive traffic?"                  │
│     Kubernetes restarts unhealthy containers              │
│                                                             │
│  3. CIRCUIT BREAKER                                        │
│     If service B is failing, stop calling it              │
│     Fail fast, don't wait for timeouts                    │
│                                                             │
│  4. RETRY WITH BACKOFF                                     │
│     Retry failed requests                                  │
│     Wait longer between each retry                        │
│                                                             │
│  5. GRACEFUL DEGRADATION                                   │
│     If recommendation service fails                        │
│     Show generic recommendations instead of error         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Did You Know?

- **12-factor started at Heroku** - Created by developers at Heroku in 2011 based on their experience running millions of apps.

- **Beyond 12 factors** - Some propose additional factors like API-first, telemetry, and authentication/authorization.

- **Microservices aren't always better** - They add complexity (networking, debugging, deployment). Start simple, split when needed.

- **Netflix pioneered many patterns** - Circuit breakers (Hystrix), service discovery (Eureka), and API gateway (Zuul) came from Netflix's cloud journey.

---

## Common Mistakes

| Mistake | Why It Hurts | Correct Understanding |
|---------|--------------|----------------------|
| "Cloud native = in the cloud" | Miss the architectural principles | Cloud native is about HOW you build |
| Starting with microservices | Over-engineering | Start monolith, split when needed |
| Storing state in containers | Data loss on restart | Use external state stores |
| Imperative management | Hard to reproduce/audit | Use declarative YAML |

---

## Quiz

1. **What is cloud native according to CNCF?**
   <details>
   <summary>Answer</summary>
   Technologies that empower building scalable applications in dynamic environments (public, private, hybrid clouds). Key elements: containers, service meshes, microservices, immutable infrastructure, declarative APIs.
   </details>

2. **What does "treat backing services as attached resources" mean?**
   <details>
   <summary>Answer</summary>
   12-Factor principle: databases, caches, message queues should be accessed via URL/connection string. Switching from local MySQL to AWS RDS should only require changing a configuration value.
   </details>

3. **Why use declarative over imperative?**
   <details>
   <summary>Answer</summary>
   Declarative specifications describe desired state, are version controlled, reproducible, and auditable. Kubernetes reconciles actual state to desired state. Imperative commands leave no record and are harder to reproduce.
   </details>

4. **What is immutable infrastructure?**
   <details>
   <summary>Answer</summary>
   Never modify running infrastructure. Instead, build new images and replace old containers. Benefits: reproducibility, easy rollback, no configuration drift, consistent testing.
   </details>

5. **What does "design for failure" mean?**
   <details>
   <summary>Answer</summary>
   Assume everything will fail and plan accordingly: run multiple replicas, implement health checks, use circuit breakers, retry with backoff, degrade gracefully. The system should survive component failures.
   </details>

---

## Summary

**Cloud Native is**:
- Containers + microservices + automation
- Designed for scale and resilience
- Not just "running in the cloud"

**12-Factor App**:
- Codebase, dependencies, config
- Backing services, build/release/run, processes
- Port binding, concurrency, disposability
- Dev/prod parity, logs, admin processes

**Key principles**:
- **Microservices**: Small, independent services
- **Immutable infrastructure**: Replace, don't modify
- **Declarative**: Describe what, not how
- **Design for failure**: Expect and handle failures

---

## Next Module

[Module 3.2: CNCF Ecosystem](module-3.2-cncf-ecosystem/) - Understanding the Cloud Native Computing Foundation and its landscape.
