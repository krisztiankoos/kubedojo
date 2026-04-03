---
title: "Module 2.2: Scaling"
slug: k8s/kcna/part2-container-orchestration/module-2.2-scaling
sidebar:
  order: 3
---
> **Complexity**: `[MEDIUM]` - Orchestration concepts
>
> **Time to Complete**: 25-30 minutes
>
> **Prerequisites**: Module 2.1 (Scheduling)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Compare** Horizontal Pod Autoscaler, Vertical Pod Autoscaler, and Cluster Autoscaler
2. **Explain** how HPA uses metrics to make scaling decisions
3. **Identify** which scaling approach fits a given workload pattern (CPU-bound, memory-bound, event-driven)
4. **Evaluate** trade-offs between over-provisioning and autoscaling for cost and reliability

---

## Why This Module Matters

One of Kubernetes' superpowers is automatic scaling—adding or removing resources based on demand. Understanding scaling concepts helps you design applications that handle variable workloads efficiently. KCNA tests your understanding of scaling mechanisms.

---

## Types of Scaling

```
┌─────────────────────────────────────────────────────────────┐
│              SCALING DIMENSIONS                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  HORIZONTAL SCALING (scale out/in)                         │
│  ─────────────────────────────────────────────────────────  │
│  Add/remove Pod replicas                                   │
│                                                             │
│  Before:  [Pod] [Pod] [Pod]                               │
│  After:   [Pod] [Pod] [Pod] [Pod] [Pod]                   │
│                                                             │
│  VERTICAL SCALING (scale up/down)                          │
│  ─────────────────────────────────────────────────────────  │
│  Increase/decrease Pod resources                           │
│                                                             │
│  Before:  [Pod: 1 CPU, 1GB]                               │
│  After:   [Pod: 2 CPU, 2GB]                               │
│                                                             │
│  CLUSTER SCALING                                           │
│  ─────────────────────────────────────────────────────────  │
│  Add/remove nodes from the cluster                         │
│                                                             │
│  Before:  [Node 1] [Node 2]                               │
│  After:   [Node 1] [Node 2] [Node 3]                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Horizontal Pod Autoscaler (HPA)

The **HPA** automatically scales the number of Pod replicas:

```
┌─────────────────────────────────────────────────────────────┐
│              HORIZONTAL POD AUTOSCALER                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  How it works:                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  1. HPA monitors metrics (CPU, memory, custom)            │
│  2. Compares to target threshold                           │
│  3. Calculates desired replicas                            │
│  4. Scales Deployment up or down                          │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                                                       │ │
│  │   Metrics Server ──→ HPA Controller                   │ │
│  │   "CPU at 80%"        │                               │ │
│  │                       │                               │ │
│  │                       ▼                               │ │
│  │              Target: 50% CPU                          │ │
│  │              Current: 80% CPU                         │ │
│  │              Current replicas: 2                      │ │
│  │              Desired: 2 × (80/50) ≈ 4                │ │
│  │                       │                               │ │
│  │                       ▼                               │ │
│  │              Scale Deployment to 4 replicas           │ │
│  │                                                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Formula (simplified):                                     │
│  desiredReplicas = currentReplicas × (currentMetric /     │
│                                        targetMetric)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### HPA Configuration (Conceptual)

```yaml
# Key HPA settings to understand:
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2        # Never scale below this
  maxReplicas: 10       # Never scale above this
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50  # Target 50% CPU
```

> **Pause and predict**: HPA scales based on average CPU utilization. If your target is 50% and current average is 80% with 2 replicas, how many replicas will HPA create? What happens when the traffic spike ends and CPU drops to 20%?

### HPA Metrics Types

| Type | Description | Example |
|------|-------------|---------|
| **Resource** | CPU, memory utilization | 50% CPU average |
| **Pods** | Custom metrics from Pods | Requests per second |
| **Object** | Metrics from other objects | Queue length |
| **External** | Metrics outside cluster | Cloud metrics |

---

## Vertical Pod Autoscaler (VPA)

The **VPA** automatically adjusts resource requests and limits:

```
┌─────────────────────────────────────────────────────────────┐
│              VERTICAL POD AUTOSCALER                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  How it works:                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  1. VPA observes actual resource usage over time          │
│  2. Recommends optimal requests/limits                     │
│  3. Can automatically update Pods (recreates them)        │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                                                       │ │
│  │   Pod starts with:          VPA observes:            │ │
│  │   requests:                  Actual usage:            │ │
│  │     cpu: 100m                 cpu: 400m               │ │
│  │     memory: 128Mi             memory: 512Mi           │ │
│  │                                                       │ │
│  │                    ↓                                  │ │
│  │                                                       │ │
│  │   VPA recommends:                                     │ │
│  │   requests:                                           │ │
│  │     cpu: 500m                                         │ │
│  │     memory: 600Mi                                     │ │
│  │                                                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Modes:                                                    │
│  • Off: Just recommendations, no action                   │
│  • Initial: Set on Pod creation only                      │
│  • Auto: Update running Pods (requires restart)          │
│                                                             │
│  Note: VPA is NOT built into Kubernetes core              │
│  It's an add-on component                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Cluster Autoscaler

The **Cluster Autoscaler** adds or removes nodes:

```
┌─────────────────────────────────────────────────────────────┐
│              CLUSTER AUTOSCALER                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SCALE UP: Add nodes when Pods can't be scheduled         │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Pods pending (unschedulable)                       │   │
│  │         │                                           │   │
│  │         ▼                                           │   │
│  │  Cluster Autoscaler detects pending Pods           │   │
│  │         │                                           │   │
│  │         ▼                                           │   │
│  │  Requests new node from cloud provider             │   │
│  │         │                                           │   │
│  │         ▼                                           │   │
│  │  New node joins cluster                            │   │
│  │         │                                           │   │
│  │         ▼                                           │   │
│  │  Pending Pods get scheduled                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  SCALE DOWN: Remove underutilized nodes                   │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Node has low utilization for X minutes            │   │
│  │         │                                           │   │
│  │         ▼                                           │   │
│  │  CA checks if Pods can move elsewhere              │   │
│  │         │                                           │   │
│  │         ▼                                           │   │
│  │  Drains node (moves Pods)                          │   │
│  │         │                                           │   │
│  │         ▼                                           │   │
│  │  Removes node from cloud                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Works with: AWS Auto Scaling, GCP MIG, Azure VMSS       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Scaling Comparison

| Aspect | HPA | VPA | Cluster Autoscaler |
|--------|-----|-----|-------------------|
| **What scales** | Pod count | Pod resources | Node count |
| **Direction** | Horizontal | Vertical | Horizontal |
| **Trigger** | Metrics threshold | Usage patterns | Unschedulable Pods |
| **Built-in** | Yes | No (add-on) | No (add-on) |
| **Downtime** | No | Yes (Pod restart) | No |

---

> **Stop and think**: The Cluster Autoscaler adds nodes when Pods are Pending, but adding a new cloud VM takes several minutes. What happens to your users during those minutes? How could you design your system to handle this delay?

## Manual Scaling

You can also scale manually:

```
┌─────────────────────────────────────────────────────────────┐
│              MANUAL SCALING                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Scale Deployment:                                         │
│  kubectl scale deployment nginx --replicas=5               │
│                                                             │
│  Scale ReplicaSet:                                         │
│  kubectl scale rs nginx-abc123 --replicas=5                │
│                                                             │
│  Scale StatefulSet:                                        │
│  kubectl scale statefulset mysql --replicas=3              │
│                                                             │
│  Or edit the resource:                                     │
│  kubectl edit deployment nginx                             │
│  # Change spec.replicas                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Scaling Best Practices

```
┌─────────────────────────────────────────────────────────────┐
│              SCALING BEST PRACTICES                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. SET RESOURCE REQUESTS                                  │
│     • HPA needs metrics to work                            │
│     • Cluster Autoscaler needs requests for capacity      │
│                                                             │
│  2. SET APPROPRIATE MIN/MAX                                │
│     • minReplicas: Ensure availability                    │
│     • maxReplicas: Control costs                          │
│                                                             │
│  3. USE POD DISRUPTION BUDGETS                            │
│     • Prevent too many Pods going down during scaling     │
│                                                             │
│  4. CONSIDER SCALING SPEED                                 │
│     • HPA has cooldown periods                             │
│     • Cluster Autoscaler takes minutes for new nodes      │
│                                                             │
│  5. DON'T MIX HPA AND VPA ON SAME DEPLOYMENT              │
│     • They can conflict                                    │
│     • Choose one or the other                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Did You Know?

- **HPA cooldown** - By default, HPA waits 3 minutes before scaling down to prevent thrashing.

- **Metrics Server required** - HPA needs Metrics Server installed to get CPU/memory metrics.

- **Custom metrics** - HPA can scale on custom metrics like HTTP requests, queue depth, or any Prometheus metric.

- **KEDA** - Kubernetes Event-Driven Autoscaler is a CNCF project that extends HPA with more event sources.

---

## Common Mistakes

| Mistake | Why It Hurts | Correct Understanding |
|---------|--------------|----------------------|
| No resource requests | HPA can't calculate utilization | Always set requests |
| Min replicas = 1 | Single point of failure | Use minReplicas >= 2 |
| Scaling on wrong metric | Ineffective scaling | Match metric to bottleneck |
| Ignoring scale-down time | Costs remain high | Configure appropriate cooldown |

---

## Quiz

1. **Your web application experiences a traffic spike every morning at 9 AM when users log in. Currently, a human operator manually scales the Deployment each morning. Which Kubernetes autoscaler would you use to automate this, and what metric would you target?**
   <details>
   <summary>Answer</summary>
   Use the Horizontal Pod Autoscaler (HPA) targeting CPU utilization or custom metrics like requests-per-second. HPA monitors average CPU utilization across all Pods in the Deployment and automatically adds replicas when usage exceeds the target (e.g., 50%). When the morning spike subsides and CPU drops, HPA scales back down after a cooldown period. This eliminates the need for manual intervention while keeping the application responsive during peak traffic.
   </details>

2. **A developer sets their Deployment's resource requests to 100m CPU and 128Mi memory, but VPA observes the application actually uses 500m CPU and 512Mi memory. What happens to the application without VPA's intervention, and what would VPA recommend?**
   <details>
   <summary>Answer</summary>
   Without VPA, the application is under-provisioned. It will be CPU-throttled (running slower than it could) and may be OOMKilled when memory usage exceeds the 128Mi limit. VPA would recommend increasing requests to approximately 500m CPU and 600Mi memory (with some buffer above observed usage). In "Auto" mode, VPA would recreate Pods with updated resource requests. This prevents throttling and OOMKills while also giving the scheduler accurate information for placement decisions.
   </details>

3. **Your HPA is configured with `minReplicas: 1` and targets 50% CPU utilization. During a brief traffic spike, it scales from 1 to 8 replicas. Once traffic drops, all 8 replicas are nearly idle. An outage occurs because the single remaining Pod after scale-down cannot handle a sudden request burst. What configuration would you change?**
   <details>
   <summary>Answer</summary>
   Set `minReplicas` to at least 2 (preferably 3) to eliminate the single point of failure. With only 1 minimum replica, the application has no redundancy during low-traffic periods, and any sudden spike must wait for HPA to detect the load increase and for new Pods to start -- which takes at least a few seconds. Keeping 2-3 minimum replicas provides both high availability and some buffer capacity to absorb initial traffic increases before HPA adds more replicas.
   </details>

4. **Your cluster runs in AWS. HPA has scaled a Deployment to 50 Pods, but only 3 nodes exist and they are all at capacity. New Pods are stuck in Pending. What component detects this situation and what does it do?**
   <details>
   <summary>Answer</summary>
   The Cluster Autoscaler detects Pending Pods that cannot be scheduled due to insufficient resources. It requests new EC2 instances from the AWS Auto Scaling Group to add nodes to the cluster. Once the new nodes register with the cluster and become Ready, the scheduler places the Pending Pods on them. This process typically takes 2-5 minutes depending on the instance type and AMI. HPA and Cluster Autoscaler work together: HPA scales Pods, and Cluster Autoscaler ensures there are enough nodes to run them.
   </details>

5. **A colleague configures both HPA (targeting CPU) and VPA (in Auto mode) on the same Deployment. After a few hours, the Deployment oscillates wildly between 2 and 20 replicas. What is causing this, and how would you fix it?**
   <details>
   <summary>Answer</summary>
   HPA and VPA are conflicting. VPA increases CPU requests (say from 100m to 500m), which changes the denominator in HPA's utilization calculation. With higher requests, the same actual CPU usage appears as a lower percentage, so HPA scales down. With fewer replicas, each Pod gets more load, VPA observes higher usage and may adjust again, and the cycle repeats. The fix is to not use both on the same Deployment for CPU. Either use HPA for horizontal scaling or VPA for right-sizing, but not both on the same resource metric. You can use VPA in "Off" mode just for recommendations while HPA handles scaling.
   </details>

---

## Summary

**Scaling types**:
- **Horizontal (HPA)**: Add/remove Pods
- **Vertical (VPA)**: Change Pod resources
- **Cluster**: Add/remove nodes

**HPA**:
- Scales based on metrics (CPU, memory, custom)
- Built into Kubernetes
- No downtime

**VPA**:
- Right-sizes resource requests
- Add-on component
- Requires Pod restart

**Cluster Autoscaler**:
- Adds nodes for pending Pods
- Removes underutilized nodes
- Cloud provider integration

---

## Next Module

[Module 2.3: Storage Orchestration](../module-2.3-storage/) - How Kubernetes manages persistent storage.
