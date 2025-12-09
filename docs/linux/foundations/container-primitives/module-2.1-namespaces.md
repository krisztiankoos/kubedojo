# Module 2.1: Linux Namespaces

> **Linux Foundations** | Complexity: `[MEDIUM]` | Time: 30-35 min

## Prerequisites

Before starting this module:
- **Required**: [Module 1.1: Kernel & Architecture](../system-essentials/module-1.1-kernel-architecture.md)
- **Required**: [Module 1.2: Processes & systemd](../system-essentials/module-1.2-processes-systemd.md)
- **Helpful**: Basic understanding of networking concepts

---

## Why This Module Matters

Namespaces are the **foundation of container isolation**. When you run a Docker container or a Kubernetes pod, namespaces create the illusion of a separate system.

Understanding namespaces helps you:

- **Debug container networking** — Why can't my container reach the host?
- **Understand pod isolation** — How do containers in a pod share resources?
- **Troubleshoot PID conflicts** — Why does my container see only its own processes?
- **Implement security** — What isolation actually exists (and doesn't)?

When `kubectl exec` doesn't behave as expected, or containers can "see" each other when they shouldn't, you need to understand namespaces.

---

## Did You Know?

- **Namespaces predate Docker by years** — The first namespace (mount) was added to Linux in 2002. Docker (2013) just made them accessible through a friendly interface.

- **Kubernetes pods share namespaces** — Containers in the same pod share network and IPC namespaces by default. This is why they can communicate via localhost and share memory.

- **User namespaces enable rootless containers** — By mapping UID 0 inside the container to an unprivileged UID outside, you can run "root" processes without actual root privileges.

- **There are 8 namespace types** — Mount, UTS, IPC, PID, Network, User, Cgroup, and Time (added in Linux 5.6). Each isolates a different aspect of the system.

---

## What Are Namespaces?

A **namespace** wraps a global system resource in an abstraction that makes it appear to processes within the namespace that they have their own isolated instance.

```
┌────────────────────────────────────────────────────────────────┐
│                         HOST SYSTEM                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Global Resource: Network Stack              │   │
│  │         eth0 (192.168.1.100), routing tables            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│              ┌───────────────┴───────────────┐                 │
│              ▼                               ▼                 │
│  ┌──────────────────────┐     ┌──────────────────────┐        │
│  │  Network Namespace 1 │     │  Network Namespace 2 │        │
│  │  eth0 (10.0.0.1)     │     │  eth0 (10.0.0.2)     │        │
│  │  Container A         │     │  Container B         │        │
│  └──────────────────────┘     └──────────────────────┘        │
└────────────────────────────────────────────────────────────────┘
```

Each namespace type isolates a specific resource:

| Namespace | Isolates | Flag | Added |
|-----------|----------|------|-------|
| Mount (mnt) | Filesystem mount points | CLONE_NEWNS | 2002 |
| UTS | Hostname and domain | CLONE_NEWUTS | 2006 |
| IPC | Inter-process communication | CLONE_NEWIPC | 2006 |
| PID | Process IDs | CLONE_NEWPID | 2008 |
| Network (net) | Network stack | CLONE_NEWNET | 2009 |
| User | User and group IDs | CLONE_NEWUSER | 2013 |
| Cgroup | Cgroup root directory | CLONE_NEWCGROUP | 2016 |
| Time | System clocks | CLONE_NEWTIME | 2020 |

---

## Viewing Namespaces

Every process belongs to a set of namespaces:

```bash
# View your shell's namespaces
ls -la /proc/$$/ns/

# Output:
# lrwxrwxrwx 1 user user 0 Dec  1 10:00 cgroup -> 'cgroup:[4026531835]'
# lrwxrwxrwx 1 user user 0 Dec  1 10:00 ipc -> 'ipc:[4026531839]'
# lrwxrwxrwx 1 user user 0 Dec  1 10:00 mnt -> 'mnt:[4026531840]'
# lrwxrwxrwx 1 user user 0 Dec  1 10:00 net -> 'net:[4026531992]'
# lrwxrwxrwx 1 user user 0 Dec  1 10:00 pid -> 'pid:[4026531836]'
# lrwxrwxrwx 1 user user 0 Dec  1 10:00 user -> 'user:[4026531837]'
# lrwxrwxrwx 1 user user 0 Dec  1 10:00 uts -> 'uts:[4026531838]'
```

The numbers in brackets are inode numbers—unique identifiers for each namespace instance.

```bash
# Compare namespaces between processes
sudo ls -la /proc/1/ns/     # PID 1 (init)
sudo ls -la /proc/$$/ns/    # Your shell

# Use lsns for a summary
lsns
```

---

## PID Namespace

Makes processes see their own PID tree, with PID 1 as their init.

### Without PID Namespace

```
Host:
PID 1 (systemd) ─┬─ PID 100 (sshd)
                 ├─ PID 200 (containerd)
                 └─ PID 300 (your_app)  ← sees all PIDs
```

### With PID Namespace

```
Host:                              Container view:
PID 1 (systemd)                    PID 1 (your_app)  ← thinks it's PID 1!
  └─ PID 300 (your_app)            (can't see host processes)
```

### Try This: Create PID Namespace

```bash
# Run a shell in a new PID namespace
sudo unshare --pid --fork --mount-proc bash

# Inside the new namespace:
ps aux
# Only shows processes in this namespace

echo $$
# Shows 1 (or a low number) - you're PID 1 in this namespace!

# Exit
exit
```

### Why PID 1 Matters in Containers

In a PID namespace:
- Your process becomes PID 1
- PID 1 has special signal handling (SIGTERM ignored by default)
- PID 1 must reap zombie children
- If PID 1 dies, all processes in the namespace are killed

This is why containers use init systems like `tini` or `dumb-init`.

---

## Network Namespace

Creates an isolated network stack: interfaces, routing, firewall rules.

### What's Isolated

Each network namespace has its own:
- Network interfaces (eth0, lo, etc.)
- IP addresses
- Routing tables
- Firewall rules (iptables)
- /proc/net
- Port space (each namespace can have its own :80)

### Try This: Create Network Namespace

```bash
# Create a network namespace
sudo ip netns add test-ns

# List namespaces
ip netns list

# Run command in namespace
sudo ip netns exec test-ns ip addr
# Only shows loopback (down)

# Bring up loopback
sudo ip netns exec test-ns ip link set lo up

# Run a shell in the namespace
sudo ip netns exec test-ns bash

# Inside: no network connectivity to outside
ping 8.8.8.8  # Fails - no route

exit

# Clean up
sudo ip netns delete test-ns
```

### How Containers Get Network Access

```
┌─────────────────────────────────────────────────────────────────┐
│                          HOST                                    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      docker0 bridge                       │   │
│  │                       172.17.0.1                          │   │
│  └────────────────┬─────────────────────┬───────────────────┘   │
│                   │                     │                        │
│              veth123                veth456                      │
│                   │                     │                        │
│  ┌────────────────┼─────┐ ┌─────────────┼────────────────┐      │
│  │  Container A   │     │ │  Container B │               │      │
│  │           eth0─┘     │ │         eth0─┘               │      │
│  │         172.17.0.2   │ │       172.17.0.3             │      │
│  │  (network namespace) │ │    (network namespace)       │      │
│  └──────────────────────┘ └──────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

Virtual ethernet pairs (veth) connect container namespaces to host bridges.

---

## Mount Namespace

Isolates filesystem mount points—each namespace sees different mounts.

### What's Isolated

- Mount points
- What filesystems are visible
- Allows private /tmp, /proc, etc.

### Try This: Mount Namespace

```bash
# Create mount namespace with private /tmp
sudo unshare --mount bash

# Inside: create a private mount
mount -t tmpfs tmpfs /tmp
echo "secret" > /tmp/hidden.txt

# This /tmp is only visible in this namespace!
cat /tmp/hidden.txt

exit

# Back on host: /tmp/hidden.txt doesn't exist
cat /tmp/hidden.txt  # No such file
```

### Container Filesystem Isolation

```
Host filesystem:
/
├── etc/passwd  (host users)
├── var/        (host data)
└── ...

Container mount namespace:
/                     (overlay mount of image + container layer)
├── etc/passwd        (container users - different file!)
├── var/              (container data)
└── ...
```

---

## UTS Namespace

Isolates hostname and domain name.

```bash
# Create UTS namespace with different hostname
sudo unshare --uts bash

# Change hostname (only in this namespace)
hostname container-host
hostname
# Shows: container-host

exit

hostname
# Shows: original hostname (unchanged)
```

This is how containers have their own hostnames without affecting the host.

---

## User Namespace

Maps UIDs inside the namespace to different UIDs outside.

### Why User Namespaces Matter

```
Without user namespace:
Container UID 0 (root) = Host UID 0 (root)  ← DANGEROUS!

With user namespace:
Container UID 0 (root) → Host UID 100000 (unprivileged)
```

### Rootless Containers

```bash
# Check if your system supports user namespaces
cat /proc/sys/kernel/unprivileged_userns_clone
# 1 = enabled

# Podman uses user namespaces by default for rootless containers
podman run --rm alpine id
# uid=0(root) gid=0(root)  ← root INSIDE container
# but mapped to your UID on the host
```

### Mapping Example

```
/etc/subuid: user:100000:65536

Meaning: user "user" can use UIDs 100000-165535

Inside container:    Outside (host):
UID 0           →    UID 100000
UID 1           →    UID 100001
UID 1000        →    UID 101000
```

---

## IPC Namespace

Isolates inter-process communication: shared memory, semaphores, message queues.

### Why It Matters

Without IPC namespace isolation:
- Containers could access each other's shared memory
- A malicious container could interfere with others

```bash
# Create IPC namespace
sudo unshare --ipc bash

# List IPC objects
ipcs
# Empty - isolated from host IPC

exit

ipcs
# May show host IPC objects
```

---

## Kubernetes and Namespaces

### Pod Namespace Sharing

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-container
spec:
  containers:
  - name: web
    image: nginx
  - name: sidecar
    image: busybox
    command: ["sh", "-c", "while true; do wget -q -O- localhost; sleep 5; done"]
```

Both containers share:
- **Network namespace** — Can reach each other via localhost
- **IPC namespace** — Can use shared memory
- **UTS namespace** — Same hostname

Each container has its own:
- **PID namespace** (by default, can be shared)
- **Mount namespace** — Separate filesystems
- **User namespace** — Separate user mappings

### Sharing Host Namespaces

```yaml
apiVersion: v1
kind: Pod
spec:
  hostNetwork: true      # Use host network namespace
  hostPID: true          # Use host PID namespace
  hostIPC: true          # Use host IPC namespace
  containers:
  - name: debug
    image: busybox
```

**Warning**: This breaks isolation! Only use for debugging or system pods.

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Assuming complete isolation | Namespaces don't isolate everything (kernel, time) | Use additional security (seccomp, AppArmor) |
| Running as root without user namespace | Container escape = host root | Use rootless containers or user namespaces |
| hostNetwork without need | Breaks network isolation | Only use when truly necessary |
| Not understanding PID 1 | Signal handling issues, zombies | Use proper init (tini, dumb-init) |
| Shared mounts without intent | Data leaks between containers | Use proper volume configurations |

---

## Quiz

### Question 1
What happens when PID 1 in a PID namespace dies?

<details>
<summary>Show Answer</summary>

**All processes in that PID namespace are killed.** The kernel sends SIGKILL to all remaining processes when the init process (PID 1) of a PID namespace terminates. This is why containers stop when their main process exits.

</details>

### Question 2
How can two containers both listen on port 80?

<details>
<summary>Show Answer</summary>

**They're in different network namespaces.** Each network namespace has its own port space. Container A's port 80 is in namespace A, Container B's port 80 is in namespace B. The host maps these to different external ports.

</details>

### Question 3
Why do containers in a Kubernetes pod share localhost?

<details>
<summary>Show Answer</summary>

**They share the same network namespace.** Kubernetes creates one network namespace per pod. All containers in the pod join this shared namespace, so they:
- Share the same IP address
- Can communicate via localhost
- Share the same port space (can't both use :80)

</details>

### Question 4
What does `unshare --pid --fork` do?

<details>
<summary>Show Answer</summary>

Creates a new **PID namespace** for the child process:
- `--pid`: Create new PID namespace
- `--fork`: Fork before executing (required for PID namespace to work correctly)

The child process will be PID 1 in the new namespace.

</details>

### Question 5
Why are user namespaces important for security?

<details>
<summary>Show Answer</summary>

User namespaces allow **UID mapping**:
- Root (UID 0) inside container → Unprivileged UID outside
- Container escape no longer grants host root
- Enables rootless containers
- Reduces blast radius of container compromise

</details>

---

## Hands-On Exercise

### Exploring Namespaces

**Objective**: Create and explore different namespace types.

**Environment**: Linux system with root access

#### Part 1: View Current Namespaces

```bash
# 1. Your shell's namespaces
ls -la /proc/$$/ns/

# 2. Compare with PID 1
sudo ls -la /proc/1/ns/

# 3. List all namespaces on system
lsns

# 4. Find namespace types
lsns -t net
lsns -t pid
```

#### Part 2: PID Namespace

```bash
# 1. Create PID namespace
sudo unshare --pid --fork --mount-proc bash

# 2. Explore inside
ps aux
echo "My PID: $$"

# 3. Try to see host processes
ls /proc/  # Only see processes in this namespace

# 4. Exit
exit
```

#### Part 3: Network Namespace

```bash
# 1. Create namespace
sudo ip netns add myns

# 2. List it
ip netns list

# 3. Check network inside
sudo ip netns exec myns ip addr
# Only lo, and it's down

# 4. Bring up loopback
sudo ip netns exec myns ip link set lo up
sudo ip netns exec myns ip addr

# 5. Try to ping outside
sudo ip netns exec myns ping -c 1 8.8.8.8
# Fails - no connectivity

# 6. Clean up
sudo ip netns delete myns
```

#### Part 4: Mount Namespace

```bash
# 1. Create mount namespace
sudo unshare --mount bash

# 2. Create private mount
mkdir -p /tmp/ns-test
mount -t tmpfs tmpfs /tmp/ns-test
echo "namespace secret" > /tmp/ns-test/secret.txt

# 3. Verify it exists
cat /tmp/ns-test/secret.txt

# 4. Exit
exit

# 5. Check from host
cat /tmp/ns-test/secret.txt
# File not found - mount was namespace-private!
```

#### Part 5: UTS Namespace

```bash
# 1. Create UTS namespace
sudo unshare --uts bash

# 2. Change hostname
hostname my-container
hostname

# 3. Exit and check host
exit
hostname  # Unchanged!
```

### Success Criteria

- [ ] Listed namespaces for current process
- [ ] Created PID namespace and verified isolation
- [ ] Created network namespace and explored it
- [ ] Created mount namespace with private mount
- [ ] Changed hostname in isolated UTS namespace

---

## Key Takeaways

1. **Namespaces create isolated views** — Each type isolates a specific resource

2. **8 namespace types** — PID, Network, Mount, UTS, IPC, User, Cgroup, Time

3. **Containers = processes + namespaces** — That's the core abstraction

4. **Pod containers share namespaces** — Network and IPC by default

5. **User namespaces enable rootless** — UID mapping is key to secure containers

---

## What's Next?

In **Module 2.2: Control Groups (cgroups)**, you'll learn how Linux limits and accounts for resource usage—the enforcement behind Kubernetes resource requests and limits.

---

## Further Reading

- [Linux Namespaces man page](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [Namespaces in Operation (LWN series)](https://lwn.net/Articles/531114/)
- [Container Security by Liz Rice](https://www.oreilly.com/library/view/container-security/9781492056690/)
- [What Are Namespaces and cgroups (Red Hat)](https://www.redhat.com/sysadmin/cgroups-part-one)
