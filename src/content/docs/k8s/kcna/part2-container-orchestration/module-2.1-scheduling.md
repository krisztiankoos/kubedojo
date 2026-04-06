---
title: "Module 2.1: Scheduling"
slug: k8s/kcna/part2-container-orchestration/module-2.1-scheduling
sidebar:
  order: 2
---

> **Complexity**: `[MEDIUM]` - Orchestration concepts
>
> **Time to Complete**: 45-60 minutes
>
> **Prerequisites**: Part 1 (Kubernetes Fundamentals)

---

## What You'll Be Able to Do

After completing this exhaustive module on Kubernetes scheduling mechanics, you will be able to:

1. **Diagnose** the exact root causes of Pods remaining in a Pending state by evaluating scheduler event logs and node capacity metrics.
2. **Design** highly available workload architectures by implementing advanced Pod anti-affinity rules and topology spread constraints.
3. **Compare** and contrast the operational impacts of node affinity versus taints and tolerations when building dedicated node pools for specialized hardware.
4. **Implement** precise resource requests and limits to guarantee predictable scheduling behavior while preventing node resource exhaustion.
5. **Evaluate** custom scheduling strategies for complex microservice deployments to optimize network latency and cluster utilization.

---

## Why This Module Matters

During the 2020 holiday season, a leading global retail corporation experienced a cascading failure across their massive, multi-region Kubernetes cluster. Developers across various teams had routinely configured their Pod resource requests to be identical to their resource limits, drastically over-provisioning CPU allocations on paper to "be safe." When Black Friday traffic spiked unexpectedly, the Horizontal Pod Autoscaler reacted precisely as configured, requesting hundreds of new checkout-service Pods to handle the massive influx of shoppers. 

The kube-scheduler, which operates strictly by evaluating the requested CPU against node capacity rather than looking at real-time metrics, determined that all nodes in the cluster were at maximum capacity. Consequently, the newly created checkout-service Pods remained permanently trapped in the Pending state. Because the critical new Pods could not be scheduled to share the load, the existing running Pods were overwhelmed by the traffic spike. They began consuming memory beyond their limits and were subsequently terminated by the Out Of Memory (OOM) killer. This scheduling gridlock caused a catastrophic four-hour complete outage during peak holiday shopping hours, resulting in an estimated fifteen million dollars in lost revenue. The root cause was not a lack of physical hardware—the underlying compute nodes were operating at only twenty percent actual CPU utilization—but a fundamental misunderstanding of how the Kubernetes scheduler evaluates node capacity versus actual usage.

Scheduling is not merely an administrative background task; it is the central nervous system of your cluster's reliability and operational efficiency. Understanding exactly how the kube-scheduler filters nodes, scores availability, and enforces complex constraints like affinity and taints is the difference between a resilient, self-healing architecture and a fragile system waiting to collapse under pressure. In this comprehensive module, you will learn the exact underlying mechanics of workload placement and how to engineer your deployments to survive catastrophic node failures, ensure high availability, and maximize your infrastructure investment.

---

## The Anatomy of the Kube-Scheduler

To master Kubernetes, you must first understand that a Pod is simply a record in the etcd database until it is bound to a specific node. When you create a Deployment, the Deployment controller creates a ReplicaSet, and the ReplicaSet controller creates Pods. At the moment of creation, these Pods have an empty `spec.nodeName` field. They are floating in the ether of the control plane, waiting for a home.

The `kube-scheduler` is an independent control plane component that constantly watches the API server for newly created Pods that have no assigned node. When it detects an unscheduled Pod, it initiates a complex, multi-phase algorithmic process known as the Scheduling Cycle to determine the absolute best node for that specific workload. This process is divided into two distinct, critical phases: Filtering and Scoring.

### Phase 1: Filtering (Predicates)

The filtering phase is a ruthless process of elimination. The scheduler evaluates every single node in the cluster against a series of hard constraints, known internally as predicates. If a node fails even one of these checks, it is immediately discarded from consideration for this specific Pod. 

The scheduler asks fundamental questions during this phase. Does this node have enough unallocated CPU and memory to satisfy the Pod's minimum resource requests? Does the node have the specific hardware labels required by the Pod's nodeSelector? If the Pod requires a specific host port to be exposed, is that port currently available on the node, or is another Pod already using it? Are the persistent volumes requested by the Pod available in the same physical availability zone as the node being evaluated?

If a cluster has one hundred nodes, and only three nodes pass all the filtering predicates, the remaining ninety-seven nodes are completely ignored for the rest of the scheduling cycle. If zero nodes pass the filtering phase, the scheduling cycle aborts immediately. The Pod is left in a Pending state, and the scheduler emits an event explaining exactly which filters caused all nodes to fail.

### Phase 2: Scoring (Priorities)

Once the scheduler has a list of feasible nodes that survived the filtering phase, it must choose the single best candidate. This is where the scoring phase, governed by priority functions, comes into play. The scheduler assigns a score from 0 to 100 to every feasible node based on a weighted set of criteria.

The scoring algorithms evaluate subtle optimization metrics. The `LeastRequestedPriority` function gives higher scores to nodes that currently have the most available resources, effectively spreading workloads evenly across the cluster to prevent hot spots. The `BalancedResourceAllocation` function looks at the ratio of CPU to memory usage on the node, preferring nodes where placing the new Pod will keep the overall resource usage balanced rather than skewing heavily toward CPU or memory exhaustion. The `ImageLocalityPriority` function checks if the container images required by the Pod are already downloaded and cached on the node; if they are, the node receives a higher score because the Pod will start significantly faster without waiting for a massive image pull over the network.

After all priority functions have been calculated and weighted, the scheduler tallies the final scores. The node with the highest total score is declared the winner.

### Phase 3: The Binding Cycle

Once a winner is selected, the scheduler does not actually start the Pod. The scheduler simply creates a Binding object and submits it to the Kubernetes API server. This Binding object instructs the API server to update the Pod's `spec.nodeName` field with the name of the winning node. 

At this point, the scheduling process is complete. The `kubelet` service running on the winning node, which is constantly watching the API server for Pods assigned to its own node name, sees the new Pod assignment. The kubelet then takes over, communicating with the container runtime (like containerd) to pull the images, set up the networking namespaces, and actually start the containers on the physical hardware.

```text
+-----------------------------------------------------------------------+
|                   THE SCHEDULING ALGORITHM                            |
+-----------------------------------------------------------------------+
|                                                                       |
|  1. WATCH: kube-scheduler sees Pod with no nodeName                   |
|                                                                       |
|  2. FILTERING (Hard Constraints)                                      |
|     Node A: Fails (Insufficient Memory)                               |
|     Node B: Passes                                                    |
|     Node C: Fails (Missing required label)                            |
|     Node D: Passes                                                    |
|                                                                       |
|  3. SCORING (Soft Preferences on Feasible Nodes)                      |
|     Node B:                                                           |
|       - Image already cached: +20 points                              |
|       - High available CPU:   +50 points                              |
|       Total Score: 70                                                 |
|                                                                       |
|     Node D:                                                           |
|       - Image not cached:       0 points                              |
|       - Very high avail CPU:  +90 points                              |
|       Total Score: 90  <--- WINNER                                    |
|                                                                       |
|  4. BINDING: Scheduler tells API server to assign Pod to Node D       |
|                                                                       |
|  5. EXECUTION: Kubelet on Node D sees assignment and starts Pod       |
|                                                                       |
+-----------------------------------------------------------------------+
```

---

> **Pause and predict**: If you have a cluster with one thousand nodes, running the filtering and scoring algorithms against every single node for every single Pod could cause massive performance bottlenecks. How do you think the Kubernetes scheduler handles massive scale to ensure Pods are scheduled quickly without analyzing every single piece of hardware in the datacenter?

---

## Resource Requests and Limits: The Foundation of Placement

The most fundamental constraint in Kubernetes scheduling is hardware resources. If you do not understand how the scheduler views CPU and memory, you cannot reliably run applications in production. Kubernetes relies on two distinct concepts for resource management: Requests and Limits.

### Resource Requests: The Scheduler's Currency

A Resource Request is the absolute minimum amount of a specific resource that a container is guaranteed to have available. When you specify a CPU request of `500m` (half of a CPU core) and a memory request of `512Mi` (512 Mebibytes), you are communicating directly with the kube-scheduler's filtering phase.

The scheduler looks at the `Allocatable` capacity of a node, which is the total physical hardware minus the resources reserved for the operating system and the kubelet itself. It then sums up the Requests of all Pods currently assigned to that node. If `Node Allocatable - Sum(Existing Requests) >= New Pod Request`, the node passes the resource filter. 

Crucially, the scheduler only cares about Requests, and it only cares about the mathematical reservation on paper. It does not look at the actual, real-time CPU or memory utilization of the node. If a node has 4 cores of allocatable capacity, and runs four Pods that each requested 1 core, the scheduler considers that node to be 100 percent full. Even if all four Pods are completely idle and using zero actual CPU cycles, the scheduler will refuse to place any more Pods on that node. This is why over-requesting resources is so dangerous; it leads to massive waste of expensive cloud infrastructure.

### Resource Limits: Runtime Enforcement

While Requests are used by the scheduler to find a node, Limits are used by the kubelet and the Linux kernel to restrict the container while it is actually running. A Resource Limit is the absolute maximum amount of a resource a container is allowed to consume.

CPU and memory are handled very differently when limits are reached, because they fall into different categories of resources: compressible and incompressible.

CPU is a compressible resource. If a container attempts to use more CPU than its defined limit, the Linux Completely Fair Scheduler (CFS) will simply throttle the container's processes. The application does not crash; it simply runs slower, waiting for its next allocated time slice.

Memory is an incompressible resource. You cannot tell an application to simply "use less memory" on the fly without changing its internal behavior. If a container attempts to allocate more memory than its defined limit, the Linux kernel's Out Of Memory (OOM) killer will intervene and forcefully terminate the container process. The kubelet will then restart the container, resulting in a pod crash loop.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demonstration-pod
spec:
  containers:
  - name: heavy-processing-app
    image: custom-processor:v2
    resources:
      requests:
        memory: "1Gi"
        cpu: "500m"
      limits:
        memory: "2Gi"
        cpu: "1000m"
```

In the above configuration, the scheduler guarantees that it will only place this Pod on a node that has at least 1 Gigabyte of unreserved memory and half a core of unreserved CPU. Once running, the container can burst up to 2 Gigabytes of memory and 1 full CPU core if the node has unused physical capacity available. If it exceeds 1 full core of usage, it will be throttled. If it exceeds 2 Gigabytes of memory usage, it will be immediately killed.

---

## Directing Traffic: Node Selectors and Affinity

Relying solely on resource availability is often insufficient for complex architectures. You frequently need to ensure that specific workloads land on specific types of hardware. For example, you might have a machine learning workload that must run on a node equipped with a GPU, or a database that requires nodes with high-IOPS solid-state drives.

### The Legacy Approach: nodeSelector

The simplest method for directing Pods to specific nodes is the `nodeSelector` field. This provides a very basic, hard-constraint mechanism based on key-value label matching. 

When you apply labels to your nodes (e.g., `kubectl label nodes worker-node-1 disktype=ssd`), you can configure your Pod to demand that label. The scheduler's filtering phase will immediately reject any node that does not possess the exact label specified in the nodeSelector.

While simple, `nodeSelector` is severely limited. It only supports strict equality matching (the label must match exactly), and it only supports logical AND operations. If you specify multiple labels in a nodeSelector, the node must possess all of them. There is no way to express a preference or a logical OR operation.

### The Modern Approach: Node Affinity

To solve the limitations of nodeSelector, Kubernetes introduced Node Affinity. This provides an incredibly expressive, albeit verbose, language for workload placement. Node affinity is divided into two distinct categories: Hard requirements and Soft preferences.

**Required During Scheduling, Ignored During Execution**
This is the hard constraint, effectively a highly advanced version of nodeSelector. If the rules defined here are not met, the Pod will not be scheduled. It supports a wide array of operators, including `In`, `NotIn`, `Exists`, `DoesNotExist`, `Gt` (Greater than), and `Lt` (Less than). This allows you to say "Schedule this Pod on a node in zone A OR zone B" using the `In` operator.

**Preferred During Scheduling, Ignored During Execution**
This is the soft preference, which hooks directly into the scoring phase of the scheduler rather than the filtering phase. You can define rules and assign them a numerical weight between 1 and 100. If a node matches the rule, its final score is increased by the weight amount. The scheduler will try its absolute best to place the Pod on a node that satisfies these preferences, but if no such node exists, the Pod will simply be scheduled on a less optimal node rather than staying stuck in a Pending state.

The phrase "Ignored During Execution" is a critical architectural detail. It means that the scheduler only evaluates these rules at the exact moment the Pod is being created and scheduled. If a Pod is successfully scheduled to a node because it has the label `environment=production`, and a cluster administrator later removes that label from the node, the Pod will not be evicted. It will continue running uninterrupted.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: advanced-affinity-pod
spec:
  affinity:
    nodeAffinity:
      # HARD CONSTRAINT: Must be in us-east-1a or us-east-1b
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: topology.kubernetes.io/zone
            operator: In
            values:
            - us-east-1a
            - us-east-1b
      # SOFT PREFERENCE: Strongly prefer nodes with dedicated SSDs
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 80
        preference:
          matchExpressions:
          - key: hardware-profile/disk
            operator: In
            values:
            - dedicated-nvme
  containers:
  - name: data-processor
    image: data-processor:latest
```

---

## Pod Affinity and Anti-Affinity: Co-location and Spreading

While Node Affinity controls how Pods relate to hardware, Pod Affinity and Anti-Affinity control how Pods relate to other Pods. This is essential for engineering both high-performance architectures and highly available systems.

### Pod Affinity: Optimizing for Latency

Pod Affinity instructs the scheduler to place a new Pod on the same topological domain as an existing Pod that matches a specific set of labels. This is primarily used to minimize network latency. 

Imagine you have a high-traffic web server that constantly reads from a Redis memory cache. If the web server Pod and the Redis Pod are placed on nodes in completely different physical data centers (different availability zones), every single cache read will incur cross-zone network latency, drastically slowing down the application. By using Pod Affinity, you can instruct the scheduler: "Do not schedule this web server Pod unless you can place it on the exact same physical node that is currently running the Redis Pod." This ensures that communication between the two Pods happens over the ultra-fast local virtual network interface, entirely bypassing the physical network switches.

### Pod Anti-Affinity: Engineering for Survival

Conversely, Pod Anti-Affinity instructs the scheduler to keep Pods away from each other. This is the cornerstone of high availability in Kubernetes. 

If you deploy a critical database with three replicas, and the scheduler happens to place all three Pods on the exact same physical node because that node had the most available resources, your architecture is extremely fragile. A single hardware failure on that one node will instantly wipe out your entire database cluster.

By applying a strict Pod Anti-Affinity rule, you force the scheduler to spread the replicas out. You instruct the scheduler: "Never place this database Pod on a node that is already running a database Pod with the same labels."

### Understanding the Topology Key

The most complex and powerful concept in Pod Affinity is the `topologyKey`. When you tell the scheduler to place a Pod "near" or "far away from" another Pod, you have to define what the boundaries of your physical environment are.

The `topologyKey` is simply a label key that exists on your nodes. 
If you set the topologyKey to `kubernetes.io/hostname`, you are defining the boundary as the individual physical server. A Pod Anti-Affinity rule with this key means "Do not place these Pods on the same physical server."

If you set the topologyKey to `topology.kubernetes.io/zone`, you are defining the boundary as an entire cloud provider availability zone. A Pod Anti-Affinity rule with this key means "Do not place these Pods in the same data center." This guarantees that even if a massive fire destroys an entire AWS or GCP availability zone, your application will survive because the scheduler was forced to place the replicas in entirely different physical facilities.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: highly-available-web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-frontend
  template:
    metadata:
      labels:
        app: web-frontend
    spec:
      affinity:
        podAntiAffinity:
          # Force the scheduler to place every replica in a DIFFERENT availability zone
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: web-frontend
            topologyKey: "topology.kubernetes.io/zone"
      containers:
      - name: web-server
        image: nginx:alpine
```

---

> **Stop and think**: You configure a Deployment with 5 replicas and a hard Pod Anti-Affinity rule using a topologyKey of `topology.kubernetes.io/zone`. Your cloud environment only has 3 availability zones available. What will happen to the 4th and 5th replicas when you apply this configuration?

---

## Taints and Tolerations: Dedicated Nodes and Evictions

Affinity is an attractive force; it allows Pods to seek out specific nodes. Taints and Tolerations represent a repulsive force; they allow nodes to actively repel Pods.

Imagine you purchase ten incredibly expensive servers equipped with top-of-the-line NVIDIA GPUs for your data science team. You add these nodes to your main Kubernetes cluster. If you do nothing, the kube-scheduler will see all that wonderful, unutilized CPU and memory, and it will start scheduling random web servers, background workers, and monitoring agents onto your multi-million dollar GPU hardware.

To prevent this, you apply a Taint to the nodes. A taint is a defensive mark placed on a node that tells the scheduler: "Do not schedule any Pods here unless they explicitly have permission."

You would taint the nodes using a command like:
`kubectl taint nodes gpu-node-01 dedicated=machine-learning:NoSchedule`

This taint consists of a key (`dedicated`), a value (`machine-learning`), and an effect (`NoSchedule`). Once applied, the node is completely quarantined. The scheduler's filtering phase will instantly reject this node for all standard workloads.

To allow the data science team's specific Pods to run on these expensive nodes, you must equip those Pods with a Toleration. A toleration is effectively a VIP pass that allows the Pod to bypass the node's taint. If the toleration in the Pod spec matches the key, value, and effect of the node's taint, the scheduler will allow the Pod to be placed there.

### The Three Effects of Taints

Taints are highly granular and support three distinct effects, each dictating a different level of severity.

1. **NoSchedule**: This is a hard constraint for new placements. The scheduler will absolutely not place new Pods on the node unless they have a matching toleration. However, if a Pod is already running on the node when the taint is applied, that existing Pod is left completely alone.
2. **PreferNoSchedule**: This is a soft constraint. The scheduler will try its best to avoid placing non-tolerating Pods on this node during the scoring phase, but if the rest of the cluster is completely full, it will reluctantly place standard Pods here to avoid leaving them Pending.
3. **NoExecute**: This is the most aggressive and destructive effect. Not only does it prevent new Pods from scheduling, but it actively attacks existing workloads. If you apply a `NoExecute` taint to a node, the kubelet will immediately begin evicting and terminating any Pod currently running on that node that does not possess a matching toleration. This is heavily used by Kubernetes internally; when a node loses network connectivity, the control plane automatically applies a `node.kubernetes.io/unreachable:NoExecute` taint to force all Pods to be evicted and rescheduled elsewhere.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: data-science-job
spec:
  # The VIP pass to bypass the node's defensive taint
  tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "machine-learning"
    effect: "NoSchedule"
  # Optional: Also add nodeSelector so it ONLY goes to these nodes
  nodeSelector:
    accelerator: nvidia-tesla-v100
  containers:
  - name: ml-processor
    image: tensor-flow-custom:v4
```

---

## Diagnosing Pending Pods: The Operator's Mindset

When you deploy an application and it fails to start, remaining stubbornly in the `Pending` state, it means the scheduling cycle has failed. The scheduler evaluated every node in your cluster and found zero valid candidates.

Do not guess why this happened. The kube-scheduler documents exactly why it rejected your workload. You must investigate the Pod's event log by running `kubectl describe pod <pod-name>`.

Scroll to the bottom of the output to the `Events:` section. You will see a `FailedScheduling` warning generated by the `default-scheduler`. The message will look something like this:

`Warning  FailedScheduling  3m22s  default-scheduler  0/15 nodes are available: 5 node(s) didn't match Pod's node affinity/selector, 6 Insufficient memory, 4 node(s) had taint {dedicated: database}, that the pod didn't tolerate.`

This single sentence tells you everything about the state of your cluster:
- You have 15 nodes total.
- 5 nodes were eliminated because your Pod has a nodeSelector or required Node Affinity rule that the nodes lack.
- 6 nodes had the right labels, but did not have enough unallocated memory to satisfy your Pod's Resource Requests.
- The remaining 4 nodes had enough memory and the right labels, but they have a defensive Taint that your Pod does not have a Toleration for.

To fix this, you have empirical choices: You can reduce the memory request of your Pod, you can add more memory-heavy nodes to the cluster, you can add the missing labels to the nodes with sufficient memory, or you can add a toleration to your Pod so it can run on the tainted database nodes. The scheduler's transparency allows you to make precise, engineering-driven decisions.

---

## Did You Know?

1. **Massive Scale Optimization**: In massive clusters, evaluating every node takes too long. By default, when a cluster grows beyond 100 nodes, the kube-scheduler stops evaluating all nodes. It uses a formula to calculate a percentage (scaling down to a minimum of 5 percent of total nodes). Once it finds enough feasible nodes in that percentage subset, it stops filtering and moves immediately to scoring, drastically reducing scheduling latency.
2. **Pluggable Architecture**: You are not restricted to the default scheduling logic. You can write your own custom scheduler in Go, deploy it as a Pod in the cluster, and specify `schedulerName: my-custom-scheduler` in your workloads. You can even run five different custom schedulers simultaneously in the same cluster.
3. **The Descheduler**: The default kube-scheduler only places Pods; it never moves them once they are running, even if the cluster becomes wildly unbalanced over time. To solve this, operators deploy a community tool called the "Descheduler," which runs as a CronJob, analyzes the cluster, and actively kills Pods that violate affinity rules or resource balances so the normal scheduler can place them better.
4. **Topology Spread Constraints**: Introduced as a stable feature in Kubernetes 1.19, Topology Spread Constraints allow you to define complex mathematical spreading logic, such as "Ensure that no availability zone has more than 2 replicas more than any other availability zone," providing much finer control than simple Pod Anti-Affinity.

---

## Common Mistakes

| Mistake | Why It Hurts | The Fix |
|---------|--------------|---------|
| Using `nodeSelector` for soft preferences | `nodeSelector` is an absolute hard constraint. If you use it to request an SSD, and all SSD nodes are full, your Pod will stay Pending forever, causing a localized outage. | Use Node Affinity with the `preferredDuringSchedulingIgnoredDuringExecution` clause to request SSDs while allowing fallback to standard disks. |
| Setting Limits without Requests | If you define a memory limit but omit the request, Kubernetes automatically sets the request equal to the limit. If you define neither, your Pod gets a "BestEffort" QoS class and will be the very first thing killed if the node experiences memory pressure. | Always define explicit resource requests to guarantee minimum capacity and achieve the "Burstable" QoS class. |
| Misunderstanding `topologyKey` | Using a topologyKey of `kubernetes.io/os` instead of `kubernetes.io/hostname` for a Pod Anti-Affinity rule in a purely Linux cluster. The scheduler will place the first replica on a node, realize the OS is Linux, and then refuse to place any other replicas anywhere else in the entire cluster. | Always double-check your topology keys. Use `hostname` for physical node separation and `zone` for datacenter separation. |
| Relying on "IgnoredDuringExecution" | Believing that removing a node label or applying a new taint will instantly clean up the cluster. The scheduler only acts at creation time; existing running Pods ignore new affinity rules. | If you need active eviction based on label changes, you must manually delete the violating Pods, use a `NoExecute` taint, or deploy the Descheduler tool. |
| Overly strict CPU Limits | CPU limits cause aggressive throttling. Because modern applications often require massive CPU bursts during startup (initialization, JIT compilation), strict limits will cause your application to take five minutes to start instead of ten seconds. | Leave CPU limits significantly higher than requests, or remove CPU limits entirely and rely on requests for placement and node-level CFS fairness. |
| Incorrect Toleration Operators | Using the `Equal` operator in a toleration but forgetting to specify the `value` field. The toleration will fail to match the taint, and the Pod will not schedule. | If you want to tolerate a specific key regardless of its value, you must explicitly change the operator to `Exists`. |

---

## Hands-On Exercise: Engineering Availability

In this exercise, you will master the art of scheduling constraints by engineering a highly available deployment and navigating defensive taints.

**Task 1**: Create a Deployment named `ha-cache` using the `redis:alpine` image. It must have 3 replicas.
<details>
<summary>Solution</summary>

```bash
kubectl create deployment ha-cache --image=redis:alpine --replicas=3 --dry-run=client -o yaml > ha-cache.yaml
```
</details>

**Task 2**: Modify the `ha-cache.yaml` file to include a strict Pod Anti-Affinity rule. Ensure that no two Redis replicas can ever run on the same physical node. Apply the file.
<details>
<summary>Solution</summary>

Edit the deployment YAML to include the affinity block under the Pod spec template:
```yaml
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: ha-cache
            topologyKey: kubernetes.io/hostname
      containers:
      - image: redis:alpine
```
Apply with `kubectl apply -f ha-cache.yaml`. Verify they are on different nodes using `kubectl get pods -o wide`.
</details>

**Task 3**: Select one of your worker nodes and apply a `NoSchedule` taint with the key `maintenance` and value `true`.
<details>
<summary>Solution</summary>

```bash
# Get your node names
kubectl get nodes

# Apply the taint to one node (e.g., node-2)
kubectl taint nodes <node-2-name> maintenance=true:NoSchedule
```
</details>

**Task 4**: Scale your `ha-cache` deployment to 5 replicas. Observe what happens to the new Pods.
<details>
<summary>Solution</summary>

```bash
kubectl scale deployment ha-cache --replicas=5
kubectl get pods
```
If you only have 3 or 4 nodes in your lab cluster, the new Pods will remain in a `Pending` state. The scheduler cannot place them because the Anti-Affinity rule forbids placing them on nodes already running a replica, and the empty node is defensively tainted against new workloads.
</details>

**Task 5**: Create a new standalone Pod named `admin-toolkit` that possesses the correct toleration to run on the tainted node, and use a nodeSelector to force it there.
<details>
<summary>Solution</summary>

Create a file `admin-pod.yaml`:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: admin-toolkit
spec:
  nodeSelector:
    kubernetes.io/hostname: <node-2-name>
  tolerations:
  - key: "maintenance"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
  containers:
  - name: shell
    image: busybox
    command: ["sleep", "3600"]
```
Run `kubectl apply -f admin-pod.yaml`. Because it has the VIP pass (toleration), it successfully bypasses the taint and schedules on the restricted node.
</details>

---

## Quiz: Operational Scenarios

Test your deep understanding of scheduling mechanics with these scenario-based questions.

1. **A critical financial processing Pod has been stuck in the Pending state for twenty minutes. When you run `kubectl describe pod`, the event log states: `0/8 nodes are available: 3 node(s) didn't match Pod's node affinity/selector, 5 Insufficient cpu.` Your monitoring dashboard shows that the 5 nodes with insufficient CPU are actually sitting at 10% overall CPU utilization. Why is the scheduler refusing to place the Pod on those seemingly empty nodes?**
   <details>
   <summary>Answer</summary>
   The kube-scheduler operates entirely on theoretical reservations, not real-time metrics. The 5 nodes have high CPU *Requests* allocated to existing Pods, mathematically maxing out the nodes' Allocatable capacity from the scheduler's perspective. Even though those existing Pods are currently idle and not utilizing their requested CPU cycles (hence the 10% actual usage), the scheduler honors their reservations. To fix this, you must either scale down over-provisioned Pods, reduce their CPU requests, or add more physical nodes.
   </details>

2. **Your infrastructure team needs to perform rolling kernel upgrades across all worker nodes over the weekend. They want to ensure that as they drain nodes, the web application replicas are completely spread out across the three physical availability zones to guarantee zero downtime. If they use a topologyKey of `kubernetes.io/hostname` for the anti-affinity rule, will this achieve their goal?**
   <details>
   <summary>Answer</summary>
   No, it will not guarantee survival across availability zones. The `hostname` topology key only forces the scheduler to place replicas on different physical servers. The scheduler could easily place all replicas on three different servers that all happen to reside in Availability Zone A. If Zone A goes offline during the upgrades, the entire application drops. To ensure survival across data center failures, they must use `topology.kubernetes.io/zone` as the topologyKey.
   </details>

3. **You configure a machine learning Deployment to request nodes equipped with expensive GPUs using a required Node Affinity rule. However, when you check the cluster later, you notice standard NGINX web servers are also running on those same GPU nodes, consuming memory and preventing new machine learning jobs from scheduling. What mechanism did you forget to implement?**
   <details>
   <summary>Answer</summary>
   You forgot to apply a Taint to the GPU nodes. Node Affinity is an attractive force—it pulls the ML workloads to the GPU nodes. However, without a defensive Taint (e.g., `gpu=true:NoSchedule`), the GPU nodes appear as standard, high-capacity hardware to the scheduler. Therefore, the scheduler freely places standard NGINX Pods on them. You must taint the nodes to repel normal traffic and add corresponding Tolerations to your ML Pods.
   </details>

4. **A junior developer creates a deployment and sets the CPU Request to `4000m` (4 full cores) and the memory limit to `50Mi`. The application actually requires about `200m` of CPU and `500Mi` of memory to run. Predict exactly what will happen during scheduling and runtime.**
   <details>
   <summary>Answer</summary>
   During scheduling, the Pod will aggressively consume cluster capacity, requiring a node with at least 4 full unallocated cores. This may cause the Pod to stay Pending if no such node exists, despite actual utilization being low. During runtime, because the memory limit is set to a tiny 50 Mebibytes (far below the actual 500Mi requirement), the container will instantly exceed its incompressible limit upon startup. The Linux kernel will trigger an Out Of Memory (OOM) kill, causing the Pod to immediately crash and enter a `CrashLoopBackOff` state.
   </details>

5. **A node in your cluster begins experiencing severe disk IO errors, effectively corrupting the hardware. To isolate it, an administrator applies a `gpu-failure=true:NoExecute` taint to the node. What exactly happens to the five running Pods currently residing on that node, assuming none of them have tolerations?**
   <details>
   <summary>Answer</summary>
   Because the taint uses the `NoExecute` effect rather than just `NoSchedule`, it actively attacks existing workloads. The kubelet on that corrupted node will immediately begin the eviction process for all five Pods. They will be gracefully terminated and, assuming they are managed by a controller like a Deployment or ReplicaSet, the controller will notice they are gone and request replacement Pods. The scheduler will then place those replacements on healthy nodes, successfully migrating traffic away from the failing hardware.
   </details>

6. **You want your analytics Pods to run on nodes with high-speed NVMe storage if possible, but you still want the analytics jobs to run on slower standard disks if the NVMe nodes are fully occupied. Which specific affinity rule configuration must you use to achieve this fallback behavior?**
   <details>
   <summary>Answer</summary>
   You must use Node Affinity with the `preferredDuringSchedulingIgnoredDuringExecution` clause. This creates a soft preference that hooks into the scheduler's scoring phase. The scheduler will evaluate all nodes, heavily weighting (scoring higher) the nodes with the NVMe label. However, if those nodes are filtered out due to insufficient resources, the scheduler will simply select the highest-scoring standard node instead of leaving the Pod in a Pending state.
   </details>

---

## Summary

**The Scheduling Lifecycle**:
1. **Filtering (Predicates)**: A ruthless elimination process checking hard constraints (Resource Requests, required nodeSelector, port conflicts).
2. **Scoring (Priorities)**: A grading system for feasible nodes to find the optimal placement (spreading workloads, caching images).
3. **Binding**: The API server is updated, and the destination kubelet takes over execution.

**Directing Workloads**:
- **Node Affinity**: How Pods select hardware. Supports hard requirements (Required) and weighted soft preferences (Preferred).
- **Pod Affinity/Anti-Affinity**: How Pods select or avoid other Pods. Heavily dependent on the `topologyKey` to define physical boundaries (host vs. zone).
- **Taints and Tolerations**: How Nodes actively repel unwanted Pods. Includes effects like `NoSchedule` (repel new) and `NoExecute` (evict existing).

**Resource Management**:
- **Requests**: Used exclusively by the scheduler for placement based on theoretical capacity.
- **Limits**: Enforced at runtime by the Linux kernel. Exceeding CPU causes throttling; exceeding memory causes OOMKilled crashes.

---

## Next Module

[Module 2.2: Scaling](../module-2.2-scaling/) - Discover how Kubernetes transitions from static placement to dynamic, automated growth by manipulating ReplicaSets based on real-time application metrics.