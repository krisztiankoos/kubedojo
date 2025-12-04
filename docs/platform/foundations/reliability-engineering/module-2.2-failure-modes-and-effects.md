# Module 2.2: Failure Modes and Effects

> **Complexity**: `[MEDIUM]`
>
> **Time to Complete**: 30-35 minutes
>
> **Prerequisites**: [Module 2.1: What is Reliability?](module-2.1-what-is-reliability.md)
>
> **Track**: Foundations

---

## Why This Module Matters

Every system fails. The question isn't "will it fail?" but "how will it fail?"

Understanding failure modes lets you design systems that fail gracefully instead of catastrophically. A service that returns cached data when the database is down is more useful than one that throws errors. A shopping cart that works without recommendations is better than one that crashes entirely.

This module teaches you to think systematically about failures—predicting them before they happen and designing responses that minimize impact.

> **The Car Analogy**
>
> Modern cars have multiple failure modes designed in. Run out of fuel? The engine stops but the steering and brakes still work. Battery dies? The car stops but the doors still open. Brake line leaks? There's a second brake circuit. Engineers didn't just hope these systems wouldn't fail—they designed specific responses for when they do.

---

## What You'll Learn

- Categories of failure modes in distributed systems
- FMEA (Failure Mode and Effects Analysis) technique
- Designing for graceful degradation
- Blast radius and failure isolation
- Common failure patterns and responses

---

## Part 1: Categories of Failure

### 1.1 The Failure Taxonomy

Not all failures are equal. Understanding the type of failure guides your response.

```
FAILURE TAXONOMY
═══════════════════════════════════════════════════════════════

BY VISIBILITY
─────────────────────────────────────────────────────────────
Obvious:    Service crashes, errors in logs
            └── Easy to detect, hard to prevent

Silent:     Wrong results, data corruption
            └── Hard to detect, often worse

BY SCOPE
─────────────────────────────────────────────────────────────
Partial:    Some requests fail, some succeed
            └── Often caused by load or specific inputs

Complete:   All requests fail
            └── Often caused by dependencies or resources

BY DURATION
─────────────────────────────────────────────────────────────
Transient:  Fails once, then works (network hiccup)
            └── Retry usually helps

Intermittent: Fails sometimes, unpredictably
              └── Hardest to debug

Permanent:  Fails until fixed (misconfiguration)
            └── Requires intervention
```

### 1.2 Common Failure Modes in Distributed Systems

| Failure Mode | What Happens | Example |
|--------------|--------------|---------|
| **Crash** | Process terminates unexpectedly | OOM kill, unhandled exception |
| **Hang** | Process alive but unresponsive | Deadlock, infinite loop, blocked I/O |
| **Performance degradation** | Works but slowly | Memory leak, CPU saturation |
| **Byzantine** | Wrong results, inconsistent behavior | Bit flip, corrupted data, buggy logic |
| **Network partition** | Can't reach other services | Firewall rule, network failure |
| **Resource exhaustion** | Runs out of something | Disk full, connection pool, file descriptors |
| **Dependency failure** | External service fails | Database down, API timeout |
| **Configuration error** | Wrong settings | Bad deploy, feature flag mistake |

### 1.3 Failure Characteristics

Every failure has characteristics that affect how you handle it:

```
FAILURE CHARACTERISTICS
═══════════════════════════════════════════════════════════════

Detectability:    How quickly can you know it failed?
                  ├── Immediate (crash)
                  ├── Delayed (health check catches it)
                  └── Unknown (silent corruption)

Recoverability:   Can the system self-heal?
                  ├── Automatic (restart, retry)
                  ├── Manual (needs operator)
                  └── Permanent (data loss)

Impact:           What's affected?
                  ├── Single request
                  ├── Single user
                  ├── Feature
                  └── Entire system

Frequency:        How often does it happen?
                  ├── Rare (once a year)
                  ├── Occasional (monthly)
                  └── Common (daily)
```

> **Try This (2 minutes)**
>
> Think of the last incident you experienced. Classify it:
> - Visibility: Obvious or silent?
> - Scope: Partial or complete?
> - Duration: Transient, intermittent, or permanent?
> - Detectability, recoverability, impact, frequency?

---

## Part 2: Failure Mode and Effects Analysis (FMEA)

### 2.1 What is FMEA?

**FMEA** (Failure Mode and Effects Analysis) is a systematic technique for identifying potential failures and their effects before they happen.

Originally from aerospace engineering, FMEA asks three questions:
1. **What can fail?** (Failure mode)
2. **What happens when it fails?** (Effect)
3. **How bad is it?** (Severity, likelihood, detectability)

```
FMEA PROCESS
═══════════════════════════════════════════════════════════════

Step 1: List components
        └── Service A, Database, Cache, Queue, External API

Step 2: For each component, list failure modes
        └── Database: slow queries, connection refused, corrupted data

Step 3: For each failure mode, determine effects
        └── Slow queries → User latency → Timeouts → Error page

Step 4: Score severity, likelihood, detectability
        └── Severity: 8/10, Likelihood: 4/10, Detection: 7/10

Step 5: Calculate Risk Priority Number (RPN)
        └── RPN = 8 × 4 × (10-7) = 96

Step 6: Prioritize mitigations by RPN
        └── Address highest RPN first
```

### 2.2 FMEA in Practice

| Component | Failure Mode | Effect | Severity | Likelihood | Detection | RPN | Mitigation |
|-----------|--------------|--------|----------|------------|-----------|-----|------------|
| Database | Connection timeout | Requests fail | 9 | 3 | 8 | 54 | Connection pooling, retry |
| Database | Corrupted data | Wrong results | 10 | 1 | 3 | 70 | Checksums, validation |
| Cache | Eviction storm | DB overload | 7 | 4 | 6 | 112 | Staggered TTLs, fallback |
| API Gateway | Memory leak | Crash, outage | 8 | 2 | 7 | 48 | Memory limits, restart |
| External API | Rate limited | Feature degraded | 5 | 6 | 9 | 30 | Caching, graceful degradation |

**Interpreting RPN:**
- 0-50: Low priority, monitor
- 51-100: Medium priority, plan mitigation
- 101-200: High priority, implement mitigation soon
- 200+: Critical, implement mitigation immediately

### 2.3 Conducting an FMEA

**Step-by-step guide:**

1. **Assemble the team** - Include people who know the system deeply
2. **Define the scope** - What system or feature are you analyzing?
3. **Create a system map** - Draw components and dependencies
4. **Brainstorm failure modes** - For each component, ask "how could this fail?"
5. **Trace effects** - Follow each failure through the system
6. **Score and prioritize** - Use RPN to focus effort
7. **Plan mitigations** - Design specific responses
8. **Review regularly** - FMEA is not one-time; systems change

> **Did You Know?**
>
> FMEA was developed by the U.S. military in the 1940s and was first used on the Apollo program. NASA required contractors to perform FMEA on all mission-critical systems. The technique helped identify and mitigate thousands of potential failures before they could endanger astronauts.

---

## Part 3: Graceful Degradation

### 3.1 What is Graceful Degradation?

**Graceful degradation** means a system continues to provide some functionality even when parts fail, rather than failing completely.

```
GRACEFUL DEGRADATION
═══════════════════════════════════════════════════════════════

WITHOUT GRACEFUL DEGRADATION
─────────────────────────────────────────────────────────────
User → App → Recommendation Service (DOWN!)
                    ↓
              500 ERROR
              "Something went wrong"

WITH GRACEFUL DEGRADATION
─────────────────────────────────────────────────────────────
User → App → Recommendation Service (DOWN!)
                    ↓
              Fallback: Show popular items
                    ↓
              User sees products, can still shop

The shopping experience is degraded (no personalization)
but functional (user can buy things).
```

### 3.2 Degradation Strategies

| Strategy | When to Use | Example |
|----------|-------------|---------|
| **Fallback to cache** | Data freshness not critical | Show cached recommendations |
| **Fallback to default** | Any reasonable response is better than error | Show "popular items" instead |
| **Feature disable** | Feature is optional | Hide recommendation panel entirely |
| **Reduced functionality** | Core function still possible | Search works but no filters |
| **Read-only mode** | Writes more critical than reads | Can view orders but not create new ones |
| **Queue for later** | Action can be deferred | Accept order, process payment later |

### 3.3 Designing Degradation Paths

For each feature, define:

```
DEGRADATION PATH DESIGN
═══════════════════════════════════════════════════════════════

Feature: Product Recommendations

Level 0 (Full):     Personalized recommendations from ML service
        ↓ (ML service timeout)
Level 1 (Degraded): User's previously viewed items from cache
        ↓ (Cache miss)
Level 2 (Fallback): Popular items in this category
        ↓ (Category service down)
Level 3 (Minimal):  Site-wide best sellers (static list)
        ↓ (Complete failure)
Level 4 (Off):      Hide recommendation panel entirely

Each level is worse but still functional.
```

> **Try This (3 minutes)**
>
> Pick a feature in your system. Define 3-4 degradation levels:
>
> | Level | Condition | Response |
> |-------|-----------|----------|
> | Full | Everything working | Normal behavior |
> | Degraded | [What fails?] | [What's the response?] |
> | Fallback | [What else fails?] | [What's the response?] |
> | Off | [When to disable?] | [What user sees?] |

---

## Part 4: Blast Radius and Isolation

### 4.1 What is Blast Radius?

**Blast radius** is the scope of impact when a failure occurs. Smaller blast radius = fewer users/features affected.

```
BLAST RADIUS
═══════════════════════════════════════════════════════════════

LARGE BLAST RADIUS (dangerous)
┌─────────────────────────────────────────────────────────────┐
│                    Shared Database                          │
│                         💥                                   │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐     │
│  │  A  │  │  B  │  │  C  │  │  D  │  │  E  │  │  F  │     │
│  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘     │
│     ↓        ↓        ↓        ↓        ↓        ↓        │
│   FAIL     FAIL     FAIL     FAIL     FAIL     FAIL       │
└─────────────────────────────────────────────────────────────┘

SMALL BLAST RADIUS (isolated)
┌─────────────────────────────────────────────────────────────┐
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐     │
│  │  A  │  │  B  │  │  C  │  │  D  │  │  E  │  │  F  │     │
│  └──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘     │
│     │        │        │        │        │        │         │
│  ┌──▼──┐  ┌──▼──┐  ┌──▼──┐  ┌──▼──┐  ┌──▼──┐  ┌──▼──┐     │
│  │ DB  │  │ DB  │  │ DB  │  │ DB  │  │ DB  │  │ DB  │     │
│  │  A  │  │  B  │  │ 💥 │  │  D  │  │  E  │  │  F  │     │
│  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘     │
│                       ↓                                    │
│                     FAIL (only C affected)                │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Isolation Patterns

**Bulkhead Pattern**

Named after ship compartments, bulkheads isolate failures to prevent them from spreading.

```
BULKHEAD PATTERN
═══════════════════════════════════════════════════════════════

Without bulkheads:
┌────────────────────────────────────────┐
│          Connection Pool (100)         │
│   ┌───────────────────────────────┐   │
│   │ Feature A (slow, uses 95)      │   │
│   │ Feature B (blocked, gets 5)    │   │ ← Both features
│   │ Feature C (blocked, gets 0)    │   │   share pool
│   └───────────────────────────────┘   │
└────────────────────────────────────────┘

With bulkheads:
┌─────────────────────────────────────────────────────────────┐
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐  │
│  │ Pool A (50)    │ │ Pool B (30)    │ │ Pool C (20)    │  │
│  │ Feature A      │ │ Feature B      │ │ Feature C      │  │
│  │ (slow, uses 50)│ │ (works fine)   │ │ (works fine)   │  │
│  └────────────────┘ └────────────────┘ └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
Feature A's slowness doesn't affect B or C.
```

**Other Isolation Patterns:**

| Pattern | How It Works | Use Case |
|---------|--------------|----------|
| **Bulkhead** | Separate resource pools | Prevent noisy neighbors |
| **Circuit breaker** | Stop calling failing service | Prevent cascade failures |
| **Timeout** | Limit how long to wait | Prevent thread/connection exhaustion |
| **Rate limiting** | Limit request rate | Prevent overload |
| **Separate deployments** | Different instances per tenant | Tenant isolation |
| **Namespaces/quotas** | Resource limits per workload | Kubernetes isolation |

### 4.3 Reducing Blast Radius

Strategies to minimize impact:

1. **Deploy incrementally** - Canary, blue-green reduce exposure
2. **Feature flags** - Disable problematic features quickly
3. **Geographic isolation** - Failures in one region don't affect others
4. **Service isolation** - Each service fails independently
5. **Data isolation** - Separate databases for critical vs. non-critical data

> **War Story: The Shared Database**
>
> A team ran all their microservices against a shared PostgreSQL database. "It's simpler," they said. Until a single poorly-optimized query locked a table, causing every service to queue up waiting for connections. The checkout service, user service, inventory service—all down simultaneously because of one bad query in the reporting service.
>
> The fix: separate databases for separate services, with clear ownership. Reporting now has its own read replica. A reporting bug can't take down checkout.

---

## Part 5: Common Failure Patterns

### 5.1 The Retry Storm

When a service is struggling, retries can make it worse:

```
RETRY STORM
═══════════════════════════════════════════════════════════════

Normal:         100 requests/sec → Service (handles fine)

Service slows:  100 req/sec → Service (slow, some timeout)
                    ↓
                Client retries (×3)
                    ↓
                300 req/sec → Service (overwhelmed)
                    ↓
                More timeouts, more retries
                    ↓
                1000 req/sec → Service (dead)

Mitigation:
- Exponential backoff (wait longer between retries)
- Jitter (randomize retry timing)
- Retry budgets (limit total retries)
- Circuit breakers (stop retrying entirely)
```

### 5.2 The Cascading Failure

One service fails, causing dependent services to fail:

```
CASCADING FAILURE
═══════════════════════════════════════════════════════════════

                    ┌─────────────┐
                    │   Service   │
                    │      A      │
                    └──────┬──────┘
                           │ calls
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼───┐  ┌─────▼───┐  ┌─────▼───┐
        │ Service │  │ Service │  │ Service │
        │    B    │  │    C    │  │    D    │
        └────┬────┘  └────┬────┘  └─────────┘
             │            │
        ┌────▼────┐  ┌────▼────┐
        │ Service │  │ Service │
        │    E    │  │    F    │ ← F fails
        └─────────┘  └─────────┘
                          │
                     C waits for F
                          │
                     A waits for C
                          │
                     All threads blocked
                          │
                     TOTAL OUTAGE

Mitigation: Timeouts, circuit breakers, async calls
```

### 5.3 The Thundering Herd

Many clients simultaneously hit a resource after an event:

```
THUNDERING HERD
═══════════════════════════════════════════════════════════════

Cache expires (TTL = 60 seconds)
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│  10,000 requests arrive simultaneously                      │
│                                                             │
│  Request 1 → Cache miss → Query database                   │
│  Request 2 → Cache miss → Query database                   │
│  Request 3 → Cache miss → Query database                   │
│  ...                                                        │
│  Request 10,000 → Cache miss → Query database              │
│                                                             │
│              Database overwhelmed                           │
└─────────────────────────────────────────────────────────────┘

Mitigation:
- Staggered TTLs (add random jitter to expiration)
- Request coalescing (one request populates, others wait)
- Warm cache before traffic arrives
- Rate limit cache refresh
```

### 5.4 Pattern Summary

| Pattern | Trigger | Result | Mitigation |
|---------|---------|--------|------------|
| Retry storm | Slow service | Overwhelming load | Backoff, budgets, breakers |
| Cascading failure | Dependency failure | System-wide outage | Timeouts, circuit breakers |
| Thundering herd | Synchronized event | Resource exhaustion | Stagger, coalesce, warm |
| Memory leak | Time, load | OOM crash | Limits, monitoring, restart |
| Connection exhaustion | Load, slow backends | New connections refused | Pooling, timeouts, bulkheads |

> **Try This (3 minutes)**
>
> Review your system for these patterns. Can any of these happen?
>
> | Pattern | Could it happen? | Current mitigation? |
> |---------|------------------|---------------------|
> | Retry storm | | |
> | Cascading failure | | |
> | Thundering herd | | |

---

## Did You Know?

- **The term "Byzantine failure"** comes from the "Byzantine Generals Problem," a thought experiment about unreliable messengers. Byzantine failures are when a system doesn't just fail, but provides wrong or inconsistent information—the hardest type to handle.

- **NASA's Mars Climate Orbiter** was lost in 1999 due to a failure mode that wasn't analyzed: unit mismatch. One team used metric units, another used imperial. The $125 million spacecraft crashed because nobody did FMEA on the interface between teams.

- **Circuit breakers** are named after electrical circuit breakers—devices that "break" (open) when current exceeds safe levels, preventing damage. The software pattern does the same: stops calling a failing service to prevent cascading damage.

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Not doing FMEA | Surprised by predictable failures | Regular FMEA sessions |
| Assuming dependencies won't fail | No fallback when they do | Design degradation paths |
| Tight coupling | One failure affects everything | Bulkheads, loose coupling |
| Unlimited retries | Retry storms | Budgets, backoff, circuit breakers |
| Same timeout everywhere | Either too aggressive or too lenient | Tune per-dependency |
| No feature flags | Can't disable broken features | Every feature behind a flag |

---

## Quiz

1. **What's the difference between a transient and an intermittent failure?**
   <details>
   <summary>Answer</summary>

   **Transient failures** occur once and then resolve—a network hiccup, a brief timeout. Retrying typically succeeds.

   **Intermittent failures** occur unpredictably—sometimes the system works, sometimes it doesn't, with no clear pattern. These are harder to debug because you can't reliably reproduce them.

   The distinction matters for mitigation: transient failures benefit from simple retries; intermittent failures require deeper investigation into patterns and conditions.
   </details>

2. **Why is a high Severity but low Detection score particularly dangerous in FMEA?**
   <details>
   <summary>Answer</summary>

   High severity + low detection means the failure has major impact AND you won't know it's happening until significant damage is done.

   Example: Silent data corruption (severity 10, detection 2). Users are getting wrong results, decisions are being made on bad data, but no alarms are firing. By the time you notice, the corruption has spread.

   These failure modes often have high RPN and should be prioritized for better detection (monitoring, checksums, validation) even if you can't reduce the severity.
   </details>

3. **How does the bulkhead pattern reduce blast radius?**
   <details>
   <summary>Answer</summary>

   The bulkhead pattern isolates resources (connection pools, thread pools, memory) so that one component's failure can't consume resources needed by others.

   Without bulkheads: A slow dependency uses all connections, blocking unrelated features.
   With bulkheads: Each feature has its own pool. A slow dependency exhausts its own pool but others continue working.

   It's like watertight compartments in a ship—a breach in one compartment doesn't sink the whole ship.
   </details>

4. **What makes retry storms particularly dangerous?**
   <details>
   <summary>Answer</summary>

   Retry storms create a positive feedback loop:
   1. Service slows down → requests timeout
   2. Clients retry → 2-3x more requests
   3. More requests → service slower → more timeouts
   4. More timeouts → more retries → even more requests
   5. System overwhelmed → complete failure

   What started as a small slowdown becomes a total outage. The "helpful" retry behavior actually kills the service faster than if clients had just failed.

   Mitigations: exponential backoff (wait longer between retries), jitter (don't retry at the same time), retry budgets (limit total retries), circuit breakers (stop retrying entirely).
   </details>

---

## Hands-On Exercise

**Task**: Conduct a mini-FMEA on a system you work with.

**Part 1: Map the System (10 minutes)**

Draw a simple diagram of a system you operate (or use the example checkout flow):

```
Example: Checkout Flow
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   API    │───▶│  Order   │───▶│ Payment  │───▶│ Inventory│
│ Gateway  │    │ Service  │    │ Service  │    │ Service  │
└──────────┘    └────┬─────┘    └────┬─────┘    └──────────┘
                     │               │
                ┌────▼─────┐    ┌────▼─────┐
                │ Database │    │ Payment  │
                │          │    │ Provider │
                └──────────┘    └──────────┘
```

**Part 2: FMEA Table (15 minutes)**

For at least 4 failure modes, complete this table:

| Component | Failure Mode | Effect on User | Severity (1-10) | Likelihood (1-10) | Detection (1-10) | RPN | Mitigation |
|-----------|--------------|----------------|-----------------|-------------------|------------------|-----|------------|
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |

**Part 3: Degradation Paths (10 minutes)**

For the highest RPN failure mode, design a degradation path:

| Level | Condition | User Experience |
|-------|-----------|-----------------|
| Full | Normal | |
| Degraded | [What fails?] | |
| Fallback | [More fails?] | |
| Minimal/Off | [Critical failure] | |

**Part 4: Blast Radius Analysis (5 minutes)**

Answer:
1. What's the largest blast radius failure in your FMEA?
2. How could you reduce it?
3. Is there a single point of failure that affects everything?

**Success Criteria**:
- [ ] System diagram with at least 4 components
- [ ] FMEA table with at least 4 failure modes analyzed
- [ ] RPN calculated correctly for each
- [ ] Degradation path for highest RPN item
- [ ] Blast radius improvement identified

---

## Further Reading

- **"Release It! Second Edition"** - Michael Nygard. Essential reading on stability patterns including circuit breakers, bulkheads, and timeouts.

- **"Failure Mode and Effects Analysis"** - D.H. Stamatis. Comprehensive guide to FMEA technique.

- **"How Complex Systems Fail"** - Richard Cook. Short paper on why FMEA alone isn't enough—complex systems fail in unexpected ways.

---

## Next Module

[Module 2.3: Redundancy and Fault Tolerance](module-2.3-redundancy-and-fault-tolerance.md) - Building systems that continue working when components fail.
