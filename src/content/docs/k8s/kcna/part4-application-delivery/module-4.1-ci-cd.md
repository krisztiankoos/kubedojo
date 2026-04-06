---
title: "Module 4.1: CI/CD Fundamentals"
slug: k8s/kcna/part4-application-delivery/module-4.1-ci-cd
sidebar:
  order: 2
---
> **Complexity**: `[MEDIUM]` - Delivery concepts
>
> **Time to Complete**: 25-30 minutes
>
> **Prerequisites**: Part 3 (Cloud Native Architecture)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Explain** the difference between Continuous Integration, Continuous Delivery, and Continuous Deployment
2. **Identify** the stages of a typical CI/CD pipeline and what each stage validates
3. **Compare** CI/CD tools (Jenkins, GitHub Actions, GitLab CI, Tekton) by architecture and use case
4. **Evaluate** GitOps as a deployment model and how it differs from traditional push-based CI/CD

---

## Why This Module Matters

Imagine launching a new feature, only for it to crash the entire application, costing your company hundreds of thousands of dollars in lost revenue and reputational damage. The stakes of software delivery are higher than ever. Modern software development isn't just about writing code; it's about *reliably and rapidly delivering* that code to users. **Continuous Integration** and **Continuous Delivery/Deployment** (CI/CD) are foundational practices designed to prevent such disasters by automating the journey of code from development to production, ensuring quality and speed. KCNA tests your understanding of these critical concepts because they underpin effective, modern cloud-native operations.

---

## What is CI/CD?

```
┌─────────────────────────────────────────────────────────────┐
│              CI/CD OVERVIEW                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CONTINUOUS INTEGRATION (CI)                               │
│  ─────────────────────────────────────────────────────────  │
│  Frequently merge code changes into a shared repository   │
│  Automatically build and test each change                 │
│                                                             │
│  Code → Build → Test → Merge                              │
│                                                             │
│  CONTINUOUS DELIVERY (CD)                                 │
│  ─────────────────────────────────────────────────────────  │
│  Automatically prepare code for release to production     │
│  Deployment is manual (button click)                      │
│                                                             │
│  CI → Package → Stage → [Manual Deploy]                  │
│                                                             │
│  CONTINUOUS DEPLOYMENT (CD)                               │
│  ─────────────────────────────────────────────────────────  │
│  Automatically deploy every change to production         │
│  No manual intervention                                   │
│                                                             │
│  The difference:                                          │
│  • Continuous Delivery: CAN deploy at any time           │
│  • Continuous Deployment: DOES deploy automatically      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## CI/CD Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│              CI/CD PIPELINE                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Code                                                      │
│    │                                                       │
│    ▼                                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. SOURCE                                          │   │
│  │     Developer commits code to Git                   │   │
│  │     Triggers pipeline                               │   │
│  └─────────────────────────────────────────────────────┘   │
│    │                                                       │
│    ▼                                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  2. BUILD                                           │   │
│  │     Compile code, resolve dependencies             │   │
│  │     Create container image                          │   │
│  └─────────────────────────────────────────────────────┘   │
│    │                                                       │
│    ▼                                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  3. TEST                                            │   │
│  │     Unit tests, integration tests                   │   │
│  │     Security scans, linting                         │   │
│  └─────────────────────────────────────────────────────┘   │
│    │                                                       │
│    ▼                                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  4. PACKAGE                                         │   │
│  │     Push container image to registry               │   │
│  │     Create Helm chart/manifests                    │   │
│  └─────────────────────────────────────────────────────┘   │
│    │                                                       │
│    ▼                                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  5. DEPLOY                                          │   │
│  │     Deploy to staging/production                    │   │
│  │     Run smoke tests                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│    │                                                       │
│    ▼                                                       │
│  Production                                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Pause and predict**: Continuous Delivery means code is always ready to deploy (manual trigger). Continuous Deployment means every change deploys automatically. Which one requires more confidence in your automated tests? What could happen if you adopt Continuous Deployment with inadequate test coverage?

## Container Registries

Container images are fundamental to modern cloud-native applications. Once your CI pipeline has successfully built and tested an image (the **PACKAGE** stage), it needs a place to be stored and managed before deployment. This is the role of a container registry.

```
┌─────────────────────────────────────────────────────────────┐
│              CONTAINER REGISTRIES                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Where container images are stored                        │
│                                                             │
│  CI builds image → Push to registry → K8s pulls image    │
│                                                             │
│  Public registries:                                       │
│  ─────────────────────────────────────────────────────────  │
│  • Docker Hub (docker.io)                                │
│  • GitHub Container Registry (ghcr.io)                   │
│  • Google Container Registry (gcr.io)                    │
│  • Quay.io                                               │
│                                                             │
│  Private registries:                                      │
│  ─────────────────────────────────────────────────────────  │
│  • Harbor (CNCF Graduated)                               │
│  • AWS ECR                                               │
│  • Azure ACR                                             │
│  • Google Artifact Registry                              │
│                                                             │
│  Harbor features:                                         │
│  • Vulnerability scanning                                 │
│  • Image signing                                          │
│  • Role-based access                                      │
│  • Replication                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## CI/CD Benefits

```
┌─────────────────────────────────────────────────────────────┐
│              CI/CD BENEFITS                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  WITHOUT CI/CD:                                            │
│  ─────────────────────────────────────────────────────────  │
│  • Manual builds ("works on my machine")                  │
│  • Infrequent releases (big bang)                        │
│  • Manual testing (error-prone)                          │
│  • Long feedback loops                                    │
│  • Risky deployments                                      │
│                                                             │
│  WITH CI/CD:                                              │
│  ─────────────────────────────────────────────────────────  │
│  • Automated builds (reproducible)                       │
│  • Frequent releases (small changes)                     │
│  • Automated testing (consistent)                        │
│  • Fast feedback (minutes, not days)                     │
│  • Safe deployments (rollback ready)                     │
│                                                             │
│  Key metrics:                                              │
│  ─────────────────────────────────────────────────────────  │
│  • Deployment frequency (how often)                       │
│  • Lead time (commit to production)                       │
│  • Change failure rate (% that cause issues)             │
│  • Mean time to recovery (fix production issues)         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## CI/CD Tools

### General CI/CD Platforms

| Tool | Description |
|------|-------------|
| **Jenkins** | Self-hosted, highly customizable |
| **GitHub Actions** | Built into GitHub |
| **GitLab CI** | Built into GitLab |
| **CircleCI** | Cloud-native CI/CD |
| **Travis CI** | Simple CI/CD |

### Kubernetes-Native CI/CD

```
┌─────────────────────────────────────────────────────────────┐
│              KUBERNETES-NATIVE CI/CD                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TEKTON (CNCF)                                            │
│  ─────────────────────────────────────────────────────────  │
│  • CI/CD as Kubernetes resources                          │
│  • Tasks, Pipelines, PipelineRuns                        │
│  • Cloud-native, serverless                               │
│                                                             │
│  ARGO CD (CNCF Graduated)                                 │
│  ─────────────────────────────────────────────────────────  │
│  • GitOps continuous delivery                             │
│  • Declarative, Git as source of truth                   │
│  • Sync cluster state with Git                           │
│                                                             │
│  FLUX (CNCF Graduated)                                    │
│  ─────────────────────────────────────────────────────────  │
│  • GitOps continuous delivery                             │
│  • Similar to Argo CD                                     │
│  • Tight Helm integration                                │
│                                                             │
│  ARGO WORKFLOWS (CNCF)                                    │
│  ─────────────────────────────────────────────────────────  │
│  • Workflow engine for Kubernetes                        │
│  • DAG-based workflows                                    │
│  • CI/CD and data pipelines                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## GitOps vs Traditional CI/CD

```
┌─────────────────────────────────────────────────────────────┐
│              GITOPS vs TRADITIONAL CI/CD                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TRADITIONAL (Push-based):                                │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Git → CI Server → Push to Cluster                        │
│                                                             │
│  ┌──────┐    ┌─────────┐    ┌─────────────┐              │
│  │ Git  │ →  │   CI    │ →  │  Cluster    │              │
│  │      │    │ Server  │    │             │              │
│  └──────┘    └─────────┘    └─────────────┘              │
│                                                             │
│  • CI needs cluster credentials                           │
│  • External system pushes changes                         │
│                                                             │
│  GITOPS (Pull-based):                                     │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Git ← Pull from Cluster                                  │
│                                                             │
│  ┌──────┐              ┌─────────────┐                    │
│  │ Git  │ ←────────── │  Cluster    │                    │
│  │      │   agent     │  (Argo CD)  │                    │
│  └──────┘   pulls     └─────────────┘                    │
│                                                             │
│  • Cluster pulls from Git                                 │
│  • No external access needed                              │
│  • Git = source of truth                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
> **Analogy**: Think of a busy restaurant kitchen. In a **traditional push-based** system, the chef (CI Server) cooks a dish and then *forces* it onto a waiting customer's (Kubernetes Cluster) table. This means the chef needs direct access to every customer's table, and if the chef is messy or makes a mistake, the customer directly experiences it.
>
> In a **GitOps pull-based** system, the chef cooks the dish, places it on a clean pass (your Git repository), and a dedicated waiter (Argo CD or Flux, running inside the cluster) constantly checks the pass. The waiter only takes dishes *when the customer's table is ready* and matches the order specified on the pass. The chef never directly touches the customer's table. This approach makes the delivery process more secure, transparent, and ensures the "customer's table" is always in the desired state.

---

## Deployment Strategies

When it's time to actually roll out a new version of your application to production, how do you do it? The way you approach this "deployment" aspect of Continuous Delivery/Deployment is crucial for minimizing downtime, reducing risk, and ensuring a smooth user experience. Let's explore common deployment strategies.

```
┌─────────────────────────────────────────────────────────────┐
│              DEPLOYMENT STRATEGIES                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ROLLING UPDATE (Kubernetes default)                      │
│  ─────────────────────────────────────────────────────────  │
│  Gradually replace old pods with new                      │
│                                                             │
│  [v1][v1][v1] → [v1][v1][v2] → [v1][v2][v2] → [v2][v2][v2]│
│                                                             │
│  + Zero downtime                                          │
│  + Simple                                                  │
│  - Slow rollback                                          │
│                                                             │
│  BLUE-GREEN                                               │
│  ─────────────────────────────────────────────────────────  │
│  Run both versions, switch traffic instantly              │
│                                                             │
│  [Blue v1] ← traffic     [Blue v1]                        │
│  [Green v2]         →    [Green v2] ← traffic             │
│                                                             │
│  + Instant rollback                                       │
│  + Full testing before switch                             │
│  - Double resources needed                                │
│                                                             │
│  CANARY                                                   │
│  ─────────────────────────────────────────────────────────  │
│  Route small % of traffic to new version                  │
│                                                             │
│  [v1][v1][v1] ← 90% traffic                              │
│  [v2]         ← 10% traffic (canary)                     │
│                                                             │
│  + Test with real traffic                                 │
│  + Gradual rollout                                        │
│  + Quick rollback (just remove canary)                   │
│  - More complex setup                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **Stop and think**: In a canary deployment, only 10% of users see the new version initially. If the canary shows increased error rates, you roll back and only 10% of users were affected. In a rolling update, by the time you notice problems, 50% of Pods may already be running the new version. How does this difference in blast radius affect which strategy you choose for a risky change?

### Strategy Comparison

| Strategy | Downtime | Rollback | Resource Cost | Complexity |
|----------|----------|----------|---------------|------------|
| **Rolling** | None | Slow | Normal | Low |
| **Blue-Green** | None | Instant | 2x during deploy | Medium |
| **Canary** | None | Fast | Slight increase | High |
| **Recreate** | Yes | Slow | Normal | Lowest |

---

## Did You Know?

- **Continuous Deployment requires confidence** - You need comprehensive automated testing and monitoring to deploy every commit automatically.

- **GitOps was coined by Weaveworks** - The term and practice were popularized by Weaveworks, creators of Flux.

- **Canary comes from coal mining** - Miners used canaries to detect toxic gases. In deployments, a canary release detects issues with real traffic.

- **DORA metrics** - DevOps Research and Assessment (DORA) identified deployment frequency, lead time, change failure rate, and MTTR as key performance indicators.

---

## Common Mistakes

| Mistake | Why It Hurts | Correct Understanding |
|---------|--------------|----------------------|
| No automated tests | Broken deploys | Tests are essential for CI |
| Manual deployments | Inconsistent, error-prone | Automate everything |
| Big bang releases | High risk | Small, frequent changes |
| No rollback plan | Stuck with bad version | Always have rollback ready |

---

## Quiz

1. **Your team currently deploys by having a senior engineer SSH into a server and run deployment scripts manually. Deployments happen once a month and often fail. The CTO wants to move to CI/CD. What specific problems would a CI/CD pipeline solve, and what stages would you include?**
   <details>
   <summary>Answer</summary>
   The manual process causes: inconsistent builds ("works on my machine"), human error during deployment, infrequent releases that bundle many changes (making failures harder to diagnose), no automated testing, and dependence on one person. A CI/CD pipeline would include: Source (Git commit triggers pipeline), Build (compile code, build container image), Test (unit tests, integration tests, security scans), Package (push image to registry, create Helm chart), and Deploy (deploy to staging, run smoke tests, then production). This makes deployments reproducible, frequent, and safe -- turning monthly risky events into routine daily operations.
   </details>

2. **Your company uses a traditional push-based CI/CD pipeline where Jenkins has admin credentials to your production Kubernetes cluster. A security audit flags this as a risk. How would switching to GitOps with Argo CD or Flux improve the security posture?**
   <details>
   <summary>Answer</summary>
   In push-based CI/CD, Jenkins needs cluster admin credentials stored outside the cluster, creating a large attack surface -- if Jenkins is compromised, the attacker has production access. In GitOps, the agent (Argo CD or Flux) runs inside the cluster and pulls desired state from Git. No external system needs cluster credentials. The cluster reaches out to Git (read-only access), and all changes flow through Git where they are auditable, reviewable, and reversible via `git revert`. This eliminates the credential exposure problem and creates a complete audit trail of every change through Git history.
   </details>

3. **You are deploying a new payment processing feature to 2 million users. A colleague suggests a standard rolling update. Why might you choose a canary deployment instead, and what metrics would you monitor to decide whether to promote the canary?**
   <details>
   <summary>Answer</summary>
   A rolling update gradually replaces all Pods, and by the time you detect a problem, a significant percentage of users may be affected. A canary deployment limits the blast radius -- you send 5% of traffic (100,000 users) to the new version first. Monitor error rate (5xx responses compared to baseline), latency (p99 response time within acceptable bounds), and business metrics (payment success rate, conversion rate). If the canary shows degradation on any metric, you roll back instantly and only 5% of users were impacted. For a payment feature where errors mean lost revenue, the controlled exposure of canary deployment is worth the added complexity.
   </details>

4. **Your DORA metrics show: deployment frequency is once per week, lead time is 14 days, change failure rate is 25%, and mean time to recovery is 4 hours. Which metric is most concerning, and what would you address first?**
   <details>
   <summary>Answer</summary>
   The 25% change failure rate is most concerning -- one in four deployments causes problems. This suggests insufficient testing in the CI/CD pipeline. Address this first by adding comprehensive automated tests (unit, integration, and end-to-end) to the pipeline so failures are caught before production. Once the change failure rate drops, the team will gain confidence to deploy more frequently (improving deployment frequency) and with shorter lead times. Frequent small deployments are inherently less risky than infrequent large ones because each change is smaller and easier to diagnose and roll back.
   </details>

5. **A blue-green deployment runs both the old version (blue) and new version (green) simultaneously, then switches all traffic at once. What is the main advantage over a rolling update, and what is the biggest cost trade-off?**
   <details>
   <summary>Answer</summary>
   The main advantage is instant rollback. If the green version has problems after the traffic switch, you switch back to blue in seconds (just change the Service selector). With a rolling update, rollback means doing another rolling update in reverse, which takes minutes. The biggest trade-off is resource cost: blue-green requires double the resources during the switchover period (both versions running at full scale). For a service running 20 Pods, you need capacity for 40. This makes blue-green expensive for large services but ideal for breaking changes where you need the safety of instant rollback.
   </details>

---

## Summary

**CI/CD concepts**:
- **CI**: Integrate and test code frequently
- **CD (Delivery)**: Always ready to deploy
- **CD (Deployment)**: Auto-deploy everything

**Pipeline stages**:
Source → Build → Test → Package → Deploy

**Deployment strategies**:
- **Rolling**: Gradual replacement (default)
- **Blue-Green**: Switch traffic between versions
- **Canary**: Test with small traffic percentage

**GitOps**:
- Git = source of truth
- Pull-based (cluster pulls from Git)
- Tools: Argo CD, Flux

---

## Next Module

[Module 4.2: Application Packaging](../module-4.2-application-packaging/) - Helm, Kustomize, and other tools for packaging Kubernetes applications.