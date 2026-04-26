---
title: "Module 2.3: Flux"
slug: platform/toolkits/cicd-delivery/gitops-deployments/module-2.3-flux
sidebar:
  order: 4
---
> **Toolkit Track** | Complexity: `[COMPLEX]` | Time: 40-45 min

## Prerequisites

Before starting this module, you should be comfortable reading Kubernetes manifests, following a basic Git workflow, and explaining why a cluster should converge from declared state rather than from manual shell history.

You should complete [Module 2.1: ArgoCD](../module-2.1-argocd/) first because this module compares Flux against ArgoCD's application-centered model rather than reteaching GitOps from the beginning.

You should also review [GitOps Discipline](/platform/disciplines/delivery-automation/gitops/) if the terms desired state, reconciliation, drift, and pull-based delivery are still new or fuzzy.

All Kubernetes examples assume Kubernetes 1.35+ and the Flux v2 GitOps Toolkit model.

The command examples first use `kubectl` explicitly, then define `alias k=kubectl`; after that point, `k` means `kubectl`.

## Learning Outcomes

After completing this module, you will be able to:

- **Design** a Flux repository and controller layout that separates sources, infrastructure, applications, and cluster-specific overlays without hiding ownership boundaries.
- **Implement** GitRepository, Kustomization, HelmRepository, and HelmRelease resources that reconcile in a predictable order with health checks and pruning.
- **Debug** failed Flux reconciliations by reading conditions, controller logs, dependency status, source artifacts, and Kubernetes events instead of guessing from symptoms.
- **Evaluate** when Flux's controller toolkit is a better operating model than ArgoCD's application-centered interface for multi-cluster platform teams.
- **Design** image automation and notification flows that preserve Git as the audit trail while still giving teams fast promotion feedback.

## Why This Module Matters

At 03:05, a platform engineer watches the deployment board turn red across one region. The application code was already tested, the image existed in the registry, and the Git change looked small: one version bump and one environment variable addition. The cluster did exactly what it had been told to do, but nobody had modeled what should happen when a required cluster substitution was missing, a dependency was only applied rather than healthy, and the rollout notification path only reported success.

Flux matters because incidents like that are rarely caused by one broken command. They happen when teams treat GitOps as a synchronization trick instead of an operating model. Flux gives each part of the model a Kubernetes API object: one object describes where configuration comes from, another describes how manifests are applied, another manages Helm releases, another scans image tags, and another sends reconciliation events. That design is powerful because it makes the delivery system inspectable through Kubernetes itself.

Flux also raises the engineering bar. A team cannot hide behind a friendly deployment button and call that governance. They must decide what counts as ready, how dependencies are ordered, which branches are allowed to change production, how image automation writes back to Git, and what signal should wake a human when reconciliation fails. This module teaches Flux from beginner to senior level by starting with the controller loop, then layering sources, workload reconciliation, Helm, image automation, multi-cluster patterns, and incident debugging.

## Read Flux as a Reconciliation System

Flux is the GitOps Toolkit, which means it is not one application that owns every deployment concept. It is a set of Kubernetes controllers that cooperate through custom resources. This is the first mental shift: when you operate Flux, you are not mainly clicking a release button; you are designing a graph of resources that controllers continuously reconcile.

A controller watches a resource, compares desired state to observed state, performs work, and writes status back to the Kubernetes API. Flux uses that same Kubernetes-native pattern for delivery. The source-controller fetches artifacts, the kustomize-controller applies Kustomize trees, the helm-controller manages Helm releases, the notification-controller sends events, and the image controllers connect registry changes back to Git.

That separation gives Flux a composable shape. You can install only the controllers you need, scale or shard controllers independently, and reason about failures at the boundary where they happen. A Git authentication problem is usually a Source problem. A failed Deployment readiness check is usually a Kustomization problem. A chart render failure is usually a HelmRelease problem. The practical skill is learning to map symptoms to the controller that owns the contract.

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                            FLUX CONTROL LOOP                               │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Git / Helm / OCI source                                                    │
│  ┌──────────────────────────────┐                                          │
│  │ desired delivery state        │                                          │
│  │ manifests, charts, values     │                                          │
│  └───────────────┬──────────────┘                                          │
│                  │ source-controller fetches artifact                       │
│                  ▼                                                          │
│  Kubernetes API objects                                                     │
│  ┌──────────────────────────────┐                                          │
│  │ GitRepository                 │                                          │
│  │ HelmRepository                │                                          │
│  │ OCIRepository                 │                                          │
│  └───────────────┬──────────────┘                                          │
│                  │ kustomize-controller or helm-controller consumes source  │
│                  ▼                                                          │
│  Workload state in the cluster                                              │
│  ┌──────────────────────────────┐                                          │
│  │ Namespace, Deployment,        │                                          │
│  │ Service, CRDs, Helm release   │                                          │
│  └───────────────┬──────────────┘                                          │
│                  │ status, events, conditions                               │
│                  ▼                                                          │
│  Operator feedback                                                          │
│  ┌──────────────────────────────┐                                          │
│  │ flux get, flux logs, alerts   │                                          │
│  │ Git commit status, Slack      │                                          │
│  └──────────────────────────────┘                                          │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

The diagram shows why Flux feels different from a traditional deployment tool. A pipeline may push a command into a cluster and then exit. Flux leaves a set of controllers inside the cluster, and those controllers keep checking whether the cluster still matches the declared source. That makes drift visible and recoverable, but it also means bad desired state can be faithfully applied until you fix Git.

The smallest useful Flux system has a source and a reconciler. The source tells Flux where to fetch content. The reconciler tells Flux which path or chart to apply from that content. If you remember only one beginner-level rule, remember this: Source objects fetch artifacts; Kustomization and HelmRelease objects consume those artifacts.

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                         FLUX ARCHITECTURE                                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  GIT REPOSITORY                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ fleet-infra/                                                       │    │
│  │ ├── clusters/                                                      │    │
│  │ │   ├── production/                                                │    │
│  │ │   │   ├── flux-system/       Flux bootstrap and self-management  │    │
│  │ │   │   └── apps.yaml          Entry point for production apps     │    │
│  │ │   └── staging/                                                   │    │
│  │ ├── infrastructure/                                                │    │
│  │ │   ├── base/                 Shared platform components           │    │
│  │ │   └── production/           Environment-specific overlays        │    │
│  │ └── apps/                                                          │    │
│  │     ├── base/                 Reusable app manifests               │    │
│  │     └── production/           Production overlays                  │    │
│  └───────────────────────────────┬────────────────────────────────────┘    │
│                                  │                                          │
│                                  ▼                                          │
│  FLUX CONTROLLERS IN THE CLUSTER                                            │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ ┌────────────────┐  ┌────────────────┐  ┌──────────────────────┐  │    │
│  │ │ Source         │  │ Kustomize      │  │ Helm                 │  │    │
│  │ │ Controller     │  │ Controller     │  │ Controller           │  │    │
│  │ │ fetches Git,   │  │ applies paths, │  │ installs and         │  │    │
│  │ │ Helm, OCI, S3  │  │ waits, prunes  │  │ upgrades charts      │  │    │
│  │ └───────┬────────┘  └───────┬────────┘  └──────────┬───────────┘  │    │
│  │         │                   │                      │              │    │
│  │ ┌───────▼────────┐  ┌───────▼────────┐  ┌──────────▼───────────┐  │    │
│  │ │ Notification   │  │ Image          │  │ Image Automation     │  │    │
│  │ │ Controller     │  │ Reflector      │  │ Controller           │  │    │
│  │ │ sends events   │  │ scans tags     │  │ commits image edits  │  │    │
│  │ └────────────────┘  └────────────────┘  └──────────────────────┘  │    │
│  └────────────────────────────────┬───────────────────────────────────┘    │
│                                   │                                         │
│                                   ▼                                         │
│  KUBERNETES CLUSTER STATE                                                  │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ Namespaces, Deployments, Services, CRDs, Helm releases, ConfigMaps │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

| Controller | Primary CRDs | Operational contract |
|------------|--------------|----------------------|
| source-controller | GitRepository, HelmRepository, OCIRepository, Bucket | Fetches external artifacts and publishes artifact status for other controllers. |
| kustomize-controller | Kustomization | Builds and applies manifest trees, prunes removed resources, waits for health, and orders dependencies. |
| helm-controller | HelmRelease | Renders charts, manages Helm install and upgrade lifecycle, and records release failures in status. |
| notification-controller | Provider, Alert, Receiver | Sends Flux events to systems such as Slack, Microsoft Teams, GitHub, and incident tools. |
| image-reflector-controller | ImageRepository, ImagePolicy | Scans registries and selects image tags according to semver, alphabetical, or numerical policy. |
| image-automation-controller | ImageUpdateAutomation | Writes selected image tags back to Git so deployment changes remain auditable. |

**Pause and predict:** if the source-controller cannot authenticate to Git, which downstream Flux resources should you expect to fail first: the Kustomization, the HelmRelease, or the Kubernetes Deployment? The best answer is that the source object becomes not ready first, then consumers that depend on that artifact report source-related failures; the Deployment may never change because Flux never gets a valid artifact to apply.

Flux status is stored in conditions, not hidden in a proprietary database. A healthy resource usually has a Ready condition with a useful message. A failing resource often has enough detail to tell you whether the problem is authentication, artifact fetch, manifest build, dependency readiness, chart rendering, apply failure, or workload health.

A senior operator reads Flux by following ownership boundaries. They do not start by restarting every controller. They ask which contract failed. Did the source produce an artifact? Did the reconciler consume the right path? Did the apply succeed? Did health checks prove the workload is ready? Did notification routes report the failure to the right audience?

The Flux CLI is a convenience wrapper around Kubernetes resources. It makes common status views easier to read, but you can always fall back to `kubectl get`, `kubectl describe`, and controller logs. This matters during incidents because you may not have the exact Flux CLI version on a jump host, while Kubernetes status and events are still available.

```bash
kubectl get ns flux-system
alias k=kubectl

flux check
flux get all
k get gitrepositories,kustomizations,helmreleases -A
k describe kustomization -n flux-system
```

The first command verifies the namespace exists. The alias line defines `k` for the rest of this module. `flux check` tests whether the installed controllers and Kubernetes API are reachable. `flux get all` gives a concise inventory, while `k describe` exposes raw conditions and events when the concise view hides too much detail.

When comparing Flux to ArgoCD, avoid the simplistic answer that one is modern and the other is old. Both are mature CNCF projects. The meaningful comparison is operating model. ArgoCD makes Applications highly visible through a UI and API. Flux makes delivery primitives first-class Kubernetes resources that platform teams can compose, template, secure, and monitor like the rest of the cluster.

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                           FLUX vs ARGOCD                                   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  FLUX                                           ARGOCD                      │
│  ────                                           ──────                      │
│                                                                            │
│  Architecture:                                  Architecture:               │
│  Controller toolkit                             Application platform        │
│  Independent CRDs                               Central API and UI          │
│  Kubernetes-native status                       Application-first status    │
│                                                                            │
│  Strengths:                                     Strengths:                  │
│  Composable automation                          Strong visual diff          │
│  Built-in image automation                      Friendly onboarding UI      │
│  OCI and Kustomize workflows                    Mature app self-service     │
│  Fits platform-as-code                          Rich RBAC and SSO patterns  │
│                                                                            │
│  Best fit:                                      Best fit:                   │
│  Platform teams building paved roads            App teams needing UI        │
│  Many clusters with Git-owned config            Central app visibility      │
│  Operators comfortable with kubectl             Mixed delivery maturity     │
│                                                                            │
│  Decision cue:                                  Decision cue:               │
│  "Everything is a Kubernetes resource."          "Applications are visible." │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

| Decision pressure | Flux tends to fit when | ArgoCD tends to fit when |
|-------------------|------------------------|--------------------------|
| Operator workflow | Platform engineers prefer Kubernetes APIs, Git review, and controller composition. | App teams need a central UI for sync, diff, rollback, and ownership visibility. |
| Multi-cluster scale | Each cluster can self-reconcile from a shared fleet repository with cluster overlays. | A central control plane can register clusters and render ApplicationSet instances. |
| Image promotion | Teams want automation to commit image tags back to Git with policy-based selection. | Teams already promote through external pipelines or want manual UI gates. |
| Extensibility | The delivery system should look like Kubernetes primitives that can be composed by other controllers. | The delivery system should expose a product-like application abstraction. |

The decision is not permanent for every organization. Some teams run Flux for platform infrastructure and ArgoCD for developer-facing applications. That split can work if ownership is clear. It fails when two tools believe they own the same resources, because each controller will try to reconcile away the other controller's changes.

A useful rule for senior design reviews is to ask, "Where is the source of truth for this object, and which controller is allowed to change it?" If the answer is ambiguous, the design is not ready. GitOps gives you an audit trail only when ownership is narrow enough that a reviewer can understand why a change will happen.

## Bootstrap Sources Before You Reconcile Workloads

Bootstrapping Flux installs the controllers and creates the initial GitRepository and Kustomization that allow Flux to manage itself. This is why Flux bootstrap is more than an installer. It creates a self-referential loop where the cluster watches the repository path that contains the Flux components and sync configuration.

A beginner often sees bootstrap as a one-time command and then forgets the repository structure it created. A senior operator treats bootstrap output as production configuration. The path you choose becomes the cluster's entry point. The branch becomes part of the deployment trust boundary. The Git provider credential becomes an identity that can change cluster state.

```bash
flux check --pre

flux bootstrap github \
  --owner=my-org \
  --repository=fleet-infra \
  --branch=main \
  --path=./clusters/prod-us-east \
  --personal
```

This command validates prerequisites, creates or updates a GitHub repository path, installs Flux controllers, and commits manifests that point the cluster at `./clusters/prod-us-east`. In a real production setup, prefer a deploy key or tightly scoped machine identity rather than a broad personal token. The principle is simple: the identity that can write the fleet repository can indirectly change clusters.

The bootstrap result should look boring, because boring is good for an entry point. You want a small `flux-system` directory that contains the Flux components and sync definition, then separate files that point toward infrastructure and application layers. Do not bury every app under `flux-system`; that path should remain the control plane seed, not the whole operating model.

```text
fleet-infra/
└── clusters/
    └── prod-us-east/
        ├── flux-system/
        │   ├── gotk-components.yaml
        │   ├── gotk-sync.yaml
        │   └── kustomization.yaml
        ├── infrastructure.yaml
        └── apps.yaml
```

A GitRepository source tells Flux how to fetch content. It does not apply that content by itself. This is a common early misunderstanding, and it causes many "Flux did nothing" debugging sessions. If only a source exists, Flux may successfully fetch the artifact while no workload changes occur because no Kustomization or HelmRelease consumes it.

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: fleet-infra
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/my-org/fleet-infra.git
  ref:
    branch: main
  ignore: |
    /*
    !/clusters
    !/infrastructure
    !/apps
```

The `interval` controls how often Flux checks the source. A one-minute interval is reasonable for a frequently changed fleet repository, but it should not become a reflex for every source. A chart repository that changes rarely may use a longer interval. A source for emergency patches may use a shorter interval with strict review controls.

The `ignore` block is a performance and ownership tool. It tells Flux which parts of a repository belong to this source artifact. That matters when a monorepo contains CI config, documentation, app source code, and deployment manifests. Fetching less content reduces work and makes the source contract easier to review.

For private repositories, Flux needs credentials stored in a Kubernetes Secret. The exact secret format depends on HTTPS username/password, token, or SSH identity. The important operating rule is that source credentials are part of your cluster security boundary. If a cluster can fetch a private repo, compromise of that cluster may expose read credentials for that repo.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: fleet-infra-auth
  namespace: flux-system
type: Opaque
stringData:
  username: flux-bot
  password: REPLACE_WITH_TOKEN
---
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: private-fleet-infra
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/my-org/private-fleet-infra.git
  ref:
    branch: main
  secretRef:
    name: fleet-infra-auth
```

Use `stringData` when writing examples or manually applying secrets because Kubernetes encodes values for you. In production, use your secret management pattern rather than committing raw secrets. Sealed Secrets, External Secrets, cloud workload identity, or SOPS-backed Flux decryption may be appropriate depending on your platform.

Flux also supports HelmRepository and OCIRepository sources. HelmRepository is useful when a HelmRelease installs a chart from a chart repository. OCIRepository is useful when you package manifests or charts as OCI artifacts. The distinction matters because the source-controller produces an artifact in each case, while the consuming controller decides what to do with it.

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
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: OCIRepository
metadata:
  name: platform-manifests
  namespace: flux-system
spec:
  interval: 5m
  url: oci://ghcr.io/my-org/platform-manifests
  ref:
    tag: prod
```

**Stop and think:** your GitRepository reports Ready, but no Deployment appears in the target namespace. Before changing YAML, what should you inspect? You should look for a Kustomization or HelmRelease that references the source, verify its `path` or chart reference, then read its status conditions to see whether the artifact was consumed.

A clean repository structure reduces accidental coupling. The following layout separates cluster entry points from shared infrastructure and app overlays. The cluster directories contain small Kustomization resources that point outward. Shared directories contain reusable declarations. Environment overlays contain the differences that reviewers should inspect carefully.

```text
fleet-infra/
├── clusters/
│   ├── production/
│   │   ├── flux-system/
│   │   │   └── gotk-sync.yaml
│   │   ├── infrastructure.yaml
│   │   └── apps.yaml
│   ├── staging/
│   │   ├── flux-system/
│   │   │   └── gotk-sync.yaml
│   │   ├── infrastructure.yaml
│   │   └── apps.yaml
│   └── development/
│       ├── flux-system/
│       │   └── gotk-sync.yaml
│       ├── infrastructure.yaml
│       └── apps.yaml
├── infrastructure/
│   ├── base/
│   ├── production/
│   ├── staging/
│   └── development/
└── apps/
    ├── podinfo/
    │   ├── base/
    │   ├── production/
    │   ├── staging/
    │   └── development/
    └── payments/
        ├── base/
        ├── production/
        └── staging/
```

This structure is not the only valid layout, but it teaches the desired separation. Clusters decide what they consume. Infrastructure and applications define reusable content. Environment overlays express controlled variation. Reviewers can ask whether a pull request changes a shared base, a production overlay, or a single cluster entry point.

A bad repository layout hides blast radius. If a single file under `clusters/production` contains every app, every infrastructure component, and every environment-specific value, reviewers cannot tell whether a change affects one service or the whole platform. Flux will still reconcile it, but the human review process becomes weaker.

A good bootstrap design also accounts for branch and path promotion. Some organizations reconcile production directly from `main` and use pull request review as the gate. Others reconcile staging from `main` and production from a protected release branch. Flux can support either pattern, but the chosen pattern must match how the organization reviews, audits, and rolls back changes.

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: production-apps
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: fleet-infra
  path: ./apps/production
  prune: true
  wait: true
  timeout: 5m
```

This resource is the first complete source-to-apply bridge. It says, "from the `fleet-infra` artifact, build and apply `./apps/production`, delete objects removed from Git, wait for readiness, and fail if readiness does not happen within five minutes." Each field represents an operational decision, not just syntax.

The `prune` setting deserves special attention. Without pruning, deleting a manifest from Git may not delete the Kubernetes object. That can leave old Deployments, ConfigMaps, Roles, or test resources running long after the repository says they are gone. With pruning enabled, Git removal becomes cluster removal, so reviewers must treat deletion as a production action.

The `wait` and `timeout` settings turn apply success into rollout feedback. Apply success only means the Kubernetes API accepted objects. Readiness means the objects reached useful operational state according to their type and configured health checks. For production dependencies, you usually want wait behavior because ordering without readiness is false confidence.

## Apply Workloads Safely with Kustomization and HelmRelease

Kustomization is the Flux resource that applies plain manifests or Kustomize overlays from a source artifact. It is the workhorse for platform infrastructure and application manifests. The key design decision is not whether Kustomize is fashionable; it is whether each Kustomization represents a coherent unit of ownership and readiness.

A small Kustomization is easier to debug but may create too many dependency edges. A huge Kustomization is easy to create but difficult to reason about during failure. The practical middle ground is to group resources that should be applied, waited on, and rolled back together. Cert-manager may be one unit. Ingress controllers may be another. A service and its namespace, config, deployment, service, and ingress may be another.

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: cert-manager
  namespace: flux-system
spec:
  interval: 10m
  retryInterval: 1m
  sourceRef:
    kind: GitRepository
    name: fleet-infra
  path: ./infrastructure/production/cert-manager
  prune: true
  wait: true
  timeout: 5m
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: cert-manager
      namespace: cert-manager
    - apiVersion: apps/v1
      kind: Deployment
      name: cert-manager-cainjector
      namespace: cert-manager
    - apiVersion: apps/v1
      kind: Deployment
      name: cert-manager-webhook
      namespace: cert-manager
```

This example treats cert-manager as a dependency whose readiness matters. The `healthChecks` list makes the dependency concrete. If the webhook Deployment is not healthy, dependent Kustomizations should not continue as if certificate resources are safe to apply. This is how Flux turns a deployment graph into an operational graph.

Dependencies are declared with `dependsOn`. They should describe real readiness requirements, not just a preferred visual order. If an app requires ingress classes, certificate issuers, or CRDs, use dependencies. If two apps are independent, avoid unnecessary dependencies because they serialize delivery and create larger failure domains.

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: ingress
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: fleet-infra
  path: ./infrastructure/production/ingress
  prune: true
  wait: true
  timeout: 5m
  dependsOn:
    - name: cert-manager
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: apps
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: fleet-infra
  path: ./apps/production
  prune: true
  wait: true
  timeout: 8m
  dependsOn:
    - name: ingress
```

The sequence now has meaning. Cert-manager must be healthy before ingress reconciles. Ingress must be healthy before applications reconcile. If the apps Kustomization is blocked, the status message should point at the not-ready dependency rather than leaving the operator to infer ordering from timestamps.

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                       DEPENDENCY-BASED RECONCILIATION                      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  cert-manager Kustomization                                                │
│  ┌──────────────────────────────┐                                          │
│  │ Apply CRDs and controllers    │                                          │
│  │ Wait for three Deployments    │                                          │
│  │ Ready=True                    │                                          │
│  └───────────────┬──────────────┘                                          │
│                  │ dependsOn satisfied                                      │
│                  ▼                                                          │
│  ingress Kustomization                                                     │
│  ┌──────────────────────────────┐                                          │
│  │ Apply ingress controller      │                                          │
│  │ Wait for controller pods      │                                          │
│  │ Ready=True                    │                                          │
│  └───────────────┬──────────────┘                                          │
│                  │ dependsOn satisfied                                      │
│                  ▼                                                          │
│  apps Kustomization                                                        │
│  ┌──────────────────────────────┐                                          │
│  │ Apply application manifests   │                                          │
│  │ Wait for workload health      │                                          │
│  │ Ready=True or failure status  │                                          │
│  └──────────────────────────────┘                                          │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

Post-build substitution is useful when a shared manifest needs cluster-specific values. It is also dangerous when teams treat substitution as casual templating without validation. A missing substitution can produce invalid manifests, unexpected defaults, or reconciliation failures that only appear when a rarely touched cluster receives a change.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-config
  namespace: flux-system
data:
  CLUSTER_NAME: prod-us-east
  ENVIRONMENT: production
  DOMAIN: api.example.com
  REPLICAS: "5"
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: api
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: fleet-infra
  path: ./apps/api/production
  prune: true
  wait: true
  timeout: 5m
  postBuild:
    substituteFrom:
      - kind: ConfigMap
        name: cluster-config
        optional: false
```

Setting `optional: false` tells Flux that the ConfigMap is required. This is a small field with a large incident-prevention effect. If a new cluster is missing `cluster-config`, the Kustomization should fail loudly during reconciliation rather than silently rendering an unsafe default or leaving unresolved placeholders for a later failure.

**Worked example:** imagine the API manifest contains `replicas: ${REPLICAS}` and `--domain=${DOMAIN}`. A new APAC cluster is bootstrapped, but the `cluster-config` ConfigMap is not applied. Without a required substitution source and health checks, the cluster may appear quiet until the next app rollout touches that manifest. With `optional: false`, `wait: true`, and explicit Deployment health checks, Flux reports the missing input during reconciliation before traffic depends on the rollout.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: production
spec:
  replicas: ${REPLICAS}
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
        - name: api
          image: ghcr.io/my-org/api-gateway:v1.8.0
          args:
            - "--domain=${DOMAIN}"
          ports:
            - containerPort: 8080
```

A reviewer should flag this Deployment if no required substitution source is visible in the same change set. The manifest is valid as a template, but it is not safe as a production declaration unless the cluster supplies the values. The senior habit is to review the whole reconciliation path, not only the manifest that changed.

**Pause and predict:** if `optional: false` is set and the ConfigMap is missing, should Flux apply a partially rendered Deployment and then mark it unhealthy, or should reconciliation fail before applying that rendered object? The safer expectation is that the Kustomization fails during build or substitution, preventing a bad rendered manifest from becoming cluster state.

HelmRelease is the Flux resource for Helm charts. Use it when a component is primarily distributed and upgraded as a Helm chart, or when chart lifecycle semantics are useful. Avoid wrapping every simple internal app in Helm just because Helm exists. If a Kustomize overlay is clearer and easier to review, Flux does not require Helm.

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
      version: "15.x"
      sourceRef:
        kind: HelmRepository
        name: bitnami
        namespace: flux-system
      interval: 1h
  values:
    replicaCount: 3
    service:
      type: ClusterIP
```

A HelmRelease consumes a HelmRepository source. The chart version range controls which chart versions are eligible. The values block controls chart configuration. For production, pinning exact chart versions may be safer than broad semver ranges because chart upgrades can change rendered resources even when your Git values do not change.

Values can also come from ConfigMaps or Secrets. This is useful when one platform team owns the HelmRelease and another process supplies environment-specific values. The risk is that values become scattered, so status and review discipline matter. A HelmRelease with three external values sources may be flexible, but it also increases debugging work.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-values
  namespace: web
data:
  values.yaml: |
    replicaCount: 2
    service:
      type: ClusterIP
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
---
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
      version: "15.10.2"
      sourceRef:
        kind: HelmRepository
        name: bitnami
        namespace: flux-system
  valuesFrom:
    - kind: ConfigMap
      name: nginx-values
      valuesKey: values.yaml
```

Helm dependencies can be modeled with `dependsOn` too. This is common when one chart expects a database, operator, or CRD provider to exist first. The same caution applies: only express true readiness dependencies. A dependency that only exists to make logs look tidy can slow recovery when an unrelated component fails.

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: wordpress
  namespace: blog
spec:
  interval: 10m
  dependsOn:
    - name: mysql
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

Flux can also install a chart from Git by pointing the chart spec at a path inside a GitRepository source. This pattern is useful for internal charts that live next to app manifests. It keeps chart changes and environment overlays reviewable in the same repository, but it also means chart authors must treat chart templates as production delivery code.

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: internal-api
  namespace: production
spec:
  interval: 10m
  chart:
    spec:
      chart: ./charts/internal-api
      sourceRef:
        kind: GitRepository
        name: fleet-infra
        namespace: flux-system
  values:
    image:
      repository: ghcr.io/my-org/internal-api
      tag: v2.4.1
```

The most common Kustomization and HelmRelease failures are not mysterious. The source artifact may not exist. The path may be wrong. Kustomize may fail to build. Helm may fail to render. Kubernetes may reject an object. A workload may fail readiness. The operator's job is to identify which step failed and stop mixing symptoms from different layers.

```bash
flux get sources git
flux get kustomizations
flux get helmreleases
flux get kustomization apps -o wide
k describe kustomization apps -n flux-system
flux logs --kind=Kustomization --name=apps --namespace=flux-system
```

Read these commands from top to bottom. First confirm the source. Then confirm the reconciler. Then inspect detailed status. Then read events. Then read controller logs. This sequence prevents a common anti-pattern where operators tail every log in the namespace before checking the one status condition that already explains the failure.

When a reconciliation is fixed in Git, you can wait for the interval or request an immediate reconciliation. `--with-source` tells Flux to refresh the source artifact first, which is often what you want after pushing a corrective commit. Use forced reconciliation as a diagnostic and recovery tool, not as the normal deployment mechanism.

```bash
flux reconcile source git fleet-infra
flux reconcile kustomization apps --with-source
flux reconcile helmrelease nginx --namespace=web
```

Suspension is another operational tool. It tells Flux to stop reconciling a resource while you investigate or perform a controlled manual action. The danger is forgetting to resume. Treat suspension like a maintenance mode that requires a ticket, alert, or explicit handoff.

```bash
flux suspend kustomization apps
k scale deployment api-gateway -n production --replicas=2
flux resume kustomization apps
flux reconcile kustomization apps --with-source
```

If you manually scale a Deployment while Flux is active, Flux will usually reconcile it back to the Git-declared value. That is not Flux being stubborn; it is Flux doing its job. Suspend only when you intentionally need a temporary break from convergence, and make the Git follow-up explicit before resuming normal operations.

## Automate Images Without Bypassing Git

Image automation is where Flux often surprises learners. Many deployment systems detect a new image and push it directly to a cluster. Flux can detect a new image, but the image-automation-controller updates Git instead. That preserves the GitOps rule that the cluster converges from Git, not from an invisible registry event.

The automation flow has three conceptual steps. ImageRepository scans a registry. ImagePolicy selects the desired tag from the observed tags. ImageUpdateAutomation edits files in Git and pushes a commit. After that, the normal source and Kustomization reconciliation path deploys the changed manifest.

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                         IMAGE AUTOMATION FLOW                              │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  1. CI builds and pushes image                                              │
│     ┌──────────────┐        ┌────────────────────────────────────────┐     │
│     │ CI pipeline  │───────▶│ Registry: ghcr.io/my-org/api:v1.2.3    │     │
│     └──────────────┘        └─────────────────┬──────────────────────┘     │
│                                               │                            │
│  2. image-reflector-controller scans tags      │                            │
│     ┌─────────────────────────────────────────▼──────────────────────┐     │
│     │ ImageRepository: records available tags for ghcr.io/my-org/api  │     │
│     └─────────────────────────────────────────┬──────────────────────┘     │
│                                               │                            │
│  3. ImagePolicy selects one tag                │                            │
│     ┌─────────────────────────────────────────▼──────────────────────┐     │
│     │ Policy: semver range >=1.2.0 <1.3.0, selected tag v1.2.3        │     │
│     └─────────────────────────────────────────┬──────────────────────┘     │
│                                               │                            │
│  4. image-automation-controller writes Git     │                            │
│     ┌─────────────────────────────────────────▼──────────────────────┐     │
│     │ ImageUpdateAutomation updates deployment.yaml and commits       │     │
│     └─────────────────────────────────────────┬──────────────────────┘     │
│                                               │                            │
│  5. normal Flux reconciliation deploys Git     │                            │
│     ┌─────────────────────────────────────────▼──────────────────────┐     │
│     │ GitRepository refreshes, Kustomization applies new image tag    │     │
│     └────────────────────────────────────────────────────────────────┘     │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

This flow is slower than a direct deploy from CI, but it is more auditable. The deployed image tag appears in Git history. Review tools, branch protections, commit signing, and notifications can inspect the change. If an image tag is bad, rollback is a Git revert or a policy change rather than a hunt through pipeline logs.

The ImageRepository should represent one image stream that a policy can reason about. It needs registry credentials when the image is private. Its interval controls how often Flux scans for tags, so a development environment may scan frequently while production may scan less frequently or rely on promotion branches.

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageRepository
metadata:
  name: api
  namespace: flux-system
spec:
  image: ghcr.io/my-org/api
  interval: 1m
  secretRef:
    name: ghcr-credentials
```

The ImagePolicy expresses selection logic. Semver works well when tags follow version semantics. Alphabetical or numerical policies can work for timestamped build tags, but only if the tag pattern is disciplined. The policy is not a magic quality gate; it only chooses from tags that already exist.

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: api-stable
  namespace: flux-system
spec:
  imageRepositoryRef:
    name: api
  filterTags:
    pattern: '^v(?P<version>[0-9]+\.[0-9]+\.[0-9]+)$'
    extract: '$version'
  policy:
    semver:
      range: ">=1.2.0 <1.3.0"
```

For development builds, teams often tag images with branch, commit, and timestamp. The policy should extract a sortable value rather than relying on accidental string ordering. A timestamp sorted numerically is clearer than hoping that alphabetical order matches deployment intent.

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: api-develop
  namespace: flux-system
spec:
  imageRepositoryRef:
    name: api
  filterTags:
    pattern: '^develop-[a-f0-9]+-(?P<ts>[0-9]+)$'
    extract: '$ts'
  policy:
    numerical:
      order: asc
```

ImageUpdateAutomation needs Git write access. That makes it a sensitive resource. It should write to a controlled branch and path, with commit messages that make automation clear. Some teams write directly to `main` for development but require pull requests for production. Others write to a promotion branch that a human or policy system merges.

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageUpdateAutomation
metadata:
  name: api-development
  namespace: flux-system
spec:
  interval: 5m
  sourceRef:
    kind: GitRepository
    name: fleet-infra
  git:
    checkout:
      ref:
        branch: main
    commit:
      author:
        name: flux-bot
        email: flux@example.com
      messageTemplate: |
        Update development image for {{ .AutomationObject }}

        {{ range .Updated.Images -}}
        - {{ . }}
        {{ end -}}
    push:
      branch: main
  update:
    path: ./apps/api/development
    strategy: Setters
```

The manifest must contain an update marker that connects a field to an ImagePolicy. Without that marker, Flux may scan tags and select a policy result but still have no field to edit. This is another example of Flux separating observation, decision, and mutation into different resources.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: development
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: ghcr.io/my-org/api:develop-a1b2c3d-1766500000 # {"$imagepolicy": "flux-system:api-develop"}
          ports:
            - containerPort: 8080
```

**Stop and think:** if image automation writes directly to the production path, what becomes your production approval gate? The answer must be explicit. It may be a branch protection rule, a pull request automation policy, a signed commit requirement, or an environment-specific ImagePolicy that only accepts promoted tags. If the answer is "Flux will handle it," the design is incomplete.

Image automation should not replace CI quality checks. CI should build, test, scan, sign, and publish images. Flux should observe eligible images and update Git according to policy. The boundary is important because Flux does not know whether your unit tests passed unless that signal is encoded in the tag, branch, registry metadata, admission policy, or promotion workflow.

A common production pattern is to allow automatic deployment in development, automatic pull request creation for staging, and human-approved promotion to production. Flux can participate in that pattern, but the exact implementation depends on your Git provider and policy tooling. The senior design principle is that higher environments should have narrower, more reviewable automation.

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                        ENVIRONMENT PROMOTION MODEL                         │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Development                                                                │
│  ┌──────────────────────────────┐                                          │
│  │ Any develop-* image tag       │                                          │
│  │ Image automation commits Git  │                                          │
│  │ Fast feedback, low risk       │                                          │
│  └───────────────┬──────────────┘                                          │
│                  │ promote selected candidate                               │
│                  ▼                                                          │
│  Staging                                                                    │
│  ┌──────────────────────────────┐                                          │
│  │ Release-candidate tag policy  │                                          │
│  │ PR or controlled automation   │                                          │
│  │ Integration and smoke tests   │                                          │
│  └───────────────┬──────────────┘                                          │
│                  │ approve release                                          │
│                  ▼                                                          │
│  Production                                                                 │
│  ┌──────────────────────────────┐                                          │
│  │ Signed version tag policy     │                                          │
│  │ Protected branch or PR gate   │                                          │
│  │ Alerts and health checks      │                                          │
│  └──────────────────────────────┘                                          │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

Notifications close the feedback loop. A GitOps system that only writes status to Kubernetes can be technically correct and operationally invisible. Alerting should route reconciliation failures to the team that owns the failing layer. Platform infrastructure failures may page the platform team. Application Kustomization failures may notify the service team and create a deployment incident.

```yaml
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
type: Opaque
stringData:
  address: https://hooks.slack.com/services/REPLACE/THIS/VALUE
---
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Alert
metadata:
  name: reconciliation-failures
  namespace: flux-system
spec:
  providerRef:
    name: slack
  eventSeverity: error
  eventSources:
    - kind: GitRepository
      name: "*"
    - kind: Kustomization
      name: "*"
    - kind: HelmRelease
      name: "*"
```

Alerts should start narrow enough to be useful. Sending every info event from every source and reconciler into one channel creates noise, and noisy channels train teams to ignore failures. Begin with error events for critical delivery resources, then add informational notifications where they support a real workflow such as release tracking.

Flux can also update Git commit status through notification providers. That is valuable when reviewers want pull requests or commits to show whether reconciliation succeeded. The important nuance is timing. A commit may pass CI before Flux applies it, and Flux may fail after CI is green because the cluster-specific environment rejected the change.

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Provider
metadata:
  name: github
  namespace: flux-system
spec:
  type: github
  address: https://github.com/my-org/fleet-infra
  secretRef:
    name: github-token
---
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Alert
metadata:
  name: apps-sync-status
  namespace: flux-system
spec:
  providerRef:
    name: github
  eventSources:
    - kind: Kustomization
      name: apps
```

A mature notification design distinguishes build success from deploy success. CI answers whether the artifact was produced and tested. Flux answers whether declared state reconciled into the cluster. Observability answers whether the service is healthy for users. Treating any one of those as a substitute for the others produces blind spots.

## Operate Flux Across Clusters and Incidents

Multi-cluster Flux is not one giant control plane pushing to many clusters. The common Flux pattern is that each cluster runs its own controllers and pulls the desired state for its cluster path. This reduces central blast radius and lets clusters keep reconciling even if a central UI is unavailable, but it also means each cluster needs correct bootstrap, credentials, and configuration.

A fleet repository should make cluster differences obvious. If production and staging differ only by values, the layout should show that. If a region has special compliance requirements, the layout should isolate that difference rather than hiding it in a long substitution file. Multi-cluster GitOps is partly a file organization problem because review quality depends on visible blast radius.

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: apps
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: fleet-infra
  path: ./apps/production
  prune: true
  wait: true
  timeout: 8m
  postBuild:
    substitute:
      CLUSTER_NAME: prod-us-east
      ENVIRONMENT: production
      DOMAIN: us-east.example.com
```

Inline `substitute` values are readable for a small number of stable cluster values. For larger or secret-bearing configuration, use `substituteFrom` with ConfigMaps and Secrets. The senior judgment is to keep values close enough for review but not so close that secrets leak or every cluster path becomes a wall of environment data.

Multi-cluster consistency should be tested before production traffic depends on it. A bootstrap checklist should verify Flux controller health, source readiness, required ConfigMaps and Secrets, dependency readiness, notification routes, and at least one forced reconciliation. This is not bureaucracy; it is how you prevent a cluster from sitting quietly misconfigured until the next emergency deployment.

```bash
flux check
flux get all
k get configmap cluster-config -n flux-system
k get secret ghcr-credentials -n flux-system
flux reconcile source git fleet-infra
flux reconcile kustomization apps --with-source
flux get kustomizations
```

A practical incident workflow starts by identifying whether the desired state changed. If Git changed, inspect the commit and the affected path. If Git did not change, look for drift, external dependencies, registry access, expired credentials, or Kubernetes API problems. Flux is a reconciler, so the first split is always desired-state change versus reconciliation environment change.

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                         FLUX INCIDENT TRIAGE                               │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Symptom observed                                                           │
│        │                                                                   │
│        ▼                                                                   │
│  Did desired state change in Git?                                           │
│        │                                                                   │
│        ├── Yes ──▶ Inspect commit, path, source artifact, reconciler status │
│        │          │                                                        │
│        │          ├── Source failed? Check credentials, branch, network     │
│        │          ├── Build failed? Check Kustomize, substitutions, values  │
│        │          ├── Apply failed? Check API errors, CRDs, validation      │
│        │          └── Health failed? Check pods, events, dependencies       │
│        │                                                                   │
│        └── No ───▶ Inspect drift, expired credentials, registry, API health │
│                   │                                                        │
│                   ├── Drift reverted? Flux may be correcting manual edits   │
│                   ├── Credentials expired? Source or registry scans fail    │
│                   ├── API degraded? Controller logs show client failures    │
│                   └── Workload degraded? App health changed after deploy    │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

When a Kustomization is stuck because a dependency is not ready, do not patch away the dependency first. Read the dependency status. The message "dependency 'flux-system/cert-manager' is not ready" is not the root cause; it is a pointer. The root cause is why cert-manager is not ready, which may be a failed webhook Deployment, missing CRD, image pull error, or bad values.

```bash
flux get kustomization apps -o wide
flux get kustomization cert-manager -o wide
k describe kustomization cert-manager -n flux-system
k get pods -n cert-manager
k get events -n cert-manager --sort-by='.lastTimestamp'
flux logs --kind=Kustomization --name=cert-manager --namespace=flux-system
```

The order matters again. Check the blocked resource, then the dependency, then the dependency's Kubernetes objects. This keeps the investigation anchored. If the dependency says apply succeeded but health failed, the next step is workload health. If the dependency says artifact fetch failed, the next step is source status.

A senior incident response also asks whether Flux should keep reconciling during mitigation. If the desired state is known bad, revert Git or suspend the affected reconciler while preparing a fix. If manual mitigation is necessary, document it and convert it into Git as soon as possible. Leaving manual drift after the incident invites Flux to undo the fix later.

```bash
flux suspend kustomization apps
k rollout undo deployment/api-gateway -n production
k rollout status deployment/api-gateway -n production --timeout=120s
git revert --no-edit HEAD
git push origin main
flux resume kustomization apps
flux reconcile kustomization apps --with-source
```

This sequence is intentionally cautious. Suspension creates room for emergency action. Rollout undo stabilizes the workload. Git revert fixes desired state. Resume and reconcile restore normal GitOps control. In a real incident, your exact commands may differ, but the principle is to end with Git and cluster state aligned.

Capacity planning for Flux is usually less dramatic than people expect. The controllers do steady reconciliation work, watch Kubernetes resources, and fetch artifacts. The load becomes meaningful when there are many repositories with short intervals, large manifest trees, heavy Helm rendering, or many clusters running the same pattern. Measure before guessing, but design intervals and controller resources intentionally.

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                      EXAMPLE FLUX LOAD ESTIMATE                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Scenario                                                                  │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ 50 GitRepositories checked every 1 minute                           │    │
│  │ 100 Kustomizations checked every 10 minutes                         │    │
│  │ 75 HelmReleases checked every 10 minutes                            │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                            │
│  Approximate API calls per minute                                           │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ Sources:          50 × 1/min × 3 calls      = 150 calls/min         │    │
│  │ Kustomizations:  100 × 1/10min × 15 calls   = 150 calls/min         │    │
│  │ HelmReleases:     75 × 1/10min × 10 calls   = 75 calls/min          │    │
│  │ Informer watches: steady background watch traffic                   │    │
│  │ Total estimate: about 375 calls/min, roughly 6 calls/second         │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                            │
│  Operational reading                                                       │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ This is normally low for a healthy Kubernetes API server, but       │    │
│  │ repository size, chart rendering, retries, and failure loops can    │    │
│  │ change the real cost. Watch controller metrics before tuning.       │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

Do not tune intervals only for speed. Short intervals increase responsiveness, but they also increase fetches, event churn, and the chance that a bad commit propagates quickly. For critical production paths, combine reasonable intervals with health checks, staged promotion, alerts, and the ability to revert quickly.

Scaling Flux can mean increasing controller resources, adjusting concurrency, sharding by label selectors, or splitting large repositories. The first step is usually not horizontal complexity. Start by measuring reconcile durations, artifact sizes, error rates, and API throttling. Then decide whether the bottleneck is Git fetch, manifest build, Helm render, Kubernetes apply, or workload readiness.

Senior teams also design ownership around Flux resources. A platform team may own infrastructure Kustomizations, source credentials, and controller configuration. Service teams may own app overlays and image policies within guardrails. Security teams may own admission controls and signing policy. The Git repository should make those ownership boundaries enforceable through CODEOWNERS, branch protection, and review rules.

Flux is strongest when it becomes part of a larger delivery control system. Git review controls desired state. CI controls artifact quality. Flux controls reconciliation. Admission controls enforce cluster policy. Observability confirms user-facing health. Incident response closes the loop when those controls were insufficient. Treating Flux as the whole system creates unrealistic expectations.

## Did You Know?

- **[Weaveworks invented the term "GitOps" in 2017](https://www.cncf.io/blog/2021/09/28/gitops-101-whats-it-all-about/)**, and Flux became one of the early Kubernetes tools associated with that operating model.
- **[Flux v2 was a complete rewrite](https://fluxcd.io/flux/migration/faq-migration/)** from the earlier monolithic Flux design into the current toolkit of specialized controllers.
- **[Flux can scale through controller configuration, concurrency tuning, and sharding](https://fluxcd.io/flux/installation/configuration/vertical-scaling/)**, but the right scaling move depends on the bottleneck you measure.
- **Flux and Argo CD are both CNCF graduated GitOps projects**, so senior tool selection should focus on workflow, ownership, and operating model rather than assuming one is inherently more mature.

## Common Mistakes

| Mistake | Why it causes trouble | Better approach |
|---------|-----------------------|-----------------|
| Creating a GitRepository and expecting workloads to appear automatically. | A source only fetches an artifact; it does not apply manifests or install charts by itself. | Pair every source with a Kustomization or HelmRelease that consumes the correct path or chart. |
| Omitting `prune: true` from long-lived application Kustomizations. | Objects removed from Git can remain in the cluster, creating hidden drift and stale attack surface. | Enable pruning for resources that should be fully owned by Git, and review deletions carefully. |
| Treating apply success as rollout success. | Kubernetes may accept objects even when pods later fail readiness, image pulls, webhooks, or dependencies. | Use `wait: true`, explicit `healthChecks`, and realistic `timeout` values for production workloads. |
| Adding `dependsOn` everywhere to make reconciliation look ordered. | Unnecessary dependencies serialize independent work and can turn one failure into a broad delivery blockage. | Use dependencies only for real readiness requirements such as CRDs, webhooks, ingress, and shared services. |
| Making substitution sources optional for required production values. | A missing ConfigMap or Secret can produce invalid manifests or environment-specific failures during rollout. | Use `optional: false`, validate new clusters, and add health checks for workloads using substituted values. |
| Letting image automation write production changes without a clear approval gate. | The registry can become an implicit deployment trigger, weakening review and audit expectations. | Use branch protection, promotion branches, signed tags, or pull request gates for production image updates. |
| Sending every Flux event into one noisy notification channel. | Teams learn to ignore alerts when success, noise, and real failures are mixed together. | Route error events by ownership first, then add informational notifications only where they support a workflow. |
| Debugging by restarting controllers before reading conditions. | Restarting can hide evidence and rarely fixes invalid desired state, bad credentials, or unhealthy workloads. | Follow the chain: source status, reconciler status, events, controller logs, then workload health. |

## Quiz

### Question 1

Your team bootstraps Flux into a new production cluster. `flux get sources git` shows the fleet repository is Ready, but no application Deployments appear in the `production` namespace. The Git repository contains `apps/production/kustomization.yaml`. What should you check next, and why?

<details>
<summary>Show Answer</summary>

Check whether a Flux `Kustomization` resource exists and references the Ready `GitRepository` with `path: ./apps/production`. A `GitRepository` only fetches an artifact; it does not apply manifests. If the source is Ready but no workload appears, the likely missing or broken contract is the consumer resource.

A useful command sequence is:

```bash
flux get kustomizations
k get kustomizations -n flux-system
k describe kustomization apps -n flux-system
```

If the Kustomization exists, inspect its path, sourceRef, status conditions, and events. The problem may be a wrong path, a Kustomize build failure, an apply error, or a health check failure.
</details>

### Question 2

A platform pull request adds an `apps` Kustomization with `dependsOn: ingress`. The `apps` Kustomization stays Not Ready with a message saying the ingress dependency is not ready. The ingress manifests were applied successfully. What is the most likely misunderstanding, and how do you fix the design?

<details>
<summary>Show Answer</summary>

The misunderstanding is confusing apply success with readiness. A dependency must become Ready, not merely have its manifests accepted by the Kubernetes API. If ingress depends on pods, webhooks, Services, or LoadBalancer readiness, the ingress Kustomization should use `wait: true`, appropriate `healthChecks`, and a realistic `timeout`.

A stronger ingress Kustomization would include checks for the ingress controller Deployment:

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: ingress
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: fleet-infra
  path: ./infrastructure/production/ingress
  prune: true
  wait: true
  timeout: 5m
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: ingress-nginx-controller
      namespace: ingress-nginx
```

Then debug the actual ingress workload with pod status, events, and controller logs rather than patching the dependent `apps` resource.
</details>

### Question 3

Your organization deploys the same API to development, staging, and production. Development should auto-deploy every `develop-<sha>-<timestamp>` image, staging should receive release candidates, and production should deploy only approved version tags. How would you design Flux image automation so Git remains the source of truth?

<details>
<summary>Show Answer</summary>

Use separate ImagePolicy objects for each environment and narrow what each policy can select. Development can use a numerical policy over extracted timestamps from `develop-*` tags. Staging can select `rc-*` tags or receive pull requests generated by automation. Production should select only signed or approved semver tags, ideally through a protected branch or pull request gate.

Development automation may write directly to the development path, but production automation should not silently update production unless your approval gate is encoded in branch protection, promotion branches, or policy tooling. The key is that ImageUpdateAutomation edits Git, then normal GitRepository and Kustomization reconciliation deploys the change.

A good answer also mentions update markers in the manifest, scoped Git credentials for the automation controller, and clear commit messages that identify automated image changes.
</details>

### Question 4

A new regional cluster is bootstrapped from the same fleet repository as existing clusters. Two weeks later, a routine rollout fails because `${REPLICAS}` and `${DOMAIN}` were not substituted in the rendered Deployment. What Flux configuration would have caught this earlier?

<details>
<summary>Show Answer</summary>

The Kustomization should require the substitution source with `optional: false`, and the cluster bootstrap checklist should verify the required ConfigMap or Secret exists before production traffic is enabled. The Kustomization should also use `wait: true`, `timeout`, and health checks for critical workloads so readiness failures surface during reconciliation.

Example:

```yaml
postBuild:
  substituteFrom:
    - kind: ConfigMap
      name: cluster-config
      optional: false
```

This prevents a missing cluster configuration input from being treated as acceptable. The design should also include a validation step such as `k get configmap cluster-config -n flux-system` and a forced reconciliation before the cluster joins production rotation.
</details>

### Question 5

During an incident, an engineer manually scales `deployment/api-gateway` from five replicas to two to reduce database pressure. Ten minutes later the Deployment returns to five replicas. What happened, and what should the incident workflow have done differently?

<details>
<summary>Show Answer</summary>

Flux reconciled the Deployment back to the value declared in Git. That is expected behavior when the Deployment is owned by a Kustomization. Manual changes are drift unless the Git desired state changes or reconciliation is suspended.

A better workflow would suspend the relevant Kustomization if manual mitigation is necessary, apply the temporary change, create or revert a Git commit that represents the intended desired state, then resume reconciliation.

```bash
flux suspend kustomization apps
k scale deployment api-gateway -n production --replicas=2
# Commit the intended production state or revert the bad change in Git.
flux resume kustomization apps
flux reconcile kustomization apps --with-source
```

The final state should be represented in Git so Flux and the cluster do not fight each other.
</details>

### Question 6

A service team wants Flux because it has built-in image automation. The team proposes that any image pushed to `ghcr.io/my-org/payments` should update production immediately. What risks should you raise in review, and what safer design would you recommend?

<details>
<summary>Show Answer</summary>

The proposal makes the registry an implicit production deployment gate. That weakens review, audit, and separation between build success and release approval. A bad or untested image tag could be selected by policy and committed to production without the team noticing until Flux applies it.

A safer design uses tag discipline and environment-specific policy. Development may auto-deploy branch tags. Staging may consume release-candidate tags. Production should consume only approved semver tags through a protected branch, pull request, or promotion workflow. Flux can still automate the Git update, but the production path should have an explicit approval control.

The review should also ask about registry credentials, commit identity, update markers, rollback path, and notifications for failed reconciliations.
</details>

### Question 7

Your team is deciding between Flux and ArgoCD for a platform-managed fleet of many clusters. Developers want visibility, while the platform team wants every cluster to pull its own infrastructure and application overlays from Git. How would you evaluate the trade-off without turning it into a popularity contest?

<details>
<summary>Show Answer</summary>

Compare operating models. Flux fits well when the platform team wants delivery primitives to be Kubernetes resources, each cluster to self-reconcile, and automation to be composed through Git, CRDs, and controller status. ArgoCD fits well when application teams need a central UI, visual diffs, self-service sync, and application-centric visibility.

A senior recommendation might be Flux for platform infrastructure and fleet reconciliation, ArgoCD for developer-facing app visibility, or one tool for both if ownership is simpler. The important constraint is avoiding dual ownership of the same Kubernetes objects. If both tools manage the same Deployment, they may reconcile against each other.

The decision should be based on ownership, review model, multi-cluster topology, audit requirements, onboarding needs, and incident workflows.
</details>

### Question 8

A HelmRelease has been failing after a chart version range allowed a new minor chart release. The application image did not change, but the rendered resources did. What should the team change in its Flux and review process?

<details>
<summary>Show Answer</summary>

The team should tighten chart version control for production, often by pinning exact chart versions or using a narrower semver range. A broad chart range can change rendered Kubernetes objects even when values and image tags remain stable. Flux is correctly reconciling the eligible chart version, but the review process did not make the chart change visible enough.

The team should inspect the HelmRelease status, chart artifact, controller logs, and rendered differences if available through its tooling. For future changes, chart upgrades should be reviewed like application releases, with staging reconciliation, health checks, and rollback instructions.

A production HelmRelease should make chart version movement intentional rather than accidental.
</details>

## Hands-On Exercise

### Scenario: Build and debug a small Flux delivery graph

In this exercise, you will install Flux into a local kind cluster, reconcile a public application source, install a Helm chart, test suspend and resume behavior, and practice reading status when a dependency blocks reconciliation. The goal is not to memorize commands. The goal is to experience the chain from source to reconciler to workload health.

### Step 1: Create the lab cluster and install Flux

Use a local kind cluster so the lab does not touch any shared environment. The `flux check --pre` command validates prerequisites before installation, and `flux install` installs the controllers without bootstrapping to a real Git provider.

```bash
kind create cluster --name flux-lab
kubectl cluster-info --context kind-flux-lab
alias k=kubectl

flux check --pre
flux install
flux check
k get pods -n flux-system
```

Success criteria for this step:

- [ ] The `flux-lab` kind cluster exists and is the active context.
- [ ] `flux check --pre` passes before installation.
- [ ] Flux controllers are running in the `flux-system` namespace.
- [ ] You can explain why this lab uses `flux install` instead of `flux bootstrap github`.

### Step 2: Reconcile a public Git source with Kustomization

Create a GitRepository pointing at the public `podinfo` repository, then create a Kustomization that applies the `./kustomize` path from that source. This demonstrates the source-consumer contract in the smallest useful form.

```bash
flux create source git podinfo \
  --url=https://github.com/stefanprodan/podinfo \
  --branch=master \
  --interval=1m \
  --export > podinfo-source.yaml

k apply -f podinfo-source.yaml

flux create kustomization podinfo \
  --source=GitRepository/podinfo \
  --path="./kustomize" \
  --prune=true \
  --wait=true \
  --interval=10m \
  --timeout=3m \
  --export > podinfo-kustomization.yaml

k apply -f podinfo-kustomization.yaml
```

Now inspect both the source and the reconciler. Read the output as a chain: source readiness first, then Kustomization readiness, then workload state.

```bash
flux get sources git
flux get kustomizations
k get pods -A | grep podinfo
k get deploy,svc -A | grep podinfo
```

Success criteria for this step:

- [ ] The `podinfo` GitRepository reports Ready.
- [ ] The `podinfo` Kustomization reports Ready.
- [ ] Podinfo workload objects appear in the cluster.
- [ ] You can explain why the GitRepository alone would not have deployed the app.

### Step 3: Add a HelmRepository and HelmRelease

This step adds Helm to the delivery graph. The HelmRepository fetches chart metadata, and the HelmRelease declares the chart installation. Treat the HelmRelease as another reconciler that consumes a source artifact.

```bash
flux create source helm bitnami \
  --url=https://charts.bitnami.com/bitnami \
  --interval=1h \
  --export > bitnami-source.yaml

k apply -f bitnami-source.yaml

k create namespace web

cat <<'EOF' | k apply -f -
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
```

Inspect the source, HelmRelease, and workload. If the chart takes time to install, use the watch command for a short period and then describe the HelmRelease if it fails.

```bash
flux get sources helm
flux get helmreleases -A
k get pods,svc -n web
k describe helmrelease nginx -n web
```

Success criteria for this step:

- [ ] The Bitnami HelmRepository reports Ready.
- [ ] The `web/nginx` HelmRelease reconciles successfully.
- [ ] NGINX pods and a Service exist in the `web` namespace.
- [ ] You can distinguish a HelmRepository source failure from a HelmRelease render or install failure.

### Step 4: Observe suspend and resume behavior

Suspend the podinfo Kustomization, make a manual change, then resume reconciliation. The purpose is to see GitOps convergence directly rather than only reading about drift.

```bash
flux suspend kustomization podinfo
k scale deployment podinfo --replicas=5
k get deployment podinfo

flux resume kustomization podinfo
flux reconcile kustomization podinfo --with-source
k get deployment podinfo
```

Before running the final `k get`, predict what replica count you expect and why. If the Git-declared podinfo configuration says a different replica count than your manual scale, Flux should converge the Deployment back to the declared state after reconciliation resumes.

Success criteria for this step:

- [ ] You suspended reconciliation for the `podinfo` Kustomization.
- [ ] You manually changed a Flux-owned Deployment.
- [ ] You resumed reconciliation and observed Flux restore the Git-declared state.
- [ ] You can explain when suspension is appropriate during an incident.

### Step 5: Create and debug a blocked dependency

Create a Kustomization that depends on a missing dependency. This intentionally creates a Not Ready state so you can practice reading dependency failure instead of guessing.

```bash
cat <<'EOF' | k apply -f -
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: blocked-demo
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: podinfo
  path: ./kustomize
  prune: true
  wait: true
  timeout: 2m
  dependsOn:
    - name: missing-dependency
EOF

flux reconcile kustomization blocked-demo --with-source
flux get kustomization blocked-demo -o wide
k describe kustomization blocked-demo -n flux-system
```

The goal is not to fix this by removing the dependency immediately. First, identify how Flux reports the failure. Then edit the object to remove the fake dependency or delete the demo resource.

```bash
k delete kustomization blocked-demo -n flux-system
```

Success criteria for this step:

- [ ] The `blocked-demo` Kustomization reports a dependency-related Not Ready state.
- [ ] You found the dependency message through `flux get` or `k describe`.
- [ ] You can explain why dependency failures should lead you to inspect the dependency resource first.
- [ ] You deleted the intentionally broken demo object after observing the failure.

### Step 6: Clean up the lab

Delete the kind cluster and generated local files. This keeps your workstation clean and prevents stale manifests from being mistaken for production examples later.

```bash
kind delete cluster --name flux-lab
rm -f podinfo-source.yaml podinfo-kustomization.yaml bitnami-source.yaml
```

Final exercise success criteria:

- [ ] You installed Flux controllers into a local cluster.
- [ ] You reconciled a GitRepository through a Kustomization.
- [ ] You reconciled a HelmRepository through a HelmRelease.
- [ ] You observed suspend and resume behavior.
- [ ] You debugged a dependency-blocked Kustomization through status conditions.
- [ ] You can map a Flux symptom to the controller contract most likely responsible.

## Next Module

Continue to [Module 2.4: Helm & Kustomize](../module-2.4-helm-kustomize/) where you will go deeper on the packaging and overlay tools that Flux consumes during reconciliation.

## Sources

- [cncf.io: what is flux cd](https://www.cncf.io/blog/2023/09/15/what-is-flux-cd/) — The CNCF Flux backgrounder explicitly says Flux was developed by Weaveworks.
- [cncf.io: gitops 101 whats it all about](https://www.cncf.io/blog/2021/09/28/gitops-101-whats-it-all-about/) — The CNCF article explicitly states that Weaveworks coined the term GitOps in 2017.
- [cncf.io: flux](https://www.cncf.io/projects/flux/) — The CNCF project page explicitly lists Flux as having reached Graduated maturity.
- [cncf.io: flux trusted by amazon d2iq microsoft red hat vmware and weaveworks](https://www.cncf.io/blog/2021/10/19/flux-trusted-by-amazon-d2iq-microsoft-red-hat-vmware-and-weaveworks/) — The CNCF post explicitly names Deutsche Telekom among companies sharing Flux usage.
- [cncf.io: flux graduates from cncf incubator](https://www.cncf.io/announcements/2022/11/30/flux-graduates-from-cncf-incubator/) — The Flux graduation announcement explicitly names Volvo and SAP as relying on Flux.
- [fluxcd.io: faq migration](https://fluxcd.io/flux/migration/faq-migration/) — The migration FAQ explicitly contrasts monolithic Flux v1 with Flux v2's specialized controllers.
- [fluxcd.io: vertical scaling](https://fluxcd.io/flux/installation/configuration/vertical-scaling/) — The scaling docs explicitly cover increasing worker concurrency and refer readers to sharding for horizontal scaling.
- [fluxcd.io: kustomizations](https://fluxcd.io/flux/components/kustomize/kustomizations/) — The Kustomization docs explicitly define `dependsOn`, `wait`, `healthChecks`, and Ready-condition behavior.
- [fluxcd.io: providers](https://fluxcd.io/flux/components/notification/providers/) — The Provider documentation explicitly documents Slack and Microsoft Teams provider types.
- [cncf.io: argo](https://www.cncf.io/projects/argo/) — The CNCF Argo project page explicitly lists Argo at Graduated maturity.
