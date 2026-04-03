---
title: "\u041c\u043e\u0434\u0443\u043b\u044c 4.3: \u0412\u0438\u043c\u043e\u0433\u0438 \u0442\u0430 \u043b\u0456\u043c\u0456\u0442\u0438 \u0440\u0435\u0441\u0443\u0440\u0441\u0456\u0432"
slug: uk/k8s/ckad/part4-environment/module-4.3-resources
sidebar: 
  order: 3
lab: 
  id: ckad-4.3-resources
  url: https://killercoda.com/kubedojo/scenario/ckad-4.3-resources
  duration: "30 min"
  difficulty: intermediate
  environment: kubernetes
---
> **Складність**: `[MEDIUM]` — Критично для продакшену, впливає на планування
>
> **Час на виконання**: 35–45 хвилин
>
> **Передумови**: Модуль 1.1 (Поди), розуміння концепцій CPU та пам'яті

---

## Що ви зможете робити

Після завершення цього модуля ви зможете:
- **Налаштувати** запити та ліміти ресурсів для CPU та пам'яті у специфікаціях Підів
- **Діагностувати** проблеми OOMKilled та обмеження CPU, зіставляючи ліміти зі спостережуваною поведінкою
- **Спроєктувати** розподіл ресурсів, що балансує продуктивність, вартість та надійність планування
- **Пояснити** як запити впливають на планування, а ліміти — на обмеження під час виконання

---

## Чому цей модуль важливий

Запити та ліміти ресурсів контролюють, скільки CPU та пам'яті можуть використовувати ваші контейнери. Без них один контейнер може спожити всі ресурси вузла, залишивши інші поди без ресурсів. Належне управління ресурсами є необхідним для стабільності кластера.

На іспиті CKAD перевіряють:
- Встановлення запитів та лімітів
- Розуміння різниці між ними
- Що відбувається при перевищенні лімітів
- LimitRanges та ResourceQuotas

> **Аналогія з орендою квартири**
>
> Запити ресурсів — це як гарантоване паркомісце — вам забезпечено цей простір. Ліміти — це як максимальна місткість будівлі — ви можете тимчасово використовувати більше простору, але є жорстка межа. Якщо ви її перевищите (пам'ять), вас виселять (OOMKilled). Якщо будівля заповнена (вузол), нові мешканці (поди) чекають, поки звільниться місце.

---

## Запити проти лімітів

### Визначення

| Термін | Значення | Коли застосовується |
|--------|----------|---------------------|
| **Запит (Request)** | Гарантований мінімум ресурсів | Під час планування |
| **Ліміт (Limit)** | Максимально дозволені ресурси | Під час виконання |

### Як вони працюють

```
┌─────────────────────────────────────────────────────────────┐
│              Запит ресурсів проти ліміту                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Пам'ять:                                                   │
│  ├── Запит: 256Mi (гарантовано, для планування)             │
│  ├── Фактичне використання може бути від 0 до ліміту       │
│  └── Ліміт: 512Mi (жорстка межа, перевищення = OOMKill)    │
│                                                             │
│  CPU:                                                       │
│  ├── Запит: 100m (гарантовано, для планування)              │
│  ├── Може перевищувати запит, якщо вузол має вільну         │
│  │   потужність                                             │
│  └── Ліміт: 500m (обмежується, якщо перевищено, НЕ вбиває) │
│                                                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │                                                    │     │
│  │  0        Запит       Факт.        Ліміт           │     │
│  │  |           |           |            |            │     │
│  │  ├───────────┼───────────┼────────────┤            │     │
│  │  │гарантовано│  з можл.  │   макс.    │            │     │
│  │  │           │  перевищ. │            │            │     │
│  │  └───────────┴───────────┴────────────┘            │     │
│  │                                                    │     │
│  └────────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Встановлення ресурсів

### Базовий синтаксис

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:
        memory: "256Mi"
        cpu: "100m"
      limits:
        memory: "512Mi"
        cpu: "500m"
```

### Одиниці вимірювання

**CPU:**
| Значення | Опис |
|----------|------|
| `1` | 1 ядро CPU |
| `1000m` | 1000 мілікорів = 1 ядро |
| `500m` | 0.5 ядра |
| `100m` | 0.1 ядра (10%) |

**Пам'ять:**
| Значення | Опис |
|----------|------|
| `128Mi` | 128 мебібайтів (на основі 1024) |
| `1Gi` | 1 гібібайт = 1024 Mi |
| `128M` | 128 мегабайтів (на основі 1000) |
| `1G` | 1 гігабайт = 1000 M |

---

## Що відбувається при досягненні лімітів

### Перевищення ліміту пам'яті

```
Контейнер використовує > ліміту → OOMKilled → Контейнер перезапускається
```

```bash
# Перевірити, чи під був OOMKilled
k describe pod my-pod | grep -A5 "Last State"
k get pod my-pod -o jsonpath='{.status.containerStatuses[0].lastState}'
```

### Перевищення ліміту CPU

```
Контейнер використовує > ліміту → Обмежується (сповільнюється, НЕ вбивається)
```

Обмеження CPU непомітне для контейнера — він просто працює повільніше.

---

## Класи QoS

Kubernetes призначає класи якості обслуговування на основі налаштувань ресурсів:

| Клас QoS | Умова | Пріоритет витіснення |
|----------|-------|----------------------|
| **Guaranteed** | Запити = Ліміти для всіх контейнерів | Останній (захищений) |
| **Burstable** | Запити < Ліміти (або встановлено лише одне) | Середній |
| **BestEffort** | Запити та ліміти не встановлені | Перший (витісняється першим) |

### Приклад Guaranteed

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"    # Те саме, що запит
    cpu: "100m"        # Те саме, що запит
```

### Приклад Burstable

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"    # Більше за запит
    cpu: "500m"        # Більше за запит
```

### Приклад BestEffort

```yaml
resources: {}  # Ресурси не визначені
```

---

## Вплив на планування

### Під не планується

Якщо жоден вузол не має достатньо **доступних** ресурсів (ємність - виділені запити):

```bash
# Перевірити, чому під у стані Pending
k describe pod my-pod

# В подіях буде:
# 0/3 nodes are available: 3 Insufficient cpu.
# або
# 0/3 nodes are available: 3 Insufficient memory.
```

### Перевірка ємності вузла

```bash
# Ємність та доступні ресурси вузла
k describe node NODE_NAME | grep -A5 Capacity
k describe node NODE_NAME | grep -A5 Allocatable

# Вже виділені ресурси
k describe node NODE_NAME | grep -A10 "Allocated resources"
```

---

## LimitRange

Стандартні значення та обмеження на рівні простору імен:

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: cpu-memory-limits
spec:
  limits:
  - default:          # Ліміти за замовчуванням, якщо не вказано
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:   # Запити за замовчуванням, якщо не вказано
      cpu: "100m"
      memory: "256Mi"
    max:              # Максимально дозволено
      cpu: "2"
      memory: "2Gi"
    min:              # Мінімально дозволено
      cpu: "50m"
      memory: "64Mi"
    type: Container
```

```bash
# Переглянути LimitRange
k get limitrange
k describe limitrange cpu-memory-limits
```

---

## ResourceQuota

Загальні обмеження ресурсів на рівні простору імен:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
spec:
  hard:
    requests.cpu: "4"
    requests.memory: "8Gi"
    limits.cpu: "8"
    limits.memory: "16Gi"
    pods: "10"
```

```bash
# Переглянути використання квоти
k get resourcequota
k describe resourcequota compute-quota
```

---

## Швидка довідка

```bash
# Встановити ресурси в специфікації пода
resources:
  requests:
    cpu: "100m"
    memory: "256Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"

# Перевірити ресурси пода
k get pod POD -o jsonpath='{.spec.containers[*].resources}'

# Перевірити ємність вузла
k describe node NODE | grep -A10 "Allocated"

# Перевірити клас QoS
k get pod POD -o jsonpath='{.status.qosClass}'
```

---

## Чи знали ви?

- **CPU — стисливий ресурс, пам'ять — ні.** Якщо ви перевищите ліміт CPU, вас обмежать. Якщо ви перевищите ліміт пам'яті, вас вб'ють.

- **Запити впливають на планування, ліміти — на час виконання.** Під із запитом пам'яті 1Gi не буде заплановано на вузлі, де доступно лише 512Mi, навіть якщо контейнер використовує лише 100Mi.

- **Kubernetes не запобігає перевищенню пам'яті.** Якщо всі поди одночасно досягнуть своїх лімітів, вузол вичерпає пам'ять і почне вбивати поди.

- **Синтаксис `cpu: 0.1`** еквівалентний `cpu: 100m` (100 мілікорів).

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| Ресурси не встановлені | Поди BestEffort витісняються першими | Завжди встановлюйте запити |
| Запит > Ліміт | Некоректно, відхиляється | Запит повинен бути ≤ Ліміту |
| Пам'яті занадто мало | Постійний OOMKilled | Профілюйте застосунок, збільшіть ліміти |
| CPU занадто мало | Застосунок працює повільно | Моніторте за допомогою `k top`, коригуйте |
| Те саме, що ємність вузла | Немає місця для системних подів | Залишайте запас |

---

## Тест

1. **Яка різниця між запитами та лімітами?**
   <details>
   <summary>Відповідь</summary>
   Запити — це гарантовані ресурси, які використовуються для рішень планування. Ліміти — це максимально дозволені ресурси, які застосовуються під час виконання. Запити повинні бути ≤ Лімітів.
   </details>

2. **Що відбувається, коли контейнер перевищує ліміт пам'яті?**
   <details>
   <summary>Відповідь</summary>
   Контейнер отримує OOMKilled (завершується) і може бути перезапущений залежно від політики перезапуску.
   </details>

3. **Що відбувається, коли контейнер перевищує ліміт CPU?**
   <details>
   <summary>Відповідь</summary>
   Контейнер обмежується (сповільнюється), але НЕ вбивається. CPU — стисливий ресурс.
   </details>

4. **Який клас QoS отримує під, якщо запити дорівнюють лімітам?**
   <details>
   <summary>Відповідь</summary>
   Guaranteed. Це клас з найвищим пріоритетом, і поди витісняються останніми.
   </details>

---

## Практична вправа

**Завдання**: Налаштувати та спостерігати за поведінкою ресурсів.

**Частина 1: Базові ресурси**
```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:
        memory: "64Mi"
        cpu: "50m"
      limits:
        memory: "128Mi"
        cpu: "100m"
EOF

# Перевірити клас QoS
k get pod resource-demo -o jsonpath='{.status.qosClass}'
echo

# Перевірити ресурси
k get pod resource-demo -o jsonpath='{.spec.containers[0].resources}'
```

**Частина 2: Демонстрація OOMKill**
```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: memory-hog
spec:
  containers:
  - name: app
    image: polinux/stress
    command: ["stress"]
    args: ["--vm", "1", "--vm-bytes", "200M", "--vm-hang", "1"]
    resources:
      limits:
        memory: "100Mi"
EOF

# Спостерігати за OOMKilled
k get pod memory-hog -w

# Перевірити причину
k describe pod memory-hog | grep -A3 "Last State"
```

**Очищення:**
```bash
k delete pod resource-demo memory-hog
```

---

## Практичні вправи

### Вправа 1: Базові ресурси (Ціль: 2 хвилини)

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill1
spec:
  containers:
  - name: nginx
    image: nginx
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "200m"
        memory: "256Mi"
EOF

k get pod drill1 -o jsonpath='{.spec.containers[0].resources}'
echo
k delete pod drill1
```

### Вправа 2: Перевірка класу QoS (Ціль: 2 хвилини)

```bash
# Guaranteed (запити = ліміти)
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill2
spec:
  containers:
  - name: nginx
    image: nginx
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "100m"
        memory: "128Mi"
EOF

k get pod drill2 -o jsonpath='{.status.qosClass}'
echo
k delete pod drill2
```

### Вправа 3: Генерація пода з ресурсами (Ціль: 2 хвилини)

```bash
# Використати --dry-run для генерації, потім додати ресурси
k run drill3 --image=nginx --dry-run=client -o yaml > /tmp/drill3.yaml

# Відредагувати для додавання ресурсів (на іспиті використовуйте vim)
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill3
spec:
  containers:
  - name: drill3
    image: nginx
    resources:
      requests:
        cpu: 50m
        memory: 64Mi
      limits:
        cpu: 100m
        memory: 128Mi
EOF

k get pod drill3 -o yaml | grep -A8 resources
k delete pod drill3
```

### Вправа 4: Deployment з ресурсами (Ціль: 3 хвилини)

```bash
cat << 'EOF' | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: drill4
spec:
  replicas: 2
  selector:
    matchLabels:
      app: drill4
  template:
    metadata:
      labels:
        app: drill4
    spec:
      containers:
      - name: nginx
        image: nginx
        resources:
          requests:
            cpu: "50m"
            memory: "64Mi"
          limits:
            cpu: "100m"
            memory: "128Mi"
EOF

k get pods -l app=drill4
k delete deploy drill4
```

### Вправа 5: Перевірка ресурсів вузла (Ціль: 2 хвилини)

```bash
# Отримати ім'я вузла
NODE=$(k get nodes -o jsonpath='{.items[0].metadata.name}')

# Перевірити ємність
k describe node $NODE | grep -A5 "Capacity:"

# Перевірити доступні ресурси
k describe node $NODE | grep -A5 "Allocatable:"

# Перевірити виділені ресурси
k describe node $NODE | grep -A10 "Allocated resources:"
```

### Вправа 6: LimitRange (Ціль: 4 хвилини)

```bash
# Створити простір імен з LimitRange
k create ns drill6

cat << 'EOF' | k apply -n drill6 -f -
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
spec:
  limits:
  - default:
      cpu: "200m"
      memory: "256Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    type: Container
EOF

# Створити під без ресурсів
k run drill6-pod --image=nginx -n drill6

# Перевірити, що стандартні значення застосовані
k get pod drill6-pod -n drill6 -o jsonpath='{.spec.containers[0].resources}'
echo

# Очищення
k delete ns drill6
```

---

## Наступний модуль

[Модуль 4.4: SecurityContexts](module-4.4-securitycontext/) — Налаштування параметрів безпеки подів та контейнерів.
