# Module 1.5: Distributed Tracing

> **Toolkit Track** | Complexity: `[COMPLEX]` | Time: 45-50 min

## Prerequisites

Before starting this module:
- [Module 1.2: OpenTelemetry](module-1.2-opentelemetry.md) — Instrumentation fundamentals
- [Module 1.1: Prometheus](module-1.1-prometheus.md) — Understanding metrics
- [Module 1.4: Loki](module-1.4-loki.md) — Log correlation (recommended)
- Familiarity with microservices architecture

## Why This Module Matters

In a monolith, debugging is straightforward: stack traces tell you what happened. In microservices, a single user request might touch 20 services across 5 teams. When something fails, you need to see the entire journey.

Distributed tracing solves this. It connects the dots across services, showing exactly where latency hides and where errors originate. Without tracing, debugging distributed systems is guesswork.

## Did You Know?

- **Google's Dapper paper (2010) started it all**—it described how Google traces every request across their massive infrastructure, inspiring Jaeger, Zipkin, and eventually OpenTelemetry
- **A single trace can have thousands of spans**—complex e-commerce transactions might generate 500+ spans across dozens of services
- **Traces are sampled, not exhaustive**—storing every trace would be prohibitively expensive; most systems sample 1-10% of traffic
- **The W3C Trace Context standard ensures interoperability**—headers like `traceparent` work across languages, frameworks, and vendors

## Tracing Concepts

### The Anatomy of a Trace

```
┌─────────────────────────────────────────────────────────────────┐
│                          TRACE                                   │
│  trace_id: abc123                                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Time ──────────────────────────────────────────────────────▶   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ SPAN: api-gateway                                           ││
│  │ span_id: s1  parent: none  duration: 500ms                  ││
│  │ ┌───────────────────────────────────────────────────────┐   ││
│  │ │                                                       │   ││
│  │ │  ┌──────────────────────────────────────────────────┐ │   ││
│  │ │  │ SPAN: user-service                               │ │   ││
│  │ │  │ span_id: s2  parent: s1  duration: 150ms        │ │   ││
│  │ │  │ ┌──────────────────────────┐                    │ │   ││
│  │ │  │ │ SPAN: postgres          │                    │ │   ││
│  │ │  │ │ span_id: s3  parent: s2 │                    │ │   ││
│  │ │  │ │ duration: 50ms          │                    │ │   ││
│  │ │  │ └──────────────────────────┘                    │ │   ││
│  │ │  └──────────────────────────────────────────────────┘ │   ││
│  │ │                                                       │   ││
│  │ │  ┌──────────────────────────────────────────────────┐ │   ││
│  │ │  │ SPAN: order-service                              │ │   ││
│  │ │  │ span_id: s4  parent: s1  duration: 300ms        │ │   ││
│  │ │  │ ┌────────────────┐ ┌─────────────────────┐      │ │   ││
│  │ │  │ │ SPAN: redis   │ │ SPAN: payment-api   │      │ │   ││
│  │ │  │ │ s5 (20ms)     │ │ s6 (200ms)          │      │ │   ││
│  │ │  │ └────────────────┘ └─────────────────────┘      │ │   ││
│  │ │  └──────────────────────────────────────────────────┘ │   ││
│  │ │                                                       │   ││
│  │ └───────────────────────────────────────────────────────┘   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Terminology

| Term | Definition |
|------|------------|
| **Trace** | The complete journey of a request through the system |
| **Span** | A single unit of work (e.g., HTTP call, DB query) |
| **Trace ID** | Unique identifier for the entire trace |
| **Span ID** | Unique identifier for a specific span |
| **Parent Span ID** | Links child span to parent |
| **Baggage** | Key-value pairs propagated across all spans |
| **Context Propagation** | Passing trace context between services |

### W3C Trace Context

```http
# Standard headers for trace propagation
traceparent: 00-abc123def456-789xyz-01
              │  │              │     │
              │  │              │     └── Flags (sampled)
              │  │              └── Parent span ID
              │  └── Trace ID
              └── Version

tracestate: vendor1=value1,vendor2=value2
            └── Vendor-specific data
```

## Tracing Backends

### Comparing Solutions

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRACING BACKENDS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  JAEGER                         TEMPO                            │
│  ┌─────────────────────┐       ┌─────────────────────┐          │
│  │ • CNCF graduated    │       │ • Grafana project   │          │
│  │ • Battle-tested     │       │ • Object storage    │          │
│  │ • Full-text search  │       │ • Cost-effective    │          │
│  │ • Cassandra/ES      │       │ • Log correlation   │          │
│  │ • Self-contained UI │       │ • Grafana native    │          │
│  └─────────────────────┘       └─────────────────────┘          │
│                                                                  │
│  ZIPKIN                         AWS X-RAY                        │
│  ┌─────────────────────┐       ┌─────────────────────┐          │
│  │ • Original OSS      │       │ • AWS native        │          │
│  │ • Simple setup      │       │ • Service maps      │          │
│  │ • Limited scale     │       │ • AWS integration   │          │
│  │ • MySQL/Cassandra   │       │ • Vendor lock-in    │          │
│  └─────────────────────┘       └─────────────────────┘          │
│                                                                  │
│  RECOMMENDATION:                                                 │
│  • Grafana stack → Tempo (seamless integration)                 │
│  • Need search → Jaeger (tag-based queries)                     │
│  • AWS-native → X-Ray (no extra infrastructure)                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Jaeger

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    JAEGER ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Applications                                                    │
│  ┌──────┐ ┌──────┐ ┌──────┐                                     │
│  │ App1 │ │ App2 │ │ App3 │                                     │
│  └──┬───┘ └──┬───┘ └──┬───┘                                     │
│     │        │        │                                          │
│     └────────┼────────┘                                          │
│              │ OTLP / Jaeger protocol                            │
│              ▼                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    JAEGER COLLECTOR                       │   │
│  │  • Validates spans                                        │   │
│  │  • Processes and indexes                                  │   │
│  │  • Writes to storage                                      │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│              ┌────────────┼────────────┐                        │
│              ▼            ▼            ▼                        │
│  ┌────────────────┐ ┌──────────┐ ┌──────────┐                  │
│  │  Elasticsearch │ │ Cassandra│ │ Badger   │                  │
│  │  (production)  │ │ (scale)  │ │ (dev)    │                  │
│  └────────────────┘ └──────────┘ └──────────┘                  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    JAEGER QUERY                           │   │
│  │  • Serves UI                                              │   │
│  │  • REST/gRPC API                                          │   │
│  │  • Search by tags, service, operation                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Deploying Jaeger

```yaml
# jaeger-allinone.yaml (development)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
  namespace: tracing
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
        - name: jaeger
          image: jaegertracing/all-in-one:1.50
          ports:
            - containerPort: 16686  # UI
            - containerPort: 4317   # OTLP gRPC
            - containerPort: 4318   # OTLP HTTP
            - containerPort: 14268  # Jaeger HTTP
            - containerPort: 6831   # Jaeger UDP (compact)
          env:
            - name: COLLECTOR_OTLP_ENABLED
              value: "true"
          resources:
            limits:
              memory: 1Gi
---
apiVersion: v1
kind: Service
metadata:
  name: jaeger
  namespace: tracing
spec:
  ports:
    - name: ui
      port: 16686
    - name: otlp-grpc
      port: 4317
    - name: otlp-http
      port: 4318
  selector:
    app: jaeger
```

### Jaeger with Elasticsearch (Production)

```yaml
# jaeger-production.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger-collector
  namespace: tracing
spec:
  replicas: 3
  selector:
    matchLabels:
      app: jaeger-collector
  template:
    metadata:
      labels:
        app: jaeger-collector
    spec:
      containers:
        - name: collector
          image: jaegertracing/jaeger-collector:1.50
          ports:
            - containerPort: 4317
            - containerPort: 14268
          env:
            - name: SPAN_STORAGE_TYPE
              value: elasticsearch
            - name: ES_SERVER_URLS
              value: http://elasticsearch:9200
            - name: ES_INDEX_PREFIX
              value: jaeger
            - name: COLLECTOR_OTLP_ENABLED
              value: "true"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger-query
  namespace: tracing
spec:
  replicas: 2
  selector:
    matchLabels:
      app: jaeger-query
  template:
    metadata:
      labels:
        app: jaeger-query
    spec:
      containers:
        - name: query
          image: jaegertracing/jaeger-query:1.50
          ports:
            - containerPort: 16686
          env:
            - name: SPAN_STORAGE_TYPE
              value: elasticsearch
            - name: ES_SERVER_URLS
              value: http://elasticsearch:9200
```

### Jaeger Operator

```yaml
# Operator-based deployment
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: production
  namespace: tracing
spec:
  strategy: production  # vs allInOne

  collector:
    replicas: 3
    resources:
      limits:
        cpu: 1
        memory: 1Gi

  query:
    replicas: 2

  storage:
    type: elasticsearch
    elasticsearch:
      nodeCount: 3
      resources:
        limits:
          memory: 4Gi
      redundancyPolicy: SingleRedundancy

  ingress:
    enabled: true
```

## Grafana Tempo

### Why Tempo?

```
TEMPO'S KEY INSIGHT: Traces are append-only, search by ID is enough

Traditional (Jaeger):                 Tempo:
─────────────────────────────────────────────────────────────────

Store + Index everything:            Store only, index nothing:
• Elasticsearch cluster              • Object storage (S3/GCS)
• Index spans by tags                • Traces by ID only
• Search: service, operation         • Search: trace ID
• Cost: $$$                          • Cost: $

Finding traces:                      Finding traces:
1. Search Jaeger UI                  1. Metrics show problem
2. Find trace by tags                2. Exemplars link to trace ID
                                     3. Logs contain trace ID
                                     4. Look up trace directly

Best for:                            Best for:
• Need tag-based search              • Grafana stack users
• Unknown trace IDs                  • Cost-conscious
• Debugging without metrics          • Metrics-to-traces workflow
```

### Tempo Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TEMPO ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Spans via OTLP                                                  │
│       │                                                          │
│       ▼                                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    DISTRIBUTOR                            │   │
│  │  • Receives spans                                         │   │
│  │  • Hashes trace ID                                        │   │
│  │  • Routes to ingester                                     │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    INGESTER                               │   │
│  │  • Batches spans by trace                                 │   │
│  │  • Holds in memory (WAL)                                  │   │
│  │  • Flushes to object storage                              │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 OBJECT STORAGE                            │   │
│  │  ┌─────────────────┐ ┌─────────────────┐                 │   │
│  │  │  Blocks         │ │  Bloom Filters  │                 │   │
│  │  │  (compressed    │ │  (trace ID      │                 │   │
│  │  │   trace data)   │ │   lookup)       │                 │   │
│  │  └─────────────────┘ └─────────────────┘                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ▲                                      │
│                           │                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    QUERIER                                │   │
│  │  • Receives trace ID queries                              │   │
│  │  • Checks bloom filters                                   │   │
│  │  • Fetches matching blocks                                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ▲                                      │
│                           │                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    QUERY FRONTEND                         │   │
│  │  • Caching                                                │   │
│  │  • Query splitting                                        │   │
│  │  • TraceQL processing                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Deploying Tempo

```yaml
# tempo-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: tempo-config
  namespace: tracing
data:
  tempo.yaml: |
    server:
      http_listen_port: 3200

    distributor:
      receivers:
        otlp:
          protocols:
            grpc:
              endpoint: 0.0.0.0:4317
            http:
              endpoint: 0.0.0.0:4318
        jaeger:
          protocols:
            thrift_http:
              endpoint: 0.0.0.0:14268

    ingester:
      trace_idle_period: 10s
      max_block_bytes: 1_000_000
      max_block_duration: 5m

    compactor:
      compaction:
        block_retention: 48h

    storage:
      trace:
        backend: s3
        s3:
          bucket: tempo-traces
          endpoint: s3.amazonaws.com
          region: us-east-1
        wal:
          path: /var/tempo/wal
        local:
          path: /var/tempo/blocks

    querier:
      frontend_worker:
        frontend_address: tempo-query-frontend:9095

    query_frontend:
      search:
        duration_slo: 5s
        throughput_bytes_slo: 1073741824
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tempo
  namespace: tracing
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tempo
  template:
    metadata:
      labels:
        app: tempo
    spec:
      containers:
        - name: tempo
          image: grafana/tempo:2.3.0
          args:
            - -config.file=/etc/tempo/tempo.yaml
          ports:
            - containerPort: 3200  # HTTP
            - containerPort: 4317  # OTLP gRPC
            - containerPort: 4318  # OTLP HTTP
          volumeMounts:
            - name: config
              mountPath: /etc/tempo
            - name: storage
              mountPath: /var/tempo
      volumes:
        - name: config
          configMap:
            name: tempo-config
        - name: storage
          emptyDir: {}
```

### TraceQL (Tempo's Query Language)

```traceql
# Find traces by service name
{ resource.service.name = "api-gateway" }

# Find slow spans
{ span.http.status_code >= 500 && duration > 1s }

# Find traces with errors
{ status = error }

# Find specific operation
{ name = "HTTP GET /users" }

# Combine conditions
{
  resource.service.name = "payment-service" &&
  span.http.method = "POST" &&
  duration > 500ms
}

# Aggregate: Find slowest operations
{ resource.service.name = "api" } | avg(duration) by (name)

# Pipeline: Filter then aggregate
{ duration > 100ms } | count() by (resource.service.name)
```

## Sampling Strategies

### Why Sample?

```
THE SAMPLING MATH:

1000 requests/second × 50 spans/request × 1KB/span = 50 MB/second
                                                    = 4.3 TB/day
                                                    = 130 TB/month

At 10% sampling:
100 requests/second × 50 spans/request × 1KB/span = 5 MB/second
                                                   = 432 GB/day
                                                   = 13 TB/month

RULE OF THUMB: Sample enough to catch errors, not so much you go broke
```

### Sampling Types

```
┌─────────────────────────────────────────────────────────────────┐
│                    SAMPLING STRATEGIES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  HEAD-BASED SAMPLING                                             │
│  Decision at trace start                                         │
│  ┌─────┐                                                         │
│  │ App │──▶ Random: 10% sampled ──▶ Propagate decision          │
│  └─────┘                           (all or nothing)              │
│                                                                  │
│  Pros: Simple, consistent                                        │
│  Cons: Might miss errors (if not sampled)                       │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  TAIL-BASED SAMPLING                                             │
│  Decision after trace complete                                   │
│  ┌─────┐     ┌─────────────┐     ┌──────────────────┐           │
│  │ App │──▶  │  Collector  │──▶  │ Keep if:         │           │
│  └─────┘     │  (buffer)   │     │ • Error occurred │           │
│              └─────────────┘     │ • Latency > 1s   │           │
│                                  │ • Important user │           │
│                                  └──────────────────┘           │
│                                                                  │
│  Pros: Never miss errors, smart decisions                       │
│  Cons: Complex, memory-intensive                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### OpenTelemetry Collector Tail Sampling

```yaml
# otel-collector-config.yaml
processors:
  tail_sampling:
    decision_wait: 10s  # Wait for all spans
    num_traces: 100000  # Traces in memory
    policies:
      # Always keep errors
      - name: errors
        type: status_code
        status_code:
          status_codes: [ERROR]

      # Always keep slow traces
      - name: slow-traces
        type: latency
        latency:
          threshold_ms: 1000

      # Always keep specific endpoints
      - name: important-endpoints
        type: string_attribute
        string_attribute:
          key: http.url
          values: ["/checkout", "/payment"]

      # Sample everything else at 10%
      - name: probabilistic
        type: probabilistic
        probabilistic:
          sampling_percentage: 10

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [tail_sampling, batch]
      exporters: [jaeger]
```

## Correlating Signals

### The Three Pillars Connected

```
┌─────────────────────────────────────────────────────────────────┐
│                    SIGNAL CORRELATION                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  WORKFLOW: Something is broken, find out why                    │
│                                                                  │
│  1. METRICS show problem                                         │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │ http_request_duration_seconds{...} = 5.2s ◀── SLOW!     │ │
│     │                                                          │ │
│     │ histogram has "exemplar" → trace_id: abc123             │ │
│     └─────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  2. TRACE shows journey                                          │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │ trace_id: abc123                                         │ │
│     │ ├─ api-gateway (50ms)                                    │ │
│     │ │  └─ user-service (100ms)                               │ │
│     │ │     └─ postgres (3000ms) ◀── HERE'S THE PROBLEM!      │ │
│     │ └─ order-service (200ms)                                 │ │
│     └─────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  3. LOGS show details                                            │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │ {trace_id="abc123"} | json                               │ │
│     │                                                          │ │
│     │ 10:30:01 user-service: Query started                     │ │
│     │ 10:30:04 postgres: Lock wait timeout exceeded           │ │
│     │ 10:30:04 user-service: Query failed, retrying           │ │
│     └─────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Exemplars in Prometheus

```yaml
# Enable exemplars in your app
from prometheus_client import Histogram
from opentelemetry import trace

histogram = Histogram('http_request_duration_seconds', 'Request duration')

def handle_request():
    span = trace.get_current_span()
    trace_id = span.get_span_context().trace_id

    with histogram.time() as metric:
        # Handle request
        process_request()

    # Attach trace_id as exemplar
    metric.observe(duration, {'trace_id': format(trace_id, '032x')})
```

```yaml
# Prometheus config to scrape exemplars
scrape_configs:
  - job_name: 'my-app'
    scrape_interval: 15s
    # Enable exemplar scraping (requires Prometheus 2.27+)
    enable_exemplars: true
```

### Grafana Correlation

```yaml
# Grafana data sources configured for correlation
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    jsonData:
      exemplarTraceIdDestinations:
        - name: trace_id
          datasourceUid: tempo

  - name: Tempo
    type: tempo
    uid: tempo
    url: http://tempo:3200
    jsonData:
      tracesToLogs:
        datasourceUid: loki
        tags: ['service.name']
        mappedTags: [{ key: 'service.name', value: 'app' }]
        mapTagNamesEnabled: true

  - name: Loki
    type: loki
    uid: loki
    url: http://loki:3100
    jsonData:
      derivedFields:
        - name: TraceID
          matcherRegex: '"trace_id":"(\w+)"'
          url: '${__value.raw}'
          datasourceUid: tempo
```

## Common Mistakes

| Mistake | Why It's Bad | Better Approach |
|---------|--------------|-----------------|
| Storing 100% of traces | Costs explode, storage overload | Sample at 1-10%, keep all errors |
| Missing context propagation | Traces disconnect at service boundaries | Use OTel auto-instrumentation, verify headers |
| Too many spans | Cardinality issues, hard to read | Span meaningful operations, not every function |
| Not correlating signals | Miss the full picture | Add trace_id to logs, use exemplars |
| Ignoring sampling bias | Missing rare errors | Use tail-based sampling for errors |
| No service name in spans | Can't filter by service | Always set `service.name` resource attribute |

## War Story: The Missing Trace

A team deployed distributed tracing across 50 microservices. Everything worked in staging. In production, traces stopped at service boundaries—only showing the first hop.

After days of debugging, they found the issue: their API gateway was stripping "unknown" headers, including `traceparent`. The gateway team had enabled a security feature that removed headers not in an allowlist.

**The fix**: Add `traceparent` and `tracestate` to the gateway's header allowlist.

**The lesson**: Trace context propagation requires every hop to pass headers. One misconfigured proxy breaks the entire trace. Test production-like configurations, not just application code.

## Quiz

### Question 1
Why is tail-based sampling more expensive than head-based sampling?

<details>
<summary>Show Answer</summary>

Tail-based sampling requires:

1. **Memory**: Must buffer all spans until the trace is complete (could be seconds or minutes)
2. **Compute**: Analyzes every span to decide if the trace is interesting (errors, high latency)
3. **Network**: Must receive ALL spans before deciding, then discard most

Head-based sampling decides at trace start:
- Uses minimal memory (just a random number)
- No analysis needed
- Discarded spans never sent

A trace with 100 spans: tail-based must process all 100 before discarding 90%. Head-based discards 90% immediately, never sending the spans at all.
</details>

### Question 2
How would you find all traces where a payment-service call took longer than 500ms?

<details>
<summary>Show Answer</summary>

**In Jaeger:**
1. Service: payment-service
2. Tags: `http.status_code=*` (any)
3. Min Duration: 500ms
4. Search

**In Tempo with TraceQL:**
```traceql
{
  resource.service.name = "payment-service" &&
  duration > 500ms
}
```

**Via metrics → exemplars:**
1. Query Prometheus: `histogram_quantile(0.99, http_request_duration_seconds_bucket{service="payment"})`
2. Click data point with high latency
3. View exemplar → links to trace ID
4. Open in Tempo/Jaeger
</details>

### Question 3
A trace shows gaps—services A→B→C are traced, but C→D appears as a separate trace. What's likely wrong?

<details>
<summary>Show Answer</summary>

Context propagation is broken between C and D. Common causes:

1. **Missing instrumentation**: Service C might be making HTTP calls without the OTel HTTP client instrumentation. The outgoing call doesn't include `traceparent` header.

2. **Header stripping**: A proxy, API gateway, or service mesh between C and D might be removing the trace headers.

3. **Async communication**: If C→D uses a message queue, you need specific instrumentation to propagate context through messages. Default HTTP instrumentation won't help.

4. **Different tracing systems**: C might use Jaeger client, D might use Zipkin—they need compatible propagation format (W3C Trace Context works across both).

Debug by checking: Do the HTTP requests from C include `traceparent` header? Does D receive and extract it?
</details>

### Question 4
You see a trace where user-service took 2 seconds, but all its child spans (db queries, cache calls) total only 200ms. Where did 1.8 seconds go?

<details>
<summary>Show Answer</summary>

The 1.8 seconds is "dark time"—work happening outside of instrumented operations. Common causes:

1. **CPU-bound code**: JSON parsing, business logic, serialization—typically not instrumented as spans

2. **Uninstrumented I/O**: File system operations, non-HTTP network calls, DNS lookups

3. **Garbage collection**: Long GC pauses appear as gaps in traces

4. **Thread pool waiting**: Time waiting for a thread to become available

5. **Missing child spans**: Some operations might not be instrumented (internal service calls, cache client)

To find it:
- Add spans around suspicious code blocks
- Profile the application (CPU, memory)
- Check for GC pauses in JVM/runtime logs
- Verify all I/O operations are instrumented
</details>

## Hands-On Exercise

### Scenario: End-to-End Tracing Investigation

Set up a traced application and practice navigating from metrics to traces to logs.

### Setup

```bash
# Create kind cluster
kind create cluster --name tracing-lab

# Install the full observability stack
kubectl create namespace tracing

# Deploy Tempo
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: tempo-config
  namespace: tracing
data:
  tempo.yaml: |
    server:
      http_listen_port: 3200
    distributor:
      receivers:
        otlp:
          protocols:
            grpc:
              endpoint: 0.0.0.0:4317
    ingester:
      trace_idle_period: 10s
      max_block_duration: 5m
    storage:
      trace:
        backend: local
        local:
          path: /var/tempo/traces
        wal:
          path: /var/tempo/wal
    query_frontend:
      search:
        duration_slo: 5s
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tempo
  namespace: tracing
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tempo
  template:
    metadata:
      labels:
        app: tempo
    spec:
      containers:
        - name: tempo
          image: grafana/tempo:2.3.0
          args: ["-config.file=/etc/tempo/tempo.yaml"]
          ports:
            - containerPort: 3200
            - containerPort: 4317
          volumeMounts:
            - name: config
              mountPath: /etc/tempo
            - name: storage
              mountPath: /var/tempo
      volumes:
        - name: config
          configMap:
            name: tempo-config
        - name: storage
          emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: tempo
  namespace: tracing
spec:
  ports:
    - name: http
      port: 3200
    - name: otlp-grpc
      port: 4317
  selector:
    app: tempo
EOF

# Wait for Tempo
kubectl -n tracing wait --for=condition=ready pod -l app=tempo --timeout=120s
```

### Deploy Traced Application

```yaml
# traced-app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: traced-demo
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: traced-demo
  template:
    metadata:
      labels:
        app: traced-demo
    spec:
      containers:
        - name: app
          image: jaegertracing/example-hotrod:1.50
          ports:
            - containerPort: 8080
          env:
            - name: OTEL_EXPORTER_OTLP_ENDPOINT
              value: "http://tempo.tracing.svc.cluster.local:4317"
            - name: OTEL_SERVICE_NAME
              value: "hotrod"
```

```bash
kubectl apply -f traced-app.yaml

# Port forward to access the demo app
kubectl port-forward svc/traced-demo 8080:8080 &

# Port forward Tempo
kubectl -n tracing port-forward svc/tempo 3200:3200 &
```

### Investigation Tasks

1. **Generate traces**
   - Open http://localhost:8080
   - Click different buttons to request rides
   - Each click generates a multi-service trace

2. **Query Tempo**
   ```bash
   # List trace IDs
   curl "http://localhost:3200/api/search?limit=10"

   # Get a specific trace
   curl "http://localhost:3200/api/traces/<trace-id>"
   ```

3. **Use TraceQL**
   ```traceql
   # Find slow driver lookups
   { name = "SQL SELECT" && duration > 100ms }

   # Find errors
   { status = error }
   ```

4. **Practice correlation**
   - Note a trace ID from a slow request
   - Search logs for that trace ID
   - Understand the full request journey

### Success Criteria

- [ ] Can generate traces from the demo app
- [ ] Can query traces by service name
- [ ] Can find slow operations within a trace
- [ ] Understand parent-child span relationships
- [ ] Can explain where latency accumulates

### Cleanup

```bash
kind delete cluster --name tracing-lab
```

## Next Steps

Congratulations! You've completed the Observability Toolkit. You now understand:
- **Prometheus** for metrics
- **OpenTelemetry** for instrumentation
- **Grafana** for visualization
- **Loki** for logs
- **Jaeger/Tempo** for traces

Consider exploring:
- [GitOps & Deployments Toolkit](../gitops-deployments/) — Deploy your observable applications
- [SRE Discipline](../../disciplines/sre/) — Apply observability for reliability

---

*"A trace is a story. Each span is a chapter. The trace ID is how you find the book. Learn to read the story, and you'll solve mysteries others can't even see."*
