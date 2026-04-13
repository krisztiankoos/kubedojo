---
title: "Module 1.8: Namespaces and Labels"
slug: k8s/kcna/part1-kubernetes-fundamentals/module-1.8-namespaces-labels
sidebar:
  order: 9
---
> **Complexity**: `[QUICK]` - Organization concepts
>
> **Time to Complete**: 20-25 minutes
>
> **Prerequisites**: Modules 1.5-1.7

---

Imagine a warehouse with 10,000 boxes and no labels, no sections, and no organization system. Finding what you need would be impossible. That's exactly what a Kubernetes cluster would be like without namespaces and labels. In this module, we'll learn how to bring order to the chaos.

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Explain** how namespaces provide logical isolation and resource organization
2. **Choose the correct mechanism** (namespace, label, or annotation) given a scenario
3. **Compare** namespace-scoped and cluster-scoped resources
4. **Evaluate** label selector expressions used by Services, Deployments, and NetworkPolicies
5. **Write** a set-based selector expression

---

## Why This Module Matters

Namespaces and labels are how Kubernetes organizes resources. Labels enable Services to find Pods, Deployments to manage ReplicaSets, and operators to select resources. KCNA tests your understanding of these organizational primitives.

---

## Namespaces

To bring order to our chaotic warehouse, the first step is building distinct rooms or zones. In Kubernetes, we call these namespaces.

### What is a Namespace?

A **namespace** is a way to divide cluster resources between multiple users or teams. Think of them as virtual clusters backed by the same physical cluster:

```
┌─────────────────────────────────────────────────────────────┐
│              NAMESPACES                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   CLUSTER                            │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  Namespace: production                       │    │   │
│  │  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐          │    │   │
│  │  │  │ Pod │ │ Svc │ │ Dep │ │ CM  │          │    │   │
│  │  │  └─────┘ └─────┘ └─────┘ └─────┘          │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  Namespace: staging                          │    │   │
│  │  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐          │    │   │
│  │  │  │ Pod │ │ Svc │ │ Dep │ │ CM  │          │    │   │
│  │  │  └─────┘ └─────┘ └─────┘ └─────┘          │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  Namespace: development                      │    │   │
│  │  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐          │    │   │
│  │  │  │ Pod │ │ Svc │ │ Dep │ │ CM  │          │    │   │
│  │  │  └─────┘ └─────┘ └─────┘ └─────┘          │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Default Namespaces

Every cluster has these built-in namespaces:

| Namespace | Purpose |
|-----------|---------|
| **default** | Default namespace for resources without a specified namespace |
| **kube-system** | Kubernetes system components (API server, CoreDNS, etc.) |
| **kube-public** | Publicly readable resources (rarely used, mostly for cluster info) |
| **kube-node-lease** | Node heartbeat leases to track node health |

### What Namespaces Provide

```
┌─────────────────────────────────────────────────────────────┐
│              NAMESPACE BENEFITS                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. NAME SCOPING                                           │
│     • Same resource name in different namespaces: OK       │
│     • "backend" in production ≠ "backend" in staging      │
│                                                             │
│  2. ACCESS CONTROL                                         │
│     • RBAC can be namespace-scoped                         │
│     • "Team A can only access namespace-a"                 │
│                                                             │
│  3. RESOURCE QUOTAS                                        │
│     • Limit CPU/memory per namespace                       │
│     • Prevent one team from using all resources           │
│                                                             │
│  4. ORGANIZATION                                           │
│     • Logical separation of applications                   │
│     • Environments (dev/staging/prod)                     │
│     • Teams (team-a, team-b)                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **Pause and predict**: Two teams share the same Kubernetes cluster. Team A accidentally deploys a Pod named "backend" that conflicts with Team B's "backend" Pod. How could namespaces have prevented this, and what other isolation benefits would they provide?

### Namespace Strategy Trade-offs

How should you divide your cluster? Here are the most common real-world strategies:

| Strategy | Pros | Cons | Best For |
|----------|------|------|----------|
| **Namespace per Environment** (e.g., `dev`, `staging`, `prod`) | Simple to understand, easy to set global quotas. | Teams can step on each other's toes within the environment. | Small organizations with few engineering teams. |
| **Namespace per Team** (e.g., `team-frontend`, `team-data`) | Great isolation between teams, clear billing and RBAC. | Harder to separate production from dev traffic within the team. | Medium organizations where teams manage their own full stacks. |
| **Namespace per App/Env** (e.g., `payment-prod`, `payment-dev`) | Maximum granular control, tight blast radius. | Sprawl. You might end up managing hundreds of namespaces. | Large enterprises with complex, critical microservices. |

### What's NOT Namespaced

Not everything lives inside a namespace. Some resources are **cluster-scoped** (they exist globally across the entire cluster):

| Cluster-Scoped | Why |
|----------------|-----|
| **Nodes** | Physical/virtual machines are shared infrastructure. |
| **PersistentVolumes** | Storage assets represent cluster-wide capacity. |
| **Namespaces** | A namespace cannot contain another namespace. |
| **ClusterRoles** | Permissions that apply across all namespaces. |
| **StorageClasses** | Configurations for how storage is provisioned globally. |

> **Pause and predict**: List which of these 8 resources are cluster-scoped vs namespace-scoped: 1) Pod, 2) Node, 3) PersistentVolume, 4) ConfigMap, 5) Secret, 6) Namespace, 7) Service, 8) StorageClass.
> <details>
> <summary>Check your answer</summary>
> <strong>Namespace-scoped:</strong> Pod, ConfigMap, Secret, Service. These belong to specific applications or teams.<br>
> <strong>Cluster-scoped:</strong> Node, PersistentVolume, Namespace, StorageClass. These represent fundamental cluster infrastructure.
> </details>

---

## Labels

Now that we have rooms (namespaces), we need a way to categorize the individual boxes inside them. That's where labels come in. Think of labels as sticky notes, and label selectors as a database `WHERE` clause asking for all boxes with specific sticky notes.

### What are Labels?

**Labels** are key-value pairs attached to resources for identification:

```yaml
metadata:
  labels:
    app: frontend
    environment: production
    team: platform
    version: v2.1.0
```

Labels can be any key-value pair, you can attach multiple labels per resource, and most importantly, they are used by Kubernetes to **select and group** resources.

### How Labels are Used

Services, Deployments, and NetworkPolicies don't track Pods by their IP addresses or exact names (since Pods are ephemeral). Instead, they track them by labels.

```
┌─────────────────────────────────────────────────────────────┐
│              LABEL SELECTORS                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Service selecting Pods:                                   │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Service:                   Pods:                          │
│  selector:                  ┌─────────────────────┐        │
│    app: web                 │ labels:             │ ✓ Match│
│                             │   app: web          │        │
│                             │   env: prod         │        │
│                             └─────────────────────┘        │
│                             ┌─────────────────────┐        │
│                             │ labels:             │ ✓ Match│
│                             │   app: web          │        │
│                             │   env: staging      │        │
│                             └─────────────────────┘        │
│                             ┌─────────────────────┐        │
│                             │ labels:             │ ✗ No   │
│                             │   app: api          │        │
│                             │   env: prod         │        │
│                             └─────────────────────┘        │
│                                                             │
│  Only Pods with "app: web" are selected                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Label Selector Types

There are two ways to query these labels. We'll start with the simplest: equality-based.

```yaml
# EQUALITY-BASED (Simple exact match)
# Give me Pods where the 'app' label exactly equals 'frontend'
selector:
  app: frontend        

# Or using the formal matchLabels syntax:
selector:
  matchLabels:
    app: frontend
    env: production    # Must match BOTH (Logical AND)
```

Sometimes you need more complex logic. What if you want Pods from multiple environments, or want to exclude a specific environment? That requires set-based selectors.

```yaml
# SET-BASED (More powerful expressions)
selector:
  matchExpressions:
  - key: app
    operator: In
    values: [frontend, backend]    # App is EITHER frontend OR backend
  - key: env
    operator: NotIn
    values: [development]          # Env is NOT development
```

Operators available for set-based selectors are `In`, `NotIn`, `Exists` (key exists, regardless of value), and `DoesNotExist`.

> **Stop and think**: Write a `matchExpressions` selector that selects Pods where the `tier` is `cache` and the `environment` is NOT `production`.
> <details>
> <summary>Check your answer</summary>
> 
> ```yaml
> selector:
>   matchExpressions:
>   - key: tier
>     operator: In
>     values: [cache]
>   - key: environment
>     operator: NotIn
>     values: [production]
> ```
> </details>

---

## Annotations

Not all metadata is used for filtering and selecting. Sometimes you just need to attach detailed notes to a resource. This is the job of annotations.

### Labels vs Annotations

```
┌─────────────────────────────────────────────────────────────┐
│              LABELS vs ANNOTATIONS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LABELS:                       ANNOTATIONS:                │
│  ─────────────────────────────────────────────────────────  │
│  • For identification          • For metadata              │
│  • Used in selectors           • NOT used in selectors     │
│  • Short values                • Can be longer             │
│  • Meaningful to K8s           • For tools/humans          │
│                                                             │
│  Label example:                Annotation example:         │
│  labels:                       annotations:                │
│    app: frontend                 description: "Main web UI"│
│    version: v2                   git-commit: "abc123..."   │
│                                  contact: "team@example.com"│
│                                                             │
│  Use labels for:               Use annotations for:        │
│  • Selection                   • Build info                │
│  • Organization                • Contact info              │
│  • Grouping                    • Configuration hints       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **Pause and predict**: Label or annotation? Classify these 6 pieces of metadata: 1) `app=web`, 2) `git-commit=8a3f9b`, 3) `environment=staging`, 4) `build-date=2023-10-25`, 5) `tier=backend`, 6) `on-call-slack=#team-alpha`.
> <details>
> <summary>Check your answer</summary>
> <strong>Labels:</strong> 1, 3, 5. These are short, identifiable categories you would likely want to query or filter by.<br>
> <strong>Annotations:</strong> 2, 4, 6. These are longer, highly specific pieces of metadata useful for tooling or humans, but you would never use a Kubernetes selector to say "route traffic to the pod built on 2023-10-25".
> </details>

---

## Real-World Labeling Scheme

Kubernetes recommends a standard set of labels to keep things consistent across tools. Here is what a well-labeled Deployment looks like in the real world:

| Label | Purpose | Example |
|-------|---------|---------|
| `app.kubernetes.io/name` | Application name | `mysql` |
| `app.kubernetes.io/instance` | Unique instance | `mysql-prod-us-east` |
| `app.kubernetes.io/version` | Version | `5.7.21` |
| `app.kubernetes.io/component` | Architecture tier | `database` |
| `app.kubernetes.io/part-of` | Higher-level system | `ecommerce-platform` |
| `app.kubernetes.io/managed-by` | Provisioning tool | `helm` |

---

## How Services and Deployments Use Labels

Understanding how the "chain" of labels connects resources is crucial. 

```
┌─────────────────────────────────────────────────────────────┐
│              LABELS IN ACTION                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Deployment:                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  name: frontend                                      │   │
│  │  selector:                                           │   │
│  │    matchLabels:                                      │   │
│  │      app: frontend    ─────────┐                    │   │
│  │  template:                      │                    │   │
│  │    metadata:                    │                    │   │
│  │      labels:                    │ Must match!       │   │
│  │        app: frontend  ←────────┘                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Service:                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  name: frontend-service                              │   │
│  │  selector:                                           │   │
│  │    app: frontend      → Finds Pods with this label  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  The chain:                                                │
│  Deployment.selector → Pod template labels                │
│  Service.selector → Pod labels                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **Stop and think**: A Service uses the selector `app: frontend` to find its Pods. If you add a new label `version: v2` to some Pods but not others, will the Service still route traffic to all of them? What would happen if you changed the Service selector to require both `app: frontend` AND `version: v2`?

---

## Real-World War Story: The Silent Outage

It's 2 AM on a Friday. The production payment Service suddenly stops routing traffic. The Pods are running, the nodes are healthy, but zero requests are getting through. What happened? 

A junior developer updated the Payment Deployment. They wanted to signify that it was a new release, so they changed the Pod template label from `app: payment` to `app: payment-v2`. 

**The impact:** The existing Payment Service was still strictly looking for `app: payment`. Because the labels no longer matched, the Service instantly dropped all the Pods from its endpoints list. The Service was empty. A single label typo caused a 30-minute total outage. Labels are the glue of Kubernetes; if the glue fails, the pieces fall apart.

---

## Worked Example: Labeling a Microservices App End-to-End

Let's look at how we tie this all together for a two-tier application (Web UI and Redis Cache).

**Step 1: Define the Pods (via Deployment templates)**
* Web Pods get labels: `app: web`, `tier: frontend`, `env: prod`
* Redis Pods get labels: `app: redis`, `tier: backend`, `env: prod`

**Step 2: Connect the Services**
* The Web Service needs to balance traffic across the web Pods. 
  * Its selector is: `app: web`
* The Redis Service needs to point internal traffic to the cache.
  * Its selector is: `app: redis`

**Step 3: Secure with NetworkPolicies (Set-based)**
* We want to ensure ONLY the frontend can talk to Redis.
* We create a NetworkPolicy on the Redis Pods that allows ingress from:
  ```yaml
  matchExpressions:
  - key: tier
    operator: In
    values: [frontend]
  ```

By designing a consistent labeling scheme, networking, routing, and scaling all snap into place automatically.

---

## Did You Know?

- **Namespaces don't provide network isolation** - By default, Pods in different namespaces can communicate. Use NetworkPolicies for isolation.
- **Labels have length limits** - Keys can be up to 63 characters (253 with prefix). Values up to 63 characters.
- **You can query by labels** - `kubectl get pods -l app=frontend,env=prod` shows pods matching both labels.
- **Namespace names are DNS subdomains** - They must be lowercase, alphanumeric, with hyphens allowed.

---

## Common Mistakes

| Mistake | Why It Hurts | Specific Impact | Correct Understanding |
|---------|--------------|-----------------|----------------------|
| Thinking namespaces isolate network | Security risk | A compromised dev Pod can reach a prod database | Use NetworkPolicies for network isolation |
| Label key typos | Selectors don't match | **Service loses all backends, causing a total outage** | Double-check label names in Services/Deployments |
| Too few labels | Hard to organize/select | Cannot target specific environments or versions during rollouts | Use a consistent labeling scheme (like `app.kubernetes.io/*`) |
| Labels for long metadata | Wrong tool | Wastes API server resources; hits 63-character limit | Use annotations for descriptions, git hashes, and build info |

---

## Quiz

1. **Your company has three teams sharing one Kubernetes cluster. Team A complains that Team B accidentally deleted their ConfigMap because both teams named it "app-config" in the default namespace. How would you restructure the cluster to prevent this, and what additional protections could namespaces provide?**
   <details>
   <summary>Answer</summary>
   Create separate namespaces for each team (e.g., `team-a`, `team-b`, `team-c`). Namespaces provide name scoping, so both teams can have a ConfigMap called "app-config" without conflict. Additionally, apply RBAC so each team can only access their own namespace, and set ResourceQuotas to prevent any single team from consuming all cluster resources. Namespaces are the primary organizational unit for multi-team clusters.
   </details>

2. **A new engineer wants to set resource quotas on Nodes to limit how much CPU each physical server can allocate. Why won't this work with namespace-level ResourceQuotas, and what type of resource are Nodes?**
   <details>
   <summary>Answer</summary>
   Nodes are cluster-scoped resources, not namespace-scoped. ResourceQuotas only apply within namespaces and control resources like Pods, Services, ConfigMaps, and compute requests/limits. Since Nodes exist outside of any namespace (they are physical or virtual machines shared by the entire cluster), they cannot be managed by namespace-level quotas. Other cluster-scoped resources include PersistentVolumes, ClusterRoles, and Namespaces themselves.
   </details>

3. **You need to create a NetworkPolicy that selects Pods from either the 'frontend' or 'api' tier, but strictly excludes any Pods marked as 'experimental'. Which selector mechanism is required for this scenario?**
   <details>
   <summary>Answer</summary>
   You must use a set-based selector with `matchExpressions`. An equality-based selector (`matchLabels`) only supports exact logical AND matches. To satisfy "EITHER frontend OR api" and "NOT experimental", you would write an expression using the `In` operator for `[frontend, api]` and the `NotIn` operator for `[experimental]`.
   </details>

4. **Your team stores build timestamps, Git commit hashes, and team contact emails on Kubernetes resources. A colleague puts all of these as labels. What problem might this cause, and what should they use instead for some of this metadata?**
   <details>
   <summary>Answer</summary>
   Labels have a 63-character value limit and are indexed by the API server, so using them for long or frequently changing metadata wastes resources and can hit length limits (Git commit hashes are 40+ characters). More importantly, labels are meant for identification and selection by Kubernetes -- using them for metadata that no selector will ever query is wasteful. Git commit hashes, build timestamps, and contact emails should be stored as annotations, which can hold longer values and are designed for tool and human metadata rather than selection.
   </details>

5. **A security engineer says "we put our teams in separate namespaces, so they are isolated from each other." Is this statement fully correct? What critical piece might be missing?**
   <details>
   <summary>Answer</summary>
   This is only partially correct. Namespaces provide name scoping and can be used with RBAC for access control and ResourceQuotas for resource limits, but they do NOT provide network isolation by default. Pods in different namespaces can still communicate freely over the network. To achieve true network isolation, you must apply NetworkPolicies that restrict cross-namespace traffic. Without NetworkPolicies, a compromised Pod in one namespace can reach any Pod in any other namespace.
   </details>

---

## Summary

**Namespaces**:
- Divide cluster resources (like rooms in a warehouse)
- Provide name scoping
- Enable RBAC and quotas
- Don't isolate network (use NetworkPolicies)

**Labels**:
- Key-value pairs for identification (like sticky notes)
- Used by selectors (Services, Deployments)
- Enable organization and selection

**Annotations**:
- Key-value pairs for metadata
- NOT used for selection
- For tools, humans, longer descriptions

**Common patterns**:
- `app`, `environment`, `version` labels
- Namespaces per team or environment
- Consistent labeling across resources

---

## Part 1 Complete!

You've finished **Kubernetes Fundamentals** (46% of the exam). You now understand:
- What Kubernetes is and why it exists
- Containers and how they work
- Control plane and node components
- Pods, Deployments, ReplicaSets
- Services and discovery
- Namespaces and labels

**Next Part**: [Part 2: Container Orchestration](/k8s/kcna/part2-container-orchestration/module-2.1-scheduling/) - How Kubernetes manages workloads at scale.