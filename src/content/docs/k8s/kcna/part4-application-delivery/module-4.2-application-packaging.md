---
title: "Module 4.2: Application Packaging"
slug: k8s/kcna/part4-application-delivery/module-4.2-application-packaging
sidebar:
  order: 3
---
> **Complexity**: `[MEDIUM]` - Tool concepts
>
> **Time to Complete**: 25-30 minutes
>
> **Prerequisites**: Module 4.1 (CI/CD Fundamentals)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Compare** Helm and Kustomize as Kubernetes application packaging approaches
2. **Explain** Helm chart structure: templates, values, and release lifecycle
3. **Identify** when to use Helm charts vs. Kustomize overlays for different management scenarios
4. **Evaluate** packaging strategies for multi-environment deployments (dev, staging, production)

---

## Why This Module Matters

Raw Kubernetes manifests become hard to manage at scale. **Helm**, **Kustomize**, and other tools help package, configure, and deploy applications. KCNA tests your understanding of these packaging approaches and when to use them.

---

## The Problem with Raw Manifests

```
┌─────────────────────────────────────────────────────────────┐
│              THE MANIFEST PROBLEM                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Managing many YAML files:                                 │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  my-app/                                                   │
│  ├── deployment.yaml                                      │
│  ├── service.yaml                                         │
│  ├── configmap.yaml                                       │
│  ├── secret.yaml                                          │
│  ├── ingress.yaml                                         │
│  └── pvc.yaml                                             │
│                                                             │
│  Problems:                                                 │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  1. DUPLICATION                                           │
│     Same app for dev/staging/prod = 3x files              │
│     Only difference: image tag, replicas, resources       │
│                                                             │
│  2. NO TEMPLATING                                         │
│     Can't parameterize values                              │
│     Hardcoded everywhere                                  │
│                                                             │
│  3. NO VERSIONING                                         │
│     What version is deployed?                             │
│     How to rollback?                                      │
│                                                             │
│  4. NO DEPENDENCIES                                       │
│     App needs Redis → manage separately                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Helm

```
┌─────────────────────────────────────────────────────────────┐
│              HELM                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  "The package manager for Kubernetes"                     │
│  CNCF Graduated project                                   │
│                                                             │
│  Key concepts:                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  CHART                                                     │
│  Package containing Kubernetes resources                  │
│  Templates + values + metadata                            │
│                                                             │
│  RELEASE                                                   │
│  Instance of a chart in a cluster                         │
│  Same chart can have multiple releases                    │
│                                                             │
│  REPOSITORY                                                │
│  Collection of charts (like npm registry)                │
│                                                             │
│  Chart structure:                                         │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  my-app/                                                   │
│  ├── Chart.yaml          # Metadata (name, version)      │
│  ├── values.yaml         # Default values                │
│  ├── templates/                                           │
│  │   ├── deployment.yaml                                 │
│  │   ├── service.yaml                                    │
│  │   └── _helpers.tpl                                   │
│  └── charts/             # Dependencies                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **Pause and predict**: You manage an application deployed to dev, staging, and production. The only differences between environments are the image tag, replica count, and database URL. Without Helm or Kustomize, you would maintain three copies of every YAML file. What problems would this duplication create over time?

### Helm Templating

```
┌─────────────────────────────────────────────────────────────┐
│              HELM TEMPLATING                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Template (templates/deployment.yaml):                    │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  apiVersion: apps/v1                                      │
│  kind: Deployment                                          │
│  metadata:                                                 │
│    name: {{ .Release.Name }}-app                         │
│  spec:                                                     │
│    replicas: {{ .Values.replicas }}                      │
│    template:                                               │
│      spec:                                                 │
│        containers:                                         │
│        - name: app                                        │
│          image: {{ .Values.image.repository }}:{{         │
│                    .Values.image.tag }}                   │
│          resources:                                        │
│            {{- toYaml .Values.resources | nindent 12 }}  │
│                                                             │
│  Values (values.yaml):                                    │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  replicas: 3                                               │
│  image:                                                    │
│    repository: nginx                                      │
│    tag: 1.25                                              │
│  resources:                                                │
│    limits:                                                 │
│      cpu: 100m                                            │
│      memory: 128Mi                                        │
│                                                             │
│  Override values:                                         │
│  ─────────────────────────────────────────────────────────  │
│  helm install my-release ./my-app \                       │
│    --set replicas=5 \                                     │
│    --set image.tag=1.26                                   │
│                                                             │
│  Or use values file:                                      │
│  helm install my-release ./my-app -f prod-values.yaml    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Helm Commands

| Command | Purpose |
|---------|---------|
| `helm install` | Install a chart |
| `helm upgrade` | Upgrade a release |
| `helm rollback` | Rollback to previous version |
| `helm uninstall` | Remove a release |
| `helm list` | List releases |
| `helm repo add` | Add chart repository |
| `helm search` | Search for charts |

---

## Kustomize

```
┌─────────────────────────────────────────────────────────────┐
│              KUSTOMIZE                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  "Kubernetes native configuration management"             │
│  Built into kubectl (kubectl apply -k)                    │
│                                                             │
│  Key difference from Helm:                                │
│  ─────────────────────────────────────────────────────────  │
│  • NO templating                                          │
│  • Uses overlays and patches                              │
│  • Pure Kubernetes YAML                                   │
│                                                             │
│  Structure:                                                │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  my-app/                                                   │
│  ├── base/                    # Common resources          │
│  │   ├── kustomization.yaml                              │
│  │   ├── deployment.yaml                                 │
│  │   └── service.yaml                                    │
│  └── overlays/                                            │
│      ├── dev/                 # Dev-specific             │
│      │   ├── kustomization.yaml                          │
│      │   └── replica-patch.yaml                          │
│      └── prod/                # Prod-specific            │
│          ├── kustomization.yaml                          │
│          └── replica-patch.yaml                          │
│                                                             │
│  How it works:                                            │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Base: The original resources                             │
│  Overlay: Modifications applied on top of base           │
│                                                             │
│        [Base]                                              │
│           │                                                │
│     ┌─────┴─────┐                                         │
│     ▼           ▼                                         │
│  [Overlay:   [Overlay:                                    │
│   Dev]       Prod]                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Kustomize Example

```
┌─────────────────────────────────────────────────────────────┐
│              KUSTOMIZE EXAMPLE                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  base/kustomization.yaml:                                 │
│  ─────────────────────────────────────────────────────────  │
│  apiVersion: kustomize.config.k8s.io/v1beta1             │
│  kind: Kustomization                                      │
│  resources:                                                │
│  - deployment.yaml                                        │
│  - service.yaml                                           │
│                                                             │
│  overlays/prod/kustomization.yaml:                        │
│  ─────────────────────────────────────────────────────────  │
│  apiVersion: kustomize.config.k8s.io/v1beta1             │
│  kind: Kustomization                                      │
│  resources:                                                │
│  - ../../base                                             │
│  namePrefix: prod-                                        │
│  replicas:                                                 │
│  - name: my-app                                           │
│    count: 5                                               │
│  images:                                                   │
│  - name: nginx                                            │
│    newTag: "1.26"                                         │
│                                                             │
│  Apply:                                                   │
│  ─────────────────────────────────────────────────────────  │
│  kubectl apply -k overlays/prod/                         │
│                                                             │
│  Kustomize features:                                      │
│  • namePrefix/nameSuffix: Add prefix to all names        │
│  • namespace: Set namespace for all resources            │
│  • images: Override image tags                           │
│  • replicas: Override replica counts                     │
│  • patches: Modify any field                             │
│  • configMapGenerator: Create ConfigMaps from files      │
│  • secretGenerator: Create Secrets from files            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Helm vs Kustomize

```
┌─────────────────────────────────────────────────────────────┐
│              HELM vs KUSTOMIZE                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  HELM:                                                     │
│  ─────────────────────────────────────────────────────────  │
│  + Powerful templating                                    │
│  + Package versioning                                     │
│  + Dependency management                                  │
│  + Large ecosystem (Artifact Hub)                        │
│  + Release tracking                                       │
│  - Complex template syntax                                │
│  - Must learn Go templating                              │
│                                                             │
│  KUSTOMIZE:                                               │
│  ─────────────────────────────────────────────────────────  │
│  + No templating = pure YAML                             │
│  + Built into kubectl                                     │
│  + Easy to understand                                     │
│  + No new syntax to learn                                 │
│  - Limited compared to templating                        │
│  - No package versioning                                 │
│  - No dependency management                               │
│                                                             │
│  When to use what:                                        │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Helm:                                                     │
│  • Distributing apps to others                           │
│  • Complex templating needs                              │
│  • Need dependency management                             │
│  • Using third-party charts                              │
│                                                             │
│  Kustomize:                                               │
│  • Internal apps with environment variations             │
│  • Simple overlays (dev/staging/prod)                    │
│  • Teams unfamiliar with templating                      │
│  • GitOps workflows                                       │
│                                                             │
│  Both together:                                            │
│  • Helm for base chart                                    │
│  • Kustomize for environment overlays                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Stop and think**: Helm uses Go templating to generate YAML, while Kustomize uses overlays on plain YAML without any templating. Which approach would be easier for a team that has never used either tool? Which would be more powerful for distributing an application to external users who need to customize many settings?

## Other Packaging Tools

```
┌─────────────────────────────────────────────────────────────┐
│              OTHER TOOLS                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  JSONNET / TANKA                                          │
│  ─────────────────────────────────────────────────────────  │
│  • Data templating language                               │
│  • Generate JSON/YAML programmatically                   │
│  • Used by Grafana Labs                                   │
│                                                             │
│  CUE                                                      │
│  ─────────────────────────────────────────────────────────  │
│  • Configuration language                                 │
│  • Strong typing and validation                          │
│  • Merge-able configurations                             │
│                                                             │
│  CARVEL (formerly k14s)                                   │
│  ─────────────────────────────────────────────────────────  │
│  • ytt: YAML templating                                  │
│  • kbld: Image building/resolving                        │
│  • kapp: Deployment tool                                 │
│  • CNCF sandbox project                                  │
│                                                             │
│  OPERATORS                                                │
│  ─────────────────────────────────────────────────────────  │
│  • For complex stateful apps                             │
│  • Custom controllers                                    │
│  • Beyond simple packaging                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Artifact Hub

```
┌─────────────────────────────────────────────────────────────┐
│              ARTIFACT HUB                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  artifacthub.io                                           │
│  CNCF project                                              │
│                                                             │
│  Central repository for:                                  │
│  ─────────────────────────────────────────────────────────  │
│  • Helm charts                                            │
│  • OPA policies                                           │
│  • Falco rules                                            │
│  • OLM operators                                          │
│  • And more...                                            │
│                                                             │
│  Use it to:                                               │
│  • Find charts for popular applications                  │
│  • Discover alternatives                                  │
│  • Check chart quality/security                          │
│                                                             │
│  Example: Need PostgreSQL?                                │
│  → Search "postgresql" on Artifact Hub                   │
│  → Find Bitnami chart                                    │
│  → helm repo add bitnami https://charts.bitnami.com/...  │
│  → helm install my-postgres bitnami/postgresql          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Did You Know?

- **Helm v3 removed Tiller** - Helm v2 required a server component (Tiller) in the cluster. Helm v3 removed it for better security.

- **Kustomize is built into kubectl** - Since Kubernetes 1.14, you can use `kubectl apply -k` without installing Kustomize separately.

- **Helm uses Go templates** - If you know Go's text/template package, you'll find Helm templating familiar.

- **Charts can have dependencies** - A chart can depend on other charts, automatically installed together (like npm packages).

---

## Common Mistakes

| Mistake | Why It Hurts | Correct Understanding |
|---------|--------------|----------------------|
| Duplicating manifests for envs | Hard to maintain | Use Helm values or Kustomize overlays |
| Complex Helm templates | Hard to debug | Keep templates simple |
| Not versioning charts | Can't track changes | Use semantic versioning |
| Hardcoded secrets | Security risk | Use external secret management |

---

## Quiz

1. **A new hire asks why the company uses Helm instead of applying raw YAML manifests with `kubectl apply`. The application has 8 Kubernetes resources and is deployed to 4 environments. What would you explain about the problems Helm solves?**
   <details>
   <summary>Answer</summary>
   With raw YAML across 4 environments, you would maintain 32 files (8 resources x 4 environments) where most content is duplicated. A change to the Deployment spec requires editing 4 files. Helm solves this with templates and values: one set of templates with a `values.yaml` per environment. Changes to shared structure happen in one place. Helm also provides versioning (track which version is deployed), rollback (revert to a previous release), dependency management (automatically install Redis when your app needs it), and the Artifact Hub ecosystem for finding pre-built charts for common applications.
   </details>

2. **Your team uses Kustomize with a base directory and overlays for dev, staging, and production. A developer wants to change the container image tag to `v2.0` only in production. How would they do this in Kustomize without modifying the base YAML?**
   <details>
   <summary>Answer</summary>
   In the production overlay's `kustomization.yaml`, add an `images` field that overrides the image tag. Kustomize patches the base resources without modifying them. The base still uses the default tag, and each overlay can specify its own. This is Kustomize's core philosophy: overlays modify base resources without templating. The production overlay might include `images: [{name: myapp, newTag: "v2.0"}]`. When you run `kubectl apply -k overlays/prod/`, Kustomize generates the final YAML with the production image tag merged into the base Deployment.
   </details>

3. **You install a PostgreSQL Helm chart from Bitnami with `helm install my-db bitnami/postgresql`. A month later, Bitnami releases a security patch for the chart. How do you upgrade, and what happens if the upgrade breaks your database?**
   <details>
   <summary>Answer</summary>
   First update the chart repository with `helm repo update`, then upgrade with `helm upgrade my-db bitnami/postgresql`. Helm tracks the release history, so each upgrade creates a new revision. If the upgrade breaks the database, run `helm rollback my-db` to revert to the previous working revision. Helm stores the complete state of each release, making rollback straightforward. Before upgrading, review the chart's changelog for breaking changes and test in a non-production environment. The release concept is one of Helm's key advantages over raw manifests.
   </details>

4. **A platform team wants to provide a standardized application template to 10 development teams. The template includes a Deployment, Service, ConfigMap, and Ingress. Teams need to customize the image, replica count, and domain name. Should they use Helm or Kustomize for this use case?**
   <details>
   <summary>Answer</summary>
   Helm is the better choice for distributing to multiple teams. Helm charts are self-contained packages that can be versioned and published to a chart repository (or Artifact Hub). Teams install the chart with their own values file without needing to understand the templates. The platform team controls the structure (templates), while each team provides their customizations (values). Kustomize would require each team to maintain their own overlay directory and understand the base structure. Helm's templating, versioning, and dependency management make it the standard for distributing reusable Kubernetes configurations.
   </details>

5. **A colleague is debugging a Helm deployment and finds that the generated YAML has unexpected values. They cannot tell what the template will produce just by reading it because of Go templating syntax. What Helm command would help them see the final YAML without deploying it, and what does this suggest about the trade-off between Helm and Kustomize?**
   <details>
   <summary>Answer</summary>
   Run `helm template my-release ./my-chart -f values.yaml` to render the templates locally without deploying, or `helm install --dry-run --debug` to simulate the install. This reveals the exact YAML that would be applied. This highlights Helm's key trade-off: Go templating is powerful but can be hard to read and debug -- conditions, loops, and helper functions make templates complex. Kustomize avoids this entirely by working with plain YAML and overlays, making the output more predictable. For teams that find Go templating confusing, Kustomize's simplicity is a real advantage, even though it lacks Helm's power.
   </details>

---

## Summary

**The problem**:
- Raw manifests don't scale
- Duplication, no parameterization
- No versioning or dependencies

**Helm**:
- Package manager for Kubernetes
- Templates + values + charts
- Powerful but complex

**Kustomize**:
- Overlays and patches
- No templating
- Built into kubectl

**When to use**:
- **Helm**: Distributing apps, complex templating, dependencies
- **Kustomize**: Internal apps, simple environment overlays
- **Both**: Helm chart + Kustomize overlays

**Artifact Hub**:
- Find Helm charts and other artifacts
- Central CNCF repository

---

## KCNA Curriculum Complete!

Congratulations! You've completed the entire KCNA curriculum covering:

| Part | Topic | Weight |
|------|-------|--------|
| Part 1 | Kubernetes Fundamentals | 44% |
| Part 2 | Container Orchestration | 28% |
| Part 3 | Cloud Native Architecture (incl. Observability) | 12% |
| Part 4 | Application Delivery | 16% |

*Updated November 2025: Observability merged into Cloud Native Architecture*

**Next steps**:
1. Review weak areas
2. Take practice quizzes
3. Study CNCF landscape
4. Schedule your exam!

Good luck on your KCNA certification!
