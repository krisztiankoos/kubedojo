---
title: "Module 1.5: Pods"
slug: k8s/kcna/part1-kubernetes-fundamentals/module-1.5-pods
sidebar:
  order: 6
---
> **Complexity**: `[MEDIUM]` - Core resource concept
>
> **Time to Complete**: 25-30 minutes
>
> **Prerequisites**: Modules 1.1-1.4

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Explain** what a Pod is and why it is the smallest deployable unit in Kubernetes
2. **Identify** when to use single-container vs. multi-container Pod patterns (sidecar, init)
3. **Compare** Pod lifecycle phases and understand what each status indicates
4. **Evaluate** whether a given scenario requires a standalone Pod or a higher-level workload resource

---

## Why This Module Matters

The Pod is the **most fundamental concept** in Kubernetes. Every workload runs in a Pod. KCNA will test your understanding of what Pods are, what they contain, and how they work.

---

## What is a Pod?

A **Pod** is the smallest deployable unit in Kubernetes:

```
┌─────────────────────────────────────────────────────────────┐
│              WHAT IS A POD?                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  A Pod is:                                                 │
│  • A group of one or more containers                       │
│  • The atomic unit of scheduling                           │
│  • Containers that share storage and network               │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                      POD                             │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │  Shared Network Namespace                      │  │   │
│  │  │  • All containers share same IP                │  │   │
│  │  │  • Containers communicate via localhost        │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  │                                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │ Container 1 │  │ Container 2 │                  │   │
│  │  │   (app)     │  │  (sidecar)  │                  │   │
│  │  └─────────────┘  └─────────────┘                  │   │
│  │                                                      │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │  Shared Storage (Volumes)                      │  │   │
│  │  │  • Both containers can access same files       │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Pods vs Containers

```
┌─────────────────────────────────────────────────────────────┐
│              POD vs CONTAINER                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Container:                    Pod:                        │
│  ─────────────────────────────────────────────────────────  │
│  • Single process              • One or more containers    │
│  • Runtime concept             • Kubernetes concept        │
│  • No shared context           • Shared network/storage    │
│  • Isolated                    • Co-located               │
│                                                             │
│  Analogy:                                                  │
│  ─────────────────────────────────────────────────────────  │
│  Container = Person                                        │
│  Pod = Apartment where people live together                │
│                                                             │
│  People in the same apartment:                             │
│  • Share the same address (IP)                            │
│  • Share kitchen and bathroom (volumes)                   │
│  • Can talk directly (localhost)                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Single-Container Pods

Most Pods have just one container:

```
┌─────────────────────────────────────────────────────────────┐
│              SINGLE-CONTAINER POD                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                      POD                             │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │           Main Application Container         │    │   │
│  │  │              (e.g., nginx)                   │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  This is the most common pattern:                          │
│  • One container per Pod                                   │
│  • Simple to manage                                        │
│  • Each Pod runs one instance of your app                  │
│                                                             │
│  "One-container-per-Pod" is the standard use case         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Pause and predict**: If a Pod is the smallest deployable unit and most Pods contain a single container, why didn't Kubernetes just make the container the smallest unit? What does the Pod abstraction give you that a bare container does not?

## Multi-Container Pods

Sometimes you need multiple containers in one Pod:

```
┌─────────────────────────────────────────────────────────────┐
│              MULTI-CONTAINER PATTERNS                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SIDECAR PATTERN                                           │
│  ─────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  POD                                                 │   │
│  │  ┌─────────────────┐  ┌─────────────────┐          │   │
│  │  │   Main App      │  │   Log Shipper   │          │   │
│  │  │   (writes logs) │─→│   (reads logs)  │          │   │
│  │  └─────────────────┘  └─────────────────┘          │   │
│  │               └────────────┘                        │   │
│  │                Shared volume                        │   │
│  └─────────────────────────────────────────────────────┘   │
│  Example: Main app + Fluentd sidecar for logging          │
│                                                             │
│  AMBASSADOR PATTERN                                        │
│  ─────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  POD                                                 │   │
│  │  ┌─────────────────┐  ┌─────────────────┐          │   │
│  │  │   Main App      │  │    Proxy        │          │   │
│  │  │   (localhost)   │─→│   (outbound)    │─→ External│   │
│  │  └─────────────────┘  └─────────────────┘          │   │
│  └─────────────────────────────────────────────────────┘   │
│  Example: App + Envoy proxy for service mesh              │
│                                                             │
│  ADAPTER PATTERN                                           │
│  ─────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  POD                                                 │   │
│  │  ┌─────────────────┐  ┌─────────────────┐          │   │
│  │  │   Main App      │  │    Adapter      │          │   │
│  │  │  (custom format)│─→│(standard format)│─→ Monitor │   │
│  │  └─────────────────┘  └─────────────────┘          │   │
│  └─────────────────────────────────────────────────────┘   │
│  Example: App + Prometheus exporter adapter               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Pod Networking

```
┌─────────────────────────────────────────────────────────────┐
│              POD NETWORKING                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Each Pod gets:                                            │
│  • Its own unique IP address                               │
│  • Can be reached directly by other Pods                   │
│  • Containers in Pod share this IP                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  POD (IP: 10.1.1.5)                                 │   │
│  │  ┌────────────┐    ┌────────────┐                  │   │
│  │  │Container A │    │Container B │                  │   │
│  │  │ Port 80    │    │ Port 8080  │                  │   │
│  │  └────────────┘    └────────────┘                  │   │
│  │         │                  │                        │   │
│  │         └────────┬─────────┘                        │   │
│  │                  │                                  │   │
│  │           localhost:80   localhost:8080             │   │
│  │           (within Pod)   (within Pod)              │   │
│  └─────────────────────────────────────────────────────┘   │
│                     │                                       │
│              10.1.1.5:80    10.1.1.5:8080                  │
│              (from outside Pod)                            │
│                                                             │
│  Within Pod: Use localhost                                 │
│  Between Pods: Use Pod IP                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Pod Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│              POD LIFECYCLE PHASES                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Pending ──────→ Running ──────→ Succeeded/Failed         │
│                                                             │
│  PENDING:                                                  │
│  • Pod accepted but not running yet                        │
│  • Waiting for scheduling                                  │
│  • Waiting for image pull                                  │
│                                                             │
│  RUNNING:                                                  │
│  • Pod bound to a node                                     │
│  • At least one container running                          │
│  • Or starting/restarting                                  │
│                                                             │
│  SUCCEEDED:                                                │
│  • All containers terminated successfully                  │
│  • Won't be restarted                                      │
│  • Common for Jobs                                         │
│                                                             │
│  FAILED:                                                   │
│  • All containers terminated                               │
│  • At least one failed (non-zero exit)                    │
│                                                             │
│  UNKNOWN:                                                  │
│  • Cannot get Pod state                                    │
│  • Usually communication error                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Pod Specification (Conceptual)

You don't need to memorize YAML for KCNA, but understand what a Pod contains:

```yaml
# Pod Specification - Key Parts
apiVersion: v1
kind: Pod
metadata:
  name: my-pod          # Pod name
  labels:               # Labels for selection
    app: web
spec:
  containers:           # List of containers
  - name: app           # Container name
    image: nginx:1.25   # Container image
    ports:              # Exposed ports
    - containerPort: 80
    resources:          # Resource limits
      limits:
        memory: "128Mi"
        cpu: "500m"
  volumes:              # Shared storage
  - name: data
    emptyDir: {}
```

**Key parts to understand**:
- **metadata**: Name and labels
- **spec.containers**: The containers to run
- **spec.volumes**: Shared storage

---

> **Stop and think**: In the sidecar pattern, a log shipper container runs alongside the main application. Why put them in the same Pod instead of separate Pods? What advantage does sharing the same network namespace and storage give you?

## Pod vs Deployment

```
┌─────────────────────────────────────────────────────────────┐
│              POD vs DEPLOYMENT                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Creating a Pod directly:                                  │
│  • Pod dies → It's gone                                    │
│  • No automatic restart                                    │
│  • No scaling                                              │
│  • Manual management                                       │
│                                                             │
│  Using a Deployment:                                       │
│  • Deployment manages Pods                                 │
│  • Pod dies → Deployment creates new one                  │
│  • Easy scaling (replicas: 3)                             │
│  • Rolling updates                                         │
│                                                             │
│  Rule of thumb:                                            │
│  ─────────────────────────────────────────────────────────  │
│  Almost NEVER create Pods directly                        │
│  Use Deployments, Jobs, DaemonSets instead                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Did You Know?

- **Pods are ephemeral** - They're designed to be disposable. When a Pod dies, it's gone forever (even with the same name, it's a new Pod).

- **The pause container** - Every Pod has a hidden "pause" container that holds network namespaces. Application containers join its namespace.

- **Pod IP is internal** - Pod IPs are only routable within the cluster. You can't reach them from outside without a Service.

- **Pods have unique names** - In a namespace, Pod names must be unique. Deployments add random suffixes (e.g., nginx-7b8d6c-xk4dz).

---

## Common Mistakes

| Mistake | Why It Hurts | Correct Understanding |
|---------|--------------|----------------------|
| "Pod = Container" | Missing Pod abstraction | Pod contains container(s) |
| "Pods have multiple IPs" | Misunderstanding networking | One IP per Pod, shared by containers |
| "Create Pods directly" | No resilience | Use Deployments instead |
| "Pods persist after deletion" | Treating as VMs | Pods are ephemeral |

---

## Quiz

1. **Your application writes logs to a file on disk. You want to ship those logs to a centralized logging system. Would you run the log shipper as a separate Pod or in the same Pod as the application? Explain your reasoning.**
   <details>
   <summary>Answer</summary>
   Run the log shipper in the same Pod as the application using the sidecar pattern. This way both containers share the same volume, so the log shipper can read the application's log files directly. If they were in separate Pods, they would have different storage and network namespaces, making it much harder to share files. The sidecar container also follows the same lifecycle as the application -- it starts and stops together, ensuring no logs are missed.
   </details>

2. **A junior developer creates a Pod directly using `kubectl run` for a production web service. The Pod crashes overnight and is not restarted. What went wrong, and what should they have used instead?**
   <details>
   <summary>Answer</summary>
   Pods created directly are not managed by any controller. When a standalone Pod crashes, nothing recreates it -- it is gone permanently. The developer should have created a Deployment, which manages Pods through a ReplicaSet. If a managed Pod crashes, the ReplicaSet controller detects that the current state does not match the desired state and creates a new Pod automatically. Deployments also provide scaling, rolling updates, and rollback capabilities that standalone Pods lack entirely.
   </details>

3. **Two containers in the same Pod need to communicate. One runs a web server on port 8080 and the other runs a metrics exporter on port 9090. How do they reach each other, and how would an external Pod reach either of them?**
   <details>
   <summary>Answer</summary>
   Within the same Pod, containers share a network namespace, so they reach each other via localhost -- the web server calls `localhost:9090` for metrics, and the exporter calls `localhost:8080` for the web server. From an external Pod, both containers are reached using the Pod's single IP address: `<pod-ip>:8080` for the web server and `<pod-ip>:9090` for the exporter. The key insight is that containers in a Pod share one IP but must use different ports, just like processes on the same machine.
   </details>

4. **Your team debates whether to put a Redis cache in the same Pod as the application that uses it, or in a separate Pod. What are the trade-offs, and which approach would you recommend?**
   <details>
   <summary>Answer</summary>
   Putting Redis in the same Pod means they always run together on the same node with low-latency localhost communication, but they cannot scale independently -- if the application needs 5 replicas, you get 5 Redis instances. Running Redis in a separate Pod (via its own Deployment or StatefulSet) allows independent scaling, independent lifecycle management, and the ability for multiple application Pods to share one Redis instance via a Service. The separate Pod approach is almost always better because Redis and the application have different scaling and persistence requirements.
   </details>

5. **A Pod has status "Running" but the application inside is not responding to HTTP requests. The Pod has not restarted. What might explain this situation, and what Kubernetes feature could prevent it?**
   <details>
   <summary>Answer</summary>
   The container process is alive (so the Pod stays "Running") but the application logic is stuck, deadlocked, or in an error state. Without health checks, Kubernetes only knows the process is running, not whether it is functioning correctly. Readiness probes would solve this: a readiness probe checks a specific endpoint or port, and if it fails, Kubernetes removes the Pod from Service endpoints so it stops receiving traffic. A liveness probe would go further by restarting the container if the application becomes unresponsive.
   </details>

---

## Summary

**Pods are**:
- The smallest deployable unit
- One or more containers
- Shared network (same IP)
- Shared storage (volumes)

**Key characteristics**:
- Each Pod has unique IP
- Containers communicate via localhost
- Pods are ephemeral (not persistent)
- Usually managed by Deployments

**Multi-container patterns**:
- Sidecar (helper alongside main)
- Ambassador (proxy for outbound)
- Adapter (format conversion)

---

## Next Module

[Module 1.6: Workload Resources](../module-1.6-workload-resources/) - Deployments, ReplicaSets, and other controllers that manage Pods.