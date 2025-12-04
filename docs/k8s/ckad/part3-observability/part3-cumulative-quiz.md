# Part 3 Cumulative Quiz: Application Observability and Maintenance

> **Time Limit**: 20 minutes (simulating exam pressure)
>
> **Passing Score**: 80% (8/10 questions)

This quiz tests your mastery of:
- Application probes (liveness, readiness, startup)
- Container logging
- Debugging techniques
- Monitoring with kubectl top
- API deprecations

---

## Instructions

1. Try each question without looking at answers
2. Time yourself—speed matters for CKAD
3. Use only `kubectl` and `kubernetes.io/docs`
4. Check answers after completing all questions

---

## Questions

### Question 1: Liveness Probe
**[2 minutes]**

Create a Pod named `health-check` with nginx that:
- Has an HTTP liveness probe on path `/` port `80`
- Checks every 10 seconds
- Waits 5 seconds before first check

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: health-check
spec:
  containers:
  - name: nginx
    image: nginx
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 10
EOF
```

</details>

---

### Question 2: Readiness Probe
**[2 minutes]**

A pod `webapp` has a readiness probe configured, but it's never becoming Ready. How do you investigate?

<details>
<summary>Answer</summary>

```bash
# Check pod status
k get pod webapp

# Describe to see probe config and events
k describe pod webapp | grep -A10 Readiness
k describe pod webapp | tail -20

# Check endpoints (pod should not be in endpoints if not ready)
k get endpoints

# Check if probe path/port is correct
k exec webapp -- curl -s localhost:8080/ready
```

</details>

---

### Question 3: Combined Probes
**[3 minutes]**

Create a Deployment named `api-server` with 2 replicas that:
- Uses image `nginx`
- Has startup probe: HTTP GET `/` port 80, failure threshold 30, period 10s
- Has liveness probe: HTTP GET `/` port 80, period 10s
- Has readiness probe: HTTP GET `/` port 80, period 5s

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
        startupProbe:
          httpGet:
            path: /
            port: 80
          failureThreshold: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /
            port: 80
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          periodSeconds: 5
EOF
```

</details>

---

### Question 4: Container Logs
**[1 minute]**

Get the last 50 lines of logs from the previous instance of container `app` in pod `crashing-pod`.

<details>
<summary>Answer</summary>

```bash
k logs crashing-pod -c app --previous --tail=50
```

</details>

---

### Question 5: Multi-Container Logs
**[2 minutes]**

A pod `multi-app` has containers named `frontend` and `backend`. Stream logs from both containers.

<details>
<summary>Answer</summary>

```bash
# All containers at once
k logs multi-app --all-containers -f

# Or separately
k logs multi-app -c frontend -f &
k logs multi-app -c backend -f
```

</details>

---

### Question 6: Debug CrashLoopBackOff
**[2 minutes]**

A pod is in CrashLoopBackOff. What's your debugging workflow?

<details>
<summary>Answer</summary>

```bash
# 1. Check current status
k get pod crashing-pod

# 2. Get logs from crashed instance
k logs crashing-pod --previous

# 3. Check exit code and events
k describe pod crashing-pod | grep -A5 "Last State"
k describe pod crashing-pod | tail -15

# 4. Check if liveness probe is too aggressive
k describe pod crashing-pod | grep -A5 Liveness

# 5. If needed, check container config
k get pod crashing-pod -o yaml | grep -A20 containers
```

</details>

---

### Question 7: Service Debug
**[2 minutes]**

A Service `web-svc` has no endpoints. How do you find and fix the problem?

<details>
<summary>Answer</summary>

```bash
# Check endpoints
k get endpoints web-svc

# Get service selector
k describe svc web-svc | grep Selector

# Get pod labels
k get pods --show-labels

# If labels don't match, fix the service or pods
# Example: Fix service selector
k patch svc web-svc -p '{"spec":{"selector":{"app":"correct-label"}}}'

# Verify
k get endpoints web-svc
```

</details>

---

### Question 8: Resource Monitoring
**[2 minutes]**

Find the top 5 pods by memory usage across all namespaces.

<details>
<summary>Answer</summary>

```bash
k top pods -A --sort-by=memory | head -6
```

(head -6 because first line is header)

</details>

---

### Question 9: API Version Lookup
**[1 minute]**

What are the current API versions for these resources?
- Ingress
- CronJob
- NetworkPolicy

<details>
<summary>Answer</summary>

```bash
# Quick lookup
k explain ingress | grep VERSION
# networking.k8s.io/v1

k explain cronjob | grep VERSION
# batch/v1

k explain networkpolicy | grep VERSION
# networking.k8s.io/v1
```

</details>

---

### Question 10: Exec Probe
**[2 minutes]**

Create a Pod named `file-check` with busybox that:
- Runs `sleep 3600`
- Has a liveness probe that checks if file `/tmp/healthy` exists
- Probe runs every 5 seconds, initial delay 10 seconds

<details>
<summary>Answer</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: file-check
spec:
  containers:
  - name: busybox
    image: busybox
    command: ['sh', '-c', 'touch /tmp/healthy && sleep 3600']
    livenessProbe:
      exec:
        command:
        - cat
        - /tmp/healthy
      initialDelaySeconds: 10
      periodSeconds: 5
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
| <6/10 | <60% | Revisit Part 3 modules |

---

## Cleanup

```bash
k delete pod health-check file-check 2>/dev/null
k delete deploy api-server 2>/dev/null
```

---

## Key Takeaways

If you scored less than 80%, review these areas:

- **Missed Q1-3**: Review Module 3.1 (Probes) - probe types and configuration
- **Missed Q4-5**: Review Module 3.2 (Logging) - log commands and multi-container
- **Missed Q6-7**: Review Module 3.3 (Debugging) - systematic troubleshooting
- **Missed Q8**: Review Module 3.4 (Monitoring) - kubectl top commands
- **Missed Q9**: Review Module 3.5 (API Deprecations) - current versions
- **Missed Q10**: Review Module 3.1 (Probes) - exec probes

---

## Next Part

[Part 4: Application Environment, Configuration and Security](../part4-environment/module-4.1-configmaps.md) - ConfigMaps, Secrets, SecurityContexts, and more.
