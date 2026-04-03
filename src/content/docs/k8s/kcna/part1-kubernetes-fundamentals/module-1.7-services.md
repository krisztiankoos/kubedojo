---
title: "Module 1.7: Services"
slug: k8s/kcna/part1-kubernetes-fundamentals/module-1.7-services
sidebar:
  order: 8
---
> **Complexity**: `[MEDIUM]` - Core networking concept
>
> **Time to Complete**: 25-30 minutes
>
> **Prerequisites**: Modules 1.5, 1.6

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Explain** why Services are needed and how they provide stable endpoints for Pods
2. **Compare** ClusterIP, NodePort, LoadBalancer, and ExternalName Service types
3. **Identify** how label selectors connect Services to their backing Pods
4. **Trace** how DNS resolution works for Service discovery within a cluster

---

## Why This Module Matters

Pods come and go—their IPs change constantly. **Services** provide stable endpoints to access Pods. Understanding Services is critical for KCNA and for understanding how Kubernetes networking works.

---

## The Problem Services Solve

```
┌─────────────────────────────────────────────────────────────┐
│              THE PROBLEM WITH POD IPs                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Without Services:                                         │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Time T1:                                                  │
│  Frontend → 10.1.1.5 (backend pod)  ✓ Works               │
│                                                             │
│  Time T2: Backend pod dies, new one created                │
│  Frontend → 10.1.1.5  ✗ Dead                              │
│  New backend pod has IP: 10.1.1.9                          │
│                                                             │
│  Problem:                                                  │
│  • Pod IPs are ephemeral                                   │
│  • Clients can't track changing IPs                        │
│  • No load balancing across replicas                       │
│                                                             │
│  With Services:                                            │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Frontend → backend-service (stable) → Backend pods       │
│                                                             │
│  Service provides:                                         │
│  • Stable IP and DNS name                                  │
│  • Automatic discovery of healthy Pods                    │
│  • Load balancing                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## What is a Service?

A **Service** is an abstraction that defines a logical set of Pods and a policy to access them:

```
┌─────────────────────────────────────────────────────────────┐
│              SERVICE CONCEPT                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                                                       │ │
│  │    Client                                             │ │
│  │       │                                               │ │
│  │       │ Request to my-service:80                      │ │
│  │       ▼                                               │ │
│  │  ┌──────────────────────────────────────────┐        │ │
│  │  │            SERVICE                        │        │ │
│  │  │  Name: my-service                        │        │ │
│  │  │  IP: 10.96.45.23 (stable ClusterIP)     │        │ │
│  │  │  Port: 80                                │        │ │
│  │  │  Selector: app=backend                   │        │ │
│  │  └──────────────────────────────────────────┘        │ │
│  │       │                                               │ │
│  │       │ Load balanced to matching Pods               │ │
│  │       ▼                                               │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐              │ │
│  │  │  Pod    │  │  Pod    │  │  Pod    │              │ │
│  │  │app=back │  │app=back │  │app=back │              │ │
│  │  │10.1.1.5 │  │10.1.1.6 │  │10.1.1.7 │              │ │
│  │  └─────────┘  └─────────┘  └─────────┘              │ │
│  │                                                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Service uses LABELS to find Pods                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Pause and predict**: If Pod IPs change every time a Pod restarts, how would a frontend application reliably communicate with a backend that has 3 replicas? What mechanism would you need to abstract away the changing IPs?

## Service Types

### 1. ClusterIP (Default)

```
┌─────────────────────────────────────────────────────────────┐
│              CLUSTERIP SERVICE                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  • Internal cluster IP only                                │
│  • Not accessible from outside cluster                     │
│  • Default type                                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   CLUSTER                            │   │
│  │                                                      │   │
│  │   Frontend Pod ──→ backend-svc ──→ Backend Pods    │   │
│  │                    (ClusterIP)                      │   │
│  │                    10.96.0.50                       │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  External: ✗ Cannot reach 10.96.0.50                      │
│                                                             │
│  Use case: Internal services (databases, caches, APIs)    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. NodePort

```
┌─────────────────────────────────────────────────────────────┐
│              NODEPORT SERVICE                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  • Exposes Service on each node's IP at a static port      │
│  • Port range: 30000-32767                                 │
│  • Accessible from outside cluster                         │
│                                                             │
│  External: http://node-ip:30080                           │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Node 1 (:30080)  Node 2 (:30080)  Node 3 (:30080) │   │
│  │       │               │               │             │   │
│  │       └───────────────┼───────────────┘             │   │
│  │                       │                              │   │
│  │                       ▼                              │   │
│  │              ┌─────────────┐                        │   │
│  │              │   Service   │                        │   │
│  │              │  NodePort   │                        │   │
│  │              └─────────────┘                        │   │
│  │                       │                              │   │
│  │              ┌────────┼────────┐                    │   │
│  │              ▼        ▼        ▼                    │   │
│  │            Pod      Pod      Pod                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Use case: Development, testing, simple external access   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. LoadBalancer

```
┌─────────────────────────────────────────────────────────────┐
│              LOADBALANCER SERVICE                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  • Provisions external load balancer (cloud provider)      │
│  • Gets external IP address                                │
│  • Most common for production external access              │
│                                                             │
│  External: http://203.0.113.50                            │
│       │                                                     │
│       ▼                                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Cloud Load Balancer (ELB, GLB, etc.)         │  │
│  │                 203.0.113.50                          │  │
│  └──────────────────────────────────────────────────────┘  │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Node 1          Node 2          Node 3             │   │
│  │    │               │               │                │   │
│  │    ▼               ▼               ▼                │   │
│  │  Pod             Pod             Pod                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Use case: Production external access in cloud            │
│  Note: Costs money in cloud environments!                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4. ExternalName

```
┌─────────────────────────────────────────────────────────────┐
│              EXTERNALNAME SERVICE                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  • Maps Service to external DNS name                       │
│  • No proxying—returns CNAME record                       │
│  • No selector (no Pods)                                   │
│                                                             │
│  Pod → my-database → database.example.com                 │
│                                                             │
│  Use case: Accessing external services with internal name │
│  Example: External database, SaaS services                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Service Type Comparison

| Type | Internal | External | Use Case |
|------|----------|----------|----------|
| **ClusterIP** | ✓ | ✗ | Internal communication |
| **NodePort** | ✓ | ✓ (via node IP) | Development/testing |
| **LoadBalancer** | ✓ | ✓ (via LB IP) | Production external |
| **ExternalName** | ✓ | N/A | External DNS mapping |

---

## Service Discovery

Kubernetes provides two ways to discover Services:

### 1. DNS (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│              DNS-BASED DISCOVERY                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Every Service gets a DNS entry:                           │
│                                                             │
│  <service-name>.<namespace>.svc.cluster.local              │
│                                                             │
│  Examples:                                                 │
│  ─────────────────────────────────────────────────────────  │
│  backend.default.svc.cluster.local                        │
│  database.production.svc.cluster.local                    │
│  redis.cache.svc.cluster.local                            │
│                                                             │
│  Shortcuts (within same namespace):                        │
│  ─────────────────────────────────────────────────────────  │
│  backend                    (same namespace)               │
│  backend.default            (namespace specified)          │
│  backend.default.svc        (svc added)                   │
│                                                             │
│  Pod can just use: http://backend:80                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. Environment Variables

```
┌─────────────────────────────────────────────────────────────┐
│              ENVIRONMENT VARIABLE DISCOVERY                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Kubernetes injects environment variables into Pods:       │
│                                                             │
│  For Service "backend" on port 80:                        │
│  ─────────────────────────────────────────────────────────  │
│  BACKEND_SERVICE_HOST=10.96.45.23                         │
│  BACKEND_SERVICE_PORT=80                                   │
│  BACKEND_PORT=tcp://10.96.45.23:80                        │
│                                                             │
│  Limitation:                                               │
│  Service must exist BEFORE Pod is created                 │
│  (DNS doesn't have this limitation)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Stop and think**: A LoadBalancer Service creates an external cloud load balancer, which costs money. If you have 10 microservices that all need external access, would you create 10 LoadBalancer Services? What alternative approach might reduce cost while still routing external HTTP traffic to the right service?

## Endpoints

Services use **Endpoints** to track Pod IPs:

```
┌─────────────────────────────────────────────────────────────┐
│              ENDPOINTS                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Service: backend                                          │
│  Selector: app=backend                                     │
│                                                             │
│       │                                                     │
│       │ Kubernetes finds matching Pods                     │
│       ▼                                                     │
│                                                             │
│  Endpoints: backend                                        │
│  Addresses:                                                │
│    - 10.1.1.5:8080                                        │
│    - 10.1.1.6:8080                                        │
│    - 10.1.1.7:8080                                        │
│                                                             │
│  When Pods change, Endpoints update automatically         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Did You Know?

- **ClusterIP is virtual** - The ClusterIP doesn't actually exist on any interface. It's handled by kube-proxy rules that redirect traffic.

- **LoadBalancer includes NodePort** - When you create a LoadBalancer Service, you also get a ClusterIP and NodePort automatically.

- **Headless Services** - Setting `clusterIP: None` creates a headless Service that returns Pod IPs directly via DNS (useful for StatefulSets).

- **Services are namespace-scoped** - A Service in namespace "dev" can only directly select Pods in "dev" namespace.

---

## Common Mistakes

| Mistake | Why It Hurts | Correct Understanding |
|---------|--------------|----------------------|
| Using Pod IPs directly | IPs change | Use Services for stable access |
| LoadBalancer everywhere | Expensive, wasteful | Use Ingress for HTTP routing |
| Wrong selector labels | Service finds no Pods | Labels must match exactly |
| Expecting external IP for ClusterIP | Won't work | Use NodePort or LoadBalancer |

---

## Quiz

1. **Your frontend Deployment connects to a backend using the backend Pod's IP address directly. After a routine update, the backend Pods are recreated with new IPs and the frontend can no longer reach them. What went wrong, and how should the frontend discover the backend?**
   <details>
   <summary>Answer</summary>
   Pod IPs are ephemeral -- they change every time a Pod is recreated. The frontend should connect through a Service, which provides a stable ClusterIP and DNS name (e.g., `backend.default.svc.cluster.local`). The Service uses label selectors to automatically track the current Pod IPs via Endpoints, so even when Pods are replaced, the Service routes traffic correctly.
   </details>

2. **A developer creates a Service with selector `app: web`, but no Pods are receiving traffic. When they run `kubectl get endpoints`, the list is empty. What is the most likely cause?**
   <details>
   <summary>Answer</summary>
   The Pods do not have a matching label. The Service selector `app: web` must exactly match a label on the Pods. Common causes include a typo in the label key or value (e.g., `app: Web` vs `app: web`), the Pods being in a different namespace, or the Pods not having the label at all. Check the Pod labels with `kubectl get pods --show-labels` and compare against the Service selector.
   </details>

3. **Your team runs a Kubernetes cluster on-premises with no cloud provider. A colleague wants to expose an application externally using a LoadBalancer Service. What will happen, and what alternative would you suggest?**
   <details>
   <summary>Answer</summary>
   Without a cloud provider, a LoadBalancer Service will stay in "Pending" state indefinitely because there is no cloud controller to provision an external load balancer. Alternatives include using a NodePort Service (accessible via any node's IP on a port in the 30000-32767 range), installing a bare-metal load balancer like MetalLB, or using an Ingress controller with NodePort to handle HTTP routing.
   </details>

4. **A microservices application has a frontend in the `web` namespace and a database in the `data` namespace. The frontend tries to connect to `postgres:5432` but gets a DNS resolution error. What is wrong, and how should the frontend reference the database Service?**
   <details>
   <summary>Answer</summary>
   Short DNS names like `postgres` only resolve within the same namespace. Since the frontend is in the `web` namespace and the database Service is in the `data` namespace, the frontend must use the fully qualified name: `postgres.data.svc.cluster.local` (or at minimum `postgres.data`). Services are namespace-scoped, and DNS resolution requires specifying the target namespace when communicating across namespace boundaries.
   </details>

5. **Your StatefulSet runs a 3-node database cluster where each replica has a different role (primary, replica-1, replica-2). A regular ClusterIP Service would load-balance across all three, but clients need to connect to specific instances. What type of Service would solve this problem?**
   <details>
   <summary>Answer</summary>
   A headless Service (with `clusterIP: None`) solves this. Instead of providing a single virtual IP with load balancing, a headless Service returns the individual Pod IPs via DNS. Combined with a StatefulSet, each Pod gets a predictable DNS name (e.g., `db-0.db-svc.default.svc.cluster.local`), allowing clients to connect directly to the primary or a specific replica by name.
   </details>

---

## Summary

**Services provide**:
- Stable IP and DNS name
- Load balancing across Pods
- Service discovery

**Service types**:

| Type | Access | Use Case |
|------|--------|----------|
| **ClusterIP** | Internal only | Backend services |
| **NodePort** | Via node IP:port | Testing |
| **LoadBalancer** | Via cloud LB | Production external |
| **ExternalName** | DNS alias | External services |

**Discovery methods**:
- DNS: `service.namespace.svc.cluster.local` (preferred)
- Environment variables (legacy)

---

## Next Module

[Module 1.8: Namespaces and Labels](../module-1.8-namespaces-labels/) - Organizing and selecting resources in Kubernetes.
