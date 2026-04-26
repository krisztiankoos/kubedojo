---
revision_pending: true
title: "Module 3.4: Observability Fundamentals"
slug: k8s/kcna/part3-cloud-native-architecture/module-3.4-observability-fundamentals
sidebar:
  order: 5
---
> **Complexity**: `[MEDIUM]` - Observability concepts
>
> **Time to Complete**: 25-30 minutes
>
> **Prerequisites**: Module 3.3 (Cloud Native Patterns)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Explain** the three pillars of observability: logs, metrics, and traces
2. **Compare** monitoring (known-unknowns) with observability (unknown-unknowns)
3. **Identify** which observability signal to use for different debugging scenarios
4. **Evaluate** observability maturity levels and what each level enables for operations teams

---

## Why This Module Matters

You can't fix what you can't see. **Observability** is how you understand what's happening inside your systems. It's especially critical in distributed systems where debugging is complex. KCNA tests your understanding of observability pillars and practices.

---

## What is Observability?

```
┌─────────────────────────────────────────────────────────────┐
│              OBSERVABILITY                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Definition:                                               │
│  ─────────────────────────────────────────────────────────  │
│  The ability to understand the internal state of a system │
│  by examining its external outputs                        │
│                                                             │
│  Monitoring vs Observability:                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  MONITORING:                                               │
│  "Is the system working?"                                 │
│  • Pre-defined metrics                                    │
│  • Known failure modes                                    │
│  • Dashboards and alerts                                  │
│                                                             │
│  OBSERVABILITY:                                            │
│  "Why isn't the system working?"                          │
│  • Explore unknown problems                               │
│  • Debug novel issues                                     │
│  • Understand system behavior                             │
│                                                             │
│  Monitoring is a subset of observability                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## The Three Pillars

```
┌─────────────────────────────────────────────────────────────┐
│              THREE PILLARS OF OBSERVABILITY                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   METRICS   │  │    LOGS     │  │   TRACES    │         │
│  │             │  │             │  │             │         │
│  │  Numbers    │  │  Events     │  │  Requests   │         │
│  │  over time  │  │  text       │  │  across     │         │
│  │             │  │             │  │  services   │         │
│  │  "How much?"│  │  "What?"    │  │  "Where?"   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  Together they answer:                                     │
│  • What is happening? (metrics)                           │
│  • What exactly happened? (logs)                          │
│  • How did it happen across services? (traces)           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Think of observability like diagnosing a patient in a hospital:
- **Metrics** are the **Vitals** (heart rate, blood pressure). They tell you *if* something is wrong right now.
- **Traces** are the **MRI / X-ray**. They show you exactly *where* the problem is across the entire body (the distributed system).
- **Logs** are the **Patient History**. They give you the detailed text notes of *what* exactly happened at a specific time.

---

> **Pause and predict**: Monitoring tells you "the system is down." Observability tells you "why the system is down." What type of data would you need beyond simple up/down checks to understand why a checkout page suddenly became slow across a microservices architecture?

## Metrics

**Metrics** are numerical measurements over time:

```
┌─────────────────────────────────────────────────────────────┐
│              METRICS                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  What metrics measure:                                     │
│  ─────────────────────────────────────────────────────────  │
│  • Request rate (requests/second)                         │
│  • Error rate (errors/second)                             │
│  • Duration (response time)                               │
│  • Saturation (CPU %, memory %)                          │
│                                                             │
│  Example metric:                                          │
│  ─────────────────────────────────────────────────────────  │
│  http_requests_total{method="GET", status="200"} 1234    │
│        │               │                          │       │
│        │               │                          │       │
│     metric name     labels/tags               value       │
│                                                             │
│  Time series:                                             │
│  ─────────────────────────────────────────────────────────  │
│  Value                                                     │
│    │                                                       │
│ 100├      ┌──┐                                            │
│    │  ┌──┐│  │   ┌──┐                                    │
│  50├──┘  └┘  └───┘  └──┐                                 │
│    │                     └──                              │
│    └─────────────────────────→ Time                      │
│                                                             │
│  Metric types:                                            │
│  • Counter: Only goes up (requests, errors)              │
│  • Gauge: Goes up and down (temperature, memory)         │
│  • Histogram: Distribution of values (latency buckets)   │
│  • Summary: Statistical distribution (percentiles)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### The RED Method

For services, track:

| Metric | Description |
|--------|-------------|
| **R**ate | Requests per second |
| **E**rrors | Failed requests per second |
| **D**uration | Time per request |

### The USE Method

For resources, track:

| Metric | Description |
|--------|-------------|
| **U**tilization | % time resource is busy |
| **S**aturation | Work queued/waiting |
| **E**rrors | Error count |

---

## Logs

**Logs** are timestamped records of events:

```
┌─────────────────────────────────────────────────────────────┐
│              LOGS                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  What logs capture:                                        │
│  ─────────────────────────────────────────────────────────  │
│  • Application events                                      │
│  • Errors and stack traces                                │
│  • Audit trails                                           │
│  • Debug information                                       │
│                                                             │
│  Log example:                                              │
│  ─────────────────────────────────────────────────────────  │
│  2024-01-15T10:23:45.123Z INFO [order-service]            │
│    orderId=12345 customerId=67890 action=created          │
│    "Order created successfully"                           │
│                                                             │
│  Log levels:                                               │
│  ─────────────────────────────────────────────────────────  │
│  DEBUG → INFO → WARN → ERROR → FATAL                      │
│  (verbose)              (critical)                        │
│                                                             │
│  Structured logging (recommended):                        │
│  ─────────────────────────────────────────────────────────  │
│  {                                                        │
│    "timestamp": "2024-01-15T10:23:45.123Z",              │
│    "level": "INFO",                                       │
│    "service": "order-service",                           │
│    "orderId": "12345",                                   │
│    "message": "Order created successfully"               │
│  }                                                        │
│                                                             │
│  Benefits of structured logs:                             │
│  • Easily searchable                                      │
│  • Machine parseable                                      │
│  • Consistent format                                      │
│                                                             │
│  In Kubernetes:                                           │
│  ─────────────────────────────────────────────────────────  │
│  Containers write to stdout/stderr                        │
│  Log collectors (Fluentd, Fluent Bit) gather logs        │
│  Send to storage (Elasticsearch, Loki)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Traces

**Traces** track requests across distributed systems:

```
┌─────────────────────────────────────────────────────────────┐
│              DISTRIBUTED TRACING                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Problem: Request flows through multiple services         │
│  ─────────────────────────────────────────────────────────  │
│  User → API Gateway → Order Service → Payment → Database │
│                                                             │
│  Where did it slow down? Where did it fail?              │
│                                                             │
│  Solution: Traces                                         │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Trace: The complete journey of a request                │
│  Span: One operation within a trace                      │
│                                                             │
│  Trace ID: abc-123                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                      │   │
│  │ ├── API Gateway (span 1)                           │   │
│  │ │   └── 50ms                                       │   │
│  │ │                                                   │   │
│  │ ├── Order Service (span 2)                         │   │
│  │ │   └── 120ms                                      │   │
│  │ │   │                                              │   │
│  │ │   ├── Payment Service (span 3)                  │   │
│  │ │   │   └── 200ms  ← Slow!                        │   │
│  │ │   │                                              │   │
│  │ │   └── Database (span 4)                         │   │
│  │ │       └── 30ms                                   │   │
│  │ │                                                   │   │
│  │ └── Total: 400ms                                   │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Trace ID propagated through all services                 │
│  Each service adds its span                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Trace Terminology

| Term | Description |
|------|-------------|
| **Trace** | Complete request journey (all spans) |
| **Span** | Single operation within trace |
| **Trace ID** | Unique identifier for the trace |
| **Span ID** | Unique identifier for the span |
| **Parent Span** | The calling operation |
| **Context propagation** | Passing trace ID between services |

---

## Connecting the Pillars

```
┌─────────────────────────────────────────────────────────────┐
│              CONNECTING METRICS, LOGS, TRACES              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Scenario: Users report slow checkout                     │
│                                                             │
│  1. METRICS show the problem                              │
│     ─────────────────────────────────────────────────────  │
│     Dashboard: checkout_duration_p99 = 5s (normally 1s)  │
│     "Checkout is slow, but why?"                         │
│                                                             │
│  2. TRACES identify where                                 │
│     ─────────────────────────────────────────────────────  │
│     Trace shows payment service taking 4s               │
│     "Payment is the bottleneck, but why?"               │
│                                                             │
│  3. LOGS explain why                                      │
│     ─────────────────────────────────────────────────────  │
│     Log: "Connection pool exhausted, waiting for         │
│           connection to external payment gateway"        │
│     "Ah! Connection pool needs tuning"                   │
│                                                             │
│  The journey:                                              │
│  Metrics (detect) → Traces (locate) → Logs (diagnose)   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **War Story: The Black Friday Outage**
> During a massive holiday sale, the monitoring dashboard lit up red: order success rates plummeted (Metrics/Vitals). The team didn't panic. They pulled up the tracing tool, which showed that requests were getting stuck specifically in the `inventory-service` span (Traces/MRI). Armed with the Trace ID, they queried the logging system. The logs revealed the smoking gun: `ERR: Connection timeout to legacy database: max_connections exceeded` (Logs/History). Because they had all three pillars connected, a critical outage was diagnosed and mitigated in 4 minutes instead of 4 hours.

---

> **Stop and think**: You have metrics, logs, and traces. A user reports slow checkout. Using the three pillars in sequence, how would you diagnose the issue? Which pillar do you start with, and why?

## Alerting

```
┌─────────────────────────────────────────────────────────────┐
│              ALERTING                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Turn metrics into notifications                          │
│                                                             │
│  ┌─────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │ Metrics │ →  │ Alert Rules │ →  │ Notification│        │
│  │         │    │ "If X > Y"  │    │ Slack/Page │        │
│  └─────────┘    └─────────────┘    └─────────────┘        │
│                                                             │
│  Good alerting practices:                                 │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  • Alert on symptoms, not causes                          │
│    Bad:  "CPU > 90%"                                     │
│    Good: "Response time > 500ms"                         │
│                                                             │
│  • Avoid alert fatigue                                    │
│    Too many alerts = ignore them all                      │
│                                                             │
│  • Actionable alerts                                      │
│    If you can't act on it, don't alert                   │
│                                                             │
│  • Severity levels                                        │
│    Critical: Page someone NOW                            │
│    Warning: Check tomorrow                               │
│    Info: FYI only                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Did You Know?

- **Observability term origin** - Comes from control theory, where a system is "observable" if internal states can be determined from external outputs.

- **OpenTelemetry is unifying observability** - It provides a single standard for metrics, traces, and logs, replacing vendor-specific instrumentation.

- **Cardinality matters** - High-cardinality labels (like user ID) in metrics can explode storage costs. Be careful what you label.

- **The 4 Golden Signals** - Google's SRE book recommends: latency, traffic, errors, and saturation as the key metrics for any service.

---

## Common Mistakes

| Mistake | Why It Hurts | Correct Understanding |
|---------|--------------|----------------------|
| Only using one pillar | Incomplete picture | Use all three together |
| Unstructured logs | Hard to search | Use structured JSON logs |
| Too many alerts | Alert fatigue | Alert on symptoms, not causes |
| Not propagating trace context | Broken traces | Pass trace IDs between services |
| High cardinality metrics | Explodes storage costs | Use labels with bounded values |
| Alerting on internal causes | Unnecessary wake-ups | Alert on user-facing symptoms |
| Logging sensitive data | Security breaches | Sanitize and mask PII |
| Infinite metric retention | Consumes expensive storage | Downsample older metrics |

---

## Hands-On Exercise: Observability Triage

**Scenario**: You are the on-call engineer for a cloud-native e-commerce platform. Users are reporting that the shopping cart is occasionally failing to load. You need to use the three pillars of observability to find the root cause.

**Success Criteria**:
- [ ] **Identify the symptom**: Look at the RED metrics dashboard and find the service with the highest latency (Duration).
- [ ] **Follow the trace**: Open the distributed tracing tool, filter for traces from the slow service, and find the longest span.
- [ ] **Check the logs**: Using the Trace ID from the slowest trace, query the centralized logging system to see the specific error or timeout message.
- [ ] **Find the root cause**: Combine the data to identify that the `inventory-service` database connection pool was exhausted.

---

## Quiz

1. **Users report that the checkout page is slow. Your dashboard shows the checkout_duration_p99 metric spiked from 500ms to 5 seconds. You have metrics, logs, and traces available. Walk through how you would use each pillar to diagnose the root cause.**
   <details>
   <summary>Answer</summary>
   Start with metrics: the dashboard already shows checkout latency is elevated, confirming the problem is real and quantifying its severity. Next, use traces: find a slow checkout trace and examine its spans to see which service in the chain is taking the most time (e.g., the payment service span shows 4 seconds instead of the usual 200ms). Finally, check logs: look at the payment service logs during the same time window for the specific trace ID, and you might find "Connection pool exhausted, waiting for available connection to payment gateway." The investigation flow is: metrics (detect) then traces (locate) then logs (diagnose).
   </details>

2. **An alerting system sends 50 alerts per day. The on-call engineer starts ignoring most of them because many are "CPU above 80%" alerts that do not correlate with actual user impact. What is this problem called, and how should the alerting strategy change?**
   <details>
   <summary>Answer</summary>
   This is alert fatigue -- when too many non-actionable alerts train engineers to ignore all alerts, including real ones. The fix is to alert on symptoms (user-facing impact) rather than causes (internal metrics). Replace "CPU above 80%" with "response time above 500ms for 5 minutes" or "error rate above 1%." A CPU spike that does not affect users should not page someone at 3 AM. Every alert should be actionable: if receiving the alert does not require immediate human action, it should be downgraded to a warning or informational notification.
   </details>

3. **Your microservice application writes logs in plain text format like `Error: payment failed for order 12345`. A colleague suggests switching to structured JSON logging. Why would this change matter when you have 200 services producing millions of log lines per day?**
   <details>
   <summary>Answer</summary>
   At scale, unstructured text logs become nearly impossible to search and analyze. Finding all payment failures requires regex parsing that is fragile and slow. Structured JSON logs like `{"level":"error","service":"payment","orderId":"12345","message":"payment failed"}` are machine-parseable, enabling fast queries (filter by service, orderId, or level), consistent across all services, and can be automatically indexed by log aggregation systems like Elasticsearch or Loki. With 200 services and millions of lines, the ability to query `service=payment AND level=error AND orderId=12345` in seconds instead of grepping through raw text is the difference between a 5-minute diagnosis and a 2-hour investigation.
   </details>

4. **A distributed trace shows that a request took 800ms total, with the API Gateway span at 50ms, Order Service at 120ms, and Database at 30ms. But these spans only add up to 200ms, not 800ms. What could explain the missing 600ms?**
   <details>
   <summary>Answer</summary>
   The missing time likely comes from a service that is not instrumented with tracing or where trace context propagation is broken. If the Order Service calls a Payment Service that does not propagate the trace ID, that span will be missing from the trace. The 600ms gap is the time spent in uninstrumented services. This is a common problem when adopting distributed tracing incrementally. The fix is to ensure all services in the call chain propagate trace context (via headers like `traceparent` or `x-b3-traceid`) and have tracing instrumentation. OpenTelemetry SDKs make this easier by providing consistent instrumentation across languages.
   </details>

5. **Your team monitors a Kubernetes service using the RED method (Rate, Errors, Duration) and notices that the error rate suddenly jumped from 0.1% to 5%. However, the rate (requests per second) dropped by 50% at the same time. What might explain both signals occurring simultaneously?**
   <details>
   <summary>Answer</summary>
   A likely explanation is that the service is partially failing, causing clients to receive errors and give up (reducing total request rate through timeouts or circuit breakers on the client side). Alternatively, a deployment went bad -- new Pods are returning errors while old Pods were taken out of service, and the load balancer sees fewer healthy endpoints (reducing capacity and thus throughput). Another possibility: an upstream service is failing, sending fewer requests downstream (lower rate) and the requests that do arrive trigger errors due to missing dependencies. The combination of increased error rate and decreased request rate is a strong signal of a systemic problem rather than just increased load.
   </details>

6. **A developer adds a `user_id` label to the `http_requests_total` metric to track how many requests each individual user makes. The system has 5 million active users. Within an hour, the Prometheus monitoring server crashes out of memory. What concept did the developer violate?**
   <details>
   <summary>Answer</summary>
   The developer caused a cardinality explosion. In time-series databases like Prometheus, every unique combination of labels creates a brand new time series. By adding a label with 5 million possible values, they instantly created 5 million new time series in memory. Labels should only be used for bounded, low-cardinality data like HTTP status codes, while high-cardinality data should be stored in logs or traces.
   </details>

7. **During a security audit, the team discovers that plain-text passwords and credit card numbers are visible in the centralized logging system. How should the team modify their observability practices to prevent this while still being able to debug issues?**
   <details>
   <summary>Answer</summary>
   The team needs to implement log sanitization and strict structured logging. Instead of logging raw HTTP request payloads or full database queries, they should log specific, safe fields like user IDs and action types. Any sensitive data must be explicitly masked or dropped before the log is written to the output stream. Structured logging makes this easier because security filters can automatically redact specific JSON keys before they leave the application.
   </details>

8. **Your team is defining alerts for a new microservice. Engineer A wants to alert when CPU usage exceeds 85%. Engineer B wants to alert when the 99th percentile response time exceeds 2 seconds. Which approach aligns with modern site reliability engineering (SRE) practices and why?**
   <details>
   <summary>Answer</summary>
   Engineer B's approach is correct because it alerts on a symptom that directly impacts the user experience. Alerting on a cause like high CPU usage often leads to alert fatigue, as a background batch job might legitimately use 100% CPU without slowing down user requests. You should monitor causes on dashboards for debugging purposes, but only page humans for symptoms like latency or elevated error rates. Every alert that wakes an engineer should represent a real, actionable problem.
   </details>

---

## Summary

**Observability**:
- Understanding internal state from external outputs
- Goes beyond monitoring (known issues)
- Enables exploring unknown problems

**Three pillars**:
- **Metrics**: Numerical data over time
- **Logs**: Event records with context
- **Traces**: Request paths across services

**Methods**:
- **RED**: Rate, Errors, Duration (services)
- **USE**: Utilization, Saturation, Errors (resources)
- **4 Golden Signals**: Latency, traffic, errors, saturation

**Best practices**:
- Use all three pillars together
- Structured logging
- Alert on symptoms
- Propagate trace context

---

## Next Module

[Module 3.5: Observability Tools](../module-3.5-observability-tools/) - Prometheus, Grafana, Jaeger, and other observability tools in Kubernetes.