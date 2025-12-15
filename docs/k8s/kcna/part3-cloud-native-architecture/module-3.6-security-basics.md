# Module 3.6: Security Basics (Theory)

> **Complexity**: `[QUICK]` - Foundations only
>
> **Time to Complete**: 15-20 minutes
>
> **Prerequisites**: Modules 3.1–3.5 (Cloud Native Architecture)

---

## Outline
- Identities and permissions (who can do what)
- Trusting what you run (images and manifests)
- Pod-level safety signals
- Mental model: security is a series of gates—identity badge (RBAC), baggage check (image trust), and seatbelt (pod safety).
- Quick scan: “Would I be comfortable running this pod on my laptop?”

---

## Identity & Access
- **Subjects**: Users, groups, and service accounts (SAs).
- **RBAC**: Roles define verbs on resources; RoleBinding/ClusterRoleBinding attach them to subjects.
- **Principle**: Least privilege—SAs for workloads, scoped roles for namespaces, avoid using default SA.

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

## Trusting Images
- Prefer **digests** over tags for immutability.
- Scan images and review base images; avoid running as root where possible.
- Image provenance/signing (conceptual): ensure images come from your build pipeline.

```
3 GATES
[Badge]  RBAC allows only the right people/pods.
[Bag]    Image provenance/scan blocks poisoned images.
[Belt]   Pod security limits blast radius at runtime.
```

## Pod Safety Basics
- **Pod Security** (concept): Restrict privileged mode, host networking, hostPath mounts, and dangerous capabilities.
- **Runtime identity**: Each pod uses its SA token for API calls—bind only what it needs.
- **Network scope** (high level): NetworkPolicies can limit which pods/services can talk.

> **KCNA expectation**: Know these levers exist and why they matter; deep hardening is for higher-level certs.

> **Analogy**: Entering a secure building—badge at the door (RBAC), bag check (image provenance), buckle up once inside (pod security). Each layer catches different risks.

> **Red flag checklist**: Running as root, wildcard RBAC (`*` verbs), `hostPath` mounts, `:latest` tags, and public registries with no scanning.
