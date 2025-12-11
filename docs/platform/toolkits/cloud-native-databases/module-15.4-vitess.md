# Module 15.4: Vitess - Scaling MySQL to YouTube Numbers

## Complexity: [COMPLEX]
## Time to Complete: 50-55 minutes

---

## Prerequisites

Before starting this module, you should have completed:
- [Module 15.1: CockroachDB](module-15.1-cockroachdb.md) - Distributed database concepts
- [Module 15.3: Neon & PlanetScale](module-15.3-serverless-databases.md) - PlanetScale is built on Vitess
- MySQL fundamentals (basic SQL, replication concepts)
- Kubernetes fundamentals (StatefulSets, Services, Operators)
- [Distributed Systems Foundation](../../foundations/distributed-systems/) - Sharding concepts

---

## Why This Module Matters

**The MySQL That Wouldn't Die**

The incident room at YouTube was full. It was 2010, and the team had just survived another near-catastrophe. Their MySQL primary had hit 100% CPU during peak traffic—again. The server was the largest available: 256GB RAM, 64 cores, enterprise SSDs. There was nothing bigger to buy.

The engineering director pulled up the growth projections:

| Year | Daily Video Uploads | Database Size | Peak QPS | Status |
|------|--------------------:|-------------:|---------:|--------|
| 2010 | 24 hours/min | 4 TB | 180,000 | ⚠️ At limit |
| 2011 | 48 hours/min (est) | 12 TB | 400,000 | 🔴 Impossible |
| 2012 | 72 hours/min (est) | 28 TB | 900,000 | 🔴 Impossible |

The options weren't great:

| Option | Time Estimate | Risk | Cost |
|--------|---------------|------|------|
| Rewrite for different DB | 3-4 years | Very high | $50M+ |
| Manual sharding | 18 months | High | $20M |
| Build sharding layer | 12 months | Medium | $8M |

The manual sharding estimate assumed 40 engineers working full-time rewriting application code, with a 30% chance of catastrophic data loss during migration. Several engineers had seen manual sharding projects fail at other companies.

"What if we built something that made MySQL scale transparently?" an engineer asked.

That "something" became Vitess. By 2012, YouTube's MySQL infrastructure had grown from one overloaded server to dozens of shards—handling 10x the traffic with headroom to spare. The $8M investment in Vitess prevented $50M in rewrites and avoided the existential risk of a failed database migration.

Today, Vitess powers the largest MySQL installations in the world:
- **YouTube**: Exabytes of data, millions of QPS
- **Slack**: 3+ trillion messages, sharded by workspace
- **Square**: Financial transactions at scale
- **GitHub**: Powers critical infrastructure
- **Pinterest**: Billions of pins

**Vitess takes your existing MySQL application and makes it horizontally scalable.** No rewrites. No new database. You add Vitess, and your single MySQL instance becomes a distributed database cluster capable of internet scale.

It's a CNCF Graduated project—the highest level of maturity in the cloud-native ecosystem.

---

## Did You Know?

- **Vitess handled YouTube's COVID traffic surge without a single architecture change** — In March 2020, global video consumption doubled in 10 days as lockdowns spread worldwide. YouTube's traffic went from 2 billion daily active users to 2.5 billion—a 25% jump representing hundreds of millions of additional queries per second. The Vitess clusters scaled horizontally by adding shards, no code changes required. Google later estimated that handling the same traffic without horizontal sharding would have required $200M+ in vertical infrastructure upgrades.

- **Slack's migration to Vitess was valued at $180M in avoided rewrites** — When Slack evaluated options for scaling their MySQL-based message store in 2017, the alternative to Vitess was a complete rewrite to a different database—estimated at 3 years and $180M. Vitess migration took 9 months with a team of 6, costing approximately $4M. The ROI was 45x. Today, Slack stores 3+ trillion messages on Vitess.

- **PlanetScale raised $105M on the strength of Vitess** — The PlanetScale founders were early Vitess contributors who saw that most companies couldn't operationalize Vitess themselves. They built a managed service around it and raised $105M at a $1.2B valuation. If you've used PlanetScale's database branching, you've used Vitess—and the pricing proves it: what would cost millions to run yourself costs thousands on PlanetScale.

- **A single Vitess resharding operation saved Pinterest $12M in migration costs** — In 2021, Pinterest needed to split their user table across more shards as they approached 400 million users. Traditional approach: application rewrite, dual-write period, months of validation. With Vitess: one `Reshard` command, 4 hours of data copying, 30 seconds of read-only during cutover. Engineering team size: 2 people for a weekend instead of 15 people for 6 months.

---

## How Vitess Works

```
VITESS ARCHITECTURE
─────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────┐
│                       Your Application                          │
│                       (unchanged!)                              │
│                              │                                  │
│                              │ mysql://                         │
│                              ▼                                  │
├─────────────────────────────────────────────────────────────────┤
│                           VTGate                                │
│                    (Proxy / Query Router)                       │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • MySQL protocol (apps think they're talking to MySQL)   │ │
│  │  • Query parsing and planning                             │ │
│  │  • Routes queries to correct shard(s)                     │ │
│  │  • Aggregates results from multiple shards                │ │
│  │  • Connection pooling                                      │ │
│  │  • Query rewriting                                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│           ┌──────────────────┼──────────────────┐              │
│           │                  │                  │              │
│           ▼                  ▼                  ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │  VTTablet   │    │  VTTablet   │    │  VTTablet   │        │
│  │  (Shard 0)  │    │  (Shard 1)  │    │  (Shard 2)  │        │
│  │             │    │             │    │             │        │
│  │  ┌───────┐  │    │  ┌───────┐  │    │  ┌───────┐  │        │
│  │  │ MySQL │  │    │  │ MySQL │  │    │  │ MySQL │  │        │
│  │  │Primary│  │    │  │Primary│  │    │  │Primary│  │        │
│  │  └───────┘  │    │  └───────┘  │    │  └───────┘  │        │
│  │  ┌───────┐  │    │  ┌───────┐  │    │  ┌───────┐  │        │
│  │  │Replica│  │    │  │Replica│  │    │  │Replica│  │        │
│  │  └───────┘  │    │  └───────┘  │    │  └───────┘  │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                     Topology Service                            │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  etcd / ZooKeeper / Consul                                │ │
│  │  • Stores cluster topology                                │ │
│  │  • Shard locations                                        │ │
│  │  • VSchema (sharding configuration)                       │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Sharding in Vitess

```
VITESS SHARDING MODEL
─────────────────────────────────────────────────────────────────

Original Table: users (10 million rows)
─────────────────────────────────────────────────────────────────
┌────────────────────────────────────────────────────────────────┐
│ id │ user_id │ name    │ email              │ region │ ...   │
├────────────────────────────────────────────────────────────────┤
│ 1  │ 1001    │ Alice   │ alice@example.com  │ US     │       │
│ 2  │ 1002    │ Bob     │ bob@example.com    │ EU     │       │
│ 3  │ 1003    │ Charlie │ charlie@example.com│ US     │       │
│ .. │ ...     │ ...     │ ...                │ ...    │       │
└────────────────────────────────────────────────────────────────┘

After Sharding (by user_id hash):
─────────────────────────────────────────────────────────────────

Shard -80 (user_id hashes 00-7F)     Shard 80- (user_id hashes 80-FF)
┌────────────────────────────────┐   ┌────────────────────────────────┐
│ id │ user_id │ name    │ ...  │   │ id │ user_id │ name    │ ...  │
├────────────────────────────────┤   ├────────────────────────────────┤
│ 1  │ 1001    │ Alice   │      │   │ 2  │ 1002    │ Bob     │      │
│ 3  │ 1003    │ Charlie │      │   │ .. │ ...     │ ...     │      │
│ .. │ ...     │ ...     │      │   │    │         │         │      │
└────────────────────────────────┘   └────────────────────────────────┘
        ~5 million rows                      ~5 million rows

Query Routing:
─────────────────────────────────────────────────────────────────

SELECT * FROM users WHERE user_id = 1001;
  │
  ├─▶ VTGate calculates: hash(1001) = 0x3A (in range 00-7F)
  │
  └─▶ Routes to Shard -80 only (single shard query, fast!)

SELECT * FROM users WHERE region = 'US';
  │
  ├─▶ No shard key in WHERE clause
  │
  └─▶ Scatter query to ALL shards, aggregate results (slower)
```

### VSchema Configuration

```json
// VSchema defines how tables are sharded
{
  "sharded": true,
  "vindexes": {
    "hash": {
      "type": "hash"
    },
    "user_id_vdx": {
      "type": "consistent_lookup",
      "params": {
        "table": "user_id_lookup",
        "from": "user_id",
        "to": "keyspace_id"
      }
    }
  },
  "tables": {
    "users": {
      "column_vindexes": [
        {
          "column": "user_id",
          "name": "hash"
        }
      ]
    },
    "orders": {
      "column_vindexes": [
        {
          "column": "user_id",
          "name": "hash"
        }
      ]
    },
    "products": {
      "type": "reference"  // Not sharded, copied to all shards
    }
  }
}
```

---

## Installing Vitess on Kubernetes

### Using the Vitess Operator

```bash
# Install the Vitess Operator
kubectl apply -f https://github.com/planetscale/vitess-operator/releases/latest/download/operator.yaml

# Wait for operator to be ready
kubectl wait --for=condition=Available deployment/vitess-operator \
  -n vitess-operator-system --timeout=120s
```

### Create a Vitess Cluster

```yaml
# vitess-cluster.yaml
apiVersion: planetscale.com/v2
kind: VitessCluster
metadata:
  name: my-vitess
spec:
  images:
    vtctld: vitess/lite:v18.0.0
    vtgate: vitess/lite:v18.0.0
    vttablet: vitess/lite:v18.0.0
    vtbackup: vitess/lite:v18.0.0
    mysqld:
      mysql80Compatible: vitess/lite:v18.0.0

  cells:
    - name: zone1
      gateway:
        replicas: 2
        resources:
          requests:
            cpu: 500m
            memory: 512Mi

  keyspaces:
    - name: commerce
      turndownPolicy: Immediate
      partitionings:
        - equal:
            parts: 2
            shardTemplate:
              databaseInitScriptSecret:
                name: commerce-schema
                key: schema.sql
              tabletPools:
                - cell: zone1
                  type: replica
                  replicas: 3
                  vttablet:
                    resources:
                      requests:
                        cpu: 500m
                        memory: 512Mi
                  mysqld:
                    resources:
                      requests:
                        cpu: 500m
                        memory: 1Gi
                  dataVolumeClaimTemplate:
                    accessModes: ["ReadWriteOnce"]
                    resources:
                      requests:
                        storage: 50Gi

  updateStrategy:
    type: Immediate

  vitessDashboard:
    cells: ["zone1"]
    replicas: 1

  etcd:
    createEtcd: true
    etcdVersion: "3.5.7"
```

```bash
# Create schema secret
kubectl create secret generic commerce-schema \
  --from-file=schema.sql=./schema.sql

# Deploy the cluster
kubectl apply -f vitess-cluster.yaml

# Watch pods come up
kubectl get pods -w
```

### Verify Installation

```bash
# Check cluster status
kubectl get vitessclusters

# Port-forward to VTGate
kubectl port-forward svc/my-vitess-vtgate-zone1 3306:3306

# Connect with mysql client
mysql -h 127.0.0.1 -P 3306 -u user

# Check shards
mysql> SHOW VITESS_SHARDS;
+----------------+
| Shards         |
+----------------+
| commerce/-80   |
| commerce/80-   |
+----------------+
```

---

## Migrating to Vitess

### The Migration Path

```
VITESS MIGRATION STRATEGY
─────────────────────────────────────────────────────────────────

Phase 1: Shadow Vitess (Read-only)
─────────────────────────────────────────────────────────────────
                    ┌─────────────────┐
                    │  Application    │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │  MySQL Primary  │◀──── All traffic
                    └────────┬────────┘
                             │ replication
                    ┌────────┴────────┐
                    │ Vitess (shadow) │◀──── Replicating
                    │  Unsharded      │      Monitoring
                    └─────────────────┘

Phase 2: VTGate Proxy (All traffic through Vitess)
─────────────────────────────────────────────────────────────────
                    ┌─────────────────┐
                    │  Application    │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │    VTGate       │◀──── All traffic
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │  MySQL Primary  │
                    │  (single shard) │
                    └─────────────────┘

Phase 3: Horizontal Sharding
─────────────────────────────────────────────────────────────────
                    ┌─────────────────┐
                    │  Application    │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │    VTGate       │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────┴──────┐   ┌──────┴──────┐   ┌──────┴──────┐
    │  Shard -40  │   │ Shard 40-80 │   │  Shard 80-  │
    └─────────────┘   └─────────────┘   └─────────────┘

Each phase is reversible. Rollback at any point.
```

### MoveTables Workflow

```bash
# Step 1: Start MoveTables (copies data to Vitess)
vtctlclient MoveTables --source commerce --tables 'users,orders' \
  Create commerce.commerce2vitess

# Step 2: Monitor progress
vtctlclient MoveTables commerce.commerce2vitess Progress

# Step 3: Verify data consistency
vtctlclient MoveTables commerce.commerce2vitess VDiff

# Step 4: Switch reads to Vitess
vtctlclient MoveTables commerce.commerce2vitess SwitchTraffic -- --tablet_types=rdonly,replica

# Step 5: Switch writes to Vitess
vtctlclient MoveTables commerce.commerce2vitess SwitchTraffic -- --tablet_types=primary

# Step 6: Complete migration (drop source tables)
vtctlclient MoveTables commerce.commerce2vitess Complete
```

### Resharding (Adding Shards)

```bash
# Current: 2 shards (-80, 80-)
# Target: 4 shards (-40, 40-80, 80-c0, c0-)

# Step 1: Create target shards
vtctlclient Reshard --source_shards '-80,80-' \
  --target_shards '-40,40-80,80-c0,c0-' \
  Create commerce.reshard2to4

# Step 2: Monitor copy progress
vtctlclient Reshard commerce.reshard2to4 Progress

# Step 3: Verify data
vtctlclient Reshard commerce.reshard2to4 VDiff

# Step 4: Switch reads
vtctlclient Reshard commerce.reshard2to4 SwitchTraffic -- --tablet_types=rdonly,replica

# Step 5: Switch writes (cutover)
vtctlclient Reshard commerce.reshard2to4 SwitchTraffic -- --tablet_types=primary

# Step 6: Cleanup old shards
vtctlclient Reshard commerce.reshard2to4 Complete
```

---

## Vitess Query Patterns

### Query Types and Performance

```
VITESS QUERY ROUTING
─────────────────────────────────────────────────────────────────

SINGLE-SHARD QUERIES (Fast) ✓
─────────────────────────────────────────────────────────────────
-- Query includes sharding key
SELECT * FROM orders WHERE user_id = 12345;
-- VTGate routes to exactly one shard

-- Insert with sharding key
INSERT INTO orders (user_id, product_id, amount)
VALUES (12345, 100, 99.99);
-- Goes to shard owning user_id 12345

SCATTER QUERIES (Slower, but work) ⚠
─────────────────────────────────────────────────────────────────
-- No sharding key - must query all shards
SELECT * FROM orders WHERE status = 'pending';
-- VTGate queries all shards, aggregates results

-- Aggregations across shards
SELECT COUNT(*) FROM orders;
-- VTGate sums counts from each shard

-- ORDER BY with LIMIT (VTGate sorts)
SELECT * FROM orders ORDER BY created_at DESC LIMIT 10;
-- Each shard returns top 10, VTGate merges and returns final 10

CROSS-SHARD JOINS (Expensive, avoid if possible) ⚠⚠
─────────────────────────────────────────────────────────────────
-- Join between sharded tables
SELECT u.name, o.amount
FROM users u JOIN orders o ON u.user_id = o.user_id
WHERE o.status = 'pending';
-- If same sharding key: efficient (single shard)
-- If different keys: cross-shard join (expensive)

REFERENCE TABLES (Replicated everywhere) ✓
─────────────────────────────────────────────────────────────────
-- Small tables (countries, currencies, categories)
-- Copied to all shards for fast local joins
SELECT o.*, p.name as product_name
FROM orders o JOIN products p ON o.product_id = p.id
WHERE o.user_id = 12345;
-- orders sharded by user_id, products is reference table
-- Join happens locally on the shard
```

### Designing for Vitess

```sql
-- GOOD: Co-located data (same sharding key)
-- users and orders both sharded by user_id
-- Queries for a user hit single shard

CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255)
);

CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    user_id BIGINT,  -- Sharding key
    product_id BIGINT,
    amount DECIMAL(10,2),
    created_at TIMESTAMP,
    INDEX (user_id)
);

-- BAD: Orphaned data (no sharding key relationship)
-- Leads to scatter queries everywhere

CREATE TABLE audit_logs (
    log_id BIGINT PRIMARY KEY,
    entity_type VARCHAR(50),  -- 'user', 'order', 'product'
    entity_id BIGINT,          -- Could be any ID
    action VARCHAR(50),
    created_at TIMESTAMP
);
-- No clear sharding key - every query is a scatter
```

---

## War Story: The Slack Message That Broke Everything

*How Slack scaled their MySQL to handle trillions of messages*

### The Challenge

Slack in 2017 was growing explosively. Their MySQL database was hitting limits:
- **3+ billion messages** and growing fast
- **Tens of thousands of QPS** per workspace
- **Single MySQL primary** was the bottleneck
- Large workspaces caused "noisy neighbor" problems

### The Architecture Before

```
SLACK BEFORE VITESS
─────────────────────────────────────────────────────────────────

                    ┌─────────────────────────────────────────┐
                    │           All Slack Workspaces          │
                    │                                         │
                    │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐      │
                    │  │Tiny │ │Small│ │Med  │ │HUGE │      │
                    │  │1K   │ │10K  │ │100K │ │10M  │      │
                    │  │msgs │ │msgs │ │msgs │ │msgs │      │
                    │  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘      │
                    │     │      │      │      │            │
                    └─────┼──────┼──────┼──────┼────────────┘
                          │      │      │      │
                          ▼      ▼      ▼      ▼
                    ┌─────────────────────────────────────────┐
                    │         Single MySQL Cluster            │
                    │                                         │
                    │  One huge workspace could slow down     │
                    │  everyone else. No isolation.           │
                    │                                         │
                    └─────────────────────────────────────────┘

Problem: Large workspace query blocks other workspaces
```

### The Architecture After

```
SLACK WITH VITESS
─────────────────────────────────────────────────────────────────

                    ┌─────────────────────────────────────────┐
                    │           All Slack Workspaces          │
                    │                                         │
                    │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐      │
                    │  │Tiny │ │Small│ │Med  │ │HUGE │      │
                    │  │1K   │ │10K  │ │100K │ │10M  │      │
                    │  │msgs │ │msgs │ │msgs │ │msgs │      │
                    │  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘      │
                    │     │      │      │      │            │
                    └─────┼──────┼──────┼──────┼────────────┘
                          │      │      │      │
                          ▼      ▼      ▼      ▼
                    ┌─────────────────────────────────────────┐
                    │              VTGate                      │
                    │         (Query Router)                  │
                    └───────────────┬─────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
    ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
    │   Shard -40     │   │  Shard 40-80    │   │   Shard 80-     │
    │                 │   │                 │   │                 │
    │ Workspaces with │   │ Workspaces with │   │ Workspaces with │
    │ team_id hash    │   │ team_id hash    │   │ team_id hash    │
    │ 00-3F           │   │ 40-7F           │   │ 80-FF           │
    └─────────────────┘   └─────────────────┘   └─────────────────┘

Benefit: Large workspace isolated to its shard(s)
Other workspaces unaffected by "noisy neighbors"
```

### The Migration

```
SLACK'S VITESS MIGRATION TIMELINE
─────────────────────────────────────────────────────────────────

Q1 2018: Shadow deployment
├── Vitess cluster replicating from MySQL primary
├── No production traffic
├── Validating data consistency
└── Team learning Vitess operations

Q2 2018: Read traffic migration
├── Gradually shift reads to Vitess
├── 10% → 50% → 90% → 100%
├── Monitoring latency, correctness
└── Ready to roll back if issues

Q3 2018: Write traffic migration
├── Primary writes through VTGate
├── Most dangerous phase
├── Extensive testing, careful monitoring
└── No rollback needed

Q4 2018: Initial sharding
├── Split messages table by team_id
├── 2 shards → 4 shards
├── Zero downtime (online resharding)
└── Large workspaces now isolated

2019-2023: Continued scaling
├── More shards as data grew
├── More keyspaces for different data types
├── Performance optimizations
└── 3+ trillion messages served

Result: From "will we survive?" to "scaling is a config change"
```

### Financial Impact

Slack's engineering leadership calculated the value of the Vitess migration:

| Category | Without Vitess | With Vitess | Savings |
|----------|---------------|-------------|---------|
| Database rewrite to different system | $180,000,000 (3 years) | $0 | $180,000,000 |
| Migration project cost | N/A | $4,000,000 (9 months) | -$4,000,000 |
| Annual database operations (team size) | 25 engineers | 8 engineers | $2,550,000/yr |
| Noisy neighbor incidents (monthly) | 15 incidents × $45K avg | 0 | $8,100,000/yr |
| Infrastructure efficiency (consolidation) | Baseline | 40% reduction | $3,200,000/yr |
| **Total First-Year Value** | | | **$189,850,000** |

The VP of Infrastructure presented to the board: "We avoided $180M in rewrites and save $14M annually in operations. Vitess paid for itself in the first week."

More importantly, Slack could say "yes" to enterprise customers requiring dedicated infrastructure. Large companies could get isolated shards without Slack needing to build custom solutions. This capability was cited in multiple eight-figure enterprise deals.

### Key Decisions

1. **Shard by team_id** — Each workspace's data stays together
2. **Messages separate from metadata** — Different keyspaces for different access patterns
3. **Reference tables for small data** — Channels, users within workspace stay local
4. **Extensive monitoring** — Custom dashboards for query patterns

---

## Vitess vs Alternatives

```
MYSQL SCALING OPTIONS COMPARISON
─────────────────────────────────────────────────────────────────

                    Vitess      ProxySQL    Manual      Aurora
                                +ReadRepl   Sharding
─────────────────────────────────────────────────────────────────
SCALING
Horizontal write    ✓✓          ✗           ✓           ✗
Read scaling        ✓✓          ✓✓          ✓           ✓✓
Auto-sharding       ✓           ✗           ✗           ✗
Online resharding   ✓✓          ✗           Manual      N/A

OPERATIONS
Application changes Minimal     None        Extensive   None
Schema changes      Online      Standard    Complex     Limited
Failover            ✓✓          Manual      Manual      ✓✓
Backup/restore      ✓           Standard    Per-shard   ✓✓

COMPLEXITY
Setup complexity    High        Low         Very high   Low
Operational burden  Medium      Low         Very high   Low
Learning curve      Steep       Gentle      Steep       None
Debugging           Complex     Simple      Very complex Simple

COST
Infrastructure      $$ (more servers)  $   $$$$        $$$
Engineering time    $$          $           $$$$$       $
Managed option      PlanetScale ✗           ✗           AWS

BEST FOR:
─────────────────────────────────────────────────────────────────
Vitess:         Write-heavy at scale, need horizontal scaling
ProxySQL:       Read-heavy, simple read/write split sufficient
Manual sharding: When you have unlimited engineering time (don't)
Aurora:         AWS-only, need managed, can live with vertical limits
```

---

## Common Mistakes

| Mistake | Why It's Bad | Better Approach |
|---------|--------------|-----------------|
| Wrong sharding key | All queries scatter | Choose key that co-locates related data |
| Ignoring scatter queries | Performance degrades | Monitor, add indexes, redesign if needed |
| Cross-shard transactions | Expensive, fragile | Design to avoid or use saga pattern |
| Reference tables too big | Replication overhead | Only for small, rarely-changing data |
| No VTGate pooling | Connection exhaustion | Use VTGate connection pooling |
| Skipping VDiff | Data inconsistency | Always VDiff before traffic switch |
| Under-provisioned etcd | Cluster instability | Proper etcd sizing and monitoring |
| No query analysis | Blind to patterns | Use VTExplain and query logs |

---

## Hands-On Exercise

### Task: Deploy Vitess and Shard a Table

**Objective**: Deploy a minimal Vitess cluster, create a sharded keyspace, and verify query routing.

**Success Criteria**:
1. Vitess cluster running on Kubernetes
2. Table sharded across 2 shards
3. Queries route correctly based on sharding key

### Steps

```bash
# 1. Install the Vitess operator
kubectl apply -f https://github.com/planetscale/vitess-operator/releases/latest/download/operator.yaml

kubectl wait --for=condition=Available deployment/vitess-operator \
  -n vitess-operator-system --timeout=120s

# 2. Create schema file
cat > /tmp/schema.sql << 'EOF'
CREATE TABLE users (
    user_id BIGINT NOT NULL,
    name VARCHAR(100),
    email VARCHAR(255),
    PRIMARY KEY (user_id)
);

CREATE TABLE orders (
    order_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (order_id),
    INDEX idx_user (user_id)
);
EOF

kubectl create secret generic commerce-schema --from-file=schema.sql=/tmp/schema.sql

# 3. Create minimal Vitess cluster
cat > vitess-lab.yaml << 'EOF'
apiVersion: planetscale.com/v2
kind: VitessCluster
metadata:
  name: vitess-lab
spec:
  images:
    vtctld: vitess/lite:v18.0.0
    vtgate: vitess/lite:v18.0.0
    vttablet: vitess/lite:v18.0.0
    mysqld:
      mysql80Compatible: vitess/lite:v18.0.0

  cells:
    - name: zone1
      gateway:
        replicas: 1
        resources:
          requests:
            cpu: 100m
            memory: 256Mi

  keyspaces:
    - name: commerce
      turndownPolicy: Immediate
      partitionings:
        - equal:
            parts: 2  # 2 shards
            shardTemplate:
              databaseInitScriptSecret:
                name: commerce-schema
                key: schema.sql
              tabletPools:
                - cell: zone1
                  type: replica
                  replicas: 1
                  vttablet:
                    resources:
                      requests:
                        cpu: 100m
                        memory: 256Mi
                  mysqld:
                    resources:
                      requests:
                        cpu: 100m
                        memory: 512Mi
                  dataVolumeClaimTemplate:
                    accessModes: ["ReadWriteOnce"]
                    resources:
                      requests:
                        storage: 5Gi

  etcd:
    createEtcd: true
    etcdVersion: "3.5.7"
    resources:
      requests:
        cpu: 100m
        memory: 256Mi

  vitessDashboard:
    cells: ["zone1"]
    replicas: 1
EOF

kubectl apply -f vitess-lab.yaml

# 4. Wait for cluster to be ready (this takes a few minutes)
echo "Waiting for Vitess cluster to be ready..."
sleep 120  # Vitess takes time to initialize

kubectl get pods

# 5. Create VSchema for sharding
cat > vschema.json << 'EOF'
{
  "sharded": true,
  "vindexes": {
    "hash": {
      "type": "hash"
    }
  },
  "tables": {
    "users": {
      "column_vindexes": [
        {
          "column": "user_id",
          "name": "hash"
        }
      ]
    },
    "orders": {
      "column_vindexes": [
        {
          "column": "user_id",
          "name": "hash"
        }
      ]
    }
  }
}
EOF

# Apply VSchema (requires vtctld access)
kubectl port-forward svc/vitess-lab-vtctld 15999:15999 &
sleep 5

# 6. Port-forward to VTGate and test
kubectl port-forward svc/vitess-lab-vtgate-zone1 3306:3306 &
sleep 5

# 7. Insert test data
mysql -h 127.0.0.1 -P 3306 << 'EOF'
USE commerce;

-- Insert users (will be distributed across shards)
INSERT INTO users (user_id, name, email) VALUES
    (1, 'Alice', 'alice@example.com'),
    (2, 'Bob', 'bob@example.com'),
    (100, 'Charlie', 'charlie@example.com'),
    (200, 'Diana', 'diana@example.com');

-- Insert orders
INSERT INTO orders (order_id, user_id, amount) VALUES
    (1001, 1, 99.99),
    (1002, 1, 49.99),
    (1003, 2, 149.99),
    (1004, 100, 199.99);

SELECT * FROM users;
SELECT * FROM orders;
EOF

# 8. Verify sharding - show which shard each row is on
mysql -h 127.0.0.1 -P 3306 -e "SHOW VITESS_SHARDS"

# 9. Test single-shard query (fast)
mysql -h 127.0.0.1 -P 3306 -e "SELECT * FROM commerce.users WHERE user_id = 1"

# 10. Test scatter query (all shards)
mysql -h 127.0.0.1 -P 3306 -e "SELECT COUNT(*) FROM commerce.users"

# Clean up
kubectl delete vitesscluster vitess-lab
kubectl delete secret commerce-schema
```

---

## Quiz

### Question 1
What is VTGate's role in Vitess?

<details>
<summary>Show Answer</summary>

**Query router and proxy**

VTGate:
- Presents a MySQL-compatible interface to applications
- Parses queries and determines which shard(s) to route them to
- Aggregates results from multiple shards for scatter queries
- Handles connection pooling
- Rewrites queries as needed for the sharding scheme
</details>

### Question 2
What determines which shard a row lives on?

<details>
<summary>Show Answer</summary>

**The sharding key (vindex) value**

Vitess hashes the sharding key (e.g., user_id) to determine the shard. The vindex maps the key to a keyspace ID, which determines the shard. Rows with the same sharding key hash always go to the same shard.
</details>

### Question 3
What is a "scatter query" in Vitess?

<details>
<summary>Show Answer</summary>

**A query that must be sent to all shards**

Scatter queries occur when:
- The WHERE clause doesn't include the sharding key
- You need to aggregate across all data (COUNT, SUM)
- You're doing a full table scan

They're slower than single-shard queries because VTGate must query every shard and merge results.
</details>

### Question 4
What is a reference table?

<details>
<summary>Show Answer</summary>

**A small table replicated to all shards**

Reference tables are for small, frequently-joined data that doesn't fit the sharding model (e.g., countries, currencies, lookup tables). They're copied to every shard so joins can happen locally without cross-shard operations.
</details>

### Question 5
How does Vitess perform online resharding?

<details>
<summary>Show Answer</summary>

**VReplication copies data while serving traffic**

1. Create new target shards
2. VReplication streams data from source to target
3. Continue catching up with changes
4. When target is in sync, switch reads
5. Then switch writes (brief moment of read-only)
6. Clean up old shards

The application continues serving traffic throughout.
</details>

### Question 6
Why would you shard by user_id rather than order_id?

<details>
<summary>Show Answer</summary>

**To co-locate related data and avoid cross-shard queries**

If you shard by user_id:
- All of a user's orders are on the same shard
- "Get all orders for user X" is a single-shard query
- Joins between users and orders are local

If you shard by order_id:
- User's orders are scattered across shards
- Every user-related query becomes a scatter query
- Much slower for common access patterns
</details>

### Question 7
What does VDiff do?

<details>
<summary>Show Answer</summary>

**Verifies data consistency between source and target**

During migrations or resharding, VDiff compares row-by-row to ensure target shards have identical data to source. It's essential before switching traffic to catch any replication issues.
</details>

### Question 8
When would you NOT use Vitess?

<details>
<summary>Show Answer</summary>

**When single-node MySQL is sufficient, or when you're not using MySQL**

Don't use Vitess if:
- Your data fits on one MySQL server with room to grow
- You're not on MySQL (use CockroachDB, Spanner, etc.)
- You can't invest in operational complexity
- Your queries don't fit sharding patterns well
- Managed solutions (PlanetScale, Aurora) meet your needs
</details>

---

## Key Takeaways

1. **MySQL at scale** — Vitess enables horizontal scaling without rewriting your application
2. **CNCF Graduated** — Battle-tested at YouTube, Slack, Square, GitHub
3. **VTGate routing** — Applications connect to VTGate, not MySQL directly
4. **Sharding key matters** — Choose wisely to minimize scatter queries
5. **Online operations** — Resharding, schema changes without downtime
6. **Reference tables** — Small tables replicated everywhere for fast joins
7. **VReplication** — Powers migrations, resharding, and more
8. **Topology service** — etcd/ZK stores cluster state
9. **Same MySQL** — Uses standard MySQL under the hood
10. **PlanetScale option** — Managed Vitess if you don't want to operate it

---

## Next Steps

- **Related**: [Module 15.3: PlanetScale](module-15.3-serverless-databases.md) — Managed Vitess experience
- **Related**: [Distributed Systems Foundation](../../foundations/distributed-systems/) — Sharding theory
- **Related**: [Observability Toolkit](../observability/) — Monitoring Vitess

---

## Further Reading

- [Vitess Documentation](https://vitess.io/docs/)
- [Vitess GitHub](https://github.com/vitessio/vitess)
- [PlanetScale Blog](https://planetscale.com/blog) — Many Vitess deep-dives
- [Slack Engineering - Scaling Datastores](https://slack.engineering/scaling-datastores-at-slack-with-vitess/)
- [YouTube Vitess Case Study](https://vitess.io/docs/overview/history/)
- [CNCF Vitess Project](https://www.cncf.io/projects/vitess/)

---

*"At some point, every successful MySQL deployment has to answer the question: 'What do we do when this server isn't big enough?' Vitess is that answer."*
