# Module 3.2: Tekton

> **Toolkit Track** | Complexity: `[COMPLEX]` | Time: 45-50 min

## Prerequisites

Before starting this module:
- [DevSecOps Discipline](../../disciplines/devsecops/) — CI/CD concepts
- Kubernetes basics (Pods, Services, CRDs)
- Container fundamentals
- YAML proficiency

## Why This Module Matters

Tekton is a Kubernetes-native CI/CD framework. Unlike hosted CI services, Tekton runs in your cluster—giving you full control, no vendor lock-in, and the ability to scale pipelines like any other Kubernetes workload.

Born from Google's Knative Build project and now a CNCF project, Tekton powers enterprise CI/CD at companies like IBM, Red Hat, and Google.

## Did You Know?

- **Tekton is named after the Greek word for "builder"**—appropriate for a build system
- **Tekton powers Google Cloud Build and OpenShift Pipelines**—it's the foundation of major enterprise CI/CD offerings
- **Tekton Pipelines runs as pods in your cluster**—each task step is a container, scaling naturally with Kubernetes
- **The Tekton Catalog has 100+ reusable tasks**—from Git clone to Kubernetes deploy, pre-built and maintained

## Tekton Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TEKTON ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CUSTOM RESOURCES                                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                                                           │   │
│  │  Task          TaskRun         Pipeline       PipelineRun│   │
│  │  (template)    (instance)      (template)     (instance) │   │
│  │  ┌─────────┐   ┌─────────┐    ┌─────────┐    ┌─────────┐│   │
│  │  │ Steps:  │──▶│ Pod     │    │ Tasks:  │───▶│ TaskRuns││   │
│  │  │ - clone │   │ running │    │ - build │    │ running ││   │
│  │  │ - build │   │         │    │ - test  │    │         ││   │
│  │  │ - push  │   │         │    │ - deploy│    │         ││   │
│  │  └─────────┘   └─────────┘    └─────────┘    └─────────┘│   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 TEKTON CONTROLLERS                        │   │
│  │                                                           │   │
│  │  ┌─────────────────┐    ┌─────────────────┐              │   │
│  │  │    Pipeline     │    │   Triggers      │              │   │
│  │  │   Controller    │    │   Controller    │              │   │
│  │  │                 │    │                 │              │   │
│  │  │ Watches CRs     │    │ Webhooks        │              │   │
│  │  │ Creates Pods    │    │ Creates Runs    │              │   │
│  │  └─────────────────┘    └─────────────────┘              │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              KUBERNETES CLUSTER                           │   │
│  │                                                           │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │                    POD (TaskRun)                    │ │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐            │ │   │
│  │  │  │ Step 1  │  │ Step 2  │  │ Step 3  │            │ │   │
│  │  │  │ (init)  │─▶│ (main)  │─▶│ (post)  │            │ │   │
│  │  │  └─────────┘  └─────────┘  └─────────┘            │ │   │
│  │  │                                                     │ │   │
│  │  │  Shared workspace volume                           │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Core Concepts

| Concept | Description |
|---------|-------------|
| **Task** | A template defining a sequence of steps (containers) |
| **TaskRun** | An instance of a Task execution |
| **Pipeline** | A template defining a sequence of Tasks |
| **PipelineRun** | An instance of a Pipeline execution |
| **Workspace** | Shared storage between steps and tasks |
| **Trigger** | Webhook listener that creates PipelineRuns |

## Installing Tekton

```bash
# Install Tekton Pipelines
kubectl apply -f https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml

# Install Tekton Triggers (for webhooks)
kubectl apply -f https://storage.googleapis.com/tekton-releases/triggers/latest/release.yaml
kubectl apply -f https://storage.googleapis.com/tekton-releases/triggers/latest/interceptors.yaml

# Install Tekton Dashboard (optional)
kubectl apply -f https://storage.googleapis.com/tekton-releases/dashboard/latest/release.yaml

# Wait for components
kubectl -n tekton-pipelines wait --for=condition=ready pod -l app=tekton-pipelines-controller --timeout=120s

# Install tkn CLI
brew install tektoncd-cli  # macOS
```

## Tasks

### Basic Task

```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: hello
spec:
  steps:
    - name: hello
      image: alpine
      script: |
        echo "Hello from Tekton!"
```

### Task with Parameters

```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: greet
spec:
  params:
    - name: name
      type: string
      description: Name to greet
      default: World

  steps:
    - name: greet
      image: alpine
      script: |
        echo "Hello, $(params.name)!"
```

### Task with Workspaces

```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: git-clone
spec:
  params:
    - name: url
      type: string

  workspaces:
    - name: output
      description: The git repo will be cloned here

  steps:
    - name: clone
      image: alpine/git
      workingDir: $(workspaces.output.path)
      script: |
        git clone $(params.url) .
        ls -la
```

### Task with Results

```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: get-version
spec:
  workspaces:
    - name: source

  results:
    - name: version
      description: The version from package.json

  steps:
    - name: get-version
      image: node:20-alpine
      workingDir: $(workspaces.source.path)
      script: |
        VERSION=$(node -p "require('./package.json').version")
        echo -n $VERSION | tee $(results.version.path)
```

### Build and Push Task

```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: build-push
spec:
  params:
    - name: image
      type: string
    - name: dockerfile
      default: Dockerfile

  workspaces:
    - name: source
    - name: dockerconfig
      description: Docker config for registry auth

  results:
    - name: digest
      description: Image digest

  steps:
    - name: build-push
      image: gcr.io/kaniko-project/executor:latest
      workingDir: $(workspaces.source.path)
      env:
        - name: DOCKER_CONFIG
          value: $(workspaces.dockerconfig.path)
      args:
        - --dockerfile=$(params.dockerfile)
        - --destination=$(params.image)
        - --context=.
        - --digest-file=$(results.digest.path)
```

## TaskRuns

### Running a Task

```yaml
apiVersion: tekton.dev/v1
kind: TaskRun
metadata:
  generateName: greet-run-
spec:
  taskRef:
    name: greet
  params:
    - name: name
      value: "Tekton"
```

```bash
# Create TaskRun
kubectl create -f taskrun.yaml

# List TaskRuns
tkn taskrun list

# View logs
tkn taskrun logs -f greet-run-xyz

# Describe
tkn taskrun describe greet-run-xyz
```

### TaskRun with Workspace

```yaml
apiVersion: tekton.dev/v1
kind: TaskRun
metadata:
  generateName: clone-run-
spec:
  taskRef:
    name: git-clone
  params:
    - name: url
      value: https://github.com/tektoncd/pipeline.git
  workspaces:
    - name: output
      emptyDir: {}  # Or use PVC for persistence
```

## Pipelines

### Basic Pipeline

```yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: build-test-deploy
spec:
  params:
    - name: repo-url
      type: string
    - name: image
      type: string

  workspaces:
    - name: shared-workspace
    - name: docker-credentials

  tasks:
    - name: fetch-source
      taskRef:
        name: git-clone
      workspaces:
        - name: output
          workspace: shared-workspace
      params:
        - name: url
          value: $(params.repo-url)

    - name: run-tests
      runAfter:
        - fetch-source
      taskRef:
        name: npm-test
      workspaces:
        - name: source
          workspace: shared-workspace

    - name: build-push
      runAfter:
        - run-tests
      taskRef:
        name: build-push
      workspaces:
        - name: source
          workspace: shared-workspace
        - name: dockerconfig
          workspace: docker-credentials
      params:
        - name: image
          value: $(params.image)
```

### Pipeline with Parallel Tasks

```yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: parallel-ci
spec:
  workspaces:
    - name: shared-workspace

  tasks:
    - name: fetch-source
      taskRef:
        name: git-clone
      workspaces:
        - name: output
          workspace: shared-workspace

    # These run in parallel after fetch-source
    - name: lint
      runAfter: [fetch-source]
      taskRef:
        name: lint
      workspaces:
        - name: source
          workspace: shared-workspace

    - name: test
      runAfter: [fetch-source]
      taskRef:
        name: test
      workspaces:
        - name: source
          workspace: shared-workspace

    - name: security-scan
      runAfter: [fetch-source]
      taskRef:
        name: trivy-scan
      workspaces:
        - name: source
          workspace: shared-workspace

    # This runs after all parallel tasks complete
    - name: build
      runAfter: [lint, test, security-scan]
      taskRef:
        name: build-push
      workspaces:
        - name: source
          workspace: shared-workspace
```

### Pipeline with Conditional Tasks

```yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: conditional-deploy
spec:
  params:
    - name: deploy-to-prod
      type: string
      default: "false"

  tasks:
    - name: build
      taskRef:
        name: build-push

    - name: deploy-staging
      runAfter: [build]
      taskRef:
        name: kubectl-deploy
      params:
        - name: namespace
          value: staging

    - name: deploy-production
      runAfter: [deploy-staging]
      when:
        - input: $(params.deploy-to-prod)
          operator: in
          values: ["true"]
      taskRef:
        name: kubectl-deploy
      params:
        - name: namespace
          value: production
```

### Using Results Between Tasks

```yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: version-pipeline
spec:
  tasks:
    - name: get-version
      taskRef:
        name: get-version
      workspaces:
        - name: source
          workspace: shared-workspace

    - name: build-image
      runAfter: [get-version]
      taskRef:
        name: build-push
      params:
        - name: image
          # Use result from previous task
          value: "myregistry/myapp:$(tasks.get-version.results.version)"
```

## PipelineRuns

### Running a Pipeline

```yaml
apiVersion: tekton.dev/v1
kind: PipelineRun
metadata:
  generateName: build-test-deploy-run-
spec:
  pipelineRef:
    name: build-test-deploy
  params:
    - name: repo-url
      value: https://github.com/org/app.git
    - name: image
      value: ghcr.io/org/app:latest
  workspaces:
    - name: shared-workspace
      volumeClaimTemplate:
        spec:
          accessModes:
            - ReadWriteOnce
          resources:
            requests:
              storage: 1Gi
    - name: docker-credentials
      secret:
        secretName: docker-credentials
```

```bash
# Create PipelineRun
kubectl create -f pipelinerun.yaml

# List PipelineRuns
tkn pipelinerun list

# View logs
tkn pipelinerun logs -f build-test-deploy-run-xyz

# Cancel a running pipeline
tkn pipelinerun cancel build-test-deploy-run-xyz
```

## Triggers

### Webhook Trigger

```yaml
# EventListener - receives webhooks
apiVersion: triggers.tekton.dev/v1beta1
kind: EventListener
metadata:
  name: github-listener
spec:
  serviceAccountName: tekton-triggers-sa
  triggers:
    - name: github-push
      bindings:
        - ref: github-push-binding
      template:
        ref: github-push-template

---
# TriggerBinding - extracts data from webhook
apiVersion: triggers.tekton.dev/v1beta1
kind: TriggerBinding
metadata:
  name: github-push-binding
spec:
  params:
    - name: repo-url
      value: $(body.repository.clone_url)
    - name: revision
      value: $(body.head_commit.id)
    - name: branch
      value: $(body.ref)

---
# TriggerTemplate - creates PipelineRun
apiVersion: triggers.tekton.dev/v1beta1
kind: TriggerTemplate
metadata:
  name: github-push-template
spec:
  params:
    - name: repo-url
    - name: revision
    - name: branch

  resourcetemplates:
    - apiVersion: tekton.dev/v1
      kind: PipelineRun
      metadata:
        generateName: github-triggered-
      spec:
        pipelineRef:
          name: build-test-deploy
        params:
          - name: repo-url
            value: $(tt.params.repo-url)
          - name: revision
            value: $(tt.params.revision)
        workspaces:
          - name: shared-workspace
            volumeClaimTemplate:
              spec:
                accessModes: [ReadWriteOnce]
                resources:
                  requests:
                    storage: 1Gi
```

### Exposing the Webhook

```yaml
# Ingress for webhook
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: github-webhook
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  rules:
    - host: tekton.example.com
      http:
        paths:
          - path: /hooks
            pathType: Prefix
            backend:
              service:
                name: el-github-listener
                port:
                  number: 8080
```

## Tekton Catalog

```bash
# Install a task from catalog
kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/git-clone/0.9/git-clone.yaml
kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/kaniko/0.6/kaniko.yaml
kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/kubernetes-actions/0.2/kubernetes-actions.yaml

# Or use tkn hub
tkn hub install task git-clone
tkn hub install task kaniko
```

### Using Catalog Tasks

```yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: catalog-pipeline
spec:
  params:
    - name: repo-url
    - name: image

  workspaces:
    - name: shared-data
    - name: docker-credentials

  tasks:
    - name: fetch-repo
      taskRef:
        name: git-clone  # From catalog
      workspaces:
        - name: output
          workspace: shared-data
      params:
        - name: url
          value: $(params.repo-url)

    - name: build-push
      runAfter: [fetch-repo]
      taskRef:
        name: kaniko  # From catalog
      workspaces:
        - name: source
          workspace: shared-data
        - name: dockerconfig
          workspace: docker-credentials
      params:
        - name: IMAGE
          value: $(params.image)
```

## Common Mistakes

| Mistake | Why It's Bad | Better Approach |
|---------|--------------|-----------------|
| No workspaces | Data lost between steps | Use PVC workspaces for shared data |
| Large PVC for each run | Expensive, slow | Use volumeClaimTemplate with cleanup |
| No resource limits | Pods can starve cluster | Set CPU/memory limits on steps |
| Hardcoded secrets | Insecure | Use Secrets and Workspaces |
| No timeouts | Stuck pipelines waste resources | Set `timeout` on Tasks and Pipelines |
| Ignoring results | Can't pass data between tasks | Use `results` for task outputs |

## War Story: The Workspace Woes

A team migrated from Jenkins to Tekton. Their first pipeline worked in isolation but failed at scale—PVCs couldn't be provisioned fast enough, and storage costs exploded with each run creating a 10GB volume.

**The fixes**:
1. Used `volumeClaimTemplate` for automatic cleanup
2. Reduced storage to actual needs (500Mi instead of 10Gi)
3. Added `fsGroup` for proper permissions
4. Implemented workspace caching for dependencies

```yaml
# Before: Each run leaves PVC behind
workspaces:
  - name: shared
    persistentVolumeClaim:
      claimName: pipeline-pvc  # Never cleaned up

# After: Auto-cleanup with template
workspaces:
  - name: shared
    volumeClaimTemplate:
      spec:
        accessModes: [ReadWriteOnce]
        resources:
          requests:
            storage: 500Mi
        # PVC deleted when PipelineRun completes
```

**The lesson**: Tekton is Kubernetes-native, which means you need to think about storage like any K8s workload.

## Quiz

### Question 1
What's the difference between a Task and a Pipeline in Tekton?

<details>
<summary>Show Answer</summary>

**Task**: A single unit of work containing one or more sequential steps. Each step runs as a container in the same pod. Steps share the pod's workspace and environment.

**Pipeline**: A collection of Tasks that can run sequentially or in parallel. Each Task runs as a separate pod. Pipelines use workspaces to share data between Tasks.

Think of it as:
- Task = one pod with multiple containers (steps)
- Pipeline = multiple pods (tasks) orchestrated together
</details>

### Question 2
How do you pass data between Tasks in a Pipeline?

<details>
<summary>Show Answer</summary>

Two mechanisms:

1. **Workspaces**: Shared storage (PVC) mounted in multiple Tasks. Good for files (source code, artifacts).

```yaml
workspaces:
  - name: shared-data
```

2. **Results**: Small string values (< 4KB) written by one Task and read by another. Good for versions, digests, URLs.

```yaml
# Task A writes
echo -n "v1.2.3" > $(results.version.path)

# Pipeline uses in Task B
value: $(tasks.taskA.results.version)
```

Use workspaces for file data, results for small values.
</details>

### Question 3
Your pipeline has lint, test, and security-scan tasks that should run in parallel after git-clone. Write the YAML.

<details>
<summary>Show Answer</summary>

```yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: parallel-checks
spec:
  tasks:
    - name: git-clone
      taskRef:
        name: git-clone

    # All three run in parallel (same runAfter)
    - name: lint
      runAfter: [git-clone]
      taskRef:
        name: lint

    - name: test
      runAfter: [git-clone]
      taskRef:
        name: test

    - name: security-scan
      runAfter: [git-clone]
      taskRef:
        name: security-scan

    # Build waits for all parallel tasks
    - name: build
      runAfter: [lint, test, security-scan]
      taskRef:
        name: build
```

Tasks with the same `runAfter` dependency run in parallel. A task with multiple `runAfter` entries waits for all of them.
</details>

### Question 4
How would you trigger a Tekton pipeline from a GitHub push webhook?

<details>
<summary>Show Answer</summary>

You need three components:

1. **EventListener**: Receives the webhook
2. **TriggerBinding**: Extracts data from the webhook payload
3. **TriggerTemplate**: Creates the PipelineRun

```yaml
apiVersion: triggers.tekton.dev/v1beta1
kind: EventListener
metadata:
  name: github
spec:
  triggers:
    - bindings: [github-binding]
      template:
        ref: github-template
---
apiVersion: triggers.tekton.dev/v1beta1
kind: TriggerBinding
metadata:
  name: github-binding
spec:
  params:
    - name: repo
      value: $(body.repository.clone_url)
---
apiVersion: triggers.tekton.dev/v1beta1
kind: TriggerTemplate
metadata:
  name: github-template
spec:
  params: [repo]
  resourcetemplates:
    - apiVersion: tekton.dev/v1
      kind: PipelineRun
      spec:
        pipelineRef: {name: my-pipeline}
        params:
          - name: repo-url
            value: $(tt.params.repo)
```

Then expose the EventListener service via Ingress and configure GitHub webhook to POST to it.
</details>

## Hands-On Exercise

### Scenario: Build a Tekton Pipeline

Create a Tekton pipeline that clones a repo, runs tests, and builds a container.

### Setup

```bash
# Create kind cluster
kind create cluster --name tekton-lab

# Install Tekton
kubectl apply -f https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml

# Wait for controller
kubectl -n tekton-pipelines wait --for=condition=ready pod -l app=tekton-pipelines-controller --timeout=120s

# Install tkn CLI if not installed
brew install tektoncd-cli
```

### Create Tasks

```yaml
# tasks.yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: git-clone-simple
spec:
  params:
    - name: url
  workspaces:
    - name: output
  steps:
    - name: clone
      image: alpine/git
      script: |
        cd $(workspaces.output.path)
        git clone $(params.url) .
        ls -la
---
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: npm-test
spec:
  workspaces:
    - name: source
  steps:
    - name: test
      image: node:20-alpine
      workingDir: $(workspaces.source.path)
      script: |
        if [ -f package.json ]; then
          npm install
          npm test || echo "No tests defined"
        else
          echo "No package.json found"
        fi
---
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: echo-done
spec:
  steps:
    - name: done
      image: alpine
      script: |
        echo "Pipeline completed successfully!"
```

```bash
kubectl apply -f tasks.yaml
```

### Create Pipeline

```yaml
# pipeline.yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: build-pipeline
spec:
  params:
    - name: repo-url
      type: string
      default: https://github.com/tektoncd/pipeline.git

  workspaces:
    - name: shared-workspace

  tasks:
    - name: fetch-source
      taskRef:
        name: git-clone-simple
      params:
        - name: url
          value: $(params.repo-url)
      workspaces:
        - name: output
          workspace: shared-workspace

    - name: run-tests
      runAfter: [fetch-source]
      taskRef:
        name: npm-test
      workspaces:
        - name: source
          workspace: shared-workspace

    - name: finish
      runAfter: [run-tests]
      taskRef:
        name: echo-done
```

```bash
kubectl apply -f pipeline.yaml
```

### Run Pipeline

```yaml
# pipelinerun.yaml
apiVersion: tekton.dev/v1
kind: PipelineRun
metadata:
  generateName: build-pipeline-run-
spec:
  pipelineRef:
    name: build-pipeline
  params:
    - name: repo-url
      value: https://github.com/kubernetes/examples.git
  workspaces:
    - name: shared-workspace
      volumeClaimTemplate:
        spec:
          accessModes:
            - ReadWriteOnce
          resources:
            requests:
              storage: 500Mi
```

```bash
# Create and watch
kubectl create -f pipelinerun.yaml

# Watch logs
tkn pipelinerun logs -f $(tkn pipelinerun list -o name | head -1 | cut -d'/' -f2)

# List runs
tkn pipelinerun list
```

### Success Criteria

- [ ] Tekton is running in the cluster
- [ ] Tasks are created
- [ ] Pipeline combines tasks
- [ ] PipelineRun executes successfully
- [ ] Can view logs with tkn CLI

### Cleanup

```bash
kind delete cluster --name tekton-lab
```

## Next Module

Continue to [Module 3.3: Argo Workflows](module-3.3-argo-workflows.md) where we'll explore DAG-based workflow orchestration.

---

*"Kubernetes-native means your pipelines scale like pods, fail like pods, and are debugged like pods. Tekton makes CI/CD a first-class Kubernetes citizen."*
