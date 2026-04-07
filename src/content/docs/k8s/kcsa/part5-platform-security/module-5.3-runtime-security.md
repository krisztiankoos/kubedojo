---
title: "Module 5.3: Runtime Security"
slug: k8s/kcsa/part5-platform-security/module-5.3-runtime-security
sidebar:
  order: 4
---
> **Complexity**: `[MEDIUM]` - Core knowledge
>
> **Time to Complete**: 45-60 minutes
>
> **Prerequisites**: [Module 5.2: Security Observability](../module-5.2-observability/)

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Implement** robust system call filtering using custom and default seccomp profiles to shrink the kernel attack surface.
2. **Compare** the enforcement mechanisms of AppArmor and SELinux, selecting the appropriate Mandatory Access Control system based on your host operating system architecture.
3. **Diagnose** workload failures caused by overly restrictive capability drops and design minimal-privilege security contexts.
4. **Evaluate** the performance and security trade-offs between standard OCI runtimes (runc) and sandboxed runtimes (gVisor, Kata Containers) for multi-tenant environments.
5. **Design** cluster-wide preventative guardrails using policy engines like OPA Gatekeeper and Kyverno to enforce runtime security baselines dynamically.

## Why This Module Matters

In early 2018, researchers discovered that Tesla's Kubernetes administrative console was fully exposed to the public internet without authentication. Attackers did not just steal data; they deployed malicious pods into the cluster. Because the cluster lacked fundamental runtime security controls, these pods ran with broad kernel privileges, unfettered network access, and no resource constraints. The attackers quietly installed Stratum mining protocol software and siphoned immense amounts of AWS compute resources to mine cryptocurrency. The financial impact of the stolen cloud compute and the subsequent incident response and architecture overhaul cost hundreds of thousands of dollars.

This incident perfectly illustrates the gap between configuration security and runtime security. Build-time scanning and static misconfiguration checks are vital, but they cannot stop an attacker who has already found a way to execute code inside your environment. Once a workload is running, it is interacting dynamically with the host kernel, the network, and the filesystem. Without runtime security controls, a compromised container is merely a Linux process with a direct, unobstructed highway to the underlying node's operating system. 

Runtime security represents the final line of defense. It assumes breach. By enforcing strict boundaries exactly when the application is running, you ensure that even if a vulnerability in your application code is exploited, the attacker finds themselves trapped in a featureless box. They cannot mount file systems, they cannot change their user ID, they cannot open raw network sockets, and they cannot trace other processes. Mastering runtime security is what separates clusters that contain breaches locally from clusters that allow lateral movement and total node compromise.

## The Runtime Security Stack

To secure a running container, you must understand that a container is not a real security boundary. A container is simply a Linux process wrapped in namespaces (for isolation) and cgroups (for resource limiting). Because all containers on a node share the exact same underlying operating system kernel, securing the runtime means placing filters and walls between the containerized process and that shared kernel.

```text
┌─────────────────────────────────────────────────────────────┐
│              RUNTIME SECURITY STACK                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LAYER 4: KUBERNETES ADMISSION                             │
│  ├── Validates pods before scheduling                      │
│  ├── Pod Security Standards                                │
│  └── Policy engines (OPA, Kyverno)                        │
│                                                             │
│  LAYER 3: CONTAINER RUNTIME                                │
│  ├── OCI runtime (runc, crun)                             │
│  ├── Sandboxed runtimes (gVisor, Kata)                    │
│  └── Runtime security configuration                        │
│                                                             │
│  LAYER 2: LINUX SECURITY MODULES                           │
│  ├── seccomp (syscall filtering)                          │
│  ├── AppArmor (file/network restrictions)                 │
│  ├── SELinux (mandatory access control)                   │
│  └── Capabilities (privilege restrictions)                 │
│                                                             │
│  LAYER 1: KERNEL                                           │
│  ├── Namespaces (isolation)                               │
│  ├── cgroups (resource limits)                            │
│  └── Core security features                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

The stack operates from the bottom up regarding execution, but from the top down regarding Kubernetes configuration. When you submit a Pod to the API server, Layer 4 (Admission) inspects the request. If approved, the Kubelet instructs Layer 3 (Container Runtime) to start the process. The runtime then configures Layer 2 (Linux Security Modules) and Layer 1 (Kernel primitives) before finally executing your application code. 

Understanding how to manipulate Layers 2, 3, and 4 is the core of Kubernetes runtime security.

## System Call Filtering with Seccomp

Every action a program wants to take that involves the hardware or system resources—reading a file, opening a network connection, checking the time—requires asking the kernel for permission. The program makes a "system call" (syscall). The Linux kernel has hundreds of system calls, but the average web application only uses a small fraction of them. 

### How Seccomp Operates

```text
┌─────────────────────────────────────────────────────────────┐
│              SECCOMP (SECURE COMPUTING MODE)                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PURPOSE:                                                  │
│  • Filter which system calls a process can make            │
│  • Block dangerous syscalls (mount, ptrace, etc.)          │
│  • Reduce kernel attack surface                            │
│                                                             │
│  HOW IT WORKS:                                             │
│  Application → Syscall → Seccomp Filter → Allow/Deny/Log  │
│                                                             │
│  PROFILE TYPES:                                            │
│  ├── RuntimeDefault - Container runtime's default profile │
│  ├── Unconfined - No filtering (dangerous)                │
│  └── Localhost - Custom profile from node                 │
│                                                             │
│  KUBERNETES 1.27+:                                         │
│  RuntimeDefault is the default for new clusters            │
│                                                             │
│  BLOCKED BY DEFAULT (RuntimeDefault):                      │
│  • mount, umount                                          │
│  • ptrace                                                 │
│  • reboot                                                 │
│  • Most kernel module operations                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Think of Seccomp (Secure Computing Mode) as a highly strict bouncer at the door of the kernel. When a process attempts to execute a syscall, Seccomp checks the process's assigned profile. If the syscall is on the allowed list, it passes. If it is on the deny list, Seccomp immediately kills the process or returns an error (like `EPERM`).

By default, Docker and containerd provide a `RuntimeDefault` profile that blocks roughly forty-four dangerous system calls while allowing the rest. This blocks calls like `kexec_load` (loading a new kernel), `bpf` (loading eBPF programs), and `unshare` (creating new namespaces)—calls that no standard web application should ever need, but which are highly useful for attackers attempting container escape.

### Implementing Seccomp in Kubernetes

Prior to Kubernetes 1.27, pods ran as `Unconfined` by default unless specified otherwise. This meant no syscall filtering was applied. Modern clusters default to `RuntimeDefault`. However, for maximum security, explicit definition in your Pod manifests is best practice.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-nginx
spec:
  securityContext:
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: nginx
    image: nginx:1.25.3
    securityContext:
      # You can also define it at the container level
      # which overrides the pod-level setting
      seccompProfile:
        type: RuntimeDefault
```

### Authoring Custom Profiles

For highly sensitive workloads, `RuntimeDefault` might still be too permissive. You can create custom profiles and place them on the worker nodes (typically in `/var/lib/kubelet/seccomp/`). 

A custom profile is written in JSON and defines a default action, the architecture, and explicit rules.

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": [
    "SCMP_ARCH_X86_64",
    "SCMP_ARCH_X86",
    "SCMP_ARCH_X32"
  ],
  "syscalls": [
    {
      "names": [
        "accept4",
        "bind",
        "close",
        "epoll_ctl",
        "epoll_pwait",
        "listen",
        "read",
        "write"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

In the profile above, the `defaultAction` is `SCMP_ACT_ERRNO`, meaning any syscall NOT explicitly listed will result in a permission error. This is a default-deny approach. Creating these profiles requires deep profiling of your application using tools like `strace` to ensure you do not break legitimate functionality.

To use this custom profile, the JSON file must exist on the node, and your pod specification must reference it using the `Localhost` type:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: custom-seccomp-pod
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: custom-profiles/strict-web.json
  containers:
  - name: web
    image: my-secure-app:v2
```

> **Stop and think**: If an attacker exploits a remote code execution vulnerability in your application and attempts to download a malware payload using `curl`, will a strict seccomp profile that only allows `read`, `write`, `open`, and `close` prevent the download? Why or why not?

## Mandatory Access Control: AppArmor

While seccomp filters the vocabulary a program can use (syscalls), AppArmor restricts what the program can talk about (files, network paths, capabilities). AppArmor is a Linux Security Module (LSM) that implements Mandatory Access Control (MAC).

```text
┌─────────────────────────────────────────────────────────────┐
│              APPARMOR                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PURPOSE:                                                  │
│  • Mandatory Access Control (MAC)                          │
│  • Restrict file access, network, capabilities             │
│  • Program-specific security policies                      │
│                                                             │
│  AVAILABLE ON:                                             │
│  • Ubuntu, Debian, SUSE                                   │
│  • NOT on RHEL/CentOS (use SELinux instead)               │
│                                                             │
│  PROFILE MODES:                                            │
│  ├── Enforce - Block violations                           │
│  ├── Complain - Log but allow (learning mode)             │
│  └── Unconfined - No restrictions                         │
│                                                             │
│  EXAMPLE RESTRICTIONS:                                     │
│  • Deny write to /etc/*                                   │
│  • Allow read from /var/log/*                             │
│  • Deny network raw access                                │
│  • Deny mount operations                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Discretionary Access Control (DAC) is the standard Linux permission model (read/write/execute flags owned by users and groups). If an attacker becomes the `root` user in a container, DAC allows them to do anything. Mandatory Access Control (MAC) overrides DAC. Even if a process runs as `root`, if the AppArmor profile says "deny write to /etc/passwd", the root process will receive a permission denied error.

AppArmor profiles must be loaded into the kernel of the Kubernetes worker nodes before they can be used. This is often done using a DaemonSet that runs a privileged init container to parse and load the profiles using the `apparmor_parser` utility.

### AppArmor Syntax and Usage

AppArmor profiles are written in a specialized syntax that is generally considered more human-readable than SELinux policies.

```text
#include <tunables/global>

profile custom-nginx flags=(attach_disconnected) {
  #include <abstractions/base>
  #include <abstractions/nameservice>

  # Allow read access to web content
  /usr/share/nginx/html/** r,
  
  # Allow read/write to specific log and cache directories
  /var/log/nginx/** rw,
  /var/cache/nginx/** rw,
  /run/nginx.pid rw,

  # Explicitly deny access to sensitive files
  deny /etc/passwd r,
  deny /etc/shadow r,
  deny /etc/kubernetes/** r,

  # Deny the ability to execute shells
  deny /bin/sh x,
  deny /bin/bash x,
  
  # Deny raw sockets (prevents certain types of network spoofing)
  deny network raw,
}
```

To apply this profile to a pod, you historically used annotations. However, in newer Kubernetes versions (1.30+), AppArmor is moving to a proper field within the `securityContext`. We will show the standard annotation method which is widely supported across production clusters today:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: apparmor-protected
  annotations:
    container.apparmor.security.beta.kubernetes.io/web: localhost/custom-nginx
spec:
  containers:
  - name: web
    image: nginx:alpine
```

**War Story**: During a red team engagement, attackers found a path traversal vulnerability in a Java web application. The application was running as the root user. The attackers attempted to read `/etc/shadow` to crack password hashes. The application had an AppArmor profile applied that explicitly denied read access to `/etc/` except for the application's specific configuration folder. The path traversal exploit succeeded in manipulating the path string, but the kernel intercepted the read request and killed the process, logging the attempt and thwarting the attack entirely.

## Mandatory Access Control: SELinux

Security-Enhanced Linux (SELinux) serves the same fundamental purpose as AppArmor but uses a vastly different architectural approach. Originally developed by the NSA, SELinux is standard on RHEL, CentOS, Fedora, and Rocky Linux distributions.

```text
┌─────────────────────────────────────────────────────────────┐
│              SELINUX                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PURPOSE:                                                  │
│  • Mandatory Access Control (MAC)                          │
│  • Label-based security                                    │
│  • Every file, process has a security context              │
│                                                             │
│  AVAILABLE ON:                                             │
│  • RHEL, CentOS, Fedora                                   │
│  • NOT on Ubuntu/Debian (use AppArmor)                    │
│                                                             │
│  MODES:                                                    │
│  ├── Enforcing - Block violations                         │
│  ├── Permissive - Log but allow                           │
│  └── Disabled - No SELinux                                │
│                                                             │
│  CONTEXT FORMAT:                                           │
│  user:role:type:level                                      │
│  system_u:system_r:container_t:s0                         │
│                                                             │
│  KUBERNETES USES:                                          │
│  • seLinuxOptions in securityContext                      │
│  • Labels for pod processes and volumes                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

While AppArmor restricts based on file paths (e.g., `/var/log/app.log`), SELinux restricts based on labels attached to objects. Every process, file, directory, and network port has an SELinux security context. This context is a string composed of four parts: `User:Role:Type:Level`.

For Kubernetes, the most critical part is the `Type`. When container runtimes (like CRI-O or containerd on RHEL) create a container, they automatically assign it a generic SELinux type, usually `container_t`. They also assign a unique Multi-Category Security (MCS) label to the Level field, such as `s0:c123,c456`.

When the container attempts to read a file on a mounted host volume, SELinux checks the policy: Is a process with type `container_t` and MCS label `c123,c456` allowed to read a file with type `container_file_t` and MCS label `c123,c456`? If the labels do not match exactly, the kernel denies access, preventing container breakout and cross-container interference.

### Configuring SELinux in Pods

You can explicitly set SELinux labels in a pod's security context. This is often required when you are mounting custom host directories that have specific SELinux types that you want a specific pod to access.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: selinux-custom-pod
spec:
  securityContext:
    seLinuxOptions:
      level: "s0:c99,c100"
  containers:
  - name: worker
    image: busybox
    command: ["sleep", "3600"]
    securityContext:
      seLinuxOptions:
        type: "container_t"
        user: "system_u"
        role: "system_r"
```

If you mount a volume and the pod receives permission denied errors, you often need to instruct Kubernetes to automatically relabel the volume to match the pod's SELinux context. You do this by appending `:z` (shared among pods) or `:Z` (private to this pod) to the volume mount path in older docker syntax, though in native Kubernetes manifests, the Kubelet handles volume relabeling automatically based on the pod's SELinux context if the storage provisioner supports it.

## Deconstructing Root with Capabilities

Historically, the Linux kernel divided privileges into two categories: privileged (user ID 0, root) and unprivileged (everyone else). This binary model meant that if a web server needed to bind to port 80 (a privileged port), it had to run as root, granting it the power to do absolutely anything else on the system.

Linux Capabilities solved this by breaking down the power of "root" into dozens of distinct, granular privileges.

```text
┌─────────────────────────────────────────────────────────────┐
│              LINUX CAPABILITIES                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PURPOSE:                                                  │
│  • Break down root privileges into discrete units          │
│  • Grant specific privileges without full root             │
│  • Reduce privilege if container is compromised            │
│                                                             │
│  DEFAULT CAPABILITIES (container runtime):                 │
│  • CHOWN, DAC_OVERRIDE, FSETID, FOWNER                    │
│  • MKNOD, NET_RAW, SETGID, SETUID                         │
│  • SETFCAP, SETPCAP, NET_BIND_SERVICE                     │
│  • SYS_CHROOT, KILL, AUDIT_WRITE                          │
│                                                             │
│  DANGEROUS CAPABILITIES:                                   │
│  • CAP_SYS_ADMIN - Near-root privileges                   │
│  • CAP_NET_ADMIN - Network configuration                  │
│  • CAP_SYS_PTRACE - Debug any process                     │
│  • CAP_DAC_READ_SEARCH - Bypass read permissions          │
│                                                             │
│  BEST PRACTICE:                                            │
│  Drop all, add only what's needed                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Container runtimes do not grant full root to containers by default. They grant a default bounding set of about fourteen capabilities. While this is better than full root, the default set still includes highly dangerous capabilities like `CAP_NET_RAW` (allows crafting raw packets, useful for ARP spoofing and DNS poisoning) and `CAP_DAC_OVERRIDE` (allows bypassing file read/write permission checks).

The absolute best practice for runtime security is to drop all capabilities and explicitly add back only the exact ones the application requires.

### Managing Capabilities in Kubernetes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: capability-tuned-pod
spec:
  containers:
  - name: application
    image: my-golang-service:1.0
    securityContext:
      capabilities:
        drop:
          - ALL
        add:
          - NET_BIND_SERVICE
```

In the example above, the container starts completely unprivileged regarding kernel capabilities, except that it is permitted to bind to a network port below 1024. If an attacker compromises this container, they cannot use raw sockets, they cannot change file ownership, and they cannot trace other processes. 

> **Pause and predict**: You drop `ALL` capabilities on a container running `tcpdump` for network troubleshooting. The container immediately crashes on startup. Which specific capability must you add back for `tcpdump` to function, and why does dropping it break the application?

## Dynamic Enforcement with Policy Engines

Seccomp, AppArmor, and Capabilities are enforced by the node's kernel. However, managing these across hundreds of pods manually is impossible and prone to human error. You need a way to ensure that *no pod can ever be scheduled* unless it adheres to your security baseline.

This is where Kubernetes Admission Controllers and Policy Engines come in. They sit at Layer 4 of our security stack. When the API server receives a request to create a pod, it pauses and sends that request to a Mutating Webhook, and then to a Validating Webhook.

### OPA Gatekeeper

Open Policy Agent (OPA) Gatekeeper is a mature, widely adopted validating admission controller.

```text
┌─────────────────────────────────────────────────────────────┐
│              OPA GATEKEEPER                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  WHAT IT IS:                                               │
│  • Policy engine for Kubernetes                            │
│  • Admission controller                                    │
│  • Uses Rego language for policies                         │
│                                                             │
│  USE CASES:                                                │
│  • Require labels on resources                             │
│  • Block privileged containers                             │
│  • Enforce resource limits                                 │
│  • Restrict registries                                     │
│  • Custom organizational policies                          │
│                                                             │
│  COMPONENTS:                                               │
│  ├── ConstraintTemplate - Define policy type              │
│  ├── Constraint - Apply policy with parameters            │
│  └── Gatekeeper controller - Enforce policies             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Gatekeeper uses a purpose-built query language called Rego. Rego is incredibly powerful and can evaluate complex logic against any JSON structure, but it has a steep learning curve. Gatekeeper operates using a two-tiered model:

1. **ConstraintTemplate**: Contains the actual Rego code logic (the "how").
2. **Constraint**: The Kubernetes Custom Resource that instantiates the template with specific parameters (the "what" and "where").

For example, a ConstraintTemplate might contain the complex logic to check if a capability is present in the `securityContext`. The Constraint would say, "Apply the capability check template to all Pods in the 'production' namespace, and reject if 'CAP_SYS_ADMIN' is found."

### Kyverno

Kyverno is a policy engine designed specifically for Kubernetes, avoiding the need to learn a new language.

```text
┌─────────────────────────────────────────────────────────────┐
│              KYVERNO                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  WHAT IT IS:                                               │
│  • Kubernetes-native policy engine                         │
│  • No new language (uses YAML)                            │
│  • Admission controller                                    │
│                                                             │
│  POLICY TYPES:                                             │
│  ├── Validate - Check and reject                          │
│  ├── Mutate - Automatically modify                        │
│  ├── Generate - Create new resources                      │
│  └── Verify Images - Signature verification               │
│                                                             │
│  ADVANTAGES:                                               │
│  • Familiar YAML syntax                                   │
│  • Kubernetes-native                                      │
│  • Easy to get started                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Because Kyverno policies are written in YAML, they are highly accessible to platform engineers already accustomed to Kubernetes manifests. Kyverno can validate, but it excels at mutating resources on the fly.

Here is a Kyverno ClusterPolicy that prevents any pod from running as the root user:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-root-user
spec:
  validationFailureAction: Enforce
  background: true
  rules:
  - name: validate-runAsNonRoot
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Running as root is not allowed. Set runAsNonRoot to true."
      pattern:
        spec:
          securityContext:
            runAsNonRoot: true
          containers:
          - =(securityContext):
              =(runAsNonRoot): true
```

If a developer attempts to `kubectl apply` a pod that omits `runAsNonRoot: true`, the API server will reject the request, displaying the message defined in the policy directly to the developer's terminal. This creates an immediate feedback loop, shifting security left.

## The Ultimate Isolation: Sandboxed Runtimes

Even with strict capabilities, seccomp profiles, and MAC, all containers on a node ultimately share a single host kernel. The Linux kernel is massive, consisting of millions of lines of C code. Zero-day vulnerabilities in the kernel are discovered regularly. If an attacker exploits a kernel vulnerability from inside a container, they bypass all layer 2 and layer 3 security controls.

For multi-tenant environments where you are running untrusted code (like a SaaS platform executing customer scripts), shared-kernel isolation is insufficient. You need sandboxed runtimes.

```text
┌─────────────────────────────────────────────────────────────┐
│              SANDBOXED RUNTIME COMPARISON                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STANDARD RUNTIME (runc)                                   │
│  ├── Direct syscalls to host kernel                       │
│  ├── Fastest performance                                  │
│  ├── Kernel vulnerability = container escape              │
│  └── Use for: Trusted workloads                           │
│                                                             │
│  gVisor (runsc)                                           │
│  ├── User-space kernel (Sentry)                           │
│  ├── Intercepts and emulates syscalls                     │
│  ├── ~70% syscall coverage                                │
│  ├── Performance overhead (varies by workload)            │
│  └── Use for: Untrusted workloads, multi-tenant           │
│                                                             │
│  Kata Containers                                          │
│  ├── Lightweight VM per container                         │
│  ├── Separate kernel (not shared)                         │
│  ├── Hardware virtualization (KVM)                        │
│  ├── Higher overhead than gVisor                          │
│  └── Use for: Maximum isolation, compliance               │
│                                                             │
│  CHOOSING A RUNTIME:                                       │
│  Trusted internal workloads → runc                        │
│  Untrusted/multi-tenant → gVisor                         │
│  Maximum isolation → Kata                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### gVisor

Developed by Google, gVisor introduces an application kernel called the "Sentry" written in Go. The Sentry runs in user space. When an application in a gVisor container makes a system call, it does not go to the host Linux kernel. Instead, the Sentry intercepts the call, emulates the required behavior, and fulfills the request safely. Because the Sentry is written in a memory-safe language and acts as an intermediate buffer, kernel exploits executed by the containerized application attack the Sentry, not the host node. The compromise is contained.

### Kata Containers

Kata Containers takes a different approach. Instead of emulating the kernel, it uses hardware virtualization technologies (like KVM) to wrap every single container (or pod) in its own lightweight micro-virtual machine. Each Kata container has its own actual Linux kernel. If an attacker breaks out of the container via a kernel exploit, they only compromise their own dedicated, isolated VM kernel, not the underlying worker node.

### Implementing RuntimeClasses

You apply sandboxed runtimes dynamically by defining a `RuntimeClass` and referencing it in the Pod specification.

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
# The handler matches the runtime configured in containerd/CRI-O on the node
handler: runsc 
---
apiVersion: v1
kind: Pod
metadata:
  name: untrusted-customer-script
spec:
  runtimeClassName: gvisor
  containers:
  - name: runner
    image: python:3.11-alpine
```

## Security Checklist & Summary

To establish a comprehensive runtime security posture, administrators must implement controls iteratively across all levels of the stack.

```text
┌─────────────────────────────────────────────────────────────┐
│              RUNTIME SECURITY CHECKLIST                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SYSTEM CALL FILTERING                                     │
│  ☐ Enable seccomp (RuntimeDefault minimum)                 │
│  ☐ Custom profiles for sensitive workloads                 │
│  ☐ Test profiles don't break applications                  │
│                                                             │
│  MANDATORY ACCESS CONTROL                                  │
│  ☐ AppArmor or SELinux enabled on nodes                   │
│  ☐ Profiles applied to pods                                │
│  ☐ Start in complain mode, then enforce                    │
│                                                             │
│  CAPABILITIES                                              │
│  ☐ Drop all capabilities by default                        │
│  ☐ Add back only what's needed                             │
│  ☐ Never add CAP_SYS_ADMIN                                 │
│                                                             │
│  RUNTIME SELECTION                                         │
│  ☐ Consider sandboxed runtime for untrusted workloads      │
│  ☐ Define RuntimeClasses for different isolation levels    │
│                                                             │
│  POLICY ENFORCEMENT                                        │
│  ☐ Deploy policy engine (Kyverno/OPA)                     │
│  ☐ Enforce Pod Security Standards                          │
│  ☐ Block privileged/host namespace access                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Technology | Purpose | Key Benefit |
|-------|-----------|---------|-------------|
| **Syscall Filter** | Seccomp | Block dangerous system calls | Shrinks kernel attack surface dynamically |
| **MAC** | AppArmor/SELinux | File, network, capability restrictions | Overrides root user file access privileges |
| **Capabilities** | Linux | Granular privilege control | Prevents privilege escalation and system modification |
| **Sandboxing** | gVisor/Kata | Kernel isolation | Defends against host kernel zero-day exploits |
| **Policy** | Kyverno/OPA | Admission enforcement | Guarantees compliance before workloads run |

---

## Did You Know?

- **The Linux kernel has over 330 system calls**, yet comprehensive profiling shows that typical microservices require fewer than 50. Dropping the unneeded syscalls eliminates vast amounts of attack surface.
- **gVisor implements its own network stack called Netstack**, written entirely in Go. This means that a network-based exploit targeting a vulnerability in the Linux kernel's TCP/IP stack will completely fail against a gVisor container.
- **AppArmor and SELinux are mutually exclusive** at the kernel level. A Linux distribution compiles its kernel to support one or the other as its primary security module. You cannot run both simultaneously on the same host.
- **RuntimeDefault seccomp became the default in Kubernetes version 1.27**. Prior to this, millions of pods in production environments ran with zero system call filtering by default, relying entirely on capability drops and namespaces for protection.

---

## Common Mistakes

| Mistake | Why It Hurts | Solution |
|---------|--------------|----------|
| **Leaving Pods Unconfined** | Without seccomp filtering, a compromised container can invoke dangerous syscalls like `kexec_load` or `ptrace` to attack the node. | Ensure `seccompProfile: type: RuntimeDefault` is applied via Pod Security Admission or policy engines. |
| **Retaining Default Capabilities** | Container runtimes leave capabilities like `CAP_NET_RAW` enabled by default, allowing attackers to perform network spoofing attacks. | Explicitly configure `drop: ["ALL"]` in the security context, adding back only specific requirements. |
| **Ignoring MAC Profiles** | Discretionary Access Control (file permissions) is useless once an attacker escalates to the root user within a container. | Apply AppArmor or SELinux profiles to enforce constraints that even the root user cannot bypass. |
| **Using One Runtime for Everything** | Running highly trusted infrastructure services and completely untrusted third-party code on the exact same kernel architecture invites catastrophic lateral movement. | Implement `RuntimeClass` and utilize gVisor or Kata for untrusted workloads. |
| **Enforcing Policies Without Testing** | Hard-enforcing strict seccomp or AppArmor profiles immediately in production will inevitably break legitimate application behaviors causing outages. | Deploy policies in "audit" or "complain" mode first, monitor logs for violations, tune the policy, and then enforce. |
| **Relying Solely on Namespaces** | Assuming namespaces provide security isolation. Namespaces only provide visibility isolation; they do not restrict access to the shared kernel. | Layer namespaces with cgroups, capabilities, seccomp, and MAC for true defense-in-depth. |

---

## Quiz

<details>
<summary>1. A developer complains that their application, which requires the ability to adjust system time for synchronization, is failing with permission errors in production. The cluster enforces strict capability drops. Which capability must be added back, and why is this generally considered a poor architectural pattern for a container?</summary>

The developer requires `CAP_SYS_TIME`. Adding this capability allows the container to alter the clock of the host worker node, because containers share the underlying kernel. This is a poor architectural pattern because if a container changes the node's time, it affects all other pods running on that node, potentially breaking TLS certificate validation, logging timestamps, and authentication tokens for other applications. Time synchronization should be handled by the worker node's operating system (e.g., via chrony or ntpd), not by individual containerized workloads.
</details>

<details>
<summary>2. You manage a Kubernetes cluster on RHEL worker nodes. You attempt to apply a workload manifest that includes an AppArmor annotation restricting access to `/etc/`. The pod schedules successfully, but upon inspection, the container can still read sensitive files in `/etc/`. What is the fundamental architecture issue causing this failure?</summary>

The fundamental issue is that RHEL (Red Hat Enterprise Linux) uses SELinux for Mandatory Access Control, not AppArmor. AppArmor and SELinux are mutually exclusive Linux Security Modules. When you apply an AppArmor annotation to a pod scheduled on an SELinux-backed node, the container runtime simply ignores the annotation because the underlying kernel has no AppArmor module loaded to enforce it. To achieve the restriction on RHEL, you must utilize SELinux contexts and labeling, configuring the `seLinuxOptions` within the pod's security context.
</details>

<details>
<summary>3. A legacy application is containerized and deployed to a cluster enforcing the `RuntimeDefault` seccomp profile. The application immediately crashes. Debugging reveals the application relies heavily on executing the `unshare` syscall to create customized execution environments. You must make the application work without completely disabling seccomp. Outline your strategy.</summary>

You cannot use `RuntimeDefault` because it explicitly blocks the `unshare` syscall to prevent namespace manipulation escapes. To resolve this securely, you must author a custom seccomp profile. You start by copying the standard `RuntimeDefault` JSON profile provided by Docker/containerd. You then modify this custom profile to explicitly add `unshare` to the `SCMP_ACT_ALLOW` array. Save this file to the node's seccomp directory (e.g., `/var/lib/kubelet/seccomp/legacy-app.json`). Finally, modify the pod manifest to utilize `seccompProfile: type: Localhost` and specify the path to your new custom profile. This grants the application the exact syscall it needs while maintaining protection against hundreds of other dangerous syscalls.
</details>

<details>
<summary>4. Your organization runs a multi-tenant CI/CD platform. Customers submit arbitrary shell scripts that execute within isolated pods. You currently use runc with strict capabilities dropped and `RuntimeDefault` seccomp. A security researcher discovers a new kernel vulnerability (like Dirty Pipe) that allows local privilege escalation. Are your customer pods secure from exploiting this vulnerability to escape? Why or why not?</summary>

No, the customer pods are not secure from this specific threat. Because you are using `runc`, all customer containers share the underlying worker node's Linux kernel. Kernel zero-day vulnerabilities like Dirty Pipe operate at a level below seccomp and capabilities—they exploit flaws in how the kernel itself processes data. If a customer script executes the exploit, it compromises the shared kernel, leading to container escape and potential node takeover. To secure arbitrary, untrusted code execution, you must transition to a sandboxed runtime like gVisor or Kata Containers, which provide an intermediate application kernel or a dedicated VM kernel, isolating the host from direct exploitation.
</details>

<details>
<summary>5. You have implemented Kyverno to enforce a policy that prevents containers from running with the `privileged: true` flag. You also have OPA Gatekeeper installed, and a colleague suggests writing a Rego policy to do the exact same thing to ensure "defense in depth." Is this a recommended approach? Justify your answer.</summary>

While defense in depth is a core security principle, duplicating identical validation logic across two separate admission controllers is an anti-pattern. It introduces unnecessary operational complexity, increases API server latency due to multiple webhook calls, and creates a nightmare for debugging when workloads are rejected. If Kyverno is already successfully enforcing the policy, adding Gatekeeper to check the exact same field provides marginal resilience at a high operational cost. Best practice dictates selecting one primary policy engine for a specific domain (e.g., Kyverno for pod security, Gatekeeper for custom organizational labeling) rather than overlapping their rulesets identically.
</details>

<details>
<summary>6. An attacker gains remote code execution in a web container running with `runAsNonRoot: true`. They discover a local privilege escalation exploit binary left behind by a developer. However, when they attempt to run the binary, the kernel blocks the execution and denies the privilege escalation, even though the file has the SetUID bit set. What specific Kubernetes security context setting prevented this attack?</summary>

The attack was prevented by the `allowPrivilegeEscalation: false` setting in the container's security context. This setting directly configures the `no_new_privs` bit in the Linux kernel for the container process. When this bit is set, the kernel guarantees that the process and any of its children can never gain more privileges than they currently possess, regardless of file permissions or SetUID/SetGID bits on executables. The exploit binary relies on escalating privileges via execution, but the kernel categorically denies the transition, neutralizing the exploit entirely.
</details>

---

## Hands-On Exercise: Engineering a Hardened Security Context

**Scenario**: You are tasked with migrating a critical backend API service to a production Kubernetes cluster. The service is written in Go, listens on port 8080, reads configuration from a mounted volume, writes temporary processing data, but otherwise requires no special system access.

**Your objective**: Construct the YAML manifest for this pod implementing the strictest possible runtime security controls based on the principle of least privilege.

**Requirements Checklist:**
- [ ] The application must run as a non-root user (User ID 10001).
- [ ] The application must be explicitly prevented from escalating privileges via SetUID binaries.
- [ ] The entire root filesystem must be mounted as read-only to prevent tampering.
- [ ] A writable temporary directory must be provided at `/tmp/workdir`.
- [ ] All default Linux capabilities must be dropped.
- [ ] Only the specific capability required to bind to network ports (if it were binding to a port under 1024, though it uses 8080) should be considered, but since it's 8080, drop absolutely everything.
- [ ] The default container runtime syscall filter must be explicitly applied.
- [ ] The pod must be prevented from accessing the host's process, network, and IPC namespaces.

**Task 1:** Draft the pod structure and specify the namespace isolation parameters to ensure the pod cannot view host resources.

**Task 2:** Configure the Pod-level `securityContext` to handle user identification and system call filtering.

**Task 3:** Configure the Container-level `securityContext` to handle capabilities, filesystem permissions, and privilege escalation controls.

**Task 4:** Assemble the complete manifest, adding the necessary volume mounts to satisfy the read-only filesystem requirement while allowing temporary writes.

<details>
<summary>View the Solution and Explanation</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hardened-api-service
  labels:
    app: api-backend
spec:
  # Task 1: Prevent host namespace access
  hostNetwork: false
  hostPID: false
  hostIPC: false

  # Task 2: Pod-level security context
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 10001
    # Apply standard syscall filtering
    seccompProfile:
      type: RuntimeDefault

  containers:
  - name: api-service
    image: my-company/backend-api:v2.4.1
    ports:
    - containerPort: 8080

    # Task 3: Container-level security context
    securityContext:
      # Prevent privilege escalation (no_new_privs)
      allowPrivilegeEscalation: false
      # Ensure container is not privileged
      privileged: false
      
      # Enforce immutability
      readOnlyRootFilesystem: true
      
      # Drop all capabilities. Since the app listens on 8080 
      # (an unprivileged port > 1024), we do not need NET_BIND_SERVICE.
      capabilities:
        drop:
          - ALL

    # Task 4: Provide explicit writable areas
    volumeMounts:
    - name: tmp-workdir
      mountPath: /tmp/workdir

  volumes:
  - name: tmp-workdir
    emptyDir: {}
```

**Why this configuration is highly secure:**
If an attacker compromises the API service via a vulnerability in the Go application code:
1. They are trapped as user 10001. They are not root.
2. Even if they find a vulnerability that usually allows privilege escalation, `allowPrivilegeEscalation: false` instructs the kernel to block it.
3. They cannot download malware, alter configurations, or install rootkits because `readOnlyRootFilesystem: true` makes the entire drive immutable. They can only write to the temporary `/tmp/workdir`, which is ephemeral.
4. They cannot use network spoofing, alter system times, or trace processes because every single Linux capability has been dropped.
5. They cannot execute advanced kernel exploits using obscure system calls because the `RuntimeDefault` seccomp profile blocks them.
6. They cannot see or interact with other processes running on the host node because `hostPID` and `hostIPC` are explicitly false.

This creates a virtually inescapable sandbox using native Kubernetes primitives.
</details>

---

## Next Module

[Module 5.4: Security Tooling](../module-5.4-security-tooling/) - Now that you understand the low-level primitives of runtime security, discover the ecosystem of specialized tooling—like Falco and Trivy—designed to automate the observation and enforcement of these exact mechanisms at scale.