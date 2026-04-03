---
title: "KCA — Сертифікований спеціаліст із Kyverno"
sidebar:
  order: 1
  label: "KCA"
---
> **Іспит із множинним вибором** | 90 хвилин | Прохідний бал: 75% | $250 USD | **Сертифікація CNCF**

## Огляд

KCA (Kyverno Certified Associate) підтверджує знання Kyverno — нативного для Kubernetes двигуна політик. Це **теоретичний іспит** — питання з множинним вибором, що перевіряють ваше розуміння того, як писати, тестувати та впроваджувати політики як код (policy-as-code) для безпеки, автоматизації та відповідності вимогам.

**KubeDojo охоплює ~95% тем KCA** через існуючий модуль Kyverno та два спеціалізовані модулі KCA, що охоплюють просунуту конфігурацію та роботу з CLI.

> **Kyverno є стандартом для політик Kubernetes.** На відміну від OPA, він використовує нативний YAML Kubernetes, що робить його надзвичайно популярним серед платформних команд. KCA підтверджує вашу здатність автоматизувати управління кластерами за допомогою політик.

---

## Модулі, специфічні для KCA

Ці модулі охоплюють сфери між загальними знаннями безпеки та вимогами іспиту KCA:

| # | Модуль | Тема | Охоплені домени |
|---|--------|-------|-----------------|
| 1 | [Просунуті політики Kyverno](module-1.1-advanced-kyverno-policies/) | verifyImages (Cosign), CEL вирази (Kubernetes 1.30+), політики очищення (cleanup), складні мутації | Домени 4-5 |
| 2 | [Операції Kyverno та CLI](module-1.2-kyverno-operations-cli/) | Команди `kyverno apply/test/jp`, звіти про політики (PolicyReports), виключення (exceptions), висока доступність (HA) | Домени 2-3, 6 |

---

## Домени іспиту

| Домен | Вага | Охоплення в KubeDojo |
|--------|--------|-------------------|
| Основи Policy-as-Code | 18% | Відмінне ([DevSecOps 4.5](../../platform/disciplines/reliability-security/devsecops/module-4.5-policy-as-code/)) |
| Архітектура та Встановлення | 18% | Відмінне ([Security Tools 4.7](../../platform/toolkits/security-quality/security-tools/module-4.7-kyverno/)) |
| Kyverno CLI | 12% | Відмінне ([Kyverno Operations & CLI](module-1.2-kyverno-operations-cli/)) |
| Застосування політик | 10% | Відмінне ([Security Tools 4.7](../../platform/toolkits/security-quality/security-tools/module-4.7-kyverno/)) |
| Написання політик | 32% | Відмінне ([Просунуті політики Kyverno](module-1.1-advanced-kyverno-policies/)) |
| Управління політиками | 10% | Відмінне ([Kyverno Operations & CLI](module-1.2-kyverno-operations-cli/)) |

---

## Домен 1: Основи Policy-as-Code (18%)

### Компетенції
- Розуміння концепції Policy-as-Code та її переваг
- Роль Admission Controllers у Kubernetes
- Відмінність між валідацією, мутацією та генерацією ресурсів
- Дотримання Pod Security Standards (PSS) через політики

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [DevSecOps 4.5](../../platform/disciplines/reliability-security/devsecops/module-4.5-policy-as-code/) | Філософія Policy-as-Code | Пряма |
| [Security Principles 4.4](../../platform/foundations/security-principles/module-4.4-secure-by-default/) | Безпека за замовчуванням та guardrails | Контекст |

---

## Домен 2: Архітектура та Встановлення (18%)

### Компетенції
- Компоненти Kyverno (Deployment, Webhooks, CRDs)
- Встановлення через Helm з кастомними значеннями
- Налаштування високої доступності (HA mode)
- Розуміння Admission Webhooks (Validating та Mutating)

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Security Tools 4.7](../../platform/toolkits/security-quality/security-tools/module-4.7-kyverno/) | Архітектура та встановлення Kyverno | Пряма |
| [Kyverno Operations & CLI](module-1.2-kyverno-operations-cli/) | HA розгортання таWebhook конфігурація | Пряма |

---

## Домен 3: Kyverno CLI (12%)

### Компетенції
- Використання `kyverno apply` для локального тестування
- Використання `kyverno test` для автоматизованих наборів тестів
- Налагодження через `kyverno jp` (JMESPath запити)
- Інтеграція CLI у конвеєри CI/CD

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Kyverno Operations & CLI](module-1.2-kyverno-operations-cli/) | Повний розбір команд CLI та тестів | Пряма |
| [CKS 5.3](../../k8s/cks/part5-supply-chain-security/module-5.3-static-analysis/) | Концепції статичного аналізу перед деплоєм | Контекст |

---

## Домен 4: Застосування політик (10%)

### Компетенції
- Вибір ресурсів через блоки `match` та `exclude`
- Таргетування за типом ресурсу, простором імен, мітками та анотаціями
- Використання Preconditions для умовного виконання політик
- Порядок виконання та вирішення конфліктів

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Security Tools 4.7](../../platform/toolkits/security-quality/security-tools/module-4.7-kyverno/) | match/exclude, вибір ресурсів | Пряма |
| [OPA & Gatekeeper 4.2](../../platform/toolkits/security-quality/security-tools/module-4.2-opa-gatekeeper/) | Селектори обмежень (порівняння) | Контекст |

---

## Домен 5: Написання політик (32%)

> **Це найбільший домен.** Вимагає глибокої практичної роботи.

### Компетенції
- Написання **validate** правил (відмова невідповідним ресурсам)
- Написання **mutate** правил (авто-виправлення при деплої)
- Написання **generate** правил (авто-створення допоміжних ресурсів)
- Написання **verifyImages** правил (підписи та атестації образів)
- Використання **CEL виразів** (альтернатива JMESPath у K8s 1.30+)
- Написання **cleanup політик** (видалення ресурсів за часом TTL)

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Security Tools 4.7](../../platform/toolkits/security-quality/security-tools/module-4.7-kyverno/) | Validate, mutate, generate з прикладами | Пряма |
| [Просунуті політики Kyverno](module-1.1-advanced-kyverno-policies/) | verifyImages, CEL вирази, cleanup, складні патерни | Пряма |
| [Supply Chain Security 4.4](../../platform/toolkits/security-quality/security-tools/module-4.4-supply-chain/) | Cosign, підписи образів (контекст verifyImages) | Пряма |

---

## Домен 6: Управління політиками (10%)

### Компетенції
- Читання та інтерпретація PolicyReports та ClusterPolicyReports
- Налаштування виключень (PolicyExceptions) для легітимних обходів
- Моніторинг Kyverno через метрики Prometheus
- Життєвий цикл політик (міграція audit -> enforce)

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Security Tools 4.7](../../platform/toolkits/security-quality/security-tools/module-4.7-kyverno/) | Звіти (reports), режим аудиту | Пряма |
| [Kyverno Operations & CLI](module-1.2-kyverno-operations-cli/) | PolicyException CRD, метрики Prometheus | Пряма |

---

## Стратегія підготовки

```
ШЛЯХ ПІДГОТОВКИ ДО KCA (рекомендований порядок)
══════════════════════════════════════════════════════════════

Тиждень 1: Основи та Архітектура (18% + 18%)
├── Модуль Security Tools 4.7 (Kyverno Intro)
├── Модуль DevSecOps 4.5 (Policy-as-Code Theory)
└── Практика: Встановіть Kyverno через Helm у kind кластер

Тиждень 2: Написання базових політик (32% - Частина 1)
├── Практика: Напишіть 10+ валідаційних політик (labels, resources)
├── Практика: Створіть мутаційні політики для додавання default securityContext
└── Вивчіть: Різницю між Enforce та Audit режимами

Тиждень 3: Просунуті функції (32% - Частина 2)
├── Модуль "Просунуті політики Kyverno" (verifyImages, CEL)
├── Практика: Підпишіть образ через Cosign та перевірте його в Kyverno
└── Практика: Створіть ClusterCleanupPolicy для видалення старих подів

Тиждень 4: CLI та Управління (12% + 10%)
├── Модуль "Операції Kyverno та CLI"
├── Практика: Запустіть `kyverno test` для своїх політик
└── Огляд: Перегляд PolicyReports та налаштування виключень
```

---

## Поради для іспиту

- **Validate vs Mutate vs Generate** — Ви ПОВИННІ знати, коли використовувати кожен тип. Validate — для заборони, Mutate — для зміни, Generate — для створення нового (наприклад, NetworkPolicy для нового Namespace).
- **JMESPath** — Вивчіть базовий синтаксис змінних `{{ request.object.metadata.name }}`. Це часто перевіряється.
- **Enforce vs Audit** — Питання часто запитують, що станеться з ресурсом у кожному з режимів.
- **CLI Команди** — Знайте різницю між `apply` (одна політика) та `test` (набір тестів).
- **Policy Library** — Ознайомтеся з офіційною бібліотекою політик на [kyverno.io](https://kyverno.io/policies/). Багато питань базуються на стандартних прикладах.

---

## Пов'язані сертифікації

```
ШЛЯХ СЕРТИФІКАЦІЇ
══════════════════════════════════════════════════════════════

Associate Рівень:
├── KCNA (Cloud Native Associate) — Основи
├── KCSA (Security Associate) — Безпека
└── KCA (Kyverno Associate) ← ВИ ТУТ

Professional Рівень:
├── CKS (K8s Security Specialist) — Глибока безпека (Kyverno — чудовий інструмент для CKS)
└── CNPE (Platform Engineer) — Політики є ключем до самообслуговування
```

KCA фокусується на конкретному інструменті, що робить його дуже практичним для **Platform Engineers** та **DevSecOps** фахівців.
