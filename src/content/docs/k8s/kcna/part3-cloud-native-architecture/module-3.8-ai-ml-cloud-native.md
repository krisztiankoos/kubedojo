---
title: "Module 3.8: AI/ML on Cloud Native Infrastructure"
slug: k8s/kcna/part3-cloud-native-architecture/module-3.8-ai-ml-cloud-native
revision_pending: false
sidebar:
  order: 9
---

# Module 3.8: AI/ML on Cloud Native Infrastructure

> **Complexity**: `[MEDIUM]` - Cloud native architecture and workload design
>
> **Time to Complete**: 35-45 minutes
>
> **Prerequisites**: Module 3.1 (Cloud Native Principles), Module 3.3 (Cloud Native Patterns), basic familiarity with Pods, Deployments, Jobs, and scheduling

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Apply** Kubernetes resource and scheduling concepts to choose appropriate runtime patterns for AI/ML training, fine-tuning, batch inference, and real-time inference workloads.
2. **Compare** GPU-enabled Kubernetes components such as device plugins, node labels, taints, autoscaling, and specialized schedulers in realistic platform design scenarios.
3. **Design** a basic cloud native serving architecture for a model endpoint that balances privacy, latency, scaling behavior, and operational responsibility.
4. **Debug** common AI/ML scheduling failures by reading Pod status, scheduler events, node capacity, and accelerator resource requests.
5. **Evaluate** when ecosystem tools such as Kubeflow, KServe, Ray, vLLM, GPU Operator, and Volcano fit the problem instead of treating every model workload as an ordinary web service.

## Why This Module Matters

A retail company launched a recommendation feature that worked during a controlled pilot, then failed during a holiday traffic surge when the business needed it most. The frontend scaled, the checkout path stayed healthy, and the database still had room, yet the recommendation endpoint slowed until it became unavailable for many shoppers. The platform team eventually found the expensive truth: the model server needed GPUs, the cluster autoscaler was adding only CPU nodes, and new inference replicas were stuck Pending while the product team watched abandoned carts climb during peak demand.

That kind of outage is common because AI/ML workloads look deceptively familiar from a Kubernetes distance. They still run in containers, use Services, emit logs, mount Secrets, and benefit from controllers, but their real limiting resources are often accelerators, GPU memory, model warm-up time, distributed worker coordination, and storage throughput. A learner who treats a model endpoint like a normal stateless API will miss the resource request that decides placement, the readiness gate that protects callers, or the autoscaling signal that shows a GPU is saturated while CPU looks calm.

KCNA does not expect you to become a machine learning engineer, tune kernels, or install every tool in the ML ecosystem. It does expect you to reason about why Kubernetes is useful for AI/ML platforms, how accelerators become schedulable resources, why training and inference use different workload patterns, and when specialized controllers or schedulers are worth their operational cost. This module uses Kubernetes 1.35+ concepts and keeps the emphasis on platform judgment: what must be scheduled, what must be isolated, what must be scaled, and what evidence you read when it fails.

## 1. Kubernetes Is Useful for AI/ML Because It Coordinates Scarce Infrastructure

Kubernetes did not become useful for AI/ML because the core control plane understands neural networks. It became useful because AI/ML platforms need the same cloud native coordination that other production systems need: repeatable deployment, scheduling, isolation, storage integration, network policy, rollout control, observability, and shared APIs for many teams. The difference is that the scarce infrastructure is often more specialized and more expensive than ordinary CPU capacity, so a sloppy scheduling decision can waste a whole accelerator node instead of a few millicores.

The shift is easiest to see by comparing an ordinary web API with a model workload. A small web API may run on almost any node that has enough CPU and memory, and if it receives too much CPU pressure it may slow down before it completely fails. A training job may need multiple GPUs, large local scratch space, high-throughput access to datasets, and several workers that start together. A model server may need one GPU, enough VRAM to load the model, and autoscaling policies tied to request latency, queue depth, or tokens generated per second rather than CPU utilization alone.

```text
┌─────────────────────────────────────────────────────────────┐
│              WHY K8S FOR AI/ML?                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Kubernetes provides what AI/ML workloads need:             │
│                                                             │
│  1. GPU SCHEDULING                                          │
│     ─────────────────────────────────────────────────────   │
│     K8s schedules GPUs like CPU/memory after a device       │
│     plugin advertises accelerator capacity to each kubelet  │
│                                                             │
│  2. DEVICE PLUGINS                                          │
│     ─────────────────────────────────────────────────────   │
│     Extend K8s to manage specialized hardware:              │
│     • NVIDIA GPUs exposed as nvidia.com/gpu                 │
│     • AMD GPUs, Intel accelerators, Google TPUs             │
│     • Any accelerator integrated through the plugin model   │
│                                                             │
│  3. BATCH PROCESSING                                        │
│     ─────────────────────────────────────────────────────   │
│     Jobs and training operators handle runs that finish,    │
│     unlike services that are expected to run continuously   │
│                                                             │
│  4. AUTOSCALING                                             │
│     ─────────────────────────────────────────────────────   │
│     Scale inference endpoints with traffic, queue length,   │
│     latency, or custom metrics when capacity exists         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

A useful mental model is to separate Kubernetes into a coordination layer and an extension layer. The core platform knows how to run Pods, place them on nodes, track desired state, expose Services, and report events. The AI/ML extensions teach that platform about specialized hardware, distributed training groups, model serving conventions, and experiment workflows. When a Pod requests a GPU, Kubernetes is not running a machine learning algorithm; it is matching a resource request against allocatable capacity that another component has published.

Pause and predict: a cluster has three CPU-only nodes and one GPU node. A Pod requests `nvidia.com/gpu: 1` but does not include any node selector or affinity. If the NVIDIA device plugin is installed only on the GPU node, where can the scheduler place the Pod, and what status should you expect if that GPU is already allocated to another Pod?

The answer is that the Pod can only run where the requested extended resource is available. If the only GPU is already allocated, the Pod remains Pending because GPU resources are non-compressible from the scheduler's point of view. CPU can be throttled when a container exceeds its CPU request, but a Pod that requests an integer GPU either receives the device or it does not start. This is why AI/ML failures often show up first as scheduling events, not application logs.

One practical war story illustrates the point. A platform team once moved a batch image-labeling workload from a hand-managed GPU server into Kubernetes and celebrated when the first Pod ran. The next day, the daily batch missed its deadline because the team had created a Deployment instead of a Job and had not set namespace-level quotas. The controller kept replacing completed Pods, several experiments consumed the same GPU pool, and the actual business batch sat Pending; the fix was not a new model, but a clearer workload pattern and resource policy.

## 2. How GPUs Become Schedulable Kubernetes Resources

Kubernetes does not automatically discover every accelerator in the data center. The kubelet receives accelerator capacity from a device plugin, and the plugin usually runs as a DaemonSet on nodes that have the hardware. The device plugin reports resources such as `nvidia.com/gpu`, and the node status then includes that resource as allocatable capacity. Until that chain works, the scheduler has no GPU resource to allocate, even if a physical server has a card installed.

A Pod requests GPUs in the `resources.limits` field. Extended resources are requested as whole units, and for common GPU configurations the request and limit act as the same scheduling signal. The scheduler then compares the Pod's request with node allocatable capacity and existing allocations before binding the Pod to a node. This is a simple idea with expensive consequences: a typo in the resource name, a missing device plugin, or a consumed GPU can block the workload before the container image is ever pulled.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-smoke-test
spec:
  restartPolicy: Never
  containers:
    - name: cuda-container
      image: nvidia/cuda:12.4.1-base-ubuntu22.04
      command: ["nvidia-smi"]
      resources:
        limits:
          nvidia.com/gpu: 1
```

This manifest is intentionally small because the important lesson is the resource request, not the application. If the cluster has a GPU node, the device plugin is healthy, the GPU is free, and the container runtime can expose the device, the Pod can run and execute `nvidia-smi`. If any of those assumptions are false, Kubernetes will not invent an accelerator; the Pod stays Pending, and the scheduler event explains which resource or placement constraint is missing.

| Concept | What It Means | Why It Matters in Practice |
|---------|---------------|----------------------------|
| **Device Plugin** | A node-level component, commonly deployed as a DaemonSet, that advertises accelerator devices to the kubelet. | Without it, Kubernetes usually sees ordinary CPU and memory but no GPU resource to schedule. |
| **`nvidia.com/gpu`** | The common extended resource name used by NVIDIA GPU plugins. | Pods request this name, so a typo or missing plugin produces Pending Pods rather than slower execution. |
| **GPU time-slicing** | A configuration that allows multiple Pods to share one physical GPU over time. | It can improve utilization for light workloads, but it weakens isolation and may hurt latency predictability. |
| **MIG** | Multi-Instance GPU partitioning on supported NVIDIA hardware, exposing hardware-isolated GPU slices. | It gives stronger isolation than time-slicing for suitable workloads, but it requires compatible hardware and planning. |
| **Whole GPU allocation** | One Pod receives exclusive access to a full physical GPU. | It is the simplest model and often best for heavy training or latency-sensitive inference. |

Node labels and taints often appear alongside GPU resources because teams rarely want every Pod to land on expensive accelerator nodes. Labels help target workloads to specific node groups, such as nodes with a particular GPU model or memory profile. Taints help keep ordinary workloads away unless those workloads explicitly tolerate the taint. The GPU resource request itself is still essential because a label says "run on this kind of node" while `nvidia.com/gpu: 1` says "allocate one accelerator device to this container."

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recommender-inference
spec:
  replicas: 2
  selector:
    matchLabels:
      app: recommender-inference
  template:
    metadata:
      labels:
        app: recommender-inference
    spec:
      nodeSelector:
        accelerator: nvidia
      tolerations:
        - key: "accelerator"
          operator: "Equal"
          value: "gpu"
          effect: "NoSchedule"
      containers:
        - name: model-server
          image: ghcr.io/example/recommender:1.0.0
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: "2"
              memory: 8Gi
            limits:
              nvidia.com/gpu: 1
              memory: 16Gi
```

Notice the separation of concerns in this Deployment. The `nodeSelector` and toleration steer the Pod toward the GPU node group, while the GPU limit reserves the accelerator. CPU and memory requests tell the scheduler how much ordinary capacity the Pod needs, and the memory limit prevents one model server from exhausting the node. This is the combined reasoning KCNA expects: apply several platform mechanisms together, then read Pod events when one of those mechanisms does not match reality.

Before running this in a real cluster, predict which failure you would see if the node label exists but the device plugin is missing. The Pod may target the right kind of node, but the scheduler still cannot satisfy `nvidia.com/gpu: 1` because no allocatable GPU resource exists. That distinction matters during incident response because changing selectors will not fix a broken device plugin, and installing a plugin will not fix a missing toleration on a tainted node.

## 3. Training, Fine-Tuning, Batch Inference, and Real-Time Inference Are Different Workloads

The biggest beginner mistake is calling every model-related container "AI" and then deploying it the same way. Kubernetes architecture starts with workload shape, not with the label on the project. Does the process finish or run forever? Does it need all workers at once? Does it serve users synchronously? Does it need one GPU, many GPUs, or no GPU after preprocessing? Those questions determine whether you choose a Job, a Deployment, a training operator, a workflow, or a serving abstraction.

```text
┌─────────────────────────────────────────────────────────────┐
│              AI/ML WORKLOAD TYPES                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TRAINING                                                   │
│  ─────────────────────────────────────────────────────────  │
│  • Runs for hours, days, or sometimes longer                │
│  • May need many GPUs distributed across nodes              │
│  • Batch workload that should complete successfully         │
│  • Distributed runs may need gang scheduling                │
│                                                             │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐ │
│  │ GPU worker │ │ GPU worker │ │ GPU worker │ │ GPU lead │ │
│  │   node A   │ │   node A   │ │   node B   │ │  node B  │ │
│  └────────────┘ └────────────┘ └────────────┘ └──────────┘ │
│                                                             │
│  INFERENCE SERVING                                          │
│  ─────────────────────────────────────────────────────────  │
│  • Runs continuously and serves predictions                 │
│  • Latency-sensitive because users or applications wait     │
│  • Often scales by adding replicas behind a Service         │
│  • May use one GPU per replica or partitioned GPU capacity  │
│                                                             │
│  Request ──▶ [Model Server] ──▶ Prediction                  │
│             [Model Server]      Autoscaled replicas         │
│             [Model Server]                                 │
│                                                             │
│  FINE-TUNING                                                │
│  ─────────────────────────────────────────────────────────  │
│  • Starts from a pretrained model and adapts it to data     │
│  • Usually shorter than full training                       │
│  • Still sensitive to checkpointing, storage, and GPUs      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Training is usually a batch problem. A data science team starts a run, waits for it to finish, and expects artifacts such as model weights, metrics, logs, and checkpoints. Kubernetes Jobs fit simple training because they track completion and do not restart successful Pods forever. Larger teams may use training operators such as PyTorchJob or TFJob because those operators understand worker roles, distributed launch behavior, failure policy, and training-specific lifecycle events that a plain Deployment does not represent.

Real-time inference is usually a service problem. A model endpoint accepts requests, returns predictions, and must stay available while traffic changes. Deployments, Services, autoscalers, and rollout strategies fit this shape because replicas can be replaced gradually and traffic can be routed away from unhealthy Pods. Inference also has special constraints: model startup may take minutes, GPU memory may be the limiting factor, and CPU utilization may not reflect the bottleneck that users experience as latency.

Batch inference sits between those two patterns. It uses a trained model to score a large offline dataset, such as millions of images, support tickets, transactions, or documents, then writes results to storage. It does not need a public endpoint because nobody is waiting on each individual request. A Job or workflow engine is usually a better fit than a Deployment, because completion, idempotent output, retry behavior, and chunk sizing matter more than steady request latency.

Fine-tuning adds another wrinkle because it starts from an existing model and adapts it to a narrower dataset or task. It may be shorter than full training, but it can still require GPUs, checkpointing, reproducible inputs, and careful namespace policy because several teams may fine-tune variants of the same base model. From a Kubernetes perspective, the important question is whether the process is finite and artifact-producing, not whether the math is called training or fine-tuning by the ML team.

| Aspect | Training | Fine-Tuning | Batch Inference | Real-Time Inference |
|--------|----------|-------------|-----------------|---------------------|
| **Duration** | Long-running but finite, often hours or days. | Finite and usually shorter than full training. | Finite, tied to a dataset or queue. | Continuous, serving as long as the product needs predictions. |
| **Kubernetes pattern** | Job, training operator, or batch scheduler. | Job or specialized operator. | Job, workflow, or queue-driven workers. | Deployment, Service, autoscaler, and rollout controls. |
| **Scaling concern** | Throughput, parallel workers, and checkpoint restart. | GPU cost, storage access, and repeatability. | Dataset throughput and failure recovery. | Latency, concurrency, readiness, and traffic spikes. |
| **Failure handling** | Resume from checkpoints or restart a failed run. | Save intermediate adapters or checkpoints. | Retry failed chunks without duplicating output. | Route around unhealthy replicas and roll out safely. |
| **Scheduling risk** | Partial worker placement can waste GPUs. | A few GPUs may block other teams if priorities are unclear. | Large queues can starve interactive workloads. | Replicas may start too slowly for sudden traffic. |

Stop and decide: your team has a script that reads yesterday's support tickets, classifies each ticket with an existing model, writes labels to a database, and exits. Would you run it as a Deployment, a Job, or a DaemonSet? Write down the Kubernetes behavior you need before choosing the resource.

A good answer chooses a Job or workflow task because the process has a clear end condition. A Deployment would keep restarting the classifier after it finishes, and a DaemonSet would run one copy on every matching node whether or not the data pipeline needs that. The decision comes from workload shape, not from the fact that a model is involved. This habit prevents many expensive mistakes because it aligns controller behavior with the lifecycle of the actual work.

## 4. Distributed Training Needs Scheduling Guarantees That Default Kubernetes May Not Provide

Default Kubernetes schedules Pods one at a time. That is enough for many independent services, but distributed training often needs a group of workers to start together. If a training job needs several GPU workers and only some are scheduled, those scheduled workers may hold expensive accelerators while waiting for peers that cannot start. From the user's point of view the job looks stuck; from the platform's point of view, scarce capacity is stranded in Pods that are not producing useful work.

Gang scheduling solves that problem by treating a set of Pods as a unit. The scheduler admits the group only when enough resources exist for the whole group, or it waits without binding partial workers. Tools such as Volcano add batch scheduling capabilities including gang scheduling, queues, and fair sharing. KCNA does not require deep configuration knowledge, but it does expect you to recognize why the default scheduler's one-Pod-at-a-time behavior can be a poor fit for distributed AI/ML jobs.

```text
┌─────────────────────────────────────────────────────────────┐
│          DEFAULT SCHEDULING VS. GANG SCHEDULING             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Default scheduler:                                         │
│                                                             │
│  worker-1 ──▶ scheduled ──▶ holds GPU                       │
│  worker-2 ──▶ scheduled ──▶ holds GPU                       │
│  worker-3 ──▶ Pending   ──▶ no GPU left                     │
│  worker-4 ──▶ Pending   ──▶ no GPU left                     │
│                                                             │
│  Result: partial job may hold GPUs while doing no work       │
│                                                             │
│  Gang scheduler:                                            │
│                                                             │
│  workers 1-4 ──▶ enough GPUs? ──▶ yes: schedule all          │
│                         │                                   │
│                         └────▶ no: schedule none yet         │
│                                                             │
│  Result: fewer stranded GPUs and clearer queue behavior      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Distributed training also makes storage and networking more important. Workers may read large datasets, exchange gradients, and write checkpoints frequently enough that a slow storage path wastes GPU time. A platform design that focuses only on GPU count can still fail if workers cannot communicate reliably or if checkpoint writes become the hidden bottleneck. Senior-level Kubernetes reasoning means asking which resource becomes limiting next, not stopping after the first successful Pod start.

Priorities and quotas matter because GPU clusters are shared. A research notebook, a production inference endpoint, a nightly batch inference job, and a training run should not all compete without policy. ResourceQuota, PriorityClass, queueing systems, and separate node pools are ways to express business intent. The platform should answer questions such as "Can an experiment delay production inference?" and "How many GPUs can one namespace consume?" before a traffic spike or training deadline forces the issue.

A practical way to evaluate a distributed training design is to imagine the failure halfway through scheduling. If half the workers can run and half cannot, does that partial run make progress, or does it waste GPUs while waiting? If the answer is waste, the workload likely needs a batch scheduler, a training operator with clearer lifecycle handling, or a queue policy that holds the whole group until enough capacity exists. This comparison of default scheduling and specialized scheduling is exactly where KCNA wants you to move from feature names to consequences.

## 5. Model Serving Adds Latency, Rollout, and Privacy Trade-Offs

Serving a model is not just running a Python process in a container. The model has to be loaded, kept warm, monitored, scaled, and updated without breaking callers. A small model may behave like an ordinary web API, but a large language model can take significant time to start and may consume most of a GPU's memory before receiving a single request. That startup behavior changes how you design readiness, rollout, and autoscaling.

Organizations self-host inference for several reasons. Privacy is a common driver because prompts, documents, images, or customer records may be too sensitive to send to an external API. Latency can improve when the model server is close to the application and data. Cost can improve at sustained high volume if the team can keep GPUs highly utilized. Control improves because the organization chooses model versions, quantization settings, runtime flags, rollout timing, and observability.

```text
┌─────────────────────────────────────────────────────────────┐
│              WHY SELF-HOST LLMs?                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PRIVACY      Sensitive data stays in controlled systems    │
│  COST         Sustained high volume may beat per-token APIs │
│  LATENCY      Co-locate model servers with applications     │
│  COMPLIANCE   Meet data residency and audit requirements    │
│  CONTROL      Choose model, version, runtime, and rollout   │
│                                                             │
│  Trade-off: The platform team owns GPUs, drivers, scaling,  │
│  model rollout, capacity planning, and incident response.   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

The trade-off is operational responsibility. A public model API hides GPU drivers, capacity planning, batching, runtime tuning, and model-server upgrades. A self-hosted platform exposes all of those concerns to the organization. Kubernetes helps coordinate the system, but it does not remove the need to understand accelerator scarcity, model memory, autoscaling metrics, or release safety. In practice, self-hosting is a platform product, not just an application deployment.

For inference, readiness probes are especially important. A container can be running while the model is still loading, and sending traffic too early creates failed requests. A readiness probe should report ready only after the server can actually answer predictions. For large models, startup probes may also be necessary so Kubernetes does not kill a slow-loading container before it has a fair chance to become healthy. Liveness should be used carefully because a model server under heavy load may need backpressure, not an aggressive restart loop.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ticket-classifier
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ticket-classifier
  template:
    metadata:
      labels:
        app: ticket-classifier
    spec:
      containers:
        - name: classifier
          image: ghcr.io/example/ticket-classifier:2.1.0
          ports:
            - containerPort: 8080
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            periodSeconds: 5
            failureThreshold: 6
          startupProbe:
            httpGet:
              path: /ready
              port: 8080
            periodSeconds: 10
            failureThreshold: 30
          resources:
            requests:
              cpu: "1"
              memory: 4Gi
            limits:
              memory: 8Gi
              nvidia.com/gpu: 1
```

This Deployment teaches two subtle points. First, readiness is about serving capability, not container existence. Second, resource limits and probes must match the model's real behavior. If the model takes several minutes to load but the startup probe gives it only one minute, Kubernetes will create a crash loop even though the image and code are correct. If readiness turns true before weights are loaded, the Service can route production requests to a replica that is technically Running but functionally useless.

Autoscaling has similar traps. HorizontalPodAutoscaler can scale on CPU and memory, but those are often weak signals for GPU-backed inference. A model server may be bottlenecked on GPU memory, batch queue depth, request latency, or token generation throughput while CPU remains moderate. Serving systems and custom metrics adapters can expose better scaling signals, but the platform still needs capacity to add replicas. Scaling from two GPU replicas to six is only useful if the cluster can actually add or free four more schedulable accelerator slots.

## 6. Ecosystem Tools Solve Different Parts of the AI/ML Lifecycle

The AI/ML on Kubernetes ecosystem is large because the lifecycle is larger than "run a container." Teams need notebooks for exploration, pipelines for repeatable training, registries for model versions, serving systems for inference, schedulers for batch jobs, and monitoring for performance drift. No single tool should be selected just because it appears in an architecture diagram. The more useful question is which part of the workflow is painful enough to justify another control plane or operator.

Kubeflow is often discussed as an end-to-end ML platform on Kubernetes. It can include notebooks, pipelines, training components, and serving integrations. It is useful when an organization wants a shared workflow environment for data scientists and ML engineers rather than isolated YAML files. It also increases platform complexity, so a small team serving one model may not need the full stack until repeated pipelines, governance, and multi-team collaboration create enough pressure.

KServe focuses on model serving. It provides abstractions for inference services, rollout patterns, autoscaling integrations, and model-server conventions. vLLM is a high-throughput inference engine often used for large language models, where batching and memory management strongly affect cost and latency. Ray is a distributed computing framework used for training, data processing, and serving patterns that need flexible distributed execution. The NVIDIA GPU Operator automates much of the node-side GPU stack, while Volcano focuses on batch scheduling behavior such as queues and gang scheduling.

| Tool | What It Does | Best-Fit Scenario |
|------|-------------|-------------------|
| **Kubeflow** | Provides a Kubernetes-native ML platform with notebooks, pipelines, training components, and serving integrations. | A platform team wants a shared ML workflow environment for multiple teams. |
| **KServe** | Standardizes model inference serving on Kubernetes with rollout and scaling patterns. | A team needs production model endpoints rather than only training jobs. |
| **Ray** | Runs distributed Python workloads for training, data processing, and serving. | A workload needs flexible distributed execution beyond a single Pod. |
| **vLLM** | Serves large language models efficiently using optimized batching and memory handling. | An organization self-hosts LLM inference and needs high throughput per GPU. |
| **NVIDIA GPU Operator** | Automates GPU driver, container runtime, monitoring, and device plugin setup. | A platform team manages NVIDIA GPU node pools and wants repeatable operations. |
| **Volcano** | Adds batch scheduling features such as gang scheduling, queues, and fair sharing. | Distributed training jobs need all workers scheduled together or predictable queue behavior. |

```text
┌─────────────────────────────────────────────────────────────┐
│              ML PIPELINE ON KUBERNETES                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Data Prep ──▶ Training ──▶ Evaluation ──▶ Serving ──▶ Monitor│
│     │             │              │             │          │ │
│  [Spark or     [Kubeflow      [tests,       [KServe,   [Prom │
│   Ray jobs]     Training]      metrics]      vLLM]      + logs│
│                                                             │
│  Kubernetes provides the API, Pods, Services, controllers,  │
│  scheduling hooks, secrets, storage integration, and events. │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Architecture check: your organization has one fraud model that is retrained weekly and served behind an internal API. The data science team does not need notebooks in the cluster. Which is more likely to be the first useful platform investment: a full Kubeflow installation, a small Job plus Deployment pattern, or a serving-focused tool such as KServe? Justify the operational cost of your choice.

A practical answer might start with a Job for retraining and a Deployment or KServe-based inference endpoint, then add Kubeflow only when repeated workflows, notebooks, lineage, or multi-team standardization justify the overhead. Tool selection should follow workflow pain. Installing a large platform before the team has a lifecycle problem can create more work than it removes, and that extra work often lands on the same platform engineers who are already responsible for GPU nodes, upgrades, observability, and incident response.

## 7. Worked Example: Debug a Pending GPU Inference Deployment

A worked example shows the reasoning process before you attempt a similar hands-on task. In this scenario, a team deploys a model server for real-time inference. The Deployment is correct enough to create Pods, but no replica becomes Running. Your goal is to move from symptom to cause using Kubernetes evidence rather than guessing. This is the same diagnostic loop you will use in the lab: observe controller status, inspect the Pod, read scheduler events, confirm node capacity, and then check placement constraints.

The team applies this Deployment to a development cluster. They expect one replica to start because they believe the cluster has a GPU node. The platform uses the common `k` alias for `kubectl`; after defining the alias once with `alias k=kubectl`, the commands below use `k` for brevity. In an exam or production incident, the habit matters more than the alias: always distinguish scheduling failure from runtime failure before changing manifests.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: image-ranker
spec:
  replicas: 1
  selector:
    matchLabels:
      app: image-ranker
  template:
    metadata:
      labels:
        app: image-ranker
    spec:
      containers:
        - name: ranker
          image: ghcr.io/example/image-ranker:1.0.0
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: "1"
              memory: 4Gi
            limits:
              memory: 8Gi
              nvidia.com/gpu: 1
```

### Step 1: Start with the controller, then inspect the Pod

A beginner often starts by changing YAML immediately, but a stronger habit is to inspect what Kubernetes created. The Deployment owns a ReplicaSet, and the ReplicaSet owns Pods. If the Deployment has unavailable replicas, the next useful evidence is usually the Pod status and events. That evidence tells you whether the scheduler, image pull, container runtime, health checks, or application code is the next place to investigate.

```bash
k get deployment image-ranker
k get pods -l app=image-ranker
```

Example output:

```text
NAME            READY   UP-TO-DATE   AVAILABLE   AGE
image-ranker    0/1     1            0           2m

NAME                             READY   STATUS    RESTARTS   AGE
image-ranker-6c9d7f8d9b-hp2lm    0/1     Pending   0          2m
```

Pending means the container has not started. That is different from CrashLoopBackOff, where the Pod was scheduled and a container started but failed. For scheduling problems, the `describe pod` output is the main source of truth because it includes scheduler events. You should read those events literally before assuming a fix, because the same Pending status can be caused by missing GPUs, taints, affinity rules, volume binding, or quota.

```bash
k describe pod -l app=image-ranker
```

Example event:

```text
Events:
  Type     Reason             Age   From               Message
  ----     ------             ----  ----               -------
  Warning  FailedScheduling   2m    default-scheduler  0/4 nodes are available: 4 Insufficient nvidia.com/gpu.
```

### Step 2: Interpret the event instead of memorizing the answer

The scheduler says it cannot find enough `nvidia.com/gpu` capacity. That does not prove the cluster has no physical GPU. It proves the Kubernetes scheduler does not currently see allocatable free capacity for that resource. The cause could be missing device plugin, no GPU nodes, a consumed GPU, a node taint without toleration, or node affinity that excludes the right node. Good debugging keeps those possibilities separate until evidence eliminates them.

The next command checks whether any node advertises GPU capacity. If no node shows `nvidia.com/gpu` under allocatable resources, the problem is lower than the workload manifest. The platform team needs to confirm GPU nodes, drivers, container runtime integration, and the device plugin. If a node does show allocatable GPU capacity, the next question is whether it is already allocated or blocked by placement rules.

```bash
k describe nodes | grep -A5 -E "Name:|Allocatable:"
```

A healthy GPU node would include a line like this somewhere under `Allocatable`:

```text
nvidia.com/gpu:  1
```

If no such line appears, deploying more model replicas will not help. The scheduler cannot allocate a resource that the nodes do not advertise. The likely fix is to install or repair the GPU device plugin, or use a managed GPU node pool that includes the required integration. This is also where managed Kubernetes details matter: the node pool may exist, but the driver and plugin integration still need to match the provider's documented path.

### Step 3: Check whether the workload is missing placement rules

Suppose a node does advertise `nvidia.com/gpu`, but the Pod is still Pending. The next useful question is whether the node has taints that repel ordinary Pods. GPU nodes are commonly tainted because they are expensive, and the platform team wants only GPU-aware workloads to land there. A Pod can request a GPU and still fail scheduling if it does not tolerate the taint on the only matching node.

```bash
k describe node gpu-node-1 | grep -A4 Taints
```

Example output:

```text
Taints: accelerator=gpu:NoSchedule
```

The Deployment above requests a GPU but does not tolerate the taint. The fix is to add a matching toleration, and many teams also add a node selector or affinity rule to express the intended node pool. The resource request reserves the device, the toleration permits the Pod to land on the protected node, and the selector or affinity communicates which hardware class the workload expects.

```yaml
spec:
  template:
    spec:
      nodeSelector:
        accelerator: nvidia
      tolerations:
        - key: "accelerator"
          operator: "Equal"
          value: "gpu"
          effect: "NoSchedule"
```

### Step 4: Verify the corrected scheduling path

After updating the Deployment, verify the Pod again instead of assuming the fix worked. A successful result should move from Pending to ContainerCreating and then Running, assuming image pulls and model startup succeed. If it moves to CrashLoopBackOff, that is progress in the debugging sequence because the problem changed from scheduling to runtime. Your next evidence would be container logs, events, probes, and resource limits rather than scheduler capacity.

```bash
k rollout status deployment/image-ranker
k get pods -l app=image-ranker -o wide
k describe pod -l app=image-ranker
```

The key lesson is the order of investigation. Start with the observed status, read scheduler events, confirm node allocatable resources, then inspect placement constraints such as taints, tolerations, selectors, and affinity. That same pattern works for the hands-on exercise later in the module, even when your local cluster has no real GPU hardware. In a CPU-only lab, the expected Pending result becomes useful evidence rather than a failed exercise.

## Patterns & Anti-Patterns

The first reliable pattern is to separate finite work from continuous serving before you write YAML. Training, fine-tuning, and batch inference usually produce artifacts or records and then stop, so Jobs, workflows, or training operators fit their lifecycle. Real-time inference accepts requests until the product is retired, so Deployments, Services, serving abstractions, and autoscaling fit better. This pattern works because the controller's reconciliation behavior matches the work: Jobs care about completion, while Deployments care about available replicas.

The second pattern is to make accelerator intent explicit in three places: resource requests, placement policy, and operational ownership. The resource request reserves the schedulable device, node selectors or affinity express the intended hardware pool, and taints or tolerations protect expensive nodes from accidental use. Ownership matters because a GPU node pool also needs driver updates, device plugin health checks, monitoring, quota policy, and cost review. The pattern scales when teams can answer who owns each layer before the first incident.

The third pattern is to scale inference from user-visible signals instead of convenient metrics. CPU is easy to collect, but it may be a poor proxy for a model server that is limited by GPU memory, batching efficiency, queue depth, token throughput, or latency. A serving platform should expose metrics that connect capacity to user experience, then make sure cluster autoscaling can add the correct accelerator node group when replicas need placement. Autoscaling that creates Pending Pods without adding useful nodes is only an alert generator.

One anti-pattern is using a Deployment for every ML container because Deployments are familiar. Teams fall into it because the YAML is common and the first test may appear to work, but a successful training script exits and then gets restarted. The better alternative is to decide whether completion is success or failure. If completion is success, choose a Job, workflow, or training operator; if continuous availability is success, choose serving infrastructure.

Another anti-pattern is installing an end-to-end ML platform before the workflow exists. Kubeflow, KServe, Ray, vLLM, GPU Operator, and Volcano are useful tools, but they solve different problems and add operational surfaces. A team with one weekly retraining job and one internal endpoint may need disciplined Jobs, Deployments, probes, quotas, and source control before it needs a full ML platform. The better alternative is to adopt the smallest abstraction that removes real pain, then add specialized tools when repeated workflows justify them.

A final anti-pattern is treating GPU sharing as a free utilization win. Time-slicing and partitioning can improve utilization for development or light inference, but they change isolation, performance predictability, and debugging. Production latency-sensitive inference may need whole GPUs or hardware partitioning, while notebooks may tolerate weaker isolation. The better alternative is to document which workloads can share, which require isolation, and which metrics prove the sharing policy is not hurting users.

## Decision Framework

Start the design by identifying the workload lifecycle. If the work finishes and produces artifacts, think Job, workflow, or training operator before you think Deployment. If the work serves synchronous requests, think Deployment, Service, probes, autoscaling, and rollout safety before you think batch scheduler. If the work needs many workers to start together, evaluate whether default scheduling can strand capacity; if partial placement wastes GPUs, a batch scheduler or training operator becomes part of the design rather than an optimization.

Next, identify the scarce resource and how Kubernetes will see it. CPU and memory are built into scheduling, but accelerators require a device plugin or vendor operator to advertise capacity. If the workload requests `nvidia.com/gpu`, verify that nodes expose allocatable capacity with that exact resource name. Then decide whether labels, affinity, taints, tolerations, quotas, and PriorityClass express the placement and fairness policy. This is where platform governance enters the design: a production inference namespace and an experimental notebook namespace should not compete with equal priority by accident.

Then decide how model serving will be operated. If privacy or latency requires self-hosting, the platform team owns driver maintenance, model-server readiness, GPU capacity planning, monitoring, rollout safety, and incident response. If an external API is acceptable, Kubernetes may still run the application, but the model capacity problem shifts to the provider contract. Neither option is universally better. The right answer depends on data sensitivity, traffic shape, latency budget, unit economics, and the team's ability to operate the stack.

Finally, decide which ecosystem tools earn their place. Choose Kubeflow when shared notebooks, pipelines, and multi-team workflow standardization are real requirements. Choose KServe when inference endpoints, rollout patterns, and model-server conventions are the problem. Choose Ray when distributed Python execution is the natural programming model. Choose vLLM when large language model serving efficiency is the bottleneck. Choose GPU Operator when repeatable GPU node operations matter, and choose Volcano when batch scheduling fairness or gang scheduling is the missing platform capability.

## Did You Know?

1. **GPU waste is a platform finance problem, not only a technical problem.** A single accelerator node can cost enough that low utilization becomes visible in cloud bills quickly, so scheduling policies, sharing strategies, and right-sized model serving directly affect business outcomes.

2. **Gang scheduling is not part of the default scheduler behavior most learners use first.** Kubernetes normally binds Pods independently, so distributed training teams often add schedulers such as Volcano when partial placement would strand GPUs and block useful work.

3. **A model server can be Running but still not ready to serve predictions.** Large models may need time to download weights, allocate GPU memory, compile kernels, or warm caches, which is why readiness and startup probes matter for inference reliability.

4. **Kubernetes won AI/ML infrastructure work through extensibility rather than original design.** Device plugins, custom controllers, operators, and specialized schedulers let the platform adapt to accelerators and ML workflows without requiring every feature in the core API.

## Common Mistakes

| Mistake | Why It Happens | How to Fix It |
|---------|----------------|---------------|
| Thinking Kubernetes automatically detects GPUs after installation. | The physical node may have an accelerator, but the kubelet does not advertise `nvidia.com/gpu` unless the device plugin or operator is working. | Install and verify the vendor device plugin or GPU Operator, then confirm node allocatable resources before deploying GPU workloads. |
| Using a Deployment for a training script that should finish. | Deployments are familiar, so teams forget that a successful training container exits and will be replaced. | Use a Job, workflow engine, or training operator for finite training, fine-tuning, and batch inference tasks. |
| Relying only on node labels for GPU workloads. | Labels steer placement, but they do not reserve accelerator capacity or tolerate protected GPU nodes. | Combine resource limits, selectors or affinity, and tolerations according to the node pool policy. |
| Scaling inference only on CPU utilization. | GPU memory, request queue depth, batching delay, or latency may saturate while CPU looks moderate. | Choose autoscaling signals that match the model server's real bottleneck and user-facing objective. |
| Ignoring model load time during rollouts. | The container process can be Running while weights are still loading and caches are still warming. | Use startup and readiness probes that reflect actual model-serving readiness before routing traffic. |
| Treating GPU time-slicing as equivalent to hardware isolation. | Shared GPUs can create noisy-neighbor effects and unpredictable latency for sensitive workloads. | Use whole GPUs or MIG where isolation matters, and reserve time-slicing for suitable light workloads. |
| Installing a full ML platform before defining the workflow problem. | The team inherits operational complexity before it has repeatable notebooks, pipelines, or multi-team needs. | Start with the smallest pattern that solves the workload, then adopt Kubeflow or KServe when their abstractions pay off. |
| Forgetting that cluster autoscaling must understand GPU node groups. | Pending GPU Pods may not cause useful scale-out if the autoscaler can only add CPU nodes. | Configure autoscaling for accelerator node pools and verify that Pending events trigger the expected capacity path. |

## Quiz

<details>
<summary>Your team deploys a real-time recommendation model as a Deployment with three replicas. During a traffic spike, the HorizontalPodAutoscaler creates more replicas, but the new Pods stay Pending with `Insufficient nvidia.com/gpu`. The web tier continues scaling normally. What should you investigate first?</summary>

Investigate whether GPU node groups and the device plugin expose enough allocatable accelerator capacity, and whether the autoscaler can add that kind of node. Pending means the Pod has not been scheduled, so image dependencies and runtime crashes are not the first issue. The event names the missing extended resource, which points to GPU capacity, existing allocations, device plugin health, or accelerator node pool scaling. This directly tests applying scheduling concepts to a real inference workload.
</details>

<details>
<summary>A data science team has a script that trains a model, writes checkpoints, uploads final weights, and then exits successfully. They ask you to run it as a Deployment so Kubernetes will keep it reliable. What should you recommend?</summary>

Recommend a Job, workflow engine, or training operator because the process has a clear completion condition and should not be restarted after success. A Deployment tries to maintain continuously running replicas, so it would restart the training after successful completion and could duplicate output or waste accelerator capacity. Reliability for this workload means restart-on-failure, checkpoint recovery, and clear completion status, not perpetual replacement of successful Pods.
</details>

<details>
<summary>A distributed training run needs several GPU workers to start together. Some workers are Running and holding GPUs, while the rest are Pending because the cluster has no remaining capacity. Which platform change best addresses the architecture problem?</summary>

Add gang scheduling through a batch scheduler or use a training operator that integrates with scheduling semantics for the worker group. The failure is partial placement of a distributed workload, not HTTP readiness or service discovery. Gang scheduling prevents a subset of workers from consuming GPUs when the full set cannot run, which improves utilization and makes queue behavior clearer. This is why specialized schedulers matter for some AI/ML workloads even when default Kubernetes works for ordinary services.
</details>

<details>
<summary>A compliance team requires that customer documents used in prompts must not leave company-controlled infrastructure, and product leadership requires low latency for an interactive workflow. Which serving design best fits those constraints?</summary>

Self-hosting the inference service close to the application can fit those privacy and latency constraints, but only if the organization accepts the operational responsibility. Keeping inference in controlled infrastructure helps address data handling requirements, and co-location can reduce network distance. The trade-off is that the team now owns accelerator nodes, model-server readiness, scaling, rollout safety, monitoring, and incident response. Kubernetes coordinates the platform, but it does not remove those responsibilities.
</details>

<details>
<summary>A platform team has one weekly fraud-model retraining job and one internal fraud inference endpoint. They are considering installing a large end-to-end ML platform immediately. What is the most defensible first step?</summary>

Start with the smallest pattern that solves the workload: a Job or workflow for retraining and a Deployment or serving-focused abstraction for inference. A weekly finite retraining task maps naturally to completion-oriented controllers, while the internal endpoint maps to serving infrastructure with probes and rollout safety. Kubeflow can be valuable later, but adopting it before the team needs notebooks, pipelines, or multi-team governance may add avoidable operational complexity. This answer evaluates tool fit instead of assuming every AI/ML workload needs the same platform.
</details>

<details>
<summary>A model-serving Pod is Running, but users receive errors for the first few minutes after every rollout. Logs show the container is downloading weights and warming the model during that time. What Kubernetes configuration should you change?</summary>

Add or adjust startup and readiness probes so traffic is withheld until the model server can actually answer requests. Running only means the container process exists; it does not prove the model is loaded, GPU memory is allocated, or caches are warm. Readiness should reflect prediction capability, and startup probes can give slow-loading models enough time before restart logic interferes. This is a design issue for serving reliability, not a reason to convert the endpoint into a batch workload.
</details>

<details>
<summary>A development cluster has one GPU shared by several lightweight notebook users. Whole-GPU allocation leaves most of the accelerator idle, but production workloads are not allowed on this cluster. Which sharing approach could improve utilization, and what trade-off must be documented?</summary>

GPU time-slicing may improve utilization for suitable development workloads, but the team must document that isolation and latency predictability are weaker than whole-GPU allocation. This can be acceptable for notebooks or lightweight experiments where occasional interference is tolerable. It is not the same as hardware isolation, so production latency-sensitive inference should use stronger isolation such as whole GPUs or appropriate hardware partitioning. The important comparison is not only utilization, but also who can tolerate noisy-neighbor behavior.
</details>

<details>
<summary>An inference Deployment requests `nvidia.com/gpu: 1`, and the cluster has a GPU node with allocatable capacity. The Pod is still Pending, and `kubectl describe node` shows the taint `accelerator=gpu:NoSchedule`. What is the most likely fix?</summary>

Add a matching toleration to the Pod, and optionally add node selection or affinity to make the intended GPU node pool explicit. A taint repels Pods unless they have a matching toleration, even when the Pod requests the right extended resource. The GPU request reserves the device, while the toleration permits scheduling onto the protected node. Selectors or affinity can make the hardware intent clearer for future operators who read the manifest.
</details>

## Hands-On Exercise: Simulate and Debug a GPU Scheduling Request

In this exercise, you will create a Pod that requests a GPU and then inspect the scheduling result. You do not need a physical GPU for the exercise. In a typical local or CPU-only cluster, the expected result is a Pending Pod with a scheduler event showing that no node has enough `nvidia.com/gpu` capacity. That expected failure is useful because it lets you practice the diagnostic path without needing accelerator hardware.

Before starting, define the common Kubernetes alias once if you want to use the shorter commands shown below. The full command `kubectl` works the same way, and the alias is only for convenience after the first explanation. Use a Kubernetes 1.35+ cluster if you want the event wording to match modern scheduling behavior closely, but focus on the reasoning rather than exact text.

```bash
alias k=kubectl
```

### Task 1: Create the GPU Pod manifest

Create a file named `gpu-pod.yaml` with a Pod that requests one NVIDIA GPU. The image and command are real, but the scheduler must find a node advertising `nvidia.com/gpu` before the container can run. The important field is the extended resource limit; without it, the Pod would not reserve an accelerator even if it happened to land on a GPU node.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-test-pod
spec:
  restartPolicy: Never
  containers:
    - name: cuda-container
      image: nvidia/cuda:12.4.1-base-ubuntu22.04
      command: ["nvidia-smi"]
      resources:
        limits:
          nvidia.com/gpu: 1
```

<details>
<summary>Solution notes for Task 1</summary>

The manifest should include `resources.limits.nvidia.com/gpu: 1` under the container. Keep the Pod name unchanged so the later commands match. If you are using a namespace for labs, apply the namespace consistently to every command rather than changing the manifest logic.
</details>

### Task 2: Apply the manifest

Apply the manifest to your current Kubernetes context. Use a disposable namespace if your environment requires one, but keep the Pod name unchanged so the later commands match. In a CPU-only cluster, applying the manifest should succeed because the API server accepts the resource request; scheduling is where the missing capacity becomes visible.

```bash
k apply -f gpu-pod.yaml
```

<details>
<summary>Solution notes for Task 2</summary>

Successful creation does not mean the Pod can run. It only means the API server stored the desired Pod. The scheduler still has to find a node with matching allocatable resources and placement rules.
</details>

### Task 3: Observe the Pod status

Check the Pod status and observe whether it starts. In a CPU-only cluster, it should remain Pending because no node advertises the extended GPU resource. If your cluster has working GPU capacity, the Pod may run and complete; in that case, the same commands still show how placement and runtime status differ.

```bash
k get pod gpu-test-pod
```

<details>
<summary>Solution notes for Task 3</summary>

Pending points to scheduling or admission constraints, not to application code inside the container. CrashLoopBackOff would mean the Pod was scheduled and the container started but failed. That distinction decides which evidence you inspect next.
</details>

### Task 4: Read scheduler events

Describe the Pod and read the scheduler events near the bottom of the output. Look for a `FailedScheduling` event that mentions `nvidia.com/gpu`, because that event connects the symptom to the missing schedulable resource. If the event mentions node affinity, taints, or quota instead, write down that constraint and follow the evidence rather than forcing the expected answer.

```bash
k describe pod gpu-test-pod
```

<details>
<summary>Solution notes for Task 4</summary>

The most useful line is usually in the Events section. A message such as `Insufficient nvidia.com/gpu` means the scheduler cannot find free allocatable GPU capacity. A taint-related message means the workload may need a toleration, while a selector-related message means the target node labels do not match.
</details>

### Task 5: Connect events to node capacity

Inspect node allocatable resources to connect the Pod event to cluster state. If no node lists `nvidia.com/gpu`, Kubernetes has no GPU capacity to allocate, even if a physical machine somewhere in the environment has accelerator hardware but no device plugin integration. This step turns a single Pod symptom into a platform diagnosis.

```bash
k describe nodes
```

<details>
<summary>Solution notes for Task 5</summary>

Look under each node's Allocatable section. If no GPU resource appears, investigate GPU nodes, drivers, container runtime integration, and the device plugin or GPU Operator. If a GPU resource appears but the Pod is still Pending, inspect taints, tolerations, selectors, affinity, quotas, and existing allocations.
</details>

### Task 6: Clean up and explain the fix path

Clean up the Pod after you have captured the result. Leaving a Pending Pod behind is harmless in a short lab, but cleanup is part of good cluster hygiene. After deleting it, explain what would need to change in a real GPU cluster for the Pod to run: available GPU nodes, working drivers, a healthy device plugin or GPU Operator, free allocatable capacity, and any required tolerations or node selection.

```bash
k delete pod gpu-test-pod
```

<details>
<summary>Solution notes for Task 6</summary>

The cleanup command removes the lab Pod and clears the Pending object from your cluster. Your explanation should connect the Pod request to the node's advertised capacity and placement policy. A complete answer mentions both the device resource and the surrounding scheduling controls, because GPU workloads often need both.
</details>

**Success Criteria:**

- [ ] You created `gpu-pod.yaml` with a container resource limit requesting `nvidia.com/gpu: 1`.
- [ ] You applied the manifest with `kubectl` or the `k` alias after defining the alias.
- [ ] You observed the Pod status and correctly distinguished Pending scheduling failure from a container runtime failure.
- [ ] You found a `FailedScheduling` event or equivalent scheduler message explaining insufficient GPU resources in a CPU-only cluster.
- [ ] You inspected node descriptions and connected missing allocatable `nvidia.com/gpu` capacity to the scheduling result.
- [ ] You can explain what would need to change in a real GPU cluster: GPU nodes, drivers, device plugin or GPU Operator, available capacity, and any required tolerations or node selection.
- [ ] You deleted the lab Pod after completing the investigation.

For extra practice, modify the manifest by adding a fake node selector such as `accelerator: nvidia` and apply it again. Compare the scheduler event with the previous result. The exact wording may differ by Kubernetes version, but the reasoning should be the same: the scheduler can only bind a Pod when resource requests, node labels, taints, tolerations, and available capacity all line up.

## Sources

- Kubernetes documentation: [Device Plugins](https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/device-plugins/)
- Kubernetes documentation: [Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- Kubernetes documentation: [Taints and Tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)
- Kubernetes documentation: [Assigning Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
- Kubernetes documentation: [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- Kubernetes documentation: [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- Kubernetes documentation: [Configure Liveness, Readiness, and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- Kubernetes documentation: [Resource Metrics Pipeline](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/)
- NVIDIA documentation: [GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/index.html)
- NVIDIA documentation: [Kubernetes Device Plugin](https://docs.nvidia.com/datacenter/cloud-native/kubernetes/latest/index.html)
- Kubeflow documentation: [Kubeflow Overview](https://www.kubeflow.org/docs/)
- KServe documentation: [KServe](https://kserve.github.io/website/latest/)
- Ray documentation: [Ray on Kubernetes](https://docs.ray.io/en/latest/cluster/kubernetes/index.html)
- vLLM documentation: [Deploying with Kubernetes](https://docs.vllm.ai/en/latest/serving/deploying_with_k8s.html)
- Volcano documentation: [Volcano Scheduler](https://volcano.sh/en/docs/)

## Next Module

[Module 3.9: WebAssembly and Cloud Native](../module-3.9-webassembly/) - The emerging technology that can complement containers for fast-starting, portable, and strongly sandboxed workloads.
