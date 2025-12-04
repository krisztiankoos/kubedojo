# Module 4.3: Container Escape

> **Complexity**: `[MEDIUM]` - Threat awareness
>
> **Time to Complete**: 25-30 minutes
>
> **Prerequisites**: [Module 4.2: Common Vulnerabilities](module-4.2-vulnerabilities.md)

---

## Why This Module Matters

Container escape—breaking out of a container to access the host—is the most severe container security failure. Understanding escape techniques helps you configure defenses and recognize dangerous configurations.

KCSA tests your ability to identify configurations that enable container escape and understand prevention strategies.

---

## What is Container Escape?

```
┌─────────────────────────────────────────────────────────────┐
│              CONTAINER ESCAPE DEFINED                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  NORMAL CONTAINER ISOLATION:                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  HOST                                               │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │ Container A │ │ Container B │ │ Container C │   │   │
│  │  │ (isolated)  │ │ (isolated)  │ │ (isolated)  │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│  Containers can't see or affect host or each other         │
│                                                             │
│  CONTAINER ESCAPE:                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  HOST ← COMPROMISED                                 │   │
│  │  ┌─────────────┐                                    │   │
│  │  │ Container A │──→ ESCAPE ──→ Full host access    │   │
│  │  │ (attacker)  │                                    │   │
│  │  └─────────────┘                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│  Attacker breaks isolation, gains host access              │
│                                                             │
│  IMPACT: Node compromise, lateral movement, cluster        │
│  compromise possible                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Escape Techniques

### 1. Privileged Container Escape

```
┌─────────────────────────────────────────────────────────────┐
│              PRIVILEGED CONTAINER ESCAPE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CONFIGURATION:                                            │
│  securityContext:                                          │
│    privileged: true                                        │
│                                                             │
│  WHAT IT GRANTS:                                           │
│  • All Linux capabilities                                  │
│  • Access to all host devices (/dev/*)                     │
│  • No seccomp filtering                                    │
│  • SELinux/AppArmor bypassed                              │
│                                                             │
│  ESCAPE METHOD:                                            │
│  1. Mount host filesystem:                                 │
│     mount /dev/sda1 /mnt                                  │
│  2. Access host files:                                     │
│     cat /mnt/etc/shadow                                   │
│  3. Modify host:                                          │
│     echo "attacker ALL=(ALL) NOPASSWD:ALL" >> /mnt/etc/...│
│  4. Escape via cron, ssh, or exec on host                 │
│                                                             │
│  TRIVIAL ESCAPE - Never use privileged: true              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. Host Namespace Escape

```
┌─────────────────────────────────────────────────────────────┐
│              HOST NAMESPACE ESCAPE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  hostPID: true                                             │
│  ├── Container sees all host processes                     │
│  ├── Can send signals to host processes                    │
│  └── Can attach to host processes (with capabilities)      │
│                                                             │
│  ESCAPE METHOD:                                            │
│  # Enter namespace of host process (e.g., PID 1)          │
│  nsenter --target 1 --mount --uts --ipc --net --pid bash  │
│                                                             │
│  hostNetwork: true                                         │
│  ├── Container uses host's network stack                   │
│  ├── Can bind to any host port                             │
│  └── Can sniff all host network traffic                    │
│                                                             │
│  hostIPC: true                                             │
│  ├── Access to host shared memory                          │
│  └── Can communicate with host processes via IPC           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. Dangerous Volume Mounts

```
┌─────────────────────────────────────────────────────────────┐
│              HOST PATH ESCAPE                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  DANGEROUS MOUNTS:                                         │
│                                                             │
│  hostPath: { path: / }                                     │
│  └── Full host filesystem access                           │
│                                                             │
│  hostPath: { path: /etc }                                  │
│  └── Modify passwd, shadow, crontab                        │
│                                                             │
│  hostPath: { path: /var/run/docker.sock }                  │
│  └── Control Docker daemon → create privileged containers  │
│                                                             │
│  hostPath: { path: /var/log }                              │
│  └── Read logs, potential sensitive data                   │
│                                                             │
│  hostPath: { path: /root/.ssh }                            │
│  └── Steal SSH keys                                        │
│                                                             │
│  ESCAPE METHOD (Docker socket):                            │
│  1. Mount docker.sock into container                       │
│  2. Run: docker run -v /:/host --privileged alpine        │
│  3. Access host via new container                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4. Capability-Based Escape

```
┌─────────────────────────────────────────────────────────────┐
│              DANGEROUS CAPABILITIES                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CAP_SYS_ADMIN                                             │
│  ├── Nearly equivalent to root                             │
│  ├── Can mount filesystems                                 │
│  └── Can escape via mount namespaces                       │
│                                                             │
│  CAP_SYS_PTRACE                                            │
│  ├── Can debug any process (with hostPID)                  │
│  ├── Read process memory                                   │
│  └── Inject code into processes                            │
│                                                             │
│  CAP_NET_ADMIN                                             │
│  ├── Configure network interfaces                          │
│  └── Capture traffic, modify routing                       │
│                                                             │
│  CAP_DAC_READ_SEARCH                                       │
│  ├── Bypass file read permission checks                    │
│  └── Read any file                                         │
│                                                             │
│  CAP_DAC_OVERRIDE                                          │
│  ├── Bypass all file permission checks                     │
│  └── Write to any file                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5. Kernel Vulnerability Escape

```
┌─────────────────────────────────────────────────────────────┐
│              KERNEL EXPLOIT ESCAPE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CONCEPT:                                                  │
│  • Containers share the host kernel                        │
│  • Kernel vulnerability = escape opportunity               │
│  • Works even with "secure" container settings             │
│                                                             │
│  EXAMPLES:                                                 │
│  ├── Dirty COW (CVE-2016-5195)                            │
│  ├── Dirty Pipe (CVE-2022-0847)                           │
│  └── Various privilege escalation CVEs                     │
│                                                             │
│  MITIGATION:                                               │
│  • Keep kernel updated                                     │
│  • Use seccomp to limit syscalls                          │
│  • Consider sandboxed runtimes (gVisor, Kata)             │
│  • Sandboxed runtimes use different kernel or intercept   │
│    syscalls, reducing kernel attack surface               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Prevention Strategies

### Pod Security Standards

```
┌─────────────────────────────────────────────────────────────┐
│              PSS PREVENTS ESCAPE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  BASELINE STANDARD BLOCKS:                                 │
│  ├── privileged: true                                      │
│  ├── hostNetwork: true                                     │
│  ├── hostPID: true                                         │
│  ├── hostIPC: true                                         │
│  └── Sensitive hostPath mounts                             │
│                                                             │
│  RESTRICTED STANDARD ADDITIONALLY:                         │
│  ├── Requires non-root                                     │
│  ├── Requires seccomp profile                              │
│  ├── Drops all capabilities                                │
│  └── Requires read-only root filesystem                    │
│                                                             │
│  ENABLE IN NAMESPACE:                                      │
│  kubectl label ns production \                             │
│    pod-security.kubernetes.io/enforce=restricted           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────┐
│              CONTAINER ESCAPE PREVENTION                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LAYER 1: POD SECURITY                                     │
│  ├── Pod Security Standards (Restricted)                   │
│  ├── No privileged containers                              │
│  ├── No host namespace sharing                             │
│  ├── No dangerous hostPath mounts                          │
│  └── Drop all capabilities                                 │
│                                                             │
│  LAYER 2: RUNTIME SECURITY                                 │
│  ├── Seccomp profiles (RuntimeDefault minimum)             │
│  ├── AppArmor/SELinux profiles                             │
│  ├── Read-only root filesystem                             │
│  └── Run as non-root user                                  │
│                                                             │
│  LAYER 3: RUNTIME ISOLATION                                │
│  ├── Consider gVisor for untrusted workloads              │
│  ├── Consider Kata Containers for strong isolation         │
│  └── Runtime classes for different security levels         │
│                                                             │
│  LAYER 4: MONITORING                                       │
│  ├── Runtime security (Falco)                              │
│  ├── File integrity monitoring                             │
│  └── Anomaly detection                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Sandboxed Runtimes

```
┌─────────────────────────────────────────────────────────────┐
│              SANDBOXED RUNTIME OPTIONS                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  gVisor (runsc)                                            │
│  ├── User-space kernel                                     │
│  ├── Intercepts and emulates syscalls                      │
│  ├── Container doesn't directly touch host kernel          │
│  ├── Performance overhead                                  │
│  └── Good for: Untrusted workloads, multi-tenant           │
│                                                             │
│  Kata Containers                                           │
│  ├── Lightweight VM per container                          │
│  ├── Separate kernel from host                             │
│  ├── Hardware virtualization isolation                     │
│  ├── More overhead than gVisor                             │
│  └── Good for: Maximum isolation, compliance               │
│                                                             │
│  USING RUNTIME CLASSES:                                    │
│  apiVersion: node.k8s.io/v1                                │
│  kind: RuntimeClass                                        │
│  metadata:                                                 │
│    name: gvisor                                            │
│  handler: runsc                                            │
│  ---                                                       │
│  spec:                                                     │
│    runtimeClassName: gvisor  # Use in pod spec            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Did You Know?

- **Most container escapes are misconfigurations**, not zero-days. Proper configuration prevents most escape scenarios.

- **Docker socket mount** is one of the most common escape vectors. Mounting /var/run/docker.sock gives control over all containers on the host.

- **gVisor intercepts over 200 syscalls** and implements them in user-space, dramatically reducing kernel attack surface.

- **Kata Containers** use the same hypervisor technology (QEMU/KVM) as virtual machines, providing VM-level isolation for containers.

---

## Common Mistakes

| Mistake | Why It Hurts | Solution |
|---------|--------------|----------|
| privileged: true for convenience | Trivial escape | Use specific capabilities |
| Mounting Docker socket | Container controls all containers | Use alternatives |
| hostPath to sensitive dirs | Direct host access | Use PV/PVC instead |
| Not enforcing PSS | Allows dangerous configs | Enable PSS in namespaces |
| Running as root | Higher privilege post-exploit | runAsNonRoot: true |

---

## Quiz

1. **What makes a privileged container easy to escape?**
   <details>
   <summary>Answer</summary>
   Privileged containers have all Linux capabilities, access to all host devices, no seccomp filtering, and bypass SELinux/AppArmor. This allows trivial escape by mounting the host filesystem or accessing host devices directly.
   </details>

2. **How can hostPID: true enable container escape?**
   <details>
   <summary>Answer</summary>
   With hostPID, the container can see all host processes and can use nsenter to enter the namespace of a host process (like PID 1/init), effectively gaining a shell on the host.
   </details>

3. **Why is mounting Docker socket dangerous?**
   <details>
   <summary>Answer</summary>
   The Docker socket gives full control over the Docker daemon. An attacker can create a new privileged container that mounts the host filesystem, escaping to the host through that container.
   </details>

4. **How do sandboxed runtimes like gVisor prevent escape?**
   <details>
   <summary>Answer</summary>
   gVisor runs a user-space kernel that intercepts and emulates system calls. The container never directly interacts with the host kernel, so kernel vulnerabilities can't be exploited for escape.
   </details>

5. **What Pod Security Standard level prevents most container escape techniques?**
   <details>
   <summary>Answer</summary>
   Baseline prevents the most dangerous settings (privileged, host namespaces). Restricted adds additional protections (non-root, seccomp, dropped capabilities) for stronger prevention.
   </details>

---

## Hands-On Exercise: Escape Path Analysis

**Scenario**: Analyze this pod specification and identify escape paths:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: risky-pod
spec:
  hostPID: true
  containers:
  - name: app
    image: ubuntu:20.04
    securityContext:
      capabilities:
        add:
        - SYS_ADMIN
        - SYS_PTRACE
    volumeMounts:
    - name: docker-sock
      mountPath: /var/run/docker.sock
    - name: host-root
      mountPath: /host
  volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
  - name: host-root
    hostPath:
      path: /
```

**Identify the escape paths:**

<details>
<summary>Escape Paths</summary>

This pod has **multiple** escape paths:

**1. Docker Socket (Easiest)**
- Mount: /var/run/docker.sock
- Attack: `docker run -v /:/host --privileged alpine chroot /host`
- Result: Full host access

**2. Host Filesystem Mount**
- Mount: / → /host
- Attack: Direct file access, modify /host/etc/passwd
- Result: Add user, access SSH keys, modify crontab

**3. hostPID + SYS_PTRACE**
- Settings: hostPID: true, CAP_SYS_PTRACE
- Attack: `nsenter -t 1 -m -u -i -n -p bash`
- Result: Enter init's namespace, shell on host

**4. hostPID + SYS_ADMIN**
- Settings: hostPID: true, CAP_SYS_ADMIN
- Attack: Mount namespace manipulation
- Result: Create mounts that access host

**Prevention**: Remove ALL of these settings. Use restricted PSS.

</details>

---

## Summary

Container escape breaks the fundamental isolation promise:

| Escape Vector | Configuration | Prevention |
|--------------|---------------|------------|
| Privileged | `privileged: true` | Never use in production |
| Host namespaces | `hostPID/Network/IPC` | Block via PSS |
| Host paths | `hostPath: /` | Use PV/PVC instead |
| Capabilities | `CAP_SYS_ADMIN` | Drop all, add minimal |
| Kernel exploits | Shared kernel | Sandboxed runtimes |

Defense strategy:
- Enforce Pod Security Standards (Baseline minimum, Restricted preferred)
- Use seccomp and AppArmor/SELinux
- Consider sandboxed runtimes for untrusted workloads
- Monitor for escape attempts with Falco

---

## Next Module

[Module 4.4: Supply Chain Threats](module-4.4-supply-chain.md) - Understanding and mitigating software supply chain risks.
