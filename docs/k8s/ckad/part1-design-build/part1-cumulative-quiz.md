# Part 1 Cumulative Quiz: Application Design and Build

> **Time Limit**: 25 minutes (simulating exam pressure)
>
> **Passing Score**: 80% (8/10 questions)

This quiz tests your mastery of:
- Container images
- Jobs and CronJobs
- Multi-container pods (sidecar, init, ambassador)
- Volumes (emptyDir, ConfigMap, Secret, PVC)

---

## Instructions

1. Try each question without looking at answers
2. Time yourself—speed matters for CKAD
3. Use only `kubectl` and `kubernetes.io/docs`
4. Check answers after completing all questions

---

## Questions

### Question 1: Image Pull Issue
**[2 minutes]**

A pod is stuck in `ImagePullBackOff`:

```bash
k get pods
# NAME      READY   STATUS             RESTARTS   AGE
# broken    0/1     ImagePullBackOff   0          5m
```

Identify the issue and fix it. The pod should run nginx version 1.21.

<details>
<summary>Answer</summary>

```bash
# Diagnose
k describe pod broken | grep -A5 Events
# Look for: failed to pull image

# Check current image
k get pod broken -o jsonpath='{.spec.containers[0].image}'
# Probably wrong tag or typo

# Fix (delete and recreate or patch)
k delete pod broken
k run broken --image=nginx:1.21
```

</details>

---

### Question 2: Create a Job
**[2 minutes]**

Create a Job named `backup-job` that:
- Uses image `busybox`
- Runs command `echo "Backup completed at $(date)"`
- Has a backoff limit of 2

<details>
<summary>Answer</summary>

```bash
# Generate and modify
k create job backup-job --image=busybox --dry-run=client -o yaml -- sh -c 'echo "Backup completed at $(date)"' > job.yaml

# Add backoffLimit: 2 to spec, then apply
# Or directly:
cat << 'EOF' | k apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: backup-job
spec:
  backoffLimit: 2
  template:
    spec:
      containers:
      - name: backup
        image: busybox
        command: ["sh", "-c", "echo Backup completed at $(date)"]
      restartPolicy: Never
EOF
```

</details>

---

### Question 3: CronJob Schedule
**[2 minutes]**

Create a CronJob named `cleanup` that:
- Runs every 30 minutes
- Uses image `busybox`
- Echoes "Cleanup running"
- Has `concurrencyPolicy: Forbid`

<details>
<summary>Answer</summary>

```bash
# Imperative then patch
k create cronjob cleanup --image=busybox --schedule="*/30 * * * *" -- echo "Cleanup running"
k patch cronjob cleanup -p '{"spec":{"concurrencyPolicy":"Forbid"}}'

# Or YAML:
cat << 'EOF' | k apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cleanup
spec:
  schedule: "*/30 * * * *"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleanup
            image: busybox
            command: ["echo", "Cleanup running"]
          restartPolicy: OnFailure
EOF
```

</details>

---

### Question 4: Multi-Container Pod
**[3 minutes]**

Create a pod named `sidecar-pod` with:
- Main container: `nginx` image
- Sidecar container: `busybox` image, running `tail -f /var/log/nginx/access.log`
- Both containers share a volume at `/var/log/nginx`

<details>
<summary>Answer</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-pod
spec:
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - name: logs
      mountPath: /var/log/nginx
  - name: sidecar
    image: busybox
    command: ["tail", "-f", "/var/log/nginx/access.log"]
    volumeMounts:
    - name: logs
      mountPath: /var/log/nginx
  volumes:
  - name: logs
    emptyDir: {}
```

```bash
k apply -f sidecar-pod.yaml
```

</details>

---

### Question 5: Init Container
**[3 minutes]**

Create a pod named `init-pod` that:
- Has an init container that creates file `/work/ready.txt` with content "initialized"
- Main container (nginx) mounts the same directory

<details>
<summary>Answer</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-pod
spec:
  initContainers:
  - name: init
    image: busybox
    command: ["sh", "-c", "echo initialized > /work/ready.txt"]
    volumeMounts:
    - name: workdir
      mountPath: /work
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - name: workdir
      mountPath: /work
  volumes:
  - name: workdir
    emptyDir: {}
```

Verify:
```bash
k exec init-pod -- cat /work/ready.txt
```

</details>

---

### Question 6: ConfigMap as Volume
**[2 minutes]**

Create a ConfigMap named `web-content` with key `index.html` containing "Hello CKAD".

Then create a pod named `web-server` that:
- Uses nginx image
- Mounts the ConfigMap at `/usr/share/nginx/html`

<details>
<summary>Answer</summary>

```bash
# Create ConfigMap
k create cm web-content --from-literal=index.html="Hello CKAD"

# Create pod
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: web-server
spec:
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - name: html
      mountPath: /usr/share/nginx/html
  volumes:
  - name: html
    configMap:
      name: web-content
EOF

# Verify
k exec web-server -- curl localhost
```

</details>

---

### Question 7: Secret Volume
**[2 minutes]**

Create a Secret named `db-creds` with:
- `username=admin`
- `password=secret123`

Mount it read-only in a pod named `secret-pod` at `/etc/db`

<details>
<summary>Answer</summary>

```bash
# Create secret
k create secret generic db-creds \
  --from-literal=username=admin \
  --from-literal=password=secret123

# Create pod
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: secret-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ["sleep", "3600"]
    volumeMounts:
    - name: secrets
      mountPath: /etc/db
      readOnly: true
  volumes:
  - name: secrets
    secret:
      secretName: db-creds
EOF

# Verify
k exec secret-pod -- cat /etc/db/password
```

</details>

---

### Question 8: Parallel Job
**[3 minutes]**

Create a Job named `parallel-job` that:
- Runs 6 completions
- With parallelism of 2
- Uses busybox to echo "Processing"

<details>
<summary>Answer</summary>

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: parallel-job
spec:
  completions: 6
  parallelism: 2
  template:
    spec:
      containers:
      - name: worker
        image: busybox
        command: ["echo", "Processing"]
      restartPolicy: Never
```

Verify:
```bash
k get pods -l job-name=parallel-job -w
# Should see 2 pods at a time, 6 total
```

</details>

---

### Question 9: Fix Multi-Container Pod
**[3 minutes]**

The following pod won't start. Identify and fix the issue:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: broken-multi
spec:
  initContainers:
  - name: init
    image: busybox
    command: ["sleep", "infinity"]  # Problem!
  containers:
  - name: main
    image: nginx
```

<details>
<summary>Answer</summary>

**Issue**: The init container runs `sleep infinity` and never exits. Init containers must complete (exit 0) for main containers to start.

**Fix**: Change the init container command to something that completes:

```yaml
initContainers:
- name: init
  image: busybox
  command: ["echo", "Init done"]
```

</details>

---

### Question 10: PVC and Pod
**[3 minutes]**

Create a PVC named `data-pvc` requesting 100Mi storage.

Then create a pod named `storage-pod` that:
- Uses nginx image
- Mounts the PVC at `/data`

Write a file to `/data/test.txt` to verify persistence.

<details>
<summary>Answer</summary>

```bash
# Create PVC
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 100Mi
EOF

# Create pod
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: storage-pod
spec:
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - name: storage
      mountPath: /data
  volumes:
  - name: storage
    persistentVolumeClaim:
      claimName: data-pvc
EOF

# Verify
k exec storage-pod -- sh -c "echo 'persistent' > /data/test.txt"
k exec storage-pod -- cat /data/test.txt
```

</details>

---

## Scoring

| Questions Correct | Score | Status |
|-------------------|-------|--------|
| 10/10 | 100% | Excellent - Ready for exam |
| 8-9/10 | 80-90% | Good - Minor review needed |
| 6-7/10 | 60-70% | Review weak areas |
| <6/10 | <60% | Revisit Part 1 modules |

---

## Cleanup

```bash
k delete pod broken sidecar-pod init-pod web-server secret-pod storage-pod broken-multi 2>/dev/null
k delete job backup-job parallel-job 2>/dev/null
k delete cronjob cleanup 2>/dev/null
k delete cm web-content 2>/dev/null
k delete secret db-creds 2>/dev/null
k delete pvc data-pvc 2>/dev/null
```

---

## Next Part

[Part 2: Application Deployment](../part2-deployment/module-2.1-deployments.md) - Deployments, Helm, Kustomize, and deployment strategies.
