---
title: "CAPA — Сертифікований спеціаліст із проєктів Argo"
sidebar:
  order: 1
  label: "CAPA"
---
> **Іспит із множинним вибором** | 90 хвилин | Прохідний бал: 75% | $250 USD | **Сертифікація CNCF**

## Огляд

CAPA (Certified Argo Project Associate) підтверджує знання чотирьох основних проєктів Argo: Argo Workflows, Argo CD, Argo Rollouts та Argo Events. Це **теоретичний іспит** — питання з множинним вибором, що перевіряють ваше розуміння концепцій Argo, його архітектури та патернів використання.

**KubeDojo охоплює ~95% тем CAPA** через існуючі модулі дисциплін та інструментарію Platform Engineering, плюс два спеціалізовані модулі CAPA, що охоплюють просунуті Argo Workflows та Argo Events.

> **Проєкт Argo є другим за популярністю проєктом CNCF Graduated** після самого Kubernetes. Понад 300 організацій використовують Argo у продакшні, включаючи Intuit (його творець), Tesla, Google, Red Hat та GitHub. Розуміння всієї екосистеми Argo — не тільки ArgoCD — стає базовою навичкою для платформних команд Kubernetes.

---

## Домени іспиту

| Домен | Вага | Охоплення в KubeDojo |
|--------|--------|-------------------|
| Argo Workflows | 36% | Відмінне (toolkit модуль + [Advanced Argo Workflows](/uk/k8s/cba/module-1.1-backstage-dev-workflow/)) |
| Argo CD | 34% | Відмінне (1 toolkit + 6 discipline модулів) |
| Argo Rollouts | 18% | Відмінне (1 dedicated toolkit модуль) |
| Argo Events | 12% | Відмінне ([Argo Events](/uk/cloud/enterprise-hybrid/module-10.2-governance/)) |

---

## Модулі, специфічні для CAPA

Ці модулі заповнюють прогалини між існуючим контентом Platform Engineering та вимогами іспиту CAPA:

| # | Модуль | Тема | Релевантність |
|---|--------|-------|-----------|
| 1 | [Просунуті Argo Workflows](/uk/k8s/cba/module-1.1-backstage-dev-workflow/) | Усі 7 типів шаблонів, артефакти, CronWorkflows, мемоїзація, гачки життєвого циклу | Домен 1 (36%) |
| 2 | [Argo Events](/uk/cloud/enterprise-hybrid/module-10.2-governance/) | EventSource, Sensor, Trigger, архітектура EventBus, подієво-орієнтована автоматизація | Домен 4 (12%) |

---

## Домен 1: Argo Workflows (36%)

### Компетенції
- Розуміння CRD Workflow та його життєвого циклу
- Використання всіх 7 типів шаблонів (container, script, resource, suspend, DAG, steps, HTTP)
- Налаштування передачі артефактів між кроками воркфлоу
- Побудова структур воркфлоу на основі DAG та кроків (steps)
- Планування воркфлоу за допомогою CronWorkflow
- Використання параметрів, змінних та конфігурацій на рівні воркфлоу

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Argo Workflows](../../platform/toolkits/cicd-delivery/ci-cd-pipelines/module-3.3-argo-workflows/) | Workflow CRD, DAG/steps, шаблони, параметри | Пряма |
| [Advanced Argo Workflows](/uk/k8s/cba/module-1.1-backstage-dev-workflow/) | Усі 7 типів шаблонів, артефакти, CronWorkflows, повтори, мемоїзація | Пряма |

---

## Домен 2: Argo CD (34%)

### Компетенції
- Розуміння CRD Application та його циклу синхронізації
- Налаштування політик синхронізації (auto-sync, self-heal, prune)
- Використання ApplicationSet для мультикластерного та мульти-тенентного розгортання
- Впровадження патерна App-of-Apps
- Налаштування RBAC за допомогою проєктів та ролей
- Управління мультикластерними розгортаннями

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [GitOps 3.1](../../platform/disciplines/delivery-automation/gitops/module-3.1-what-is-gitops/) | Що таке GitOps? 4 принципи OpenGitOps | Пряма |
| [GitOps 3.6](../../platform/disciplines/delivery-automation/gitops/module-3.6-multi-cluster/) | Мультикластерний GitOps | Пряма |
| [GitOps Toolkit 2.1](/uk/platform/toolkits/cicd-delivery/source-control/module-11.1-gitlab/) | Практичний ArgoCD, ApplicationSet, App-of-Apps | Пряма |

---

## Домен 3: Argo Rollouts (18%)

### Компетенції
- Налаштування стратегій розгортання Canary та Blue-Green
- Написання AnalysisTemplates для автоматичного відкату (rollback)
- Інтеграція з провайдерами управління трафіком (Istio, Nginx, ALB)
- Розуміння життєвого циклу CRD Rollout та потоку просування змін

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Argo Rollouts](/uk/linux/foundations/container-primitives/module-2.2-cgroups/) | Canary, blue-green, шаблони аналізу, управління трафіком | Пряма |

---

## Домен 4: Argo Events (12%)

### Компетенції
- Розуміння архітектури EventSource, Sensor та Trigger
- Налаштування джерел подій (webhook, S3, Kafka, GitHub, cron тощо)
- Написання сенсорів (Sensors) з фільтрами подій та залежностями
- Тригери Argo Workflows, ресурсів K8s або HTTP ендпоінтів на основі подій

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Argo Events](/uk/cloud/enterprise-hybrid/module-10.2-governance/) | EventSource, Sensor, EventBus, архітектура тригерів | Пряма |

---

## Стратегія підготовки

```
ШЛЯХ ПІДГОТОВКИ ДО CAPA (рекомендований порядок)
══════════════════════════════════════════════════════════════

Тиждень 1-2: Основи GitOps та Argo CD (34% іспиту!)
├── Модулі дисципліни GitOps 3.1-3.6 (теорія)
├── Модуль ArgoCD toolkit (практика)
├── Фокус: Application CRD, політики синхронізації, ApplicationSet
└── Практика: Деплой додатків, авто-синхронізація, налаштування RBAC

Тиждень 3-4: Argo Workflows (36% іспиту!)
├── Модуль Argo Workflows toolkit (практика)
├── Модуль "Advanced Argo Workflows" (усі 7 типів шаблонів)
└── Практика: Побудова DAG, передача артефактів, CronWorkflow

Тиждень 5: Argo Rollouts (18%)
├── Модуль Argo Rollouts toolkit (практика)
├── Фокус: Canary vs. Blue-Green, AnalysisTemplate
└── Практика: Деплой canary з аналізом метрик Prometheus

Тиждень 6: Argo Events (12%) + Рецензія
├── Модуль Argo Events (теорія та практика)
├── Практика: Налаштування конвеєра webhook -> sensor -> workflow
└── Повторення: Перегляд усіх CRD та їхніх полів
```

---

## Поради для іспиту

- **Це теоретичний іспит** — терміналу не буде, але практичний досвід допоможе швидше розуміти питання.
- **Argo Workflows + Argo CD = 70% іспиту** — інвестуйте сюди найбільше часу.
- **Знайте поля CRD** — іспит перевіряє, чи розумієте ви, що робить кожне поле специфікації (наприклад, `selfHeal` vs. `prune`).
- **Типи шаблонів мають значення** — очікуйте питань, що розрізняють 7 типів шаблонів Argo Workflows.
- **Генератори ApplicationSet** — знайте всі типи генераторів (особливо list, cluster, git, matrix).
- **Архітектура Argo Events** — розумійте потік EventSource -> EventBus -> Sensor -> Trigger.

---

## Пов'язані сертифікації

```
ШЛЯХ СЕРТИФІКАЦІЇ ARGO & GITOPS
══════════════════════════════════════════════════════════════

Associate Рівень:
├── KCNA (Cloud Native Associate) — Основи K8s
└── CAPA (Argo Project Associate) ← ВИ ТУТ

Professional Рівень:
├── CKAD (K8s Developer) — Розгортання застосунків
└── CNPE (Platform Engineer) — Платформна інженерія (багато Argo CD)
```

CAPA ідеально підходить для **Platform Engineers**, оскільки екосистема Argo є ключовою для побудови сучасних IDP та конвеєрів доставки.
