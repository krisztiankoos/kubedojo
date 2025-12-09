# Module 4.2: AppArmor Profiles

> **Linux Security** | Complexity: `[MEDIUM]` | Time: 30-35 min

## Prerequisites

Before starting this module:
- **Required**: [Module 2.3: Capabilities & LSMs](../../foundations/container-primitives/module-2.3-capabilities-lsms.md)
- **Required**: [Module 1.4: Users & Permissions](../../foundations/system-essentials/module-1.4-users-permissions.md)
- **Helpful**: Understanding of basic security concepts

---

## Why This Module Matters

AppArmor provides **mandatory access control (MAC)** — security policies that applications cannot bypass, even as root. While traditional permissions (DAC) can be changed by the file owner, AppArmor policies are enforced by the kernel.

Understanding AppArmor helps you:

- **Secure Kubernetes pods** — Apply container-specific profiles
- **Limit application damage** — Compromised apps can only access allowed resources
- **Pass CKS exam** — AppArmor is directly tested
- **Debug "permission denied"** — When DAC permissions are fine but access fails

When your container can't write to a file despite having correct permissions, AppArmor might be the cause.

---

## Did You Know?

- **AppArmor is path-based, SELinux is label-based** — AppArmor policies use file paths ("/etc/passwd"), SELinux uses security labels. Path-based is simpler but can be bypassed via hard links (if allowed).

- **Ubuntu, Debian, and SUSE use AppArmor by default** — RHEL/CentOS use SELinux. Kubernetes works with both, but you need to know which your nodes use.

- **Docker containers get a default AppArmor profile** — Called "docker-default", it restricts dangerous operations. Running `--security-opt apparmor=unconfined` removes this protection.

- **AppArmor has been in the Linux kernel since 2006** (kernel 2.6.36). It's maintained by Canonical (Ubuntu) and is simpler than SELinux.

---

## How AppArmor Works

### MAC vs DAC

```
┌─────────────────────────────────────────────────────────────────┐
│                    ACCESS CONTROL                                │
│                                                                  │
│  DAC (Discretionary)           MAC (Mandatory - AppArmor)       │
│  ┌───────────────────────┐    ┌───────────────────────────┐    │
│  │ Owner controls access │    │ Policy controls access    │    │
│  │ User can change perms │    │ User cannot change policy │    │
│  │ rwxr-xr-x            │    │ Kernel enforces rules     │    │
│  └───────────────────────┘    └───────────────────────────┘    │
│                                                                  │
│  Root bypasses DAC             Root CANNOT bypass MAC           │
│                                                                  │
│  Access = DAC allows           Access = DAC allows              │
│                                       AND MAC allows            │
└─────────────────────────────────────────────────────────────────┘
```

### Profile Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| **Enforce** | Blocks and logs violations | Production |
| **Complain** | Logs but allows violations | Testing/development |
| **Unconfined** | No restrictions | Disabled |

---

## AppArmor Status and Profiles

### Checking Status

```bash
# Check if AppArmor is enabled
sudo aa-status

# Sample output:
# apparmor module is loaded.
# 42 profiles are loaded.
# 38 profiles are in enforce mode.
#    /usr/sbin/cups-browsed
#    /usr/bin/evince
#    docker-default
# 4 profiles are in complain mode.
#    /usr/sbin/rsyslogd
# 12 processes have profiles defined.
# 10 processes are in enforce mode.
# 2 processes are in complain mode.

# Check specific process
ps auxZ | grep nginx
```

### Profile Locations

```bash
# Profile files
/etc/apparmor.d/           # Main profiles
/etc/apparmor.d/tunables/  # Variables
/etc/apparmor.d/abstractions/  # Reusable includes

# Cache (compiled profiles)
/var/cache/apparmor/
```

---

## Profile Syntax

### Basic Structure

```
#include <tunables/global>

profile my-app /path/to/executable flags=(attach_disconnected) {
  #include <abstractions/base>

  # File access rules
  /etc/myapp/** r,           # Read config
  /var/log/myapp/** rw,      # Read/write logs
  /var/run/myapp.pid w,      # Write PID file

  # Network access
  network inet tcp,          # TCP allowed
  network inet udp,          # UDP allowed

  # Capabilities
  capability net_bind_service,  # Bind ports < 1024

  # Deny rules (explicit)
  deny /etc/shadow r,        # Cannot read shadow

  # Execute other programs
  /usr/bin/ls ix,            # Inherit this profile
  /usr/bin/id px,            # Use /usr/bin/id's profile
}
```

### Permission Flags

| Flag | Meaning |
|------|---------|
| `r` | Read |
| `w` | Write |
| `a` | Append |
| `x` | Execute |
| `m` | Memory map executable |
| `k` | Lock |
| `l` | Link |

### Execute Modes

| Mode | Meaning |
|------|---------|
| `ix` | Inherit current profile |
| `px` | Switch to target's profile |
| `Px` | Switch to target's profile (enforce) |
| `ux` | Unconfined |
| `Ux` | Unconfined (enforce) |

### Glob Patterns

```
/path/to/file     # Exact file
/path/to/dir/     # Directory only
/path/to/dir/*    # Files in directory
/path/to/dir/**   # Files in directory and subdirs
/path/to/dir/file{1,2,3}  # file1, file2, file3
```

---

## Managing Profiles

### Load/Unload Profiles

```bash
# Load a profile (enforce mode)
sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.nginx

# Load in complain mode
sudo apparmor_parser -C /etc/apparmor.d/usr.sbin.nginx

# Remove a profile
sudo apparmor_parser -R /etc/apparmor.d/usr.sbin.nginx

# Reload all profiles
sudo systemctl reload apparmor
```

### Switch Profile Modes

```bash
# Set to complain mode
sudo aa-complain /path/to/profile
# or
sudo aa-complain /usr/sbin/nginx

# Set to enforce mode
sudo aa-enforce /path/to/profile
# or
sudo aa-enforce /usr/sbin/nginx

# Disable profile (unconfined)
sudo aa-disable /path/to/profile
```

### Generate Profile

```bash
# Generate profile for a program
sudo aa-genprof /usr/bin/myapp

# Interactive: Run the program, aa-genprof logs events
# Then mark events as allowed/denied to build profile

# Auto-generate from logs
sudo aa-logprof
```

---

## Example Profile

### Nginx Profile

```
#include <tunables/global>

profile nginx /usr/sbin/nginx flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  #include <abstractions/nameservice>

  # Capabilities
  capability dac_override,
  capability net_bind_service,
  capability setgid,
  capability setuid,

  # Network
  network inet tcp,
  network inet6 tcp,

  # Binary and libraries
  /usr/sbin/nginx mr,
  /lib/** mr,
  /usr/lib/** mr,

  # Configuration
  /etc/nginx/** r,
  /etc/ssl/** r,

  # Web content
  /var/www/** r,
  /srv/www/** r,

  # Logs
  /var/log/nginx/** rw,

  # Runtime
  /run/nginx.pid rw,
  /run/nginx/ rw,

  # Temp files
  /tmp/** rw,
  /var/lib/nginx/** rw,

  # Workers
  /usr/sbin/nginx ix,

  # Deny sensitive files
  deny /etc/shadow r,
  deny /etc/gshadow r,
}
```

---

## Container AppArmor

### Docker Default Profile

Docker automatically applies "docker-default" profile:

```bash
# Check container's AppArmor profile
docker inspect <container> | jq '.[0].AppArmorProfile'
# Output: "docker-default"

# Run with custom profile
docker run --security-opt apparmor=my-profile nginx

# Run without AppArmor (dangerous!)
docker run --security-opt apparmor=unconfined nginx
```

### Custom Container Profile

```
#include <tunables/global>

profile my-container-profile flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  network inet tcp,
  network inet udp,

  # Container filesystem
  / r,
  /** r,
  /app/** rw,
  /tmp/** rw,

  # Deny dangerous operations
  deny mount,
  deny umount,
  deny ptrace,
  deny /proc/*/mem rw,
  deny /proc/sysrq-trigger rw,

  # Capabilities
  capability chown,
  capability dac_override,
  capability setuid,
  capability setgid,
}
```

---

## Kubernetes AppArmor

### Applying Profile to Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  annotations:
    # Format: container.apparmor.security.beta.kubernetes.io/<container-name>: <profile>
    container.apparmor.security.beta.kubernetes.io/my-container: localhost/my-profile
spec:
  containers:
  - name: my-container
    image: nginx
```

### Profile Types

| Value | Meaning |
|-------|---------|
| `runtime/default` | Container runtime's default |
| `localhost/<profile>` | Profile loaded on node |
| `unconfined` | No AppArmor (dangerous) |

### Loading Profiles on Nodes

```bash
# Profile must exist on the node at /etc/apparmor.d/
# Load it:
sudo apparmor_parser -r /etc/apparmor.d/my-profile

# Or use DaemonSet to deploy profiles to all nodes
```

### Example: Restricted Nginx Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: restricted-nginx
  annotations:
    container.apparmor.security.beta.kubernetes.io/nginx: localhost/k8s-nginx
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80
```

---

## Debugging AppArmor

### View Denials

```bash
# Check dmesg
sudo dmesg | grep -i apparmor

# Check audit log
sudo cat /var/log/audit/audit.log | grep apparmor

# Check syslog
sudo grep apparmor /var/log/syslog

# Sample denial:
# audit: type=1400 audit(...): apparmor="DENIED" operation="open"
#   profile="docker-default" name="/etc/shadow" pid=1234
#   comm="cat" requested_mask="r" denied_mask="r"
```

### Common Issues

```bash
# Issue: Container can't write to /app/data
# Check: Profile allows /app/** but not write

# Issue: Network connection refused
# Check: Profile has network rules

# Issue: Exec fails
# Check: Profile has execute permission for binary

# Generate missing rules from logs
sudo aa-logprof
```

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Profile not loaded on node | Pod fails to start | Use DaemonSet to deploy profiles |
| Typo in annotation | Profile not applied | Verify annotation format |
| Using unconfined | No protection | Use runtime/default or custom |
| Profile too restrictive | App crashes | Test in complain mode first |
| Not checking denials | Silent failures | Monitor audit logs |
| Hardcoding paths | Containers have different paths | Use abstractions |

---

## Quiz

### Question 1
What's the difference between AppArmor's enforce and complain modes?

<details>
<summary>Show Answer</summary>

- **Enforce mode**: Blocks violations AND logs them. Policy is actively enforced.
- **Complain mode**: Allows violations but logs them. Used for testing profiles.

Complain mode is useful for developing profiles without breaking applications.

</details>

### Question 2
How do you apply an AppArmor profile to a Kubernetes container?

<details>
<summary>Show Answer</summary>

Use an annotation on the pod:

```yaml
metadata:
  annotations:
    container.apparmor.security.beta.kubernetes.io/<container-name>: localhost/<profile-name>
```

The profile must exist on the node at `/etc/apparmor.d/` and be loaded.

</details>

### Question 3
What does `/etc/app/** rw,` mean in an AppArmor profile?

<details>
<summary>Show Answer</summary>

- `/etc/app/` — The directory path
- `**` — Match all files and subdirectories recursively
- `rw` — Read and write permissions

This rule allows read and write access to everything under `/etc/app/`.

</details>

### Question 4
Why can't root bypass AppArmor restrictions?

<details>
<summary>Show Answer</summary>

AppArmor is **Mandatory Access Control (MAC)**. Unlike DAC (file permissions), MAC policies are enforced by the kernel regardless of user privileges.

Root can:
- Manage AppArmor policies (load/unload)
- Set processes to unconfined

But root CANNOT bypass an active AppArmor profile for a confined process.

</details>

### Question 5
How do you debug why an AppArmor-confined process is being denied?

<details>
<summary>Show Answer</summary>

1. **Check logs**:
```bash
sudo dmesg | grep -i apparmor
sudo grep apparmor /var/log/syslog
```

2. **Look for DENIED entries** with the operation, path, and profile name

3. **Use aa-logprof** to generate rules from denials:
```bash
sudo aa-logprof
```

4. **Test in complain mode** to log all violations without blocking:
```bash
sudo aa-complain /etc/apparmor.d/my-profile
```

</details>

---

## Hands-On Exercise

### Working with AppArmor

**Objective**: Create, test, and apply AppArmor profiles.

**Environment**: Ubuntu/Debian system with AppArmor

#### Part 1: Check AppArmor Status

```bash
# 1. Verify AppArmor is running
sudo aa-status

# 2. List loaded profiles
sudo aa-status | grep "profiles are loaded"

# 3. Check a running process
ps auxZ | head -10
```

#### Part 2: Create a Simple Profile

```bash
# 1. Create a test script
cat > /tmp/test-app.sh << 'EOF'
#!/bin/bash
echo "Reading /etc/hostname:"
cat /etc/hostname
echo "Reading /etc/shadow:"
cat /etc/shadow 2>&1
echo "Writing to /tmp:"
echo "test" > /tmp/test-output.txt
echo "Done"
EOF
chmod +x /tmp/test-app.sh

# 2. Run without AppArmor
/tmp/test-app.sh

# 3. Create AppArmor profile
sudo tee /etc/apparmor.d/tmp.test-app.sh << 'EOF'
#include <tunables/global>

profile test-app /tmp/test-app.sh {
  #include <abstractions/base>
  #include <abstractions/bash>

  /tmp/test-app.sh r,
  /bin/bash ix,
  /bin/cat ix,
  /usr/bin/cat ix,

  # Allow hostname, deny shadow
  /etc/hostname r,
  deny /etc/shadow r,

  # Allow /tmp writes
  /tmp/** rw,
}
EOF

# 4. Load the profile
sudo apparmor_parser -r /etc/apparmor.d/tmp.test-app.sh

# 5. Test again
/tmp/test-app.sh
# shadow should be denied now

# 6. Check denial in logs
sudo dmesg | tail -5 | grep apparmor
```

#### Part 3: Complain Mode

```bash
# 1. Set to complain mode
sudo aa-complain /etc/apparmor.d/tmp.test-app.sh

# 2. Run script
/tmp/test-app.sh
# Everything works now

# 3. Check logs for what would have been denied
sudo dmesg | grep "ALLOWED" | tail -5

# 4. Set back to enforce
sudo aa-enforce /etc/apparmor.d/tmp.test-app.sh
```

#### Part 4: Docker AppArmor (if available)

```bash
# 1. Check default profile
docker run --rm alpine cat /proc/1/attr/current
# Should show: docker-default

# 2. Run unconfined (compare)
docker run --rm --security-opt apparmor=unconfined alpine cat /proc/1/attr/current
# Shows: unconfined

# 3. Test restriction
docker run --rm alpine cat /etc/shadow
# Fails due to docker-default profile

docker run --rm --security-opt apparmor=unconfined alpine cat /etc/shadow
# May work (if root)
```

#### Cleanup

```bash
sudo aa-disable /etc/apparmor.d/tmp.test-app.sh
sudo rm /etc/apparmor.d/tmp.test-app.sh
rm /tmp/test-app.sh /tmp/test-output.txt
```

### Success Criteria

- [ ] Checked AppArmor status and loaded profiles
- [ ] Created a custom AppArmor profile
- [ ] Tested enforce vs complain mode
- [ ] Verified denials in logs
- [ ] (Docker) Tested container profile behavior

---

## Key Takeaways

1. **MAC complements DAC** — AppArmor restricts even root users

2. **Path-based rules** — Simple to write but understand glob patterns

3. **Test in complain mode** — Avoid breaking apps while developing profiles

4. **Kubernetes uses annotations** — Profile must exist on node

5. **Monitor denials** — dmesg and audit logs show what's blocked

---

## What's Next?

In **Module 4.3: SELinux Contexts**, you'll learn the alternative MAC system used by RHEL/CentOS—more complex but more powerful than AppArmor.

---

## Further Reading

- [AppArmor Wiki](https://gitlab.com/apparmor/apparmor/-/wikis/home)
- [Ubuntu AppArmor Guide](https://ubuntu.com/server/docs/security-apparmor)
- [Kubernetes AppArmor](https://kubernetes.io/docs/tutorials/security/apparmor/)
- [Docker AppArmor Security](https://docs.docker.com/engine/security/apparmor/)
