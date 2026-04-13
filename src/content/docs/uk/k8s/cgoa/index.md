---
title: "CGOA — Сертифікований спеціаліст із GitOps"
sidebar:
  order: 1
  label: "CGOA"
---
> **Іспит із множинним вибором** | 90 хвилин | Прохідний бал: 75% | $250 USD | **Сертифікація CNCF**

## Огляд

CGOA (Certified GitOps Associate) підтверджує знання принципів, термінології та практик GitOps. Це **іспит на знання** — питання з множинним вибором, які перевіряють ваше розуміння того, як GitOps змінює життєвий цикл доставки ПЗ. Хоча він не вимагає написання коду, ви повинні розуміти, як працюють інструменти типу ArgoCD та Flux на концептуальному рівні.

**KubeDojo охоплює ~100% тем CGOA** через комплексну дисципліну GitOps та відповідні набори інструментів.

> **GitOps — це майбутнє операцій Kubernetes.** Це практика використання Git як єдиного джерела істини для інфраструктури. CGOA підтверджує, що ви розумієте не просто інструменти, а філософію "Operations by Pull Request", яка робить хмарні системи масштабованими та безпечними.

---

## Домени іспиту

| Домен | Вага | Охоплення в KubeDojo |
|--------|--------|-------------------|
| Основи GitOps | 20% | Відмінне ([GitOps 3.1](../../platform/disciplines/delivery-automation/gitops/module-3.1-what-is-gitops/)) |
| Принципи GitOps | 30% | Відмінне ([GitOps 3.1](../../platform/disciplines/delivery-automation/gitops/module-3.1-what-is-gitops/)) |
| Робочі процеси (Workflows) | 35% | Відмінне ([GitOps 3.2-3.4](../../platform/disciplines/delivery-automation/gitops/)) |
| Інструментарій та екосистема | 15% | Відмінне ([GitOps Toolkit](../../platform/toolkits/cicd-delivery/gitops-deployments/)) |

---

## Домен 1: Основи GitOps (20%)

### Компетенції
- Розуміння походження GitOps та його зв'язку з DevOps та IaC
- Відмінність між моделями Pull та Push
- Роль контролю версій як "Source of Truth"
- Переваги декларативного опису системи

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [GitOps 3.1](../../platform/disciplines/delivery-automation/gitops/module-3.1-what-is-gitops/) | Що таке GitOps? Історія та Pull vs Push | Пряма |
| [IaC 6.1](../../platform/disciplines/delivery-automation/iac/module-6.1-iac-fundamentals/) | Основи IaC — декларативність та ідемпотентність | Пряма |

---

## Домен 2: Принципи GitOps (30%)

### Компетенції
- **Чотири принципи OpenGitOps** (Декларативність, Версіонованість, Pull, Узгодження)
- Розуміння петлі узгодження (Reconciliation loop)
- Концепція дрейфу конфігурації (Configuration drift) та його виправлення
- Ідемпотентність та незмінність (Immutability)

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [GitOps 3.1](../../platform/disciplines/delivery-automation/gitops/module-3.1-what-is-gitops/) | Детальний розбір 4-х принципів OpenGitOps | Пряма |
| [GitOps 3.4](/uk/k8s/ckad/part3-observability/module-3.5-api-deprecations/) | Детекція та автоматичне виправлення дрейфу | Пряма |

---

## Домен 3: Робочі процеси (Workflows) (35%)

### Компетенції
- Стратегії репозиторіїв (Monorepo vs. Polyrepo)
- Просування змін між середовищами (Environment promotion)
- Управління секретами у GitOps (SOPS, Sealed Secrets)
- Роль CI в GitOps процесі (Build -> Push image -> Update Git)
- Безпека та комплаєнс (аудит через історію Git)

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [GitOps 3.2](../../platform/disciplines/delivery-automation/gitops/module-3.2-repository-strategies/) | Структури репозиторіїв та папки середовищ | Пряма |
| [GitOps 3.3](/uk/linux/foundations/everyday-use/module-0.2-environment-permissions/) | Патерни просування змін | Пряма |
| [GitOps 3.5](../../platform/disciplines/delivery-automation/gitops/module-3.5-secrets/) | Секрети: SOPS, Sealed Secrets, Vault | Пряма |

---

## Домен 4: Інструментарій та екосистема (15%)

### Компетенції
- Знання основних інструментів: ArgoCD та Flux
- Розуміння ролі Helm та Kustomize у GitOps
- Екосистема CNCF та проєкти OpenGitOps
- Інтеграція з прогресивною доставкою (Argo Rollouts, Flagger)

### Шлях навчання в KubeDojo

| Модуль | Тема | Релевантність |
|--------|-------|-----------|
| [GitOps Toolkit 2.1](/uk/platform/toolkits/cicd-delivery/source-control/module-11.1-gitlab/) | Практичний ArgoCD | Пряма |
| [GitOps Toolkit 2.3](/uk/platform/toolkits/cicd-delivery/source-control/module-11.1-gitlab/) | Практичний Flux | Пряма |
| [GitOps Toolkit 2.2](/uk/linux/foundations/container-primitives/module-2.2-cgroups/) | Прогресивна доставка у GitOps | Пряма |

---

## Стратегія підготовки

```
ШЛЯХ ПІДГОТОВКИ ДО CGOA (рекомендований порядок)
══════════════════════════════════════════════════════════════

Тиждень 1: Теорія та Принципи (50%)
├── Модуль GitOps 3.1 (Основи та 4 Принципи)
├── Модуль IaC 6.1 (Декларативність)
└── Вивчіть: Чому Pull краще за Push для безпеки?

Тиждень 2: Практичні процеси (35%)
├── Модулі GitOps 3.2 - 3.4 (Репо, Просування, Дрейф)
├── Модуль GitOps 3.5 (Секрети)
└── Огляд: Як виглядає CI/CD конвеєр у світі GitOps?

Тиждень 3: Інструменти (15%)
├── Модулі ArgoCD та Flux (хоча б концептуально)
├── Вивчіть: Різниця між Helm чартами та Kustomize overlays
└── Огляд: Що таке OpenGitOps та хто в нього входить?
```

---

## Поради для іспиту

- **Запам'ятайте 4 принципи OpenGitOps** — Це фундамент іспиту. Знайте їх напам'ять.
- **Pull vs Push** — Розумійте переваги Pull моделі (немає креденшалів у CI, автоматичне виправлення дрейфу).
- **Дрейф (Drift)** — Знайте, що це таке і як GitOps інструменти (ArgoCD/Flux) реагують на нього.
- **Секрети** — Розумійте, що секрети НЕ мають зберігатися у відкритому вигляді в Git. Знайте методи шифрування.
- **Аудит** — Git історія є вашим логом аудиту. Хто, що і коли змінив — все є в Git.

---

## Пов'язані сертифікації

```
ШЛЯХ СЕРТИФІКАЦІЇ
══════════════════════════════════════════════════════════════

Associate Рівень:
├── KCNA (Cloud Native Associate) — База
├── PCA (Prometheus Associate) — Моніторинг
└── CGOA (GitOps Associate) ← ВИ ТУТ

Professional Рівень:
├── CKAD (K8s Developer) — Деплой (GitOps допомагає!)
└── CNPE (Platform Engineer) — GitOps є ядром дисципліни
```

CGOA є обов'язковим для майбутніх **Platform Engineers**, оскільки GitOps є стандартом де-факто для управління сучасними платформами.
