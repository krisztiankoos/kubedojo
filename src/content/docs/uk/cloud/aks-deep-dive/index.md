---
title: "Глибоке занурення в Azure AKS"
slug: uk/cloud/aks-deep-dive
sidebar:
  order: 0
en_commit: "d17204311ac4f39e1498fbf70adbbcd021222118"
en_file: "src/content/docs/cloud/aks-deep-dive/index.md"
---
**Kubernetes рівня продакшн на Azure — від пулів вузлів до масштабування за допомогою KEDA.**

AKS — це найбільш динамічно зростаючий керований сервіс Kubernetes, що тісно інтегрований з екосистемою Azure. Цей трек охоплює архітектуру пулів вузлів (node pools) та інтеграцію з Entra ID, чотири мережеві моделі CNI (Kubenet, Azure CNI, CNI Overlay, Cilium), безпеку без використання секретів за допомогою Workload Identity та Key Vault, а також експлуатацію в продакшні з Container Insights, Managed Prometheus та автомасштабуванням KEDA.

---

## Модулі

| # | Модуль | Час | Що ви дізнаєтесь |
|---|--------|------|-------------------|
| 1 | [Модуль 7.1: Архітектура AKS та управління вузлами](module-7.1-aks-architecture/) | 2 год | Системні/користувацькі пули вузлів, VMSS, зони доступності, Entra ID RBAC |
| 2 | [Модуль 7.2: Просунуті мережі AKS](module-7.2-aks-networking/) | 3.5 год | Kubenet проти Azure CNI, Overlay та Cilium, мережеві політики, Private Link |
| 3 | [Модуль 7.3: AKS Workload Identity та безпека](module-7.3-aks-identity/) | 1.5 год | Entra Workload Identity, Secrets Store CSI, Azure Policy, Defender |
| 4 | [Модуль 7.4: Сховища, обсервабіліті та масштабування AKS](module-7.4-aks-production/) | 2.5 год | Azure Disks/Files, Container Insights, Managed Prometheus, KEDA |
| 5 | [Модуль 7.5: Azure Kubernetes Fleet Manager та мультикластерні операції](module-7.5-aks-fleet-manager/) | 2.5 год | Azure Kubernetes Fleet Manager, Azure Arc, крос-регіональність, GitOps з Flux |

**Загальний час**: ~12 годин

---

## Передумови

- [Основи Azure DevOps](../azure-essentials/) — фундаментальні знання Entra ID, VNet, ВМ та сховищ
- [Архітектурні патерни хмар](../architecture-patterns/) — компроміси керованого K8s, мультикластерність, інтеграція IAM

## Що далі

Після «Глибокого занурення в AKS» ознайомтеся з мультихмарними шаблонами або перейдіть до [треку з розробки платформ (Platform Engineering)](../../platform/).