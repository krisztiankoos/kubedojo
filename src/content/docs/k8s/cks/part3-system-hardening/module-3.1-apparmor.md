---
title: "Module 3.1: AppArmor for Containers"
slug: k8s/cks/part3-system-hardening/module-3.1-apparmor
sidebar:
  order: 1
lab:
  id: cks-3.1-apparmor
  url: https://killercoda.com/kubedojo/scenario/cks-3.1-apparmor
  duration: "40 min"
  difficulty: advanced
  environment: kubernetes
---
> **Complexity**: `[MEDIUM]` - Linux security essential
>
> **Time to Complete**: 45-50 minutes
>
> **Prerequisites**: Linux basics, container runtime knowledge

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Create** AppArmor profiles that restrict container file access and network operations
2. **Deploy** pods with AppArmor profiles applied via security context annotations
3. **Debug** AppArmor denials by interpreting kernel audit logs
4. **Audit** running containers to verify correct AppArmor profile enforcement

---

## Why This Module Matters

AppArmor is a Linux security module that restricts what applications can do—which files they can access, which network operations they can perform, which capabilities they can use. When applied to containers, AppArmor adds a security layer beyond the container runtime.

CKS tests your ability to create AppArmor profiles and apply them to pods.

---

## What is AppArmor?

```
┌─────────────────────────────────────────────────────────────┐
│              APPARMOR OVERVIEW                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  AppArmor = Application Armor                              │
│  ─────────────────────────────────────────────────────────  │
│  • Mandatory Access Control (MAC) system                   │
│  • Restricts per-program capabilities                      │
│  • Default on Ubuntu, Debian                               │
│  • Alternative to SELinux (RHEL/CentOS)                   │
│                                                             │
│  How it works:                                             │
│                                                             │
│  ┌─────────────────┐     ┌─────────────────┐              │
│  │  Application    │────►│  System Call    │              │
│  │  (Container)    │     │                 │              │
│  └─────────────────┘     └────────┬────────┘              │
│                                   │                        │
│                                   ▼                        │
│                          ┌─────────────────┐              │
│                          │  AppArmor       │              │
│                          │  Profile Check  │              │
│                          └────────┬────────┘              │
│                                   │                        │
│                      ┌────────────┴────────────┐          │
│                      ▼                         ▼          │
│                 ┌─────────┐              ┌─────────┐      │
│                 │ ALLOWED │              │ DENIED  │      │
│                 └─────────┘              └─────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## AppArmor Modes

```
┌─────────────────────────────────────────────────────────────┐
│              APPARMOR PROFILE MODES                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Enforce Mode                                              │
│  └── Policy is enforced, violations are blocked AND logged │
│      aa-enforce /path/to/profile                           │
│                                                             │
│  Complain Mode                                             │
│  └── Policy violations are logged but NOT blocked          │
│      aa-complain /path/to/profile                          │
│      (Useful for testing new profiles)                     │
│                                                             │
│  Disabled/Unconfined                                       │
│  └── No restrictions applied                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Checking AppArmor Status

```bash
# Check if AppArmor is enabled
cat /sys/module/apparmor/parameters/enabled
# Output: Y (enabled) or N (disabled)

# Check AppArmor status
sudo aa-status

# Output example:
# apparmor module is loaded.
# 47 profiles are loaded.
# 47 profiles are in enforce mode.
#    /usr/bin/evince
#    /usr/sbin/cupsd
#    docker-default
# 0 profiles are in complain mode.
# 10 processes have profiles defined.

# List loaded profiles
sudo aa-status --profiles

# Check if container runtime supports AppArmor
docker info | grep -i apparmor
# Output: Security Options: apparmor
```

---

## Default Container Profile

```bash
# Docker/containerd use 'docker-default' profile
# This profile:
# - Denies mounting filesystems
# - Denies access to /proc/sys
# - Denies raw network access
# - Allows normal container operations

# Check default profile
cat /etc/apparmor.d/containers/docker-default 2>/dev/null || \
  cat /etc/apparmor.d/docker 2>/dev/null
```

---

> **Stop and think**: AppArmor's `complain` mode logs violations without blocking them, while `enforce` mode blocks and logs. If you're deploying a new profile to production for the first time, why is jumping straight to `enforce` mode risky? What workflow minimizes the chance of breaking your application?

## Creating Custom AppArmor Profiles

### Profile Location

```bash
# AppArmor profiles are stored in:
/etc/apparmor.d/

# For Kubernetes, create in:
/etc/apparmor.d/
# Profile must be loaded on each node where pod might run
```

### Profile Structure

```
#include <tunables/global>

profile my-container-profile flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  # File access rules
  /etc/passwd r,                    # Read /etc/passwd
  /var/log/myapp/** rw,            # Read/write to log directory
  /tmp/** rw,                       # Read/write to tmp

  # Network rules
  network inet tcp,                 # Allow TCP
  network inet udp,                 # Allow UDP

  # Capability rules
  capability net_bind_service,      # Allow binding to ports < 1024

  # Deny rules
  deny /etc/shadow r,               # Deny reading shadow
  deny /proc/sys/** w,              # Deny writing to /proc/sys
}
```

### Rule Syntax

```
┌─────────────────────────────────────────────────────────────┐
│              APPARMOR RULE SYNTAX                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  File Access:                                              │
│  ─────────────────────────────────────────────────────────  │
│  /path/to/file r,        # Read                            │
│  /path/to/file w,        # Write                           │
│  /path/to/file rw,       # Read and Write                  │
│  /path/to/file a,        # Append                          │
│  /path/to/file ix,       # Execute, inherit profile        │
│  /path/to/dir/ r,        # Read directory                  │
│  /path/to/dir/** rw,     # Recursive read/write            │
│                                                             │
│  Network:                                                  │
│  ─────────────────────────────────────────────────────────  │
│  network,                # Allow all networking            │
│  network inet,           # IPv4                            │
│  network inet6,          # IPv6                            │
│  network inet tcp,       # IPv4 TCP only                   │
│  network inet udp,       # IPv4 UDP only                   │
│                                                             │
│  Capabilities:                                             │
│  ─────────────────────────────────────────────────────────  │
│  capability dac_override,    # Bypass file permissions     │
│  capability net_admin,       # Network admin               │
│  capability sys_ptrace,      # Trace processes             │
│                                                             │
│  Deny:                                                     │
│  ─────────────────────────────────────────────────────────  │
│  deny /path/file w,      # Explicitly deny (logs)          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Creating a Profile for Kubernetes

### Step 1: Write the Profile

```bash
# Create profile on each node
sudo tee /etc/apparmor.d/k8s-deny-write << 'EOF'
#include <tunables/global>

profile k8s-deny-write flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  # Allow most read operations
  file,

  # Deny all write operations except /tmp
  deny /** w,
  /tmp/** rw,

  # Allow network
  network,
}
EOF
```

### Step 2: Load the Profile

```bash
# Parse and load the profile
sudo apparmor_parser -r /etc/apparmor.d/k8s-deny-write

# Verify it's loaded
sudo aa-status | grep k8s-deny-write

# To remove a profile
sudo apparmor_parser -R /etc/apparmor.d/k8s-deny-write
```

### Step 3: Apply to Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secured-pod
  annotations:
    # Format: container.apparmor.security.beta.kubernetes.io/<container-name>: <profile>
    container.apparmor.security.beta.kubernetes.io/app: localhost/k8s-deny-write
spec:
  containers:
  - name: app
    image: nginx
```

---

## AppArmor Profile Reference Values

```yaml
# Annotation format:
container.apparmor.security.beta.kubernetes.io/<container-name>: <profile-ref>

# Profile reference options:
# runtime/default    - Use container runtime's default profile
# localhost/<name>   - Use profile loaded on node with <name>
# unconfined        - No AppArmor restrictions (dangerous!)
```

---

> **What would happen if**: You create an AppArmor profile and load it on `node-1`, but not on `node-2`. Your pod has no nodeSelector. The pod starts successfully on `node-1`. Then the pod is rescheduled to `node-2` after a node drain. What happens?

## Common Profiles for Containers

### Deny Write to Root Filesystem

```
#include <tunables/global>

profile k8s-readonly flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  # Read everything
  /** r,

  # Write only to specific paths
  /tmp/** rw,
  /var/tmp/** rw,
  /run/** rw,

  # Deny write elsewhere
  deny /** w,

  network,
}
```

### Deny Network Access

```
#include <tunables/global>

profile k8s-deny-network flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  file,

  # Deny all network access
  deny network,
}
```

### Deny Sensitive File Access

```
#include <tunables/global>

profile k8s-deny-sensitive flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  file,
  network,

  # Deny access to sensitive files
  deny /etc/shadow r,
  deny /etc/gshadow r,
  deny /etc/sudoers r,
  deny /etc/sudoers.d/** r,
  deny /root/** rwx,
}
```

---

> **Pause and predict**: You apply an AppArmor profile that has `deny /etc/** w,` to a container running nginx. Nginx needs to write to `/etc/nginx/conf.d/` during startup for configuration templating. Will the container start successfully, or will it crash?

## Real Exam Scenarios

### Scenario 1: Apply Existing Profile

```bash
# Check if profile is loaded
sudo aa-status | grep my-profile

# Apply to pod
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  annotations:
    container.apparmor.security.beta.kubernetes.io/nginx: localhost/my-profile
spec:
  containers:
  - name: nginx
    image: nginx
EOF
```

### Scenario 2: Create and Apply Profile

```bash
# Create profile that denies write to /etc
sudo tee /etc/apparmor.d/k8s-deny-etc-write << 'EOF'
#include <tunables/global>

profile k8s-deny-etc-write flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  file,
  network,
  deny /etc/** w,
}
EOF

# Load profile
sudo apparmor_parser -r /etc/apparmor.d/k8s-deny-etc-write

# Apply to pod
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: secured-nginx
  annotations:
    container.apparmor.security.beta.kubernetes.io/nginx: localhost/k8s-deny-etc-write
spec:
  containers:
  - name: nginx
    image: nginx
EOF

# Verify
kubectl exec secured-nginx -- touch /etc/test
# Should fail due to AppArmor
```

### Scenario 3: Debug AppArmor Issues

```bash
# Check pod events
kubectl describe pod secured-pod | grep -i apparmor

# Check if profile is loaded on node
ssh node1 'sudo aa-status | grep k8s'

# Check audit logs for denials
sudo dmesg | grep -i apparmor | tail -10

# Or check audit log
sudo journalctl -k | grep -i apparmor
```

---

## Did You Know?

- **AppArmor profiles must be loaded on every node** where a pod might run. DaemonSets can help distribute profiles.

- **The 'flags=(attach_disconnected,mediate_deleted)' part** is essential for container profiles because containers may have disconnected paths and deleted files.

- **AppArmor is Ubuntu/Debian default**, while SELinux is RHEL/CentOS default. The CKS exam uses Ubuntu, so AppArmor is the focus.

- **You can generate profiles** using `aa-genprof` or `aa-logprof` which monitor application behavior and create profiles based on observed actions.

---

## Common Mistakes

| Mistake | Why It Hurts | Solution |
|---------|--------------|----------|
| Profile not loaded on node | Pod fails to schedule | Load on all nodes |
| Wrong annotation format | Profile not applied | Check exact annotation key |
| Missing abstractions | Profile too restrictive | Include base abstractions |
| Using 'unconfined' | No security | Use runtime/default minimum |
| Not testing in complain mode | Breaks application | Test with aa-complain first |

---

## Quiz

1. **During a CKS exam task, you're asked to apply an AppArmor profile called `k8s-restricted` to a container named `web` in a pod. You write the annotation as `container.apparmor.security.beta.kubernetes.io/nginx: localhost/k8s-restricted`. The pod starts but the profile isn't applied. What went wrong?**
   <details>
   <summary>Answer</summary>
   The container name in the annotation key must match the container name in the pod spec exactly. The annotation references `nginx` but the container is named `web`. The correct annotation is `container.apparmor.security.beta.kubernetes.io/web: localhost/k8s-restricted`. This is a common exam mistake because the annotation key embeds the container name, not the image name. Always verify with `kubectl describe pod` to check if the AppArmor profile is actually applied -- the events section will show whether the profile was loaded.
   </details>

2. **A Falco alert fires: "Sensitive file read: `/etc/shadow` was read by process `cat` in container `app-server`." Your team wants to prevent this using AppArmor. Write the minimal profile rules needed, and explain why you'd test in complain mode first.**
   <details>
   <summary>Answer</summary>
   Add `deny /etc/shadow r,` and `deny /etc/gshadow r,` rules to the AppArmor profile. Test in complain mode first (`aa-complain /etc/apparmor.d/<profile>`) because blocking file access can have unintended consequences -- some applications legitimately read `/etc/passwd` (which is near shadow in the rules) or other `/etc/` files. Complain mode logs what would be blocked without actually blocking, letting you verify the profile doesn't break the application. Once verified, switch to enforce mode with `aa-enforce /etc/apparmor.d/<profile>`. Load the profile on all nodes where the pod might run with `apparmor_parser -r`.
   </details>

3. **You deploy an AppArmor profile to all 5 worker nodes using a DaemonSet. The profile works on 4 nodes, but pods on `node-5` fail with "AppArmor profile not found." You verify the DaemonSet pod is running on `node-5`. What could cause this inconsistency?**
   <details>
   <summary>Answer</summary>
   The DaemonSet pod running doesn't guarantee the profile is loaded into the kernel's AppArmor module. Possible causes: (1) The DaemonSet's init script failed silently on `node-5` -- check `apparmor_parser` exit code in pod logs. (2) AppArmor may not be enabled on `node-5` (`cat /sys/module/apparmor/parameters/enabled` returns `N`). (3) The profile file may have a syntax error that only manifests on a different kernel version on `node-5`. (4) The DaemonSet may not have the required privileges (`privileged: true` or `CAP_MAC_ADMIN`) to load profiles. Debug with `ssh node-5 'sudo aa-status | grep <profile-name>'` to verify the profile is actually loaded in the kernel.
   </details>

4. **Your organization wants to adopt AppArmor for all production containers but has 200+ microservices. Creating individual profiles per service would take months. What pragmatic approach provides immediate security improvement?**
   <details>
   <summary>Answer</summary>
   Apply the `runtime/default` profile to all containers immediately -- this is the container runtime's built-in AppArmor profile that blocks common dangerous operations (mounting filesystems, accessing `/proc/sys`, raw network access) without breaking most applications. Set it via the annotation `container.apparmor.security.beta.kubernetes.io/<container>: runtime/default`. This gives immediate security improvement. Then incrementally create custom profiles for high-risk services using `aa-genprof` or `aa-logprof` to generate profiles from observed behavior. Start with complain mode, refine, then enforce. This two-phase approach provides defense in depth without months of upfront work.
   </details>

---

## Hands-On Exercise

**Task**: Create and apply an AppArmor profile that denies network access.

```bash
# Step 1: Check AppArmor is enabled (run on node)
cat /sys/module/apparmor/parameters/enabled
# Should output: Y

# Step 2: Create the profile
sudo tee /etc/apparmor.d/k8s-deny-network << 'EOF'
#include <tunables/global>

profile k8s-deny-network flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  # Allow file operations
  file,

  # Deny network access
  deny network,
}
EOF

# Step 3: Load the profile
sudo apparmor_parser -r /etc/apparmor.d/k8s-deny-network

# Step 4: Verify it's loaded
sudo aa-status | grep k8s-deny-network

# Step 5: Create pod with the profile
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: no-network-pod
  annotations:
    container.apparmor.security.beta.kubernetes.io/app: localhost/k8s-deny-network
spec:
  containers:
  - name: app
    image: curlimages/curl
    command: ["sleep", "3600"]
EOF

# Step 6: Wait for pod
kubectl wait --for=condition=Ready pod/no-network-pod --timeout=60s

# Step 7: Test network is blocked
kubectl exec no-network-pod -- curl -s https://kubernetes.io --connect-timeout 5
# Should fail due to AppArmor denying network

# Step 8: Create pod without restriction for comparison
kubectl run network-allowed --image=curlimages/curl --rm -it --restart=Never -- \
  curl -s https://kubernetes.io -o /dev/null -w "%{http_code}"
# Should succeed (200)

# Cleanup
kubectl delete pod no-network-pod
```

**Success criteria**: Pod with AppArmor profile cannot make network connections.

---

## Summary

**AppArmor Basics**:
- Linux Mandatory Access Control
- Per-program restrictions
- Profiles loaded on nodes

**Profile Application**:
```yaml
annotations:
  container.apparmor.security.beta.kubernetes.io/<container>: localhost/<profile>
```

**Common Profile Rules**:
- `deny /path w,` - Deny write
- `deny network,` - Deny networking
- `capability X,` - Allow capability

**Exam Tips**:
- Know annotation format
- Practice loading profiles
- Understand profile locations

---

## Next Module

[Module 3.2: Seccomp Profiles](../module-3.2-seccomp/) - System call filtering for containers.
