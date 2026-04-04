---
title: "Module 1.4: Observability Fundamentals"
slug: prerequisites/modern-devops/module-1.4-observability
sidebar:
  order: 5
---
> **Complexity**: `[MEDIUM]` - Critical operational skill
>
> **Time to Complete**: 35-40 minutes
>
> **Prerequisites**: Basic understanding of distributed systems

---

## What You'll Be Able to Do

After this module, you will be able to:
- **Explain** the three pillars of observability (metrics, logs, traces) and what questions each answers
- **Distinguish** between monitoring ("is it broken?") and observability ("why is it broken?")
- **Describe** how Prometheus, Grafana, and Loki work together in a typical K8s stack
- **Design** basic SLIs/SLOs for a web application and explain why they matter more than uptime %

---

## Why This Module Matters

"Is the system working?" seems like a simple question. In distributed systems like Kubernetes, it's not. Applications span multiple pods, nodes, and services. Observability gives you the ability to understand what's happening inside your system based on its external outputs. Without it, you're flying blind.

---

## What is Observability?

Observability is **the ability to understand the internal state of a system by examining its outputs**.

```
┌─────────────────────────────────────────────────────────────┐
│              MONITORING vs OBSERVABILITY                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  MONITORING (Traditional)                                   │
│  "Is it up? Is it slow?"                                   │
│  - Predefined dashboards                                   │
│  - Known failure modes                                     │
│  - Reactive: alert when threshold breached                 │
│                                                             │
│  OBSERVABILITY (Modern)                                     │
│  "Why is it slow? What's different?"                       │
│  - Explore arbitrary questions                             │
│  - Discover unknown failure modes                          │
│  - Proactive: understand before it breaks                  │
│                                                             │
│  Key insight: Monitoring tells you WHAT is wrong           │
│               Observability tells you WHY                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **Pause and predict**: If a new microservice is deployed and immediately crashes due to an unforeseen memory leak, will traditional monitoring or modern observability be more useful for diagnosing the root cause?

---

## The Three Pillars

```
┌─────────────────────────────────────────────────────────────┐
│              THREE PILLARS OF OBSERVABILITY                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   METRICS   │  │    LOGS     │  │   TRACES    │        │
│  │             │  │             │  │             │        │
│  │  Numbers    │  │  Events     │  │  Requests   │        │
│  │  over time  │  │  with text  │  │  across     │        │
│  │             │  │             │  │  services   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │
│         ▼                ▼                ▼                │
│  "CPU at 90%"    "Error: DB      "Request took           │
│  "5xx errors     connection      300ms: 150ms in         │
│   increasing"    failed"         service A, 150ms        │
│                                  in service B"           │
│                                                             │
│  WHEN to use:    WHEN to use:    WHEN to use:            │
│  - Dashboards    - Debugging     - Performance           │
│  - Alerting      - Auditing      - Dependencies          │
│  - Trends        - Security      - Bottlenecks           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Metrics

Metrics are **numeric measurements collected over time**. They are highly efficient to store and query.

### Types of Metrics

```
Counter (always increases):
  - http_requests_total
  - errors_total
  - bytes_sent_total

Gauge (can go up or down):
  - temperature_celsius
  - memory_usage_bytes
  - active_connections

Histogram (distribution):
  - request_duration_seconds
  - Shows: p50, p90, p99 latencies
```

### Prometheus (The Standard)

```yaml
# Prometheus collects metrics by scraping endpoints
# Your app exposes metrics at /metrics

# Example metrics endpoint output:
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/api",status="200"} 1234
http_requests_total{method="POST",path="/api",status="500"} 12

# HELP request_duration_seconds Request latency
# TYPE request_duration_seconds histogram
request_duration_seconds_bucket{le="0.1"} 800
request_duration_seconds_bucket{le="0.5"} 1100
request_duration_seconds_bucket{le="1.0"} 1200
```

### PromQL (Query Language)

```promql
# Rate of requests per second over 5 minutes
rate(http_requests_total[5m])

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))

# 99th percentile latency
histogram_quantile(0.99, rate(request_duration_seconds_bucket[5m]))
```

---

## Logs

Logs are **timestamped records of discrete events**.

### Structured vs Unstructured

```
UNSTRUCTURED (hard to parse):
2024-01-15 10:23:45 ERROR Failed to connect to database: connection refused

STRUCTURED (JSON, easy to query):
{
  "timestamp": "2024-01-15T10:23:45Z",
  "level": "error",
  "message": "Failed to connect to database",
  "error": "connection refused",
  "service": "api",
  "pod": "api-7d8f9-abc12",
  "trace_id": "abc123def456"
}
```

### Log Levels

| Level | When to Use |
|-------|-------------|
| DEBUG | Detailed info for debugging (disabled in prod) |
| INFO | Normal operations, milestones |
| WARN | Something unexpected, but recoverable |
| ERROR | Something failed, needs attention |
| FATAL | Application cannot continue |

### Kubernetes Logging

```bash
# View logs
kubectl logs pod-name
kubectl logs pod-name -c container-name  # Multi-container
kubectl logs pod-name --previous         # Previous crash
kubectl logs -f pod-name                 # Follow (tail)
kubectl logs -l app=nginx                # By label
```

In production, logs go to a central system. Common stacks:
- **ELK (Elasticsearch, Logstash, Kibana)**: The traditional heavyweight champion for text search and analysis.
- **EFK (Elasticsearch, Fluentd, Kibana)**: A popular Kubernetes-native variant replacing Logstash with Fluentd.
- **Loki + Grafana**: Grafana's logging solution that indexes only metadata (labels), making it significantly cheaper and natively integrated with Prometheus.

---

## Traces

Traces **follow a request across multiple services**.

```
┌─────────────────────────────────────────────────────────────┐
│              DISTRIBUTED TRACE                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Request (trace_id: abc123)                           │
│  Total time: 500ms                                         │
│                                                             │
│  ├─ Frontend (100ms)                                       │
│  │   └─ Render page                                        │
│  │                                                          │
│  ├─ API Gateway (50ms)                                     │
│  │   └─ Auth check                                         │
│  │                                                          │
│  ├─ User Service (150ms)                                   │
│  │   ├─ Get user data (50ms)                              │
│  │   └─ Database query (100ms)  ← Slow!                   │
│  │                                                          │
│  └─ Order Service (200ms)                                  │
│      ├─ Fetch orders (50ms)                               │
│      └─ Cache lookup (150ms)   ← Also slow!               │
│                                                             │
│  Traces answer: "Why is this request slow?"               │
│  Answer: DB query in User Service + Cache in Orders       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Concepts

| Term | Definition |
|------|------------|
| Trace | Complete journey of a request |
| Span | Single operation within a trace |
| Trace ID | Unique identifier for the trace |
| Span ID | Unique identifier for a span |
| Parent ID | Links child spans to parents |

### Tracing Tools
- **Jaeger**: CNCF graduated, highly popular for Kubernetes environments.
- **Zipkin**: Twitter-originated, mature tracing system.
- **OpenTelemetry**: The modern standard for instrumenting code and gathering all telemetry data in a vendor-neutral way.

---

## The Observability Stack

```
┌─────────────────────────────────────────────────────────────┐
│              TYPICAL KUBERNETES OBSERVABILITY STACK         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  COLLECTION                                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Prometheus     Fluentd/      OpenTelemetry         │   │
│  │  (metrics)      Fluent Bit    (logs/traces)         │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  STORAGE                                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Prometheus    Elasticsearch   Jaeger/              │   │
│  │  (time series) or Loki         Tempo                │   │
│  │                (logs)          (traces)             │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  VISUALIZATION                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   GRAFANA                            │   │
│  │  - Dashboards for all three pillars                 │   │
│  │  - Unified view                                     │   │
│  │  - Alerting                                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **Stop and think**: If Prometheus holds your metrics, Loki holds your logs, and Tempo holds your traces, what component allows an engineer to easily jump from a latency spike on a graph directly to the logs for those slow requests?

---

## Service Level Indicators & Objectives (SLIs/SLOs)

"Uptime %" is often misleading. If your API is technically "up" but takes 30 seconds to respond, your users will abandon it. Site Reliability Engineering (SRE) uses SLIs and SLOs to focus on user experience.

- **SLI (Service Level Indicator):** A direct, measurable fact about a service's behavior. Example: *The proportion of HTTP GET requests that return a 200 OK within 100ms.*
- **SLO (Service Level Objective):** Your target for the SLI. Example: *99.9% of requests over the last 30 days must meet the SLI criteria.*
- **SLA (Service Level Agreement):** The business contract outlining financial penalties if the SLO is missed. Engineers primarily focus on SLIs and SLOs.

---

## Kubernetes-Native Metrics

```bash
# First, install metrics-server (kind clusters don't include it by default)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
# For kind/local clusters, patch it to work without TLS verification:
kubectl patch deployment metrics-server -n kube-system --type=json \
  -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
# Wait ~60 seconds for metrics to start collecting, then:
kubectl top nodes
kubectl top pods

# Resource usage
NAME          CPU(cores)   MEMORY(bytes)
node-1        250m         1024Mi
node-2        100m         512Mi
```

### Key Kubernetes Metrics

| Metric | What It Tells You |
|--------|-------------------|
| `container_cpu_usage_seconds_total` | CPU consumption |
| `container_memory_usage_bytes` | Memory consumption |
| `kube_pod_status_phase` | Pod lifecycle state |
| `kube_deployment_status_replicas_available` | Healthy replicas |
| `apiserver_request_duration_seconds` | API server latency |

---

## Alerting

```yaml
# Prometheus AlertManager rule
groups:
  - name: kubernetes
    rules:
      - alert: PodCrashLooping
        expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Pod {{ $labels.pod }} is crash looping"

      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error rate above 5%"
```

### Alert Best Practices

```
Good alerts:
✓ Actionable (someone can fix it)
✓ Urgent (needs immediate attention)
✓ Not noisy (low false positives)
✓ Based on SLO violations

Bad alerts:
✗ "CPU at 80%" (so what? Are users affected?)
✗ Every pod restart (expected sometimes in K8s)
✗ Alert fatigue = ignored alerts
```

---

## Golden Signals

Google's SRE book defines four golden signals:

```
┌─────────────────────────────────────────────────────────────┐
│              FOUR GOLDEN SIGNALS                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. LATENCY                                                │
│     Time to service a request                              │
│     "How long do requests take?"                           │
│                                                             │
│  2. TRAFFIC                                                │
│     Demand on your system                                  │
│     "How many requests per second?"                        │
│                                                             │
│  3. ERRORS                                                 │
│     Rate of failed requests                                │
│     "What percentage of requests fail?"                    │
│                                                             │
│  4. SATURATION                                             │
│     How "full" your service is                            │
│     "How close to capacity?"                               │
│                                                             │
│  If you track these four things well, you'll catch        │
│  most problems before users notice.                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## War Story: The Silent Blackout

Imagine an e-commerce checkout service on Black Friday. Suddenly, the database CPU spiked to 100%. The legacy monitoring system triggered a "High CPU" alert. The panicked on-call engineer restarted the database, but the CPU immediately spiked again. Meanwhile, thousands of customers couldn't check out.

With modern observability:
1. An **SLO alert** fires first: "Checkout success rate dropped below 99%".
2. The engineer opens the **Grafana dashboard** and sees the *Traffic* golden signal is normal, but *Latency* has skyrocketed.
3. They look at a **Trace (Jaeger)** for a slow checkout request. It shows the `PaymentService` is waiting 30 seconds for a response from an external 3rd-party payment gateway.
4. The database CPU spike was just a secondary symptom—threads were queueing up waiting for the gateway, locking up resources. The engineer quickly flips a feature flag to use a backup gateway. The system recovers instantly.

*Observability didn't just point out that a server was busy; it provided the context to answer WHY the system was failing.*

---

## Trade-offs in Observability

Observability provides immense power, but it isn't free. Storing every piece of telemetry indefinitely will quickly bankrupt your infrastructure budget.

- **Cost vs. Granularity**: High-resolution metrics (scraping every 1 second) provide incredible detail but multiply your storage costs exponentially. Downsampling older metrics is essential for long-term retention.
- **Logs vs. Metrics**: Logging every single HTTP request just to count traffic is computationally expensive and wastes massive amounts of disk space. Instead, use Prometheus metrics to count events cheaply, and reserve logs for actionable or sampled diagnostic data.
- **100% Tracing vs. Sampling**: Tracing every single request in a high-throughput microservice architecture adds heavy network and storage overhead. Most mature systems implement "head sampling" (tracing a random 1% of requests) or "tail sampling" (tracing only the requests that end in errors or high latency).

---

## Common Mistakes

| Mistake | Why It Hurts | Solution |
|---------|--------------|----------|
| Unstructured logs | Cannot be queried or aggregated efficiently; requires fragile regex parsing. | Implement JSON structured logging across all applications. |
| No trace correlation | Impossible to follow a request's path across distributed microservices to find the root cause. | Inject and log trace IDs across all service boundaries. |
| Too many alerts | Causes "alert fatigue"; engineers get overwhelmed and start ignoring critical warnings. | Alert strictly on user-facing symptoms and SLO breaches, not internal causes. |
| Dashboard overload | Causes information paralysis during high-stress incidents when speed of diagnosis is critical. | Build focused dashboards centered strictly around the Golden Signals. |
| No retention policy | Observability data grows exponentially, leading to massive storage costs and slow queries. | Define strict TTLs (Time to Live) and downsample older data. |
| Using logs for metrics | High processing cost to count occurrences or calculate rates via text parsing. | Use Prometheus counters and histograms instead of log scraping. |
| Missing standard labels | Cannot slice or filter telemetry data by environment, region, or application version. | Apply consistent labels (e.g., `env=prod`, `version=v1.2`) to all observability data. |

---

## Did You Know?

- **Netflix engineers** can trace a single request's journey across hundreds of microservices. Their massive observability infrastructure processes billions of events per second to ensure playback never buffers.
- **The term "observability"** originates from control theory in the 1960s. Engineer Rudolf E. Kálmán defined a system as "observable" if its internal state can be perfectly inferred simply by looking at its external outputs.
- **Alert fatigue is real and dangerous.** Industry studies show that when engineering teams receive too many false or non-actionable alerts, they begin ignoring up to 90% of them, risking catastrophic outages.
- **Prometheus was the second** project ever to graduate from the Cloud Native Computing Foundation (CNCF), right after Kubernetes itself. This highlights just how fundamental metrics collection is to cloud-native architectures.

---

## Quiz

1. **Scenario: You are investigating a sudden spike in 500 Internal Server Errors in your web application. You know the exact timestamp but need to see the specific stack traces to understand the code failure. Which pillar of observability is most appropriate here?**
   <details>
   <summary>Answer</summary>
   Logs. While metrics told you that the error rate spiked (the symptom), logs contain the detailed, timestamped text records of discrete events. Looking at the logs for that specific timestamp will reveal the stack trace and the precise context of why the application crashed.
   </details>

2. **Scenario: A user reports that clicking the "Checkout" button in your 15-microservice architecture takes over 10 seconds. However, individual service dashboards show low CPU usage across the board. What observability concept should you use to find the bottleneck?**
   <details>
   <summary>Answer</summary>
   Distributed Traces. Traces are designed to follow a single user request as it traverses multiple services. By looking at a trace for a slow checkout request, you can visualize exactly how many milliseconds were spent in each service span, quickly identifying whether the delay is a slow database query, a slow API call, or network latency.
   </details>

3. **Scenario: Your manager wants to ensure maximum uptime and suggests creating a critical page-out alert anytime a database node's CPU exceeds 80%. Based on SLO principles, how should you advise your manager?**
   <details>
   <summary>Answer</summary>
   You should advise against this, as high CPU is a cause, not a symptom. Following SLO principles and the Golden Signals, alerts should be based on user-facing impact, such as increased Latency or elevated Error rates. A database running at 80% CPU might be operating perfectly efficiently without impacting users, making this a noisy, non-actionable alert that causes alert fatigue.
   </details>

4. **Scenario: Your Kubernetes cluster generates a terabyte of log data daily, leading to massive storage costs. You discover developers are writing log messages for every HTTP request just to count how many times an endpoint is hit. What architectural change should you recommend?**
   <details>
   <summary>Answer</summary>
   You should recommend migrating from logs to metrics for counting requests. Emitting and storing text logs for every event is highly inefficient. Instead, developers should instrument their code to increment a Prometheus counter metric (e.g., `http_requests_total`). Metrics use minimal storage because they aggregate numbers over time rather than storing individual text records.
   </details>

5. **Scenario: During an incident post-mortem, the team realizes the on-call engineer took 45 minutes to diagnose the issue because they had to manually cross-reference timestamps between a metrics dashboard and a separate logging terminal. How does a modern observability stack solve this?**
   <details>
   <summary>Answer</summary>
   A modern stack uses a unified visualization layer, like Grafana, combined with trace correlation. If developers inject trace IDs into their structured logs, Grafana allows engineers to look at a spike on a metrics graph, click on it, and instantly jump to the exact logs and distributed traces associated with that time window and specific request. This eliminates manual timestamp matching.
   </details>

6. **Scenario: Your team uses an SLI defined as "HTTP 200 responses delivered in under 200ms," with an SLO target of 99.9%. Over the last month, you only hit 98%. The product owner is pushing for a massive new feature release next week. What should the engineering team do?**
   <details>
   <summary>Answer</summary>
   The team should halt feature development and focus entirely on reliability and performance fixes. When an SLO is breached, it means the "error budget" is depleted, and the system is currently too unreliable for users. Releasing new features introduces change and risk, which will likely degrade the system further. The mathematical objectivity of an SLO helps resolve business vs. engineering disputes.
   </details>

7. **Scenario: A junior developer submits a pull request that logs security events like this: `[WARN] User bob@company.com failed login from IP 192.168.1.5`. Why is this approach problematic at scale, and what is the alternative?**
   <details>
   <summary>Answer</summary>
   This is unstructured logging. At scale, if an analyst needs to count all failed logins for a specific IP, they must write complex and brittle regular expressions to extract the data from the text string. The alternative is structured logging (usually JSON), where variables like user email and IP address are stored as distinct, indexable fields (e.g., `{"level":"warn", "event":"failed_login", "user":"bob@company.com"}`). This allows for instant, reliable querying.
   </details>

---

## Hands-On Exercise

**Task**: Explore Kubernetes observability basics.

```bash
# 1. Deploy a sample application
kubectl create deployment web --image=nginx:1.25 --replicas=3
kubectl expose deployment web --port=80

# 2. View logs
kubectl logs -l app=web --all-containers
kubectl logs -l app=web -f  # Follow logs

# 3. Check resource usage
# Install metrics-server first (if not already done):
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch deployment metrics-server -n kube-system --type=json \
  -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
# Wait ~60 seconds, then:
kubectl top pods
kubectl top nodes

# 4. Simulate a problem
# Scale down to 0 (break it)
kubectl scale deployment web --replicas=0

# Check events (kubernetes logs)
kubectl get events --sort-by='.lastTimestamp'

# 5. View pod status (basic metrics)
kubectl get pods -o wide
kubectl describe pod -l app=web

# 6. Generate some logs
kubectl scale deployment web --replicas=1
kubectl exec -it $(kubectl get pod -l app=web -o name | head -1) -- \
  curl -s localhost > /dev/null

# View nginx access logs
kubectl logs -l app=web | tail

# 7. Explore with JSONPath (metrics-like queries)
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\n"}{end}'

# 8. Cleanup
kubectl delete deployment web
kubectl delete service web
```

**Success criteria**: Understand logs, events, and basic resource monitoring.

---

## Summary

**Observability** is about understanding your system:

**Three pillars**:
- **Metrics**: Numbers over time (Prometheus)
- **Logs**: Event records (ELK, Loki)
- **Traces**: Request journeys (Jaeger)

**Golden signals** (what to monitor):
- Latency
- Traffic
- Errors
- Saturation

**Kubernetes specifics**:
- `kubectl logs` for pod logs
- `kubectl top` for resource metrics
- Events for cluster activity
- Prometheus for comprehensive metrics

**Key insight**: Observability is not just monitoring. It's the ability to ask arbitrary questions about your system and get answers.

---

## Next Module

[Module 1.5: Platform Engineering Concepts](../module-1.5-platform-engineering/) - Building internal developer platforms.