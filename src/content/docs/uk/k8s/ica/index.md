---
title: "ICA — Сертифікований спеціаліст із Istio"
sidebar:
  order: 1
  label: "ICA"
---
> **Іспит із множинним вибором** | 90 хвилин | Прохідний бал: 75% | $250 USD | **Сертифікація CNCF**

## Огляд

ICA (Istio Certified Associate) підтверджує знання архітектури Istio, управління трафіком, безпеки (mTLS) та спостережуваності у сервісній мережі (service mesh). Як і PCA, це **теоретичний іспит** — питання з множинним вибором, які перевіряють ваше розуміння того, як Istio вирішує проблеми мікросервісів у масштабі.

**KubeDojo охоплює ~90% тем ICA** через існуючі модулі мереж та спостережуваності, плюс один спеціалізований модуль ICA, що охоплює просунуту конфігурацію Istio та режими Ambient Mesh.

> **Istio є найпопулярнішим Service Mesh у світі.** Він став проєктом CNCF Graduated у 2023 році і є стандартом для корпоративних компаній, яким потрібен mTLS за замовчуванням, просунуте керування трафіком та глибока видимість мережі без зміни коду застосунку.

---

## Модулі, специфічні для ICA

Цей модуль заповнює прогалину між загальними знаннями сервісних мереж та вимогами іспиту ICA:

| # | Модуль | Тема | Охоплені домени |
|---|--------|-------|-----------------|
| 1 | [Глибоке занурення в Istio](/uk/k8s/cks/part2-cluster-hardening/module-2.1-rbac-deep-dive/) | Envoy Proxy, режими Sidecar vs. Ambient, WASM розширення, мультикластерні топології, налагодження istioctl | Домени 1-5 |

---

## Домени іспиту

| Домен | Вага | Охоплення в KubeDojo |
|--------|--------|-------------------|
| Основи Service Mesh | 15% | Відмінне ([Networking 1.4](../../platform/disciplines/reliability-security/networking/module-1.4-service-mesh/)) |
| Архітектура Istio | 20% | Відмінне ([Глибоке занурення в Istio](/uk/k8s/cks/part2-cluster-hardening/module-2.1-rbac-deep-dive/)) |
| Управління трафіком | 25% | Відмінне ([Networking 1.4](../../platform/disciplines/reliability-security/networking/module-1.4-service-mesh/)) |
| Безпека та ідентичність | 20% | Відмінне ([Security 4.8](/uk/platform/toolkits/security-quality/code-quality/module-12.5-trivy/)) |
| Спостережуваність | 20% | Відмінне ([Observability Toolkit](../../platform/toolkits/observability-intelligence/observability/)) |

---

## Домен 1: Основи Service Mesh (15%)

### Компетенції
- Розуміння проблем, які вирішує service mesh (надійність, безпека, видимість)
- Порівняння service mesh із традиційними бібліотеками додатків
- Розуміння концепції Data Plane vs. Control Plane

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Мережі 1.4](../../platform/disciplines/reliability-security/networking/module-1.4-service-mesh/) | Чому нам потрібен Service Mesh? Основи | Пряма |
| [Розподілені системи 5.1](../../platform/foundations/distributed-systems/module-5.1-what-makes-systems-distributed/) | Виклики мережі в розподілених системах | Контекст |

---

## Домен 2: Архітектура Istio (20%)

### Компетенції
- Розуміння компонентів Istiod (Pilot, Citadel, Galley)
- Робота з Envoy Proxy як Data Plane
- **Режим Ambient Mesh** (ztunnel, waypoints) — *Нова критична тема!*
- Ін'єкція sidecar-контейнерів
- Життєвий цикл конфігурації Istio

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Глибоке занурення в Istio](/uk/k8s/cks/part2-cluster-hardening/module-2.1-rbac-deep-dive/) | Детальна архітектура Istiod та Ambient Mesh | Пряма |
| [Networking Toolkit 1.2](../../platform/toolkits/infrastructure-networking/networking/module-1.2-service-mesh/) | Встановлення та базова архітектура | Пряма |

---

## Домен 3: Управління трафіком (25%)

### Компетенції
- Використання Gateway та VirtualService для зовнішнього трафіку
- Налаштування DestinationRule (subset, load balancing, outlier detection)
- Впровадження стійкості: retries, timeouts, circuit breakers
- Користувацька маршрутизація: Canary, Blue-Green, Mirroring
- ServiceEntry для доступу до зовнішніх сервісів

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Мережі 1.4](../../platform/disciplines/reliability-security/networking/module-1.4-service-mesh/) | Практична маршрутизація Istio | Пряма |
| [Release Engineering 1.1](/uk/k8s/kcna/part4-application-delivery/module-4.3-release-strategies/) | Стратегії Canary та Blue-Green | Контекст |

---

## Домен 4: Безпека та ідентичність (20%)

### Компетенції
- Розуміння mTLS (Mutual TLS) у Istio
- Налаштування PeerAuthentication та RequestAuthentication
- Використання AuthorizationPolicy (RBAC на рівні L7)
- Ідентичність через SPIFFE
- Інтеграція із зовнішніми Identity Providers (JWT/OIDC)

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Мережі 1.4](../../platform/disciplines/reliability-security/networking/module-1.4-service-mesh/) | mTLS та політики авторизації Istio | Пряма |
| [Security Tools 4.8](/uk/platform/toolkits/security-quality/code-quality/module-12.5-trivy/) | SPIFFE/SPIRE — ідентичність у сервісній мережі | Пряма |

---

## Домен 5: Спостережуваність (20%)

### Компетенції
- Генерація та збір метрик (Prometheus інтеграція)
- Розподілене трасування з Istio
- Використання Kiali для візуалізації топології мережі
- Налаштування логів доступу Envoy (Access Logs)

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Observability Toolkit 1.5](../../platform/toolkits/observability-intelligence/observability/module-1.5-tracing/) | Розподілене трасування | Пряма |
| [Networking Toolkit 1.2](../../platform/toolkits/infrastructure-networking/networking/module-1.2-service-mesh/) | Kiali, Grafana та Prometheus для Istio | Пряма |

---

## Стратегія підготовки

```
ШЛЯХ ПІДГОТОВКИ ДО ICA (рекомендований порядок)
══════════════════════════════════════════════════════════════

Тиждень 1: Концепції та Data Plane (15% + 20%)
├── Модуль Мережі 1.4 (Service Mesh Intro)
├── Модуль "Глибоке занурення в Istio" ( Envoy & istiod)
└── Практика: Встановіть Istio через istioctl, вивчіть компоненти

Тиждень 2: Traffic Management (25%)
├── Практика: Gateway -> VirtualService -> DestinationRule
├── Реалізуйте Canary розгортання з вагами
└── Вивчіть: Circuit Breaking та Outlier Detection

Тиждень 3: Безпека (20%)
├── Практика: Увімкніть STRICT mTLS у всьому кластері
├── Напишіть AuthorizationPolicy для доступу між сервісами
└── Вивчіть: JWT валідація через RequestAuthentication

Тиждень 4: Ambient Mesh та Спостережуваність (20%)
├── Модуль "Глибоке занурення в Istio" (Ambient Mode)
├── Практика: Kiali для візуалізації трафіку
└── Огляд: istioctl analyze та дебаг Envoy конфігурації
```

---

## Поради для іспиту

- **VirtualService vs DestinationRule** — Чітко розумійте різницю: VirtualService каже "куди йти" (routing), DestinationRule каже "як поводитись" (TLS, LB, subsets).
- **Ambient Mesh — це майбутнє** — Очікуйте багато питань про режим без Sidecar. Знайте, що таке `ztunnel` та `Waypoint proxy`.
- **istioctl — ваш кращий друг** — Знайте команди `istioctl analyze`, `istioctl proxy-config` та `istioctl dashboard`.
- **mTLS рівні** — Розрізняйте `PERMISSIVE` та `STRICT` режими в PeerAuthentication.
- **Envoy фільтри** — Хоча глибокого Envoy не буде, розуміння того, як Istio генерує Envoy config, допоможе.

---

## Пов'язані сертифікації

```
ШЛЯХ СЕРТИФІКАЦІЇ
══════════════════════════════════════════════════════════════

Рівень Associate:
├── KCNA (Cloud Native Associate) — Основи K8s
├── PCA (Prometheus Associate) — Моніторинг
└── ICA (Istio Associate) ← ВИ ТУТ

Рівень Professional:
├── CKA (K8s Administrator) — Операції
├── CKS (K8s Security Specialist) — Зміцнення (Istio допомагає!)
└── CNPE (Platform Engineer) — Service Mesh є обов'язковим
```

ICA ідеально підходить для **Platform Engineers**, оскільки Istio часто є центральним компонентом внутрішньої платформи розробки (IDP).
