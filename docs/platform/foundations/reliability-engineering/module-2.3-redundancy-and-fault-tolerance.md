# Module 2.3: Redundancy and Fault Tolerance

> **Complexity**: `[MEDIUM]`
>
> **Time to Complete**: 30-35 minutes
>
> **Prerequisites**: [Module 2.2: Failure Modes and Effects](module-2.2-failure-modes-and-effects.md)
>
> **Track**: Foundations

---

## Why This Module Matters

You've identified how your system can fail. Now, how do you keep it working when those failures happen?

The answer is **redundancy**—having more than one of critical components so that when one fails, another can take over. But redundancy isn't just "add more servers." Done wrong, it adds complexity without adding reliability. Done right, it lets your system survive failures that would otherwise cause outages.

This module teaches you to think about redundancy as an engineering discipline: when to use it, how to implement it, and the trade-offs involved.

> **The Airplane Analogy**
>
> Commercial aircraft have redundant everything: multiple engines, multiple hydraulic systems, multiple flight computers, multiple pilots. But it's not just duplication—each redundant system is designed to be independent. Separate power sources, separate wiring paths, separate maintenance schedules. The goal isn't just "more," it's "independent."

---

## What You'll Learn

- Types of redundancy and when to use each
- The difference between high availability and fault tolerance
- Active-passive vs. active-active architectures
- Common redundancy patterns in distributed systems
- The hidden costs and risks of redundancy

---

## Part 1: Understanding Redundancy

### 1.1 What is Redundancy?

**Redundancy** is having extra components beyond the minimum required for normal operation, so the system can continue if some components fail.

```
REDUNDANCY BASICS
═══════════════════════════════════════════════════════════════

NO REDUNDANCY (Single Point of Failure)
────────────────────────────────────────
    Request ──▶ [Service] ──▶ Response
                    │
                If fails → Outage

WITH REDUNDANCY
────────────────────────────────────────
                ┌─────────┐
    Request ──▶ │Service A│ ──▶ Response
                └────┬────┘
                     │ fails
                ┌────▼────┐
                │Service B│ ──▶ Response (continued)
                └─────────┘
```

### 1.2 Types of Redundancy

| Type | Description | Example |
|------|-------------|---------|
| **Hardware redundancy** | Multiple physical components | RAID arrays, dual power supplies |
| **Software redundancy** | Multiple service instances | 3 replicas of a pod |
| **Data redundancy** | Multiple copies of data | Database replication |
| **Geographic redundancy** | Multiple locations | Multi-region deployment |
| **Temporal redundancy** | Retry over time | Automatic retry with backoff |
| **Informational redundancy** | Extra data for validation | Checksums, parity bits |

### 1.3 Redundancy Notation: N+M

Redundancy is often expressed as N+M:
- **N** = minimum needed for normal operation
- **M** = extra for failure tolerance

```
REDUNDANCY NOTATION
═══════════════════════════════════════════════════════════════

N+0: No redundancy
    [A] → If A fails, outage

N+1: One spare
    [A] [B] → Either can handle the load alone
    Survives 1 failure

N+2: Two spares
    [A] [B] [C] → Any two can handle the load
    Survives 2 failures

2N: Full duplication
    [A₁] [A₂] → Complete duplicate system
    [B₁] [B₂]   Often in different locations
```

> **Gotcha: N+1 Isn't Always Enough**
>
> N+1 protects against single failures, but what about during maintenance? If you have 3 servers (N+1 where N=2) and take one down for updates, you're now at N+0. If another fails, you're down. Consider N+2 for critical systems to allow for maintenance + one unexpected failure.

---

## Part 2: High Availability vs. Fault Tolerance

### 2.1 The Distinction

These terms are often used interchangeably, but they're different:

| Aspect | High Availability (HA) | Fault Tolerance (FT) |
|--------|------------------------|----------------------|
| Goal | Minimize downtime | Zero downtime |
| During failure | Brief interruption okay | No interruption |
| Data loss | May lose in-flight data | No data loss |
| Cost | Moderate | High |
| Complexity | Moderate | High |
| Use case | Most web services | Financial, medical, aviation |

```
HIGH AVAILABILITY vs FAULT TOLERANCE
═══════════════════════════════════════════════════════════════

HIGH AVAILABILITY
────────────────────────────────────────────────────────────
Time: ──────────────────────────────────────────────────────▶

      Normal      Failure   Recovery   Normal
      ████████████ ▒▒▒▒▒▒▒▒ ████████████████████████████
                   ↑
              Brief outage (seconds to minutes)
              In-flight requests may fail

FAULT TOLERANCE
────────────────────────────────────────────────────────────
Time: ──────────────────────────────────────────────────────▶

      Normal      Failure   (seamless)   Normal
      █████████████████████████████████████████████████████
                   ↑
              No visible outage
              In-flight requests succeed
```

### 2.2 When to Use Which

**High Availability is usually sufficient when:**
- Brief outages are acceptable
- Retrying failed requests is okay
- Cost matters
- Simpler architecture is valuable

**Fault Tolerance is required when:**
- Any downtime is unacceptable
- Transactions can't be retried
- Legal/regulatory requirements
- Lives depend on the system

> **Try This (2 minutes)**
>
> Classify these systems—do they need HA or FT?
>
> | System | HA or FT? | Why? |
> |--------|-----------|------|
> | Blog | | |
> | Online banking | | |
> | Aircraft control | | |
> | E-commerce checkout | | |
> | Pacemaker | | |

---

## Part 3: Redundancy Architectures

### 3.1 Active-Passive (Standby)

One component handles traffic; others wait to take over.

```
ACTIVE-PASSIVE
═══════════════════════════════════════════════════════════════

NORMAL OPERATION
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│    Traffic ──▶ [Active: Primary] ──▶ Response              │
│                                                             │
│                [Passive: Standby] ← (idle, syncing)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

AFTER FAILOVER
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                [Failed: Primary] ✗                         │
│                                                             │
│    Traffic ──▶ [Now Active: Standby] ──▶ Response          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Characteristics:**
- Simpler to implement
- Standby capacity is "wasted" during normal operation
- Failover takes time (seconds to minutes)
- Risk: Standby may have stale data or config

**Use when:**
- Cost is a concern
- You can tolerate brief failover time
- Traffic doesn't justify multiple active instances

### 3.2 Active-Active (Load Shared)

All components handle traffic simultaneously.

```
ACTIVE-ACTIVE
═══════════════════════════════════════════════════════════════

NORMAL OPERATION
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                ┌──▶ [Active: Node A] ──┐                   │
│                │                        │                   │
│    Traffic ──▶ LB                       ├──▶ Response       │
│                │                        │                   │
│                └──▶ [Active: Node B] ──┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

AFTER NODE A FAILS
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                     [Failed: Node A] ✗                     │
│                                                             │
│    Traffic ──▶ LB ──▶ [Active: Node B] ──▶ Response        │
│                                                             │
│    (All traffic now handled by B; may need to scale)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Characteristics:**
- All capacity is used during normal operation
- No failover time—traffic immediately routes away from failed node
- More complex (need to handle shared state)
- Better resource utilization

**Use when:**
- Traffic justifies multiple instances
- You need instant failover
- Workload can be distributed

### 3.3 Comparison

| Aspect | Active-Passive | Active-Active |
|--------|----------------|---------------|
| Resource usage | ~50% (standby idle) | ~100% |
| Failover time | Seconds to minutes | Instant |
| Complexity | Lower | Higher |
| State management | Sync to standby | Distributed state |
| Scaling | Limited | Horizontal |
| Cost efficiency | Lower | Higher |

> **Did You Know?**
>
> Most cloud load balancers use active-active architecture internally. AWS ELB, for example, runs across multiple availability zones with all nodes active. When one fails, traffic is simply not sent there—no failover needed because there's no single "active" node.

---

## Part 4: Redundancy Patterns

### 4.1 Database Replication

```
DATABASE REPLICATION PATTERNS
═══════════════════════════════════════════════════════════════

PRIMARY-REPLICA (Read Scaling)
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│    Writes ──▶ [Primary] ──sync──▶ [Replica 1]              │
│                   │                                         │
│                   └───sync──▶ [Replica 2]                  │
│                                                             │
│    Reads ───▶ [Any Replica] ──▶ Response                   │
│                                                             │
│    + Read scalability                                       │
│    - Single write point, replication lag                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

MULTI-PRIMARY (Write Scaling)
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│    Writes ──▶ [Primary A] ◀──sync──▶ [Primary B]           │
│                                                             │
│    + Write scalability                                      │
│    - Conflict resolution complexity                        │
│    - Harder to reason about consistency                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Kubernetes Redundancy

```
KUBERNETES POD REDUNDANCY
═══════════════════════════════════════════════════════════════

Deployment: replicas: 3

┌──────────────────────────────────────────────────────────┐
│  Node 1           Node 2           Node 3               │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐         │
│  │  Pod A  │      │  Pod B  │      │  Pod C  │         │
│  └─────────┘      └─────────┘      └─────────┘         │
└──────────────────────────────────────────────────────────┘

                          │
                    Service (LB)
                          │
                     ┌────┴────┐
                     │ Traffic │
                     └─────────┘

If Pod A fails:
- Kubernetes detects via health check
- Traffic routes to B and C
- New pod scheduled automatically
```

```yaml
# Kubernetes deployment with redundancy
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 3                    # N+2 redundancy
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1          # Always keep 2 running
      maxSurge: 1
  template:
    spec:
      affinity:
        podAntiAffinity:         # Spread across nodes
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: api-server
            topologyKey: kubernetes.io/hostname
      containers:
      - name: api
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
        livenessProbe:           # Detect failures
          httpGet:
            path: /health
            port: 8080
          periodSeconds: 10
        readinessProbe:          # Route traffic only when ready
          httpGet:
            path: /ready
            port: 8080
          periodSeconds: 5
```

### 4.3 Multi-Region Redundancy

```
MULTI-REGION ARCHITECTURE
═══════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│                        Global DNS                           │
│                    (Route53, CloudFlare)                    │
│                           │                                 │
│           ┌───────────────┼───────────────┐                │
│           │               │               │                 │
│           ▼               ▼               ▼                 │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│    │ Region A │    │ Region B │    │ Region C │           │
│    │ (US-East)│    │ (EU-West)│    │ (AP-SE)  │           │
│    │          │    │          │    │          │           │
│    │ [App]    │    │ [App]    │    │ [App]    │           │
│    │ [DB Pri] │◀──▶│ [DB Rep] │◀──▶│ [DB Rep] │           │
│    │          │    │          │    │          │           │
│    └──────────┘    └──────────┘    └──────────┘           │
│                                                             │
│    Benefits:                                                │
│    - Survive entire region failure                         │
│    - Lower latency for global users                        │
│    - Disaster recovery                                      │
│                                                             │
│    Challenges:                                              │
│    - Cross-region data replication lag                     │
│    - Complexity of distributed state                       │
│    - Cost (3x infrastructure)                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.4 Circuit Breaker Pattern

Not traditional redundancy, but enables graceful handling when redundancy fails:

```
CIRCUIT BREAKER
═══════════════════════════════════════════════════════════════

States:
┌─────────┐     failures > threshold     ┌─────────┐
│ CLOSED  │ ─────────────────────────▶  │  OPEN   │
│(normal) │                              │(failing)│
└─────────┘                              └────┬────┘
     ▲                                        │
     │                                   timeout
     │         ┌──────────┐                  │
     └─────────│HALF-OPEN │◀─────────────────┘
    success    │ (testing)│
               └──────────┘
                    │
               failure → back to OPEN

Implementation:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Request ──▶ Circuit Breaker ──▶ Service                  │
│                     │                                       │
│               (if OPEN)                                     │
│                     │                                       │
│                     └──▶ Fallback Response                 │
│                         (cached data, default, error)      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **Try This (3 minutes)**
>
> Your service calls a payment provider. Design the circuit breaker:
>
> - After how many failures should it open?
> - How long before trying again (half-open)?
> - What's the fallback response?

---

## Part 5: The Costs of Redundancy

### 5.1 Redundancy Isn't Free

```
THE COSTS OF REDUNDANCY
═══════════════════════════════════════════════════════════════

FINANCIAL COSTS
─────────────────────────────────────────────────────────────
- 2x or 3x infrastructure costs
- Cross-region data transfer fees
- Additional monitoring/management tools
- More complex debugging (more places to look)

COMPLEXITY COSTS
─────────────────────────────────────────────────────────────
- More moving parts = more failure modes
- State synchronization challenges
- Split-brain scenarios
- Harder to reason about behavior

OPERATIONAL COSTS
─────────────────────────────────────────────────────────────
- More deployments to manage
- More configuration to keep in sync
- More capacity planning complexity
- Testing redundancy (does failover actually work?)
```

### 5.2 Common Redundancy Failures

| Failure | What Happens | Prevention |
|---------|--------------|------------|
| **Correlated failure** | Both primary and backup fail together | Independent failure domains |
| **Split brain** | Both think they're primary | Proper leader election, fencing |
| **Replication lag** | Backup has stale data | Monitor lag, consider sync replication |
| **Untested failover** | Failover doesn't work when needed | Regular failover drills |
| **Config drift** | Backup has different config | Infrastructure as code, sync config |

### 5.3 The Redundancy Paradox

> **Did You Know?**
>
> Adding redundancy can sometimes *decrease* reliability. More components means more things that can fail. If the redundancy mechanism itself is complex, it adds failure modes. A 2013 study found that ~30% of failures at large internet companies involved failure of the failover mechanism itself.

```
THE REDUNDANCY PARADOX
═══════════════════════════════════════════════════════════════

Simple system:
    Component A ─── Reliability: 99%

"More reliable" with redundancy:
    Component A ───┐
                   ├─── Failover Logic ─── Output
    Component B ───┘

    A reliability: 99%
    B reliability: 99%
    Failover reliability: 95%

    System reliability = P(A works) + P(A fails) × P(failover works) × P(B works)
                      = 0.99 + 0.01 × 0.95 × 0.99
                      = 0.99 + 0.0094
                      = 99.94%

    But if failover has bugs...

    Failover reliability: 50% (untested, has bugs)
    System reliability = 0.99 + 0.01 × 0.50 × 0.99 = 99.49%

    WORSE than no redundancy!
```

**Lesson**: Redundancy only helps if the failover mechanism is reliable. Test it regularly.

> **War Story: The Backup That Wasn't**
>
> A financial services company had "highly available" PostgreSQL: a primary with streaming replication to a standby. They were proud of their architecture diagrams. They never tested failover.
>
> When the primary failed, they triggered manual failover. The standby came up—with a 6-hour replication lag. Transactions from the last 6 hours were gone. It turned out monitoring had been alerting on lag for months, but the alerts went to a distribution list nobody read.
>
> Recovery took 3 days: restore from backup, replay transaction logs, reconcile with payment processors, apologize to customers. The CEO learned what "replication lag" means the hard way.
>
> Now they run failover drills monthly. They verify replication lag every deploy. And someone actually reads the alerts.

---

## Did You Know?

- **RAID 5 lost data** at major companies because the rebuild process (after one disk failed) stressed the remaining disks, causing a second failure before rebuild completed. RAID 6 (which tolerates two failures) is now recommended for large arrays.

- **The DNS root servers** use Anycast—the same IP address is announced from multiple locations. Your request goes to the nearest one. If one fails, routing protocols automatically send you elsewhere. No failover logic needed.

- **Google's Borg** (precursor to Kubernetes) was designed around the assumption that machines will fail. Jobs are automatically rescheduled when machines die. Google expects ~1% of machines to fail per year, so redundancy isn't optional—it's the default.

- **The "Pets vs. Cattle" metaphor** for servers was coined by Bill Baker at Microsoft. Pets have names, are irreplaceable, and get nursed back to health when sick. Cattle have numbers, are identical, and get replaced when sick. Modern cloud-native redundancy assumes cattle: any instance is expendable.

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Same failure domain | Both replicas fail together | Spread across zones/regions |
| Not testing failover | Failover doesn't work | Regular chaos engineering |
| Sync replication everywhere | Performance impact | Use async where eventual consistency okay |
| Ignoring replication lag | Read your own writes fails | Read from primary after write |
| No health checks | Traffic sent to failed node | Implement proper health checks |
| Manual failover | Slow recovery | Automate failover |

---

## Quiz

1. **What does N+2 redundancy mean, and why might you choose it over N+1?**
   <details>
   <summary>Answer</summary>

   N+2 means having two spare components beyond the minimum needed for normal operation.

   Why N+2 over N+1:
   - **Maintenance**: With N+1, if you take one component down for maintenance, you're at N+0. Another failure causes an outage. N+2 allows maintenance + one unexpected failure.
   - **Rolling updates**: During deployment, you temporarily have one fewer healthy component.
   - **Concurrent failures**: While rare, two components can fail close together, especially if there's a common cause (bad deploy, correlated failure).

   N+2 is common for critical systems where maintenance windows are frequent or where the cost of outage is high.
   </details>

2. **What's the key difference between high availability and fault tolerance?**
   <details>
   <summary>Answer</summary>

   **High Availability (HA)**: System remains operational with minimal downtime. Brief interruptions during failure are acceptable. In-flight requests may fail but new requests succeed quickly.

   **Fault Tolerance (FT)**: System continues operating without any interruption. No requests fail, even during component failure. Typically uses synchronous replication and instant failover.

   HA is cheaper and simpler; FT is more expensive and complex. Most web services use HA because users can retry. Financial transactions, medical systems, and aviation control need FT because any failure can have serious consequences.
   </details>

3. **Why might active-active be preferred over active-passive for a web service?**
   <details>
   <summary>Answer</summary>

   Active-active advantages:
   1. **No failover time**: Traffic immediately routes away from failed nodes
   2. **Better resource utilization**: All capacity handles traffic (passive nodes are "wasted")
   3. **No standby staleness**: All nodes are processing real traffic, so config and behavior are validated
   4. **Horizontal scaling**: Easy to add more active nodes as load increases
   5. **Geographic distribution**: Can serve users from nearest active node

   Active-passive is simpler and may be preferred when:
   - Traffic is low
   - Stateful workloads are hard to distribute
   - Cost of idle standby is acceptable
   </details>

4. **How can adding redundancy actually decrease reliability?**
   <details>
   <summary>Answer</summary>

   Redundancy can decrease reliability when:

   1. **Failover mechanism is unreliable**: If the code/process that detects failure and switches to backup is buggy or untested, it can fail to failover or failover incorrectly.

   2. **Added complexity introduces bugs**: More components = more code = more potential bugs. The redundancy management layer itself can fail.

   3. **Split-brain scenarios**: Both nodes think they're primary, causing data corruption or conflicts.

   4. **Correlated failures**: If redundant components share a failure domain (same rack, same code bug, same config), they can fail together.

   5. **Masking problems**: Redundancy can hide underlying issues until they affect enough components to cause an outage.

   Prevention: Test failover regularly, keep redundancy mechanisms simple, use independent failure domains.
   </details>

---

## Hands-On Exercise

**Task**: Design and test redundancy for a Kubernetes deployment.

**Part A: Create a Redundant Deployment (15 minutes)**

```bash
# Create namespace
kubectl create namespace redundancy-lab

# Create a deployment with redundancy
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: redundancy-lab
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: web-app
              topologyKey: kubernetes.io/hostname
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 2
          periodSeconds: 3
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            cpu: 50m
            memory: 64Mi
---
apiVersion: v1
kind: Service
metadata:
  name: web-app
  namespace: redundancy-lab
spec:
  selector:
    app: web-app
  ports:
  - port: 80
    targetPort: 80
EOF
```

**Part B: Verify Redundancy (5 minutes)**

```bash
# Check pods are distributed
kubectl get pods -n redundancy-lab -o wide

# Check service endpoints
kubectl get endpoints web-app -n redundancy-lab
```

**Part C: Test Failover (10 minutes)**

Terminal 1 - Watch pods:
```bash
kubectl get pods -n redundancy-lab -w
```

Terminal 2 - Simulate failure:
```bash
# Delete one pod
kubectl delete pod -n redundancy-lab -l app=web-app \
  $(kubectl get pod -n redundancy-lab -l app=web-app -o jsonpath='{.items[0].metadata.name}')

# Observe:
# - Pod terminates
# - New pod is scheduled
# - Endpoints update
```

Terminal 2 - More aggressive failure:
```bash
# Delete two pods simultaneously
kubectl delete pod -n redundancy-lab -l app=web-app \
  $(kubectl get pod -n redundancy-lab -l app=web-app -o jsonpath='{.items[0].metadata.name} {.items[1].metadata.name}')

# Observe: System recovers even with 2/3 pods gone
```

**Part D: Test PodDisruptionBudget (5 minutes)**

```bash
# Add a PodDisruptionBudget
cat <<EOF | kubectl apply -f -
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-app-pdb
  namespace: redundancy-lab
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: web-app
EOF

# Try to drain a node (if you have multiple nodes)
# kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# The PDB will prevent draining if it would leave fewer than 2 pods
```

**Part E: Clean Up**

```bash
kubectl delete namespace redundancy-lab
```

**Analysis Questions:**
1. How long did it take for a new pod to become ready after deletion?
2. Did the service maintain endpoints during the failure?
3. What would happen if all 3 pods were deleted simultaneously?
4. How does podAntiAffinity improve reliability?

**Success Criteria**:
- [ ] Deployment created with 3 replicas
- [ ] Pod anti-affinity configured
- [ ] Single pod failure tested and recovered
- [ ] Multi-pod failure tested and recovered
- [ ] Understand what PodDisruptionBudget does

---

## Further Reading

- **"Designing Data-Intensive Applications"** - Martin Kleppmann. Chapters on replication and fault tolerance are essential reading.

- **"Site Reliability Engineering"** - Google. Chapter on managing risk and error budgets.

- **"Building Microservices"** - Sam Newman. Practical patterns for service redundancy.

---

## Next Module

[Module 2.4: Measuring and Improving Reliability](module-2.4-measuring-and-improving-reliability.md) - SLIs, SLOs, and the practice of continuous reliability improvement.
