# Module 2.4: Helm & Kustomize

> **Toolkit Track** | Complexity: `[MEDIUM]` | Time: 35-40 min

## Prerequisites

Before starting this module:
- [Module 2.1: ArgoCD](module-2.1-argocd.md) or [Module 2.3: Flux](module-2.3-flux.md)
- Basic Kubernetes YAML knowledge
- Understanding of templating concepts

## Why This Module Matters

Raw Kubernetes YAML doesn't scale. When you have 50 services, each with development, staging, and production variants, you need a way to manage configuration. Helm and Kustomize are the two dominant solutions—and they work together beautifully.

Helm packages applications as charts with templates. Kustomize overlays modifications without templates. Understanding both—and when to use each—is essential for Kubernetes operations.

## Did You Know?

- **Helm v3 removed Tiller entirely**—Helm v2's server-side component was a security concern; now Helm is purely client-side
- **Kustomize is built into kubectl**—since 1.14, you can use `kubectl apply -k` without installing anything
- **The name "Helm" follows the Kubernetes nautical theme**—a helm steers a ship, Helm steers your deployments
- **Kustomize was created by Google for internal use**—they needed a template-free way to customize configurations

## Helm vs Kustomize

```
┌─────────────────────────────────────────────────────────────────┐
│                    HELM vs KUSTOMIZE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  HELM                              KUSTOMIZE                     │
│  ────                              ─────────                     │
│                                                                  │
│  Model: Packaging                  Model: Patching               │
│  • Chart = package                 • Base + overlays             │
│  • Templates + values              • No templates                │
│  • Releases tracked                • Pure YAML                   │
│                                                                  │
│  Good for:                         Good for:                     │
│  • Third-party apps                • Your own apps               │
│  • Complex applications            • Environment variants        │
│  • Version management              • Last-mile customization     │
│  • Sharing across teams            • Patching Helm output        │
│                                                                  │
│  Template syntax:                  Patch syntax:                 │
│  {{ .Values.replicas }}            - op: replace                 │
│                                      path: /spec/replicas        │
│                                      value: 3                    │
│                                                                  │
│  BEST PRACTICE: Use together!                                   │
│  Helm for packages → Kustomize for environment-specific patches │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Helm Fundamentals

### Chart Structure

```
my-app/
├── Chart.yaml          # Metadata
├── values.yaml         # Default values
├── charts/             # Dependencies
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── _helpers.tpl    # Template helpers
│   ├── NOTES.txt       # Post-install notes
│   └── tests/
│       └── test-connection.yaml
└── README.md
```

### Chart.yaml

```yaml
apiVersion: v2
name: my-app
description: A Helm chart for my application
type: application  # or "library"
version: 1.0.0     # Chart version
appVersion: "2.3.1"  # App version

keywords:
  - app
  - web

home: https://github.com/org/my-app
sources:
  - https://github.com/org/my-app

maintainers:
  - name: Platform Team
    email: platform@example.com

dependencies:
  - name: postgresql
    version: "12.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
```

### values.yaml

```yaml
# values.yaml - defaults
replicaCount: 1

image:
  repository: myapp
  tag: "latest"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: nginx
  hosts:
    - host: myapp.local
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 50m
    memory: 64Mi

postgresql:
  enabled: true
  auth:
    database: myapp
```

### Template Syntax

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-app.fullname" . }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "my-app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "my-app.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 80
          {{- if .Values.resources }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          {{- end }}
          {{- if .Values.env }}
          env:
            {{- range $key, $value := .Values.env }}
            - name: {{ $key }}
              value: {{ $value | quote }}
            {{- end }}
          {{- end }}
```

### Template Helpers

```yaml
# templates/_helpers.tpl
{{/*
Expand the name of the chart.
*/}}
{{- define "my-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "my-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "my-app.labels" -}}
helm.sh/chart: {{ include "my-app.chart" . }}
{{ include "my-app.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "my-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "my-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

### Helm Commands

```bash
# Create new chart
helm create my-app

# Lint chart
helm lint my-app/

# Template locally (dry-run)
helm template my-release my-app/ -f values-prod.yaml

# Install
helm install my-release my-app/ \
  --namespace production \
  --create-namespace \
  -f values-prod.yaml

# Upgrade
helm upgrade my-release my-app/ \
  --namespace production \
  -f values-prod.yaml

# Rollback
helm rollback my-release 1 --namespace production

# List releases
helm list --all-namespaces

# Get release values
helm get values my-release --namespace production

# Uninstall
helm uninstall my-release --namespace production

# Package chart
helm package my-app/

# Push to OCI registry
helm push my-app-1.0.0.tgz oci://ghcr.io/org/charts
```

### Helm Dependencies

```bash
# Update dependencies
helm dependency update my-app/

# Build dependencies
helm dependency build my-app/
```

```yaml
# Chart.yaml
dependencies:
  - name: postgresql
    version: "12.1.0"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
    tags:
      - database

  - name: redis
    version: "17.x"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
```

```yaml
# values.yaml
postgresql:
  enabled: true
  primary:
    persistence:
      size: 10Gi

redis:
  enabled: false
```

## Kustomize Fundamentals

### Directory Structure

```
my-app/
├── base/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
└── overlays/
    ├── development/
    │   ├── kustomization.yaml
    │   └── replica-patch.yaml
    ├── staging/
    │   ├── kustomization.yaml
    │   └── namespace.yaml
    └── production/
        ├── kustomization.yaml
        ├── replica-patch.yaml
        └── ingress.yaml
```

### Base kustomization.yaml

```yaml
# base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - deployment.yaml
  - service.yaml
  - configmap.yaml

# Common labels for all resources
commonLabels:
  app: my-app

# Common annotations
commonAnnotations:
  team: platform
```

### Overlay kustomization.yaml

```yaml
# overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: production
namePrefix: prod-

resources:
  - ../../base
  - ingress.yaml

# Strategic merge patches
patches:
  - path: replica-patch.yaml

# Or inline patches
patches:
  - patch: |-
      - op: replace
        path: /spec/replicas
        value: 5
    target:
      kind: Deployment
      name: my-app

# Image overrides
images:
  - name: myapp
    newName: myregistry/myapp
    newTag: v2.0.0

# ConfigMap/Secret generators
configMapGenerator:
  - name: app-config
    literals:
      - ENVIRONMENT=production
      - LOG_LEVEL=info

secretGenerator:
  - name: app-secrets
    literals:
      - DATABASE_URL=postgres://prod-db:5432/app
    type: Opaque
```

### Patch Types

```yaml
# Strategic Merge Patch (default)
# replica-patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 5

---
# JSON Patch
# kustomization.yaml
patches:
  - patch: |-
      - op: replace
        path: /spec/replicas
        value: 5
      - op: add
        path: /metadata/labels/env
        value: production
    target:
      kind: Deployment
      name: my-app

---
# Patch file with target
# kustomization.yaml
patches:
  - path: increase-memory.yaml
    target:
      kind: Deployment
      labelSelector: "app=my-app"
```

### Components (Reusable Patches)

```yaml
# components/monitoring/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component

patches:
  - patch: |-
      - op: add
        path: /spec/template/metadata/annotations/prometheus.io~1scrape
        value: "true"
      - op: add
        path: /spec/template/metadata/annotations/prometheus.io~1port
        value: "8080"
    target:
      kind: Deployment

---
# overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base

components:
  - ../../components/monitoring
  - ../../components/security
```

### Replacements (Variable Substitution)

```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - deployment.yaml
  - configmap.yaml

replacements:
  - source:
      kind: ConfigMap
      name: app-config
      fieldPath: data.HOSTNAME
    targets:
      - select:
          kind: Deployment
          name: my-app
        fieldPaths:
          - spec.template.spec.containers.[name=app].env.[name=HOSTNAME].value
```

### Kustomize Commands

```bash
# Build (render YAML)
kustomize build overlays/production

# Apply
kubectl apply -k overlays/production

# Preview diff
kubectl diff -k overlays/production

# View resources
kustomize build overlays/production | kubectl get -f - -o name
```

## Helm + Kustomize Together

### Pattern: Kustomize Wrapping Helm

```
my-deployment/
├── base/
│   ├── kustomization.yaml
│   └── helmrelease.yaml      # Flux HelmRelease or ArgoCD Application
└── overlays/
    ├── staging/
    │   ├── kustomization.yaml
    │   └── values-patch.yaml
    └── production/
        ├── kustomization.yaml
        └── values-patch.yaml
```

### ArgoCD: Helm + Kustomize

```yaml
# ArgoCD Application using both
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  source:
    repoURL: https://charts.example.com
    chart: my-app
    targetRevision: 1.0.0

    # Helm values
    helm:
      values: |
        replicaCount: 3

    # Plus Kustomize patches
    kustomize:
      patches:
        - patch: |-
            - op: add
              path: /metadata/annotations
              value:
                custom.annotation: "true"
          target:
            kind: Deployment
```

### Flux: Post-Rendering with Kustomize

```yaml
# HelmRelease with post-rendering
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: my-app
spec:
  chart:
    spec:
      chart: my-app
      sourceRef:
        kind: HelmRepository
        name: my-charts

  values:
    replicaCount: 3

  # Post-render with Kustomize
  postRenderers:
    - kustomize:
        patches:
          - patch: |-
              - op: add
                path: /metadata/labels/custom
                value: label
            target:
              kind: Deployment

        images:
          - name: my-app
            newTag: v2.0.0-custom
```

### Umbrella Chart Pattern

```yaml
# Chart.yaml - umbrella chart
apiVersion: v2
name: platform
version: 1.0.0

dependencies:
  - name: cert-manager
    version: "1.13.0"
    repository: https://charts.jetstack.io
    condition: cert-manager.enabled

  - name: ingress-nginx
    version: "4.8.0"
    repository: https://kubernetes.github.io/ingress-nginx
    condition: ingress-nginx.enabled

  - name: prometheus
    version: "25.0.0"
    repository: https://prometheus-community.github.io/helm-charts
    condition: prometheus.enabled
```

```yaml
# values.yaml
cert-manager:
  enabled: true
  installCRDs: true

ingress-nginx:
  enabled: true
  controller:
    replicaCount: 2

prometheus:
  enabled: true
  alertmanager:
    enabled: false
```

## Common Mistakes

| Mistake | Why It's Bad | Better Approach |
|---------|--------------|-----------------|
| Hardcoded values in templates | Can't customize | Use `{{ .Values.x }}` with defaults |
| Deeply nested values | Hard to override | Keep values 2-3 levels deep max |
| No schema validation | Invalid values accepted | Use `values.schema.json` |
| Kustomize without base | Duplication across overlays | Always use base + overlays |
| Mixing patch types | Confusing, hard to debug | Pick one style per patch file |
| Over-templating | Unmaintainable | Use Kustomize for simple overrides |

## War Story: The Template Explosion

A team created a Helm chart with 50+ template values for every possible configuration. The `values.yaml` was 800 lines. Nobody could understand it.

Worse, they templated things that never changed—like the container port or health check paths. Every deployment required reviewing dozens of irrelevant values.

**The fix**: They stripped the chart to 20 essential values. For environment-specific tweaks, they used Kustomize overlays. The result: a readable chart plus simple patches.

```yaml
# Before: values.yaml had 50+ values
# After: values.yaml
replicaCount: 1
image:
  repository: myapp
  tag: latest
resources: {}

# Environment differences via Kustomize overlay
# overlays/production/patch.yaml
```

**The lesson**: Don't template everything. Template what varies between releases. Use Kustomize for what varies between environments.

## Quiz

### Question 1
When would you use Helm over Kustomize, and vice versa?

<details>
<summary>Show Answer</summary>

**Use Helm when:**
- Installing third-party applications (nginx-ingress, prometheus, etc.)
- Packaging complex applications with many configuration options
- You need version management and rollback
- Sharing applications across teams or organizations
- Application has complex conditional logic

**Use Kustomize when:**
- Customizing your own applications for different environments
- Patching third-party Helm charts with minor changes
- You want template-free, pure YAML
- Making last-mile customizations
- Simple overlay patterns (dev/staging/prod)

**Best practice**: Use both! Helm for packaging, Kustomize for environment customization.
</details>

### Question 2
What's wrong with this Helm template?

```yaml
containers:
  - name: app
    image: myapp:{{ .Values.image.tag }}
    env:
      {{- range .Values.env }}
      - name: {{ .name }}
        value: {{ .value }}
      {{- end }}
```

<details>
<summary>Show Answer</summary>

Two issues:

1. **Missing quote function for tag**: If `tag` is a number like `1.0`, YAML will interpret it as a float. Use `{{ .Values.image.tag | quote }}` or `"{{ .Values.image.tag }}"`.

2. **Values not quoted**: The `value` field should be quoted in case it contains special characters.

Fixed:
```yaml
containers:
  - name: app
    image: "myapp:{{ .Values.image.tag }}"
    env:
      {{- range .Values.env }}
      - name: {{ .name | quote }}
        value: {{ .value | quote }}
      {{- end }}
```
</details>

### Question 3
Write a Kustomize patch that adds a sidecar container to all Deployments in the overlay.

<details>
<summary>Show Answer</summary>

```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base

patches:
  - patch: |-
      - op: add
        path: /spec/template/spec/containers/-
        value:
          name: sidecar
          image: fluentd:latest
          resources:
            limits:
              memory: 100Mi
              cpu: 50m
    target:
      kind: Deployment

# Or using strategic merge patch file:
# sidecar-patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: not-used  # Will be overwritten by target selector
spec:
  template:
    spec:
      containers:
        - name: sidecar
          image: fluentd:latest
```

The JSON Patch with `/-` adds to the end of the containers array.
</details>

### Question 4
How do you pass values to a Helm subchart (dependency)?

<details>
<summary>Show Answer</summary>

In the parent chart's `values.yaml`, nest values under the subchart name:

```yaml
# Parent values.yaml
replicaCount: 3

# Values for postgresql subchart
postgresql:
  auth:
    database: myapp
    username: myuser
  primary:
    persistence:
      size: 20Gi

# Values for redis subchart
redis:
  architecture: standalone
  master:
    persistence:
      enabled: false
```

The subchart name must match the `name` field in `Chart.yaml` dependencies. Helm automatically passes the nested values to the subchart.

You can also use `--set postgresql.auth.database=myapp` on the command line.
</details>

## Hands-On Exercise

### Scenario: Multi-Environment Application

Create a Helm chart with Kustomize overlays for dev, staging, and production.

### Create Helm Chart

```bash
# Create chart
helm create my-app
cd my-app

# Simplify values.yaml
cat > values.yaml << 'EOF'
replicaCount: 1

image:
  repository: nginx
  tag: "1.25"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 50m
    memory: 64Mi

env: []
EOF
```

### Create Kustomize Structure

```bash
cd ..
mkdir -p kustomize/{base,overlays/{dev,staging,production}}

# Generate base from Helm
helm template my-app ./my-app > kustomize/base/all.yaml

# Create base kustomization
cat > kustomize/base/kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - all.yaml
EOF

# Dev overlay
cat > kustomize/overlays/dev/kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: dev
namePrefix: dev-
resources:
  - ../../base
patches:
  - patch: |-
      - op: replace
        path: /spec/replicas
        value: 1
    target:
      kind: Deployment
EOF

# Production overlay
cat > kustomize/overlays/production/kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: production
namePrefix: prod-
resources:
  - ../../base
patches:
  - patch: |-
      - op: replace
        path: /spec/replicas
        value: 5
      - op: replace
        path: /spec/template/spec/containers/0/resources/limits/memory
        value: 512Mi
    target:
      kind: Deployment
images:
  - name: nginx
    newTag: "1.25-alpine"
EOF
```

### Build and Compare

```bash
# Build dev
kustomize build kustomize/overlays/dev

# Build production
kustomize build kustomize/overlays/production

# Compare
diff <(kustomize build kustomize/overlays/dev) \
     <(kustomize build kustomize/overlays/production)
```

### Apply to Cluster

```bash
# Create namespaces
kubectl create namespace dev
kubectl create namespace production

# Apply
kubectl apply -k kustomize/overlays/dev
kubectl apply -k kustomize/overlays/production

# Verify
kubectl get pods -n dev
kubectl get pods -n production
```

### Success Criteria

- [ ] Helm chart renders correctly
- [ ] Kustomize overlays modify base
- [ ] Dev has 1 replica, production has 5
- [ ] Production uses alpine image tag
- [ ] Can apply to different namespaces

### Cleanup

```bash
kubectl delete -k kustomize/overlays/dev
kubectl delete -k kustomize/overlays/production
kubectl delete namespace dev production
rm -rf my-app kustomize
```

## Summary

You've completed the GitOps & Deployments Toolkit! You now understand:

- **ArgoCD**: Application-centric GitOps with UI
- **Argo Rollouts**: Progressive delivery (canary, blue-green)
- **Flux**: Toolkit-based GitOps with image automation
- **Helm & Kustomize**: Package management and overlays

These tools form the foundation of modern Kubernetes deployment practices.

## Next Steps

Continue to [CI/CD Pipelines Toolkit](../ci-cd-pipelines/) where we'll explore Dagger, Tekton, and Argo Workflows for building before deploying.

---

*"The best config is the one you understand. The second best is the one that works. Helm and Kustomize help you get both."*
