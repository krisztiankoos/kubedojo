---
title: "Module 3.3: Cloud Native Patterns"
slug: k8s/kcna/part3-cloud-native-architecture/module-3.3-patterns
sidebar:
  order: 4
---
> **Complexity**: `[MEDIUM]` - Architecture concepts
>
> **Time to Complete**: 30-35 minutes
>
> **Prerequisites**: Module 3.2 (CNCF Ecosystem)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Explain** service mesh architecture and when it adds value over plain Kubernetes networking
2. **Compare** serverless, service mesh, and GitOps patterns by use case and trade-offs
3. **Identify** which architectural pattern addresses a given distributed systems challenge
4. **Evaluate** the overhead vs. benefit of adopting patterns like service mesh or event-driven architecture

---

## Why This Module Matters

Beyond basic concepts, cloud native includes patterns for solving complex problems—service mesh for microservice communication, serverless for event-driven workloads, GitOps for deployment automation. KCNA tests your understanding of these architectural patterns.

---

## Service Mesh

```
┌─────────────────────────────────────────────────────────────┐
│              SERVICE MESH                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Problem: Microservices need:                              │
│  • Service-to-service communication                        │
│  • Load balancing                                          │
│  • Security (mTLS)                                         │
│  • Observability (traces, metrics)                         │
│  • Traffic management (canary, retries)                   │
│                                                             │
│  Without service mesh:                                     │
│  ─────────────────────────────────────────────────────────  │
│  Each service implements this itself = duplication        │
│                                                             │
│  With service mesh:                                        │
│  ─────────────────────────────────────────────────────────  │
│  Infrastructure layer handles it transparently            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                CONTROL PLANE                        │   │
│  │  (Istio/Linkerd control plane)                     │   │
│  │  Configuration, certificates, policies             │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                   │
│                         │ configures                       │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                DATA PLANE                           │   │
│  │                                                      │   │
│  │  ┌───────────────┐      ┌───────────────┐          │   │
│  │  │ Service A     │      │ Service B     │          │   │
│  │  │ ┌───────────┐ │      │ ┌───────────┐ │          │   │
│  │  │ │   App     │ │      │ │   App     │ │          │   │
│  │  │ └───────────┘ │      │ └───────────┘ │          │   │
│  │  │ ┌───────────┐ │      │ ┌───────────┐ │          │   │
│  │  │ │  Sidecar  │ │←────→│ │  Sidecar  │ │          │   │
│  │  │ │  (Envoy)  │ │      │ │  (Envoy)  │ │          │   │
│  │  │ └───────────┘ │      │ └───────────┘ │          │   │
│  │  └───────────────┘      └───────────────┘          │   │
│  │                                                      │   │
│  │  All traffic goes through sidecars                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Service Mesh Benefits

| Feature | Description |
|---------|-------------|
| **mTLS** | Automatic encryption between services |
| **Traffic management** | Canary releases, A/B testing |
| **Retries/Timeouts** | Automatic retry with backoff |
| **Circuit breaking** | Fail fast when service is down |
| **Observability** | Automatic metrics, traces, logs |
| **Access control** | Service-to-service authorization |

> **Pause and predict**: A service mesh adds a sidecar proxy to every Pod. This means for 100 application Pods, you now have 200 containers running. What trade-off is being made, and when would the overhead be worth it?

### Popular Service Meshes

| Mesh | Key Characteristics |
|------|---------------------|
| **Istio** | Feature-rich, uses Envoy, complex |
| **Linkerd** | Lightweight, simple, CNCF graduated |
| **Cilium** | eBPF-based, no sidecars needed |

---

## Serverless / FaaS

```
┌─────────────────────────────────────────────────────────────┐
│              SERVERLESS                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  What is serverless?                                       │
│  ─────────────────────────────────────────────────────────  │
│  • Run code without managing servers                       │
│  • Pay only when code runs                                 │
│  • Automatic scaling (including to zero)                  │
│                                                             │
│  Types:                                                    │
│                                                             │
│  FaaS (Function as a Service):                            │
│  ─────────────────────────────────────────────────────────  │
│  Event → Function executes → Result                       │
│                                                             │
│  ┌─────────┐     ┌─────────────┐     ┌─────────┐          │
│  │  Event  │ ──→ │  Function   │ ──→ │ Result  │          │
│  │(HTTP,   │     │(Your code)  │     │         │          │
│  │ Queue,  │     │             │     │         │          │
│  │ Timer)  │     └─────────────┘     └─────────┘          │
│  └─────────┘                                               │
│                                                             │
│  Example: Process uploaded image                          │
│  1. Image uploaded to S3 (event)                          │
│  2. Function triggered                                     │
│  3. Function resizes image                                │
│  4. Function saves result                                 │
│                                                             │
│  Kubernetes Serverless:                                   │
│  ─────────────────────────────────────────────────────────  │
│  • Knative: Serverless on Kubernetes                      │
│  • OpenFaaS: Functions on Kubernetes                      │
│  • KEDA: Event-driven autoscaling                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Serverless Characteristics

| Aspect | Description |
|--------|-------------|
| **No server management** | Platform handles infrastructure |
| **Auto-scaling** | Scales up with load, down to zero |
| **Event-driven** | Triggered by events |
| **Pay-per-use** | Billed per execution |
| **Stateless** | Functions don't maintain state |
| **Short-lived** | Functions have time limits |

---

## GitOps

```
┌─────────────────────────────────────────────────────────────┐
│              GITOPS                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Git = Single source of truth                             │
│                                                             │
│  Traditional CI/CD:                                        │
│  ─────────────────────────────────────────────────────────  │
│  Git → CI → Build → Push to cluster                       │
│                                                             │
│  GitOps:                                                   │
│  ─────────────────────────────────────────────────────────  │
│  Git ← Pull ← Agent in cluster                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                      │   │
│  │  ┌──────────┐                    ┌──────────────┐   │   │
│  │  │   Git    │                    │  Kubernetes  │   │   │
│  │  │   Repo   │←─── Agent pulls ───│   Cluster    │   │   │
│  │  │(desired) │                    │  (actual)    │   │   │
│  │  └──────────┘                    └──────────────┘   │   │
│  │       │                                │             │   │
│  │       │                                │             │   │
│  │       └──── Agent reconciles ──────────┘             │   │
│  │             (makes actual = desired)                │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  GitOps tools:                                             │
│  • Argo CD (CNCF Graduated)                               │
│  • Flux (CNCF Graduated)                                  │
│                                                             │
│  Benefits:                                                 │
│  • Declarative (Git stores desired state)                │
│  • Auditable (Git history = change log)                  │
│  • Reversible (git revert = rollback)                    │
│  • Secure (cluster pulls, no push credentials needed)    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### GitOps Principles

| Principle | Description |
|-----------|-------------|
| **Declarative** | Desired state in Git |
| **Versioned** | Git provides history |
| **Automated** | Changes auto-applied |
| **Audited** | Git log = audit trail |

---

## Autoscaling Patterns

```
┌─────────────────────────────────────────────────────────────┐
│              AUTOSCALING PATTERNS                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  HORIZONTAL POD AUTOSCALER (HPA)                          │
│  ─────────────────────────────────────────────────────────  │
│  Scale based on metrics (CPU, memory, custom)             │
│  [Pod][Pod] → [Pod][Pod][Pod][Pod]                       │
│                                                             │
│  VERTICAL POD AUTOSCALER (VPA)                            │
│  ─────────────────────────────────────────────────────────  │
│  Adjust resource requests/limits                          │
│  [100m CPU] → [500m CPU]                                 │
│                                                             │
│  CLUSTER AUTOSCALER                                       │
│  ─────────────────────────────────────────────────────────  │
│  Add/remove nodes based on pending pods                   │
│  [Node 1][Node 2] → [Node 1][Node 2][Node 3]            │
│                                                             │
│  KEDA (Kubernetes Event-Driven Autoscaler)                │
│  ─────────────────────────────────────────────────────────  │
│  Scale on external events                                 │
│  • Queue messages                                         │
│  • Database connections                                   │
│  • Custom metrics                                         │
│  • Scale to zero!                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Operators and CRDs

```
┌─────────────────────────────────────────────────────────────┐
│              OPERATORS                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  What is an Operator?                                      │
│  ─────────────────────────────────────────────────────────  │
│  Software that extends Kubernetes to manage complex apps  │
│  "Human operator knowledge, codified"                     │
│                                                             │
│  How it works:                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  1. Custom Resource Definition (CRD):                     │
│     Defines new resource type                             │
│     kind: PostgresCluster                                 │
│                                                             │
│  2. Custom Resource (CR):                                 │
│     Instance of the CRD                                   │
│     "I want a 3-node Postgres cluster"                   │
│                                                             │
│  3. Operator (Controller):                                │
│     Watches CRs, takes action                             │
│     Creates Pods, Services, PVCs as needed               │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                      │   │
│  │  You write:              Operator creates:          │   │
│  │  ──────────────          ─────────────────          │   │
│  │  kind: PostgresCluster   • StatefulSet              │   │
│  │  spec:                   • Service                  │   │
│  │    replicas: 3           • PVCs                     │   │
│  │    version: 14           • ConfigMaps               │   │
│  │                          • Secrets                  │   │
│  │                          • Handles backups          │   │
│  │                          • Handles failover         │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Popular Operators:                                        │
│  • Prometheus Operator                                    │
│  • cert-manager                                           │
│  • Strimzi (Kafka)                                        │
│  • PostgreSQL Operators                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Stop and think**: In traditional CI/CD, the CI server pushes changes to the cluster. In GitOps, the cluster pulls from Git. Why is the pull-based model considered more secure? Think about what credentials each approach needs and where they are stored.

## Multi-Tenancy Patterns

```
┌─────────────────────────────────────────────────────────────┐
│              MULTI-TENANCY                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Running multiple tenants on same cluster                 │
│                                                             │
│  NAMESPACE-BASED:                                          │
│  ─────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Cluster                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │ NS: team-a  │  │ NS: team-b  │  │ NS: team-c  │ │   │
│  │  │ [Pods]      │  │ [Pods]      │  │ [Pods]      │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Isolation via:                                            │
│  • RBAC (who can access what)                             │
│  • ResourceQuotas (limit resources per namespace)         │
│  • NetworkPolicies (network isolation)                    │
│  • LimitRanges (default resource limits)                 │
│                                                             │
│  CLUSTER-PER-TENANT:                                       │
│  ─────────────────────────────────────────────────────────  │
│  Strongest isolation, higher cost                         │
│                                                             │
│  VIRTUAL CLUSTERS:                                         │
│  ─────────────────────────────────────────────────────────  │
│  Tools like vCluster create isolated "virtual" clusters   │
│  Stronger isolation than namespaces, less than clusters  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Did You Know?

- **Sidecars are going away** - Service meshes like Cilium use eBPF to avoid sidecar containers. Istio now supports "ambient mesh" without sidecars.

- **GitOps coined by Weaveworks** - The term and practice were popularized by Weaveworks, creators of Flux.

- **Operators have a maturity model** - From basic install (Level 1) to auto-pilot (Level 5), measuring automation capability.

- **KEDA is CNCF Graduated** - Kubernetes Event-Driven Autoscaler became a graduated project, showing the importance of event-driven patterns.

---

## Common Mistakes

| Mistake | Why It Hurts | Correct Understanding |
|---------|--------------|----------------------|
| Service mesh for simple apps | Adds unnecessary complexity | Use when microservice complexity justifies it |
| Confusing serverless and containers | Different models | Serverless = event-triggered, auto-scale to zero |
| Push-based CD as GitOps | Not true GitOps | GitOps = cluster pulls from Git |
| Operators for simple apps | Over-engineering | Use Operators for complex stateful apps |

---

## Quiz

1. **Your company has 30 microservices, and each team independently implements retry logic, timeouts, and circuit breakers in their application code. Bugs in one team's retry logic caused a cascading failure last month. How would a service mesh solve this problem, and what is the trade-off?**
   <details>
   <summary>Answer</summary>
   A service mesh moves retry logic, timeouts, circuit breakers, and mTLS out of application code and into the infrastructure layer (sidecar proxies like Envoy). Each team no longer needs to implement these patterns -- the mesh handles them transparently. This eliminates inconsistencies between teams and ensures uniform behavior. The trade-off is operational complexity (managing the mesh control plane), additional resource consumption (sidecar containers alongside every Pod), and added latency (traffic passes through the proxy). The overhead is justified when you have many services with complex communication patterns.
   </details>

2. **An engineer wants to deploy their application using GitOps with Argo CD. They commit a YAML change to Git, but the cluster does not update. A colleague suggests running `kubectl apply` directly to fix it. Why is this a bad idea in a GitOps workflow, and what should they do instead?**
   <details>
   <summary>Answer</summary>
   Direct `kubectl apply` violates the core GitOps principle: Git is the single source of truth. If you make changes directly to the cluster, Git and the cluster diverge. The next time Argo CD syncs, it will detect the drift and revert the manual change to match Git. The engineer should instead check why Argo CD is not syncing -- perhaps the Git webhook is not configured, the sync is paused, or there is a validation error in the YAML. The whole point of GitOps is that changes flow through Git, providing audit trails and the ability to revert via `git revert`.
   </details>

3. **A team manages PostgreSQL on Kubernetes by manually creating StatefulSets, Services, PVCs, ConfigMaps, and Secrets. When the primary database fails, a human must intervene to promote a replica. How would a Kubernetes Operator improve this, and what does "codifying operational knowledge" mean?**
   <details>
   <summary>Answer</summary>
   A PostgreSQL Operator (like Crunchy Data or Zalando's operator) uses a Custom Resource Definition to let you declare `kind: PostgresCluster` with desired replicas and version. The Operator's controller automatically creates all necessary resources (StatefulSet, Services, PVCs, Secrets) and -- critically -- handles failover automatically. When the primary fails, the Operator promotes a replica, updates the Service endpoint, and reconfigures replication without human intervention. "Codifying operational knowledge" means translating the steps a DBA would take during failover into automated controller logic that runs 24/7.
   </details>

4. **Your application processes uploaded images. Traffic is unpredictable -- sometimes 0 requests per hour, sometimes 10,000. Standard HPA has a minimum of 1 replica, so you are paying for an idle Pod most of the time. What CNCF project addresses this, and how does it differ from standard HPA?**
   <details>
   <summary>Answer</summary>
   KEDA (Kubernetes Event-Driven Autoscaler, CNCF Graduated) addresses this. Unlike standard HPA which scales based on Pod metrics like CPU and has a minimum of 1 replica, KEDA can scale to zero -- removing all Pods when there are no events (no images to process). When a new image is uploaded (triggering an event from a queue, HTTP request, or storage notification), KEDA creates Pods to handle the work. KEDA supports dozens of event sources beyond just CPU/memory. This eliminates the cost of idle Pods for bursty, event-driven workloads.
   </details>

5. **Your cluster hosts multiple teams, and you need to isolate them so Team A cannot see Team B's resources. You could create separate clusters per team or use namespaces within one cluster. What are the trade-offs of each approach, and what newer technology offers a middle ground?**
   <details>
   <summary>Answer</summary>
   Separate clusters provide the strongest isolation (completely independent control planes and etcd), but they are expensive and operationally complex (managing multiple clusters, distributing shared services). Namespace-based isolation is cheaper and simpler, but provides weaker isolation: it relies on RBAC, ResourceQuotas, and NetworkPolicies, and a misconfiguration could expose resources across namespaces. Virtual clusters (like vCluster) offer a middle ground: they create isolated "virtual" Kubernetes clusters inside a single physical cluster, each with its own virtual control plane, providing stronger isolation than namespaces but less overhead than separate clusters.
   </details>

---

## Summary

**Service Mesh**:
- Handles service-to-service communication
- mTLS, traffic management, observability
- Control plane + data plane (sidecars)
- Examples: Istio, Linkerd, Cilium

**Serverless**:
- Run code without managing servers
- Event-driven, scale to zero
- Pay per execution
- Kubernetes: Knative, OpenFaaS, KEDA

**GitOps**:
- Git = source of truth
- Agent pulls and reconciles
- Auditable, reversible
- Tools: Argo CD, Flux

**Operators**:
- Extend Kubernetes with CRDs
- Automate complex app management
- Codify operational knowledge

---

## Next Module

[Module 3.4: Observability Fundamentals](../module-3.4-observability-fundamentals/) - Understanding the three pillars of observability: metrics, logs, and traces.
