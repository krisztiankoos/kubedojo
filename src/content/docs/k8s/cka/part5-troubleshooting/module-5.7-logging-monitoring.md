---
title: "Module 5.7: Logging & Monitoring"
slug: k8s/cka/part5-troubleshooting/module-5.7-logging-monitoring
sidebar:
  order: 8
lab:
  id: cka-5.7-logging-monitoring
  url: https://killercoda.com/kubedojo/scenario/cka-5.7-logging-monitoring
  duration: "35 min"
  difficulty: intermediate
  environment: kubernetes
---
> **Complexity**: `[MEDIUM]` - Essential observability skills
>
> **Time to Complete**: 40-50 minutes
>
> **Prerequisites**: Module 5.1 (Methodology), Modules 5.2-5.6 (troubleshooting specifics)

---

## What You'll Be Able to Do

After this module, you will be able to:
- **Query** container logs using kubectl logs with container selection, previous logs, and follow mode
- **Monitor** cluster resource usage with kubectl top (nodes and pods) and explain metrics-server
- **Implement** sidecar-based logging for applications that write to files instead of stdout
- **Debug** metrics-server issues and explain how resource metrics flow from kubelet to API server

---

## Why This Module Matters

Logs and metrics are your eyes into what's happening in a cluster. Without them, troubleshooting is guesswork. Understanding how to access container logs, interpret events, and use metrics to identify resource issues is fundamental to effective Kubernetes operations.

> **The Security Camera Analogy**
>
> Logs are like security camera footage - they record what happened and when. Events are like a security guard's incident reports - notable occurrences written down. Metrics are like building sensors - temperature, occupancy, power usage. Together, they tell the complete story of what's happening in your cluster.

---

## What You'll Learn

By the end of this module, you'll be able to:
- Access and filter container logs effectively
- Understand Kubernetes events and their significance
- Use kubectl top for resource metrics
- Navigate log locations on nodes
- Apply logging strategies for troubleshooting

---

## Did You Know?

- **Logs go to stdout/stderr**: Kubernetes captures whatever containers write to stdout and stderr - that's the only logging "magic"
- **Events are stored in etcd**: Events are regular Kubernetes objects with a 1-hour default TTL
- **Metrics Server is not installed by default**: kubectl top requires Metrics Server to be running
- **Log rotation is kubelet's job**: kubelet rotates container logs based on size and count settings

---

## Part 1: Container Logs

### 1.1 How Container Logging Works

```
┌──────────────────────────────────────────────────────────────┐
│                 CONTAINER LOGGING FLOW                        │
│                                                               │
│   Container                                                   │
│   ┌────────────────────────────────────────────────────┐     │
│   │  Application                                        │     │
│   │       │                                             │     │
│   │       ├── stdout ──────┐                           │     │
│   │       │                │                           │     │
│   │       └── stderr ──────┼────▶ Container runtime    │     │
│   │                        │      captures output      │     │
│   └────────────────────────────────────────────────────┘     │
│                            │                                  │
│                            ▼                                  │
│   Node filesystem                                             │
│   /var/log/containers/<pod>_<ns>_<container>-<id>.log        │
│                            │                                  │
│                            ▼                                  │
│   kubectl logs (reads these files via kubelet API)           │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### 1.2 Basic Log Commands

```bash
# View logs from a pod (single container)
k logs <pod>

# View logs from specific container (multi-container pod)
k logs <pod> -c <container>

# Follow logs in real-time
k logs <pod> -f

# Show last N lines
k logs <pod> --tail=50

# Show logs since time
k logs <pod> --since=1h
k logs <pod> --since=30m

# Show logs with timestamps
k logs <pod> --timestamps

# Combine options
k logs <pod> --tail=100 --timestamps -f
```

> **Stop and think**: If a pod has multiple containers and you run `kubectl logs <pod>`, what happens? How does Kubernetes know which container's logs to show?

### 1.3 Multi-Container Pod Logs

```bash
# List containers in a pod
k get pod <pod> -o jsonpath='{.spec.containers[*].name}'

# Get logs from specific container
k logs <pod> -c <container>

# Get logs from all containers
k logs <pod> --all-containers=true

# Get logs from init containers
k logs <pod> -c <init-container>
```

### 1.4 Previous Container Logs

Crucial for CrashLoopBackOff troubleshooting:

```bash
# Get logs from previous container instance (after crash)
k logs <pod> --previous
k logs <pod> -c <container> --previous

# This shows what was logged before the container died
# Essential for understanding why it crashed
```

### 1.5 Logs from Labels/Selectors

```bash
# Logs from all pods with a label
k logs -l app=nginx

# Logs from all pods in a deployment
k logs deployment/my-deployment

# Follow logs from all matching pods
k logs -l app=nginx -f

# With container name for multi-container pods
k logs -l app=nginx -c <container>
```

---

## Part 2: Kubernetes Events

### 2.1 Understanding Events

```
┌──────────────────────────────────────────────────────────────┐
│                   KUBERNETES EVENTS                           │
│                                                               │
│   Events are generated by:                                    │
│   • Scheduler (scheduling decisions)                         │
│   • kubelet (container lifecycle)                            │
│   • Controllers (resource management)                        │
│   • API server (API operations)                              │
│                                                               │
│   Event Types:                                                │
│   • Normal:  Informational, things working as expected       │
│   • Warning: Something unexpected, might need attention      │
│                                                               │
│   Important: Events expire after ~1 hour by default!         │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

> **Pause and predict**: If a pod was created 3 days ago and has been CrashLoopBackOff ever since, will `kubectl get events` show the original scheduling and creation events? Why or why not?

### 2.2 Viewing Events

```bash
# All events in current namespace
k get events

# All events cluster-wide
k get events -A

# Sort by time (most recent last)
k get events --sort-by='.lastTimestamp'

# Sort by time (most recent first)
k get events --sort-by='.lastTimestamp' | tac

# Filter by type
k get events --field-selector type=Warning

# Events for specific object
k get events --field-selector involvedObject.name=<pod-name>

# Watch events in real-time
k get events -w
```

### 2.3 Common Event Reasons

| Reason | Type | What It Means |
|--------|------|---------------|
| Scheduled | Normal | Pod assigned to node |
| Pulled | Normal | Image successfully pulled |
| Created | Normal | Container created |
| Started | Normal | Container started |
| Killing | Normal | Container being terminated |
| FailedScheduling | Warning | Couldn't find suitable node |
| FailedMount | Warning | Volume mount failed |
| Unhealthy | Warning | Probe failed |
| BackOff | Warning | Container crashing, backing off |
| FailedCreate | Warning | Controller couldn't create pod |
| Evicted | Warning | Pod evicted from node |
| OOMKilling | Warning | Container killed for OOM |

### 2.4 Events in Describe Output

```bash
# Events appear in describe output
k describe pod <pod>
# Look for the Events section at the bottom

k describe node <node>
# Shows node-level events

k describe pvc <pvc>
# Shows volume binding events
```

---

## Part 3: Resource Metrics

### 3.1 Metrics Server

```
┌──────────────────────────────────────────────────────────────┐
│                   METRICS SERVER                              │
│                                                               │
│   Nodes                    Metrics Server                     │
│   ┌──────────┐            ┌──────────────┐                   │
│   │ kubelet  │────────────│ Collects     │                   │
│   │ /metrics │            │ aggregates   │                   │
│   └──────────┘            │ exposes      │                   │
│                           └──────┬───────┘                   │
│                                  │                           │
│                           metrics.k8s.io API                  │
│                                  │                           │
│                                  ▼                           │
│                           kubectl top                        │
│                                                               │
│   Without Metrics Server → kubectl top fails                 │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Checking Metrics Server

```bash
# Check if Metrics Server is installed
k -n kube-system get pods | grep metrics-server

# Check metrics API
k get apiservices | grep metrics

# If not installed, top commands will fail
k top nodes  # Error: Metrics API not available
```

### 3.3 Using kubectl top

```bash
# Node resource usage
k top nodes

# Pod resource usage (current namespace)
k top pods

# Pod resource usage (all namespaces)
k top pods -A

# Sort by CPU
k top pods --sort-by=cpu

# Sort by memory
k top pods --sort-by=memory

# Per-container usage
k top pods --containers

# Specific pod
k top pod <pod-name>
```

> **Stop and think**: If `kubectl top pods` shows a pod using 200m CPU, but its limit is 100m, what is likely happening to the application running inside that pod?

### 3.4 Interpreting Metrics

```
┌──────────────────────────────────────────────────────────────┐
│                   METRIC INTERPRETATION                       │
│                                                               │
│   NAME         CPU(cores)   MEMORY(bytes)                    │
│   my-pod       100m         256Mi                            │
│                                                               │
│   CPU: 100m = 100 millicores = 0.1 CPU core                 │
│        1000m = 1 core                                        │
│                                                               │
│   Memory: Mi = mebibytes (1024 * 1024 bytes)                │
│           Gi = gibibytes                                     │
│                                                               │
│   Compare against requests/limits:                           │
│   If usage >> requests: might get OOMKilled                 │
│   If usage >> limit: will get OOMKilled or CPU throttled    │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### 3.5 Resource Comparison

```bash
# Compare actual usage vs requests
# Step 1: Get requests
k get pod <pod> -o jsonpath='{.spec.containers[0].resources.requests}'

# Step 2: Get actual usage
k top pod <pod>

# If actual >> requests, pod is under-requested
# If actual << requests, pod is over-requested
```

---

## Part 4: Node-Level Logs

### 4.1 Log Locations on Nodes

```
┌──────────────────────────────────────────────────────────────┐
│                NODE LOG LOCATIONS                             │
│                                                               │
│   Container logs:                                             │
│   /var/log/containers/<pod>_<ns>_<container>-<id>.log        │
│                                                               │
│   Pod logs (symlinks):                                        │
│   /var/log/pods/<ns>_<pod>_<uid>/                            │
│                                                               │
│   kubelet logs:                                               │
│   journalctl -u kubelet                                       │
│                                                               │
│   Container runtime logs:                                     │
│   journalctl -u containerd                                    │
│   journalctl -u docker (if using docker)                     │
│                                                               │
│   System logs:                                                │
│   /var/log/syslog or /var/log/messages                       │
│   journalctl                                                  │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 Accessing Node Logs

```bash
# SSH to node first
ssh <node>

# Container logs directly
ls /var/log/containers/
tail -f /var/log/containers/<pod>*.log

# kubelet logs
journalctl -u kubelet -f
journalctl -u kubelet --since "10 minutes ago"
journalctl -u kubelet | grep -i error

# Container runtime logs
journalctl -u containerd -f

# System messages
dmesg | tail -50
journalctl -xe
```

### 4.3 Control Plane Component Logs

On control plane nodes:

```bash
# If using static pods (kubeadm)
# Logs available via kubectl
k -n kube-system logs kube-apiserver-<node>
k -n kube-system logs kube-scheduler-<node>
k -n kube-system logs kube-controller-manager-<node>
k -n kube-system logs etcd-<node>

# Or directly on node via journalctl (if systemd services)
journalctl -u kube-apiserver
journalctl -u kube-scheduler
journalctl -u kube-controller-manager
journalctl -u etcd
```

---

## Part 5: Logging Strategies for Troubleshooting

### 5.1 The Log Analysis Workflow

```
┌──────────────────────────────────────────────────────────────┐
│              LOG ANALYSIS WORKFLOW                            │
│                                                               │
│   1. Start with events                                        │
│      k describe <resource> | grep -A 20 Events               │
│                                                               │
│   2. Check recent events cluster-wide                        │
│      k get events --sort-by='.lastTimestamp' | tail          │
│                                                               │
│   3. Get container logs                                       │
│      k logs <pod>                                             │
│      k logs <pod> --previous  (if crashed)                   │
│                                                               │
│   4. Filter for errors                                        │
│      k logs <pod> | grep -i error                            │
│      k logs <pod> | grep -i exception                        │
│                                                               │
│   5. Check timing                                             │
│      k logs <pod> --timestamps --since=10m                   │
│                                                               │
│   6. Check related components                                 │
│      If pod issues: check node                               │
│      If network issues: check CNI, kube-proxy                │
│      If DNS issues: check CoreDNS                            │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### 5.2 Filtering Log Output

```bash
# Search for errors
k logs <pod> | grep -i error
k logs <pod> | grep -i exception
k logs <pod> | grep -i fatal

# Exclude noise
k logs <pod> | grep -v "INFO"
k logs <pod> | grep -v "health check"

# Complex filters
k logs <pod> | grep -E "error|warning|failed"

# With timestamps and filtering
k logs <pod> --timestamps | grep "2024-01-15T10:3"

# Count error occurrences
k logs <pod> | grep -c error
```

### 5.3 Multi-Pod Log Analysis

```bash
# Logs from all pods in deployment
k logs deployment/<name> --all-containers

# Aggregate logs from multiple pods with labels
k logs -l app=frontend --all-containers

# Using stern (not built-in, but useful)
# stern <pod-name-pattern>

# Workaround: loop through pods
for pod in $(k get pods -l app=nginx -o name); do
  echo "=== $pod ==="
  k logs $pod --tail=5
done
```

### 5.4 Correlating Events and Logs

```bash
# Get event time
k get events --field-selector involvedObject.name=my-pod

# Note the timestamp, then check logs around that time
k logs my-pod --since-time="2024-01-15T10:30:00Z"

# Or use relative time
k logs my-pod --since=5m
```

---

## Part 6: Monitoring Patterns

### 6.1 Proactive Monitoring Commands

```bash
# Quick cluster health check
k get nodes
k get pods -A | grep -v Running
k top nodes
k get events -A --field-selector type=Warning

# Create a simple monitoring script
watch -n 5 'kubectl get pods -A | grep -v Running | grep -v Completed'
```

### 6.2 Resource Pressure Detection

```bash
# Check for node pressure
k describe nodes | grep -E "MemoryPressure|DiskPressure|PIDPressure"

# Check for pods using excessive resources
k top pods -A --sort-by=memory | head -10
k top pods -A --sort-by=cpu | head -10

# Check for pending pods (might indicate resource shortage)
k get pods -A --field-selector=status.phase=Pending
```

### 6.3 Debugging with Temporary Pods

```bash
# Create debug pod with networking tools
k run debug --image=nicolaka/netshoot --rm -it --restart=Never -- bash

# Simple debug pod
k run debug --image=busybox:1.36 --rm -it --restart=Never -- sh

# Debug with specific service account
k run debug --image=busybox:1.36 --rm -it --restart=Never --serviceaccount=<sa> -- sh

# Debug in specific namespace
k run debug -n <namespace> --image=busybox:1.36 --rm -it --restart=Never -- sh
```

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Forgetting `--previous` | Can't see crash logs | Use `--previous` for CrashLoopBackOff |
| Not filtering logs | Too much noise | Use grep, `--since`, `--tail` |
| Ignoring events | Miss obvious clues | Always check events first |
| Missing multi-container | Logs from wrong container | Use `-c <container>` or `--all-containers` |
| Events expired | No historical data | Check logs immediately after incident |
| No Metrics Server | kubectl top fails | Install Metrics Server |

---

## Quiz

### Q1: Investigating a Crash
You deploy a new version of your application. The pod enters a `CrashLoopBackOff` state. When you run `kubectl logs my-app`, you only see a single line saying "Starting application...", but the application keeps crashing. How do you find the actual error that caused the crash, and why does the standard log command hide it?

<details>
<summary>Answer</summary>

You must use the command `kubectl logs my-app --previous` to see the actual error. When a pod is in a `CrashLoopBackOff` state, it means the container is repeatedly dying and being restarted by the kubelet. The standard `kubectl logs` command only shows the output of the *currently running* container instance. Since the current instance just started and hasn't crashed yet, you only see the initial startup message. By appending the `--previous` flag, you instruct Kubernetes to retrieve the logs from the container instance that most recently terminated, which will contain the stack trace or error message explaining why it died.

</details>

### Q2: Missing Historical Context
A developer reports that their batch job failed sometime over the weekend, about 48 hours ago. They ask you to check the Kubernetes events to see if there were any node scheduling issues or image pull errors at that time. When you run `kubectl get events --field-selector involvedObject.name=batch-job`, it returns "No resources found". What happened to the events, and how could you have preserved them?

<details>
<summary>Answer</summary>

Kubernetes events have a default time-to-live (TTL) of exactly one hour. They are not designed for long-term auditing or historical logging; rather, they are transient objects stored in etcd to provide immediate feedback about cluster operations. After the one-hour window expires, the Kubernetes garbage collector automatically deletes them to prevent etcd from running out of storage space. To preserve events for long-term analysis, you must export them to an external logging system or observability platform using a dedicated event-shipping tool (like eventrouter or a fluentd plugin) before they expire.

</details>

### Q3: Missing Resource Metrics
You are trying to determine if a specific deployment needs its memory limits increased. You run the command `kubectl top pods -n production`, but the API server returns an error stating "metrics not available". You verify that your kubeconfig is correct and you have the necessary RBAC permissions. What cluster component is likely missing or failing, and why does this command depend on it?

<details>
<summary>Answer</summary>

The cluster is likely missing the Metrics Server, or the Metrics Server deployment is currently unhealthy. The `kubectl top` command does not directly query the nodes or the kubelet for resource utilization data. Instead, it queries the `metrics.k8s.io` API, which must be served by an aggregation layer component. The Metrics Server acts as this component; it continuously polls the kubelet API on each node, aggregates the CPU and memory usage data, and exposes it through the metrics API. Without this server running and correctly registered with the main API server, the metrics endpoint will not exist, causing the command to fail.

</details>

### Q4: Aggregating Sidecar Logs
You have a pod named `web-app` that runs your main application container and a sidecar container running a log forwarding agent. You suspect the log forwarder is failing to authenticate, but you also want to see if the main application is logging any connection errors at the same time. How can you view the logs from both containers simultaneously in a single command, and why is this useful?

<details>
<summary>Answer</summary>

You can view the combined output by using the command `kubectl logs web-app --all-containers=true`. By default, if you run `kubectl logs` against a multi-container pod without specifying a container, Kubernetes will either prompt you to specify one or just pick the first one listed in the pod spec. Using the `--all-containers` flag instructs the API server to fetch the logs from every container within the specified pod and interleave them in the output. This is highly useful for correlating events across tightly coupled containers, as it allows you to see the exact sequence of events occurring across both the main application and its sidecar.

</details>

### Q5: Bypassing the API Server
The Kubernetes API server is currently unresponsive due to a certificate expiration issue. You have SSH access to the worker node where a critical database pod is running, and you need to check its logs immediately to ensure it hasn't corrupted its data volume. How do you view the logs for this specific container directly on the node, and what component manages these files?

<details>
<summary>Answer</summary>

You can view the logs directly by navigating to the `/var/log/containers/` directory on the worker node. Inside this directory, you will find log files named using the pattern `<pod-name>_<namespace>_<container-name>-<container-id>.log`. These files are actually symbolic links that point to the actual log files generated by the container runtime (such as containerd or CRI-O). The kubelet is responsible for managing these symlinks and also handles the log rotation based on its configured maximum size and file count limits, ensuring the node's disk does not fill up.

</details>

### Q6: Diagnosis Strategy
A pod is stuck in the `Pending` state. A junior administrator suggests running `kubectl logs my-pending-pod` to see what the application is complaining about. Why is this the wrong approach, and what command should they run instead to understand why the pod is stuck?

<details>
<summary>Answer</summary>

Running `kubectl logs` is the wrong approach because a pod in the `Pending` state has not yet been scheduled to a node, or its containers have not yet started executing. Since no container runtime is running the application process, there is absolutely no standard output or standard error to capture, meaning the logs command will return an error or nothing at all. Instead, the administrator should check the Kubernetes events by running `kubectl describe pod my-pending-pod` or `kubectl get events`. Events will reveal cluster-level scheduling issues, such as a lack of node resources, failed persistent volume claims, or unmet node affinity rules that are preventing the pod from starting.

</details>

---

## Hands-On Exercise: Log and Metric Analysis

### Scenario

Practice using logs and metrics for troubleshooting.

### Setup

```bash
# Create test namespace
k create ns logging-lab

# Create a pod that generates logs
cat <<'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: log-generator
  namespace: logging-lab
spec:
  containers:
  - name: logger
    image: busybox:1.36
    command:
    - sh
    - -c
    - |
      i=0
      while true; do
        echo "$(date '+%Y-%m-%d %H:%M:%S') INFO: Log message $i"
        if [ $((i % 5)) -eq 0 ]; then
          echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: Something went wrong at iteration $i" >&2
        fi
        i=$((i+1))
        sleep 2
      done
EOF

# Create a crashy pod for --previous demo
cat <<'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: crashy-pod
  namespace: logging-lab
spec:
  containers:
  - name: crasher
    image: busybox:1.36
    command:
    - sh
    - -c
    - |
      echo "Starting up..."
      sleep 5
      echo "About to crash!"
      exit 1
EOF
```

### Task 1: Basic Log Operations

```bash
# View logs
k logs -n logging-lab log-generator

# Follow logs
k logs -n logging-lab log-generator -f
# (Ctrl+C to stop)

# Last 10 lines
k logs -n logging-lab log-generator --tail=10

# With timestamps
k logs -n logging-lab log-generator --tail=10 --timestamps
```

### Task 2: Filtering Logs

```bash
# Find errors only
k logs -n logging-lab log-generator | grep ERROR

# Count errors
k logs -n logging-lab log-generator | grep -c ERROR

# Exclude INFO messages
k logs -n logging-lab log-generator | grep -v INFO
```

### Task 3: Previous Container Logs

```bash
# Wait for crashy-pod to crash and restart
k get pod -n logging-lab crashy-pod -w

# When it shows CrashLoopBackOff or restarts, check previous logs
k logs -n logging-lab crashy-pod --previous
```

### Task 4: Events Analysis

```bash
# All events in namespace
k get events -n logging-lab --sort-by='.lastTimestamp'

# Describe pod for events
k describe pod -n logging-lab crashy-pod | grep -A 10 Events

# Watch for new events
k get events -n logging-lab -w
```

### Task 5: Metrics (if Metrics Server installed)

```bash
# Node metrics
k top nodes

# Pod metrics
k top pods -n logging-lab

# All pods by memory
k top pods -A --sort-by=memory | head
```

### Success Criteria

- [ ] Viewed live logs with follow
- [ ] Filtered logs for errors
- [ ] Retrieved previous container logs
- [ ] Analyzed events for crash information
- [ ] Used kubectl top (if Metrics Server available)

### Cleanup

```bash
k delete ns logging-lab
```

---

## Practice Drills

### Drill 1: View Last N Logs (30 sec)
```bash
# Task: Show last 20 log lines
k logs <pod> --tail=20
```

### Drill 2: Logs with Timestamps (30 sec)
```bash
# Task: Show logs with timestamps
k logs <pod> --timestamps
```

### Drill 3: Previous Container Logs (30 sec)
```bash
# Task: Get logs from crashed container
k logs <pod> --previous
```

### Drill 4: Multi-Container Logs (1 min)
```bash
# Task: Get logs from specific container
k get pod <pod> -o jsonpath='{.spec.containers[*].name}'
k logs <pod> -c <container-name>
```

### Drill 5: Recent Events (30 sec)
```bash
# Task: Show events sorted by time
k get events --sort-by='.lastTimestamp'
```

### Drill 6: Warning Events (30 sec)
```bash
# Task: Show only warning events
k get events --field-selector type=Warning
```

### Drill 7: Node Metrics (30 sec)
```bash
# Task: Show node resource usage
k top nodes
```

### Drill 8: Pod Metrics Sorted (30 sec)
```bash
# Task: Show top memory-consuming pods
k top pods -A --sort-by=memory | head
```

---

## Part 5 Summary

Congratulations on completing Part 5: Troubleshooting! You've learned:

1. **Methodology**: Systematic approach to diagnosis
2. **Application Failures**: Pod, container, and deployment issues
3. **Control Plane**: API server, scheduler, controller manager, etcd
4. **Worker Nodes**: kubelet, runtime, and node resources
5. **Networking**: Pod connectivity, DNS, and CNI
6. **Services**: ClusterIP, NodePort, LoadBalancer, Ingress
7. **Logging & Monitoring**: Logs, events, and metrics

With 30% of the CKA exam weight, troubleshooting is critical. Practice the drills until they're second nature.

---

## Next Steps

Continue to [Part 6: Mock Exams](../part6-mock-exams/) to test your knowledge with realistic exam scenarios.