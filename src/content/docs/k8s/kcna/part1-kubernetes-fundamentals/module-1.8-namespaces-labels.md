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

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Explain** how namespaces provide logical isolation and resource organization
2. **Identify** when to use namespaces vs. labels vs. annotations for different purposes
3. **Compare** namespace-scoped and cluster-scoped resources
4. **Evaluate** label selector expressions used by Services, Deployments, and NetworkPolicies

---

## Why This Module Matters

Namespaces and labels are how Kubernetes organizes resources. Labels enable Services to find Pods, Deployments to manage ReplicaSets, and operators to select resources. KCNA tests your understanding of these organizational primitives.

---

## Namespaces

### What is a Namespace?

A **namespace** is a way to divide cluster resources between multiple users or teams:

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
| **default** | Default namespace for resources without namespace |
| **kube-system** | Kubernetes system components (API server, etc.) |
| **kube-public** | Publicly readable resources (rarely used) |
| **kube-node-lease** | Node heartbeat leases |

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

### What's NOT Namespaced

Some resources are **cluster-scoped** (exist across all namespaces):

| Cluster-Scoped | Why |
|----------------|-----|
| **Nodes** | Physical/virtual machines |
| **PersistentVolumes** | Storage is cluster-wide |
| **Namespaces** | They contain other resources |
| **ClusterRoles** | Cluster-wide permissions |
| **StorageClasses** | Storage configurations |

---

## Labels

### What are Labels?

**Labels** are key-value pairs attached to resources for identification:

```
┌─────────────────────────────────────────────────────────────┐
│              LABELS                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Labels are arbitrary metadata:                            │
│                                                             │
│  metadata:                                                 │
│    labels:                                                 │
│      app: frontend                                         │
│      environment: production                               │
│      team: platform                                        │
│      version: v2.1.0                                       │
│                                                             │
│  Labels can be:                                            │
│  • Any key-value pair                                      │
│  • Multiple labels per resource                            │
│  • Used for selection                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### How Labels are Used

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
│  Only Pods with "app: web" are selected                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Label Selector Types

```
┌─────────────────────────────────────────────────────────────┐
│              SELECTOR TYPES                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  EQUALITY-BASED:                                           │
│  ─────────────────────────────────────────────────────────  │
│  selector:                                                 │
│    app: frontend        # app equals frontend              │
│                                                             │
│  Or using matchLabels:                                     │
│  selector:                                                 │
│    matchLabels:                                            │
│      app: frontend                                         │
│      env: production                                       │
│                                                             │
│  SET-BASED (more powerful):                                │
│  ─────────────────────────────────────────────────────────  │
│  selector:                                                 │
│    matchExpressions:                                       │
│    - key: app                                              │
│      operator: In                                          │
│      values: [frontend, backend]                          │
│    - key: env                                              │
│      operator: NotIn                                       │
│      values: [development]                                │
│                                                             │
│  Operators: In, NotIn, Exists, DoesNotExist               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Annotations

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

---

> **Stop and think**: A Service uses the selector `app: frontend` to find its Pods. If you add a new label `version: v2` to some Pods but not others, will the Service still route traffic to all of them? What would happen if you changed the Service selector to require both `app: frontend` AND `version: v2`?

## Common Label Conventions

Kubernetes recommends these standard labels:

| Label | Purpose | Example |
|-------|---------|---------|
| `app.kubernetes.io/name` | Application name | `mysql` |
| `app.kubernetes.io/instance` | Instance name | `mysql-prod` |
| `app.kubernetes.io/version` | Version | `5.7.21` |
| `app.kubernetes.io/component` | Component | `database` |
| `app.kubernetes.io/part-of` | Higher-level app | `wordpress` |
| `app.kubernetes.io/managed-by` | Managing tool | `helm` |

---

## How Services, Deployments Use Labels

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

---

## Did You Know?

- **Namespaces don't provide network isolation** - By default, Pods in different namespaces can communicate. Use NetworkPolicies for isolation.

- **Labels have length limits** - Keys can be up to 63 characters (253 with prefix). Values up to 63 characters.

- **You can query by labels** - `kubectl get pods -l app=frontend,env=prod` shows pods matching both labels.

- **Namespace names are DNS subdomains** - They must be lowercase, alphanumeric, with hyphens allowed.

---

## Common Mistakes

| Mistake | Why It Hurts | Correct Understanding |
|---------|--------------|----------------------|
| Thinking namespaces isolate network | Security risk | Use NetworkPolicies for isolation |
| Label key typos | Selectors don't match | Double-check label names |
| Too few labels | Hard to organize/select | Use consistent labeling scheme |
| Labels for long metadata | Wrong tool | Use annotations for descriptions |

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

3. **A Deployment has the selector `matchLabels: {app: api, version: v2}`, but its Pod template only has the label `app: api`. What will happen when you try to create this Deployment?**
   <details>
   <summary>Answer</summary>
   The Deployment will fail validation. The Deployment's selector must match the labels in its Pod template. Since the template is missing the `version: v2` label, the selector would never match the Pods it creates, which makes no sense. Kubernetes requires that the selector matches the template labels to ensure the Deployment can manage its own Pods. You must either add `version: v2` to the Pod template labels or remove it from the selector.
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
- Divide cluster resources
- Provide name scoping
- Enable RBAC and quotas
- Don't isolate network (use NetworkPolicies)

**Labels**:
- Key-value pairs for identification
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

**Next Part**: [Part 2: Container Orchestration](../part2-container-orchestration/module-2.1-scheduling/) - How Kubernetes manages workloads at scale.
