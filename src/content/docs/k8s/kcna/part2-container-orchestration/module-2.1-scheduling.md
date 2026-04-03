---
title: "Module 2.1: Scheduling"
slug: k8s/kcna/part2-container-orchestration/module-2.1-scheduling
sidebar:
  order: 2
---
> **Complexity**: `[MEDIUM]` - Orchestration concepts
>
> **Time to Complete**: 25-30 minutes
>
> **Prerequisites**: Part 1 (Kubernetes Fundamentals)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Explain** how the Kubernetes scheduler selects nodes using filtering and scoring
2. **Compare** scheduling mechanisms: nodeSelector, affinity, taints, and tolerations
3. **Identify** why a pod is pending based on scheduler constraints and resource availability
4. **Evaluate** scheduling strategies for different workload placement requirements

---

## Why This Module Matters

Scheduling is how Kubernetes decides where to run your Pods. Understanding scheduling concepts helps you predict where workloads will run and how to influence placement. KCNA tests your conceptual understanding of scheduling.

---

## What is Scheduling?

**Scheduling** is the process of assigning Pods to nodes:

```
┌─────────────────────────────────────────────────────────────┐
│              SCHEDULING OVERVIEW                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  New Pod Created                                           │
│       │                                                     │
│       │ No node assigned (spec.nodeName empty)             │
│       ▼                                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              KUBE-SCHEDULER                           │  │
│  │                                                       │  │
│  │  1. Filter: Which nodes CAN run this Pod?            │  │
│  │     • Enough resources?                               │  │
│  │     • Meets constraints?                              │  │
│  │                                                       │  │
│  │  2. Score: Which node is BEST?                       │  │
│  │     • Spread workloads                               │  │
│  │     • Image already present?                          │  │
│  │     • Custom priorities                               │  │
│  │                                                       │  │
│  │  3. Bind: Assign Pod to winning node                 │  │
│  └──────────────────────────────────────────────────────┘  │
│       │                                                     │
│       ▼                                                     │
│  Pod assigned to Node 2                                    │
│       │                                                     │
│       ▼                                                     │
│  kubelet on Node 2 runs the Pod                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Scheduling Process

### Step 1: Filtering

The scheduler eliminates nodes that can't run the Pod:

```
┌─────────────────────────────────────────────────────────────┐
│              FILTERING PHASE                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Pod requires:                                             │
│  • 2 CPU                                                   │
│  • 4GB memory                                              │
│  • nodeSelector: disk=ssd                                  │
│                                                             │
│  Nodes evaluated:                                          │
│  ─────────────────────────────────────────────────────────  │
│  Node 1: 1 CPU free      ✗ Not enough CPU                 │
│  Node 2: 4 CPU, 8GB      ✗ No disk=ssd label             │
│  Node 3: 3 CPU, 6GB, ssd ✓ Passes filters                │
│  Node 4: 4 CPU, 8GB, ssd ✓ Passes filters                │
│                                                             │
│  Feasible nodes: [Node 3, Node 4]                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: Scoring

The scheduler ranks feasible nodes:

```
┌─────────────────────────────────────────────────────────────┐
│              SCORING PHASE                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Scoring criteria:                                         │
│  ─────────────────────────────────────────────────────────  │
│  • LeastRequestedPriority: Prefer less utilized nodes     │
│  • BalancedResourceAllocation: Balance CPU/memory         │
│  • ImageLocality: Prefer nodes with image cached          │
│  • NodeAffinity: Match affinity preferences               │
│  • PodSpread: Spread Pods across failure domains          │
│                                                             │
│  Scoring example:                                          │
│  ─────────────────────────────────────────────────────────  │
│  Node 3: Score 75                                          │
│    • More utilized (-10)                                   │
│    • Image cached (+15)                                    │
│    • Balanced resources (+70)                              │
│                                                             │
│  Node 4: Score 85  ← Winner                               │
│    • Less utilized (+20)                                   │
│    • Image not cached (0)                                 │
│    • Well balanced (+65)                                  │
│                                                             │
│  Pod scheduled to Node 4                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Pause and predict**: The scheduler uses filtering and then scoring. Why not just pick the first node that passes filtering? What could go wrong if the scheduler always placed Pods on the same node that happens to be evaluated first?

## Node Selection Methods

### 1. nodeSelector

Simple label matching:

```yaml
# Pod spec
spec:
  nodeSelector:
    disk: ssd
    region: us-west

# Only nodes with BOTH labels are considered
```

### 2. Node Affinity

More expressive than nodeSelector:

```
┌─────────────────────────────────────────────────────────────┐
│              NODE AFFINITY                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Two types:                                                │
│                                                             │
│  requiredDuringSchedulingIgnoredDuringExecution:          │
│  • MUST match                                              │
│  • Pod won't schedule if no node matches                  │
│  • Like nodeSelector but more powerful                    │
│                                                             │
│  preferredDuringSchedulingIgnoredDuringExecution:         │
│  • PREFER to match                                         │
│  • Pod will schedule even if no match                     │
│  • Soft preference                                         │
│                                                             │
│  "IgnoredDuringExecution" means:                          │
│  • Labels checked only at scheduling time                 │
│  • If labels change later, Pod stays                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. Pod Affinity/Anti-Affinity

Place Pods relative to other Pods:

```
┌─────────────────────────────────────────────────────────────┐
│              POD AFFINITY / ANTI-AFFINITY                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  POD AFFINITY: "Schedule near other Pods"                  │
│  ─────────────────────────────────────────────────────────  │
│  "Run this cache Pod on same node as web Pod"             │
│                                                             │
│  ┌─────────────┐                                          │
│  │   Node 1    │                                          │
│  │ ┌────────┐  │                                          │
│  │ │ Web Pod│  │  ← Cache Pod wants to be here           │
│  │ └────────┘  │                                          │
│  │ ┌────────┐  │                                          │
│  │ │ Cache  │  │  ← Placed via affinity                  │
│  │ └────────┘  │                                          │
│  └─────────────┘                                          │
│                                                             │
│  POD ANTI-AFFINITY: "Schedule away from other Pods"       │
│  ─────────────────────────────────────────────────────────  │
│  "Spread replicas across different nodes"                 │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Node 1    │  │   Node 2    │  │   Node 3    │       │
│  │ ┌────────┐  │  │ ┌────────┐  │  │ ┌────────┐  │       │
│  │ │Web Pod │  │  │ │Web Pod │  │  │ │Web Pod │  │       │
│  │ │Replica1│  │  │ │Replica2│  │  │ │Replica3│  │       │
│  │ └────────┘  │  │ └────────┘  │  │ └────────┘  │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│                                                             │
│  Each replica on different node = high availability       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Taints and Tolerations

**Taints** repel Pods. **Tolerations** allow Pods to schedule on tainted nodes:

```
┌─────────────────────────────────────────────────────────────┐
│              TAINTS AND TOLERATIONS                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Node has taint:                                           │
│  gpu=true:NoSchedule                                       │
│  "Don't schedule regular Pods here"                        │
│                                                             │
│  Regular Pod:                    GPU Pod with toleration:  │
│  ┌──────────────┐               ┌──────────────┐          │
│  │ No toleration │               │ tolerations: │          │
│  └──────────────┘               │ - key: gpu   │          │
│        │                         │   value: true│          │
│        │                         │   effect:    │          │
│        ▼                         │   NoSchedule │          │
│  ┌─────────────┐                └──────────────┘          │
│  │ GPU Node    │                       │                   │
│  │ (tainted)   │                       ▼                   │
│  │             │  ✗ Repelled    ┌─────────────┐           │
│  │             │ ←─────────────  │Can schedule │ ✓         │
│  └─────────────┘                └─────────────┘           │
│                                                             │
│  Taint effects:                                            │
│  • NoSchedule: Don't schedule new Pods                    │
│  • PreferNoSchedule: Try to avoid, but allow if needed    │
│  • NoExecute: Evict existing Pods too                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Stop and think**: A node has a taint `gpu=true:NoSchedule`. You deploy a regular web application Pod without any tolerations. Will it run on that node? Now imagine a machine learning Pod that needs GPUs -- what would you add to its spec so it can be scheduled there?

## Resource Requests and Limits

Resources affect scheduling decisions:

```
┌─────────────────────────────────────────────────────────────┐
│              REQUESTS vs LIMITS                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  resources:                                                │
│    requests:         # Minimum guaranteed                  │
│      cpu: "500m"     # 0.5 CPU cores                      │
│      memory: "256Mi" # 256 MiB                            │
│    limits:           # Maximum allowed                     │
│      cpu: "1000m"    # 1 CPU core                         │
│      memory: "512Mi" # 512 MiB                            │
│                                                             │
│  REQUESTS:                                                 │
│  • Used by scheduler to find suitable nodes               │
│  • Node must have this much allocatable                   │
│  • Guaranteed to the container                            │
│                                                             │
│  LIMITS:                                                   │
│  • Maximum the container can use                          │
│  • CPU: Throttled if exceeded                             │
│  • Memory: OOMKilled if exceeded                          │
│                                                             │
│  Scheduling uses REQUESTS, not limits:                    │
│  "Can this node fit the requested resources?"             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Did You Know?

- **Scheduler is pluggable** - You can run custom schedulers or multiple schedulers in a cluster.

- **DaemonSets bypass normal scheduling** - They use their own controller to ensure one Pod per node.

- **Preemption** - If no node can fit a high-priority Pod, the scheduler can evict lower-priority Pods to make room.

- **Topology spread** - Kubernetes can spread Pods across zones, racks, or any topology domain for high availability.

---

## Common Mistakes

| Mistake | Why It Hurts | Correct Understanding |
|---------|--------------|----------------------|
| No resource requests | Scheduler can't make good decisions | Always set requests |
| Requests too high | Wasted resources | Match actual needs |
| Confusing affinity types | Pod might not schedule | required = must; preferred = try |
| Forgetting tolerations | Pods can't use tainted nodes | Add tolerations for special nodes |

---

## Quiz

1. **A Pod has been stuck in Pending state for 15 minutes. The events show "0/5 nodes are available: 2 Insufficient cpu, 3 node(s) had taint {gpu=true:NoSchedule}." What does this tell you about the cluster, and what are your options to get the Pod scheduled?**
   <details>
   <summary>Answer</summary>
   The scheduler evaluated all 5 nodes and rejected each one. Two nodes lack sufficient CPU to satisfy the Pod's resource requests. Three nodes have a GPU taint that the Pod does not tolerate. Options include: reducing the Pod's CPU request if the application can run with less, adding a toleration for the GPU taint if the Pod can run on GPU nodes, scaling down other workloads to free CPU, or adding new nodes. The event message tells you exactly which filter rejected each node.
   </details>

2. **Your team runs a critical database with 3 replicas. You notice all 3 Pods are running on the same node. If that node fails, all replicas go down simultaneously. How would you configure the Deployment to spread replicas across different nodes?**
   <details>
   <summary>Answer</summary>
   Use pod anti-affinity with `requiredDuringSchedulingIgnoredDuringExecution` to force each replica onto a different node. The anti-affinity rule would match Pods with the same app label and use `topologyKey: kubernetes.io/hostname` to ensure no two replicas share a node. Alternatively, you could use topology spread constraints for a more flexible approach. Without anti-affinity, the scheduler may co-locate Pods on the same node if that node scores highest.
   </details>

3. **A developer sets their Pod's resource requests to 4 CPU and 8GB memory "just to be safe," but the application actually uses 0.5 CPU and 1GB. What problem does this create for scheduling, and what Kubernetes feature could help right-size these values?**
   <details>
   <summary>Answer</summary>
   Over-requesting wastes cluster capacity. The scheduler uses requests (not actual usage) to place Pods, so 4 CPU of allocatable capacity is reserved on the node even though only 0.5 CPU is used. This means 3.5 CPU is wasted and unavailable for other Pods, potentially causing new Pods to stay Pending due to "insufficient CPU" even though the cluster is mostly idle. The Vertical Pod Autoscaler (VPA) can observe actual usage over time and recommend or automatically adjust requests to match real needs.
   </details>

4. **Your cluster has dedicated GPU nodes for machine learning workloads. You want to ensure regular web application Pods never get scheduled on these expensive GPU nodes. What Kubernetes mechanism would you use, and how does it work?**
   <details>
   <summary>Answer</summary>
   Apply a taint to the GPU nodes, for example `kubectl taint nodes gpu-node-1 gpu=true:NoSchedule`. This repels all Pods that do not have a matching toleration. Only ML workloads with the corresponding toleration (`key: gpu, value: "true", effect: NoSchedule`) in their Pod spec can be scheduled on those nodes. Regular web Pods will be filtered out during the scheduling phase and placed on other nodes. This prevents expensive GPU resources from being used by workloads that do not need them.
   </details>

5. **You want a Pod to prefer running in the us-west region but still be schedulable in us-east if us-west has no capacity. Would you use `requiredDuringSchedulingIgnoredDuringExecution` or `preferredDuringSchedulingIgnoredDuringExecution` for the node affinity rule? What happens with each option if us-west nodes are full?**
   <details>
   <summary>Answer</summary>
   Use `preferredDuringSchedulingIgnoredDuringExecution`. With "preferred," the scheduler will try to place the Pod on us-west nodes (giving them a higher score), but if no us-west nodes have capacity, the Pod still gets scheduled on us-east. With "required," the Pod would stay Pending indefinitely if us-west is full, because the scheduler treats it as a hard constraint that cannot be violated. The "preferred" option provides soft preference while maintaining availability.
   </details>

---

## Summary

**Scheduling process**:
1. Filter: Find feasible nodes
2. Score: Rank by preference
3. Bind: Assign to best node

**Node selection methods**:
- **nodeSelector**: Simple label matching
- **Node affinity**: Required or preferred rules
- **Pod affinity/anti-affinity**: Place relative to other Pods
- **Taints/tolerations**: Repel or allow specific Pods

**Resources**:
- Requests: Used by scheduler, guaranteed minimum
- Limits: Maximum allowed, enforced at runtime

---

## Next Module

[Module 2.2: Scaling](../module-2.2-scaling/) - How Kubernetes automatically scales applications.
