---
title: "Module 1.6: Workload Resources"
slug: k8s/kcna/part1-kubernetes-fundamentals/module-1.6-workload-resources
sidebar:
  order: 7
---
> **Complexity**: `[MEDIUM]` - Core resource concepts
>
> **Time to Complete**: 30-35 minutes
>
> **Prerequisites**: Module 1.5 (Pods)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Compare** Deployments, ReplicaSets, DaemonSets, StatefulSets, and Jobs by use case
2. **Identify** which workload resource to use for a given application scenario
3. **Explain** how Deployments manage rolling updates and rollbacks through ReplicaSets
4. **Evaluate** the relationship between controllers and the Pods they manage

---

## Why This Module Matters

You rarely create Pods directly—you use **workload resources** that manage Pods for you. Understanding Deployments, ReplicaSets, DaemonSets, and other controllers is essential for KCNA.

---

## The Workload Resource Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│              WORKLOAD RESOURCE HIERARCHY                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  You create:         Deployment                            │
│                           │                                 │
│                           │ creates & manages               │
│                           ▼                                 │
│  Auto-created:       ReplicaSet                            │
│                           │                                 │
│                           │ creates & manages               │
│                           ▼                                 │
│  Auto-created:    Pod    Pod    Pod                        │
│                                                             │
│  Why this hierarchy?                                       │
│  ─────────────────────────────────────────────────────────  │
│  • Deployment: Handles updates and rollbacks               │
│  • ReplicaSet: Maintains desired number of Pods            │
│  • Pod: Runs the actual containers                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployments

The **Deployment** is the most common way to run applications:

```
┌─────────────────────────────────────────────────────────────┐
│              DEPLOYMENT                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  What it does:                                             │
│  ─────────────────────────────────────────────────────────  │
│  • Declaratively manages ReplicaSets and Pods              │
│  • Provides rolling updates                                 │
│  • Supports rollbacks                                       │
│  • Scales applications up/down                             │
│                                                             │
│  Example:                                                  │
│  ─────────────────────────────────────────────────────────  │
│  "I want 3 replicas of nginx:1.25"                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Deployment: nginx                                   │   │
│  │  replicas: 3                                         │   │
│  │  image: nginx:1.25                                   │   │
│  │                                                      │   │
│  │  └─→ ReplicaSet: nginx-7b8d6c                       │   │
│  │       │                                              │   │
│  │       ├─→ Pod: nginx-7b8d6c-abc12                   │   │
│  │       ├─→ Pod: nginx-7b8d6c-def34                   │   │
│  │       └─→ Pod: nginx-7b8d6c-ghi56                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  When to use: Stateless applications                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Rolling Updates

```
┌─────────────────────────────────────────────────────────────┐
│              ROLLING UPDATE                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Update from nginx:1.25 to nginx:1.26:                    │
│                                                             │
│  Step 1: Create new ReplicaSet                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Old RS (nginx:1.25): ●●●  (3 pods)                 │   │
│  │  New RS (nginx:1.26): ○    (1 pod starting)         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Step 2: Scale new up, old down                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Old RS (nginx:1.25): ●●   (2 pods)                 │   │
│  │  New RS (nginx:1.26): ○○   (2 pods)                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Step 3: Complete                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Old RS (nginx:1.25):      (0 pods, kept for rollback)│  │
│  │  New RS (nginx:1.26): ○○○  (3 pods)                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Benefits:                                                 │
│  • Zero downtime                                           │
│  • Gradual rollout                                         │
│  • Automatic rollback on failure                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ReplicaSets

A **ReplicaSet** maintains a stable set of replica Pods:

```
┌─────────────────────────────────────────────────────────────┐
│              REPLICASET                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  What it does:                                             │
│  ─────────────────────────────────────────────────────────  │
│  • Ensures specified number of Pods are running            │
│  • Creates new Pods if too few                             │
│  • Deletes Pods if too many                                │
│  • Uses labels to identify Pods it owns                    │
│                                                             │
│  Example:                                                  │
│  ─────────────────────────────────────────────────────────  │
│  ReplicaSet wants: 3 pods                                  │
│  Currently: 2 pods                                         │
│  Action: Create 1 more pod                                 │
│                                                             │
│  ReplicaSet wants: 3 pods                                  │
│  Currently: 4 pods                                         │
│  Action: Delete 1 pod                                      │
│                                                             │
│  Important:                                                │
│  ─────────────────────────────────────────────────────────  │
│  You rarely create ReplicaSets directly!                  │
│  Use Deployments—they manage ReplicaSets for you.         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Pause and predict**: Deployments create ReplicaSets, which create Pods. Why this three-level hierarchy? What would you lose if Deployments created Pods directly without the ReplicaSet layer in between?

## StatefulSets

For **stateful applications** that need stable identities:

```
┌─────────────────────────────────────────────────────────────┐
│              STATEFULSET                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  What it provides:                                         │
│  ─────────────────────────────────────────────────────────  │
│  • Stable, unique network identifiers                      │
│  • Stable, persistent storage                              │
│  • Ordered, graceful deployment and scaling                │
│  • Ordered, graceful deletion and termination              │
│                                                             │
│  Example: Database cluster                                 │
│  ─────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  StatefulSet: mysql                                  │   │
│  │                                                      │   │
│  │  mysql-0  ──→ PVC: mysql-data-0  (10GB)            │   │
│  │  mysql-1  ──→ PVC: mysql-data-1  (10GB)            │   │
│  │  mysql-2  ──→ PVC: mysql-data-2  (10GB)            │   │
│  │                                                      │   │
│  │  DNS: mysql-0.mysql.default.svc.cluster.local      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Key differences from Deployment:                          │
│  • Pods get persistent names (mysql-0, mysql-1)           │
│  • Each Pod gets its own PVC                               │
│  • Created in order (0, then 1, then 2)                   │
│                                                             │
│  When to use: Databases, clustered apps, ordered startup  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## DaemonSets

For running a Pod on **every node**:

```
┌─────────────────────────────────────────────────────────────┐
│              DAEMONSET                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  What it does:                                             │
│  ─────────────────────────────────────────────────────────  │
│  • Runs one Pod per node                                   │
│  • Automatically adds Pod when new node joins              │
│  • Removes Pod when node leaves                            │
│                                                             │
│  Example: Log collector                                    │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │ Node 1  │  │ Node 2  │  │ Node 3  │  │ Node 4  │      │
│  │┌───────┐│  │┌───────┐│  │┌───────┐│  │┌───────┐│      │
│  ││fluent-││  ││fluent-││  ││fluent-││  ││fluent-││      │
│  ││  bit  ││  ││  bit  ││  ││  bit  ││  ││  bit  ││      │
│  │└───────┘│  │└───────┘│  │└───────┘│  │└───────┘│      │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
│                                                             │
│  Common use cases:                                         │
│  • Log collectors (Fluentd, Fluent Bit)                   │
│  • Monitoring agents (Prometheus Node Exporter)           │
│  • Network plugins (CNI)                                   │
│  • Storage drivers                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Jobs and CronJobs

For **batch and scheduled workloads**:

```
┌─────────────────────────────────────────────────────────────┐
│              JOB                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  What it does:                                             │
│  • Creates Pods that run to completion                     │
│  • Retries if Pod fails                                    │
│  • Tracks successful completions                           │
│                                                             │
│  Example: Database backup                                  │
│  Job "backup" → Creates Pod → Pod runs backup → Completes │
│                                                             │
│  Options:                                                  │
│  • completions: 5  (run 5 times total)                    │
│  • parallelism: 2  (run 2 at a time)                      │
│  • backoffLimit: 3 (retry 3 times on failure)             │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              CRONJOB                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  What it does:                                             │
│  • Creates Jobs on a schedule                              │
│  • Uses cron syntax                                        │
│                                                             │
│  Example: Nightly backup                                   │
│  schedule: "0 2 * * *"  # Every day at 2 AM              │
│                                                             │
│  ┌──────┐    ┌──────┐    ┌──────┐                        │
│  │ Day 1│    │ Day 2│    │ Day 3│                        │
│  │ 2 AM │    │ 2 AM │    │ 2 AM │                        │
│  │  ↓   │    │  ↓   │    │  ↓   │                        │
│  │ Job  │    │ Job  │    │ Job  │                        │
│  └──────┘    └──────┘    └──────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Workload Resource Comparison

| Resource | Purpose | Pod Identity | Replicas |
|----------|---------|--------------|----------|
| **Deployment** | Stateless apps | Random names | Variable |
| **ReplicaSet** | Maintain count | Random names | Fixed |
| **StatefulSet** | Stateful apps | Stable names | Ordered |
| **DaemonSet** | Per-node agent | Per node | One per node |
| **Job** | Run to completion | Temporary | Until done |
| **CronJob** | Scheduled Jobs | Temporary | Per schedule |

---

> **Stop and think**: A database cluster needs Pods with stable network identities (e.g., mysql-0, mysql-1, mysql-2) that persist across restarts. Why can't a regular Deployment provide this? What would happen to a database replication setup if Pod names were random?

## When to Use What?

```
┌─────────────────────────────────────────────────────────────┐
│              CHOOSING A WORKLOAD RESOURCE                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Is it a one-time task?                                    │
│  └─→ YES: Job                                              │
│                                                             │
│  Does it need to run on a schedule?                        │
│  └─→ YES: CronJob                                          │
│                                                             │
│  Does it need to run on every node?                        │
│  └─→ YES: DaemonSet                                        │
│                                                             │
│  Does it need stable identity and storage?                 │
│  └─→ YES: StatefulSet                                      │
│                                                             │
│  Is it a stateless application?                            │
│  └─→ YES: Deployment (most common!)                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Did You Know?

- **Deployments keep old ReplicaSets** - By default, Kubernetes keeps 10 old ReplicaSets to enable rollback. This is configurable.

- **StatefulSet Pods are created sequentially** - Pod-0 must be running before Pod-1 is created. This ensures ordered startup.

- **DaemonSets bypass the scheduler** - Originally, DaemonSets placed Pods directly. Now they use the scheduler by default.

- **CronJob time zone is controller-manager's time** - Be careful about time zones when scheduling CronJobs.

---

## Common Mistakes

| Mistake | Why It Hurts | Correct Understanding |
|---------|--------------|----------------------|
| Creating ReplicaSets directly | Lose update features | Use Deployments |
| Using Deployment for databases | Lose data on reschedule | Use StatefulSet |
| Manual scaling | No automation | Use HPA or set replicas |
| Ignoring Job failures | Silent errors | Check completions and status |

---

## Quiz

1. **Your team needs to run a PostgreSQL database cluster on Kubernetes with three replicas that maintain their data across restarts. A colleague suggests using a Deployment. Why would this not work, and what resource should they use instead?**
   <details>
   <summary>Answer</summary>
   A Deployment would not work because its Pods get random names (e.g., postgres-7b8d6c-abc12) that change on restart, and all Pods share the same storage configuration. A PostgreSQL cluster needs stable identities (postgres-0 is always the primary, postgres-1 and postgres-2 are replicas) and each Pod needs its own persistent volume. A StatefulSet provides both: stable, predictable Pod names, individual PersistentVolumeClaims per Pod, and ordered startup/shutdown so the primary starts before replicas.
   </details>

2. **You need to collect logs from every node in your cluster using Fluent Bit. New nodes are added weekly as the cluster scales. Which workload resource ensures Fluent Bit runs on every node, including new ones, without manual intervention?**
   <details>
   <summary>Answer</summary>
   A DaemonSet is the right choice. It ensures exactly one Pod runs on every node in the cluster. When a new node joins, the DaemonSet automatically schedules a Fluent Bit Pod on it. When a node is removed, the DaemonSet's Pod is cleaned up. This is the standard pattern for per-node agents like log collectors, monitoring exporters, and CNI plugins. Using a Deployment would not guarantee one Pod per node and could place multiple Pods on some nodes while leaving others without any.
   </details>

3. **Your application needs to run a database migration script once before a new version is deployed. The script takes about 5 minutes and should not run again if it succeeds. Which workload resource fits this requirement, and why?**
   <details>
   <summary>Answer</summary>
   A Job is the right resource. Jobs create Pods that run to completion -- the Pod executes the migration script, exits with code 0 on success, and is not restarted. If the Pod fails, the Job retries based on the backoffLimit setting. Unlike a Deployment (which would keep restarting the migration forever) or a standalone Pod (which provides no retry mechanism), a Job tracks completions and ensures the task finishes successfully exactly the required number of times.
   </details>

4. **During a rolling update, you change the image tag in a Deployment from nginx:1.25 to nginx:1.26. Kubernetes creates a new ReplicaSet. After the update completes, the old ReplicaSet still exists with 0 replicas. Why does Kubernetes keep it instead of deleting it?**
   <details>
   <summary>Answer</summary>
   Kubernetes keeps old ReplicaSets to enable rollbacks. If the new version has problems, you can run `kubectl rollout undo` and Kubernetes will scale the old ReplicaSet back up and scale the new one down, reverting to the previous version without needing to redeploy. By default, Kubernetes retains the last 10 ReplicaSets (configurable via revisionHistoryLimit). Each old ReplicaSet represents a previous version of your application that you can quickly roll back to.
   </details>

5. **Your company runs nightly data processing jobs at 2 AM and weekly report generation every Monday at 6 AM. How would you implement this in Kubernetes, and what happens if a Monday job overlaps with the nightly job?**
   <details>
   <summary>Answer</summary>
   Use two CronJobs: one with schedule "0 2 * * *" for the nightly job and one with "0 6 * * 1" for the weekly report. Each CronJob creates a Job at its scheduled time, and each Job creates Pods that run to completion. If both run simultaneously on Monday, they execute independently as separate Jobs on the cluster -- Kubernetes schedules both sets of Pods normally. The CronJob resource also has concurrencyPolicy settings (Allow, Forbid, Replace) to control what happens if a previous run has not finished when the next one is scheduled.
   </details>

---

## Summary

**Workload resources manage Pods**:

| Resource | Use Case |
|----------|----------|
| **Deployment** | Stateless apps (web servers, APIs) |
| **StatefulSet** | Stateful apps (databases, caches) |
| **DaemonSet** | Per-node agents (logging, monitoring) |
| **Job** | One-time tasks (backups, migrations) |
| **CronJob** | Scheduled tasks (nightly jobs) |

**Key hierarchy**:
- Deployment → ReplicaSet → Pods
- You create Deployment
- K8s creates the rest

**Best practice**: Almost never create Pods or ReplicaSets directly. Use higher-level resources.

---

## Next Module

[Module 1.7: Services](../module-1.7-services/) - How Pods are exposed and discovered within and outside the cluster.
