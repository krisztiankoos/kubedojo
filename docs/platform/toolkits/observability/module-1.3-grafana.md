# Module 1.3: Grafana

> **Toolkit Track** | Complexity: `[MEDIUM]` | Time: 40-45 min

## Prerequisites

Before starting this module:
- [Module 1.1: Prometheus](module-1.1-prometheus.md)
- [Module 1.2: OpenTelemetry](module-1.2-opentelemetry.md)
- Basic PromQL knowledge
- Understanding of metrics and time series

## Why This Module Matters

Data without visualization is just numbers. Grafana transforms raw metrics into actionable insights. It's the window into your systems—the first place you look during an incident, the source of truth for SLOs, the tool that makes observability accessible to everyone.

Grafana has evolved from a dashboarding tool into a complete observability platform. Understanding it deeply—beyond basic charts—unlocks powerful capabilities for correlation, alerting, and investigation.

## Did You Know?

- **Grafana is used by millions of users** at companies like Bloomberg, PayPal, and CERN—from startups to enterprises
- **The name "Grafana"** comes from combining "graphite" and "graphana" (an earlier fork). It was created in 2014 by Torkel Ödegaard
- **Grafana Labs' LGTM stack** (Loki, Grafana, Tempo, Mimir) provides a complete open-source alternative to commercial observability platforms
- **Dashboard variables** can reduce a 100-dashboard sprawl to 10 reusable dashboards—most teams don't use them enough

## Grafana Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     GRAFANA ECOSYSTEM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  GRAFANA (Visualization)                                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│    │
│  │  │Dashboards│  │ Explore  │  │ Alerting │  │  Users   ││    │
│  │  │          │  │          │  │          │  │  & Auth  ││    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘│    │
│  │                                                         │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │              DATA SOURCE PLUGINS                  │  │    │
│  │  │  Prometheus │ Loki │ Tempo │ Elasticsearch │ ...  │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│           ┌──────────────────┼──────────────────┐               │
│           ▼                  ▼                  ▼               │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │  Prometheus  │   │    Loki      │   │    Tempo     │        │
│  │   (Mimir)    │   │   (logs)     │   │   (traces)   │        │
│  │   metrics    │   │              │   │              │        │
│  └──────────────┘   └──────────────┘   └──────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Grafana Stack (LGTM)

| Component | Purpose |
|-----------|---------|
| **Loki** | Log aggregation (like Prometheus for logs) |
| **Grafana** | Visualization and exploration |
| **Tempo** | Distributed tracing |
| **Mimir** | Scalable Prometheus metrics storage |

### War Story: Dashboard Hell

A team had 200 dashboards. Nobody could find anything. Each engineer created their own versions. During incidents, people argued about which dashboard was "correct."

The fix? Dashboard standards. One dashboard per service, using variables for flexibility. Team ownership with review processes. The dashboard count dropped to 30—and everyone could find what they needed.

## Dashboard Design Principles

### The Four Golden Signals

```
FOUR GOLDEN SIGNALS
─────────────────────────────────────────────────────────────────

Every dashboard should answer these questions:

1. LATENCY - How long does it take?
   └── Histogram quantiles (p50, p95, p99)

2. TRAFFIC - How much load are we handling?
   └── Requests per second

3. ERRORS - What's failing?
   └── Error rate as percentage

4. SATURATION - How "full" is the system?
   └── CPU, memory, queue depth


DASHBOARD LAYOUT
─────────────────────────────────────────────────────────────────
┌────────────────────────────────────────────────────────────────┐
│  SERVICE: $service    ENVIRONMENT: $env    TIME: $__interval  │
├────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │    Latency      │ │    Traffic      │ │    Errors       │ │
│  │    (p99)        │ │    (RPS)        │ │    (%)          │ │
│  │   STAT PANEL    │ │   STAT PANEL    │ │   STAT PANEL    │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
├────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐│
│  │                      REQUEST RATE                          ││
│  │  ════════════════════════════════════════════════         ││
│  │                                                            ││
│  └───────────────────────────────────────────────────────────┘│
│  ┌───────────────────────────────────────────────────────────┐│
│  │                      LATENCY                               ││
│  │  ────────── p99  ────────── p95  ────────── p50           ││
│  │                                                            ││
│  └───────────────────────────────────────────────────────────┘│
│  ┌───────────────────────────────────────────────────────────┐│
│  │                      ERROR RATE                            ││
│  │  ════════════════════════════════════════════════         ││
│  │                                                            ││
│  └───────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────┘
```

### Dashboard Hierarchy

```
DASHBOARD ORGANIZATION
─────────────────────────────────────────────────────────────────

LEVEL 1: Overview Dashboard
├── All services at a glance
├── Traffic heatmap
├── Error hotspots
└── Click to drill down

LEVEL 2: Service Dashboard
├── Golden signals for one service
├── Dependencies (upstream/downstream)
├── Resource utilization
└── Click to drill down

LEVEL 3: Component Dashboard
├── Individual pods/instances
├── Detailed metrics
├── Debug information
└── Linked to logs/traces
```

## Dashboard Variables

### Variable Types

```
GRAFANA VARIABLES
─────────────────────────────────────────────────────────────────

QUERY VARIABLE (dynamic from data source)
  Name: service
  Query: label_values(http_requests_total, service)
  Result: Dropdown with all services

CUSTOM VARIABLE (static list)
  Name: percentile
  Values: 50,90,95,99
  Result: Dropdown with percentile options

INTERVAL VARIABLE (time-based)
  Name: interval
  Values: 1m,5m,15m,1h
  Auto: Based on time range

DATASOURCE VARIABLE
  Name: datasource
  Type: prometheus
  Result: Switch between Prometheus instances

TEXT VARIABLE (user input)
  Name: filter
  Type: text
  Result: Free-text filter input
```

### Using Variables

```promql
# In queries, use $variable or ${variable}
rate(http_requests_total{service="$service"}[$interval])

# Multi-value with regex
rate(http_requests_total{service=~"$service"}[$interval])

# With custom variable for percentile
histogram_quantile(0.$percentile,
  sum by (le)(rate(http_request_duration_bucket{service="$service"}[$interval]))
)
```

### Variable Configuration

```json
{
  "templating": {
    "list": [
      {
        "name": "service",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(http_requests_total, service)",
        "multi": true,
        "includeAll": true,
        "allValue": ".*",
        "refresh": 2
      },
      {
        "name": "interval",
        "type": "interval",
        "auto": true,
        "auto_min": "10s",
        "options": [
          {"value": "1m", "text": "1 minute"},
          {"value": "5m", "text": "5 minutes"},
          {"value": "15m", "text": "15 minutes"}
        ]
      }
    ]
  }
}
```

## Panel Types

### Choosing the Right Panel

| Panel Type | Use Case | Example |
|------------|----------|---------|
| **Time series** | Metrics over time | Request rate, latency trends |
| **Stat** | Single current value | Current error rate, RPS |
| **Gauge** | Value vs. thresholds | CPU usage, SLO budget |
| **Bar gauge** | Compare values | Top 5 endpoints by latency |
| **Table** | Detailed data | Pod status, error details |
| **Heatmap** | Distribution over time | Latency distribution |
| **Logs** | Log entries | Loki integration |
| **Traces** | Distributed traces | Tempo/Jaeger integration |

### Time Series Best Practices

```
TIME SERIES CONFIGURATION
─────────────────────────────────────────────────────────────────

LEGEND
├── Format: {{service}} - {{method}}
├── Placement: Bottom or Right
└── Hide if too many series (use tooltip)

AXES
├── Left Y: Main metric (e.g., RPS)
├── Right Y: Secondary (e.g., error %)
└── Label units explicitly

THRESHOLDS
├── Warning: Yellow line
├── Critical: Red line
└── Fill below threshold for visibility

SERIES OVERRIDES
├── Error series: Red
├── Success series: Green
└── Specific series styling
```

### Stat Panel with Thresholds

```json
{
  "type": "stat",
  "title": "Error Rate",
  "targets": [
    {
      "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100",
      "legendFormat": ""
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "percent",
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"color": "green", "value": null},
          {"color": "yellow", "value": 1},
          {"color": "red", "value": 5}
        ]
      },
      "mappings": [],
      "color": {"mode": "thresholds"}
    }
  },
  "options": {
    "colorMode": "background",
    "graphMode": "none",
    "textMode": "value"
  }
}
```

## Grafana Alerting

### Alert Rules

```yaml
# Grafana alerting (unified alerting)
apiVersion: 1
groups:
  - name: service-alerts
    folder: Production
    interval: 1m
    rules:
      - uid: high-error-rate
        title: High Error Rate
        condition: C
        data:
          # Query A: Error requests
          - refId: A
            datasourceUid: prometheus
            model:
              expr: sum(rate(http_requests_total{status=~"5.."}[5m]))

          # Query B: Total requests
          - refId: B
            datasourceUid: prometheus
            model:
              expr: sum(rate(http_requests_total[5m]))

          # Expression C: Error rate
          - refId: C
            datasourceUid: __expr__
            model:
              type: math
              expression: $A / $B * 100
              conditions:
                - evaluator:
                    type: gt
                    params: [5]  # > 5%

        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error rate is {{ $values.C }}%"
```

### Contact Points

```yaml
# Contact points configuration
apiVersion: 1
contactPoints:
  - name: slack-alerts
    receivers:
      - uid: slack-1
        type: slack
        settings:
          url: https://hooks.slack.com/services/...
          recipient: "#alerts"
          title: "{{ .CommonLabels.alertname }}"
          text: "{{ .CommonAnnotations.summary }}"

  - name: pagerduty
    receivers:
      - uid: pd-1
        type: pagerduty
        settings:
          integrationKey: "<key>"
          severity: "{{ .CommonLabels.severity }}"
```

## Explore Mode

### Ad-hoc Investigation

```
EXPLORE MODE
─────────────────────────────────────────────────────────────────

┌────────────────────────────────────────────────────────────────┐
│  [Prometheus ▼]    [Loki ▼]    [Tempo ▼]                       │
├────────────────────────────────────────────────────────────────┤
│  QUERY: rate(http_requests_total{service="api"}[5m])           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  [Run Query]  [Add Query]  [Split]                       │ │
│  └──────────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  RESULT:                                                        │
│  ════════════════════════════════════════════════              │
│                                          ^                      │
│                                         /                       │
│  ──────────────────────────────────────/──────────             │
│                                                                 │
│  [Split] Split panes for comparison                            │
│  [Logs]  Link to Loki for this time range                      │
│  [Traces] Link to Tempo for this trace ID                      │
│                                                                 │
└────────────────────────────────────────────────────────────────┘

Use Cases:
• Incident investigation
• Metric exploration
• Query building before dashboard
• Correlating metrics, logs, traces
```

### Correlating Signals

```
SIGNAL CORRELATION
─────────────────────────────────────────────────────────────────

1. Start with metric anomaly
   rate(http_requests_total{status="500"}[5m]) > 0

2. Click "Explore" on spike timestamp

3. Split view → Add Loki
   {service="api"} |= "error" | json

4. Find error with trace_id

5. Split view → Add Tempo
   Paste trace_id → See full trace

6. Identify root cause in upstream service
```

## Dashboard as Code

### Provisioning

```yaml
# provisioning/dashboards/dashboards.yaml
apiVersion: 1
providers:
  - name: 'default'
    orgId: 1
    folder: 'Production'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    options:
      path: /var/lib/grafana/dashboards
```

### Grafonnet (Jsonnet)

```jsonnet
// dashboard.jsonnet
local grafana = import 'grafonnet/grafana.libsonnet';
local dashboard = grafana.dashboard;
local row = grafana.row;
local prometheus = grafana.prometheus;
local graphPanel = grafana.graphPanel;

dashboard.new(
  'Service Dashboard',
  tags=['production', 'service'],
  time_from='now-1h',
)
.addTemplate(
  grafana.template.datasource(
    'datasource',
    'prometheus',
    'Prometheus',
  )
)
.addTemplate(
  grafana.template.query(
    'service',
    'label_values(http_requests_total, service)',
    datasource='$datasource',
  )
)
.addRow(
  row.new(
    title='Golden Signals',
  )
  .addPanel(
    graphPanel.new(
      'Request Rate',
      datasource='$datasource',
    )
    .addTarget(
      prometheus.target(
        'sum(rate(http_requests_total{service="$service"}[5m]))',
        legendFormat='RPS',
      )
    )
  )
  .addPanel(
    graphPanel.new(
      'Error Rate',
      datasource='$datasource',
    )
    .addTarget(
      prometheus.target(
        'sum(rate(http_requests_total{service="$service",status=~"5.."}[5m])) / sum(rate(http_requests_total{service="$service"}[5m]))',
        legendFormat='Error %',
      )
    )
  )
)
```

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Too many panels | Slow, overwhelming | Focus on golden signals |
| No variables | Duplicate dashboards | Use template variables |
| Hardcoded time ranges | Stale data | Use relative ranges |
| Missing units | Unclear data | Always set units |
| No thresholds | Can't spot issues | Add visual thresholds |
| Direct queries everywhere | Slow dashboards | Use recording rules |

## Quiz

Test your understanding:

<details>
<summary>1. Why are dashboard variables important?</summary>

**Answer**: Variables provide:
- **Reusability**: One dashboard for many services
- **Exploration**: Easy switching between environments
- **Maintenance**: Fewer dashboards to maintain
- **Consistency**: Same layout, different data

Without variables, teams create duplicate dashboards for each service, leading to maintenance nightmares.
</details>

<details>
<summary>2. What are the Four Golden Signals and why use them?</summary>

**Answer**: The Four Golden Signals are:
1. **Latency**: How long requests take
2. **Traffic**: Request volume
3. **Errors**: Failure rate
4. **Saturation**: Resource utilization

They provide a complete picture of service health. If all four are healthy, the service is likely healthy. They're recommended by Google's SRE book as the minimum monitoring.
</details>

<details>
<summary>3. When should you use Explore vs. Dashboards?</summary>

**Answer**:
- **Dashboards**: Known questions, ongoing monitoring, team visibility
- **Explore**: Ad-hoc investigation, incident response, query building

Explore is for investigation, dashboards are for monitoring. Build dashboards from queries developed in Explore.
</details>

<details>
<summary>4. How does Grafana help with signal correlation?</summary>

**Answer**: Grafana enables correlation through:
- **Linked data sources**: Jump from metric to logs to traces
- **Common labels**: TraceID, service name across signals
- **Split view**: Compare signals side-by-side
- **Time synchronization**: Same time range across panels

This enables rapid root cause analysis: metric spike → related logs → distributed trace.
</details>

## Hands-On Exercise: Build a Service Dashboard

Create a complete service dashboard:

### Setup

```bash
# Deploy Grafana using Helm
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install grafana grafana/grafana \
  --namespace monitoring \
  --set adminPassword=admin \
  --set persistence.enabled=true \
  --set persistence.size=10Gi
```

### Step 1: Access Grafana

```bash
# Get admin password
kubectl get secret -n monitoring grafana -o jsonpath="{.data.admin-password}" | base64 -d

# Port forward
kubectl port-forward -n monitoring svc/grafana 3000:80

# Login at http://localhost:3000 (admin / <password>)
```

### Step 2: Add Prometheus Data Source

1. Go to Configuration → Data Sources
2. Add Prometheus
3. URL: `http://prometheus-server:80`
4. Save & Test

### Step 3: Create Dashboard with Variables

```json
{
  "title": "Service Dashboard",
  "templating": {
    "list": [
      {
        "name": "service",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(up, job)",
        "multi": false,
        "includeAll": false
      },
      {
        "name": "interval",
        "type": "interval",
        "auto": true,
        "auto_min": "10s",
        "options": [
          {"value": "1m", "text": "1m"},
          {"value": "5m", "text": "5m"},
          {"value": "15m", "text": "15m"}
        ]
      }
    ]
  }
}
```

### Step 4: Add Golden Signal Panels

**Request Rate (Time Series)**:
```promql
sum(rate(http_requests_total{job="$service"}[$interval]))
```

**Error Rate (Stat Panel)**:
```promql
sum(rate(http_requests_total{job="$service",status=~"5.."}[$interval]))
/
sum(rate(http_requests_total{job="$service"}[$interval]))
* 100
```

**Latency P99 (Time Series)**:
```promql
histogram_quantile(0.99,
  sum by (le)(rate(http_request_duration_seconds_bucket{job="$service"}[$interval]))
)
```

**CPU Usage (Gauge)**:
```promql
avg(rate(process_cpu_seconds_total{job="$service"}[$interval])) * 100
```

### Step 5: Configure Thresholds

For Error Rate Stat:
- Green: < 1%
- Yellow: 1-5%
- Red: > 5%

For CPU Gauge:
- Green: < 70%
- Yellow: 70-85%
- Red: > 85%

### Success Criteria

You've completed this exercise when you can:
- [ ] Create dashboard with variables
- [ ] Switch services using dropdown
- [ ] See all four golden signals
- [ ] Thresholds change panel colors
- [ ] Export dashboard as JSON

## Key Takeaways

1. **Four Golden Signals**: Latency, Traffic, Errors, Saturation
2. **Variables reduce duplication**: One dashboard serves many use cases
3. **Choose panels wisely**: Right visualization for the data
4. **Explore for investigation**: Dashboards for monitoring
5. **Dashboard as code**: Version control your dashboards

## Further Reading

- [Grafana Documentation](https://grafana.com/docs/grafana/latest/) — Official docs
- [Grafonnet](https://grafana.github.io/grafonnet-lib/) — Dashboard as code
- [Dashboard Best Practices](https://grafana.com/docs/grafana/latest/best-practices/) — Official guide
- [LGTM Stack](https://grafana.com/oss/) — Complete observability

## Summary

Grafana transforms metrics into insights. The Four Golden Signals provide a framework for service health. Variables create reusable, maintainable dashboards. Explore mode enables rapid investigation during incidents. Dashboard as code brings version control to visualization. Together with Prometheus, Loki, and Tempo, Grafana forms a complete observability platform.

---

## Next Module

Continue to [Module 1.4: Logging with Loki](module-1.4-loki.md) to learn about log aggregation and analysis.
