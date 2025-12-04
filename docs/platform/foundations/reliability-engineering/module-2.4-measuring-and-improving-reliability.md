# Module 2.4: Measuring and Improving Reliability

> **Complexity**: `[MEDIUM]`
>
> **Time to Complete**: 35-40 minutes
>
> **Prerequisites**: [Module 2.3: Redundancy and Fault Tolerance](module-2.3-redundancy-and-fault-tolerance.md)
>
> **Track**: Foundations

---

## Why This Module Matters

"We need to improve reliability" is a vague goal. Improve what? By how much? How will you know if you've succeeded?

This module teaches you to measure reliability objectively using SLIs (Service Level Indicators), set meaningful targets with SLOs (Service Level Objectives), and create a continuous improvement process. Without measurement, reliability is just hope. With measurement, it's engineering.

> **The Fitness Analogy**
>
> "I want to get fit" is a vague goal. "I want to run a 5K in under 25 minutes by March" is specific and measurable. You can track progress (current time), know when you've succeeded (under 25 minutes), and adjust training if needed. SLOs do the same for system reliability—they turn "be reliable" into "this specific thing, measured this way, at this target."

---

## What You'll Learn

- What SLIs, SLOs, and SLAs are and how they differ
- How to choose good SLIs for your services
- Setting realistic SLOs
- Using error budgets for decision-making
- Continuous reliability improvement practices

---

## Part 1: The SLI/SLO/SLA Framework

### 1.1 Definitions

| Term | What It Is | Who Cares | Example |
|------|------------|-----------|---------|
| **SLI** (Service Level Indicator) | Measurement of service behavior | Engineers | 99.2% of requests succeed |
| **SLO** (Service Level Objective) | Target for an SLI | Engineering + Product | 99.9% of requests should succeed |
| **SLA** (Service Level Agreement) | Contract with consequences | Business + Customers | 99.5% uptime or credit issued |

```
SLI → SLO → SLA RELATIONSHIP
═══════════════════════════════════════════════════════════════

SLI (what you measure):
    "Request success rate is currently 99.2%"
    └── A metric, a fact

SLO (what you target):
    "Request success rate should be ≥99.9%"
    └── An internal goal, aspirational

SLA (what you promise):
    "Request success rate will be ≥99.5% or customer gets credit"
    └── An external contract, legally binding

Relationship:
    SLO should be stricter than SLA (give yourself buffer)
    SLA ≤ SLO

    Example:
    - SLA to customers: 99.5%
    - Internal SLO: 99.9%
    - Buffer: 0.4% to catch problems before breach
```

### 1.2 Why This Matters

Without SLOs:
- "Is the service reliable enough?" → "I think so?"
- "Should we ship this feature or fix reliability?" → Arguments
- "How urgent is this incident?" → Depends on who's loudest

With SLOs:
- "Is the service reliable enough?" → "Yes, we're at 99.95% against a 99.9% target"
- "Should we ship or fix reliability?" → "We have 3 hours of error budget left—fix first"
- "How urgent is this incident?" → "It's burning 10x normal error budget—high priority"

### 1.3 SLOs Enable Trade-offs

```
SLO-BASED DECISION MAKING
═══════════════════════════════════════════════════════════════

Scenario: Team wants to ship new feature that adds risk

WITHOUT SLO:
    Product: "Ship it!"
    Engineering: "It might break things!"
    Product: "But customers want it!"
    Engineering: "But reliability!"
    → Argument, politics, loudest voice wins

WITH SLO:
    Current reliability: 99.95%
    SLO target: 99.9%
    Error budget: 0.05% (21.6 minutes this month)
    Budget used: 5 minutes
    Budget remaining: 16.6 minutes

    Decision: We have error budget. Ship it, but monitor closely.
    If we were at 99.85%, decision would be: Fix reliability first.

    → Data-driven decision, no argument needed
```

> **Did You Know?**
>
> Google's SRE team famously uses error budgets to manage the tension between development velocity and reliability. When error budget is healthy, teams ship fast. When budget is depleted, feature freezes happen automatically—no negotiation needed. This has been adopted industry-wide as a best practice.

---

## Part 2: Choosing Good SLIs

### 2.1 The Four Golden Signals

Google's SRE book recommends monitoring these four signals:

| Signal | What It Measures | Example SLI |
|--------|------------------|-------------|
| **Latency** | How long requests take | p99 latency < 200ms |
| **Traffic** | How much demand | Requests per second |
| **Errors** | Rate of failures | Error rate < 0.1% |
| **Saturation** | How "full" the system is | CPU < 80% |

```
THE FOUR GOLDEN SIGNALS
═══════════════════════════════════════════════════════════════

          ┌─────────────────────────────────────────────┐
Traffic ──▶         YOUR SERVICE                       │──▶ Response
          │                                             │
          │  Latency: How fast?                        │
          │  Errors: How often fails?                  │
          │  Saturation: How full?                     │
          │                                             │
          └─────────────────────────────────────────────┘

These four signals capture most user-visible problems:
- High latency → Users wait → Bad experience
- High errors → Features broken → Bad experience
- High traffic → Might cause others → Leading indicator
- High saturation → About to have problems → Early warning
```

### 2.2 SLI Categories

| Category | Measures | Good For |
|----------|----------|----------|
| **Availability** | Is it up? | Basic health |
| **Latency** | Is it fast? | User experience |
| **Throughput** | Can it handle load? | Capacity |
| **Correctness** | Is the output right? | Data quality |
| **Freshness** | Is data current? | Real-time systems |
| **Durability** | Is data safe? | Storage systems |

### 2.3 Good SLI Characteristics

A good SLI is:

| Characteristic | Why It Matters | Example |
|----------------|----------------|---------|
| **Measurable** | You can actually collect the data | Request latency from logs |
| **User-centric** | Reflects user experience | Measured at the edge, not internally |
| **Actionable** | You can do something about it | Not external dependencies |
| **Proportional** | Worse SLI = worse experience | p99 latency, not mean |

```
GOOD vs BAD SLIs
═══════════════════════════════════════════════════════════════

BAD: "Server CPU utilization"
    - Not user-centric (users don't care about CPU)
    - Not proportional (80% CPU might be fine)

GOOD: "Request latency p99"
    - User-centric (directly affects experience)
    - Proportional (higher = worse)

BAD: "Database is up"
    - Binary (up/down)
    - Doesn't capture degradation

GOOD: "Percentage of queries completing in <100ms"
    - Continuous (captures degradation)
    - User-centric
```

> **Try This (3 minutes)**
>
> For a service you work with, define one SLI for each category:
>
> | Category | Your SLI |
> |----------|----------|
> | Availability | |
> | Latency | |
> | Correctness | |

---

## Part 3: Setting SLOs

### 3.1 SLO Principles

**1. Start with user expectations, not technical capabilities**

```
WRONG: "Our system can do 99.99%, so that's our SLO"
RIGHT: "Users expect checkout to work. What reliability do they need?"
```

**2. Not everything needs the same SLO**

```
DIFFERENTIATED SLOs
═══════════════════════════════════════════════════════════════

Service              SLO        Rationale
─────────────────────────────────────────────────────────────
Payment processing   99.99%     Money is involved, high stakes
Product search       99.9%      Important but degraded is okay
Recommendations      99.0%      Nice to have, can hide if down
Internal reporting   95.0%      Async, users can wait
```

**3. SLO should be achievable but challenging**

```
Too easy:    99% (you'll never improve)
Too hard:    99.999% (you'll always fail, SLO becomes meaningless)
Just right:  99.9% (achievable with effort, gives error budget)
```

### 3.2 The SLO Setting Process

```
SLO SETTING PROCESS
═══════════════════════════════════════════════════════════════

Step 1: Measure current state
        └── "We're currently at 99.5% availability"

Step 2: Understand user needs
        └── "Users complain when we're below 99%"

Step 3: Consider business context
        └── "We're competing with Company X at 99.9%"

Step 4: Set initial SLO
        └── "Target 99.9%, with 99.5% as minimum"

Step 5: Implement and measure
        └── Track SLI against SLO

Step 6: Review and adjust
        └── "We're consistently at 99.95%, raise target?"
        └── "We're always missing, lower target?"
```

### 3.3 SLO Document Template

```markdown
# Service: Payment API
# Version: 1.2
# Last reviewed: 2024-01-15

## SLIs

| SLI | Definition | Measurement |
|-----|------------|-------------|
| Availability | Successful responses / Total requests | HTTP 2xx/3xx vs 5xx |
| Latency | Request duration at p99 | Measured at load balancer |
| Correctness | Valid payment responses | Reconciliation check |

## SLOs

| SLI | SLO Target | Error Budget (monthly) |
|-----|------------|----------------------|
| Availability | ≥99.95% | 21.6 minutes |
| Latency p99 | ≤500ms | 0.05% of requests |
| Correctness | ≥99.99% | 0.01% of responses |

## Error Budget Policy

- Budget >50%: Normal development velocity
- Budget 25-50%: Increased monitoring, cautious releases
- Budget <25%: Feature freeze, reliability focus
- Budget depleted: All hands on reliability

## Review Schedule

- Weekly: Error budget check
- Monthly: SLO review meeting
- Quarterly: SLO target review
```

> **Gotcha: The SLO Ceiling Problem**
>
> If you consistently exceed your SLO by a large margin, you might be over-investing in reliability. Being at 99.99% when your SLO is 99.9% means you could move faster. Consider either: raising the SLO (if users benefit) or deliberately spending error budget on velocity (if they don't).

---

## Part 4: Error Budgets in Practice

### 4.1 Calculating Error Budget

```
ERROR BUDGET CALCULATION
═══════════════════════════════════════════════════════════════

SLO: 99.9% availability
Error budget: 100% - 99.9% = 0.1%

Monthly error budget:
- Minutes in month: 30 days × 24 hours × 60 min = 43,200 minutes
- Error budget: 43,200 × 0.001 = 43.2 minutes

Weekly error budget:
- Minutes in week: 7 × 24 × 60 = 10,080 minutes
- Error budget: 10,080 × 0.001 = 10.08 minutes

Budget burn rate:
- Normal: ~1 minute per day
- Incident: 10 minutes in 1 hour = 10x burn rate
```

### 4.2 Error Budget Visualization

```
ERROR BUDGET DASHBOARD
═══════════════════════════════════════════════════════════════

MONTHLY ERROR BUDGET: 43.2 minutes (SLO: 99.9%)

Week 1:  [████████████████████░░░░░░░░░░░░░░░░░░] Used: 8 min
Week 2:  [█████████████████████████░░░░░░░░░░░░░] Used: 15 min
Week 3:  [██████████████████████████████░░░░░░░░] Used: 25 min (incident)
Week 4:  [████████████████████████████████░░░░░░] Used: 32 min
         ─────────────────────────────────────────
         Total used: 32 minutes | Remaining: 11.2 minutes

Status: ⚠️ 26% remaining - Cautious releases

Last 30 days trend:
         Budget ──────────────────────────────────
    100% │ ●
         │   ●●
         │      ●●●
         │          ●●
         │             ●●●●●●
     50% │─────────────────────────────────────── Warning
         │                     ●●●●●●●●●●●●●●●●●●
      0% │────────────────────────────────────────────────▶
         Day 1                                      Day 30
```

### 4.3 Error Budget Policies

| Budget Level | Policy | Actions |
|--------------|--------|---------|
| **>75%** | Green - Full velocity | Ship features, experiment |
| **50-75%** | Yellow - Caution | Normal releases, increased monitoring |
| **25-50%** | Orange - Slow down | Only critical releases, postmortems for all incidents |
| **<25%** | Red - Stop | Feature freeze, all hands on reliability |
| **Depleted** | Emergency | War room until budget recovers |

> **Try This (3 minutes)**
>
> Your service has a 99.9% SLO. This month:
> - Incident 1: 15 minutes of downtime
> - Incident 2: 8 minutes of degraded performance (counts as 50%)
> - Incident 3: 5 minutes of downtime
>
> Calculate:
> 1. Total budget (43.2 minutes for 99.9%)
> 2. Budget consumed: _____ minutes
> 3. Budget remaining: _____ minutes
> 4. What policy level are you at?

---

## Part 5: Continuous Improvement

### 5.1 The Reliability Improvement Cycle

```
RELIABILITY IMPROVEMENT CYCLE
═══════════════════════════════════════════════════════════════

        ┌─────────────────────────────────────────────────┐
        │                                                 │
        ▼                                                 │
    ┌─────────┐                                          │
    │ MEASURE │ ← SLIs, error budget tracking            │
    └────┬────┘                                          │
         │                                                │
         ▼                                                │
    ┌─────────┐                                          │
    │ ANALYZE │ ← Why are we missing SLO?                │
    └────┬────┘                                          │
         │                                                │
         ▼                                                │
    ┌─────────┐                                          │
    │PRIORITIZE│ ← What will have most impact?           │
    └────┬────┘                                          │
         │                                                │
         ▼                                                │
    ┌─────────┐                                          │
    │ IMPROVE │ ← Implement fixes                        │
    └────┬────┘                                          │
         │                                                │
         └────────────────────────────────────────────────┘
```

### 5.2 Postmortems

Every significant incident should have a **blameless postmortem**:

```
POSTMORTEM TEMPLATE
═══════════════════════════════════════════════════════════════

## Incident: Payment API Outage 2024-01-15

### Summary
- Duration: 23 minutes
- Impact: 12,000 failed transactions
- Error budget consumed: 23 minutes (53% of monthly)

### Timeline
- 14:32 - Deploy of version 2.3.1
- 14:35 - Error rate spikes to 15%
- 14:38 - Alert fires, on-call paged
- 14:45 - Rollback initiated
- 14:55 - Service recovered

### Contributing Factors
1. Database migration had incompatible schema change
2. Canary deployment disabled for "quick fix"
3. Integration tests didn't cover this code path

### Action Items
| Action | Owner | Due |
|--------|-------|-----|
| Re-enable canary deployments | Alice | 2024-01-16 |
| Add integration test for schema | Bob | 2024-01-20 |
| Review migration process | Team | 2024-01-22 |

### Lessons Learned
- "Quick fixes" are rarely quick
- Canary deployments exist for a reason
```

### 5.3 Reliability Reviews

Regular reliability reviews keep teams focused:

**Weekly**: Error budget check
- How much budget consumed?
- Any incidents to review?
- Upcoming risky changes?

**Monthly**: SLO review
- Are we meeting SLOs?
- What's trending?
- What's the biggest reliability risk?

**Quarterly**: Strategy review
- Are SLOs still appropriate?
- What systemic improvements are needed?
- Resource allocation for reliability work

### 5.4 Reliability Investment

```
RELIABILITY INVESTMENT FRAMEWORK
═══════════════════════════════════════════════════════════════

When error budget is healthy:
    ├── Invest in observability improvements
    ├── Build automation to reduce MTTR
    ├── Conduct chaos engineering experiments
    └── Pay down reliability tech debt

When error budget is depleted:
    ├── Stop feature work
    ├── Focus on top incident causes
    ├── Increase monitoring coverage
    └── Implement quick-win reliability fixes

Investment allocation (example):
    ┌─────────────────────────────────────────────────────┐
    │         Engineering Time Allocation                 │
    │                                                     │
    │  Features    █████████████████████████  60%         │
    │  Reliability ████████████             25%           │
    │  Tech Debt   █████                    15%           │
    │                                                     │
    │  If SLO missed 2 consecutive months:               │
    │                                                     │
    │  Features    ████████████             30%           │
    │  Reliability █████████████████████████  50%         │
    │  Tech Debt   ████████                 20%           │
    └─────────────────────────────────────────────────────┘
```

> **War Story: The Team That Stopped Blaming**
>
> A platform team had a toxic incident culture. After every outage: "Who deployed last? Whose code was it? Who's responsible?" Engineers hid information. Post-incident meetings were interrogations. The same problems kept happening.
>
> A new engineering director introduced blameless postmortems. The first one felt awkward—people kept trying to assign blame. She redirected: "We're not asking who. We're asking why the system allowed this to happen."
>
> Six months later: postmortem participation doubled. Engineers volunteered information. Action items actually got completed because people owned them willingly, not defensively. Incident recurrence dropped 60%.
>
> The insight: When people fear blame, they hide information. When they feel safe, they share what went wrong. Reliability improves when learning replaces blame.

---

## Did You Know?

- **Google publishes SLOs** for many of their services. GCP has public SLOs that trigger automatic credits if breached. This transparency builds trust and sets industry standards.

- **The "rule of 10"** in SLO setting: It takes roughly 10x effort to add each nine of reliability. Going from 99% to 99.9% is hard. Going from 99.9% to 99.99% is 10x harder.

- **SLOs predate software**. The concept comes from manufacturing quality control. Walter Shewhart developed statistical quality control at Bell Labs in the 1920s—the same principles apply today.

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Too many SLIs | Can't focus, alert fatigue | 3-5 SLIs per service max |
| SLO = current performance | No room to improve or buffer | Set slightly below current |
| Measuring internally, not at edge | Misses user experience | Measure where users connect |
| Ignoring error budget | SLO is just a number | Make budget decisions automatic |
| No postmortems | Same incidents repeat | Blameless postmortem culture |
| Yearly SLO review | SLOs become stale | Quarterly minimum |

---

## Quiz

1. **What's the difference between an SLI and an SLO?**
   <details>
   <summary>Answer</summary>

   **SLI (Service Level Indicator)** is a measurement of service behavior—a metric, a fact. "Our availability is 99.85%" is an SLI.

   **SLO (Service Level Objective)** is a target for that measurement—a goal. "Availability should be ≥99.9%" is an SLO.

   SLIs tell you where you are. SLOs tell you where you want to be. The gap between them is what you work to close.
   </details>

2. **Why should SLOs be stricter than SLAs?**
   <details>
   <summary>Answer</summary>

   SLAs have consequences—often financial penalties or contract breaches. If your SLO equals your SLA, you have no buffer. The moment you miss your SLO, you've also breached your SLA.

   By setting a stricter SLO (e.g., SLO: 99.9%, SLA: 99.5%), you get:
   1. **Warning time**: When you miss SLO, you know to focus on reliability before SLA breach
   2. **Buffer**: Normal variation won't breach SLA
   3. **Improvement incentive**: Teams aim higher than the minimum

   The gap between SLO and SLA is your safety margin.
   </details>

3. **How do error budgets help resolve the tension between velocity and reliability?**
   <details>
   <summary>Answer</summary>

   Without error budgets, "ship features" and "be reliable" are subjective goals that conflict—whoever argues loudest wins.

   With error budgets:
   - Reliability is quantified: "We have X minutes of budget"
   - Velocity is enabled: "Budget remaining? Ship fast"
   - Reliability is protected: "Budget depleted? Focus on reliability"

   The decision is data-driven, not political. Product teams know features will ship when budget is healthy. Engineering knows reliability will be prioritized when budget is depleted. Both sides get what they need.
   </details>

4. **What makes a good SLI?**
   <details>
   <summary>Answer</summary>

   A good SLI is:

   1. **Measurable**: You can actually collect the data reliably
   2. **User-centric**: Reflects what users experience, not internal metrics
   3. **Proportional**: Worse SLI = worse user experience (linear relationship)
   4. **Actionable**: Your team can influence it
   5. **Captured at the edge**: Measured where users connect, not deep in the stack

   Example: "Request latency p99 measured at the load balancer" is better than "API server response time mean" because it's user-centric (what they actually experience), proportional (slower = worse), and measured at the edge.
   </details>

---

## Hands-On Exercise

**Task**: Define SLIs and SLOs for a service and create an error budget dashboard.

**Part A: Define SLIs (10 minutes)**

Choose a service you work with (or use the example "User API" service).

Define SLIs using this template:

| SLI Name | Definition | Measurement Method | Good Threshold |
|----------|------------|-------------------|----------------|
| Availability | % of successful responses | (2xx + 3xx) / total at LB | ≥99.9% |
| Latency | p99 request duration | Histogram at LB | ≤200ms |
| | | | |
| | | | |

**Part B: Set SLOs (10 minutes)**

For each SLI, set an SLO:

| SLI | SLO Target | Error Budget (monthly) | Rationale |
|-----|------------|----------------------|-----------|
| Availability | 99.9% | 43.2 minutes | Users expect high availability |
| Latency p99 | 200ms | 0.1% of requests | UX degrades above 200ms |
| | | | |

**Part C: Calculate Current Status (10 minutes)**

Using real data from your service (or the sample data below):

Sample data for this month:
- Total requests: 5,000,000
- Failed requests (5xx): 3,500
- Requests over 200ms: 6,000
- Downtime: 15 minutes

Calculate:
1. Current availability: ____%
2. Current latency compliance: ____%
3. Error budget consumed (availability): ____ minutes
4. Error budget remaining: ____ minutes
5. Current policy level: ____

**Part D: Create Improvement Plan (10 minutes)**

Based on your calculations:

1. Which SLI needs the most attention?
2. What would you investigate first?
3. What's one action that would improve it?

| Priority | Issue | Proposed Action | Expected Impact |
|----------|-------|-----------------|-----------------|
| 1 | | | |
| 2 | | | |

**Success Criteria**:
- [ ] At least 3 SLIs defined
- [ ] SLOs set with rationale
- [ ] Current status calculated correctly
- [ ] Improvement plan with prioritized actions

**Sample Answers**:

<details>
<summary>Check your calculations</summary>

Using the sample data:
1. Availability: (5,000,000 - 3,500) / 5,000,000 = 99.93%
2. Latency compliance: (5,000,000 - 6,000) / 5,000,000 = 99.88%
3. Error budget consumed: 15 minutes
4. Error budget remaining: 43.2 - 15 = 28.2 minutes (65% remaining)
5. Policy level: Yellow (50-75% remaining) - Normal operations but increased monitoring

Analysis:
- Latency (99.88%) is below SLO (99.9%)—needs attention
- Availability (99.93%) is meeting SLO (99.9%)—healthy
- Focus on latency improvements

</details>

---

## Further Reading

- **"Site Reliability Engineering"** - Google. Chapters 4 (SLOs), 5 (Error Budgets), and 15 (Postmortems).

- **"The Art of SLOs"** - Workshop materials from Google. Practical guidance on implementing SLOs.

- **"Implementing Service Level Objectives"** - Alex Hidalgo. Deep dive into SLO implementation.

---

## Reliability Engineering: What's Next?

Congratulations! You've completed the Reliability Engineering foundation. You now understand:

- What reliability means and how to measure it
- How systems fail and how to design for failure
- Redundancy patterns for fault tolerance
- SLIs, SLOs, and error budgets for continuous improvement

**Where to go from here:**

| Your Interest | Next Track |
|---------------|------------|
| Understanding what's happening | [Observability Theory](../observability-theory/) |
| Operating reliable systems | [SRE Discipline](../../disciplines/sre/) |
| Building secure systems | [Security Principles](../security-principles/) |
| Distributed system challenges | [Distributed Systems](../distributed-systems/) |

---

## Track Summary

| Module | Key Takeaway |
|--------|--------------|
| 2.1 | Reliability is measurable; each nine is 10x harder |
| 2.2 | Predict failure modes with FMEA; design degradation paths |
| 2.3 | Redundancy enables survival; but test your failover |
| 2.4 | SLIs measure, SLOs target, error budgets enable decisions |

*"Hope is not a strategy. Measure reliability, set targets, and engineer toward them."*
