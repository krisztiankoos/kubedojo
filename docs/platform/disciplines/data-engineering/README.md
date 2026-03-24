# Data Engineering on Kubernetes

**Run data infrastructure where your applications already live.**

Kafka, Spark, Flink, Airflow — the backbone of modern data pipelines. This discipline teaches you to run them on Kubernetes, where they benefit from the same orchestration, scaling, and observability as your application workloads.

---

## Modules

| # | Module | Time | What You'll Learn |
|---|--------|------|-------------------|
| 1.1 | [Stateful Workloads & Storage](module-1.1-stateful-workloads.md) | 3h | CSI internals, Local PVs, StatefulSets, Operators for state |
| 1.2 | [Apache Kafka on K8s (Strimzi)](module-1.2-kafka.md) | 3.5h | KRaft, Strimzi Operator, schema management, securing Kafka |
| 1.3 | [Stream Processing with Flink](module-1.3-flink.md) | 3.5h | Flink Operator, checkpointing, event time, watermarks |
| 1.4 | [Batch Processing with Spark](module-1.4-spark.md) | 3h | Spark on K8s, Spark Operator, dynamic allocation |
| 1.5 | [Data Orchestration with Airflow](module-1.5-airflow.md) | 2.5h | KubernetesExecutor, DAGs, Helm deployment |
| 1.6 | [Building a Data Lakehouse](module-1.6-lakehouse.md) | 3.5h | Iceberg, Delta Lake, Trino on K8s, Hive Metastore |

**Total time**: ~19 hours

---

## Prerequisites

- Kubernetes Storage (PV/PVC, StorageClasses)
- Kubernetes Jobs and CronJobs
- Basic Python (for Airflow and Spark exercises)

## Why on Kubernetes?

Running data infrastructure on K8s gives you unified tooling (same CI/CD, same monitoring, same RBAC), elastic scaling, and reduced operational overhead. The trade-off is complexity — these modules teach you to handle it.
