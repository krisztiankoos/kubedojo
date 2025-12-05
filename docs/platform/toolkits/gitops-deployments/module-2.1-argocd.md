# Module 2.1: ArgoCD

> **Toolkit Track** | Complexity: `[COMPLEX]` | Time: 45-50 min

## Prerequisites

Before starting this module:
- [GitOps Discipline](../../disciplines/gitops/) — GitOps principles and practices
- Kubernetes basics (Deployments, Services, Namespaces)
- Git fundamentals
- kubectl experience

## Why This Module Matters

ArgoCD is the most popular GitOps tool in the Kubernetes ecosystem. It watches Git repositories and automatically syncs your cluster state to match what's defined in version control. No more `kubectl apply` from laptops—every change is auditable, reviewable, and reversible.

Understanding ArgoCD isn't just about knowing the tool—it's about adopting a deployment philosophy that eliminates configuration drift and makes rollbacks trivial.

## Did You Know?

- **ArgoCD syncs over 1 million applications in production**—it's used by Intuit (its creator), Tesla, NVIDIA, and thousands of companies
- **The name "Argo" comes from Greek mythology**—the ship that carried Jason and the Argonauts, fitting for a tool that "navigates" deployments
- **ArgoCD was originally built for Intuit's 150+ Kubernetes clusters**—they needed a way to manage deployments at scale without tribal knowledge
- **ArgoCD supports 50+ config management tools**—Helm, Kustomize, Jsonnet, plain YAML, and custom plugins

## ArgoCD Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARGOCD ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  GIT REPOSITORY                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  apps/                                                    │   │
│  │  ├── deployment.yaml                                      │   │
│  │  ├── service.yaml                                         │   │
│  │  └── configmap.yaml                                       │   │
│  └────────────────────────────┬─────────────────────────────┘   │
│                               │                                  │
│                               │ Watch + Fetch                    │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    ARGOCD SERVER                          │   │
│  │                                                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
│  │  │ API Server  │  │ Repo Server │  │ Application │       │   │
│  │  │             │  │             │  │ Controller  │       │   │
│  │  │ • UI/CLI    │  │ • Clone     │  │             │       │   │
│  │  │ • Auth      │  │ • Render    │  │ • Watch     │       │   │
│  │  │ • RBAC      │  │ • Cache     │  │ • Sync      │       │   │
│  │  └─────────────┘  └─────────────┘  └──────┬──────┘       │   │
│  │                                           │               │   │
│  └───────────────────────────────────────────┼──────────────┘   │
│                                              │                   │
│                                              │ Apply             │
│                                              ▼                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   KUBERNETES CLUSTER                      │   │
│  │                                                           │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │   │
│  │  │ Deploy  │  │ Service │  │ Config  │  │ Secret  │     │   │
│  │  │         │  │         │  │  Map    │  │         │     │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Purpose |
|-----------|---------|
| **API Server** | Serves UI, CLI, RBAC, webhook endpoints |
| **Repo Server** | Clones repos, renders manifests (Helm/Kustomize) |
| **Application Controller** | Watches apps, detects drift, triggers sync |
| **Dex** | OIDC provider for SSO integration |
| **Redis** | Caching for repo server performance |

## Installing ArgoCD

### Quick Install

```bash
# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods
kubectl -n argocd wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server --timeout=120s

# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
echo

# Port forward to access UI
kubectl -n argocd port-forward svc/argocd-server 8080:443 &
```

### Production Install with Helm

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

helm install argocd argo/argo-cd \
  --namespace argocd \
  --create-namespace \
  --set server.replicas=2 \
  --set controller.replicas=2 \
  --set repoServer.replicas=2 \
  --set redis.enabled=true \
  --set server.ingress.enabled=true \
  --set server.ingress.hosts[0]=argocd.example.com
```

### ArgoCD CLI

```bash
# Install CLI
brew install argocd  # macOS
# or
curl -sSL -o argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x argocd && sudo mv argocd /usr/local/bin/

# Login
argocd login localhost:8080 --username admin --password <password> --insecure

# Add cluster (if managing external clusters)
argocd cluster add my-cluster-context
```

## Applications

### Basic Application

```yaml
# app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/org/app-manifests.git
    targetRevision: HEAD
    path: apps/my-app

  destination:
    server: https://kubernetes.default.svc
    namespace: my-app

  syncPolicy:
    automated:
      prune: true       # Delete resources removed from Git
      selfHeal: true    # Revert manual changes
    syncOptions:
      - CreateNamespace=true
```

### Application with Helm

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: nginx
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://charts.bitnami.com/bitnami
    chart: nginx
    targetRevision: 15.4.0
    helm:
      releaseName: nginx
      values: |
        replicaCount: 3
        service:
          type: ClusterIP

      # Or reference values file from Git
      # valueFiles:
      #   - values-production.yaml

      # Or set individual parameters
      # parameters:
      #   - name: replicaCount
      #     value: "3"

  destination:
    server: https://kubernetes.default.svc
    namespace: nginx
```

### Application with Kustomize

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: app-production
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/org/app.git
    targetRevision: HEAD
    path: overlays/production

    # Kustomize-specific options
    kustomize:
      images:
        - myapp=myregistry/myapp:v2.0.0
      namePrefix: prod-
      commonLabels:
        env: production

  destination:
    server: https://kubernetes.default.svc
    namespace: production
```

## Sync Strategies

### Sync Waves and Hooks

```yaml
# Sync waves: Control order of resource creation
apiVersion: v1
kind: Namespace
metadata:
  name: my-app
  annotations:
    argocd.argoproj.io/sync-wave: "-1"  # Create first
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: config
  annotations:
    argocd.argoproj.io/sync-wave: "0"   # Create second
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  annotations:
    argocd.argoproj.io/sync-wave: "1"   # Create third
```

### Resource Hooks

```yaml
# Pre-sync hook: Run before sync
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrate
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      containers:
        - name: migrate
          image: myapp:latest
          command: ["./migrate.sh"]
      restartPolicy: Never
---
# Post-sync hook: Run after sync
apiVersion: batch/v1
kind: Job
metadata:
  name: notify-slack
  annotations:
    argocd.argoproj.io/hook: PostSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      containers:
        - name: notify
          image: curlimages/curl
          command:
            - curl
            - -X
            - POST
            - $(SLACK_WEBHOOK)
            - -d
            - '{"text":"Deployment complete!"}'
      restartPolicy: Never
```

### Hook Types

| Hook | When It Runs |
|------|--------------|
| `PreSync` | Before sync begins |
| `Sync` | During sync (with manifests) |
| `PostSync` | After all Sync hooks complete |
| `SyncFail` | When sync fails |
| `Skip` | Skip applying this resource |

## App of Apps Pattern

### Why App of Apps?

```
MANAGING 50 APPLICATIONS:

Without App of Apps:                 With App of Apps:
─────────────────────────────────────────────────────────────────

argocd/                             argocd/
├── app1.yaml                       └── root-app.yaml  ◀── ONE FILE
├── app2.yaml
├── app3.yaml                       apps/
├── ...                             ├── app1/
└── app50.yaml                      │   └── application.yaml
                                    ├── app2/
50 Application CRs to manage        │   └── application.yaml
                                    └── ...

Problem: How do you deploy                ▲
the Application CRs themselves?           │
                                    Root app watches
                                    this directory
```

### Implementing App of Apps

```yaml
# root-app.yaml - The "app of apps"
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/argocd-apps.git
    targetRevision: HEAD
    path: apps
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

```
# Repository structure
argocd-apps/
├── apps/
│   ├── cert-manager/
│   │   └── application.yaml
│   ├── ingress-nginx/
│   │   └── application.yaml
│   ├── monitoring/
│   │   └── application.yaml
│   └── my-apps/
│       ├── app1.yaml
│       ├── app2.yaml
│       └── app3.yaml
└── root-app.yaml
```

```yaml
# apps/cert-manager/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cert-manager
  namespace: argocd
  annotations:
    argocd.argoproj.io/sync-wave: "-2"  # Install early
spec:
  project: default
  source:
    repoURL: https://charts.jetstack.io
    chart: cert-manager
    targetRevision: v1.13.0
    helm:
      values: |
        installCRDs: true
  destination:
    server: https://kubernetes.default.svc
    namespace: cert-manager
```

## ApplicationSets

### Template-Based Application Generation

```yaml
# Generate apps from Git directories
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: cluster-addons
  namespace: argocd
spec:
  generators:
    - git:
        repoURL: https://github.com/org/cluster-addons.git
        revision: HEAD
        directories:
          - path: addons/*

  template:
    metadata:
      name: '{{path.basename}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/org/cluster-addons.git
        targetRevision: HEAD
        path: '{{path}}'
      destination:
        server: https://kubernetes.default.svc
        namespace: '{{path.basename}}'
```

### Multi-Cluster Deployment

```yaml
# Deploy to multiple clusters
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: my-app
  namespace: argocd
spec:
  generators:
    - list:
        elements:
          - cluster: production
            url: https://prod.k8s.example.com
            values:
              replicas: "5"
          - cluster: staging
            url: https://staging.k8s.example.com
            values:
              replicas: "2"

  template:
    metadata:
      name: 'my-app-{{cluster}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/org/my-app.git
        targetRevision: HEAD
        path: deploy
        helm:
          parameters:
            - name: replicas
              value: '{{values.replicas}}'
      destination:
        server: '{{url}}'
        namespace: my-app
```

### Generator Types

| Generator | Use Case |
|-----------|----------|
| `list` | Static list of elements |
| `clusters` | All registered ArgoCD clusters |
| `git` | Directories or files in a Git repo |
| `matrix` | Combine two generators |
| `merge` | Merge multiple generators |
| `pullRequest` | GitHub/GitLab PRs for preview environments |

## Projects and RBAC

### ArgoCD Projects

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: team-a
  namespace: argocd
spec:
  description: Team A's applications

  # Allowed source repos
  sourceRepos:
    - https://github.com/org/team-a-*
    - https://charts.bitnami.com/bitnami

  # Allowed destination clusters/namespaces
  destinations:
    - namespace: team-a-*
      server: https://kubernetes.default.svc
    - namespace: '*'
      server: https://staging.example.com

  # Allowed resource kinds
  clusterResourceWhitelist:
    - group: ''
      kind: Namespace
  namespaceResourceWhitelist:
    - group: '*'
      kind: '*'

  # Deny specific resources
  namespaceResourceBlacklist:
    - group: ''
      kind: Secret  # Can't create secrets directly

  # Roles for this project
  roles:
    - name: developer
      description: Can sync applications
      policies:
        - p, proj:team-a:developer, applications, sync, team-a/*, allow
        - p, proj:team-a:developer, applications, get, team-a/*, allow
      groups:
        - team-a-developers  # OIDC group
```

### RBAC Policies

```yaml
# argocd-rbac-cm ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-rbac-cm
  namespace: argocd
data:
  policy.default: role:readonly

  policy.csv: |
    # Admin: Full access
    g, admins, role:admin

    # Developer: Sync and view
    p, role:developer, applications, get, */*, allow
    p, role:developer, applications, sync, */*, allow
    p, role:developer, logs, get, */*, allow

    # Viewer: Read-only
    p, role:viewer, applications, get, */*, allow
    p, role:viewer, projects, get, *, allow

    # Map groups to roles
    g, developers, role:developer
    g, viewers, role:viewer

  scopes: '[groups]'
```

## Multi-Tenancy

### Namespace Isolation

```yaml
# Restrict team to their namespaces
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: team-payments
  namespace: argocd
spec:
  destinations:
    # Only these namespaces
    - namespace: payments-*
      server: https://kubernetes.default.svc

  # Must use these labels
  clusterResourceWhitelist: []  # No cluster resources

  sourceRepos:
    - https://github.com/company/payments-*

  # Enforce resource quotas via sync waves
  orphanedResources:
    warn: true
```

### Soft Multi-Tenancy Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    MULTI-TENANT ARGOCD                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TEAM A                        TEAM B                            │
│  ┌────────────────────┐       ┌────────────────────┐            │
│  │ Project: team-a    │       │ Project: team-b    │            │
│  │                    │       │                    │            │
│  │ Repos: org/team-a-*│       │ Repos: org/team-b-*│            │
│  │ NS: team-a-*       │       │ NS: team-b-*       │            │
│  └─────────┬──────────┘       └─────────┬──────────┘            │
│            │                            │                        │
│            ▼                            ▼                        │
│  ┌────────────────────┐       ┌────────────────────┐            │
│  │ team-a-production  │       │ team-b-production  │            │
│  │ team-a-staging     │       │ team-b-staging     │            │
│  └────────────────────┘       └────────────────────┘            │
│                                                                  │
│  SHARED ARGOCD INSTANCE                                          │
│  • SSO via OIDC (groups → project roles)                        │
│  • Audit logging enabled                                         │
│  • Resource quotas per project                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Common Mistakes

| Mistake | Why It's Bad | Better Approach |
|---------|--------------|-----------------|
| Secrets in Git | Exposed credentials | Use External Secrets, Sealed Secrets, or Vault |
| No sync waves | Resources created in wrong order | Use sync-wave annotations for dependencies |
| Ignoring prune | Orphaned resources accumulate | Enable `prune: true` or manage orphaned resources |
| Manual kubectl changes | Drift from Git source | Enable `selfHeal: true` to revert changes |
| No projects | No isolation between teams | Create projects per team with RBAC |
| Hardcoded image tags | Can't track what's deployed | Use image updater or Git automation |

## War Story: The Accidental Wipe

A platform team enabled `prune: true` on their root app-of-apps without testing. When they accidentally deleted an application manifest from Git, ArgoCD helpfully pruned all 200 resources in that namespace—including a production database PVC.

**The fix**:
1. Always use `finalizers` to prevent accidental deletion
2. Enable `orphanedResources.warn` before enabling `prune`
3. Use `argocd.argoproj.io/sync-options: Prune=false` for stateful resources

```yaml
# Protect against accidental deletion
metadata:
  finalizers:
    - resources-finalizer.argocd.argoproj.io
  annotations:
    argocd.argoproj.io/sync-options: Prune=false
```

**The lesson**: GitOps is powerful—it applies what's in Git. Make sure what's in Git is what you want.

## Quiz

### Question 1
What's the difference between `selfHeal` and `prune` in ArgoCD sync policy?

<details>
<summary>Show Answer</summary>

**selfHeal**: Reverts manual changes made to the cluster that differ from Git. If someone runs `kubectl edit deployment` and changes replicas, ArgoCD will change it back.

**prune**: Deletes resources from the cluster that no longer exist in Git. If you remove a ConfigMap from your manifests, ArgoCD will delete it from the cluster.

Both can be dangerous if misconfigured:
- `selfHeal` can undo emergency fixes (disable before hotfixes)
- `prune` can delete stateful data (protect PVCs with annotations)
</details>

### Question 2
You have 5 services that must be deployed in order: Namespace → ConfigMap → Secret → Deployment → Ingress. How do you ensure this order?

<details>
<summary>Show Answer</summary>

Use sync waves with annotations:

```yaml
# namespace.yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-2"

# configmap.yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-1"

# secret.yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "0"

# deployment.yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "1"

# ingress.yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "2"
```

Lower numbers sync first. ArgoCD waits for each wave's resources to be healthy before proceeding.
</details>

### Question 3
How would you deploy the same application to 10 clusters with different configurations per cluster?

<details>
<summary>Show Answer</summary>

Use an ApplicationSet with a list generator:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: my-app
spec:
  generators:
    - list:
        elements:
          - cluster: prod-us
            url: https://prod-us.example.com
            replicas: "10"
            region: us-east-1
          - cluster: prod-eu
            url: https://prod-eu.example.com
            replicas: "5"
            region: eu-west-1
          # ... 8 more clusters

  template:
    metadata:
      name: 'my-app-{{cluster}}'
    spec:
      source:
        repoURL: https://github.com/org/my-app.git
        path: deploy
        helm:
          parameters:
            - name: replicas
              value: '{{replicas}}'
            - name: region
              value: '{{region}}'
      destination:
        server: '{{url}}'
        namespace: my-app
```

For dynamic cluster lists, use the `clusters` generator with labels.
</details>

### Question 4
Your team accidentally pushed a broken config to Git and ArgoCD deployed it. How do you roll back?

<details>
<summary>Show Answer</summary>

Several options:

1. **Git revert** (recommended):
   ```bash
   git revert HEAD
   git push
   ```
   ArgoCD syncs the reverted state automatically.

2. **ArgoCD rollback**:
   ```bash
   argocd app rollback my-app --revision 5
   ```
   This syncs to a previous Git commit. Note: If auto-sync is enabled, it will re-sync to HEAD.

3. **Disable auto-sync, fix, re-enable**:
   ```bash
   argocd app set my-app --sync-policy none
   # Fix the issue in Git
   argocd app sync my-app
   argocd app set my-app --sync-policy automated
   ```

Git revert is preferred because it maintains the audit trail and works with any sync policy.
</details>

## Hands-On Exercise

### Scenario: GitOps for a Multi-Environment Application

Deploy an application to staging and production with ArgoCD, using different configurations per environment.

### Setup

```bash
# Create kind cluster
kind create cluster --name argocd-lab

# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods
kubectl -n argocd wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server --timeout=120s

# Get password
ARGO_PWD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
echo "ArgoCD password: $ARGO_PWD"

# Port forward
kubectl -n argocd port-forward svc/argocd-server 8080:443 &
```

### Create Git Repository Structure

```bash
# Create local directory structure
mkdir -p argocd-lab/{base,overlays/{staging,production},apps}

# Base kustomization
cat > argocd-lab/base/deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo
  template:
    metadata:
      labels:
        app: demo
    spec:
      containers:
        - name: app
          image: nginx:1.25
          ports:
            - containerPort: 80
          resources:
            requests:
              cpu: 10m
              memory: 32Mi
EOF

cat > argocd-lab/base/service.yaml << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: demo-app
spec:
  selector:
    app: demo
  ports:
    - port: 80
EOF

cat > argocd-lab/base/kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
EOF

# Staging overlay
cat > argocd-lab/overlays/staging/kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: staging
namePrefix: staging-
resources:
  - ../../base
patches:
  - patch: |-
      - op: replace
        path: /spec/replicas
        value: 1
    target:
      kind: Deployment
      name: demo-app
EOF

# Production overlay
cat > argocd-lab/overlays/production/kustomization.yaml << 'EOF'
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
        value: 3
    target:
      kind: Deployment
      name: demo-app
EOF
```

### Create ArgoCD Applications

Since we're using local files, we'll apply manifests directly:

```bash
# Create namespaces
kubectl create namespace staging
kubectl create namespace production

# Apply manifests
kubectl apply -k argocd-lab/overlays/staging/
kubectl apply -k argocd-lab/overlays/production/
```

For a real GitOps setup, create Application resources pointing to your Git repo:

```yaml
# apps/staging.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: demo-staging
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/YOUR_ORG/argocd-lab.git
    targetRevision: HEAD
    path: overlays/staging
  destination:
    server: https://kubernetes.default.svc
    namespace: staging
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### Verify Deployment

```bash
# Check staging (1 replica)
kubectl -n staging get pods

# Check production (3 replicas)
kubectl -n production get pods

# Access ArgoCD UI
open https://localhost:8080
# Login: admin / $ARGO_PWD
```

### Success Criteria

- [ ] ArgoCD is running and accessible
- [ ] Can view applications in the UI
- [ ] Staging has 1 replica
- [ ] Production has 3 replicas
- [ ] Understand Application and Kustomize structure

### Cleanup

```bash
kind delete cluster --name argocd-lab
rm -rf argocd-lab
```

## Next Module

Continue to [Module 2.2: Argo Rollouts](module-2.2-argo-rollouts.md) where we'll implement progressive delivery with canary and blue-green deployments.

---

*"The best deployment is the one you don't have to think about. GitOps with ArgoCD makes that possible."*
