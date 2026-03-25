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

1. **What two phases does the scheduler use?**
   <details>
   <summary>Answer</summary>
   Filtering (which nodes CAN run the Pod) and Scoring (which node is BEST). After these, the Pod is bound to the winning node.
   </details>

2. **What's the difference between nodeSelector and node affinity?**
   <details>
   <summary>Answer</summary>
   nodeSelector is simple label matching (must have exact labels). Node affinity is more expressive with required/preferred rules and operators like In, NotIn, Exists.
   </details>

3. **What does a taint do?**
   <details>
   <summary>Answer</summary>
   A taint repels Pods from scheduling on a node. Only Pods with matching tolerations can schedule on tainted nodes.
   </details>

4. **Are resource requests or limits used for scheduling?**
   <details>
   <summary>Answer</summary>
   Requests. The scheduler checks if a node has enough allocatable resources to satisfy the Pod's requests. Limits are enforced at runtime.
   </details>

5. **What is pod anti-affinity used for?**
   <details>
   <summary>Answer</summary>
   Spreading Pods across nodes/zones. For example, ensuring replicas of a Deployment run on different nodes for high availability.
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

[Module 2.2: Scaling](module-2.2-scaling/) - How Kubernetes automatically scales applications.
