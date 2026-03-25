---
title: "Module 1.2: Container Fundamentals"
slug: k8s/kcna/part1-kubernetes-fundamentals/module-1.2-container-fundamentals
sidebar:
  order: 3
---
> **Complexity**: `[QUICK]` - Foundational concepts
>
> **Time to Complete**: 20-25 minutes
>
> **Prerequisites**: Module 1.1

---

## Why This Module Matters

You can't understand Kubernetes without understanding containers. KCNA tests your knowledge of container concepts—not how to build Dockerfiles, but what containers are and how they work.

---

## What is a Container?

A container is a **lightweight, standalone, executable package** that includes everything needed to run a piece of software:

```
┌─────────────────────────────────────────────────────────────┐
│              WHAT'S INSIDE A CONTAINER                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    CONTAINER                         │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  Application Code                            │    │   │
│  │  │  (your app, scripts, binaries)              │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  Dependencies                                │    │   │
│  │  │  (libraries, packages, frameworks)          │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  Runtime                                     │    │   │
│  │  │  (Python, Node.js, Java JVM, etc.)          │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  System Tools & Libraries                    │    │   │
│  │  │  (minimal OS userspace)                     │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  NOT included: Kernel (shared with host)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Containers vs Virtual Machines

```
┌─────────────────────────────────────────────────────────────┐
│         VIRTUAL MACHINES vs CONTAINERS                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  VIRTUAL MACHINES                    CONTAINERS             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ┌─────┐ ┌─────┐ ┌─────┐          ┌─────┐ ┌─────┐ ┌─────┐ │
│  │App A│ │App B│ │App C│          │App A│ │App B│ │App C│ │
│  ├─────┤ ├─────┤ ├─────┤          ├─────┤ ├─────┤ ├─────┤ │
│  │Bins │ │Bins │ │Bins │          │Bins │ │Bins │ │Bins │ │
│  │Libs │ │Libs │ │Libs │          │Libs │ │Libs │ │Libs │ │
│  ├─────┤ ├─────┤ ├─────┤          └──┬──┘ └──┬──┘ └──┬──┘ │
│  │Guest│ │Guest│ │Guest│             │       │       │     │
│  │ OS  │ │ OS  │ │ OS  │             │       │       │     │
│  └──┬──┘ └──┬──┘ └──┬──┘             └───────┼───────┘     │
│     └───────┼───────┘                        │             │
│             │                        ┌───────┴───────┐     │
│     ┌───────┴───────┐                │Container      │     │
│     │  Hypervisor   │                │Runtime        │     │
│     └───────┬───────┘                └───────┬───────┘     │
│             │                                │             │
│     ┌───────┴───────┐                ┌───────┴───────┐     │
│     │   Host OS     │                │   Host OS     │     │
│     └───────┬───────┘                └───────┬───────┘     │
│             │                                │             │
│     ┌───────┴───────┐                ┌───────┴───────┐     │
│     │   Hardware    │                │   Hardware    │     │
│     └───────────────┘                └───────────────┘     │
│                                                             │
│  Each VM has full OS                 Containers share      │
│  (heavy, slow to start)             host kernel (light)    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Comparison Table

| Aspect | Virtual Machine | Container |
|--------|-----------------|-----------|
| **Size** | GBs | MBs |
| **Startup** | Minutes | Seconds |
| **Isolation** | Strong (separate kernel) | Process-level (shared kernel) |
| **Overhead** | High | Low |
| **Density** | ~10s per host | ~100s per host |
| **Portability** | Medium | High |

---

## How Containers Work

Containers use Linux kernel features:

### 1. Namespaces (Isolation)

```
┌─────────────────────────────────────────────────────────────┐
│              LINUX NAMESPACES                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Namespace     What It Isolates                            │
│  ─────────────────────────────────────────────────────────  │
│  PID           Process IDs (container sees own PIDs)       │
│  Network       Network interfaces, IPs, ports              │
│  Mount         Filesystem mounts                           │
│  UTS           Hostname and domain name                    │
│  IPC           Inter-process communication                 │
│  User          User and group IDs                          │
│                                                             │
│  Each container gets its own namespaces                    │
│  → Appears to have its own isolated system                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. Cgroups (Resource Limits)

```
┌─────────────────────────────────────────────────────────────┐
│              CONTROL GROUPS (cgroups)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Cgroups limit and track resources:                        │
│                                                             │
│  CPU:      "Container A gets max 2 cores"                  │
│  Memory:   "Container B gets max 512MB"                    │
│  Disk I/O: "Container C gets max 100MB/s"                  │
│  Network:  "Container D gets max 100Mbps"                  │
│                                                             │
│  Without cgroups:                                          │
│  One container could consume ALL resources                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. Union Filesystems (Layers)

```
┌─────────────────────────────────────────────────────────────┐
│              CONTAINER IMAGE LAYERS                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Container Image (read-only layers):                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Layer 4: Application code       (your app)         │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  Layer 3: Dependencies           (npm packages)     │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  Layer 2: Runtime                (Node.js)          │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  Layer 1: Base OS                (Ubuntu slim)      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Running Container adds:                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Writable layer  (runtime changes, logs, temp files)│   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Benefits:                                                 │
│  • Layers are cached and reused                           │
│  • Multiple containers share base layers                  │
│  • Efficient storage and transfer                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Container Images

### What is an Image?

An **image** is a read-only template used to create containers:

| Concept | Analogy |
|---------|---------|
| Image | Recipe / Blueprint |
| Container | Cake / Building |

### Image Naming Convention

```
registry/repository:tag

Examples:
docker.io/library/nginx:1.25
gcr.io/google-containers/pause:3.9
mycompany.com/myapp:v2.1.0

Parts:
• registry:    Where image is stored (docker.io, gcr.io)
• repository:  Name of the image (nginx, myapp)
• tag:         Version identifier (1.25, latest, v2.1.0)
```

### Image Registries

| Registry | Description |
|----------|-------------|
| Docker Hub | Default public registry |
| gcr.io | Google Container Registry |
| ECR | Amazon Elastic Container Registry |
| ACR | Azure Container Registry |
| Quay.io | Red Hat registry |

---

## Container Runtimes

Kubernetes doesn't run containers directly—it uses a **container runtime**:

```
┌─────────────────────────────────────────────────────────────┐
│              CONTAINER RUNTIME INTERFACE (CRI)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    Kubernetes                               │
│                         │                                   │
│                         │ CRI (standard interface)          │
│                         │                                   │
│         ┌───────────────┼───────────────┐                  │
│         │               │               │                   │
│         ▼               ▼               ▼                   │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐              │
│   │containerd│   │  CRI-O   │   │  Docker  │              │
│   │          │   │          │   │(via shim)│              │
│   └──────────┘   └──────────┘   └──────────┘              │
│                                                             │
│  containerd: Default in most K8s distributions            │
│  CRI-O:      Lightweight, Kubernetes-focused              │
│  Docker:     Deprecated in K8s 1.24+                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Key point for KCNA**: Kubernetes uses CRI to talk to container runtimes. The most common runtime is containerd.

---

## Container Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│              CONTAINER LIFECYCLE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Pull Image                                             │
│     Download image from registry                           │
│                    │                                        │
│                    ▼                                        │
│  2. Create Container                                       │
│     Prepare filesystem, namespaces, cgroups               │
│                    │                                        │
│                    ▼                                        │
│  3. Start Container                                        │
│     Execute the container's entry point                   │
│                    │                                        │
│                    ▼                                        │
│  4. Running                                                │
│     Container is executing                                 │
│                    │                                        │
│         ┌─────────┴─────────┐                              │
│         │                   │                               │
│         ▼                   ▼                               │
│  5a. Stop              5b. Crash                          │
│      Graceful              Unexpected                      │
│      shutdown              termination                     │
│         │                   │                               │
│         └─────────┬─────────┘                              │
│                   │                                         │
│                   ▼                                         │
│  6. Remove Container                                       │
│     Clean up resources                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Did You Know?

- **Containers aren't new** - The concepts date back to Unix chroot (1979) and FreeBSD jails (2000). Docker popularized them in 2013.

- **Docker isn't required for Kubernetes** - Since K8s 1.24, containerd is the default. Docker as a runtime is deprecated.

- **The OCI defines standards** - Open Container Initiative standardizes image formats and runtimes, ensuring portability.

- **Containers share the host kernel** - This is why Windows containers can't run on Linux and vice versa (without virtualization).

---

## Common Mistakes

| Mistake | Why It Hurts | Correct Understanding |
|---------|--------------|----------------------|
| "Containers are lightweight VMs" | Missing the architectural difference | Containers share kernel; VMs don't |
| "Each container has its own OS" | Wastes resources mentally | Containers share host kernel |
| "Docker = Containers" | Docker is just one runtime | containerd, CRI-O also run containers |
| "Images and containers are the same" | Confuses template vs instance | Image is template; container is running instance |

---

## Quiz

1. **What Linux feature provides process isolation for containers?**
   <details>
   <summary>Answer</summary>
   Namespaces. They isolate PIDs, network, mounts, hostname, IPC, and users for each container.
   </details>

2. **What Linux feature limits container resource usage?**
   <details>
   <summary>Answer</summary>
   Control groups (cgroups). They limit CPU, memory, disk I/O, and network bandwidth.
   </details>

3. **What's the relationship between an image and a container?**
   <details>
   <summary>Answer</summary>
   An image is a read-only template (like a recipe). A container is a running instance created from that image (like a cake from a recipe).
   </details>

4. **What is the default container runtime in modern Kubernetes?**
   <details>
   <summary>Answer</summary>
   containerd. Docker as a runtime was deprecated in Kubernetes 1.24.
   </details>

5. **Why are containers more efficient than VMs?**
   <details>
   <summary>Answer</summary>
   Containers share the host kernel instead of running a full OS. This makes them smaller (MBs vs GBs), faster to start (seconds vs minutes), and allows higher density (100s vs 10s per host).
   </details>

---

## Summary

**Containers are**:
- Lightweight, isolated processes
- Packaged with dependencies
- Created from images
- Share the host kernel

**Key technologies**:
- **Namespaces**: Process isolation
- **Cgroups**: Resource limits
- **Union filesystems**: Layered images

**Container runtimes**:
- containerd (default)
- CRI-O
- Docker (deprecated in K8s)

**Images vs Containers**:
- Image = read-only template
- Container = running instance

---

## Next Module

[Module 1.3: Kubernetes Architecture - Control Plane](module-1.3-control-plane/) - Understanding the brain of Kubernetes.
