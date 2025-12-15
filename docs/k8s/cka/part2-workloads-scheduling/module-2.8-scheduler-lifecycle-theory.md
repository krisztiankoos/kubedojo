# Module 2.8: Scheduler & Pod Lifecycle Theory

> **Complexity**: `[MEDIUM]` - High exam yield
>
> **Time to Complete**: 25-35 minutes
>
> **Prerequisites**: Module 2.5 (Resource Management), Module 2.6 (Scheduling)

---

## Outline
- Why the scheduler behaves the way it does (filter → score → bind)
- How QoS, requests/limits, and priority influence placement and evictions
- Pod lifecycle signals: grace periods, disruption budgets, preemption
- Eviction manager decisions under resource pressure

---

## Scheduler Decision Flow
- **Filter (Predicates)**: Node readiness, taints/tolerations, node selector/affinity, volumes (attach/mount), resource requests vs. allocatable.
- **Score (Priorities)**: Spreads across topology domains, balances CPU/memory usage, respects soft preferences (`preferredDuringScheduling...`), and considers PodTopologySpread.
- **Bind**: Writes a Binding object to the API server; kubelet then pulls images and starts containers.

> **Exam tip**: If a pod is Pending, check events for "0/3 nodes are available" and the specific filter that failed (taints, volume attach, insufficient CPU).

## Priority, Preemption, and PDBs
- **Pod Priority**: Higher-priority pods can preempt lower ones to free capacity. Define via `priorityClassName`.
- **Preemption**: Scheduler selects victim pods on candidate nodes, evicts them, then binds the high-priority pod. PDBs can block preemption; the pod stays Pending.
- **Three-way interaction**: `priorityClass` + `PodDisruptionBudget` + taints/tolerations determine whether critical pods displace others or remain blocked.

## QoS and Resource Guarantees
- **Guaranteed**: Requests == limits for all containers; last to be evicted under memory pressure.
- **Burstable**: Requests set, limits optional; middle priority during eviction.
- **BestEffort**: No requests or limits; first evicted.
- **Scheduling impact**: Requests drive bin-packing; limits do not. Overcommitting limits does not block scheduling but can throttle at runtime.

## Evictions and Node Pressure
- **Kubelet eviction manager** watches signals: `memory.available`, `nodefs.available`, `imagefs.available`, PID pressure.
- **Soft vs. hard thresholds**: Soft includes grace periods; hard is immediate.
- **Outcomes**: Pod is terminated with a reason (`Evicted`), not rescheduled on the same node; controller recreates it elsewhere.

## Pod Lifecycle Highlights
- **Termination sequence**: PreStop hook (if any) → SIGTERM → grace period countdown → SIGKILL after timeout → volumes detached.
- **Grace periods**: Default 30s; set `terminationGracePeriodSeconds`. For critical services, pair with readiness probes to drop traffic early.
- **Disruptions**: Voluntary (drain, upgrade, preemption) honor PDBs; involuntary (OOMKill, node pressure) do not. Always specify desired disruption policy via PDB where SLOs matter.
