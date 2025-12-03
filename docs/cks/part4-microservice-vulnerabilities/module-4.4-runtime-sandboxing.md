# Module 4.4: Runtime Sandboxing

> **Complexity**: `[MEDIUM]` - Advanced container isolation
>
> **Time to Complete**: 40-45 minutes
>
> **Prerequisites**: Module 4.3 (Secrets Management), container runtime concepts

---

## Why This Module Matters

Standard containers share the host kernel directly. If an attacker exploits a kernel vulnerability from within a container, they can escape to the host and compromise all workloads. Runtime sandboxing adds an extra isolation layer between containers and the kernel.

CKS tests your understanding of container isolation techniques.

---

## The Container Isolation Problem

```
┌─────────────────────────────────────────────────────────────┐
│              STANDARD CONTAINER ISOLATION                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Standard containers (runc):                               │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Container A │  │ Container B │  │ Container C │        │
│  │             │  │             │  │ (attacker)  │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │
│         └────────────────┼────────────────┘                │
│                          │                                 │
│                          ▼                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                    HOST KERNEL                        │ │
│  │                                                       │ │
│  │  🎯 Kernel exploit from any container                │ │
│  │     = Access to ALL containers and host              │ │
│  │                                                       │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  ⚠️  Single point of failure: the shared kernel          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Sandboxing Solutions

```
┌─────────────────────────────────────────────────────────────┐
│              RUNTIME SANDBOXING OPTIONS                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  gVisor (runsc)                                            │
│  ─────────────────────────────────────────────────────────  │
│  • User-space kernel written in Go                        │
│  • Intercepts syscalls, implements in user space          │
│  • Low overhead, medium isolation                         │
│  • Good for: untrusted workloads, multi-tenant            │
│                                                             │
│  Kata Containers                                           │
│  ─────────────────────────────────────────────────────────  │
│  • Lightweight VM per container                           │
│  • Real Linux kernel per container                        │
│  • Higher overhead, maximum isolation                     │
│  • Good for: strict isolation requirements                │
│                                                             │
│  Firecracker                                               │
│  ─────────────────────────────────────────────────────────  │
│  • MicroVM technology (used by AWS Lambda)                │
│  • Minimal virtual machine monitor                        │
│  • Fast boot, small footprint                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## gVisor Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              gVisor (runsc) ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                    Container                          │ │
│  │                    Application                        │ │
│  └───────────────────────┬───────────────────────────────┘ │
│                          │ syscalls                        │
│                          ▼                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │               gVisor Sentry (user-space)              │ │
│  │                                                       │ │
│  │  • Implements ~300 Linux syscalls                    │ │
│  │  • Runs in user space, not kernel                    │ │
│  │  • Written in Go (memory-safe)                       │ │
│  │  • Can't be exploited by kernel CVEs                │ │
│  │                                                       │ │
│  └───────────────────────┬───────────────────────────────┘ │
│                          │ limited syscalls               │
│                          ▼                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                    Host Kernel                        │ │
│  │                                                       │ │
│  │  Sentry only uses ~50 syscalls from host             │ │
│  │  Much smaller attack surface                         │ │
│  │                                                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Kata Containers Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              KATA CONTAINERS ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   Container A   │  │   Container B   │                  │
│  └────────┬────────┘  └────────┬────────┘                  │
│           │                    │                           │
│           ▼                    ▼                           │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │    Guest VM     │  │    Guest VM     │                  │
│  │  ┌───────────┐  │  │  ┌───────────┐  │                  │
│  │  │  Guest    │  │  │  │  Guest    │  │                  │
│  │  │  Kernel   │  │  │  │  Kernel   │  │                  │
│  │  └───────────┘  │  │  └───────────┘  │                  │
│  └────────┬────────┘  └────────┬────────┘                  │
│           │                    │                           │
│           └────────┬───────────┘                           │
│                    ▼                                       │
│  ┌──────────────────────────────────────────────────────┐ │
│  │        Hypervisor (QEMU/Cloud Hypervisor)            │ │
│  └──────────────────────────────────────────────────────┘ │
│                    │                                       │
│                    ▼                                       │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                    Host Kernel                        │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  Each container has its own kernel - full isolation       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## RuntimeClass

Kubernetes uses RuntimeClass to specify which container runtime to use.

### Define RuntimeClass

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc  # Name in containerd config
---
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: kata
handler: kata-qemu  # Name in containerd config
```

### Use RuntimeClass in Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sandboxed-pod
spec:
  runtimeClassName: gvisor  # Use gVisor instead of runc
  containers:
  - name: app
    image: nginx
```

---

## Installing gVisor

### On the Node

```bash
# Add gVisor repository (Debian/Ubuntu)
curl -fsSL https://gvisor.dev/archive.key | sudo gpg --dearmor -o /usr/share/keyrings/gvisor-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/gvisor-archive-keyring.gpg] https://storage.googleapis.com/gvisor/releases release main" | sudo tee /etc/apt/sources.list.d/gvisor.list

# Install
sudo apt update && sudo apt install -y runsc

# Verify
runsc --version
```

### Configure containerd

```toml
# /etc/containerd/config.toml

# Add after [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]

[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runsc]
  runtime_type = "io.containerd.runsc.v1"

[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runsc.options]
  TypeUrl = "io.containerd.runsc.v1.options"
```

### Restart containerd

```bash
sudo systemctl restart containerd
```

### Create RuntimeClass

```bash
cat <<EOF | kubectl apply -f -
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc
EOF
```

---

## Using gVisor

### Create Sandboxed Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gvisor-test
spec:
  runtimeClassName: gvisor
  containers:
  - name: test
    image: nginx
```

### Verify gVisor is Running

```bash
# Create the pod
kubectl apply -f gvisor-pod.yaml

# Check runtime
kubectl get pod gvisor-test -o jsonpath='{.spec.runtimeClassName}'
# Output: gvisor

# Inside the container, check kernel version
kubectl exec gvisor-test -- uname -a
# Output shows "gVisor" instead of host kernel version

# Check dmesg (gVisor intercepts this)
kubectl exec gvisor-test -- dmesg 2>&1 | head -5
# Output shows gVisor's simulated kernel messages
```

---

## gVisor Limitations

```
┌─────────────────────────────────────────────────────────────┐
│              gVisor LIMITATIONS                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Not all syscalls supported:                              │
│  ├── Some advanced syscalls not implemented               │
│  ├── May break certain applications                       │
│  └── Check compatibility before using                      │
│                                                             │
│  Performance overhead:                                     │
│  ├── ~5-15% for compute workloads                        │
│  ├── Higher for I/O intensive workloads                   │
│  └── Syscall interception has cost                        │
│                                                             │
│  Not compatible with:                                     │
│  ├── Host networking (hostNetwork: true)                 │
│  ├── Host PID namespace (hostPID: true)                  │
│  ├── Privileged containers                                │
│  └── Some volume types                                    │
│                                                             │
│  Good for:                                                │
│  ├── Web applications                                     │
│  ├── Microservices                                        │
│  ├── Untrusted workloads                                 │
│  └── Multi-tenant environments                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Scheduling with RuntimeClass

### NodeSelector for RuntimeClass

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc
scheduling:
  nodeSelector:
    gvisor.kubernetes.io/enabled: "true"  # Only schedule on these nodes
  tolerations:
  - key: "gvisor"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
```

### Ensure Workloads Use Correct Nodes

```bash
# Label nodes that have gVisor installed
kubectl label node worker1 gvisor.kubernetes.io/enabled=true

# Now pods with runtimeClassName: gvisor will only schedule on labeled nodes
```

---

## Real Exam Scenarios

### Scenario 1: Create RuntimeClass and Use It

```bash
# Step 1: Create RuntimeClass
cat <<EOF | kubectl apply -f -
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc
EOF

# Step 2: Create pod using RuntimeClass
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: untrusted-workload
spec:
  runtimeClassName: gvisor
  containers:
  - name: app
    image: nginx
EOF

# Step 3: Verify
kubectl get pod untrusted-workload -o yaml | grep runtimeClassName
kubectl exec untrusted-workload -- uname -a  # Shows gVisor
```

### Scenario 2: Identify Pods Not Using Sandboxing

```bash
# Find all pods without runtimeClassName
kubectl get pods -A -o json | jq -r '
  .items[] |
  select(.spec.runtimeClassName == null) |
  "\(.metadata.namespace)/\(.metadata.name)"
'

# Find pods with specific RuntimeClass
kubectl get pods -A -o json | jq -r '
  .items[] |
  select(.spec.runtimeClassName == "gvisor") |
  "\(.metadata.namespace)/\(.metadata.name)"
'
```

### Scenario 3: Enforce RuntimeClass for Namespace

```yaml
# Use a ValidatingAdmissionPolicy (K8s 1.28+) or OPA/Gatekeeper
# Example with namespace annotation for documentation

apiVersion: v1
kind: Namespace
metadata:
  name: untrusted-workloads
  labels:
    security.kubernetes.io/sandbox-required: "true"
```

---

## Comparison: runc vs gVisor vs Kata

```
┌───────────────────────────────────────────────────────────────────┐
│                    RUNTIME COMPARISON                              │
├─────────────────┬─────────────────┬─────────────────┬─────────────┤
│ Feature         │ runc (default)  │ gVisor          │ Kata        │
├─────────────────┼─────────────────┼─────────────────┼─────────────┤
│ Isolation       │ Namespaces only │ User-space      │ VM per pod  │
│                 │                 │ kernel          │             │
├─────────────────┼─────────────────┼─────────────────┼─────────────┤
│ Kernel sharing  │ Shared          │ Intercepted     │ Not shared  │
├─────────────────┼─────────────────┼─────────────────┼─────────────┤
│ Overhead        │ Minimal         │ Low-Medium      │ Medium-High │
├─────────────────┼─────────────────┼─────────────────┼─────────────┤
│ Boot time       │ ~100ms          │ ~200ms          │ ~500ms      │
├─────────────────┼─────────────────┼─────────────────┼─────────────┤
│ Memory          │ Low             │ Low-Medium      │ Higher      │
├─────────────────┼─────────────────┼─────────────────┼─────────────┤
│ Compatibility   │ Full            │ Most apps       │ Most apps   │
├─────────────────┼─────────────────┼─────────────────┼─────────────┤
│ Use case        │ General         │ Untrusted       │ High        │
│                 │                 │ workloads       │ security    │
└─────────────────┴─────────────────┴─────────────────┴─────────────┘
```

---

## Did You Know?

- **gVisor was developed by Google** and is used in Google Cloud Run and other GCP services. It intercepts about 300 Linux syscalls and implements them in user space.

- **Kata Containers merged from Intel Clear Containers and Hyper runV**. It uses the same OCI interface as runc, so it's a drop-in replacement.

- **The handler name in RuntimeClass** must match the runtime name configured in containerd/CRI-O. Common names: `runsc` (gVisor), `kata-qemu` or `kata` (Kata).

- **AWS Fargate uses Firecracker**, another micro-VM technology similar to Kata but optimized for fast boot times.

---

## Common Mistakes

| Mistake | Why It Hurts | Solution |
|---------|--------------|----------|
| Wrong handler name | Pod fails to schedule | Match containerd config |
| No RuntimeClass | Uses default runc | Create RuntimeClass first |
| gVisor on incompatible workload | App crashes | Test compatibility first |
| Missing node selector | Schedules on wrong node | Use scheduling in RuntimeClass |
| Expecting full syscall support | App fails | Check gVisor syscall table |

---

## Quiz

1. **What is the main security benefit of gVisor?**
   <details>
   <summary>Answer</summary>
   gVisor intercepts syscalls in user space, so kernel vulnerabilities in the host can't be directly exploited from the container. It reduces the attack surface from ~300+ syscalls to ~50.
   </details>

2. **How does Kata Containers achieve isolation?**
   <details>
   <summary>Answer</summary>
   Kata runs each container (or pod) in a lightweight VM with its own Linux kernel. Container syscalls go to the guest kernel, not the host kernel, providing hardware-level isolation.
   </details>

3. **What Kubernetes resource specifies the container runtime?**
   <details>
   <summary>Answer</summary>
   RuntimeClass. It maps a name (used in pod spec) to a handler (configured in containerd). Pods reference it with `spec.runtimeClassName`.
   </details>

4. **What are the limitations of gVisor?**
   <details>
   <summary>Answer</summary>
   Not all syscalls supported, some applications may not work, higher I/O overhead, incompatible with hostNetwork/hostPID/privileged containers.
   </details>

---

## Hands-On Exercise

**Task**: Create and use a RuntimeClass for sandboxed workloads.

```bash
# Step 1: Check if gVisor is available (on lab environment)
runsc --version 2>/dev/null || echo "gVisor not installed (expected in exam environment)"

# Step 2: Check existing RuntimeClasses
kubectl get runtimeclass

# Step 3: Create RuntimeClass (works even if gVisor not installed)
cat <<EOF | kubectl apply -f -
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc
EOF

# Step 4: Create pod without sandboxing
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: standard-pod
spec:
  containers:
  - name: test
    image: busybox
    command: ["sleep", "3600"]
EOF

# Step 5: Create pod with sandboxing
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: sandboxed-pod
spec:
  runtimeClassName: gvisor
  containers:
  - name: test
    image: busybox
    command: ["sleep", "3600"]
EOF

# Step 6: Compare pod specs
echo "=== Standard Pod ==="
kubectl get pod standard-pod -o jsonpath='{.spec.runtimeClassName}'
echo ""

echo "=== Sandboxed Pod ==="
kubectl get pod sandboxed-pod -o jsonpath='{.spec.runtimeClassName}'
echo ""

# Step 7: List all RuntimeClasses
kubectl get runtimeclass -o wide

# Cleanup
kubectl delete pod standard-pod sandboxed-pod
kubectl delete runtimeclass gvisor
```

**Success criteria**: Understand RuntimeClass configuration and pod assignment.

---

## Summary

**Why Sandboxing?**
- Containers share host kernel
- Kernel exploit = escape to host
- Sandboxing adds isolation layer

**gVisor**:
- User-space kernel
- Intercepts syscalls
- Low overhead
- Good for untrusted workloads

**Kata Containers**:
- VM per container
- Full kernel isolation
- Higher overhead
- Maximum security

**RuntimeClass**:
- Kubernetes abstraction for runtimes
- Handler matches containerd config
- Pod uses `runtimeClassName`

**Exam Tips**:
- Know RuntimeClass YAML format
- Understand gVisor vs Kata tradeoffs
- Be able to apply RuntimeClass to pods

---

## Part 4 Complete!

You've finished **Minimize Microservice Vulnerabilities** (20% of CKS). You now understand:
- Security Contexts for pods and containers
- Pod Security Admission standards
- Secrets management and encryption
- Runtime sandboxing with gVisor

**Next Part**: [Part 5: Supply Chain Security](../part5-supply-chain-security/module-5.1-image-security.md) - Securing container images and the software supply chain.
