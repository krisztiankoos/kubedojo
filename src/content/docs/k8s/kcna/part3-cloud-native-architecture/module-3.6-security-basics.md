---
title: "Module 3.6: Security Basics (Theory)"
slug: k8s/kcna/part3-cloud-native-architecture/module-3.6-security-basics
sidebar:
  order: 7
---

> **Complexity**: `[QUICK]` - Foundations only
>
> **Time to Complete**: 20-25 minutes
>
> **Prerequisites**: Modules 3.1-3.5 (Cloud Native Architecture)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Explain** the key Kubernetes security concepts: RBAC, NetworkPolicies, Secrets, and Pod Security Standards
2. **Identify** common security misconfigurations that lead to real-world breaches
3. **Compare** authentication, authorization, and admission control as layers of API security
4. **Evaluate** whether a given cluster configuration follows security best practices

---

## Why This Module Matters

In February 2018, security researchers discovered that Tesla's Kubernetes dashboard was publicly accessible with no authentication. Attackers had slipped in, deployed cryptocurrency mining containers across Tesla's cloud infrastructure, and hid the evidence by keeping CPU usage artificially low. The breach was not caused by a sophisticated zero-day exploit. It was caused by a missing password on an admin console.

This incident illustrates a pattern that repeats across the industry: most Kubernetes security failures come from misconfiguration, not from advanced attacks. Default settings left unchanged, overly permissive access controls, and unvetted container images account for the vast majority of real-world breaches.

This module gives you the conceptual foundation to understand Kubernetes security. You will not configure anything here -- that is for higher-level certifications like CKS and KCSA. Instead, you will learn the mental model that makes all of those hands-on skills make sense.

---

## The Three Gates: A Building Security Analogy

Imagine entering a secure office building. You pass through three checkpoints, and each one catches a different category of threat.

```
THE THREE SECURITY GATES

  YOU ──► GATE 1 ──► GATE 2 ──► GATE 3 ──► INSIDE
          Badge       Bag Check   Seatbelt

  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
  │   GATE 1:      │  │   GATE 2:      │  │   GATE 3:      │
  │   BADGE         │  │   BAG CHECK    │  │   SEATBELT     │
  │                │  │                │  │                │
  │ "Who are you?" │  │ "What are you  │  │ "What can you  │
  │ "What can you  │  │  bringing in?" │  │  do once        │
  │  access?"      │  │                │  │  inside?"      │
  │                │  │                │  │                │
  │ K8s: API Auth  │  │ K8s: Image     │  │ K8s: Pod       │
  │ & RBAC         │  │ trust, scans,  │  │ Security,      │
  │                │  │ provenance     │  │ NetworkPolicy  │
  └────────────────┘  └────────────────┘  └────────────────┘
```

**Gate 1 -- Badge (Identity & Access)**: Your badge determines who you are and which doors you can open. In Kubernetes, this involves authenticating your identity and using RBAC to control which actions you can perform on which resources.

**Gate 2 -- Bag Check (Image Trust)**: Security scans your bag before you enter. In Kubernetes, image scanning and provenance verification ensure that only trusted, vulnerability-free software runs in your cluster.

**Gate 3 -- Seatbelt (Runtime Safety)**: Once inside, seatbelts, fire exits, and safety rules limit the damage if something goes wrong. In Kubernetes, Pod Security Standards and NetworkPolicies restrict what containers can do and who they can talk to.

Each gate is independent. A failure at any single gate can lead to a breach, even if the other two are solid. Defense in depth means all three must be in place.

---

## Gate 1: Identity and Access Control

### The API Request Lifecycle

Before diving into permissions, it is crucial to understand the three stages every request to the Kubernetes API must pass through. Think of this as the complete security checkpoint at Gate 1:

1. **Authentication (AuthN)**: *Who are you?* Kubernetes verifies your identity using certificates, bearer tokens, or external identity providers (like OIDC). If it cannot identify you, the request is rejected immediately with a `401 Unauthorized`.
2. **Authorization (AuthZ)**: *Are you allowed to do this?* Once identified, Kubernetes checks if you have the right permissions. This is where **RBAC** (Role-Based Access Control) lives. If you lack permission, the request gets a `403 Forbidden`.
3. **Admission Control**: *Is this request safe and well-formed?* Even if you are authenticated and authorized to create a Pod, Admission Controllers can intercept the request to mutate it (e.g., automatically inject a sidecar container) or validate it (e.g., reject it if it violates a security policy). 

These three layers work together to protect the cluster's control plane.

### Subjects, Roles, and Bindings (RBAC)

Role-Based Access Control (RBAC) is the primary authorization mechanism in Kubernetes. 

```
RBAC FLOW

  SUBJECT              BINDING              ROLE               RESOURCE
  (who)                (glue)               (permissions)      (what)

  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐
  │ User     │    │              │    │ Role         │    │ Pods     │
  │ Group    │───►│ RoleBinding  │───►│ (namespace)  │───►│ Secrets  │
  │ Service  │    │ or Cluster   │    │ or Cluster   │    │ ConfigMaps│
  │ Account  │    │ RoleBinding  │    │ Role (global)│    │ Deploys  │
  └──────────┘    └──────────────┘    └──────────────┘    └──────────┘

  "Who"            "connects"           "can do what"       "to which
                    who to what                              things"
```

- **Subject**: A user, a group, or a ServiceAccount (the identity used by pods).
- **Role / ClusterRole**: A list of permissions (which verbs on which resources). A Role is scoped to a single namespace. A ClusterRole applies cluster-wide.
- **RoleBinding / ClusterRoleBinding**: The glue that attaches a subject to a role.

### Example: A Minimal RBAC Configuration

This Role grants read-only access to ConfigMaps and Secrets in a single namespace, and the RoleBinding attaches it to a ServiceAccount named `app`:

```yaml
# Minimal Role + Binding example (namespace-scoped)
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: read-config
rules:
- apiGroups: [""]
  resources: ["configmaps","secrets"]
  verbs: ["get","list"]
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: bind-read-config
subjects:
- kind: ServiceAccount
  name: app
roleRef:
  kind: Role
  name: read-config
  apiGroup: rbac.authorization.k8s.io
```

> **Pause and predict**: RBAC has Roles (namespace-scoped) and ClusterRoles (cluster-wide). If a developer only needs to manage Pods in one namespace, would you give them a Role or a ClusterRole? What could go wrong if you default to ClusterRoles for convenience?

### The Principle of Least Privilege

Every subject should have only the permissions it needs and nothing more. In practice this means:

- Create dedicated ServiceAccounts per workload instead of using the `default` SA.
- Use namespace-scoped Roles instead of ClusterRoles when possible.
- Never grant wildcard verbs (`*`) or wildcard resources (`*`) unless you have an explicit, documented reason.
- Audit who has `cluster-admin` -- this role can do anything to anything.

---

## Gate 2: Image Trust

A container image is a black box of software. If you run an image you have not verified, you are trusting whoever built it with full access to your cluster's resources.

### Why Tags Lie

Consider this image reference: `nginx:1.25`. The tag `1.25` looks specific, but tags are mutable pointers. The image behind `nginx:1.25` today might be different from the one behind `nginx:1.25` tomorrow. Someone could push a compromised image under the same tag.

An image digest, on the other hand, is a cryptographic hash of the image contents:

```
TAG (mutable -- can change)
  nginx:1.25

DIGEST (immutable -- content-addressed)
  nginx@sha256:6a5db2a1c89e0deaf...

If a single byte changes, the digest changes.
Tags can be re-pointed. Digests cannot be faked.
```

For production workloads, referencing images by digest guarantees you are running exactly the image you tested. **However, this introduces a trade-off**: pinning by digest means you will not automatically pull patch updates (like moving seamlessly from `1.25.1` to `1.25.2`). You must use automation tools (like Dependabot or Renovate) to systematically update digests in your manifests, which increases your operational complexity.

### Image Scanning

Image scanning tools inspect the layers of a container image and compare installed packages against databases of known vulnerabilities (CVEs). Scanning answers questions like:

- Does this image contain a version of OpenSSL with a known critical vulnerability?
- Is the base image outdated?
- Are there packages installed that the application does not need?

Scanning does not make images secure by itself. It gives you visibility so you can make informed decisions about what to deploy.

### Image Provenance

Provenance answers the question: "Where did this image come from, and was it built by a trusted pipeline?" Signing images with tools like cosign or Notary creates a verifiable chain of custody from source code to running container. At the KCNA level, you just need to know the concept exists and why it matters.

---

## Gate 3: Pod Security and Network Segmentation

Once a workload is running, you need to limit the damage it can cause if it is compromised.

### What Running as Root Means

By default, many container images run their processes as the `root` user inside the container. If an attacker exploits a vulnerability in that application, they inherit root privileges. Combined with certain misconfigurations (like a mounted host filesystem or extra Linux capabilities), this can lead to a full node compromise -- meaning the attacker escapes the container entirely and controls the underlying machine.

### Why Host Networking Is Dangerous

A pod with `hostNetwork: true` shares the node's network namespace. It can see all network traffic on the node, bind to any port, and potentially intercept traffic meant for other pods. This bypasses Kubernetes networking entirely and should only be used for specific infrastructure components like CNI plugins.

### Pod Security Standards

Kubernetes defines three levels of pod security restriction, enforced by the built-in Pod Security Admission controller:

| Level | What It Allows | Use Case |
|---|---|---|
| **Privileged** | Everything. No restrictions. | System-level infrastructure (CNI, storage drivers) |
| **Baseline** | Blocks the most dangerous settings (hostNetwork, privileged containers, hostPath) while remaining broadly compatible | General-purpose workloads with minimal changes |
| **Restricted** | Requires running as non-root, drops all capabilities, enforces read-only root filesystem | Security-sensitive and hardened workloads |

Think of these as presets. **There is a strict trade-off between security and developer friction:**
- **Baseline** is acceptable for most general-purpose or legacy workloads because it blocks the worst offenses without requiring code changes.
- **Restricted** provides the highest security but creates friction; developers must explicitly design their applications to run as non-root and handle dropped capabilities gracefully.

> **Stop and think**: By default, every Pod in a Kubernetes cluster can communicate with every other Pod. If an attacker compromises a single Pod in the frontend namespace, what resources could they access without NetworkPolicies in place?

### Network Segmentation with NetworkPolicies

By default, every pod in a Kubernetes cluster can communicate with every other pod. This means a compromised pod in one namespace could reach databases, admin interfaces, or internal APIs in another namespace.

NetworkPolicies act as firewall rules for pods. They let you declare which pods can talk to which other pods, and on which ports:

```
WITHOUT NetworkPolicy          WITH NetworkPolicy

  ┌─────┐     ┌─────┐          ┌─────┐     ┌─────┐
  │ Web │────►│ DB  │          │ Web │────►│ DB  │
  └─────┘     └─────┘          └─────┘     └─────┘
      │                                        X
      │                                        │ (blocked)
  ┌─────┐     ┌─────┐          ┌─────┐     ┌─────┐
  │ Log │────►│ DB  │          │ Log │     │ DB  │
  └─────┘     └─────┘          └─────┘     └─────┘

  Everyone can reach              Only Web can
  reach everything                reach DB
```

At the KCNA level, know that NetworkPolicies exist, that they are namespace-scoped, and that they implement a default-deny posture when configured -- meaning traffic is blocked unless a policy explicitly allows it.

---

## Did You Know?

1. **The default ServiceAccount in every namespace automatically gets mounted into every pod** that does not specify a different one. If that SA has broad permissions, every pod in the namespace inherits them -- even pods that never need to call the Kubernetes API.

2. **Over 60% of container images in public registries contain at least one known critical or high-severity vulnerability**, according to recurring industry surveys. Running unscanned public images is like inviting strangers into your building without a bag check.

3. **Kubernetes RBAC was not always the default**. Before Kubernetes 1.8, the default authorization mode was ABAC (Attribute-Based Access Control), which required restarting the API server to change policies. RBAC was promoted to stable in 1.8 and became the standard.

4. **A single pod with `privileged: true` and `hostPID: true`** can see and interact with every process on the node, effectively giving it full control of the host machine. This is why the Restricted Pod Security Standard explicitly forbids both settings.

---

## Common Mistakes

| Mistake | Why It Is Dangerous | What To Do Instead |
|---|---|---|
| Using the `default` ServiceAccount for all workloads | Every pod gets the same permissions; one compromised pod exposes everything | Create a dedicated SA per workload with only the RBAC it needs |
| Granting `cluster-admin` to CI/CD pipelines | A compromised pipeline can delete any resource in any namespace | Create a scoped Role with only the verbs and resources the pipeline uses |
| Referencing images by tag (`:latest` or `:v2`) | Tags are mutable; the image can change without you knowing | Use digests (`@sha256:...`) for production deployments |
| Running containers as root | Container escape vulnerabilities become full node compromises | Set `runAsNonRoot: true` in the pod's security context |
| No NetworkPolicies in any namespace | Every pod can talk to every other pod, including databases and admin APIs | Apply a default-deny ingress policy per namespace, then allow specific traffic |
| Using wildcard RBAC rules (`verbs: ["*"]`) | Accidentally grants destructive permissions (delete, escalate) | List each verb explicitly: `get`, `list`, `watch`, `create`, `update` |

---

## Knowledge Check

**Question 1**: Your company uses `myapp:production` as the image tag for all deployments. A developer pushes a new build to the same tag. What security risk does this create, and how would you address it?

<details>
<summary>Answer</summary>

Mutable tags mean the image content can change without the reference changing. A deployment using `myapp:production` might pull a different image on each node or after a restart, potentially running untested or compromised code. This also breaks reproducibility -- you cannot tell which exact image is running. The fix is to reference images by their content-addressable digest (e.g., `myapp@sha256:abc123...`), which guarantees immutability. If the image content changes, the digest changes too.

</details>

**Question 2**: An intern deployed a pod with `privileged: true`. What risks does this create?

<details>
<summary>Answer</summary>

A privileged container has full access to all Linux capabilities and can interact with the host kernel directly. If an attacker compromises the application running in that pod, they can escape the container, access the host filesystem, manipulate other containers on the same node, and potentially pivot to other nodes. This effectively turns a single application vulnerability into a full cluster compromise. The pod should be redeployed without privileged mode and with a Restricted or Baseline Pod Security Standard enforced on the namespace.

</details>

**Question 3**: A team creates a single ClusterRole with `resources: ["*"]` and `verbs: ["*"]`, then binds it to all developers via a ClusterRoleBinding. Why is this a problem?

<details>
<summary>Answer</summary>

This grants every developer full administrative access to every resource in every namespace, including the ability to read Secrets, delete Deployments, modify RBAC rules, and even escalate their own permissions further. It violates the principle of least privilege entirely. If any developer's credentials are compromised, the attacker gains unlimited cluster access. Instead, each team should receive namespace-scoped Roles with only the specific verbs and resources they need for their workloads.

</details>

**Question 4**: Your cluster has no NetworkPolicies configured. A pod in the `frontend` namespace is compromised. What can the attacker reach?

<details>
<summary>Answer</summary>

Without NetworkPolicies, Kubernetes allows all pod-to-pod communication by default. The attacker can reach every pod in every namespace -- databases in the `backend` namespace, admin tools in the `monitoring` namespace, and any internal API. They can also attempt to reach the Kubernetes API server if the pod's ServiceAccount has permissions. The mitigation is to apply default-deny NetworkPolicies to each namespace and then create explicit allow rules only for the traffic flows that are actually required.

</details>

**Question 5**: A security audit finds that 200 pods across 15 namespaces are all using the `default` ServiceAccount. The `default` SA has a ClusterRoleBinding to a role that allows reading Secrets cluster-wide. What is the blast radius, and how would you remediate it?

<details>
<summary>Answer</summary>

The blast radius is severe: every one of those 200 pods can read every Secret in every namespace, including database passwords, API keys, and TLS certificates. A compromise of any single pod gives the attacker access to all cluster secrets. Remediation requires two steps: first, remove the ClusterRoleBinding from the `default` ServiceAccount; second, create individual ServiceAccounts for each workload with only the specific permissions each one needs. Pods that do not need Kubernetes API access should have `automountServiceAccountToken: false` set.

</details>

**Question 6**: A developer successfully authenticates to the cluster and has an RBAC Role allowing them to `create` Pods. However, when they try to deploy a Pod with `hostNetwork: true`, the API server rejects the request. Compare the roles of authentication, authorization, and admission control in this scenario. Which layer blocked the request?

<details>
<summary>Answer</summary>

The developer successfully passed **Authentication** (their identity was verified as a valid user) and **Authorization** (RBAC confirmed they had the specific permission to `create` Pods). The request was blocked by **Admission Control** (specifically, a Pod Security Admission controller). While RBAC checks *if* you have permission to interact with a resource endpoint, Admission Control inspects the *contents* of the resource payload to ensure it complies with cluster-wide policies (like blocking the dangerous `hostNetwork` setting) before it is finally written to the database.

</details>

---

## Security Audit Exercise

### Worked Example: Applying the Three Gates

Before you try the exercise below, let's look at how to evaluate a configuration using the Three Gates framework.

**Scenario**: A developer provides the following snippet for a new internal analytics tool:
- `image: internal-registry/analytics:v2`
- `serviceAccountName: default`
- `securityContext: { privileged: true }`

**Analysis & Remediation**:
1. **Gate 1 (Badge)**: It uses the `default` ServiceAccount, which might share excessive permissions with other pods. *Fix*: Create a dedicated `analytics-sa` ServiceAccount with least-privilege RBAC.
2. **Gate 2 (Bag Check)**: It uses a mutable tag (`:v2`). *Fix*: Resolve the tag to an immutable digest (`@sha256:...`) and ensure the image is scanned in the CI pipeline.
3. **Gate 3 (Seatbelt)**: It requests `privileged: true`. *Fix*: Remove the privileged flag and apply the Baseline Pod Security Standard to the namespace.

### Your Turn

Review the following scenarios. For each one, identify which of the Three Gates it primarily violates (Badge, Bag Check, or Seatbelt) and **propose a specific configuration fix** to secure it.

| # | Scenario | Gate Violated | Proposed Fix |
|---|---|---|---|
| 1 | A web app deployment mounts the node's root filesystem using `hostPath: /`. | ? | ? |
| 2 | A CI/CD pipeline uses a ServiceAccount bound to a ClusterRole with `verbs: ["*"]`. | ? | ? |
| 3 | A deployment pulls `nginx:latest` directly from Docker Hub for a production app. | ? | ? |
| 4 | All pods in the `backend` namespace can freely receive traffic from the `frontend` and `testing` namespaces. | ? | ? |

<details>
<summary>Answers</summary>

| # | Gate Violated | Proposed Fix |
|---|---|---|
| 1 | Seatbelt (Gate 3) | Remove the `hostPath` mount. Enforce the Baseline or Restricted Pod Security Standard on the namespace to block host filesystem access, preventing container escapes. |
| 2 | Badge (Gate 1) | Remove the wildcard verbs. Create a namespace-scoped Role that explicitly lists only the exact verbs (e.g., `create`, `update`, `get`) and resources (e.g., `deployments`, `services`) the pipeline actually needs. |
| 3 | Bag Check (Gate 2) | Change `nginx:latest` to a specific image digest (`nginx@sha256:...`). Ensure the image is pulled from a trusted, scanned internal registry rather than directly from Docker Hub. |
| 4 | Seatbelt (Gate 3) | Implement a default-deny NetworkPolicy in the `backend` namespace. Then, create a specific NetworkPolicy that only allows ingress traffic from pods labeled as part of the `frontend` namespace. |

</details>

---

## What Is Next?

Continue to [Module 3.7: Community and Collaboration](/k8s/kcna/part3-cloud-native-architecture/module-3.7-community-collaboration/) to learn how open-source governance, SIGs, and the CNCF ecosystem shape Kubernetes development.