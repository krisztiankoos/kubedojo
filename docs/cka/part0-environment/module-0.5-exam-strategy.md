# Module 0.5: Exam Strategy - Three-Pass Method

> **Complexity**: `[QUICK]` - Strategy, not technical skills
>
> **Time to Complete**: 15-20 minutes to read, lifetime to master
>
> **Prerequisites**: Modules 0.1-0.4

---

## Why This Module Matters

You can know Kubernetes perfectly and still fail the CKA.

How? Time.

16 questions. 120 minutes. That's 7.5 minutes average per question. But questions aren't equal—some take 2 minutes, others take 15. If you spend 15 minutes on a hard question first and don't finish the easy ones, you've thrown away points.

The **Three-Pass Method** is a strategy that maximizes your score regardless of question difficulty.

---

## The Problem: Linear Thinking

Most people approach exams linearly:

```
Question 1 → Question 2 → Question 3 → ... → Question 16
```

This fails when:
- Question 3 is a 15-minute troubleshooting nightmare
- You spend 20 minutes on it (perfectionism)
- You rush through Questions 14-16
- You miss easy points you could have gotten

The CKA passing score is **66%**. You don't need perfect—you need efficient.

---

## The Solution: Three-Pass Method

Instead of linear, work in passes:

```
┌─────────────────────────────────────────────────────────────────┐
│                     THE THREE-PASS METHOD                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PASS 1: QUICK WINS (1-3 minutes each)                          │
│  ├── Scan ALL 16 questions first                                │
│  ├── Do every task you can complete quickly                     │
│  ├── Skip anything that looks complex                           │
│  └── Goal: Secure easy points, bank time                        │
│                                                                  │
│  PASS 2: MEDIUM TASKS (4-6 minutes each)                        │
│  ├── Return to skipped questions                                │
│  ├── Do tasks requiring moderate effort                         │
│  ├── Skip if stuck after 5-6 minutes                            │
│  └── Goal: Steady progress                                      │
│                                                                  │
│  PASS 3: COMPLEX TASKS (remaining time)                         │
│  ├── Tackle the hardest questions last                          │
│  ├── Use ALL remaining time                                     │
│  ├── Partial solutions get partial credit                       │
│  └── Goal: Maximize remaining points                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Recognizing Task Complexity

Before you can use the three-pass method, you need to instantly categorize questions.

### Quick Wins (1-3 minutes)

**Indicators**:
- "Create a Pod/Deployment/Service"
- "Add a label to..."
- "Scale deployment to..."
- "Expose service on port..."
- Single-step operations
- Resources you create often

**Examples**:
- Create an nginx pod
- Add label `env=prod` to all pods in namespace
- Scale deployment `web` to 5 replicas
- Create a NodePort service for deployment `api`

### Medium Tasks (4-6 minutes)

**Indicators**:
- "Configure RBAC..."
- "Create a NetworkPolicy..."
- "Set up a PersistentVolumeClaim..."
- "Configure a ConfigMap and use it in..."
- Multi-step but straightforward
- Requires looking up syntax

**Examples**:
- Create Role and RoleBinding for user to list pods
- Create NetworkPolicy allowing only frontend pods to reach backend
- Create PVC and mount it in a pod
- Create ConfigMap and inject as environment variables

### Complex Tasks (8-15 minutes)

**Indicators**:
- "Troubleshoot why..."
- "Fix the broken..."
- "The cluster is not..."
- "Debug and resolve..."
- Multi-cluster or multi-step
- Requires investigation

**Examples**:
- Troubleshoot why pods are not scheduling
- Fix the broken deployment (something is wrong, figure it out)
- Node is NotReady, find and fix the issue
- Application cannot connect to database, resolve

---

## Part 2: Pass 1 - Quick Wins

### What To Do

1. **Start of exam**: Read through ALL 16 questions quickly (5 minutes)
2. **Identify quick wins**: Mark them mentally or on scratch paper
3. **Execute quick wins**: Do all easy questions first
4. **Don't get distracted**: If anything takes longer than expected, skip

### Time Budget

- Scan all questions: 5 minutes
- Quick wins (assume 4-6 questions): 15-20 minutes
- **Pass 1 total**: ~25 minutes

### Example Quick Wins

```yaml
# Question: Create a pod named 'web' running nginx in namespace 'production'
# Time: <1 minute

kubectl run web --image=nginx -n production

# Done. Next question.
```

```yaml
# Question: Scale deployment 'api' to 3 replicas
# Time: <30 seconds

kubectl scale deploy api --replicas=3

# Done. Next question.
```

```yaml
# Question: Create a ClusterIP service for deployment 'backend' on port 8080
# Time: <1 minute

kubectl expose deploy backend --port=8080

# Done. Next question.
```

### The Psychology

Quick wins build confidence. After Pass 1, you've already answered 4-6 questions correctly. That's potentially 25-35% of the exam done in 25 minutes. The pressure is off.

---

## Part 3: Pass 2 - Medium Tasks

### What To Do

1. **Return to skipped questions**: Start with the least complex
2. **Use documentation**: This is where kubernetes.io helps
3. **Time-box yourself**: If stuck after 5-6 minutes, move on
4. **Accept "good enough"**: Partial solutions > nothing

### Time Budget

- Medium tasks (assume 6-8 questions): 50-60 minutes
- **Pass 2 total**: ~55 minutes
- **Cumulative**: ~80 minutes (40 minutes remaining)

### Example Medium Tasks

```yaml
# Question: Create a NetworkPolicy that allows pods with label 'role=frontend'
#           to access pods with label 'role=backend' on port 3306

# Time: 4-5 minutes
# Strategy: Look up NetworkPolicy template, modify

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  podSelector:
    matchLabels:
      role: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - port: 3306
```

```yaml
# Question: Create a ServiceAccount 'app-sa', a Role that can list pods,
#           and bind them together

# Time: 5-6 minutes
# Strategy: kubectl create commands + YAML for binding

kubectl create serviceaccount app-sa
kubectl create role pod-reader --verb=get,list,watch --resource=pods
kubectl create rolebinding app-sa-binding --role=pod-reader --serviceaccount=default:app-sa
```

---

## Part 4: Pass 3 - Complex Tasks

### What To Do

1. **Use ALL remaining time**: No need to rush now
2. **Methodical troubleshooting**: Gather info → hypothesize → test
3. **Partial credit**: Fixing SOME of the issue is better than nothing
4. **Don't panic**: You've already secured most of your points

### Time Budget

- Complex tasks (assume 2-4 questions): 40 minutes
- **Pass 3 total**: ~40 minutes
- **Buffer**: 0 minutes (you've used all time strategically)

### Example Complex Task

```
Question: The deployment 'critical-app' in namespace 'production' is not
working correctly. Pods are in CrashLoopBackOff. Troubleshoot and fix.
```

**Troubleshooting Approach**:

```bash
# Step 1: Gather information (2 minutes)
kubectl get pods -n production
kubectl describe pod critical-app-xxx -n production
kubectl logs critical-app-xxx -n production
kubectl get events -n production --sort-by='.lastTimestamp'

# Step 2: Identify issue (from logs/events)
# Example: ConfigMap 'app-config' not found

# Step 3: Fix
kubectl get cm -n production  # Confirm it's missing
kubectl create configmap app-config --from-literal=KEY=value -n production

# Step 4: Verify
kubectl get pods -n production -w  # Watch until Running
```

### Partial Credit Strategy

If you can't fully solve a complex task:

1. **Fix what you can**: If 3 things are broken, fix 2
2. **Document your progress**: The grader may see partial work
3. **Don't leave it blank**: Any progress is better than none

---

## Part 5: Context Switching Discipline

Every CKA question specifies a cluster context. **This is critical.**

### The #1 Exam Mistake

Solving a problem on the wrong cluster. You do everything right, but on the wrong context. Zero points.

### The Rule

**EVERY question, FIRST action**: Switch context.

```bash
# At the start of EVERY question
kubectl config use-context <context-from-question>
```

Make it muscle memory. Read question → switch context → then solve.

### Verification

After switching:
```bash
kubectl config current-context
```

This takes 2 seconds. It can save 7 minutes of wasted work.

---

## Part 6: The "Good Enough" Mindset

Perfectionists fail the CKA. Here's why.

### Perfectionism Trap

```
Question: Create a deployment with 3 replicas, resource limits,
          health checks, and a ConfigMap volume

Perfectionist:
- Spends 10 minutes crafting perfect YAML
- Double-checks every field
- Adds optional best practices
- Runs out of time on other questions
```

### Good Enough Approach

```
Good Enough:
- Creates working deployment (3 minutes)
- Adds required fields only
- Verifies it works
- Moves on

Result: Same points, 7 minutes saved
```

### The 80% Rule

If your solution works and meets the requirements, it's done. Don't:
- Add "nice to have" features
- Refactor for cleanliness
- Add comments explaining your logic
- Double-check already-working solutions

---

## Part 7: Time Checkpoints

Set mental checkpoints during the exam:

| Time Elapsed | Checkpoint | Status Check |
|--------------|------------|--------------|
| 30 minutes | End of Pass 1 | Should have 4-6 questions done |
| 80 minutes | End of Pass 2 | Should have 10-12 questions done |
| 110 minutes | Pass 3 in progress | Working on complex tasks |
| 120 minutes | Exam ends | Submit |

If you're behind at a checkpoint, speed up. Skip more aggressively.

> **Success Story: From Failed to 89%**
>
> A candidate failed their first CKA attempt with 58%. They'd spent 18 minutes on a troubleshooting question in the first pass, then rushed through everything else. On their second attempt, they used the three-pass method religiously. Pass 1: 6 questions in 22 minutes. Pass 2: 7 questions in 50 minutes. Pass 3: 3 complex questions with 48 minutes remaining. Final score: 89%. Same knowledge, different strategy, completely different outcome.

---

## Part 8: Pre-Exam Routine

### 5 Minutes Before

1. **Environment ready**: Water, quiet space, ID
2. **Mental state**: Calm, focused, confident
3. **Remember**: Three-pass method. Quick wins first.

### First 5 Minutes of Exam

1. **Read ALL questions**: Don't start solving yet
2. **Categorize mentally**: Quick / Medium / Complex
3. **Plan your passes**: Know which questions you'll hit first
4. **Set up aliases**: If not pre-configured

### Last 5 Minutes of Exam

1. **Don't start new complex tasks**: Not enough time
2. **Verify critical answers**: Quick sanity checks
3. **Submit any partial work**: Something > nothing
4. **Breathe**: You did your best

---

## Did You Know?

- **66% is passing**. That means you can get 5-6 questions completely wrong and still pass. The three-pass method ensures you don't leave easy points on the table.

- **Partial credit exists**. If a question is worth 7 points and you get 4 things right, you might get 4 points. Always attempt something.

- **The exam is designed to be hard**. The Linux Foundation expects many people to run out of time. Your strategy matters as much as your knowledge.

- **Second attempts are allowed**. If you fail, you get one free retake with your exam purchase. This isn't the end of the world.

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Starting with Question 1 | Might be hard | Scan all first, pick easy ones |
| Perfectionism | Time waste | "Good enough" mindset |
| Wrong context | Zero points | Always switch context first |
| Stuck on hard question | Time drain | Skip after 5-6 minutes, return later |
| Not using remaining time | Leaving points | Use ALL time on complex tasks |
| Panicking | Poor decisions | Trust your preparation |

---

## Quiz

1. **You're at 30 minutes and have only finished 2 questions. What do you do?**
   <details>
   <summary>Answer</summary>
   You're behind. Immediately switch to easier questions (Pass 1). Skip anything that's taking too long. Recover time by focusing on quick wins only.
   </details>

2. **A question asks you to troubleshoot a broken deployment. How do you categorize it?**
   <details>
   <summary>Answer</summary>
   Complex (Pass 3). "Troubleshoot" questions require investigation and are unpredictable in time. Save for last when you have remaining time to spend.
   </details>

3. **What's the FIRST thing you do when starting any question?**
   <details>
   <summary>Answer</summary>
   Switch to the correct context. `kubectl config use-context <context>`. This prevents solving problems on the wrong cluster.
   </details>

4. **You've partially solved a complex question but time is running out. What do you do?**
   <details>
   <summary>Answer</summary>
   Leave your partial solution. Partial credit is possible. Move on to the next question if there's one you can finish completely, otherwise keep working on this one.
   </details>

---

## Hands-On Exercise

**Task**: Practice categorizing questions and timing yourself.

### Exercise 1: Question Categorization

Categorize these sample CKA questions as `[QUICK]`, `[MEDIUM]`, or `[COMPLEX]`:

1. Create a pod named `nginx` running the `nginx:1.25` image
2. The deployment `web-app` is not starting. Pods show `CrashLoopBackOff`. Find and fix the issue.
3. Scale the deployment `api` to 5 replicas
4. Create a NetworkPolicy that allows pods with label `role=frontend` to access pods with label `role=db` on port 3306
5. Create a ClusterRole that allows listing and getting pods, and bind it to user `developer`
6. Node `worker-02` is in `NotReady` state. Troubleshoot and fix.
7. Add the label `env=production` to all pods in namespace `app`
8. Create a PersistentVolumeClaim requesting 5Gi storage with `ReadWriteOnce` access mode

<details>
<summary>Answers</summary>

1. `[QUICK]` - Single kubectl command
2. `[COMPLEX]` - Requires investigation
3. `[QUICK]` - Single kubectl command
4. `[MEDIUM]` - Requires YAML, but straightforward
5. `[MEDIUM]` - Multi-step but documented
6. `[COMPLEX]` - Troubleshooting required
7. `[QUICK]` - Single kubectl command with selector
8. `[MEDIUM]` - Requires YAML template

</details>

### Exercise 2: Timed Practice

Set a timer and practice:

1. **2 minutes**: Create a deployment with 3 replicas and expose it
2. **5 minutes**: Create a complete RBAC setup (Role, RoleBinding, ServiceAccount)
3. **3 minutes**: Create a NetworkPolicy from documentation

**Success Criteria**:
- [ ] Can categorize question complexity in <10 seconds
- [ ] Understand which pass each question belongs to
- [ ] Can execute quick wins without hesitation

---

## Summary: Three-Pass Reference Card

```
╔═══════════════════════════════════════════════════════════════╗
║               THREE-PASS EXAM STRATEGY                         ║
╠═══════════════════════════════════════════════════════════════╣
║                                                                ║
║  BEFORE SOLVING: Read ALL 16 questions (5 min)                 ║
║                                                                ║
║  PASS 1: QUICK WINS                                            ║
║  • 1-3 min tasks                                               ║
║  • Create, scale, label, expose                                ║
║  • Target: ~25 min for 4-6 questions                           ║
║                                                                ║
║  PASS 2: MEDIUM TASKS                                          ║
║  • 4-6 min tasks                                               ║
║  • RBAC, NetworkPolicy, PVC, ConfigMap                         ║
║  • Target: ~55 min for 6-8 questions                           ║
║                                                                ║
║  PASS 3: COMPLEX TASKS                                         ║
║  • 8-15 min tasks                                              ║
║  • Troubleshooting, multi-step, debugging                      ║
║  • Target: ~40 min for remaining questions                     ║
║                                                                ║
║  ALWAYS: Switch context first. Good enough > perfect.          ║
║                                                                ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Next Steps

Congratulations! You've completed **Part 0: Environment & Exam Technique**.

You now have:
- ✅ A working multi-node Kubernetes cluster
- ✅ Optimized shell with aliases and autocomplete
- ✅ Vim configured for YAML editing
- ✅ Knowledge of where to find documentation fast
- ✅ A strategy to maximize your exam score

**Next**: [Part 1: Cluster Architecture, Installation & Configuration](../part1-cluster-architecture/)

This is where the real Kubernetes learning begins.
