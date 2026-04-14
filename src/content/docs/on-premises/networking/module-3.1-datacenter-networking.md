---
title: "Module 3.1: Datacenter Network Architecture"
slug: on-premises/networking/module-3.1-datacenter-networking
sidebar:
  order: 2
---

> **Complexity**: `[COMPLEX]` | Time: 60 minutes
>
> **Prerequisites**: [Module 2.1: Datacenter Fundamentals](/on-premises/provisioning/module-2.1-datacenter-fundamentals/), [Linux: TCP/IP Essentials](/linux/foundations/networking/module-3.1-tcp-ip-essentials/)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Design** spine-leaf network topologies that mathematically eliminate east-west traffic bottlenecks by applying non-blocking Clos network principles.
2. **Implement** sophisticated VLAN boundaries, link aggregation, and MTU jumbo frame configurations to optimize hardware performance for Kubernetes overlay networks.
3. **Compare** the performance implications of DPDK, SR-IOV, and next-generation SmartNICs/DPUs when scaling high-throughput datacenter workloads.
4. **Evaluate** the BGP control plane integration between modern Container Network Interfaces (like Calico and Cilium) and the physical Top-of-Rack switches.
5. **Diagnose** complex network congestion issues caused by improper oversubscription ratios, MTU mismatches, and spanning-tree reconvergence events in multi-rack architectures.

---

## Why This Module Matters

On October 4, 2021, Facebook (Meta) suffered a catastrophic global outage that erased billions of dollars in market capitalization and caused an estimated sixty million dollars in lost ad revenue within a span of six hours. The root cause was not a complex software bug, but a routine BGP configuration update that mistakenly withdrew all routing information for the company's authoritative DNS servers. Because the datacenter network could no longer advertise its internal routes to the global internet, Facebook vanished from the web.

Even worse, the datacenter network's design meant that internal systems relied on the same routing infrastructure. Physical access to server rooms was blocked because the electronic badge readers could not reach the authorization databases over the isolated network. Engineers with physical keys had to use angle grinders to access the hardware cages. This incident starkly illustrates a foundational truth: the datacenter network is the absolute bedrock of application availability. 

In public cloud environments, engineers rarely consider switch oversubscription, uplink bandwidth, or BGP route reflection; the cloud provider abstracts these complexities away. However, in bare-metal Kubernetes deployments, the network architecture is entirely your responsibility. A poorly designed Top-of-Rack connection or an incorrect MTU setting can silently drop packets, trigger TCP retransmissions, and degrade a high-performance microservice architecture into an unresponsive bottleneck. You must design for the traffic you will have during peak load, not just the traffic you have on day one.

Consider a media streaming company that deployed a 60-node Kubernetes cluster connected to a single pair of ToR switches. When they deployed a video transcoding pipeline generating 8 Gbps of east-west traffic, their 6:1 oversubscription ratio became a severe bottleneck. Packet drops hit 3%, TCP retransmissions spiked, and video latency jumped from 200ms to 4 seconds, causing buffering and a revenue drop of $12,000/hour. Fixing it required adding spine switches, upgrading to 25GbE server connections, and implementing a proper leaf-spine topology with ECMP (Equal-Cost Multi-Path) routing. The migration took 3 weeks of weekend maintenance windows. Total cost: $85,000 in new hardware plus $40,000 in engineering time. The CTO's postmortem note: "We designed our network for the workload we had, not the workload we would have in 6 months."

> **The Highway Analogy**
>
> A datacenter network is like a highway system. The ToR switches are local roads (one per rack). The spine switches are highways connecting all the local roads. If your local roads are 2-lane but your highway is 8-lane, traffic flows. But if your highway is only 2-lane while every local road feeds 10 lanes of traffic, you get gridlock at the on-ramps. Oversubscription ratio is the ratio of total local road capacity to highway capacity.

---

## The Evolution of Datacenter Topologies

### Why Not Traditional 3-Tier?

The traditional datacenter network (access → aggregation → core) was designed for north-south traffic (client → server). Kubernetes generates massive east-west traffic (pod → pod, pod → service, pod → storage). The aggregation layer inherently becomes a severe bottleneck.

```mermaid
flowchart TD
    subgraph Traditional 3-Tier [Avoid for K8s]
    C[Core Switch] --> A1[Aggregation 1]
    C --> A2[Aggregation 2]
    A1 --> T1[ToR 1]
    A1 --> T2[ToR 2]
    A1 --> T3[ToR 3]
    A2 --> T4[ToR 4]
    A2 --> T5[ToR 5]
    end
```

**Problem:** East-west traffic between ToR 1 and ToR 5 must traverse both aggregation and core layers. This structural limitation guarantees high latency and aggregation overload during peak Kubernetes scaling events.

### Spine-Leaf Architecture

```mermaid
flowchart TD
    subgraph Spine-Leaf Topology [Recommended for K8s]
    S1[Spine 1] --- L1[Leaf 1 ToR]
    S1 --- L2[Leaf 2 ToR]
    S1 --- L3[Leaf 3 ToR]
    S1 --- L4[Leaf 4 ToR]
    S2[Spine 2] --- L1
    S2 --- L2
    S2 --- L3
    S2 --- L4
    S3[Spine 3] --- L1
    S3 --- L2
    S3 --- L3
    S3 --- L4
    end
```

**Benefits of Spine-Leaf:**
- Every leaf connects to EVERY spine (full mesh).
- Any-to-any traffic guarantees a maximum of 2 hops (leaf → spine → leaf).
- Equal-cost paths allow ECMP to load-balance seamlessly across all spines.
- Capacity can be added effortlessly by adding more spines (horizontal scaling).

> **Pause and predict**: Looking at the spine-leaf diagram above, count the number of hops a packet takes from a server in rack 1 to a server in rack 4. Now count the hops in the traditional 3-tier topology. Why does this difference matter for Kubernetes east-west traffic?

Spine-leaf topology is an application of the Clos network architecture, originally described by Charles Clos in his 1953 Bell System Technical Journal paper 'A Study of Non-Blocking Switching Networks', vol. 32, pp. 406-424. The fundamental genius of a Clos network is that it provides a strictly non-blocking interconnect fabric. By structuring the network in a folded multi-stage array, every input can reach every output without contention, assuming sufficient interconnect links are provisioned. 

- **The term "Top of Rack" is becoming misleading** as many modern deployments use "End of Row" (EoR) or "Middle of Row" (MoR) switch placements. But "ToR" persists as the industry vocabulary regardless of physical placement.

While many vendors suggest that the dominant server-to-ToR link speed in modern hyperscale datacenters is 25 GbE, with ToR-to-spine links at 100 GbE, this remains an unverified generalization. No single authoritative standards body mandates this combination, and the explosive growth of machine learning workloads is rapidly pushing hyperscale environments toward massive 400 GbE and 800 GbE deployments. 

### Spine-Leaf Sizing

| Component | Speed | Ports | Use Case |
|-----------|-------|-------|----------|
| **Leaf (ToR)** | 25GbE down, 100GbE up | 48x 25G + 6x 100G | Per-rack switch |
| **Spine** | 100GbE | 32x 100G | Interconnect fabric |
| **Border leaf** | 100GbE down, 400GbE up | 48x 100G + 8x 400G | WAN/internet uplinks |

**Example Calculation:**
- Leaf Downlink: 48 x 25GbE = 1,200 Gbps
- Leaf Uplink: 6 x 100GbE = 600 Gbps
- Oversubscription ratio = 1,200 / 600 = **2:1**

For Kubernetes east-west heavy workloads, target **2:1 or better** (3:1 is acceptable for light workloads). Avoid **5:1+** as it will predictably cause packet drops under load.

To support these massive backbone speeds, IEEE standards have continually evolved. 100 Gigabit Ethernet is standardized under IEEE 802.3ba-2010, ratified June 17, 2010. Pushing the boundary further, 800 Gigabit Ethernet is standardized under IEEE 802.3df-2024, approved February 16, 2024. Looking forward, the 1.6 Terabit Ethernet standard (IEEE 802.3dj) targeting 200 Gb/s per lane was originally slated for 2026 but is at risk of schedule slippage due to extreme signal integrity challenges.

---

## Virtualization and Encapsulation

### Overcoming VLAN Limits with VXLAN

IEEE 802.1Q VLAN tagging supports a maximum of 4,094 usable VLAN IDs (a 12-bit field; IDs 0 and 4095 are reserved). In multi-tenant cloud environments, this limitation was catastrophic. To overcome this, VXLAN (Virtual eXtensible LAN) is defined by IETF RFC 7348, published August 2014. VXLAN uses a 24-bit Virtual Network Identifier (VNI), supporting up to 16,777,216 (~16 million) logical network segments. 

To achieve this, VXLAN encapsulates Layer-2 Ethernet frames in UDP/IP packets and uses IANA-assigned UDP destination port 4789. By encapsulating the traffic in UDP, the datacenter's core switches can perform Equal-Cost Multi-Path (ECMP) load balancing by hashing the diverse source ports dynamically generated by the encapsulation engine.

### Modern Overlays: EVPN and GENEVE

While VXLAN provided the data plane encapsulation, it initially lacked a standard control plane, relying instead on inefficient multicast flooding to learn MAC addresses. To solve this, the EVPN (Ethernet VPN) control plane is defined in IETF RFC 7432 (BGP MPLS-Based Ethernet VPN), published February 2015. 

EVPN-VXLAN integration (using EVPN as a control plane over a VXLAN data plane) is specified in RFC 8365, 'A Network Virtualization Overlay Solution Using Ethernet VPN (EVPN)'. This combination allows switches to use BGP to actively share MAC and IP reachability information, completely eliminating broadcast storms. Seeking even more flexibility, GENEVE (Generic Network Virtualization Encapsulation) is defined in IETF RFC 8926, published November 2020. Unlike VXLAN, GENEVE features an extensible option header that allows for the insertion of rich metadata, such as telemetry and security tags.

---

## VLAN Design for Kubernetes

### Recommended VLANs

```mermaid
graph TD
    subgraph VLAN Architecture
    V10["VLAN 10: Management<br>10.0.10.0/24"] --- V10a["BMC/IPMI, Jump hosts"]
    V20["VLAN 20: K8s Node<br>10.0.20.0/22"] --- V20a["kubelet, API, etcd, Pods"]
    V30["VLAN 30: Storage<br>10.0.30.0/24 (MTU 9000)"] --- V30a["Ceph, NFS, iSCSI"]
    V40["VLAN 40: PXE<br>10.0.40.0/24 (Isolated)"] --- V40a["DHCP, TFTP, HTTP"]
    V50["VLAN 50: External<br>10.0.50.0/24"] --- V50a["Load balancer VIPs"]
    end
```

> **Stop and think**: You are designing VLANs for a new cluster. A colleague suggests putting storage traffic (Ceph replication) and Kubernetes pod traffic on the same VLAN to simplify the network. What problems would this cause during a Ceph rebalancing event, and how would it affect application latency?

### Server NIC Assignment

To guarantee high availability, physical server interfaces are grouped. Link Aggregation Control Protocol (LACP) is defined in IEEE 802.3ad, added to the IEEE 802.3 standard in March 2000, and later incorporated into IEEE 802.3-2018. 

```mermaid
flowchart LR
    subgraph Server NIC Configuration
    N0[NIC 0: 25GbE] --> B["Bond (LACP Active-Active 50Gbps)"]
    N1[NIC 1: 25GbE] --> B
    B --> T["Trunk Port: VLANs 20, 30, 50"]
    N2[NIC 2: 1GbE] --> A1["Access Port: VLAN 10 (Mgmt)"]
    N3[BMC NIC: 1GbE] --> A2["Access Port: VLAN 10 (IPMI)"]
    end
```

**Linux Bond Setup (Ubuntu netplan):**

```yaml
# /etc/netplan/01-bond.yaml
network:
  version: 2
  bonds:
    bond0:
      interfaces: [eno1, eno2]
      parameters:
        mode: 802.3ad
        lacp-rate: fast
        transmit-hash-policy: layer3+4
  vlans:
    vlan20:
      id: 20
      link: bond0
      addresses: [10.0.20.10/22]
    vlan30:
      id: 30
      link: bond0
      addresses: [10.0.30.10/24]
      mtu: 9000
```

---

## MTU Configuration

### Why Jumbo Frames Matter

Default Ethernet MTU is 1500 bytes. Kubernetes overlay networks (VXLAN, Geneve) add significant headers:

```mermaid
flowchart LR
    subgraph Standard MTU 1500 Bytes
    direction LR
    A1[VXLAN 50B] --- A2[Inner Ethernet 14B] --- A3[IP 20B] --- A4[TCP 20B] --- A5[Payload 1396B]
    end
    subgraph Jumbo MTU 9000 Bytes
    direction LR
    B1[VXLAN 50B] --- B2[Inner Ethernet 14B] --- B3[IP 20B] --- B4[TCP 20B] --- B5[Payload 8896B]
    end
```

- **Standard MTU Overhead**: 104 bytes (7% of each packet wasted).
- **Jumbo MTU Overhead**: 104 bytes (1.2% of each packet wasted).

**With jumbo frames:**
- 6x less header overhead per byte of data.
- Fewer packets per data transfer resulting in less CPU interrupt load.
- Absolutely critical for high-throughput storage traffic (Ceph, NFS).

**IMPORTANT:** ALL devices in the path must support jumbo frames: Server NICs, bonds, VLANs, switches, and routers. A single device with an MTU of 1500 causes fragmentation and an instant performance drop.

### MTU Settings by Network

| Network | MTU | Reason |
|---------|-----|--------|
| Management (VLAN 10) | 1500 | Low traffic, no overlay |
| K8s Node (VLAN 20) | 9000 or 1500 | 9000 if CNI uses VXLAN overlay; 1500 if native routing |
| Storage (VLAN 30) | 9000 | Always jumbo for storage performance |
| PXE (VLAN 40) | 1500 | PXE/TFTP doesn't benefit from jumbo |
| External (VLAN 50) | 1500 | Internet-facing, standard MTU |

```bash
# Verify MTU on a path
ping -c 4 -M do -s 8972 10.0.30.1
# -c 4: limit to 4 packets
# -M do: don't fragment
# -s 8972: 8972 + 28 (IP+ICMP header) = 9000
# If this works, the path supports MTU 9000
# If "Message too long", something in the path has a smaller MTU

# Check interface MTU
ip link show bond0

# Set MTU on Linux dynamically
ip link set bond0 mtu 9000
```

---

## Hardware Acceleration and SmartNICs

To cope with massive data throughput without saturating the host CPU, the industry relies heavily on hardware acceleration. DPDK (Data Plane Development Kit) version 26.03.0 is the March 2026 release, following the project's YY.MM.patch versioning scheme. DPDK bypasses the Linux kernel networking stack entirely to process packets directly in user space. Alternatively, SR-IOV (Single Root I/O Virtualization) is a PCI-SIG specification that allows a single PCIe Physical Function (PF) to present multiple Virtual Functions (VFs) to the host, enabling near-native network performance for VMs without hypervisor involvement.

For machine learning and AI workloads, Remote Direct Memory Access (RDMA) is absolutely critical. RoCE v2 (RDMA over Converged Ethernet version 2) encapsulates RDMA transport in UDP/IP datagrams, making it routable across L3 networks (unlike RoCE v1 which was L2-only). 

To offload these complex encapsulation and security tasks from the main x86 CPU, specialized Data Processing Units (DPUs) are utilized. The NVIDIA BlueField-3 DPU is a 400 Gb/s infrastructure compute platform with 16 Arm A78 cores, up to 32 GB DDR5, and PCIe Gen5. Similarly, Intel co-developed the Mount Evans IPU (E2000 chip) with Google; it integrates 16 Arm Neoverse N1 cores and 200 Gb/s Ethernet connectivity.

**Comparing Performance Implications:**
- **DPDK**: Yields extremely high packet rates by bypassing the kernel, but consumes expensive x86 CPU cores merely for polling network queues.
- **SR-IOV**: Provides near-line-rate performance with virtually zero x86 CPU overhead by passing physical interfaces directly to pods, but sacrifices SDN flexibility (e.g., live migration and software overlays become difficult).
- **SmartNICs/DPUs**: Fully offload virtual switching, overlay encapsulation, and security to dedicated Arm cores on the NIC. This maintains full SDN flexibility while reclaiming 100% of x86 CPU cores for the actual application workload.

> **Stop and think**: If RoCE v2 utilizes UDP encapsulation for routing across a Layer 3 fabric, how does the network infrastructure guarantee the lossless delivery required by RDMA? What mechanisms must the Top-of-Rack switches implement to prevent UDP packet drops during microbursts?

---

## Modern Switch Operating Systems and SDN

Datacenter switches have evolved from monolithic black boxes into open compute platforms. SONiC (Software for Open Networking in the Cloud) governance was transferred from Microsoft to the Linux Foundation on April 14, 2022. It follows a strict release cadence, as SONiC publishes two major releases per year on a biannual cadence (approximately May and November). 

Open-source routing daemons power these platforms. FRRouting (FRR) 10.6.0 is the latest stable release, published March 26, 2026, with 1,585 commits from 86 developers. For virtual switching at the host level, Open vSwitch (OVS) 3.7.0 is the latest stable release, released February 16, 2026. 

Commercial vendors also maintain massive footprints with highly robust OS branches. Arista EOS 4.35.2F is the version referenced in Arista's current (2026) product documentation. Similarly, Cisco NX-OS 10.5(5)M for the Nexus 9000 series was released March 16, 2026 and is the latest release in the 10.5 maintenance train. 

In the realm of Software-Defined Networking (SDN) and fabric management, VMware NSX (rebranded from VMware NSX-T Data Center) version 4.2.3 is the latest release as of 2026. For multivendor intent-based fabric management, Juniper Apstra 6.x is the current major release line. Finally, OpenFlow 1.5.1 (protocol version 0x06) is the latest publicly available OpenFlow specification published by the Open Networking Foundation (ONF).

---

## L2 vs L3: Where to Route

Use of BGP as the sole routing protocol for large-scale datacenter fabrics is documented in IETF RFC 7938, published August 2015. 

### L2 Domain Boundaries

```mermaid
graph TD
    subgraph Small Cluster: Less than 3 Racks
    R1[Rack A] --- V[Single L2 Domain / VLAN]
    R2[Rack B] --- V
    R3[Rack C] --- V
    end
    subgraph Large Cluster: 5+ Racks
    L1["Rack A (VLAN 20a)"] --- BGP((L3 Routing - BGP between leaves))
    L2["Rack B (VLAN 20b)"] --- BGP
    L3["Rack C (VLAN 20c)"] --- BGP
    end
```

**Rule of thumb:**
- **< 200 nodes, < 3 racks:** L2 (single broadcast domain) is fine. Simple ARP works natively.
- **> 200 nodes or > 5 racks:** L3 routing between racks with BGP. Each rack receives its own /24 or /25 subnet.
- Broadcast storms can propagate across all racks if left as a massive flat L2 domain. L3 isolation limits failures to a single boundary.

---

## CNI Integration with Datacenter Fabric

> **Pause and predict**: Your cluster uses VXLAN overlay networking (the default for most CNIs). Each packet adds 50 bytes of overhead. At 1 million packets per second (common for microservices), how much bandwidth is wasted on headers alone? Would switching to BGP native routing eliminate this overhead?

By leveraging standard BGP capabilities, modern Container Network Interfaces can seamlessly peer with your ToR switches. Cilium CNI version 1.19 is the latest stable minor release as of early 2026; version 1.20.0-pre.1 is available as a pre-release as of April 1, 2026. Similarly, Calico CNI version 3.31.4 is the latest stable release, released February 20, 2026.

### Calico BGP Mode (No Overlay)

The diagram below shows Calico peering directly with the datacenter ToR switches via BGP. This eliminates the VXLAN encapsulation layer entirely -- pod IPs become first-class citizens in the datacenter routing table, meaning external systems can reach pods without NAT or proxy:

```mermaid
flowchart TD
    subgraph Calico BGP with Datacenter Fabric
    S1[Spine 1] --> L1[Leaf 1]
    S1 --> L2[Leaf 2]
    S2[Spine 2] --> L1
    S2 --> L2
    L1 --> N1["Node 1<br>Calico BGP<br>Pod: 10.244.1.0/24"]
    L2 --> N2["Node 2<br>Calico BGP<br>Pod: 10.244.2.0/24"]
    N1 -. BGP Peer .- L1
    N2 -. BGP Peer .- L2
    end
```

**Result:** Pod IPs are natively routable on the datacenter network. No overlay (VXLAN/Geneve) means zero encapsulation overhead. External services can communicate with pods directly because leaf switches possess precise routes to the pod CIDRs.

```yaml
# Calico BGPConfiguration
apiVersion: projectcalico.org/v3
kind: BGPConfiguration
metadata:
  name: default
spec:
  asNumber: 64512
  nodeToNodeMeshEnabled: false  # Disable full mesh, use route reflectors
  serviceClusterIPs:
    - cidr: 10.96.0.0/12

---
# Peer with ToR switch
apiVersion: projectcalico.org/v3
kind: BGPPeer
metadata:
  name: rack-a-tor
spec:
  peerIP: 10.0.20.1  # ToR switch IP
  asNumber: 64501      # ToR AS number
  nodeSelector: "rack == 'rack-a'"
```

### Cilium Native Routing

```yaml
# Cilium with native routing (no overlay)
apiVersion: cilium.io/v2alpha1
kind: CiliumBGPPeeringPolicy
metadata:
  name: rack-a-peering
spec:
  nodeSelector:
    matchLabels:
      rack: rack-a
  virtualRouters:
    - localASN: 64512
      exportPodCIDR: true
      neighbors:
        - peerAddress: "10.0.20.1/32"
          peerASN: 64501
```

---

## Did You Know?

1. Charles Clos published his seminal paper on non-blocking switching networks in the Bell System Technical Journal in March 1953.
2. IETF RFC 7348 formalized the creation of VXLAN in August 2014, breaking through the 4,094 VLAN limit.
3. 800 Gigabit Ethernet was officially approved on February 16, 2024, under IEEE 802.3df-2024.
4. SONiC governance was successfully transferred from Microsoft to the Linux Foundation on April 14, 2022.
5. **Meta's datacenter fabric uses a 4-plane spine-leaf topology** (F4 architecture) with custom switches running FBOSS. Each plane has independent failure domains. Newer designs scale to 16-plane (F16).
6. **Jumbo frames (9000 MTU) were standardized in 1998** but still are not universally supported. Many enterprise firewalls and WAN links silently fragment them, causing performance degradation.
7. **BGP was designed for internet routing between ISPs in 1989** but has been adopted for datacenter use because of its simplicity and scalability, evolving to use EVPN-VXLAN for multi-tenancy.

---

## Common Mistakes

| Mistake | Why | Fix |
|---------|-----|-----|
| Single ToR switch (no redundancy) | Switch failure equals rack offline because there is no secondary path. | Dual ToR with MLAG or MC-LAG. |
| MTU mismatch in path | Causes silent fragmentation and TCP retransmissions across the overlay. | Verify MTU end-to-end with `ping -c 4 -M do -s 8972`. |
| Flat L2 network at scale | Broadcast storms can propagate across all 8 racks, causing ARP floods. | Route between racks at L3 with BGP. |
| Oversubscribed uplinks | Results in packet drops under heavy east-west load. | Target 2:1 or better oversubscription. |
| No separate storage VLAN | Storage traffic competes with pod traffic, saturating the interface. | Dedicated VLAN with jumbo frames for Ceph/NFS. |
| CNI overlay when unnecessary | Adds extra encapsulation overhead, consuming CPU cycles. | Use Calico/Cilium BGP mode on bare metal. |
| Not monitoring switch ports | You don't know about packet drops until users complain. | Implement SNMP/gNMI monitoring on all switch ports. |
| PXE on production VLAN | Creates a severe risk of accidental OS reimaging during reboots. | Isolated PXE VLAN with restricted DHCP. |

---

## Quiz

### Question 1
Your leaf switch has 48x 25GbE downlink ports and 4x 100GbE uplink ports. What is the oversubscription ratio, and is it acceptable for Kubernetes?

<details>
<summary>Answer</summary>

**Oversubscription ratio: 3:1.** To calculate this, divide the total downlink bandwidth (48 ports × 25 Gbps = 1,200 Gbps) by the total uplink bandwidth (4 ports × 100 Gbps = 400 Gbps), resulting in a 3:1 ratio. For most standard Kubernetes workloads, this 3:1 oversubscription ratio is perfectly acceptable because microservices typically generate moderate, bursty east-west traffic that will not saturate the uplinks. However, if your cluster handles storage-heavy workloads like Ceph or ML/AI training with continuous all-reduce operations, this ratio will inevitably cause congestion and packet drops. In such demanding scenarios, you must target a 2:1 or even 1:1 non-blocking ratio by adding more 100GbE uplinks to the leaf switch.
</details>

### Question 2
Your team is deploying a new bare-metal Kubernetes cluster. The storage team insists that external monitoring tools must be able to reach pod IP addresses directly without going through an Ingress controller or NAT. Which networking approach should you configure with your Top-of-Rack switches to satisfy this requirement while minimizing encapsulation overhead?

<details>
<summary>Answer</summary>

**You should configure native routing (BGP).** Implementing BGP natively eliminates encapsulation overhead, as VXLAN adds 50 bytes per packet which results in measurable CPU load and bandwidth waste at millions of packets per second. Because pod IPs become natively routable across the entire datacenter fabric, external systems such as load balancers or monitoring tools can reach the pods directly without NAT or proxies. This approach seamlessly integrates with your ToR switches that already utilize BGP, transforming your pod CIDRs into first-class citizens in the datacenter routing tables. Consequently, performance is vastly improved and network debugging is vastly simplified since network tools like `tcpdump` will reveal real source and destination IP addresses.
</details>

### Question 3
You are designing the network for a 200-node Kubernetes cluster across 8 racks. Should you use L2 or L3 between racks?

<details>
<summary>Answer</summary>

**L3 (routed) between racks is the correct choice for a cluster of this size.** If you were to span a single L2 domain across 8 racks, all 200 nodes would reside in a massive broadcast domain, causing ARP traffic to scale exponentially and waste network capacity. A single spanning-tree reconvergence event or bridging loop in this flat L2 topology could easily paralyze the entire cluster with a broadcast storm. By implementing an L3 design, each rack is assigned its own isolated /25 subnet, and BGP seamlessly routes traffic between the racks at the leaf switches. This strictly confines broadcast traffic to a single rack while allowing the network infrastructure to scale horizontally to thousands of nodes without introducing stability risks.
</details>

### Question 4
A server's bonded interface shows 50 Gbps capacity (2x 25GbE LACP), but `iperf3` between two servers shows only 24 Gbps. Why?

<details>
<summary>Answer</summary>

**LACP (802.3ad) bond bandwidth is calculated per-flow, not as a single aggregate stream.** The protocol distributes traffic across physical links based on a hash of the packet header (such as source/destination IP and port), meaning a single TCP connection can only traverse one physical link at a time, maxing out at 25 Gbps. To actually achieve the 50 Gbps aggregate bandwidth, your workload must generate multiple concurrent connections that the hashing algorithm can distribute across both links. You can verify this behavior by running a tool like `iperf3` with the `-P` flag to simulate multiple parallel streams. Additionally, ensuring your Linux bond is configured with the `layer3+4` transmit hash policy will provide much better flow distribution for Kubernetes traffic compared to basic MAC address hashing.
</details>

### Question 5
Your machine learning cluster relies on RoCE (RDMA over Converged Ethernet) for low-latency GPU memory transfers. The network team plans to span the cluster across multiple racks connected via Layer 3 spine switches. A junior engineer suggests using RoCE v1 to minimize encapsulation overhead. Why will this design fail to scale across the racks, and what architectural change is required?

<details>
<summary>Answer</summary>

**The design will fail because RoCE v1 is strictly a Layer-2 protocol that relies solely on MAC addresses.** It cannot be routed across the Layer-3 boundaries that separate the individual racks in your modern spine-leaf topology. To scale the RDMA traffic across multiple racks, you must implement RoCE v2, which encapsulates the RDMA transport in standard UDP/IP datagrams. This UDP encapsulation allows the datacenter's spine switches to route the RDMA traffic across standard L3 networks using ECMP load balancing. By upgrading to RoCE v2, you free the machine learning cluster from the constraints of a single broadcast domain.
</details>

### Question 6
A new network engineer configures a Kubernetes cluster using a VXLAN overlay but forgets to adjust the network MTU, leaving all physical switches at the default 1500 bytes. What precise symptom will the application layer experience when transferring large files?

<details>
<summary>Answer</summary>

**The application layer will experience severe throughput degradation and increased latency due to silent IP fragmentation.** Because VXLAN adds 50 bytes of overhead to every packet, the encapsulated frame will easily exceed the standard 1500-byte MTU of the physical switches if Jumbo frames are not configured. When this occurs, the switch or kernel must either drop the packet entirely or fragment it into smaller pieces. Fragmentation drastically increases the CPU interrupt load on the receiving nodes as they struggle to reassemble the packets. This overhead ultimately leads to dropped connections, TCP retransmissions, and plummeting application performance.
</details>

### Question 7
Your organization wants to scale a bare-metal Kubernetes cluster to 500 nodes spanning 15 racks. The security team insists on keeping all nodes in a single VLAN to simplify firewall rules. What network failure mode is this design highly susceptible to?

<details>
<summary>Answer</summary>

**This design is highly susceptible to crippling broadcast storms and ARP flooding across the datacenter.** In a flat L2 network, broadcast traffic such as ARP requests must be flooded to every single node residing within the VLAN. As the node count grows to 500, the volume of background broadcast traffic scales exponentially and can easily saturate the network links. Furthermore, a single spanning-tree reconvergence event or a bridging loop anywhere in the 15 racks could cause a broadcast storm that paralyzes the entire cluster simultaneously. To prevent this cascading failure, the network must be divided into L3 boundaries routed at the Top-of-Rack switches.
</details>

---

## Hands-On Exercise: Design a Network for a K8s Cluster

**Task**: Design the network architecture for a 100-node Kubernetes cluster in 4 racks.

### Requirements
- 100 worker nodes + 3 control plane nodes
- Ceph storage cluster (3 dedicated OSD nodes)
- MetalLB for external load balancing
- Calico CNI with BGP mode
- PXE provisioning capability

### Progressive Tasks

**Task 1: Define the VLAN structure**
Map out the necessary subnets and assignments for management, Kubernetes node traffic, storage, provisioning, and external VIPs.
<details>
<summary>Solution</summary>

```text
VLAN 10: Management (10.0.10.0/24) — BMC, jump hosts
VLAN 20: Kubernetes (10.0.20.0/22) — node communication, pod traffic
VLAN 30: Storage (10.0.30.0/24) — Ceph cluster + public network, MTU 9000
VLAN 40: Provisioning (10.0.40.0/24) — PXE boot, isolated
VLAN 50: External (10.0.50.0/24) — MetalLB VIP range
```
</details>

**Task 2: Design the switching fabric**
Select the appropriate hardware and determine the oversubscription ratio for the Top-of-Rack connectivity.
<details>
<summary>Solution</summary>

```text
Spine: 2x 100GbE switches (32 ports each)
Leaf: 4x 25GbE ToR switches (48 down + 6x 100G up), one per rack
Oversubscription: 48x25=1200 / 6x100=600 = 2:1 ✓
```
</details>

**Task 3: Plan server NIC assignment**
Define how the physical NICs on the servers will be bonded and mapped to the VLANs.
<details>
<summary>Solution</summary>

```text
Per server:
  bond0 (eno1+eno2, LACP, 2x 25GbE): VLAN 20 + 30 + 50 trunk
  eno3 (1GbE): VLAN 10 management
  BMC (1GbE): VLAN 10
```
</details>

**Task 4: Define BGP peering**
Assign Autonomous System (AS) numbers to your spines, leaves, and Kubernetes nodes.
<details>
<summary>Solution</summary>

```text
Leaf AS numbers: 64501 (rack-a), 64502 (rack-b), etc.
Spine AS: 64500
Calico node AS: 64512
Each node peers with its local leaf switch
Leaf switches peer with both spines
```
</details>

**Task 5: Calculate bandwidth**
Verify the total intra-rack and spine bandwidth capacity of your design.
<details>
<summary>Solution</summary>

```text
25 nodes per rack × 25 Gbps = 625 Gbps intra-rack
6 × 100 Gbps = 600 Gbps to spine (effective ~1:1 for connected hosts; 2:1 at full switch capacity)
Total spine bandwidth: 2 × 32 × 100G = 6,400 Gbps
```
</details>

### Success Criteria
- [ ] VLAN design documented with subnets and purposes.
- [ ] Spine-leaf topology sized with oversubscription ratio < 3:1.
- [ ] Server NIC assignment defined (bond + management + BMC).
- [ ] BGP AS numbers assigned correctly.
- [ ] MTU documented per VLAN (9000 explicitly set for storage).
- [ ] PXE VLAN isolated from production.
- [ ] MetalLB VIP range defined on external VLAN.

---

## Next Module

Continue to [Module 3.2: BGP & Routing for Kubernetes](../module-3.2-bgp-routing/) to deep-dive into advanced Route Reflectors, EVPN distribution, and optimizing path selection between your nodes and the physical datacenter fabric.