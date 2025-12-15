# Module 3.8: Cluster Networking Data Path (Theory)

> **Complexity**: `[MEDIUM]` - Core troubleshooting topic
>
> **Time to Complete**: 25-35 minutes
>
> **Prerequisites**: Module 3.1 (Services), Module 3.6 (Network Policies), Module 3.7 (CNI)

---

## Outline
- Service to Pod data path (ClusterIP/NodePort) and kube-proxy roles
- CNI responsibilities vs. kube-proxy; what encapsulation/routing looks like
- CoreDNS resolution path and common failure modes
- How to reason about drops: conntrack, policies, and readiness

---

## Service → Pod Flow
- **NodePort/ClusterIP**: Traffic hits kube-proxy rules, which select a backend Pod IP from Endpoints/EndpointSlice.
- **iptables mode**: DNAT happens early; conntrack preserves flow to the same pod for a connection.
- **IPVS mode**: kube-proxy programs a virtual service with schedulers (rr, lc, wrr). Lower per-packet overhead than iptables in large clusters.
- **Hairpin**: Pod calling its own Service may need hairpin mode enabled on the kubelet; otherwise packets are dropped.

## CNI vs. kube-proxy
- **CNI**: Assigns pod IPs, sets up veth pairs, configures routing/encapsulation (vxlan/geneve), and may enforce policies.
- **kube-proxy**: Service/VIP handling only. If Services work but pods cannot reach each other, investigate CNI routes/encap.
- **Quick matrix**:
  - **Calico**: BGP/no-encap by default; network policies enforced in the dataplane.
  - **Flannel**: Simple overlay (vxlan, host-gw); policies often delegated to another component.
  - **Cilium**: eBPF data path; can replace kube-proxy (kube-proxy replacement mode) and enforce policies at L3–L7.

## DNS Path (CoreDNS)
- Pod `/etc/resolv.conf` usually points to cluster DNS Service (`kube-dns`/`coredns`).
- Query flow: app → dnsmasq/glibc stub → ClusterIP → kube-proxy → CoreDNS Pod → upstream (or stub domains).
- Watch for `ndots` behavior: names with fewer dots may trigger search path expansion; set `ndots` appropriately to reduce latency.
- Common failures: missing Endpoints for CoreDNS, NetworkPolicy blocking UDP/53, NodeLocal DNSCache not running on node, or CoreDNS crashloop.

## Troubleshooting Mental Model
- **Connectivity but no Service**: Check Endpoints/EndpointSlice; pod readiness gates inclusion.
- **Service reachable, pod unreachable**: Inspect conntrack (`conntrack -L`) and kube-proxy mode; stale entries can pin traffic to deleted pods.
- **NodePort issues**: Verify host firewall rules and cloud security groups; kube-proxy only programs node-local rules.
- **Cross-node drops**: Trace CNI routing/encap; confirm MTU matches overlay settings to avoid silent fragmentation drops.
