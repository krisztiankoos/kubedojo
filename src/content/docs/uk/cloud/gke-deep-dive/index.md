---
title: "Глибоке занурення в GCP GKE"
slug: uk/cloud/gke-deep-dive
sidebar:
  order: 0
en_commit: "47bf257c3ec7632099185c630faf64d73e48caea"
en_file: "src/content/docs/cloud/gke-deep-dive/index.md"
---
**Kubernetes промислового рівня в Google Cloud — від Autopilot до керування Fleet.**

GKE — це найбільш регламентований керований сервіс Kubernetes, із такими функціями, як Autopilot, Dataplane V2 (eBPF) та керування Fleet, що виходять далеко за межі стандартного Kubernetes. Цей трек охоплює архітектурні рішення (Standard проти Autopilot), мережеву інфраструктуру з Dataplane V2 та Gateway API, Workload Identity та Binary Authorization, варіанти зберігання даних, а також мультикластерні операції за допомогою Fleet та Managed Prometheus.

---

## Модулі

| # | Модуль | Час | Що ви вивчите |
|---|--------|------|-------------------|
| 1 | [Модуль 6.1: Архітектура GKE: Standard vs Autopilot](module-6.1-gke-architecture/) | 2 год | Режими кластерів, канали релізів, регіональні та зональні кластери, автооновлення |
| 2 | [Модуль 6.2: Мережева інфраструктура GKE: Dataplane V2 та Gateway API](module-6.2-gke-networking/) | 3 год | VPC-native кластери, eBPF, Cloud Load Balancing, канаркові релізи через Gateway API |
| 3 | [Модуль 6.3: GKE Workload Identity та безпека](module-6.3-gke-identity/) | 2.5 год | Workload Identity Federation, Binary Authorization, Shielded Nodes |
| 4 | [Модуль 6.4: Сховища даних GKE](module-6.4-gke-storage/) | 2 год | Persistent Disks (зональні/регіональні), Filestore, Cloud Storage FUSE, Backup for GKE |
| 5 | [Модуль 6.5: Спостережуваність та керування Fleet у GKE](module-6.5-gke-fleet/) | 3 год | Cloud Operations, Managed Prometheus, Fleet, Multi-Cluster Services, розподіл витрат |

**Загальний час**: ~12.5 годин

---

## Передумови

- [Основи GCP DevOps](../gcp-essentials/) — IAM, VPC, основи Compute Engine
- [Архітектурні патерни хмар](../architecture-patterns/) — компроміси керованих K8s, мультикластерність, інтеграція з IAM

## Що далі

Після курсу «Глибоке занурення в GKE» ознайомтеся з мультихмарними патернами або перейдіть до [треку Platform Engineering](../../platform/).
