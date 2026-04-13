---
title: "OTCA — Сертифікований спеціаліст із OpenTelemetry"
sidebar:
  order: 1
  label: "OTCA"
---
> **Іспит із множинним вибором** | 90 хвилин | Прохідний бал: 75% | $250 USD | **Сертифікація CNCF**

## Огляд

OTCA (OpenTelemetry Certified Associate) підтверджує знання стандарту OpenTelemetry (OTel), його архітектури, API, SDK та Collector. Це **теоретичний іспит** — питання з множинним вибором, які перевіряють ваше розуміння того, як OTel уніфікує збір метрик, логів та трасувань.

**KubeDojo охоплює ~90% тем OTCA** через існуючі модулі спостережуваності та інструментарій OTel, плюс один спеціалізований модуль OTCA, що охоплює конфігурацію Collector та специфікації OTLP.

> **OpenTelemetry є стандартом де-факто для інструментування.** Це другий за активністю проєкт у CNCF (після Kubernetes). OTCA підтверджує ваше володіння уніфікованим рівнем телеметрії, який працює з будь-яким бекендом (Prometheus, Jaeger, Honeycomb, Datadog тощо).

---

## Модулі, специфічні для OTCA

Цей модуль заповнює прогалину між загальним моніторингом та глибиною OTel:

| # | Модуль | Тема | Охоплені домени |
|---|--------|-------|-----------------|
| 1 | [Глибоке занурення в OpenTelemetry](module-1.1-opentelemetry-deep-dive/) | OTLP специфікація, архітектура Collector (receivers, processors, exporters), Context Propagation (W3C), Resource Attributes, Semantic Conventions | Домени 1-5 |

---

## Домени іспиту

| Домен | Вага | Охоплення в KubeDojo |
|--------|--------|-------------------|
| Основи Спостережуваності | 15% | Відмінне ([Foundations 3.1-3.2](../../platform/foundations/observability-theory/)) |
| Архітектура OpenTelemetry | 25% | Відмінне ([Глибоке занурення в OTel](module-1.1-opentelemetry-deep-dive/)) |
| OpenTelemetry Collector | 30% | Відмінне ([Observability Toolkit 1.2](../../platform/toolkits/observability-intelligence/observability/module-1.2-opentelemetry/)) |
| Інструментування (SDK & API) | 20% | Відмінне ([Foundations 3.3](/uk/k8s/kcna/part3-cloud-native-architecture/module-3.1-cloud-native-principles/)) |
| Впровадження та Екосистема | 10% | Відмінне ([Глибоке занурення в OTel](module-1.1-opentelemetry-deep-dive/)) |

---

## Домен 1: Основи Спостережуваності (15%)

### Компетенції
- Розуміння Трьох Стовпів: Метрики, Траси, Логи
- Концепція "Події" (Event) як першоджерела
- Чому OTel виник як злиття OpenTracing та OpenCensus
- Переваги вендор-нейтрального інструментування

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Foundations 3.1](../../platform/foundations/observability-theory/module-3.1-what-is-observability/) | Що таке спостережуваність? | Пряма |
| [Foundations 3.2](../../platform/foundations/observability-theory/module-3.2-the-three-pillars/) | Три стовпи телеметрії | Пряма |

---

## Домен 2: Архітектура OpenTelemetry (25%)

### Компетенції
- Розуміння OTLP (OpenTelemetry Protocol)
- Поняття Resource (метадані про джерело телеметрії)
- Semantic Conventions: стандартизовані імена тегів (labels)
- Контекст та прокидання контексту (Context Propagation)
- W3C Trace Context стандарт

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Глибоке занурення в OTel](module-1.1-opentelemetry-deep-dive/) | Протоколи, ресурси та атрибути | Пряма |
| [Foundations 3.3](/uk/k8s/kcna/part3-cloud-native-architecture/module-3.1-cloud-native-principles/) | Принципи інструментування | Пряма |

---

## Домен 3: OpenTelemetry Collector (30%)

### Компетенції
- Архітектура Collector: Receivers, Processors, Exporters, Extensions
- Конфігурація через YAML конвеєри (Pipelines)
- Розгортання: Agent vs. Gateway режими
- Обробка даних: фільтрація, збагачення атрибутами, семплювання (sampling)
- Налаштування OTLP ендпоінтів

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Observability Toolkit 1.2](../../platform/toolkits/observability-intelligence/observability/module-1.2-opentelemetry/) | Практична конфігурація Collector | Пряма |
| [Глибоке занурення в OTel](module-1.1-opentelemetry-deep-dive/) | Просунуті процесори та Gateway архітектура | Пряма |

---

## Домен 4: Інструментування (SDK & API) (20%)

### Компетенції
- Різниця між OTel API (код розробника) та SDK (реалізація)
- Авто-інструментування (Java Agents, JS Wrappers, Python wrappers)
- Ручне інструментування: створення Span, додавання подій (Attributes & Events)
- Життєвий цикл Span: Start, End, Status
- Налаштування Providers та Exporters в коді

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Foundations 3.3](/uk/k8s/kcna/part3-cloud-native-architecture/module-3.1-cloud-native-principles/) | Що вимірювати та як? | Пряма |
| [Глибоке занурення в OTel](module-1.1-opentelemetry-deep-dive/) | Практичні приклади SDK для різних мов | Пряма |

---

## Домен 5: Впровадження та Екосистема (10%)

### Компетенції
- Сумісність з Prometheus (Prometheus Exporter/Receiver)
- Сумісність з Jaeger та Zipkin
- Статус стабільності компонентів OTel (Signals stability)
- Роль OTel у хмарних провайдерах

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [Observability Toolkit 1.1](../../platform/toolkits/observability-intelligence/observability/module-1.1-prometheus/) | Інтеграція OTel з Prometheus | Контекст |
| [Observability Toolkit 1.5](../../platform/toolkits/observability-intelligence/observability/module-1.5-tracing/) | OTel та Jaeger/Tempo | Пряма |

---

## Стратегія підготовки

```
ШЛЯХ ПІДГОТОВКИ ДО OTCA (рекомендований порядок)
══════════════════════════════════════════════════════════════

Тиждень 1: Теорія та Архітектура (40%)
├── Модулі Foundations 3.1 - 3.3
├── Модуль "Глибоке занурення в OTel" (Контекст & OTLP)
└── Вивчіть: Різницю між API та SDK

Тиждень 2: OTel Collector (30%)
├── Модуль Observability Toolkit 1.2
├── Практика: Налаштуйте конвеєр: OTLP Receiver -> Batch Processor -> Logging Exporter
└── Вивчіть: Режими Agent та Gateway

Тиждень 3: Інструментування (20%)
├── Практика: Запустіть авто-інструментування для Python або Java застосунку
├── Додайте ручні атрибути до Span
└── Вивчіть: Semantic Conventions (стандарти іменування)

Тиждень 4: Екосистема та Рецензія (10%)
├── Огляд: Як OTel працює з Prometheus та Jaeger
└── Тести: Перевірте знання про W3C Traceparent формат
```

---

## Поради для іспиту

- **API vs SDK** — Це ключове розмежування. API стабільне і використовується в коді застосунку, SDK налаштовується в точці входу (main).
- **Receivers/Processors/Exporters** — Знайте структуру YAML конфігурації Collector. Exporters надсилають дані, Receivers отримують.
- **Trace Context** — Розумійте `traceparent` заголовок W3C (TraceID, SpanID, Flags).
- **Sampling** — Знайте різницю між Head-based (на старті) та Tail-based (на виході) семплюванням.
- **OTLP** — Знайте, що це нативний протокол OTel, який працює поверх gRPC або HTTP.

---

## Пов'язані сертифікації

```
ШЛЯХ СЕРТИФІКАЦІЇ
══════════════════════════════════════════════════════════════

Associate Рівень:
├── KCNA (Cloud Native Associate) — База
├── PCA (Prometheus Associate) — Метрики
└── OTCA (OpenTelemetry Associate) ← ВИ ТУТ

Professional Рівень:
├── CNPE (Platform Engineer) — OTel є стандартом для IDP
└── CKA/CKAD — Спостережуваність є частиною екзамену
```

OTCA — це найсучасніша сертифікація для **SRE** та **Platform Engineers**, що працюють з телеметрією у мультихмарних середовищах.
