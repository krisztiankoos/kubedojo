---
title: "Module 4.5: Storage Troubleshooting"
slug: k8s/cka/part4-storage/module-4.5-troubleshooting
sidebar:
  order: 6
lab:
  id: cka-4.5-troubleshooting
  url: https://killercoda.com/kubedojo/scenario/cka-4.5-troubleshooting
  duration: "40 min"
  difficulty: advanced
  environment: kubernetes
---
> **Complexity**: `[MEDIUM]` - Diagnosing and fixing storage issues
>
> **Time to Complete**: 35-45 minutes
>
> **Prerequisites**: Modules 4.1-4.4 (all previous storage modules)

---

## What You'll Be Able to Do

After this module, you will be able to:
- **Diagnose** storage failures systematically (PVC Pending, mount errors, capacity issues, permission denied)
- **Trace** the storage provisioning chain from PVC → StorageClass → provisioner → PV → mount
- **Fix** common storage issues: volume mount errors, capacity limits, and permissions mismatches
- **Design** a troubleshooting checklist for storage problems in CKA exam scenarios

---

## Why This Module Matters

Storage issues are among the most common problems in Kubernetes clusters. Pods stuck in ContainerCreating, PVCs that never bind, permission errors, and capacity problems can bring applications to a halt. The CKA exam heavily tests troubleshooting skills, and storage problems appear frequently. This module gives you a systematic approach to diagnose and fix storage issues.

> **The Detective Analogy**
>
> Troubleshooting storage is like being a detective. The pod won't start - that's the crime. Your tools are `kubectl describe`, `kubectl logs`, and `kubectl get events` - your magnifying glass, fingerprint kit, and witness interviews. You follow the evidence: Pod → PVC → PV → StorageClass → CSI driver. Each step reveals clues until you find the culprit.

---

## What You'll Learn

By the end of this module, you'll be able to:
- Systematically troubleshoot storage issues
- Debug PVC binding problems
- Fix volume mount errors
- Diagnose CSI driver issues
- Resolve permissions and capacity problems

---

## Did You Know?

- **Most storage issues are misconfiguration**: Wrong StorageClass name, mismatched access modes, or missing labels cause 80% of problems
- **Events are your best friend**: `kubectl describe` shows recent events that often contain the exact error message
- **CSI drivers have their own logs**: When the usual commands don't help, check CSI controller and node logs

---

## Part 1: Troubleshooting Framework

### 1.1 The Storage Debug Path

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Storage Troubleshooting Path                      │
│                                                                      │
│   Pod Issue                                                          │
│       │                                                              │
│       ▼                                                              │
│   1. k describe pod <name>                                          │
│      └─► Check Events section                                       │
│      └─► Check volume mount errors                                  │
│          │                                                          │
│          ▼                                                          │
│   2. k get pvc <name>                                               │
│      └─► Is STATUS "Bound"?                                         │
│      └─► If "Pending", check Events                                 │
│          │                                                          │
│          ▼                                                          │
│   3. k get pv                                                       │
│      └─► Does matching PV exist?                                    │
│      └─► Is STATUS "Available" or "Bound"?                          │
│          │                                                          │
│          ▼                                                          │
│   4. k get sc <storageclass>                                        │
│      └─► Does StorageClass exist?                                   │
│      └─► Is provisioner correct?                                    │
│          │                                                          │
│          ▼                                                          │
│   5. Check CSI driver                                               │
│      └─► Is driver installed?                                       │
│      └─► Check driver pod logs                                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Key Commands Reference

```bash
# Pod-level debugging
k describe pod <pod-name>
k get pod <pod-name> -o yaml
k logs <pod-name>

# PVC debugging
k get pvc
k describe pvc <pvc-name>
k get pvc <pvc-name> -o yaml

# PV debugging
k get pv
k describe pv <pv-name>
k get pv <pv-name> -o yaml

# StorageClass debugging
k get sc
k describe sc <sc-name>

# Events (often most useful!)
k get events --sort-by='.lastTimestamp'
k get events --field-selector involvedObject.name=<pvc-name>

# CSI debugging
k get pods -n kube-system | grep csi
k logs -n kube-system <csi-pod> -c <container>
```

---

## Part 2: PVC Binding Problems

### 2.1 PVC Stuck in Pending

**Symptoms**: PVC shows `STATUS: Pending`, never becomes Bound

```bash
k get pvc
# NAME     STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS
# my-pvc   Pending                                       fast-ssd
```

**Debug steps**:
```bash
# Step 1: Check events
k describe pvc my-pvc
# Look at Events section for errors
```

### 2.2 Common Pending Causes

**Cause 1: No matching PV exists (static provisioning)**
```
Events:
  Type     Reason              Message
  ----     ------              -------
  Normal   FailedBinding       no persistent volumes available for this claim
```

**Solution**: Create a PV that matches the PVC requirements:
```bash
# Check what PVC needs
k get pvc my-pvc -o yaml | grep -A5 spec:

# Create matching PV or fix PVC to match existing PV
```

**Cause 2: StorageClass doesn't exist**
```
Events:
  Type     Reason              Message
  ----     ------              -------
  Warning  ProvisioningFailed  storageclass.storage.k8s.io "fast-ssd" not found
```

**Solution**:
```bash
# List available StorageClasses
k get sc

# Fix PVC to use existing StorageClass
k patch pvc my-pvc -p '{"spec":{"storageClassName":"standard"}}'
# Note: You may need to delete and recreate PVC
```

**Cause 3: No CSI driver/provisioner**
```
Events:
  Type     Reason              Message
  ----     ------              -------
  Warning  ProvisioningFailed  failed to provision volume: no csi driver
```

**Solution**: Install the required CSI driver for your storage backend

**Cause 4: WaitForFirstConsumer mode**
```bash
k get pvc my-pvc
# STATUS: Pending (this is normal until pod uses it!)

k get sc fast-ssd -o jsonpath='{.volumeBindingMode}'
# WaitForFirstConsumer
```

**Solution**: This is expected behavior! Create a pod that uses the PVC, and it will bind.

> **Pause and predict**: You see a PVC in `Pending` status with no error events. Before diving into debugging, what single piece of information should you check on the StorageClass that might immediately explain the Pending status as normal behavior?

### 2.3 Access Mode Mismatch

**Symptoms**: PVC won't bind even though PV exists

```bash
k get pv
# NAME   CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS
# pv-1   100Gi      RWO            Retain           Available

k get pvc
# NAME     STATUS    ACCESS MODES   STORAGECLASS
# my-pvc   Pending   RWX            manual
```

**Problem**: PVC requests RWX, PV only offers RWO

**Solution**:
```bash
# Option 1: Change PVC to match PV
k delete pvc my-pvc
# Recreate with RWO

# Option 2: Create new PV with RWX (if storage supports it)
```

### 2.4 StorageClass Mismatch

```bash
k get pv pv-1 -o jsonpath='{.spec.storageClassName}'
# manual

k get pvc my-pvc -o jsonpath='{.spec.storageClassName}'
# fast
```

**Problem**: PVC and PV have different storageClassName

**Solution**: Align storageClassName on both resources

---

## Part 3: Volume Mount Errors

### 3.1 Pod Stuck in ContainerCreating

**Symptoms**: Pod stays in ContainerCreating state

```bash
k get pods
# NAME     READY   STATUS              RESTARTS   AGE
# my-pod   0/1     ContainerCreating   0          5m
```

**Debug**:
```bash
k describe pod my-pod
# Look for volume-related errors in Events
```

### 3.2 Common Mount Errors

**Error 1: PVC not found**
```
Events:
  Warning  FailedMount  Unable to attach or mount volumes:
  persistentvolumeclaim "my-pvc" not found
```

**Solution**:
```bash
# Check PVC exists in same namespace
k get pvc my-pvc -n <namespace>

# Fix pod spec if PVC name is wrong
```

**Error 2: Volume already attached to another node**
```
Events:
  Warning  FailedAttachVolume  Multi-Attach error for volume "pvc-xxx":
  Volume is already attached to node "node-1"
```

**Cause**: RWO volume attached to another node (common during node failures)

**Solution**:
```bash
# Wait for old pod to terminate, or force delete
k delete pod <old-pod> --force --grace-period=0

# If using StatefulSet, might need to delete old PV attachment
k get volumeattachment
```

**Error 3: Permission denied**
```
Events:
  Warning  FailedMount  MountVolume.SetUp failed:
  mount failed: exit status 32, permission denied
```

**Solution**:
```yaml
# Add securityContext to pod
spec:
  securityContext:
    fsGroup: 1000        # Group ID for volume
  containers:
  - name: app
    securityContext:
      runAsUser: 1000    # User ID
```

**Error 4: hostPath doesn't exist**
```
Events:
  Warning  FailedMount  hostPath type check failed:
  path /data/myapp does not exist
```

**Solution**:
```yaml
# Use DirectoryOrCreate type
volumes:
- name: data
  hostPath:
    path: /data/myapp
    type: DirectoryOrCreate    # Instead of Directory
```

> **Stop and think**: A pod is stuck in `ContainerCreating` and `kubectl describe pod` shows "Multi-Attach error for volume." You know the volume is RWO. Before force-deleting the old pod, what should you check first? Could force-deleting cause data corruption?

### 3.3 Mount Timeout

```
Events:
  Warning  FailedMount  Unable to attach or mount volumes:
  timeout expired waiting for volumes to attach
```

**Causes**:
- CSI driver not responding
- Storage backend unreachable
- Node issues

**Debug**:
```bash
# Check CSI driver pods
k get pods -n kube-system | grep csi

# Check CSI driver logs
k logs -n kube-system <csi-controller-pod> -c csi-provisioner

# Check node conditions
k describe node <node-name> | grep -A5 Conditions
```

---

## Part 4: Capacity Problems

### 4.1 Volume Full

**Symptoms**: Application errors about disk space

**Debug**:
```bash
# Check PVC capacity
k get pvc my-pvc
# CAPACITY: 10Gi

# Check actual usage in pod
k exec my-pod -- df -h /data
# Shows actual usage
```

**Solution 1: Expand PVC** (if StorageClass supports it)
```bash
# Check if expansion is allowed
k get sc <storageclass> -o jsonpath='{.allowVolumeExpansion}'
# true

# Expand PVC
k patch pvc my-pvc -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'

# Monitor expansion status
k describe pvc my-pvc | grep -A5 Conditions
```

**Solution 2: Clean up data**
```bash
k exec my-pod -- rm -rf /data/tmp/*
```

### 4.2 Insufficient Capacity

```
Events:
  Warning  ProvisioningFailed  insufficient capacity
```

**Causes**:
- Storage backend is full
- Quota exceeded
- Regional capacity limits (cloud)

**Debug**:
```bash
# Check ResourceQuota
k get resourcequota -n <namespace>

# Check LimitRange
k get limitrange -n <namespace>

# For cloud, check cloud console for capacity
```

---

## Part 5: CSI Driver Issues

### 5.1 CSI Driver Not Installed

**Symptoms**: PVC stuck pending, events mention CSI

```bash
k describe pvc my-pvc
# Events:
#   Warning  ProvisioningFailed  error getting CSI driver name
```

**Debug**:
```bash
# List CSI drivers
k get csidrivers

# Check if driver pods are running
k get pods -n kube-system | grep csi

# Check CSINode objects
k get csinode
```

### 5.2 CSI Driver Crashlooping

```bash
k get pods -n kube-system | grep csi
# NAME                          READY   STATUS             RESTARTS
# ebs-csi-controller-xxx        0/6     CrashLoopBackOff   5
```

**Debug**:
```bash
# Check logs
k logs -n kube-system ebs-csi-controller-xxx -c csi-provisioner
k logs -n kube-system ebs-csi-controller-xxx -c csi-attacher

# Common causes:
# - Missing cloud credentials
# - Wrong IAM permissions
# - Network connectivity issues
```

### 5.3 CSI Driver Permissions

For cloud storage, CSI drivers need appropriate permissions:

**AWS**: IAM role with EBS permissions
```bash
# Check service account
k get sa -n kube-system ebs-csi-controller-sa -o yaml
# Look for eks.amazonaws.com/role-arn annotation
```

**GCP**: Workload Identity or node service account
**Azure**: Managed Identity or service principal

> **Pause and predict**: You see a CSI controller pod in `CrashLoopBackOff`. The pod logs show "failed to assume IAM role." The EBS CSI driver was working yesterday. What could have changed, and where would you look to verify the IAM configuration?

---

## Part 6: Quick Reference: Error Messages

### 6.1 Error Message Cheatsheet

| Error Message | Likely Cause | Quick Fix |
|---------------|--------------|-----------|
| `no persistent volumes available` | No matching PV for static provisioning | Create matching PV |
| `storageclass not found` | Wrong StorageClass name | Check `k get sc` |
| `waiting for first consumer` | WaitForFirstConsumer mode | Create pod using PVC |
| `Multi-Attach error` | RWO volume on multiple nodes | Delete old pod first |
| `permission denied` | Filesystem permissions | Set fsGroup/runAsUser |
| `path does not exist` | hostPath missing | Use DirectoryOrCreate |
| `timeout waiting for volumes` | CSI driver issue | Check CSI pods/logs |
| `insufficient capacity` | No space in storage backend | Expand or clean up |
| `volume is already attached` | Stale volume attachment | Delete VolumeAttachment |

### 6.2 Quick Debug Commands

```bash
# One-liner for common checks
echo "=== PVCs ===" && k get pvc && \
echo "=== PVs ===" && k get pv && \
echo "=== StorageClasses ===" && k get sc && \
echo "=== Recent Events ===" && k get events --sort-by='.lastTimestamp' | tail -20
```

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Not checking Events | Missing the actual error message | Always `k describe` first |
| Ignoring namespace | PVC in different namespace than pod | Verify namespace matches |
| Forgetting WaitForFirstConsumer | Thinking PVC is broken when Pending | Check volumeBindingMode |
| Deleting PVC before pod | Pod can't unmount properly | Delete pod first |
| Not checking CSI logs | Generic errors hide real cause | Check CSI driver pods |
| Wrong YAML indentation | Volume spec invalid | Use `--dry-run=client -o yaml` |

---

## Quiz

### Q1: Systematic Triage
A developer reports their pod has been stuck in `ContainerCreating` for 10 minutes. They have already tried deleting and recreating the pod twice. Walk through the exact sequence of commands you would run to diagnose this, starting from the pod and working down through the storage stack. At each step, what specific information are you looking for?

<details>
<summary>Answer</summary>

Start with `kubectl describe pod <name>` and look at the **Events section** for volume-related errors (FailedMount, FailedAttach, timeout). This tells you whether the issue is a missing PVC, a mount error, or an attach error. Next, `kubectl get pvc <name>` to check if the PVC is `Bound` -- if it shows `Pending`, the problem is upstream. If Pending, `kubectl describe pvc <name>` reveals why: "storageclass not found," "no persistent volumes available," or "waiting for first consumer." Then check `kubectl get sc` to verify the StorageClass exists and has the right provisioner. Finally, `kubectl get pods -n kube-system | grep csi` to verify the CSI driver is running, and check its logs with `kubectl logs`. Each step narrows the problem: pod events tell you the symptom, PVC status tells you where the chain breaks, and CSI logs reveal the root cause.

</details>

### Q2: The Pending PVC That Is Not Broken
A new team member files an urgent ticket: "PVC `data-volume` has been Pending for 2 hours, nothing is working!" You check `kubectl describe pvc data-volume` and see no error events -- just a normal "waiting for first consumer to be created" message. The team member insists something is wrong because other PVCs bind immediately. How do you explain what is happening, and what should the team member do next?

<details>
<summary>Answer</summary>

The PVC is using a StorageClass with `volumeBindingMode: WaitForFirstConsumer`. This means the PV is deliberately **not provisioned until a pod that uses the PVC is scheduled**. This is the correct behavior for zone-specific storage (like AWS EBS or GCE PD) to ensure the volume is created in the same availability zone as the pod. The "other PVCs" that bind immediately likely use a StorageClass with `Immediate` binding mode or an NFS-type provisioner. The team member needs to create a pod that references this PVC in its volumes section. Once the scheduler assigns the pod to a node, the provisioner will create the PV in the correct zone, the PVC will bind, and the pod will start. This is not a bug -- it is a feature that prevents cross-zone mount failures.

</details>

### Q3: Node Failure and Multi-Attach
A 3-node cluster loses node-2 (it goes `NotReady`). A StatefulSet pod on node-2 used an RWO EBS volume. Kubernetes tries to reschedule the pod to node-3, but the new pod is stuck in `ContainerCreating` with "Multi-Attach error for volume: Volume is already exclusively attached to node-2." The old pod shows `Terminating` but will not complete because node-2 is down. What are the steps to recover, and what are the risks of force-deleting the old pod?

<details>
<summary>Answer</summary>

The RWO volume is still attached to the unreachable node-2, and the new pod on node-3 cannot attach it simultaneously. Recovery steps: (1) Verify node-2 is truly down: `kubectl get node node-2` and check conditions. (2) Force-delete the stuck pod: `kubectl delete pod <name> --force --grace-period=0`. This removes the pod from the API server but does **not** cleanly unmount the volume on node-2. (3) Delete the stale VolumeAttachment: `kubectl get volumeattachment`, find the one for this volume, and `kubectl delete volumeattachment <name>`. This tells the control plane to release the volume. (4) The new pod on node-3 should now be able to attach the volume. **Risk**: force-deleting without clean unmount can cause **data corruption** if the application was mid-write when node-2 went down. EBS volumes have built-in consistency, but application-level data (like database WAL files) may be incomplete. After recovery, run an application-level integrity check (e.g., `fsck` or database repair).

</details>

### Q4: Permission Denied After Migration
A team migrates their application to a new container image that runs as `uid 1000` (previously ran as root). After the migration, the pod starts but the application logs show "Permission denied: cannot write to /data/app.log." The PVC mounts successfully and `kubectl describe pod` shows no errors. What is the root cause, and what is the correct fix without reverting to running as root?

<details>
<summary>Answer</summary>

The root cause is a **filesystem ownership mismatch**. The PV's files were created by the previous container running as root (`uid 0`), so they are owned by root. The new container runs as `uid 1000` and cannot write to root-owned files. The correct fix is to set `fsGroup` in the pod's security context: `spec.securityContext.fsGroup: 1000`. This tells the kubelet to recursively change the group ownership of all files in the mounted volume to GID 1000, and set the setgid bit so new files inherit this group. Additionally, set `runAsUser: 1000` and `runAsNonRoot: true` in the container's securityContext. Do NOT revert to running as root -- that would be a security regression. For volumes with many files, the fsGroup change can cause slow pod startup on first mount, which is a known trade-off.

</details>

### Q5: Dynamic Provisioning Silently Failing
A PVC referencing StorageClass `premium-ssd` stays Pending. `kubectl describe pvc` shows the event: "waiting for a volume to be created, either by external provisioner 'ebs.csi.aws.com' or manually created by system administrator." The StorageClass exists and looks correct. Other PVCs using the default StorageClass work fine. Where do you look next, and what are the three most likely causes?

<details>
<summary>Answer</summary>

The error means the PVC reached the provisioner but the provisioner has not acted. Next step: check the CSI driver pods in `kube-system` with `kubectl get pods -n kube-system | grep csi` and then check their logs with `kubectl logs -n kube-system <csi-controller-pod> -c csi-provisioner`. The three most likely causes: (1) **CSI controller is crashlooping or not running** -- the provisioner sidecar cannot process the request. Check pod status and restart counts. (2) **IAM/permission issue** -- the CSI driver lacks permission to create EBS volumes (e.g., expired IAM role, wrong IRSA annotation on the service account, or missing `ec2:CreateVolume` permission). Check `kubectl get sa -n kube-system ebs-csi-controller-sa -o yaml` for the role-arn annotation. (3) **Invalid StorageClass parameters** -- the `parameters` section contains values the provisioner cannot use (wrong `type`, invalid `kmsKeyId`, or unsupported `iopsPerGB` value). The CSI provisioner logs will show the specific error from the AWS API.

</details>

### Q6: Full Troubleshooting Scenario
On exam day, you are given this scenario: A Deployment with 2 replicas is failing. Pod-1 is `Running`, Pod-2 is `ContainerCreating`. Both reference PVC `app-data`. The PVC is `Bound` to a PV with access mode `RWO`. The StorageClass uses `volumeBindingMode: WaitForFirstConsumer` and `reclaimPolicy: Delete`. `kubectl get pods -o wide` shows Pod-1 on node-A and Pod-2 scheduled to node-B. What is the problem, and provide two distinct solutions (one quick fix for the exam, one proper production fix).

<details>
<summary>Answer</summary>

The problem is that both pods share one PVC with **RWO** access mode, and they are on different nodes. RWO means the volume can only be attached to one node at a time. Pod-1 on node-A has the volume, so Pod-2 on node-B gets a Multi-Attach error. **Quick exam fix**: Scale the Deployment to 1 replica (`kubectl scale deploy <name> --replicas=1`) so only one pod needs the volume. Or, add a `nodeAffinity`/`nodeSelector` to force all pods onto the same node (RWO allows multiple pods on the same node). **Proper production fix**: Convert the Deployment to a **StatefulSet** with `volumeClaimTemplates`, giving each replica its own independent PVC and PV. Alternatively, if the workload truly needs shared storage, switch to a storage backend that supports `ReadWriteMany` (RWX) like NFS or EFS, and update the PVC access mode. The `reclaimPolicy: Delete` is also risky for a stateful app -- consider changing to `Retain` on the PV.

</details>

---

## Hands-On Exercise: Storage Troubleshooting Scenarios

### Setup

```bash
# Create namespace
k create ns storage-debug

# We'll create broken configurations and fix them
```

### Scenario 1: PVC Won't Bind (Wrong StorageClass)

```bash
# Create a PVC with wrong StorageClass
cat <<EOF | k apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: broken-pvc-1
  namespace: storage-debug
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: nonexistent-class
EOF

# Check status
k get pvc -n storage-debug broken-pvc-1

# Debug
k describe pvc -n storage-debug broken-pvc-1
# Look for: storageclass "nonexistent-class" not found

# Fix: List available StorageClasses and recreate PVC
k get sc
k delete pvc -n storage-debug broken-pvc-1

# Recreate with correct StorageClass (use your cluster's SC)
cat <<EOF | k apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: broken-pvc-1
  namespace: storage-debug
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: standard    # Use actual SC name
EOF
```

### Scenario 2: Pod Can't Mount (Wrong PVC Name)

```bash
# Create a valid PVC
cat <<EOF | k apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: correct-pvc
  namespace: storage-debug
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
EOF

# Create pod with wrong PVC reference
cat <<EOF | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: broken-pod-1
  namespace: storage-debug
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ['sleep', '3600']
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: wrong-pvc-name    # This doesn't exist!
EOF

# Check pod status
k get pod -n storage-debug broken-pod-1
# STATUS: ContainerCreating

# Debug
k describe pod -n storage-debug broken-pod-1
# Look for: persistentvolumeclaim "wrong-pvc-name" not found

# Fix
k delete pod -n storage-debug broken-pod-1

cat <<EOF | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: broken-pod-1
  namespace: storage-debug
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ['sleep', '3600']
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: correct-pvc    # Fixed!
EOF
```

### Scenario 3: hostPath Type Error

```bash
# Create pod with strict hostPath type
cat <<EOF | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: broken-pod-2
  namespace: storage-debug
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ['sleep', '3600']
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    hostPath:
      path: /tmp/nonexistent-path-xyz
      type: Directory    # Fails if directory doesn't exist
EOF

# Debug
k describe pod -n storage-debug broken-pod-2
# May show: hostPath type check failed

# Fix: Use DirectoryOrCreate
k delete pod -n storage-debug broken-pod-2

cat <<EOF | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: broken-pod-2
  namespace: storage-debug
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ['sleep', '3600']
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    hostPath:
      path: /tmp/nonexistent-path-xyz
      type: DirectoryOrCreate    # Creates if missing
EOF
```

### Success Criteria
- [ ] Identified StorageClass error from events
- [ ] Fixed PVC to use correct StorageClass
- [ ] Identified wrong PVC name from pod events
- [ ] Fixed pod to reference correct PVC
- [ ] Understood hostPath type requirements

### Cleanup

```bash
k delete ns storage-debug
```

---

## Practice Drills

### Drill 1: Quick Status Check (1 min)
```bash
# Task: Check if all PVCs in namespace are Bound
k get pvc -n <namespace>
# Look for any not showing "Bound"
```

### Drill 2: Find PVC Events (1 min)
```bash
# Task: Get events for a specific PVC
k describe pvc <pvc-name> | grep -A20 Events
```

### Drill 3: Check Volume in Pod (2 min)
```bash
# Task: Verify a volume is mounted correctly in pod
k exec <pod> -- df -h
k exec <pod> -- ls -la /data
```

### Drill 4: Debug ContainerCreating (2 min)
```bash
# Task: Find why pod is stuck in ContainerCreating
k describe pod <pod-name>
# Check Events for mount errors
```

### Drill 5: Check CSI Driver Status (2 min)
```bash
# Task: Verify CSI driver is running
k get pods -n kube-system | grep csi
k get csidrivers
```

### Drill 6: Find Matching PV (2 min)
```bash
# Task: Find why PVC won't bind to existing PV
k get pvc <pvc-name> -o yaml | grep -E 'storage:|accessModes:|storageClassName:'
k get pv <pv-name> -o yaml | grep -E 'storage:|accessModes:|storageClassName:'
# Compare values
```

### Drill 7: Check VolumeAttachments (1 min)
```bash
# Task: List all volume attachments
k get volumeattachment
# Useful for debugging Multi-Attach errors
```

### Drill 8: Get Recent Storage Events (1 min)
```bash
# Task: Get recent events related to PVCs
k get events --field-selector reason=FailedBinding
k get events --field-selector reason=ProvisioningFailed
```

---

## Summary: Storage Troubleshooting Checklist

```
□ Pod stuck? → k describe pod → check Events
□ PVC Pending? → k describe pvc → check Events
□ StorageClass exists? → k get sc
□ PV available? → k get pv
□ Access modes match? → Compare PVC and PV
□ StorageClassName match? → Compare PVC and PV
□ CSI driver running? → k get pods -n kube-system | grep csi
□ Permissions issue? → Check securityContext fsGroup
□ Capacity issue? → Check quotas and storage backend
```

---

## Next Steps

Congratulations! You've completed Part 4: Storage. You should now be able to:
- Configure volumes (emptyDir, hostPath, projected)
- Work with PersistentVolumes and PersistentVolumeClaims
- Use StorageClasses for dynamic provisioning
- Create and restore from volume snapshots
- Troubleshoot common storage issues

Continue to the [Part 4 Cumulative Quiz](../part4-cumulative-quiz/) to test your knowledge, then proceed to [Part 5: Troubleshooting](/k8s/cka/part5-troubleshooting/).
