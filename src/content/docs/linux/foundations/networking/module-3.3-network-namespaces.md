---
title: "Module 3.3: Network Namespaces & veth"
slug: linux/foundations/networking/module-3.3-network-namespaces
sidebar:
  order: 4
lab:
  id: "linux-3.3-network-namespaces"
  url: "https://killercoda.com/kubedojo/scenario/linux-3.3-network-namespaces"
  duration: "40 min"
  difficulty: "advanced"
  environment: "ubuntu"
---
> **Linux Foundations** | Complexity: `[MEDIUM]` | Time: 30-35 min

## Prerequisites

Before starting this module:
- **Required**: [Module 2.1: Linux Namespaces](../container-primitives/module-2.1-namespaces/)
- **Required**: [Module 3.1: TCP/IP Essentials](../module-3.1-tcp-ip-essentials/)
- **Helpful**: Basic understanding of bridges and switches

---

## What You'll Be Able to Do

After this module, you will be able to:
- **Create** network namespaces and connect them with veth pairs
- **Explain** how container networking works at the Linux level (namespaces + bridges + veth)
- **Trace** a packet from one container to another through the network stack
- **Debug** container-to-container connectivity by inspecting bridges, routes, and iptables rules

---

## Why This Module Matters

Every container and Kubernetes pod has its own network namespace. Understanding how network namespaces work and how they're connected explains:

- **Pod networking** — How pods get IP addresses and communicate
- **Container network debugging** — Why can't my container reach the network?
- **CNI plugins** — What they actually do under the hood
- **Network isolation** — How pods are isolated yet connected

When you wonder how a pod has its own IP or why two containers can't see each other, network namespaces are the answer.

---

## Did You Know?

- **Network namespaces were added to Linux in 2006** (kernel 2.6.24), but didn't become widely used until Docker popularized containers in 2013.

- **Each pod in Kubernetes has exactly one network namespace** shared by all containers in that pod. This is why containers in a pod can communicate via localhost.

- **veth pairs are like virtual Ethernet cables** — One end goes in the container, the other end connects to a bridge or the host. You can have thousands of them on a single host.

- **The CNI spec is only about 20 pages** — Yet it defines how all container networking works in Kubernetes. Simple specification, powerful abstraction.

---

## Network Namespace Recap

A **network namespace** provides an isolated network stack:

```
┌─────────────────────────────────────────────────────────────────┐
│                    NETWORK NAMESPACE ISOLATION                   │
│                                                                  │
│  Host Network Namespace          Container Network Namespace    │
│  ┌───────────────────────┐       ┌────────────────────────┐    │
│  │ eth0: 192.168.1.100   │       │ eth0: 10.0.0.5         │    │
│  │ lo: 127.0.0.1         │       │ lo: 127.0.0.1          │    │
│  │ docker0: 172.17.0.1   │       │                         │    │
│  │                       │       │ Own routing table       │    │
│  │ Own routing table     │       │ Own iptables rules     │    │
│  │ Own iptables rules    │       │ Own ports (80, 443)    │    │
│  │ Own ports             │       │                         │    │
│  └───────────────────────┘       └────────────────────────┘    │
│                                                                  │
│  Completely separate network stacks                              │
│  Same port can be used in each namespace                        │
└─────────────────────────────────────────────────────────────────┘
```

### Creating Network Namespaces

```bash
# Create namespace
sudo ip netns add red

# List namespaces
ip netns list

# Execute command in namespace
sudo ip netns exec red ip link

# Delete namespace
sudo ip netns delete red
```

> **Stop and think**: If a network namespace is completely isolated with its own loopback interface, how can a process inside it ever send a packet to a process on the host machine? What kind of construct would bridge that isolation boundary?

---

## Virtual Ethernet (veth) Pairs

**veth pairs** are virtual network interfaces that act like a pipe—packets sent into one end come out the other.

### How veth Works

```
┌─────────────────────────────────────────────────────────────────┐
│                       VETH PAIR                                  │
│                                                                  │
│  ┌────────────────────┐         ┌────────────────────┐         │
│  │  veth-host         │ ═══════ │  veth-container    │         │
│  │  (in host ns)      │  pipe   │  (in container ns) │         │
│  └────────────────────┘         └────────────────────┘         │
│                                                                  │
│  Packets in one end → come out the other end                    │
│  Like a virtual Ethernet cable                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Creating veth Pairs

```bash
# Create veth pair
sudo ip link add veth-host type veth peer name veth-ns

# They're created together as a pair
ip link show type veth
```

---

## Connecting Namespaces

### Simple Two-Namespace Setup

```
┌─────────────────────────────────────────────────────────────────┐
│                  CONNECTING TWO NAMESPACES                       │
│                                                                  │
│  ┌──────────────────┐                ┌──────────────────┐       │
│  │  Namespace: red  │                │ Namespace: blue  │       │
│  │                  │                │                  │       │
│  │  veth-red        │════════════════│  veth-blue       │       │
│  │  10.0.0.1/24     │    veth pair   │  10.0.0.2/24     │       │
│  │                  │                │                  │       │
│  └──────────────────┘                └──────────────────┘       │
│                                                                  │
│  red$ ping 10.0.0.2  →  works!                                 │
│  blue$ ping 10.0.0.1 →  works!                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Try This: Connect Two Namespaces

```bash
# 1. Create namespaces
sudo ip netns add red
sudo ip netns add blue

# 2. Create veth pair
sudo ip link add veth-red type veth peer name veth-blue

# 3. Move each end to a namespace
sudo ip link set veth-red netns red
sudo ip link set veth-blue netns blue

# 4. Assign IP addresses
sudo ip netns exec red ip addr add 10.0.0.1/24 dev veth-red
sudo ip netns exec blue ip addr add 10.0.0.2/24 dev veth-blue

# 5. Bring interfaces up
sudo ip netns exec red ip link set veth-red up
sudo ip netns exec blue ip link set veth-blue up
sudo ip netns exec red ip link set lo up
sudo ip netns exec blue ip link set lo up

# 6. Test connectivity
sudo ip netns exec red ping -c 2 10.0.0.2

# 7. Cleanup
sudo ip netns delete red
sudo ip netns delete blue
```

> **Pause and predict**: We just connected two namespaces using a single veth pair. If we have 50 containers on a host that all need to talk to each other, creating a direct veth pair between every single combination of containers would require 1,225 pairs! How do physical data centers solve this many-to-many connection problem, and how might we emulate that in software?

---

## Linux Bridges

A **bridge** connects multiple network interfaces at Layer 2 (like a virtual switch).

### Bridge Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     LINUX BRIDGE                                 │
│                                                                  │
│  Container 1          Container 2          Container 3          │
│  ┌──────────┐        ┌──────────┐        ┌──────────┐          │
│  │ eth0     │        │ eth0     │        │ eth0     │          │
│  │10.0.0.2  │        │10.0.0.3  │        │10.0.0.4  │          │
│  └────┬─────┘        └────┬─────┘        └────┬─────┘          │
│       │                   │                   │                 │
│       │ veth              │ veth              │ veth            │
│       │                   │                   │                 │
│  ┌────▼───────────────────▼───────────────────▼────┐            │
│  │                    br0 (bridge)                  │            │
│  │                    10.0.0.1/24                   │            │
│  └─────────────────────────┬───────────────────────┘            │
│                            │                                     │
│                     NAT / Routing                                │
│                            │                                     │
│                     ┌──────▼──────┐                             │
│                     │    eth0     │                             │
│                     │192.168.1.100│                             │
│                     └─────────────┘                             │
│                        Host NIC                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Creating a Bridge

```bash
# Create bridge
sudo ip link add br0 type bridge

# Bring it up
sudo ip link set br0 up

# Assign IP (becomes gateway for containers)
sudo ip addr add 10.0.0.1/24 dev br0

# Connect veth to bridge
sudo ip link set veth-host master br0
```

> **Stop and think**: We've seen namespaces, veth pairs, and bridges. When you run `docker run nginx`, Docker automates all of this in milliseconds. Based on what we've learned, what exact sequence of networking commands do you think the Docker daemon executes behind the scenes to give that Nginx container internet access?

---

## Container Networking in Practice

### How Docker Creates Container Networks

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCKER NETWORKING                             │
│                                                                  │
│  1. docker run nginx                                            │
│       │                                                          │
│       ▼                                                          │
│  2. Create network namespace for container                      │
│       │                                                          │
│       ▼                                                          │
│  3. Create veth pair                                            │
│       │                                                          │
│       ▼                                                          │
│  4. Move one end (eth0) into container namespace               │
│       │                                                          │
│       ▼                                                          │
│  5. Connect other end to docker0 bridge                        │
│       │                                                          │
│       ▼                                                          │
│  6. Assign IP from bridge subnet (172.17.0.x)                  │
│       │                                                          │
│       ▼                                                          │
│  7. Set up iptables rules for NAT                              │
│                                                                  │
│  Result: Container has network access via docker0 bridge       │
└─────────────────────────────────────────────────────────────────┘
```

### Viewing Docker Networks

```bash
# See docker bridge
ip link show docker0

# See veth interfaces (host side)
ip link show type veth

# See bridge members
bridge link show

# Inside container
docker exec container-id ip addr
docker exec container-id ip route
```

---

## Kubernetes Pod Networking

### CNI (Container Network Interface)

Kubernetes uses CNI plugins for pod networking.

```
┌─────────────────────────────────────────────────────────────────┐
│                    CNI WORKFLOW                                  │
│                                                                  │
│  kubelet: "Create network for pod xyz"                          │
│       │                                                          │
│       ▼                                                          │
│  CNI Plugin (Calico/Flannel/Cilium):                           │
│       │                                                          │
│       ├── 1. Create network namespace                           │
│       │                                                          │
│       ├── 2. Create veth pair                                   │
│       │                                                          │
│       ├── 3. Attach to pod namespace                            │
│       │                                                          │
│       ├── 4. Assign IP from IPAM                                │
│       │                                                          │
│       ├── 5. Set up routes                                      │
│       │                                                          │
│       └── 6. Return IP to kubelet                               │
│                                                                  │
│  kubelet: "Pod IP is 10.244.1.5"                               │
└─────────────────────────────────────────────────────────────────┘
```

### Pod Network Namespace

```
┌─────────────────────────────────────────────────────────────────┐
│                    POD NETWORKING                                │
│                                                                  │
│  Pod with two containers:                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Shared Network Namespace                       │   │
│  │                                                          │   │
│  │  ┌──────────────┐        ┌──────────────┐              │   │
│  │  │ Container A  │        │ Container B  │              │   │
│  │  │ (nginx)      │        │ (sidecar)    │              │   │
│  │  │ port 80      │        │ port 9090    │              │   │
│  │  └──────────────┘        └──────────────┘              │   │
│  │                                                          │   │
│  │  eth0: 10.244.1.5                                       │   │
│  │  localhost works between containers                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                          veth                                   │
│                            │                                    │
│  ┌─────────────────────────▼───────────────────────────────┐   │
│  │                      cni0 bridge                         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Inspecting Pod Networking

```bash
# Find pod's network namespace
# Get container ID
CONTAINER_ID=$(crictl ps --name nginx -q)

# Get PID
PID=$(crictl inspect $CONTAINER_ID | jq .info.pid)

# Access namespace
sudo nsenter -t $PID -n ip addr

# Or via Kubernetes
kubectl exec pod-name -- ip addr
kubectl exec pod-name -- ip route
kubectl exec pod-name -- cat /etc/resolv.conf
```

---

## Building a Mini Container Network

### Complete Example

```bash
#!/bin/bash
# Create a container-like network setup

# 1. Create bridge
sudo ip link add cni0 type bridge
sudo ip link set cni0 up
sudo ip addr add 10.244.0.1/24 dev cni0

# 2. Create "container" namespace
sudo ip netns add container1

# 3. Create veth pair
sudo ip link add veth0 type veth peer name eth0

# 4. Move eth0 to container namespace
sudo ip link set eth0 netns container1

# 5. Connect veth0 to bridge
sudo ip link set veth0 master cni0
sudo ip link set veth0 up

# 6. Configure container interface
sudo ip netns exec container1 ip addr add 10.244.0.2/24 dev eth0
sudo ip netns exec container1 ip link set eth0 up
sudo ip netns exec container1 ip link set lo up

# 7. Add default route in container
sudo ip netns exec container1 ip route add default via 10.244.0.1

# 8. Enable forwarding on host
sudo sysctl -w net.ipv4.ip_forward=1

# 9. Add NAT for external access
sudo iptables -t nat -A POSTROUTING -s 10.244.0.0/24 ! -o cni0 -j MASQUERADE

# Test
echo "Testing connectivity..."
sudo ip netns exec container1 ping -c 2 10.244.0.1  # Gateway
sudo ip netns exec container1 ping -c 2 8.8.8.8     # Internet (if NAT works)

# Cleanup (run after testing)
# sudo ip netns delete container1
# sudo ip link delete cni0
# sudo iptables -t nat -D POSTROUTING -s 10.244.0.0/24 ! -o cni0 -j MASQUERADE
```

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Interface not up | No connectivity | `ip link set <if> up` |
| Missing IP address | Can't communicate | `ip addr add` in namespace |
| No route to gateway | Can't reach outside | Add default route |
| Bridge not up | veth pairs don't communicate | Bring bridge up |
| Missing NAT | Container can't reach internet | Add MASQUERADE rule |
| Forgot loopback | localhost doesn't work | `ip link set lo up` |

---

## Quiz

### Question 1
You are troubleshooting a Kubernetes node where a specific pod cannot reach the internet. You use `ip link` on the host and see `eth0` (the physical NIC) and `cni0` (the bridge), but you don't see any other interfaces. Inside the pod, you see an `eth0` interface with an IP address. What component is missing on the host side, and how does it relate to the pod's `eth0`?

<details>
<summary>Show Answer</summary>

The host is missing the host-side counterpart of the **veth (virtual Ethernet) pair**. When a container network is created, a veth pair acts like a virtual patch cable connecting the isolated container network namespace to the host's network. One end is placed inside the container (usually renamed to `eth0`), and the other end remains on the host (often attached to a bridge like `cni0`). If the host-side veth interface is missing or was accidentally deleted, packets leaving the container's `eth0` have nowhere to go, completely breaking the pod's network connectivity.

</details>

### Question 2
You have a Kubernetes pod running an Nginx web server on port 80 and a sidecar container running a log forwarding agent. You need the sidecar to fetch metrics directly from Nginx. When configuring the sidecar, you set the metrics URL to `http://localhost:80/metrics`, but your colleague argues this won't work because they are two separate containers. Who is correct and why?

<details>
<summary>Show Answer</summary>

You are correct; the `localhost` address will work perfectly. In Kubernetes, all containers within a single pod are launched into the exact same **network namespace**. Because they share this namespace, they share the same network stack, including the loopback interface (`lo`), the routing table, and the port space. From a networking perspective, the two containers act as if they are processes running on the exact same machine, allowing the sidecar to reach the Nginx container via `localhost:80` without any external routing.

</details>

### Question 3
You have manually created three network namespaces (`web`, `db`, and `cache`) on a Linux host. You want all three of them to be able to communicate with each other using the `10.0.0.0/24` subnet. You've created three veth pairs, placing one end of each into the respective namespaces. What is the most efficient way to connect the three host-side veth interfaces together so traffic can flow between any of the namespaces?

<details>
<summary>Show Answer</summary>

The most efficient approach is to create a **Linux bridge** on the host and attach all three host-side veth interfaces to it. A Linux bridge functions as a virtual Layer 2 switch in software. By connecting the host ends of the veth pairs to this bridge, you create a shared Layer 2 broadcast domain for the namespaces. When the `web` namespace sends an ARP request for the `db` namespace's IP, the bridge forwards it to all connected veth interfaces, allowing the namespaces to discover each other and communicate directly just like physical machines plugged into a physical switch.

</details>

### Question 4
You have a container connected to a host bridge (`br0`) via a veth pair. The container has an IP of `10.0.0.5`, the bridge has `10.0.0.1`, and the host's physical interface (`eth0`) has `192.168.1.100`. The container can successfully ping the bridge IP (`10.0.0.1`), but pings to `8.8.8.8` fail. The host itself can ping `8.8.8.8`. Assuming IP forwarding is enabled on the host, what specific rule needs to be added to allow the container to reach the internet?

<details>
<summary>Show Answer</summary>

You need to add a **NAT (Network Address Translation) MASQUERADE** rule using iptables on the host. Even though the packet from the container reaches the host and is forwarded out to the internet, the source IP of the packet is still the container's private IP (`10.0.0.5`). When the external server (like 8.8.8.8) tries to reply, it doesn't know how to route traffic back to `10.0.0.5` over the public internet. A MASQUERADE rule rewrites the source IP of outgoing packets to match the host's physical IP (`192.168.1.100`), ensuring return traffic comes back to the host, which then translates it back and forwards it to the container.

</details>

### Question 5
A developer complains that their newly deployed pod is stuck in the `ContainerCreating` state. You check the kubelet logs on the node and see an error: `networkPlugin cni failed to set up pod "my-app" network: failed to allocate for range 10.244.1.0/24: no IP addresses available`. Based on this error, which specific step of the container networking setup process has failed?

<details>
<summary>Show Answer</summary>

The process failed at the **IP Address Management (IPAM)** step executed by the CNI plugin. When the kubelet creates a pod, it calls the CNI plugin to handle the complex network wiring. The plugin creates the network namespace, creates the veth pair, and attaches it to the host bridge. However, before the pod can communicate, the CNI plugin must assign it a unique IP address from the node's designated subnet block. In this scenario, the subnet `10.244.1.0/24` is completely full, so the IPAM component cannot allocate a new IP, causing the CNI plugin to fail and the pod creation to halt.

</details>

---

## Hands-On Exercise

### Building Container Networks

**Objective**: Create and connect network namespaces like containers.

**Environment**: Linux system with root access

#### Part 1: Create Two Connected Namespaces

```bash
# 1. Create namespaces
sudo ip netns add ns1
sudo ip netns add ns2

# 2. Create veth pair
sudo ip link add veth-ns1 type veth peer name veth-ns2

# 3. Move to namespaces
sudo ip link set veth-ns1 netns ns1
sudo ip link set veth-ns2 netns ns2

# 4. Configure IPs
sudo ip netns exec ns1 ip addr add 10.0.0.1/24 dev veth-ns1
sudo ip netns exec ns2 ip addr add 10.0.0.2/24 dev veth-ns2

# 5. Bring up interfaces
sudo ip netns exec ns1 ip link set veth-ns1 up
sudo ip netns exec ns2 ip link set veth-ns2 up
sudo ip netns exec ns1 ip link set lo up
sudo ip netns exec ns2 ip link set lo up

# 6. Test
sudo ip netns exec ns1 ping -c 2 10.0.0.2
```

#### Part 2: Add a Bridge

```bash
# 1. Create bridge
sudo ip link add br0 type bridge
sudo ip link set br0 up
sudo ip addr add 10.0.0.254/24 dev br0

# 2. Create namespace connected to bridge
sudo ip netns add ns3
sudo ip link add veth-ns3 type veth peer name veth-br
sudo ip link set veth-ns3 netns ns3
sudo ip link set veth-br master br0
sudo ip link set veth-br up

# 3. Configure ns3
sudo ip netns exec ns3 ip addr add 10.0.0.3/24 dev veth-ns3
sudo ip netns exec ns3 ip link set veth-ns3 up
sudo ip netns exec ns3 ip link set lo up
sudo ip netns exec ns3 ip route add default via 10.0.0.254

# 4. Test connectivity
sudo ip netns exec ns3 ping -c 2 10.0.0.254  # Bridge
ping -c 2 10.0.0.3  # From host
```

#### Part 3: Inspect Real Container Networks

```bash
# If Docker is installed:
# 1. Check docker0 bridge
ip addr show docker0

# 2. Run a container
docker run -d --name test nginx

# 3. Find veth pair
ip link show type veth

# 4. Check bridge members
bridge link show

# 5. See inside container
docker exec test ip addr
docker exec test ip route

# 6. Cleanup
docker rm -f test
```

#### Cleanup

```bash
sudo ip netns delete ns1
sudo ip netns delete ns2
sudo ip netns delete ns3
sudo ip link delete br0
```

### Success Criteria

- [ ] Created and connected two namespaces
- [ ] Verified ping works between namespaces
- [ ] Set up a bridge connecting namespaces
- [ ] Understand the veth + bridge pattern
- [ ] (Docker) Inspected real container networking

---

## Key Takeaways

1. **Network namespaces isolate** — Each has its own interfaces, routes, firewall rules

2. **veth pairs connect** — One end in container, one end on host/bridge

3. **Bridges are virtual switches** — Connect multiple containers at Layer 2

4. **CNI automates this** — Creates namespaces, veth pairs, assigns IPs for pods

5. **Pod containers share namespace** — Why localhost works between them

---

## What's Next?

In **Module 3.4: iptables & netfilter**, you'll learn how Linux filters and manipulates packets—the foundation of Kubernetes Services and Network Policies.

---

## Further Reading

- [Linux Network Namespaces](https://man7.org/linux/man-pages/man7/network_namespaces.7.html)
- [CNI Specification](https://github.com/containernetworking/cni/blob/master/SPEC.md)
- [Kubernetes Networking Model](https://kubernetes.io/docs/concepts/cluster-administration/networking/)
- [Container Networking Deep Dive](https://iximiuz.com/en/posts/container-networking-is-simple/)