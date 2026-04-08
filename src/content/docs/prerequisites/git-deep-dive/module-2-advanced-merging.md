---
title: "Module 2: The Art of the Branch — Advanced Merging"
sidebar:
  order: 2
description: "Mastering Git merge strategies, conflict resolution, and branching models for Kubernetes infrastructure."
timeToComplete: "75 minutes"
complexity: "MEDIUM"
prerequisites: ["Module 1 (Git Internals)"]
nextModule: "[Module 3: History as a Choice](../module-3-interactive-rebasing/)"
---

# Module 2: The Art of the Branch — Advanced Merging

## Learning Outcomes
- **Diagnose** the root cause of complex merge conflicts within Kubernetes manifest files by analyzing the merge base and divergent commit histories.
- **Implement** three-way and fast-forward merges strategically to maintain a clean, navigable project history.
- **Resolve** intricate multi-file conflicts during infrastructure-as-code integration without introducing YAML syntax errors or regression bugs.
- **Evaluate** different branching strategies (Trunk-based, GitFlow, GitHub Flow) to select the optimal workflow for a high-velocity Kubernetes platform team.
- **Execute** octopus merges to integrate multiple independent feature branches into a single integration or release branch simultaneously.

## Why This Module Matters
In late 2022, a major fintech company experienced a catastrophic deployment failure that took down their core payment processing API for over six hours. The root cause was not a flaw in the application logic, nor was it a misconfigured load balancer. The outage stemmed entirely from a botched Git merge. Two separate platform teams had been working on long-lived feature branches for months, modifying the same set of Kubernetes deployment manifests to introduce different auto-scaling behaviors and resource requests. When the time came for the release, the resulting merge conflict spanned hundreds of lines across dozens of YAML files.

The engineer assigned to resolve the conflict, under immense pressure and fatigued, accidentally accepted incoming changes that overwrote the liveness probe configurations while simultaneously corrupting the YAML indentation of the resource limits. The merged code passed a superficial review because the diff was simply too massive to parse effectively. Once deployed, the Kubernetes scheduler immediately began crash-looping the pods due to the malformed probes, while the cluster autoscaler went rogue based on the broken resource definitions. The financial impact was measured in the millions, but the cultural impact was worse: developers became terrified of merging.

Merging branches in Git is not merely a mechanical process of combining text files; it is the act of reconciling parallel timelines of human intent. In infrastructure-as-code environments, where a single misaligned space in a YAML file can tear down a production cluster, mastering the mechanics of the merge is a non-negotiable survival skill. This module takes you deep into the heart of Git's merge engines. You will learn how Git mathematically determines what changed, why conflicts actually happen, and how to resolve them with surgical precision rather than panic. You will move beyond typing `git merge` and hoping for the best, evolving into an engineer who orchestrates integration with absolute confidence.

## Core Content

### The Geometry of Integration: Fast-Forward vs. Three-Way Merges

When you issue a `git merge` command, Git does not blindly smash files together. It performs a geometric analysis of your commit history to determine the safest way to integrate changes. Understanding this geometry is the difference between controlling your project's history and being a victim of it.

#### The Fast-Forward Merge
Imagine you are laying bricks in a straight line. You stop to take a break. While you are resting, a colleague continues laying bricks starting exactly where you left off, continuing in the same straight line. When you return, integrating their work into your view of the wall requires no complex decisions; you simply walk to the end of their newly laid bricks.

This is a **fast-forward merge**. It occurs when the current branch tip is a direct ancestor of the branch you are trying to merge. Git simply moves your branch pointer forward to point to the same commit as the incoming branch. No new "merge commit" is created because the history is entirely linear.

```bash
# Setting up a fast-forward scenario
git init cluster-config
cd cluster-config
echo "apiVersion: v1" > config.yaml
git add config.yaml
git commit -m "Initialize cluster config"

# Create a new branch and add a commit
git checkout -b feature/add-metadata
echo "kind: ConfigMap" >> config.yaml
git commit -am "Add ConfigMap kind"

# Switch back to main and merge
git checkout main
git merge feature/add-metadata
```

Output of the merge:
```text
Updating a1b2c3d..e4f5g6h
Fast-forward
 config.yaml | 1 +
 1 file changed, 1 insertion(+)
```

Because `main` had not diverged—no new commits were added to `main` while `feature/add-metadata` was being developed—Git just moved the `main` pointer forward.

> **Pause and predict**: Before running `git log --oneline --graph` after this merge, sketch out what you think the history graph will look like. Will there be a fork and a merge commit? 
> 
> *Verification*: Because this was a fast-forward merge, `main` simply moved to the tip of `feature/add-metadata`. There is no fork and no merge commit. `git log --oneline --graph` will show a single straight line of commits ending with "Add ConfigMap kind".

#### The Three-Way Merge
Real-world development is rarely linear. While your colleague was extending the brick wall, you started building a parallel wall right next to it. Now, you need to connect them. This requires actual construction work.

A **three-way merge** happens when the history has diverged. The current branch and the incoming branch have a common ancestor (the merge base), but both have advanced independently.

```mermaid
gitGraph
   commit id: "D"
   commit id: "E"
   branch feature/rbac
   checkout main
   commit id: "A"
   commit id: "B"
   commit id: "C"
   checkout feature/rbac
   commit id: "F"
   commit id: "G"
   checkout main
   merge feature/rbac id: "H (merge commit)"
```

To resolve this, Git uses three points of reference:
1. The tip of your current branch (`C`)
2. The tip of the incoming branch (`G`)
3. The common ancestor of both branches (`E`) — the **merge base**.

Git compares `C` against `E` to see what you changed, and `G` against `E` to see what they changed. It then attempts to apply both sets of changes to `E` simultaneously. If the changes do not overlap on the same lines, Git successfully creates a new **merge commit** (`H`). This commit is unique: it has two parents.

> **Pause and predict**: What do you think happens if both branch `main` and branch `feature/rbac` modified the exact same `subjects` list in a RoleBinding manifest, but added different users? How will Git's three-way merge handle this specific scenario?

### The Merge Base and Recursive Strategies

The true genius of Git lies in how it finds the merge base. When histories are complex, with branches crossing and merging multiple times, finding the optimal common ancestor is computationally difficult.

By default, Git uses the **recursive** strategy (specifically, the `ort` strategy in modern Git versions, which stands for "Ostensibly Recursive's Twin"). If Git finds multiple potential common ancestors, it creates a temporary, virtual merge commit of those ancestors, and uses *that* as the merge base for your actual merge.

Let's look at how Git analyzes changes.

| Change Type | Branch A (main) vs Base | Branch B (feature) vs Base | Git's Action during Merge |
| :--- | :--- | :--- | :--- |
| File added | Not present | Added | File is added |
| File modified | Unchanged | Modified | Modification applied |
| File deleted | Deleted | Unchanged | File remains deleted |
| File modified | Modified (Line 10) | Modified (Line 50) | Both modifications applied |
| File modified | Modified (Line 20) | Modified (Line 20) | **CONFLICT** |

If you ever need to manually verify what Git considers the merge base before attempting a risky merge, you can use:

```bash
git merge-base main feature/ingress-update
```
This returns the commit hash of the optimal common ancestor.

> **Pause and predict**: Look at the following branch topology:
> ```mermaid
> gitGraph
>    commit id: "A"
>    commit id: "B"
>    branch feature/db
>    checkout main
>    commit id: "C"
>    commit id: "D"
>    checkout feature/db
>    commit id: "E"
>    commit id: "F"
>    branch feature/cache
>    checkout feature/cache
>    commit id: "G"
>    commit id: "H"
> ```
> If you are on `main` and run `git merge feature/cache`, which commit is the merge base? 
> 
> *Answer*: The merge base is commit `B`. To find it, trace backwards from `main` (commit D) and `feature/cache` (commit H) until their paths intersect. They first meet at `B`, making it the common ancestor used for the three-way merge.

### Conflict Resolution in Infrastructure-as-Code: Multi-File Complexity

Conflicts are not errors; they are Git asking for human judgment because its mathematical models cannot safely guess your intent.

In Kubernetes infrastructure, conflicts rarely occur in isolation. Because resources are often linked via tools like Kustomize or Helm, modifying an architecture usually means touching multiple files. Resolving a multi-file conflict incorrectly can result in valid Git history but fundamentally broken infrastructure state.

Let's walk through a complex, multi-file conflict scenario.

#### The Scenario
Team Alpha is working on branch `feature/ha-redis`. Team Beta is working on branch `feature/redis-auth`.
Both teams modify `redis-deployment.yaml` and the `kustomization.yaml` file that orchestrates the deployment.

Team Alpha's changes (`feature/ha-redis`):
Modified `redis-deployment.yaml` for High Availability:
```yaml
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: redis
        image: redis:7.0.11-alpine
```
Modified `kustomization.yaml` to add global labeling:
```yaml
resources:
- redis-deployment.yaml
commonLabels:
  high-availability: "true"
```

Team Beta's changes (`feature/redis-auth`):
Modified `redis-deployment.yaml` for authentication:
```yaml
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: redis
        image: redis:7.0.11
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: password
```
Modified `kustomization.yaml` to generate the required secret:
```yaml
resources:
- redis-deployment.yaml
secretGenerator:
- name: redis-secret
  literals:
  - password=supersecret
```

When you attempt to merge `feature/redis-auth` into `feature/ha-redis`, Git halts on multiple files simultaneously.

```bash
git checkout feature/ha-redis
git merge feature/redis-auth
# Auto-merging redis-deployment.yaml
# CONFLICT (content): Merge conflict in redis-deployment.yaml
# Auto-merging kustomization.yaml
# CONFLICT (content): Merge conflict in kustomization.yaml
# Automatic merge failed; fix conflicts and then commit the result.
```

#### The Resolution Process

1. **Understand the markers:**
   - `<<<<<<< HEAD`: The start of your current branch's changes.
   - `=======`: The separator between the two conflicting changes.
   - `>>>>>>> feature/redis-auth`: The end of the incoming branch's changes.

2. **Determine the desired outcome across all files:**
   We want High Availability (replicas: 3) AND authentication (env vars). For the infrastructure to actually work, the Kustomization file must include BOTH the `commonLabels` AND the `secretGenerator` so that the `redis-secret` referenced in the deployment actually exists.

3. **Edit the first file (`redis-deployment.yaml`):**
   Remove the markers and manually weave the YAML back together, paying extreme attention to the 2-space indentation rule.

```yaml
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: redis
        image: redis:7.0.11-alpine
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: password
```

4. **Edit the second file (`kustomization.yaml`):**
   Combine both configuration blocks to ensure the architecture remains sound.

```yaml
resources:
- redis-deployment.yaml
commonLabels:
  high-availability: "true"
secretGenerator:
- name: redis-secret
  literals:
  - password=supersecret
```

5. **Verify and Commit:**
   Never assume your manual YAML edit is valid, especially across multiple integrated files. Always validate before committing. You can use tools like `kubectl apply --dry-run=client` or `kustomize build`. Once verified, add both files and commit to finalize the merge.

```bash
# We will use 'k' as an alias for kubectl going forward
alias k=kubectl
kustomize build . | k apply -f - --dry-run=client

# If successful:
git add redis-deployment.yaml kustomization.yaml
git commit -m "Merge redis-auth, resolving multi-file replicas, image, and secret generator conflicts"
```

**War Story:** A junior DevOps engineer once resolved a similar multi-file conflict by perfectly fixing the Deployment YAML but accidentally running `git checkout --ours kustomization.yaml` to blindly bypass the second conflict. Git accepted the merge. The Deployment expected a secret that the Kustomization file was no longer generating. The pods crash-looped instantly in production, causing a complete loss of cache availability. Always resolve and validate multi-file conflicts holistically.

### The Octopus Merge: Taming Multiple Branches

Occasionally, a platform team needs to integrate several independent feature branches into a release candidate branch all at once. Doing this sequentially creates a messy, ladder-like history of merge commits.

Git provides a strategy called the **Octopus Merge**, which allows merging more than two branches into a single commit.

```mermaid
graph LR
    A((A)) --> B((B))
    B --> C((C: main))
    
    B --> D((D: b1))
    B --> E((E: b2))
    B --> F((F: b3))
    
    C --> G((G: Octopus Merge))
    D --> G
    E --> G
    F --> G
```

To perform an octopus merge:

```bash
git checkout release-v1.5
git merge feature/ingress feature/autoscaling feature/network-policies
```

> **Pause and predict**: What do you think happens if Git successfully merges `feature/ingress` and `feature/autoscaling`, but then detects a complex conflict when attempting to merge `feature/network-policies`? Will it pause and ask you to resolve it like a standard three-way merge?

**The All-or-Nothing Rule:** Unlike a standard two-branch merge which pauses mid-flight and leaves conflict markers in your working directory, an octopus merge will categorically refuse to complete if it encounters a conflict requiring manual resolution. It does not pause. If it fails, Git aborts the entire octopus merge automatically, leaving your working directory exactly as it was. It is designed solely for cleanly combining independent, non-overlapping development efforts. If it fails, you must fall back to sequential merging or resolve the conflicts between the specific branches before attempting again.

> **Stop and think**: If an octopus merge fails due to a conflict between `feature/autoscaling` and `feature/network-policies`, which approach would you choose:
A) Abandon the octopus merge entirely and merge all three sequentially.
B) Merge the two conflicting branches into each other first, resolve the conflict, and then retry the octopus merge with the updated branches.
Why is your chosen approach safer for maintaining a clean history?

### Branching Strategies for High-Velocity Teams

A merge strategy is only as good as the branching model that dictates when and where merges happen. Different models solve different organizational problems.

> **Stop and think**: Imagine you are advising a new platform team. They have 12 engineers, deploy to production twice a week, and have automated test coverage but it sometimes produces false positives. Which branching strategy would you recommend and why? Keep your answer in mind as you read the following models.

#### 1. GitFlow: The Legacy Enterprise Model
GitFlow uses strict isolation. It maintains a `main` branch (always production-ready) and a `develop` branch (integration). Features branch off `develop` and merge back. Releases branch off `develop`, undergo stabilization, and merge to both `main` and `develop`.

- **Pros:** Extremely rigid, explicit phases for QA and stabilization.
- **Cons:** Produces "merge hell." Feature branches live too long. It is fundamentally incompatible with Continuous Integration and Continuous Deployment (CI/CD) principles, as code sits unintegrated for weeks.

#### 2. GitHub Flow: The Web Application Standard
Everything branches off `main`. When a feature is ready, you open a Pull Request against `main`. Once reviewed and passing tests, it merges into `main` and deploys immediately.

- **Pros:** Simple, encourages small, short-lived branches, perfect for CI/CD.
- **Cons:** Requires rigorous automated testing. If your pipeline isn't rock-solid, a bad merge breaks production instantly.

#### 3. Trunk-Based Development: The Elite Standard
The defining characteristic of high-performing DevOps teams. Developers merge their code into `main` (the trunk) multiple times a day. Branches are either non-existent or last only a few hours.

```mermaid
gitGraph
   commit
   branch feature-1
   checkout feature-1
   commit
   checkout main
   merge feature-1
   branch feature-2
   checkout feature-2
   commit
   checkout main
   merge feature-2
   commit
```

- **Pros:** Eliminates merge hell entirely. Integration is continuous. Requires extensive use of feature flags to hide incomplete work in production.
- **Cons:** Extremely high barrier to entry. Requires advanced testing, feature flagging architecture, and high team discipline.

For Kubernetes platform teams building internal platforms, **Trunk-Based Development** paired with GitOps (like ArgoCD or Flux) is the gold standard. Long-lived feature branches containing infrastructure changes inevitably rot, because the underlying cluster state evolves out from under them.

## Did You Know?

1. Linus Torvalds originally designed Git's octopus merge specifically because he grew frustrated merging dozens of separate Linux kernel subsystem maintainer branches sequentially.
2. In Git version 2.33 (released August 2021), a completely new merge backend called `ort` (Ostensibly Recursive's Twin) was introduced, which mathematically processes large renames and complex merges up to 500x faster than the old recursive strategy.
3. The conflict marker symbols (`<<<<<<<`, `=======`, `>>>>>>>`) predate Git by decades. They were established by the `merge` program developed at Bell Labs in the late 1980s for the RCS version control system.
4. Git allows you to configure specific merge drivers for different file types via `.gitattributes`. You could theoretically write a custom merge driver specifically designed to intelligently merge Kubernetes YAML files without breaking indentation, though maintaining it is notoriously difficult.

## Common Mistakes

| Mistake | Why It Happens | How to Fix It |
| :--- | :--- | :--- |
| **Panic committing unresolved markers** | Engineer feels overwhelmed, attempts to save work mid-conflict by running `git commit -a`, thereby committing `<<<<<<<` directly into the codebase. | Run `git merge --abort` immediately to reset the working directory to the pre-merge state, take a breath, and start over. |
| **Breaking YAML indentation** | Manually deleting conflict markers and inadvertently shifting blocks of YAML, creating invalid structural relationships. | Always use `kubectl diff` or `kubectl apply --dry-run=client` on the modified file before finalizing the merge commit. |
| **"Ostrich merging" (ignoring upstream)** | Keeping a feature branch alive for 6 weeks without pulling from main, resulting in a monolithic, unresolvable conflict later. | Merge `main` into your feature branch (or rebase against it) daily. Conflict resolution should be a continuous, small-scale tax, not a massive end-of-project penalty. |
| **Resolving logic, breaking syntax** | Focusing so hard on getting both sets of configuration into the file that you create duplicate keys (e.g., two `spec` blocks in a pod definition). | Understand the schema of the file you are editing. Use IDE plugins with Kubernetes schema validation enabled during conflict resolution. |
| **Accidental "Evil Merges"** | While resolving a conflict, the engineer sneaks in an unrelated fix or typo correction that was not part of either branch. | A merge commit should *only* contain the resolution of the conflict. Make unrelated fixes in a separate, discrete commit afterward. |
| **Deleting the wrong side** | Misunderstanding `HEAD` vs the incoming branch, and blindly choosing "Accept Current Change" when the incoming branch contained critical security patches. | Read the code inside the markers. Never trust automated UI buttons in IDEs without verifying what exact lines will survive the merge. |

> **Stop and think**: Review the mistakes in the table above. Which of these would cause the most catastrophic failure in your current team's specific context? Rank them by potential severity based on your deployment pipeline's safeguards (or lack thereof).

## Quiz

<details>
<summary>Question 1: Your team is practicing Trunk-Based Development. You have been working on a new Kubernetes network policy for about 4 hours on a local branch. When you attempt to push to main, Git rejects it, stating the remote contains work you do not have. What is the safest sequence of actions to integrate your work?</summary>
To safely integrate your work without creating a messy history, you should fetch the remote changes and perform a rebase by running `git pull --rebase origin main`. This command first fetches the new commits from the remote `main` branch and temporarily rewinds your local network policy commits. It then applies the incoming commits from your team, and finally replays your 4 hours of work on top of the newly updated history. Doing this maintains a strictly linear and clean project history, which is critical in Trunk-Based Development to avoid unnecessary and confusing merge commits for short-lived local changes.
</details>

<details>
<summary>Question 2: You trigger an automated pipeline that attempts an octopus merge, integrating four different microservice deployment updates into a staging branch. Git halts and reports a conflict between two of the branches. What happens to the staging branch in this exact moment, and how is the pipeline affected?</summary>
In this exact moment, nothing happens to the staging branch because an octopus merge is an all-or-nothing operation designed for independent branches. Unlike a standard two-branch merge that pauses mid-flight and leaves conflict markers in your working directory, Git will completely abort the octopus merge automatically upon detecting any conflict. It immediately resets your working directory and staging branch back to their exact pre-merge state. This built-in safety mechanism is highly beneficial for automated pipelines, as it prevents CI/CD systems from becoming trapped in complex, multi-dimensional conflict states that require manual human intervention.
</details>

<details>
<summary>Question 3: A junior engineer just resolved a massive 500-line multi-file conflict involving a StatefulSet and a ConfigMap, and you need to review their work. Looking at the standard full file diff is overwhelming and includes unrelated changes. How can you, as a reviewer, isolate and view *only* the specific manual conflict resolutions the engineer made?</summary>
You can isolate the manual conflict resolutions by inspecting the merge commit itself using the `git show <merge-commit-hash>` command. When you run this on a merge commit, Git displays a specialized "combined diff" instead of a standard linear diff. This combined diff intelligently filters the output to only show the specific lines that were modified differently from *both* parent branches, highlighting exactly where the engineer's manual resolution deviated from what Git's automatic merge would have attempted. This provides the precise, surgical view required to audit complex manual conflict resolutions without being drowned in the noise of unrelated feature changes.
</details>

<details>
<summary>Question 4: An incident occurs in production because a `ConfigMap` update was inexplicably lost during a recent deployment. Looking at the Git history, you see a merge commit connecting a feature branch to main. The file changed on both branches, but the feature branch's changes are completely missing in the final merge commit. What likely happened during the conflict resolution?</summary>
The engineer performing the merge likely encountered a complex conflict within the `ConfigMap`, became overwhelmed, and mistakenly opted to completely overwrite the incoming changes. They probably used a command like `git checkout --ours configmap.yaml` or blindly clicked "Accept Current Changes" in their IDE's conflict resolution interface. By doing so, they entirely discarded the valid configuration updates from the feature branch while keeping their own, and then finalized the merge commit without realizing the loss of data. This scenario underscores exactly why a visual inspection and validation of the final merged files (such as using `kubectl diff`) is absolutely mandatory before committing a resolved conflict.
</details>

<details>
<summary>Question 5: Your organization is adopting GitOps with ArgoCD to manage Kubernetes clusters, but the QA team insists on keeping the legacy GitFlow branching model with long-lived `develop` and release branches. Why will this combination inevitably lead to deployment failures and configuration drift?</summary>
This combination will fail because GitFlow isolates infrastructure changes in long-lived branches for extended periods, which fundamentally violates the core philosophy of GitOps. In a proper GitOps architecture, the main branch of the Git repository must serve as the absolute, real-time source of truth for the cluster's state. When changes sit unmerged in a `develop` branch for weeks, the actual cluster state inevitably drifts as other hotfixes or updates are applied directly to the mainline. This severe divergence makes rapid, predictable iteration impossible and practically guarantees massive, unresolvable merge conflicts when the long-lived branches are finally integrated.
</details>

<details>
<summary>Question 6: You are tasked with taking over a legacy `feature/database-migration` branch that was abandoned by a former employee. Before attempting to integrate it, you run `git merge-base main feature/database-migration` and it returns a commit hash from 8 months ago. What does this immediately tell you about the risk profile of this impending merge, and how should you proceed?</summary>
The exceptionally old merge base immediately tells you that the risk profile for this integration is critically high, as the mathematical distance between the two branches almost guarantees massive, systemic conflicts. Because the feature branch has been completely isolated from the mainline for 8 months, the semantic logic and underlying architecture of the project have likely evolved significantly, rendering the old code incompatible even if it merges cleanly at a text level. Instead of attempting a direct three-way merge, you should abandon that approach and deeply analyze the legacy branch's intent. The safest path forward is to either cherry-pick the relevant functional commits or rebuild the migration logic from scratch against the modern trunk.
</details>

## Hands-On Exercise

In this exercise, you will intentionally create a complex three-way conflict within a Kubernetes deployment manifest, resolve it manually ensuring structural integrity, and validate the result.

### Setup Instructions

1. Create a fresh Git repository and initialize a baseline manifest.
   ```bash
   mkdir k8s-merge-lab && cd k8s-merge-lab
   git init
   ```

2. Create the baseline `deployment.yaml`.
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: api-server
   spec:
     replicas: 2
     template:
       spec:
         containers:
         - name: api
           image: nginx:1.20
   ```

3. Commit the baseline.
   ```bash
   git add deployment.yaml
   git commit -m "chore: initial api deployment"
   ```

### Tasks

1. **Create the Scale Branch:** Create a branch named `feature/scale-up`. Modify the `replicas` count to `5` and commit the change.
2. **Create the Image Update Branch:** Switch back to `main`. Create a new branch named `feature/update-image`. Modify the `image` to `nginx:1.24` and commit the change.
3. **Trigger the Conflict:** Switch back to the `feature/scale-up` branch. Attempt to merge `feature/update-image` into your current branch.
4. **Resolve the Conflict:** Open `deployment.yaml`. You will see conflict markers. Manually resolve the file so that the final state has BOTH `replicas: 5` and `image: nginx:1.24`.
5. **Validate the YAML:** Use the Kubernetes client dry-run feature to ensure your resolved YAML is valid before committing.
6. **Finalize the Merge:** Add the resolved file and finalize the merge commit.

### Solutions and Success Criteria

<details>
<summary>View Solutions</summary>

**Task 1: Create the Scale Branch**
```bash
git checkout -b feature/scale-up
sed -i.bak 's/replicas: 2/replicas: 5/g' deployment.yaml && rm deployment.yaml.bak
git add deployment.yaml
git commit -m "feat: scale api to 5 replicas"
```

**Task 2: Create the Image Update Branch**
```bash
git checkout main
git checkout -b feature/update-image
sed -i.bak 's/image: nginx:1.20/image: nginx:1.24/g' deployment.yaml && rm deployment.yaml.bak
git add deployment.yaml
git commit -m "chore: update nginx to 1.24"
```

**Task 3: Trigger the Conflict**
```bash
git checkout feature/scale-up
git merge feature/update-image
# Output will show CONFLICT (content)
```

**Task 4: Resolve the Conflict**
Open `deployment.yaml` in your editor. It will look similar to this:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
<<<<<<< HEAD
  replicas: 5
  template:
    spec:
      containers:
      - name: api
        image: nginx:1.20
=======
  replicas: 2
  template:
    spec:
      containers:
      - name: api
        image: nginx:1.24
>>>>>>> feature/update-image
```

Edit the file to remove markers and combine the desired state:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 5
  template:
    spec:
      containers:
      - name: api
        image: nginx:1.24
```

**Task 5: Validate the YAML**
```bash
k apply -f deployment.yaml --dry-run=client
# Expect output: deployment.apps/api-server created (dry run)
```

**Task 6: Finalize the Merge**
```bash
git add deployment.yaml
git commit -m "Merge branch 'feature/update-image' into feature/scale-up resolving replicas and image"
```

</details>

**Success Criteria:**
- [ ] Running `git log --graph --oneline` shows a branching path that converges with a merge commit.
- [ ] `cat deployment.yaml` shows no `<<<<<<<` markers.
- [ ] The file contains exactly `replicas: 5` and `image: nginx:1.24`.
- [ ] The YAML indentation is perfectly aligned (2 spaces per level).
- [ ] Running `kubectl apply -f deployment.yaml --dry-run=client` reports success.

## Next Module