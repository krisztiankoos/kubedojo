# Module 1.2: OpenTelemetry

> **Toolkit Track** | Complexity: `[COMPLEX]` | Time: 45-50 min

## Prerequisites

Before starting this module:
- [Module 1.1: Prometheus](module-1.1-prometheus.md)
- [Observability Theory Track](../../foundations/observability-theory/)
- Basic understanding of distributed tracing
- Familiarity with at least one programming language

## Why This Module Matters

The observability landscape was fragmented. Prometheus for metrics, Jaeger for traces, different agents for different backends. Each vendor had its own SDK. Switching vendors meant rewriting instrumentation code.

OpenTelemetry (OTel) unifies this chaos. One SDK, one protocol, any backend. Instrument once, export anywhere. It's become the industry standard—backed by every major observability vendor and cloud provider.

If you're building new services, OpenTelemetry is the instrumentation layer you should use.

## Did You Know?

- **OpenTelemetry merged OpenTracing and OpenCensus** in 2019, unifying two competing standards and ending years of fragmentation
- **OTel is the second most active CNCF project** after Kubernetes—with contributions from Google, Microsoft, AWS, and every major observability vendor
- **Auto-instrumentation can capture 80% of telemetry** with zero code changes—just deploy the OTel agent
- **The OTel Collector processes millions of spans per second** on modest hardware—it's designed for scale

## OpenTelemetry Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 OPENTELEMETRY ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  APPLICATION                                                     │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │     │
│  │  │   Traces     │  │   Metrics    │  │    Logs      │ │     │
│  │  │  (spans)     │  │  (counters)  │  │  (records)   │ │     │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │     │
│  │         │                 │                 │          │     │
│  │  ┌──────▼─────────────────▼─────────────────▼───────┐ │     │
│  │  │              OTel SDK                            │ │     │
│  │  │  • Context propagation                           │ │     │
│  │  │  • Batching & sampling                           │ │     │
│  │  │  • Export to collector                           │ │     │
│  │  └──────────────────────┬───────────────────────────┘ │     │
│  └─────────────────────────┼─────────────────────────────┘     │
│                            │                                    │
│                            │ OTLP (gRPC/HTTP)                   │
│                            ▼                                    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                   OTEL COLLECTOR                        │    │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐          │    │
│  │  │ Receivers│───▶│Processors│───▶│ Exporters│          │    │
│  │  │ (OTLP,   │    │ (batch,  │    │ (Jaeger, │          │    │
│  │  │  Jaeger, │    │  filter, │    │  Prom,   │          │    │
│  │  │  Zipkin) │    │  sample) │    │  Loki)   │          │    │
│  │  └──────────┘    └──────────┘    └──────────┘          │    │
│  └───────────────────────────┬────────────────────────────┘    │
│                              │                                  │
│           ┌──────────────────┼──────────────────┐              │
│           ▼                  ▼                  ▼              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │    Jaeger    │   │  Prometheus  │   │    Loki      │       │
│  │   (traces)   │   │   (metrics)  │   │    (logs)    │       │
│  └──────────────┘   └──────────────┘   └──────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Components

| Component | Purpose |
|-----------|---------|
| **SDK** | Instrument applications, create telemetry |
| **API** | Vendor-neutral interface for instrumentation |
| **OTLP** | OpenTelemetry Protocol—standard wire format |
| **Collector** | Receive, process, export telemetry |
| **Auto-instrumentation** | Instrument common libraries automatically |

### The Three Pillars in OTel

```
TRACES                    METRICS                   LOGS
─────────────────────────────────────────────────────────────────

Spans with context        Aggregated numbers        Discrete events
│                         │                         │
├─ TraceID (links)        ├─ Counter                ├─ Timestamp
├─ SpanID                 ├─ Gauge                  ├─ Severity
├─ ParentSpanID           ├─ Histogram              ├─ Body
├─ Attributes             ├─ Attributes             ├─ Attributes
└─ Events                 └─ Exemplars (→trace)     └─ TraceID (→trace)

All three can be correlated via TraceID and common attributes
```

### War Story: The Instrumentation Rewrite

A company used Jaeger for tracing, Prometheus for metrics, DataDog for logs. Three SDKs, three sets of instrumentation code, inconsistent context propagation.

When they wanted to switch tracing backends, they faced a six-month rewrite. Every service, every library, all the instrumentation code had to change.

With OpenTelemetry: they would have changed one line in the Collector config. Same instrumentation, different backend. That's the power of vendor-neutral telemetry.

## SDK Instrumentation

### Python Example

```python
# Install: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# Configure resource (service identity)
resource = Resource.create({
    "service.name": "order-service",
    "service.version": "1.0.0",
    "deployment.environment": "production",
})

# Configure tracer provider
provider = TracerProvider(resource=resource)

# Add OTLP exporter
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317")
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

# Set global tracer provider
trace.set_tracer_provider(provider)

# Get tracer
tracer = trace.get_tracer(__name__)

# Use tracer
@tracer.start_as_current_span("process_order")
def process_order(order_id: str):
    span = trace.get_current_span()
    span.set_attribute("order.id", order_id)

    # Nested span
    with tracer.start_as_current_span("validate_order") as child_span:
        child_span.set_attribute("validation.type", "full")
        validate(order_id)

    with tracer.start_as_current_span("save_order"):
        save(order_id)
```

### Java Example

```java
// Add dependency: io.opentelemetry:opentelemetry-api
// Add dependency: io.opentelemetry:opentelemetry-sdk
// Add dependency: io.opentelemetry:opentelemetry-exporter-otlp

import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;

public class OrderService {
    private static final Tracer tracer =
        GlobalOpenTelemetry.getTracer("order-service", "1.0.0");

    public void processOrder(String orderId) {
        Span span = tracer.spanBuilder("process_order")
            .setAttribute("order.id", orderId)
            .startSpan();

        try (Scope scope = span.makeCurrent()) {
            validateOrder(orderId);
            saveOrder(orderId);
        } catch (Exception e) {
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }

    private void validateOrder(String orderId) {
        Span span = tracer.spanBuilder("validate_order").startSpan();
        try (Scope scope = span.makeCurrent()) {
            // validation logic
        } finally {
            span.end();
        }
    }
}
```

### Metrics Example (Python)

```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Configure meter provider
exporter = OTLPMetricExporter(endpoint="http://otel-collector:4317")
reader = PeriodicExportingMetricReader(exporter, export_interval_millis=1000)
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

# Get meter
meter = metrics.get_meter(__name__)

# Create instruments
request_counter = meter.create_counter(
    name="http_requests_total",
    description="Total HTTP requests",
    unit="1",
)

request_duration = meter.create_histogram(
    name="http_request_duration_seconds",
    description="HTTP request duration",
    unit="s",
)

# Use instruments
def handle_request(method: str, path: str):
    start = time.time()
    try:
        # handle request
        request_counter.add(1, {"method": method, "path": path, "status": "200"})
    finally:
        duration = time.time() - start
        request_duration.record(duration, {"method": method, "path": path})
```

## Auto-Instrumentation

### Zero-Code Instrumentation

```
AUTO-INSTRUMENTATION
─────────────────────────────────────────────────────────────────

Without OTel Agent:              With OTel Agent:
┌────────────────────┐           ┌────────────────────┐
│  Your Application  │           │  Your Application  │
│                    │           │  (unchanged code)  │
│  No telemetry :(   │           │         │          │
│                    │           │         ▼          │
└────────────────────┘           │  ┌──────────────┐  │
                                 │  │  OTel Agent  │  │
                                 │  │  (injected)  │  │
                                 │  └──────┬───────┘  │
                                 │         │          │
                                 │  Traces, metrics,  │
                                 │  logs automatically │
                                 └────────────────────┘

Instruments:
• HTTP clients/servers (requests, Flask, FastAPI, Spring)
• Database clients (SQLAlchemy, JDBC, psycopg2)
• Message queues (Kafka, RabbitMQ)
• gRPC, Redis, AWS SDK, and more...
```

### Python Auto-Instrumentation

```bash
# Install
pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install

# Run with auto-instrumentation
opentelemetry-instrument \
  --traces_exporter otlp \
  --metrics_exporter otlp \
  --service_name my-service \
  --exporter_otlp_endpoint http://otel-collector:4317 \
  python app.py
```

### Java Agent

```bash
# Download agent
wget https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar

# Run with agent
java -javaagent:opentelemetry-javaagent.jar \
  -Dotel.service.name=my-service \
  -Dotel.exporter.otlp.endpoint=http://otel-collector:4317 \
  -jar myapp.jar
```

### Kubernetes Auto-Instrumentation

```yaml
# Using OTel Operator
apiVersion: opentelemetry.io/v1alpha1
kind: Instrumentation
metadata:
  name: auto-instrumentation
spec:
  exporter:
    endpoint: http://otel-collector:4317
  propagators:
    - tracecontext
    - baggage
  python:
    image: ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-python:latest
  java:
    image: ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-java:latest
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    metadata:
      annotations:
        # Enable auto-instrumentation for Python
        instrumentation.opentelemetry.io/inject-python: "true"
    spec:
      containers:
        - name: app
          image: my-python-app
```

## OTel Collector

### Collector Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     OTEL COLLECTOR                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  RECEIVERS                PROCESSORS              EXPORTERS      │
│  ┌──────────┐            ┌──────────┐           ┌──────────┐   │
│  │   otlp   │───────────▶│  batch   │──────────▶│   otlp   │   │
│  └──────────┘            └──────────┘           └──────────┘   │
│  ┌──────────┐            ┌──────────┐           ┌──────────┐   │
│  │  jaeger  │───────────▶│ memory   │──────────▶│  jaeger  │   │
│  └──────────┘            │ limiter  │           └──────────┘   │
│  ┌──────────┐            └──────────┘           ┌──────────┐   │
│  │prometheus│───────────▶┌──────────┐──────────▶│prometheus│   │
│  └──────────┘            │ filter   │           └──────────┘   │
│  ┌──────────┐            └──────────┘           ┌──────────┐   │
│  │  zipkin  │───────────▶┌──────────┐──────────▶│   loki   │   │
│  └──────────┘            │ sampling │           └──────────┘   │
│                          └──────────┘                           │
│                                                                  │
│  PIPELINES (connect receivers → processors → exporters)         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ traces:   receivers: [otlp]                              │   │
│  │           processors: [batch, sampling]                  │   │
│  │           exporters: [jaeger, otlp]                      │   │
│  │                                                          │   │
│  │ metrics:  receivers: [otlp, prometheus]                  │   │
│  │           processors: [batch]                            │   │
│  │           exporters: [prometheus]                        │   │
│  │                                                          │   │
│  │ logs:     receivers: [otlp]                              │   │
│  │           processors: [batch]                            │   │
│  │           exporters: [loki]                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Collector Configuration

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

  # Scrape Prometheus endpoints
  prometheus:
    config:
      scrape_configs:
        - job_name: 'otel-collector'
          static_configs:
            - targets: ['localhost:8888']

processors:
  # Batch for efficiency
  batch:
    timeout: 1s
    send_batch_size: 1024

  # Prevent OOM
  memory_limiter:
    check_interval: 1s
    limit_mib: 1000
    spike_limit_mib: 200

  # Add resource attributes
  resource:
    attributes:
      - key: environment
        value: production
        action: upsert

  # Filter out health checks
  filter:
    spans:
      exclude:
        match_type: regexp
        span_names:
          - "health.*"
          - "readiness.*"

exporters:
  # Export to Jaeger
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true

  # Export to Prometheus
  prometheus:
    endpoint: 0.0.0.0:8889

  # Export to another OTLP endpoint
  otlp:
    endpoint: tempo:4317
    tls:
      insecure: true

  # Debug logging
  logging:
    verbosity: detailed

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch, filter]
      exporters: [jaeger, otlp]

    metrics:
      receivers: [otlp, prometheus]
      processors: [memory_limiter, batch, resource]
      exporters: [prometheus]

    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [logging]
```

### Sampling Strategies

```yaml
processors:
  # Tail-based sampling (requires trace completion)
  tail_sampling:
    decision_wait: 10s
    num_traces: 100
    expected_new_traces_per_sec: 10
    policies:
      # Always sample errors
      - name: errors
        type: status_code
        status_code:
          status_codes: [ERROR]

      # Sample 10% of successful traces
      - name: success-sampling
        type: probabilistic
        probabilistic:
          sampling_percentage: 10

      # Always sample slow traces
      - name: latency
        type: latency
        latency:
          threshold_ms: 1000

  # Head-based sampling (decision at trace start)
  probabilistic_sampler:
    sampling_percentage: 25
```

## Context Propagation

### How Context Flows

```
CONTEXT PROPAGATION
─────────────────────────────────────────────────────────────────

Service A                    Service B                   Service C
┌──────────────┐            ┌──────────────┐           ┌──────────────┐
│   Span A     │            │   Span B     │           │   Span C     │
│  TraceID: X  │───HTTP────▶│  TraceID: X  │───gRPC───▶│  TraceID: X  │
│  SpanID: 1   │   Headers  │  SpanID: 2   │  Metadata │  SpanID: 3   │
│  Parent: -   │            │  Parent: 1   │           │  Parent: 2   │
└──────────────┘            └──────────────┘           └──────────────┘
       │                           │                          │
       │                           │                          │
       ▼                           ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DISTRIBUTED TRACE                        │
│                                                                 │
│  Span A ─────────────────────────────────────────────          │
│         └── Span B ──────────────────────────                  │
│                     └── Span C ────────────                    │
│                                                                 │
│  TraceID: X (same across all services)                         │
│  Each span knows its parent → forms tree                       │
└─────────────────────────────────────────────────────────────────┘
```

### Propagator Configuration

```python
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator

# Use multiple propagators for compatibility
propagator = CompositePropagator([
    TraceContextTextMapPropagator(),  # W3C standard
    W3CBaggagePropagator(),           # W3C baggage
    B3MultiFormat(),                   # Zipkin B3 (legacy)
])
set_global_textmap(propagator)
```

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| No resource attributes | Can't identify service | Set service.name, environment |
| Unbatched exports | High overhead | Use batch processor |
| No memory limits | Collector OOM | Configure memory_limiter |
| Missing propagation | Broken traces | Configure propagators consistently |
| Over-sampling | Cost explosion | Use tail sampling |
| No collector | Direct export overhead | Deploy collector as buffer |

## Quiz

Test your understanding:

<details>
<summary>1. Why use the OTel Collector instead of exporting directly from apps?</summary>

**Answer**: The Collector provides:
- **Buffering**: Handles backend unavailability
- **Batching**: Efficient network usage
- **Processing**: Filter, sample, transform
- **Protocol conversion**: Receive in one format, export in another
- **Centralized config**: Change exporters without app changes
- **Reduced app overhead**: Offload processing to collector
</details>

<details>
<summary>2. What's the difference between head-based and tail-based sampling?</summary>

**Answer**:
- **Head-based**: Decision made at trace start (probabilistic). Simple, but might miss interesting traces.
- **Tail-based**: Decision made after trace completes. Can sample based on latency, errors, attributes. More powerful but requires buffering complete traces.

Use tail-based when you need to capture all errors or slow traces.
</details>

<details>
<summary>3. How does context propagation work across services?</summary>

**Answer**: Context flows via HTTP headers or gRPC metadata:
1. Service A creates span, injects TraceID/SpanID into headers
2. HTTP client adds headers: `traceparent: 00-{traceId}-{spanId}-01`
3. Service B extracts headers, creates child span with same TraceID
4. Child span's ParentSpanID = Service A's SpanID

This creates a linked trace across all services.
</details>

<details>
<summary>4. When should you use auto-instrumentation vs. manual?</summary>

**Answer**:
- **Auto-instrumentation**: HTTP, database, messaging libraries. Get 80% coverage with zero code.
- **Manual instrumentation**: Business logic, custom spans for important operations, adding specific attributes.

Best practice: Start with auto-instrumentation, add manual spans for business-critical paths.
</details>

## Hands-On Exercise: End-to-End Observability

Deploy OTel Collector and instrument an application:

### Setup

```bash
# Create namespace
kubectl create namespace observability

# Deploy OTel Collector
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
  namespace: observability
data:
  config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318

    processors:
      batch:
        timeout: 1s
      memory_limiter:
        check_interval: 1s
        limit_mib: 512

    exporters:
      logging:
        verbosity: detailed
      prometheus:
        endpoint: 0.0.0.0:8889

    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [logging]
        metrics:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [prometheus]
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otel-collector
  namespace: observability
spec:
  replicas: 1
  selector:
    matchLabels:
      app: otel-collector
  template:
    metadata:
      labels:
        app: otel-collector
    spec:
      containers:
        - name: collector
          image: otel/opentelemetry-collector-contrib:latest
          args: ["--config=/etc/otel/config.yaml"]
          ports:
            - containerPort: 4317
            - containerPort: 4318
            - containerPort: 8889
          volumeMounts:
            - name: config
              mountPath: /etc/otel
      volumes:
        - name: config
          configMap:
            name: otel-collector-config
---
apiVersion: v1
kind: Service
metadata:
  name: otel-collector
  namespace: observability
spec:
  selector:
    app: otel-collector
  ports:
    - name: otlp-grpc
      port: 4317
    - name: otlp-http
      port: 4318
    - name: prometheus
      port: 8889
EOF
```

### Step 1: Create Instrumented App

```python
# app.py
from flask import Flask, request
import time
import random

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Configure resource
resource = Resource.create({
    "service.name": "demo-app",
    "service.version": "1.0.0",
})

# Configure tracing
trace_provider = TracerProvider(resource=resource)
trace_exporter = OTLPSpanExporter(endpoint="otel-collector.observability:4317", insecure=True)
trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
trace.set_tracer_provider(trace_provider)

# Configure metrics
metric_exporter = OTLPMetricExporter(endpoint="otel-collector.observability:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
metric_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(metric_provider)

# Create instruments
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)
request_counter = meter.create_counter("http_requests_total")

# Create Flask app
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/")
def hello():
    request_counter.add(1, {"path": "/", "method": "GET"})
    return "Hello, OTel!"

@app.route("/slow")
def slow():
    with tracer.start_as_current_span("slow_operation") as span:
        delay = random.uniform(0.5, 2.0)
        span.set_attribute("delay", delay)
        time.sleep(delay)
    request_counter.add(1, {"path": "/slow", "method": "GET"})
    return f"Slept for {delay:.2f}s"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

### Step 2: Deploy App

```yaml
# demo-app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app
  namespace: observability
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-app
  template:
    metadata:
      labels:
        app: demo-app
    spec:
      containers:
        - name: app
          image: python:3.10
          command: ["python", "-u", "/app/app.py"]
          ports:
            - containerPort: 8080
          volumeMounts:
            - name: app-code
              mountPath: /app
          env:
            - name: OTEL_EXPORTER_OTLP_ENDPOINT
              value: "http://otel-collector:4317"
      volumes:
        - name: app-code
          configMap:
            name: demo-app-code
```

### Step 3: Verify Telemetry

```bash
# Check collector logs for traces
kubectl logs -n observability -l app=otel-collector -f

# Port-forward to Prometheus endpoint
kubectl port-forward -n observability svc/otel-collector 8889:8889

# Query metrics
curl localhost:8889/metrics | grep http_requests
```

### Success Criteria

You've completed this exercise when you can:
- [ ] Deploy OTel Collector with OTLP receiver
- [ ] See traces in collector logs
- [ ] Query metrics from Prometheus endpoint
- [ ] Understand the trace → span relationship

## Key Takeaways

1. **OTel unifies observability**: One SDK, any backend
2. **Collector is essential**: Buffer, process, export
3. **Auto-instrumentation gets you started**: Add manual spans for business logic
4. **Context propagation links services**: TraceID flows via headers
5. **Sampling controls costs**: Tail sampling for best results

## Further Reading

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/) — Official docs
- [OTel Collector Contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib) — Additional components
- [OTel Demo App](https://github.com/open-telemetry/opentelemetry-demo) — Full reference architecture
- [Practical OpenTelemetry](https://www.honeycomb.io/opentelemetry) — Honeycomb's guide

## Summary

OpenTelemetry is the future of observability instrumentation. Its vendor-neutral approach, comprehensive language support, and powerful Collector make it the standard for cloud-native applications. Auto-instrumentation provides immediate value, while manual instrumentation adds business context. The Collector centralizes processing and enables flexible routing to any backend.

---

## Next Module

Continue to [Module 1.3: Grafana](module-1.3-grafana.md) to learn about visualization and dashboards for your telemetry.
