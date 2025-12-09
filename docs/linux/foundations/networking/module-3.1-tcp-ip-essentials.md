# Module 3.1: TCP/IP Essentials

> **Linux Foundations** | Complexity: `[MEDIUM]` | Time: 30-35 min

## Prerequisites

Before starting this module:
- **Required**: Basic understanding of what networks are
- **Helpful**: [Module 1.1: Kernel & Architecture](../system-essentials/module-1.1-kernel-architecture.md)

---

## Why This Module Matters

Every Kubernetes pod, every service, every ingress request—they all ride on TCP/IP. When networking doesn't work, you need to understand the fundamentals.

Understanding TCP/IP helps you:

- **Debug connectivity** — Why can't my pod reach this service?
- **Understand Kubernetes networking** — How do Services, NodePorts, LoadBalancers work?
- **Troubleshoot performance** — Is it latency? Packet loss? Wrong routing?
- **Configure networks** — Subnets, CIDR, routes

When `curl` hangs, when packets disappear, when latency spikes—you need TCP/IP knowledge.

---

## Did You Know?

- **TCP was designed to survive nuclear war** — The Internet's predecessor, ARPANET, was funded by DARPA. TCP/IP's ability to route around failures comes from this military origin.

- **The 3-way handshake (SYN, SYN-ACK, ACK) takes 1.5 round trips** — This is why TCP connections have higher latency than UDP. For a 100ms RTT, that's 150ms just to establish a connection.

- **Linux can handle millions of concurrent TCP connections** — With proper tuning (see sysctl settings), a single Linux server can maintain millions of connections. The kernel's networking stack is remarkably efficient.

- **IP addresses are just 32 bits (IPv4) or 128 bits (IPv6)** — That's it! All the routing magic happens with these simple numbers. IPv4's 32 bits give us ~4.3 billion addresses, which we've exhausted, hence IPv6.

---

## The Network Stack

### OSI Model vs TCP/IP Model

```
┌─────────────────────────────────────────────────────────────────┐
│           OSI Model          │         TCP/IP Model            │
├─────────────────────────────────────────────────────────────────┤
│  7. Application              │                                 │
│  6. Presentation             │  Application                    │
│  5. Session                  │  (HTTP, DNS, SSH)               │
├─────────────────────────────────────────────────────────────────┤
│  4. Transport                │  Transport                      │
│     (TCP, UDP)               │  (TCP, UDP)                     │
├─────────────────────────────────────────────────────────────────┤
│  3. Network                  │  Internet                       │
│     (IP)                     │  (IP)                           │
├─────────────────────────────────────────────────────────────────┤
│  2. Data Link                │                                 │
│  1. Physical                 │  Network Access                 │
│     (Ethernet, WiFi)         │  (Ethernet)                     │
└─────────────────────────────────────────────────────────────────┘
```

### How Data Flows

```
Application: "GET /index.html HTTP/1.1"
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Transport Layer (TCP)                                         │
│ + Source Port: 54321                                         │
│ + Dest Port: 80                                              │
│ + Sequence Number, ACK, Flags                                │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Network Layer (IP)                                           │
│ + Source IP: 192.168.1.100                                   │
│ + Dest IP: 10.0.0.50                                        │
│ + TTL, Protocol                                              │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Data Link Layer (Ethernet)                                   │
│ + Source MAC: aa:bb:cc:dd:ee:ff                             │
│ + Dest MAC: 11:22:33:44:55:66                               │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
     Wire / Radio / Fiber
```

---

## IP Addressing

### IPv4 Address Structure

```
IP Address: 192.168.1.100
Binary:     11000000.10101000.00000001.01100100

Subnet Mask: 255.255.255.0 (or /24)
Binary:      11111111.11111111.11111111.00000000

Network:     192.168.1.0   (first 24 bits)
Host:        .100          (last 8 bits)
Broadcast:   192.168.1.255 (all host bits = 1)
```

### CIDR Notation

| CIDR | Subnet Mask | Hosts | Common Use |
|------|-------------|-------|------------|
| /32 | 255.255.255.255 | 1 | Single host |
| /24 | 255.255.255.0 | 254 | Small network |
| /16 | 255.255.0.0 | 65,534 | Medium network |
| /8 | 255.0.0.0 | 16M | Large network |

### Private IP Ranges

| Range | CIDR | Class | Use |
|-------|------|-------|-----|
| 10.0.0.0 - 10.255.255.255 | 10.0.0.0/8 | A | Large orgs |
| 172.16.0.0 - 172.31.255.255 | 172.16.0.0/12 | B | Medium orgs |
| 192.168.0.0 - 192.168.255.255 | 192.168.0.0/16 | C | Home/small |

### Kubernetes IP Ranges

```
┌─────────────────────────────────────────────────────────────────┐
│                    KUBERNETES NETWORKING                         │
│                                                                  │
│  Pod Network:       10.244.0.0/16                               │
│  Service Network:   10.96.0.0/12                                │
│  Node Network:      192.168.1.0/24                              │
│                                                                  │
│  Pod on Node 1:     10.244.1.15/24                             │
│  Pod on Node 2:     10.244.2.23/24                             │
│  ClusterIP Service: 10.96.0.1                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Viewing IP Configuration

```bash
# Show all interfaces
ip addr

# Show specific interface
ip addr show eth0

# Legacy command
ifconfig

# Show IPv4 only
ip -4 addr

# Brief format
ip -br addr
```

---

## TCP vs UDP

### TCP: Reliable, Ordered

```
┌──────────────────────────────────────────────────────────────────┐
│                    TCP 3-WAY HANDSHAKE                           │
│                                                                  │
│    Client                                         Server         │
│      │                                              │            │
│      │────────── SYN (seq=100) ────────────────────▶│            │
│      │                                              │            │
│      │◀───────── SYN-ACK (seq=300, ack=101) ───────│            │
│      │                                              │            │
│      │────────── ACK (seq=101, ack=301) ───────────▶│            │
│      │                                              │            │
│      │         Connection Established               │            │
│      │                                              │            │
│      │◀═══════════ Data Transfer ═══════════════════│            │
│      │                                              │            │
│      │────────── FIN ──────────────────────────────▶│            │
│      │◀───────── FIN-ACK ───────────────────────────│            │
│      │────────── ACK ──────────────────────────────▶│            │
│      │                                              │            │
└──────────────────────────────────────────────────────────────────┘
```

TCP Features:
- **Reliable** — Retransmits lost packets
- **Ordered** — Packets delivered in sequence
- **Connection-oriented** — Handshake required
- **Flow control** — Sender adjusts to receiver capacity
- **Congestion control** — Adapts to network conditions

### UDP: Fast, Simple

```
┌──────────────────────────────────────────────────────────────────┐
│                         UDP                                       │
│                                                                   │
│    Client                                         Server          │
│      │                                              │             │
│      │────────── Data ─────────────────────────────▶│             │
│      │────────── Data ─────────────────────────────▶│             │
│      │────────── Data ─────────────────────────────▶│             │
│      │                                              │             │
│    No handshake, no acknowledgments, no guarantees               │
└──────────────────────────────────────────────────────────────────┘
```

UDP Features:
- **Fast** — No connection overhead
- **Simple** — Just send data
- **Unreliable** — Packets can be lost
- **Unordered** — Packets can arrive out of order
- **No flow control** — Sender can overwhelm receiver

### When to Use Which

| TCP | UDP |
|-----|-----|
| HTTP/HTTPS | DNS (queries) |
| SSH | DHCP |
| Database connections | Video streaming |
| API calls | Gaming |
| File transfer | VoIP |

---

## Routing

### How Routing Works

```
┌─────────────────────────────────────────────────────────────────┐
│                      ROUTING DECISION                            │
│                                                                  │
│  Packet destined for: 10.0.0.50                                 │
│                                                                  │
│  Routing Table:                                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ Destination     Gateway         Interface    Metric    │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │ 192.168.1.0/24  0.0.0.0         eth0         0        │     │
│  │ 10.0.0.0/8      192.168.1.1     eth0         100      │ ←   │
│  │ 0.0.0.0/0       192.168.1.1     eth0         0        │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Match: 10.0.0.0/8 → Send to gateway 192.168.1.1 via eth0       │
└─────────────────────────────────────────────────────────────────┘
```

### Viewing Routes

```bash
# Show routing table
ip route

# Legacy command
route -n
netstat -rn

# Example output:
# default via 192.168.1.1 dev eth0 proto dhcp metric 100
# 10.244.0.0/16 via 10.244.0.0 dev cni0
# 192.168.1.0/24 dev eth0 proto kernel scope link src 192.168.1.100
```

### Kubernetes Routing

```bash
# Pod-to-pod routing on same node
10.244.1.0/24 dev cni0  # Local pods

# Pod-to-pod routing across nodes (example with Flannel)
10.244.2.0/24 via 192.168.1.102 dev eth0  # Pods on node2

# Default route for external traffic
default via 192.168.1.1 dev eth0
```

### Adding Routes

```bash
# Add route
sudo ip route add 10.0.0.0/8 via 192.168.1.1

# Add default gateway
sudo ip route add default via 192.168.1.1

# Delete route
sudo ip route del 10.0.0.0/8

# Routes are not persistent! Use netplan/NetworkManager for persistence
```

---

## Ports and Sockets

### Port Ranges

| Range | Name | Use |
|-------|------|-----|
| 0-1023 | Well-known | System services (requires root) |
| 1024-49151 | Registered | Applications |
| 49152-65535 | Dynamic/Ephemeral | Client connections |

### Common Ports

| Port | Service | Protocol |
|------|---------|----------|
| 22 | SSH | TCP |
| 53 | DNS | UDP/TCP |
| 80 | HTTP | TCP |
| 443 | HTTPS | TCP |
| 6443 | Kubernetes API | TCP |
| 10250 | Kubelet | TCP |
| 2379 | etcd | TCP |

### Viewing Connections

```bash
# Show all listening ports
ss -tlnp
# t=TCP, l=listening, n=numeric, p=process

# Show all connections
ss -tanp

# Legacy netstat
netstat -tlnp

# Find what's using a port
ss -tlnp | grep :80
lsof -i :80
```

---

## Practical Diagnostics

### Connectivity Testing

```bash
# Basic ping
ping -c 4 8.8.8.8

# TCP connectivity test
nc -zv 10.0.0.50 80
# or
curl -v telnet://10.0.0.50:80

# Test with timeout
timeout 5 bash -c "</dev/tcp/10.0.0.50/80" && echo "Open" || echo "Closed"
```

### Path Discovery

```bash
# Trace route
traceroute 8.8.8.8
# or
mtr 8.8.8.8

# TCP traceroute (for firewalled networks)
traceroute -T -p 443 8.8.8.8
```

### Interface Statistics

```bash
# Interface stats
ip -s link

# Detailed stats
cat /proc/net/dev

# Watch in real-time
watch -n1 'cat /proc/net/dev'
```

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Wrong subnet mask | Can't reach hosts | Verify CIDR notation |
| Missing default route | Can't reach internet | Add default gateway |
| Firewall blocking | Connection refused/timeout | Check iptables/firewalld |
| Port already in use | Service won't start | Find and stop conflicting service |
| MTU mismatch | Connection hangs mid-transfer | Ensure consistent MTU |
| DNS but no route | Resolves but can't connect | Check routing table |

---

## Quiz

### Question 1
What's the difference between 192.168.1.0/24 and 192.168.1.0/16?

<details>
<summary>Show Answer</summary>

- **/24** = 255.255.255.0 = 256 addresses (192.168.1.0 - 192.168.1.255)
- **/16** = 255.255.0.0 = 65,536 addresses (192.168.0.0 - 192.168.255.255)

The /24 network is a subset of the /16 network. /24 covers just the .1.x subnet, /16 covers all .x.x subnets.

</details>

### Question 2
Why does TCP use a 3-way handshake?

<details>
<summary>Show Answer</summary>

The 3-way handshake ensures:
1. **Client can send** (SYN received by server)
2. **Server can send** (SYN-ACK received by client)
3. **Both agree on sequence numbers** (synchronized)

This establishes a reliable, bidirectional connection with agreed-upon starting sequence numbers for ordered delivery.

</details>

### Question 3
When would you use UDP instead of TCP?

<details>
<summary>Show Answer</summary>

Use UDP when:
- **Speed matters more than reliability** (gaming, live video)
- **You handle reliability yourself** (DNS, custom protocols)
- **Single request-response** (DNS queries)
- **Broadcast/multicast** (UDP only)
- **Lower overhead needed** (IoT, sensors)

UDP has no connection setup overhead and no retransmission delay.

</details>

### Question 4
What does `ip route add default via 192.168.1.1` do?

<details>
<summary>Show Answer</summary>

It adds a **default gateway**. Any packet whose destination doesn't match a more specific route will be sent to 192.168.1.1.

This is how your machine knows where to send packets destined for the internet or any unknown network.

</details>

### Question 5
How do you find what process is listening on port 443?

<details>
<summary>Show Answer</summary>

```bash
# Modern way
ss -tlnp | grep :443

# Legacy
netstat -tlnp | grep :443

# Using lsof
lsof -i :443

# Sample output:
# LISTEN  0  128  *:443  *:*  users:(("nginx",pid=1234,fd=6))
```

</details>

---

## Hands-On Exercise

### TCP/IP Exploration

**Objective**: Understand IP configuration, routing, and connectivity testing.

**Environment**: Any Linux system

#### Part 1: IP Configuration

```bash
# 1. View your IP addresses
ip addr

# 2. Note your main interface name and IP
ip -4 -br addr

# 3. View interface details
ip addr show eth0 || ip addr show ens33 || ip addr show enp0s3

# 4. Check MAC address
ip link show | grep ether
```

#### Part 2: Routing

```bash
# 1. View routing table
ip route

# 2. Find default gateway
ip route | grep default

# 3. Trace route to internet
traceroute -m 10 8.8.8.8 || tracepath 8.8.8.8

# 4. Check which interface reaches a destination
ip route get 8.8.8.8
```

#### Part 3: Connectivity Testing

```bash
# 1. Ping local gateway
GATEWAY=$(ip route | grep default | awk '{print $3}')
ping -c 4 $GATEWAY

# 2. Ping external
ping -c 4 8.8.8.8

# 3. Test TCP connectivity
nc -zv google.com 443 || timeout 5 bash -c "</dev/tcp/google.com/443" && echo "Open"

# 4. Time a connection
time curl -s -o /dev/null https://google.com
```

#### Part 4: Port Investigation

```bash
# 1. List listening ports
ss -tlnp

# 2. List all TCP connections
ss -tanp | head -20

# 3. Check a specific port
ss -tlnp | grep :22

# 4. Count connections by state
ss -tan | awk 'NR>1 {print $1}' | sort | uniq -c
```

#### Part 5: Interface Statistics

```bash
# 1. View packet counts
ip -s link show eth0 || ip -s link show $(ip route | grep default | awk '{print $5}')

# 2. Check for errors
ip -s link | grep -A2 errors

# 3. View detailed stats
cat /proc/net/dev
```

### Success Criteria

- [ ] Identified your IP address and subnet
- [ ] Found your default gateway
- [ ] Successfully traced a route
- [ ] Tested TCP connectivity
- [ ] Listed listening ports on your system

---

## Key Takeaways

1. **TCP/IP is the foundation** — Every network communication in Kubernetes uses it

2. **CIDR defines networks** — /24, /16, /8 determine how many hosts and which IPs

3. **Routing decides the path** — The routing table determines where packets go

4. **TCP vs UDP tradeoffs** — Reliability vs speed, choose based on use case

5. **Diagnostic tools are essential** — ip, ss, ping, traceroute are your friends

---

## What's Next?

In **Module 3.2: DNS in Linux**, you'll learn how names become IP addresses—essential for understanding Kubernetes service discovery.

---

## Further Reading

- [TCP/IP Illustrated](https://www.amazon.com/TCP-Illustrated-Vol-Addison-Wesley-Professional/dp/0201633469) by W. Richard Stevens
- [Linux Network Administrator's Guide](https://tldp.org/LDP/nag2/index.html)
- [iproute2 Documentation](https://wiki.linuxfoundation.org/networking/iproute2)
- [Kubernetes Networking Guide](https://kubernetes.io/docs/concepts/cluster-administration/networking/)
