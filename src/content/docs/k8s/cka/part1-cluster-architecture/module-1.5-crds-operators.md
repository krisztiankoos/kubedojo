---
title: "Module 1.5: CRDs & Operators - Extending Kubernetes"
slug: k8s/cka/part1-cluster-architecture/module-1.5-crds-operators
sidebar:
  order: 6
lab:
  id: cka-1.5-crds-operators
  url: https://killercoda.com/kubedojo/scenario/cka-1.5-crds-operators
  duration: "40 min"
  difficulty: advanced
  environment: kubernetes
---
> **Complexity**: `[MEDIUM]` - New to CKA 2025
>
> **Time to Complete**: 35-45 minutes
>
> **Prerequisites**: Module 1.1 (Control Plane understanding)

---

## What You'll Be Able to Do

After this module, you will be able to:
- **Create** Custom Resource Definitions and explain how they extend the Kubernetes API
- **Deploy** an operator and manage its custom resources
- **Explain** the operator pattern (custom controller + CRD) and when it's appropriate
- **Debug** CRD validation errors and operator reconciliation failures

---

## Why This Module Matters

CRDs and Operators are **new to the CKA 2025 curriculum**.

Kubernetes ships with built-in resources: Pods, Deployments, Services. But what if you need a "Database" resource that automatically handles backups, failover, and scaling? What if you want a "Certificate" resource that auto-renews from Let's Encrypt?

Custom Resource Definitions (CRDs) let you create new resource types. Operators are controllers that manage these custom resources. Together, they're how the Kubernetes ecosystem extends beyond the core.

This is how Prometheus, Cert-Manager, ArgoCD, and hundreds of other tools integrate with Kubernetes. Understanding CRDs and Operators is essential for working with modern Kubernetes.

> **The Building Blocks Analogy**
>
> Think of Kubernetes like a LEGO set. It comes with standard blocks (Pods, Services). CRDs are custom blocks you design yourself—a "Database" block, a "Certificate" block. Operators are instruction manuals that know how to combine these blocks into working systems. You don't build manually; the operator follows the instructions automatically.

---

## What You'll Learn

By the end of this module, you'll be able to:
- Understand what CRDs and Operators are
- Create and manage Custom Resource Definitions
- Create instances of custom resources
- Understand the Operator pattern
- Work with common operators (cert-manager, prometheus)

---

## Part 1: Custom Resource Definitions (CRDs)

### 1.1 What Is a CRD?

A CRD extends the Kubernetes API with a new resource type.

```
Built-in Resources:          Custom Resources (via CRDs):
├── Pod                      ├── Certificate (cert-manager)
├── Deployment               ├── Prometheus (prometheus-operator)
├── Service                  ├── PostgreSQL (postgres-operator)
├── ConfigMap                ├── VirtualService (istio)
└── ...                      └── YourOwnResource
```

Once a CRD is created, you can use `kubectl` to manage the new resource type just like built-in resources:

```bash
# Built-in resource
kubectl get pods

# Custom resource (after CRD is installed)
kubectl get certificates
kubectl get prometheuses
kubectl get postgresqls
```

### 1.2 CRD Structure

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: crontabs.stable.example.com    # <plural>.<group>
spec:
  group: stable.example.com            # API group
  versions:
    - name: v1                         # API version
      served: true                     # Enable this version
      storage: true                    # Store in etcd
      schema:
        openAPIV3Schema:               # Validation schema
          type: object
          properties:
            spec:
              type: object
              properties:
                cronSpec:
                  type: string
                image:
                  type: string
                replicas:
                  type: integer
  scope: Namespaced                    # or Cluster
  names:
    plural: crontabs                   # kubectl get crontabs
    singular: crontab                  # kubectl get crontab
    kind: CronTab                      # Kind in YAML
    shortNames:
      - ct                             # kubectl get ct
```

### 1.3 Creating a CRD

```bash
# Apply the CRD
kubectl apply -f crontab-crd.yaml

# Verify it was created
kubectl get crd crontabs.stable.example.com

# Now you can create instances
kubectl get crontabs
# No resources found (expected - we haven't created any yet)
```

> **Did You Know?**
>
> CRDs are stored in etcd just like built-in resources. Once created, they become first-class API citizens. The API server handles validation, RBAC, and watch mechanisms automatically.

---

## Part 2: Creating Custom Resources

> **Pause and predict**: You've just applied a CRD that defines a new "Database" resource type. You then create a Database custom resource with `replicas: 3`. Will Kubernetes automatically create 3 pods for your database? Why or why not?

### 2.1 Custom Resource Instance

Once the CRD exists, you can create instances:

```yaml
apiVersion: stable.example.com/v1
kind: CronTab
metadata:
  name: my-cron-job
  namespace: default
spec:
  cronSpec: "* * * * */5"
  image: my-awesome-cron-image
  replicas: 3
```

```bash
kubectl apply -f my-crontab.yaml
kubectl get crontabs
kubectl get ct    # Using shortName
kubectl describe crontab my-cron-job
```

### 2.2 Custom Resource Operations

All standard kubectl operations work:

```bash
# Create
kubectl apply -f crontab.yaml

# List
kubectl get crontabs -A

# Describe
kubectl describe crontab my-cron-job

# Edit
kubectl edit crontab my-cron-job

# Delete
kubectl delete crontab my-cron-job

# Watch
kubectl get crontabs -w

# Get as YAML
kubectl get crontab my-cron-job -o yaml
```

---

## Part 3: The Operator Pattern

### 3.1 What Is an Operator?

A CRD alone doesn't do anything—it's just data storage. An **Operator** is a controller that:
1. Watches for changes to custom resources
2. Takes action to reconcile desired state with actual state

```
┌────────────────────────────────────────────────────────────────┐
│                     Operator Pattern                            │
│                                                                 │
│   You create:                                                   │
│   ┌─────────────────────────────────────────┐                  │
│   │ apiVersion: databases.example.com/v1    │                  │
│   │ kind: PostgreSQL                        │                  │
│   │ spec:                                   │                  │
│   │   version: "15"                         │                  │
│   │   replicas: 3                           │                  │
│   │   storage: 100Gi                        │                  │
│   └─────────────────────────────────────────┘                  │
│                          │                                      │
│                          ▼                                      │
│   ┌─────────────────────────────────────────┐                  │
│   │           Operator (Controller)          │                  │
│   │                                          │                  │
│   │   Watches PostgreSQL resources           │                  │
│   │   Creates:                               │                  │
│   │   • StatefulSet with 3 replicas          │                  │
│   │   • PVCs for 100Gi storage               │                  │
│   │   • Services for connections             │                  │
│   │   • Secrets for credentials              │                  │
│   │   • ConfigMaps for configuration         │                  │
│   │                                          │                  │
│   │   Manages:                               │                  │
│   │   • Automatic failover                   │                  │
│   │   • Backups                              │                  │
│   │   • Version upgrades                     │                  │
│   └─────────────────────────────────────────┘                  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

> **What would happen if**: The cert-manager operator pod crashes but the CRDs remain. Can you still create Certificate custom resources? Will existing certificates continue to serve TLS traffic?

### 3.2 Operator Components

An operator typically includes:
1. **CRD(s)** - Define the custom resource types
2. **Controller** - Deployment running the reconciliation logic
3. **RBAC** - Permissions to manage resources
4. **Webhooks** (optional) - Validation and mutation

### 3.3 Reconciliation Loop

```
┌─────────────────────────────────────────────────────────────┐
│                  Reconciliation Loop                         │
│                                                              │
│   ┌─────────┐                                               │
│   │  Watch  │◄─────────────────────────────────────────┐    │
│   └────┬────┘                                          │    │
│        │ Event: PostgreSQL resource changed            │    │
│        ▼                                               │    │
│   ┌─────────┐                                          │    │
│   │  Read   │ Get current state from cluster           │    │
│   └────┬────┘                                          │    │
│        │                                               │    │
│        ▼                                               │    │
│   ┌─────────┐                                          │    │
│   │ Compare │ Current state vs. Desired state          │    │
│   └────┬────┘                                          │    │
│        │                                               │    │
│        ▼                                               │    │
│   ┌─────────┐                                          │    │
│   │  Act    │ Create/Update/Delete resources           │    │
│   └────┬────┘                                          │    │
│        │                                               │    │
│        └─────────────────────────────────────────────►─┘    │
│                  Repeat forever                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

> **War Story: The Self-Healing Database**
>
> A company used a PostgreSQL operator. At 3 AM, the primary database node failed. Without human intervention, the operator detected the failure, promoted a replica to primary, updated service endpoints, and notified the team via Slack. By the time the on-call engineer checked, everything was running. Total downtime: 90 seconds. Without the operator, it would have been a 30-minute manual failover.

---

## Part 4: Working with Real Operators

### 4.1 cert-manager

cert-manager automates TLS certificate management:

```bash
# Install cert-manager (includes CRDs)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Check CRDs created
kubectl get crd | grep cert-manager
# certificates.cert-manager.io
# clusterissuers.cert-manager.io
# issuers.cert-manager.io
# ...
```

```yaml
# Create a Certificate resource
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: myapp-tls
  namespace: default
spec:
  secretName: myapp-tls-secret
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - myapp.example.com
```

The cert-manager operator watches this Certificate and:
1. Requests a certificate from Let's Encrypt
2. Completes the ACME challenge
3. Stores the certificate in the specified Secret
4. Auto-renews before expiration

### 4.2 Prometheus Operator

```bash
# Check Prometheus CRDs
kubectl get crd | grep monitoring.coreos.com
# prometheuses.monitoring.coreos.com
# servicemonitors.monitoring.coreos.com
# alertmanagers.monitoring.coreos.com
```

```yaml
# Create a Prometheus instance
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: main
  namespace: monitoring
spec:
  replicas: 2
  serviceAccountName: prometheus
  serviceMonitorSelector:
    matchLabels:
      team: frontend
```

### 4.3 Discovering What's Installed

```bash
# List all CRDs in cluster
kubectl get crd

# See all custom resources of a type
kubectl get certificates -A

# Check if operator is running
kubectl get pods -A | grep operator
kubectl get pods -A | grep -E "cert-manager|prometheus"
```

---

## Part 5: CRD Deep Dive

> **Stop and think**: What happens if you delete a CRD while there are still custom resources of that type in the cluster? Do the custom resources survive, or are they deleted too?

### 5.1 Schema Validation

CRDs can enforce validation:

```yaml
schema:
  openAPIV3Schema:
    type: object
    required:
      - spec
    properties:
      spec:
        type: object
        required:
          - cronSpec
          - image
        properties:
          cronSpec:
            type: string
            pattern: '^(\d+|\*)(/\d+)?(\s+(\d+|\*)(/\d+)?){4}$'
          image:
            type: string
          replicas:
            type: integer
            minimum: 1
            maximum: 10
            default: 1
```

Now invalid resources are rejected:

```bash
# This would fail validation
kubectl apply -f bad-crontab.yaml
# Error: spec.replicas: Invalid value: 15: must be <= 10
```

### 5.2 Additional Printer Columns

Show custom columns in `kubectl get`:

```yaml
versions:
  - name: v1
    additionalPrinterColumns:
      - name: Schedule
        type: string
        jsonPath: .spec.cronSpec
      - name: Replicas
        type: integer
        jsonPath: .spec.replicas
      - name: Age
        type: date
        jsonPath: .metadata.creationTimestamp
```

```bash
kubectl get crontabs
# NAME          SCHEDULE       REPLICAS   AGE
# my-cron-job   * * * * */5    3          5m
```

### 5.3 Subresources

Enable status and scale subresources:

```yaml
versions:
  - name: v1
    subresources:
      status: {}           # Enable /status subresource
      scale:               # Enable kubectl scale
        specReplicasPath: .spec.replicas
        statusReplicasPath: .status.replicas
```

```bash
# Now this works
kubectl scale crontab my-cron-job --replicas=5
```

---

## Part 6: Namespaced vs. Cluster-Scoped

### 6.1 Scope Types

```yaml
# Namespaced (default)
scope: Namespaced
# Resources exist within a namespace
# kubectl get crontabs -n myapp

# Cluster-scoped
scope: Cluster
# Resources are cluster-wide (like Nodes, PVs)
# kubectl get clusterissuers (cert-manager example)
```

### 6.2 When to Use Each

| Scope | Use When | Examples |
|-------|----------|----------|
| **Namespaced** | Resource belongs to a team/app | Certificate, Database, Application |
| **Cluster** | Resource is shared/global | ClusterIssuer, StorageProfile |

---

## Part 7: Exam-Relevant Operations

### 7.1 Check What CRDs Exist

```bash
# List all CRDs
kubectl get crd

# Get details about a CRD
kubectl describe crd certificates.cert-manager.io

# See the full CRD definition
kubectl get crd certificates.cert-manager.io -o yaml
```

### 7.2 Work with Custom Resources

```bash
# List custom resources
kubectl get <resource-name> -A

# Get specific resource
kubectl get certificate my-cert -o yaml

# Edit custom resource
kubectl edit certificate my-cert

# Delete custom resource
kubectl delete certificate my-cert
```

### 7.3 Find API Resources

```bash
# List all resource types (including custom)
kubectl api-resources

# Filter by group
kubectl api-resources --api-group=cert-manager.io

# Show if namespaced
kubectl api-resources --namespaced=true
```

---

## Did You Know?

- **OperatorHub.io** catalogs hundreds of operators. Search for what you need before building your own.

- **Operator SDK** and **Kubebuilder** are frameworks for building operators in Go. You can also build operators in Python, Ansible, or Helm.

- **OLM (Operator Lifecycle Manager)** manages operator installation and upgrades. It's what OpenShift uses to install operators.

- **Finalizers** let custom resources prevent deletion until cleanup is complete. This is how operators ensure databases are properly backed up before deletion.

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Creating CR before CRD | "resource not found" | Always install CRD first |
| Wrong API group/version | YAML validation fails | Check CRD for correct apiVersion |
| Forgetting operator install | CR does nothing | CRD alone doesn't act; need operator |
| Deleting CRD with existing CRs | Data loss | Delete CRs first, then CRD |
| Wrong scope assumption | Resource in wrong place | Check CRD scope: Namespaced vs Cluster |

---

## Quiz

1. **You join a new team and run `kubectl get pods -A` but only see a handful of system pods. A colleague says "the databases are managed by an operator." How would you discover what CRDs are installed, find the database custom resources, and determine which operator manages them?**
   <details>
   <summary>Answer</summary>
   Start with `kubectl get crd` to list all Custom Resource Definitions in the cluster — this shows you every custom type available. Look for database-related names (e.g., `postgresqls.acid.zalan.do` or `databases.example.com`). Then list instances: `kubectl get <resource-name> -A` (e.g., `kubectl get postgresqls -A`). To find the operator managing them, run `kubectl get pods -A | grep operator` or check the CRD's API group and search for pods in kube-system or a dedicated namespace. You can also run `kubectl api-resources` which shows all resource types including their API group, helping you trace which operator project owns them.
   </details>

2. **A developer creates a `Certificate` custom resource for cert-manager, but after 10 minutes the certificate Secret hasn't been created. The CRD exists and `kubectl get certificate my-cert` shows the resource. What are the three things you should check, in order?**
   <details>
   <summary>Answer</summary>
   First, check if the cert-manager operator pods are running: `kubectl get pods -n cert-manager`. A CRD without its operator is just data storage — no controller is watching to act on the Certificate CR. Second, if the operator is running, check the operator logs: `kubectl logs -n cert-manager deploy/cert-manager` for reconciliation errors, such as missing ClusterIssuer, DNS challenge failures, or rate limiting from Let's Encrypt. Third, describe the Certificate resource: `kubectl describe certificate my-cert` and check the Status and Events sections for specific error messages like "issuer not found" or "ACME challenge failed." The operator writes status conditions to the CR, which is your most direct diagnostic.
   </details>

3. **Your team wants to create a "BackupPolicy" CRD that should apply to entire clusters, not individual namespaces. A junior engineer sets `scope: Namespaced`. What problems will this cause, and what should the scope be?**
   <details>
   <summary>Answer</summary>
   With `scope: Namespaced`, every team would need to create their own BackupPolicy in each namespace, leading to duplication and inconsistency. More critically, cluster-wide backup policies (like "back up all PVs every 6 hours") don't logically belong to any single namespace. The scope should be `Cluster`, making BackupPolicy resources cluster-wide — similar to how cert-manager uses `ClusterIssuer` for cluster-wide certificate issuers vs `Issuer` for namespace-scoped ones. With cluster scope, names must be globally unique, you don't use `-n namespace` with kubectl commands, and RBAC requires ClusterRoles (not Roles) to manage them. Choose Namespaced for resources owned by a team or application, and Cluster for shared infrastructure policies.
   </details>

4. **You accidentally run `kubectl delete crd certificates.cert-manager.io`. What happens to all the Certificate custom resources in the cluster, and can you recover them?**
   <details>
   <summary>Answer</summary>
   Deleting a CRD cascades and deletes ALL custom resources of that type across all namespaces. Every Certificate CR in the cluster is immediately removed from etcd. The TLS Secrets that were already created by cert-manager still exist (they're regular Kubernetes Secrets, not custom resources), so existing TLS traffic continues working. However, no new certificates can be issued, and existing certificates won't auto-renew since the Certificate CRs are gone. Recovery requires reinstalling cert-manager (which recreates the CRD) and then recreating all Certificate CRs. This is why the "Common Mistakes" section warns to delete CRs first, then the CRD — and why you should always have your CRs defined in version control (GitOps) for disaster recovery.
   </details>

---

## Hands-On Exercise

**Task**: Create a simple CRD and custom resources.

**Steps**:

1. **Create a CRD for a "Website" resource**:
```bash
cat > website-crd.yaml << 'EOF'
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: websites.stable.example.com
spec:
  group: stable.example.com
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              required:
                - url
              properties:
                url:
                  type: string
                replicas:
                  type: integer
                  default: 1
      additionalPrinterColumns:
        - name: URL
          type: string
          jsonPath: .spec.url
        - name: Replicas
          type: integer
          jsonPath: .spec.replicas
        - name: Age
          type: date
          jsonPath: .metadata.creationTimestamp
  scope: Namespaced
  names:
    plural: websites
    singular: website
    kind: Website
    shortNames:
      - ws
EOF

kubectl apply -f website-crd.yaml
```

2. **Verify the CRD**:
```bash
kubectl get crd websites.stable.example.com
kubectl api-resources | grep website
```

3. **Create a Website instance**:
```bash
cat > my-website.yaml << 'EOF'
apiVersion: stable.example.com/v1
kind: Website
metadata:
  name: company-site
  namespace: default
spec:
  url: https://example.com
  replicas: 3
EOF

kubectl apply -f my-website.yaml
```

4. **Work with the custom resource**:
```bash
# List websites
kubectl get websites
kubectl get ws    # Short name

# Describe
kubectl describe website company-site

# Get as YAML
kubectl get website company-site -o yaml

# Edit
kubectl edit website company-site
```

5. **Create another website**:
```bash
cat > blog.yaml << 'EOF'
apiVersion: stable.example.com/v1
kind: Website
metadata:
  name: blog
spec:
  url: https://blog.example.com
  replicas: 2
EOF

kubectl apply -f blog.yaml
kubectl get ws
```

6. **Explore installed operators (if any)**:
```bash
# Check for cert-manager
kubectl get crd | grep cert-manager

# Check for prometheus operator
kubectl get crd | grep monitoring.coreos.com

# List all CRDs
kubectl get crd
```

7. **Cleanup**:
```bash
kubectl delete website company-site blog
kubectl delete crd websites.stable.example.com
rm website-crd.yaml my-website.yaml blog.yaml
```

**Success Criteria**:
- [ ] Can create a CRD
- [ ] Can create custom resource instances
- [ ] Can query custom resources with kubectl
- [ ] Understand the relationship between CRD and CR
- [ ] Know how to find CRDs in a cluster

---

## Practice Drills

### Drill 1: CRD Exploration (Target: 3 minutes)

Explore existing CRDs in your cluster:

```bash
# List all CRDs
kubectl get crd

# Get details on a specific CRD
kubectl get crd <crd-name> -o yaml | head -50

# List instances of a CRD
kubectl get <resource-name> -A

# Describe a CRD
kubectl describe crd <crd-name>
```

### Drill 2: Create a Simple CRD (Target: 5 minutes)

```bash
# Create CRD
cat << 'EOF' | kubectl apply -f -
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: apps.example.com
spec:
  group: example.com
  names:
    kind: App
    listKind: AppList
    plural: apps
    singular: app
    shortNames:
      - ap
  scope: Namespaced
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                image:
                  type: string
                replicas:
                  type: integer
EOF

# Verify CRD exists
kubectl get crd apps.example.com

# Create an instance
cat << 'EOF' | kubectl apply -f -
apiVersion: example.com/v1
kind: App
metadata:
  name: my-app
spec:
  image: nginx:1.25
  replicas: 3
EOF

# Query using short name
kubectl get ap

# Cleanup
kubectl delete app my-app
kubectl delete crd apps.example.com
```

### Drill 3: CRD with Validation (Target: 5 minutes)

```bash
cat << 'EOF' | kubectl apply -f -
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databases.stable.example.com
spec:
  group: stable.example.com
  names:
    kind: Database
    plural: databases
    singular: database
    shortNames:
      - db
  scope: Namespaced
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          required:
            - spec
          properties:
            spec:
              type: object
              required:
                - engine
                - version
              properties:
                engine:
                  type: string
                  enum:
                    - postgres
                    - mysql
                    - mongodb
                version:
                  type: string
                storage:
                  type: string
                  default: "10Gi"
EOF

# Try to create invalid resource (should fail)
cat << 'EOF' | kubectl apply -f -
apiVersion: stable.example.com/v1
kind: Database
metadata:
  name: invalid-db
spec:
  engine: oracle  # Not in enum!
  version: "14"
EOF

# Create valid resource
cat << 'EOF' | kubectl apply -f -
apiVersion: stable.example.com/v1
kind: Database
metadata:
  name: prod-db
spec:
  engine: postgres
  version: "14"
EOF

# Cleanup
kubectl delete database prod-db
kubectl delete crd databases.stable.example.com
```

### Drill 4: Find Operator-Managed Resources (Target: 3 minutes)

```bash
# Find CRDs from popular operators
kubectl get crd | grep -E "cert-manager|prometheus|istio|argocd"

# If cert-manager is installed
kubectl get certificates -A
kubectl get clusterissuers

# If prometheus operator is installed
kubectl get servicemonitors -A
kubectl get prometheusrules -A

# General: Find all custom resources
kubectl api-resources --api-group="" | head -20
kubectl api-resources | grep -v "^NAME"
```

### Drill 5: CRD Status Subresource (Target: 5 minutes)

```bash
cat << 'EOF' | kubectl apply -f -
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: tasks.work.example.com
spec:
  group: work.example.com
  names:
    kind: Task
    plural: tasks
  scope: Namespaced
  versions:
    - name: v1
      served: true
      storage: true
      subresources:
        status: {}
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                command:
                  type: string
            status:
              type: object
              properties:
                phase:
                  type: string
                completedAt:
                  type: string
EOF

# Create task
cat << 'EOF' | kubectl apply -f -
apiVersion: work.example.com/v1
kind: Task
metadata:
  name: build-job
spec:
  command: "make build"
EOF

# View the task
kubectl get task build-job -o yaml

# Cleanup
kubectl delete task build-job
kubectl delete crd tasks.work.example.com
```

### Drill 6: Troubleshooting - CRD Not Found (Target: 3 minutes)

```bash
# Try to create a resource for non-existent CRD
cat << 'EOF' | kubectl apply -f -
apiVersion: nonexistent.example.com/v1
kind: Widget
metadata:
  name: test
spec:
  size: large
EOF

# Error: no matches for kind "Widget"

# Diagnose
kubectl get crd | grep widget  # Nothing
kubectl api-resources | grep -i widget  # Nothing

# Solution: CRD must be created before resources
# Create the CRD first, then the resource
```

### Drill 7: Challenge - Create Your Own CRD

Design and implement a CRD for a "Backup" resource with:

- Group: `backup.example.com`
- Required fields: `source`, `destination`, `schedule` (cron format)
- Optional field: `retention` (integer, default 7)
- Validation: `schedule` must be a string

```bash
# YOUR TASK: Create the CRD and a sample Backup resource
```

<details>
<summary>Solution</summary>

```bash
cat << 'EOF' | kubectl apply -f -
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: backups.backup.example.com
spec:
  group: backup.example.com
  names:
    kind: Backup
    plural: backups
    shortNames:
      - bk
  scope: Namespaced
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          required:
            - spec
          properties:
            spec:
              type: object
              required:
                - source
                - destination
                - schedule
              properties:
                source:
                  type: string
                destination:
                  type: string
                schedule:
                  type: string
                retention:
                  type: integer
                  default: 7
EOF

cat << 'EOF' | kubectl apply -f -
apiVersion: backup.example.com/v1
kind: Backup
metadata:
  name: daily-db-backup
spec:
  source: /data/postgres
  destination: s3://backups/postgres
  schedule: "0 2 * * *"
  retention: 14
EOF

kubectl get bk
kubectl delete backup daily-db-backup
kubectl delete crd backups.backup.example.com
```

</details>

---

## Next Module

[Module 1.6: RBAC](../module-1.6-rbac/) - Role-Based Access Control for securing your cluster.
