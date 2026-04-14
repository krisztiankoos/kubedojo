---
title: "Мультикластерність та платформи"
slug: "uk/on-premises/multi-cluster"
sidebar:
  order: 0
en_commit: "47bf257c3ec7632099185c630faf64d73e48caea"
en_file: "src/content/docs/on-premises/multi-cluster/index.md"
---

Локальні (on-premises) організації рідко обмежуються лише одним кластером Kubernetes. Зі зростанням команд та навантажень виникає потреба у декількох кластерах — для ізоляції середовищ dev/staging/prod, регіональних розгортань, орендарів (tenants) або зменшення радіуса ураження (blast-radius). На відміну від хмари, де створення кластера триває хвилини й коштує лише API-виклики, локальна мультикластерність означає управління фізичними серверами, розміщенням control plane та автоматизацією життєвого циклу на обмеженому обладнанні.

Цей розділ охоплює інфраструктурні платформи (vSphere, OpenStack, Harvester), стратегії control plane для запуску багатьох кластерів на кількох серверах (vCluster, Kamaji) та інструменти декларативного управління, що дозволяють ставитися до кластерів як до cattle за допомогою Cluster API на bare metal.

## Модулі

| Модуль | Опис | Час |
|--------|-------------|------|
| [Модуль 5.1: Приватні хмарні платформи](module-5.1-private-cloud/) | VMware vSphere + Tanzu, OpenStack + Magnum, Harvester | 45 хв |
| [Модуль 5.2: Control Plane для мультикластерності](module-5.2-multi-cluster-control-planes/) | vCluster, Kamaji, спільні vs виділені control planes | 50 хв |
| [Модуль 5.3: Cluster API на Bare Metal](module-5.3-cluster-api-bare-metal/) | CAPM3, CAPV, декларативний життєвий цикл, GitOps-кластери | 50 хв |
| [Управління флотом (Fleet Management)](module-5.4-fleet-management/) | Масштабне управління кластерами, розповсюдження політик та централізована спостережуваність (observability) | 45 хв |
| [Active-Active Multi-Site](module-5.5-active-active-multi-site/) | Disaster recovery, міжкластерні мережі, глобальне балансування та реплікація стану | 60 хв |