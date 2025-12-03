# Part 0 Cumulative Quiz: Environment & Strategy

> **Time Limit**: 10 minutes (simulating exam pressure)
>
> **Passing Score**: 80% (8/10 questions)

This quiz tests your mastery of:
- CKAD exam structure and domains
- Developer workflow optimization
- kubectl shortcuts and aliases
- Exam strategy

---

## Instructions

1. Try each question without looking at answers
2. Time yourself—speed matters for CKAD
3. Check answers after completing all questions

---

## Questions

### Question 1: Exam Domains
**[30 seconds]**

What is the largest weighted domain on the CKAD exam, and what percentage is it worth?

<details>
<summary>Answer</summary>

**Application Environment, Configuration and Security** at **25%**.

This includes ConfigMaps, Secrets, ServiceAccounts, resource requirements, SecurityContexts, and CRDs.

</details>

---

### Question 2: Multi-Container Patterns
**[30 seconds]**

Name the three multi-container pod patterns you must know for CKAD.

<details>
<summary>Answer</summary>

1. **Init containers** - Run before main containers, must complete successfully
2. **Sidecar** - Run alongside main container for the pod's lifetime
3. **Ambassador** - Proxy connections to external services

</details>

---

### Question 3: Imperative Command
**[1 minute]**

Write the single command to create a Job named `process-data` using busybox that echoes "Processing complete".

<details>
<summary>Answer</summary>

```bash
k create job process-data --image=busybox -- echo "Processing complete"
```

</details>

---

### Question 4: YAML Generation
**[1 minute]**

Write the command to generate a deployment YAML file for `web-app` with nginx image and 3 replicas, without actually creating it.

<details>
<summary>Answer</summary>

```bash
k create deploy web-app --image=nginx --replicas=3 --dry-run=client -o yaml > web-app.yaml
```

Key elements:
- `--dry-run=client` prevents creation
- `-o yaml` outputs YAML format

</details>

---

### Question 5: Pattern Recognition
**[30 seconds]**

Your application needs to wait for a database service to be available before starting. Which multi-container pattern should you use?

<details>
<summary>Answer</summary>

**Init container**

Init containers run before the main container starts and must complete successfully. They're perfect for:
- Waiting for dependencies
- Downloading/generating config
- Running database migrations

</details>

---

### Question 6: Context Management
**[30 seconds]**

Write the command to switch to a context named `ckad-cluster` and set the default namespace to `dev`.

<details>
<summary>Answer</summary>

```bash
k config use-context ckad-cluster
k config set-context --current --namespace=dev
```

Or combine:
```bash
k config use-context ckad-cluster && k config set-context --current --namespace=dev
```

</details>

---

### Question 7: Probe Types
**[30 seconds]**

What are the three probe types in Kubernetes, and what happens when each fails?

<details>
<summary>Answer</summary>

1. **Liveness probe** - Container is restarted when it fails
2. **Readiness probe** - Pod is removed from Service endpoints when it fails
3. **Startup probe** - Container is killed and restarts when it fails (during startup)

</details>

---

### Question 8: JSONPath
**[1 minute]**

Write the command to extract just the image names from all containers in a pod named `multi-app`.

<details>
<summary>Answer</summary>

```bash
k get pod multi-app -o jsonpath='{.spec.containers[*].image}'
```

Or for one per line:
```bash
k get pod multi-app -o jsonpath='{range .spec.containers[*]}{.image}{"\n"}{end}'
```

</details>

---

### Question 9: CronJob Schedule
**[30 seconds]**

What cron schedule expression runs a job at 2:30 AM every day?

<details>
<summary>Answer</summary>

```
30 2 * * *
```

Format: `minute hour day-of-month month day-of-week`
- 30 = minute 30
- 2 = hour 2 (2 AM)
- * = every day of month
- * = every month
- * = every day of week

</details>

---

### Question 10: Three-Pass Strategy
**[30 seconds]**

In the three-pass exam strategy, what types of tasks should you tackle in Pass 1?

<details>
<summary>Answer</summary>

**Quick wins** - tasks that take 1-3 minutes:
- Create pod/deployment/service (imperative commands)
- Add labels, annotations
- Expose a deployment
- Simple ConfigMap/Secret creation

Secure easy points first before tackling complex questions.

</details>

---

## Scoring

| Questions Correct | Score | Status |
|-------------------|-------|--------|
| 10/10 | 100% | Excellent - Ready to proceed |
| 8-9/10 | 80-90% | Good - Minor review needed |
| 6-7/10 | 60-70% | Review weak areas |
| <6/10 | <60% | Revisit Part 0 modules |

---

## Key Takeaways

If you scored less than 80%, review these areas:

- **Missed Q1-2**: Review Module 0.1 domain breakdown and patterns
- **Missed Q3-4**: Practice imperative commands and --dry-run pattern
- **Missed Q5-7**: Review probe types and multi-container patterns
- **Missed Q8**: Practice JSONPath queries in Module 0.2
- **Missed Q9**: Memorize cron schedule format
- **Missed Q10**: Understand exam time management strategy

---

## Next Part

[Part 1: Application Design and Build](../part1-design-build/module-1.1-container-images.md) - Container images, Jobs, multi-container pods, and volumes.
