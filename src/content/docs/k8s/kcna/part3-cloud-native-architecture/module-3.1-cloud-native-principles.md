---
title: "Module 3.1: Cloud Native Principles"
slug: k8s/kcna/part3-cloud-native-architecture/module-3.1-cloud-native-principles
sidebar:
  order: 2
---
> **Complexity**: `[MEDIUM]` - Architecture concepts
>
> **Time to Complete**: 30-35 minutes
>
> **Prerequisites**: Part 2 (Container Orchestration)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Explain** the CNCF definition of cloud native and its core principles
2. **Compare** cloud native applications with traditional monolithic architectures
3. **Identify** the twelve-factor app principles and how they apply to Kubernetes workloads
4. **Evaluate** whether an application design follows cloud native best practices

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

> **Pause and predict**: Factor 6 says "execute the app as stateless processes." But databases need to store data. Does this mean databases cannot be cloud native? How does Kubernetes handle the tension between statelessness and the need for persistent data?

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

> **Stop and think**: Your company runs a monolithic e-commerce app. A bug in the payment module crashes the entire application, including the shopping cart and product catalog. How would a microservices architecture change the blast radius of this failure?

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

1. **A colleague says "we moved our monolith to a container on Kubernetes, so now we are cloud native." Is this statement correct? What would actually make their application cloud native?**
   <details>
   <summary>Answer</summary>
   Simply containerizing a monolith is not cloud native -- it is "lift and shift." Cloud native is about how you design applications, not just where they run. To be truly cloud native, the application should be broken into microservices that scale independently, use declarative configuration (ConfigMaps/Secrets rather than hardcoded values), treat backing services as attached resources, write logs to stdout for collection, start quickly for disposability, and be designed for failure with health checks, retries, and graceful degradation. You can run cloud native apps on-premises and non-cloud-native apps in the cloud.
   </details>

2. **Your application connects to a PostgreSQL database using a hardcoded connection string in the source code. When migrating from a local database to AWS RDS, the team must rebuild and redeploy the container. Which 12-Factor principle does this violate, and how would Kubernetes solve it?**
   <details>
   <summary>Answer</summary>
   This violates Factor 3 (Config: store config in the environment) and Factor 4 (Backing Services: treat as attached resources). The database connection string should not be in the source code. In Kubernetes, store it in a Secret or ConfigMap and inject it as an environment variable or mounted file. Switching from local PostgreSQL to AWS RDS then requires only updating the Secret value -- no code change, no image rebuild, no redeployment of the application container.
   </details>

3. **An operations engineer SSHs into a production server to manually update a configuration file and restart a service. This fixes the immediate issue, but a week later the same server behaves differently from other servers running the "same" application. What principle was violated, and what is the cloud native alternative?**
   <details>
   <summary>Answer</summary>
   This violates immutable infrastructure. Manual changes create "snowflake servers" -- each server diverges over time, making behavior unpredictable and unreproducible. The cloud native alternative is to never modify running infrastructure. Instead, fix the configuration in the source (Dockerfile, Helm chart, ConfigMap), build a new container image, and deploy it through the CI/CD pipeline. If the fix is configuration-only, update the ConfigMap or Secret and let Kubernetes roll out the change. The old container is replaced, never modified, ensuring all instances are identical.
   </details>

4. **A startup is building a new e-commerce platform and wants to start with 15 microservices for every feature (user auth, product catalog, shopping cart, payment, shipping, etc.). A senior engineer pushes back. Why might starting with microservices be a mistake, and what approach does the cloud native community recommend?**
   <details>
   <summary>Answer</summary>
   Starting with many microservices adds enormous complexity before you understand your domain boundaries: distributed debugging, inter-service networking, data consistency, deployment coordination, and operational overhead for a small team. The recommended approach is to start with a well-structured monolith and split into microservices when specific components need to scale independently or when team boundaries justify separation. Microservices solve organizational and scaling problems, but they create operational problems. If you do not yet have those scaling problems, microservices are premature over-engineering.
   </details>

5. **Your payment service calls an external payment gateway. During peak hours, the gateway becomes slow (5-second response times instead of 200ms). Without any failure handling, your payment service threads are all blocked waiting for responses, and soon the entire service becomes unresponsive. What cloud native "design for failure" patterns would prevent this cascading failure?**
   <details>
   <summary>Answer</summary>
   Multiple patterns work together: a circuit breaker detects repeated slow responses and stops calling the gateway temporarily, failing fast instead of blocking. Timeouts ensure no request waits more than a defined threshold. Retry with exponential backoff retries failed requests with increasing delays to avoid overwhelming the recovering gateway. Graceful degradation could queue payment requests for later processing instead of failing entirely. In Kubernetes, readiness probes would remove the unhealthy payment Pods from Service endpoints so they stop receiving new traffic. A service mesh like Istio can implement circuit breaking and retries at the infrastructure level.
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

[Module 3.2: CNCF Ecosystem](../module-3.2-cncf-ecosystem/) - Understanding the Cloud Native Computing Foundation and its landscape.
