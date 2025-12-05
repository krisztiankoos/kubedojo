# Module 3.3: Argo Workflows

> **Toolkit Track** | Complexity: `[COMPLEX]` | Time: 40-45 min

## Prerequisites

Before starting this module:
- [DevSecOps Discipline](../../disciplines/devsecops/) — CI/CD concepts
- Kubernetes basics (Pods, Services)
- Container fundamentals
- DAG (Directed Acyclic Graph) concepts helpful

## Why This Module Matters

Argo Workflows is a container-native workflow engine for orchestrating parallel jobs on Kubernetes. While Tekton focuses on CI/CD pipelines, Argo Workflows excels at complex DAGs, data processing, and ML workflows.

It powers machine learning pipelines at companies like Intuit, Google, NVIDIA, and GitHub. When you need more than simple build-test-deploy, Argo Workflows provides the flexibility.

## Did You Know?

- **Argo Workflows powers Kubeflow Pipelines**—the ML workflow engine uses Argo Workflows as its execution layer
- **GitHub Actions is built on Argo Workflows concepts**—many of the same DAG patterns apply
- **Argo Workflows can run 10,000+ pods in a single workflow**—it's designed for massive parallel data processing
- **The Argo project includes 4 tools**—Workflows, CD (ArgoCD), Events, and Rollouts—all designed to work together

## Argo Workflows Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 ARGO WORKFLOWS ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  WORKFLOW SPEC                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  apiVersion: argoproj.io/v1alpha1                         │   │
│  │  kind: Workflow                                           │   │
│  │  spec:                                                    │   │
│  │    templates:                                             │   │
│  │      - name: main                                         │   │
│  │        dag:                                               │   │
│  │          tasks:                                           │   │
│  │            - name: A                                      │   │
│  │            - name: B (depends: A)                         │   │
│  │            - name: C (depends: A)                         │   │
│  │            - name: D (depends: B && C)                    │   │
│  └────────────────────────────┬─────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               WORKFLOW CONTROLLER                         │   │
│  │                                                           │   │
│  │  • Parses workflow DAG                                    │   │
│  │  • Creates pods for each step                             │   │
│  │  • Handles retries, timeouts                              │   │
│  │  • Passes artifacts between steps                         │   │
│  │  • Reports status                                         │   │
│  └────────────────────────────┬─────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               KUBERNETES CLUSTER                          │   │
│  │                                                           │   │
│  │   A ──────────────────┐                                   │   │
│  │   │                   │                                   │   │
│  │   ▼                   ▼                                   │   │
│  │   B                   C     (parallel)                    │   │
│  │   │                   │                                   │   │
│  │   └───────────────────┘                                   │   │
│  │           │                                               │   │
│  │           ▼                                               │   │
│  │           D                                               │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Core Concepts

| Concept | Description |
|---------|-------------|
| **Workflow** | A complete job definition with templates |
| **Template** | A step type (container, DAG, steps, script) |
| **DAG** | Directed Acyclic Graph of tasks |
| **Artifact** | Data passed between steps (files, S3 objects) |
| **Parameter** | Values passed between steps (strings) |
| **WorkflowTemplate** | Reusable workflow definition |

## Installing Argo Workflows

```bash
# Create namespace
kubectl create namespace argo

# Install Argo Workflows
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/latest/download/install.yaml

# Wait for controller
kubectl -n argo wait --for=condition=ready pod -l app=workflow-controller --timeout=120s

# Install CLI
brew install argo  # macOS
# or
curl -sLO https://github.com/argoproj/argo-workflows/releases/latest/download/argo-linux-amd64.gz
gunzip argo-linux-amd64.gz && chmod +x argo-linux-amd64 && sudo mv argo-linux-amd64 /usr/local/bin/argo

# Port forward UI
kubectl -n argo port-forward svc/argo-server 2746:2746 &
# Open https://localhost:2746
```

## Workflow Types

### Simple Container Workflow

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hello-world-
spec:
  entrypoint: hello
  templates:
    - name: hello
      container:
        image: alpine
        command: [echo]
        args: ["Hello, Argo Workflows!"]
```

### Steps (Sequential)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: steps-example-
spec:
  entrypoint: main
  templates:
    - name: main
      steps:
        - - name: step1
            template: echo
            arguments:
              parameters: [{name: message, value: "Step 1"}]
        - - name: step2
            template: echo
            arguments:
              parameters: [{name: message, value: "Step 2"}]
        - - name: step3a
            template: echo
            arguments:
              parameters: [{name: message, value: "Step 3A"}]
          - name: step3b
            template: echo
            arguments:
              parameters: [{name: message, value: "Step 3B"}]

    - name: echo
      inputs:
        parameters:
          - name: message
      container:
        image: alpine
        command: [echo]
        args: ["{{inputs.parameters.message}}"]
```

### DAG (Directed Acyclic Graph)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: dag-example-
spec:
  entrypoint: main
  templates:
    - name: main
      dag:
        tasks:
          - name: checkout
            template: git-clone

          - name: lint
            template: run-lint
            dependencies: [checkout]

          - name: test
            template: run-test
            dependencies: [checkout]

          - name: security-scan
            template: run-trivy
            dependencies: [checkout]

          - name: build
            template: build-image
            dependencies: [lint, test, security-scan]

          - name: deploy
            template: kubectl-apply
            dependencies: [build]

    - name: git-clone
      container:
        image: alpine/git
        command: [sh, -c]
        args: ["git clone https://github.com/org/repo.git /work"]

    - name: run-lint
      container:
        image: golangci/golangci-lint
        command: [golangci-lint, run]

    - name: run-test
      container:
        image: golang:1.21
        command: [go, test, ./...]

    - name: run-trivy
      container:
        image: aquasec/trivy
        command: [trivy, fs, /work]

    - name: build-image
      container:
        image: gcr.io/kaniko-project/executor
        args: ["--destination=myregistry/app:latest"]

    - name: kubectl-apply
      container:
        image: bitnami/kubectl
        command: [kubectl, apply, -f, /work/k8s/]
```

## Parameters and Artifacts

### Parameters (Strings)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: params-example-
spec:
  entrypoint: main
  arguments:
    parameters:
      - name: repo
        value: https://github.com/org/app.git
      - name: branch
        value: main

  templates:
    - name: main
      dag:
        tasks:
          - name: generate
            template: generate-message

          - name: consume
            template: print-message
            dependencies: [generate]
            arguments:
              parameters:
                - name: msg
                  value: "{{tasks.generate.outputs.parameters.message}}"

    - name: generate-message
      container:
        image: alpine
        command: [sh, -c]
        args: ["echo 'Generated at $(date)' > /tmp/message.txt"]
      outputs:
        parameters:
          - name: message
            valueFrom:
              path: /tmp/message.txt

    - name: print-message
      inputs:
        parameters:
          - name: msg
      container:
        image: alpine
        command: [echo]
        args: ["Received: {{inputs.parameters.msg}}"]
```

### Artifacts (Files)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: artifacts-example-
spec:
  entrypoint: main
  templates:
    - name: main
      dag:
        tasks:
          - name: generate
            template: generate-file

          - name: process
            template: process-file
            dependencies: [generate]
            arguments:
              artifacts:
                - name: input
                  from: "{{tasks.generate.outputs.artifacts.output}}"

    - name: generate-file
      container:
        image: alpine
        command: [sh, -c]
        args: ["echo 'data: 12345' > /tmp/data.json"]
      outputs:
        artifacts:
          - name: output
            path: /tmp/data.json

    - name: process-file
      inputs:
        artifacts:
          - name: input
            path: /tmp/input.json
      container:
        image: alpine
        command: [sh, -c]
        args: ["cat /tmp/input.json && echo 'Processed!'"]
```

### S3 Artifacts

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: s3-artifacts-
spec:
  entrypoint: main
  artifactRepositoryRef:
    configMap: artifact-repositories
    key: default

  templates:
    - name: main
      dag:
        tasks:
          - name: generate
            template: generate-data

          - name: process
            template: process-data
            dependencies: [generate]
            arguments:
              artifacts:
                - name: input
                  from: "{{tasks.generate.outputs.artifacts.output}}"

    - name: generate-data
      container:
        image: python:3.11
        command: [python, -c]
        args:
          - |
            import json
            data = {"results": [1, 2, 3, 4, 5]}
            with open('/tmp/data.json', 'w') as f:
                json.dump(data, f)
      outputs:
        artifacts:
          - name: output
            path: /tmp/data.json
            s3:
              key: workflows/{{workflow.name}}/data.json

    - name: process-data
      inputs:
        artifacts:
          - name: input
            path: /tmp/data.json
      container:
        image: python:3.11
        command: [python, -c]
        args:
          - |
            import json
            with open('/tmp/data.json') as f:
                data = json.load(f)
            print(f"Sum: {sum(data['results'])}")
```

## Loops and Parallelism

### Parallel Loops

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: parallel-loop-
spec:
  entrypoint: main
  templates:
    - name: main
      dag:
        tasks:
          - name: process
            template: process-item
            arguments:
              parameters:
                - name: item
                  value: "{{item}}"
            withItems:
              - one
              - two
              - three

    - name: process-item
      inputs:
        parameters:
          - name: item
      container:
        image: alpine
        command: [echo]
        args: ["Processing: {{inputs.parameters.item}}"]
```

### Dynamic Parallelism (Fan-out)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: fan-out-
spec:
  entrypoint: main
  templates:
    - name: main
      dag:
        tasks:
          - name: generate-list
            template: generate

          - name: process-items
            template: process-item
            dependencies: [generate-list]
            arguments:
              parameters:
                - name: item
                  value: "{{item}}"
            withParam: "{{tasks.generate-list.outputs.result}}"

          - name: aggregate
            template: aggregate-results
            dependencies: [process-items]

    - name: generate
      script:
        image: python:3.11-alpine
        command: [python]
        source: |
          import json
          items = ["item1", "item2", "item3", "item4", "item5"]
          print(json.dumps(items))

    - name: process-item
      inputs:
        parameters:
          - name: item
      container:
        image: alpine
        command: [echo]
        args: ["Processing: {{inputs.parameters.item}}"]
```

## WorkflowTemplates

### Reusable Template

```yaml
apiVersion: argoproj.io/v1alpha1
kind: WorkflowTemplate
metadata:
  name: ci-pipeline
spec:
  arguments:
    parameters:
      - name: repo
      - name: branch
        value: main
      - name: image

  entrypoint: main
  templates:
    - name: main
      dag:
        tasks:
          - name: clone
            template: git-clone
            arguments:
              parameters:
                - name: repo
                  value: "{{workflow.parameters.repo}}"
                - name: branch
                  value: "{{workflow.parameters.branch}}"

          - name: test
            template: run-tests
            dependencies: [clone]

          - name: build
            template: build-push
            dependencies: [test]
            arguments:
              parameters:
                - name: image
                  value: "{{workflow.parameters.image}}"

    - name: git-clone
      inputs:
        parameters: [{name: repo}, {name: branch}]
      container:
        image: alpine/git
        command: [git, clone, "--branch", "{{inputs.parameters.branch}}", "{{inputs.parameters.repo}}"]

    - name: run-tests
      container:
        image: golang:1.21
        command: [go, test, ./...]

    - name: build-push
      inputs:
        parameters: [{name: image}]
      container:
        image: gcr.io/kaniko-project/executor
        args: ["--destination={{inputs.parameters.image}}"]
```

### Using WorkflowTemplate

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: run-ci-
spec:
  workflowTemplateRef:
    name: ci-pipeline
  arguments:
    parameters:
      - name: repo
        value: https://github.com/org/app.git
      - name: image
        value: ghcr.io/org/app:latest
```

## Error Handling

### Retries

```yaml
templates:
  - name: flaky-task
    retryStrategy:
      limit: 3
      retryPolicy: Always
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 1m
    container:
      image: alpine
      command: [sh, -c]
      args: ["exit $((RANDOM % 2))"]  # Randomly fails
```

### Continue on Error

```yaml
dag:
  tasks:
    - name: optional-task
      template: might-fail
      continueOn:
        failed: true

    - name: required-task
      template: must-succeed
      dependencies: [optional-task]
```

### Timeouts

```yaml
templates:
  - name: limited-task
    activeDeadlineSeconds: 300  # 5 minute timeout
    container:
      image: alpine
      command: [sleep, "600"]  # Would run 10 min
```

## Argo Events Integration

```yaml
# Trigger workflow from GitHub webhook
apiVersion: argoproj.io/v1alpha1
kind: Sensor
metadata:
  name: github-sensor
spec:
  template:
    serviceAccountName: argo-events-sa
  dependencies:
    - name: github
      eventSourceName: github
      eventName: push
  triggers:
    - template:
        name: workflow-trigger
        k8s:
          operation: create
          source:
            resource:
              apiVersion: argoproj.io/v1alpha1
              kind: Workflow
              metadata:
                generateName: github-triggered-
              spec:
                workflowTemplateRef:
                  name: ci-pipeline
                arguments:
                  parameters:
                    - name: repo
                      value: ""  # Filled by parameter
                    - name: branch
                      value: ""
          parameters:
            - src:
                dependencyName: github
                dataKey: body.repository.clone_url
              dest: spec.arguments.parameters.0.value
            - src:
                dependencyName: github
                dataKey: body.ref
              dest: spec.arguments.parameters.1.value
```

## Common Mistakes

| Mistake | Why It's Bad | Better Approach |
|---------|--------------|-----------------|
| No resource limits | Pods consume all resources | Set limits on all containers |
| Large artifacts in-line | Slow, memory issues | Use S3/GCS artifact repository |
| No timeouts | Stuck workflows | Set `activeDeadlineSeconds` |
| Sequential when parallel | Slow workflows | Use DAG for parallel tasks |
| Hardcoded secrets | Insecure | Use Kubernetes Secrets |
| No retry strategy | Transient failures kill workflow | Add retries for flaky tasks |

## War Story: The 10,000 Pod Workflow

A data team ran ML training with 10,000 parallel pods processing different hyperparameter combinations. The workflow failed repeatedly—not from OOM or timeouts, but from the Kubernetes API being overwhelmed.

**The fix**:
1. Added `parallelism` limit to the workflow
2. Used `nodeSelector` to spread across node pools
3. Implemented batch processing with `withItems` chunks

```yaml
spec:
  parallelism: 100  # Max 100 pods at once
  templates:
    - name: process-batch
      parallelism: 20  # Max 20 per batch
```

**The lesson**: Kubernetes has limits. Design workflows that respect them.

## Quiz

### Question 1
What's the difference between Steps and DAG templates?

<details>
<summary>Show Answer</summary>

**Steps**: Defines sequential stages. Each stage can have parallel items (using `- -` syntax), but stages execute in order.

```yaml
steps:
  - - name: step1  # Stage 1
  - - name: step2a  # Stage 2 (parallel)
    - name: step2b
  - - name: step3  # Stage 3
```

**DAG**: Defines explicit dependencies. Tasks run as soon as their dependencies complete—maximum parallelism automatically.

```yaml
dag:
  tasks:
    - name: A
    - name: B
      dependencies: [A]
    - name: C
      dependencies: [A]
    - name: D
      dependencies: [B, C]
```

Use Steps for simple sequential logic. Use DAG for complex dependency graphs.
</details>

### Question 2
How do you pass a file from one task to another?

<details>
<summary>Show Answer</summary>

Use artifacts:

```yaml
templates:
  - name: generate
    container:
      image: alpine
      command: [sh, -c, "echo 'data' > /tmp/file.txt"]
    outputs:
      artifacts:
        - name: my-artifact
          path: /tmp/file.txt

  - name: consume
    inputs:
      artifacts:
        - name: my-artifact
          path: /tmp/input.txt
    container:
      image: alpine
      command: [cat, /tmp/input.txt]
```

In the DAG:
```yaml
- name: consume
  dependencies: [generate]
  arguments:
    artifacts:
      - name: my-artifact
        from: "{{tasks.generate.outputs.artifacts.my-artifact}}"
```

For small strings (< 256KB), use parameters instead.
</details>

### Question 3
Write a DAG that runs A, then B and C in parallel, then D.

<details>
<summary>Show Answer</summary>

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: abc-dag-
spec:
  entrypoint: main
  templates:
    - name: main
      dag:
        tasks:
          - name: A
            template: echo
            arguments:
              parameters: [{name: msg, value: "A"}]

          - name: B
            template: echo
            dependencies: [A]
            arguments:
              parameters: [{name: msg, value: "B"}]

          - name: C
            template: echo
            dependencies: [A]
            arguments:
              parameters: [{name: msg, value: "C"}]

          - name: D
            template: echo
            dependencies: [B, C]
            arguments:
              parameters: [{name: msg, value: "D"}]

    - name: echo
      inputs:
        parameters: [{name: msg}]
      container:
        image: alpine
        command: [echo]
        args: ["{{inputs.parameters.msg}}"]
```
</details>

### Question 4
Your workflow processes 1000 items. How do you prevent cluster overload?

<details>
<summary>Show Answer</summary>

Use the `parallelism` setting at workflow and template level:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
spec:
  # Workflow-level limit
  parallelism: 50  # Max 50 pods total

  templates:
    - name: process-items
      # Template-level limit
      parallelism: 10  # Max 10 concurrent within this template
      dag:
        tasks:
          - name: process
            template: process-one
            withItems: "{{workflow.parameters.items}}"
```

Also consider:
- `resourceDuration` limits
- `activeDeadlineSeconds` for timeouts
- Node selectors to spread load
- Batch items into chunks
</details>

## Hands-On Exercise

### Scenario: Build a Data Processing Workflow

Create an Argo Workflow that processes data in parallel.

### Setup

```bash
# Create kind cluster
kind create cluster --name argo-lab

# Install Argo Workflows
kubectl create namespace argo
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/latest/download/install.yaml

# Patch to allow running workflows without auth (dev only)
kubectl patch deployment argo-server -n argo --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--auth-mode=server"}]'

# Wait for controller
kubectl -n argo wait --for=condition=ready pod -l app=workflow-controller --timeout=120s

# Port forward UI
kubectl -n argo port-forward svc/argo-server 2746:2746 &
```

### Create Workflow

```yaml
# workflow.yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: data-pipeline-
  namespace: argo
spec:
  entrypoint: main
  parallelism: 3

  templates:
    - name: main
      dag:
        tasks:
          - name: generate-data
            template: generate

          - name: process-items
            template: process
            dependencies: [generate-data]
            arguments:
              parameters:
                - name: item
                  value: "{{item}}"
            withParam: "{{tasks.generate-data.outputs.result}}"

          - name: aggregate
            template: aggregate
            dependencies: [process-items]

    - name: generate
      script:
        image: python:3.11-alpine
        command: [python]
        source: |
          import json
          items = [f"item-{i}" for i in range(5)]
          print(json.dumps(items))

    - name: process
      inputs:
        parameters:
          - name: item
      container:
        image: alpine
        command: [sh, -c]
        args:
          - |
            echo "Processing: {{inputs.parameters.item}}"
            sleep 2
            echo "Done: {{inputs.parameters.item}}"

    - name: aggregate
      container:
        image: alpine
        command: [echo]
        args: ["All items processed!"]
```

### Run Workflow

```bash
# Submit workflow
argo submit -n argo workflow.yaml --watch

# List workflows
argo list -n argo

# Get details
argo get -n argo @latest

# View logs
argo logs -n argo @latest
```

### View in UI

Open https://localhost:2746 and explore:
- Workflow visualization
- Task logs
- Artifact inspection

### Success Criteria

- [ ] Argo Workflows is running
- [ ] Workflow executes successfully
- [ ] Parallel processing works (3 at a time)
- [ ] Can view in UI
- [ ] Understand DAG structure

### Cleanup

```bash
kind delete cluster --name argo-lab
```

## Summary

You've completed the CI/CD Pipelines Toolkit! You now understand:

- **Dagger**: Programmable, portable pipelines
- **Tekton**: Kubernetes-native CI/CD
- **Argo Workflows**: DAG-based workflow orchestration

These tools provide different approaches to the same problem—choose based on your needs.

## Next Steps

Continue to [Security Tools Toolkit](../security-tools/) where we'll cover Vault, OPA, Falco, and supply chain security.

---

*"A workflow is a program. Write it like code, test it like code, version it like code."*
