# Module 1.3: Mental Models for Operations

> **Complexity**: `[MEDIUM]`
>
> **Time to Complete**: 30-35 minutes
>
> **Prerequisites**: [Module 1.2: Feedback Loops](module-1.2-feedback-loops.md)
>
> **Track**: Foundations

---

## Why This Module Matters

You've got 20 metrics dashboards, 500 alerts, and a system doing something unexpected. Where do you focus? What do you change? How do you know if your fix will help or make things worse?

**Mental models** are thinking tools that help you navigate complexity. They're not the territory (your actual system), but they're maps that help you make sense of it. The right mental model helps you see patterns others miss and find solutions that actually work.

This module gives you practical frameworks used by the best SREs and operators to understand and influence production systems.

> **The Map Analogy**
>
> A subway map isn't geographically accurate—it's schematically useful. Mental models work the same way. A stock-and-flow diagram doesn't capture every aspect of your system, but it helps you see where things accumulate and why. "All models are wrong, but some are useful."

---

## What You'll Learn

- Donella Meadows' leverage points for system intervention
- Stock-and-flow diagrams for operational analysis
- Causal loop diagrams for visualizing feedback
- Practical application to production incidents
- How to choose the right model for the situation

---

## Part 1: Leverage Points

### 1.1 What Are Leverage Points?

**Leverage points** are places in a system where a small change can produce big results. Donella Meadows identified 12 leverage points, ranked from least to most effective.

The counterintuitive insight: the most obvious interventions are often the weakest.

```
LEVERAGE POINTS (Least to Most Effective)
═══════════════════════════════════════════════════════════════

WEAK LEVERAGE                          STRONG LEVERAGE
(Easy but ineffective)                 (Hard but transformative)
      │                                        │
      ▼                                        ▼

12. Numbers (constants, parameters)
11. Buffers (stock sizes)
10. Stock-and-flow structures
 9. Delays
 8. Balancing feedback loops
 7. Reinforcing feedback loops
 6. Information flows
 5. Rules of the system
 4. Power to add/change rules
 3. Goals of the system
 2. Mindset/paradigm
 1. Power to transcend paradigms
```

### 1.2 Leverage Points in Practice

Let's apply this to a real scenario: "The API is slow."

| Leverage | Intervention | Example | Effectiveness |
|----------|--------------|---------|---------------|
| 12 | Tune numbers | Increase timeout from 5s to 10s | Weak—masks problem |
| 11 | Resize buffers | Increase connection pool from 20 to 50 | Weak—delays problem |
| 9 | Reduce delays | Faster metrics collection | Moderate |
| 8 | Add balancing loop | Add autoscaling | Moderate |
| 7 | Break reinforcing loop | Add circuit breaker | Strong |
| 6 | Add information flow | Add distributed tracing | Strong |
| 5 | Change rules | "No deploy Friday" → "Deploy anytime with canary" | Strong |
| 3 | Change goals | "Maximize throughput" → "Maximize reliability" | Very strong |

> **Did You Know?**
>
> Most incident response stays at leverage point 12—tweaking numbers. "Increase replicas." "Raise the timeout." "Bump the memory limit." These interventions are easy, but they rarely solve the underlying problem. They buy time, not solutions.

### 1.3 Finding High-Leverage Interventions

**Ask these questions:**

1. **Where's the reinforcing loop?** Breaking it is high leverage.
2. **Who doesn't have information they need?** Adding visibility is high leverage.
3. **What goal is the system actually optimizing for?** Changing goals is very high leverage.
4. **What rule prevents the obvious solution?** Changing rules is high leverage.

**Example:**

```
SCENARIO: Frequent production incidents

Low leverage (12):
"Add more on-call engineers"
→ More people doing the same broken process

Medium leverage (8):
"Add PagerDuty escalation policies"
→ Better balancing loop, but doesn't prevent incidents

High leverage (6):
"Implement pre-production environments with production traffic replay"
→ New information flow catches issues earlier

Very high leverage (3):
"Change team goal from 'ship features' to 'ship reliable features'"
→ Changes what the system optimizes for
```

---

## Part 2: Stock-and-Flow Diagrams

### 2.1 The Building Blocks

**Stocks** are accumulations—things that can be measured at a point in time.
**Flows** are rates—things measured over time.

```
STOCK-AND-FLOW BASICS
═══════════════════════════════════════════════════════════════

           INFLOW                              OUTFLOW
       (rate: items/s)                     (rate: items/s)
             │                                    │
             │                                    │
             ▼                                    │
      ╔═════════════════════╗                    │
      ║                     ║                    │
      ║     STOCK           ║────────────────────┘
      ║   (items: count)    ║
      ║                     ║
      ╚═════════════════════╝

Stock changes = Inflow - Outflow
If inflow > outflow → Stock grows
If inflow < outflow → Stock shrinks
If inflow = outflow → Stock stable
```

### 2.2 Operational Stocks and Flows

| Stock | Inflow | Outflow | Why It Matters |
|-------|--------|---------|----------------|
| Request queue | Incoming requests | Processed requests | Queue depth = latency |
| Connection pool | New connections | Released connections | Full pool = blocked requests |
| Error budget | Time passing | Incidents | Budget = deploy freedom |
| Technical debt | Shortcuts taken | Refactoring done | Debt = future velocity |
| On-call fatigue | Alerts | Rest time | Fatigue = burnout |

### 2.3 Drawing Stock-and-Flow Diagrams

**Example: Request Processing**

```
REQUEST PROCESSING STOCK-AND-FLOW
═══════════════════════════════════════════════════════════════

                    Incoming
                    requests
                    (100/s)
                       │
                       ▼
              ╔═══════════════╗
              ║               ║
              ║  Queue Depth  ║────── Latency depends on this
              ║   (50 items)  ║
              ║               ║
              ╚═══════╤═══════╝
                      │
                      ▼
                  Processed
                   requests
                   (100/s)
                      │
                      ├────────────────┐
                      │                │
                      ▼                ▼
              ╔═══════════════╗   ╔═══════════════╗
              ║   Successes   ║   ║   Failures    ║
              ║   (95/s)      ║   ║   (5/s)       ║
              ╚═══════════════╝   ╚═══════╤═══════╝
                                          │
                                          │ Retries
                                          │ (3/s)
                                          ▼
                                  Back to Incoming
                                     requests
```

**Insights from this diagram:**
- If incoming rate exceeds processing rate, queue grows unboundedly
- Retries add to inflow, creating a reinforcing loop
- Failures that retry increase effective load by 6% (5 failures × 60% retry = 3 extra requests)

### 2.4 Using Stock-and-Flow for Incidents

**Incident: Latency increasing over time**

Step 1: Identify the stock (queue depth)
Step 2: Compare inflow vs outflow
Step 3: Find why they're imbalanced

```
DIAGNOSIS
═══════════════════════════════════════════════════════════════

Queue depth increasing means: inflow > outflow

Possible causes:

INFLOW INCREASED:
- Traffic spike (marketing campaign?)
- Retry storm (failures causing retries)
- Batch job started

OUTFLOW DECREASED:
- Fewer workers (pods crashed?)
- Each request slower (database issue?)
- Dependency slow (downstream latency)

Check each systematically:
1. Traffic rate change? → Check LB metrics
2. Retry rate change? → Check error rates
3. Worker count change? → Check pod count
4. Processing time change? → Check service latency
```

> **War Story: The Invisible Stock**
>
> A team spent weeks debugging "random" latency spikes. All their dashboards showed healthy services. They finally discovered the problem: Linux's TCP listen queue (a stock they hadn't considered). The queue was filling up and dropping connections. The inflow was bursty, outflow was limited by `net.core.somaxconn`. Once they visualized it as a stock-and-flow problem, the fix was obvious: increase the buffer and improve connection acceptance rate.

---

## Part 3: Causal Loop Diagrams

### 3.1 Notation

Causal loop diagrams show cause-and-effect relationships:

```
CAUSAL LOOP NOTATION
═══════════════════════════════════════════════════════════════

A ──(+)──▶ B    "A increases" causes "B increases"
                "A decreases" causes "B decreases"
                (Same direction)

A ──(−)──▶ B    "A increases" causes "B decreases"
                "A decreases" causes "B increases"
                (Opposite direction)

Loop types:
- Reinforcing (R): Even number of (−) links
- Balancing (B): Odd number of (−) links
```

### 3.2 Drawing Causal Loops

**Example: Autoscaling System**

```
AUTOSCALING CAUSAL LOOP DIAGRAM
═══════════════════════════════════════════════════════════════

                         ┌───────────────────────────────────┐
                         │                                   │
                         │              (−)                  │
                         │    B1: Autoscaler                 │
                         │    (Balancing)                    │
            ┌────────────┘                                   │
            │                                                │
            ▼                                                │
      ┌──────────┐                                    ┌──────┴─────┐
      │   CPU    │───────────(+)─────────────────────▶│  Scaling   │
      │  Usage   │                                    │  Decision  │
      └────┬─────┘                                    └──────┬─────┘
           │                                                 │
           │                                                 │
           │         ┌───────────────────────────────────────┘
           │         │
           │         │  (+)
           │         ▼
           │   ┌──────────┐
           │   │   Pod    │
           │   │  Count   │
           │   └────┬─────┘
           │        │
           │        │ (−)
           │        │
           └────────┘

Reading: High CPU → Scale up decision → More pods → Lower CPU per pod
This is a balancing loop (one negative link).
```

### 3.3 Complex System Example

**Microservices Under Load**

```
MICROSERVICES UNDER LOAD - CAUSAL LOOPS
═══════════════════════════════════════════════════════════════

                    ┌─────────────────────────────────┐
                    │                                 │
                    │    R1: Retry Storm              │
                    │    (Reinforcing - DANGEROUS)    │
                    │                                 │
       ┌────────────┘                                 │
       │                                              │
       ▼                                              │
 ┌──────────┐         ┌──────────┐         ┌─────────┴──┐
 │  Load    │───(+)──▶│ Latency  │───(+)──▶│  Timeouts  │
 │          │         │          │         │            │
 └──────────┘         └──────────┘         └─────┬──────┘
       ▲                    │                    │
       │                    │                    │
       │              ┌─────┘                    │
       │              │                          │
       │    (+)       │ (+)                      │ (+)
       │              ▼                          │
       │        ┌──────────┐                     │
       │        │ Resource │                     │
       │        │  Usage   │                     │
       │        └──────────┘                     │
       │                                         │
       │                                         │
       │              ┌──────────┐               │
       └──────────────│ Retries  │◀──────(+)────┘
                      │          │
                      └──────────┘

Loop R1: Load → Latency → Timeouts → Retries → More Load
(All positive links = Reinforcing = Exponential growth to failure)

ADDING A CIRCUIT BREAKER:

                    ┌─────────────────────────────────┐
                    │                                 │
                    │    B2: Circuit Breaker          │
                    │    (Balancing - PROTECTIVE)     │
                    │                                 │
                    │                                 │
                    ▼                                 │
              ┌──────────┐                           │
              │ Failures │──────(+)─────────────────▶│
              │          │                           │
              └────┬─────┘                           │
                   │                              ┌──┴───────┐
                   │ (+)                          │ Circuit  │
                   │                              │  Opens   │
                   ▼                              └──┬───────┘
              ┌──────────┐                          │
              │ Requests │◀────────(−)──────────────┘
              │ to Dep.  │
              └──────────┘

Loop B2: Failures → Circuit opens → Fewer requests → Fewer failures
(One negative link = Balancing = Stabilizing)
```

### 3.4 Using Causal Loops for Design

Before building a feature, draw its causal loops:

1. What stocks are affected?
2. What new feedback loops are created?
3. Are they reinforcing or balancing?
4. What delays exist?
5. What could make a balancing loop become unstable?

> **Gotcha: Feedback Loop Interactions**
>
> Individual loops may be stable, but *combinations* can be dangerous. Example: Two autoscalers (HPA for CPU, custom for queue depth) might fight each other. One scales up → queue drains → other scales down → CPU spikes → first scales up more. Always consider how loops interact.

---

## Part 4: Applying Mental Models to Incidents

### 4.1 The Incident Analysis Framework

When an incident occurs, use mental models systematically:

```
INCIDENT ANALYSIS WITH MENTAL MODELS
═══════════════════════════════════════════════════════════════

1. STOCK-AND-FLOW: What's accumulating?
   - Queue depths
   - Memory usage
   - Connection counts
   - Error counts

2. CAUSAL LOOPS: What's driving the accumulation?
   - Identify reinforcing loops (causing growth)
   - Identify broken balancing loops (failed to stabilize)

3. LEVERAGE POINTS: Where to intervene?
   - Can we break a reinforcing loop? (high leverage)
   - Can we add information? (high leverage)
   - Can we tune parameters? (low leverage, but fast)

4. DELAYS: What's hidden?
   - Are we seeing stale data?
   - Will our fix take time to show effect?
   - Could we oscillate?
```

### 4.2 Worked Example

**Incident: Database connection exhaustion**

**Stock-and-Flow Analysis:**

```
         New queries              Completed queries
          (50/s)                     (40/s)
             │                          │
             │                          │
             ▼                          │
      ╔═══════════════╗                │
      ║  Active       ║                │
      ║  Connections  ║────────────────┘
      ║  (200 → max)  ║
      ╚═══════════════╝

Inflow (50/s) > Outflow (40/s) → Stock grows
Why is outflow low? Queries are slower.
Why are queries slower? Lock contention.
```

**Causal Loop Analysis:**

```
R1: Death Spiral

Queries slow → More concurrent queries → More lock contention
           → Queries even slower → More concurrent → ...
                    (+)                (+)
```

**Leverage Point Analysis:**

| Leverage | Option | Effectiveness |
|----------|--------|---------------|
| 12 | Increase pool size | Buys time, makes contention worse |
| 8 | Add read replicas | Medium—balances read load |
| 7 | Add circuit breaker on slow queries | High—breaks the spiral |
| 6 | Add query timing visibility | High—see which queries are slow |
| 5 | Change rule: "All queries must have timeout" | Very high—prevents accumulation |

**Action Plan:**

1. Immediate: Kill long-running queries (break the loop)
2. Short-term: Add query timeouts (change rules)
3. Medium-term: Add slow query alerting (information flow)
4. Long-term: Read replica for heavy queries (structural change)

---

## Did You Know?

- **Donella Meadows** was lead author of "Limits to Growth" (1972), which used system dynamics to model global resource depletion. Her leverage points framework came from decades of modeling complex systems.

- **Jay Forrester**, who invented system dynamics, originally developed it to understand why GE's factories had boom-bust hiring cycles. He discovered feedback delays were causing oscillation—same problem we see in autoscalers.

- **Stock-and-flow thinking** is required for understanding climate change, economics, and epidemics. The COVID pandemic was essentially a stock (infections) with inflow (new cases) and outflow (recoveries + deaths), with multiple feedback loops (behavior change, healthcare capacity).

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Jumping to parameter tuning | Low leverage, treats symptoms | First identify loops, then find highest leverage |
| Ignoring delays | Causes oscillation or surprise | Map delays explicitly, account for them |
| Missing feedback loops | Unexpected behavior | Draw causal loop diagram before debugging |
| Optimizing one stock | May harm another | Consider all affected stocks |
| Not validating the model | Model may be wrong | Test predictions against reality |

---

## Quiz

1. **Why are high-leverage interventions often counterintuitive?**
   <details>
   <summary>Answer</summary>

   High-leverage interventions are counterintuitive because:

   1. **They're not obvious**: Changing a goal or paradigm doesn't feel like "doing something"
   2. **They're harder**: Adding a circuit breaker requires more design than increasing a timeout
   3. **Results are delayed**: Structural changes take time to show effects
   4. **They require systemic understanding**: You need to see the whole system to find them

   Low-leverage interventions (tuning parameters) feel productive because they're immediate and tangible, but they rarely solve the underlying problem. We're biased toward action over understanding.
   </details>

2. **In a stock-and-flow diagram, what does it mean when a stock is growing?**
   <details>
   <summary>Answer</summary>

   A growing stock means **inflow exceeds outflow**. This is important because:

   - It's not about the absolute rate—100/s in and 100/s out = stable
   - Even small differences compound over time
   - Growing stocks eventually hit limits (queue overflow, memory exhaustion, connection pool full)

   The key diagnostic question is: "Why is inflow > outflow?" Either inflow increased (more demand) or outflow decreased (slower processing). Check both.
   </details>

3. **How do you identify if a causal loop is reinforcing or balancing?**
   <details>
   <summary>Answer</summary>

   Count the negative (-) links in the loop:
   - **Even number (0, 2, 4...)**: Reinforcing loop (amplifies change)
   - **Odd number (1, 3, 5...)**: Balancing loop (opposes change)

   Alternative method: Trace the loop manually
   - If A increases → trace through → A increases more = Reinforcing
   - If A increases → trace through → A decreases = Balancing

   Reinforcing loops create exponential growth or collapse. Balancing loops create stability or oscillation (with delays).
   </details>

4. **Why is "add more information flow" often a high-leverage intervention?**
   <details>
   <summary>Answer</summary>

   Information flow is high leverage because:

   1. **Feedback requires information**: Without seeing the problem, the system can't correct it
   2. **People make better decisions with data**: A dashboard showing the issue leads to faster resolution
   3. **It enables other loops**: Autoscaling, alerting, and circuit breakers all need information to function
   4. **It persists**: Once you add observability, it keeps providing value

   Classic example: Adding distributed tracing doesn't fix latency directly, but it reveals where latency comes from. This information enables targeted fixes that otherwise would be impossible.
   </details>

---

## Hands-On Exercise

This exercise has two parts: a practical Kubernetes observation and a conceptual analysis.

### Part A: Observe Stocks and Flows in Kubernetes (15 minutes)

**Objective**: See stocks and flows in action using a Kubernetes Job queue.

**Prerequisites**: A running Kubernetes cluster (kind, minikube, or any cluster)

**Step 1: Create a job processing system**

```bash
# Create namespace
kubectl create namespace stocks-lab

# Create a series of jobs (the "queue")
for i in {1..10}; do
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: task-$i
  namespace: stocks-lab
spec:
  template:
    spec:
      containers:
      - name: worker
        image: busybox
        command: ["sh", "-c", "echo Processing task $i; sleep $((RANDOM % 10 + 5))"]
      restartPolicy: Never
  backoffLimit: 2
EOF
done
```

**Step 2: Watch the stock (pending jobs) drain**

```bash
# Watch jobs - this shows the "stock" of work
kubectl get jobs -n stocks-lab -w

# In another terminal, watch pods (the workers processing the queue)
kubectl get pods -n stocks-lab -w
```

**Step 3: Observe stocks and flows**

```bash
# Count pending vs completed (stock levels)
echo "Pending: $(kubectl get jobs -n stocks-lab --field-selector status.successful=0 --no-headers | wc -l)"
echo "Completed: $(kubectl get jobs -n stocks-lab --field-selector status.successful=1 --no-headers | wc -l)"
```

**What to observe:**
- **Stock**: Number of pending jobs (accumulation)
- **Inflow**: Jobs being created (we created 10)
- **Outflow**: Jobs completing (depends on processing time)
- **Delay**: Time between job creation and completion

**Step 4: Add more inflow (simulate load spike)**

```bash
# Add 5 more jobs while others are still processing
for i in {11..15}; do
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: task-$i
  namespace: stocks-lab
spec:
  template:
    spec:
      containers:
      - name: worker
        image: busybox
        command: ["sh", "-c", "echo Processing task $i; sleep 3"]
      restartPolicy: Never
EOF
done
```

Notice how the "pending" stock grows when inflow exceeds outflow capacity.

**Step 5: Clean up**

```bash
kubectl delete namespace stocks-lab
```

---

### Part B: Analyze a System Using Mental Models (25 minutes)

**Task**: Apply all three mental models to a system.

**Choose a system** you operate (or use this scenario: a job processing system with a queue, workers, and a results store).

**Section 1: Stock-and-Flow Diagram (10 minutes)**

Draw a stock-and-flow diagram including:
- At least 2 stocks (e.g., queue depth, active workers)
- Inflows and outflows for each
- Any connections between stocks

Answer:
- What happens if inflow doubles?
- What happens if processing slows 50%?
- Where are the limits (max queue, max connections)?

**Section 2: Causal Loop Diagram (10 minutes)**

Draw a causal loop diagram including:
- At least one balancing loop (stabilizing mechanism)
- At least one potential reinforcing loop (risk)
- Mark all links as (+) or (-)

Answer:
- What could trigger the reinforcing loop?
- What could break the balancing loop?

**Section 3: Leverage Point Analysis (5 minutes)**

For a hypothetical incident ("processing is falling behind"), list interventions at different leverage levels:

| Leverage Level | Intervention | Why This Level |
|----------------|--------------|----------------|
| 12 (parameters) | | |
| 8 (balancing loops) | | |
| 7 (reinforcing loops) | | |
| 6 (information flows) | | |
| 5 (rules) | | |

**Success Criteria**:
- [ ] Part A: Observed jobs being created and completed
- [ ] Part A: Can explain the stock (pending jobs) and flows (creation/completion)
- [ ] Part B: Stock-and-flow diagram with 2+ stocks, clear inflows/outflows
- [ ] Part B: Causal loop diagram with 1+ balancing and 1+ reinforcing loop
- [ ] Part B: 5 interventions mapped to leverage levels
- [ ] Part B: Clear reasoning for each intervention's level

---

## Further Reading

- **"Thinking in Systems: A Primer"** - Donella Meadows, Chapters 5-6 on leverage points and system traps. Essential reading.

- **"Business Dynamics"** - John Sterman. Academic but thorough treatment of system dynamics modeling.

- **"An Introduction to Systems Thinking"** - Barry Richmond. Practical guide to stock-and-flow and causal loop diagrams.

- **"Places to Intervene in a System"** - Donella Meadows (original article). Free online, shorter than the book.

---

## Next Module

[Module 1.4: Complexity and Emergent Behavior](module-1.4-complexity-and-emergent-behavior.md) - The Cynefin framework, why complex systems fail, and designing for resilience in uncertain environments.
