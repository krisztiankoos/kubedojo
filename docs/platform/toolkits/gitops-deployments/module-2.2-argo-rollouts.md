# Module 2.2: Argo Rollouts

> **Toolkit Track** | Complexity: `[COMPLEX]` | Time: 45-50 min

## Prerequisites

Before starting this module:
- [Module 2.1: ArgoCD](module-2.1-argocd.md) — GitOps fundamentals
- [GitOps Discipline](../../disciplines/gitops/) — Deployment concepts
- Understanding of Kubernetes Deployments and Services
- Basic networking concepts (traffic splitting)

## Why This Module Matters

Kubernetes Deployments use rolling updates by default—gradually replacing old pods with new ones. But rolling updates can't answer: "Is this new version actually better?" They blindly proceed until all pods are replaced.

Argo Rollouts enables progressive delivery: canary deployments, blue-green switches, and automated rollbacks based on metrics. You can deploy to 10% of traffic, verify metrics look good, then automatically promote to 100%—or roll back if they don't.

## Did You Know?

- **Argo Rollouts was born from Intuit's frustration with Kubernetes Deployments**—they needed a way to safely deploy thousands of times per day
- **The canary deployment pattern is named after canaries in coal mines**—miners brought canaries underground; if the canary died, the air was toxic
- **Netflix pioneered automated canary analysis**—their Kayenta system inspired Argo Rollouts' analysis features
- **Blue-green deployments can double your resource usage**—you need capacity for both versions simultaneously

## Rollout Strategies

### Rolling Update vs. Progressive Delivery

```
ROLLING UPDATE (Native Kubernetes)
─────────────────────────────────────────────────────────────────

Time ──────────────────────────────────────────────────────────▶

Pods:  [v1][v1][v1][v1][v1]
       [v1][v1][v1][v1][v2] → 1 pod replaced
       [v1][v1][v1][v2][v2] → 2 pods replaced
       [v1][v1][v2][v2][v2] → 3 pods replaced
       [v1][v2][v2][v2][v2] → 4 pods replaced
       [v2][v2][v2][v2][v2] → Done!

Traffic: No control - pods receive traffic as soon as ready
Rollback: Must wait for new rolling update
Analysis: None - hope for the best

─────────────────────────────────────────────────────────────────

CANARY (Argo Rollouts)
─────────────────────────────────────────────────────────────────

Time ──────────────────────────────────────────────────────────▶

Pods:  [v1][v1][v1][v1][v1]
       [v1][v1][v1][v1][v1] + [v2]  → Canary pod added

Traffic: v1 (90%) ─────────────────────────────────────────────▶
         v2 (10%) ─────────────────────────────────────────────▶

Analysis: Is error rate OK? Is latency OK?
          ├── Yes: Increase to 50%, then 100%
          └── No: Rollback immediately, alert on-call

Result: Bad versions never reach more than 10% of users
```

### Blue-Green Strategy

```
BLUE-GREEN DEPLOYMENT
─────────────────────────────────────────────────────────────────

BEFORE:
┌──────────────────────────────────────────────────────────────┐
│                                                               │
│  BLUE (Active)              GREEN (Inactive)                  │
│  ┌─────────────────┐       ┌─────────────────┐               │
│  │     v1 pods     │       │    (empty)      │               │
│  │  [v1][v1][v1]   │       │                 │               │
│  └────────┬────────┘       └─────────────────┘               │
│           │                                                   │
│           ▼                                                   │
│      ┌─────────┐                                             │
│      │ Service │ ──────▶ 100% traffic                        │
│      └─────────┘                                             │
│                                                               │
└──────────────────────────────────────────────────────────────┘

AFTER DEPLOYMENT:
┌──────────────────────────────────────────────────────────────┐
│                                                               │
│  BLUE (Inactive)            GREEN (Active)                    │
│  ┌─────────────────┐       ┌─────────────────┐               │
│  │     v1 pods     │       │     v2 pods     │               │
│  │  [v1][v1][v1]   │       │  [v2][v2][v2]   │               │
│  └─────────────────┘       └────────┬────────┘               │
│                                     │                         │
│                                     ▼                         │
│                               ┌─────────┐                     │
│                               │ Service │ ──────▶ 100%       │
│                               └─────────┘                     │
│                                                               │
│  (kept for instant rollback)                                 │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Installing Argo Rollouts

```bash
# Install controller
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# Install kubectl plugin
brew install argoproj/tap/kubectl-argo-rollouts  # macOS
# or
curl -LO https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-linux-amd64
chmod +x kubectl-argo-rollouts-linux-amd64
sudo mv kubectl-argo-rollouts-linux-amd64 /usr/local/bin/kubectl-argo-rollouts

# Verify
kubectl argo rollouts version
```

## Canary Rollouts

### Basic Canary

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 5
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: app
          image: myapp:v2
          ports:
            - containerPort: 8080

  strategy:
    canary:
      # Traffic split steps
      steps:
        - setWeight: 10
        - pause: {duration: 5m}   # Wait 5 minutes
        - setWeight: 30
        - pause: {duration: 5m}
        - setWeight: 60
        - pause: {duration: 5m}
        # 100% happens automatically after last step

      # Traffic routing (for service mesh / ingress)
      canaryService: my-app-canary
      stableService: my-app-stable

      # Analysis at each step
      analysis:
        templates:
          - templateName: success-rate
        startingStep: 1
        args:
          - name: service-name
            value: my-app-canary
```

### Canary with Traffic Management

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 5
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: app
          image: myapp:v2

  strategy:
    canary:
      canaryService: my-app-canary
      stableService: my-app-stable

      trafficRouting:
        # NGINX Ingress
        nginx:
          stableIngress: my-app-ingress
          annotationPrefix: nginx.ingress.kubernetes.io

        # OR Istio
        # istio:
        #   virtualService:
        #     name: my-app-vs

        # OR AWS ALB
        # alb:
        #   ingress: my-app-ingress
        #   servicePort: 80

      steps:
        - setWeight: 10
        - pause: {duration: 2m}
        - setWeight: 30
        - pause: {duration: 2m}
        - setWeight: 60
        - pause: {duration: 2m}
---
# Services for traffic splitting
apiVersion: v1
kind: Service
metadata:
  name: my-app-stable
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: my-app-canary
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
```

### Canary with Manual Approval

```yaml
strategy:
  canary:
    steps:
      - setWeight: 10
      - pause: {}          # Infinite pause - requires manual promotion
      - setWeight: 50
      - pause: {duration: 5m}
      - setWeight: 100
```

```bash
# Check rollout status
kubectl argo rollouts get rollout my-app

# Promote past the pause
kubectl argo rollouts promote my-app

# Or abort and rollback
kubectl argo rollouts abort my-app
```

## Blue-Green Rollouts

### Basic Blue-Green

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: app
          image: myapp:v2

  strategy:
    blueGreen:
      activeService: my-app-active
      previewService: my-app-preview

      # Wait for analysis before promotion
      prePromotionAnalysis:
        templates:
          - templateName: smoke-tests
        args:
          - name: service-name
            value: my-app-preview

      # Require manual approval
      autoPromotionEnabled: false

      # Keep old ReplicaSet for quick rollback
      scaleDownDelaySeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: my-app-active
spec:
  selector:
    app: my-app
  ports:
    - port: 80
---
apiVersion: v1
kind: Service
metadata:
  name: my-app-preview
spec:
  selector:
    app: my-app
  ports:
    - port: 80
```

### Blue-Green with Automatic Promotion

```yaml
strategy:
  blueGreen:
    activeService: my-app-active
    previewService: my-app-preview

    # Auto-promote after preview is ready
    autoPromotionEnabled: true
    autoPromotionSeconds: 60  # Wait 60s after ready

    # Analysis before switching
    prePromotionAnalysis:
      templates:
        - templateName: smoke-tests

    # Analysis after switching
    postPromotionAnalysis:
      templates:
        - templateName: success-rate
      args:
        - name: duration
          value: "5m"
```

## Analysis Templates

### Prometheus Metrics Analysis

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
    - name: service-name
    - name: threshold
      value: "0.95"  # 95% success rate

  metrics:
    - name: success-rate
      interval: 1m
      count: 5  # Run 5 times
      successCondition: result[0] >= {{args.threshold}}
      failureLimit: 3

      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(
              http_requests_total{
                service="{{args.service-name}}",
                status=~"2.."
              }[1m]
            )) /
            sum(rate(
              http_requests_total{
                service="{{args.service-name}}"
              }[1m]
            ))
```

### Latency Analysis

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: latency-check
spec:
  args:
    - name: service-name
    - name: percentile
      value: "0.99"
    - name: threshold-ms
      value: "500"

  metrics:
    - name: p99-latency
      interval: 1m
      count: 5
      successCondition: result[0] < {{args.threshold-ms}}
      failureLimit: 2

      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            histogram_quantile(
              {{args.percentile}},
              sum(rate(
                http_request_duration_seconds_bucket{
                  service="{{args.service-name}}"
                }[2m]
              )) by (le)
            ) * 1000
```

### Web Hook Analysis (Custom Checks)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: custom-check
spec:
  args:
    - name: canary-hash

  metrics:
    - name: integration-tests
      successCondition: result.passed == true
      failureLimit: 1

      provider:
        web:
          url: https://ci.example.com/api/test
          method: POST
          headers:
            - key: Content-Type
              value: application/json
          body: |
            {
              "pod_hash": "{{args.canary-hash}}",
              "test_suite": "smoke"
            }
          jsonPath: "{$.result}"
```

### Kayenta Analysis (Automated Canary Analysis)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: kayenta-analysis
spec:
  args:
    - name: start-time
    - name: end-time

  metrics:
    - name: kayenta
      provider:
        kayenta:
          address: http://kayenta.monitoring:8090
          application: my-app
          canaryConfigName: my-canary-config
          metricsAccountName: prometheus-account
          storageAccountName: gcs-account
          threshold:
            pass: 95
            marginal: 75
          scopes:
            - name: default
              controlScope:
                scope: production
                start: "{{args.start-time}}"
                end: "{{args.end-time}}"
              experimentScope:
                scope: canary
                start: "{{args.start-time}}"
                end: "{{args.end-time}}"
```

## Analysis Runs

### Inline Analysis

```yaml
strategy:
  canary:
    steps:
      - setWeight: 20
      - pause: {duration: 2m}

      # Run analysis at this step
      - analysis:
          templates:
            - templateName: success-rate
          args:
            - name: service-name
              value: my-app-canary

      - setWeight: 50
      - pause: {duration: 2m}
      - setWeight: 100
```

### Background Analysis

```yaml
strategy:
  canary:
    analysis:
      # Start analysis after first step
      startingStep: 1

      templates:
        - templateName: success-rate
        - templateName: latency-check

      args:
        - name: service-name
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
```

### Analysis with Dry-Run

```yaml
strategy:
  canary:
    analysis:
      templates:
        - templateName: success-rate

      # Don't fail rollout, just report
      dryRun:
        - metricName: success-rate
```

## Experiments

### A/B Testing

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Experiment
metadata:
  name: homepage-experiment
spec:
  duration: 1h

  templates:
    - name: control
      replicas: 2
      selector:
        matchLabels:
          app: homepage
          variant: control
      template:
        metadata:
          labels:
            app: homepage
            variant: control
        spec:
          containers:
            - name: app
              image: homepage:v1

    - name: experiment
      replicas: 2
      selector:
        matchLabels:
          app: homepage
          variant: experiment
      template:
        metadata:
          labels:
            app: homepage
            variant: experiment
        spec:
          containers:
            - name: app
              image: homepage:v2-new-design

  analyses:
    - name: conversion-rate
      templateName: conversion-analysis
      args:
        - name: control-service
          value: homepage-control
        - name: experiment-service
          value: homepage-experiment
```

### Experiment as Part of Rollout

```yaml
strategy:
  canary:
    steps:
      - setWeight: 0

      # Run experiment before any traffic
      - experiment:
          duration: 30m
          templates:
            - name: experiment
              specRef: canary
              replicas: 2
          analyses:
            - name: smoke-test
              templateName: smoke-tests

      - setWeight: 20
      - pause: {duration: 5m}
      - setWeight: 100
```

## Observing Rollouts

### CLI Commands

```bash
# Watch rollout in real-time
kubectl argo rollouts get rollout my-app --watch

# See rollout history
kubectl argo rollouts history rollout my-app

# Get detailed status
kubectl argo rollouts status my-app

# List all rollouts
kubectl argo rollouts list rollouts

# Dashboard (web UI)
kubectl argo rollouts dashboard
```

### Rollout Status

```
NAME                                  KIND        STATUS     AGE
my-app                                Rollout     ✔ Healthy  5d
├──# revision:3
│  └──⧫ my-app-7f8b9c6d4-xxxxx       Pod         ✔ Running  1h
│  └──⧫ my-app-7f8b9c6d4-yyyyy       Pod         ✔ Running  1h
│  └──⧫ my-app-7f8b9c6d4-zzzzz       Pod         ✔ Running  1h
├──# revision:2
│  └──⧫ my-app-5f7b8c5d3-aaaaa       Pod         ◌ ScaledDown  2h
└──# revision:1
   └──⧫ my-app-4f6b7c4d2-bbbbb       Pod         ◌ ScaledDown  3d
```

### Notifications

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
  annotations:
    notifications.argoproj.io/subscribe.on-rollout-completed.slack: rollouts-channel
    notifications.argoproj.io/subscribe.on-rollout-step-completed.slack: rollouts-channel
    notifications.argoproj.io/subscribe.on-analysis-run-failed.slack: rollouts-alerts
spec:
  # ...
```

## Common Mistakes

| Mistake | Why It's Bad | Better Approach |
|---------|--------------|-----------------|
| No analysis templates | Blind deployment, no safety | Always add success-rate and latency analysis |
| Too aggressive steps | Problems hit many users | Start at 5-10%, pause longer at each step |
| Ignoring canary metrics | Analysis passes but users suffer | Include business metrics, not just infrastructure |
| No scaleDownDelay | Instant rollback impossible | Keep old version for 30-60 seconds minimum |
| Same replica count | Canary gets equal load despite traffic | Scale canary based on traffic weight |
| Manual promotion in prod | Human bottleneck, slow deployments | Use automated analysis for well-understood services |

## War Story: The 1-Minute Canary

A team set up Argo Rollouts with analysis but configured only 1-minute pause at each step. Their canary went from 10% to 100% in 5 minutes—faster than their metrics aggregation window.

The result? Analysis always passed because there wasn't enough data to detect problems. A bad deploy went to 100% before anyone noticed latency had tripled.

**The fix**:
- Analysis queries should cover `2-3x` the pause duration
- Pause at least as long as your SLO measurement window
- Use `count` in analysis to require multiple successful measurements

```yaml
steps:
  - setWeight: 10
  - pause: {duration: 10m}  # 10 minutes, not 1

metrics:
  - name: success-rate
    interval: 2m
    count: 5               # Run 5 times = 10 minutes of data
    successCondition: result[0] >= 0.99
```

**The lesson**: Canary analysis needs enough data points. Speed is not the goal—confidence is.

## Quiz

### Question 1
What's the key difference between canary and blue-green deployments?

<details>
<summary>Show Answer</summary>

**Canary**: Gradually shifts traffic from old to new (e.g., 10% → 30% → 60% → 100%). Both versions run simultaneously with controlled traffic split. Good for: detecting problems with minimal user impact.

**Blue-Green**: Maintains two complete environments. Traffic switches 100% at once (0% → 100%). Good for: instant rollback, testing full environment before switch.

Trade-offs:
- Canary uses fewer resources (one set of pods scaled up/down)
- Blue-Green requires double capacity but offers instant rollback
- Canary detects issues gradually; blue-green is all-or-nothing
</details>

### Question 2
Your analysis template uses `count: 3` and `interval: 1m`. How long will the analysis run before passing?

<details>
<summary>Show Answer</summary>

At least 3 minutes (3 runs × 1 minute apart).

The analysis runs every minute for 3 iterations:
- t=0: First measurement
- t=1m: Second measurement
- t=2m: Third measurement
- t=2m+: Analysis completes if all passed

If any measurement fails and `failureLimit` is reached, analysis fails immediately. If not, it retries until `count` successes are achieved or `failureLimit` is exceeded.
</details>

### Question 3
Write a PromQL query for analysis that checks if error rate is below 1% for a canary service.

<details>
<summary>Show Answer</summary>

```yaml
query: |
  sum(rate(
    http_requests_total{
      service="{{args.service-name}}",
      status=~"5.."
    }[2m]
  )) /
  sum(rate(
    http_requests_total{
      service="{{args.service-name}}"
    }[2m]
  )) < 0.01

# Or as successCondition:
successCondition: result[0] < 0.01
query: |
  sum(rate(http_requests_total{service="{{args.service-name}}",status=~"5.."}[2m])) /
  sum(rate(http_requests_total{service="{{args.service-name}}"}[2m]))
```

Key points:
- Use `rate()` for per-second rates
- Time range (2m) should be 2x the analysis interval
- Compare 5xx status codes to total requests
- Threshold of 0.01 = 1%
</details>

### Question 4
Your rollout is stuck in "Paused" state. What commands would you use to investigate and resolve?

<details>
<summary>Show Answer</summary>

```bash
# See detailed status and reason for pause
kubectl argo rollouts get rollout my-app

# Check analysis runs
kubectl argo rollouts get rollout my-app --watch

# If analysis failed, check why
kubectl get analysisruns -l rollout=my-app

# View analysis run details
kubectl describe analysisrun <name>

# Options to resolve:
# 1. If pause is intentional (manual gate):
kubectl argo rollouts promote my-app

# 2. If analysis failed, fix and retry:
kubectl argo rollouts retry rollout my-app

# 3. If you want to abort and rollback:
kubectl argo rollouts abort my-app

# 4. Force to stable version:
kubectl argo rollouts undo my-app
```
</details>

## Hands-On Exercise

### Scenario: Progressive Delivery Pipeline

Implement a canary deployment with automated analysis.

### Setup

```bash
# Create kind cluster
kind create cluster --name rollouts-lab

# Install Argo Rollouts
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# Install Prometheus for analysis
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.enabled=false

# Wait for components
kubectl -n argo-rollouts wait --for=condition=ready pod -l app.kubernetes.io/name=argo-rollouts --timeout=120s
```

### Deploy Demo Application

```yaml
# rollout.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: demo-rollout
spec:
  replicas: 5
  selector:
    matchLabels:
      app: demo
  template:
    metadata:
      labels:
        app: demo
    spec:
      containers:
        - name: demo
          image: argoproj/rollouts-demo:blue
          ports:
            - containerPort: 8080

  strategy:
    canary:
      canaryService: demo-canary
      stableService: demo-stable

      steps:
        - setWeight: 20
        - pause: {duration: 30s}
        - setWeight: 50
        - pause: {duration: 30s}
        - setWeight: 80
        - pause: {duration: 30s}
---
apiVersion: v1
kind: Service
metadata:
  name: demo-stable
spec:
  selector:
    app: demo
  ports:
    - port: 80
      targetPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: demo-canary
spec:
  selector:
    app: demo
  ports:
    - port: 80
      targetPort: 8080
```

```bash
kubectl apply -f rollout.yaml

# Watch the rollout
kubectl argo rollouts get rollout demo-rollout --watch
```

### Trigger a New Release

```bash
# Update to new image (yellow version)
kubectl argo rollouts set image demo-rollout demo=argoproj/rollouts-demo:yellow

# Watch the canary progress
kubectl argo rollouts get rollout demo-rollout --watch
```

### Add Analysis

```yaml
# analysis.yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: always-pass
spec:
  metrics:
    - name: always-pass
      count: 3
      interval: 10s
      successCondition: result == "true"
      provider:
        job:
          spec:
            template:
              spec:
                containers:
                  - name: check
                    image: busybox
                    command: [sh, -c, 'echo "true"']
                restartPolicy: Never
            backoffLimit: 0
```

```bash
kubectl apply -f analysis.yaml

# Update rollout to use analysis
kubectl patch rollout demo-rollout --type merge -p '
spec:
  strategy:
    canary:
      analysis:
        templates:
          - templateName: always-pass
'

# Trigger new rollout
kubectl argo rollouts set image demo-rollout demo=argoproj/rollouts-demo:green

# Watch analysis
kubectl argo rollouts get rollout demo-rollout --watch
```

### Test Rollback

```bash
# Abort during rollout
kubectl argo rollouts set image demo-rollout demo=argoproj/rollouts-demo:red

# While in progress, abort
kubectl argo rollouts abort demo-rollout

# Check that pods rolled back
kubectl argo rollouts get rollout demo-rollout
```

### Success Criteria

- [ ] Argo Rollouts controller is running
- [ ] Can perform canary deployment with weight steps
- [ ] Can observe rollout progress with CLI
- [ ] Analysis runs and affects promotion
- [ ] Can abort and rollback a rollout

### Cleanup

```bash
kind delete cluster --name rollouts-lab
```

## Next Module

Continue to [Module 2.3: Flux](module-2.3-flux.md) where we'll explore the alternative GitOps toolkit approach.

---

*"Ship fast, but ship safe. Progressive delivery lets you have both."*
