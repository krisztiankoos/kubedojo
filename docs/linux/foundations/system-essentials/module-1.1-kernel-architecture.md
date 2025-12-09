# Module 1.1: Kernel & Architecture

> **Linux Foundations** | Complexity: `[MEDIUM]` | Time: 25-30 min

## Prerequisites

Before starting this module:
- **Required**: Basic familiarity with using a terminal
- **Helpful**: Have a Linux system available (VM, WSL, or native)

---

## Why This Module Matters

Every container you run, every Kubernetes pod you deploy, every Linux server you manage—they all depend on **one piece of software**: the Linux kernel.

Understanding the kernel isn't just academic. It's practical:

- **Container security** depends on kernel isolation
- **Performance tuning** requires understanding kernel behavior
- **Troubleshooting** often traces back to kernel-level issues
- **Kubernetes node problems** are frequently kernel problems

When someone says "containers share the host kernel," do you really understand what that means? By the end of this module, you will.

---

## Did You Know?

- **The Linux kernel has over 30 million lines of code**, making it one of the largest open-source projects ever. Yet it boots in seconds and runs on everything from Raspberry Pis to supercomputers.

- **Linus Torvalds wrote the first Linux kernel in 1991** as a hobby project. His famous post to a newsgroup began: "I'm doing a (free) operating system (just a hobby, won't be big and professional like gnu)."

- **Over 95% of the world's top supercomputers run Linux**. All 500 of the TOP500 supercomputers use Linux as their operating system.

- **The kernel is re-entrant**, meaning multiple processes can be executing kernel code simultaneously. This is essential for multicore systems and is one reason Linux scales so well.

---

## What Is the Kernel?

The **kernel** is the core of the operating system. It's the software that:
- Talks directly to hardware
- Manages memory
- Schedules processes
- Provides isolation between programs
- Handles I/O operations

Think of it as the **supreme manager** of your computer. Every program runs with the kernel's permission and under its supervision.

```
┌─────────────────────────────────────────────────────────┐
│                    User Applications                     │
│         (bash, nginx, kubectl, your programs)            │
├─────────────────────────────────────────────────────────┤
│                    System Libraries                      │
│                (glibc, libssl, libcurl)                  │
├─────────────────────────────────────────────────────────┤
│                      System Calls                        │
│            (the interface to the kernel)                 │
├─────────────────────────────────────────────────────────┤
│                     LINUX KERNEL                         │
│   ┌──────────┬──────────┬──────────┬──────────────┐     │
│   │ Process  │  Memory  │   File   │   Network    │     │
│   │ Scheduler│ Manager  │  System  │    Stack     │     │
│   └──────────┴──────────┴──────────┴──────────────┘     │
│   ┌──────────────────────────────────────────────┐      │
│   │           Device Drivers                     │      │
│   └──────────────────────────────────────────────┘      │
├─────────────────────────────────────────────────────────┤
│                       HARDWARE                           │
│              (CPU, RAM, Disk, Network)                   │
└─────────────────────────────────────────────────────────┘
```

---

## Kernel Space vs User Space

This is the most important concept in this module.

### Two Worlds

Linux divides memory into two distinct spaces:

| Kernel Space | User Space |
|-------------|------------|
| Protected memory area | Regular memory area |
| Full hardware access | No direct hardware access |
| Runs with elevated privileges | Runs with restricted privileges |
| Kernel and drivers live here | Applications live here |
| Crash = entire system crash | Crash = just that application |

### Why the Separation?

**Protection.** If any program could access hardware directly, a bug in Firefox could corrupt your disk. A malicious program could read any process's memory.

The separation ensures:
- Programs can't interfere with each other
- Programs can't crash the system
- Programs can't access unauthorized resources

### The CPU Enforces This

Modern CPUs have **privilege rings** (x86) or **exception levels** (ARM):

```
┌─────────────────────────────────────────┐
│              Ring 3 (User)              │  ← Applications run here
├─────────────────────────────────────────┤
│              Ring 2 (unused)            │
├─────────────────────────────────────────┤
│              Ring 1 (unused)            │
├─────────────────────────────────────────┤
│            Ring 0 (Kernel)              │  ← Kernel runs here
└─────────────────────────────────────────┘
```

Linux uses only Ring 0 (kernel) and Ring 3 (user). When a process tries to execute a privileged instruction from Ring 3, the CPU generates an exception.

---

## System Calls: The Bridge

If user space can't access hardware, how does anything work?

**System calls** (syscalls) are the answer. They're the **only** way for user programs to request kernel services.

### Common System Calls

| Category | System Calls | Purpose |
|----------|-------------|---------|
| Process | fork, exec, exit, wait | Create and manage processes |
| File | open, read, write, close | File operations |
| Network | socket, bind, connect, send | Network operations |
| Memory | mmap, brk, mprotect | Memory management |
| System | ioctl, sysinfo, uname | System information |

### How a System Call Works

```
User Space                         Kernel Space
    │                                   │
    │  1. Program calls read()          │
    │  ─────────────────────────────►   │
    │                                   │
    │  2. Library prepares syscall      │
    │     (put args in registers)       │
    │                                   │
    │  3. Execute SYSCALL instruction   │
    │  ══════════════════════════════►  │ ← Mode switch!
    │                                   │
    │                    4. Kernel validates args
    │                    5. Kernel reads from disk
    │                    6. Kernel copies data to user buffer
    │                                   │
    │  ◄══════════════════════════════  │ ← Mode switch back
    │  7. Return to user space          │
    │                                   │
```

### Try This: Count System Calls

```bash
# Count system calls when running ls
strace -c ls /tmp

# Output shows syscall count and time
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 25.00    0.000050           4        12           openat
 20.00    0.000040           3        14           close
 15.00    0.000030           2        13           fstat
...
```

Every `openat`, `read`, `write`, and `close` is a journey from user space to kernel space and back.

---

## Kernel Modules

The Linux kernel is **modular**. Not everything is compiled in—some functionality is loaded on demand.

### Why Modules?

- **Flexibility**: Load only what you need
- **Memory efficiency**: Don't waste RAM on unused drivers
- **Hot-plugging**: Load drivers when devices connect
- **Development**: Test new code without rebooting

### Managing Modules

```bash
# List loaded modules
lsmod

# Example output:
# Module                  Size  Used by
# overlay               151552  0
# br_netfilter           32768  0
# bridge                311296  1 br_netfilter
# nf_conntrack          176128  1 br_netfilter

# Get info about a module
modinfo overlay

# Load a module (requires root)
sudo modprobe br_netfilter

# Remove a module
sudo modprobe -r br_netfilter

# Show module dependencies
modprobe --show-depends overlay
```

### Kubernetes-Relevant Modules

| Module | Purpose | Why K8s Needs It |
|--------|---------|-----------------|
| `overlay` | OverlayFS support | Container image layers |
| `br_netfilter` | Bridge netfilter | Network policies, kube-proxy |
| `ip_vs` | IPVS load balancing | kube-proxy IPVS mode |
| `nf_conntrack` | Connection tracking | Service routing |

If these modules aren't loaded, Kubernetes features won't work:

```bash
# Check if required modules are loaded
for mod in overlay br_netfilter ip_vs nf_conntrack; do
    lsmod | grep -q "^$mod" && echo "$mod: loaded" || echo "$mod: NOT loaded"
done
```

---

## The Kernel and Containers

Now for the crucial insight: **containers share the host kernel**.

### What This Means

```
┌─────────────────────────────────────────────────────────────┐
│                         HOST SYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│  Container A        Container B        Container C          │
│  ┌───────────┐     ┌───────────┐      ┌───────────┐        │
│  │ App + Libs│     │ App + Libs│      │ App + Libs│        │
│  │ (Alpine)  │     │ (Ubuntu)  │      │ (RHEL)    │        │
│  └───────────┘     └───────────┘      └───────────┘        │
├─────────────────────────────────────────────────────────────┤
│                     SHARED HOST KERNEL                       │
│                    (e.g., Linux 5.15)                        │
├─────────────────────────────────────────────────────────────┤
│                         HARDWARE                             │
└─────────────────────────────────────────────────────────────┘
```

Each container has its own filesystem and libraries, but they all use **the same kernel**.

### Implications

| Aspect | Implication |
|--------|-------------|
| **Performance** | No kernel overhead (unlike VMs) |
| **Security** | Kernel vulnerability affects ALL containers |
| **Compatibility** | Container must be compatible with host kernel |
| **Features** | Container can only use host kernel's capabilities |

### Try This: Same Kernel, Different "OS"

```bash
# On your host
uname -r  # Shows: 5.15.0-generic (example)

# Inside an Alpine container
docker run --rm alpine uname -r  # Shows: 5.15.0-generic (SAME!)

# Inside an Ubuntu container
docker run --rm ubuntu uname -r  # Shows: 5.15.0-generic (SAME!)
```

The "OS" in container images is just **userspace tools and libraries**. The kernel is always from the host.

### Security Implications

A kernel exploit affects EVERYTHING:

```
Vulnerability in kernel 5.15
         │
         ├── Affects host system
         ├── Affects ALL containers on that host
         └── Affects ALL Kubernetes pods on that node
```

This is why:
- Kernel updates are critical
- Node isolation matters
- Some workloads need dedicated nodes
- gVisor/Kata Containers exist (they add kernel isolation)

---

## Kernel Versions and Compatibility

### Version Numbering

```bash
uname -r
# Output: 5.15.0-generic

# Breaking down: 5.15.0-generic
# 5      = Major version
# 15     = Minor version (features added)
# 0      = Patch level (bug fixes)
# generic = Distribution-specific suffix
```

### Checking Kernel Information

```bash
# Kernel version
uname -r

# All system information
uname -a

# Detailed kernel info
cat /proc/version

# Kernel boot parameters
cat /proc/cmdline
```

### Why Version Matters for Kubernetes

Different kernel versions have different features:

| Feature | Minimum Kernel | Used By |
|---------|---------------|---------|
| Namespaces | 2.6.24+ | Container isolation |
| cgroups v1 | 2.6.24+ | Resource limits |
| cgroups v2 | 4.5+ | Modern resource management |
| eBPF (basic) | 3.15+ | Cilium, Falco |
| eBPF (advanced) | 4.14+ | Full Cilium features |
| User namespaces | 3.8+ | Rootless containers |

```bash
# Check cgroup version
mount | grep cgroup
# cgroup2 on /sys/fs/cgroup type cgroup2 = v2
# cgroup on /sys/fs/cgroup type cgroup = v1
```

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Ignoring kernel updates | Security vulnerabilities | Regular kernel updates with testing |
| Wrong kernel modules | K8s features don't work | Check module requirements for your setup |
| Assuming container isolation is complete | Security breach affects all containers | Defense in depth, consider gVisor for untrusted workloads |
| Not checking kernel compatibility | Features don't work | Verify kernel version supports needed features |
| Modifying kernel params without understanding | System instability | Research sysctl changes thoroughly |

---

## Quiz

Test your understanding:

### Question 1
What prevents user applications from directly accessing hardware?

<details>
<summary>Show Answer</summary>

**CPU privilege levels (rings)**. The CPU runs the kernel in Ring 0 (privileged) and applications in Ring 3 (unprivileged). Attempts to execute privileged instructions from Ring 3 cause an exception.

</details>

### Question 2
Why do containers on the same host show the same kernel version?

<details>
<summary>Show Answer</summary>

**Containers share the host kernel**. Unlike VMs, containers don't have their own kernel. They only package userspace (libraries, tools, applications) and rely on the host's kernel for system calls.

</details>

### Question 3
What is a system call, and why is it necessary?

<details>
<summary>Show Answer</summary>

**A system call is a request from user space to the kernel for a privileged operation**. It's necessary because user applications can't directly access hardware or protected resources. System calls provide a controlled interface for operations like file I/O, network access, and process management.

</details>

### Question 4
Which kernel modules are commonly required for Kubernetes?

<details>
<summary>Show Answer</summary>

Common modules include:
- `overlay` - For container image layers (OverlayFS)
- `br_netfilter` - For network policies and kube-proxy
- `ip_vs` - For kube-proxy IPVS mode
- `nf_conntrack` - For connection tracking in services

</details>

### Question 5
What's the security implication of containers sharing the host kernel?

<details>
<summary>Show Answer</summary>

**A kernel vulnerability affects ALL containers and the host**. There's no isolation at the kernel level—if an attacker escapes to kernel space, they have access to everything. This is why kernel patching is critical and why some workloads require additional isolation (gVisor, Kata Containers, or dedicated nodes).

</details>

---

## Hands-On Exercise

### Exploring Kernel Space and User Space

**Objective**: Understand the boundary between kernel and user space through practical exploration.

**Environment**: Any Linux system (VM, WSL2, or native)

#### Part 1: Examine Kernel Information

```bash
# 1. Check your kernel version
uname -r
uname -a

# 2. See detailed kernel info
cat /proc/version

# 3. Check kernel boot parameters
cat /proc/cmdline
```

**Questions to answer:**
- What kernel version are you running?
- Was your kernel compiled with any special options?

#### Part 2: Explore Kernel Modules

```bash
# 1. List all loaded modules
lsmod | head -20

# 2. Count total modules
lsmod | wc -l

# 3. Find container-related modules
lsmod | grep -E 'overlay|bridge|netfilter|ip_vs'

# 4. Get info about a specific module
modinfo overlay 2>/dev/null || modinfo ext4
```

**Questions to answer:**
- How many modules are loaded?
- Which container-related modules are present?

#### Part 3: Trace System Calls

```bash
# 1. Trace system calls for a simple command
strace -c ls /tmp 2>&1 | head -20

# 2. Trace specific syscalls
strace -e openat cat /etc/hostname

# 3. Count syscalls for a more complex operation
strace -c curl -s https://example.com > /dev/null 2>&1 || \
  strace -c wget -q https://example.com -O /dev/null 2>&1
```

**Questions to answer:**
- Which system calls does `ls` use most frequently?
- How many times did the command cross the user/kernel boundary?

#### Part 4: Container Kernel Sharing (if Docker available)

```bash
# 1. Check host kernel
echo "Host kernel: $(uname -r)"

# 2. Check kernel inside containers
docker run --rm alpine uname -r
docker run --rm ubuntu uname -r
docker run --rm centos:7 uname -r 2>/dev/null || \
  docker run --rm amazonlinux uname -r
```

**Questions to answer:**
- Are the kernel versions the same?
- What does this prove about container architecture?

### Success Criteria

- [ ] Identified your kernel version and boot parameters
- [ ] Listed loaded kernel modules and found container-related ones
- [ ] Traced system calls and understood the user/kernel boundary
- [ ] (If Docker available) Demonstrated kernel sharing between containers

---

## Key Takeaways

1. **The kernel is the core** — It manages hardware, memory, processes, and provides isolation

2. **User space vs kernel space** — CPU-enforced separation protects the system from buggy or malicious programs

3. **System calls bridge the gap** — The only way for programs to request kernel services

4. **Modules provide flexibility** — Load features on demand, especially important for container and network functionality

5. **Containers share the host kernel** — Major performance benefit but significant security consideration

---

## What's Next?

In **Module 1.2: Processes & systemd**, you'll learn how the kernel manages processes—the foundation for understanding how containers are really just isolated processes.

---

## Further Reading

- [Linux Kernel Documentation](https://www.kernel.org/doc/html/latest/)
- [The Linux Programming Interface](https://man7.org/tlpi/) by Michael Kerrisk
- [Linux Insides](https://0xax.gitbooks.io/linux-insides/) — Deep dive into kernel internals
- [Container Security](https://www.oreilly.com/library/view/container-security/9781492056690/) by Liz Rice — Excellent coverage of kernel security features
