---
title: "Module 15.1: CockroachDB - Distributed SQL That Survives Anything"
slug: platform/toolkits/data-ai-platforms/cloud-native-databases/module-15.1-cockroachdb
sidebar:
  order: 2
---
## Complexity: [COMPLEX]
## Time to Complete: 55-65 minutes

---

## Prerequisites

Before starting this module, you should have completed:
- [Distributed Systems Foundation](/platform/foundations/distributed-systems/) - Consensus, CAP theorem
- [Reliability Engineering Foundation](/platform/foundations/reliability-engineering/) - SLOs, failure modes
- Basic SQL and PostgreSQL familiarity
- Kubernetes fundamentals (StatefulSets, PVCs)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

- **Deploy CockroachDB on Kubernetes with multi-region topology and automatic data replication**
- **Configure CockroachDB zone configurations and locality-aware queries for geo-distributed applications**
- **Implement CockroachDB backup schedules, changefeeds, and rolling upgrades for production operations**
- **Evaluate CockroachDB's distributed SQL capabilities against traditional PostgreSQL for global applications**


## Why This Module Matters

**The $4.2 Million Phone Call That Never Came**

A regional cloud outage can turn a manually operated failover plan into an expensive, high-stress incident for a high-volume platform.

Last year, this exact scenario had been catastrophic:

| 2022 Aurora PostgreSQL Outage | Impact |
|-------------------------------|--------|
| Detection time | Several minutes passed before humans recognized the problem |
| Manual failover coordination | Manual failover added substantial operational delay |
| DNS propagation to DR site | DNS cutover added more recovery delay |
| Cache warming in us-west-2 | Recovery also required warm-up time in the failover region |
| **Total downtime** | **Nearly an hour of disruption** |
| **Revenue lost** | **Substantial revenue was at risk during the outage** |
| **SLA credits issued** | **Customer remediation costs followed the outage** |
| **Customer churn (90 days)** | **Some longer-tail customer impact followed the incident** |
| **Post-incident engineering** | **Significant follow-up engineering work was required** |

Tonight was different. Six months ago, they'd migrated to CockroachDB.

The engineer watched the dashboard. Traffic automatically shifted to us-west-2 and eu-west-1. Latency increased by 50ms for affected users. The database never even paged her—the latency spike wasn't severe enough to trigger alerts.

She went back to sleep.

**CockroachDB is designed so leadership can move automatically after failures, reducing or avoiding manual failover work when quorum is preserved.**

This is what CockroachDB was built for: a distributed SQL database that treats datacenter failures as routine events, not emergencies. Named after the famously resilient insect, it uses [the same Raft consensus algorithm that powers etcd and Kubernetes itself](https://github.com/etcd-io/raft).

---

## Did You Know?

- **DoorDash has described moving important workloads from Aurora Postgres to CockroachDB** — The defensible lesson here is about reducing single-database blast radius and improving resilience, not a precise annual savings number.

- **Cockroach Labs has raised significant funding around the argument that resilience matters** — Major outages can be extremely expensive for large businesses, but precise fundraising and outage-loss figures need direct sourcing.

- **Some teams use active-active database designs to reduce the cost and complexity of warm-standby disaster recovery** — Exact savings depend on the workload, topology, and licensing model.

- **Features like `REGIONAL BY ROW` can help support data-locality and residency requirements** — Compliance outcomes still depend on the full system design and legal review, not just one database feature.

---

## How CockroachDB Works

```
COCKROACHDB ARCHITECTURE
─────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────┐
│                    CockroachDB Cluster                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SQL Layer (PostgreSQL-compatible)                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • Parses SQL queries                                     │  │
│  │  • Query planning and optimization                        │  │
│  │  • Distributed query execution                            │  │
│  │  • Transaction coordination                               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            │                                     │
│                            ▼                                     │
│  Transaction Layer                                               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • MVCC (Multi-Version Concurrency Control)               │  │
│  │  • Serializable isolation by default                      │  │
│  │  • Distributed transactions with 2PC                      │  │
│  │  • Automatic transaction retries                          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            │                                     │
│                            ▼                                     │
│  Distribution Layer                                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • Data divided into "ranges" (~512MB each)               │  │
│  │  • Each range replicated 3x (configurable)                │  │
│  │  • Raft consensus per range                               │  │
│  │  • Automatic rebalancing and splitting                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            │                                     │
│                            ▼                                     │
│  Storage Layer (Pebble - LSM-tree)                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • Key-value storage engine                               │  │
│  │  • SSTable-based (like RocksDB/LevelDB)                   │  │
│  │  • Compression and encryption at rest                     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Ranges and Replication

```
DATA DISTRIBUTION WITH RANGES
─────────────────────────────────────────────────────────────────

Table: orders (1TB of data)
─────────────────────────────────────────────────────────────────

Split into ~2000 ranges (512MB each):
┌──────────┐ ┌──────────┐ ┌──────────┐     ┌──────────┐
│ Range 1  │ │ Range 2  │ │ Range 3  │ ... │Range 2000│
│ order_id │ │ order_id │ │ order_id │     │ order_id │
│  1-5000  │ │5001-10000│ │10001-15k │     │  ...     │
└──────────┘ └──────────┘ └──────────┘     └──────────┘

Each range replicated 3x across nodes:
─────────────────────────────────────────────────────────────────

Range 1:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Node 1    │    │   Node 2    │    │   Node 3    │
│  (Leader)   │───▶│  (Follower) │    │  (Follower) │
│   Range 1   │    │   Range 1   │    │   Range 1   │
│   ██████    │    │   ██████    │    │   ██████    │
└─────────────┘    └─────────────┘    └─────────────┘
      │                   │                  │
      │   Raft consensus ensures all        │
      │   replicas agree before commit      │
      └───────────────────┴──────────────────┘

Range 2 has DIFFERENT leader (distributed leadership):
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Node 1    │    │   Node 2    │    │   Node 3    │
│  (Follower) │    │  (Leader)   │───▶│  (Follower) │
│   Range 2   │    │   Range 2   │    │   Range 2   │
└─────────────┘    └─────────────┘    └─────────────┘

Result: No single point of failure, load distributed across nodes
```

### Multi-Region Architecture

```
MULTI-REGION DEPLOYMENT
─────────────────────────────────────────────────────────────────

                         Global DNS / Load Balancer
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    US-EAST      │     │    US-WEST      │     │    EU-WEST      │
│                 │     │                 │     │                 │
│  ┌───────────┐  │     │  ┌───────────┐  │     │  ┌───────────┐  │
│  │  Node 1   │  │     │  │  Node 4   │  │     │  │  Node 7   │  │
│  │  Node 2   │◄─┼─────┼─▶│  Node 5   │◄─┼─────┼─▶│  Node 8   │  │
│  │  Node 3   │  │     │  │  Node 6   │  │     │  │  Node 9   │  │
│  └───────────┘  │     │  └───────────┘  │     │  └───────────┘  │
│                 │     │                 │     │                 │
│  ┌───────────┐  │     │  ┌───────────┐  │     │  ┌───────────┐  │
│  │   Apps    │  │     │  │   Apps    │  │     │  │   Apps    │  │
│  └───────────┘  │     │  └───────────┘  │     │  └───────────┘  │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘

Cross-region latency: ~70ms US-East to US-West, ~90ms to EU

WRITE PATH (consensus required):
─────────────────────────────────────────────────────────────────
App (US-East) → Local node → Raft consensus (2/3 regions) → Commit
                             │
                             └─ If range leader is in US-East: ~5ms
                                If range leader is in US-West: ~70ms + 5ms
                                If range leader is in EU-West: ~90ms + 5ms

READ PATH (local reads with follower reads enabled):
─────────────────────────────────────────────────────────────────
App (US-East) → Local node → Read from local replica → Return
                             (slightly stale, ~1-5ms behind)

App (US-East) → Local node → Consistent read (default) → Return
                             (contacts leader, may cross region)
```

---

## Installing CockroachDB on Kubernetes

### Option 1: Helm Chart (Recommended)

```bash
# Add CockroachDB Helm repository
helm repo add cockroachdb https://charts.cockroachdb.com/
helm repo update

# Create namespace
kubectl create namespace cockroachdb

# Install CockroachDB cluster
helm install cockroachdb cockroachdb/cockroachdb \
  --namespace cockroachdb \
  --set statefulset.replicas=3 \
  --set storage.persistentVolume.size=100Gi \
  --set storage.persistentVolume.storageClass=premium-ssd

# Wait for pods to be ready
kubectl rollout status statefulset/cockroachdb -n cockroachdb

# Initialize the cluster (first time only)
kubectl exec -n cockroachdb -it cockroachdb-0 -- \
  /cockroach/cockroach init --certs-dir=/cockroach/cockroach-certs
```

### Option 2: CockroachDB Operator

```yaml
# cockroachdb-operator.yaml
apiVersion: crdb.cockroachlabs.com/v1alpha1
kind: CrdbCluster
metadata:
  name: cockroachdb
  namespace: cockroachdb
spec:
  dataStore:
    pvc:
      spec:
        accessModes:
          - ReadWriteOnce
        resources:
          requests:
            storage: 100Gi
        storageClassName: premium-ssd
  resources:
    requests:
      cpu: "2"
      memory: "8Gi"
    limits:
      cpu: "4"
      memory: "16Gi"
  tlsEnabled: true
  image:
    name: cockroachdb/cockroach:v23.2.0
  nodes: 3
  additionalLabels:
    app: cockroachdb
  topology:
    - locality: region=us-east,zone=us-east-1a
      nodeCount: 1
    - locality: region=us-east,zone=us-east-1b
      nodeCount: 1
    - locality: region=us-east,zone=us-east-1c
      nodeCount: 1
```

```bash
# Install the operator
kubectl apply -f https://raw.githubusercontent.com/cockroachdb/cockroach-operator/master/install/crds.yaml
kubectl apply -f https://raw.githubusercontent.com/cockroachdb/cockroach-operator/master/install/operator.yaml

# Deploy the cluster
kubectl apply -f cockroachdb-operator.yaml
```

### Verifying Installation

```bash
# Check pod status
kubectl get pods -n cockroachdb
# NAME            READY   STATUS    RESTARTS   AGE
# cockroachdb-0   1/1     Running   0          5m
# cockroachdb-1   1/1     Running   0          4m
# cockroachdb-2   1/1     Running   0          3m

# Access the SQL shell
kubectl exec -n cockroachdb -it cockroachdb-0 -- \
  /cockroach/cockroach sql --certs-dir=/cockroach/cockroach-certs

# Check cluster status
root@cockroachdb-0:26257/defaultdb> SHOW CLUSTER SETTING version;
# 23.2

# View node status
root@cockroachdb-0:26257/defaultdb> SELECT node_id, address, locality FROM crdb_internal.gossip_nodes;
```

---

## Core Operations

### Creating Databases and Users

```sql
-- Create a database
CREATE DATABASE myapp;

-- Create a user with password
CREATE USER app_user WITH PASSWORD 'securepassword';

-- Grant permissions
GRANT ALL ON DATABASE myapp TO app_user;

-- Create schema with appropriate settings
USE myapp;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email STRING NOT NULL UNIQUE,
    name STRING NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    region STRING NOT NULL,

    INDEX idx_users_email (email),
    INDEX idx_users_region (region)
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    total DECIMAL(10,2) NOT NULL,
    status STRING NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT now(),

    INDEX idx_orders_user (user_id),
    INDEX idx_orders_status (status)
);
```

### Multi-Region Configuration

```sql
-- Enable multi-region (requires enterprise license or use free tier)
ALTER DATABASE myapp PRIMARY REGION "us-east";
ALTER DATABASE myapp ADD REGION "us-west";
ALTER DATABASE myapp ADD REGION "eu-west";

-- Configure survival goal
ALTER DATABASE myapp SURVIVE REGION FAILURE;

-- Regional by row (data stays in user's region)
ALTER TABLE users SET LOCALITY REGIONAL BY ROW AS region;

-- Now queries automatically route to the right region:
INSERT INTO users (email, name, region)
VALUES ('alice@example.de', 'Alice', 'eu-west');
-- This row is stored in EU region

SELECT * FROM users WHERE region = 'eu-west';
-- This query served from EU region (low latency for EU users)
```

### Monitoring and Observability

```yaml
# ServiceMonitor for Prometheus
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: cockroachdb
  namespace: cockroachdb
spec:
  selector:
    matchLabels:
      app: cockroachdb
  endpoints:
    - port: http
      path: /_status/vars
      interval: 15s
```

```bash
# Access the built-in Admin UI
kubectl port-forward svc/cockroachdb-public -n cockroachdb 8080:8080

# Open http://localhost:8080
# Shows: Cluster health, query performance, range distribution, hot spots
```

### Key Metrics to Monitor

```
CRITICAL COCKROACHDB METRICS
─────────────────────────────────────────────────────────────────

Cluster Health:
├── liveness_livenodes      # Should equal total nodes
├── ranges_unavailable      # Should be 0
├── ranges_underreplicated  # Should be 0 (replication catching up)

Performance:
├── sql_query_latency_p99   # Target: <100ms for OLTP
├── sql_txn_latency_p99     # Transaction latency
├── sql_conns               # Active connections
├── sql_statements_total    # Query throughput

Replication:
├── raft_leader_not_found   # Should be 0
├── raft_leader_transfers   # Spikes indicate instability
├── replication_lag         # Should be <100ms typically

Storage:
├── capacity_used_percent   # Alert at 80%
├── rocksdb_compactions     # Background work
├── gc_pause_total          # GC impact
```

---

## War Story: The Black Friday That Didn't Burn

*How an e-commerce platform survived their biggest sales day with zero incidents*

### The Setup

A fast-growing e-commerce company was preparing for Black Friday 2023. Previous years had been nightmares:
- Earlier peak events exposed scaling limits in the prior Aurora PostgreSQL design.
- A previous peak-season incident still required manual failover and caused customer-visible degradation.

For 2023, they migrated to CockroachDB six months before Black Friday.

### The Architecture

```
BLACK FRIDAY ARCHITECTURE
─────────────────────────────────────────────────────────────────

                    CloudFront CDN
                         │
                    ┌────┴────┐
                    │   ALB   │
                    └────┬────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  us-east-1  │  │  us-west-2  │  │  eu-west-1  │
│             │  │             │  │             │
│ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │
│ │ CRDB ×3 │ │  │ │ CRDB ×3 │ │  │ │ CRDB ×3 │ │
│ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │
│      │      │  │      │      │  │      │      │
│ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │
│ │ App ×50 │ │  │ │ App ×50 │ │  │ │ App ×20 │ │
│ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │
└─────────────┘  └─────────────┘  └─────────────┘

Total: 9 CockroachDB nodes, 120 app instances
Peak capacity: 150K TPS (tested)
```

### Black Friday Timeline

**6:00 AM EST - Early Birds**
- Traffic: 5,000 TPS (normal)
- Latency: P99 = 12ms
- Status: All green

**9:00 AM EST - Deal Drops**
- Traffic spikes to 45,000 TPS
- CockroachDB automatically rebalances hot ranges
- Some inventory rows become "hot" (everyone wants the same TV)
- Latency: P99 = 45ms (still fine)

**12:00 PM EST - The Surge**
```
┌─────────────────────────────────────────────────────────────┐
│ TRAFFIC SPIKE - NOON BLACK FRIDAY                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ TPS     ▲                                                  │
│ 100K    │                    ████                          │
│         │                  ██████████                      │
│  80K    │                ████████████████                  │
│         │              ████████████████████                │
│  60K    │            ████████████████████████              │
│         │          ██████████████████████████              │
│  40K    │        ████████████████████████████████          │
│         │      ████████████████████████████████████        │
│  20K    │    ██████████████████████████████████████████    │
│         │  ████████████████████████████████████████████████│
│     0   └──────────────────────────────────────────────────▶
│           6AM    9AM    12PM   3PM    6PM    9PM   Time    │
│                                                             │
│ Peak: 98,000 TPS at 12:47 PM                               │
└─────────────────────────────────────────────────────────────┘
```

**12:45 PM EST - The Test**
- Traffic: 98,000 TPS (peak)
- A peak-period availability-zone network issue briefly disrupted part of the deployment
- Several CockroachDB nodes in the affected zone became temporarily unreachable

**What happened:**
1. Raft leaders in us-east-1a couldn't reach followers
2. New leaders were elected automatically on surviving replicas after the failure
3. Write latency increased noticeably for the affected ranges during failover
4. Application retries can hide some failover turbulence, but exact transaction outcomes need real evidence
5. Whether data loss occurs depends on quorum, replication, and the exact failure mode

**12:52 PM EST - Recovery**
- us-east-1a network recovered
- Nodes rejoined cluster
- Replication caught up shortly after the affected nodes returned
- Latency returned to normal

### The Numbers

| Metric | 2022 (Aurora) | 2023 (CockroachDB) |
|--------|---------------|-------------------|
| Peak TPS | Lower peak throughput | Higher peak throughput after the migration |
| Downtime | Customer-visible outage occurred | Much lower disruption was the goal of the new design |
| Failed transactions | Many transactions failed under load | Transaction impact was materially lower in the newer design |
| Data loss | No data loss was reported in this anecdote | The design goal was to preserve committed data during failures |
| Lost revenue | Significant revenue was at risk during the outage | Lower disruption reduced business impact |
| On-call pages | Heavy pager load | Far fewer human interventions were needed |

### Financial Impact: Black Friday 2023 vs 2022

| Category | 2022 (Aurora) | 2023 (CockroachDB) | Impact |
|----------|---------------|-------------------|--------|
| **Direct revenue loss** | Significant outage cost | Reduced outage cost | Improvement depends on real incident frequency |
| **SLA credits issued** | Customer remediation cost | Reduced remediation cost | Improvement depends on actual contracts and incidents |
| **Customer churn (30 days)** | Some longer-tail business impact | Lower disruption can reduce follow-on impact | Effect size depends on real customer behavior |
| **Brand damage (est.)** | Reputational cost was possible | Lower disruption can reduce reputational risk | This effect is hard to quantify precisely |
| **Engineering overtime** | Extra staffing cost | Lower incident load can reduce overtime | Savings depend on team structure and incident history |
| **Post-mortem & fixes** | Follow-up engineering cost | Lower disruption can reduce follow-up work | Savings depend on the actual incident profile |
| **CockroachDB license cost** | $0 | Recurring platform cost | Ongoing cost depends on edition, scale, and contract |
| **Migration investment** | $0 | One-time migration cost | Migration cost depends heavily on scope and staffing |
| **Net Impact (Year 1)** | | | **Business value depends on actual outage rates and migration costs** |
| **Net Impact (Ongoing)** | | | **Ongoing value depends on steady-state operating costs and avoided incidents** |

A resilience migration can have a strong business case, but it should be argued with a real postmortem and a finance model rather than an invented boardroom quote.

### Lessons Learned

1. **Distributed by default beats manual failover** — CockroachDB's automatic leader election meant no human intervention needed
2. **Test at scale before you need scale** — They ran 150K TPS tests in staging
3. **Hot spots need attention** — Pre-sharded popular product inventory tables
4. **Connection pooling matters** — PgBouncer in front of CockroachDB for 10K+ connections
5. **Regional read replicas reduce latency** — Follower reads for product catalog

---

## CockroachDB vs Alternatives

```
DATABASE COMPARISON FOR DISTRIBUTED WORKLOADS
─────────────────────────────────────────────────────────────────

                    CockroachDB  Spanner    Aurora     YugabyteDB
─────────────────────────────────────────────────────────────────
ARCHITECTURE
Distributed         ✓✓           ✓✓         ✗          ✓✓
Multi-region        ✓✓           ✓✓         Limited    ✓✓
Self-hosted         ✓            ✗          ✗          ✓
Cloud-native        ✓            ✓          ✓          ✓

CONSISTENCY
Serializable        ✓ (default)  ✓          ✗          ✓
Strong consistency  ✓            ✓          ✓          ✓
Global consistency  ✓            ✓✓         ✗          ✓

COMPATIBILITY
PostgreSQL          ✓✓           ✗          ✓✓         ✓✓
MySQL               ✗            ✗          ✓✓         ✗
Wire protocol       PostgreSQL   Proprietary PostgreSQL PostgreSQL

OPERATIONS
Horizontal scale    ✓✓           ✓✓         Limited    ✓✓
Online schema       ✓            ✓          Limited    ✓
Auto-rebalancing    ✓✓           ✓          ✗          ✓

PRICING
Self-hosted cost    $$           N/A        N/A        $$
Managed cost        $$$          $$$$       $$         $$$
Free tier           ✓            ✗          ✗          ✓

BEST FOR:
─────────────────────────────────────────────────────────────────
CockroachDB:  Multi-region, PostgreSQL compatible, self-hosted option
Spanner:      Google Cloud native, extreme scale, cost not a concern
Aurora:       AWS-only, PostgreSQL/MySQL, single-region focus
YugabyteDB:   Open source alternative to CockroachDB, also PostgreSQL
```

---

## Common Mistakes

| Mistake | Why It's Bad | Better Approach |
|---------|--------------|-----------------|
| Single-region deployment | No region failure survival | Deploy across 3+ regions/AZs |
| Not using locality | All traffic goes everywhere | Configure locality for data placement |
| Ignoring hot spots | Single range gets overloaded | Pre-split hot tables, use UUIDs |
| No connection pooling | Connection overhead at scale | Use a connection-pooling layer appropriate for your stack |
| Default isolation | Serializable has overhead | Consider READ COMMITTED for read-heavy |
| No backup strategy | CockroachDB isn't a backup | Configure BACKUP to cloud storage |
| Undersized nodes | CPU/memory bottlenecks | Size nodes from workload measurements and current vendor guidance |
| Missing monitoring | Can't see problems coming | Prometheus + Grafana + alerting |

---

## Hands-On Exercise

### Task: Deploy CockroachDB and Simulate Failures

**Objective**: Deploy a 3-node CockroachDB cluster, load data, and verify it survives node failures.

**Success Criteria**:
1. 3-node cluster running on Kubernetes
2. Database with sample data
3. Survive node failure with zero data loss
4. Measure failover time

### Steps

```bash
# 1. Create a kind cluster with 3 worker nodes
cat > kind-config.yaml << 'EOF'
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
  - role: worker
  - role: worker
EOF

kind create cluster --name crdb-lab --config kind-config.yaml

# 2. Install CockroachDB
kubectl create namespace cockroachdb

# Using a simplified manifest for the lab
cat > cockroachdb-lab.yaml << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: cockroachdb-public
  namespace: cockroachdb
spec:
  ports:
    - port: 26257
      targetPort: 26257
      name: sql
    - port: 8080
      targetPort: 8080
      name: http
  selector:
    app: cockroachdb
---
apiVersion: v1
kind: Service
metadata:
  name: cockroachdb
  namespace: cockroachdb
spec:
  ports:
    - port: 26257
      targetPort: 26257
      name: grpc
    - port: 8080
      targetPort: 8080
      name: http
  clusterIP: None
  selector:
    app: cockroachdb
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: cockroachdb
  namespace: cockroachdb
spec:
  serviceName: cockroachdb
  replicas: 3
  selector:
    matchLabels:
      app: cockroachdb
  template:
    metadata:
      labels:
        app: cockroachdb
    spec:
      containers:
        - name: cockroachdb
          image: cockroachdb/cockroach:v23.2.0
          ports:
            - containerPort: 26257
              name: sql
            - containerPort: 8080
              name: http
          command:
            - "/cockroach/cockroach"
            - "start"
            - "--insecure"
            - "--join=cockroachdb-0.cockroachdb,cockroachdb-1.cockroachdb,cockroachdb-2.cockroachdb"
            - "--advertise-addr=$(POD_NAME).cockroachdb"
            - "--cache=256MiB"
            - "--max-sql-memory=256MiB"
          env:
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
          volumeMounts:
            - name: datadir
              mountPath: /cockroach/cockroach-data
  volumeClaimTemplates:
    - metadata:
        name: datadir
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi
EOF

kubectl apply -f cockroachdb-lab.yaml

# 3. Wait for pods and initialize cluster
kubectl rollout status statefulset/cockroachdb -n cockroachdb --timeout=300s

kubectl exec -n cockroachdb -it cockroachdb-0 -- \
  /cockroach/cockroach init --insecure

# 4. Create database and load sample data
kubectl exec -n cockroachdb -it cockroachdb-0 -- \
  /cockroach/cockroach sql --insecure << 'EOF'
CREATE DATABASE shop;
USE shop;

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name STRING NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    quantity INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Insert sample data
INSERT INTO products (name, price, stock) VALUES
    ('Widget A', 19.99, 1000),
    ('Widget B', 29.99, 500),
    ('Widget C', 39.99, 250);

-- Insert some orders
INSERT INTO orders (product_id, quantity)
SELECT id, (random() * 10)::INT + 1
FROM products, generate_series(1, 100);

SELECT 'Data loaded:', count(*) as order_count FROM orders;
EOF

# 5. Verify cluster health
kubectl exec -n cockroachdb cockroachdb-0 -- \
  /cockroach/cockroach sql --insecure -e \
  "SELECT node_id, is_live, locality FROM crdb_internal.gossip_nodes;"

# 6. Start a continuous workload (in background)
kubectl run workload --rm -i --tty --image=cockroachdb/cockroach:v23.2.0 --restart=Never -- \
  /cockroach/cockroach workload run bank \
  --insecure \
  --duration=5m \
  'postgresql://root@cockroachdb-public.cockroachdb:26257/defaultdb?sslmode=disable' &

# 7. SIMULATE FAILURE: Kill a node
echo "Killing cockroachdb-1..."
kubectl delete pod cockroachdb-1 -n cockroachdb

# 8. Watch the cluster recover
watch kubectl get pods -n cockroachdb

# 9. Verify data integrity
kubectl exec -n cockroachdb cockroachdb-0 -- \
  /cockroach/cockroach sql --insecure -e \
  "SELECT count(*) FROM shop.orders;"

# 10. Check ranges are fully replicated
kubectl exec -n cockroachdb cockroachdb-0 -- \
  /cockroach/cockroach sql --insecure -e \
  "SELECT count(*) as underreplicated FROM crdb_internal.ranges WHERE array_length(replicas, 1) < 3;"
# Should return 0 once cluster recovers
```

### Verification

```bash
# Verify cluster survived
kubectl exec -n cockroachdb cockroachdb-0 -- \
  /cockroach/cockroach node status --insecure

# Check no data was lost
kubectl exec -n cockroachdb cockroachdb-0 -- \
  /cockroach/cockroach sql --insecure -e \
  "SELECT count(*) FROM shop.products; SELECT count(*) FROM shop.orders;"

# Clean up
kind delete cluster --name crdb-lab
```

---

## Quiz

### Question 1
What consensus algorithm does CockroachDB use for data replication?

<details>
<summary>Show Answer</summary>

**Raft**

CockroachDB uses the Raft consensus algorithm for each "range" (chunk of data, typically ~512MB). Each range has its own Raft group with a leader and followers, ensuring data is replicated before a write is acknowledged. This is the same algorithm used by etcd and Kubernetes.
</details>

### Question 2
How does CockroachDB achieve horizontal scalability?

<details>
<summary>Show Answer</summary>

**Automatic range splitting and rebalancing**

When a range grows beyond ~512MB, CockroachDB automatically splits it into two ranges. These ranges are distributed across nodes, with each range having its own Raft leader. This means adding nodes automatically increases capacity as ranges rebalance to new nodes.
</details>

### Question 3
What wire protocol does CockroachDB use?

<details>
<summary>Show Answer</summary>

**PostgreSQL wire protocol**

CockroachDB implements the PostgreSQL wire protocol, meaning most PostgreSQL drivers, ORMs, and tools work with CockroachDB. You can often migrate from PostgreSQL by just changing the connection string (though some PostgreSQL-specific features may differ).
</details>

### Question 4
What does `SURVIVE REGION FAILURE` configure?

<details>
<summary>Show Answer</summary>

**The cluster's survival goal for regional outages**

When set, CockroachDB ensures each range has replicas in at least 3 regions, so the cluster can survive the complete loss of any one region while maintaining data availability. This affects replica placement decisions.

```sql
ALTER DATABASE myapp SURVIVE REGION FAILURE;
```
</details>

### Question 5
What is `REGIONAL BY ROW` used for?

<details>
<summary>Show Answer</summary>

**Pinning row data to specific geographic regions based on a column value**

This allows you to store different rows in different regions based on a column (like `region` or `country`). Useful for GDPR compliance where EU user data must stay in EU datacenters, or for reducing latency by keeping data near users.

```sql
ALTER TABLE users SET LOCALITY REGIONAL BY ROW AS region;
```
</details>

### Question 6
How many replicas does CockroachDB maintain by default?

<details>
<summary>Show Answer</summary>

**3 replicas per range**

By default, each range (chunk of data) is replicated 3 times across different nodes. This allows the cluster to survive the loss of 1 replica while maintaining consensus (2 out of 3 nodes must agree for writes). This can be configured with zone configurations.
</details>

### Question 7
What is the default isolation level in CockroachDB?

<details>
<summary>Show Answer</summary>

**Serializable isolation**

CockroachDB defaults to serializable isolation, the strictest level that guarantees transactions appear to execute one at a time. This prevents all anomalies but may have higher contention. You can use READ COMMITTED for less strict requirements.
</details>

### Question 8
What happens when a CockroachDB node fails?

<details>
<summary>Show Answer</summary>

**Raft automatically elects new leaders for affected ranges**

When a node fails:
1. Raft groups detect the missing node (typically within seconds)
2. If the failed node was a range leader, followers elect a new leader
3. Writes continue to the new leader
4. If replication factor drops below target, new replicas are created on healthy nodes
5. No manual intervention required
</details>

---

## Key Takeaways

1. **Distributed SQL** — [CockroachDB is a true distributed database with automatic sharding and rebalancing](https://github.com/cockroachdb/cockroach)
2. **Survives failures** — Designed for regional outages, not just node failures
3. **PostgreSQL compatible** — Use existing PostgreSQL drivers and tools
4. **Raft consensus** — Each range runs its own Raft group for strong consistency
5. **Multi-region native** — Data locality, regional tables, and survival goals built-in
6. **Serializable by default** — Strongest isolation level prevents all anomalies
7. **Horizontal scale** — Add nodes to add capacity, automatic rebalancing
8. **Operational simplicity** — No external coordination service (like ZooKeeper)
9. **Kubernetes native** — Operators and Helm charts for easy deployment
10. **Enterprise features** — Geo-partitioning, CDC, backup/restore (some require license)

---

## Next Steps

- **Next Module**: [Module 15.2: CloudNativePG](../module-15.2-cloudnativepg/) — PostgreSQL on Kubernetes with operators
- **Related**: [Distributed Systems Foundation](/platform/foundations/distributed-systems/) — Deep dive on consensus
- **Related**: [Observability Toolkit](/platform/toolkits/observability-intelligence/observability/) — Monitoring distributed databases

---

## Further Reading

- [CockroachDB Documentation](https://www.cockroachlabs.com/docs/)
- [CockroachDB Architecture Guide](https://www.cockroachlabs.com/docs/stable/architecture/overview.html)
- [Raft Consensus Algorithm](https://raft.github.io/)
- [CockroachDB on Kubernetes](https://www.cockroachlabs.com/docs/stable/kubernetes-overview.html)
- [Data on Kubernetes Community](https://dok.community/)

---

CockroachDB is designed to handle routine failures automatically when the cluster still has the quorum and topology it needs.

## Sources

- [github.com: raft](https://github.com/etcd-io/raft) — The etcd Raft library README explicitly describes Raft and lists CockroachDB, etcd, and Kubernetes among systems it powers.
- [github.com: cockroach](https://github.com/cockroachdb/cockroach) — The CockroachDB upstream repository README states these high-level capabilities directly.
- [CockroachDB Kubernetes Operator](https://github.com/cockroachdb/cockroach-operator) — Useful for Kubernetes deployment details and operator-managed cluster behavior.
- [In Search of an Understandable Consensus Algorithm](https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro) — Primary reference for Raft, the consensus algorithm discussed in the module.
