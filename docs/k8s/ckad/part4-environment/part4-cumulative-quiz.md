# Part 4 Cumulative Quiz: Application Environment, Configuration and Security

> **Time Limit**: 25 minutes (simulating exam pressure)
>
> **Passing Score**: 80% (8/10 questions)

This quiz tests your mastery of:
- ConfigMaps and Secrets
- Resource requirements and limits
- SecurityContexts
- ServiceAccounts
- Custom Resource Definitions

---

## Instructions

1. Try each question without looking at answers
2. Time yourself—speed matters for CKAD
3. Use only `kubectl` and `kubernetes.io/docs`
4. Check answers after completing all questions

---

## Questions

### Question 1: ConfigMap from Literal
**[2 minutes]**

Create a ConfigMap named `app-settings` with these values:
- `LOG_LEVEL=debug`
- `MAX_CONNECTIONS=100`
- `ENVIRONMENT=staging`

<details>
<summary>Answer</summary>

```bash
k create configmap app-settings \
  --from-literal=LOG_LEVEL=debug \
  --from-literal=MAX_CONNECTIONS=100 \
  --from-literal=ENVIRONMENT=staging
```

</details>

---

### Question 2: Secret as Environment Variable
**[3 minutes]**

Create a Secret named `db-creds` with `username=admin` and `password=secret123`. Then create a Pod named `db-client` using nginx that has these values as environment variables `DB_USER` and `DB_PASS`.

<details>
<summary>Answer</summary>

```bash
k create secret generic db-creds \
  --from-literal=username=admin \
  --from-literal=password=secret123

cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: db-client
spec:
  containers:
  - name: nginx
    image: nginx
    env:
    - name: DB_USER
      valueFrom:
        secretKeyRef:
          name: db-creds
          key: username
    - name: DB_PASS
      valueFrom:
        secretKeyRef:
          name: db-creds
          key: password
EOF
```

</details>

---

### Question 3: Resource Limits
**[2 minutes]**

Create a Pod named `limited-pod` with nginx that has:
- Memory request: 128Mi
- Memory limit: 256Mi
- CPU request: 100m
- CPU limit: 200m

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: limited-pod
spec:
  containers:
  - name: nginx
    image: nginx
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "200m"
EOF
```

</details>

---

### Question 4: SecurityContext - Run As Non-Root
**[3 minutes]**

Create a Pod named `secure-pod` with busybox that:
- Runs as user ID 1000
- Runs as group ID 3000
- Has `fsGroup` set to 2000
- Runs command `id && sleep 3600`

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
  containers:
  - name: busybox
    image: busybox
    command: ['sh', '-c', 'id && sleep 3600']
EOF
```

Verify: `k logs secure-pod` should show `uid=1000 gid=3000 groups=2000,3000`

</details>

---

### Question 5: ConfigMap as Volume
**[3 minutes]**

Create a ConfigMap named `nginx-config` from this content:
```
server {
    listen 8080;
    location / {
        return 200 'ConfigMap works!\n';
    }
}
```

Then create a Pod named `nginx-custom` that mounts this ConfigMap to `/etc/nginx/conf.d/default.conf`.

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' > /tmp/default.conf
server {
    listen 8080;
    location / {
        return 200 'ConfigMap works!\n';
    }
}
EOF

k create configmap nginx-config --from-file=/tmp/default.conf

cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: nginx-custom
spec:
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - name: config
      mountPath: /etc/nginx/conf.d/default.conf
      subPath: default.conf
  volumes:
  - name: config
    configMap:
      name: nginx-config
EOF
```

</details>

---

### Question 6: ServiceAccount
**[2 minutes]**

Create a ServiceAccount named `app-sa` and a Pod named `app-pod` with nginx that uses this ServiceAccount.

<details>
<summary>Answer</summary>

```bash
k create sa app-sa

cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  serviceAccountName: app-sa
  containers:
  - name: nginx
    image: nginx
EOF

# Verify
k get pod app-pod -o jsonpath='{.spec.serviceAccountName}'
```

</details>

---

### Question 7: Decode Secret
**[1 minute]**

A Secret named `api-secret` exists with a key `api-key`. How do you decode and display its value?

<details>
<summary>Answer</summary>

```bash
k get secret api-secret -o jsonpath='{.data.api-key}' | base64 -d
echo  # newline
```

</details>

---

### Question 8: Drop Capabilities
**[3 minutes]**

Create a Pod named `minimal-caps` with nginx that:
- Drops ALL capabilities
- Adds only `NET_BIND_SERVICE` capability
- Prevents privilege escalation

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: minimal-caps
spec:
  containers:
  - name: nginx
    image: nginx
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE
EOF
```

</details>

---

### Question 9: QoS Class
**[2 minutes]**

Create a Pod named `guaranteed-pod` with nginx that has Guaranteed QoS class. What resource configuration is required?

<details>
<summary>Answer</summary>

For Guaranteed QoS, requests must equal limits for both CPU and memory:

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: guaranteed-pod
spec:
  containers:
  - name: nginx
    image: nginx
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "128Mi"
        cpu: "100m"
EOF

# Verify
k get pod guaranteed-pod -o jsonpath='{.status.qosClass}'
# Should output: Guaranteed
```

</details>

---

### Question 10: Custom Resource
**[3 minutes]**

Given that a CRD for `databases.example.com` exists, create a Custom Resource:
- Name: `production-db`
- Kind: `Database`
- apiVersion: `example.com/v1`
- spec.engine: `postgres`
- spec.replicas: `3`

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: example.com/v1
kind: Database
metadata:
  name: production-db
spec:
  engine: postgres
  replicas: 3
EOF

# Verify
k get databases
k describe database production-db
```

</details>

---

## Scoring

| Questions Correct | Score | Status |
|-------------------|-------|--------|
| 10/10 | 100% | Excellent - Ready for exam |
| 8-9/10 | 80-90% | Good - Minor review needed |
| 6-7/10 | 60-70% | Review weak areas |
| <6/10 | <60% | Revisit Part 4 modules |

---

## Cleanup

```bash
k delete configmap app-settings nginx-config 2>/dev/null
k delete secret db-creds api-secret 2>/dev/null
k delete pod db-client limited-pod secure-pod nginx-custom app-pod minimal-caps guaranteed-pod 2>/dev/null
k delete sa app-sa 2>/dev/null
k delete database production-db 2>/dev/null
```

---

## Key Takeaways

If you scored less than 80%, review these areas:

- **Missed Q1, Q5**: Review Module 4.1 (ConfigMaps) - creation and volume mounting
- **Missed Q2, Q7**: Review Module 4.2 (Secrets) - env vars and decoding
- **Missed Q3, Q9**: Review Module 4.3 (Resources) - requests, limits, QoS
- **Missed Q4, Q8**: Review Module 4.4 (SecurityContexts) - user/group, capabilities
- **Missed Q6**: Review Module 4.5 (ServiceAccounts) - creating and assigning
- **Missed Q10**: Review Module 4.6 (CRDs) - custom resources

---

## Next Part

[Part 5: Services and Networking](../part5-networking/module-5.1-services.md) - Services, Ingress, and Network Policies.
