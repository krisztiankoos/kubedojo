---
title: "Module 4.2: Application Packaging"
slug: k8s/kcna/part4-application-delivery/module-4.2-application-packaging
sidebar:
  order: 3
revision_pending: false
---

# Module 4.2: Application Packaging

> **Complexity**: `[MEDIUM]` - Tool concepts
>
> **Time to Complete**: 35-45 minutes
>
> **Prerequisites**: Module 4.1 (CI/CD Fundamentals)
>
> **Scope**: Packaging decisions for Kubernetes 1.35 application delivery, with Helm and Kustomize as the primary comparison tools.

## Learning Outcomes

After completing this module, you will be able to:

1. **Compare** Helm and Kustomize packaging strategies for Kubernetes 1.35 application delivery.
2. **Design** environment-specific deployment configuration using Helm values or Kustomize overlays.
3. **Diagnose** packaging failures by inspecting rendered manifests, release history, and overlay output.
4. **Evaluate** when Artifact Hub, chart repositories, or in-repository bases are appropriate for team delivery.
5. **Implement** a small multi-environment packaging workflow using the `k` CLI alias.

## Why This Module Matters

An operations team at a regional payments company once shipped an urgent checkout fix to production by editing raw Kubernetes manifests copied from staging. The patch looked tiny: one image tag, one environment variable, and one replica count. Two hours later, the checkout API was serving old code from half of its pods because the production Deployment, Service, ConfigMap, and Ingress files had drifted from the staging copies in different ways. The rollback was not a single command; it was a careful reconstruction of which YAML files had changed, which ones had been missed, and which resources had already been reconciled by the cluster.

That kind of incident is expensive because the failure is not really a YAML typo. The deeper failure is that the organization has no packaging model. Raw manifests are excellent for learning Kubernetes objects, but they do not answer operational questions such as "which version is deployed?", "how do we apply the same app to three environments without copying everything?", "how do we review the generated YAML before it reaches the cluster?", or "how do we distribute a known-good platform pattern to many teams?" Application packaging tools exist because those questions show up every week in real delivery work.

This module teaches the KCNA-level packaging landscape through the two tools you are most likely to meet first: Helm and Kustomize. Helm treats a Kubernetes application like a package with templates, values, versions, dependencies, and release history. Kustomize treats an application like a base set of ordinary Kubernetes resources plus overlays that patch those resources for each environment. By the end, you should be able to look at a delivery problem, choose a packaging approach, and explain the tradeoff in practical terms rather than tool slogans.

For command examples, this module uses the standard shorthand `alias k=kubectl`. In a real shell you can run `alias k=kubectl` once, then use commands such as `k apply -k overlays/prod/` exactly where the module uses them. That convention keeps examples readable while still pointing at the Kubernetes CLI you will use on Kubernetes 1.35 and later clusters.

---

## The Problem with Raw Manifests

The first Kubernetes application you deploy often starts as a small group of YAML files: a Deployment, a Service, maybe a ConfigMap, and perhaps an Ingress. That is a healthy learning path because it forces you to see the API objects directly. The same directness becomes painful when the application moves through dev, staging, and production, because every environment needs mostly the same resources with a few carefully controlled differences.

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

The diagram shows the core scaling problem: each copied file becomes another place where intent can diverge from reality. If dev has three replicas, staging has two, and production has eight, the replica difference is intentional. If production has an old readiness probe because someone copied a file before a health-check fix landed, the difference is accidental. Packaging tools help teams separate intended variation from accidental drift.

Raw manifests also hide release history. Kubernetes stores object state, but it does not know that a group of resources collectively represents version `1.8.3` of your billing service. The API server can tell you the current Deployment template, but it cannot answer whether the Service, ConfigMap, Ingress, and HorizontalPodAutoscaler were all deployed as one application version. Packaging adds an application-level unit above individual resources.

Pause and predict: if a team copies six raw manifests into dev, staging, and production directories, what kind of change is most likely to drift first? Think about fields that are easy to forget during review, such as probes, labels, resource requests, or environment variables, and then compare your prediction with how packaging tools centralize shared structure.

The goal is not to avoid YAML. Kubernetes still consumes YAML or JSON objects through the API. The goal is to make the source of those objects easier to reason about before they reach the cluster. A good packaging workflow lets you review the final manifest, apply environment-specific changes intentionally, roll back a bad release, and keep ownership clear between platform teams and application teams.

A useful way to think about raw manifests is to imagine a restaurant with three printed menus for breakfast, lunch, and dinner. If the kitchen changes the allergy warning for one ingredient, every menu that mentions that ingredient must be updated accurately. If one menu is missed, the mistake may not show up until a customer orders from that specific menu. Kubernetes environment directories have the same failure mode when shared application structure is copied instead of packaged.

Packaging tools create a contract around what is shared and what is allowed to vary. In a healthy workflow, the Deployment's selector labels, container port, readiness probe shape, and Service target port are shared structure. The image tag, replica count, resource requests, and external hostname are environment inputs. Once the team agrees on that boundary, code review becomes more precise because reviewers know whether a change is altering the application design or only selecting an environment value.

Consider a simple checkout service that needs different database URLs, replica counts, and image tags in each environment. Without packaging, the easiest path is to create three directories and copy the YAML. With packaging, the team keeps one shared definition of the application shape and supplies different inputs for each environment. That sounds small until an incident forces the team to prove exactly which configuration reached production.

There is a second reason KCNA cares about packaging: modern platform teams rarely deploy only their own code. They install ingress controllers, metrics systems, certificate managers, policy engines, databases, and observability agents. Those systems often come from upstream projects or vendors, and the operational question becomes whether to consume a published package, adapt a base configuration, or maintain everything internally.

## Helm: Packages, Templates, Values, and Releases

Helm describes itself as the package manager for Kubernetes because it gives Kubernetes resources the package concepts developers already know from other ecosystems. A Helm chart is a distributable bundle. A release is an installed instance of that chart in a cluster. A repository is a place where charts can be published and discovered. Those concepts matter because they let teams talk about application versions instead of only individual API objects.

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

The chart structure is deliberately split between templates and values. Templates describe the shape of the Kubernetes resources, while values describe the configurable inputs that change per installation. This is similar to building a house from a plan where the wall layout is fixed but the paint colors, appliance models, and number of garage spaces are selected from a permitted list. The package author controls the structure; the installer controls the inputs.

> **Pause and predict**: You manage an application deployed to dev, staging, and production. The only differences between environments are the image tag, replica count, and database URL. Without Helm or Kustomize, you would maintain three copies of every YAML file. What problems would this duplication create over time?

Helm's power comes from rendering templates into normal Kubernetes manifests. A template can insert a release name, choose a replica count from `.Values`, include optional resources, or format a resource block with helper functions. The cluster never receives "Helm YAML" as a special API type. Helm renders the chart locally or through the client workflow, then sends ordinary Kubernetes objects to the API server.

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

That rendering step is the reason Helm is both useful and dangerous. It is useful because a chart can expose dozens of controlled settings without forcing each application team to edit every Kubernetes object by hand. It is dangerous because Go template syntax can obscure the final result, especially when charts use nested conditionals, helper templates, loops, and values that override other values. A responsible Helm workflow includes rendering before applying.

The most maintainable charts treat values as an interface, not as a dumping ground. A chart might expose `replicaCount`, `image.repository`, `image.tag`, `resources`, `service.port`, and `ingress.hosts` because those are normal installation decisions. It should be more cautious about exposing every internal label, selector, probe field, and volume mount as a casual override. Too many knobs make consumers feel powerful at first, then make upgrades unpredictable because every installation can become a special case.

Chart authors also need to distinguish chart version from application version. The chart version changes when the package changes: templates, default values, dependencies, or packaging behavior. The application version usually tracks the software being installed, such as the web service image version. Those fields may move together for a simple internal chart, but they are conceptually different, and confusing them makes rollback and compatibility discussions harder.

The practical debugging move is to inspect the generated output before it changes the cluster. `helm template my-release ./my-app -f prod-values.yaml` renders the manifests locally, while `helm install --dry-run --debug my-release ./my-app -f prod-values.yaml` simulates an installation and shows what Helm would submit. Those commands are not optional polish; they are how you turn a templating system back into reviewable Kubernetes resources.

| Command | Purpose |
|---------|---------|
| `helm install` | Install a chart |
| `helm upgrade` | Upgrade a release |
| `helm rollback` | Rollback to previous version |
| `helm uninstall` | Remove a release |
| `helm list` | List releases |
| `helm repo add` | Add chart repository |
| `helm search` | Search for charts |

The release lifecycle is Helm's other major advantage over raw manifests. When you run `helm install`, Helm records a release. When you run `helm upgrade`, it creates another revision of that release. If the upgrade fails or the new version behaves badly, `helm rollback` can return the release to an earlier revision. Kubernetes Deployments have rollout history for pod templates, but Helm tracks a broader application package across all resources in the chart.

War story: a data platform team upgraded a dashboard chart and discovered that the new chart version changed a default ServiceAccount annotation. The pods started, but the cloud permissions they expected were no longer attached, so dashboards could not read metrics. Because the team had kept a release history and rendered the chart diff during review, they could identify the changed manifest, roll back the Helm release, and prepare a values override for the next attempt.

Before running this in a real cluster, what output would you expect from `helm list` after installing the same chart twice with two different release names? The important mental model is that the chart is the package, while each release is an installed instance with its own name, namespace, values, revision history, and lifecycle.

Helm is especially strong when a platform team needs to distribute a reusable pattern. A chart can document supported values, publish versioned releases, depend on other charts, and be installed by teams that do not need to read every template. That does not make Helm the best choice for every internal app. It means Helm shines when packaging, distribution, dependency management, and release rollback are central requirements.

One practical review habit is to ask for both the values change and the rendered manifest change in the same pull request discussion. The values file tells you what the author intended to change. The rendered manifest tells you what Kubernetes will actually receive. When those two views disagree, the team has found a packaging bug before it becomes a cluster incident.

## Kustomize: Bases, Overlays, and Patches

Kustomize starts from a different philosophy. Instead of inventing template placeholders inside YAML, it keeps Kubernetes resources as plain YAML and layers changes on top. A base directory contains the shared objects. Overlay directories refer to the base and then apply environment-specific changes such as name prefixes, namespaces, image tags, replica counts, labels, annotations, and patches.

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

This model fits teams that want their source files to remain recognizable Kubernetes objects. If a developer opens `base/deployment.yaml`, they see a Deployment, not a Deployment mixed with template expressions. If production needs a different image tag, the production overlay says so explicitly. If staging needs an extra annotation, the staging overlay patches that field without changing the shared base.

Kustomize is built into `kubectl` through commands such as `k apply -k overlays/prod/`, which is why it appears often in GitOps workflows. A GitOps controller can watch an overlay path, build the final manifests, and apply them to the cluster. The review conversation stays close to Kubernetes itself: "this overlay changes the image tag and replica count" rather than "this values file interacts with these template branches."

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

The example shows the core idea: the production overlay does not copy the Deployment. It points at the base, adds `prod-` to resource names, changes the replica count, and updates the image tag. Kustomize then produces the final manifests. You can preview those manifests with `k kustomize overlays/prod/` before applying them with `k apply -k overlays/prod/`.

The tradeoff is that Kustomize is not a general programming language. That restraint is intentional. Kustomize can patch fields, transform names, generate ConfigMaps and Secrets from local files, and change images or replicas in common cases. It is not designed to express deeply conditional logic or compute complex resource structures from arbitrary values. When a team tries to make Kustomize behave like a template engine, the result usually becomes harder to read than a clear Helm chart.

Kustomize generators deserve a careful mental model. A ConfigMap generator can build a ConfigMap from files or literals, and Kustomize can add a content hash to the generated name so pods roll when configuration changes. That behavior is useful, but it also means references must be managed through Kustomize rather than hardcoded by hand. If a team mixes generated names with manually written references, it can create confusing failures where the ConfigMap exists but the pod points at the wrong name.

Patches are strongest when they are narrow and reviewable. A production overlay that changes only `spec.replicas` and a container image tag is easy to understand. A production overlay that replaces the entire pod template is a warning sign because the base no longer describes the production application. When patches grow large, the team should ask whether it has one application with small environment differences or several application variants that deserve separate bases.

War story: a product team maintained a single base for an API service and overlays for dev, staging, production, and a temporary performance environment. A production incident review found that every environment had the same readiness probe because the probe lived in the base, while only replica counts and resource requests varied in overlays. The team could prove the difference was intentional by reading the overlay, which made the review faster and reduced blame-driven guessing.

Which approach would you choose here and why: a team owns one internal service, wants dev and production variations, and prefers reviewers to see plain Kubernetes YAML? Kustomize is usually the first answer because it keeps the base readable and expresses environment deltas directly, but the answer can change if the same service must be packaged for many external teams.

Kustomize still requires discipline. If every overlay contains huge strategic merge patches that rewrite most of the base, the base no longer communicates much. If name prefixes are used without thinking through Service selectors, NetworkPolicies, or external references, generated names can surprise operators. The tool keeps YAML plain, but the team still needs conventions for overlay size, review expectations, and preview commands.

The simplest Kustomize convention is to make every overlay explain its purpose through the files it changes. `replica-patch.yaml`, `resources-patch.yaml`, and `ingress-host-patch.yaml` are easier to review than one large `production.patch.yaml` file that changes unrelated fields. The file names are not enforced by Kubernetes, but they create human affordances that matter during review and incident response.

## Comparing Helm and Kustomize in Real Delivery Work

The Helm-versus-Kustomize question is often presented as a rivalry, but the better question is what kind of configuration problem you are solving. Helm is a packaging and distribution tool with templating and release history. Kustomize is a configuration composition tool with bases and overlays. Both produce Kubernetes manifests, but they optimize for different parts of the delivery workflow.

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

The easiest way to compare the tools is to ask who owns the variability. In Helm, the chart author decides which values are supported, and the installer supplies those values. That is excellent for a platform team publishing a reusable application pattern. In Kustomize, the base author provides shared resources, and each overlay author patches the resources for a specific environment. That is excellent for a team that owns both the app and the environment-specific differences.

> **Stop and think**: Helm uses Go templating to generate YAML, while Kustomize uses overlays on plain YAML without any templating. Which approach would be easier for a team that has never used either tool? Which would be more powerful for distributing an application to external users who need to customize many settings?

Debugging also feels different. A Helm problem often starts with the question "what did this values combination render?" You answer it with `helm template`, `helm get values`, `helm get manifest`, release history, and chart documentation. A Kustomize problem often starts with the question "which overlay patch changed this field?" You answer it with `k kustomize`, directory review, and inspection of the base-plus-overlay relationship.

Release history is another major distinction. Helm maintains release revisions, which supports rollback at the application package level. Kustomize itself does not maintain release state; the state is usually in Git history, a GitOps controller, or the Kubernetes objects. That can be perfectly acceptable, especially when Git is the source of truth, but it changes how the team thinks about rollback and audit trails.

Dependencies create a similar split. Helm charts can declare chart dependencies, which is useful when an application package needs related components. Kustomize composes resources and remote bases, but it is not a package dependency manager in the same sense. If your app needs Redis, a message queue, and a metrics sidecar packaged together for many teams, Helm's dependency model is often easier to govern.

Security review cuts across both approaches. A Helm chart can create cluster-scoped RBAC, CRDs, admission webhooks, and privileged workloads. A Kustomize base can do the same if it contains those resources. The packaging tool does not make the resources safe. The review habit is to render or build the final manifests, search for cluster-scoped permissions, inspect ServiceAccounts and RoleBindings, and confirm that any CRDs or webhooks are expected by the platform team.

Cost and reliability review also cut across both approaches. Replica counts, resource requests, persistent volume sizes, load balancer annotations, and autoscaling settings are application packaging concerns because they are part of what reaches the cluster. Treating packaging as "just deployment syntax" misses the fact that one values file or overlay can double infrastructure spend, remove availability buffers, or change storage behavior. Good packaging review includes operational impact.

There is a legitimate combined pattern: render a Helm chart as a base and then use Kustomize overlays for environment-specific changes. This shows up when an upstream project publishes a chart, but an organization wants to add local labels, policies, or image overrides through a GitOps repository. The combination can be effective, but it should be documented carefully because debugging now requires understanding both rendering steps.

For KCNA, do not memorize "Helm is better" or "Kustomize is simpler" as universal claims. Instead, evaluate the operational shape. Distribution, versioned packages, dependencies, and release rollback point toward Helm. Plain YAML, small environment deltas, GitOps-friendly overlays, and low template complexity point toward Kustomize. Complex stateful behavior that reconciles custom resources may point beyond packaging into the Operator pattern.

## Other Packaging Tools and the Wider Ecosystem

Helm and Kustomize are the KCNA essentials, but they are not the only ways teams generate or manage Kubernetes configuration. Jsonnet and Tanka treat configuration as data structures that can be composed programmatically. CUE focuses on typed configuration and validation. Carvel provides a toolkit where ytt handles YAML templating, kbld handles image references, and kapp handles application deployment. Operators use controllers and custom resources when packaging alone is not enough.

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

The important KCNA lesson is not to collect tool names. The important lesson is to match the tool to the configuration problem. If a team needs to generate many similar resources from a rich data model, a data templating language may be appropriate. If a team needs schema-like validation and composable constraints, CUE may be attractive. If a platform wants a suite of focused tools for templating, image resolution, and deployment ownership, Carvel may fit.

Operators sit in a different category because they change the runtime behavior of the cluster. A Helm chart can install a database, but it does not continuously reason about backups, failover, storage expansion, or custom upgrade choreography unless the chart hooks become very complex. An Operator can watch custom resources and reconcile real operational state. That power is useful for complex stateful systems, but it also introduces controller code, custom APIs, and a larger operational surface.

Artifact Hub is the discovery layer many learners meet when they look for real packages. It is a CNCF project that indexes Helm charts and other cloud native artifacts, which makes it a practical starting point when you need a packaged ingress controller, database chart, policy bundle, or operator entry. Discovery is only the first step, though. You still need to inspect maintainers, chart versions, security posture, values, and upgrade notes.

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

Using a package from Artifact Hub should feel like adopting a dependency, not downloading a random snippet. Check whether the package is maintained, whether it has recent releases, whether the source repository is clear, whether values are documented, and whether the chart version supports the Kubernetes version you run. A package that installs cleanly today can still create upgrade risk if it has weak maintenance or unclear defaults.

The ecosystem view also explains why packaging conversations often involve security and supply chain concerns. A chart can create RBAC permissions, install CRDs, configure admission webhooks, or mount volumes. Before installing a third-party package, render the manifests, review cluster-scoped permissions, and apply the same change-management discipline you would apply to application code. Packaging makes delivery easier, but it does not remove engineering judgment.

The same ecosystem view helps explain why teams sometimes standardize on more than one tool. A platform organization may publish Helm charts for reusable services, use Kustomize overlays in GitOps repositories, and adopt an Operator for a database that needs continuous reconciliation. That is not inconsistency if each tool owns a clear job. It becomes inconsistency only when nobody can explain which layer owns defaults, environment differences, upgrades, and emergency rollback.

## Patterns & Anti-Patterns

The first strong pattern is to keep shared application shape in one place and environment intent in another. With Helm, that usually means chart templates plus values files such as `values-dev.yaml`, `values-staging.yaml`, and `values-prod.yaml`. With Kustomize, it means a base plus overlays. The pattern works because reviewers can distinguish structural changes from environment-specific changes, which reduces accidental drift during routine releases.

The second strong pattern is to render before applying. For Helm, render with `helm template` or a dry run and inspect the generated Deployment, Service, ConfigMap, RBAC objects, and hooks. For Kustomize, build the overlay with `k kustomize overlays/prod/` before running `k apply -k overlays/prod/`. This habit catches surprising names, missing labels, incorrect selectors, and unintended permissions before the API server accepts them.

The third strong pattern is to version what other teams consume. If a platform group publishes a Helm chart, it should treat chart versions as a compatibility contract. If a team publishes a Kustomize base for others to reuse, it should document expected overlays and breaking changes. Consumers need to know whether a change is a patch-level fix, a new optional setting, or a structural change that requires migration work.

The fourth strong pattern is to keep secrets out of package defaults. Charts and overlays often need to refer to credentials, but they should not embed realistic secrets, long-lived tokens, or production passwords. Use Kubernetes Secret references, external secret controllers, sealed-secret workflows, or environment-specific secret delivery systems. Packaging should wire references and names, not become a storage location for credentials.

An anti-pattern appears when Helm templates become a programming contest. Deep nesting, dynamic resource names, multiple layers of helper templates, and conditionals that change object kinds make charts hard to review. Teams fall into this because Helm can express so much. The better alternative is to expose a small, documented values surface and keep the rendered Kubernetes objects predictable.

Another anti-pattern appears when Kustomize overlays rewrite most of the base. At that point the overlay is no longer a focused environment delta; it is a second copy of the application hidden behind patches. Teams fall into this when the base is too generic or when environments are not actually similar. The better alternative is to split bases by meaningful application shape or choose Helm if the variability is genuinely broad.

A third anti-pattern is treating Artifact Hub discovery as approval. Finding a chart does not mean it is safe for your cluster. Teams fall into this because package managers make installation feel routine. The better alternative is to render the manifests, review permissions, inspect maintenance signals, pin versions, and test upgrades in a non-production environment before depending on the package.

One more anti-pattern is hiding policy decisions inside application packages. For example, a chart that silently creates broad cluster-admin permissions for convenience teaches consumers to accept dangerous defaults. A Kustomize base that quietly adds privileged security context settings creates the same risk. Packaging should make policy decisions visible, documented, and reviewable, especially when the resource affects namespaces or workloads beyond one application.

## Decision Framework

Start with the ownership model. If one team owns the application and the environments, Kustomize is often enough because the same team can manage a base and overlays in one repository. If a platform team needs to distribute a reusable package to many teams, Helm is usually stronger because it provides values, chart versions, repositories, dependencies, and a familiar install or upgrade lifecycle.

Next, evaluate the kind of variation you need. If differences are mostly image tags, replica counts, labels, namespaces, resource requests, and small patches, Kustomize expresses those changes clearly. If differences include optional components, repeated object groups, conditional resources, dependencies, and many user-facing settings, Helm's templating model may be worth the extra complexity. The decision should follow the shape of the variability, not a team preference for one command.

Then decide how rollback and audit should work. If you want an application-level release history with install, upgrade, rollback, and uninstall commands, Helm gives you that model directly. If your organization already uses GitOps and treats Git commits as the release history, Kustomize overlays can fit cleanly because rollback is a Git revert plus reconciliation. Both are valid, but the team must be explicit about where release truth lives.

Finally, consider the debugging path under pressure. During an outage, an engineer needs to answer what changed and what the cluster received. Helm gives commands such as `helm get values`, `helm get manifest`, and `helm history`, while Kustomize gives directory diffs and generated overlay output. A mature team practices those commands before an incident, because packaging tools only help when operators know how to inspect their results.

Use Helm when the application is a product-like package, when many consumers need configurable installs, when dependencies matter, or when release rollback is a key requirement. Use Kustomize when you want plain Kubernetes resources, small environment-specific overlays, and Git-centered review. Use both only when each layer has a clear job, such as consuming an upstream chart and applying local organization policy overlays.

When you are unsure, write down the expected change process before choosing the tool. Who edits the shared application shape? Who edits environment values? Where is the reviewed rendered output stored, if anywhere? What command shows the current deployed package? What command or Git operation rolls back a bad change? The answers usually make the tool choice obvious because Helm and Kustomize place those responsibilities in different parts of the workflow.

## Did You Know?

- **Helm v3 removed Tiller in 2019** - Helm v2 required a server-side component named Tiller, but Helm v3 moved to a client-side architecture that aligns better with Kubernetes RBAC.
- **Kustomize has been built into kubectl since Kubernetes 1.14** - That means `kubectl apply -k` and the shorter `k apply -k` workflow are available without installing a separate Kustomize binary.
- **Helm charts have two version concepts** - `version` identifies the chart package, while `appVersion` usually identifies the application version the chart installs.
- **Artifact Hub indexes more than Helm charts** - It also lists OPA policies, Falco rules, OLM operators, and other cloud native artifacts that teams can evaluate before adoption.

## Common Mistakes

| Mistake | Why It Happens | How to Fix It |
|---------|----------------|---------------|
| Duplicating manifests for environments | Copying YAML feels faster during the first release, but later fixes must be repeated across many files. | Use Helm values or Kustomize overlays so shared structure changes in one place and environment differences remain intentional. |
| Building overly complex Helm templates | Teams keep adding conditionals and helper templates until nobody can predict the rendered manifest. | Keep the values surface small, render with `helm template`, and move unusual variants into separate charts when needed. |
| Not versioning charts | A chart without clear versions makes upgrades and rollback conversations vague. | Use semantic chart versions, pin dependencies, and document breaking changes for consumers. |
| Hardcoding secrets in values files or overlays | Packaging examples often need credentials, and teams copy placeholders into real workflows. | Store secret material in a dedicated secret-management system and keep packages limited to references, names, and wiring. |
| Applying before rendering | The command succeeds quickly, so teams skip reviewing the generated YAML. | Preview with `helm template`, `helm install --dry-run --debug`, or `k kustomize` before changing shared clusters. |
| Treating Artifact Hub packages as automatically trusted | Search results look official even when maintenance, permissions, or defaults need review. | Inspect maintainers, source repositories, values, RBAC, CRDs, and recent releases before installation. |
| Using Kustomize patches to replace the whole base | The base no longer represents common intent, and overlays become hidden copies. | Keep overlays small, split bases when application shapes diverge, or choose Helm for broad variability. |

## Quiz

<details><summary>1. Your team deploys the same API to dev, staging, and production, and each directory contains copied Deployment, Service, ConfigMap, and Ingress files. A readiness probe fix reached dev but not production. What packaging failure should you diagnose, and how would Helm or Kustomize reduce the risk?</summary>

The failure is accidental drift caused by copying raw manifests across environments. Helm would reduce the risk by keeping the Deployment structure in one template and moving environment differences into values files. Kustomize would reduce the risk by keeping the readiness probe in the base and changing only environment-specific fields in overlays. In either approach, reviewers can tell whether a difference is intentional instead of hunting through copied YAML.

</details>

<details><summary>2. A platform team wants to publish a reusable web-service package for ten product teams. Each consumer needs to set image, replicas, ingress host, resource requests, and optional Redis dependency. Would you recommend Helm or Kustomize, and what tradeoff should you explain?</summary>

Helm is the better fit because the platform team is distributing a versioned package to many consumers with a defined values surface and possible dependencies. Consumers can install or upgrade the chart with their own values without maintaining overlay directories that mirror the platform team's base. The tradeoff is that Helm templates can become harder to debug, so the team should document values clearly and teach consumers to render manifests before applying them.

</details>

<details><summary>3. A developer says Kustomize is safer because it has no templates, then proposes a production overlay that patches nearly every field in the Deployment. What would you challenge in that design?</summary>

The absence of templates does not automatically make a configuration safe or understandable. If the overlay rewrites most of the base, the base no longer communicates shared intent and the overlay behaves like a hidden copy. I would ask whether production is really the same application shape as the base, whether the base should be split, or whether Helm would better express the amount of variation. The fix is to keep overlays focused on intentional deltas.

</details>

<details><summary>4. A Helm upgrade changes an annotation used by cloud identity integration, and pods lose access to metrics. Which Helm inspection and recovery concepts matter most?</summary>

First inspect what changed by comparing rendered manifests, checking `helm get values`, and reviewing `helm get manifest` or chart diffs if your workflow records them. Helm release history matters because each upgrade creates a revision that can be rolled back with `helm rollback` if the previous revision is known good. The root lesson is that Helm tracks an application release across many resources, but teams still need to review generated YAML and chart release notes before upgrading.

</details>

<details><summary>5. Your organization uses GitOps, and each environment is reconciled from a different repository path. The app only varies by image tag, namespace, replica count, and resource requests. Which packaging approach is easiest to justify, and what command should reviewers use before merging?</summary>

Kustomize is easiest to justify because the variation is small and environment-specific, while Git already provides the release history and review trail. Reviewers should build the overlay with `k kustomize overlays/prod/` or the equivalent path used by the repository before merging. That preview shows the final Kubernetes objects, making it easier to catch unexpected names, labels, selectors, or resource changes before the GitOps controller applies them.

</details>

<details><summary>6. A teammate finds a PostgreSQL chart on Artifact Hub and wants to install it directly into production because it has many downloads. What evaluation steps should happen before adoption?</summary>

Downloads are a discovery signal, not an approval signal. The team should inspect maintainers, source repository, recent releases, chart values, Kubernetes version compatibility, RBAC permissions, CRDs, storage defaults, backup assumptions, and upgrade notes. They should render the manifests, test the install and upgrade path in a non-production environment, and pin the chart version. A package manager makes installation easier, but it does not replace supply-chain review.

</details>

<details><summary>7. A learner can explain Helm charts and Kustomize overlays but cannot decide which to use for a new internal service. What decision sequence should they apply?</summary>

They should start with ownership, then variation, then rollback, then debugging. If the same team owns the service and environments and the differences are small, Kustomize is likely enough. If the service must be distributed as a versioned package with many configurable settings or dependencies, Helm is likely stronger. They should also decide whether release truth lives in Helm release history or in Git history through a GitOps workflow.

</details>

## Hands-On Exercise

In this exercise, you will design a packaging workflow for a small web application without needing a live cluster. The goal is to practice the decisions an engineer makes before applying anything: define shared shape, choose the packaging model, preview generated manifests, and explain rollback. If you do have a Kubernetes 1.35 test cluster, the same commands can be adapted to apply a real Deployment and Service.

### Task 1: Define the shared application shape

Create a mental or local outline for a web service with a Deployment, Service, ConfigMap, and Ingress. Decide which fields are truly shared across dev and production, such as labels, ports, readiness probes, and Service selectors. Then decide which fields should vary, such as image tag, replica count, host name, resource requests, and database URL reference.

<details><summary>Solution guidance</summary>

The shared shape should include object kinds, stable labels, container ports, health probes, and Service selector logic. Environment differences should be limited to values that genuinely vary by environment. If the two environments need different object structures, call that out early because it may change whether a single base or chart is appropriate.

</details>

### Task 2: Choose Helm or Kustomize for the first implementation

Assume one product team owns the service and stores dev and production configuration in one Git repository. Choose either Helm values or Kustomize overlays, and write a short justification that mentions ownership, variation, rollback, and debugging. Your answer should include how you would preview generated manifests before any apply operation.

<details><summary>Solution guidance</summary>

Kustomize is a strong first choice if one team owns the service, the variation is small, and Git is already the release history. Helm is defensible if the team expects to distribute the package to other teams or manage dependencies. A complete answer mentions `k kustomize overlays/prod/` for Kustomize preview or `helm template` for Helm preview.

</details>

### Task 3: Add production-specific configuration safely

For a Kustomize answer, describe what belongs in `base/` and what belongs in `overlays/prod/`. For a Helm answer, describe what belongs in templates and what belongs in `prod-values.yaml`. Make sure the production database credential itself is not stored in the package, only referenced by name.

<details><summary>Solution guidance</summary>

In Kustomize, the base contains common resources and the production overlay changes image tag, replicas, namespace, host name, and resource requests. In Helm, templates contain the resource shape and `prod-values.yaml` supplies production inputs. In both cases, the package should reference a Secret or external-secret resource rather than embedding real credential material.

</details>

### Task 4: Diagnose a bad rollout plan before it reaches the cluster

Imagine review shows that production will change the image tag and also remove a readiness probe. Explain how you would catch that from rendered output and what conversation you would have with the author. Include one command using the `k` alias if your chosen design uses Kustomize.

<details><summary>Solution guidance</summary>

The rendered output should be reviewed before apply, using `k kustomize overlays/prod/` for Kustomize or `helm template my-release ./chart -f prod-values.yaml` for Helm. Removing a readiness probe is a structural change, not a normal production-only value change, so the author should explain why it is safe. If it was accidental drift, move the probe back into the shared base or template.

</details>

### Task 5: Plan rollback and ownership

Write down how rollback works for your chosen approach. If you chose Helm, include release history and `helm rollback`. If you chose Kustomize, include Git revert, GitOps reconciliation, and how you would confirm the overlay output after reverting. Then identify who owns future changes to shared structure.

<details><summary>Solution guidance</summary>

For Helm, rollback can use Helm release revisions, but the team should still understand what changed between chart and values versions. For Kustomize, rollback usually means reverting the Git change and letting the GitOps controller reconcile, or manually applying the previous overlay output in a controlled emergency. Ownership should be explicit so shared fields do not become casual environment patches.

</details>

### Success Criteria

- [ ] You separated shared Kubernetes object structure from environment-specific configuration.
- [ ] You justified Helm or Kustomize using ownership, variation, rollback, and debugging criteria.
- [ ] You included a preview step before applying generated manifests.
- [ ] You avoided storing real credentials in chart values, overlays, or examples.
- [ ] You described how to diagnose an unexpected rendered manifest change.
- [ ] You explained a rollback path that fits the packaging approach.

## Sources

- [Helm documentation: Using Helm](https://helm.sh/docs/intro/using_helm/)
- [Helm documentation: Charts](https://helm.sh/docs/topics/charts/)
- [Helm documentation: Chart Template Guide](https://helm.sh/docs/chart_template_guide/)
- [Helm command reference: install](https://helm.sh/docs/helm/helm_install/)
- [Helm command reference: upgrade](https://helm.sh/docs/helm/helm_upgrade/)
- [Helm command reference: rollback](https://helm.sh/docs/helm/helm_rollback/)
- [Kubernetes documentation: Declarative Management of Kubernetes Objects Using Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)
- [kubectl Kustomize reference: kustomization file](https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/)
- [kubectl command reference: apply](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_apply/kubectl_apply/)
- [Artifact Hub documentation](https://artifacthub.io/docs/)
- [CNCF project page: Helm](https://www.cncf.io/projects/helm/)
- [CNCF project page: Kustomize](https://www.cncf.io/projects/kustomize/)

## KCNA Curriculum Complete!

Congratulations. You have completed the entire KCNA curriculum covering the major domains that appear in the certification blueprint, including Kubernetes fundamentals, orchestration, cloud native architecture, observability, and application delivery. Treat this point as a transition from learning new concepts to practicing diagnosis, comparison, and scenario reasoning under exam timing.

| Part | Topic | Weight |
|------|-------|--------|
| Part 1 | Kubernetes Fundamentals | 44% |
| Part 2 | Container Orchestration | 28% |
| Part 3 | Cloud Native Architecture (incl. Observability) | 12% |
| Part 4 | Application Delivery | 16% |

Updated November 2025: Observability merged into Cloud Native Architecture, so application delivery should be studied alongside the monitoring and feedback loops that tell teams whether a packaged release behaved correctly.

## Next Module

You have completed the KCNA curriculum path. Use the [KCNA overview](/k8s/kcna/) to review weak areas, revisit the CNCF landscape, and prepare an exam practice plan.
