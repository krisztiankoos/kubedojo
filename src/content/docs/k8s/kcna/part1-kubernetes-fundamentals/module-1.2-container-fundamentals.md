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

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Explain** what containers are and how they differ from virtual machines
2. **Identify** the Linux kernel features (namespaces, cgroups) that enable container isolation
3. **Compare** container runtimes (Docker, containerd, CRI-O) and their roles in Kubernetes
4. **Explain** the OCI image and runtime specifications and why they matter for portability

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

> **Pause and predict**: If containers share the host kernel (unlike VMs which have their own), what security implications does this have? What happens if a container exploits a kernel vulnerability?

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

> **Stop and think**: Docker was deprecated as a Kubernetes runtime in version 1.24. If Docker is the most popular container tool, why would Kubernetes drop support for it? What does Kubernetes actually need from a runtime?

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

1. **A developer says "containers are just lightweight VMs." How would you correct this misconception, and why does the distinction matter?**
   <details>
   <summary>Answer</summary>
   Containers and VMs have fundamentally different architectures. VMs include a full guest operating system and run on a hypervisor, providing strong isolation at the cost of heavy resource usage. Containers share the host kernel and use Linux namespaces and cgroups for isolation -- they are isolated processes, not virtual machines. This distinction matters because sharing the kernel means containers start in seconds (not minutes), use megabytes (not gigabytes), and you can run hundreds per host (not just tens). However, it also means containers have weaker isolation than VMs since a kernel vulnerability could affect all containers on the host.
   </details>

2. **Your team builds a container image on a developer's laptop using Docker. Can that same image run in a Kubernetes cluster that uses containerd instead of Docker? Why or why not?**
   <details>
   <summary>Answer</summary>
   Yes, the image will work. Container images follow the OCI (Open Container Initiative) standard, which defines a common image format. Docker, containerd, and CRI-O all understand OCI images. The image you build with Docker produces an OCI-compliant image that any compliant runtime can execute. This portability is one of the key benefits of container standardization -- you build once and run on any OCI-compatible runtime.
   </details>

3. **A container image has four layers: base OS, runtime, dependencies, and application code. If you update only your application code, what happens to the other three layers when you rebuild?**
   <details>
   <summary>Answer</summary>
   The other three layers are reused from cache. Container images use a union filesystem where each layer builds on the previous one. Only layers that change (and layers above them) need rebuilding. Since your application code is the top layer, the base OS, runtime, and dependency layers remain cached. This is why layer ordering matters in Dockerfiles -- put frequently-changing content in later layers. It also means that multiple containers sharing the same base layers on a node only store those layers once, saving disk space.
   </details>

4. **You learn that Kubernetes deprecated Docker as a runtime in version 1.24. A worried colleague asks if all their Docker-built images will stop working. What would you explain?**
   <details>
   <summary>Answer</summary>
   Their images will continue working perfectly. Kubernetes deprecated Docker as a container runtime (the component that runs containers), not Docker images. Docker images are OCI-standard images that containerd (the new default runtime) fully supports. What was removed was the "dockershim" -- a compatibility layer that let Kubernetes talk to Docker's API. Since containerd was always the component inside Docker that actually ran containers, removing Docker just removes an unnecessary middle layer. Images built with `docker build` work identically on containerd.
   </details>

5. **An organization needs strong security isolation between workloads from different customers on the same host. Would containers alone provide sufficient isolation? What alternative approach might they consider?**
   <details>
   <summary>Answer</summary>
   Containers alone may not provide sufficient isolation for multi-tenant workloads with strict security requirements. Since containers share the host kernel, a kernel vulnerability could allow one tenant's container to access another's data. For stronger isolation, the organization could consider: running containers inside lightweight VMs (like Kata Containers or Firecracker), using gVisor which interposes a user-space kernel between containers and the host, or using separate nodes per tenant. The choice depends on the security requirements versus the performance and cost trade-offs.
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

[Module 1.3: Kubernetes Architecture - Control Plane](../module-1.3-control-plane/) - Understanding the brain of Kubernetes.
