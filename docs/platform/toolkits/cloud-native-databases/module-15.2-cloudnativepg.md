# Module 15.2: CloudNativePG - PostgreSQL Done Right on Kubernetes

## Complexity: [MEDIUM]
## Time to Complete: 45-50 minutes

---

## Prerequisites

Before starting this module, you should have completed:
- [Module 15.1: CockroachDB](module-15.1-cockroachdb.md) - Distributed database concepts
- PostgreSQL fundamentals (basic SQL, replication concepts)
- Kubernetes fundamentals (StatefulSets, PVCs, Operators)
- [Reliability Engineering Foundation](../../foundations/reliability-engineering/) - HA concepts

---

## Why This Module Matters

**The Database That Runs Itself**

The platform engineer stared at her terminal at 2:47 AM. PostgreSQL primary had crashed. In the old days, this would have meant:
1. SSH into the standby server
2. Manually promote it to primary
3. Update DNS or connection strings
4. Verify replication is working
5. Figure out what happened to the old primary
6. Spend the next day doing a post-mortem

Instead, she watched the CloudNativePG operator:
1. Detect the primary failure (3 seconds)
2. Promote the healthiest replica (2 seconds)
3. Update the Kubernetes Service endpoints (instant)
4. Begin rebuilding a new replica (automatic)
5. Send a Slack notification (configured)

Total downtime: 5 seconds. She went back to sleep.

**CloudNativePG is the PostgreSQL operator that actually works.** It's a CNCF Sandbox project that handles the hard parts of running PostgreSQL on Kubernetes: automated failover, continuous backups, point-in-time recovery, and declarative configuration. You describe what you want; the operator makes it happen.

Unlike generic database operators that try to support everything, CloudNativePG focuses exclusively on PostgreSQL, and it shows in the quality.

---

## Did You Know?

- **CloudNativePG was created by the team behind 2ndQuadrant** — The founders built some of the most critical PostgreSQL replication and backup tools (pglogical, Barman, pg_basebackup improvements). They know PostgreSQL internals deeply.

- **It's the only PostgreSQL operator in the CNCF** — While many PostgreSQL operators exist (Zalando, CrunchyData, KubeDB), CloudNativePG was the first accepted into the CNCF Sandbox, signaling community trust.

- **Failover uses Kubernetes primitives, not external tools** — No HAProxy, no Patroni, no etcd dependency. CloudNativePG uses Kubernetes leader election and Service endpoints for routing. Simpler architecture, fewer failure modes.

- **Continuous backup to object storage is built-in** — WAL archiving to S3/GCS/Azure happens automatically. Point-in-time recovery to any second in your retention window requires one command.

- **The operator watches PostgreSQL process health, not just pod health** — Kubernetes liveness probes check if a pod is running. CloudNativePG checks if PostgreSQL is actually accepting connections and replicating correctly. It catches failures Kubernetes would miss.

- **It supports PostgreSQL's native streaming replication** — Not some custom replication layer. Standard PostgreSQL replication means you can use standard PostgreSQL tools for troubleshooting.

---

## CloudNativePG Architecture

```
CLOUDNATIVEPG ARCHITECTURE
─────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CloudNativePG Operator (Deployment)                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • Watches Cluster CRDs                                   │  │
│  │  • Manages PostgreSQL lifecycle                           │  │
│  │  • Handles failover and promotion                         │  │
│  │  • Coordinates backups                                    │  │
│  │  • Updates Service endpoints                              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            │                                     │
│                            │ manages                             │
│                            ▼                                     │
│  PostgreSQL Cluster (Pods)                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                                                            │  │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │  │
│  │   │   Pod 1     │  │   Pod 2     │  │   Pod 3     │       │  │
│  │   │  PRIMARY    │  │  REPLICA    │  │  REPLICA    │       │  │
│  │   │             │  │             │  │             │       │  │
│  │   │ PostgreSQL  │──│ PostgreSQL  │  │ PostgreSQL  │       │  │
│  │   │  + Barman   │  │             │──│             │       │  │
│  │   │  (backups)  │  │             │  │             │       │  │
│  │   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │  │
│  │          │                │                │              │  │
│  │   ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐       │  │
│  │   │    PVC      │  │    PVC      │  │    PVC      │       │  │
│  │   │  (data)     │  │  (data)     │  │  (data)     │       │  │
│  │   └─────────────┘  └─────────────┘  └─────────────┘       │  │
│  │                                                            │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Services                                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  cluster-name-rw  ──▶ Primary (read-write)                │  │
│  │  cluster-name-ro  ──▶ Replicas (read-only, load balanced) │  │
│  │  cluster-name-r   ──▶ Any node (reads, including primary) │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Backup Storage                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  S3/GCS/Azure Blob                                        │  │
│  │  • Base backups (full snapshots)                          │  │
│  │  • WAL archives (continuous)                              │  │
│  │  • Enables point-in-time recovery                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Failover Process

```
AUTOMATED FAILOVER SEQUENCE
─────────────────────────────────────────────────────────────────

BEFORE: Normal operation
─────────────────────────────────────────────────────────────────
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Pod 1     │    │   Pod 2     │    │   Pod 3     │
│  PRIMARY    │───▶│  REPLICA    │    │  REPLICA    │
│  (writes)   │    │  (sync)     │───▶│  (async)    │
└─────────────┘    └─────────────┘    └─────────────┘
      │
      │ cluster-rw Service points here
      ▼
  Applications

DURING: Primary fails (T=0)
─────────────────────────────────────────────────────────────────
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Pod 1     │    │   Pod 2     │    │   Pod 3     │
│    DEAD     │ X  │  REPLICA    │    │  REPLICA    │
│             │    │  (standby)  │    │  (standby)  │
└─────────────┘    └─────────────┘    └─────────────┘

Operator detects failure (T+3s):
• PostgreSQL not responding
• Pod health check fails
• Streaming replication broken

AFTER: Failover complete (T+5s)
─────────────────────────────────────────────────────────────────
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Pod 1     │    │   Pod 2     │    │   Pod 3     │
│  REBUILDING │◀───│  PRIMARY    │───▶│  REPLICA    │
│  (new repl) │    │  (promoted) │    │  (sync)     │
└─────────────┘    └─────────────┘    └─────────────┘
                         │
                         │ cluster-rw Service updated
                         ▼
                    Applications

Total downtime: ~5 seconds
No manual intervention required
No DNS changes needed
```

---

## Installing CloudNativePG

### Install the Operator

```bash
# Using kubectl (recommended for production)
kubectl apply --server-side -f \
  https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.22/releases/cnpg-1.22.0.yaml

# Or using Helm
helm repo add cnpg https://cloudnative-pg.github.io/charts
helm upgrade --install cnpg \
  cnpg/cloudnative-pg \
  --namespace cnpg-system \
  --create-namespace

# Verify operator is running
kubectl get pods -n cnpg-system
# NAME                                       READY   STATUS
# cnpg-cloudnative-pg-xxxxxxxxx-xxxxx       1/1     Running
```

### Create a PostgreSQL Cluster

```yaml
# postgres-cluster.yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: my-postgres
  namespace: default
spec:
  instances: 3

  # PostgreSQL version
  imageName: ghcr.io/cloudnative-pg/postgresql:16.1

  # Storage configuration
  storage:
    size: 50Gi
    storageClass: premium-ssd

  # PostgreSQL configuration
  postgresql:
    parameters:
      max_connections: "200"
      shared_buffers: "256MB"
      effective_cache_size: "768MB"
      maintenance_work_mem: "128MB"
      checkpoint_completion_target: "0.9"
      wal_buffers: "16MB"
      default_statistics_target: "100"
      random_page_cost: "1.1"
      effective_io_concurrency: "200"
      work_mem: "6553kB"
      min_wal_size: "1GB"
      max_wal_size: "4GB"
      max_worker_processes: "4"
      max_parallel_workers_per_gather: "2"
      max_parallel_workers: "4"

  # Bootstrap from scratch (new cluster)
  bootstrap:
    initdb:
      database: app
      owner: app_user
      secret:
        name: app-user-secret

  # Backup configuration
  backup:
    barmanObjectStore:
      destinationPath: s3://my-backups/postgres/
      s3Credentials:
        accessKeyId:
          name: backup-creds
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: backup-creds
          key: SECRET_ACCESS_KEY
      wal:
        compression: gzip
        maxParallel: 2
    retentionPolicy: "30d"

  # Resource limits
  resources:
    requests:
      cpu: "1"
      memory: "2Gi"
    limits:
      cpu: "2"
      memory: "4Gi"

  # Affinity for HA across zones
  affinity:
    topologyKey: topology.kubernetes.io/zone

  # Enable monitoring
  monitoring:
    enablePodMonitor: true
```

```bash
# Create the secret for app user
kubectl create secret generic app-user-secret \
  --from-literal=username=app_user \
  --from-literal=password=supersecurepassword

# Create backup credentials secret
kubectl create secret generic backup-creds \
  --from-literal=ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE \
  --from-literal=SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Deploy the cluster
kubectl apply -f postgres-cluster.yaml

# Watch the cluster come up
kubectl get pods -w
# NAME            READY   STATUS    RESTARTS   AGE
# my-postgres-1   1/1     Running   0          2m
# my-postgres-2   1/1     Running   0          1m
# my-postgres-3   1/1     Running   0          30s
```

### Verify Cluster Status

```bash
# Check cluster status
kubectl get cluster my-postgres

# NAME          INSTANCES   READY   STATUS                     AGE
# my-postgres   3           3       Cluster in healthy state   5m

# Detailed status
kubectl describe cluster my-postgres

# Get connection string
kubectl get secret my-postgres-app -o jsonpath='{.data.uri}' | base64 -d
# postgresql://app_user:supersecurepassword@my-postgres-rw:5432/app

# Connect to the database
kubectl exec -it my-postgres-1 -- psql -U app_user -d app
```

---

## Day-2 Operations

### Scaling the Cluster

```yaml
# Scale up to 5 replicas
kubectl patch cluster my-postgres --type merge -p '{"spec":{"instances":5}}'

# Scale down (operator handles graceful removal)
kubectl patch cluster my-postgres --type merge -p '{"spec":{"instances":3}}'
```

### Performing Backups

```yaml
# Trigger an on-demand backup
apiVersion: postgresql.cnpg.io/v1
kind: Backup
metadata:
  name: my-postgres-backup-manual
spec:
  cluster:
    name: my-postgres
```

```bash
# Create the backup
kubectl apply -f backup.yaml

# Check backup status
kubectl get backup my-postgres-backup-manual
# NAME                        AGE   CLUSTER       PHASE
# my-postgres-backup-manual   2m    my-postgres   completed

# List all backups
kubectl get backup

# Scheduled backups
apiVersion: postgresql.cnpg.io/v1
kind: ScheduledBackup
metadata:
  name: my-postgres-daily
spec:
  schedule: "0 2 * * *"  # 2 AM daily
  backupOwnerReference: self
  cluster:
    name: my-postgres
```

### Point-in-Time Recovery

```yaml
# Restore to a specific point in time
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: my-postgres-restored
spec:
  instances: 3

  storage:
    size: 50Gi
    storageClass: premium-ssd

  bootstrap:
    recovery:
      source: my-postgres
      recoveryTarget:
        # Restore to this exact timestamp
        targetTime: "2024-01-15 14:30:00.000000+00"

  externalClusters:
    - name: my-postgres
      barmanObjectStore:
        destinationPath: s3://my-backups/postgres/
        s3Credentials:
          accessKeyId:
            name: backup-creds
            key: ACCESS_KEY_ID
          secretAccessKey:
            name: backup-creds
            key: SECRET_ACCESS_KEY
        wal:
          compression: gzip
```

### Rolling Updates

```yaml
# Update PostgreSQL version (rolling update)
kubectl patch cluster my-postgres --type merge -p '
{
  "spec": {
    "imageName": "ghcr.io/cloudnative-pg/postgresql:16.2"
  }
}'

# Change configuration (some require restart)
kubectl patch cluster my-postgres --type merge -p '
{
  "spec": {
    "postgresql": {
      "parameters": {
        "max_connections": "300"
      }
    }
  }
}'

# Watch the rolling update
kubectl get pods -w
```

### Switchover (Planned Failover)

```bash
# Promote a specific replica to primary
kubectl cnpg promote my-postgres my-postgres-2

# Or using annotation
kubectl annotate cluster my-postgres \
  cnpg.io/targetPrimary=my-postgres-2
```

---

## Monitoring and Observability

### Built-in Metrics

```yaml
# CloudNativePG exports Prometheus metrics automatically
# Enable PodMonitor for automatic scraping
spec:
  monitoring:
    enablePodMonitor: true
```

### Key Metrics

```
CLOUDNATIVEPG METRICS
─────────────────────────────────────────────────────────────────

Cluster Health:
├── cnpg_collector_up                    # Collector running
├── cnpg_pg_replication_lag              # Replication lag (bytes)
├── cnpg_pg_replication_streaming        # Streaming replication status

Database Metrics:
├── cnpg_pg_database_size_bytes          # Database size
├── cnpg_pg_stat_activity_count          # Active connections
├── cnpg_pg_stat_replication_*           # Replication stats

Performance:
├── cnpg_pg_stat_bgwriter_*              # Background writer stats
├── cnpg_pg_stat_database_*              # Per-database stats
├── cnpg_pg_locks_*                      # Lock statistics

Backup:
├── cnpg_pg_wal_archive_status           # WAL archiving status
├── cnpg_collector_last_backup_timestamp # Last successful backup
```

### Grafana Dashboard

```bash
# Import the CloudNativePG Grafana dashboard
# Dashboard ID: 20417

# Or use kubectl plugin
kubectl cnpg status my-postgres
```

---

## War Story: The Schema Migration That Saved the Company

*How point-in-time recovery rescued a production database*

### The Incident

A fintech startup was deploying a new feature with database migrations. The migration script had been tested in staging, but staging had 1% of production data.

**13:42** - Developer runs migration: `ALTER TABLE transactions ADD COLUMN category VARCHAR(50)`

**13:43** - Migration continues: `UPDATE transactions SET category = classify(description)` — This should have been a background job.

**13:44** - Database CPU hits 100%. All connections exhausted. The UPDATE was scanning 50 million rows, locking the entire table.

**13:45** - Payments start failing. Customer support tickets flood in.

**13:46** - Panicked developer kills the migration. But the damage is done—half the rows have been updated, half haven't. Data is inconsistent.

**13:47** - Options discussed:
1. Manual fix? Would take days to identify and repair affected rows
2. Restore from last night's backup? Lose 14 hours of transactions
3. Point-in-time recovery to 13:41? Lose 6 minutes of data

### The Recovery

```bash
# Step 1: Check WAL archiving status
kubectl cnpg status prod-postgres

# Continuous Backup status:
# WAL archiving: OK (Last archived: 13:46:32)

# Step 2: Create recovered cluster
cat > recovery.yaml << 'EOF'
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: prod-postgres-recovered
spec:
  instances: 3
  storage:
    size: 500Gi
    storageClass: premium-ssd
  bootstrap:
    recovery:
      source: prod-postgres
      recoveryTarget:
        targetTime: "2024-01-15 13:41:00.000000+00"  # 1 minute before migration
  externalClusters:
    - name: prod-postgres
      barmanObjectStore:
        destinationPath: s3://company-backups/postgres/
        s3Credentials:
          accessKeyId:
            name: backup-creds
            key: ACCESS_KEY_ID
          secretAccessKey:
            name: backup-creds
            key: SECRET_ACCESS_KEY
EOF

kubectl apply -f recovery.yaml

# Step 3: Wait for recovery (took 12 minutes for 500GB database)
watch kubectl get cluster prod-postgres-recovered

# Step 4: Verify data
kubectl exec -it prod-postgres-recovered-1 -- psql -U postgres -d app -c \
  "SELECT COUNT(*) FROM transactions WHERE category IS NOT NULL;"
# 0 rows — migration hadn't run yet, perfect!

# Step 5: Switch application to recovered cluster
kubectl patch deployment api-server -p \
  '{"spec":{"template":{"spec":{"containers":[{"name":"api","env":[{"name":"DATABASE_HOST","value":"prod-postgres-recovered-rw"}]}]}}}}'
```

### Timeline

```
INCIDENT TIMELINE
─────────────────────────────────────────────────────────────────

13:41 │ Normal operations
      │ WAL continuously archived to S3
      │
13:42 │ Migration starts (ADD COLUMN)
      │ ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ Quick
      │
13:43 │ UPDATE begins
      │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
      │ ████████████████████████████████████ Table locked
      │
13:44 │ CPU 100%, connections exhausted
      │ ████████████████████████████████████ INCIDENT
      │
13:45 │ Payments failing
      │ ████████████████████████████████████ CRITICAL
      │
13:46 │ Migration killed, data inconsistent
      │ ████████████████████████████████████ DAMAGE DONE
      │
13:47 │ PITR decision made
      │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ Recovery started
      │
13:59 │ Recovery complete (12 min for 500GB)
      │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
      │
14:00 │ App switched to recovered cluster
      │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ RESOLVED

Total data loss: 1 minute (13:41-13:42)
Alternative without PITR: 14 hours (last night's backup)
```

### Post-Incident Improvements

1. **Migration review process** — All migrations reviewed by DBA team
2. **Staging with production-scale data** — Subset of anonymized production data
3. **Backup verification** — Weekly restore tests to verify backups work
4. **Migration patterns** — Background jobs for large updates
5. **Connection limits** — Per-application connection pools

---

## CloudNativePG vs Other Operators

```
POSTGRESQL OPERATOR COMPARISON
─────────────────────────────────────────────────────────────────

                    CloudNativePG  Zalando    CrunchyData  KubeDB
─────────────────────────────────────────────────────────────────
ARCHITECTURE
Primary/replica     ✓              ✓          ✓            ✓
Streaming replic.   ✓              ✓          ✓            ✓
External etcd       ✗              ✓ (Patroni) ✗           ✗
External HAProxy    ✗              ✓          Optional     ✓
CNCF member         ✓ (Sandbox)    ✗          ✗            ✗

FEATURES
Auto failover       ✓✓             ✓          ✓            ✓
PITR                ✓✓             ✓          ✓✓           ✓
Backup to S3        ✓✓ (native)    ✓          ✓✓           ✓
Connection pooling  ✓ (PgBouncer)  ✓          ✓            ✓
Logical replication ✓              ✓          ✓            Limited
Fencing             ✓✓             ✓          ✓            ✓

OPERATIONS
Rolling updates     ✓              ✓          ✓            ✓
Online resize       ✓              Limited    ✓            ✓
Clone from backup   ✓✓             ✓          ✓            ✓
Declarative config  ✓✓             ✓          ✓            ✓

OBSERVABILITY
Prometheus export   ✓✓             ✓          ✓            ✓
Grafana dashboards  ✓              ✓          ✓✓           ✓

PRODUCTION-READY
Documentation       ✓✓             ✓          ✓✓           ✓
Community           Growing        Large      Large        Medium
Enterprise support  EDB            Zalando    CrunchyData  AppsCode

BEST FOR:
─────────────────────────────────────────────────────────────────
CloudNativePG:   Simple architecture, CNCF, no external dependencies
Zalando:         Battle-tested (runs Zalando's production), Patroni expertise
CrunchyData:     Enterprise features, PostgreSQL company backing
KubeDB:          Multi-database shops (also MySQL, MongoDB, etc.)
```

---

## Common Mistakes

| Mistake | Why It's Bad | Better Approach |
|---------|--------------|-----------------|
| No backup configured | Data loss is permanent | Always configure barmanObjectStore |
| Single replica | No failover, no HA | Minimum 3 instances for production |
| No resource limits | Pod can be OOM killed | Set appropriate requests/limits |
| Storage too small | Cluster stops when full | Monitor usage, auto-expand or alert |
| No affinity rules | All pods on same node | Spread across zones with topologyKey |
| Missing monitoring | Can't see problems | Enable PodMonitor, set up alerts |
| Direct pod access | Bypasses failover | Always use Services (cluster-rw, cluster-ro) |
| No PITR testing | Backups may not work | Regular restore drills |

---

## Hands-On Exercise

### Task: Deploy PostgreSQL and Test Failover

**Objective**: Deploy a 3-node PostgreSQL cluster, verify failover works, and perform point-in-time recovery.

**Success Criteria**:
1. 3-node cluster running
2. Data survives primary failure
3. Automatic failover completes in <10 seconds
4. Backup to local storage working

### Steps

```bash
# 1. Install CloudNativePG operator
kubectl apply --server-side -f \
  https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.22/releases/cnpg-1.22.0.yaml

kubectl wait --for=condition=Available deployment/cnpg-controller-manager \
  -n cnpg-system --timeout=120s

# 2. Create a minimal cluster (no S3 for lab simplicity)
cat > postgres-lab.yaml << 'EOF'
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: lab-postgres
spec:
  instances: 3

  storage:
    size: 5Gi

  postgresql:
    parameters:
      max_connections: "100"

  bootstrap:
    initdb:
      database: testdb
      owner: testuser
EOF

kubectl apply -f postgres-lab.yaml

# 3. Wait for cluster to be ready
kubectl wait --for=condition=Ready cluster/lab-postgres --timeout=300s

# 4. Check cluster status
kubectl cnpg status lab-postgres 2>/dev/null || kubectl describe cluster lab-postgres

# 5. Insert test data
kubectl exec -it lab-postgres-1 -- psql -U testuser -d testdb << 'EOF'
CREATE TABLE important_data (
    id SERIAL PRIMARY KEY,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO important_data (value)
SELECT 'Record ' || generate_series(1, 1000);

SELECT COUNT(*) as record_count FROM important_data;
EOF

# 6. Note which pod is primary
kubectl get pods -l cnpg.io/cluster=lab-postgres -o wide
PRIMARY_POD=$(kubectl get pods -l cnpg.io/cluster=lab-postgres \
  -o jsonpath='{.items[?(@.metadata.labels.role=="primary")].metadata.name}')
echo "Primary pod: $PRIMARY_POD"

# 7. SIMULATE FAILURE: Delete the primary pod
echo "Killing primary pod: $PRIMARY_POD"
kubectl delete pod $PRIMARY_POD

# 8. Watch failover happen
# In another terminal: watch kubectl get pods -l cnpg.io/cluster=lab-postgres

# 9. Wait for new primary
sleep 10
kubectl get pods -l cnpg.io/cluster=lab-postgres -o wide

# 10. Verify data survived
NEW_PRIMARY=$(kubectl get pods -l cnpg.io/cluster=lab-postgres \
  -o jsonpath='{.items[?(@.metadata.labels.role=="primary")].metadata.name}')
echo "New primary: $NEW_PRIMARY"

kubectl exec -it $NEW_PRIMARY -- psql -U testuser -d testdb \
  -c "SELECT COUNT(*) as record_count FROM important_data;"
# Should show 1000 records

# 11. Check cluster health
kubectl describe cluster lab-postgres | grep -A 10 "Status:"

# Clean up
kubectl delete cluster lab-postgres
```

### Verification

```bash
# All checks should pass:
# ✓ Cluster came up with 3 instances
# ✓ Primary failover completed automatically
# ✓ All 1000 records survived
# ✓ New primary is serving traffic
```

---

## Quiz

### Question 1
What makes CloudNativePG different from other PostgreSQL operators?

<details>
<summary>Show Answer</summary>

**No external dependencies (no etcd, Patroni, HAProxy)**

CloudNativePG uses native Kubernetes primitives for leader election and service routing. This simpler architecture means fewer components to fail and easier troubleshooting. Most other operators rely on external tools like Patroni (which needs etcd) or HAProxy for connection routing.
</details>

### Question 2
What Services does CloudNativePG create for a cluster named "my-postgres"?

<details>
<summary>Show Answer</summary>

**Three services: my-postgres-rw, my-postgres-ro, my-postgres-r**

- `my-postgres-rw`: Points to primary only (read-write traffic)
- `my-postgres-ro`: Points to replicas only (read-only, load balanced)
- `my-postgres-r`: Points to any node (reads from any, including primary)

Applications should use these services, not pod names, to survive failovers.
</details>

### Question 3
How does CloudNativePG achieve point-in-time recovery?

<details>
<summary>Show Answer</summary>

**Continuous WAL archiving to object storage (S3/GCS/Azure)**

CloudNativePG continuously archives Write-Ahead Log (WAL) files to object storage. Combined with periodic base backups, this allows recovery to any point in time within the retention window. The recovery process replays WAL files up to the specified timestamp.
</details>

### Question 4
What happens when a CloudNativePG primary fails?

<details>
<summary>Show Answer</summary>

**Automatic failover sequence:**
1. Operator detects failure (typically 3-5 seconds)
2. Healthiest replica is promoted to primary
3. Kubernetes Service endpoints are updated immediately
4. Other replicas start following the new primary
5. Old primary pod is rebuilt as a replica

Applications using the `-rw` Service automatically connect to the new primary with no configuration changes.
</details>

### Question 5
What is the `barmanObjectStore` configuration used for?

<details>
<summary>Show Answer</summary>

**Continuous backup to object storage**

The `barmanObjectStore` section configures:
- Destination path for backups (S3, GCS, Azure)
- Credentials for access
- WAL compression settings
- Retention policies

It enables both base backups and continuous WAL archiving for point-in-time recovery.
</details>

### Question 6
How do you trigger a manual backup in CloudNativePG?

<details>
<summary>Show Answer</summary>

**Create a Backup custom resource:**

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Backup
metadata:
  name: my-manual-backup
spec:
  cluster:
    name: my-postgres
```

The operator detects the new Backup resource and triggers a backup to the configured object storage.
</details>

### Question 7
Why should you spread PostgreSQL pods across availability zones?

<details>
<summary>Show Answer</summary>

**To survive AZ failures**

If all PostgreSQL pods are in the same AZ and that AZ has an outage, your entire database is unavailable. Spreading across zones ensures that an AZ failure only affects one pod, while the cluster continues operating with the remaining pods.

Configure with:
```yaml
spec:
  affinity:
    topologyKey: topology.kubernetes.io/zone
```
</details>

### Question 8
What's the minimum recommended number of instances for a production cluster?

<details>
<summary>Show Answer</summary>

**3 instances**

With 3 instances:
- 1 primary for writes
- 2 replicas for failover and read scaling
- Can survive 1 node failure while maintaining HA
- Synchronous replication to at least 1 replica ensures no data loss

Single-instance clusters have no failover capability. Two instances can't provide true HA (losing primary means no failover).
</details>

---

## Key Takeaways

1. **CNCF Sandbox project** — Community-vetted, growing adoption
2. **No external dependencies** — No etcd, Patroni, or HAProxy required
3. **Automatic failover** — Typically 5-10 seconds, no manual intervention
4. **Built-in backups** — Continuous WAL archiving to S3/GCS/Azure
5. **Point-in-time recovery** — Restore to any second in retention window
6. **Declarative configuration** — All settings in Kubernetes CRDs
7. **Native PostgreSQL** — Standard streaming replication, standard tools
8. **Three Services** — rw (primary), ro (replicas), r (any)
9. **Rolling updates** — Version upgrades with zero downtime
10. **Production-ready** — Used by enterprises, banks, fintechs

---

## Next Steps

- **Next Module**: [Module 15.3: Neon & PlanetScale](module-15.3-serverless-databases.md) — Serverless databases
- **Related**: [GitOps & Deployments](../gitops-deployments/) — Managing database config with GitOps
- **Related**: [Observability Toolkit](../observability/) — Monitoring PostgreSQL

---

## Further Reading

- [CloudNativePG Documentation](https://cloudnative-pg.io/documentation/)
- [CloudNativePG GitHub](https://github.com/cloudnative-pg/cloudnative-pg)
- [PostgreSQL Streaming Replication](https://www.postgresql.org/docs/current/warm-standby.html)
- [Barman (Backup and Recovery Manager)](https://pgbarman.org/)
- [Data on Kubernetes Community](https://dok.community/)

---

*"The best database operator is one you forget is there. CloudNativePG handles the hard parts of PostgreSQL on Kubernetes so you can focus on your application."*
