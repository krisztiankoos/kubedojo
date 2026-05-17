---
revision_pending: false
title: "Module 4.3: Resource Requirements and Limits"
slug: k8s/ckad/part4-environment/module-4.3-resources
sidebar:
  order: 3
lab:
  id: ckad-4.3-resources
  url: https://killercoda.com/kubedojo/scenario/ckad-4.3-resources
  duration: "30 min"
  difficulty: intermediate
  environment: kubernetes
---
> **Complexity**: `[MEDIUM]` - Critical for production, affects scheduling
>
> **Time to Complete**: 35-45 minutes
>
> **Prerequisites**: Module 1.1 (Pods), understanding of CPU and memory concepts

---

## Learning Outcomes

These outcomes focus on decisions you can defend under CKAD pressure and in a real cluster. By the end, you should be able to read a resource specification, predict the scheduler and kubelet behavior it creates, and choose the next diagnostic command without guessing from symptoms alone.

- **Implement** CPU and memory requests and limits in Pod, Deployment, LimitRange, and ResourceQuota specifications.
- **Diagnose** Pending pods, OOMKilled restarts, and CPU throttling by correlating resource settings with Kubernetes status and events.
- **Design** resource allocations that balance application performance, node capacity, QoS class, and namespace policy.
- **Compare** requests, limits, LimitRanges, and ResourceQuotas so you can predict whether a workload is rejected, scheduled, slowed, killed, or evicted.

## Why This Module Matters

Hypothetical scenario: a release rolls out during a busy afternoon, and two different failures appear at the same time. One new pod stays Pending with an `Insufficient cpu` event, while another pod starts successfully and then restarts with `Reason: OOMKilled`. Both failures mention resources, but they happen at different phases of the Kubernetes control loop, so treating them as the same problem wastes time and can push the cluster further out of balance.

Resource requests and limits are the contract between your workload, the scheduler, and the node runtime. A request tells the scheduler how much capacity must be reserved before a pod can land on a node. A limit tells the kubelet and container runtime how much CPU or memory a running container may consume. The two fields sit next to each other in YAML, but they answer different operational questions: "Can this pod fit here?" and "What happens after it starts?"

The apartment lease analogy still works if you use it carefully. A request is like a guaranteed parking spot that the building manager reserves before you move in, while a limit is like a maximum occupancy rule enforced after you are already inside. For memory, crossing the occupancy rule can evict the process because memory is not safely compressible. For CPU, crossing the rule normally slows the container because CPU time can be divided into smaller slices.

The CKAD exam often tests this topic through small manifests and short failure descriptions rather than long theory questions. You may need to add resources to a pod quickly, explain why a namespace policy injected defaults, or find why a pod cannot schedule even though a node still shows idle CPU at the operating system level. Everything in this module assumes Kubernetes 1.35 or later, and the mechanics covered here are stable across the resource API objects you use in day-to-day cluster work.

## Requests, Limits, and the Scheduler's Promise

Requests and limits are easiest to learn when you separate the control plane decision from the node decision. The scheduler evaluates requests before the pod runs, using node allocatable capacity and the sum of already admitted pod requests. The kubelet and runtime enforce limits after the pod is running, using operating system controls for CPU and memory. That separation is why a pod can fail to schedule before it has used any resource at all, and why a scheduled pod can later be killed for exceeding memory.

| Term | Meaning | When Enforced |
|------|---------|---------------|
| **Request** | Guaranteed minimum resources | Scheduling time |
| **Limit** | Maximum allowed resources | Runtime |

Think of a request as a reservation in the scheduler's ledger. If a pod requests `500m` CPU and `256Mi` memory, the scheduler looks for a node with at least that much unreserved allocatable capacity. It does not run your process, measure actual usage, or predict future spikes. It only decides whether the declared reservation can fit alongside the reservations that are already present on the node.

Think of a limit as a runtime boundary. A memory limit is a hard boundary because the container cannot keep allocating memory beyond it without being terminated. A CPU limit is usually a pacing boundary because the runtime can throttle the container and let it continue later. That difference matters during incident response: memory pressure produces restarts and state loss, while CPU throttling usually produces latency, slower batch work, and confusingly low throughput.

```text
┌─────────────────────────────────────────────────────────────┐
│                 Resource Request vs Limit                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Memory:                                                    │
│  ├── Request: 256Mi (guaranteed, used for scheduling)      │
│  ├── Actual usage can vary between 0 and Limit             │
│  └── Limit: 512Mi (hard cap, exceeding = OOMKill)          │
│                                                             │
│  CPU:                                                       │
│  ├── Request: 100m (guaranteed, used for scheduling)       │
│  ├── Can burst above request if node has spare capacity    │
│  └── Limit: 500m (throttled if exceeded, NOT killed)       │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │                                                    │    │
│  │  0        Request      Actual       Limit          │    │
│  │  |           |           |            |            │    │
│  │  ├───────────┼───────────┼────────────┤            │    │
│  │  │ guaranteed│  burstable │  max      │            │    │
│  │  └───────────┴───────────┴────────────┘            │    │
│  │                                                    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

The scheduler uses requests rather than limits because scheduling needs a stable reservation model. If the scheduler used limits, clusters with conservative safety caps would appear full even when most applications normally use far less. If the scheduler used live usage, placement would become unstable because a quiet application could suddenly spike after a new pod arrived. Requests are the middle ground: they represent the amount you are willing to reserve even when the container is not currently using it.

This model also explains why over-requesting is expensive even when your applications are quiet. A cluster can have idle CPU at the node level while the scheduler refuses new pods because the request ledger is full. The node may look underused in a monitoring graph, but the scheduler is honoring the promises already made to running pods. In CKAD tasks, the fastest way to confirm this is to inspect pod events and then inspect the node's allocated resources section.

Pause and predict: a pod requests `100m` CPU and has a CPU limit of `500m`. If the node has spare CPU, the pod can use up to its limit; if neighboring pods also need CPU, the runtime shares time according to each container's cgroup settings and throttles those that hit quota. The request got the pod scheduled, but it did not permanently cap runtime consumption.

Memory behaves less forgivingly because the kernel cannot safely slow memory allocation in the same way it can slow CPU execution. Once a container exceeds its memory limit, the process is a candidate for termination and Kubernetes reports the last state as `OOMKilled`. If several pods on a node use more memory than their requests at the same time, kubelet eviction can also happen before individual container limits are crossed. The exact symptom depends on whether the pressure is local to a container limit or shared across the node.

## Writing Resource Specs That Kubernetes Can Admit

The resource stanza belongs under each container, not directly under the pod spec. This detail is common in exam mistakes because the pod has one scheduling result, but the resources are declared per container and then summed for scheduling. A pod with two containers that each request `100m` CPU has a pod-level scheduling request of `200m` CPU. Init containers are handled differently for scheduling, but for CKAD resource basics, the key habit is to put the stanza at the container level every time.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:
        memory: "256Mi"
        cpu: "100m"
      limits:
        memory: "512Mi"
        cpu: "500m"
```

This manifest says the container needs a reserved tenth of a CPU core and `256Mi` of memory to be scheduled. It may burst up to half a CPU core when runtime capacity allows, and it may allocate memory up to `512Mi` before the limit becomes fatal. The values are strings here because quoting resource quantities avoids YAML surprises and keeps the visual distinction clear. Kubernetes accepts unquoted resource quantities too, but quoted values are a reliable habit in examples and generated manifests.

CPU is measured in cores, and the `m` suffix means millicores. One full core is `1` or `1000m`, so `250m` means one quarter of a core. CPU requests and limits can be fractional because CPU time can be scheduled in slices. For human review, millicores are usually easier for small services because `100m` is more readable than `0.1`.

| Value | Meaning |
|-------|---------|
| `1` | 1 CPU core |
| `1000m` | 1000 millicores = 1 core |
| `500m` | 0.5 cores |
| `100m` | 0.1 cores (10%) |

Memory quantities can use binary suffixes such as `Mi` and `Gi`, or decimal suffixes such as `M` and `G`. Kubernetes accepts both, but they are not identical because binary units are based on powers of 1024 and decimal units are based on powers of 1000. Most Kubernetes examples use `Mi` and `Gi`, and that is the safer convention when you want the value to match how operators discuss memory on nodes. In a small limit, the difference between `128M` and `128Mi` is not huge, but consistent units reduce review errors.

| Value | Meaning |
|-------|---------|
| `128Mi` | 128 mebibytes (1024-based) |
| `1Gi` | 1 gibibyte = 1024 Mi |
| `128M` | 128 megabytes (1000-based) |
| `1G` | 1 gigabyte = 1000 M |

Before running this, what output do you expect from the JSONPath query: a request map, a limit map, both maps, or nothing? This small prediction step matters because Kubernetes may mutate a pod at admission time if a LimitRange supplies defaults. When the object you inspect differs from the YAML you wrote, admission policy is one of the first places to look.

When you generate manifests in an exam or local lab, keep the resource stanza close to the container it controls. For a Deployment, the resource stanza sits under `spec.template.spec.containers[]`, not under the Deployment's top-level `spec`. That placement can feel nested, but it mirrors the object model: a Deployment creates ReplicaSets, ReplicaSets create Pods, and the pod template carries the container settings used by each replica.

Resource values should come from evidence when you have it and from conservative defaults when you do not. For a known service, use observed steady-state and peak usage, then set requests near the capacity you want reserved during normal operation. For a new service in a learning cluster, choose modest requests and limits that let the pod run without hiding obvious memory leaks. The important habit is to make the value intentional rather than leaving production pods in BestEffort by accident.

## Multi-Container Resource Math

Most beginner examples show one container per pod, but Kubernetes sums resource requirements across the containers that run together. A sidecar for logging, a proxy, or a local helper process consumes real node capacity even when the main application is the only thing users notice. The scheduler places the pod as one unit, so it needs enough allocatable capacity for the combined request. If you forget the helper container, the pod may run correctly in a quiet lab but fail placement or cause pressure when replicas increase.

The arithmetic is simple for regular app containers. If a pod has an `app` container requesting `200m` CPU and a `sidecar` requesting `50m`, the pod asks the scheduler to reserve `250m` CPU. Memory requests add the same way, and limits describe the runtime ceilings for each container separately. This is why a small sidecar should still have resources: it may be small, but multiplying it across many replicas turns a forgotten request into a capacity planning error.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-container-demo
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:
        cpu: "200m"
        memory: "256Mi"
      limits:
        cpu: "500m"
        memory: "512Mi"
  - name: sidecar
    image: busybox
    command: ["sh", "-c", "sleep 3600"]
    resources:
      requests:
        cpu: "50m"
        memory: "64Mi"
      limits:
        cpu: "100m"
        memory: "128Mi"
```

For this pod, the steady scheduling reservation is `250m` CPU and `320Mi` memory. The app container and sidecar can each be limited independently, so the app can be OOMKilled without the sidecar exceeding its own memory limit, and the sidecar can be throttled without changing the app container's CPU limit. Pod status can summarize the outcome, but container status gives the precise reason for each container. During troubleshooting, always inspect the container name attached to a restart or last state.

Init containers add one more wrinkle because they run before regular app containers rather than alongside them. For each resource type, Kubernetes considers the larger of the init-container requirement and the sum of the regular app-container requirements for scheduling. That means a heavy migration init container can make a pod require more memory to schedule even if the long-running app is small. The pod may look oversized from steady-state usage, but the scheduler must reserve enough capacity for the largest startup phase.

This distinction matters when a workload has a database migration, certificate generation step, or cache warmup before the main process starts. If the init container requests `1Gi` memory and the app containers together request `320Mi`, the pod needs the larger startup reservation for memory placement. Lowering the app container request will not help the pod schedule if the init container remains the largest request. You must inspect the whole pod spec, not only the container that stays running.

Which number would you use for a capacity estimate: the main container request, the sum of regular containers, or the init-container maximum? The defensible answer depends on the resource and phase, but the scheduler's placement model is the source of truth. Sum the regular containers, compare that sum with the largest init-container request for each resource, then use the larger value for scheduling. This habit prevents sidecars and startup work from disappearing in your mental math.

Extended resources and huge pages follow the same general theme: declare what must be reserved before the pod runs, and expect Kubernetes to schedule from that declaration rather than live usage. CKAD resource questions usually stay with CPU and memory, but the underlying lesson transfers. Kubernetes cannot protect shared capacity with guesses hidden inside an application. The pod spec has to state the reservation clearly enough for admission, scheduling, and node enforcement to do their jobs.

## Runtime Enforcement: OOMKills, Throttling, and QoS

Runtime symptoms become much clearer when you remember that CPU and memory have different failure modes. CPU is compressible because the runtime can give a container fewer time slices and let it continue. Memory is not compressible in the same practical sense because an allocation either succeeds or it does not. Kubernetes reflects that difference in pod status, container last state, and node events.

```text
Container uses > limit → OOMKilled → Container restarts
```

An OOMKilled container exceeded its memory boundary, or it was selected during memory pressure in a way that terminated the process. The `Last State` field is especially useful because a restarted container may currently look healthy while its previous termination reason tells the real story. In CKAD troubleshooting, you usually do not need a full observability stack to identify this symptom. The pod status, restart count, and event history are enough to prove that memory enforcement is involved.

```bash
# Check if a pod was OOMKilled
kubectl describe pod my-pod | grep -A5 "Last State"
kubectl get pod my-pod -o jsonpath='{.status.containerStatuses[0].lastState}'
```

If the limit is too low, raising it may be correct, but it should not be the only thought. A memory limit protects the node from a runaway process, so increasing it without evidence can move the failure from one container to the whole node. First compare the limit with real usage, application runtime overhead, startup spikes, and cache behavior. Then decide whether the application needs more memory, a lower cache ceiling, fewer concurrent workers, or a different request-to-limit ratio.

```text
Container uses > limit → Throttled (slowed down, NOT killed)
```

CPU throttling is quieter than an OOMKill because the container usually remains Running. The application may report slow responses, delayed readiness, missed timeouts, or low throughput, while Kubernetes still shows the pod as healthy. `kubectl top` can reveal current usage when Metrics Server is installed, but throttling itself is often better confirmed through runtime or application metrics. On the exam, the main distinction is that CPU limits slow work, while memory limits can terminate work.

Pause and predict: a pod has `requests.cpu: 100m` and `limits.cpu: 500m`, and the node has one full CPU core available. The pod can consume up to `500m` while capacity is available, but it is not guaranteed that amount during contention. If several pods burst at once, their requests and runtime controls influence how CPU time is shared. This is why a service can be scheduled successfully and still perform poorly if its CPU limit is too tight.

Kubernetes assigns a Quality of Service class to each pod from its resource settings. QoS does not replace requests, limits, or quotas; it influences eviction order when the node is under pressure. Guaranteed pods receive the strongest eviction protection because every container has equal CPU and memory requests and limits. BestEffort pods receive the weakest protection because they have no declared reservation, so any usage is above their request of zero.

| QoS Class | Condition | Eviction Likelihood |
|-----------|-----------|---------------------|
| **Guaranteed** | Requests = Limits for all containers | Lowest (protected) |
| **Burstable** | Requests < Limits (or only one set) | Medium |
| **BestEffort** | No requests or limits set | Highest |

A Guaranteed pod is useful when predictability matters more than burst flexibility. The request equals the limit for every resource on every container, so Kubernetes knows the pod's reserved amount and maximum amount are the same. This can be appropriate for tightly sized infrastructure components or workloads that must be protected during memory pressure. The tradeoff is that the scheduler reserves the full amount up front, which can reduce packing efficiency.

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"    # Same as request
    cpu: "100m"        # Same as request
```

Burstable pods are common for application workloads because they reserve a realistic baseline while allowing controlled headroom. A web service might request enough CPU and memory for normal traffic, then allow extra CPU or memory for short spikes. This is efficient when the cluster has many services whose peaks do not happen at the same time. It becomes risky when limits are set so high that simultaneous bursts can pressure the node.

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"    # Higher than request
    cpu: "500m"        # Higher than request
```

BestEffort pods are acceptable for disposable experiments, but they are a poor default for production. They can run when spare capacity exists, yet they have no reservation and are first in line when kubelet needs to reclaim resources. A BestEffort pod can also make capacity planning misleading because it consumes real CPU and memory without appearing in the scheduler's request ledger. For CKAD work, assume that important pods should have at least requests.

```yaml
resources: {}  # No resources defined
```

Stop and think: a pod has limits but no requests. Kubernetes may copy limits into requests in some cases, and namespace defaults can also mutate missing fields. That means the QoS class you expect from the manifest may differ from the object stored after admission. Inspect the created pod when the behavior matters, because admission-time defaults are part of the cluster's contract.

## Scheduling, Namespace Policy, and Capacity Signals

Scheduling failures are often easier to solve than runtime failures because the scheduler leaves direct evidence in events. A Pending pod with `Insufficient cpu` or `Insufficient memory` has not failed inside the container; it has failed the placement test. The test compares pod requests against node allocatable capacity that is not already reserved by other pods. That is why lowering a limit alone does not make a Pending pod schedule if the request is still too large.

```bash
# Check why a pod is Pending
kubectl describe pod my-pod

# Events may show:
# 0/3 nodes are available: 3 Insufficient cpu.
# or
# 0/3 nodes are available: 3 Insufficient memory.
```

Node capacity has several layers, and the distinction matters during troubleshooting. Capacity is the raw amount reported by the node, while allocatable is what Kubernetes considers available for pods after reserving resources for the system and kubelet. Allocated resources are the sum of pod requests and limits already admitted to the node. The scheduler primarily cares about allocatable minus requested resources, not current operating system idleness.

```bash
# Node capacity and allocatable
kubectl describe node NODE_NAME | grep -A5 Capacity
kubectl describe node NODE_NAME | grep -A5 Allocatable

# Already allocated
kubectl describe node NODE_NAME | grep -A10 "Allocated resources"
```

Exercise scenario: a pod requests two CPU cores, each node has four cores, and every node still shows idle CPU in a dashboard. The pod can still remain Pending if existing pods have already reserved the schedulable CPU through requests. In that situation, increasing the pod's limit does nothing, and lowering the pod's request only helps if the lower value remains honest for the workload. The durable fixes are right-sizing requests, moving or scaling other workloads, or adding capacity.

LimitRange is an admission policy object for a namespace. It can set default requests and limits for containers that omit them, and it can reject containers that fall outside configured minimum or maximum values. This is useful when a namespace hosts many small workloads and you want every pod to enter the scheduler with a baseline resource contract. It is not a replacement for application-specific sizing because defaults are only safe guesses.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: cpu-memory-limits
spec:
  limits:
  - default:          # Default limits if not specified
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:   # Default requests if not specified
      cpu: "100m"
      memory: "256Mi"
    max:              # Maximum allowed
      cpu: "2"
      memory: "2Gi"
    min:              # Minimum allowed
      cpu: "50m"
      memory: "64Mi"
    type: Container
```

```bash
# View LimitRange objects in the current namespace
kubectl get limitrange
kubectl describe limitrange cpu-memory-limits
```

A LimitRange changes admission behavior before scheduling starts. If a pod omits resources and the namespace has defaults, the API server can store a pod spec that includes values the author did not write. If a pod asks for less than the minimum or more than the maximum, admission rejects it before the scheduler sees it. This distinction gives you a clean troubleshooting order: admission errors appear when creating the object, scheduling errors appear after the object exists and remains Pending.

ResourceQuota is also namespace-scoped, but it controls the total budget consumed by objects in that namespace. A quota can cap total requested CPU, requested memory, CPU limits, memory limits, pod count, and many other resources. When a quota tracks compute resources, pods usually need resource fields so the API server can calculate whether the new object would exceed the namespace budget. LimitRange defaults and ResourceQuota often work together because defaults give the quota something to count.

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
spec:
  hard:
    requests.cpu: "4"
    requests.memory: "8Gi"
    limits.cpu: "8"
    limits.memory: "16Gi"
    pods: "10"
```

```bash
# View quota usage in the current namespace
kubectl get resourcequota
kubectl describe resourcequota compute-quota
```

Quota failures are admission failures, not scheduler failures. If a namespace has already used most of its `requests.memory` budget, a new pod can be rejected even when nodes have plenty of free memory. That protects the namespace boundary and keeps one team or exercise from consuming more than its assigned share. The fix is to reduce the new pod's request, delete or resize other namespace workloads, or raise the quota through the normal administrative path.

The quick reference below keeps the common inspection commands in one place. Use them after you know which phase you are debugging: object admission, scheduler placement, or runtime enforcement. A command that shows node allocation will not explain a rejected ResourceQuota, and a quota command will not explain an OOMKilled container. Matching the command to the phase is the skill this module is trying to build.

```bash
# Check pod resources
kubectl get pod POD -o jsonpath='{.spec.containers[*].resources}'

# Check node capacity and allocation
kubectl describe node NODE | grep -A10 "Allocated"

# Check QoS class
kubectl get pod POD -o jsonpath='{.status.qosClass}'

# Check current usage when Metrics Server is available
kubectl top pod POD
```

## Worked Example: Tuning a Small Web Pod

Start with a small web Deployment that has a realistic baseline and a modest burst allowance. The Deployment uses two replicas so the scheduler must place two pod reservations, not just one. Each replica requests `50m` CPU and `64Mi` memory, so the total requested footprint is `100m` CPU and `128Mi` memory across the Deployment. Each replica can burst to `100m` CPU and `128Mi` memory before the limit applies.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resource-web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: resource-web
  template:
    metadata:
      labels:
        app: resource-web
    spec:
      containers:
      - name: nginx
        image: nginx
        resources:
          requests:
            cpu: "50m"
            memory: "64Mi"
          limits:
            cpu: "100m"
            memory: "128Mi"
```

This example is intentionally small because it teaches the arithmetic without requiring a large cluster. If you apply it to a single-node learning environment, the request footprint should be easy to fit. If the pod remains Pending, the resource request is only one possible cause; node selectors, taints, image pull issues, and namespace policy can also block progress. The first diagnostic command should still be `kubectl describe pod` because it reports scheduler events and admission-related clues close to the object.

```bash
kubectl apply -f resource-web.yaml
kubectl get deploy resource-web
kubectl get pods -l app=resource-web
kubectl get pod -l app=resource-web -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.status.qosClass}{"\n"}{end}'
```

Suppose both pods run and report Burstable QoS. That result follows directly from the manifest because requests are lower than limits for both CPU and memory. If you change each limit to equal its matching request, the pods become Guaranteed, but they also lose burst headroom. If you remove the resource stanza entirely, they become BestEffort unless a LimitRange injects defaults.

Now suppose the Deployment needs to handle short traffic bursts without frequent CPU throttling. Raising the CPU limit from `100m` to `250m` may help latency if the node has spare capacity, but it does not change scheduling because the CPU request remains `50m` per replica. Raising the CPU request changes scheduling and reservation, which can improve fairness during contention but may reduce how many pods fit. The right edit depends on whether the problem is runtime burst capacity or scheduler reservation.

Memory tuning has a different risk profile. Raising the memory limit can reduce OOMKilled restarts when the application genuinely needs more memory, but it also increases the maximum memory the node may need to absorb during bursts. Raising the memory request reserves more schedulable capacity and improves eviction standing because kubelet compares usage against requests during pressure. For stateful or cache-heavy processes, the request should usually reflect a real operating baseline rather than the smallest value that lets the pod start.

Which approach would you choose here and why: raise only the limit, raise only the request, raise both, or investigate the application first? A defensible answer names the symptom. Pending pods point toward requests and capacity, OOMKilled restarts point toward memory limit or application behavior, and slow-but-running pods point toward CPU throttling, insufficient CPU request under contention, or application-level bottlenecks.

The final check is to inspect the stored object, not only the file you edited. Admission can add defaults, controllers can template pods from a Deployment, and humans can apply a different file than the one under review. `kubectl get` with JSONPath is concise, while `kubectl describe` is better when you need events and node allocation context. In exam conditions, use the shortest command that proves the specific claim you need to make.

## Patterns & Anti-Patterns

Resource management has a few repeatable patterns that scale beyond a single manifest. They are not moral rules; they are ways to make scheduler placement, runtime behavior, and namespace governance predictable. A good pattern names when it applies and what tradeoff it accepts. A bad pattern usually starts from a reasonable shortcut and becomes harmful when traffic, replicas, or neighboring workloads change.

| Pattern | When to Use | Why It Works | Scaling Consideration |
|---------|-------------|--------------|-----------------------|
| Baseline request with measured burst limit | Stateless services with variable traffic | Scheduler reserves normal demand while runtime allows short spikes | Revisit after load tests and production measurements |
| Guaranteed resources for critical fixed-size pods | Infrastructure or latency-sensitive components with stable usage | QoS protection is strongest and runtime envelope is explicit | Packing efficiency drops because burst sharing is reduced |
| Namespace defaults plus quota | Shared training, team, or tenant namespaces | Every pod has countable resources and the namespace has a budget | Defaults must be reviewed so tiny labs do not inherit oversized reservations |
| Separate diagnosis by phase | Any Pending, rejected, slow, or restarting pod | Admission, scheduling, and runtime failures leave different evidence | Run the phase-specific command before changing YAML |

The strongest pattern for CKAD is phase-based troubleshooting. If creation fails, inspect admission policy such as LimitRange and ResourceQuota. If the object exists but stays Pending, inspect scheduler events and node allocated resources. If the pod runs and then restarts or slows down, inspect container state, limits, and live usage where available. This order keeps you from changing a limit when the request is the actual blocker.

| Anti-pattern | What Goes Wrong | Better Alternative |
|--------------|-----------------|--------------------|
| No resources on production pods | Pods become BestEffort unless defaults apply and capacity planning becomes misleading | Set at least CPU and memory requests for important workloads |
| Requests copied from limits without thought | The scheduler reserves peak capacity and the cluster appears full early | Set requests from normal demand and limits from safe burst or protection boundaries |
| Tiny memory limits for runtime-heavy apps | Containers restart during startup, garbage collection, or cache warmup | Measure process memory, include runtime overhead, and add deliberate headroom |
| Giant CPU limits as a performance fix | Throttling may move around and noisy workloads can affect neighbors | Measure throttling, tune requests, and scale replicas or code paths when needed |

Teams fall into these anti-patterns because resource YAML looks simple. The hard part is not syntax; it is deciding which number represents a reservation, which number represents a safety boundary, and which symptom proves the current number is wrong. For CKAD, you need to be fast with syntax, but the exam still rewards the same mental model used in production. Describe the pod, identify the phase, then edit the field that affects that phase.

One more practical pattern is to make resource changes observable. A pull request that changes requests or limits should explain the symptom it addresses, the expected scheduling impact, and the expected runtime impact. In a lab, you can write that reasoning in a note beside the command. In a real repository, it belongs in review context so future maintainers know whether a value was measured, inherited, or chosen as a safe starting point.

## Decision Framework

Use this framework when a resource problem appears and you need to choose the next move quickly. The goal is not to memorize every possible Kubernetes event. The goal is to classify the failure phase, then choose the object and field that can actually influence that phase. A Pending pod is not fixed by a larger memory limit unless the request also changes, and an OOMKilled pod is not fixed by a smaller CPU request unless the real issue is elsewhere.

```text
Resource symptom appears
        |
        v
Was the object rejected by the API server?
        |-- yes --> Check LimitRange and ResourceQuota admission rules
        |
        no
        v
Does the pod exist but stay Pending?
        |-- yes --> Check requests, node allocatable capacity, and scheduler events
        |
        no
        v
Does the container restart with OOMKilled?
        |-- yes --> Check memory limit, memory usage, runtime overhead, and leaks
        |
        no
        v
Is the pod Running but slow under load?
        |-- yes --> Check CPU limits, CPU requests under contention, and app metrics
        |
        no
        v
Inspect QoS, eviction events, and neighboring workload pressure
```

The framework also helps you decide between changing a request and changing a limit. A request change affects scheduling and reservation. A limit change affects runtime enforcement and the maximum burst or memory boundary. Changing both is appropriate when the workload's true baseline and safe maximum have both changed. Changing neither is appropriate when the symptom points to a selector, image, probe, or application bug instead.

| Symptom | First Evidence to Check | Field or Object Most Likely Involved | Why |
|---------|-------------------------|--------------------------------------|-----|
| Pod rejected at creation | API error from `kubectl apply` | LimitRange or ResourceQuota | Admission policy runs before scheduling |
| Pod remains Pending | `kubectl describe pod` events | CPU or memory requests | Scheduler fits requests against allocatable capacity |
| Container restarts as OOMKilled | Container last state | Memory limit or application memory behavior | Runtime enforces memory as a hard cap |
| Pod is Running but slow | Usage, latency, throttling metrics | CPU limit, CPU request, or replica count | CPU pressure slows work rather than killing it |
| Pod evicted during pressure | Pod status and node events | QoS class and usage above requests | Kubelet eviction considers requests and pod priority signals |

When you size a new application, start by asking what failure you are trying to prevent. A memory limit prevents one container from consuming unbounded memory, but it can create restarts if set below real peaks. A CPU limit protects neighbors from unbounded CPU use, but it can create latency if set below demand. A request prevents the scheduler from overcommitting declared baseline capacity, but it can strand usable node resources if set above realistic need.

For a small stateless web service, a common first pass is a modest CPU request, a higher CPU limit, a memory request near normal usage, and a memory limit that includes startup and peak headroom. For a batch job, you may choose a larger request so the job gets enough CPU during contention and finishes predictably. For a critical control component, you may set requests equal to limits to get Guaranteed QoS. The design choice follows the workload's tolerance for latency, restart, eviction, and inefficient packing.

For namespace policy, decide whether you need defaults, ceilings, or budgets. LimitRange supplies defaults and per-container minimum or maximum values. ResourceQuota supplies namespace-wide totals and object count budgets. Defaults without quotas can still allow too many pods to consume the cluster, while quotas without defaults can reject pods that omit requests. Using both gives you a namespace that admits ordinary pods consistently while still enforcing a total budget.

The final decision rule is to avoid changing resource values blindly during an incident. If the pod is Pending, prove the requested resource is the constraint. If the container is OOMKilled, prove whether the limit is below observed peak or the application is allocating unexpectedly. If the service is slow, prove whether CPU throttling is happening before raising limits. Fast diagnosis is not the same as random YAML editing; it is a short path from symptom to mechanism.

## Did You Know?

- **CPU is compressible, memory is not.** If you exceed CPU limits, you're throttled. If you exceed memory limits, you're killed.
- **Requests affect scheduling, limits affect runtime.** A pod with 1Gi memory request won't schedule on a node with only 512Mi available, even if the container only uses 100Mi.
- **Kubernetes doesn't prevent memory overcommit.** If all pods burst to their limits simultaneously, the node can run out of memory and start evicting or killing workloads.
- **The `cpu: 0.1` syntax** is equivalent to `cpu: 100m` because Kubernetes expresses fractional CPU in millicores, where `1000m` equals one core.

## Common Mistakes

Most resource mistakes come from confusing a field's syntax with its operational meaning. The table below keeps the failure, cause, and repair in the same row so you can map each mistake to the phase where it appears. When you practice, say the phase out loud before choosing the fix; that habit prevents a surprising number of wrong edits.

| Mistake | Why It Happens | How to Fix It |
|---------|----------------|---------------|
| No resources set | BestEffort pods are easy to create and may work in empty clusters | Set at least CPU and memory requests for important pods |
| Request greater than limit | The author treats both fields as independent notes instead of an ordered envelope | Keep each request less than or equal to its matching limit |
| Memory limit too low | Runtime overhead, startup spikes, or cache growth were not included | Profile the app, inspect OOMKilled state, and raise the limit only with evidence |
| CPU limit too low | The pod remains Running, so throttling looks like an application slowdown | Check usage and throttling signals, then tune limits, requests, or replicas |
| Request same as node capacity | The pod leaves no allocatable room for system reservations or other pods | Leave node headroom and size requests against allocatable capacity |
| Quota without default requests | Pods that omit resources cannot be counted against compute quota cleanly | Pair ResourceQuota with LimitRange defaults in shared namespaces |
| Editing a Deployment but inspecting an old Pod | Controllers create replacement pods, and old pods keep old specs until recreated | Roll out the updated template and inspect the new pod's stored resources |

## Quiz

Use these scenarios to test whether you can identify the phase before naming the fix. Each answer explains the reasoning because resource troubleshooting is mostly about connecting a symptom to the Kubernetes component that produced it. If you can do that consistently, the YAML edits become straightforward.

<details>
<summary>Question 1: A pod keeps restarting, and `kubectl describe` shows `Last State: Terminated, Reason: OOMKilled`. The container has `limits.memory: 128Mi`, and the developer says the app usually uses about 80MB. What do you check before changing the manifest?</summary>

Check the container's actual memory usage, startup behavior, runtime overhead, and any caches or temporary allocations that are not included in the developer's estimate. The OOMKilled reason points to runtime memory enforcement, so the memory limit is directly relevant, but raising it blindly can move pressure to the node. Compare observed peaks with the limit, then decide whether to raise the limit, reduce application memory use, or change concurrency. The key is that requests affect scheduling, while this symptom comes from a runtime memory boundary.
</details>

<details>
<summary>Question 2: A pod stays Pending with `0/3 nodes are available: 3 Insufficient cpu`. The pod requests two CPU cores, and each node has four cores but already runs several workloads. What are your practical options?</summary>

The scheduler cannot find a node with two unreserved allocatable CPU cores, so you need to change the request or the available capacity. You can reduce the request if evidence shows the workload does not need two reserved cores, move or scale down other workloads, or add node capacity. Changing only the CPU limit will not fix this Pending state because the scheduler fits requests. Inspect `kubectl describe node` allocated resources to see how much CPU is already reserved.
</details>

<details>
<summary>Question 3: A Deployment has five replicas with no resource requests or limits. During node memory pressure, these pods are evicted before neighboring services. Why did Kubernetes treat them as easier eviction candidates?</summary>

Pods with no requests and no limits are BestEffort unless namespace defaults changed the stored spec. BestEffort pods have no declared reservation, so any memory usage is above their request of zero. During pressure, kubelet eviction logic gives weaker protection to pods that exceed requests, especially those with no reservation. The fix is to set realistic requests, and for critical workloads consider whether Guaranteed or carefully sized Burstable QoS is appropriate.
</details>

<details>
<summary>Question 4: A namespace has a LimitRange with default CPU and memory values. A developer creates a pod without resources, then sees requests and limits on the stored pod. What happened, and why can this help with ResourceQuota?</summary>

The LimitRange admission plugin applied namespace defaults to the container before the object was stored. That means the manifest the developer wrote is not the entire story; the stored pod includes policy-driven resource values. This helps ResourceQuota because compute quotas need request and limit values to count resource usage consistently. The right diagnostic commands are `kubectl get pod ... -o jsonpath` for the stored resources and `kubectl describe limitrange` for the namespace defaults.
</details>

<details>
<summary>Question 5: A service is Running and never restarts, but latency rises sharply under load after a CPU limit was lowered. The pod request stayed the same. Which resource mechanism is most suspicious?</summary>

CPU throttling is the first resource mechanism to investigate because CPU limits slow a container rather than killing it. The unchanged request means scheduling reservation did not change, so the pod can still land on the same nodes. Lowering the limit reduced the maximum CPU time the container can consume during bursts, which can show up as latency or lower throughput. Confirm with CPU usage and throttling metrics if available, then decide whether to raise the limit, adjust replicas, or tune the application.
</details>

<details>
<summary>Question 6: A new pod is rejected immediately with a quota error, but the cluster has nodes with free memory. Why is the scheduler not the component to debug first?</summary>

The object was rejected during admission, so the scheduler never received a pod to place. ResourceQuota is namespace-scoped and can reject a pod when adding its requests or limits would exceed the namespace budget. Free node memory does not override a namespace quota because quotas protect allocation boundaries before scheduling. Inspect `kubectl describe resourcequota`, then reduce the pod request, remove other namespace workloads, or request a quota change.
</details>

## Hands-On Exercise

This exercise uses small pods so it can run in a local training cluster, but the observations are the same ones you use in larger environments. You will create a pod with explicit resources, trigger a memory limit failure, inspect QoS, and then practice the short commands that expose requests, limits, node allocation, and namespace defaults. If your cluster lacks Metrics Server, the `kubectl top` portions are optional and the rest of the exercise still teaches the core mechanics.

### Task 1: Create a Pod with Explicit Requests and Limits

Create a pod that requests less than it is allowed to use, then inspect the stored resources and QoS class. Before you apply it, predict the QoS class from the manifest: requests exist, limits exist, and the values are not equal. That prediction should lead you to Burstable unless a namespace policy mutates the object in an unexpected way.

<details>
<summary>Solution</summary>

```bash
cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:
        memory: "64Mi"
        cpu: "50m"
      limits:
        memory: "128Mi"
        cpu: "100m"
EOF

# Check QoS class
kubectl get pod resource-demo -o jsonpath='{.status.qosClass}'
echo

# Check resources
kubectl get pod resource-demo -o jsonpath='{.spec.containers[0].resources}'
echo
```

</details>

### Task 2: Trigger and Inspect an OOMKilled Container

Create a pod that intentionally tries to allocate more memory than its limit allows. This is not a production pattern; it is a controlled lab for connecting the memory limit to the container's last state. The image pull may take a short time, so wait for initialization before checking the failure reason.

<details>
<summary>Solution</summary>

```bash
cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: memory-hog
spec:
  containers:
  - name: app
    image: polinux/stress
    command: ["stress"]
    args: ["--vm", "1", "--vm-bytes", "200M", "--vm-hang", "1"]
    resources:
      limits:
        memory: "100Mi"
EOF

# Wait for pod initialization because image pull may take time
kubectl wait --for=condition=Initialized pod/memory-hog --timeout=60s

# Allow time for the stress test to hit the memory limit
sleep 10
kubectl get pod memory-hog

# Check the previous container state
kubectl describe pod memory-hog | grep -A3 "Last State"
```

</details>

### Task 3: Practice Fast Resource Inspection

Use short inspections to connect resource settings with pod and node state. These commands are intentionally repetitive because CKAD speed comes from knowing which field proves which claim. If a command returns an empty value, decide whether the pod has no resources, the JSONPath is wrong, or admission policy changed a different field than you expected.

<details>
<summary>Solution</summary>

```bash
cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill1
spec:
  containers:
  - name: nginx
    image: nginx
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "200m"
        memory: "256Mi"
EOF

kubectl get pod drill1 -o jsonpath='{.spec.containers[0].resources}'
echo
kubectl get pod drill1 -o jsonpath='{.status.qosClass}'
echo
kubectl delete pod drill1
```

</details>

### Task 4: Compare Guaranteed and Burstable Pods

Create a pod whose requests equal limits and compare it with the first pod from this exercise. The goal is not to claim one QoS class is always better. The goal is to see how a small YAML change changes eviction protection and scheduler reservation. Guaranteed is stronger during pressure, while Burstable often packs more efficiently.

<details>
<summary>Solution</summary>

```bash
cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill2
spec:
  containers:
  - name: nginx
    image: nginx
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "100m"
        memory: "128Mi"
EOF

kubectl get pod drill2 -o jsonpath='{.status.qosClass}'
echo
kubectl delete pod drill2
```

</details>

### Task 5: Add Resources to a Deployment Template

Create a Deployment with two replicas and verify that the resource stanza lives under the pod template container. This task mirrors the exam pattern where you generate or edit a controller object, then inspect the created pods. The important distinction is that changing the Deployment template affects new pods created from that template, not arbitrary old pods from earlier manifests.

<details>
<summary>Solution</summary>

```bash
cat << 'EOF' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: drill4
spec:
  replicas: 2
  selector:
    matchLabels:
      app: drill4
  template:
    metadata:
      labels:
        app: drill4
    spec:
      containers:
      - name: nginx
        image: nginx
        resources:
          requests:
            cpu: "50m"
            memory: "64Mi"
          limits:
            cpu: "100m"
            memory: "128Mi"
EOF

kubectl get pods -l app=drill4
kubectl get deploy drill4 -o jsonpath='{.spec.template.spec.containers[0].resources}'
echo
kubectl delete deploy drill4
```

</details>

### Task 6: Observe Namespace Defaults with LimitRange

Create a namespace with a LimitRange, then create a pod that omits resources. The stored pod should show default requests and limits even though the pod command did not include them. This task proves that admission can mutate the object before the scheduler sees it, which is the same mechanism that helps ResourceQuota count resource usage consistently.

<details>
<summary>Solution</summary>

```bash
# Create namespace with LimitRange
kubectl create namespace drill6

cat << 'EOF' | kubectl apply -n drill6 -f -
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
spec:
  limits:
  - default:
      cpu: "200m"
      memory: "256Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    type: Container
EOF

# Create pod without resources
kubectl run drill6-pod --image=nginx -n drill6

# Check defaults were applied
kubectl get pod drill6-pod -n drill6 -o jsonpath='{.spec.containers[0].resources}'
echo

# Cleanup
kubectl delete namespace drill6
```

</details>

### Cleanup

Remove any remaining pods from the earlier tasks so the namespace is ready for the next module. Cleanup is part of the exercise because resource labs can leave failed pods behind, and those pods can confuse later inspections. If a resource does not exist because you already deleted it, the `--ignore-not-found` flag keeps the cleanup idempotent.

<details>
<summary>Solution</summary>

```bash
kubectl delete pod resource-demo memory-hog drill1 drill2 --ignore-not-found
kubectl delete deploy drill4 --ignore-not-found
kubectl delete namespace drill6 --ignore-not-found
```

</details>

### Success Criteria

- [ ] You can explain why `resource-demo` is Burstable from its request and limit values.
- [ ] You can find `OOMKilled` in the previous container state for `memory-hog`.
- [ ] You can inspect a pod's stored resources with JSONPath.
- [ ] You can distinguish a pod-level QoS result from a container-level resource stanza.
- [ ] You can identify where resources belong inside a Deployment pod template.
- [ ] You can show that LimitRange defaults were applied to a pod that omitted resources.

## Sources

- [Kubernetes: Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Kubernetes: Pod Quality of Service Classes](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Kubernetes: Node-pressure Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)
- [Kubernetes: Limit Ranges](https://kubernetes.io/docs/concepts/policy/limit-range/)
- [Kubernetes: Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
- [Kubernetes API Reference: LimitRange v1](https://kubernetes.io/docs/reference/kubernetes-api/policy-resources/limit-range-v1/)
- [Kubernetes API Reference: ResourceQuota v1](https://kubernetes.io/docs/reference/kubernetes-api/policy-resources/resource-quota-v1/)
- [Kubernetes kubectl reference: describe](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_describe/)
- [Kubernetes kubectl reference: top](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_top/)
- [Kubernetes: Assign CPU Resources to Containers and Pods](https://kubernetes.io/docs/tasks/configure-pod-container/assign-cpu-resource/)
- [Kubernetes: Assign Memory Resources to Containers and Pods](https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/)
- [Kubernetes: Configure Default Memory Requests and Limits for a Namespace](https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/memory-default-namespace/)

## Next Module

[Module 4.4: SecurityContexts](../module-4.4-securitycontext/) - Next, you will configure pod and container security settings, then connect those controls to the runtime boundaries that resource settings introduced here.
