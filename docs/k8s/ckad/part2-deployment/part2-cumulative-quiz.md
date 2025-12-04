# Part 2 Cumulative Quiz: Application Deployment

> **Time Limit**: 25 minutes (simulating exam pressure)
>
> **Passing Score**: 80% (8/10 questions)

This quiz tests your mastery of:
- Deployments and rolling updates/rollbacks
- Helm package manager
- Kustomize
- Deployment strategies (blue/green, canary)

---

## Instructions

1. Try each question without looking at answers
2. Time yourself—speed matters for CKAD
3. Use only `kubectl` and `kubernetes.io/docs`
4. Check answers after completing all questions

---

## Questions

### Question 1: Rolling Update Configuration
**[2 minutes]**

Create a Deployment named `webapp` with 4 replicas using `nginx:1.20` that:
- Uses `RollingUpdate` strategy
- Has `maxSurge: 1`
- Has `maxUnavailable: 0`

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
EOF
```

</details>

---

### Question 2: Rollback
**[2 minutes]**

A Deployment named `api` was updated but is failing. Roll it back to revision 2.

```bash
# Verify current state
k rollout history deploy/api
```

<details>
<summary>Answer</summary>

```bash
# Check history
k rollout history deploy/api

# Rollback to revision 2
k rollout undo deploy/api --to-revision=2

# Verify
k rollout status deploy/api
```

</details>

---

### Question 3: Helm Install with Values
**[2 minutes]**

Install a chart from the `bitnami` repository:
- Release name: `my-nginx`
- Chart: `bitnami/nginx`
- Set `replicaCount=3`
- Namespace: `web` (create if doesn't exist)

<details>
<summary>Answer</summary>

```bash
# Add repo if needed
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install with values
helm install my-nginx bitnami/nginx \
  --set replicaCount=3 \
  -n web --create-namespace
```

</details>

---

### Question 4: Helm Rollback
**[1 minute]**

A Helm release `my-app` was upgraded and is now broken. Roll it back to the previous version.

<details>
<summary>Answer</summary>

```bash
# Check history
helm history my-app

# Rollback to previous
helm rollback my-app

# Or to specific revision
helm rollback my-app 1
```

</details>

---

### Question 5: Kustomize Basic
**[3 minutes]**

Create a Kustomization that:
- Includes `deployment.yaml`
- Sets namespace to `production`
- Adds prefix `prod-` to all names

Then apply it.

<details>
<summary>Answer</summary>

```bash
# Create kustomization.yaml
cat << 'EOF' > kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml

namespace: production
namePrefix: prod-
EOF

# Preview
kubectl kustomize ./

# Apply
kubectl apply -k ./
```

</details>

---

### Question 6: Kustomize Image Override
**[2 minutes]**

Create a Kustomization that overrides the `nginx` image to use tag `1.22` instead of whatever is in the base manifests.

<details>
<summary>Answer</summary>

```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml

images:
- name: nginx
  newTag: "1.22"
```

```bash
kubectl kustomize ./
```

</details>

---

### Question 7: Blue/Green Switch
**[3 minutes]**

You have two deployments:
- `app-blue` with label `version: blue`
- `app-green` with label `version: green`

A Service `app-svc` currently points to blue. Switch it to green.

<details>
<summary>Answer</summary>

```bash
# Switch service selector to green
kubectl patch svc app-svc -p '{"spec":{"selector":{"version":"green"}}}'

# Verify
kubectl get ep app-svc
kubectl describe svc app-svc
```

</details>

---

### Question 8: Canary Setup
**[3 minutes]**

Set up a canary deployment where:
- Stable deployment `stable-app` has 9 replicas (90%)
- Canary deployment `canary-app` has 1 replica (10%)
- A single Service routes to both

Both deployments already exist with label `app: myapp`.

<details>
<summary>Answer</summary>

```bash
# Scale deployments for 10% canary
kubectl scale deploy stable-app --replicas=9
kubectl scale deploy canary-app --replicas=1

# Create service that matches both (using common label)
kubectl expose deploy stable-app --name=myapp-svc --port=80 --selector=app=myapp

# Verify endpoints include pods from both deployments
kubectl get ep myapp-svc
```

</details>

---

### Question 9: Deployment Strategy
**[2 minutes]**

A database application requires that only one version runs at a time (no concurrent versions). What Deployment strategy should you use, and how do you configure it?

<details>
<summary>Answer</summary>

Use the `Recreate` strategy:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database
spec:
  strategy:
    type: Recreate
  # ... rest of spec
```

The `Recreate` strategy terminates all existing pods before creating new ones, ensuring no two versions run simultaneously.

</details>

---

### Question 10: Helm Values
**[2 minutes]**

Get the currently applied values for a Helm release named `production-app`. Then upgrade it keeping existing values but adding `service.type=LoadBalancer`.

<details>
<summary>Answer</summary>

```bash
# Get current values
helm get values production-app

# Upgrade keeping existing values, adding new one
helm upgrade production-app CHART_NAME \
  --reuse-values \
  --set service.type=LoadBalancer
```

Key: `--reuse-values` keeps all existing custom values.

</details>

---

## Scoring

| Questions Correct | Score | Status |
|-------------------|-------|--------|
| 10/10 | 100% | Excellent - Ready for exam |
| 8-9/10 | 80-90% | Good - Minor review needed |
| 6-7/10 | 60-70% | Review weak areas |
| <6/10 | <60% | Revisit Part 2 modules |

---

## Cleanup

```bash
k delete deploy webapp api stable-app canary-app 2>/dev/null
k delete svc app-svc myapp-svc 2>/dev/null
helm uninstall my-nginx -n web 2>/dev/null
helm uninstall my-app 2>/dev/null
helm uninstall production-app 2>/dev/null
k delete ns web 2>/dev/null
```

---

## Key Takeaways

If you scored less than 80%, review these areas:

- **Missed Q1-2**: Review Module 2.1 (Deployments) - rolling updates and rollbacks
- **Missed Q3-4**: Review Module 2.2 (Helm) - install, upgrade, rollback commands
- **Missed Q5-6**: Review Module 2.3 (Kustomize) - basic structure and transformations
- **Missed Q7-8**: Review Module 2.4 (Strategies) - blue/green and canary patterns
- **Missed Q9-10**: Review strategy types and Helm values management

---

## Next Part

[Part 3: Application Observability and Maintenance](../part3-observability/module-3.1-probes.md) - Probes, logging, debugging, and API deprecations.
