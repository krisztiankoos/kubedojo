# Part 5 Cumulative Quiz: Services and Networking

> **Time Limit**: 20 minutes (simulating exam pressure)
>
> **Passing Score**: 80% (8/10 questions)

This quiz tests your mastery of:
- Service types and discovery
- Ingress routing
- NetworkPolicies

---

## Instructions

1. Try each question without looking at answers
2. Time yourself—speed matters for CKAD
3. Use only `kubectl` and `kubernetes.io/docs`
4. Check answers after completing all questions

---

## Questions

### Question 1: Create ClusterIP Service
**[2 minutes]**

Create a Deployment named `web-app` with 3 replicas using nginx. Expose it with a ClusterIP Service named `web-service` on port 80.

<details>
<summary>Answer</summary>

```bash
k create deployment web-app --image=nginx --replicas=3
k expose deployment web-app --name=web-service --port=80 --target-port=80
```

</details>

---

### Question 2: Create NodePort Service
**[2 minutes]**

Create a NodePort Service named `external-web` that exposes the `web-app` deployment on NodePort 30080.

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Service
metadata:
  name: external-web
spec:
  type: NodePort
  selector:
    app: web-app
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080
EOF
```

Or delete existing service and recreate:
```bash
k expose deployment web-app --name=external-web --type=NodePort --port=80 --target-port=80
# Then patch for specific nodePort
k patch svc external-web -p '{"spec":{"ports":[{"port":80,"targetPort":80,"nodePort":30080}]}}'
```

</details>

---

### Question 3: Service DNS
**[1 minute]**

How would a pod in namespace `frontend` access a Service named `api` in namespace `backend` using DNS?

<details>
<summary>Answer</summary>

```
api.backend
# or
api.backend.svc
# or full FQDN
api.backend.svc.cluster.local
```

</details>

---

### Question 4: Debug Service Connectivity
**[2 minutes]**

A Service named `my-svc` has no endpoints. What commands would you run to diagnose the issue?

<details>
<summary>Answer</summary>

```bash
# Check endpoints
k get endpoints my-svc

# Get service selector
k describe svc my-svc | grep Selector

# Check pod labels
k get pods --show-labels

# Verify selector matches pod labels
# If mismatch, fix selector or pod labels
```

</details>

---

### Question 5: Simple Ingress
**[3 minutes]**

Create an Ingress named `app-ingress` that routes traffic for host `myapp.example.com` to a Service named `app-service` on port 80.

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-service
            port:
              number: 80
EOF
```

</details>

---

### Question 6: Path-Based Ingress
**[3 minutes]**

Create an Ingress named `multi-path` for host `shop.example.com` that:
- Routes `/api` to `api-svc:8080`
- Routes `/web` to `web-svc:80`

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-path
spec:
  rules:
  - host: shop.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-svc
            port:
              number: 8080
      - path: /web
        pathType: Prefix
        backend:
          service:
            name: web-svc
            port:
              number: 80
EOF
```

</details>

---

### Question 7: Default Deny NetworkPolicy
**[2 minutes]**

Create a NetworkPolicy named `deny-all` that denies all ingress traffic to pods in namespace `secure`.

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: secure
spec:
  podSelector: {}
  policyTypes:
  - Ingress
EOF
```

</details>

---

### Question 8: Allow Specific Pods
**[3 minutes]**

Create a NetworkPolicy named `allow-frontend` that:
- Applies to pods with label `tier=backend`
- Allows ingress only from pods with label `tier=frontend`
- Only on port 8080

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend
spec:
  podSelector:
    matchLabels:
      tier: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: frontend
    ports:
    - protocol: TCP
      port: 8080
EOF
```

</details>

---

### Question 9: Namespace Selector
**[2 minutes]**

Create a NetworkPolicy that allows ingress to pods labeled `app=db` only from pods in namespaces labeled `env=production`.

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-from-prod
spec:
  podSelector:
    matchLabels:
      app: db
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          env: production
EOF
```

</details>

---

### Question 10: Egress Policy
**[3 minutes]**

Create a NetworkPolicy that:
- Applies to pods with label `role=web`
- Allows egress only to pods labeled `role=api` on port 8080
- Allows egress to DNS (kube-dns) for name resolution

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-egress
spec:
  podSelector:
    matchLabels:
      role: web
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          role: api
    ports:
    - protocol: TCP
      port: 8080
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
EOF
```

</details>

---

## Scoring

| Questions Correct | Score | Status |
|-------------------|-------|--------|
| 10/10 | 100% | Excellent - Ready for exam |
| 8-9/10 | 80-90% | Good - Minor review needed |
| 6-7/10 | 60-70% | Review weak areas |
| <6/10 | <60% | Revisit Part 5 modules |

---

## Cleanup

```bash
k delete deployment web-app 2>/dev/null
k delete svc web-service external-web 2>/dev/null
k delete ingress app-ingress multi-path 2>/dev/null
k delete netpol deny-all allow-frontend db-from-prod web-egress 2>/dev/null
```

---

## Key Takeaways

If you scored less than 80%, review these areas:

- **Missed Q1-2**: Review Module 5.1 (Services) - Service types and creation
- **Missed Q3-4**: Review Module 5.1 (Services) - DNS and debugging
- **Missed Q5-6**: Review Module 5.2 (Ingress) - routing rules
- **Missed Q7-10**: Review Module 5.3 (NetworkPolicies) - selectors and rules

---

## CKAD Curriculum Complete!

Congratulations on completing all CKAD curriculum modules:

- **Part 1**: Application Design and Build (Pods, Jobs, Multi-container patterns)
- **Part 2**: Application Deployment (Deployments, Helm, Kustomize)
- **Part 3**: Application Observability (Probes, Logging, Debugging)
- **Part 4**: Application Environment (ConfigMaps, Secrets, Security)
- **Part 5**: Services and Networking (Services, Ingress, NetworkPolicies)

### Next Steps

1. **Practice, practice, practice** - Speed matters for CKAD
2. **Use killer.sh** for realistic exam simulation
3. **Review weak areas** - Focus on topics you scored lowest on
4. **Master imperative commands** - Save time on the exam

Good luck on your CKAD exam!
