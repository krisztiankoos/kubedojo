---
title: "Module 1.2: Argo Events \u2014 Event-Driven Automation for Kubernetes"
slug: k8s/capa/module-1.2-argo-events
sidebar:
  order: 3
---
> **Complexity**: `[COMPLEX]` — Multiple interacting CRDs and integration patterns
>
> **Time to Complete**: 50-60 minutes
>
> **Prerequisites**: Module 1 (Argo Workflows basics), familiarity with Kubernetes CRDs
>
> **CAPA Domain**: 4 — Argo Events (12% of exam)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Design** event-driven architectures using Argo Events' fundamental components: EventSource, Sensor, and EventBus, orchestrating complex distributed workflows.
2. **Implement** Sensor triggers that dynamically submit Argo Workflows, create Kubernetes objects, or execute HTTP requests based on real-time event filtering.
3. **Compare** and evaluate EventBus backend implementations (NATS JetStream vs Kafka) based on persistence, delivery guarantees, and scalability requirements.
4. **Diagnose** event pipeline failures by analyzing EventSource configurations, Sensor dependency logic, and EventBus message routing, resolving common misconfigurations.
5. **Evaluate** security postures by properly integrating Kubernetes Secrets for webhooks, cloud provider authentication, and Kafka cluster connectivity.

---

## Why This Module Matters

Imagine a global e-commerce platform processing thousands of orders per minute during a holiday sale. Every order placed, every payment processed, and every inventory update represents a distinct state change. For years, the platform engineering team at "GlobalRetail Inc." relied on traditional cron-based scripts to process these changes. They had dozens of scheduled jobs polling cloud storage buckets, querying external APIs, and searching message queues. 

This polling architecture was inherently fragile. During peak traffic, the polling scripts hit aggressive API rate limits, causing massive delays. Worse, the delay between an event occurring and the polling script detecting it meant that fulfillment pipelines were consistently lagging behind real-time customer expectations. When one script failed at 3:00 AM, the entire fulfillment chain halted, leading to significant financial impact and exhausted engineers diagnosing undocumented shell scripts.

By migrating to an Event-Driven Architecture (EDA) with Argo Events, the team eliminated polling entirely. Instead of asking "did anything change?", the infrastructure natively reacted to events the millisecond they occurred. Argo Events provided a declarative, Kubernetes-native nervous system. Events flowed in through standardized ingress points, decisions were made dynamically via dependency logic, and actions were triggered instantly. No glue code, no rate limits, and no 3:00 AM pages. Mastering this framework allows you to build highly scalable, reactive automation that operates cleanly within the Kubernetes ecosystem.

---

## Did You Know?

- **Argo was accepted to CNCF on March 26, 2020** and officially moved to graduated maturity on December 6, 2022, cementing its status as an enterprise-grade solution.
- **Argo Events supports 20+ event sources and 10+ triggers**, allowing deep integration with almost any cloud-native system or external provider.
- **The EventBus uses NATS JetStream by default**, providing robust at-least-once delivery and event persistence natively, without requiring you to manage a separate standalone message broker.
- **Argo Events standardizes on CloudEvents version 1.0**, which is a CNCF graduated specification ensuring your event payloads are universally portable across different cloud providers.

---

## Part 1: Event-Driven Architecture (EDA) Fundamentals

### 1.1 Why Events?

There are two fundamental ways for a system to detect that a state change has occurred: polling and reactive events.

| Approach | How It Works | Downside |
|----------|-------------|----------|
| **Polling** | Ask "did anything change?" on a timer | Wastes resources, delayed detection, API rate limits |
| **Reactive (events)** | Get notified the instant something changes | Requires event infrastructure |

Polling architectures consume compute cycles even when no work needs to be done. They suffer from the "polling paradox": poll too infrequently, and your system's latency increases; poll too frequently, and you overwhelm external APIs or databases. Event-driven architectures resolve this by inverting the communication flow. Events are immediate, highly efficient, and fully decoupled. The producer of an event does not know who consumes it, and the consumer does not care how the event was originally generated.

### 1.2 The CloudEvents Specification

To ensure interoperability, the industry needed a standardized way to describe events. The CloudEvents specification is the CNCF standard envelope for event data, and Argo Events uses it internally to normalize all incoming stimuli.

```json
{
  "specversion": "1.0",
  "type": "com.github.push",
  "source": "https://github.com/myorg/myrepo",
  "id": "A234-1234-1234",
  "time": "2025-11-05T17:31:00Z",
  "datacontenttype": "application/json",
  "data": {
    "ref": "refs/heads/main",
    "commits": [{"message": "fix: update config"}]
  }
}
```

Every standardized event contains key routing fields: `specversion`, `type`, `source`, and `id`. The `data` field carries the actual payload specific to the event type.

---

## Part 2: Argo Events Architecture

### 2.1 The Four Components

Argo Events is an event-driven workflow automation framework for Kubernetes. It operates using four main logical concepts mapped to Custom Resource Definitions (CRDs).

**Legacy ASCII Architectural Representation:**
```text
┌──────────────────────────────────────────────────────────────────────┐
│                        ARGO EVENTS ARCHITECTURE                      │
│                                                                      │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────────┐  │
│  │  EventSource   │    │   EventBus     │    │     Sensor         │  │
│  │                │    │  (NATS         │    │                    │  │
│  │  - Webhook     │───▶│   JetStream)   │───▶│  - Dependencies   │  │
│  │  - GitHub      │    │                │    │  - Filters         │  │
│  │  - S3          │    │  Namespace-    │    │  - Trigger         │  │
│  │  - Cron        │    │  scoped msg    │    │    templates       │  │
│  │  - Kafka       │    │  broker        │    │                    │  │
│  │  - SNS/SQS     │    │                │    │                    │  │
│  └────────────────┘    └────────────────┘    └───────┬────────────┘  │
│                                                      │               │
│                                                      ▼               │
│                                            ┌────────────────────┐    │
│                                            │    Triggers        │    │
│                                            │                    │    │
│                                            │  - Argo Workflow   │    │
│                                            │  - K8s Resource    │    │
│                                            │  - HTTP Request    │    │
│                                            │  - Notification    │    │
│                                            └────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

**Modern Architectural Representation:**
```mermaid
flowchart TD
    subgraph Sources [EventSources]
        W[Webhook]
        G[GitHub]
        S[S3]
        C[Cron]
        K[Kafka]
        SQ[SNS/SQS]
    end

    subgraph Bus [EventBus]
        EB[NATS JetStream <br/> Namespace-scoped msg broker]
    end

    subgraph Sens [Sensor]
        D[Dependencies]
        F[Filters]
        TT[Trigger templates]
    end

    subgraph Actions [Triggers]
        AW[Argo Workflow]
        KR[K8s Resource]
        HR[HTTP Request]
        N[Notification]
    end

    Sources -->|CloudEvents| EB
    EB --> Sens
    Sens --> Actions
```

The data flow is always unidirectional from left to right:
1. **EventSource** — Connects to external systems, ingests the proprietary data, and normalizes it.
2. **EventBus** — The internal transport layer that reliably routes messages to interested consumers.
3. **Sensor** — The brain of the operation. It listens for events, applies filtering, and evaluates dependency logic.
4. **Trigger** — The action taken when a Sensor's conditions are perfectly met.

### 2.2 How the Pieces Connect

**Legacy ASCII Data Flow:**
```text
GitHub push ──▶ EventSource "github" ──▶ EventBus "default"
                                              │
S3 upload ────▶ EventSource "s3" ─────▶ EventBus "default"
                                              │
                                              ▼
                                     Sensor "build-on-push"
                                     (depends on: github push)
                                              │
                                              ▼
                                     Trigger: submit Argo Workflow
```

**Modern Flow Representation:**
```mermaid
flowchart LR
    GH[GitHub push] --> ES1[EventSource <br/> github]
    S3[S3 upload] --> ES2[EventSource <br/> s3]
    ES1 --> EB[EventBus <br/> default]
    ES2 --> EB
    EB --> S[Sensor <br/> build-on-push]
    S --> AW[Trigger: submit <br/> Argo Workflow]
```

Each component is a completely separate Kubernetes Custom Resource. This separation of concerns allows platform engineers to manage event ingress independently from the logic executing the downstream workflows.

---

## Part 3: Deep Dive into EventSource

An EventSource definition converts external inputs into CloudEvents and dispatches them through EventBus. The EventSource catalog currently includes AMQP, AWS SNS, AWS SQS, Azure Events Hub, Azure Queue Storage, Calendar, File, GCP PubSub, GitHub, GitLab, Kafka, NATS, Slack, Stripe, Webhooks, and other named connectors.

### 3.1 Webhook EventSource

The most universal entry point is a simple HTTP webhook. It exposes an endpoint that listens for incoming POST requests.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: EventSource
metadata:
  name: webhook-events
spec:
  webhook:
    build-trigger:
      port: "12000"
      endpoint: /build
      method: POST
    deploy-trigger:
      port: "12000"
      endpoint: /deploy
      method: POST
```

This manifests as a pod actively listening on port 12000. It supports multiple endpoints simultaneously.

### 3.2 GitHub EventSource

For CI/CD scenarios, the GitHub EventSource is heavily utilized. It manages webhook validation directly.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: EventSource
metadata:
  name: github-events
spec:
  github:
    code-push:
      repositories:
        - owner: myorg
          names:
            - myrepo
      webhook:
        endpoint: /push
        port: "13000"
        method: POST
        url: https://events.example.com
      events:
        - push
        - pull_request
      apiToken:
        name: github-access       # K8s Secret name
        key: token                 # Key within the Secret
      webhookSecret:
        name: github-access
        key: webhook-secret
```

### 3.3 S3 EventSource

Monitoring object storage allows data engineering teams to trigger automated ETL pipelines the moment a file lands in a bucket.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: EventSource
metadata:
  name: s3-events
spec:
  s3:
    data-upload:
      bucket:
        name: data-pipeline-input
      events:
        - s3:ObjectCreated:*
      filter:
        prefix: "uploads/"
        suffix: ".csv"
      endpoint: s3.amazonaws.com
      region: us-east-1
      accessKey:
        name: s3-credentials
        key: accesskey
      secretKey:
        name: s3-credentials
        key: secretkey
```

### 3.4 Calendar (Cron) EventSource

Time itself is an event. This replaces traditional Kubernetes CronJobs and brings scheduled tasks into the centralized event framework.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: EventSource
metadata:
  name: calendar-events
spec:
  calendar:
    nightly-cleanup:
      schedule: "0 0 * * *"       # Midnight daily
      timezone: "America/New_York"
    hourly-check:
      schedule: "0 * * * *"       # Every hour
      timezone: "UTC"
```

### 3.5 Other EventSource Types

| Type | Use Case |
|------|----------|
| **Kafka** | Consume messages from Kafka topics |
| **AWS SNS** | Subscribe to SNS topics |
| **AWS SQS** | Poll SQS queues |
| **GCP PubSub** | Subscribe to Pub/Sub topics |
| **NATS** | Consume from NATS subjects |
| **Redis Streams** | Consume from Redis streams |
| **Slack** | Slash commands and interactive messages |
| **Generic** | Any custom event source via a sidecar container |

> **Stop and think**: If an external system uses a proprietary TCP protocol that isn't listed in the catalog, how would you integrate it? You would build a small microservice to receive the proprietary protocol and then forward it to an Argo Events Generic or Webhook EventSource.

---

## Part 4: The EventBus and Message Brokers

The EventBus acts as the central nervous system. The default EventBus is a namespaced Kubernetes custom resource requiring one per namespace for EventSources and Sensors. This means isolation is built-in; events do not cross namespace boundaries natively, which significantly improves security and reduces noisy-neighbor problems.

### 4.1 Creating the Default EventBus

If you do not specify an explicit `eventBusName` in your configurations, the system attempts to connect to an EventBus named `default`.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: EventBus
metadata:
  name: default
spec:
  jetstream:
    version: "2.9.22"
    replicas: 3
    persistence:
      storageClassName: standard
      volumeSize: 10Gi
```

### 4.2 EventBus Backends

Argo Events supports three EventBus implementations (NATS/JetStream/Kafka), with STAN noted as deprecated. NATS-backed EventBus is documented as supported via NATS Streaming and JetStream.

| Backend | Status | Notes |
|---------|--------|-------|
| **JetStream** (NATS) | Recommended | At-least-once delivery, persistence, built-in |
| **Kafka** | Supported | Use when you already run Kafka and want a single broker |
| **STAN** | Deprecated | Legacy NATS Streaming; migrate to JetStream |

JetStream is the modern standard because it embeds persistence directly without the overhead of ZooKeeper or KRaft needed by traditional Kafka deployments. It guarantees that if a Sensor pod crashes, the event is retained and will be re-delivered once the Sensor recovers.

---

## Part 5: Sensors, Dependencies, and AND/OR Logic

Sensors define event dependencies, subscribe to EventBus, and execute triggers when dependencies resolve. They hold the "business logic" of your event pipeline.

### 5.1 Basic Sensor Structure

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Sensor
metadata:
  name: build-sensor
spec:
  dependencies:
    - name: github-push
      eventSourceName: github-events
      eventName: code-push
  triggers:
    - template:
        name: trigger-build
        argoWorkflow:
          operation: submit
          source:
            resource:
              apiVersion: argoproj.io/v1alpha1
              kind: Workflow
              metadata:
                generateName: build-
              spec:
                entrypoint: build
                templates:
                  - name: build
                    container:
                      image: golang:1.22
                      command: [make, build]
```

### 5.2 Event Dependencies — AND/OR Logic

When integrating multiple sources, a Sensor can apply advanced boolean logic.

```yaml
spec:
  dependencies:
    - name: github-push
      eventSourceName: github-events
      eventName: code-push
    - name: security-scan
      eventSourceName: webhook-events
      eventName: scan-complete
  # AND logic (default): trigger fires when BOTH events arrive
```

You can define explicit OR logic by separating conditions at the trigger level:

```yaml
spec:
  dependencies:
    - name: github-push
      eventSourceName: github-events
      eventName: code-push
    - name: manual-trigger
      eventSourceName: webhook-events
      eventName: build-trigger
  triggers:
    - template:
        name: build-on-push
        conditions: "github-push"     # fires on github-push alone
        argoWorkflow:
          # ...workflow spec...
    - template:
        name: build-on-manual
        conditions: "manual-trigger"  # fires on manual-trigger alone
        argoWorkflow:
          # ...workflow spec...
```

---

## Part 6: Filters - Controlling the Flow

Filters prevent unwanted events from initiating triggers. They perform pre-execution validation based on the payload.

### 6.1 Data Filters

Evaluate the internal JSON payload of the event:

```yaml
dependencies:
  - name: github-push
    eventSourceName: github-events
    eventName: code-push
    filters:
      data:
        - path: body.ref
          type: string
          value:
            - "refs/heads/main"
```

### 6.2 Expression Filters

Apply boolean logic directly to payload fields:

```yaml
filters:
  exprs:
    - expr: body.action == "opened" || body.action == "synchronize"
      fields:
        - name: body.action
          path: body.action
```

### 6.3 Context Filters

Filter on the CloudEvents envelope metadata rather than the raw data payload:

```yaml
filters:
  context:
    type: com.github.push
    source: myorg/myrepo
```

> **Pause and predict**: If an event matches the data filter but fails the context filter, what happens? The dependency is marked as unmet, and the trigger will not fire. All filters must pass simultaneously (AND logic).

---

## Part 7: Triggers - Acting on Events

Trigger resources executed by a Sensor include Argo Workflows, Kubernetes object creation, HTTP/serverless, NATS/Kafka messages, Slack, Azure Event Hubs, Custom triggers, and OpenWhisk.

### 7.1 Argo Workflow Trigger

```yaml
triggers:
  - template:
      name: run-build
      argoWorkflow:
        operation: submit        # submit, resubmit, resume, retry, stop, terminate
        source:
          resource:
            apiVersion: argoproj.io/v1alpha1
            kind: Workflow
            metadata:
              generateName: build-
            spec:
              entrypoint: main
              arguments:
                parameters:
                  - name: git-sha
              templates:
                - name: main
                  container:
                    image: builder:latest
                    command: [./build.sh]
        parameters:
          - src:
              dependencyName: github-push
              dataKey: body.after      # Git SHA from the push event
            dest: spec.arguments.parameters.0.value
```

### 7.2 Kubernetes Resource Trigger

```yaml
triggers:
  - template:
      name: create-namespace
      k8s:
        operation: create
        source:
          resource:
            apiVersion: v1
            kind: Namespace
            metadata:
              generateName: pr-env-
        parameters:
          - src:
              dependencyName: github-pr
              dataKey: body.number
            dest: metadata.labels.pr-number
```

### 7.3 HTTP Trigger

```yaml
triggers:
  - template:
      name: notify-slack
      http:
        url: https://hooks.slack.com/services/T00/B00/XXXX
        method: POST
        headers:
          Content-Type: application/json
        payload:
          - src:
              dependencyName: github-push
              dataKey: body.head_commit.message
            dest: text
```

| Trigger Type | Use Case |
|-------------|----------|
| `argoWorkflow` | Start CI/CD pipelines, data processing, ML training |
| `k8s` | Create/patch any K8s resource (ConfigMap, Job, Namespace) |
| `http` | Call external APIs, send notifications |
| `log` | Debug — print event to sensor logs |

---

## Part 8: Authentication, Secrets, and Security

Platform security mandates that sensitive credentials are never stored directly inside EventSource definitions. Always utilize native Kubernetes Secrets.

### 8.1 Webhook Secrets

```yaml
# Create the secret
kubectl create secret generic github-access \
  --from-literal=token=ghp_xxxxxxxxxxxxx \
  --from-literal=webhook-secret=mysecretvalue

# Reference in EventSource
spec:
  github:
    code-push:
      apiToken:
        name: github-access
        key: token
      webhookSecret:
        name: github-access
        key: webhook-secret
```

### 8.2 S3 / Cloud Provider Credentials

```yaml
kubectl create secret generic s3-credentials \
  --from-literal=accesskey=AKIAIOSFODNN7EXAMPLE \
  --from-literal=secretkey=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

### 8.3 Kafka Authentication

```yaml
spec:
  kafka:
    events:
      url: kafka-broker:9093
      topic: events
      tls:
        caCertSecret:
          name: kafka-tls
          key: ca.crt
      sasl:
        mechanism: PLAIN
        userSecret:
          name: kafka-sasl
          key: user
        passwordSecret:
          name: kafka-sasl
          key: password
```

---

## Part 9: Integration with Argo Workflows

The most powerful feature of Argo Events is dynamic parameter injection. Data from the triggering event is injected deeply into the Workflow parameters.

**Legacy ASCII Parameter Injection Flow:**
```text
└─▶ Sensor extracts body.after (commit SHA)
       └─▶ Injects into Workflow spec.arguments.parameters.0.value
            └─▶ Workflow template uses {{workflow.parameters.git-sha}}
```

**Modern Parameter Injection Flow:**
```mermaid
flowchart TD
    E[GitHub push event] -->|Sensor extracts body.after| P[Injects into Workflow spec.arguments.parameters.0.value]
    P -->|Workflow template uses| W[{{workflow.parameters.git-sha}}]
```

### 9.1 Parameter Mapping Syntax

```yaml
parameters:
  - src:
      dependencyName: github-push
      dataKey: body.after           # JSON path in event payload
    dest: spec.arguments.parameters.0.value  # JSON path in Workflow resource
```

### 9.2 Passing Event Data to Multiple Parameters

```yaml
parameters:
  - src:
      dependencyName: github-push
      dataKey: body.after
    dest: spec.arguments.parameters.0.value
  - src:
      dependencyName: github-push
      dataKey: body.repository.full_name
    dest: spec.arguments.parameters.1.value
  - src:
      dependencyName: github-push
      dataKey: body.ref
    dest: spec.arguments.parameters.2.value
```

### 9.3 Using a WorkflowTemplate Reference

```yaml
triggers:
  - template:
      name: trigger-build
      argoWorkflow:
        operation: submit
        source:
          resource:
            apiVersion: argoproj.io/v1alpha1
            kind: Workflow
            metadata:
              generateName: build-
            spec:
              workflowTemplateRef:
                name: build-pipeline
              arguments:
                parameters:
                  - name: git-sha
                    value: placeholder    # will be overwritten by parameter mapping
        parameters:
          - src:
              dependencyName: github-push
              dataKey: body.after
            dest: spec.arguments.parameters.0.value
```

---

## Part 10: Installation, Versioning, and Helm

Understanding the lifecycle and installation model is critical for production deployment.

Argo Events installation docs require Kubernetes version 1.11 or higher and kubectl version 1.11.0 or higher. The documented installation flow is to create `argo-events` namespace, apply install manifests, and then create the EventBus via the native example manifest. 

For version 1.7 and newer, namespace-scoped installs must use `--namespaced`, with optional `--managed-namespace`; pre-1.7 setups used three controller deployments with per-controller `--namespaced` flags. This architectural shift greatly simplified managing scoped environments.

**Versioning Policy:**
Release policy is semver x.y.z with only the two most recent minor branches maintained. Release policy requires matching image versions across eventsource, sensor, eventbus-controller, eventsource-controller, sensor-controller, and events-webhook to prevent serialization mismatches over the message bus.

When deploying via Helm, Argo Helm chart documentation states that only the latest upstream versions are officially supported; older versions are not guaranteed for bug/security patching. The Argo Helm chart metadata in argo-helm main currently sets `version: 2.4.21` and `appVersion: 1.9.10` for argo-events.

---

## Part 11: Practical Patterns

### Pattern 1: GitHub Push Triggers a Build

**Legacy ASCII Diagram:**
```text
┌──────────┐     ┌──────────────┐     ┌─────────┐     ┌──────────────┐
│  GitHub   │────▶│ EventSource  │────▶│ EventBus│────▶│    Sensor    │
│  webhook  │     │ (github)     │     │(default)│     │ (build-on-   │
└──────────┘     └──────────────┘     └─────────┘     │   push)      │
                                                       └──────┬───────┘
                                                              │
```
```text
┌──────────────┐
                                                       │ Argo Workflow│
                                                       │ (build +     │
                                                       │  test + push)│
                                                       └──────────────┘
```

**Modern Flow Diagram:**
```mermaid
flowchart LR
    GH[GitHub webhook] -->|POST| ES[EventSource github]
    ES -->|CloudEvents| EB[EventBus default]
    EB -->|Consume| S[Sensor build-on-push]
    S -->|Submit| AW[Argo Workflow build + test + push]
```

### Pattern 2: S3 Upload Triggers a Data Processing Pipeline

```yaml
# EventSource
spec:
  s3:
    csv-upload:
      bucket:
        name: data-pipeline
      events:
        - s3:ObjectCreated:*
      filter:
        prefix: "uploads/"
        suffix: ".csv"

# Sensor trigger passes the object key to the Workflow
parameters:
  - src:
      dependencyName: csv-upload
      dataKey: notification.0.s3.object.key
    dest: spec.arguments.parameters.0.value
```

### Pattern 3: Cron Schedule Triggers a Cleanup Workflow

```yaml
# EventSource
spec:
  calendar:
    nightly:
      schedule: "0 2 * * *"       # 2 AM daily
      timezone: "UTC"

# Sensor — no data mapping needed, just submit the Workflow
triggers:
  - template:
      name: nightly-cleanup
      argoWorkflow:
        operation: submit
        source:
          resource:
            apiVersion: argoproj.io/v1alpha1
            kind: Workflow
            metadata:
              generateName: cleanup-
            spec:
              workflowTemplateRef:
                name: cleanup-old-resources
```

---

## Common Mistakes

| Mistake | Why It Happens | Solution |
|---------|---------------|----------|
| No EventBus created | People deploy EventSource + Sensor and forget the bus | Always create an EventBus named `default` in the namespace first |
| Wrong `dataKey` path | Event payload structure is not what you expected | Use a `log` trigger first to print the raw event, then build your path |
| Sensor dependency name mismatch | Typo between `dependencies[].name` and `triggers[].parameters[].src.dependencyName` | Copy-paste the dependency name; do not retype it |
| Secrets in wrong namespace | Secret exists in `default` but EventSource is in `argo-events` | Secrets must be in the same namespace as the EventSource that references them |
| Webhook not reachable | EventSource pod has no Ingress or Service exposing it | Create a Service and Ingress/Route for the EventSource pod's port |
| STAN backend used in new install | Old tutorials still reference STAN | Always use JetStream — STAN is deprecated |
| Filters too broad | Sensor fires on every push, not just `main` | Add a data filter on `body.ref` to match `refs/heads/main` |

---

## Quiz

Test your understanding before the hands-on exercise. Ensure you have synthesized the architectural concepts fully.

**Scenario 1:** You are designing a CI pipeline that processes data from external systems. To do this, you need to string together the primary Custom Resources. What are the four Argo Events CRDs in order of data flow?
<details>
<summary>Answer</summary>

EventSource, EventBus, Sensor, Trigger (the trigger is defined within the Sensor CR, not a separate CRD — but the conceptual flow is EventSource → EventBus → Sensor → Trigger action).

</details>

**Scenario 2:** You must choose a highly available, fault-tolerant message broker for your EventBus. You want native Kubernetes integration without external ZooKeeper nodes. What is the recommended EventBus backend, and what technology does it use?
<details>
<summary>Answer</summary>

JetStream, which is built on NATS. It provides at-least-once delivery with persistence. STAN (NATS Streaming) is deprecated.

</details>

**Scenario 3:** Your compliance team states that a deployment can only begin if a GitHub push event occurs AND a security vulnerability scan passes from a separate webhook source. How do you make a Sensor trigger only when events from two different EventSources BOTH arrive?
<details>
<summary>Answer</summary>

List both as dependencies in the Sensor spec. By default, all dependencies use AND logic — the trigger fires only when all dependencies are satisfied. You can also be explicit with the `conditions` field: `"dep-one && dep-two"`.

</details>

**Scenario 4:** Your team deployed a GitHub EventSource. The manifest applies correctly, but events never reach the Sensor. The EventBus pods are running healthily. What is the most likely network or configuration issue?
<details>
<summary>Answer</summary>

The EventSource pod's webhook port is not exposed to the internet. GitHub cannot deliver webhooks to a pod that has no Service, Ingress, or external URL. Check that the `webhook.url` in the EventSource spec is reachable from GitHub and that a Service/Ingress routes traffic to the correct port.

</details>

**Scenario 5:** A build workflow requires knowing exactly which Git commit to clone. How do you pass the Git commit SHA from a GitHub push event directly into an Argo Workflow parameter before it executes?
<details>
<summary>Answer</summary>

In the Sensor trigger's `parameters` section, set `src.dependencyName` to the dependency name, `src.dataKey` to `body.after` (the field in the GitHub push payload that contains the new SHA), and `dest` to the JSON path in the Workflow resource, e.g., `spec.arguments.parameters.0.value`.

</details>

**Scenario 6:** A large organization has a centralized `argo-events` namespace handling global webhooks, but developers want to run Sensors in their own application namespaces (`team-alpha`, `team-beta`). What is the scope of an EventBus, and can events published in namespace A be consumed natively by a Sensor in namespace B?
<details>
<summary>Answer</summary>

The EventBus is namespace-scoped. Events published to the EventBus in namespace A are only available to Sensors in namespace A. Cross-namespace event delivery is not supported by default. If you need cross-namespace communication, use an external broker (Kafka) or HTTP triggers between namespaces.

</details>

**Scenario 7:** A webhook is noisy, firing on every single branch modification. You want a Sensor to fire on GitHub push events, but ONLY for pushes to the `main` branch. Which filter type do you use and what does it look like?
<details>
<summary>Answer</summary>

Use a data filter on the dependency:

```yaml
filters:
  data:
    - path: body.ref
      type: string
      value:
        - "refs/heads/main"
```

This inspects the event payload and only allows events where `body.ref` equals `refs/heads/main`.

</details>

---

## Hands-On Exercise: Event-Driven Build Pipeline

### Goal
Deploy a complete Argo Events pipeline: a webhook EventSource receives a POST, publishes to the EventBus, a Sensor picks it up, and triggers an Argo Workflow that prints the event data.

### Prerequisites
- A running Kubernetes cluster.
- Argo Events installed via official manifests.
- Argo Workflows installed.

### Success Checklist
- [ ] EventBus is fully healthy and accepting connections.
- [ ] EventSource pod is actively listening for webhooks.
- [ ] Sensor is actively monitoring dependencies.
- [ ] Webhook triggers the correct Argo Workflow without errors.

### Task 1: Establish the EventBus Infrastructure
Create a namespace-scoped EventBus named `default` utilizing JetStream.
<details>
<summary>Solution</summary>

```bash
cat <<'EOF' | k apply -n argo-events -f -
apiVersion: argoproj.io/v1alpha1
kind: EventBus
metadata:
  name: default
spec:
  jetstream:
    version: "2.9.22"
    replicas: 3
EOF
```

Verify it is running:
```bash
k get pods -n argo-events -l eventbus-name=default --watch
```
</details>

### Task 2: Configure the Webhook EventSource
Deploy a Webhook EventSource that listens on port `12000` at the `/build` endpoint.
<details>
<summary>Solution</summary>

```bash
cat <<'EOF' | k apply -n argo-events -f -
apiVersion: argoproj.io/v1alpha1
kind: EventSource
metadata:
  name: webhook
spec:
  webhook:
    build:
      port: "12000"
      endpoint: /build
      method: POST
EOF
```

Check the pod status:
```bash
k get pods -n argo-events -l eventsource-name=webhook
```
</details>

### Task 3: Deploy the Dependent Sensor
Create a Sensor that listens to the `webhook-build` dependency and triggers a Workflow.
<details>
<summary>Solution</summary>

```bash
cat <<'EOF' | k apply -n argo-events -f -
apiVersion: argoproj.io/v1alpha1
kind: Sensor
metadata:
  name: build-sensor
spec:
  dependencies:
    - name: webhook-build
      eventSourceName: webhook
      eventName: build
  triggers:
    - template:
        name: trigger-workflow
        argoWorkflow:
          operation: submit
          source:
            resource:
              apiVersion: argoproj.io/v1alpha1
              kind: Workflow
              metadata:
                generateName: event-build-
              spec:
                entrypoint: print-event
                arguments:
                  parameters:
                    - name: message
                templates:
                  - name: print-event
                    inputs:
                      parameters:
                        - name: message
                    container:
                      image: alpine:3.19
                      command: [sh, -c]
                      args:
                        - echo "Received event data:" && echo "{{inputs.parameters.message}}"
          parameters:
            - src:
                dependencyName: webhook-build
                dataKey: body.project
              dest: spec.arguments.parameters.0.value
EOF
```
</details>

### Task 4: Execute the Event Trigger
Simulate a webhook payload manually to initiate the workflow.
<details>
<summary>Solution</summary>

```bash
k port-forward -n argo-events svc/webhook-eventsource-svc 12000:12000 &

curl -X POST http://localhost:12000/build \
  -H "Content-Type: application/json" \
  -d '{"project": "kubedojo", "branch": "main", "commit": "abc123"}'
```
</details>

### Task 5: Validate the Argo Workflow Output
Verify that the event successfully traversed the pipeline and executed the Workflow action.
<details>
<summary>Solution</summary>

```bash
k get workflows -n argo-events
k logs -n argo-events -l workflows.argoproj.io/workflow  # check the output
```
</details>

### Task 6: Clean Up the Environment
Remove the created resources to prevent lingering state.
<details>
<summary>Solution</summary>

```bash
k delete sensor build-sensor -n argo-events
k delete eventsource webhook -n argo-events
k delete eventbus default -n argo-events
```
</details>

---

## Summary

| Concept | Key Takeaway |
|---------|-------------|
| EDA vs Polling | Events are immediate and efficient; polling wastes resources and hits rate limits |
| EventSource | Entry point — connects external systems to the EventBus |
| EventBus | Internal broker (JetStream recommended), namespace-scoped |
| Sensor | Decision-maker — dependencies, filters, AND/OR logic |
| Triggers | Actions — submit Workflows, create K8s resources, call HTTP endpoints |
| Filters | Data, expression, and context filters narrow which events fire triggers |
| Secrets | Always use K8s Secrets; never inline credentials |
| Parameter mapping | `src.dataKey` extracts from event, `dest` injects into trigger resource |

---

## Next Module

[Module 3: Argo CD — GitOps Delivery](/platform/toolkits/cicd-delivery/gitops-deployments/module-2.1-argocd/) — Expand your knowledge by mastering declarative, Git-driven continuous delivery strategies that bring your deployed workloads fully into sync with your source control repositories.