---
title: "Module 2.3: Storage Orchestration"
slug: k8s/kcna/part2-container-orchestration/module-2.3-storage
sidebar:
  order: 4
---
> **Complexity**: `[MEDIUM]` - Storage concepts
>
> **Time to Complete**: 25-30 minutes
>
> **Prerequisites**: Module 2.2 (Scaling)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Explain** the relationship between Volumes, PersistentVolumes, PersistentVolumeClaims, and StorageClasses
2. **Compare** access modes (ReadWriteOnce, ReadOnlyMany, ReadWriteMany) and their use cases
3. **Identify** when to use ephemeral vs. persistent storage for different workload types
4. **Evaluate** CSI drivers and their role in providing pluggable storage backends

---

## Why This Module Matters

Containers are ephemeral—when they restart, data is lost. Kubernetes provides storage abstractions that let stateful applications persist data across Pod restarts and rescheduling. KCNA tests your understanding of how Kubernetes manages storage.

---

## The Storage Problem

```
┌─────────────────────────────────────────────────────────────┐
│              WHY STORAGE IS NEEDED                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Without persistent storage:                               │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  1. Database Pod writes data                               │
│     [Pod] → writes → [container filesystem]               │
│                                                             │
│  2. Pod crashes or gets rescheduled                        │
│     [Pod] 💥 → deleted                                     │
│                                                             │
│  3. New Pod starts                                         │
│     [New Pod] → empty filesystem! Data lost!              │
│                                                             │
│  With persistent storage:                                  │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  1. Database Pod writes to volume                          │
│     [Pod] → writes → [Persistent Volume]                  │
│                                                             │
│  2. Pod crashes or gets rescheduled                        │
│     [Pod] 💥 → [Persistent Volume] still exists!         │
│                                                             │
│  3. New Pod starts and attaches to same volume            │
│     [New Pod] → reads → [Persistent Volume] Data safe!    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Storage Concepts Overview

```
┌─────────────────────────────────────────────────────────────┐
│              KUBERNETES STORAGE MODEL                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Three key resources:                                      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  PersistentVolume (PV)                              │   │
│  │  • Actual storage resource                          │   │
│  │  • Provisioned by admin OR dynamically             │   │
│  │  • Cluster-wide resource                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↑                                   │
│                         │ binds to                         │
│                         │                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  PersistentVolumeClaim (PVC)                        │   │
│  │  • Request for storage                              │   │
│  │  • Created by users/applications                    │   │
│  │  • Namespace-scoped resource                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↑                                   │
│                         │ used by                          │
│                         │                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Pod                                                │   │
│  │  • Mounts PVC as volume                            │   │
│  │  • Reads/writes to storage                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## PersistentVolume (PV)

A **PersistentVolume** is a piece of storage in the cluster:

```
┌─────────────────────────────────────────────────────────────┐
│              PERSISTENTVOLUME                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Key attributes:                                           │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  capacity:                                                 │
│    storage: 10Gi          # How much storage              │
│                                                             │
│  accessModes:                                              │
│  - ReadWriteOnce          # How it can be accessed        │
│                                                             │
│  persistentVolumeReclaimPolicy: Retain                    │
│                            # What happens when released   │
│                                                             │
│  storageClassName: fast   # Class of storage              │
│                                                             │
│  Access Modes:                                             │
│  ─────────────────────────────────────────────────────────  │
│  • ReadWriteOnce (RWO): One node can mount read-write     │
│  • ReadOnlyMany (ROX): Many nodes can mount read-only     │
│  • ReadWriteMany (RWX): Many nodes can mount read-write   │
│                                                             │
│  Reclaim Policies:                                         │
│  ─────────────────────────────────────────────────────────  │
│  • Retain: Keep data after PVC deleted (manual cleanup)   │
│  • Delete: Delete storage when PVC deleted               │
│  • Recycle: (Deprecated) Basic scrub and reuse           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Pause and predict**: A PersistentVolume is cluster-scoped, but a PersistentVolumeClaim is namespace-scoped. Why do you think the designers made this distinction? What would happen if a team in one namespace could claim a PV that another team was already using?

## PersistentVolumeClaim (PVC)

A **PersistentVolumeClaim** is a request for storage:

```
┌─────────────────────────────────────────────────────────────┐
│              PERSISTENTVOLUMECLAIM                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User creates PVC:                                         │
│  ─────────────────────────────────────────────────────────  │
│  "I need 5GB of fast storage with ReadWriteOnce access"   │
│                                                             │
│  apiVersion: v1                                            │
│  kind: PersistentVolumeClaim                              │
│  metadata:                                                 │
│    name: my-data                                          │
│  spec:                                                     │
│    accessModes:                                            │
│      - ReadWriteOnce                                      │
│    resources:                                              │
│      requests:                                             │
│        storage: 5Gi                                       │
│    storageClassName: fast                                 │
│                                                             │
│  Kubernetes finds matching PV:                            │
│  ─────────────────────────────────────────────────────────  │
│  ┌───────────┐                     ┌───────────┐          │
│  │   PVC     │                     │    PV     │          │
│  │ 5Gi       │ ────── binds ─────→ │ 10Gi      │          │
│  │ RWO       │                     │ RWO       │          │
│  │ fast      │                     │ fast      │          │
│  └───────────┘                     └───────────┘          │
│                                                             │
│  PVC gets 10Gi (smallest PV that satisfies request)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## StorageClass

A **StorageClass** enables dynamic provisioning:

```
┌─────────────────────────────────────────────────────────────┐
│              STORAGECLASS                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Without StorageClass (Static Provisioning):              │
│  ─────────────────────────────────────────────────────────  │
│  1. Admin creates PV manually                              │
│  2. User creates PVC                                       │
│  3. PVC binds to pre-existing PV                          │
│                                                             │
│  With StorageClass (Dynamic Provisioning):                │
│  ─────────────────────────────────────────────────────────  │
│  1. Admin creates StorageClass                            │
│  2. User creates PVC referencing StorageClass             │
│  3. PV is automatically created!                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  StorageClass: fast                                 │   │
│  │  provisioner: kubernetes.io/aws-ebs               │   │
│  │  parameters:                                        │   │
│  │    type: gp3                                        │   │
│  │    iopsPerGB: "10"                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│           │                                                 │
│           │ PVC requests "fast" StorageClass              │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Provisioner automatically creates:                 │   │
│  │  • AWS EBS volume                                   │   │
│  │  • PersistentVolume                                │   │
│  │  • Binds PVC to new PV                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Common provisioners:                                      │
│  • kubernetes.io/aws-ebs (AWS)                           │
│  • kubernetes.io/gce-pd (GCP)                            │
│  • kubernetes.io/azure-disk (Azure)                      │
│  • rancher.io/local-path (local)                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Volume Types

Kubernetes supports many volume types:

| Type | Description | Persistent |
|------|-------------|------------|
| **emptyDir** | Temporary directory, deleted with Pod | No |
| **hostPath** | Mount from node's filesystem | Node-specific |
| **persistentVolumeClaim** | Use PVC for storage | Yes |
| **configMap** | Mount ConfigMap as files | No |
| **secret** | Mount Secret as files | No |
| **nfs** | Network File System | Yes |
| **awsElasticBlockStore** | AWS EBS volume | Yes |
| **gcePersistentDisk** | GCP persistent disk | Yes |
| **azureDisk** | Azure managed disk | Yes |

---

## Static vs Dynamic Provisioning

```
┌─────────────────────────────────────────────────────────────┐
│              STATIC vs DYNAMIC                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STATIC PROVISIONING:                                      │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Admin                    User                             │
│    │                        │                               │
│    │ 1. Create PV           │                               │
│    ▼                        │                               │
│  [PV: 100Gi]               │                               │
│                             │ 2. Create PVC                 │
│                             ▼                               │
│  [PV: 100Gi] ←── binds ── [PVC: 50Gi]                     │
│                                                             │
│  Pros: Full control, pre-allocate storage                 │
│  Cons: Admin must create PVs in advance                   │
│                                                             │
│  DYNAMIC PROVISIONING:                                     │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Admin creates once:       User                            │
│  [StorageClass: fast]        │                             │
│                              │ 1. Create PVC               │
│                              │    storageClassName: fast   │
│                              ▼                              │
│  Provisioner ───────────→ [PV: 50Gi] ── binds ── [PVC]   │
│  automatically                                              │
│  creates                                                    │
│                                                             │
│  Pros: Self-service, on-demand, efficient                 │
│  Cons: Requires cloud provider or storage system          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## PV Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│              PV LIFECYCLE                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Available ──→ Bound ──→ Released ──→ (Reclaim Policy)    │
│                                                             │
│  AVAILABLE:                                                │
│  • PV exists, not claimed by any PVC                      │
│  • Ready to be bound                                       │
│                                                             │
│  BOUND:                                                    │
│  • PV is claimed by a PVC                                 │
│  • Pod can use it                                         │
│  • One-to-one relationship                                │
│                                                             │
│  RELEASED:                                                 │
│  • PVC deleted, but PV still has data                     │
│  • Not available for new claims                           │
│                                                             │
│  After release (based on reclaimPolicy):                  │
│  • Retain: Stays Released, manual cleanup needed          │
│  • Delete: PV and underlying storage deleted              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Stop and think**: Your database runs on a Pod in us-east-1a. The Pod crashes and gets rescheduled to a node in us-east-1b, but the PersistentVolume was an EBS volume in us-east-1a. What problem does this create, and how does `WaitForFirstConsumer` storage binding help?

## Using Storage in Pods

```yaml
# Pod using a PVC
apiVersion: v1
kind: Pod
metadata:
  name: database
spec:
  containers:
  - name: mysql
    image: mysql:8.0
    volumeMounts:
    - name: data
      mountPath: /var/lib/mysql    # Where to mount in container
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: mysql-pvc         # Reference to PVC
```

---

## Did You Know?

- **Volume binding** - Kubernetes only binds PV to PVC when a Pod actually needs it (WaitForFirstConsumer mode). This ensures storage is provisioned in the same zone as the Pod.

- **StorageClass is cluster-scoped** - Unlike PVCs (namespace-scoped), StorageClasses are available to all namespaces.

- **emptyDir survives container restarts** - Data in emptyDir is only lost when the Pod is deleted, not when a container restarts.

- **CSI is the standard** - Container Storage Interface (CSI) is the modern way to integrate storage systems with Kubernetes. Legacy in-tree volume plugins are being migrated to CSI.

---

## Common Mistakes

| Mistake | Why It Hurts | Correct Understanding |
|---------|--------------|----------------------|
| Using emptyDir for permanent data | Data lost when Pod deleted | Use PVC for persistent data |
| Expecting RWX everywhere | Not all storage supports it | Check storage capabilities |
| Forgetting reclaim policy | Might delete data accidentally | Set Retain for important data |
| Static provisioning at scale | Too much admin work | Use dynamic provisioning |

---

## Quiz

1. **A developer creates a Pod with a MySQL container that stores data in the container filesystem. After a routine update, the Pod is recreated and all database records are gone. What happened, and how should they have configured storage to prevent data loss?**
   <details>
   <summary>Answer</summary>
   Container filesystems are ephemeral -- when a Pod is deleted, all data in the container's writable layer is lost permanently. The developer should have created a PersistentVolumeClaim (PVC) and mounted it into the container at `/var/lib/mysql`. The PVC binds to a PersistentVolume that persists independently of the Pod lifecycle. When the Pod is recreated, it reattaches to the same PVC and finds all data intact. This is the fundamental reason persistent storage exists in Kubernetes.
   </details>

2. **Your application needs a shared filesystem where 5 Pods across 3 different nodes all read and write the same files simultaneously. Which access mode do you need, and why won't the most common access mode work?**
   <details>
   <summary>Answer</summary>
   You need ReadWriteMany (RWX), which allows multiple nodes to mount the volume simultaneously for both reading and writing. The most common access mode, ReadWriteOnce (RWO), only allows a single node to mount the volume in read-write mode. If your Pods are spread across multiple nodes (which is likely with 5 Pods on 3 nodes), RWO would prevent Pods on other nodes from mounting the volume. Not all storage backends support RWX -- you would need a network filesystem like NFS, EFS (AWS), or a distributed storage solution like CephFS.
   </details>

3. **An admin pre-creates 50 PVs of various sizes for the team. Developers complain that they have to wait for the admin to create new PVs whenever they need storage. How would you change this to a self-service model?**
   <details>
   <summary>Answer</summary>
   Create StorageClasses that enable dynamic provisioning. Instead of pre-creating PVs, the admin creates one or more StorageClasses (e.g., "fast" for SSD, "standard" for HDD) with a provisioner (like `kubernetes.io/aws-ebs`). Developers then create PVCs referencing the StorageClass, and Kubernetes automatically provisions a PV of the requested size on demand. This is more efficient (no wasted pre-allocated storage), scales better, and eliminates the admin bottleneck.
   </details>

4. **A team accidentally deletes a PVC that was backing their production database. With the `Delete` reclaim policy, the underlying cloud disk is destroyed. How would you configure the system differently to prevent this kind of data loss?**
   <details>
   <summary>Answer</summary>
   Change the reclaim policy to `Retain`. With Retain, when a PVC is deleted, the PV transitions to "Released" state but the underlying storage and data are preserved. An admin can then manually recover the data or rebind the PV to a new PVC. Additionally, consider using PVC protection (enabled by default) which prevents deletion of PVCs that are actively used by Pods, and implement RBAC to restrict who can delete PVCs in production namespaces.
   </details>

5. **A Pod mounts an emptyDir volume for temporary data processing and also mounts a PVC for long-term results. The container restarts due to a crash, and later the entire Pod is rescheduled to a different node. Which data survives each event?**
   <details>
   <summary>Answer</summary>
   On container restart (Pod stays on same node): both the emptyDir and PVC data survive, because emptyDir persists for the lifetime of the Pod (not the container). On Pod rescheduling to a different node: only the PVC data survives. The emptyDir is tied to the Pod's lifecycle on that specific node -- when the Pod is deleted, the emptyDir is deleted too. The PVC data persists independently because the PersistentVolume exists at the cluster level and can be reattached when the new Pod starts on the new node.
   </details>

---

## Summary

**Storage resources**:
- **PersistentVolume (PV)**: Actual storage
- **PersistentVolumeClaim (PVC)**: Request for storage
- **StorageClass**: Enables dynamic provisioning

**Access modes**:
- **RWO**: One node read-write
- **ROX**: Many nodes read-only
- **RWX**: Many nodes read-write

**Provisioning**:
- **Static**: Admin creates PVs manually
- **Dynamic**: PVs created automatically via StorageClass

**Reclaim policies**:
- **Retain**: Keep data after PVC deletion
- **Delete**: Remove storage when PVC deleted

---

## Next Module

[Module 2.4: Configuration](../module-2.4-configuration/) - Managing application configuration with ConfigMaps and Secrets.
