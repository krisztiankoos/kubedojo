# Module 5.1: Cilium

> **Toolkit Track** | Complexity: `[COMPLEX]` | Time: 50-60 minutes

## Overview

Kubernetes networking is hard. Cilium makes it observable, secure, and fast. Built on eBPF, Cilium provides CNI networking, network policies, load balancing, and deep visibility—all without the overhead of traditional proxies. This module covers Cilium as a modern CNI and security tool.

**What You'll Learn**:
- Cilium architecture and eBPF fundamentals
- Network policies beyond vanilla Kubernetes
- Hubble for network observability
- Service mesh without sidecars

**Prerequisites**:
- Kubernetes networking basics (Services, Pods, CNI)
- [Security Principles Foundations](../../foundations/security-principles/)
- Linux networking concepts (TCP/IP, DNS)

---

## Why This Module Matters

Traditional CNI plugins do basic networking. Cilium does that plus identity-based security, L7 visibility, transparent encryption, and multi-cluster connectivity—all at kernel speed. It's replacing kube-proxy, competing with service meshes, and becoming the default CNI for major managed Kubernetes offerings.

> 💡 **Did You Know?** Cilium uses eBPF (extended Berkeley Packet Filter) to run custom programs inside the Linux kernel. This means network decisions happen at kernel speed without context switching to userspace. Google, AWS, and Azure all offer Cilium as their CNI option. It's the only CNCF graduated CNI project.

---

## eBPF: The Technology Behind Cilium

```
eBPF: PROGRAMMABLE KERNEL
════════════════════════════════════════════════════════════════════

Traditional Networking:
┌─────────────────────────────────────────────────────────────────┐
│  Packet arrives                                                  │
│       │                                                          │
│       ▼                                                          │
│  Kernel (fixed path) ──▶ iptables ──▶ Userspace proxy ──▶ App  │
│                           (slow)        (slow)                   │
└─────────────────────────────────────────────────────────────────┘

With eBPF (Cilium):
┌─────────────────────────────────────────────────────────────────┐
│  Packet arrives                                                  │
│       │                                                          │
│       ▼                                                          │
│  Kernel + eBPF programs ──────────────────────────────────▶ App │
│  (filtering, routing, load balancing all in kernel)             │
│                                                                  │
│  • No iptables (replaced by eBPF maps)                          │
│  • No userspace proxy for L3/L4                                 │
│  • Direct path to application                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Why eBPF Matters

| Feature | Traditional | eBPF (Cilium) |
|---------|-------------|---------------|
| **Performance** | iptables chains grow linearly | O(1) hash map lookups |
| **Visibility** | Packet capture, tcpdump | Rich telemetry, Hubble |
| **Security** | IP-based policies | Identity-based policies |
| **Updates** | Kernel module or reboot | Dynamic, no restart |

---

## Cilium Architecture

```
CILIUM ARCHITECTURE
════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│                         KUBERNETES NODE                          │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    CILIUM AGENT                          │   │
│  │                                                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │   Policy    │  │  Identity   │  │    Hubble   │     │   │
│  │  │   Engine    │  │   Manager   │  │   (observ)  │     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │   │
│  │                         │                                │   │
│  │                         ▼                                │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │              eBPF Dataplane                       │   │   │
│  │  │  • CNI (pod networking)                          │   │   │
│  │  │  • kube-proxy replacement                        │   │   │
│  │  │  • Network policies                              │   │   │
│  │  │  • Load balancing                                │   │   │
│  │  │  • Encryption (WireGuard)                        │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐                   │
│  │   Pod A   │  │   Pod B   │  │   Pod C   │                   │
│  │  id=12345 │  │  id=67890 │  │  id=11111 │                   │
│  └───────────┘  └───────────┘  └───────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       CONTROL PLANE                              │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │ Cilium Operator │  │  Hubble Relay   │                      │
│  │ (cluster-wide)  │  │ (aggregation)   │                      │
│  └─────────────────┘  └─────────────────┘                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Purpose |
|-----------|---------|
| **Cilium Agent** | DaemonSet on each node, manages eBPF programs |
| **Cilium Operator** | Cluster-wide operations, IPAM, CRD management |
| **Hubble** | Network observability, flow logs, metrics |
| **Hubble Relay** | Aggregates Hubble data across nodes |
| **Hubble UI** | Web interface for flow visualization |

### Installation

```bash
# Install Cilium CLI
curl -L --fail --remote-name-all https://github.com/cilium/cilium-cli/releases/latest/download/cilium-linux-amd64.tar.gz
sudo tar xzvfC cilium-linux-amd64.tar.gz /usr/local/bin

# Install Cilium (replaces kube-proxy)
cilium install \
  --set kubeProxyReplacement=true \
  --set hubble.enabled=true \
  --set hubble.relay.enabled=true \
  --set hubble.ui.enabled=true

# Verify installation
cilium status --wait

# Run connectivity test
cilium connectivity test
```

---

## Identity-Based Security

### The Problem with IP-Based Policies

```
IP-BASED VS IDENTITY-BASED
════════════════════════════════════════════════════════════════════

Traditional NetworkPolicy (IP-based):
─────────────────────────────────────────────────────────────────
"Allow traffic from 10.0.1.0/24 to port 80"

Problems:
• IPs change (pod restarts, scaling)
• Can't express "allow frontend to backend"
• No visibility into WHAT is communicating

Cilium (Identity-based):
─────────────────────────────────────────────────────────────────
"Allow traffic from pods with label app=frontend to app=backend"

Benefits:
• Works regardless of IP
• Human-readable policies
• Policies follow workloads across clusters
```

### Cilium Identity System

```
HOW CILIUM IDENTITY WORKS
════════════════════════════════════════════════════════════════════

1. Pod created with labels: app=frontend, env=prod
        │
        ▼
2. Cilium assigns IDENTITY based on labels
   Identity 12345 = {app=frontend, env=prod}
        │
        ▼
3. Every packet carries identity (not IP)
   Source: id=12345 → Destination: id=67890
        │
        ▼
4. Policy evaluated against identity
   "Allow id matching {app=frontend} → {app=backend}"

Result: Works even when IPs change!
```

---

## Network Policies

### Kubernetes NetworkPolicy (Cilium extends this)

```yaml
# Standard Kubernetes NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

### CiliumNetworkPolicy (L3-L7)

```yaml
# Cilium extends with L7 rules
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: api-policy
spec:
  endpointSelector:
    matchLabels:
      app: api
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: frontend
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
      rules:
        http:
        - method: "GET"
          path: "/api/v1/.*"
        - method: "POST"
          path: "/api/v1/orders"
```

### Advanced Policy Examples

```yaml
# DNS-based egress policy
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-external-api
spec:
  endpointSelector:
    matchLabels:
      app: worker
  egress:
  - toFQDNs:
    - matchName: "api.stripe.com"
    - matchPattern: "*.amazonaws.com"
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
---
# Cluster-wide policy
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: default-deny-all
spec:
  endpointSelector: {}  # All pods
  ingress:
  - fromEndpoints:
    - {}  # Only from pods with Cilium identity (not external)
  egress:
  - toEndpoints:
    - {}
  - toEntities:
    - kube-apiserver
    - dns
```

> 💡 **Did You Know?** Cilium's FQDN-based policies resolve DNS and automatically update eBPF maps with IP addresses. This means you can write `allow traffic to api.stripe.com` and it just works—even when Stripe's IP addresses change. No more hardcoding IPs or CIDR blocks for external services.

---

## Hubble: Network Observability

### What is Hubble?

Hubble provides deep visibility into network traffic using eBPF. It captures flows without sampling and without the performance overhead of traditional packet capture.

```
HUBBLE ARCHITECTURE
════════════════════════════════════════════════════════════════════

┌───────────────────────────────────────────────────────────────┐
│                        HUBBLE UI                               │
│                   (Web visualization)                          │
└───────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌───────────────────────────────────────────────────────────────┐
│                      HUBBLE RELAY                              │
│              (Aggregates from all nodes)                       │
└───────────────────────────────────────────────────────────────┘
         ▲                    ▲                    ▲
         │                    │                    │
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Hubble Node │      │ Hubble Node │      │ Hubble Node │
│   (eBPF)    │      │   (eBPF)    │      │   (eBPF)    │
└─────────────┘      └─────────────┘      └─────────────┘
     Node 1               Node 2               Node 3
```

### Using Hubble CLI

```bash
# Install Hubble CLI
curl -L --fail --remote-name-all https://github.com/cilium/hubble/releases/latest/download/hubble-linux-amd64.tar.gz
sudo tar xzvfC hubble-linux-amd64.tar.gz /usr/local/bin

# Port-forward to Hubble Relay
cilium hubble port-forward &

# Observe flows in real-time
hubble observe

# Filter by namespace
hubble observe --namespace production

# Filter by pod
hubble observe --pod production/frontend-xxx

# Filter by verdict (allowed/denied)
hubble observe --verdict DROPPED

# Filter by L7 protocol
hubble observe --protocol http

# Show DNS queries
hubble observe --protocol dns

# Follow specific flow
hubble observe --from-pod production/frontend --to-pod production/backend
```

### Hubble Flow Output

```
TIMESTAMP             SOURCE                        DESTINATION                   TYPE    VERDICT
2024-01-15T10:23:45Z  production/frontend-abc       production/backend-xyz        L7/HTTP FORWARDED
                      HTTP GET /api/users -> 200 OK (15ms)

2024-01-15T10:23:46Z  production/frontend-abc       external/8.8.8.8:53          L3/L4   FORWARDED
                      DNS query: api.stripe.com

2024-01-15T10:23:47Z  production/worker-def         external/api.stripe.com:443   L3/L4   DROPPED
                      Policy denied: no matching egress rule
```

### Hubble Metrics

```yaml
# Enable Hubble metrics for Prometheus
cilium upgrade \
  --set hubble.enabled=true \
  --set hubble.metrics.enabled="{dns,drop,tcp,flow,icmp,http}"

# Key metrics:
# hubble_flows_processed_total - Total flows
# hubble_drop_total - Dropped packets by reason
# hubble_dns_queries_total - DNS queries
# hubble_http_requests_total - HTTP requests with status codes
```

> 💡 **Did You Know?** Hubble can show you exactly why a packet was dropped—including which policy denied it. No more guessing with `tcpdump`. When debugging connectivity issues, `hubble observe --verdict DROPPED` instantly shows you what's blocked and by which rule.

---

## Kube-Proxy Replacement

### Why Replace Kube-Proxy?

```
KUBE-PROXY VS CILIUM
════════════════════════════════════════════════════════════════════

kube-proxy (iptables mode):
─────────────────────────────────────────────────────────────────
• Creates iptables rules for each Service
• Rules grow O(n) with services
• 10,000 services = 10,000+ iptables rules
• Updates are slow, cause connection drops

Cilium kube-proxy replacement:
─────────────────────────────────────────────────────────────────
• eBPF maps for service lookup
• O(1) hash table lookups
• Handles millions of services
• Updates are atomic, no drops
```

### Performance Comparison

| Metric | kube-proxy (iptables) | Cilium eBPF |
|--------|----------------------|-------------|
| **Latency** | ~1ms per 1000 rules | ~100μs constant |
| **Memory** | Grows with services | Constant |
| **CPU** | High at scale | Low |
| **Update time** | Seconds | Milliseconds |

### Configuration

```bash
# Install with kube-proxy replacement
cilium install --set kubeProxyReplacement=true

# Verify kube-proxy is replaced
cilium status | grep KubeProxyReplacement

# Check which Services are handled by Cilium
kubectl exec -n kube-system cilium-xxxxx -- cilium service list
```

> 💡 **Did You Know?** Cilium's kube-proxy replacement has been battle-tested at massive scale. Datadog runs Cilium on clusters with 15,000+ nodes, and Adobe uses it across 150 clusters. At these scales, traditional kube-proxy with iptables simply doesn't work—updates take too long and cause connection drops. eBPF solved what was once considered an unsolvable Kubernetes scaling limit.

---

## Transparent Encryption

### WireGuard Integration

```bash
# Enable WireGuard encryption
cilium install \
  --set encryption.enabled=true \
  --set encryption.type=wireguard

# Verify encryption
cilium status | grep Encryption

# Check WireGuard peers
kubectl exec -n kube-system cilium-xxxxx -- cilium encrypt status
```

```
TRANSPARENT ENCRYPTION
════════════════════════════════════════════════════════════════════

Without Encryption:
Pod A ──────[plaintext]──────▶ Pod B
       Anyone on network can see traffic

With Cilium WireGuard:
Pod A ──[encrypted tunnel]──▶ Pod B
       Traffic encrypted at kernel level
       No sidecar needed
       No application changes
```

---

## Service Mesh Without Sidecars

### Cilium Service Mesh

```
TRADITIONAL SERVICE MESH VS CILIUM
════════════════════════════════════════════════════════════════════

Traditional (Istio, Linkerd):
┌─────────────────────────────────────────────────────────────────┐
│  Pod                                                             │
│  ┌─────────────┐    ┌─────────────┐                            │
│  │    App      │───▶│   Sidecar   │───▶ Network                │
│  │             │◀───│   (Envoy)   │◀─── (via proxy)            │
│  └─────────────┘    └─────────────┘                            │
│                                                                  │
│  • Extra container per pod                                      │
│  • Memory/CPU overhead                                          │
│  • Complex injection                                            │
└─────────────────────────────────────────────────────────────────┘

Cilium Service Mesh (sidecar-free):
┌─────────────────────────────────────────────────────────────────┐
│  Pod                                                             │
│  ┌─────────────┐                                                │
│  │    App      │───▶ eBPF (in kernel) ───▶ Network             │
│  └─────────────┘                                                │
│                                                                  │
│  • No sidecar needed                                            │
│  • Lower resource usage                                         │
│  • Simpler operations                                           │
└─────────────────────────────────────────────────────────────────┘
```

### Enabling Service Mesh Features

```bash
# Install with L7 proxy (for HTTP visibility)
cilium install \
  --set hubble.enabled=true \
  --set envoy.enabled=true

# Enable for specific services
kubectl annotate service my-service io.cilium/l7-parser=http
```

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Not running connectivity test | Unknown networking issues | Run `cilium connectivity test` after install |
| Mixing CNIs | Conflicts, broken networking | Remove old CNI before installing Cilium |
| Forgetting cluster-wide policies | Default allow = security gap | Always set default deny policy |
| Ignoring Hubble metrics | Blind to network issues | Enable and alert on `hubble_drop_total` |
| Over-permissive FQDN policies | `*.example.com` too broad | Use specific FQDNs or matchName |
| Not enabling kube-proxy replacement | Running two systems | Set `kubeProxyReplacement=true` |

---

## War Story: The DNS That Wasn't

*A team deployed Cilium with default deny policies. Everything looked fine until an app couldn't resolve DNS.*

**What went wrong**: They forgot to allow DNS egress. Cilium blocked pods from reaching kube-dns.

**The policy that fixed it**:
```yaml
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: allow-dns
spec:
  endpointSelector: {}
  egress:
  - toEntities:
    - kube-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: UDP
      - port: "53"
        protocol: TCP
```

**Lesson**: When implementing default deny, ALWAYS allow DNS first. Use `toEntities: [kube-dns]` instead of hardcoding IPs.

---

## Quiz

### Question 1
What's the advantage of identity-based policies over IP-based policies?

<details>
<summary>Show Answer</summary>

**Identity-based (Cilium)**:
- Works when pods restart and get new IPs
- Human-readable (app=frontend → app=backend)
- Follows workloads across nodes and clusters
- Based on Kubernetes labels, not infrastructure

**IP-based (traditional)**:
- Breaks when IPs change
- Hard to audit (what does 10.0.1.42 mean?)
- Requires constant updates
- Doesn't understand Kubernetes semantics

</details>

### Question 2
Why does Cilium replace kube-proxy?

<details>
<summary>Show Answer</summary>

**Performance at scale**:
- kube-proxy uses iptables with O(n) lookup time
- 10,000 services = 10,000+ iptables rules
- Updates cause brief connection drops

**Cilium eBPF**:
- O(1) hash table lookups
- Handles millions of services
- Atomic updates, no drops
- Lower CPU/memory usage

Additional benefits:
- DSR (Direct Server Return) for load balancing
- Session affinity without iptables
- Better observability via Hubble

</details>

### Question 3
How do you debug a dropped packet in Cilium?

<details>
<summary>Show Answer</summary>

```bash
# 1. Use Hubble to see drops
hubble observe --verdict DROPPED

# Shows:
# - Source/destination pod
# - Policy that caused drop
# - Timestamp

# 2. Check specific pod
hubble observe --pod production/myapp --verdict DROPPED

# 3. Check policy matches
cilium policy selectors

# 4. Trace specific flow
cilium monitor --type drop

# 5. Check endpoint policies
cilium endpoint get <endpoint-id> -o json | jq '.status.policy'
```

</details>

---

## Hands-On Exercise

### Objective
Deploy Cilium, implement network policies, and observe traffic with Hubble.

### Environment Setup

```bash
# Create kind cluster without default CNI
cat > kind-config.yaml << 'EOF'
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  disableDefaultCNI: true
  kubeProxyMode: none  # Cilium will replace kube-proxy
nodes:
- role: control-plane
- role: worker
- role: worker
EOF

kind create cluster --config kind-config.yaml

# Install Cilium
cilium install --set kubeProxyReplacement=true
cilium status --wait

# Enable Hubble
cilium hubble enable --ui
```

### Tasks

1. **Verify Cilium is working**:
   ```bash
   cilium connectivity test
   ```

2. **Deploy test workloads**:
   ```bash
   kubectl create namespace test
   kubectl -n test run frontend --image=nginx --labels="app=frontend"
   kubectl -n test run backend --image=nginx --labels="app=backend"
   kubectl -n test expose pod backend --port=80
   ```

3. **Test connectivity** (should work):
   ```bash
   kubectl -n test exec frontend -- curl -s backend
   ```

4. **Apply default deny policy**:
   ```yaml
   apiVersion: cilium.io/v2
   kind: CiliumNetworkPolicy
   metadata:
     name: default-deny
     namespace: test
   spec:
     endpointSelector: {}
     ingress: []
     egress: []
   ```

5. **Test connectivity** (should fail):
   ```bash
   kubectl -n test exec frontend -- curl -s --connect-timeout 5 backend
   ```

6. **Observe with Hubble**:
   ```bash
   cilium hubble port-forward &
   hubble observe --namespace test --verdict DROPPED
   ```

7. **Add allow policy**:
   ```yaml
   apiVersion: cilium.io/v2
   kind: CiliumNetworkPolicy
   metadata:
     name: allow-frontend-backend
     namespace: test
   spec:
     endpointSelector:
       matchLabels:
         app: backend
     ingress:
     - fromEndpoints:
       - matchLabels:
           app: frontend
       toPorts:
       - ports:
         - port: "80"
   ```

8. **Test connectivity** (should work again):
   ```bash
   kubectl -n test exec frontend -- curl -s backend
   ```

### Success Criteria
- [ ] Cilium connectivity test passes
- [ ] Default deny blocks traffic
- [ ] Hubble shows DROPPED verdict
- [ ] Allow policy restores specific traffic
- [ ] Hubble shows FORWARDED verdict

### Bonus Challenge
Add an L7 policy that only allows GET requests to `/api/*`:
```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
# ... complete the policy
```

---

## Further Reading

- [Cilium Documentation](https://docs.cilium.io/)
- [eBPF.io](https://ebpf.io/) - Learn eBPF fundamentals
- [Cilium Network Policy Editor](https://editor.cilium.io/) - Visual policy builder
- [Hubble Documentation](https://docs.cilium.io/en/stable/observability/hubble/)

---

## Next Module

Continue to [Module 5.2: Service Mesh](module-5.2-service-mesh.md) to learn about service mesh patterns with Istio and comparing sidecar vs sidecar-free approaches.

---

*"The best firewall is the one you can actually understand. Cilium makes network security visible."*
