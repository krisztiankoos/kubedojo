# Module 1.1: Prometheus

> **Toolkit Track** | Complexity: `[COMPLEX]` | Time: 45-50 min

## Prerequisites

Before starting this module:
- [Observability Theory Track](../../foundations/observability-theory/)
- [SRE Discipline](../../disciplines/sre/) (recommended)
- Basic Kubernetes knowledge
- Understanding of metrics concepts

## Why This Module Matters

Prometheus is the de facto standard for metrics in cloud-native environments. Born at SoundCloud in 2012, it became the second project to graduate from CNCF (after Kubernetes). If you run Kubernetes, you're almost certainly running Prometheus.

Understanding Prometheus isn't optional—it's foundational. Every SRE, platform engineer, and DevOps practitioner needs to query metrics, set up alerts, and debug performance issues using Prometheus.

## Did You Know?

- **Prometheus processes millions of samples per second** on modest hardware—its pull-based model and time-series database are remarkably efficient
- **The name comes from Greek mythology**—Prometheus stole fire from the gods. The project "stole" ideas from Google's Borgmon monitoring system
- **PromQL is Turing-complete**—you can technically compute anything with it, though you probably shouldn't
- **Prometheus was designed for reliability over accuracy**—it prioritizes being available during outages when you need it most, even if some metrics are missing

## Prometheus Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   PROMETHEUS ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TARGETS                        PROMETHEUS SERVER                │
│  ┌──────────┐                  ┌─────────────────────────────┐  │
│  │ App /    │◀── scrape ──────│  ┌─────────────────────────┐│  │
│  │ metrics  │                  │  │    Retrieval            ││  │
│  └──────────┘                  │  │    (pull metrics)       ││  │
│  ┌──────────┐                  │  └───────────┬─────────────┘│  │
│  │ Node     │◀── scrape ──────│              │              │  │
│  │ Exporter │                  │  ┌───────────▼─────────────┐│  │
│  └──────────┘                  │  │    TSDB                 ││  │
│  ┌──────────┐                  │  │    (time-series DB)     ││  │
│  │ kube-    │◀── scrape ──────│  └───────────┬─────────────┘│  │
│  │ metrics  │                  │              │              │  │
│  └──────────┘                  │  ┌───────────▼─────────────┐│  │
│                                │  │    HTTP Server          ││  │
│  SERVICE DISCOVERY             │  │    (PromQL queries)     ││  │
│  ┌──────────┐                  │  └─────────────────────────┘│  │
│  │ K8s API  │── discover ────▶│                              │  │
│  │ Consul   │                  └──────────────┬──────────────┘  │
│  │ File SD  │                                 │                  │
│  └──────────┘                                 │                  │
│                                               ▼                  │
│                                ┌─────────────────────────────┐  │
│                                │      ALERTMANAGER          │  │
│                                │  ┌───────────────────────┐  │  │
│                                │  │ Dedup, Group, Route   │  │  │
│                                │  └───────────┬───────────┘  │  │
│                                │              │               │  │
│                                │  ┌───────────▼───────────┐  │  │
│                                │  │ PagerDuty │ Slack     │  │  │
│                                │  │ Email     │ Webhook   │  │  │
│                                │  └───────────────────────┘  │  │
│                                └─────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Purpose |
|-----------|---------|
| **Prometheus Server** | Scrapes targets, stores metrics, serves queries |
| **TSDB** | Time-series database optimized for metrics |
| **Alertmanager** | Handles alerts: deduplication, grouping, routing |
| **Pushgateway** | For short-lived jobs that can't be scraped |
| **Exporters** | Expose metrics from third-party systems |

### Pull vs. Push Model

```
PULL MODEL (Prometheus)                PUSH MODEL (Traditional)
─────────────────────────────────────────────────────────────────

Prometheus ──▶ Scrape ──▶ Target       Agent ──▶ Push ──▶ Server
     │                        │             │                │
     │  "I'll get metrics     │             │  "Here are     │
     │   when I'm ready"      │             │   my metrics"  │
     │                        │             │                │

PROS:                                  PROS:
• Easy to detect target down          • Works behind firewalls
• Central control of scrape rate      • Good for short-lived jobs
• No agent config needed              • Event-driven possible

CONS:                                  CONS:
• Targets must be reachable           • Central server overload
• NAT/firewall challenges             • No target health detection
```

### War Story: The Missing Metrics

A team migrated to Kubernetes. Their Prometheus dashboards went dark—no app metrics. Panic ensued.

The problem? Prometheus couldn't discover pods. Service discovery was misconfigured. The apps were healthy, exposing metrics correctly, but Prometheus didn't know they existed.

Lesson: In Kubernetes, service discovery is as important as metric exposition. If Prometheus can't find your targets, your metrics don't exist.

## PromQL Fundamentals

### Data Types

```
PROMQL DATA TYPES
─────────────────────────────────────────────────────────────────

INSTANT VECTOR (single point per series)
http_requests_total{method="GET"}
→ Returns latest value for each matching series

RANGE VECTOR (multiple points per series)
http_requests_total{method="GET"}[5m]
→ Returns 5 minutes of samples for each series

SCALAR (single numeric value)
42 or count(up)
→ Returns a single number

STRING (rarely used)
"hello"
→ Returns a string value
```

### Essential Queries

```promql
# Basic Selection
http_requests_total                           # All series with this metric
http_requests_total{status="200"}             # Filter by label
http_requests_total{status=~"2.."}            # Regex match (2xx)
http_requests_total{status!="500"}            # Negative match

# Aggregation
sum(http_requests_total)                      # Total across all series
sum by (method)(http_requests_total)          # Group by method
sum without (instance)(http_requests_total)   # Exclude instance label

# Rate and Increase
rate(http_requests_total[5m])                 # Per-second rate over 5m
irate(http_requests_total[5m])                # Instant rate (last 2 points)
increase(http_requests_total[1h])             # Total increase over 1h

# Mathematical Operations
http_requests_total * 2                       # Scalar multiply
http_errors_total / http_requests_total       # Error rate
```

### Rate vs. Irate

```
RATE vs IRATE
─────────────────────────────────────────────────────────────────

rate(metric[5m])
├── Calculates average per-second rate over entire range
├── Smooths out spikes
├── Better for alerting (less noise)
└── Use for: dashboards, SLOs, capacity planning

irate(metric[5m])
├── Uses only last two data points
├── Shows actual instant rate
├── More responsive to changes
└── Use for: debugging, seeing real-time spikes

Example:
  rate(): "Over the last 5 minutes, you averaged 100 req/s"
  irate(): "Right now, you're doing 500 req/s"
```

### SLO Queries

```promql
# Error Rate (fraction of requests that failed)
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))

# Availability (1 - error rate)
1 - (
  sum(rate(http_requests_total{status=~"5.."}[5m]))
  /
  sum(rate(http_requests_total[5m]))
)

# Latency Percentiles (histogram)
histogram_quantile(0.99,
  sum by (le)(rate(http_request_duration_seconds_bucket[5m]))
)

# Apdex Score
(
  sum(rate(http_request_duration_seconds_bucket{le="0.3"}[5m]))
  +
  sum(rate(http_request_duration_seconds_bucket{le="1.2"}[5m])) / 2
)
/
sum(rate(http_request_duration_seconds_count[5m]))
```

## Service Discovery

### Kubernetes Service Discovery

```yaml
# Prometheus configuration for K8s
scrape_configs:
  # Scrape pods with prometheus.io/scrape annotation
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      # Only scrape pods with annotation
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      # Use annotation for port
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: (.+)
        replacement: ${1}
      # Use annotation for path
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
```

### Pod Annotations

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
  annotations:
    prometheus.io/scrape: "true"    # Enable scraping
    prometheus.io/port: "8080"      # Metrics port
    prometheus.io/path: "/metrics"  # Metrics path (default)
spec:
  containers:
    - name: app
      ports:
        - containerPort: 8080
          name: metrics
```

### ServiceMonitor (Prometheus Operator)

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
    - port: metrics
      interval: 15s
      path: /metrics
  namespaceSelector:
    matchNames:
      - production
```

## Alerting

### Alert Rules

```yaml
# alerting-rules.yaml
groups:
  - name: application
    rules:
      # High Error Rate
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m]))
          > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"

      # Service Down
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "{{ $labels.instance }} has been down for more than 1 minute"

      # High Latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.99,
            sum by (le)(rate(http_request_duration_seconds_bucket[5m]))
          ) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "P99 latency is {{ $value | humanizeDuration }}"
```

### Alertmanager Configuration

```yaml
# alertmanager.yaml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/...'

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'default'
    slack_configs:
      - channel: '#alerts'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<key>'
        severity: critical

  - name: 'slack'
    slack_configs:
      - channel: '#alerts-warning'
        send_resolved: true
```

## Recording Rules

### Why Recording Rules?

```
WITHOUT RECORDING RULES
─────────────────────────────────────────────────────────────────

Dashboard Query:
  sum by (service)(rate(http_requests_total[5m])) /
  sum by (service)(rate(http_requests_total[5m]))

Executed: Every dashboard refresh (e.g., every 30s)
Problem: Expensive query runs constantly
         Same calculation done multiple times


WITH RECORDING RULES
─────────────────────────────────────────────────────────────────

Recording Rule:
  record: service:http_requests:rate5m
  expr: sum by (service)(rate(http_requests_total[5m]))

Dashboard Query:
  service:http_requests:rate5m

Executed: Once per evaluation interval
Benefit: Pre-computed, fast to query
         Consistent values across dashboards
```

### Recording Rule Examples

```yaml
groups:
  - name: http_rules
    interval: 30s
    rules:
      # Request rate by service
      - record: service:http_requests:rate5m
        expr: sum by (service)(rate(http_requests_total[5m]))

      # Error rate by service
      - record: service:http_errors:rate5m
        expr: sum by (service)(rate(http_requests_total{status=~"5.."}[5m]))

      # Error ratio (for SLO)
      - record: service:http_error_ratio:rate5m
        expr: |
          service:http_errors:rate5m
          /
          service:http_requests:rate5m

      # Latency percentiles
      - record: service:http_latency_p99:rate5m
        expr: |
          histogram_quantile(0.99,
            sum by (service, le)(rate(http_request_duration_seconds_bucket[5m]))
          )
```

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Using `rate()` on gauges | Wrong values | Use `rate()` only on counters |
| Missing `rate()` on counters | Shows total, not rate | Wrap counter queries in `rate()` |
| Too short range for `rate()` | Missing samples | Range >= 4x scrape interval |
| High cardinality labels | Memory explosion | Avoid unbounded labels (user_id, request_id) |
| No recording rules | Slow dashboards | Pre-compute expensive queries |
| Alerting on `irate()` | Flapping alerts | Use `rate()` for alerting |

## Quiz

Test your understanding:

<details>
<summary>1. Why does Prometheus use a pull model instead of push?</summary>

**Answer**: Pull provides several advantages:
- **Target health detection**: If scrape fails, target is down
- **Central control**: Prometheus controls scrape rate, not targets
- **Simpler targets**: No agent configuration needed
- **Debugging**: Can manually curl /metrics endpoint

Pull challenges (NAT, firewalls) are solved with Pushgateway for short-lived jobs.
</details>

<details>
<summary>2. What's the difference between `rate()` and `increase()`?</summary>

**Answer**:
- `rate(counter[5m])`: Per-second average rate over the range
- `increase(counter[5m])`: Total increase over the range

They're related: `increase(counter[5m]) ≈ rate(counter[5m]) * 300`

Use `rate()` for "requests per second", `increase()` for "total requests in last hour".
</details>

<details>
<summary>3. Why are recording rules important?</summary>

**Answer**: Recording rules:
- **Pre-compute** expensive queries at regular intervals
- **Speed up** dashboard loading
- **Ensure consistency** across queries using same data
- **Reduce load** on Prometheus during high query periods
- **Enable longer ranges** by storing pre-aggregated data

Without them, complex queries run on every dashboard refresh.
</details>

<details>
<summary>4. What causes high cardinality problems?</summary>

**Answer**: High cardinality occurs when labels have many unique values:
- `user_id`: millions of users = millions of time series
- `request_id`: every request = unbounded series
- `url_path`: with path parameters = explosion

Each unique label combination creates a new time series. Prometheus stores all series in memory. High cardinality = memory exhaustion.

Solution: Remove high-cardinality labels or aggregate them.
</details>

## Hands-On Exercise: Prometheus from Scratch

Deploy Prometheus and write queries:

### Setup

```bash
# Create namespace
kubectl create namespace monitoring

# Deploy Prometheus using Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --set alertmanager.enabled=true \
  --set server.persistentVolume.size=10Gi
```

### Step 1: Access Prometheus

```bash
# Port-forward to Prometheus
kubectl port-forward -n monitoring svc/prometheus-server 9090:80

# Open http://localhost:9090 in browser
```

### Step 2: Explore Built-in Metrics

```promql
# What targets are being scraped?
up

# Total memory by instance
node_memory_MemTotal_bytes

# CPU usage (requires node-exporter)
rate(node_cpu_seconds_total{mode!="idle"}[5m])

# Kubernetes pods running
kube_pod_status_phase{phase="Running"}
```

### Step 3: Deploy Sample App with Metrics

```yaml
# sample-app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sample-app
  namespace: monitoring
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sample-app
  template:
    metadata:
      labels:
        app: sample-app
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      containers:
        - name: app
          image: quay.io/brancz/prometheus-example-app:v0.3.0
          ports:
            - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: sample-app
  namespace: monitoring
spec:
  selector:
    app: sample-app
  ports:
    - port: 80
      targetPort: 8080
```

```bash
kubectl apply -f sample-app.yaml

# Generate some traffic
kubectl run curl --image=curlimages/curl -it --rm -- \
  sh -c 'while true; do curl -s sample-app.monitoring/metrics; sleep 1; done'
```

### Step 4: Write Queries

```promql
# Check if sample-app is being scraped
up{job="kubernetes-pods", kubernetes_name="sample-app"}

# Request rate
rate(http_requests_total{kubernetes_name="sample-app"}[5m])

# Error rate
sum(rate(http_requests_total{kubernetes_name="sample-app",status=~"5.."}[5m]))
/
sum(rate(http_requests_total{kubernetes_name="sample-app"}[5m]))

# Latency P99
histogram_quantile(0.99,
  sum by (le)(rate(http_request_duration_seconds_bucket{kubernetes_name="sample-app"}[5m]))
)
```

### Step 5: Create Alert Rule

```yaml
# alert-rules.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-alert-rules
  namespace: monitoring
data:
  alerts.yaml: |
    groups:
      - name: sample-app
        rules:
          - alert: SampleAppHighErrorRate
            expr: |
              sum(rate(http_requests_total{kubernetes_name="sample-app",status=~"5.."}[5m]))
              /
              sum(rate(http_requests_total{kubernetes_name="sample-app"}[5m]))
              > 0.01
            for: 1m
            labels:
              severity: warning
            annotations:
              summary: "Sample app error rate too high"
```

### Success Criteria

You've completed this exercise when you can:
- [ ] Access Prometheus UI
- [ ] See sample-app in targets
- [ ] Query request rate and error rate
- [ ] Calculate latency percentiles
- [ ] Understand the alert rule syntax

## Key Takeaways

1. **Pull model is intentional**: Prometheus knows when targets are down
2. **PromQL is powerful**: rate(), histogram_quantile(), aggregations
3. **Service discovery is critical**: Especially in Kubernetes
4. **Recording rules for performance**: Pre-compute expensive queries
5. **Labels are powerful but dangerous**: Avoid high cardinality

## Further Reading

- [Prometheus Documentation](https://prometheus.io/docs/) — Official docs
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/) — Quick reference
- [Robust Perception Blog](https://www.robustperception.io/blog/) — Deep dives
- [Prometheus Operator](https://prometheus-operator.dev/) — Kubernetes-native management

## Summary

Prometheus is the foundation of cloud-native observability. Its pull-based model, powerful PromQL query language, and Kubernetes integration make it essential for any platform engineer. Understanding metrics collection, querying, and alerting with Prometheus enables effective monitoring and incident response.

---

## Next Module

Continue to [Module 1.2: OpenTelemetry](module-1.2-opentelemetry.md) to learn about vendor-agnostic observability instrumentation.
