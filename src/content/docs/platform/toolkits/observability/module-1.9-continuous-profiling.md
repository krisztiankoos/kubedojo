---
title: "Module 1.9: Continuous Profiling - The 4th Pillar of Observability"
slug: platform/toolkits/observability/module-1.9-continuous-profiling
sidebar:
  order: 10
---
## Complexity: [MEDIUM]

**Time to Complete**: 40 minutes
**Prerequisites**: Module 1.1 (Prometheus basics), Module 1.2 (OpenTelemetry concepts), general understanding of observability
**Learning Objectives**:
- Understand why continuous profiling is the 4th pillar of observability
- Deploy Parca for eBPF-based continuous profiling
- Use Pyroscope with the Grafana stack
- Read flame graphs and identify CPU/memory hotspots
- Choose the right profiling tool for your environment

---

## Why This Module Matters

Your metrics dashboard shows CPU running at 80%. Your traces confirm requests are slow. Your logs say... nothing useful. You know *something* is burning resources, but you have no idea *which function in which service* is responsible.

This is the gap that continuous profiling fills. It answers the question that metrics, logs, and traces cannot: **what exact line of code is consuming your resources right now?**

> A mid-size fintech team was spending $50,000/month extra on oversized EC2 instances. Their Go payment service consumed 4 CPU cores at steady state. They assumed it was "just the nature of the workload." After deploying continuous profiling, they discovered a single JSON serialization function was responsible for 62% of CPU time -- a hot loop that re-encoded already-encoded payloads. A 12-line fix dropped CPU usage to 1.5 cores. They downsized their instances the same week and saved over $35,000/month.

Profiling is not a luxury. It is how you stop guessing and start *seeing* what your code actually does at runtime.

---

## Did You Know?

- Google has run **cluster-wide continuous profiling** since 2010 -- their internal tool (Google-Wide Profiling) inspired both Parca and Pyroscope
- A single flame graph can reveal performance problems that would take **days of log analysis** to find -- it compresses millions of stack samples into one visual
- eBPF-based profilers like Parca add less than **1% CPU overhead** while profiling every process on a node, because sampling happens in the kernel
- Continuous profiling can catch **memory leaks before they cause OOMs** by showing allocation hotspots trending upward over time -- something metrics alone cannot pinpoint to a specific code path

---

## The 4th Pillar of Observability

For years, observability meant three pillars: metrics, logs, and traces. But there was always a blind spot:

```
┌──────────────────────────────────────────────────────────────────┐
│                  The Four Pillars of Observability                │
│                                                                  │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────────┐ │
│  │  Metrics   │  │   Logs    │  │  Traces   │  │  Profiles    │ │
│  │           │  │           │  │           │  │              │ │
│  │ "What is  │  │ "What     │  │ "Where is │  │ "Which code  │ │
│  │  happening │  │  happened │  │  time     │  │  is burning  │ │
│  │  overall?" │  │  exactly?"│  │  spent?"  │  │  resources?" │ │
│  │           │  │           │  │           │  │              │ │
│  │ CPU: 80%  │  │ Error at  │  │ /pay took │  │ marshal()    │ │
│  │ Mem: 6 GB │  │ 14:03:22  │  │ 320ms in  │  │ uses 62%    │ │
│  │ RPS: 1200 │  │ line 42   │  │ svc-pay   │  │ of CPU time  │ │
│  └───────────┘  └───────────┘  └───────────┘  └──────────────┘ │
│                                                                  │
│  Aggregates      Discrete        Request-scoped   Code-level     │
│  over time       events          latency          resource use   │
└──────────────────────────────────────────────────────────────────┘
```

Without profiling, you know the *what* and *where* but not the *why at the code level*.

---

## Types of Profiles

Not all resource consumption problems are CPU problems. Profilers capture different profile types:

| Profile Type | What It Measures | When You Need It |
|-------------|-----------------|-----------------|
| **CPU** | Time spent executing on-CPU | Function is slow, high CPU usage |
| **Memory Allocation** | Bytes allocated by function | Memory growing, GC pressure |
| **Goroutine** (Go) | Number of active goroutines | Goroutine leaks, concurrency bugs |
| **Mutex** | Time spent waiting on locks | Contention under concurrency |
| **Block** | Time spent blocked on I/O, channels | Unexplained latency, idle waiting |
| **Wall Clock** | Real elapsed time including off-CPU | End-to-end function duration |

CPU profiles are the starting point for most investigations. Memory allocation profiles are the second most common. The others are language-specific and situational.

---

## Parca: eBPF-Based Continuous Profiling

### Architecture

Parca uses eBPF to sample stack traces from every process on a node -- no code changes, no language agents, no restarts. It is to profiling what Pixie (see [Module 1.6](module-1.6-pixie/)) is to tracing.

```
┌────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Parca Server                         │  │
│  │  ┌─────────────┐  ┌──────────┐  ┌────────────────┐  │  │
│  │  │  Storage     │  │  Query   │  │  Web UI        │  │  │
│  │  │  (columnar)  │  │  Engine  │  │  (flame graphs)│  │  │
│  │  └─────────────┘  └──────────┘  └────────────────┘  │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │ gRPC                            │
│  ┌───────────┐  ┌───────┴───────┐  ┌───────────────┐     │
│  │  Node 1   │  │   Node 2      │  │   Node 3      │     │
│  │ ┌───────┐ │  │ ┌───────────┐ │  │ ┌───────────┐ │     │
│  │ │ Parca │ │  │ │   Parca   │ │  │ │   Parca   │ │     │
│  │ │ Agent │ │  │ │   Agent   │ │  │ │   Agent   │ │     │
│  │ │(eBPF) │ │  │ │  (eBPF)  │ │  │ │  (eBPF)  │ │     │
│  │ └───┬───┘ │  │ └─────┬─────┘ │  │ └─────┬─────┘ │     │
│  │     │     │  │       │       │  │       │       │     │
│  │ [kernel]  │  │  [kernel]     │  │  [kernel]     │     │
│  └───────────┘  └───────────────┘  └───────────────┘     │
└────────────────────────────────────────────────────────────┘
```

**Key properties**:
- **Zero instrumentation**: eBPF samples stack traces from the kernel -- works with any language
- **Always-on**: Runs continuously with negligible overhead, so you have data *before* incidents
- **Columnar storage**: Efficient storage of profile data for querying over time
- **Diff views**: Compare profiles between two time ranges to see what changed

### Installation via Helm

```bash
# Add the Parca Helm repo
helm repo add parca https://parca-dev.github.io/helm-charts
helm repo update

# Install the Parca server
helm install parca-server parca/parca \
  --namespace parca --create-namespace

# Install the Parca agent (DaemonSet with eBPF)
helm install parca-agent parca/parca-agent \
  --namespace parca \
  --set "config.node=\$(NODE_NAME)" \
  --set "config.stores[0].address=parca-server.parca.svc:7070" \
  --set "config.stores[0].insecure=true"

# Verify everything is running
kubectl get pods -n parca
# NAME                            READY   STATUS    RESTARTS
# parca-server-5b8f9c7d4-x2k9l   1/1     Running   0
# parca-agent-abc12               1/1     Running   0   (one per node)
# parca-agent-def34               1/1     Running   0
```

### Dashboard: Flame Graphs, Diffs, and Labels

Access the Parca UI:

```bash
kubectl port-forward -n parca svc/parca-server 7070:7070
# Open http://localhost:7070
```

**Flame graphs** are the primary visualization. Each bar represents a function. Width = proportion of total samples. Wider bars = more resource consumption.

```
Reading a flame graph (bottom-up):

 ┌─────────────────────────────────────────────────┐
 │               main.handleRequest                │  100% of samples
 ├──────────────────────────┬──────────────────────┤
 │   json.Marshal (62%)     │  db.Query (30%)      │
 ├──────────────┬───────────┤                      │
 │ reflect (40%)│encode(22%)│                      │
 └──────────────┴───────────┴──────────────────────┘

 ^^^ This tells you: json.Marshal dominates, and reflect inside it
     is the real culprit. Optimize there first.
```

**Diff views** compare two time windows. Functions that got slower turn red; functions that improved turn green. This is invaluable after deployments -- you can see exactly which code paths regressed.

**Label filtering** lets you slice profiles by Kubernetes metadata: namespace, pod, container, node. Ask questions like "show me CPU profiles only for pods in the `payments` namespace."

---

## Pyroscope: Profiling for the Grafana Stack

### Architecture

Pyroscope (now part of Grafana Labs) takes a different approach: it supports both **push mode** (application sends profiles via SDK) and **pull mode** (scrapes pprof endpoints, like Prometheus scrapes metrics).

```
┌──────────────────────────────────────────────────────────┐
│                       Pyroscope                           │
│                                                          │
│  Push Mode:                    Pull Mode:                │
│  ┌─────────┐                  ┌─────────────┐            │
│  │  App +   │──── SDK push──▶│  Pyroscope   │            │
│  │  Agent   │                │  Server      │            │
│  └─────────┘                 │             │◀── scrape   │
│                              │             │   /debug/   │
│  ┌─────────┐                 │             │   pprof     │
│  │  App +   │──── SDK push──▶│             │            │
│  │  Agent   │                └──────┬──────┘            │
│  └─────────┘                       │                    │
│                              ┌─────▼──────┐             │
│                              │  Grafana    │             │
│                              │  (visualize)│             │
│                              └────────────┘             │
└──────────────────────────────────────────────────────────┘
```

### Integration with Grafana

Pyroscope is a first-class Grafana data source. This means you can:

- View flame graphs directly in Grafana dashboards alongside metrics and traces
- Correlate a latency spike on a Grafana panel with the exact profile from that time window
- Use Grafana Explore to query profiles with the same UX as querying Loki or Tempo

```bash
# Deploy Pyroscope with Helm
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install pyroscope grafana/pyroscope \
  --namespace pyroscope --create-namespace

# Add Pyroscope as a data source in Grafana
# Settings > Data Sources > Add > Pyroscope
# URL: http://pyroscope.pyroscope.svc:4040
```

### Language-Specific Profiling

Pyroscope provides SDKs for deep, language-aware profiling:

| Language | Profile Types | Integration Method |
|----------|--------------|-------------------|
| **Go** | CPU, allocs, goroutines, mutex, block | `import pyroscope` or scrape `/debug/pprof` |
| **Java** | CPU, allocs, lock, wall | `pyroscope-java` agent (async-profiler) |
| **Python** | CPU, wall | `pyroscope-io` pip package |
| **Ruby** | CPU, wall | `pyroscope` gem (Stackprof-based) |
| **.NET** | CPU, exceptions, allocs | `Pyroscope.Dotnet` NuGet package |

Go example:

```go
import "github.com/grafana/pyroscope-go"

func main() {
    pyroscope.Start(pyroscope.Config{
        ApplicationName: "payment-service",
        ServerAddress:   "http://pyroscope.pyroscope.svc:4040",
        Tags:            map[string]string{"region": "us-east-1"},
        ProfileTypes: []pyroscope.ProfileType{
            pyroscope.ProfileCPU,
            pyroscope.ProfileAllocObjects,
            pyroscope.ProfileAllocSpace,
            pyroscope.ProfileGoroutines,
        },
    })
    // ... rest of your application
}
```

---

## When to Use Profiling vs Metrics vs Traces

Use this decision tree when diagnosing performance issues:

```
                    "Something is slow or using too many resources"
                                      │
                          ┌───────────┴───────────┐
                          │ Do you know WHICH      │
                          │ service is affected?    │
                          └───────────┬───────────┘
                             no/      │      \yes
                            ▼         │       ▼
                     ┌──────────┐     │   ┌──────────────────┐
                     │ METRICS  │     │   │ Do you know WHICH│
                     │ Start    │     │   │ request/endpoint?│
                     │ here.    │     │   └────────┬─────────┘
                     │ Find the │     │      no/   │    \yes
                     │ hot svc. │     │     ▼      │     ▼
                     └──────────┘     │  ┌──────┐  │  ┌──────────────┐
                                      │  │TRACES│  │  │ Do you know  │
                                      │  │Find  │  │  │ WHICH code   │
                                      │  │the   │  │  │ path?        │
                                      │  │path. │  │  └──────┬───────┘
                                      │  └──────┘  │    no/  │  \yes
                                      │            │   ▼     │   ▼
                                      │            │ ┌─────┐ │  Read the
                                      │            │ │PROF-│ │  code and
                                      │            │ │ILING│ │  optimize.
                                      │            │ │Find │ │
                                      │            │ │the  │ │
                                      │            │ │func.│ │
                                      │            │ └─────┘ │
                                      └────────────┘─────────┘
```

**Rule of thumb**: Metrics tell you *what* is wrong. Traces tell you *where* in the request path. Profiles tell you *which function* in the code.

---

## Hands-On Exercise: Deploy Parca and Find a CPU Hotspot

**Objective**: Deploy Parca, run a sample application with a known CPU hotspot, and use flame graphs to identify the offending function.

### Step 1: Create the Test Environment

```bash
# Create a kind cluster (if you don't have one)
kind create cluster --name profiling-lab

# Install Parca server and agent
helm repo add parca https://parca-dev.github.io/helm-charts
helm repo update

helm install parca-server parca/parca \
  --namespace parca --create-namespace

helm install parca-agent parca/parca-agent \
  --namespace parca \
  --set "config.stores[0].address=parca-server.parca.svc:7070" \
  --set "config.stores[0].insecure=true"
```

### Step 2: Deploy a Sample App with a CPU Hotspot

```bash
# Deploy a Go app that has an intentional CPU hotspot
kubectl create namespace demo

kubectl apply -n demo -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hotspot-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hotspot-app
  template:
    metadata:
      labels:
        app: hotspot-app
    spec:
      containers:
      - name: app
        image: golang:1.22
        command: ["/bin/sh", "-c"]
        args:
        - |
          cat > /tmp/main.go << 'GOEOF'
          package main

          import (
              "crypto/sha256"
              "fmt"
              "net/http"
              "strings"
          )

          func expensiveHash(data string) string {
              result := data
              for i := 0; i < 1000; i++ {
                  h := sha256.Sum256([]byte(result))
                  result = fmt.Sprintf("%x", h)
              }
              return result
          }

          func cheapHandler(w http.ResponseWriter, r *http.Request) {
              fmt.Fprintf(w, "ok")
          }

          func hotspotHandler(w http.ResponseWriter, r *http.Request) {
              data := strings.Repeat("payload", 100)
              result := expensiveHash(data)
              fmt.Fprintf(w, "hash: %s", result[:16])
          }

          func main() {
              http.HandleFunc("/cheap", cheapHandler)
              http.HandleFunc("/hotspot", hotspotHandler)
              fmt.Println("Listening on :8080")
              http.ListenAndServe(":8080", nil)
          }
          GOEOF
          cd /tmp && go run main.go
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: hotspot-app
spec:
  selector:
    app: hotspot-app
  ports:
  - port: 8080
EOF

# Wait for the app to be ready
kubectl wait --for=condition=ready pod -l app=hotspot-app -n demo --timeout=120s
```

### Step 3: Generate Load on the Hotspot Endpoint

```bash
# Generate traffic that hits both endpoints
kubectl run -n demo loadgen --rm -i --restart=Never --image=busybox -- sh -c '
  while true; do
    wget -q -O /dev/null http://hotspot-app:8080/hotspot
    wget -q -O /dev/null http://hotspot-app:8080/cheap
    sleep 0.1
  done
'
```

### Step 4: Analyze with Parca

```bash
# Port-forward the Parca UI
kubectl port-forward -n parca svc/parca-server 7070:7070
```

Open http://localhost:7070 and:

1. Select the `demo/hotspot-app` target from the label selector
2. Choose a 5-minute time window
3. Look at the flame graph -- you should see `expensiveHash` and `sha256.Sum256` dominating the CPU profile
4. Try the **diff view**: compare the profile before and during load to see the hotspot appear

### Success Criteria

- [ ] Parca server and agent are running in the cluster
- [ ] You can access the Parca web UI
- [ ] The flame graph shows `expensiveHash` as the dominant CPU consumer
- [ ] You can identify `sha256.Sum256` as the specific hot function inside it
- [ ] You understand how this information would guide an optimization (cache the hash, reduce iterations, use a faster hash)

### Cleanup

```bash
kubectl delete namespace demo
helm uninstall parca-server parca-agent -n parca
kubectl delete namespace parca
kind delete cluster --name profiling-lab
```

---

## Comparison: Parca vs Pyroscope vs Commercial

| Feature | Parca | Pyroscope (Grafana) | Datadog Continuous Profiler |
|---------|-------|--------------------|-----------------------------|
| **Collection** | eBPF (zero instrumentation) | SDK push + pull scrape | Agent + language libraries |
| **Language Support** | Any (kernel-level stacks) | Go, Java, Python, Ruby, .NET | Go, Java, Python, Ruby, .NET, PHP, Node.js |
| **Grafana Integration** | Via data source plugin | Native (first-class) | No (Datadog UI only) |
| **Storage** | Self-hosted (columnar) | Self-hosted or Grafana Cloud | Datadog Cloud |
| **Diff Views** | Yes | Yes | Yes |
| **Cost** | Free (open-source, Apache 2.0) | Free self-hosted / paid Cloud | Per-host pricing (~$12/host/mo) |
| **Overhead** | <1% CPU (eBPF) | 2-5% CPU (SDK-dependent) | 2-5% CPU |
| **Best For** | Zero-touch cluster profiling | Grafana-native teams | Existing Datadog customers |

**Choose Parca** if you want profiling across all workloads with zero code changes.
**Choose Pyroscope** if your team already uses Grafana and wants deep language-specific profiles integrated into dashboards.
**Choose Datadog** if you are already paying for Datadog and want one-click enablement.

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Profiling only during incidents | You have no baseline to compare against | Run continuously -- profiles are cheap to collect |
| Ignoring memory profiles | Focus only on CPU, miss allocation-driven GC pauses | Collect both CPU and alloc profiles by default |
| Reading flame graphs top-down | Misunderstanding the visualization | Read bottom-up: root at the bottom, leaves (hot functions) at the top |
| Deploying Parca Agent without privileges | eBPF programs fail to load | Agent needs `privileged: true` or specific capabilities (`SYS_ADMIN`, `BPF`) |
| Not using diff views after deploys | Missing performance regressions | Compare profiles from before and after every deployment |
| Sampling too aggressively | High overhead, distorted results | Default 19Hz (or 100Hz) is sufficient for most workloads |

---

## Quiz

### Question 1
What are the four pillars of observability?

<details>
<summary>Show Answer</summary>

**Metrics, Logs, Traces, and Profiles**

Metrics show aggregate system health. Logs capture discrete events. Traces follow individual requests across services. Profiles reveal which code paths consume CPU, memory, and other resources at the function level.
</details>

### Question 2
How does Parca collect profiling data without code changes?

<details>
<summary>Show Answer</summary>

**Parca uses eBPF to sample stack traces directly from the Linux kernel.**

The Parca Agent runs as a DaemonSet and attaches eBPF programs to kernel perf events. These programs capture stack traces at a configured frequency (e.g., 19 times per second) from every process on the node, regardless of programming language.
</details>

### Question 3
What is the key difference between Parca and Pyroscope in terms of data collection?

<details>
<summary>Show Answer</summary>

**Parca is eBPF-based (zero instrumentation), while Pyroscope primarily uses language SDKs and pull-mode scraping.**

Parca works at the kernel level and profiles every process automatically. Pyroscope provides deeper, language-aware profiles (goroutine counts, mutex contention, allocation types) but requires adding an SDK or exposing a pprof endpoint. Many teams use both: Parca for breadth, Pyroscope for depth.
</details>

### Question 4
In a flame graph, what does the width of a bar represent?

<details>
<summary>Show Answer</summary>

**The proportion of total samples in which that function appeared on the stack.**

A wider bar means the function (or functions it called) was on-CPU more often. The widest bars at the top of the graph are your optimization targets. Note that flame graphs are *not* timelines -- the x-axis is alphabetical or sorted by size, not chronological.
</details>

### Question 5
When should you reach for profiling instead of traces?

<details>
<summary>Show Answer</summary>

**When you know which service is slow but not which function or code path is responsible.**

Traces tell you that Service A spent 200ms in the `/checkout` handler. Profiling tells you that 140ms of that was in `json.Marshal` calling `reflect.ValueOf`. Profiling picks up where tracing leaves off -- it gives you the code-level *why*.
</details>

---

## Key Takeaways

1. **Profiles are the 4th pillar** -- they answer "which code" when metrics, logs, and traces cannot
2. **Always-on profiling** gives you baselines to compare against during incidents
3. **Parca** profiles everything via eBPF with zero instrumentation and negligible overhead
4. **Pyroscope** gives language-aware depth and integrates natively with Grafana
5. **Flame graphs** are the primary visualization -- read them bottom-up, optimize the widest bars
6. **Diff views** after deployments catch performance regressions before users notice
7. **CPU and memory allocation** are the two profiles you should always collect
8. **Profiling complements tracing** -- use traces to find the slow service, profiles to find the slow function

---

## Further Reading

- [Parca Documentation](https://www.parca.dev/docs/overview) - Official Parca guides
- [Pyroscope Documentation](https://grafana.com/docs/pyroscope/latest/) - Grafana Pyroscope docs
- [Brendan Gregg's Flame Graphs](https://www.brendangregg.com/flamegraphs.html) - The original flame graph inventor's guide
- [Google-Wide Profiling Paper](https://research.google/pubs/pub36575/) - The research that started it all
- [eBPF for Profiling](https://ebpf.io/applications/#profiling) - How eBPF enables low-overhead profiling

---

## Next Module

Continue to Module 2.1 or explore related modules:
- [Module 1.6: Pixie](module-1.6-pixie/) - eBPF-based observability (same kernel technology, different focus)
- [Module 1.2: OpenTelemetry](module-1.2-opentelemetry/) - Traces and metrics that profiling complements
- [Module 1.3: Grafana](module-1.3-grafana/) - Where Pyroscope profiles are visualized
