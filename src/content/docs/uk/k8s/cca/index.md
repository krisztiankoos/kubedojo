---
title: "CCA — Сертифікований спеціаліст із хмарних технологій (Cilium)"
sidebar:
  order: 1
  label: "CCA"
---
> **Іспит із множинним вибором** | 90 хвилин | Прохідний бал: 75% | $250 USD | **Сертифікація CNCF**

## Огляд

CCA (Cilium Certified Associate) підтверджує знання мереж, безпеки та спостережуваності на базі Cilium. Це **теоретичний іспит** — питання з множинним вибором, які перевіряють ваше розуміння того, як eBPF змінює ландшафт хмарних технологій через Cilium.

**KubeDojo охоплює ~90% тем CCA** через модулі мереж, безпеки та eBPF, плюс один спеціалізований модуль CCA, що охоплює специфічні особливості архітектури Cilium та Hubble.

> **Cilium є стандартом де-факто для мереж на базі eBPF.** Це один із найбільш динамічних проєктів CNCF, який використовується Google (GKE), Amazon (EKS) та Azure (AKS) як мережевий рівень наступного покоління. CCA підтверджує ваше володіння найсучаснішим стеком мереж Kubernetes.

---

## Модулі, специфічні для CCA

Цей модуль фокусується на глибині архітектури Cilium, необхідній для іспиту:

| # | Модуль | Тема | Охоплені домени |
|---|--------|-------|-----------------|
| 1 | [Глибоке занурення в Cilium](/uk/k8s/cks/part2-cluster-hardening/module-2.1-rbac-deep-dive/) | Архітектура eBPF, режими інкапсуляції vs. Direct Routing, Hubble Relay, ClusterMesh, політики L7 | Домени 1-5 |

---

## Домени іспиту

| Домен | Вага | Охоплення в KubeDojo |
|--------|--------|-------------------|
| Архітектура та eBPF | 20% | Відмінне ([Networking Toolkit 1.1](/uk/cloud/aws-essentials/module-1.1-iam/)) |
| Мережеві концепції | 25% | Відмінне ([Networking 1.1](../../platform/disciplines/reliability-security/networking/module-1.1-cni-architecture/)) |
| Безпека та політики | 25% | Відмінне ([Networking 1.2](../../platform/disciplines/reliability-security/networking/module-1.2-network-policies/)) |
| Спостережуваність (Hubble) | 15% | Відмінне ([Observability Toolkit 1.7](../../platform/toolkits/observability-intelligence/observability/module-1.7-hubble/)) |
| Мультикластер та Service Mesh | 15% | Відмінне ([Networking 1.5](../../platform/disciplines/reliability-security/networking/module-1.5-multi-cluster-networking/)) |

---

## Домен 1: Архітектура та eBPF (20%)

### Компетенції
- Розуміння основ eBPF (програми, мапи, гачки)
- Переваги Cilium над традиційними рішеннями на базі iptables
- Компоненти Cilium (Agent, Operator, CNI plugin)
- Життєвий цикл пакету в Cilium

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Networking Toolkit 1.1](/uk/cloud/aws-essentials/module-1.1-iam/) | Що таке eBPF та Cilium? Архітектура | Пряма |
| [Глибоке занурення в Cilium](/uk/k8s/cks/part2-cluster-hardening/module-2.1-rbac-deep-dive/) | Технічні деталі мап eBPF та обробки пакетів | Пряма |

---

## Домен 2: Мережеві концепції (25%)

### Компетенції
- Режими мережі: VXLAN (Overlay) vs. Native Routing (BGP)
- IP Address Management (IPAM) у Cilium
- Балансування навантаження на рівні вузла (XDP)
- Інтеграція з Ingress та Gateway API

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Мережі 1.1](../../platform/disciplines/reliability-security/networking/module-1.1-cni-architecture/) | Основи CNI та маршрутизації | Пряма |
| [Глибоке занурення в Cilium](/uk/k8s/cks/part2-cluster-hardening/module-2.1-rbac-deep-dive/) | Конфігурація VXLAN та Direct Routing | Пряма |

---

## Домен 3: Безпека та політики (25%)

### Компетенції
- CiliumNetworkPolicy (CNP) та ClusterwideCNP (CCNP)
- Політики на рівнях L3/L4 (IP/Port) та L7 (HTTP/DNS/Kafka)
- Використання міток (Labels) та ідентичності (Identity-based security)
- Шифрування трафіку: IPsec та WireGuard

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Мережі 1.2](../../platform/disciplines/reliability-security/networking/module-1.2-network-policies/) | Політики Cilium та безпека L7 | Пряма |
| [Security Tools 4.5](/uk/platform/toolkits/security-quality/code-quality/module-12.5-trivy/) | Tetragon — безпека виконання від творців Cilium | Контекст |

---

## Домен 4: Спостережуваність (15%)

### Компетенції
- Архітектура Hubble (Relay, UI, CLI)
- Метрики Hubble (метки, типи потоків)
- Візуалізація топології мережі та виявлення проблем
- Налагодження через `cilium-dbg` та `hubble observe`

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Observability 1.7](../../platform/toolkits/observability-intelligence/observability/module-1.7-hubble/) | Практична робота з Hubble | Пряма |
| [Мережі 1.6](../../platform/disciplines/reliability-security/networking/module-1.6-troubleshooting/) | Налагодження мережі в K8s | Контекст |

---

## Домен 5: Мультикластер та Service Mesh (15%)

### Компетенції
- ClusterMesh: з'єднання незалежних кластерів
- Cilium Service Mesh (режим Ambient, Ingress)
- Глобальні сервіси та Load Balancing між кластерами
- Інтеграція з Istio (Sidecar acceleration)

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Мережі 1.5](../../platform/disciplines/reliability-security/networking/module-1.5-multi-cluster-networking/) | Мультикластерні мережі та ClusterMesh | Пряма |
| [Глибоке занурення в Cilium](/uk/k8s/cks/part2-cluster-hardening/module-2.1-rbac-deep-dive/) | Cilium як заміна Service Mesh | Пряма |

---

## Стратегія підготовки

```
ШЛЯХ ПІДГОТОВКИ ДО CCA (рекомендований порядок)
══════════════════════════════════════════════════════════════

Тиждень 1: eBPF та Основи (20%)
├── Модуль Networking Toolkit 1.1 (Cilium Intro)
├── Модуль "Глибоке занурення в Cilium" (eBPF & Maps)
└── Практика: Встановіть Cilium, вивчіть статус через `cilium status`

Тиждень 2: Мережа та Маршрутизація (25%)
├── Практика: Перемикання між VXLAN та Direct Routing
├── Вивчіть: Як Cilium замінює kube-proxy (Maglev, XDP)
└── Огляд: IPAM режими у хмарних провайдерах

Тиждень 3: Безпека та Політики (25%)
├── Практика: Напишіть CiliumNetworkPolicy для фільтрації DNS
├── Реалізуйте L7 політику для обмеження HTTP методів
└── Вивчіть: WireGuard шифрування між вузлами

Тиждень 4: Hubble та ClusterMesh (15% + 15%)
├── Модуль Observability 1.7 (Hubble)
├── Практика: Налаштуйте ClusterMesh між двома кластерами
└── Огляд: `hubble observe` для дебагу пакетів
```

---

## Поради для іспиту

- **Identity-based Security** — Розумійте, чому Cilium використовує числові ідентифікатори замість IP-адрес для політик (масштабованість!).
- **eBPF Maps** — Знайте, що мапи є основним механізмом передачі даних між ядром та Cilium agent.
- **CLI Команди** — Запам'ятайте різницю між `cilium status`, `cilium connectivity test` та `hubble observe`.
- **L7 Visibility** — Hubble бачить HTTP шляхи та DNS запити тільки якщо застосована відповідна політика L7.
- **ClusterMesh** — Знайте вимоги для ClusterMesh (непересічні CIDR, доступ до etcd або kvstore).

---

## Пов'язані сертифікації

```
ШЛЯХ СЕРТИФІКАЦІЇ
══════════════════════════════════════════════════════════════

Рівень Associate:
├── KCNA (Cloud Native Associate) — Основи K8s
├── KCSA (Security Associate) — Основи безпеки
└── CCA (Cilium Associate) ← ВИ ТУТ

Рівень Professional:
├── CKA (K8s Administrator) — Мережі є великою частиною
├── CKS (K8s Security Specialist) — Політики Cilium допомагають у CKS
└── CNPE (Platform Engineer) — eBPF є ядром сучасних платформ
```

CCA — це ідеальний вибір для тих, хто хоче бути на передовій **Cloud-Native Networking**.
