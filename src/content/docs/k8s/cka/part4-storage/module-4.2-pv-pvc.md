---
title: "Module 4.2: PersistentVolumes & PersistentVolumeClaims"
slug: k8s/cka/part4-storage/module-4.2-pv-pvc
sidebar:
  order: 3
lab:
  id: cka-4.2-pv-pvc
  url: https://killercoda.com/kubedojo/scenario/cka-4.2-pv-pvc
  duration: "40 min"
  difficulty: intermediate
  environment: kubernetes
---
> **Complexity**: `[MEDIUM]` - Core storage abstraction
>
> **Time to Complete**: 40-50 minutes
>
> **Prerequisites**: Module 4.1 (Volumes), Module 1.2 (CSI)

---

## What You'll Be Able to Do

After this module, you will be able to:
- **Create** PersistentVolumes and PersistentVolumeClaims with appropriate access modes and storage classes
- **Explain** the PV lifecycle (Available → Bound → Released → Deleted) and reclaim policies
- **Debug** PVC stuck in Pending by checking StorageClass, capacity, access modes, and node affinity
- **Implement** static provisioning for local storage and dynamic provisioning with StorageClasses

---

## Why This Module Matters

PersistentVolumes (PV) and PersistentVolumeClaims (PVC) are the foundation of persistent storage in Kubernetes. They separate storage provisioning from consumption, allowing administrators to manage storage independently from developers who consume it. The CKA exam heavily tests PV/PVC creation, binding, and troubleshooting.

> **The Apartment Rental Analogy**
>
> Think of storage like renting an apartment. The **PersistentVolume** is the actual apartment - it exists whether anyone lives there or not. The **PersistentVolumeClaim** is like a tenant's application form specifying their needs: "I need 2 bedrooms, central location, parking spot." The building manager (Kubernetes) matches applications to available apartments. The tenant (pod) doesn't need to know which specific apartment they got - just that it meets their requirements.

---

## What You'll Learn

By the end of this module, you'll be able to:
- Create PersistentVolumes manually
- Create PersistentVolumeClaims to request storage
- Understand the binding process between PV and PVC
- Configure access modes and reclaim policies
- Use PVCs in pods
- Troubleshoot common PV/PVC issues

---

## Did You Know?

- **PVs are cluster-scoped**: Unlike most resources, PersistentVolumes don't belong to any namespace - they're available cluster-wide
- **Binding is permanent**: Once a PVC binds to a PV, that binding is exclusive until the PVC is deleted (or the PV is reclaimed)
- **Size matters differently**: A PVC requesting 5Gi can bind to a 100Gi PV if no closer match exists - the extra space is reserved but potentially wasted

---

## Part 1: Understanding the PV/PVC Model

### 1.1 The Storage Abstraction

```
┌──────────────────────────────────────────────────────────────────────┐
│                    PV/PVC Abstraction Model                           │
│                                                                       │
│   Cluster Admin                        Developer                      │
│   ┌─────────────┐                      ┌─────────────┐               │
│   │ Provisions  │                      │ Requests    │               │
│   │ Storage     │                      │ Storage     │               │
│   └──────┬──────┘                      └──────┬──────┘               │
│          │                                    │                       │
│          ▼                                    ▼                       │
│   ┌─────────────┐      Binding        ┌─────────────┐               │
│   │ Persistent  │◄───────────────────►│ Persistent  │               │
│   │ Volume (PV) │                      │ VolumeClaim │               │
│   │             │                      │ (PVC)       │               │
│   │ 100Gi NFS   │                      │ 50Gi RWO    │               │
│   └──────┬──────┘                      └──────┬──────┘               │
│          │                                    │                       │
│          │        Physical Storage            │     Mount in Pod      │
│          ▼                                    ▼                       │
│   ┌─────────────┐                      ┌─────────────┐               │
│   │   NFS       │                      │    Pod      │               │
│   │   Server    │─────────────────────►│  /data      │               │
│   └─────────────┘                      └─────────────┘               │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.2 Why This Separation?

| Concern | Who Handles It | Resource |
|---------|---------------|----------|
| What storage is available? | Admin | PersistentVolume |
| How much storage is needed? | Developer | PersistentVolumeClaim |
| Where to mount it? | Developer | Pod spec |
| Storage backend details | Admin | PV + StorageClass |

### 1.3 PV/PVC Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PV/PVC Lifecycle                                │
│                                                                      │
│   PV Created ──► Available ──► Bound ──► Released ──► [Reclaim]     │
│       │              │            │           │            │         │
│       │              │            │           │            │         │
│       │         PVC Created      PVC         PVC       Retain/      │
│       │         & Matched        Exists     Deleted    Delete/      │
│       │                                                Recycle      │
│                                                                      │
│   PV Phases:                                                         │
│   • Available: Ready for binding                                     │
│   • Bound: Linked to a PVC                                          │
│   • Released: PVC deleted, awaiting reclaim                         │
│   • Failed: Automatic reclamation failed                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Part 2: Creating PersistentVolumes

### 2.1 PV Specification

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-nfs-data
  labels:
    type: nfs
    environment: production
spec:
  capacity:
    storage: 100Gi                    # Size of the volume
  volumeMode: Filesystem              # Filesystem or Block
  accessModes:
    - ReadWriteMany                   # Can be mounted by multiple nodes
  persistentVolumeReclaimPolicy: Retain   # What happens when released
  storageClassName: manual            # Must match PVC (or empty)
  mountOptions:
    - hard
    - nfsvers=4.1
  nfs:                                # Backend-specific configuration
    path: /exports/data
    server: nfs-server.example.com
```

### 2.2 Access Modes

| Mode | Abbreviation | Description |
|------|--------------|-------------|
| ReadWriteOnce | RWO | Single node read-write |
| ReadOnlyMany | ROX | Multiple nodes read-only |
| ReadWriteMany | RWX | Multiple nodes read-write |
| ReadWriteOncePod | RWOP | Single pod read-write (K8s 1.22+) |

**Backend support varies**:
- **NFS**: RWO, ROX, RWX
- **AWS EBS**: RWO only
- **GCE PD**: RWO, ROX
- **Azure Disk**: RWO only
- **Local**: RWO only

### 2.3 Reclaim Policies

| Policy | Behavior | Use Case |
|--------|----------|----------|
| Retain | PV preserved after PVC deletion | Production data, manual cleanup |
| Delete | PV and underlying storage deleted | Dynamic provisioning, dev/test |
| Recycle | Basic scrub (`rm -rf /data/*`) | **Deprecated** - don't use |

> **Stop and think**: A junior admin creates a PV with `reclaimPolicy: Delete` for a production PostgreSQL database. A developer accidentally deletes the PVC. What happens to the data? What reclaim policy should have been used, and what additional steps would be needed to reuse that PV after a PVC deletion?

### 2.4 Volume Modes

```yaml
spec:
  volumeMode: Filesystem    # Default - mounted as directory
  # OR
  volumeMode: Block         # Raw block device (for databases)
```

### 2.5 Common PV Types

**hostPath PV** (testing only):
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-hostpath
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Delete
  storageClassName: manual
  hostPath:
    path: /mnt/data
    type: DirectoryOrCreate
```

**NFS PV**:
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-nfs
spec:
  capacity:
    storage: 50Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: nfs
  nfs:
    server: 192.168.1.100
    path: /exports/share
```

**Local PV** (node-specific):
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-local
spec:
  capacity:
    storage: 200Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-storage
  local:
    path: /mnt/disks/ssd1
  nodeAffinity:                        # Required for local volumes!
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - worker-node-1
```

---

## Part 3: Creating PersistentVolumeClaims

### 3.1 PVC Specification

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-claim
  namespace: production              # PVCs are namespaced!
spec:
  accessModes:
    - ReadWriteOnce                  # Must match or be subset of PV
  volumeMode: Filesystem
  resources:
    requests:
      storage: 50Gi                  # Minimum size needed
  storageClassName: manual           # Match PV's storageClassName
  selector:                          # Optional: target specific PVs
    matchLabels:
      type: nfs
      environment: production
```

### 3.2 Binding Rules

A PVC binds to a PV when:
1. **storageClassName** matches (or both empty)
2. **accessModes** requested are available in PV
3. **resources.requests.storage** <= PV capacity
4. **selector** (if specified) matches PV labels

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Binding Decision                               │
│                                                                      │
│   PVC Request          PV Available        Match?                    │
│   ─────────────        ────────────        ──────                    │
│   50Gi RWO             100Gi RWO           ✓ Size OK, mode OK       │
│   50Gi RWX             100Gi RWO           ✗ Access mode mismatch   │
│   50Gi RWO manual      100Gi RWO fast      ✗ StorageClass mismatch  │
│   50Gi RWO             30Gi RWO            ✗ Size too small         │
│                                                                      │
│   Note: PVC can bind to larger PV, but not smaller                  │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.3 Creating PVC via kubectl

```bash
# Quick way to create a PVC (limited options)
cat <<EOF | k apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-claim
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard
EOF
```

### 3.4 Checking PVC Status

```bash
# List PVCs
k get pvc
# NAME       STATUS   VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS
# my-claim   Bound    pv-001   10Gi       RWO            standard

# Detailed view
k describe pvc my-claim

# Check which PV it bound to
k get pvc my-claim -o jsonpath='{.spec.volumeName}'
```

---

## Part 4: Using PVCs in Pods

### 4.1 Basic Pod with PVC

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-storage
spec:
  containers:
  - name: app
    image: nginx:1.25
    volumeMounts:
    - name: data
      mountPath: /usr/share/nginx/html
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: my-claim              # Reference the PVC name
```

### 4.2 PVC in Deployments

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: nginx:1.25
        volumeMounts:
        - name: shared-data
          mountPath: /data
      volumes:
      - name: shared-data
        persistentVolumeClaim:
          claimName: shared-pvc        # Must be RWX for multi-replica
```

**Important**: For Deployments with multiple replicas, you need:
- A PVC with `ReadWriteMany` access mode, OR
- A StatefulSet with volumeClaimTemplates (each replica gets its own PVC)

> **Pause and predict**: You create a Deployment with 3 replicas, each mounting the same PVC with access mode `ReadWriteOnce`. Replica 1 starts fine on node-1. What happens when replica 2 gets scheduled to node-2? Would changing to `ReadWriteOncePod` (RWOP) make things better or worse?

### 4.3 Read-Only PVC Mount

```yaml
volumes:
- name: data
  persistentVolumeClaim:
    claimName: my-claim
    readOnly: true                     # Mount as read-only
```

---

## Part 5: PV/PVC Matching with Selectors

### 5.1 Label-Based Selection

```yaml
# PV with labels
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-fast-ssd
  labels:
    type: ssd
    speed: fast
    region: us-east
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteOnce
  storageClassName: ""                # Empty for manual binding
  hostPath:
    path: /mnt/ssd
---
# PVC selecting specific PV
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: fast-storage-claim
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: ""                # Must match PV
  selector:
    matchLabels:
      type: ssd
      speed: fast
    matchExpressions:
    - key: region
      operator: In
      values:
        - us-east
        - us-west
```

### 5.2 Direct Volume Selection

Force a PVC to bind to a specific PV by name:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: specific-pv-claim
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: ""
  volumeName: pv-fast-ssd             # Bind to this specific PV
```

---

## Part 6: PV Release and Cleanup

### 6.1 Understanding Released State

When a PVC is deleted:
```
PVC Deleted ──► PV status changes to "Released"
                     │
                     ├── Retain: Data kept, PV not reusable
                     │           Admin must manually clean up
                     │
                     └── Delete: PV and storage deleted automatically
```

### 6.2 Reclaiming a Released PV

```bash
# Check PV status
k get pv pv-data
# NAME      CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM
# pv-data   100Gi      RWO            Retain           Released   default/old-claim

# Remove the claim reference to make PV available again
k patch pv pv-data -p '{"spec":{"claimRef": null}}'

# Verify it's Available
k get pv pv-data
# STATUS: Available
```

### 6.3 Manually Deleting Data

For Retain policy, data remains on the storage. Clean up steps:
1. Back up data if needed
2. Delete data from underlying storage
3. Remove claimRef (as above) or delete/recreate PV

> **Pause and predict**: You have a PV in `Released` state after its PVC was deleted. You patch the PV to remove the `claimRef`, making it `Available` again. A new PVC binds to it. Will the new PVC see the old data that was on the volume, or will it be empty?

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| PVC stuck in Pending | No matching PV available | Check storageClassName, size, access modes |
| Access mode mismatch | PVC requesting RWX, PV only has RWO | Use compatible access modes |
| StorageClass mismatch | PVC and PV have different storageClassName | Align storageClassName or use "" for both |
| Deleted PVC, lost data | Reclaim policy was Delete | Use Retain for important data |
| Can't reuse Released PV | claimRef still set | Patch PV to remove claimRef |
| Local PV missing nodeAffinity | Pod can't find volume | Add required nodeAffinity section |
| PVC in wrong namespace | Pod can't reference it | PVCs must be in same namespace as pod |

---

## Quiz

### Q1: Cross-Namespace Storage Mystery
A developer in the `frontend` namespace creates a PVC requesting 10Gi with `storageClassName: manual`. An admin has created a 50Gi PV with `storageClassName: manual` in the cluster. The PVC binds successfully. But when the developer tries to reference this PVC from a pod in the `backend` namespace, the pod fails. Why does the pod fail, and what is the correct approach?

<details>
<summary>Answer</summary>

PersistentVolumes are **cluster-scoped** (no namespace), so the PV itself is visible everywhere. However, PersistentVolumeClaims are **namespaced** -- the PVC `my-claim` in `frontend` cannot be referenced by a pod in `backend`. The pod fails because it cannot find a PVC with that name in its own namespace. The correct approach is to create a separate PVC in the `backend` namespace. Note that the 50Gi PV is already bound to the `frontend` PVC exclusively, so the `backend` PVC would need its own PV or dynamic provisioning.

</details>

### Q2: Wasted Storage Investigation
Your cluster has three PVs: 10Gi, 50Gi, and 100Gi, all with `storageClassName: standard` and `accessModes: [ReadWriteOnce]`. A developer creates a PVC requesting 20Gi with the same StorageClass. After binding, they complain that `kubectl get pvc` shows 50Gi capacity, not 20Gi. They ask: "Where did the extra 30Gi go? Can another PVC use it?"

<details>
<summary>Answer</summary>

Kubernetes selects the **smallest PV that satisfies the request** -- the 10Gi PV is too small, so the 50Gi PV binds. The binding is exclusive: the entire 50Gi PV is reserved for this PVC, even though only 20Gi was requested. No other PVC can use the remaining 30Gi -- it is effectively wasted. This is a key reason dynamic provisioning (via StorageClasses) is preferred in production: it creates PVs sized exactly to the request. To avoid waste with static provisioning, admins should create PVs that closely match expected PVC sizes.

</details>

### Q3: Multi-Replica Deployment Failure
A team deploys a 3-replica Deployment where each pod mounts the same PVC (access mode `ReadWriteOnce`). Replica 1 starts on node-A. Replica 2 is scheduled to node-B but gets stuck in `ContainerCreating` with a Multi-Attach error. What is the root cause, and what are two different solutions?

<details>
<summary>Answer</summary>

`ReadWriteOnce` (RWO) means the volume can only be mounted by a **single node** at a time. Replica 2 on node-B cannot attach the volume that is already mounted on node-A. Two solutions: (1) Switch to a storage backend that supports `ReadWriteMany` (RWX) like NFS, and change the PVC access mode to RWX so all replicas on different nodes can mount it simultaneously. (2) Convert the Deployment to a **StatefulSet** with `volumeClaimTemplates`, which gives each replica its own independent PVC and PV -- this is the correct pattern for stateful workloads like databases where each replica needs its own storage.

</details>

### Q4: Released PV Recovery
A production PostgreSQL PVC was accidentally deleted. The PV has `reclaimPolicy: Retain` and now shows status `Released`. The team needs to recover the data. They try creating a new PVC with the same name and spec, but it stays `Pending` instead of binding to the Released PV. What is blocking the binding, and what are the exact steps to recover?

<details>
<summary>Answer</summary>

A Released PV still has a `claimRef` pointing to the old, deleted PVC. Even though a new PVC has the same name, the PV controller will not rebind it automatically because the UID in the claimRef does not match. The recovery steps are: (1) Verify the PV still has data: `kubectl get pv <name> -o yaml` and check the backend path. (2) Remove the stale claimRef: `kubectl patch pv <name> -p '{"spec":{"claimRef": null}}'`. This changes the PV status to `Available`. (3) Create the new PVC with matching storageClassName, access modes, and optionally `volumeName: <pv-name>` to force binding to that specific PV. The data on the underlying storage is preserved throughout this process because the Retain policy prevents deletion.

</details>

### Q5: Static Binding Trap
A developer creates a PVC without specifying `storageClassName`. The cluster has a default StorageClass. Meanwhile, an admin has manually created a PV with `storageClassName: ""`. The PVC never binds to the manual PV and instead triggers dynamic provisioning. Why, and how should the PVC be configured for manual binding?

<details>
<summary>Answer</summary>

When `storageClassName` is **omitted** from a PVC, Kubernetes uses the cluster's **default StorageClass**, which triggers dynamic provisioning -- it does not look for PVs with empty storageClassName. To explicitly opt out of dynamic provisioning and bind to the manual PV, the PVC must set `storageClassName: ""` (empty string). This tells Kubernetes: "only bind to PVs that also have no StorageClass, and do not trigger any provisioner." Both the PV and PVC must have `storageClassName: ""` for manual binding to work. This distinction between "omitted" and "empty string" is a common exam gotcha.

</details>

### Q6: Local PV Scheduling Failure
A team creates a local PV backed by an SSD at `/mnt/disks/ssd1` on `worker-node-1`, but forgets to add `nodeAffinity`. A pod using this PV gets scheduled to `worker-node-2` and fails with a mount error. Explain why the nodeAffinity is required for local PVs (but not for NFS or cloud PVs), and write the nodeAffinity section needed.

<details>
<summary>Answer</summary>

Local PVs reference storage that is **physically attached to a specific node** -- the path `/mnt/disks/ssd1` only exists on `worker-node-1`. Without nodeAffinity, the scheduler does not know which node has the storage and may schedule the pod anywhere. NFS and cloud PVs do not need this because NFS is network-accessible from all nodes, and cloud PVs are attached dynamically by the CSI driver. The required nodeAffinity section constrains the scheduler to place pods on the correct node:

```yaml
nodeAffinity:
  required:
    nodeSelectorTerms:
    - matchExpressions:
      - key: kubernetes.io/hostname
        operator: In
        values:
        - worker-node-1
```

This ensures pods using the local PV are only scheduled to `worker-node-1` where the disk exists.

</details>

---

## Hands-On Exercise: Static PV Provisioning

### Scenario
Create a PV and PVC, then use the storage in a pod. Verify data persists across pod deletion.

### Setup

```bash
# Create namespace
k create ns pv-lab
```

### Task 1: Create a PersistentVolume

```bash
cat <<EOF | k apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: lab-pv
  labels:
    lab: storage
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /tmp/lab-pv-data
    type: DirectoryOrCreate
EOF
```

Verify:
```bash
k get pv lab-pv
# STATUS should be "Available"
```

### Task 2: Create a PersistentVolumeClaim

```bash
cat <<EOF | k apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: lab-pvc
  namespace: pv-lab
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 500Mi
  storageClassName: manual
  selector:
    matchLabels:
      lab: storage
EOF
```

Verify binding:
```bash
k get pvc -n pv-lab
# STATUS should be "Bound"

k get pv lab-pv
# CLAIM should show "pv-lab/lab-pvc"
```

### Task 3: Use PVC in a Pod

```bash
cat <<EOF | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: storage-pod
  namespace: pv-lab
spec:
  containers:
  - name: writer
    image: busybox:1.36
    command: ['sh', '-c', 'echo "Data written at \$(date)" > /data/timestamp.txt; sleep 3600']
    volumeMounts:
    - name: storage
      mountPath: /data
  volumes:
  - name: storage
    persistentVolumeClaim:
      claimName: lab-pvc
EOF
```

### Task 4: Verify Data Persistence

```bash
# Check the written data
k exec -n pv-lab storage-pod -- cat /data/timestamp.txt

# Delete the pod
k delete pod -n pv-lab storage-pod

# Recreate pod
cat <<EOF | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: storage-pod-v2
  namespace: pv-lab
spec:
  containers:
  - name: reader
    image: busybox:1.36
    command: ['sh', '-c', 'cat /data/timestamp.txt; sleep 3600']
    volumeMounts:
    - name: storage
      mountPath: /data
  volumes:
  - name: storage
    persistentVolumeClaim:
      claimName: lab-pvc
EOF

# Verify data persisted
k logs -n pv-lab storage-pod-v2
# Should show the original timestamp
```

### Task 5: Test Released State

```bash
# Delete the PVC (pod must be deleted first)
k delete pod -n pv-lab storage-pod-v2
k delete pvc -n pv-lab lab-pvc

# Check PV status
k get pv lab-pv
# STATUS should be "Released" (because of Retain policy)

# Make PV available again
k patch pv lab-pv -p '{"spec":{"claimRef": null}}'

k get pv lab-pv
# STATUS should be "Available"
```

### Success Criteria
- [ ] PV created and shows "Available"
- [ ] PVC created and binds to PV
- [ ] Pod can write data to mounted volume
- [ ] Data persists after pod deletion
- [ ] PV shows "Released" after PVC deletion
- [ ] PV can be made "Available" again

### Cleanup

```bash
k delete ns pv-lab
k delete pv lab-pv
```

---

## Practice Drills

### Drill 1: Create PV (2 min)
```bash
# Task: Create 5Gi PV with RWO access, Retain policy, storageClassName "slow"
# Backend: hostPath /mnt/data
```

### Drill 2: Create PVC (1 min)
```bash
# Task: Create PVC requesting 2Gi with RWO, storageClassName "slow"
```

### Drill 3: Check Binding (1 min)
```bash
# Task: Verify PVC bound to correct PV
# Commands: k get pvc, k get pv, check CLAIM column
```

### Drill 4: PVC Selector (2 min)
```bash
# Task: Create PVC that only binds to PVs with label "tier: gold"
# Use selector.matchLabels
```

### Drill 5: Pod with PVC (2 min)
```bash
# Task: Create pod mounting PVC "data-pvc" at /app/data
# Image: nginx
```

### Drill 6: Troubleshoot Pending PVC (2 min)
```bash
# Given: PVC stuck in Pending
# Task: Identify why it won't bind
# Check: k describe pvc, look at Events
```

### Drill 7: Reclaim Released PV (1 min)
```bash
# Task: Make a "Released" PV available again
# Command: k patch pv <name> -p '{"spec":{"claimRef": null}}'
```

### Drill 8: Local PV with nodeAffinity (3 min)
```bash
# Task: Create local PV that only works on node "worker-1"
# Include required nodeAffinity section
```

---

## Next Module

Continue to [Module 4.3: StorageClasses & Dynamic Provisioning](../module-4.3-storageclasses/) to learn about automatic PV creation.
