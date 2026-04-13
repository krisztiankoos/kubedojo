---
title: "Module 1.4: High-Performance Storage for AI"
slug: platform/disciplines/data-ai/ai-infrastructure/module-1.4-ai-storage
sidebar:
  order: 5
---
> **Discipline Module** | Complexity: `[MEDIUM]` | Time: 3 hours

## Prerequisites

Before starting this module:
- **Required**: Kubernetes storage fundamentals (PersistentVolumes, PersistentVolumeClaims, StorageClasses, CSI drivers)
- **Required**: Basic understanding of ML training data pipelines (datasets, batches, data loaders)
- **Recommended**: [Module 1.1: GPU Provisioning](../module-1.1-gpu-provisioning/) — GPU workload basics
- **Recommended**: Experience with object storage (S3, GCS, MinIO)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

- **Design high-throughput storage architectures for AI workloads — training data, checkpoints, and model artifacts**
- **Implement storage solutions using CSI drivers, NFS, and object storage optimized for large-scale data access**
- **Configure caching layers that reduce data loading bottlenecks during distributed training**
- **Evaluate storage options — local NVMe, network-attached, cloud object stores — against AI workload I/O patterns**

## Why This Module Matters

You spent months building a beautiful GPU platform. The GPUs are provisioned, shared efficiently, connected by InfiniBand. Then your ML team starts training and reports this:

> "Our 8-GPU job only uses 40% GPU utilization. The GPUs are waiting for data."

This is the **IO bottleneck** — the most common and most underestimated performance killer in AI infrastructure. Your $300,000 DGX node is sitting idle 60% of the time because the storage system cannot feed data to the GPUs fast enough.

The numbers are stark:

| Component | Throughput | Latency |
|-----------|-----------|---------|
| GPU compute (A100 BF16) | 312 TFLOPS | nanoseconds |
| GPU memory (HBM3) | 2 TB/s | nanoseconds |
| NVMe SSD (local) | 7 GB/s | 10-100 μs |
| Network storage (CephFS) | 1-5 GB/s | 0.5-5 ms |
| Object storage (S3) | 100-500 MB/s | 10-100 ms |

There is a **1,000x gap** between GPU memory speed and network storage speed. Bridging this gap is what this module is about.

---

## The IO Bottleneck in ML Workloads

### Where IO Happens

Every training step involves IO at multiple stages:

```mermaid
flowchart LR
    subgraph Training_Loop ["Training Loop (This dominates when storage is slow)"]
        direction LR
        A["1. Load batch\nRead from storage\n(IO bound)\n100ms - 5s"] --> B["2. Transfer to GPU\nCPU RAM → GPU VRAM\n(PCIe bound)\n1-10ms"]
        B --> C["3. Compute\nForward + Backward\n(compute)\n10-100ms"]
    end
```

### Workload IO Profiles

Different ML workloads have radically different IO characteristics:

| Workload | Data Size | Access Pattern | Read Size | Throughput Need |
|----------|-----------|---------------|-----------|-----------------|
| Image classification (ImageNet) | 150 GB | Random, small files | 100-500 KB | 2-5 GB/s |
| Object detection (COCO) | 20 GB | Random, medium files | 200 KB - 5 MB | 1-3 GB/s |
| NLP pre-training (C4) | 800 GB | Sequential, large files | 1-100 MB | 5-20 GB/s |
| Video training | 5-50 TB | Sequential, very large | 50-500 MB | 10-50 GB/s |
| LLM fine-tuning (tokenized) | 10-100 GB | Sequential | 1-10 MB | 1-5 GB/s |
| Checkpoint save | 1-50 GB per save | Sequential write | Full model | 5-20 GB/s burst |

The key insight: **image training** does millions of small random reads (hard for network storage), while **LLM training** does large sequential reads (easier to cache).

> **Pause and predict**: If you are training a large language model vs an image classification model, how will the I/O read patterns differ?

### Profiling IO Bottlenecks

Before optimizing, measure. Run your training job with GPU utilization monitoring:

```bash
# Monitor GPU utilization during training
# If GPU util is < 80% and you're not memory-bound, you're IO-bound

# Quick check: watch nvidia-smi during training
kubectl exec -it training-pod -- watch -n 1 'nvidia-smi --query-gpu=utilization.gpu,utilization.memory --format=csv,noheader'

# Better: check PyTorch DataLoader timing
# Add this to your training script:
# import time
# for batch in dataloader:
#     load_end = time.time()
#     print(f"Data load: {load_end - load_start:.3f}s")
#     # ... training step ...
#     load_start = time.time()
```

> **Stop and think**: If your GPU utilization is at 40%, what metrics would you check to confirm it's an I/O bottleneck rather than a CPU compute bottleneck?

---

## Storage Tiers for AI

### The Storage Pyramid

AI workloads need a multi-tier storage architecture:

```mermaid
flowchart TD
    A["GPU VRAM (training)\n2 TB/s, μs latency\nManaged by framework"]
    B["Local NVMe (hot cache)\n3-14 GB/s, 10-100 μs\nTopoLVM, OpenEBS LVM"]
    C["Distributed FS (warm)\n1-10 GB/s, 0.5-5 ms\nCephFS, GlusterFS, JuiceFS"]
    D["Object Storage (cold)\n100 MB-5 GB/s, 10-100 ms\nS3, GCS, MinIO"]
    E["Tape/Archive\nArchival\nGlacier, Coldline"]

    A -->|"Cost $, Speed $$$$"| B
    B -->|"Cost $$, Speed $$$"| C
    C -->|"Cost $$$, Speed $$"| D
    D -->|"Cost $$$$, Speed $"| E
```

The platform team's job is to build infrastructure that automatically moves data between tiers based on access patterns.

---

## Local NVMe Caching

### Why Local Storage Matters

A modern NVMe SSD delivers 3-7 GB/s sequential read and 500K-1M IOPS random read. This is 10-50x faster than network storage for the random small-file reads that image training demands.

The strategy: keep the active dataset (or a cache of it) on local NVMe while the canonical copy lives in object storage.

### TopoLVM: Topology-Aware Local Volumes

TopoLVM is a CSI driver that provisions PersistentVolumes from local LVM volume groups, with **topology awareness** — it ensures Pods are scheduled on nodes that have available local storage.

```bash
# Install TopoLVM
helm repo add topolvm https://topolvm.github.io/topolvm
helm repo update

helm install topolvm topolvm/topolvm \
  --namespace topolvm-system \
  --create-namespace \
  --set controller.replicaCount=2 \
  --set node.volumeGroup.name=nvme-vg    # LVM VG name on each node
```

Create a StorageClass:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nvme-local
provisioner: topolvm.io
parameters:
  topolvm.io/device-class: nvme       # Maps to a device class in TopoLVM config
volumeBindingMode: WaitForFirstConsumer # Delay binding until Pod is scheduled
allowVolumeExpansion: true
reclaimPolicy: Delete
```

Use in a training Pod:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: training-cache
  namespace: ml-training
spec:
  storageClassName: nvme-local
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 500Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: image-trainer
  namespace: ml-training
spec:
  containers:
    - name: trainer
      image: nvcr.io/nvidia/pytorch:24.09-py3
      volumeMounts:
        - name: cache
          mountPath: /data/cache
        - name: dataset
          mountPath: /data/s3     # S3 FUSE mount or pre-downloaded
      resources:
        limits:
          nvidia.com/gpu: 4
  volumes:
    - name: cache
      persistentVolumeClaim:
        claimName: training-cache
    - name: dataset
      persistentVolumeClaim:
        claimName: imagenet-s3
```

### OpenEBS LVM Local PV

OpenEBS provides a simpler alternative for local NVMe provisioning:

```bash
# Install OpenEBS LVM LocalPV
helm repo add openebs https://openebs.github.io/openebs
helm repo update

helm install openebs openebs/openebs \
  --namespace openebs \
  --create-namespace \
  --set lvm-localpv.enabled=true \
  --set engines.replicated.mayastor.enabled=false
```

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: openebs-nvme
provisioner: local.csi.openebs.io
parameters:
  storage: "lvm"
  vgPattern: "nvme-vg"          # LVM volume group pattern
  fsType: "xfs"                  # XFS recommended for large files
volumeBindingMode: WaitForFirstConsumer
```

### Init Container Pattern for Data Staging

A common pattern: use an init container to stage data from object storage to local NVMe before training begins:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: training-with-staging
  namespace: ml-training
spec:
  template:
    spec:
      initContainers:
        - name: stage-data
          image: amazon/aws-cli:2.17
          command: ["sh", "-c"]
          args:
            - |
              echo "Staging dataset from S3..."
              start=$(date +%s)
              aws s3 sync s3://my-datasets/imagenet/ /data/cache/imagenet/ \
                --no-sign-request --quiet
              end=$(date +%s)
              size=$(du -sh /data/cache/imagenet/ | cut -f1)
              echo "Staged $size in $((end-start)) seconds"
          volumeMounts:
            - name: cache
              mountPath: /data/cache
          resources:
            requests:
              cpu: "4"
              memory: 8Gi
      containers:
        - name: trainer
          image: nvcr.io/nvidia/pytorch:24.09-py3
          command: ["torchrun", "--nproc_per_node=4", "train.py", "--data_dir=/data/cache/imagenet"]
          volumeMounts:
            - name: cache
              mountPath: /data/cache
          resources:
            limits:
              nvidia.com/gpu: 4
      volumes:
        - name: cache
          persistentVolumeClaim:
            claimName: training-cache
      restartPolicy: OnFailure
```

---

## Distributed Filesystems

### CephFS

Ceph is the most widely deployed distributed storage system in Kubernetes. CephFS provides a POSIX-compatible filesystem backed by the Ceph cluster.

**Strengths for AI**:
- POSIX semantics (training frameworks expect filesystem APIs)
- Scalable metadata server (can handle millions of small files)
- Multi-reader access (ReadWriteMany) for data-parallel training
- Integrated with Rook for Kubernetes-native deployment

**Weaknesses for AI**:
- Latency: 0.5-5ms per operation (100-1000x slower than local NVMe)
- Throughput ceiling: limited by network and OSD count
- Small file performance: poor for millions of tiny files (image datasets)

```yaml
# Rook-Ceph CephFS StorageClass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: cephfs-ai
provisioner: rook-ceph.cephfs.csi.ceph.com
parameters:
  clusterID: rook-ceph
  fsName: ai-filesystem
  pool: ai-data-pool
  csi.storage.k8s.io/provisioner-secret-name: rook-csi-cephfs-provisioner
  csi.storage.k8s.io/provisioner-secret-namespace: rook-ceph
  csi.storage.k8s.io/node-stage-secret-name: rook-csi-cephfs-node
  csi.storage.k8s.io/node-stage-secret-namespace: rook-ceph
mountOptions:
  - noatime                    # Disable access time updates (major perf win)
  - nodiratime
```

### JuiceFS

JuiceFS is a cloud-native distributed filesystem purpose-built for the gap between object storage and high-performance compute. It separates metadata (stored in Redis, PostgreSQL, or TiKV) from data (stored in any object storage).

```mermaid
flowchart LR
    Client["POSIX Client\n(FUSE/CSI)"]
    Meta["Metadata Engine\n(Redis/PG)"]
    Obj["Object Storage\n(S3)"]
    Cache["Local Cache\n(NVMe or RAM)"]

    Client -->|"Metadata"| Meta
    Client -->|"Data path"| Obj
    Client <-->|"Local caching"| Cache
```

**Why JuiceFS excels for AI**:
1. **Transparent caching**: Reads are cached on local NVMe. Second read of same file is at NVMe speed.
2. **POSIX compatible**: Drop-in replacement for local filesystem in training scripts.
3. **Any object store backend**: S3, GCS, Azure Blob, MinIO — your data stays where it is.
4. **Metadata engine flexibility**: Redis for speed, PostgreSQL for durability, TiKV for scale.
5. **Kubernetes-native**: CSI driver with dynamic provisioning.

### Installing JuiceFS CSI Driver

```bash
# Install JuiceFS CSI Driver
helm repo add juicefs https://juicedata.github.io/charts/
helm repo update

helm install juicefs-csi juicefs/juicefs-csi-driver \
  --namespace kube-system \
  --set storageClasses[0].name=juicefs-sc \
  --set storageClasses[0].enabled=true \
  --set storageClasses[0].backend.name=ai-data \
  --set storageClasses[0].backend.metaurl=redis://:password@redis-master:6379/1 \
  --set storageClasses[0].backend.storage=s3 \
  --set storageClasses[0].backend.bucket=s3://my-ai-datasets \
  --set storageClasses[0].backend.accessKey=AKIAIOSFODNN7EXAMPLE \
  --set storageClasses[0].backend.secretKey=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
  --set storageClasses[0].cachePVC=juicefs-cache
```

### JuiceFS StorageClass with Caching

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: juicefs-ai
provisioner: csi.juicefs.com
parameters:
  csi.storage.k8s.io/provisioner-secret-name: juicefs-secret
  csi.storage.k8s.io/provisioner-secret-namespace: kube-system
  juicefs/mount-options: |
    cache-dir=/var/jfsCache
    cache-size=512000          # 500GB local cache
    buffer-size=1024           # 1GB read-ahead buffer
    prefetch=3                 # Prefetch 3 blocks ahead
    max-uploads=40             # Parallel upload threads
    metacache-expire=300       # Metadata cache TTL (seconds)
    open-cache=300             # Open file handle cache
reclaimPolicy: Retain
volumeBindingMode: Immediate
```

---

## Dataset Caching: Fluid and Alluxio

### The Caching Problem

Consider this scenario: 50 ML engineers share a 500GB ImageNet dataset stored in S3. Without caching:

```
Engineer 1 training job: Downloads 500GB from S3 → 30 min
Engineer 2 training job: Downloads 500GB from S3 → 30 min
...
Engineer 50 training job: Downloads 500GB from S3 → 30 min

Total: 25 TB downloaded, 25 hours of wait time, $50+ in S3 egress
```

With a caching layer:

```
Engineer 1 training job: Downloads 500GB from S3 → 30 min (cold)
Engineer 2 training job: Reads from cache → 2 min (warm)
...
Engineer 50 training job: Reads from cache → 2 min (warm)

Total: 500GB downloaded, 2 hours total wait, $1 in S3 egress
```

> **Stop and think**: How much money could you save in cloud egress costs if 50 engineers are constantly downloading a 500GB dataset from S3 every day, and you switch to local caching?

### Fluid: Kubernetes-Native Dataset Orchestration

Fluid is a CNCF sandbox project that brings dataset-aware scheduling to Kubernetes. It manages datasets as first-class resources and uses cache engines (Alluxio, JuiceFS, JindoFS) under the hood.

```bash
# Install Fluid
helm repo add fluid https://fluid-cloudnative.github.io/charts
helm repo update

helm install fluid fluid/fluid \
  --namespace fluid-system \
  --create-namespace
```

Define a dataset and its caching runtime:

```yaml
apiVersion: data.fluid.io/v1alpha1
kind: Dataset
metadata:
  name: imagenet
  namespace: ml-training
spec:
  mounts:
    - mountPoint: s3://my-datasets/imagenet/
      name: imagenet
      options:
        aws.accessKeyId: AKIAIOSFODNN7EXAMPLE
        aws.region: us-east-1
      encryptOptions:
        - name: aws.secretAccessKey
          valueFrom:
            secretKeyRef:
              name: s3-credentials
              key: secretAccessKey
---
apiVersion: data.fluid.io/v1alpha1
kind: AlluxioRuntime
metadata:
  name: imagenet
  namespace: ml-training
spec:
  replicas: 3                    # 3 cache workers
  tieredstore:
    levels:
      - mediumtype: SSD
        path: /dev/shm,/var/cache/alluxio
        quota: 100Gi,400Gi       # 100GB RAM + 400GB SSD cache per worker
        high: "0.95"
        low: "0.7"
  fuse:
    args:
      - fuse
      - --attr-timeout=7200s
      - --entry-timeout=7200s
    cleanPolicy: OnDemand
  properties:
    alluxio.user.metadata.cache.enabled: "true"
    alluxio.user.metadata.cache.expireTime: "2day"
    alluxio.user.streaming.data.timeout: "300sec"
```

Use the dataset in a training Pod:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: imagenet-training
  namespace: ml-training
spec:
  template:
    spec:
      containers:
        - name: trainer
          image: nvcr.io/nvidia/pytorch:24.09-py3
          command: ["python", "train.py", "--data_dir=/data/imagenet"]
          volumeMounts:
            - name: imagenet
              mountPath: /data/imagenet
              readOnly: true
          resources:
            limits:
              nvidia.com/gpu: 4
      volumes:
        - name: imagenet
          persistentVolumeClaim:
            claimName: imagenet    # Automatically created by Fluid
      restartPolicy: OnFailure
```

### Fluid's Data-Aware Scheduling

Fluid tracks where cached data resides and preferentially schedules Pods on nodes that already have the data cached:

```yaml
# Fluid automatically injects scheduling hints
# Pods using the 'imagenet' dataset prefer nodes where Alluxio workers
# have already cached ImageNet data

# You can also trigger pre-warming:
apiVersion: data.fluid.io/v1alpha1
kind: DataLoad
metadata:
  name: imagenet-warmup
  namespace: ml-training
spec:
  dataset:
    name: imagenet
    namespace: ml-training
  loadMetadata: true
  target:
    - path: /
      replicas: 2    # Cache 2 copies for fault tolerance
```

### Alluxio Standalone (without Fluid)

For teams that want more control, Alluxio can be deployed independently:

```bash
helm repo add alluxio https://alluxio-charts.storage.googleapis.com/openSource
helm repo update

helm install alluxio alluxio/alluxio \
  --namespace alluxio \
  --create-namespace \
  --set master.count=1 \
  --set worker.count=3 \
  --set worker.resources.limits.memory=32Gi \
  --set tieredStore.levels[0].level=0 \
  --set tieredStore.levels[0].mediumtype=MEM \
  --set tieredStore.levels[0].path=/dev/shm \
  --set tieredStore.levels[0].quota=16Gi \
  --set tieredStore.levels[1].level=1 \
  --set tieredStore.levels[1].mediumtype=SSD \
  --set tieredStore.levels[1].path=/mnt/nvme/alluxio \
  --set tieredStore.levels[1].quota=500Gi \
  --set properties."alluxio.underfs.s3.region"=us-east-1
```

---

## Checkpoint Storage

### Why Checkpoint IO Matters

During training, checkpoints must be saved periodically. A checkpoint for a 70B parameter model is:

```
Model parameters:   70B × 2 bytes (BF16)  = 140 GB
Optimizer state:    70B × 8 bytes (Adam)   = 560 GB
Total:              ~700 GB per checkpoint
```

If your storage can write at 2 GB/s, saving one checkpoint takes **350 seconds** — almost 6 minutes. During this time, GPUs are either idle (synchronous checkpoint) or must continue while carefully not overwriting the in-flight checkpoint (asynchronous).

### Strategies for Fast Checkpointing

**Synchronous (simple, slow)**:
```python
# Training pauses during save
torch.save(model.state_dict(), "/checkpoints/latest.pt")
# 6 minutes of idle GPUs
```

**Asynchronous with background thread**:
```python
import threading

def save_async(state_dict, path):
    torch.save(state_dict, path)

# Clone state dict to CPU, then save in background
state_dict_cpu = {k: v.cpu().clone() for k, v in model.state_dict().items()}
thread = threading.Thread(target=save_async, args=(state_dict_cpu, path))
thread.start()
# Training continues immediately
```

**Sharded checkpoints** (PyTorch FSDP / DeepSpeed):
```python
# Each GPU saves its own shard in parallel
# 8 GPUs writing 87.5 GB each at 2 GB/s = 44 seconds (vs 350 seconds serial)
from torch.distributed.checkpoint import save
save(model.state_dict(), checkpoint_id=f"/checkpoints/step_{step}")
```

> **Pause and predict**: What is the risk of using asynchronous checkpointing if the node crashes exactly while the background thread is writing the checkpoint?

### Recommended Checkpoint Storage

| Storage Type | Write Speed | Best For |
|-------------|-------------|----------|
| Local NVMe (TopoLVM) | 5-7 GB/s | Fastest saves; risk of data loss on node failure |
| CephFS / GlusterFS (RWX) | 1-5 GB/s | Shared access, multi-node distributed saves |
| JuiceFS (NVMe cache + S3) | 3-7 GB/s local, async to S3 | Best of both: fast writes, durable storage |
| NFS | 0.5-2 GB/s | Simple, widely available; potential bottleneck |

---

## Try This: Measure Your Storage Performance

Run this inside a Pod on your cluster to understand your storage baseline:

```bash
# Create a test pod with your storage class
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: storage-bench
  namespace: default
spec:
  containers:
    - name: bench
      image: ubuntu:22.04
      command: ["sleep", "infinity"]
      volumeMounts:
        - name: test-vol
          mountPath: /data
      resources:
        requests:
          cpu: "4"
          memory: 8Gi
  volumes:
    - name: test-vol
      persistentVolumeClaim:
        claimName: bench-pvc
EOF

# Inside the pod:
kubectl exec -it storage-bench -- bash

apt-get update && apt-get install -y fio

# Sequential read (simulates loading a large dataset)
fio --name=seq-read --rw=read --bs=1M --size=10G \
  --numjobs=4 --direct=1 --directory=/data \
  --runtime=60 --time_based --group_reporting

# Random read (simulates image dataset loading)
fio --name=rand-read --rw=randread --bs=256K --size=10G \
  --numjobs=8 --direct=1 --directory=/data \
  --runtime=60 --time_based --group_reporting \
  --iodepth=32

# Sequential write (simulates checkpoint saves)
fio --name=seq-write --rw=write --bs=1M --size=10G \
  --numjobs=4 --direct=1 --directory=/data \
  --runtime=60 --time_based --group_reporting
```

---

## Did You Know?

1. **ImageNet, the dataset that launched the deep learning revolution, contains 14 million images totaling about 150GB**. But the images are tiny JPEG files (average ~10KB each). This means loading ImageNet requires 14 million random reads — a worst case for any storage system. This is why ImageNet training was one of the first workloads to expose storage bottlenecks in GPU clusters.

2. **The concept of "data gravity" is literal in AI infrastructure**. Moving a 10TB dataset across the internet takes hours to days, but computing on it takes seconds to minutes. This is why cloud providers offer "data import" services where they physically ship hard drives. Google's Transfer Appliance can hold 1 PB and ships via FedEx — sometimes the highest-bandwidth network is a truck full of disks.

3. **Meta reported that during Llama 3 training, their storage system served 240 PB of data over the 54-day run** — roughly 4.4 PB per day, or 51 GB per second sustained. This required a custom distributed filesystem (Tectonic) because no off-the-shelf system could handle this throughput at this scale.

---

## War Story: The Cache That Saved $200K

A medical imaging startup trained models on a 2TB dataset of CT scans stored in Google Cloud Storage (GCS). They had 20 GPU nodes, each running training jobs that loaded the full dataset.

**Before caching**: Each job downloaded 2TB from GCS at ~500 MB/s = 67 minutes startup time. With 20 nodes running 3 jobs/day each, they downloaded **120 TB/day** from GCS.

- GCS egress cost: $0.12/GB × 120,000 GB/day = $14,400/day = **$432,000/month**
- GPU idle time during downloads: 20 nodes × 3 jobs × 67 min = 67 GPU-hours/day wasted

**After JuiceFS with NVMe cache**: First job on each node downloads from GCS (cold cache). Subsequent jobs read from local NVMe cache at 5 GB/s = 7 minutes.

- GCS egress: 20 nodes × 2TB × 1 download/week = 40TB/week = **$19,200/month**
- GPU idle time: negligible (7 min cached vs 67 min uncached)

**Monthly savings**: $432,000 - $19,200 = **$412,800/month**. The caching infrastructure (JuiceFS + NVMe on each node) cost $3,000/month.

**Lesson**: In AI infrastructure, the most impactful optimization is often the simplest: cache the dataset close to the GPUs.

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Using S3 FUSE mounts for training | FUSE adds 2-10x latency overhead per IO operation | Use JuiceFS or Alluxio with local NVMe cache; or download to local disk first |
| Network storage for ImageNet-style training | Millions of small random reads kill network storage | Cache dataset on local NVMe; or use WebDataset/TFRecord for sequential access |
| Synchronous checkpoints on slow storage | GPUs idle for minutes during each checkpoint save | Use async checkpointing or sharded distributed checkpoints |
| No `noatime` mount option | Every file read triggers a metadata write (access time update) | Always mount with `noatime,nodiratime` for training volumes |
| RWO volumes for multi-node training | ReadWriteOnce cannot be mounted on multiple nodes | Use RWX storage (CephFS, NFS, JuiceFS) or local cache per node |
| Ignoring storage class `volumeBindingMode` | PVC binds to wrong node before Pod is scheduled | Always use `WaitForFirstConsumer` for local storage |
| Not pre-warming cache before training | First epoch runs at cold-cache speed, skewing benchmark results | Use Fluid's `DataLoad` CRD or an init container to warm cache |
| Using ext4 for large files | ext4 fragments large sequential writes | Use XFS for datasets and checkpoint volumes; it handles large files better |

---

## Quiz: Check Your Understanding

### Question 1
*Scenario*: Your ML team wants to train a new ResNet model directly against a 150GB S3 bucket containing 14 million individual JPEG files. They've mounted the bucket using an S3 FUSE driver. They report that the training is exceptionally slow, even though the total dataset is relatively small. What underlying characteristics of object storage make this architecture problematic for this specific workload?

<details>
<summary>Show Answer</summary>

Three compounding issues explain why this approach fails. First, object storage systems like S3 exhibit high per-request latency (10-100ms); when multiplied across 14 million independent image reads, this cumulative latency becomes the primary bottleneck. Second, S3 is optimized for high throughput on large files, not high IOPS for tiny 10KB files, meaning the HTTP/TLS protocol overhead for each GET request often exceeds the time taken to transfer the actual image data. Finally, object stores lack sequential prefetching logic, so they cannot anticipate and stream the next files the way a local filesystem or advanced caching layer would. To solve this, the team should either pack the files into sequential archives (like WebDataset) or introduce a caching layer like JuiceFS with a local NVMe tier.
</details>

### Question 2
*Scenario*: Your infrastructure team needs to improve data loading times for a 5TB training dataset. Engineer A proposes installing JuiceFS, while Engineer B argues for deploying Alluxio with Fluid. In what architectural scenarios would you choose JuiceFS over Alluxio, and why?

<details>
<summary>Show Answer</summary>

JuiceFS and Alluxio take fundamentally different architectural approaches to solving the data caching problem. JuiceFS is designed as a complete POSIX-compliant distributed filesystem that happens to use object storage as its data backend and Redis/SQL for metadata, making it an excellent drop-in replacement when you need simple, robust filesystem semantics with transparent local NVMe caching. Alluxio, on the other hand, acts as a pure caching middleware layer that sits between your compute and existing storage systems (like HDFS or S3), without storing the canonical data itself. You would choose JuiceFS for its operational simplicity and seamless POSIX integration. Conversely, you would choose Alluxio (especially paired with Fluid) when you require advanced dataset-aware scheduling, multi-tier caching (RAM+SSD), or need to unify multiple disparate storage backends under a single namespace.
</details>

### Question 3
*Scenario*: You are observing a massive 70B parameter LLM training job. Every 1000 steps (which take about 2 seconds each), the job halts for 350 seconds to save a 700GB checkpoint to a standard NFS share. The ML team is complaining about lost compute time. Quantify the GPU time wasted by this synchronous operation and propose a multi-faceted solution to minimize it.

<details>
<summary>Show Answer</summary>

Currently, the training job spends 2000 seconds on compute and 350 seconds blocked on I/O, meaning nearly 15% of your expensive GPU time is entirely wasted waiting for storage. This synchronous checkpointing creates a severe bottleneck because all compute must halt while the single node writes out the monolithic 700GB state to a slow NFS target. To drastically reduce this waste, you should first implement sharded distributed checkpoints, allowing each GPU to write only its own portion of the model state in parallel. Second, transition to asynchronous checkpointing, where the state is quickly copied to host CPU RAM (taking only seconds) and then written to disk in a background thread. Finally, upgrading the storage target from slow NFS to a high-throughput local NVMe cache or parallel filesystem (like CephFS) ensures those background writes complete rapidly without saturating the network.
</details>

### Question 4
*Scenario*: Your cluster runs multiple ML training pods that access a shared 10TB dataset. When you use standard PersistentVolumeClaims (PVCs) backed by a network filesystem, the pods are scheduled randomly across your 50 nodes, and each node constantly fetches data from the remote storage. If you implement Fluid, how does its data-aware scheduling fundamentally change this behavior?

<details>
<summary>Show Answer</summary>

Standard Kubernetes scheduling with regular PVCs has no awareness of data locality, meaning a pod will be scheduled on any node that meets its CPU/GPU requirements, completely ignoring whether that node has the required data cached locally. This leads to severe "cold cache" penalties as each new node must pull data from remote storage. Fluid fundamentally changes this by orchestrating the datasets as first-class citizens and actively tracking which nodes have cached portions of the data via engines like Alluxio. Fluid then automatically injects scheduling hints (like node affinities) into your training pods, ensuring the Kubernetes scheduler preferentially places them on nodes where the data is already warm. This data-aware placement drastically reduces network I/O, lowers object storage egress costs, and accelerates training startup times.
</details>

---

## Hands-On Exercise: JuiceFS Cache Over S3 with Latency Measurement

### Objective

Deploy JuiceFS with a local NVMe cache backed by S3-compatible object storage, load a dataset, and measure the difference between cold-cache and warm-cache read performance.

### Environment

- Kubernetes cluster with at least one node
- MinIO or any S3-compatible storage (we will deploy MinIO for this exercise)
- A node with local storage available (emptyDir is acceptable for the exercise)

### Step 1: Deploy MinIO (S3-compatible Object Store)

```bash
# Install MinIO for local S3-compatible storage
kubectl create namespace storage

cat <<'EOF' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: minio
  namespace: storage
spec:
  replicas: 1
  selector:
    matchLabels:
      app: minio
  template:
    metadata:
      labels:
        app: minio
    spec:
      containers:
        - name: minio
          image: minio/minio:RELEASE.2024-10-13T13-34-11Z
          args: ["server", "/data", "--console-address", ":9001"]
          env:
            - name: MINIO_ROOT_USER
              value: minioadmin
            - name: MINIO_ROOT_PASSWORD
              value: minioadmin123
          ports:
            - containerPort: 9000
            - containerPort: 9001
          volumeMounts:
            - name: data
              mountPath: /data
      volumes:
        - name: data
          emptyDir:
            sizeLimit: 20Gi
---
apiVersion: v1
kind: Service
metadata:
  name: minio
  namespace: storage
spec:
  ports:
    - port: 9000
      targetPort: 9000
      name: api
    - port: 9001
      targetPort: 9001
      name: console
  selector:
    app: minio
EOF

kubectl -n storage wait --for=condition=Ready pod -l app=minio --timeout=120s
```

### Step 2: Create a Test Dataset in MinIO

```bash
# Create a bucket and upload test data
kubectl -n storage run mc --rm -it --restart=Never \
  --image=minio/mc:RELEASE.2024-10-08T09-37-26Z -- bash -c '
  mc alias set local http://minio:9000 minioadmin minioadmin123
  mc mb local/ai-datasets

  # Create a 1GB test dataset (256 files of 4MB each)
  for i in $(seq 1 256); do
    dd if=/dev/urandom of=/tmp/data_${i}.bin bs=4M count=1 2>/dev/null
    mc cp /tmp/data_${i}.bin local/ai-datasets/training/
    rm /tmp/data_${i}.bin
  done

  echo "Dataset created:"
  mc ls local/ai-datasets/training/ | wc -l
  mc du local/ai-datasets/
'
```

### Step 3: Deploy Redis (JuiceFS Metadata Engine)

```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: storage
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          ports:
            - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: storage
spec:
  ports:
    - port: 6379
  selector:
    app: redis
EOF
```

### Step 4: Install JuiceFS CSI Driver

```bash
helm repo add juicefs https://juicedata.github.io/charts/
helm repo update

# Create the JuiceFS secret
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: juicefs-secret
  namespace: storage
type: Opaque
stringData:
  name: ai-data
  metaurl: redis://redis.storage.svc:6379/1
  storage: s3
  bucket: http://minio.storage.svc:9000/ai-datasets
  access-key: minioadmin
  secret-key: minioadmin123
EOF

# Install the CSI driver
helm install juicefs-csi juicefs/juicefs-csi-driver \
  --namespace kube-system \
  --version v0.24.8
```

### Step 5: Create JuiceFS StorageClass and PVC

```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: juicefs-cache
provisioner: csi.juicefs.com
parameters:
  csi.storage.k8s.io/provisioner-secret-name: juicefs-secret
  csi.storage.k8s.io/provisioner-secret-namespace: storage
  csi.storage.k8s.io/node-publish-secret-name: juicefs-secret
  csi.storage.k8s.io/node-publish-secret-namespace: storage
  juicefs/mount-options: "cache-size=10240,buffer-size=512"
reclaimPolicy: Delete
volumeBindingMode: Immediate
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: juicefs-data
  namespace: storage
spec:
  storageClassName: juicefs-cache
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 20Gi
EOF
```

### Step 6: Measure Cold vs Warm Cache Performance

```bash
cat <<'BENCHEOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: cache-benchmark
  namespace: storage
spec:
  containers:
    - name: bench
      image: ubuntu:22.04
      command: ["bash", "-c"]
      args:
        - |
          apt-get update -qq && apt-get install -y -qq time bc 2>/dev/null

          echo "=== COLD CACHE READ (first access, data fetched from S3) ==="
          sync; echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true

          cold_start=$(date +%s%N)
          total_bytes=0
          for f in /data/training/data_*.bin; do
            cat "$f" > /dev/null 2>&1
            total_bytes=$((total_bytes + $(stat -c%s "$f" 2>/dev/null || echo 0)))
          done
          cold_end=$(date +%s%N)

          cold_ms=$(( (cold_end - cold_start) / 1000000 ))
          cold_mbps=$(echo "scale=2; $total_bytes / 1048576 / ($cold_ms / 1000)" | bc 2>/dev/null || echo "N/A")
          echo "Cold read: ${cold_ms}ms for $(echo "$total_bytes / 1048576" | bc)MB = ${cold_mbps} MB/s"
          echo ""

          echo "=== WARM CACHE READ (second access, data from local cache) ==="
          warm_start=$(date +%s%N)
          for f in /data/training/data_*.bin; do
            cat "$f" > /dev/null 2>&1
          done
          warm_end=$(date +%s%N)

          warm_ms=$(( (warm_end - warm_start) / 1000000 ))
          warm_mbps=$(echo "scale=2; $total_bytes / 1048576 / ($warm_ms / 1000)" | bc 2>/dev/null || echo "N/A")
          echo "Warm read: ${warm_ms}ms for $(echo "$total_bytes / 1048576" | bc)MB = ${warm_mbps} MB/s"
          echo ""

          speedup=$(echo "scale=1; $cold_ms / $warm_ms" | bc 2>/dev/null || echo "N/A")
          echo "=== RESULT: Warm cache is ${speedup}x faster than cold ==="

          sleep 3600
      volumeMounts:
        - name: data
          mountPath: /data
      resources:
        requests:
          cpu: "2"
          memory: 4Gi
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: juicefs-data
  restartPolicy: Never
BENCHEOF

# Wait and check results
kubectl -n storage wait --for=condition=Ready pod/cache-benchmark --timeout=300s
sleep 60
kubectl -n storage logs cache-benchmark
```

### Step 7: Cleanup

```bash
kubectl delete namespace storage
```

### Success Criteria

You have completed this exercise when:
- [ ] MinIO is running and contains a 1GB test dataset (256 files)
- [ ] Redis metadata engine is running
- [ ] JuiceFS CSI driver is installed and StorageClass is created
- [ ] PVC is bound and mountable
- [ ] Cold cache read time is measured (expect: 30-120 seconds for 1GB)
- [ ] Warm cache read time is measured (expect: 2-10 seconds for 1GB)
- [ ] Warm cache read is at least 3x faster than cold cache read
- [ ] You can explain why the speedup occurs (local NVMe/memory vs S3 network round-trip)

---

## Key Takeaways

1. **IO is the most common bottleneck in GPU training** — if GPU utilization is below 80%, investigate storage first
2. **Local NVMe is 10-50x faster than network storage** for the random small-file reads that image training demands
3. **JuiceFS bridges the gap** between object storage (cheap, durable, slow) and local NVMe (fast, ephemeral)
4. **Fluid/Alluxio add data-aware scheduling** — Pods prefer nodes that already have their dataset cached
5. **Checkpointing must be fast** — synchronous saves to slow storage can waste 15%+ of GPU time; use sharded async checkpoints
6. **Mount with `noatime`** — a one-line fix that eliminates unnecessary metadata writes on every file read
7. **Measure before optimizing** — use `fio` to benchmark your storage and `nvidia-smi` to correlate with GPU utilization
8. **The init container pattern** for data staging is simple, reliable, and often sufficient for datasets under 1TB

---

## Further Reading

**Documentation**:
- **JuiceFS**: juicefs.com/docs/
- **Fluid**: github.com/fluid-cloudnative/fluid
- **Alluxio**: docs.alluxio.io
- **TopoLVM**: github.com/topolvm/topolvm
- **Rook-Ceph**: rook.io/docs/rook/latest/

**Papers**:
- **"Analyzing and Mitigating Data Stalls in DNN Training"** — Jayaram et al. (IO bottleneck analysis)
- **"CoorDL: Coordinated and Progressive Data Loading for Deep Learning"** — Mohan et al.

**Talks**:
- **"Building a Petabyte-Scale AI Data Platform on Kubernetes"** — KubeCon EU 2024
- **"JuiceFS: A Cloud-Native Distributed File System for AI Workloads"** — CNCF Webinar

---

## Summary

Storage is the hidden bottleneck that prevents expensive GPUs from reaching their potential. A multi-tier approach — local NVMe for hot data, distributed filesystem for warm data, object storage for cold data — combined with intelligent caching (JuiceFS, Fluid/Alluxio) bridges the 1,000x performance gap between GPU memory and network storage. Fast checkpoint storage with async and sharded writes minimizes GPU idle time during saves. Measure, cache, and measure again.

---

## Next Module

Continue to [Module 1.5: Serving LLMs at Scale](../module-1.5-llm-serving/) to learn how to deploy large language models for inference with vLLM, continuous batching, and KEDA autoscaling.

---

*"Data is the new oil, but storage is the pipeline. A clogged pipeline makes the oil worthless."* — Anonymous infrastructure engineer