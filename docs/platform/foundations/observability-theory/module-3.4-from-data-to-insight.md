# Module 3.4: From Data to Insight

> **Complexity**: `[MEDIUM]`
>
> **Time to Complete**: 30-35 minutes
>
> **Prerequisites**: [Module 3.3: Instrumentation Principles](module-3.3-instrumentation-principles.md)
>
> **Track**: Foundations

---

## Why This Module Matters

You've instrumented your services. Logs are flowing, metrics are being scraped, traces are being collected. Now what?

Having data isn't the same as having understanding. The real value of observability comes from turning data into **insight**—answering questions, detecting problems, and building mental models of system behavior.

This module teaches you how to use observability data effectively: asking the right questions, building useful alerts, debugging systematically, and developing intuition about your systems.

> **The Medical Analogy**
>
> A doctor doesn't just collect test results—they interpret them. Blood pressure, heart rate, and lab results are data. A diagnosis is insight. The same data can mean different things in different contexts. Observability is similar: metrics, logs, and traces are raw data. Understanding why your system behaves the way it does is insight.

---

## What You'll Learn

- How to ask good questions of your observability data
- Building effective alerts (signal vs. noise)
- Debugging systematically with observability
- Dashboards that tell stories
- Building mental models of system behavior

---

## Part 1: Asking Questions

### 1.1 The Question Hierarchy

Not all questions are equally useful. Start broad, narrow down:

```
THE QUESTION HIERARCHY
═══════════════════════════════════════════════════════════════

Level 1: DETECTION
─────────────────────────────────────────────────────────────
"Is something wrong?"
    → Alerts, SLO dashboards, error rates
    → Answers: Yes/No

Level 2: SCOPE
─────────────────────────────────────────────────────────────
"How bad is it? Who's affected?"
    → Break down by dimension: region, user type, endpoint
    → Answers: X% of users, Y region, Z feature

Level 3: LOCALIZATION
─────────────────────────────────────────────────────────────
"Where is the problem?"
    → Service dependency analysis, trace flamegraphs
    → Answers: Service X, database Y, function Z

Level 4: ROOT CAUSE
─────────────────────────────────────────────────────────────
"Why is this happening?"
    → Logs, code, recent changes
    → Answers: Bug in version 2.3.1, config change, external dependency
```

### 1.2 Good Questions vs. Bad Questions

```
QUESTION QUALITY
═══════════════════════════════════════════════════════════════

BAD QUESTIONS (vague, hard to answer)
─────────────────────────────────────────────────────────────
"Why is the site slow?"
    → What is "slow"? For whom? Since when?

"Is everything okay?"
    → Define "okay"

"What happened yesterday?"
    → What specifically?

GOOD QUESTIONS (specific, answerable)
─────────────────────────────────────────────────────────────
"What's the p99 latency for /api/checkout in the last hour?"
    → Specific metric, specific endpoint, specific timeframe

"Which users experienced errors during the deploy at 3pm?"
    → Specific event, specific population

"What changed between 2pm (working) and 3pm (broken)?"
    → Specific comparison, specific times
```

### 1.3 The Exploratory Investigation Pattern

```
EXPLORATORY INVESTIGATION
═══════════════════════════════════════════════════════════════

START: "Something is wrong" (symptom)

1. QUANTIFY
   "How wrong? What's the error rate/latency/failure count?"
   → Establishes baseline for comparison

2. SEGMENT
   "Is it all requests or some? Which ones?"
   → Group by: endpoint, user_type, region, version, time
   → Find: Where is the problem concentrated?

3. CORRELATE
   "What else happened at the same time?"
   → Deploys, config changes, dependency issues, traffic spike
   → Find: Potential causes

4. EXEMPLIFY
   "Show me a specific failing request"
   → Trace → Logs → Detailed error
   → Find: Concrete evidence

5. HYPOTHESIZE
   "I think the problem is X because of Y"
   → Test: If X is the problem, what else should be true?

6. VERIFY
   "Let me confirm by checking Z"
   → Additional queries to confirm/refute hypothesis

7. RESOLVE
   "The problem is X, fixed by Y"
   → Document for future reference
```

> **Try This (3 minutes)**
>
> Think of a recent incident. Walk through the investigation pattern:
> - How did you quantify the problem?
> - How did you segment to narrow down?
> - What correlations did you look for?
> - Did you find a specific example to examine?

---

## Part 2: Effective Alerting

### 2.1 Alert Philosophy

```
ALERTING PRINCIPLES
═══════════════════════════════════════════════════════════════

ALERT ONLY WHEN ACTION IS NEEDED
─────────────────────────────────────────────────────────────
If the alert fires and you do nothing → Remove the alert
If the alert fires and you always do the same thing → Automate it
If the alert fires and you investigate → Good alert

ALERT ON SYMPTOMS, NOT CAUSES
─────────────────────────────────────────────────────────────
Bad:  "CPU > 80%"           (cause - might be fine)
Good: "Error rate > 1%"     (symptom - users affected)
Good: "p99 latency > 500ms" (symptom - users affected)

ALERT ON USER IMPACT
─────────────────────────────────────────────────────────────
Would a user notice? Alert.
Would only you notice? Maybe don't alert.

Error budget burn rate > threshold → Users will be affected → Alert
```

### 2.2 SLO-Based Alerting

```
SLO-BASED ALERTS
═══════════════════════════════════════════════════════════════

Instead of arbitrary thresholds, alert based on error budget:

SLO: 99.9% availability (error budget: 43 minutes/month)

Alert conditions:
─────────────────────────────────────────────────────────────
SEVERE (page immediately):
    Error budget burn rate that would exhaust budget in 1 hour
    = 720x normal burn rate
    "At this rate, we're out of budget in 1 hour"

HIGH (page during business hours):
    Error budget burn rate that would exhaust budget in 6 hours
    = 120x normal burn rate
    "At this rate, we're out of budget in 6 hours"

MEDIUM (ticket):
    Error budget burn rate that would exhaust budget in 3 days
    = 10x normal burn rate
    "At this rate, we're out of budget this week"

LOW (dashboard):
    Any error budget consumption
    "We're using budget, but within acceptable range"
```

### 2.3 Reducing Alert Fatigue

| Problem | Cause | Solution |
|---------|-------|----------|
| Too many alerts | Low thresholds | Raise thresholds, use SLO-based |
| Alerts for non-issues | Alerting on causes | Alert on symptoms instead |
| Flapping alerts | Sensitive thresholds | Add duration requirement (5 min) |
| Duplicate alerts | Multiple rules for same issue | Deduplicate, use alert hierarchy |
| Unactionable alerts | No clear response | Add runbook, or delete alert |

```
ALERT HYGIENE CHECKLIST
═══════════════════════════════════════════════════════════════

For each alert, answer:
[ ] Does this require human action?
[ ] Is the action clear? (link to runbook)
[ ] Does this fire rarely enough to be noticed?
[ ] Is the severity appropriate?
[ ] Has this alert been useful in the last 30 days?

If you can't answer "yes" to all → Fix or remove the alert.
```

> **Did You Know?**
>
> Google's SRE teams aim for a 50% "signal ratio"—meaning 50% of pages should be real issues requiring intervention. Below 50%, alerts are too noisy and get ignored. Above 80%, you're probably missing issues because you're not alerting enough.

---

## Part 3: Debugging with Observability

### 3.1 The Debugging Workflow

```
DEBUGGING WORKFLOW
═══════════════════════════════════════════════════════════════

            ┌─────────────────────────────────────────────┐
METRICS ───▶│ Alert fires: Error rate spike              │
            │ Dashboard: 5% errors on /api/checkout      │
            └──────────────────┬──────────────────────────┘
                               │
            ┌──────────────────▼──────────────────────────┐
METRICS ───▶│ Segment: Which errors? Where?              │
            │ 90% of errors from US-West region          │
            │ Started 14:32, correlates with deploy      │
            └──────────────────┬──────────────────────────┘
                               │
            ┌──────────────────▼──────────────────────────┐
TRACES ────▶│ Exemplar: Get example failing trace        │
            │ Trace abc-123: Timeout on payment-service  │
            │ 3 retry attempts, all timed out            │
            └──────────────────┬──────────────────────────┘
                               │
            ┌──────────────────▼──────────────────────────┐
LOGS ──────▶│ Detail: What's in the logs?                │
            │ "Connection refused: payment-db-west-02"   │
            │ Database server is unreachable             │
            └──────────────────┬──────────────────────────┘
                               │
            ┌──────────────────▼──────────────────────────┐
ROOT CAUSE ▶│ payment-db-west-02 in maintenance         │
            │ Failover didn't trigger correctly          │
            └─────────────────────────────────────────────┘
```

### 3.2 Common Debugging Patterns

**"It's slow"**

```
DEBUGGING LATENCY
═══════════════════════════════════════════════════════════════

1. Confirm: What's the actual latency? p50? p99?
2. Scope: All requests or some? Which endpoints?
3. Trace: Get example slow traces
4. Flamegraph: Where is time spent?
   └── Network call to service X: 800ms (80% of time)
5. Drill down: Why is service X slow?
6. Repeat until root cause found
```

**"It's broken"**

```
DEBUGGING ERRORS
═══════════════════════════════════════════════════════════════

1. Confirm: What's the error rate? Error types?
2. Scope: Which users? Which endpoints? Which versions?
3. Compare: What's different about failing requests?
4. Exemplify: Get specific error logs
   └── Stack trace, error message, context
5. Correlate: What changed? Deploy? Config? Dependency?
6. Hypothesize and verify
```

**"It's weird"**

```
DEBUGGING STRANGE BEHAVIOR
═══════════════════════════════════════════════════════════════

1. Define: What exactly is "weird"? Quantify it.
2. Baseline: What's "normal"? Compare to historical data.
3. Isolate: Find the smallest reproducing case.
4. Trace: Follow request through system.
5. Diff: What's different from normal requests?
6. Often: Race condition, caching issue, state dependency
```

### 3.3 Comparison: Then vs. Now

```
COMPARISON QUERIES
═══════════════════════════════════════════════════════════════

"It was working yesterday, now it's broken"

Query pattern:
    Compare: metric_X at time_good vs time_bad

    Example:
    GOOD: 2024-01-15 10:00-12:00, error_rate = 0.1%
    BAD:  2024-01-16 10:00-12:00, error_rate = 5.0%

    Segment by deploy_version:
    GOOD: version 2.3.0, error_rate = 0.1%
    BAD:  version 2.3.1, error_rate = 4.9%

    Conclusion: Version 2.3.1 introduced the problem.

Similar pattern for:
    - Before/after deploy
    - This week vs. last week
    - Failing user vs. working user
```

---

## Part 4: Dashboards That Tell Stories

### 4.1 Dashboard Anti-Patterns

```
DASHBOARD ANTI-PATTERNS
═══════════════════════════════════════════════════════════════

THE WALL OF METRICS
─────────────────────────────────────────────────────────────
┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐
│    ││    ││    ││    ││    ││    ││    ││    │
└────┘└────┘└────┘└────┘└────┘└────┘└────┘└────┘
┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐
│    ││    ││    ││    ││    ││    ││    ││    │
└────┘└────┘└────┘└────┘└────┘└────┘└────┘└────┘

Problem: No hierarchy, everything equal importance
Result: Eyes glaze over, important signals missed

THE VANITY DASHBOARD
─────────────────────────────────────────────────────────────
┌────────────────────────────────────────────────────────────┐
│  REQUESTS TODAY: 1,234,567,890                             │
│  UPTIME: 99.999%                                           │
│  SERVERS: 1,234                                            │
└────────────────────────────────────────────────────────────┘

Problem: Big numbers that never change actionably
Result: Looks impressive, helps no one
```

### 4.2 Good Dashboard Structure

```
DASHBOARD STRUCTURE
═══════════════════════════════════════════════════════════════

LEVEL 1: EXECUTIVE SUMMARY (top)
┌─────────────────────────────────────────────────────────────┐
│  SLO Status: 99.95% (target: 99.9%) ✅                     │
│  Error Budget: 65% remaining                                │
│  Active Incidents: 0                                        │
└─────────────────────────────────────────────────────────────┘
"At a glance: Are we okay?"

LEVEL 2: THE GOLDEN SIGNALS (middle)
┌─────────────────────────────────────────────────────────────┐
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Latency    │  │    Errors    │  │   Traffic    │     │
│  │   p50: 45ms  │  │    0.1%      │  │   1,234/s    │     │
│  │   p99: 200ms │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
"What's the current behavior?"

LEVEL 3: DRILL-DOWN (expandable)
┌─────────────────────────────────────────────────────────────┐
│  By Endpoint:        By Region:        By Version:          │
│  /api/checkout 50ms  US-West 45ms     v2.3.1 48ms          │
│  /api/search   30ms  EU-Central 52ms  v2.3.0 45ms          │
│  /api/user     25ms  AP-South 60ms                          │
└─────────────────────────────────────────────────────────────┘
"Where should I look if something's wrong?"
```

### 4.3 Dashboard Design Principles

| Principle | Why | Example |
|-----------|-----|---------|
| **Hierarchy** | Important things first | SLO status at top, details below |
| **Context** | Show what normal looks like | Current value + historical range |
| **Action** | Link to next step | Click metric → See traces |
| **Consistency** | Same layout across services | Everyone knows where to look |
| **Simplicity** | Only what's needed | Remove metrics nobody looks at |

> **Try This (3 minutes)**
>
> Look at one of your dashboards:
> - Can you tell system health in 5 seconds?
> - Is there a clear hierarchy?
> - Do you know what to click if something's wrong?
> - When did you last remove a panel?

---

## Part 5: Building Mental Models

### 5.1 What is a Mental Model?

A **mental model** is your understanding of how the system actually works—not the documentation, but your intuition built from experience.

```
MENTAL MODEL COMPONENTS
═══════════════════════════════════════════════════════════════

ARCHITECTURE
    "Request comes in at load balancer, goes to API server,
     which calls auth service, then the appropriate backend."

DEPENDENCIES
    "If Redis is down, sessions break. If Postgres is down,
     nothing works. If payment API is slow, checkout is slow."

BEHAVIOR UNDER STRESS
    "Under high load, the API starts queueing requests.
     Past 1000 QPS, we see cascading timeouts."

FAILURE MODES
    "When disk fills, logs stop but service keeps running.
     When memory fills, OOM killer takes random processes."

RECENT CHANGES
    "We deployed v2.3.1 yesterday, added new caching layer
     last week, migrated database replica last month."
```

### 5.2 Building Mental Models

```
HOW TO BUILD MENTAL MODELS
═══════════════════════════════════════════════════════════════

1. WATCH NORMAL BEHAVIOR
   └── What do metrics look like during a normal day?
   └── What's the typical request flow?
   └── What are normal log patterns?

2. WATCH ABNORMAL BEHAVIOR
   └── What happens during incidents?
   └── What breaks first under load?
   └── What error messages appear?

3. TRACE REQUESTS END-TO-END
   └── Pick a request type, follow it through
   └── Understand every service it touches
   └── Know the critical path

4. LEARN FROM POSTMORTEMS
   └── What failed? Why didn't we catch it?
   └── What was the actual impact?
   └── What did we learn about the system?

5. EXPERIMENT (carefully)
   └── What happens if we scale down?
   └── What happens if we add latency?
   └── Chaos engineering builds models
```

### 5.3 Sharing Mental Models

Mental models in one person's head don't scale. Share them:

| Method | When | Example |
|--------|------|---------|
| **Runbooks** | Common scenarios | "If X, do Y because Z" |
| **Architecture diagrams** | System overview | Request flow, dependencies |
| **Postmortems** | After incidents | What happened and why |
| **Pairing** | Onboarding | Debug together, share intuition |
| **Documentation** | Reference | "The system works like this..." |

---

## Did You Know?

- **NASA's Mission Control** uses a layered dashboard system called "Flight Director Console." The top level shows overall mission health. Lower levels show subsystem details. This hierarchy-based design is over 60 years old but still the gold standard.

- **The term "runbook"** comes from IBM mainframe operations in the 1960s. Operators had physical books of procedures to "run" for common scenarios. Digital runbooks serve the same purpose.

- **Expert intuition is real**. Studies show experienced operators can often sense something is wrong before any alert fires—they've internalized subtle patterns. This is the goal of building mental models.

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Alerting on everything | Alert fatigue, ignored pages | Alert on symptoms, not causes |
| Dashboard sprawl | Can't find the right dashboard | Hierarchy, templates, linking |
| No runbooks | Every incident is new | Document common scenarios |
| Siloed investigation | Can't correlate across signals | Shared trace IDs, linked tools |
| Over-reliance on dashboards | Miss issues dashboards don't show | Combine with exploration |
| Not sharing knowledge | One expert, team bottleneck | Postmortems, pairing, docs |

---

## Quiz

1. **Why should you alert on symptoms rather than causes?**
   <details>
   <summary>Answer</summary>

   **Alerting on symptoms** (error rate, latency) tells you when users are affected. You know action is needed.

   **Alerting on causes** (CPU, memory, connections) often fires when nothing is wrong. High CPU might be fine if latency is good. Low disk might never cause issues.

   Examples:
   - Bad: "CPU > 80%" (might be fine, might not be)
   - Good: "Error rate > 1%" (users definitely affected)
   - Bad: "DB connections > 90%" (might handle it fine)
   - Good: "p99 latency > 500ms" (users definitely affected)

   When you alert on symptoms, every alert means user impact. When you alert on causes, you're often paged for non-issues.
   </details>

2. **What's the benefit of SLO-based alerting over threshold-based alerting?**
   <details>
   <summary>Answer</summary>

   **Threshold-based**: "Alert if error rate > X" - arbitrary number, doesn't consider time or budget.

   **SLO-based**: "Alert if error budget burn rate threatens monthly target" - tied to actual user impact over time.

   Benefits of SLO-based:
   1. **Context-aware**: A 1% error rate might be fine for 5 minutes but not for 5 hours
   2. **Budget-preserving**: Alerts fire when you'll actually miss your SLO
   3. **Less noise**: Brief spikes don't page if budget is healthy
   4. **Proportional severity**: Burn rate determines urgency (1 hour vs 6 hours to exhaustion)

   SLO-based alerts say "this matters" rather than "this is different from arbitrary threshold."
   </details>

3. **What is the exploratory investigation pattern and why is it effective?**
   <details>
   <summary>Answer</summary>

   The exploratory investigation pattern is a systematic approach:
   1. **Quantify** - How bad is it?
   2. **Segment** - Which subset is affected?
   3. **Correlate** - What else happened?
   4. **Exemplify** - Show me a specific case
   5. **Hypothesize** - I think X is the cause
   6. **Verify** - Test the hypothesis
   7. **Resolve** - Fix and document

   It's effective because:
   - **Systematic**: Doesn't skip steps or jump to conclusions
   - **Evidence-based**: Each step produces data to inform the next
   - **Narrowing**: Each step reduces the scope of the problem
   - **Verifiable**: Hypotheses are tested, not assumed

   Without a pattern, debugging becomes random guessing. With a pattern, you efficiently converge on the answer.
   </details>

4. **Why are mental models important for operations?**
   <details>
   <summary>Answer</summary>

   Mental models are your internalized understanding of how the system works. They're important because:

   1. **Speed**: You know what to check without reading documentation
   2. **Intuition**: You can sense when something is "off" even without alerts
   3. **Prediction**: You can anticipate what will happen (e.g., "if we lose Redis, sessions break")
   4. **Context**: You understand why things are designed the way they are
   5. **Efficiency**: You skip irrelevant paths and focus on likely causes

   Without mental models, every incident is like operating a new system—slow, methodical, starting from scratch. With mental models, you leverage experience to solve problems faster.

   The challenge: Mental models are in people's heads. Sharing them through runbooks, postmortems, and pairing is essential for team resilience.
   </details>

---

## Hands-On Exercise

**Task**: Design an observability workflow for a common scenario.

**Scenario**: You receive an alert: "p99 latency for /api/search exceeded 500ms"

**Part 1: Investigation Plan (10 minutes)**

Write out your investigation steps using the exploratory pattern:

| Step | Question | How You'd Answer (tool/query) |
|------|----------|-------------------------------|
| Quantify | What's the actual p99? How long has it been elevated? | |
| Segment | All search requests or some? Which dimensions? | |
| Correlate | What changed? Deploys? Traffic spike? | |
| Exemplify | Get a specific slow trace | |
| Hypothesize | What do you think is the cause? | |
| Verify | How would you confirm? | |

**Part 2: Alert Design (10 minutes)**

Design an SLO-based alert for this scenario:

| Element | Your Design |
|---------|-------------|
| SLO target | p99 latency for /api/search ≤ ___ms |
| Measurement window | ___ minutes |
| Severe alert | Burn rate = ___ (exhausts budget in ___ hours) |
| High alert | Burn rate = ___ (exhausts budget in ___ hours) |
| Runbook link | Steps to investigate (from Part 1) |

**Part 3: Dashboard Design (10 minutes)**

Sketch a simple dashboard for search health:

```
Top row (Executive Summary):
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  [What should be here?]                                    │
│                                                            │
└────────────────────────────────────────────────────────────┘

Middle row (Golden Signals):
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│                  │ │                  │ │                  │
│  [Panel 1]       │ │  [Panel 2]       │ │  [Panel 3]       │
│                  │ │                  │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘

Bottom row (Drill-down):
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  [What breakdowns would be useful?]                        │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Success Criteria**:
- [ ] Investigation plan covers all steps of exploratory pattern
- [ ] Alert design includes SLO target and multiple severity levels
- [ ] Dashboard has clear hierarchy (summary → signals → details)
- [ ] Each dashboard panel has a clear purpose

---

## Further Reading

- **"Practical Monitoring"** - Mike Julian. Excellent coverage of alerting philosophy and dashboard design.

- **"The Art of Monitoring"** - James Turnbull. Comprehensive guide to building monitoring systems.

- **"Thinking in Systems"** - Donella Meadows. Foundational book on building mental models of complex systems.

---

## Observability Theory: What's Next?

Congratulations! You've completed the Observability Theory foundation. You now understand:

- What observability is and how it differs from monitoring
- The three pillars: logs, metrics, traces
- How to instrument systems effectively
- How to turn data into insight

**Where to go from here:**

| Your Interest | Next Track |
|---------------|------------|
| Implementing observability | [Observability Toolkit](../../toolkits/observability/) |
| Operating with observability | [SRE Discipline](../../disciplines/sre/) |
| Security observability | [Security Principles](../security-principles/) |
| Foundational concepts | [Distributed Systems](../distributed-systems/) |

---

## Track Summary

| Module | Key Takeaway |
|--------|--------------|
| 3.1 | Observability lets you ask questions you didn't predict; monitoring answers predefined questions |
| 3.2 | Logs (detail), metrics (aggregation), traces (flow)—connected by correlation IDs |
| 3.3 | Instrument boundaries and business operations; keep cardinality bounded; sample traces |
| 3.4 | Alert on symptoms not causes; debug systematically; build and share mental models |

*"The goal isn't to have all the data. The goal is to understand the system."*
