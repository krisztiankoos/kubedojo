---
title: "Part 3 Cumulative Quiz: Application Observability and Maintenance"
sidebar:
  order: 6
---

> **Complexity**: CKAD intermediate-to-advanced observability review
>
> **Estimated Time**: 70-90 minutes for study, practice, quiz, and cleanup
>
> **Prerequisites**: Completed Part 3 modules on probes, logs, debugging, resource monitoring, and API versions
>
> **Cluster Assumption**: Kubernetes 1.35 or later, with the Metrics Server installed for `kubectl top`
>
> **Command Note**: This module uses `k` as a short alias for `kubectl`; configure it with `alias k=kubectl` before starting.

## Learning Outcomes

By the end of this cumulative module, you will be able to **debug** unhealthy application workloads by comparing Pod status, Events, probe configuration, current logs, previous container logs, and Service endpoints.

You will be able to **design** probe strategies that separate slow startup, process health, and traffic readiness without causing unnecessary restarts or sending traffic to an unprepared container.

You will be able to **evaluate** observability evidence from `kubectl describe`, `k logs`, `k top`, and API discovery commands to choose the next highest-value troubleshooting action under CKAD exam pressure.

You will be able to **compare** common failure modes such as CrashLoopBackOff, NotReady Pods, empty Endpoints, missing metrics, and deprecated API manifests, then justify the command sequence that confirms or rejects each hypothesis.

You will be able to **implement** a complete diagnostic workflow for a realistic application incident and verify that the fix actually changed cluster state rather than only changing a YAML file.

## Why This Module Matters

A team deploys a payment API minutes before a busy sale begins, and the rollout looks green because the Deployment reports the desired number of replicas. A few minutes later, customer requests start timing out, the Service has fewer endpoints than expected, and one container is restarting so quickly that its current logs only show the latest boot banner. Nobody is helped by a memorized command if the operator cannot decide whether the next move is `describe`, `logs --previous`, `top`, endpoint inspection, or a probe change.

This is the point where CKAD observability stops being a list of commands and becomes a diagnostic craft. Kubernetes gives you many signals, but those signals are uneven: Events are short-lived, logs can belong to the wrong container instance, readiness affects traffic without restarting a container, and liveness can hide a slow startup problem by repeatedly killing the process. A capable application operator does not run every command randomly; they build a hypothesis, gather the cheapest evidence, and then change only the field that matches the failure.

Part 3 is cumulative because real incidents are cumulative. A failing application might involve a bad readiness path, a Service selector typo, a memory limit that forces restarts, and a manifest copied from an older API version. Each isolated topic from earlier modules is useful, but the exam and the workplace both reward learners who can combine them quickly. This module teaches that combination: read the symptom, narrow the system boundary, inspect the right evidence, make the smallest safe fix, and verify through Kubernetes state.

The stakes are practical rather than theoretical. A readiness probe that points to the wrong port can remove every Pod from a Service while the containers continue running. A liveness probe that fires before startup completes can turn a slow application into an endless CrashLoopBackOff. A missing previous log command can erase the only useful stack trace from the container instance that actually failed. These are small configuration errors, but in production they become outages because traffic, restarts, and evidence all move independently.

## Core Content

### 1. Observability Starts With Boundaries, Not Commands

The first mistake in Kubernetes troubleshooting is treating every symptom as a Pod problem. A user-facing outage crosses several boundaries: client request, Service, Endpoints or EndpointSlices, Pod readiness, container process, filesystem, resource pressure, and sometimes the API version used to create the object. The fastest diagnostic path is not the longest command list; it is the shortest path that identifies which boundary is broken.

Use this mental model before touching YAML. If a Service has no endpoints, the immediate question is not whether nginx is installed correctly. The immediate question is whether the Service selector matches Ready Pods, because only Ready matching Pods should receive traffic. If a Pod is Running but not Ready, the immediate question is whether readiness is failing because the application is not accepting traffic or because the probe is aimed at the wrong place. If a Pod is restarting, current logs may be misleading because they show the new container instance, while `--previous` shows the one that died.

```ascii
+-------------------+      +-------------------+      +-------------------+
| External symptom  | ---> | Kubernetes route  | ---> | Container reality |
| timeout or 503    |      | Service endpoints |      | process and logs  |
+-------------------+      +-------------------+      +-------------------+
          |                          |                          |
          v                          v                          v
+-------------------+      +-------------------+      +-------------------+
| Check Service     |      | Check readiness   |      | Check previous    |
| selector and port |      | probe and Events  |      | logs and restarts |
+-------------------+      +-------------------+      +-------------------+
```

The diagram is deliberately simple because the first pass through an incident should be simple. You are trying to locate the broken boundary before you dive into details. When the boundary is Service-to-Pod, inspect selectors and endpoints. When the boundary is kubelet-to-container, inspect probes, restart counts, Events, and logs. When the boundary is scheduler-to-node resources, inspect requests, limits, node pressure, and metrics.

A useful CKAD habit is to ask, “What would have to be true for this symptom to appear?” A Service with no endpoints requires either no matching Pods, matching Pods that are not Ready, or a selector that points at the wrong labels. A CrashLoopBackOff requires a container that exits, is killed by a probe, or cannot start successfully. A missing `kubectl top` result requires either missing Metrics Server, a scrape delay, or an object that is not currently emitting metrics. Each symptom has a small set of likely causes, and that set determines the next command.

**Active learning prompt**: Before reading further, imagine a Pod that says `Running` but receives no traffic from its Service. Write down two different reasons this can happen. One reason should involve the Pod itself, and one reason should involve the Service object that routes to it.

### 2. Probe Strategy: Startup, Liveness, and Readiness Have Different Jobs

Probes are often taught as three similar YAML blocks, but their meanings are different enough that mixing them up creates outages. A startup probe protects slow initialization by delaying liveness and readiness checks until the application has had enough time to boot. A liveness probe answers, “Should kubelet restart this container because it is broken?” A readiness probe answers, “Should this Pod receive traffic right now?” Those questions point to different risks, so the probe configuration should reflect different failure behavior.

Readiness should usually be more conservative than liveness. If an application temporarily loses a database connection, it might be correct to remove the Pod from Service endpoints while keeping the process alive so it can reconnect. If liveness checks the same dependency too aggressively, kubelet may restart a process that would have recovered on its own. That creates extra load during an outage and can make the incident worse.

Startup probes are especially important for applications that perform migrations, warm caches, load models, or initialize large dependency graphs. Without a startup probe, liveness begins after `initialDelaySeconds`, and a delay that works on a developer laptop may fail on a loaded node. A startup probe gives the application a longer boot window while still allowing liveness to protect it after startup succeeds. This is not just a convenience; it changes the failure semantics from “restart during slow boot” to “restart after startup has failed beyond an acceptable threshold.”

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: observed-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: observed-api
  template:
    metadata:
      labels:
        app: observed-api
    spec:
      containers:
      - name: api
        image: nginx:1.27
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
          timeoutSeconds: 2
        readinessProbe:
          httpGet:
            path: /
            port: 80
          periodSeconds: 5
          timeoutSeconds: 2
```

This Deployment is intentionally modest because the structure matters more than the image. The startup probe allows up to five minutes of startup attempts before kubelet treats startup as failed. After startup succeeds, liveness checks every ten seconds and can restart the container if the HTTP endpoint stops responding. Readiness checks more frequently because Service routing benefits from faster traffic removal and restoration.

The probe you choose should match the failure you want Kubernetes to handle. HTTP probes are natural when the application exposes a health endpoint. TCP probes are useful when an open socket is a good readiness signal, although they cannot verify application-level correctness. Exec probes are useful when health depends on local files or commands inside the container, but they can be expensive and brittle if they run complex shell logic. A probe is part of your control plane contract with kubelet, so keep it narrow, fast, and meaningful.

| Probe Type | Main Question | Typical Action When Failing | Common CKAD Risk |
|---|---|---|---|
| startupProbe | Has the application completed initialization yet? | Delays other probes, then restarts if startup never succeeds | Missing it for slow apps causes liveness restarts during boot |
| livenessProbe | Is the container broken enough to restart? | Restarts the container after failure threshold is reached | Checking external dependencies can trigger restart storms |
| readinessProbe | Should this Pod receive Service traffic? | Removes or adds Pod endpoints without restart | Wrong path or port makes healthy Pods unreachable |
| exec probe | Does a command inside the container succeed? | Depends on probe field using it | Shell assumptions fail in minimal images |
| httpGet probe | Does an HTTP endpoint return success? | Depends on probe field using it | Path, named port, or scheme mismatch causes false failure |

A strong probe strategy treats restarts as expensive. Restarting is useful when the process is wedged, deadlocked, or unable to recover. Restarting is harmful when the application is simply waiting for a dependency, handling backpressure, or warming up slowly. Readiness is the safer signal for temporary inability to serve traffic because it changes routing without destroying process state.

**Active learning prompt**: Suppose an API cannot serve requests while its database is unavailable, but it automatically reconnects when the database returns. Would you put the database check in liveness, readiness, both, or neither? Justify the operational consequence of your choice before you compare it with the quiz scenarios later.

### 3. Worked Example: Debug a Pod That Runs but Never Receives Traffic

This worked example shows the diagnostic sequence before you are asked to solve a similar problem independently. The scenario is common: a Deployment appears to have Pods, the containers are not crashing, but requests through the Service fail. The goal is to avoid jumping straight into the container when the routing layer may already explain the problem.

First, create a small broken workload that has a label mismatch between the Pod template and the Service selector. This is runnable in a practice namespace, and it uses only standard Kubernetes resources. The Deployment creates Pods labeled `app: checkout-api`, while the Service selects `app: checkout`, so the Service has no matching endpoints even though Pods exist.

```bash
k create namespace observability-lab
k -n observability-lab create deployment checkout-api --image=nginx:1.27 --replicas=2
k -n observability-lab label deployment checkout-api tier=frontend
k -n observability-lab expose deployment checkout-api --name=checkout-svc --port=80 --target-port=80
k -n observability-lab patch svc checkout-svc -p '{"spec":{"selector":{"app":"checkout"}}}'
```

Now inspect the symptom from the Service boundary. The first command confirms the Service selector, and the second command checks whether Kubernetes found any Ready Pods that match it. Depending on your cluster version and display settings, `k get endpoints` may show `<none>` for the Service, while EndpointSlices provide the newer representation of the same routing data.

```bash
k -n observability-lab describe svc checkout-svc
k -n observability-lab get endpoints checkout-svc
k -n observability-lab get endpointslice -l kubernetes.io/service-name=checkout-svc
```

The expected evidence points away from container logs. The containers are probably fine, because the Service cannot even select them. The next command compares Pod labels with the Service selector. This is a higher-value move than running `k logs` because the failure boundary is already between Service and Pod selection.

```bash
k -n observability-lab get pods --show-labels
k -n observability-lab get svc checkout-svc -o jsonpath='{.spec.selector}{"\n"}'
```

A focused fix changes either the Service selector or the Pod labels. In most real environments, you should understand ownership before patching labels because Deployments recreate Pods from their templates. For this lab, patch the Service selector to match the Deployment label that already exists. Then verify that endpoints appear instead of assuming the patch worked.

```bash
k -n observability-lab patch svc checkout-svc -p '{"spec":{"selector":{"app":"checkout-api"}}}'
k -n observability-lab get endpoints checkout-svc
k -n observability-lab get endpointslice -l kubernetes.io/service-name=checkout-svc
```

The lesson is that observability is not only about looking inside containers. Kubernetes routing is itself observable, and its state often explains an outage earlier than application logs do. A Service does not send traffic to all Pods in a namespace; it sends traffic to Ready Pods whose labels match the selector and whose ports match the target. If the selector is wrong, the application can be perfectly healthy and still unreachable through the Service.

A similar pattern appears with readiness probes. If labels match but Pods are not Ready, the Service may still have no usable endpoints. In that case the next evidence is `k describe pod`, especially the readiness probe section and the Events near the bottom. The correct fix might be changing a probe path, exposing the right container port, or repairing the application health endpoint. The boundary-first method still holds: prove whether routing, readiness, or process health is responsible before editing YAML.

```bash
k -n observability-lab get pods
k -n observability-lab describe pod -l app=checkout-api
k -n observability-lab logs -l app=checkout-api --tail=40
```

This worked example also shows why verification must observe cluster state, not only command success. A successful `patch` command means the API accepted the change. It does not mean traffic now has endpoints, probes now pass, or the application now responds correctly. Always follow a fix with the state that the fix was supposed to change.

### 4. CrashLoopBackOff: Preserve Evidence Before It Disappears

CrashLoopBackOff is not a root cause; it is Kubernetes telling you that a container repeatedly started and then stopped. The cause may be an application exception, a missing file, bad command arguments, a failed probe, an image issue that appears before the loop begins, or resource pressure. Your job is to separate “the process exited” from “kubelet killed the process” and then inspect the evidence from the container instance that failed.

The most important habit is checking previous logs early. Current logs belong to the currently running or recently started container instance. If the container starts, prints a boot message, crashes, and restarts, current logs might not include the stack trace from the previous instance. The `--previous` flag asks Kubernetes for the logs from the last terminated container instance, which is often the only place the root cause appears.

```bash
k get pod crashing-pod
k describe pod crashing-pod
k logs crashing-pod --previous --tail=80
k logs crashing-pod --tail=80
```

Use `describe` to connect logs with lifecycle details. The `Last State` section can show exit codes, reasons, and timestamps. Events can show probe failures, image pull problems, OOM kills, failed mounts, and scheduling problems. If Events mention liveness probe failures before restarts, the application may not be exiting by itself; kubelet may be killing it because the configured health check fails.

```bash
k describe pod crashing-pod | sed -n '/Containers:/,/Conditions:/p'
k describe pod crashing-pod | sed -n '/Events:/,$p'
```

When a Pod has more than one container, always specify the container name. Sidecars and init containers produce different evidence, and `k logs pod-name` may choose a default that is not the failing container. In a CKAD setting, this is a frequent source of wasted time because the command succeeds while answering the wrong question.

```bash
k get pod multi-app -o jsonpath='{.spec.containers[*].name}{"\n"}'
k logs multi-app -c backend --previous --tail=60
k logs multi-app -c frontend --tail=60
```

Resource pressure adds another layer. If the container was OOMKilled, logs may be incomplete because the kernel terminated the process. `kubectl top` helps identify current CPU and memory usage, but it does not replace lifecycle state because top shows live metrics rather than the exact reason for a previous termination. Use both signals together: lifecycle tells you what happened, metrics tells you whether the condition is still present.

```bash
k top pod crashing-pod
k top pod crashing-pod --containers
k describe pod crashing-pod | grep -A8 "Last State"
```

The following decision flow is a practical way to avoid command wandering during CrashLoopBackOff. It starts with evidence that is most likely to disappear or be misunderstood, then moves toward configuration. You do not need to memorize the diagram; practice the habit of asking whether the container died by itself, kubelet killed it, or the environment prevented it from running correctly.

```ascii
+----------------------+
| Pod is CrashLooping  |
+----------+-----------+
           |
           v
+----------------------+
| Read previous logs   |
| k logs --previous    |
+----------+-----------+
           |
           v
+----------------------+
| Describe lifecycle   |
| exit code + Events   |
+----------+-----------+
           |
           v
+----------------------+        +----------------------+
| Probe failure shown? | -----> | Inspect probe path, |
+----------+-----------+  yes   | port, delay, timing |
           | no                 +----------------------+
           v
+----------------------+        +----------------------+
| OOMKilled or limits? | -----> | Compare top metrics |
+----------+-----------+  yes   | with requests/limits|
           | no                 +----------------------+
           v
+----------------------+
| Inspect command, env,|
| mounts, image, args  |
+----------------------+
```

A senior troubleshooting stance is to change one thing at a time and verify the specific expected result. If liveness is too aggressive, increasing `initialDelaySeconds` should reduce probe-related restarts, not necessarily fix an application exception. If memory limits are too low, changing a probe path will not fix OOMKilled. If a command path is wrong, resource metrics may look normal because the process exits before doing real work. Evidence narrows the fix.

### 5. Logs, Metrics, and API Discovery Under Exam Pressure

CKAD tasks often reward speed, but speed should come from practiced command selection rather than from guessing. Logs answer “what did the process emit?” Metrics answer “what resources are objects consuming now?” API discovery answers “what schema does this cluster accept?” These tools are complementary, and confusing them leads to shallow troubleshooting.

Logs are strongest for application behavior and container output. Use `--tail` to keep output focused, `-f` to follow active logs, `--previous` for restarted containers, and `-c` for a specific container. Use label selectors when the question is about all replicas of a Deployment, but remember that combined logs from multiple Pods can interleave lines and hide sequence. For exact diagnosis, narrow the evidence when needed.

```bash
k logs deploy/checkout-api --tail=100
k logs deploy/checkout-api --all-containers --tail=100
k logs pod/checkout-api-abc123 -c api --previous --tail=80
k logs -l app=checkout-api --since=10m --tail=200
```

Metrics are strongest for current resource usage and relative comparison. They depend on Metrics Server, so an error from `k top` might be an observability-system problem rather than an application problem. Sorting helps under exam pressure when you need the highest CPU or memory consumer. Use `--containers` when a multi-container Pod hides which container is responsible.

```bash
k top pods -A --sort-by=memory
k top pods -n observability-lab --sort-by=cpu
k top pod checkout-api-abc123 --containers
k top nodes
```

API discovery prevents stale-manifest mistakes. Kubernetes 1.35 accepts current stable APIs for common CKAD resources such as `networking.k8s.io/v1` Ingress, `batch/v1` CronJob, and `networking.k8s.io/v1` NetworkPolicy. Instead of relying on memory during an exam, use `k explain` or `k api-resources` to confirm the group and version that the cluster serves.

```bash
k explain ingress | grep VERSION
k explain cronjob | grep VERSION
k explain networkpolicy | grep VERSION
k api-resources | grep -E 'ingresses|cronjobs|networkpolicies'
```

The subtle point is that discovery commands teach you what the API server knows, not whether your particular manifest is semantically correct. A CronJob might use `batch/v1` and still fail because field names are wrong. An Ingress might use the right API version and still route incorrectly because `pathType` or backend service names are wrong. Discovery is the first gate, not the full validation story.

A useful pressure-tested sequence is symptom, scope, evidence, fix, verification. Symptom is what the user or task reports. Scope identifies whether the object boundary is Service, Pod, container, metrics, or manifest API. Evidence uses the smallest command that tests that boundary. Fix changes one relevant thing. Verification observes the state that should change as a result. This sequence is slower than guessing once, but faster than guessing three times.

```ascii
+----------+     +-------+     +----------+     +------+     +-------------+
| Symptom  | --> | Scope | --> | Evidence | --> | Fix  | --> | Verification|
+----------+     +-------+     +----------+     +------+     +-------------+
| 503      |     | svc   |     | endpoints|     | label|     | endpoints   |
| restart  |     | pod   |     | previous |     | probe|     | restarts    |
| high mem |     | node  |     | top      |     | limit|     | top + state |
| bad YAML |     | api   |     | explain  |     | field|     | apply dryrun|
+----------+     +-------+     +----------+     +------+     +-------------+
```

**Active learning prompt**: Your team says, “The Deployment is broken because the Service returns 503.” Decide which command you would run first and why. Then decide what command you would run second if the first command showed empty endpoints.

### 6. From Quiz Review to Operational Practice

This module still includes a cumulative quiz, but the quiz is no longer the first teaching event. You have now reviewed the diagnostic model, probe semantics, a worked Service example, CrashLoopBackOff evidence, and the distinction among logs, metrics, and API discovery. The quiz scenarios below ask you to apply that model rather than recall isolated commands.

Before taking the quiz, set a realistic constraint. Give yourself enough time to reason, but do not let yourself browse randomly through every previous module. The CKAD exam expects you to use documentation, but it also expects a strong command-line workflow. In practice, your fastest answers will come from recognizing the failure boundary, not from memorizing every flag.

If you miss a question, classify the miss. Was the problem that you chose the wrong boundary, forgot a command flag, changed the wrong object, or failed to verify? That classification matters because the remediation is different. A wrong boundary requires more scenario practice. A forgotten flag requires command repetition. A missing verification step requires a stricter habit after every fix.

## Did You Know?

1. Readiness failures do not restart a container; they remove the Pod from Service endpoints until the readiness condition becomes true again.

2. `k logs --previous` only works when Kubernetes still has a terminated container instance to read, so repeated restarts and cleanup can make this evidence disappear.

3. EndpointSlices are the scalable successor to the older Endpoints object, but `k get endpoints` remains useful for quick CKAD-style checks on small Services.

4. `kubectl top` reports metrics collected through the resource metrics pipeline, so it is a live usage view rather than a historical incident recorder.

## Common Mistakes

| Mistake | Why It Hurts | Better Practice |
|---|---|---|
| Checking application logs before checking whether a Service has endpoints | The container might be healthy while routing is broken, so logs can waste time and distract from selector or readiness evidence | Start at the boundary implied by the symptom, then move inward only when routing state is plausible |
| Using the same dependency-heavy endpoint for liveness and readiness | A temporary dependency outage can trigger restarts instead of only removing traffic from the Pod | Keep liveness focused on process health and use readiness for traffic-serving ability |
| Forgetting `--previous` during CrashLoopBackOff | Current logs may show only the latest restart and miss the failing container instance | Capture previous logs early, then connect them to exit codes and Events |
| Omitting `-c` in multi-container Pods | Kubernetes may show logs for the wrong container or ask for a container choice during time pressure | List container names and inspect the container that matches the symptom |
| Treating `kubectl top` as a root-cause tool | Metrics show current usage, not the complete history or reason for termination | Combine metrics with `describe`, Events, restart counts, and termination reasons |
| Patching a Service selector without verifying endpoints | The API can accept a patch that still selects no Ready Pods | Verify with Endpoints or EndpointSlices after every routing change |
| Copying old manifests without API discovery | Deprecated or removed API versions fail before workload behavior can even be tested | Confirm current versions with `k explain` or `k api-resources` in the target cluster |
| Increasing probe delays without understanding the failure | Timing changes can hide an application bug or prolong an outage | Read Events and logs first, then adjust probe type, path, port, threshold, or delay intentionally |

## Quiz

### Question 1: Service Routes to No Pods

Your team exposes a Deployment named `orders-api` through a Service named `orders-svc`. The Deployment has two Running Pods, but requests through the Service fail with connection errors. `k get endpoints orders-svc` shows no addresses. What should you inspect first, and what is a focused fix if the Service selector does not match the Pod labels?

<details>
<summary>Answer</summary>

Start with the routing boundary because the Service has no endpoints. Inspect the Service selector and the Pod labels, then patch either the Service selector or the workload labels so they match the intended ownership model.

```bash
k describe svc orders-svc
k get pods --show-labels
k get svc orders-svc -o jsonpath='{.spec.selector}{"\n"}'

# Example focused fix when Pods are labeled app=orders-api:
k patch svc orders-svc -p '{"spec":{"selector":{"app":"orders-api"}}}'

# Verify the state that should change:
k get endpoints orders-svc
k get endpointslice -l kubernetes.io/service-name=orders-svc
```

The key reasoning is that logs are not the first evidence when the Service already proves it has no endpoints. The application can be healthy and still unreachable when labels or readiness prevent endpoint registration.

</details>

### Question 2: Running Pod Is Not Ready

A Pod named `catalog-0` is Running but never becomes Ready. The readiness probe is configured as an HTTP GET on `/ready` port `8080`, but the application listens on port `8000`. What commands would you use to confirm the probe failure, and how would you correct the configuration?

<details>
<summary>Answer</summary>

Confirm the readiness failure through `describe`, then inspect the container port or application behavior to verify the mismatch. Correct the Pod template in the controller that owns the Pod, because editing a live Pod directly is usually not durable.

```bash
k describe pod catalog-0 | sed -n '/Readiness:/,/Environment:/p'
k describe pod catalog-0 | sed -n '/Events:/,$p'
k get pod catalog-0 -o jsonpath='{.spec.containers[*].ports}{"\n"}'

# If this Pod is owned by a Deployment named catalog:
k patch deployment catalog --type='json' \
  -p='[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/port","value":8000}]'

k rollout status deployment catalog
k get pods -l app=catalog
k get endpoints catalog
```

The correction should be verified through readiness and endpoints, not only through patch success. A Ready Pod should appear in the relevant Service endpoints if labels and ports also match.

</details>

### Question 3: Slow Startup Causes Restart Loop

A Java application takes three minutes to initialize on a busy node. The Deployment has a liveness probe with `initialDelaySeconds: 20`, `periodSeconds: 10`, and `failureThreshold: 3`. The Pods enter CrashLoopBackOff even though the application works locally. How would you redesign the probes so Kubernetes does not kill the application during normal startup?

<details>
<summary>Answer</summary>

Add a startup probe that allows enough time for initialization, then keep liveness for post-startup process health and readiness for traffic serving. The startup probe disables liveness and readiness until startup succeeds, which prevents normal slow boot from becoming a restart loop.

```bash
k patch deployment java-api --type='json' -p='[
  {
    "op": "add",
    "path": "/spec/template/spec/containers/0/startupProbe",
    "value": {
      "httpGet": {
        "path": "/healthz",
        "port": 8080
      },
      "periodSeconds": 10,
      "failureThreshold": 30
    }
  },
  {
    "op": "replace",
    "path": "/spec/template/spec/containers/0/livenessProbe/httpGet/path",
    "value": "/healthz"
  },
  {
    "op": "replace",
    "path": "/spec/template/spec/containers/0/readinessProbe/httpGet/path",
    "value": "/ready"
  }
]'

k rollout status deployment java-api
k describe pod -l app=java-api | sed -n '/Startup:/,/Environment:/p'
```

The important design choice is not simply increasing liveness delay. A startup probe models the separate startup phase, while readiness can still keep the Pod out of traffic until it is truly able to serve.

</details>

### Question 4: CrashLoopBackOff With Missing Stack Trace

A Pod named `billing-worker` is in CrashLoopBackOff. Running `k logs billing-worker` only shows the newest startup message, and the useful exception is not visible. What evidence should you collect next, and how do you decide whether the process exited or kubelet killed it?

<details>
<summary>Answer</summary>

Collect previous logs and lifecycle details before the evidence is replaced by another restart. Use `describe` to inspect the terminated state, exit code, reason, and Events, then compare that with logs.

```bash
k logs billing-worker --previous --tail=100
k describe pod billing-worker | sed -n '/Last State:/,/Ready:/p'
k describe pod billing-worker | sed -n '/Events:/,$p'
```

If previous logs show an application exception and `Last State` shows a nonzero exit code, the process likely exited by itself. If Events show repeated liveness probe failures followed by restarts, kubelet likely killed the container because the probe failed. If the reason is `OOMKilled`, resource pressure is central and current logs may be incomplete.

</details>

### Question 5: Multi-Container Pod Hides the Failing Container

A Pod named `web-stack` has containers named `frontend`, `backend`, and `log-agent`. The Pod restarts repeatedly, but the frontend logs look normal. How do you identify which container is failing and retrieve the relevant logs?

<details>
<summary>Answer</summary>

List container names and inspect container statuses from `describe` or JSON output, then request logs for the container with restarts or a terminated previous state. Do not rely on the default container selection.

```bash
k get pod web-stack -o jsonpath='{.spec.containers[*].name}{"\n"}'
k describe pod web-stack | sed -n '/Containers:/,/Conditions:/p'

k logs web-stack -c backend --previous --tail=100
k logs web-stack -c backend --tail=100
```

If `backend` shows restarts and previous logs contain the exception, that is the evidence to use for the fix. The `frontend` logs can be correct and still irrelevant because a Pod-level symptom can be caused by any container in the Pod.

</details>

### Question 6: High Memory During an Incident

An API Deployment is responding slowly. One Pod is suspected of using much more memory than the others, but it has not restarted yet. What commands help you compare usage across the namespace and then inspect container-level usage for the suspicious Pod?

<details>
<summary>Answer</summary>

Use `kubectl top` for current resource comparison, sorted by memory, then inspect the suspicious Pod by container if it has more than one container.

```bash
k top pods -n production --sort-by=memory
k top pod suspicious-pod -n production --containers
k describe pod suspicious-pod -n production | sed -n '/Limits:/,/Requests:/p'
```

Metrics help identify the live resource pattern, but they do not prove the historical cause of a previous restart. If the Pod later restarts, pair this with `describe` and previous logs to check for `OOMKilled` or application-level failure.

</details>

### Question 7: Manifest Uses a Deprecated API

A teammate gives you an Ingress manifest that starts with `apiVersion: extensions/v1beta1`, and `k apply` fails on a Kubernetes 1.35 cluster. How do you confirm the supported API version and avoid guessing the replacement shape?

<details>
<summary>Answer</summary>

Use API discovery against the target cluster, then inspect the resource schema. For Ingress in modern Kubernetes, the stable API is `networking.k8s.io/v1`, and the manifest must use the current field structure.

```bash
k explain ingress | grep VERSION
k explain ingress.spec
k api-resources | grep ingress
```

A correct fix changes more than the version string if the old manifest used obsolete fields. For example, `pathType` is required in modern Ingress paths, and backend service references use the current `service.name` and `service.port` structure.

</details>

### Question 8: Probe Fix Without Verification

You patch a Deployment to change its readiness path from `/health` to `/ready`. The command succeeds, so a teammate says the incident is fixed. What verification sequence would you run before agreeing?

<details>
<summary>Answer</summary>

Verify rollout, Pod readiness, Events, and Service endpoints because those are the states the readiness fix should affect. Patch success only proves that the API accepted the change.

```bash
k rollout status deployment checkout-api
k get pods -l app=checkout-api
k describe pod -l app=checkout-api | sed -n '/Readiness:/,/Environment:/p'
k describe pod -l app=checkout-api | sed -n '/Events:/,$p'
k get endpoints checkout-svc
```

The incident is fixed only if the new Pods become Ready and the Service has the expected endpoints. If readiness still fails, the path change did not address the actual boundary or another issue remains.

</details>

## Hands-On Exercise

In this exercise you will build and repair a small observability incident in a practice namespace. The goal is not to memorize the exact YAML; the goal is to practice moving from symptom to boundary, from boundary to evidence, and from evidence to the smallest useful fix. Run this in a disposable cluster or namespace because the exercise intentionally creates broken routing and probe behavior.

### Exercise Setup

Create a namespace and deploy a small application with two intentional problems. The Service selector will not match the Pod labels, and the readiness probe will point at the wrong port. These two failures let you practice separating Service routing from Pod readiness.

```bash
k create namespace part3-observability
```

```bash
cat << 'EOF' | k apply -n part3-observability -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inventory-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: inventory-api
  template:
    metadata:
      labels:
        app: inventory-api
        tier: backend
    spec:
      containers:
      - name: nginx
        image: nginx:1.27
        ports:
        - containerPort: 80
        readinessProbe:
          httpGet:
            path: /
            port: 8080
          periodSeconds: 5
          timeoutSeconds: 2
        livenessProbe:
          httpGet:
            path: /
            port: 80
          periodSeconds: 10
          timeoutSeconds: 2
EOF
```

```bash
cat << 'EOF' | k apply -n part3-observability -f -
apiVersion: v1
kind: Service
metadata:
  name: inventory-svc
spec:
  selector:
    app: inventory
  ports:
  - port: 80
    targetPort: 80
EOF
```

### Step 1: Observe the Routing Boundary

Start with the Service because the user-facing symptom is that traffic through the Service does not work. Inspect the Service selector, Pod labels, Endpoints, and EndpointSlices. Do not change anything until you can explain whether the Service has matching Pods.

```bash
k -n part3-observability describe svc inventory-svc
k -n part3-observability get pods --show-labels
k -n part3-observability get endpoints inventory-svc
k -n part3-observability get endpointslice -l kubernetes.io/service-name=inventory-svc
```

Expected reasoning: the Service selector uses `app: inventory`, while the Pods use `app: inventory-api`. Even if the Pods were Ready, this Service would not select them. This means the first fix should address labels or selector logic before you spend time on logs.

### Step 2: Fix the Service Selector and Verify the New Symptom

Patch the Service selector to match the Pods. Then verify endpoints again. You may still see no ready addresses if readiness is failing, which is useful because it reveals the next boundary.

```bash
k -n part3-observability patch svc inventory-svc -p '{"spec":{"selector":{"app":"inventory-api"}}}'
k -n part3-observability get endpoints inventory-svc
k -n part3-observability get pods
```

If the endpoints are still empty or not usable, do not undo the selector fix. The selector problem was real, but it was not the only problem. Multi-cause incidents are common, and the discipline is to keep confirmed fixes while continuing to inspect the next failing boundary.

### Step 3: Inspect Readiness Evidence

Now inspect one of the Pods and read the readiness probe section plus Events. The readiness probe points to port `8080`, but nginx listens on port `80` in this manifest. This is exactly the kind of error that leaves containers running while keeping them out of Service traffic.

```bash
POD_NAME="$(k -n part3-observability get pod -l app=inventory-api -o jsonpath='{.items[0].metadata.name}')"
k -n part3-observability describe pod "$POD_NAME" | sed -n '/Readiness:/,/Environment:/p'
k -n part3-observability describe pod "$POD_NAME" | sed -n '/Events:/,$p'
```

Expected reasoning: readiness is the traffic gate, so a wrong readiness port explains why Pods do not become Ready. Liveness uses port `80`, so the containers may avoid restarts while still failing readiness. That difference is the teaching point: liveness and readiness do not have the same operational meaning.

### Step 4: Fix the Readiness Probe in the Deployment Template

Patch the Deployment template so new Pods use the correct readiness port. Because Pods managed by Deployments are recreated from the template, changing only a live Pod would not be durable. After the patch, wait for rollout and verify Pod readiness.

```bash
k -n part3-observability patch deployment inventory-api --type='json' \
  -p='[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/port","value":80}]'

k -n part3-observability rollout status deployment inventory-api
k -n part3-observability get pods -l app=inventory-api
k -n part3-observability get endpoints inventory-svc
```

Expected reasoning: the fix should produce Ready Pods and Service endpoints. If rollout completes but endpoints remain empty, return to selector, labels, readiness Events, and port configuration. The verification state must match the intended effect of the fix.

### Step 5: Add a CrashLoopBackOff Evidence Drill

Create a Pod that exits immediately so you can practice previous logs and lifecycle inspection. This is a controlled failure, not an application you are trying to keep running. The important behavior is that the current state changes while the previous container logs preserve the failure message.

```bash
cat << 'EOF' | k apply -n part3-observability -f -
apiVersion: v1
kind: Pod
metadata:
  name: failing-worker
spec:
  restartPolicy: Always
  containers:
  - name: worker
    image: busybox:1.36
    command:
    - sh
    - -c
    - echo "starting worker"; echo "fatal: missing required queue name"; exit 2
EOF
```

Wait briefly, then inspect the Pod status, previous logs, and lifecycle state. If the first `--previous` attempt is too early, wait a few seconds and run it again. The aim is to catch the terminated instance rather than only the newest start.

```bash
k -n part3-observability get pod failing-worker
k -n part3-observability logs failing-worker --previous --tail=20
k -n part3-observability describe pod failing-worker | sed -n '/Last State:/,/Ready:/p'
k -n part3-observability describe pod failing-worker | sed -n '/Events:/,$p'
```

Expected reasoning: the previous logs show the application-level failure, and the lifecycle section shows a nonzero exit code. This is different from a liveness-probe kill or an OOM kill, so the next fix would target command arguments, environment, or application configuration rather than probe timing.

### Step 6: Check Metrics and API Discovery

If your cluster has Metrics Server, compare resource usage in the namespace. If it does not, note the failure as an observability-system limitation rather than an application diagnosis. Then confirm API versions for common resources using discovery commands.

```bash
k top pods -n part3-observability --sort-by=memory
k top pod -n part3-observability --containers
k explain ingress | grep VERSION
k explain cronjob | grep VERSION
k explain networkpolicy | grep VERSION
```

Expected reasoning: metrics are useful only when the metrics pipeline is available and current. API discovery is useful for confirming what the target cluster accepts. Neither replaces `describe`, Events, logs, endpoints, or rollout verification; they answer different questions.

### Success Criteria

- [ ] You can explain why the initial Service had no endpoints before inspecting application logs.
- [ ] You patched the Service selector and verified the endpoint state after the patch.
- [ ] You identified the readiness probe port mismatch from `describe` output and Events.
- [ ] You patched the Deployment template rather than treating a managed Pod as the durable source of truth.
- [ ] You verified that Pods became Ready and that the Service gained endpoints after the readiness fix.
- [ ] You captured previous logs from the intentionally failing Pod and connected them to the exit code.
- [ ] You used `kubectl top` appropriately or recognized that Metrics Server was unavailable.
- [ ] You confirmed at least one current API version with `k explain` or `k api-resources`.
- [ ] You can describe the difference between fixing routing, fixing readiness, and fixing a crashing process.

### Cleanup

Remove the practice namespace after you complete the exercise. Deleting the namespace removes the Deployment, Service, Pods, and intentionally failing worker created by this lab.

```bash
k delete namespace part3-observability
```

## Next Module

[Part 4: Application Environment, Configuration and Security](/k8s/ckad/part4-environment/module-4.1-configmaps/) — move from observing running applications to configuring environment data, Secrets, and security settings that shape how applications behave in the cluster.
