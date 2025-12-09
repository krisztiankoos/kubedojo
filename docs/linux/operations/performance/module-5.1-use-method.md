# Module 5.1: USE Method

> **Linux Performance** | Complexity: `[MEDIUM]` | Time: 25-30 min

## Prerequisites

Before starting this module:
- **Required**: [Module 1.2: Processes & Systemd](../../foundations/system-essentials/module-1.2-processes-systemd.md)
- **Required**: [Module 2.2: cgroups](../../foundations/container-primitives/module-2.2-cgroups.md)
- **Helpful**: Basic understanding of system metrics

---

## Why This Module Matters

When a system is slow, where do you start? Random debugging wastes time. The **USE Method** provides a systematic checklist for analyzing any performance problem.

Understanding the USE Method helps you:

- **Diagnose systematically** — Check every resource in order
- **Find root causes faster** — Don't miss obvious bottlenecks
- **Communicate clearly** — "CPU saturation" is precise, "slow" isn't
- **Set Kubernetes limits** — Know what metrics matter

Performance problems have causes. The USE Method helps you find them.

---

## Did You Know?

- **USE was created by Brendan Gregg** — A Netflix performance engineer who also created DTrace, BPF tools, and flame graphs. His work defines modern observability.

- **USE stands for Utilization, Saturation, Errors** — Three metrics for every resource. If all three are fine, the resource isn't your bottleneck.

- **Most performance issues are simple** — Brendan Gregg estimates 80% of issues are found in the first few USE checks. Complex analysis is rarely needed.

- **The method applies to any system** — Linux, databases, networks, applications. The resources change, but the method stays the same.

---

## The USE Method

### Core Concept

For every **resource**, check:

| Metric | Definition | Example |
|--------|------------|---------|
| **U**tilization | Time resource was busy | CPU 80% utilized |
| **S**aturation | Work queued, waiting | 10 processes waiting for CPU |
| **E**rrors | Error events | Disk I/O errors |

### Why This Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE ANALYSIS                          │
│                                                                  │
│  Without Method:                 With USE Method:                │
│  ┌───────────────────────┐      ┌───────────────────────────┐   │
│  │ "It's slow"           │      │ Check CPU: U, S, E        │   │
│  │ "Maybe it's the DB?"  │      │ Check Memory: U, S, E     │   │
│  │ "Let's try rebooting" │      │ Check Disk: U, S, E       │   │
│  │ "Who changed what?"   │      │ Check Network: U, S, E    │   │
│  └───────────────────────┘      │                           │   │
│                                 │ → Found: Disk saturation  │   │
│  Time: Hours                    └───────────────────────────┘   │
│  Result: Maybe fixed                                            │
│                                 Time: 5 minutes                 │
│                                 Result: Root cause found        │
└─────────────────────────────────────────────────────────────────┘
```

### Resource Checklist

| Resource | Utilization Tool | Saturation Tool | Errors Tool |
|----------|------------------|-----------------|-------------|
| CPU | `top`, `mpstat` | `vmstat`, load average | `dmesg` |
| Memory | `free`, `vmstat` | `vmstat si/so` | `dmesg` |
| Disk I/O | `iostat %util` | `iostat avgqu-sz` | `smartctl`, `dmesg` |
| Network | `sar -n DEV` | `netstat`, `ss` | `ip -s link` |

---

## CPU Metrics

### Utilization

```bash
# Overall CPU utilization
top -bn1 | head -5
# %Cpu(s): 23.5 us, 5.2 sy, 0.0 ni, 70.1 id, 0.2 wa, 0.0 hi, 1.0 si

# Per-CPU utilization
mpstat -P ALL 1 3
# Shows each CPU core

# CPU breakdown:
# us = user (application code)
# sy = system (kernel)
# ni = nice (low priority)
# id = idle
# wa = iowait (waiting for I/O)
# hi = hardware interrupts
# si = software interrupts
# st = steal (VM overhead)
```

**High utilization isn't bad** — 100% CPU means you're using what you paid for. Problems start with saturation.

### Saturation

```bash
# Load average (processes wanting CPU)
uptime
# load average: 4.52, 3.21, 2.18
# Numbers = 1, 5, 15 minute averages

# Rule of thumb:
# Load < CPU cores = OK
# Load > CPU cores = Saturation

# Check CPU count
nproc
# 4

# Run queue (processes waiting)
vmstat 1
#  r  b   swpd   free   buff  cache ...
#  8  0      0 123456  78910 234567 ...
# r = run queue (waiting for CPU)
# b = blocked (waiting for I/O)
```

### Errors

```bash
# Check kernel messages
dmesg | grep -i "cpu\|mce\|error"

# MCE = Machine Check Exception (hardware error)
# These are rare but critical
```

---

## Memory Metrics

### Utilization

```bash
# Memory overview
free -h
#               total        used        free      shared  buff/cache   available
# Mem:           15Gi       4.2Gi       2.1Gi       512Mi        9.1Gi        10Gi
# Swap:         2.0Gi       100Mi       1.9Gi

# Key insight: "available" matters, not "free"
# buff/cache can be reclaimed when needed

# Detailed memory
cat /proc/meminfo

# Per-process memory
ps aux --sort=-%mem | head -10
```

**"Free" memory isn't wasted** — Linux uses spare RAM for caching. Low "free" with high "available" is normal and efficient.

### Saturation

```bash
# Check for swapping
vmstat 1
#    si   so    bi    bo
#     0    0    50    20
# si = swap in (pages from disk)
# so = swap out (pages to disk)

# Active swapping = memory saturation

# Check swap usage
swapon --show

# OOM killer activity
dmesg | grep -i "out of memory\|oom"
```

### Errors

```bash
# Memory errors
dmesg | grep -i "memory\|ecc\|error"

# ECC = Error Correcting Code (server RAM)
# Uncorrectable errors = hardware failing
```

---

## Disk I/O Metrics

### Utilization

```bash
# Disk utilization
iostat -xz 1
# Device            %util  avgqu-sz  await  r/s    w/s
# sda                75.2      2.3    12.5  100    200

# %util = percentage of time disk was busy
# 100% = disk is bottleneck

# Per-disk utilization
iostat -x 1 | grep -E "^sd|^nvm"
```

### Saturation

```bash
# Queue length
iostat -x 1
# avgqu-sz = average queue size
# High queue = requests waiting

# await = average time (ms) for I/O
# High await with high queue = saturation

# iowait from CPU perspective
vmstat 1
# Look at wa column
```

### Errors

```bash
# Disk errors
dmesg | grep -i "error\|fail\|i/o"

# SMART data (disk health)
sudo smartctl -a /dev/sda | grep -i error

# Filesystem errors
sudo fsck -n /dev/sda1
```

---

## Network Metrics

### Utilization

```bash
# Interface statistics
ip -s link show eth0
# TX bytes, RX bytes

# Bandwidth utilization
sar -n DEV 1
# Shows Mbps per interface

# Real-time bandwidth
# Install iftop or nload
sudo iftop -i eth0
```

### Saturation

```bash
# Socket queues
ss -s
# Shows socket statistics

# Dropped packets (queue overflow)
netstat -s | grep -i drop
ip -s link | grep -i drop

# TCP retransmits (network saturation)
netstat -s | grep retrans
```

### Errors

```bash
# Interface errors
ip -s link show eth0
# Look for errors, dropped, overruns

# Network errors in dmesg
dmesg | grep -i "network\|eth\|link"
```

---

## USE Method Checklist

### Quick Reference

```bash
#!/bin/bash
# use-check.sh - Quick USE method scan

echo "=== CPU ==="
echo "Utilization:"
top -bn1 | head -5 | tail -1
echo "Saturation (load):"
uptime
echo ""

echo "=== Memory ==="
echo "Utilization:"
free -h | head -2
echo "Saturation (swap activity):"
vmstat 1 2 | tail -1 | awk '{print "si="$7, "so="$8}'
echo ""

echo "=== Disk ==="
echo "Utilization & Saturation:"
iostat -x 1 2 | grep -E "^sd|^nvm|^Device" | tail -3
echo ""

echo "=== Network ==="
echo "Errors:"
ip -s link show | grep -E "^[0-9]:|errors"
echo ""

echo "=== Recent Errors ==="
dmesg | tail -20 | grep -i "error\|fail\|oom" || echo "None recent"
```

### Systematic Walkthrough

1. **CPU**: High load average? High utilization?
2. **Memory**: Swapping? OOM kills?
3. **Disk**: High %util? High queue depth?
4. **Network**: Drops? Errors? Retransmits?

If all clear, the problem is likely application-level.

---

## Kubernetes Connection

### Node Resources

```bash
# Kubernetes node conditions
kubectl describe node worker-1 | grep -A 5 Conditions
#  MemoryPressure   False
#  DiskPressure     False
#  PIDPressure      False

# These map to USE:
# MemoryPressure = Memory saturation
# DiskPressure = Disk utilization
# PIDPressure = Process saturation
```

### Container Metrics

```bash
# Pod resource usage
kubectl top pod --containers

# Node resource usage
kubectl top node

# These show utilization, not saturation
# For saturation, check node metrics
```

### Resource Limits Connection

```yaml
# Kubernetes resource limits
resources:
  requests:
    cpu: "100m"      # Minimum guaranteed
    memory: "128Mi"
  limits:
    cpu: "500m"      # Maximum allowed
    memory: "512Mi"  # OOM killed if exceeded

# Requests affect scheduling (utilization)
# Limits cause throttling/killing (saturation/errors)
```

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Focusing only on utilization | High utilization isn't always bad | Check saturation too |
| Ignoring errors | Hardware issues cause performance problems | Always check dmesg |
| Random debugging | Time wasted, root cause missed | Follow USE systematically |
| Checking one metric | Multiple resources can be bottlenecks | Check all resources |
| Confusing "free" memory | Linux caches aggressively | Look at "available" |
| Ignoring steal time | VM overhead on cloud | Check st% in top |

---

## Quiz

### Question 1
What does high CPU utilization with low saturation indicate?

<details>
<summary>Show Answer</summary>

The CPU is working hard but keeping up. Processes are being scheduled without waiting.

This is **normal and healthy** — you're using your CPU effectively. High utilization only becomes a problem when combined with high saturation (processes waiting).

</details>

### Question 2
How do you check memory saturation on Linux?

<details>
<summary>Show Answer</summary>

Check for swap activity with `vmstat`:

```bash
vmstat 1
# si = swap in, so = swap out
# Non-zero values = memory saturation
```

Also check for OOM killer activity:
```bash
dmesg | grep -i oom
```

"Free" memory being low is NOT saturation — check "available" instead.

</details>

### Question 3
What does a load average of 8.0 mean on a 4-core system?

<details>
<summary>Show Answer</summary>

**CPU saturation**. Load average represents processes wanting to run.

- 4 cores can run 4 processes simultaneously
- Load of 8 = 4 running + 4 waiting
- On average, 4 processes are queued

Rule: Load > CPU count = saturation
8 > 4 = saturated

Check with `uptime` and `nproc`.

</details>

### Question 4
What's the difference between disk utilization and saturation?

<details>
<summary>Show Answer</summary>

**Utilization** (`%util`): How much time the disk was busy
- 100% = disk was busy the whole time

**Saturation** (`avgqu-sz`): Requests waiting in queue
- High queue = disk can't keep up

A disk can be 100% utilized but still not saturated (if it handles requests fast enough). Saturation means requests are backing up.

Check with `iostat -x`:
```bash
# %util = utilization
# avgqu-sz = queue length (saturation)
# await = total time including queue wait
```

</details>

### Question 5
When all USE metrics are fine, where is the problem likely?

<details>
<summary>Show Answer</summary>

**Application level**. If Linux resources (CPU, memory, disk, network) all show low utilization, no saturation, and no errors, the system isn't the bottleneck.

Common application issues:
- Lock contention
- Database queries
- External API calls
- Application bugs
- Configuration problems

Use application-level profiling (tracing, APM) to find the cause.

</details>

---

## Hands-On Exercise

### Practicing the USE Method

**Objective**: Apply the USE method systematically to analyze system performance.

**Environment**: Any Linux system

#### Part 1: CPU Analysis

```bash
# 1. Create CPU load
yes > /dev/null &
yes > /dev/null &
yes > /dev/null &
PID1=$!

# 2. Check CPU utilization
top -bn1 | head -8

# 3. Check saturation
uptime
cat /proc/loadavg
nproc

# 4. Check for errors
dmesg | tail -10 | grep -i error

# 5. Clean up
killall yes
```

#### Part 2: Memory Analysis

```bash
# 1. Check current state
free -h

# 2. Check available vs free
cat /proc/meminfo | grep -E "MemTotal|MemFree|MemAvailable|Buffers|Cached"

# 3. Check saturation (swap)
vmstat 1 3

# 4. Check OOM history
dmesg | grep -i "out of memory" || echo "No OOM events"

# 5. Top memory users
ps aux --sort=-%mem | head -5
```

#### Part 3: Disk Analysis

```bash
# 1. Check disk utilization
iostat -x 1 3

# 2. Identify busy disks
iostat -x | awk '$NF > 50 {print "Busy:", $1, $NF"%"}'

# 3. Check for errors
dmesg | grep -i "i/o error\|disk" | tail -5

# 4. Check filesystem usage (different from I/O)
df -h
```

#### Part 4: Network Analysis

```bash
# 1. Check interface errors
ip -s link show | grep -A 6 "^2:"

# 2. Check socket statistics
ss -s

# 3. Check drops
netstat -s | grep -i "drop\|error" | head -10

# 4. Connection states
ss -tan | awk '{print $1}' | sort | uniq -c | sort -rn
```

#### Part 5: Full USE Scan

```bash
# Run complete USE analysis
echo "=== CPU ===" && \
uptime && \
echo "" && \
echo "=== Memory ===" && \
free -h && \
echo "" && \
echo "=== Disk ===" && \
iostat -x 1 1 | grep -E "^sd|^nvm|avg" && \
echo "" && \
echo "=== Errors ===" && \
dmesg | tail -20 | grep -iE "error|fail|oom|drop" || echo "Clean"
```

### Success Criteria

- [ ] Checked CPU utilization, saturation, and errors
- [ ] Checked memory utilization and swap activity
- [ ] Checked disk I/O utilization and queue depth
- [ ] Checked network errors and drops
- [ ] Ran complete USE scan
- [ ] Identified which resources are healthy

---

## Key Takeaways

1. **USE = Utilization, Saturation, Errors** — Check all three for each resource

2. **Systematic beats random** — Follow the checklist, don't guess

3. **Saturation matters more than utilization** — Busy isn't bad, queuing is

4. **Check all resources** — Don't stop at the first issue

5. **If USE is clean, look at the application** — OS isn't always the problem

---

## What's Next?

In **Module 5.2: CPU & Scheduling**, you'll dive deeper into CPU metrics, understand the Linux scheduler, and learn how Kubernetes CPU limits actually work.

---

## Further Reading

- [Brendan Gregg's USE Method](https://www.brendangregg.com/usemethod.html)
- [Linux Performance Analysis in 60s](https://netflixtechblog.com/linux-performance-analysis-in-60-000-milliseconds-accc10403c55)
- [Systems Performance Book](https://www.brendangregg.com/systems-performance-2nd-edition-book.html)
- [Kubernetes Node Conditions](https://kubernetes.io/docs/concepts/architecture/nodes/#condition)
