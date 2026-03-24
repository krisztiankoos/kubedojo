# Модуль 4.6: Custom Resource Definitions (CRDs)

> **Складність**: `[MEDIUM]` — Нове у CKAD 2025, важливе концептуальне розуміння
>
> **Час на виконання**: 35–45 хвилин
>
> **Передумови**: Розуміння ресурсів Kubernetes та структури API

---

## Чому цей модуль важливий

Custom Resource Definitions розширюють Kubernetes власними типами ресурсів. Замість того, щоб працювати лише з подами, сервісами та Deployments, ви можете визначити ресурси на кшталт `Database`, `Certificate` або `BackupJob`, які мають сенс для вашого домену.

На іспиті CKAD (2025) перевіряють:
- Розуміння того, що таке CRDs
- Роботу з власними ресурсами
- Використання `kubectl` для взаємодії з CR
- Розпізнавання патернів Operator

> **Аналогія з формами документів**
>
> Вбудовані ресурси Kubernetes — це як стандартні державні форми — усі використовують однакову форму Під, однакову форму Сервіс. CRDs — це як створення власної форми для вашої організації. Ви визначаєте, які поля вона має (`spec`), а Kubernetes зберігає та валідує її. Оператори — це як автоматизовані клерки, що стежать за цими формами та виконують дії, коли вони подані.

---

## Основи CRD

### Що таке CRD?

**Custom Resource Definition (CRD)** повідомляє Kubernetes про новий тип ресурсу:

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databases.example.com    # формат plural.group
spec:
  group: example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              engine:
                type: string
              size:
                type: string
  scope: Namespaced
  names:
    plural: databases
    singular: database
    kind: Database
    shortNames:
    - db
```

### Що таке Custom Resource (CR)?

Після створення CRD ви можете створювати екземпляри — Custom Resources:

```yaml
apiVersion: example.com/v1
kind: Database
metadata:
  name: my-database
spec:
  engine: postgres
  size: large
```

---

## Компоненти CRD

### Назви

```yaml
names:
  plural: databases      # Використовується в URL: /apis/example.com/v1/databases
  singular: database     # Використовується в CLI: kubectl get database
  kind: Database         # Використовується в YAML: kind: Database
  shortNames:
  - db                   # Скорочення: kubectl get db
```

### Область видимості

```yaml
scope: Namespaced    # Ресурси існують у просторах імен
# або
scope: Cluster       # Ресурси на рівні кластера
```

### Версії

```yaml
versions:
- name: v1
  served: true       # API-сервер обслуговує цю версію
  storage: true      # Зберігати в etcd цією версією (лише одна може бути true)
```

### Валідація схеми

```yaml
schema:
  openAPIV3Schema:
    type: object
    required: ["spec"]
    properties:
      spec:
        type: object
        required: ["engine"]
        properties:
          engine:
            type: string
            enum: ["postgres", "mysql", "mongodb"]
          size:
            type: string
            default: "small"
```

---

## Робота з CRDs

### Перегляд встановлених CRDs

```bash
# Список усіх CRDs
k get crd

# Описати CRD
k describe crd certificates.cert-manager.io

# Отримати YAML CRD
k get crd mycrd.example.com -o yaml
```

### Робота з Custom Resources

```bash
# Список власних ресурсів (після створення CRD)
k get databases
k get db                    # Використовуючи shortName

# Описати CR
k describe database my-database

# Отримати YAML CR
k get database my-database -o yaml

# Видалити CR
k delete database my-database
```

---

## Поширені CRDs, які вам зустрінуться

### cert-manager

```bash
k get crd | grep cert-manager
# certificates.cert-manager.io
# clusterissuers.cert-manager.io
# issuers.cert-manager.io

# Створити Certificate
k get certificates
k describe certificate my-cert
```

### Prometheus Operator

```bash
k get crd | grep monitoring
# servicemonitors.monitoring.coreos.com
# prometheusrules.monitoring.coreos.com
```

### Gateway API

```bash
k get crd | grep gateway
# gateways.gateway.networking.k8s.io
# httproutes.gateway.networking.k8s.io
```

---

## Патерн Operator

### Що таке Operator?

**Operator** = CRD + Контролер

- **CRD**: Визначає «що» (структура власного ресурсу)
- **Контролер**: Обробляє «як» (стежить за CR та виконує дії)

```
┌─────────────────────────────────────────────────────────────┐
│                     Патерн Operator                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Користувач створює Custom Resource                      │
│  ┌─────────────────────────────────┐                       │
│  │ apiVersion: example.com/v1      │                       │
│  │ kind: Database                  │                       │
│  │ spec:                           │                       │
│  │   engine: postgres              │                       │
│  └─────────────────────────────────┘                       │
│                    │                                        │
│                    ▼                                        │
│  2. Контролер стежить за Database CR                       │
│  ┌─────────────────────────────────┐                       │
│  │ Під оператора                   │                       │
│  │ - Бачить новий Database CR      │                       │
│  │ - Створює StatefulSet           │                       │
│  │ - Створює Service               │                       │
│  │ - Створює Secret (пароль)       │                       │
│  │ - Оновлює статус CR             │                       │
│  └─────────────────────────────────┘                       │
│                    │                                        │
│                    ▼                                        │
│  3. Створені фактичні ресурси                              │
│  ┌─────────────────────────────────┐                       │
│  │ StatefulSet: my-database        │                       │
│  │ Service: my-database            │                       │
│  │ Secret: my-database-creds       │                       │
│  └─────────────────────────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Навіщо використовувати Operators?

| Перевага | Приклад |
|----------|---------|
| Абстракція | Створіть `Database`, оператор обробить StatefulSet, PVC тощо |
| Автоматизація | Оператор обробляє резервні копії, відмовостійкість, масштабування |
| Експертиза домену | Оператор знає, як правильно налаштувати Postgres |
| Операції другого дня | Оновлення, відновлення, моніторинг вбудовані |

---

## kubectl explain з CRDs

```bash
# Працює і для CRDs (якщо встановлені)
k explain database
k explain database.spec
k explain certificate.spec.secretName
```

---

## Швидка довідка

```bash
# Список CRDs
k get crd

# Переглянути деталі CRD
k describe crd NAME

# Робота з власними ресурсами
k get <resource>
k describe <resource> NAME
k delete <resource> NAME

# Отримати ресурси API (включаючи CRDs)
k api-resources | grep example.com

# Перевірити, чи CRD існує
k get crd myresource.example.com
```

---

## Візуалізація

```
┌─────────────────────────────────────────────────────────────┐
│            CRD створює нову точку доступу API               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  До CRD:                                                    │
│  ┌─────────────────────────────────┐                       │
│  │ /api/v1/pods                    │                       │
│  │ /api/v1/services                │                       │
│  │ /apis/apps/v1/deployments       │                       │
│  └─────────────────────────────────┘                       │
│                                                             │
│  Після CRD (group: example.com, plural: databases):        │
│  ┌─────────────────────────────────┐                       │
│  │ /api/v1/pods                    │                       │
│  │ /api/v1/services                │                       │
│  │ /apis/apps/v1/deployments       │                       │
│  │ /apis/example.com/v1/databases  │  ← НОВЕ!              │
│  └─────────────────────────────────┘                       │
│                                                             │
│  Команди kubectl тепер працюють:                            │
│  $ k get databases                                         │
│  $ k describe database my-db                               │
│  $ k delete database my-db                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Чи знали ви?

- **CRDs самі по собі є ресурсом Kubernetes.** Група `apiextensions.k8s.io/v1` визначає, як створювати власні ресурси.

- **Видалення CRD видаляє всі його Custom Resources.** Будьте обережні! `kubectl delete crd databases.example.com` видаляє всі CR типу Database.

- **CRDs підтримують кілька версій.** Ви можете одночасно обслуговувати v1alpha1, v1beta1 та v1 для плавної міграції.

- **Найпопулярніші проєкти Kubernetes — це Operators.** Prometheus, cert-manager, ArgoCD, Istio — усі активно використовують CRDs.

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| Плутати CRD з CR | CRD — це визначення, CR — екземпляр | CRD = шаблон, CR = фактичний ресурс |
| Випадкове видалення CRD | Видаляє також усі CR | Перевірте двічі перед видаленням CRDs |
| Не перевіряти наявність CRD | Команди kubectl не спрацюють | Спочатку `k get crd NAME` |
| Думати, що CRDs самі щось роблять | CRDs лише зберігають дані | Потрібен контролер/оператор для дій |
| Неправильне використання plural/singular | Команди kubectl не спрацюють | Перевірте `k api-resources` для правильних назв |

---

## Тест

1. **Яка різниця між CRD та Custom Resource?**
   <details>
   <summary>Відповідь</summary>
   CRD (Custom Resource Definition) визначає новий тип ресурсу (як схема). Custom Resource (CR) — це екземпляр цього типу (фактичні дані). CRD — це визначення, CR — об'єкт, створений з нього.
   </details>

2. **Що відбувається при видаленні CRD?**
   <details>
   <summary>Відповідь</summary>
   Усі Custom Resources цього типу також видаляються. Це каскадне видалення.
   </details>

3. **Що таке Operator?**
   <details>
   <summary>Відповідь</summary>
   Operator — це патерн, що поєднує CRD з контролером. CRD визначає структуру ресурсу, а контролер стежить за CR та виконує автоматичні дії (створення подів, керування станом тощо).
   </details>

4. **Як переглянути список усіх CRDs у кластері?**
   <details>
   <summary>Відповідь</summary>
   `kubectl get crd` або `kubectl get customresourcedefinitions`
   </details>

---

## Практична вправа

**Завдання**: Працювати з CRD та Custom Resources.

**Частина 1: Створення CRD**
```bash
cat << 'EOF' | k apply -f -
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: websites.example.com
spec:
  group: example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              domain:
                type: string
              replicas:
                type: integer
  scope: Namespaced
  names:
    plural: websites
    singular: website
    kind: Website
    shortNames:
    - ws
EOF

# Перевірити створення CRD
k get crd websites.example.com
```

**Частина 2: Створення Custom Resources**
```bash
cat << 'EOF' | k apply -f -
apiVersion: example.com/v1
kind: Website
metadata:
  name: my-blog
spec:
  domain: blog.example.com
  replicas: 3
---
apiVersion: example.com/v1
kind: Website
metadata:
  name: my-shop
spec:
  domain: shop.example.com
  replicas: 5
EOF

# Список з різними назвами
k get websites
k get website
k get ws
```

**Частина 3: Перевірка та зміна**
```bash
# Описати
k describe website my-blog

# Отримати YAML
k get ws my-blog -o yaml

# Редагувати
k edit website my-blog
# Змініть replicas на 2
```

**Частина 4: Дослідження API**
```bash
# Перевірити ресурси API
k api-resources | grep example.com

# Використати explain
k explain website
```

**Очищення:**
```bash
k delete website my-blog my-shop
k delete crd websites.example.com
```

---

## Практичні вправи

### Вправа 1: Список CRDs (Ціль: 1 хвилина)

```bash
# Список усіх CRDs
k get crd

# Підрахувати CRDs
k get crd --no-headers | wc -l
```

### Вправа 2: Описати CRD (Ціль: 1 хвилина)

```bash
# Якщо cert-manager або подібне встановлено
k describe crd certificates.cert-manager.io 2>/dev/null || echo "cert-manager not installed"

# Інакше використовуйте будь-який CRD
k get crd -o name | head -1 | xargs k describe
```

### Вправа 3: Створити CRD (Ціль: 3 хвилини)

```bash
cat << 'EOF' | k apply -f -
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: backups.drill.example.com
spec:
  group: drill.example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              schedule:
                type: string
              retention:
                type: integer
  scope: Namespaced
  names:
    plural: backups
    singular: backup
    kind: Backup
    shortNames:
    - bk
EOF

k get crd backups.drill.example.com
k delete crd backups.drill.example.com
```

### Вправа 4: Створити та запитати CR (Ціль: 3 хвилини)

```bash
# Спочатку створити CRD
cat << 'EOF' | k apply -f -
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: tasks.drill.example.com
spec:
  group: drill.example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              priority:
                type: string
  scope: Namespaced
  names:
    plural: tasks
    singular: task
    kind: Task
EOF

# Створити CR
cat << 'EOF' | k apply -f -
apiVersion: drill.example.com/v1
kind: Task
metadata:
  name: important-task
spec:
  priority: high
EOF

# Запит
k get tasks
k describe task important-task
k get task important-task -o yaml

# Очищення
k delete task important-task
k delete crd tasks.drill.example.com
```

### Вправа 5: Перевірка ресурсів API (Ціль: 2 хвилини)

```bash
# Список усіх ресурсів API
k api-resources

# Фільтрувати за конкретною групою
k api-resources | grep networking

# Показати лише ресурси на основі CRD (власні)
k api-resources | grep -v "^NAME" | grep "\."
```

### Вправа 6: Використання kubectl explain для CRD (Ціль: 2 хвилини)

```bash
# Створити простий CRD
cat << 'EOF' | k apply -f -
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: configs.drill.example.com
spec:
  group: drill.example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              key:
                type: string
              value:
                type: string
  scope: Namespaced
  names:
    plural: configs
    singular: config
    kind: Config
EOF

# Використати explain
k explain config
k explain config.spec

# Очищення
k delete crd configs.drill.example.com
```

---

## Наступний модуль

[Підсумковий тест частини 4](part4-cumulative-quiz.uk.md) — Перевірте свої знання з тем оточення, конфігурації та безпеки.
