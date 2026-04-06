---
title: "Module 3.2: RBAC Fundamentals"
slug: k8s/kcsa/part3-security-fundamentals/module-3.2-rbac
sidebar:
  order: 3
---
> **Complexity**: `[MEDIUM]` - Core knowledge
>
> **Time to Complete**: 30-35 minutes
>
> **Prerequisites**: [Module 3.1: Pod Security](../module-3.1-pod-security/)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Evaluate** RBAC policies for over-permissioned roles and privilege escalation risks
2. **Assess** whether a given Role or ClusterRole follows the principle of least privilege
3. **Identify** dangerous RBAC patterns: wildcard verbs, cluster-admin bindings, escalation paths
4. **Explain** how Roles, ClusterRoles, RoleBindings, and ClusterRoleBindings interact

---

## Why This Module Matters

RBAC (Role-Based Access Control) is Kubernetes' primary authorization mechanism. It determines who can do what in your cluster. Misconfigured RBAC is one of the most common security issues in Kubernetes—either too permissive (security risk) or too restrictive (operational issues).

Consider a real-world scenario: A company's CI/CD pipeline was hijacked because a developer granted a ServiceAccount a wildcard `*` verb on all resources to "make the deployment work." An attacker compromised the CI/CD pipeline container, discovered the ServiceAccount token, and used those wildcard permissions to deploy a privileged daemonset across the entire cluster, taking over all nodes. What started as a shortcut became a full cluster compromise.

Understanding RBAC is essential for both the exam and real-world Kubernetes administration to prevent these exact scenarios.

---

## RBAC Concepts

Think of RBAC like a corporate office security system:
- **Roles** are like **security badges** programmed for specific access (e.g., "Can open doors on the 3rd floor").
- **Subjects** are the **employees or contractors** who need access.
- **RoleBindings** are the act of **handing that specific badge to an employee**.

Just like an employee cannot enter a room without a programmed badge, a subject in Kubernetes cannot perform an action without a bound Role.

```
┌─────────────────────────────────────────────────────────────┐
│              RBAC BUILDING BLOCKS                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  WHO                           WHAT                        │
│  (Subjects)                    (Rules)                     │
│  ┌─────────────┐              ┌─────────────┐              │
│  │ Users       │              │ Verbs       │              │
│  │ Groups      │              │ Resources   │              │
│  │ ServiceAccts│              │ API Groups  │              │
│  └──────┬──────┘              └──────┬──────┘              │
│         │                            │                      │
│         │         BINDING            │                      │
│         │      (Connection)          │                      │
│         │     ┌───────────┐          │                      │
│         └────→│ Role      │←─────────┘                      │
│               │ Binding   │                                 │
│               └───────────┘                                 │
│                                                             │
│  Role = Collection of permissions (verbs on resources)     │
│  Binding = Connects subjects to roles                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Roles vs ClusterRoles

```
┌─────────────────────────────────────────────────────────────┐
│              ROLE SCOPE                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ROLE (Namespace-scoped)                                   │
│  ├── Defines permissions within a single namespace         │
│  ├── Can only reference namespace-scoped resources         │
│  └── Bound with RoleBinding                                │
│                                                             │
│  CLUSTERROLE (Cluster-scoped)                              │
│  ├── Defines permissions cluster-wide                      │
│  ├── Can reference any resource (including cluster-wide)   │
│  ├── Can be bound with:                                    │
│  │   ├── ClusterRoleBinding (cluster-wide access)          │
│  │   └── RoleBinding (namespace-scoped access)             │
│  └── Used for cluster-wide resources or reusable roles     │
│                                                             │
│  WHEN TO USE WHAT:                                         │
│  • Single namespace permissions → Role + RoleBinding       │
│  • Same role in multiple namespaces → ClusterRole +        │
│    RoleBinding per namespace                               │
│  • Cluster-wide permissions → ClusterRole +                │
│    ClusterRoleBinding                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Stop and think**: If RBAC only allows additive permissions (no deny rules), how would you prevent a specific user from accessing Secrets in a namespace where they have a broad Role?

## Role Definition

```yaml
# Namespace-scoped Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: pod-reader
rules:
- apiGroups: [""]           # "" = core API group
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

```yaml
# Cluster-scoped ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
- apiGroups: [""]
  resources: ["nodes"]      # Cluster-scoped resource
  verbs: ["get", "watch", "list"]
```

### Rule Components

| Component | Description | Examples |
|-----------|-------------|----------|
| **apiGroups** | API group containing resource | `""` (core), `"apps"`, `"networking.k8s.io"` |
| **resources** | Resource types | `"pods"`, `"deployments"`, `"secrets"` |
| **verbs** | Actions allowed | `"get"`, `"list"`, `"create"`, `"delete"` |
| **resourceNames** | Specific resource names (optional) | `["my-configmap"]` |

### Common Verbs

```
┌─────────────────────────────────────────────────────────────┐
│              RBAC VERBS                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  READ OPERATIONS                                           │
│  ├── get      - Read a single resource                     │
│  ├── list     - List all resources                         │
│  └── watch    - Watch for changes                          │
│                                                             │
│  WRITE OPERATIONS                                          │
│  ├── create   - Create new resources                       │
│  ├── update   - Update existing resources                  │
│  ├── patch    - Partially update resources                 │
│  └── delete   - Delete resources                           │
│                                                             │
│  SPECIAL VERBS                                             │
│  ├── deletecollection - Delete multiple resources          │
│  ├── bind     - Bind roles (for RoleBindings)              │
│  ├── escalate - Modify roles (requires special permission) │
│  ├── impersonate - Act as another user                     │
│  └── * (wildcard) - All verbs (DANGEROUS)                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Role Bindings

```yaml
# Binds Role to users/groups in a namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: production
subjects:
- kind: User
  name: alice
  apiGroup: rbac.authorization.k8s.io
- kind: Group
  name: developers
  apiGroup: rbac.authorization.k8s.io
- kind: ServiceAccount
  name: my-app
  namespace: production
roleRef:
  kind: Role                    # or ClusterRole
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

```yaml
# Cluster-wide binding
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-nodes-everywhere
subjects:
- kind: Group
  name: operations
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: node-reader
  apiGroup: rbac.authorization.k8s.io
```

---

## Built-in Roles

Kubernetes includes default ClusterRoles:

```
┌─────────────────────────────────────────────────────────────┐
│              BUILT-IN CLUSTERROLES                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  USER-FACING ROLES                                         │
│                                                             │
│  cluster-admin                                             │
│  ├── Full access to everything                             │
│  ├── Can do anything in any namespace                      │
│  └── DANGEROUS - use sparingly                             │
│                                                             │
│  admin                                                     │
│  ├── Full access within a namespace                        │
│  ├── Can create roles/bindings in namespace                │
│  └── Use for namespace administrators                      │
│                                                             │
│  edit                                                      │
│  ├── Read/write to most namespace resources                │
│  ├── Cannot view or modify roles/bindings                  │
│  └── Use for developers                                    │
│                                                             │
│  view                                                      │
│  ├── Read-only access to most namespace resources          │
│  ├── Cannot see secrets                                    │
│  └── Use for auditors, observers                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### System Roles

```
┌─────────────────────────────────────────────────────────────┐
│              SYSTEM CLUSTERROLES                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  system:* roles are for Kubernetes components              │
│                                                             │
│  system:kube-scheduler                                     │
│  └── Permissions for the scheduler                         │
│                                                             │
│  system:kube-controller-manager                            │
│  └── Permissions for controller manager                    │
│                                                             │
│  system:node                                               │
│  └── Permissions for kubelets (with Node authorization)    │
│                                                             │
│  system:masters group                                      │
│  └── Bound to cluster-admin (full access)                  │
│  └── Certificate O=system:masters = cluster-admin          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## RBAC Best Practices

### Least Privilege

```
┌─────────────────────────────────────────────────────────────┐
│              LEAST PRIVILEGE RBAC                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  BAD: Overly permissive                                    │
│  rules:                                                    │
│  - apiGroups: ["*"]        # All API groups                │
│    resources: ["*"]        # All resources                 │
│    verbs: ["*"]            # All actions                   │
│                                                             │
│  GOOD: Precisely scoped                                    │
│  rules:                                                    │
│  - apiGroups: [""]                                         │
│    resources: ["pods"]                                     │
│    verbs: ["get", "list"]                                  │
│  - apiGroups: [""]                                         │
│    resources: ["pods/log"]                                 │
│    verbs: ["get"]                                          │
│                                                             │
│  GUIDELINES:                                               │
│  • Use namespace-scoped roles when possible                │
│  • Avoid wildcards (*)                                     │
│  • Grant specific verbs, not ["*"]                         │
│  • Prefer RoleBinding over ClusterRoleBinding              │
│  • Review and audit regularly                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **Pause and predict**: A ServiceAccount has `create` permission on Pods but not on Secrets. Can it still access secrets in the namespace? Think about what a newly created pod can do.

### Dangerous Permissions

```
┌─────────────────────────────────────────────────────────────┐
│              DANGEROUS RBAC PERMISSIONS                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PRIVILEGE ESCALATION RISKS:                               │
│                                                             │
│  CREATE pods                                               │
│  └── Can create privileged pods, escape to host            │
│                                                             │
│  CREATE/UPDATE roles/rolebindings                          │
│  └── Can grant themselves more permissions                 │
│                                                             │
│  GET secrets                                               │
│  └── Can read all secrets (tokens, passwords)              │
│                                                             │
│  IMPERSONATE users/groups                                  │
│  └── Can act as any user                                   │
│                                                             │
│  EXEC into pods                                            │
│  └── Can run commands in any container                     │
│                                                             │
│  CREATE serviceaccounts + secrets                          │
│  └── Can create tokens for any service account             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ServiceAccount RBAC

```yaml
# Create a ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  namespace: production
---
# Create a Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: configmap-reader
  namespace: production
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]
---
# Bind the Role to the ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-configmap-reader
  namespace: production
subjects:
- kind: ServiceAccount
  name: my-app
  namespace: production
roleRef:
  kind: Role
  name: configmap-reader
  apiGroup: rbac.authorization.k8s.io
---
# Use the ServiceAccount in a Pod
apiVersion: v1
kind: Pod
metadata:
  name: my-app
  namespace: production
spec:
  serviceAccountName: my-app
  # ...
```

---

## Aggregated ClusterRoles

ClusterRoles can aggregate other ClusterRoles:

```yaml
# ClusterRole with aggregation rule
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring-endpoints
  labels:
    rbac.example.com/aggregate-to-monitoring: "true"
rules:
- apiGroups: [""]
  resources: ["pods", "services", "endpoints"]
  verbs: ["get", "list", "watch"]
---
# Aggregating ClusterRole (combines all matching)
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring
aggregationRule:
  clusterRoleSelectors:
  - matchLabels:
      rbac.example.com/aggregate-to-monitoring: "true"
# Rules are automatically combined from aggregated roles
rules: []  # Populated by controller
```

The built-in `admin`, `edit`, and `view` roles use aggregation.

> **Stop and think**: Aggregated ClusterRoles automatically include rules from any ClusterRole with a matching label. What security risk does this introduce if an attacker can create ClusterRoles with arbitrary labels?

---

## Did You Know?

- **RBAC is default-deny** - if no role grants permission, the action is denied. There's no "deny" rule in RBAC.

- **Role escalation protection** - you can't grant permissions you don't have. To create a RoleBinding to a Role, you need either (a) the `bind` verb on that role, or (b) all the permissions in that role.

- **The `view` role doesn't include secrets** by design. This lets you give broad read access without exposing sensitive data.

- **Wildcards aggregate** - using `resources: ["*"]` grants access to resources that don't exist yet (future CRDs).

---

## Common Mistakes

| Mistake | Why It Hurts | Solution |
|---------|--------------|----------|
| Using cluster-admin for apps | Way too much access | Create specific roles |
| Wildcards in production | Grants more than intended | Specify exact resources/verbs |
| ClusterRoleBinding for namespaced needs | Cluster-wide access when namespace is enough | Use RoleBinding |
| Not reviewing default SA | May have unintended permissions | Audit default SA bindings |
| Shared roles for different teams | Can't revoke individually | Team-specific roles |

---

## Quiz

1. **A new development team needs read access to Deployments and Services across exactly five namespaces. Should you create five separate Roles or one ClusterRole? What binding strategy would you use, and why?**
   <details>
   <summary>Answer</summary>
   Create one ClusterRole with `get`, `list`, and `watch` verbs on Deployments and Services, then create five RoleBindings (one per namespace) referencing that ClusterRole. This approach avoids duplicating the identical Role definition across multiple namespaces while keeping access strictly scoped to only the five required namespaces. Using a ClusterRoleBinding in this scenario would be incorrect, as it would unnecessarily grant cluster-wide access to all namespaces. The RoleBinding to a ClusterRole pattern gives you highly reusable permission definitions without sacrificing precise namespace-scoped access control. It keeps your RBAC configuration DRY (Don't Repeat Yourself) and much easier to audit.
   </details>

2. **During a security audit, you discover a ServiceAccount with `create` permission on Pods and `get` permission on Secrets. The team says they need pod creation for their CI/CD pipeline. Explain the privilege escalation risk and propose a safer approach.**
   <details>
   <summary>Answer</summary>
   With `create pods` permission, the CI/CD ServiceAccount can simply create a pod that mounts any secret in the namespace as a volume, effectively escalating from reading specific secrets to reading all secrets. It could also create privileged pods that mount the host filesystem, enabling a full container escape and node compromise. To mitigate this risk, you should use a dedicated namespace for CI/CD containing only the specific secrets it actually requires to operate. Additionally, you must enforce Pod Security Standards (Restricted) to prevent the creation of privileged pods or host mounts in that namespace. Finally, restrict the ServiceAccount to only `create` higher-level resources like Deployments instead of raw Pods, ensuring that admission controllers can properly validate the pod templates before creation.
   </details>

3. **The built-in `view` ClusterRole deliberately excludes access to Secrets. A developer binds `view` to their ServiceAccount but later requests and receives a second Role granting `get secrets`. What is the resulting effective permission, and what RBAC principle does this demonstrate?**
   <details>
   <summary>Answer</summary>
   The ServiceAccount will effectively receive both the broad `view` permissions AND the `get secrets` permission because Kubernetes RBAC is strictly additive. There are no deny rules in Kubernetes RBAC, meaning the union of all granted permissions across all bindings always applies to the subject. This scenario demonstrates why you must comprehensively audit all bindings for a subject, rather than looking at individual roles in isolation to determine access. The `view` ClusterRole's exclusion of secrets is merely a design choice for that specific role, not a hard enforcement mechanism across the entire cluster. Any additional Role or ClusterRole binding will successfully override this intent, highlighting the critical need to carefully restrict who is allowed to create RoleBindings.
   </details>

4. **A cluster has 30 namespaces. You need to grant an automated monitoring tool read-only access to pods, services, and endpoints in ALL namespaces. Compare two approaches: (a) a ClusterRoleBinding to a ClusterRole, vs (b) 30 RoleBindings to a ClusterRole. When would you choose each?**
   <details>
   <summary>Answer</summary>
   Approach (a) is operationally simpler because a single ClusterRoleBinding automatically covers all current namespaces and any future namespaces created later. You should choose this method when the monitoring tool legitimately needs absolute, cluster-wide access and is highly trusted by the administration team. Approach (b) requires manually maintaining 30 separate RoleBindings, but it provides explicit, granular control over access boundaries. You should choose the multiple RoleBinding approach when certain namespaces contain highly sensitive workloads that the monitoring tool should absolutely not access under any circumstances. The fundamental trade-off here is operational simplicity versus strict security granularity and adherence to the principle of least privilege.
   </details>

5. **You want to prevent a specific group of contractors from ever being granted the `cluster-admin` role. Since RBAC has no explicit deny rules, what strategies could you use to enforce this strict policy?**
   <details>
   <summary>Answer</summary>
   Since Kubernetes RBAC is additive-only, you cannot create a rule that explicitly denies permissions to a subject within the RBAC system itself. To enforce this policy, you must rely on external mechanisms like an admission controller (such as Kyverno or OPA Gatekeeper) to intercept and block the creation of ClusterRoleBindings that reference the `cluster-admin` role for that specific group. Additionally, you should strictly restrict which users possess the `create` and `update` verbs on `clusterrolebindings` to minimize the overall attack surface. You can also implement a rigorous policy-as-code approach where all RBAC manifests must be reviewed in a Git repository before being applied to the cluster. Finally, utilizing audit logging to trigger immediate alerts when high-privilege bindings are created can ensure rapid remediation if your preventative controls ever fail.
   </details>

---

## Hands-On Exercise: RBAC Design

**Scenario**: Design RBAC for a development team with these requirements:

1. Developers can view all resources in the `dev` namespace
2. Developers can create/update/delete Deployments and Services in `dev`
3. Team lead can do everything developers can, plus manage ConfigMaps and Secrets
4. CI/CD service account needs to deploy to `staging` namespace

**Create the RBAC resources:**

<details>
<summary>Solution</summary>

```yaml
# Developer Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: dev
  name: developer
rules:
- apiGroups: [""]
  resources: ["*"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["create", "update", "patch", "delete"]
- apiGroups: [""]
  resources: ["services"]
  verbs: ["create", "update", "patch", "delete"]
---
# Team Lead Role (extends developer)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: dev
  name: team-lead
rules:
- apiGroups: [""]
  resources: ["*"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["create", "update", "patch", "delete"]
- apiGroups: [""]
  resources: ["services", "configmaps", "secrets"]
  verbs: ["create", "update", "patch", "delete"]
---
# CI/CD Role for staging
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: staging
  name: deployer
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
- apiGroups: [""]
  resources: ["services", "configmaps"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
---
# Bindings
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: dev
  name: developers-binding
subjects:
- kind: Group
  name: developers
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: developer
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: dev
  name: team-lead-binding
subjects:
- kind: User
  name: lead@example.com
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: team-lead
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: staging
  name: cicd-binding
subjects:
- kind: ServiceAccount
  name: cicd-deployer
  namespace: cicd
roleRef:
  kind: Role
  name: deployer
  apiGroup: rbac.authorization.k8s.io
```

</details>

---

## Summary

RBAC is Kubernetes' authorization system:

| Component | Purpose | Scope |
|-----------|---------|-------|
| **Role** | Define permissions | Namespace |
| **ClusterRole** | Define permissions | Cluster |
| **RoleBinding** | Grant role to subjects | Namespace |
| **ClusterRoleBinding** | Grant role to subjects | Cluster |

Best practices:
- Follow least privilege
- Avoid wildcards (`*`)
- Prefer namespace-scoped roles
- Be careful with pod create, secrets access, and impersonation
- Audit RBAC regularly

---

## Next Module

[Module 3.3: Secrets Management](../module-3.3-secrets/) - How to securely handle sensitive data in Kubernetes.