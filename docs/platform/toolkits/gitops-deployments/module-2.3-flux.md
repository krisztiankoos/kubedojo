# Module 2.3: Flux

> **Toolkit Track** | Complexity: `[COMPLEX]` | Time: 40-45 min

## Prerequisites

Before starting this module:
- [Module 2.1: ArgoCD](module-2.1-argocd.md) — GitOps concepts (for comparison)
- [GitOps Discipline](../../disciplines/gitops/) — GitOps principles
- Kubernetes basics
- Git fundamentals

## Why This Module Matters

Flux is the GitOps Toolkit—a set of specialized controllers that each do one thing well. While ArgoCD is an application, Flux is a framework. This gives you incredible flexibility but requires understanding how the pieces fit together.

Flux was created by Weaveworks, the company that coined "GitOps." It's now a CNCF graduated project, running in production at companies like Deutsche Telekom, Volvo, and SAP.

## Did You Know?

- **Weaveworks invented the term "GitOps" in 2017**—Flux was the first tool to implement the concept
- **Flux v2 was a complete rewrite**—the original Flux was a monolith; Flux v2 is a toolkit of specialized controllers
- **Flux can reconcile 1000+ resources per second**—its controller architecture makes it extremely efficient
- **Flux is the only CNCF graduated GitOps project**—ArgoCD is also CNCF but at incubating stage (as of 2024)

## Flux Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUX ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  GIT REPOSITORY                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  clusters/                                                │   │
│  │  ├── production/                                          │   │
│  │  │   ├── flux-system/       (Flux components)            │   │
│  │  │   └── apps/              (Applications)               │   │
│  │  └── staging/                                             │   │
│  └────────────────────────────┬─────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              FLUX CONTROLLERS (GitOps Toolkit)            │   │
│  │                                                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │   Source     │  │ Kustomize    │  │    Helm      │    │   │
│  │  │  Controller  │  │ Controller   │  │  Controller  │    │   │
│  │  │              │  │              │  │              │    │   │
│  │  │ Fetches Git, │  │ Applies      │  │ Manages Helm │    │   │
│  │  │ Helm repos,  │  │ Kustomize    │  │ releases     │    │   │
│  │  │ S3, OCI      │  │ overlays     │  │              │    │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │   │
│  │         │                 │                 │             │   │
│  │         └─────────────────┴─────────────────┘             │   │
│  │                           │                               │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │ Notification │  │    Image     │  │  Image       │    │   │
│  │  │ Controller   │  │  Reflector   │  │  Automation  │    │   │
│  │  │              │  │              │  │              │    │   │
│  │  │ Slack, Teams │  │ Scans        │  │ Updates Git  │    │   │
│  │  │ alerts       │  │ registries   │  │ with new     │    │   │
│  │  │              │  │ for tags     │  │ image tags   │    │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   KUBERNETES CLUSTER                      │   │
│  │                                                           │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │   │
│  │  │ Deploy  │  │ Service │  │  Helm   │  │ Config  │     │   │
│  │  │         │  │         │  │ Release │  │  Map    │     │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Core Controllers

| Controller | CRD | Purpose |
|------------|-----|---------|
| **source-controller** | GitRepository, HelmRepository, OCIRepository, Bucket | Fetches artifacts from external sources |
| **kustomize-controller** | Kustomization | Applies Kustomize overlays |
| **helm-controller** | HelmRelease | Manages Helm chart installations |
| **notification-controller** | Alert, Provider | Sends notifications to Slack, Teams, etc. |
| **image-reflector-controller** | ImageRepository, ImagePolicy | Scans registries for new tags |
| **image-automation-controller** | ImageUpdateAutomation | Commits image tag updates to Git |

## Installing Flux

### Bootstrap with CLI

```bash
# Install Flux CLI
brew install fluxcd/tap/flux  # macOS
# or
curl -s https://fluxcd.io/install.sh | sudo bash

# Check prerequisites
flux check --pre

# Bootstrap with GitHub
flux bootstrap github \
  --owner=my-org \
  --repository=fleet-infra \
  --branch=main \
  --path=./clusters/my-cluster \
  --personal

# Bootstrap with GitLab
flux bootstrap gitlab \
  --owner=my-group \
  --repository=fleet-infra \
  --branch=main \
  --path=./clusters/my-cluster
```

### Bootstrap Result

```
# Creates this structure in your repo:
fleet-infra/
└── clusters/
    └── my-cluster/
        └── flux-system/
            ├── gotk-components.yaml    # Flux controllers
            ├── gotk-sync.yaml          # Self-management
            └── kustomization.yaml
```

### Manual Installation

```bash
# Install all components
kubectl apply -f https://github.com/fluxcd/flux2/releases/latest/download/install.yaml

# Or specific components
flux install \
  --components=source-controller,kustomize-controller,helm-controller \
  --export > flux-components.yaml
```

## Source Management

### GitRepository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 1m                    # How often to check for updates
  url: https://github.com/org/my-app.git
  ref:
    branch: main                  # or tag: v1.0.0, semver: ">=1.0.0"

  # For private repos
  secretRef:
    name: git-credentials

  # Ignore certain paths
  ignore: |
    # Exclude all
    /*
    # Include only deploy folder
    !/deploy
---
# Secret for private repos
apiVersion: v1
kind: Secret
metadata:
  name: git-credentials
  namespace: flux-system
type: Opaque
data:
  username: <base64>
  password: <base64>  # Or use SSH key with 'identity' field
```

### HelmRepository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: HelmRepository
metadata:
  name: bitnami
  namespace: flux-system
spec:
  interval: 1h
  url: https://charts.bitnami.com/bitnami
---
# OCI Registry (Helm 3.8+)
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: HelmRepository
metadata:
  name: podinfo
  namespace: flux-system
spec:
  interval: 1h
  url: oci://ghcr.io/stefanprodan/charts
  type: oci
```

### OCIRepository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: OCIRepository
metadata:
  name: manifests
  namespace: flux-system
spec:
  interval: 5m
  url: oci://ghcr.io/org/manifests
  ref:
    tag: latest

  # For private registries
  secretRef:
    name: oci-credentials
```

## Kustomization

### Basic Kustomization

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 10m
  retryInterval: 2m

  sourceRef:
    kind: GitRepository
    name: my-app

  path: ./deploy/overlays/production

  prune: true                     # Delete removed resources
  wait: true                      # Wait for resources to be ready

  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: my-app
      namespace: production

  # Substitute variables
  postBuild:
    substitute:
      ENVIRONMENT: production
      CLUSTER_NAME: prod-us-east
    substituteFrom:
      - kind: ConfigMap
        name: cluster-config
      - kind: Secret
        name: cluster-secrets
```

### Kustomization Dependencies

```yaml
# Install cert-manager first
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: cert-manager
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: infrastructure
  path: ./cert-manager
---
# Then install ingress (depends on cert-manager)
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: ingress
  namespace: flux-system
spec:
  interval: 10m
  dependsOn:
    - name: cert-manager        # Wait for cert-manager
  sourceRef:
    kind: GitRepository
    name: infrastructure
  path: ./ingress
---
# Then install apps (depends on ingress)
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: apps
  namespace: flux-system
spec:
  interval: 10m
  dependsOn:
    - name: ingress             # Wait for ingress
  sourceRef:
    kind: GitRepository
    name: apps
  path: ./production
```

## HelmRelease

### Basic HelmRelease

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: nginx
  namespace: web
spec:
  interval: 10m
  chart:
    spec:
      chart: nginx
      version: "15.x"           # Semver range
      sourceRef:
        kind: HelmRepository
        name: bitnami
        namespace: flux-system
      interval: 1h

  values:
    replicaCount: 3
    service:
      type: ClusterIP

  # Or from ConfigMap/Secret
  valuesFrom:
    - kind: ConfigMap
      name: nginx-values
      valuesKey: values.yaml
```

### HelmRelease with Dependencies

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: wordpress
  namespace: blog
spec:
  interval: 10m
  dependsOn:
    - name: mysql               # Wait for MySQL to be ready
      namespace: database
  chart:
    spec:
      chart: wordpress
      version: "18.x"
      sourceRef:
        kind: HelmRepository
        name: bitnami
        namespace: flux-system

  values:
    externalDatabase:
      host: mysql.database.svc.cluster.local
      database: wordpress
    mariadb:
      enabled: false
```

### HelmRelease from Git

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: my-app
  namespace: production
spec:
  interval: 10m
  chart:
    spec:
      chart: ./charts/my-app    # Path to chart in repo
      sourceRef:
        kind: GitRepository
        name: my-app
        namespace: flux-system
```

## Image Automation

### Automated Image Updates

```
┌─────────────────────────────────────────────────────────────────┐
│                    IMAGE AUTOMATION FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. CI builds and pushes new image                              │
│     ┌─────────┐      ┌─────────────────┐                        │
│     │   CI    │─────▶│ Container       │                        │
│     │  Build  │      │ Registry        │                        │
│     └─────────┘      │ myapp:v1.2.3    │                        │
│                      └────────┬────────┘                        │
│                               │                                  │
│  2. Image Reflector scans     │                                  │
│     ┌─────────────────────────▼──────────────────────────┐      │
│     │              ImageRepository                        │      │
│     │  Scans registry every 1m                           │      │
│     │  Finds new tag: v1.2.3                             │      │
│     └─────────────────────────┬──────────────────────────┘      │
│                               │                                  │
│  3. Image Policy selects      │                                  │
│     ┌─────────────────────────▼──────────────────────────┐      │
│     │              ImagePolicy                            │      │
│     │  Policy: semver, filter: ^v1\.2\.x                 │      │
│     │  Selected: v1.2.3                                  │      │
│     └─────────────────────────┬──────────────────────────┘      │
│                               │                                  │
│  4. Image Automation updates  │                                  │
│     ┌─────────────────────────▼──────────────────────────┐      │
│     │          ImageUpdateAutomation                      │      │
│     │  Updates deployment.yaml in Git                    │      │
│     │  Commits: "Update myapp to v1.2.3"                 │      │
│     └─────────────────────────┬──────────────────────────┘      │
│                               │                                  │
│  5. Flux syncs change         │                                  │
│     ┌─────────────────────────▼──────────────────────────┐      │
│     │              Kustomization                          │      │
│     │  Detects Git change, applies new manifest          │      │
│     └──────────────────────────────────────────────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Configuration

```yaml
# 1. ImageRepository - Scans container registry
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageRepository
metadata:
  name: my-app
  namespace: flux-system
spec:
  image: ghcr.io/org/my-app
  interval: 1m
  secretRef:
    name: registry-credentials
---
# 2. ImagePolicy - Selects which tags to use
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: my-app
  namespace: flux-system
spec:
  imageRepositoryRef:
    name: my-app
  policy:
    semver:
      range: ">=1.0.0"    # Use any 1.x.x or higher
---
# Or use alphabetical for date-based tags
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: my-app-dev
  namespace: flux-system
spec:
  imageRepositoryRef:
    name: my-app
  policy:
    alphabetical:
      order: desc         # Latest date first
  filterTags:
    pattern: '^main-[a-f0-9]+-(?P<ts>.*)'
    extract: '$ts'
---
# 3. ImageUpdateAutomation - Commits updates
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageUpdateAutomation
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 30m
  sourceRef:
    kind: GitRepository
    name: fleet-infra

  git:
    checkout:
      ref:
        branch: main
    commit:
      author:
        name: fluxcdbot
        email: flux@example.com
      messageTemplate: |
        Update image to {{range .Updated.Images}}{{println .}}{{end}}
    push:
      branch: main

  update:
    path: ./clusters/production
    strategy: Setters
```

### Marking Images for Update

```yaml
# In your deployment.yaml, add markers
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      containers:
        - name: app
          image: ghcr.io/org/my-app:v1.0.0  # {"$imagepolicy": "flux-system:my-app"}
```

## Notifications

### Slack Notifications

```yaml
# Provider - Where to send
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Provider
metadata:
  name: slack
  namespace: flux-system
spec:
  type: slack
  channel: gitops-alerts
  secretRef:
    name: slack-webhook
---
apiVersion: v1
kind: Secret
metadata:
  name: slack-webhook
  namespace: flux-system
data:
  address: <base64-encoded-webhook-url>
---
# Alert - What to send
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Alert
metadata:
  name: all-alerts
  namespace: flux-system
spec:
  providerRef:
    name: slack
  eventSeverity: info
  eventSources:
    - kind: GitRepository
      name: "*"
    - kind: Kustomization
      name: "*"
    - kind: HelmRelease
      name: "*"
```

### GitHub Commit Status

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Provider
metadata:
  name: github
  namespace: flux-system
spec:
  type: github
  address: https://github.com/org/repo
  secretRef:
    name: github-token
---
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Alert
metadata:
  name: sync-status
  namespace: flux-system
spec:
  providerRef:
    name: github
  eventSources:
    - kind: Kustomization
      name: apps
```

## Multi-Cluster Management

### Repository Structure

```
fleet-infra/
├── clusters/
│   ├── production/
│   │   ├── flux-system/
│   │   │   └── gotk-sync.yaml
│   │   └── apps.yaml          # Points to apps/production
│   ├── staging/
│   │   ├── flux-system/
│   │   │   └── gotk-sync.yaml
│   │   └── apps.yaml          # Points to apps/staging
│   └── dev/
│       └── ...
├── infrastructure/
│   ├── base/                  # Shared infra (cert-manager, ingress)
│   ├── production/            # Prod-specific configs
│   └── staging/
└── apps/
    ├── base/                  # App definitions
    ├── production/            # Prod overlays
    └── staging/               # Staging overlays
```

### Cluster Kustomization

```yaml
# clusters/production/apps.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: apps
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: flux-system
  path: ./apps/production
  prune: true

  # Cluster-specific substitutions
  postBuild:
    substitute:
      CLUSTER_NAME: prod-us-east
      ENVIRONMENT: production
```

## Flux vs ArgoCD

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUX vs ARGOCD                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FLUX                              ARGOCD                        │
│  ────                              ──────                        │
│                                                                  │
│  Architecture:                     Architecture:                 │
│  • Toolkit of controllers          • Monolithic application     │
│  • CLI-driven                       • Web UI-driven              │
│  • GitOps-native only               • GitOps + traditional       │
│                                                                  │
│  Strengths:                        Strengths:                    │
│  • Simpler to extend               • Beautiful UI                │
│  • Image automation built-in       • Easier onboarding           │
│  • OCI artifacts native            • Rich RBAC/SSO               │
│  • Lower resource usage            • Diff visualization          │
│                                                                  │
│  Best for:                         Best for:                     │
│  • Platform teams                  • Application teams           │
│  • Automation-first                • UI-first                    │
│  • Multi-cluster at scale          • Developer self-service      │
│                                                                  │
│  Philosophy:                       Philosophy:                   │
│  "Everything is a CR"              "Applications are first-class"│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

RECOMMENDATION:
• Small team, wants UI → ArgoCD
• Platform team, automation-heavy → Flux
• Both work great, pick one and master it
```

## Common Mistakes

| Mistake | Why It's Bad | Better Approach |
|---------|--------------|-----------------|
| No dependencies | Resources apply in random order | Use `dependsOn` for order |
| Missing healthChecks | Flux doesn't wait for readiness | Add deployment health checks |
| Hardcoded values | Can't reuse across environments | Use `postBuild.substitute` |
| No prune | Orphaned resources accumulate | Enable `prune: true` |
| Long intervals | Slow to detect changes | 1m for git, 10m for apps |
| No notifications | Silent failures | Set up Slack/Teams alerts |

## War Story: The Substitution Surprise

A team used Flux's `postBuild.substitute` feature to inject environment-specific values. They had a deployment with:

```yaml
replicas: ${REPLICAS}
```

In production, `REPLICAS=5`. In staging, they forgot to define it. The substitution kept the literal string `${REPLICAS}`, which Kubernetes rejected as invalid integer.

But the error wasn't obvious—the Kustomization showed `Applied successfully` because Kubernetes accepted the manifest. The Deployment just never became ready.

**The fix**:
```yaml
postBuild:
  substituteFrom:
    - kind: ConfigMap
      name: cluster-config
      optional: false  # Fail if missing
```

**The lesson**: Always validate substitutions are defined, and add `healthChecks` to catch silent failures.

## Quiz

### Question 1
What's the main architectural difference between Flux and ArgoCD?

<details>
<summary>Show Answer</summary>

**Flux**: A toolkit of independent controllers (source-controller, kustomize-controller, helm-controller, etc.). Each controller manages specific CRDs and can be installed independently. Configuration is entirely through Kubernetes resources.

**ArgoCD**: A monolithic application with a web UI, API server, and backend. It's installed as a single unit and has its own Application CRD. Configuration can be through UI, CLI, or CRDs.

Flux is more composable and automation-friendly. ArgoCD is more user-friendly with better visualization. Both achieve the same GitOps outcomes.
</details>

### Question 2
How does Flux's image automation work?

<details>
<summary>Show Answer</summary>

Three components work together:

1. **ImageRepository**: Scans a container registry at intervals, finds all available tags

2. **ImagePolicy**: Selects which tag to use based on policy (semver, alphabetical, numerical)

3. **ImageUpdateAutomation**: Updates YAML files in Git with the selected tag and commits the change

The automation requires markers in your YAML:
```yaml
image: myapp:v1.0.0  # {"$imagepolicy": "flux-system:my-app"}
```

This closes the GitOps loop: CI pushes image → Flux updates Git → Flux applies from Git.
</details>

### Question 3
You have three Kustomizations: cert-manager, ingress, and apps. Apps depends on ingress, ingress depends on cert-manager. How would you configure this?

<details>
<summary>Show Answer</summary>

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: cert-manager
spec:
  # No dependencies, runs first
  path: ./cert-manager
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: ingress
spec:
  dependsOn:
    - name: cert-manager
  path: ./ingress
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: apps
spec:
  dependsOn:
    - name: ingress
  path: ./apps
```

Flux will:
1. Apply cert-manager and wait for it to be healthy
2. Then apply ingress and wait for it to be healthy
3. Then apply apps
</details>

### Question 4
Your Flux reconciliation is failing. What commands would you use to debug?

<details>
<summary>Show Answer</summary>

```bash
# Check overall Flux health
flux check

# See all Flux resources and their status
flux get all

# Specific resource status
flux get sources git
flux get kustomizations
flux get helmreleases

# Detailed info on a failing resource
flux get kustomization my-app -o wide

# View events and conditions
kubectl describe kustomization my-app -n flux-system

# View controller logs
flux logs --kind=Kustomization --name=my-app

# Force immediate reconciliation
flux reconcile kustomization my-app --with-source

# Suspend to stop reconciliation during debugging
flux suspend kustomization my-app
flux resume kustomization my-app
```
</details>

## Hands-On Exercise

### Scenario: GitOps with Flux

Bootstrap Flux and deploy an application with image automation.

### Setup

```bash
# Create kind cluster
kind create cluster --name flux-lab

# Check Flux prerequisites
flux check --pre

# Since we don't have a real Git repo, we'll use local manifests
# Install Flux controllers only
flux install
```

### Deploy Application Manually (Simulated GitOps)

```bash
# Create a GitRepository pointing to a public repo
flux create source git podinfo \
  --url=https://github.com/stefanprodan/podinfo \
  --branch=master \
  --interval=1m \
  --export > podinfo-source.yaml

kubectl apply -f podinfo-source.yaml

# Create Kustomization to deploy podinfo
flux create kustomization podinfo \
  --source=GitRepository/podinfo \
  --path="./kustomize" \
  --prune=true \
  --interval=10m \
  --export > podinfo-kustomization.yaml

kubectl apply -f podinfo-kustomization.yaml
```

### Verify Deployment

```bash
# Check Flux resources
flux get sources git
flux get kustomizations

# Check deployed pods
kubectl get pods -A | grep podinfo

# Watch reconciliation
flux get kustomizations --watch
```

### Deploy a HelmRelease

```bash
# Add Bitnami repository
flux create source helm bitnami \
  --url=https://charts.bitnami.com/bitnami \
  --interval=1h \
  --export > bitnami-source.yaml

kubectl apply -f bitnami-source.yaml

# Deploy NGINX via Helm
cat <<EOF | kubectl apply -f -
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: nginx
  namespace: default
spec:
  interval: 10m
  chart:
    spec:
      chart: nginx
      version: "15.x"
      sourceRef:
        kind: HelmRepository
        name: bitnami
        namespace: flux-system
  values:
    replicaCount: 2
    service:
      type: ClusterIP
EOF

# Check HelmRelease status
flux get helmreleases
```

### Suspend and Resume

```bash
# Suspend reconciliation
flux suspend kustomization podinfo

# Make a change (it won't be reverted)
kubectl scale deployment podinfo --replicas=5

# Resume reconciliation (change will be reverted)
flux resume kustomization podinfo

# Verify pods went back to original count
kubectl get pods | grep podinfo
```

### Success Criteria

- [ ] Flux controllers are running
- [ ] GitRepository source is synced
- [ ] Kustomization applies manifests
- [ ] HelmRelease deploys chart
- [ ] Understand suspend/resume behavior

### Cleanup

```bash
kind delete cluster --name flux-lab
rm -f podinfo-*.yaml bitnami-source.yaml
```

## Next Module

Continue to [Module 2.4: Helm & Kustomize](module-2.4-helm-kustomize.md) where we'll dive deep into the package management tools that power GitOps.

---

*"GitOps is not a tool, it's a practice. Flux gives you the toolkit to practice it well."*
