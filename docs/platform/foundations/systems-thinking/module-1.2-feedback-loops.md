# Module 1.2: Feedback Loops

> **Complexity**: `[MEDIUM]`
>
> **Time to Complete**: 30-35 minutes
>
> **Prerequisites**: [Module 1.1: What is Systems Thinking?](module-1.1-what-is-systems-thinking.md)
>
> **Track**: Foundations

---

## Why This Module Matters

It's Black Friday. Your e-commerce site is handling record traffic. The autoscaler adds pods to handle load. More pods mean more database connections. The database connection pool fills up. Queries start timing out. Timeouts trigger retries. Retries add more load. The autoscaler adds more pods. More pods, more connections, more timeouts, more retries...

In 20 minutes, you've gone from "handling load well" to "complete outage"—and most of the damage was self-inflicted.

This is a **feedback loop** gone wrong. Understanding feedback loops is the difference between building systems that stabilize under pressure and systems that destroy themselves.

> **The Thermostat Analogy**
>
> Your home thermostat is a feedback loop. Temperature drops below setpoint → heater turns on → temperature rises → heater turns off. This is a **balancing loop**—it opposes change. But imagine if your thermostat worked the other way: temperature drops → heater turns *off*. That's a **reinforcing loop**—it amplifies change. Your house would freeze. Many production incidents are just thermostats wired backwards.

---

## What You'll Learn

- The two types of feedback loops and how to identify them
- How delays turn stabilizing loops into destructive oscillations
- Common feedback loops in distributed systems
- How to design systems that use feedback safely
- Strategies for breaking dangerous feedback loops

---

## Part 1: Two Types of Loops

### 1.1 Reinforcing Loops (Positive Feedback)

**Reinforcing loops** amplify change. Whatever direction the system is moving, reinforcing loops push it further in that direction.

They're called "positive" not because they're good, but because they add to the existing trend.

```
REINFORCING LOOP: THE RETRY STORM
═══════════════════════════════════════════════════════════════

     ┌─────────────────────────────────────────────┐
     │                                             │
     ▼                                             │
┌─────────┐      ┌─────────┐      ┌─────────┐     │
│ Latency │─────▶│Timeouts │─────▶│ Retries │─────┘
│Increases│      │ Occur   │      │ Happen  │
└─────────┘      └─────────┘      └─────────┘
                                       │
                                       │ More load
                                       ▼
                              ┌─────────────────┐
                              │ Server becomes  │
                              │ more overloaded │
                              └─────────────────┘

Each retry adds load → more latency → more timeouts → more retries
This is exponential growth toward failure.
```

**Common reinforcing loops in production:**

| Loop | How It Works | Danger |
|------|--------------|--------|
| Retry storms | Failure → retry → more load → more failure | Cascading outage |
| Cache stampede | Cache expires → all requests hit DB → DB slows → more misses | Database overload |
| Connection pool exhaustion | Slow queries → connections held longer → pool fills → more waiting | Complete stall |
| Viral growth | Users invite users → more users → more invites | Good problem to have! |

### 1.2 Balancing Loops (Negative Feedback)

**Balancing loops** oppose change. They push the system back toward a target or equilibrium.

Called "negative" because they subtract from the current trend.

```
BALANCING LOOP: AUTOSCALING
═══════════════════════════════════════════════════════════════

                     Target: 70% CPU
                          │
                          │
     ┌─────────────────────────────────────────────┐
     │                    │                        │
     ▼                    │                        │
┌─────────┐         ┌─────┴─────┐           ┌─────────┐
│ CPU at  │────────▶│  Compare  │──────────▶│  Scale  │
│   85%   │         │ to target │           │  pods   │
└─────────┘         └───────────┘           └────┬────┘
                                                 │
     ┌───────────────────────────────────────────┘
     │
     ▼
┌─────────┐
│CPU drops│──── Opposes the original change
│ to 70%  │
└─────────┘
```

**Common balancing loops in production:**

| Loop | How It Works | Purpose |
|------|--------------|---------|
| Autoscaling | High CPU → add pods → lower CPU | Maintain performance |
| Rate limiting | Too many requests → reject some → manageable load | Protect resources |
| Circuit breaker | Failures → open circuit → reduce downstream load | Prevent cascade |
| Queue backpressure | Queue full → reject new items → queue drains | Prevent memory exhaustion |

> **Did You Know?**
>
> Your body has hundreds of balancing feedback loops. Blood sugar rises → pancreas releases insulin → cells absorb sugar → blood sugar drops. Fever rises → you sweat → cooling → temperature drops. Engineers who understand biology often build better distributed systems.

### 1.3 Identifying Loop Types

Quick test: If the system starts moving in a direction, does this loop...
- Push it **further** that direction? → **Reinforcing**
- Push it **back** toward a target? → **Balancing**

```
IDENTIFYING FEEDBACK LOOPS
═══════════════════════════════════════════════════════════════

Ask: "If A increases, what happens eventually to A?"

Reinforcing:
A ↑ → B ↑ → C ↑ → A ↑ (increases more)
A ↓ → B ↓ → C ↓ → A ↓ (decreases more)

Balancing:
A ↑ → B ↑ → C ↓ → A ↓ (returns toward target)
A ↓ → B ↓ → C ↑ → A ↑ (returns toward target)

Count the "↓" inversions in the loop:
- Even number (0, 2, 4...) = Reinforcing
- Odd number (1, 3, 5...) = Balancing
```

---

## Part 2: Delays Make Everything Worse

### 2.1 The Problem with Delays

Feedback loops have inherent **delays**—time between cause and effect. In theory, balancing loops stabilize systems. In practice, delays can turn them into oscillating disasters.

```
BALANCING LOOP WITHOUT DELAY
═══════════════════════════════════════════════════════════════

CPU %
100│
   │         Target: 70%
 70│─────────────────────────────────────────── Stable!
   │
 40│
   └──────────────────────────────────────────── Time

BALANCING LOOP WITH DELAY
═══════════════════════════════════════════════════════════════

CPU %
100│    ╱╲         ╱╲         ╱╲
   │   ╱  ╲       ╱  ╲       ╱  ╲
 70│──╱────╲─────╱────╲─────╱────╲───────────── Oscillating
   │ ╱      ╲   ╱      ╲   ╱      ╲
 40│╱        ╲ ╱        ╲ ╱        ╲
   └──────────────────────────────────────────── Time
         │         │
         └─────────┴── Delay causes overshoot/undershoot
```

### 2.2 Why Delays Cause Oscillation

Consider a shower with delayed temperature feedback:

1. Water is cold
2. You turn up the hot water
3. (Delay: water travels through pipes)
4. Water is still cold
5. You turn up the hot water more
6. (More delay)
7. Suddenly, water is scalding
8. You turn down the hot water
9. (Delay)
10. Water is still hot, you turn it down more
11. Water becomes freezing

**The same thing happens with autoscalers:**

1. CPU is high (85%)
2. Autoscaler adds 5 pods
3. (Delay: pods starting, 2 minutes)
4. CPU still high (measured before new pods ready)
5. Autoscaler adds 5 more pods
6. All 10 new pods become ready
7. CPU crashes to 30%
8. Autoscaler removes pods
9. (Delay)
10. CPU spikes again...

### 2.3 Sources of Delay in Production Systems

| Delay Type | Duration | Example |
|------------|----------|---------|
| Metric collection | 10-60s | Prometheus scrape interval |
| Metric aggregation | 15-60s | Query evaluation |
| Alert threshold | 30-300s | "Fire after 5 minutes of..." |
| Autoscaler cooldown | 30-600s | Prevent thrashing |
| Pod startup | 10-300s | Image pull, readiness probe |
| Human response | 300-3600s | Page, wake up, investigate |
| DNS propagation | 30-86400s | TTL-dependent |
| Cache invalidation | Variable | TTL, explicit purge |

> **War Story: The Autoscaler That Destroyed Itself**
>
> A team configured their HPA to scale on custom metrics from a queue. But the metric had a 2-minute delay. The HPA evaluated every 15 seconds. So it would see "queue is full," scale up, then see "queue is STILL full" (stale metric), scale up more. By the time fresh metrics arrived, they had 400 pods for a queue that 20 pods could handle. The sudden spike in pods exhausted their IP addresses, crashed the node autoscaler, and brought down the whole cluster.
>
> The fix: increase HPA evaluation interval to exceed metric delay, and add stabilization windows.

---

## Part 3: Feedback Loops in Distributed Systems

### 3.1 Common Destructive Loops

**The Retry Storm**

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Client ──▶ Request ──▶ Server ──▶ Timeout            │
│      │                                 │                │
│      │                    ┌────────────┘                │
│      │                    │                             │
│      │                    ▼                             │
│      └──── Retry ◀── "No response, try again"          │
│                                                         │
│   Problem: Each retry adds load, making timeouts       │
│   more likely, causing more retries.                    │
│                                                         │
│   Without intervention: Exponential load growth         │
└─────────────────────────────────────────────────────────┘
```

**The Thundering Herd**

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Cache expires at 12:00:00                             │
│         │                                               │
│         ▼                                               │
│   1000 requests all see cache miss                      │
│         │                                               │
│         ▼                                               │
│   1000 requests all hit database                        │
│         │                                               │
│         ▼                                               │
│   Database overwhelmed, queries slow/fail               │
│         │                                               │
│         ▼                                               │
│   Cache never gets populated (requests fail)            │
│         │                                               │
│         ▼                                               │
│   More requests, more cache misses... (loop)            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**The Connection Pool Death Spiral**

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Database slow (for any reason)                        │
│         │                                               │
│         ▼                                               │
│   Queries take longer                                   │
│         │                                               │
│         ▼                                               │
│   Connections held longer                               │
│         │                                               │
│         ▼                                               │
│   Connection pool fills up                              │
│         │                                               │
│         ▼                                               │
│   New requests wait for connections                     │
│         │                                               │
│         ▼                                               │
│   Timeouts, retries, more connections needed            │
│         │                                               │
│         ▼                                               │
│   Database even slower (more concurrent queries)        │
│         │                                               │
│         └───────────────── (loops back) ────────────────┘
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Common Stabilizing Loops

**Circuit Breaker**

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Failures exceed threshold                             │
│         │                                               │
│         ▼                                               │
│   Circuit opens (stops calling downstream)              │
│         │                                               │
│         ▼                                               │
│   Downstream gets less load                             │
│         │                                               │
│         ▼                                               │
│   Downstream recovers                                   │
│         │                                               │
│         ▼                                               │
│   Circuit closes (half-open test succeeds)              │
│         │                                               │
│         ▼                                               │
│   Normal operation resumes                              │
│                                                         │
│   This is a BALANCING loop that protects the system.   │
└─────────────────────────────────────────────────────────┘
```

**Rate Limiting**

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Incoming traffic increases                            │
│         │                                               │
│         ▼                                               │
│   Rate limiter activates                                │
│         │                                               │
│         ▼                                               │
│   Excess requests rejected (429)                        │
│         │                                               │
│         ▼                                               │
│   Actual load stays constant                            │
│         │                                               │
│         ▼                                               │
│   System remains healthy                                │
│                                                         │
│   This is a BALANCING loop that caps load.             │
└─────────────────────────────────────────────────────────┘
```

> **Gotcha: Retries vs Rate Limits**
>
> Rate limits are a balancing loop for the *server*, but combined with client retries, they create a reinforcing loop! Server limits rate → client sees 429 → client retries → more requests → more 429s → more retries. Solution: exponential backoff with jitter.

---

## Part 4: Designing with Feedback in Mind

### 4.1 Principles for Safe Feedback

**1. Add damping to balancing loops**

Damping slows down the response, reducing oscillation.

```yaml
# Kubernetes HPA with stabilization
spec:
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min of low CPU before scaling down
      policies:
      - type: Percent
        value: 10                       # Only remove 10% of pods at a time
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60    # Wait 1 min before scaling up more
      policies:
      - type: Percent
        value: 100                      # Can double pods quickly
        periodSeconds: 60
```

**2. Break reinforcing loops with circuit breakers**

```python
# Pseudocode for retry with circuit breaker
def call_service(request):
    if circuit_breaker.is_open():
        return fallback_response()  # Don't add load

    try:
        response = make_request(request)
        circuit_breaker.record_success()
        return response
    except Timeout:
        circuit_breaker.record_failure()
        if circuit_breaker.should_open():
            circuit_breaker.open()  # Stop the loop
        raise
```

**3. Add jitter to prevent synchronization**

```python
# Bad: All caches expire at the same time
cache.set(key, value, ttl=3600)

# Good: Randomize expiration
import random
jittered_ttl = 3600 + random.randint(-300, 300)  # 55-65 minutes
cache.set(key, value, ttl=jittered_ttl)
```

**4. Make delays explicit and visible**

```
# Good: Document delays in your architecture
METRIC PIPELINE DELAYS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
App → Prometheus:     15s (scrape interval)
Prometheus → Alert:   60s (pending duration)
Alert → PagerDuty:    10s (webhook)
PagerDuty → Engineer: 30s (phone call)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL: ~2 minutes minimum
```

### 4.2 Feedback Loop Checklist

When designing a system, for each feedback mechanism:

- [ ] Is it reinforcing or balancing?
- [ ] What's the total loop delay?
- [ ] Is there damping to prevent oscillation?
- [ ] Is there a way to break the loop if it goes wrong?
- [ ] Can multiple instances synchronize (thundering herd)?
- [ ] What happens if the feedback signal is delayed or lost?

---

## Did You Know?

- **The term "feedback"** was coined by rocket scientists in the 1920s. They needed to describe how a missile's guidance system used its current position to adjust its trajectory.

- **The 2010 Flash Crash** (stock market dropped 9% in minutes) was caused by a feedback loop. Automated selling triggered more automated selling. Circuit breakers now halt trading when prices move too fast.

- **Audio feedback** (microphone screech) is a reinforcing loop: sound enters mic → amplified → comes out speaker → enters mic louder. Musicians use limiters (damping) to control it.

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Retries without backoff | Creates reinforcing loop | Exponential backoff with jitter |
| Tight autoscaler settings | Oscillation, resource waste | Stabilization windows, damping |
| Same cache TTL everywhere | Thundering herd | Jitter TTLs |
| No circuit breakers | Cascading failures | Add circuit breakers at boundaries |
| Ignoring metric delay | Autoscaler overshoot | Match evaluation interval to metric lag |
| Coupling rate limit to retries | 429s cause more 429s | Backoff on rate limit responses |

---

## Quiz

1. **What's the difference between a reinforcing and a balancing feedback loop?**
   <details>
   <summary>Answer</summary>

   **Reinforcing loops** amplify change—if the system is moving in a direction, reinforcing loops push it further. They create exponential growth or decline (retry storms, viral growth).

   **Balancing loops** oppose change—they push the system back toward a target or equilibrium. They stabilize (autoscaling, thermostats, rate limiting).

   Quick test: If A increases, does A eventually increase more (reinforcing) or decrease back toward a target (balancing)?
   </details>

2. **Why do delays cause balancing loops to oscillate?**
   <details>
   <summary>Answer</summary>

   Delays cause oscillation because the corrective action is based on old information. By the time the action takes effect, the situation has changed:

   1. System sees high CPU (stale data)
   2. System adds pods
   3. During delay, even more pods added (still seeing stale high CPU)
   4. All pods become ready simultaneously
   5. CPU crashes low (overshoot)
   6. System removes pods
   7. Process repeats (undershoot)

   The longer the delay relative to how fast the system changes, the worse the oscillation.
   </details>

3. **How does a thundering herd create a reinforcing loop?**
   <details>
   <summary>Answer</summary>

   1. Cache expires simultaneously for many users
   2. All requests become cache misses
   3. All requests hit the database
   4. Database overwhelmed, queries slow or fail
   5. Cache cannot be repopulated (requests failing)
   6. More requests, still cache misses
   7. Even more database load
   8. Database slower, even less cache repopulation...

   The "reinforcing" element: cache failure → database load → more cache failure → more database load. Without intervention (like a single-writer pattern or mutex), it spirals.
   </details>

4. **What does "jitter" accomplish in distributed systems?**
   <details>
   <summary>Answer</summary>

   Jitter adds randomness to break synchronization. Without jitter:
   - All caches expire at the same time
   - All retries happen at the same time
   - All health checks run at the same time

   This synchronization turns individual actions into coordinated spikes that overwhelm systems.

   With jitter:
   - Cache expires are spread over minutes
   - Retries are staggered
   - Load remains more even

   Jitter converts a spike into a spread, preventing thundering herds and correlated behavior.
   </details>

---

## Hands-On Exercise

**Task**: Identify and map feedback loops in a real system.

**Scenario**: You're analyzing an API service with the following characteristics:
- Fronted by a load balancer
- Autoscales on CPU (HPA)
- Has retry logic for downstream calls
- Uses Redis cache with 1-hour TTL (exact, no jitter)
- Rate limited at 1000 req/s
- Circuit breaker on database calls

**Steps**:

1. **Draw the system** (5 minutes)
   - Include: Users, LB, API pods, Redis, Database
   - Mark the feedback mechanisms

2. **Identify all feedback loops** (15 minutes)

   For each loop, document:
   - The elements involved
   - Whether it's reinforcing or balancing
   - Key delays in the loop
   - What could go wrong

3. **Find dangerous combinations** (10 minutes)
   - Which reinforcing loops could trigger together?
   - Which balancing loops might fight each other?
   - Where could delays cause oscillation?

4. **Propose improvements** (10 minutes)
   - How would you add damping?
   - Where would you add jitter?
   - What circuit breakers are missing?

**Success Criteria**:
- [ ] System diagram with feedback loops marked
- [ ] At least 3 reinforcing loops identified
- [ ] At least 2 balancing loops identified
- [ ] Delays documented for each loop
- [ ] At least 2 dangerous combinations found
- [ ] Improvement proposals with rationale

**Example Analysis**:

```
FEEDBACK LOOPS IDENTIFIED
═══════════════════════════════════════════════════════════════

REINFORCING LOOPS (Dangerous):
1. Retry → Load → Timeout → Retry
   Delay: ~3s per retry
   Risk: Cascading failure

2. Cache miss → DB load → DB slow → Cache miss
   Delay: Cache TTL (1 hour) - SYNCHRONIZED!
   Risk: Hourly thundering herd

3. Rate limit → 429 → Client retry → Rate limit
   Delay: Immediate
   Risk: Retry amplification

BALANCING LOOPS (Stabilizing):
1. High CPU → HPA → More pods → Lower CPU
   Delay: ~2 min (metric + pod startup)
   Risk: Oscillation if delay too long

2. DB failures → Circuit open → Less DB load → Recovery
   Delay: 30s (circuit breaker timeout)
   Risk: May not open fast enough

DANGEROUS COMBINATIONS:
- Cache stampede triggers retry storm triggers autoscaler
- Rate limiter + retries = amplification
```

---

## Further Reading

- **"Thinking in Systems"** - Donella Meadows, Chapter 2 on feedback loops. Clear explanations with real-world examples.

- **"Release It!"** - Michael Nygard. Chapters on stability patterns (circuit breakers, timeouts, bulkheads) are all about managing feedback loops.

- **"How Complex Systems Fail"** - Richard Cook. Short read on why feedback loops in complex systems create surprising failures.

- **"Control Theory for Engineers"** - Any introductory text. Understanding PID controllers illuminates how to tune autoscalers.

---

## Next Module

[Module 1.3: Mental Models for Operations](module-1.3-mental-models-for-operations.md) - Leverage points, stock-and-flow diagrams, and practical frameworks for thinking about production systems.
