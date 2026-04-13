---
title: "Module 1.1: Container Images"
slug: k8s/ckad/part1-design-build/module-1.1-container-images
sidebar:
  order: 1
lab:
  id: ckad-1.1-container-images
  url: https://killercoda.com/kubedojo/scenario/ckad-1.1-container-images
  duration: "30 min"
  difficulty: intermediate
  environment: kubernetes
---

> **Complexity**: `[MEDIUM]` - Requires understanding of Dockerfile and image registries
>
> **Time to Complete**: 60-75 minutes
>
> **Prerequisites**: Module 0.2 (Developer Workflow), basic container knowledge

## Learning Outcomes

After completing this deeply technical module, you will be well-equipped to:
- **Diagnose and evaluate** complex image pull errors, including `ImagePullBackOff` and hidden authentication failures across distributed Kubernetes nodes.
- **Design** highly robust and predictable container deployment strategies by utilizing explicit image pull policies and correctly binding registry credentials.
- **Analyze and optimize** a Dockerfile that rigidly follows enterprise best practices for payload size, security surface area, and aggressive layer caching.
- **Compare** the nuanced structural differences between Docker's `ENTRYPOINT` and `CMD` instructions, and **implement** their overrides within Kubernetes Pod specifications.
- **Explain** the intricacies of the Open Container Initiative (OCI) image specification standard and the fundamental architecture of layered union filesystems.

## Why This Module Matters

In 2020, a widespread incident brought countless CI/CD pipelines and production Kubernetes clusters to a grinding halt. Docker Hub began enforcing strict rate limits on their public registries. Companies that had improperly configured their Kubernetes nodes to constantly pull common base images without a local caching strategy found themselves facing cascading `ImagePullBackOff` errors. Production scaling failed, disaster recovery processes stalled indefinitely, and millions of dollars were lost in engineering time and delayed deployments.

Understanding the mechanics of container images is not merely an academic exercise; it is the absolute foundation of platform stability. Kubernetes does not execute source code directly; it orchestrates container images. Every application—whether a massive monolithic system or a lightweight microservice daemon—must be completely encapsulated into a standardized artifact format before it can be deployed to a cluster. The Certified Kubernetes Application Developer (CKAD) exam rigorously expects you to demonstrate a masterful understanding of how these images are structured, referenced, cryptographically authenticated, and safely executed within a tightly controlled pod environment.

> Before the widespread adoption of containerization, deploying software felt like loading individual, irregularly shaped boxes onto a massive cargo ship. Every host operating system handled system dependencies differently, and applications frequently broke when migrating from a local developer's laptop to a staging or production server. The container image functions exactly like the standardized physical shipping container. It possesses universal dimensions and interfaces, ensuring that the enclosed software payload runs identically whether it is deployed on a legacy on-premise hypervisor or a modern managed Kubernetes service in the public cloud.

## The Architecture of Container Images & OCI Standards

To truly master Kubernetes, an engineer must look beyond the generic concept of a "Docker image" and understand the strict, vendor-neutral specifications that govern the container ecosystem. Container images are heavily standardized by the Open Container Initiative (OCI). Understanding this ecosystem ensures you are fully prepared for modern platform engineering, deep interoperability, and stringent security compliance requirements.

### The OCI Image Specification

The latest stable version of the OCI Image Specification is version 1.1.1. This provides the critical foundation for all modern container runtimes. The preceding release was highly significant, as OCI image-spec version 1.1.0 was the first minor release of the OCI Image Specification since version 1.0.0 in July 2017. 

When building, pushing, or inspecting an image, you will invariably encounter the underlying image manifest. The OCI image manifest `schemaVersion` must be set to 2 for backward compatibility with Docker. If you are dealing with a traditional standalone build, the OCI image manifest media type for a single-architecture image is `application/vnd.oci.image.manifest.v1+json`.

However, we operate in a globally distributed, multi-architecture world where ARM64 and AMD64 hardware nodes frequently coexist within the same Kubernetes cluster. To handle this natively, the OCI Image Index (media type `application/vnd.oci.image.index.v1+json`) is the OCI standard for multi-platform 'fat manifests'. When a node's kubelet instructs the runtime daemon to pull an image, the runtime fetches this central index, automatically evaluates the host hardware, and selects the precise nested manifest that matches the host node's architecture.

### Storage Layers and Media Types

Under the hood, container images consist of read-only layers stacked via a union filesystem; a running container adds a thin writable layer using copy-on-write functionality. This design is highly efficient. For example, if fifty distinct containers on the same Kubernetes node utilize the exact same foundational application image, the physical node does not duplicate the underlying filesystem fifty distinct times. Instead, the runtime maps the read-only foundational layers into memory once. When an individual container process writes a temporary file or mutates a system parameter, the storage driver dynamically copies the specific file from the lower read-only layer into the upper writable layer assigned exclusively to that running container. Once the container terminates, this ephemeral upper layer is permanently discarded.

When transferring these discrete layers over the network, they are represented by specific compression media types. OCI image layer media types include `application/vnd.oci.image.layer.v1.tar`, `application/vnd.oci.image.layer.v1.tar+gzip`, and `application/vnd.oci.image.layer.v1.tar+zstd`. The addition of the zstd variant enables significantly better compression efficiency compared to legacy formats, severely cutting down on deployment bandwidth.

Historically, some organizations attempted to use non-distributable layers to restrict the movement of proprietary or licensed software. However, non-distributable layer media types (`application/vnd.oci.image.layer.nondistributable.v1.tar` variants) are deprecated in the OCI Image Specification. They were deprecated because they introduced critical friction across restricted network boundaries and heavily fragmented the ecosystem. Registry operators and CI pipelines struggled to manage layers that could not be reliably synced or externally replicated.

### Distribution and Runtime Specifications

To comprehensively govern how centralized registries manage and distribute these artifacts, the latest stable version of the OCI Distribution Specification is version 1.1.1. A groundbreaking addition to this standard is the mechanism for supply-chain artifact discovery. The OCI Distribution Specification version 1.1 defines a Referrers API at `GET /v2/<name>/referrers/<digest>` for supply-chain artifact discovery. This allows external systems to natively associate Software Bills of Materials (SBOMs), vulnerability scans, and digital signatures with an image without ever mutating the target image's original cryptographic digest.

At the lowest conceptual level of the compute stack, once an image is downloaded and successfully unpacked onto the disk, the container payload must be isolated and executed. The latest stable version of the OCI Runtime Specification is version 1.3.0. This critical specification dictates exactly how the container runtime interfaces directly with the host Linux kernel to construct the execution sandbox, instantiating the necessary Linux namespaces and control groups (cgroups) to enforce strict resource quotas.

## The Modern Container Build Ecosystem

Modern container tooling is far broader than a single daemon running on a developer machine. Over the years, the ecosystem has heavily diversified to support massively concurrent builds, advanced distributed caching, and tighter security integrations.

### Docker Engine and containerd Architecture

The latest stable version of Docker Engine is version 29.4.0. While Docker remains a dominant tool for local developer workflows, its internal architectural topology has evolved considerably. Docker Engine 29.0+ defaults to the containerd image store on fresh installations; systems upgraded from earlier versions continue using overlay2. 

When Kubernetes directly interacts with the Container Runtime Interface (CRI) on a worker node, `containerd` is predominantly the underlying technology serving the pods. The latest stable version of containerd is version 2.2.2. For environments operating on legacy infrastructure, `overlay2` (OverlayFS) is the default storage driver for Docker Engine on Linux on pre-29.0 or upgraded installations.

### Modern Builders: BuildKit, Buildx, and Alternatives

To assemble images quickly and securely, BuildKit became the default builder for Docker Engine on Linux in version 23.0 (released February 1, 2023). It brought massive performance improvements through highly concurrent, parallel execution of independent build stages and sophisticated intermediate artifact handling. The latest stable version of BuildKit is version 0.29.0, and the latest stable version of `docker/buildx` (the CLI plugin interfacing with the daemon) is version 0.33.0. BuildKit has also forcefully hardened its supply chain security posture; the default provenance format in BuildKit switched from SLSA v0.2 to SLSA v1.0, generating robust attestations for every build to mitigate sophisticated tampering attacks.

Other highly capable tools exist for building and running containers, especially in rootless or restrictive CI/CD environments. For instance, the latest stable version of Podman is version 5.8.1, offering a fully daemonless container execution environment. Similarly, the latest stable version of Buildah is version 1.43.0, specializing exclusively in constructing OCI-compliant image payloads directly from bash scripts or standard Dockerfiles.

Engineering teams must also remain aware of deprecated tooling to prevent technical debt. The `GoogleContainerTools/kaniko` repository was archived on June 3, 2025 and is no longer maintained. Many organizations have migrated to BuildKit or alternative managed build services to ensure ongoing support.

## Image Naming Convention

Understanding exact image nomenclature is critical. Every Kubernetes Pod specification utilizes a string reference to instruct the node's container runtime exactly where and how to pull the correct container payload. 

```text
[registry/][namespace/]image[:tag][@digest]
```

This structure is deliberate and acts as a fully qualified address for your software.

| Component | Required | Example | Default |
|-----------|----------|---------|---------|
| Registry | No | `docker.io`, `gcr.io`, `quay.io` | `docker.io` |
| Namespace | No | `library`, `mycompany` | `library` |
| Image | Yes | `nginx`, `myapp` | - |
| Tag | No | `latest`, `1.19.0`, `alpine` | `latest` |
| Digest | No | `sha256:abc123...` | - |

Let's examine how these references translate into real-world configurations within a cluster environment.

```yaml
# Full specification
image: docker.io/library/nginx:1.21.0

# Equivalent short form (docker.io/library implied)
image: nginx:1.21.0

# Different registry
image: gcr.io/google-containers/nginx:1.21.0

# Custom namespace
image: myregistry.com/myteam/myapp:v2.0.0

# With digest (immutable reference)
image: nginx@sha256:abc123def456...

# Latest tag (avoid in production)
image: nginx:latest
image: nginx  # same as above
```

### Why Tags Matter

Relying on default behaviors in high-stakes production environments is extremely dangerous.

```yaml
# BAD: latest can change unexpectedly
image: nginx:latest

# GOOD: specific version, reproducible
image: nginx:1.21.0

# BETTER: specific version with Alpine base (smaller)
image: nginx:1.21.0-alpine
```

You must explicitly define tags to prevent unexpected application variations during node rescheduling events.

## Dockerfile Basics

A Dockerfile defines precisely how an artifact is constructed from the ground up. To leverage the latest caching optimizations, the recommended Dockerfile frontend pin for the latest stable 1.x syntax is 'docker/dockerfile:1'. 

A well-optimized Dockerfile is structurally essential. Multi-stage builds in Dockerfiles were introduced in Docker Engine 17.05, allowing developers to dramatically reduce the final image size by systematically discarding heavy intermediate build tools. 

```dockerfile
# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first (layer caching)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port (documentation)
EXPOSE 8080

# Command to run
CMD ["python", "app.py"]
```

Every command maps directly to structural changes in the resulting payload:

| Instruction | Purpose | Example |
|-------------|---------|---------|
| `FROM` | Base image | `FROM nginx:alpine` |
| `WORKDIR` | Set working directory | `WORKDIR /app` |
| `COPY` | Copy files from build context | `COPY src/ /app/` |
| `RUN` | Execute command during build | `RUN apt-get update` |
| `ENV` | Set environment variable | `ENV PORT=8080` |
| `EXPOSE` | Document port (doesn't publish) | `EXPOSE 8080` |
| `CMD` | Default command to run | `CMD ["nginx", "-g", "daemon off;"]` |
| `ENTRYPOINT` | Main executable | `ENTRYPOINT ["python"]` |

> **Pause and predict**: In a Kubernetes Pod spec, `command` overrides one Dockerfile instruction and `args` overrides another. Which is which? Many developers get this backwards. Think about it before reading the mapping below.

### CMD vs ENTRYPOINT

The distinction between `CMD` and `ENTRYPOINT` heavily dictates how the container behaves when arbitrary arguments are passed via the runtime API.

```dockerfile
# CMD: Easily overridden
FROM nginx
CMD ["nginx", "-g", "daemon off;"]
# Can run: docker run myimage sleep 10 (replaces CMD)

# ENTRYPOINT: Hard to override
FROM python
ENTRYPOINT ["python"]
CMD ["app.py"]
# Runs: python app.py
# Can run: docker run myimage script.py (only replaces CMD)
```

In Kubernetes Pod specifications, the terminology shifts slightly:
- `ENTRYPOINT` strictly maps to `command:`
- `CMD` strictly maps to `args:`

```yaml
spec:
  containers:
  - name: app
    image: python:3.9
    command: ["python"]    # Overrides ENTRYPOINT
    args: ["myapp.py"]     # Overrides CMD
```

## Building Images

While you won't actively compile heavy container payloads from scratch during the CKAD exam, diagnosing runtime configuration errors demands an intimate understanding of the developer build cycle.

```bash
# Build in current directory
docker build -t myapp:v1.0.0 .

# Build with specific Dockerfile
docker build -t myapp:v1.0.0 -f Dockerfile.prod .

# Build with build arguments
docker build --build-arg VERSION=1.0.0 -t myapp:v1.0.0 .
```

Once cleanly built and verified locally, images must be relocated to a centralized registry for scalable cluster consumption.

```bash
# Tag an existing image
docker tag myapp:v1.0.0 myregistry.com/team/myapp:v1.0.0

# Push to registry
docker push myregistry.com/team/myapp:v1.0.0

# Push all tags
docker push myregistry.com/team/myapp --all-tags
```

## Image Pull Policy

Kubernetes is designed to be highly resilient but relies completely on explicit node instructions. It decides when to communicate over the network with a remote registry and when to utilize local storage based on the `imagePullPolicy`.

```yaml
spec:
  containers:
  - name: app
    image: nginx:1.21.0
    imagePullPolicy: Always  # IfNotPresent | Never | Always
```

| Policy | Behavior | Use When |
|--------|----------|----------|
| `Always` | Pull every time | Using `latest` tag, need freshest image |
| `IfNotPresent` | Pull only if not cached | Specific tags, save bandwidth |
| `Never` | Never pull, use cached | Local development, air-gapped |

> **Stop and think**: If you specify `image: nginx` (no tag) in a pod spec, what `imagePullPolicy` does Kubernetes use by default? What about `image: nginx:1.21.0`? The defaults are different -- why does that make sense?

### Default Behavior

Kubernetes dynamically alters its default pulling behavior based on the string provided in the image tag field. This fail-safe mechanism prevents massive bandwidth consumption while ensuring volatile tags remain forcibly updated.

| Image Tag | Default Policy |
|-----------|---------------|
| No tag (implies `:latest`) | `Always` |
| `:latest` | `Always` |
| Specific tag (`:v1.0.0`) | `IfNotPresent` |
| Digest (`@sha256:...`) | `IfNotPresent` |

## Private Registries

Rigorous enterprise environments lock down their container images. To securely pull from private, internally hosted repositories, your pods absolutely require valid authentication tokens logically mapped as Kubernetes Secrets.

### Step 1: Create a Secret

```bash
# Create docker-registry secret
k create secret docker-registry regcred \
  --docker-server=myregistry.com \
  --docker-username=user \
  --docker-password=password \
  --docker-email=user@example.com
```

### Step 2: Reference in Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: private-app
spec:
  containers:
  - name: app
    image: myregistry.com/team/myapp:v1.0.0
  imagePullSecrets:
  - name: regcred
```

### Alternative: ServiceAccount Default

To avoid manually appending secrets to every single pod definition, you can gracefully bind the secret directly to a ServiceAccount. Pods utilizing this ServiceAccount automatically inherit the associated credentials.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
imagePullSecrets:
- name: regcred
```
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: private-app
spec:
  serviceAccountName: myapp-sa
  containers:
  - name: app
    image: myregistry.com/team/myapp:v1.0.0
```

## Image Security Best Practices

### 1. Use Specific Tags

```yaml
# BAD
image: nginx:latest

# GOOD
image: nginx:1.21.0-alpine
```

### 2. Use Minimal Base Images

A large footprint mathematically equals a massive vulnerability attack surface. You must ruthlessly minimize the tools packaged inside the container.

```dockerfile
# 133MB
FROM python:3.9

# 45MB - much smaller
FROM python:3.9-slim

# 17MB - even smaller
FROM python:3.9-alpine
```

The official Alpine Linux Docker image is approximately 5 MB in size, delivering extreme density. The latest stable Alpine Linux release is 3.23.3. 

Alternatively, `FROM scratch` in a Dockerfile creates a container from an empty base image with no OS files, no shell, and no package manager. This approach is highly favored for compiled binaries.

Regarding intermediate ultra-minimalist ecosystems, there are conflicting reports regarding the maintenance of distroless images. While Chainguard independently built a second-generation distroless image ecosystem using the Wolfi package base, the original `GoogleContainerTools/distroless` repository remains a separate, still-active Google project. You should evaluate both ecosystems carefully to determine which meets your strict supply-chain constraints.

### 3. Run as Non-Root

```dockerfile
FROM python:3.9-slim
RUN useradd -m appuser
USER appuser
COPY --chown=appuser:appuser . /app
```

Enforce execution parameters systematically via Kubernetes SecurityContexts:

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
  containers:
  - name: app
    image: myapp:v1.0.0
```

### 4. Use Read-Only Filesystem

```yaml
spec:
  containers:
  - name: app
    image: myapp:v1.0.0
    securityContext:
      readOnlyRootFilesystem: true
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {}
```

Modern deployments also guarantee provenance via digital signatures. The latest stable version of Cosign is version 3.0.6. Cosign v3 stores container image signatures as OCI image-spec version 1.1 referring artifacts (using the subject field), integrating perfectly into the modern supply chain.

## Troubleshooting Image Issues

> **What would happen if**: A pod references a private registry image but has no `imagePullSecrets`. The image exists and is correctly tagged. What error would you see, and how would you distinguish it from a simple typo in the image name?

Diagnosing fetch failures is a mandatory skill for any operations engineer. An `ImagePullBackOff` state is merely a symptom; you must trace the underlying network or authentication cause.

| Error | Cause | Solution |
|-------|-------|----------|
| `ImagePullBackOff` | Can't pull image | Check image name, registry access |
| `ErrImagePull` | Pull failed | Verify image exists, check credentials |
| `InvalidImageName` | Malformed image reference | Fix image name format |
| `ImageInspectError` | Image inspection failed | Check image manifest |

### Debugging Steps

```bash
# Check pod events
k describe pod myapp | grep -A10 Events

# Check image name
k get pod myapp -o jsonpath='{.spec.containers[0].image}'

# Verify secret exists
k get secret regcred

# Test pull manually (if docker available)
docker pull myregistry.com/team/myapp:v1.0.0
```

### Example: Fixing ImagePullBackOff

```bash
# Pod stuck in ImagePullBackOff
k get pods
# NAME    READY   STATUS             RESTARTS   AGE
# myapp   0/1     ImagePullBackOff   0          5m

# Check events
k describe pod myapp
# Events:
#   Failed to pull image "nginx:latst": rpc error: ...not found

# Found it: typo in tag (latst instead of latest)

# Fix: Edit the pod or delete and recreate
k delete pod myapp
k run myapp --image=nginx:latest
```

## Did You Know?

- **Container images are strictly layered.** Each Dockerfile instruction generates a discrete, read-only layer. Since the foundational release of Docker Engine 1.0 in June 2014, these layers have been aggressively cached to dramatically reduce network consumption. This is why you should put frequently changing content (like `COPY . .`) at the end of your Dockerfile.
- **Unauthenticated Docker Hub rate limits cap pulls at 100 per 6 hours.** This invisible quota frequently cripples organizations that blindly autoscale their Kubernetes environments. Docker Personal (free) authenticated pulls are similarly restricted to 200 per 6-hour window, while paid enterprise plans remain strictly unlimited.
- **Image digests (`@sha256:...`) provide absolute cryptographic immutability.** A cryptographic digest perpetually guarantees exact binary content, neutralizing severe supply-chain tampering.
- **The `latest` tag possesses no intrinsic chronological meaning.** It is merely a default string pointer applied if omitted. The vast majority of container-related production outages are directly attributed to teams mistakenly overwriting `latest` with unverified code.

## Common Mistakes

| Mistake | Why It Hurts | Solution |
|---------|--------------|----------|
| Using `latest` in production | Unpredictable and volatile updates | Always pin specific image tags |
| Typos in image names | Results in immediate `ImagePullBackOff` | Double-check nomenclature and namespaces |
| Forgetting `imagePullSecrets` | Cluster lacks authorization to pull private images | Attach secret references explicitly in pod specs |
| Wrong `imagePullPolicy` | Degrades node performance via unnecessary cache misses | Explicitly dictate caching behavior per environment |
| Swollen base images | Exposes massive attack surface and slows CI/CD pipelines | Deploy minimalist `-slim` or `-alpine` alternatives |
| Layer ordering failures | Destroys build caching when source code overrides dependencies | Execute `COPY requirements` prior to full project `COPY . .` |

## Quiz

<details>
   <summary>1. A developer pushes a fix to their app and deploys it using `image: myapp` (no tag). The pod restarts, but the old version is still running. They swear they pushed the new image. What's going on?</summary>
   Without a tag, Kubernetes defaults to `:latest` and sets `imagePullPolicy: Always`. However, the developer likely pushed without tagging as `latest`, or the node has a cached version. The real problem is using `latest` in the first place -- it's ambiguous and unreproducible. The fix is to use specific version tags (e.g., `myapp:v1.2.3`) so each deployment references an exact image. This also makes rollbacks predictable since you know exactly which version each revision used.
</details>

<details>
   <summary>2. Your colleague deployed a pod that's stuck in `ImagePullBackOff`. They say the image name is correct because they can `docker pull` it on their laptop. What are the three most likely causes, and how do you systematically diagnose which one?</summary>
   Run `kubectl describe pod <name>` and check the Events section. The three most likely causes are: (1) the image name has a typo (e.g., `ngix` instead of `nginx`) -- the Events will say "not found"; (2) it's a private registry and the pod is missing `imagePullSecrets` -- the Events will show "unauthorized" or "authentication required"; (3) the tag doesn't exist in the registry -- Events will say "manifest unknown". Their laptop works because Docker is logged into the registry locally. The cluster nodes need separate authentication via `imagePullSecrets` or a ServiceAccount with registry credentials.
</details>

<details>
   <summary>3. You have a Dockerfile with `ENTRYPOINT ["python"]` and `CMD ["app.py"]`. In your Kubernetes pod spec, you want to run `python test.py` instead. Should you override `command`, `args`, or both?</summary>
   Override only `args: ["test.py"]`. In Kubernetes, `command` maps to Docker's `ENTRYPOINT` and `args` maps to `CMD`. Since you still want `python` as the entrypoint, leave `command` alone and just change `args`. If you set `command: ["python"]` AND `args: ["test.py"]`, it works but is redundant. If you only set `command: ["test.py"]`, it would try to execute `test.py` directly without the Python interpreter, which would fail.
</details>

<details>
   <summary>4. Your production cluster pulls images slowly because every pod restart re-downloads from the registry. All your images use specific version tags like `v2.1.0`. A teammate suggests setting `imagePullPolicy: Never` to fix it. Why is that dangerous, and what's the correct solution?</summary>
   `Never` means pods will fail to start on any node that doesn't already have the image cached -- this breaks scaling to new nodes and disaster recovery. The correct solution is `imagePullPolicy: IfNotPresent`, which is actually the default for specific version tags. If pods are still re-pulling, check whether someone has overridden the policy to `Always` in the pod spec. With `IfNotPresent`, the image is pulled once per node and cached, giving you fast restarts without the risk of `Never`.
</details>

<details>
   <summary>5. A developer shows you a Dockerfile that builds successfully, but the resulting image is 800MB and takes 5 minutes to build every time they change a single line of application code. The Dockerfile starts with `FROM ubuntu:latest`, runs a `COPY . .`, and then uses `RUN` to install heavily dependent packages. Why is this Dockerfile inefficient, and what are the two most impactful changes you can make to fix it?</summary>
   This Dockerfile suffers from poor layer caching and an overly large base image. Because `COPY . .` copies all application code before installing dependencies, any change to the source code invalidates the cache for the subsequent `RUN` commands, forcing a full dependency reinstallation on every build. Furthermore, `ubuntu:latest` is massive and contains tools unnecessary for most runtimes. The two most impactful changes are: 1) Switch to a minimal base image like an `-alpine` or `-slim` variant to drastically reduce the initial footprint. 2) Move the copying of dependency files (like `requirements.txt` or `package.json`) and the associated `RUN` install command above the `COPY . .` instruction so that dependencies remain cached unless the dependency manifest itself changes.
</details>

<details>
   <summary>6. Your security team mandates that all container images deployed to production must have an attached SBOM and a Cosign signature. They want to verify these attachments dynamically before pulling the main image, but without altering the image's original cryptographic digest. How does the OCI Distribution Spec v1.1.1 enable your registry to satisfy this requirement?</summary>
   It uses the Referrers API (`GET /v2/<name>/referrers/<digest>`), which allows the registry to link supplementary metadata (like signatures or attestations) directly to an image manifest as referring artifacts. This ensures the original image digest remains perfectly intact while still satisfying the security team's verification mandate.
</details>

<details>
   <summary>7. You are migrating a legacy deployment to a new multi-architecture Kubernetes cluster that contains both ARM64 and AMD64 nodes. When you deploy the application, you notice pods are scheduled on both node types and successfully pull the correct binaries without you needing to specify architecture-specific image tags. What underlying mechanism makes this seamless execution possible?</summary>
   The container runtime fetches an OCI Image Index (media type `application/vnd.oci.image.index.v1+json`), functioning as a "fat manifest." The runtime automatically evaluates the host node's architecture against this index and seamlessly resolves to the specific nested manifest that matches the hardware, eliminating the need for explicit architectural tagging in the pod spec.
</details>

<details>
   <summary>8. A vendor provides you with a proprietary software image that uses non-distributable OCI layer media types to enforce licensing restrictions. When attempting to sync this image to your private air-gapped registry, the CI pipeline throws synchronization errors and fails to transfer the layers. Based on the OCI Image Specification v1.1.0, why is this failure expected, and what should you tell the vendor?</summary>
   The failure is expected because non-distributable layer media types were officially deprecated in OCI Image Spec v1.1.0 due to the exact friction and fragmentation you are experiencing. You should inform the vendor that their distribution model relies on deprecated standards that fail across restricted network boundaries, and they must provide fully distributable payloads instead.
</details>

## Hands-On Exercise

**Scenario**: You have been tasked with investigating and remediating a broken application deployment in a staging environment.

**Task 1: Setup the broken environment**

```bash
# Create a deployment with intentional image problems
k create deploy broken-app --image=nginx:nonexistent
```

**Task 2: Diagnose the failure**
Observe the state of the deployment to identify the exact cause of the crash.

```bash
# Check pod status
k get pods
# Shows ImagePullBackOff

# Get details
k describe pod -l app=broken-app | grep -A5 Events
# Shows: nginx:nonexistent not found

# Fix by patching the deployment
k set image deploy/broken-app nginx=nginx:1.21.0

# Verify
k get pods
# Should show Running

# Cleanup
k delete deploy broken-app
```

**Success Criteria:**
- [ ] Identified the `ImagePullBackOff` status.
- [ ] Successfully queried the cluster events log.
- [ ] Mutated the deployment's image reference dynamically.
- [ ] Validated the transition to the `Running` phase.

## Practice Drills

### Drill 1: Image Name Parsing (Target: 2 minutes)

Identify the components of these image references:

```text
1. nginx
   Registry: docker.io (default)
   Namespace: library (default)
   Image: nginx
   Tag: latest (default)

2. gcr.io/google-containers/pause:3.2
   Registry: gcr.io
   Namespace: google-containers
   Image: pause
   Tag: 3.2

3. mycompany.com/team/app:v2.0.0-alpine
   Registry: mycompany.com
   Namespace: team
   Image: app
   Tag: v2.0.0-alpine
```

### Drill 2: Fix ImagePullBackOff (Target: 3 minutes)

```bash
# Create broken pod
k run broken --image=nginx:1.999.0

# Diagnose
k describe pod broken | grep -A5 Events

# Fix
k delete pod broken
k run broken --image=nginx:1.21.0

# Verify
k get pod broken

# Cleanup
k delete pod broken
```

### Drill 3: Private Registry Secret (Target: 4 minutes)

```bash
# Create registry secret
k create secret docker-registry myregistry \
  --docker-server=private.registry.io \
  --docker-username=testuser \
  --docker-password=testpass

# Create pod with secret reference
cat << EOF | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: private-pod
spec:
  containers:
  - name: app
    image: private.registry.io/app:latest
  imagePullSecrets:
  - name: myregistry
EOF

# Check if secret is referenced
k get pod private-pod -o jsonpath='{.spec.imagePullSecrets}'

# Cleanup
k delete pod private-pod
k delete secret myregistry
```

### Drill 4: Override Command and Args (Target: 3 minutes)

```bash
# Create pod that overrides CMD
cat << EOF | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: custom-cmd
spec:
  containers:
  - name: busybox
    image: busybox
    command: ["sh", "-c"]
    args: ["echo 'Custom command' && sleep 10"]
EOF

# Check logs
k logs custom-cmd

# Verify the command
k get pod custom-cmd -o jsonpath='{.spec.containers[0].command}'
k get pod custom-cmd -o jsonpath='{.spec.containers[0].args}'

# Cleanup
k delete pod custom-cmd
```

### Drill 5: imagePullPolicy Testing (Target: 3 minutes)

```bash
# Create pods with different policies
cat << EOF | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: pull-always
spec:
  containers:
  - name: nginx
    image: nginx:1.21.0
    imagePullPolicy: Always
---
apiVersion: v1
kind: Pod
metadata:
  name: pull-ifnotpresent
spec:
  containers:
  - name: nginx
    image: nginx:1.21.0
    imagePullPolicy: IfNotPresent
EOF

# Check policies
k get pod pull-always -o jsonpath='{.spec.containers[0].imagePullPolicy}'
k get pod pull-ifnotpresent -o jsonpath='{.spec.containers[0].imagePullPolicy}'

# Cleanup
k delete pod pull-always pull-ifnotpresent
```

### Drill 6: Complete Image Troubleshooting (Target: 5 minutes)

**Scenario:** A colleague pushed a deployment but pods won't start.

```bash
# Setup (simulating the problem)
k create deploy webapp --image=nginx:alpine-wrong-tag

# YOUR TASK: Find and fix the issue

# Step 1: Check deployment status
k get deploy webapp
k get pods -l app=webapp

# Step 2: Investigate the error
k describe pods -l app=webapp | grep -A10 Events

# Step 3: Find correct image tag
# (In real scenario, check registry or documentation)
# The correct tag is nginx:alpine

# Step 4: Fix
k set image deploy/webapp nginx=nginx:alpine

# Step 5: Verify
k rollout status deploy/webapp
k get pods -l app=webapp

# Cleanup
k delete deploy webapp
```

### Drill 7: Optimize a Dockerfile (Target: 5 minutes)

**Scenario:** A colleague hands you this Dockerfile. It works, but it takes forever to build and results in an unnecessarily large image.

```dockerfile
FROM node:18
WORKDIR /usr/src/app
COPY . .
RUN npm install
CMD ["node", "index.js"]
```

**Your Tasks:**
1. Identify the layer caching issue causing slow rebuilds.
2. Identify the base image size issue.
3. Rewrite the Dockerfile to optimize it.

**Solution:**
```dockerfile
# 1. Switch to a smaller base image (alpine)
FROM node:18-alpine
WORKDIR /usr/src/app

# 2. Copy ONLY package files first for layer caching
COPY package*.json ./
RUN npm install

# 3. Copy the rest of the application code AFTER dependencies
COPY . .
CMD ["node", "index.js"]
```

## Next Module

[Module 1.2: Jobs and CronJobs](../module-1.2-jobs-cronjobs/) - Master executing isolated workloads and scheduling highly resilient cron infrastructure.