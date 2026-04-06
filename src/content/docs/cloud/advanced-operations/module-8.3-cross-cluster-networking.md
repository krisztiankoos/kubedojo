---
title: "Module 8.3: Cross-Cluster & Cross-Region Networking"
slug: cloud/advanced-operations/module-8.3-cross-cluster-networking
sidebar:
  order: 4
---
> **Complexity**: `[COMPLEX]`
>
> **Time to Complete**: 3 hours
>
> **Prerequisites**: [Module 8.2: Advanced Cloud Networking & Transit Hubs](../module-8.2-transit-hubs/), working knowledge of Kubernetes Services and Ingress
>
> **Track**: Advanced Cloud Operations

## What You'll Be Able to Do

After completing this module, you will be able to:

- **Configure cross-cluster service discovery using DNS, service mesh, or Kubernetes MCS (Multi-Cluster Services) API**
- **Implement cross-region pod-to-pod connectivity with VPN tunnels, peering, or overlay networks**
- **Deploy service mesh multi-cluster topologies (Istio, Linkerd) for encrypted cross-cluster traffic routing**
- **Design network architectures that minimize cross-region latency while maintaining security isolation between clusters**

---

## Why This Module Matters

**July 2022. A major ride-sharing company. Peak Friday evening traffic.**

The platform engineering team had deployed a second Kubernetes cluster in a new region to reduce latency for east coast users. The migration plan was clean: DNS-based traffic splitting, 10% canary to the new region, gradual ramp-up. What they didn't plan for was service discovery. The payment service in the new cluster needed to call the fraud detection service, which still ran exclusively in the original cluster. The team had hardcoded the fraud service's internal ClusterIP in a ConfigMap. ClusterIPs don't route across clusters.

The hotfix was a mess: an ExternalName service pointing to an NLB in front of the fraud service, which routed through a VPC peering connection. Latency for fraud checks jumped from 12ms to 89ms. The payment timeout was 100ms. One in five fraud checks started timing out, which the system interpreted as "fraud check passed" (fail-open design -- a separate problem). Fraudulent transactions spiked 340% over the weekend before anyone noticed.

Cross-cluster networking is the problem nobody thinks about until they have two clusters. Then it becomes the most urgent problem they have. This module teaches you the networking models, tools, and patterns for making pods in different clusters -- and different regions -- communicate reliably. You will learn the difference between flat and island networking, how Cilium Cluster Mesh and the Multi-Cluster Services API work, how to handle the cost implications of cross-AZ traffic, and how to design for the split-brain scenarios that make multi-cluster networking genuinely hard.

---

## Flat vs. Island Networking Models

When you run multiple Kubernetes clusters, you have a fundamental architectural choice: should pods in different clusters be able to reach each other directly by IP, or should they communicate only through explicit service discovery mechanisms?

### Flat Networking (Routable Pod CIDRs)

In a flat network, every pod across every cluster has a unique, routable IP address. A pod in cluster-A can reach a pod in cluster-B by IP, the same way it would reach a pod in its own cluster.

```
FLAT NETWORKING MODEL
════════════════════════════════════════════════════════════════

  Cluster A (us-east-1)              Cluster B (eu-west-1)
  Pod CIDR: 100.64.0.0/16           Pod CIDR: 100.65.0.0/16
  ┌─────────────────────┐           ┌─────────────────────┐
  │                     │           │                     │
  │  frontend-pod       │           │  frontend-pod       │
  │  100.64.12.5        │           │  100.65.8.22        │
  │       │             │           │       │             │
  │       │ Direct IP   │           │       │             │
  │       ▼             │    VPC    │       ▼             │
  │  api-pod            │  Peering  │  api-pod            │
  │  100.64.33.18  ─────┼──────────┼──▶ 100.65.41.9      │
  │                     │    or    │                     │
  │                     │   TGW    │                     │
  └─────────────────────┘           └─────────────────────┘

  Requirements:
  - Non-overlapping Pod CIDRs across ALL clusters
  - VPC-level routing for pod CIDRs (routes in VPC route tables)
  - CNI must advertise pod routes to the VPC (e.g., AWS VPC CNI)
```

**Pros**: Simple mental model. Any pod can reach any other pod. No service mesh or gateway required for basic connectivity. Tools like `curl <pod-ip>` work across clusters.

**Cons**: Requires globally unique pod CIDRs (IPAM becomes critical). Every cluster's pod CIDR must be routable through VPC infrastructure. Scales poorly (route table limits). No inherent access control (any pod can reach any pod unless you add NetworkPolicy).

### Island Networking (Isolated Pod CIDRs)

In the island model, each cluster is a networking island. Pod CIDRs can overlap between clusters. Cross-cluster communication happens only through explicit gateways or service abstractions.

```
ISLAND NETWORKING MODEL
════════════════════════════════════════════════════════════════

  Cluster A (us-east-1)              Cluster B (eu-west-1)
  Pod CIDR: 10.244.0.0/16           Pod CIDR: 10.244.0.0/16
  ┌─────────────────────┐           ┌─────────────────────┐
  │                     │           │                     │
  │  frontend-pod       │           │  frontend-pod       │
  │  10.244.1.5         │           │  10.244.1.5         │
  │       │             │           │       ▲             │
  │       ▼             │           │       │             │
  │  Gateway/LB  ───────┼───HTTPS──┼──▶ Gateway/LB       │
  │  (NodePort,NLB,     │  (public │  (NodePort,NLB,     │
  │   or Istio GW)      │  or priv │   or Istio GW)      │
  │                     │  link)   │                     │
  └─────────────────────┘           └─────────────────────┘

  Pod CIDRs CAN overlap (10.244.x.x in both clusters)
  Communication: Only through explicit gateways
  Access control: Built into the gateway layer
```

**Pros**: No CIDR coordination needed. Clusters are independently deployable. Natural access control boundary. Scales to hundreds of clusters. Works across cloud providers.

**Cons**: Higher latency (extra hop through gateway). More complex service discovery. Requires explicit configuration for every cross-cluster service. Debugging is harder (you can't just `curl <pod-ip>` across clusters).

### Decision Framework

| Factor | Choose Flat | Choose Island |
|---|---|---|
| Number of clusters | < 10 | 10+ |
| Cloud providers | Single cloud | Multi-cloud |
| Team autonomy | Low (centralized platform) | High (independent teams) |
| Service mesh | Already using one | Not using / optional |
| Compliance | Low (no strict boundaries) | High (network isolation required) |
| Migration from monolith | Yes (pods need to reach legacy IPs) | No |
| CNI | AWS VPC CNI, Azure CNI | Calico, Cilium (overlay mode) |

> **Stop and think**: If your company acquires a startup that uses the exact same Pod CIDR (e.g., 10.244.0.0/16) as your main clusters, which networking model will you be forced to use to connect them?

---

## Cilium Cluster Mesh

Cilium Cluster Mesh is the most mature open-source solution for connecting multiple Kubernetes clusters at the networking and service discovery level. It enables pods in one cluster to discover and communicate with services in another cluster as if they were local.

### How It Works

```
CILIUM CLUSTER MESH ARCHITECTURE
════════════════════════════════════════════════════════════════

  Cluster A                           Cluster B
  ┌────────────────────────┐         ┌────────────────────────┐
  │  ┌──────────────────┐  │         │  ┌──────────────────┐  │
  │  │  Cilium Agent     │  │         │  │  Cilium Agent     │  │
  │  │  (every node)     │  │         │  │  (every node)     │  │
  │  └────────┬─────────┘  │         │  └────────┬─────────┘  │
  │           │             │         │           │             │
  │  ┌────────┴─────────┐  │   gRPC  │  ┌────────┴─────────┐  │
  │  │  clustermesh-     │──┼─────────┼──│  clustermesh-     │  │
  │  │  apiserver        │  │         │  │  apiserver        │  │
  │  │  (watches local   │◀─┼─────────┼──│  (watches local   │  │
  │  │   endpoints)      │  │         │  │   endpoints)      │  │
  │  └────────┬─────────┘  │         │  └────────┬─────────┘  │
  │           │             │         │           │             │
  │  ┌────────┴─────────┐  │         │  ┌────────┴─────────┐  │
  │  │  etcd (kvstore)   │  │         │  │  etcd (kvstore)   │  │
  │  │  stores service   │  │         │  │  stores service   │  │
  │  │  + endpoint info  │  │         │  │  + endpoint info  │  │
  │  └──────────────────┘  │         │  └──────────────────┘  │
  └────────────────────────┘         └────────────────────────┘

  1. Each cluster runs a clustermesh-apiserver that exposes its
     service and endpoint information
  2. Cilium agents in each cluster connect to the OTHER cluster's
     apiserver to learn about remote services
  3. When a pod in Cluster A resolves a service that exists in
     both clusters, Cilium load-balances across local AND remote
     endpoints
  4. Traffic between clusters flows directly (pod IP to pod IP)
     through the underlying network (VPC peering, TGW, etc.)
```

### Setting Up Cluster Mesh

```bash
# Prerequisites: Cilium installed in both clusters with cluster mesh enabled
# Both clusters must have non-overlapping Pod CIDRs
# Underlying network must route pod CIDRs between clusters

# Install Cilium CLI
CILIUM_CLI_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/cilium-cli/main/stable.txt)
curl -L --fail --remote-name-all \
  https://github.com/cilium/cilium-cli/releases/download/${CILIUM_CLI_VERSION}/cilium-darwin-arm64.tar.gz
sudo tar xzvf cilium-darwin-arm64.tar.gz -C /usr/local/bin

# Install Cilium with cluster mesh support on Cluster A
cilium install \
  --set cluster.name=cluster-a \
  --set cluster.id=1 \
  --set ipam.operator.clusterPoolIPv4PodCIDRList="100.64.0.0/16"

# Install Cilium with cluster mesh support on Cluster B
cilium install \
  --set cluster.name=cluster-b \
  --set cluster.id=2 \
  --set ipam.operator.clusterPoolIPv4PodCIDRList="100.65.0.0/16"

# Enable cluster mesh on both clusters
cilium clustermesh enable --context cluster-a
cilium clustermesh enable --context cluster-b

# Connect the clusters
cilium clustermesh connect --context cluster-a --destination-context cluster-b

# Verify the connection
cilium clustermesh status --context cluster-a
```

### Cross-Cluster Service Discovery

Once Cluster Mesh is connected, services with the same name and namespace in both clusters are automatically merged. You can also use annotations to control the behavior.

```yaml
# Deploy a service in both clusters with the same name
# Cilium will load-balance across endpoints in BOTH clusters
apiVersion: v1
kind: Service
metadata:
  name: fraud-detection
  namespace: payments
  annotations:
    # Optional: prefer local endpoints, use remote only as fallback
    io.cilium/global-service: "true"
    io.cilium/service-affinity: "local"
spec:
  selector:
    app: fraud-detection
  ports:
    - port: 8080
      targetPort: 8080
```

```yaml
# Service affinity options:
# "local"  - prefer endpoints in the same cluster (fallback to remote)
# "remote" - prefer endpoints in the remote cluster
# "none"   - load-balance equally across all clusters (default)
---
# To make a service available ONLY to the local cluster
# (not exported to cluster mesh), omit the global-service annotation
apiVersion: v1
kind: Service
metadata:
  name: internal-cache
  namespace: payments
  # No io.cilium/global-service annotation = local only
spec:
  selector:
    app: redis-cache
  ports:
    - port: 6379
```

> **Pause and predict**: If you annotate a service with `io.cilium/service-affinity: "local"`, what happens when all local endpoints for that service crash? Will the requests fail, or will they route to the remote cluster?

### Network Policies Across Clusters

Cilium Cluster Mesh extends network policies across cluster boundaries.

```yaml
# Allow traffic from cluster-b's frontend to cluster-a's API
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-cross-cluster-frontend
  namespace: payments
spec:
  endpointSelector:
    matchLabels:
      app: fraud-detection
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: payment-frontend
            io.cilium.k8s.policy.cluster: cluster-b
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
```

---

## Multi-Cluster Services API (MCS API)

The Kubernetes Multi-Cluster Services API (KEP-1645) is the official Kubernetes approach to cross-cluster service discovery. It is less feature-rich than Cilium Cluster Mesh but more vendor-neutral.

### Core Concepts

```
MCS API ARCHITECTURE
════════════════════════════════════════════════════════════════

  Cluster A                              Cluster B
  ┌────────────────────────┐            ┌────────────────────────┐
  │                        │            │                        │
  │  Service: web-api      │            │  Service: web-api      │
  │  (ClusterIP)           │            │  (ClusterIP)           │
  │                        │            │                        │
  │  ServiceExport:        │            │  ServiceExport:        │
  │  "export web-api to    │            │  "export web-api to    │
  │   the cluster set"     │            │   the cluster set"     │
  │          │             │            │          │             │
  └──────────┼─────────────┘            └──────────┼─────────────┘
             │                                     │
             ▼                                     ▼
  ┌──────────────────────────────────────────────────────────┐
  │                   MCS Controller                         │
  │  (GKE Multi-Cluster Services, Submariner, Lighthouse)   │
  │                                                          │
  │  Creates ServiceImport in BOTH clusters:                │
  │  web-api.payments.svc.clusterset.local                   │
  │  Endpoints: [cluster-a IPs] + [cluster-b IPs]           │
  └──────────────────────────────────────────────────────────┘

  Resolution:
  web-api.payments.svc.cluster.local     -> local endpoints only
  web-api.payments.svc.clusterset.local  -> ALL cluster endpoints
```

### Using MCS API on GKE

GKE has native MCS API support through Multi-Cluster Services.

```bash
# Register clusters to a fleet
gcloud container fleet memberships register cluster-a \
  --gke-cluster=us-central1/cluster-a \
  --enable-workload-identity

gcloud container fleet memberships register cluster-b \
  --gke-cluster=europe-west1/cluster-b \
  --enable-workload-identity

# Enable multi-cluster services
gcloud container fleet multi-cluster-services enable

# Grant the required IAM role
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:PROJECT_ID.svc.id.goog[gke-mcs/gke-mcs-importer]" \
  --role="roles/compute.networkViewer"
```

```yaml
# Export a service from Cluster A
apiVersion: net.gke.io/v1
kind: ServiceExport
metadata:
  name: fraud-detection
  namespace: payments
---
# The MCS controller automatically creates a ServiceImport
# in all clusters in the fleet. Pods can now resolve:
# fraud-detection.payments.svc.clusterset.local
#
# This returns endpoints from ALL clusters that export
# the same service name in the same namespace.
```

### MCS API vs. Cilium Cluster Mesh

| Feature | MCS API | Cilium Cluster Mesh |
|---|---|---|
| Kubernetes-native | Yes (KEP-1645) | No (Cilium-specific) |
| Service discovery | DNS (clusterset.local) | eBPF (transparent) |
| Pod-to-pod direct | Depends on implementation | Yes (requires flat network) |
| Network policy across clusters | No | Yes (CiliumNetworkPolicy) |
| Cloud support | GKE native, others via Submariner | Any (self-managed) |
| Overlapping pod CIDRs | Depends on implementation | No (requires unique CIDRs) |
| Service affinity (prefer local) | Via topology hints | Via annotation |
| Maturity | GA on GKE, alpha elsewhere | GA (Cilium 1.14+) |

---

## Cross-AZ and Cross-Region Cost Management

Cross-cluster networking is not just a technical challenge -- it is a cost challenge. When clusters span availability zones or regions, every byte of cross-boundary traffic has a price.

### Topology-Aware Routing

Kubernetes 1.27+ supports topology hints that tell kube-proxy to prefer endpoints in the same zone.

```yaml
# Enable topology-aware routing on a service
apiVersion: v1
kind: Service
metadata:
  name: fraud-detection
  namespace: payments
  annotations:
    service.kubernetes.io/topology-mode: Auto
spec:
  selector:
    app: fraud-detection
  ports:
    - port: 8080
```

```
TOPOLOGY-AWARE ROUTING
════════════════════════════════════════════════════════════════

WITHOUT topology hints:            WITH topology hints:
  AZ-a        AZ-b                   AZ-a        AZ-b
  ┌─────┐    ┌─────┐                ┌─────┐    ┌─────┐
  │ Cli │───▶│ Svc │ Cross-AZ!      │ Cli │    │     │
  │     │    │ Pod │ $0.01/GB       │     │    │ Svc │
  │     │    └─────┘                │     │    │ Pod │
  │     │    ┌─────┐                │  ┌──┴──┐ └─────┘
  │     │    │ Svc │                │  │ Svc │
  │     │───▶│ Pod │ Cross-AZ!      │  │ Pod │ Same-AZ!
  └─────┘    └─────┘                └──┴─────┘ Free!
                                      │
  kube-proxy picks randomly           kube-proxy prefers
  from all endpoints                  same-zone endpoints
```

### Monitoring Cross-AZ Traffic

```bash
# Use VPC Flow Logs to identify cross-AZ traffic patterns
# Enable flow logs on each subnet
aws ec2 create-flow-logs \
  --resource-type Subnet \
  --resource-ids subnet-prod-az1a subnet-prod-az1b subnet-prod-az1c \
  --traffic-type ALL \
  --log-destination-type s3 \
  --log-destination arn:aws:s3:::vpc-flow-logs-bucket \
  --log-format '${az-id} ${srcaddr} ${dstaddr} ${bytes} ${flow-direction}'

# Query with Athena to find top cross-AZ talkers
# (assumes flow logs are partitioned in S3)
cat <<'SQL'
SELECT
  srcaddr,
  dstaddr,
  az_id,
  SUM(bytes) / 1073741824 AS gb_transferred,
  SUM(bytes) / 1073741824 * 0.01 AS estimated_cost_usd
FROM vpc_flow_logs
WHERE srcaddr LIKE '100.64.%'   -- pod CIDR
  AND dstaddr LIKE '100.64.%'   -- pod CIDR
  AND az_id != dst_az_id         -- cross-AZ
  AND date = '2026-03-24'
GROUP BY srcaddr, dstaddr, az_id
ORDER BY gb_transferred DESC
LIMIT 20
SQL
```

> **Stop and think**: Does topology-aware routing guarantee that cross-AZ traffic will never happen? What triggers kube-proxy to spill traffic over to another zone?

---

## Global Load Balancing

When you run clusters in multiple regions, you need a way to route users to the nearest healthy cluster. Global load balancing solves this at the edge.

### Cloud-Native Global LB Options

```
GLOBAL LOAD BALANCING COMPARISON
════════════════════════════════════════════════════════════════

AWS: Route53 + Global Accelerator
  Route53: DNS-based (latency/geolocation/failover routing)
  Global Accelerator: Anycast IP, TCP/UDP level, health checks

GCP: Cloud Load Balancing (Global)
  Single anycast IP for the entire world
  HTTP(S), TCP, UDP load balancing
  Native integration with GKE NEG (Network Endpoint Groups)

Azure: Front Door + Traffic Manager
  Front Door: HTTP/HTTPS, edge caching, WAF
  Traffic Manager: DNS-based, any protocol

Cloudflare / Fastly / Akamai:
  CDN + LB, provider-agnostic, works across clouds
```

### GCP Global Load Balancer with Multi-Cluster Gateway

```yaml
# GKE Gateway API with multi-cluster support
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: global-gateway
  namespace: payments
spec:
  gatewayClassName: gke-l7-global-external-managed-mc
  listeners:
    - name: https
      port: 443
      protocol: HTTPS
      tls:
        mode: Terminate
        certificateRefs:
          - name: payments-tls
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: payments-route
  namespace: payments
spec:
  parentRefs:
    - name: global-gateway
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api/payments
      backendRefs:
        - group: net.gke.io
          kind: ServiceImport
          name: payments-api
          port: 8080
```

### DNS-Based Failover with Route53

```bash
# Create health checks for each regional endpoint
HEALTH_CHECK_EAST=$(aws route53 create-health-check \
  --caller-reference "east-$(date +%s)" \
  --health-check-config '{
    "Type": "HTTPS",
    "ResourcePath": "/healthz",
    "FullyQualifiedDomainName": "east.api.example.com",
    "Port": 443,
    "RequestInterval": 10,
    "FailureThreshold": 3
  }' \
  --query 'HealthCheck.Id' --output text)

HEALTH_CHECK_WEST=$(aws route53 create-health-check \
  --caller-reference "west-$(date +%s)" \
  --health-check-config '{
    "Type": "HTTPS",
    "ResourcePath": "/healthz",
    "FullyQualifiedDomainName": "west.api.example.com",
    "Port": 443,
    "RequestInterval": 10,
    "FailureThreshold": 3
  }' \
  --query 'HealthCheck.Id' --output text)

# Create latency-based routing with failover
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890 \
  --change-batch '{
    "Changes": [
      {
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "api.example.com",
          "Type": "A",
          "SetIdentifier": "us-east-1",
          "Region": "us-east-1",
          "AliasTarget": {
            "HostedZoneId": "Z2FDTNDATAQYW2",
            "DNSName": "east-nlb-abc123.elb.us-east-1.amazonaws.com",
            "EvaluateTargetHealth": true
          },
          "HealthCheckId": "'$HEALTH_CHECK_EAST'"
        }
      },
      {
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "api.example.com",
          "Type": "A",
          "SetIdentifier": "eu-west-1",
          "Region": "eu-west-1",
          "AliasTarget": {
            "HostedZoneId": "Z32O12XQLNTSW2",
            "DNSName": "west-nlb-xyz789.elb.eu-west-1.amazonaws.com",
            "EvaluateTargetHealth": true
          },
          "HealthCheckId": "'$HEALTH_CHECK_WEST'"
        }
      }
    ]
  }'
```

---

## Split-Brain: The Multi-Cluster Nightmare

Split-brain occurs when clusters lose connectivity to each other but continue operating independently. Each cluster believes it is the authoritative source of truth. When connectivity restores, you have conflicting state.

```
SPLIT-BRAIN SCENARIO
════════════════════════════════════════════════════════════════

  Normal Operation:
  Cluster A ◄────────────────────► Cluster B
  "User X balance: $500"           "User X balance: $500"

  Network partition occurs:
  Cluster A          ╳              Cluster B
  User deposits $100               User withdraws $200
  "User X: $600"                   "User X: $300"

  Network restores:
  Cluster A ◄────────────────────► Cluster B
  "User X: $600"    vs             "User X: $300"

  Which is correct? BOTH are. And NEITHER is.
  The real answer should be $400 ($500 + $100 - $200)
  but neither cluster knows about the other's operation.
```

### Mitigation Strategies

**Strategy 1: Single writer, multiple readers.** Only one cluster can write to a given data partition. Other clusters serve read-only copies. If the writer fails, promote a reader (with potential data loss).

**Strategy 2: CRDTs (Conflict-free Replicated Data Types).** Design your data structures so that concurrent modifications can be automatically merged. Counters, sets, and registers can all be made conflict-free, but this requires application-level changes.

**Strategy 3: Fencing tokens.** The write path requires a token from a distributed lock service (like etcd or ZooKeeper). During a partition, only the cluster that holds the token can write. The other cluster rejects writes until it reacquires the token.

```yaml
# Strategy 1: Leader election for cross-cluster write authority
# Using a Kubernetes Lease object in a "coordination" cluster
apiVersion: coordination.k8s.io/v1
kind: Lease
metadata:
  name: payments-write-leader
  namespace: coordination
spec:
  holderIdentity: cluster-a
  leaseDurationSeconds: 30
  acquireTime: "2026-03-24T10:15:00Z"
  renewTime: "2026-03-24T10:15:25Z"
  leaseTransitions: 3
```

```python
# Application-level split-brain detection
# Each cluster periodically checks if it can reach the other
import requests
import time

PEER_CLUSTERS = {
    "cluster-b": "https://cluster-b.internal.example.com/healthz",
    "cluster-c": "https://cluster-c.internal.example.com/healthz",
}

def check_partition():
    """Detect if we're in a network partition."""
    unreachable = []
    for cluster, url in PEER_CLUSTERS.items():
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code != 200:
                unreachable.append(cluster)
        except requests.exceptions.RequestException:
            unreachable.append(cluster)

    if unreachable:
        # We might be partitioned. Switch to safe mode:
        # - Reject writes that require cross-cluster consistency
        # - Continue serving reads from local cache
        # - Alert the on-call team
        enter_safe_mode(unreachable)
        return True
    return False

def enter_safe_mode(unreachable_clusters):
    """Restrict operations during detected partition."""
    print(f"PARTITION DETECTED: Cannot reach {unreachable_clusters}")
    print("Entering safe mode: rejecting cross-cluster writes")
    # Set a readiness probe to fail for write endpoints
    # This makes the load balancer stop sending write traffic here
    with open("/tmp/write-ready", "w") as f:
        f.write("false")
```

> **Pause and predict**: If you use a single-writer, multiple-reader database architecture across two clusters, what happens to write requests during a network partition if the active writer is in the partitioned cluster?

---

## Did You Know?

1. **Cilium Cluster Mesh can connect up to 511 clusters** in a single mesh (limited by the cluster ID field, which is 9 bits minus the zero value). In practice, most organizations connect 3-10 clusters, but the theoretical limit means Cilium can scale to truly massive multi-cluster deployments. Each cluster can have up to 64,000 nodes.

2. **Cross-AZ data transfer in AWS generated an estimated $1 billion in revenue for Amazon in 2023** according to industry analysts. This single line item -- charging $0.01/GB for traffic between availability zones in the same region -- is one of the most profitable products in cloud computing. GCP made cross-zone traffic free in 2022, pressuring AWS to reduce (but not eliminate) these charges.

3. **The Multi-Cluster Services API (KEP-1645) was first proposed in 2019** and reached beta in GKE in 2022, but is still not universally available across all Kubernetes distributions. The slow adoption reflects the genuine complexity of the problem: service discovery across trust boundaries, with potentially overlapping namespaces and conflicting RBAC policies, is fundamentally harder than single-cluster service discovery.

4. **Google's internal cluster networking system, called Borg Naming Service (BNS)**, has supported cross-cluster service discovery since the early 2010s. The MCS API and GKE's multi-cluster services are directly inspired by BNS's architecture, where every job across every cluster is discoverable via a hierarchical naming scheme: `/bns/<cluster>/<user>/<job>/<task>`.

---

## Common Mistakes

| Mistake | Why It Happens | How to Fix It |
|---|---|---|
| Overlapping pod CIDRs across clusters | Default CNI settings use the same range (e.g., 10.244.0.0/16) | Plan pod CIDRs before deploying clusters. Use unique ranges (100.64.x.0/16, 100.65.x.0/16, etc.) |
| Hardcoding ClusterIPs in config | Works in single-cluster, breaks in multi-cluster | Use DNS names (service.namespace.svc.cluster.local) or MCS API (service.namespace.svc.clusterset.local) |
| Not considering DNS TTL during failover | DNS records have TTLs that clients cache | Set health check intervals to 10s and DNS TTL to 30-60s. Use Global Accelerator (anycast) for instant failover without DNS. |
| Ignoring cross-AZ costs for pod traffic | "It's just a penny per GB" | For 50TB/month cross-AZ: $1,000/month. Enable topology-aware routing. Monitor with VPC Flow Logs. |
| Using ClusterIP services for cross-cluster communication | ClusterIPs are local to each cluster | Use LoadBalancer or NodePort services, or Cilium global services, or MCS API ServiceExport |
| No health checking for cross-cluster endpoints | Assuming remote cluster is always healthy | Implement active health checks. Use Cilium's built-in health probing or external health check endpoints. |
| Flat networking without network policies | "Any pod can reach any pod" is convenient but dangerous | Deploy CiliumNetworkPolicy or NetworkPolicy to restrict cross-cluster traffic to explicitly allowed paths. |
| Not testing split-brain scenarios | "The network never partitions" | It does. Run chaos engineering experiments (disconnect clusters, observe behavior). Implement partition detection and safe mode. |

---

## Quiz

<details>
<summary>1. Your organization is merging with another company. You now have 15 clusters spread across AWS, GCP, and on-premises environments, with overlapping 10.244.0.0/16 pod subnets. Would you choose an island or flat networking model to connect these clusters, and why?</summary>

You would choose the island networking model for this scenario. Island networking is required here because flat networking demands globally unique pod CIDRs, which you no longer have due to the overlapping subnets from the merger. Furthermore, flat networking scales poorly beyond a handful of clusters and is notoriously difficult to configure across disparate cloud providers and on-premises boundaries. By treating each cluster as an isolated island, you rely on explicit gateways to route cross-cluster traffic, completely sidestepping the IP overlap issue and maintaining clean administrative boundaries across the 15 clusters.
</details>

<details>
<summary>2. Your platform team is debating whether to implement Cilium Cluster Mesh or the Kubernetes Multi-Cluster Services (MCS) API to allow frontend pods in cluster A to discover backend pods in cluster B. If the team requires the service discovery mechanism to be completely transparent to the application code without changing DNS suffixes, which solution should they choose and why?</summary>

The team should choose Cilium Cluster Mesh for this requirement. Cilium Cluster Mesh operates transparently at the eBPF and kernel level, intercepting standard Kubernetes DNS requests and seamlessly load-balancing across local and remote endpoints using the exact same `cluster.local` DNS name. In contrast, the MCS API introduces a new DNS suffix (`clusterset.local`), which would require the application code or configuration to explicitly target the new domain to reach cross-cluster endpoints. Because Cilium merges services with the same name and namespace across clusters, it satisfies the requirement for zero application-level changes while enabling global discovery.
</details>

<details>
<summary>3. A service has 6 replicas: 4 running in us-east-1a and 2 running in us-east-1b. A client pod makes a request from us-east-1a. How does traffic distribution change if you enable topology-aware routing on the service?</summary>

Without topology hints, kube-proxy randomly distributes traffic across all 6 endpoints, meaning roughly 33% of requests from the client in `us-east-1a` would cross the availability zone boundary to `us-east-1b`. With topology-aware routing enabled (`topology-mode: Auto`), kube-proxy creates endpoint slices that heavily prefer routing traffic to endpoints located in the exact same zone as the requesting client. Because there are four healthy endpoints available in `us-east-1a` to handle the load, kube-proxy will route nearly 100% of the client's traffic to those local endpoints. This eliminates the latency and the $0.01/GB cross-AZ data transfer charges that would otherwise occur.
</details>

<details>
<summary>4. Your multi-region payment gateway experiences a 10-minute network partition where the US-East and EU-West clusters lose connectivity to each other, but both remain online and accept user traffic. Explain the 'split-brain' phenomenon that occurs during this time and why it is dangerous for the system's data integrity.</summary>

During this partition, a 'split-brain' scenario occurs because both the US-East and EU-West clusters continue operating independently, with each believing it is the sole authoritative source of truth. This is incredibly dangerous because users might perform concurrent write operations—such as depositing funds in the US and withdrawing them in the EU—creating conflicting state changes that the system cannot easily reconcile once the network restores. Since neither cluster is aware of the other's transactions during the outage, simple synchronization will overwrite or lose data. To prevent catastrophic data corruption, systems must implement application-level mitigations like single-writer architectures, CRDTs, or strict partition detection that forces the system into a read-only safe mode.
</details>

<details>
<summary>5. You are tasked with exposing a critical internal API from Cluster A to Cluster B. However, you discover that both clusters were provisioned with the default 10.244.0.0/16 pod CIDR. What architectural options do you have to establish this connectivity despite the overlapping IP space?</summary>

Because the pod CIDRs overlap, direct pod-to-pod communication (flat networking) and tools like Cilium Cluster Mesh are immediately ruled out. Your most straightforward option is to expose the API in Cluster A via a LoadBalancer service (such as an internal NLB) and configure Cluster B's pods to call that load balancer's IP or DNS name. Alternatively, you could deploy an API Gateway or a service mesh east-west gateway to bridge the traffic between the environments without requiring routable pod IPs. If a long-term, native multi-cluster mesh is required, your only definitive solution is to rebuild or re-IP one of the clusters so their subnet ranges no longer conflict.
</details>

<details>
<summary>6. Your organization is designing a multi-region active-passive disaster recovery architecture for a mission-critical web application. The lead architect proposes using GCP Global Load Balancing instead of AWS Route53 DNS-based failover. Why might the architect prefer the GCP Global Load Balancer for this specific multi-region failover scenario?</summary>

The architect likely prefers GCP Global Load Balancing because it utilizes a single anycast IP address that routes traffic at the network edge, allowing for near-instantaneous failover when a region goes down. In contrast, Route53 relies on DNS-based failover, which is inherently limited by DNS TTLs and client-side caching behaviors. Even if you configure a very low TTL in Route53, many client devices and intermediate ISPs will cache the stale IP address, meaning it could take several minutes for all users to be routed to the healthy region. Furthermore, GCP's solution provides advanced L7 features like header-based routing and native integration with GKE network endpoint groups, which a pure DNS solution cannot match.
</details>

---

## Hands-On Exercise: Connect Two Clusters with Cilium Cluster Mesh

In this exercise, you will set up two local kind clusters, install Cilium with Cluster Mesh, and verify cross-cluster service discovery.

### Prerequisites

- Docker installed
- kind (Kubernetes in Docker) installed
- cilium CLI installed
- kubectl installed

### Task 1: Create Two kind Clusters

Create two clusters with non-overlapping pod CIDRs.

<details>
<summary>Solution</summary>

```bash
# Cluster A configuration
cat <<'EOF' > cluster-a.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  disableDefaultCNI: true
  podSubnet: "100.64.0.0/16"
  serviceSubnet: "10.96.0.0/16"
nodes:
  - role: control-plane
  - role: worker
  - role: worker
EOF

# Cluster B configuration
cat <<'EOF' > cluster-b.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  disableDefaultCNI: true
  podSubnet: "100.65.0.0/16"
  serviceSubnet: "10.97.0.0/16"
nodes:
  - role: control-plane
  - role: worker
  - role: worker
EOF

# Create clusters
kind create cluster --name cluster-a --config cluster-a.yaml
kind create cluster --name cluster-b --config cluster-b.yaml

# Verify both clusters are running
kubectl --context kind-cluster-a get nodes
kubectl --context kind-cluster-b get nodes
```
</details>

### Task 2: Install Cilium with Cluster Mesh

Install Cilium on both clusters with cluster mesh enabled.

<details>
<summary>Solution</summary>

```bash
# Install Cilium on Cluster A
cilium install --context kind-cluster-a \
  --set cluster.name=cluster-a \
  --set cluster.id=1 \
  --set ipam.mode=kubernetes

# Install Cilium on Cluster B
cilium install --context kind-cluster-b \
  --set cluster.name=cluster-b \
  --set cluster.id=2 \
  --set ipam.mode=kubernetes

# Wait for Cilium to be ready
cilium status --context kind-cluster-a --wait
cilium status --context kind-cluster-b --wait

# Enable cluster mesh
cilium clustermesh enable --context kind-cluster-a
cilium clustermesh enable --context kind-cluster-b

# Wait for cluster mesh to be ready
cilium clustermesh status --context kind-cluster-a --wait

# Connect the clusters
cilium clustermesh connect \
  --context kind-cluster-a \
  --destination-context kind-cluster-b

# Verify connection
cilium clustermesh status --context kind-cluster-a
```
</details>

### Task 3: Deploy a Global Service

Deploy a service in both clusters and verify cross-cluster discovery.

<details>
<summary>Solution</summary>

```bash
# Deploy the rebel-base service in both clusters
kubectl --context kind-cluster-a apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rebel-base
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: rebel-base
  template:
    metadata:
      labels:
        app: rebel-base
    spec:
      containers:
        - name: rebel-base
          image: docker.io/nginx:stable
          command: ["/bin/sh", "-c"]
          args:
            - |
              echo "Cluster A: Alderaan base" > /usr/share/nginx/html/index.html
              nginx -g "daemon off;"
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: rebel-base
  annotations:
    io.cilium/global-service: "true"
spec:
  selector:
    app: rebel-base
  ports:
    - port: 80
EOF

kubectl --context kind-cluster-b apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rebel-base
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: rebel-base
  template:
    metadata:
      labels:
        app: rebel-base
    spec:
      containers:
        - name: rebel-base
          image: docker.io/nginx:stable
          command: ["/bin/sh", "-c"]
          args:
            - |
              echo "Cluster B: Hoth base" > /usr/share/nginx/html/index.html
              nginx -g "daemon off;"
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: rebel-base
  annotations:
    io.cilium/global-service: "true"
spec:
  selector:
    app: rebel-base
  ports:
    - port: 80
EOF
```
</details>

### Task 4: Verify Cross-Cluster Load Balancing

Run a client pod and verify that requests are load-balanced across both clusters.

<details>
<summary>Solution</summary>

```bash
# Run a test pod in Cluster A
kubectl --context kind-cluster-a run test-client \
  --image=curlimages/curl \
  --restart=Never \
  --rm -it -- sh -c '
    echo "Testing cross-cluster load balancing..."
    for i in $(seq 1 20); do
      curl -s http://rebel-base.default.svc.cluster.local
    done | sort | uniq -c | sort -rn
  '

# Expected output (roughly even distribution):
#   10 Cluster A: Alderaan base
#   10 Cluster B: Hoth base

# Now test with local affinity
kubectl --context kind-cluster-a annotate service rebel-base \
  io.cilium/service-affinity=local --overwrite

# Run the test again - should strongly prefer Cluster A
kubectl --context kind-cluster-a run test-client-2 \
  --image=curlimages/curl \
  --restart=Never \
  --rm -it -- sh -c '
    for i in $(seq 1 20); do
      curl -s http://rebel-base.default.svc.cluster.local
    done | sort | uniq -c | sort -rn
  '

# Expected output (mostly local):
#   18 Cluster A: Alderaan base
#    2 Cluster B: Hoth base
```
</details>

### Task 5: Clean Up

```bash
kind delete cluster --name cluster-a
kind delete cluster --name cluster-b
rm cluster-a.yaml cluster-b.yaml
```

### Success Criteria

- [ ] Two kind clusters created with non-overlapping pod CIDRs
- [ ] Cilium installed and healthy on both clusters
- [ ] Cluster Mesh connected (cilium clustermesh status shows connected)
- [ ] Global service deployed and accessible from both clusters
- [ ] Cross-cluster load balancing verified (responses from both clusters)
- [ ] Service affinity tested (local preference works)

---

## Next Module

[Module 8.4: Cross-Account IAM & Enterprise Identity](../module-8.4-enterprise-identity/) -- Now that your clusters can talk to each other across accounts, learn how to manage WHO can access WHAT. Cross-account roles, workload identity federation, and the art of building trust boundaries that don't become bottlenecks.