---
title: "\u041c\u043e\u0434\u0443\u043b\u044c 1.3: \u041f\u0456\u0434\u0438 \u0437 \u043a\u0456\u043b\u044c\u043a\u043e\u043c\u0430 \u043a\u043e\u043d\u0442\u0435\u0439\u043d\u0435\u0440\u0430\u043c\u0438"
slug: uk/k8s/ckad/part1-design-build/module-1.3-multi-container-pods
sidebar:
  order: 3
---
> **Складність**: `[MEDIUM]` — Ключова навичка CKAD, що вимагає розпізнавання паттернів
>
> **Час на виконання**: 50–60 хвилин
>
> **Передумови**: Модуль 1.1 (Образи контейнерів), Модуль 1.2 (Jobs та CronJobs)

---

## Чому цей модуль важливий

Більшість застосунків потребують більше одного контейнера. Вебсерверу потрібен відправник логів. API потребує проксі. Обробнику даних потрібен ініціалізатор. Піди з кількома контейнерами — це спосіб компонувати ці частини.

**Це ключова тема CKAD.** Очікуйте 2–4 запитання саме про паттерни з кількома контейнерами. Вам потрібно розпізнавати, коли використовувати кожен паттерн, і реалізовувати їх швидко.

> **Аналогія з фуд-траком**
>
> Під — як фуд-трак. Основний контейнер — це шеф-кухар — він готує їжу. Але успішному фуд-траку потрібно більше: хтось для прийому замовлень (sidecar), хтось для підготовки перед відкриттям (init), і, можливо, каса, повернута до клієнтів іншим боком (ambassador). Вони всі ділять один трак (Під), ділять робочий простір (файлову систему) і працюють разом — але кожен має окрему роль.

---

## Паттерни з кількома контейнерами

### Три паттерни, які ви мусите знати

```
┌─────────────────────────────────────────────────────────────────┐
│              Паттерни з кількома контейнерами                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INIT-КОНТЕЙНЕР                                                  │
│  ┌─────────────┐    ┌─────────────┐                             │
│  │    Init-    │───▶│  Основний   │                             │
│  │  контейнер  │    │  контейнер  │                             │
│  │(запуск першим)│   │(запуск після)│                            │
│  └─────────────┘    └─────────────┘                             │
│  • Ініціалізація даних, очікування залежностей, налаштування     │
│                                                                  │
│  SIDECAR                                                        │
│  ┌─────────────┐    ┌─────────────┐                             │
│  │  Основний   │◀──▶│   Sidecar   │                             │
│  │  контейнер  │    │  контейнер  │                             │
│  │(логіка додатку)│  │ (помічник)  │                            │
│  └─────────────┘    └─────────────┘                             │
│  • Відправка логів, моніторинг, синхронізація конфігурації       │
│                                                                  │
│  AMBASSADOR                                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Основний   │───▶│  Ambassador │───▶│  Зовнішній  │         │
│  │  контейнер  │    │   (проксі)  │    │   сервіс    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│  • Проксіювання з'єднань, обробка TLS, обмеження швидкості      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Init-контейнери

Init-контейнери запускаються **перед** стартом контейнерів застосунку. Вони виконуються послідовно, кожен має завершитися успішно перед стартом наступного.

### Сценарії використання

- Очікування готовності сервісу
- Клонування git-репозиторію або завантаження файлів
- Генерація конфігураційних файлів
- Запуск міграцій бази даних
- Очікування встановлення дозволів

### YAML для Init-контейнера

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-demo
spec:
  initContainers:
  - name: init-wait
    image: busybox
    command: ['sh', '-c', 'until nslookup myservice; do echo waiting; sleep 2; done']
  - name: init-setup
    image: busybox
    command: ['sh', '-c', 'echo "Setup complete" > /data/ready']
    volumeMounts:
    - name: shared
      mountPath: /data
  containers:
  - name: main
    image: nginx
    volumeMounts:
    - name: shared
      mountPath: /usr/share/nginx/html
  volumes:
  - name: shared
    emptyDir: {}
```

### Ключові властивості

| Властивість | Поведінка |
|-------------|-----------|
| Порядок запуску | Послідовний (init1, потім init2, потім основний) |
| Невдача | Під перезапускається, якщо будь-який init-контейнер не вдається |
| Політика перезапуску | Завжди перезапускати з першого init при перезапуску Підa |
| Ресурси | Можуть мати інші ліміти ресурсів, ніж контейнери застосунку |
| Проби | Немає liveness/readiness проб (їм просто потрібно завершитися з кодом 0) |

### Статус Init-контейнера

```bash
# Перевірити статус init-контейнера
k get pod init-demo

# Детальний статус
k describe pod init-demo | grep -A10 "Init Containers"

# Логи init-контейнера
k logs init-demo -c init-wait
```

---

## Sidecar-контейнери

Sidecar-контейнери працюють **поруч** з основним контейнером протягом усього життя Підa. Вони розширюють функціональність без модифікації основного застосунку.

### Сценарії використання

- Агрегація логів (відправка логів до центральної системи)
- Агенти моніторингу (збір метрик)
- Синхронізація конфігурації (відстеження змін конфігурації)
- Проксі сервісних меш (Istio, Linkerd)
- Наповнення кешу

### YAML для Sidecar

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-demo
spec:
  containers:
  - name: main
    image: nginx
    volumeMounts:
    - name: logs
      mountPath: /var/log/nginx
  - name: log-shipper
    image: busybox
    command: ['sh', '-c', 'tail -F /var/log/nginx/access.log']
    volumeMounts:
    - name: logs
      mountPath: /var/log/nginx
  volumes:
  - name: logs
    emptyDir: {}
```

### Спільний доступ до даних між контейнерами

Контейнери у Піді можуть ділити:

1. **Томи** (найчастіше)
```yaml
volumes:
- name: shared
  emptyDir: {}
```

2. **Мережу** (один localhost)
```yaml
# Основний контейнер відкриває :8080
# Sidecar може звертатися до localhost:8080
```

3. **Простір процесів** (рідко)
```yaml
spec:
  shareProcessNamespace: true
```

---

## Паттерн Ambassador

Ambassador-контейнери проксіюють з'єднання до зовнішніх сервісів, абстрагуючи складність від основного контейнера.

### Сценарії використання

- Пулінг з'єднань до бази даних
- Термінація TLS
- Виявлення сервісів
- Обмеження швидкості
- Трансляція протоколів

### YAML для Ambassador

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ambassador-demo
spec:
  containers:
  - name: main
    image: myapp
    env:
    - name: DB_HOST
      value: "localhost"    # Ambassador обробляє реальне з'єднання
    - name: DB_PORT
      value: "5432"
  - name: db-proxy
    image: ambassador-proxy
    env:
    - name: REAL_DB_HOST
      value: "db.production.svc"
    - name: REAL_DB_PORT
      value: "5432"
    ports:
    - containerPort: 5432   # Слухає на localhost:5432 для основного
```

---

## Розпізнавання паттернів

Коли використовувати кожен паттерн?

| Сценарій | Паттерн | Чому |
|----------|---------|------|
| Очікування бази даних перед стартом | Init | Одноразова перевірка залежності |
| Відправка логів до Elasticsearch | Sidecar | Безперервна операція |
| Завантаження конфігурації перед стартом додатку | Init | Завдання налаштування |
| Відстеження змін конфігураційного файлу | Sidecar | Безперервна операція |
| Проксіювання з'єднань до бази даних | Ambassador | Шар абстракції |
| Запуск міграцій бази даних | Init | Одноразова операція |
| Додавання TLS до додатку без TLS | Ambassador | Обробка протоколу |
| Збір метрик Prometheus | Sidecar | Безперервна операція |

---

## Швидке створення Підів з кількома контейнерами

Ви не можете створити Піди з кількома контейнерами імперативно. Використовуйте паттерн "згенерувати-і-відредагувати":

### Крок 1: Згенерувати базу

```bash
k run multi --image=nginx --dry-run=client -o yaml > multi.yaml
```

### Крок 2: Додати контейнери

Відредагуйте `multi.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi
spec:
  containers:
  - name: nginx
    image: nginx
  - name: sidecar           # ДОДАЙТЕ ЦЕ
    image: busybox          # ДОДАЙТЕ ЦЕ
    command: ["sleep", "3600"]  # ДОДАЙТЕ ЦЕ
```

### Крок 3: Додати Init-контейнери (за потреби)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi
spec:
  initContainers:           # ДОДАЙТЕ ЦЮ СЕКЦІЮ
  - name: init
    image: busybox
    command: ["sh", "-c", "echo init done"]
  containers:
  - name: nginx
    image: nginx
  - name: sidecar
    image: busybox
    command: ["sleep", "3600"]
```

---

## Налагодження Підів з кількома контейнерами

### Вказання контейнера

```bash
# Логи конкретного контейнера
k logs multi -c sidecar

# Exec у конкретний контейнер
k exec -it multi -c sidecar -- sh

# Describe показує всі контейнери
k describe pod multi
```

### Перевірка статусу контейнера

```bash
# Статуси всіх контейнерів
k get pod multi -o jsonpath='{.status.containerStatuses[*].name}'

# Перевірка готовності
k get pod multi -o jsonpath='{range .status.containerStatuses[*]}{.name}{"\t"}{.ready}{"\n"}{end}'
```

### Типові проблеми

| Симптом | Причина | Рішення |
|---------|---------|---------|
| Під застряг у `Init:0/1` | Init-контейнер не завершується | Перевірте логи init-контейнера |
| Один контейнер у `CrashLoopBackOff` | Команда контейнера завершується | Виправте команду або додайте `sleep` |
| Контейнери не можуть ділити дані | Немає спільного тому | Додайте том `emptyDir` |
| Основний не може досягти sidecar | Неправильна конфігурація мережі | Використовуйте `localhost:port` |

---

## Чи знали ви?

- **Init-контейнери можуть мати інші образи, ніж контейнери застосунку.** Використовуйте спеціалізовані інструменти (як `git`, клієнти баз даних) в init-контейнерах без роздування вашого образу застосунку.

- **Sidecar-контейнери традиційно перезапускаються разом з Підом**, але Kubernetes 1.28+ додав нативну підтримку sidecar з `restartPolicy: Always` для init-контейнерів, роблячи їх справжніми sidecar-контейнерами, що перезапускаються незалежно.

- **Паттерн ambassador з'явився раніше за сервісні меші.** До Istio та Linkerd розробники використовували ambassador-контейнери для обробки крос-функціональних задач. Тепер сервісні меші автоматизують ін'єкцію sidecar.

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| Забули `-c container` | Логи не того контейнера | Завжди вказуйте контейнер |
| Init-контейнер зі `sleep` | Під ніколи не запуститься | Init має завершитися з кодом 0 |
| Немає спільного тому | Контейнери не можуть обмінюватися файлами | Додайте `emptyDir` |
| Sidecar завершується негайно | Під постійно перезапускається | Додайте `sleep infinity` або реальний сервіс |
| Неправильний порт у localhost | Відмова з'єднання | Перевірте відповідність портів |

---

## Тест

1. **У якому порядку запускаються init-контейнери?**
   <details>
   <summary>Відповідь</summary>
   Послідовно, один за одним. Кожен має завершитися успішно (вийти з кодом 0) перед стартом наступного. Контейнери застосунку запускаються лише після завершення всіх init-контейнерів.
   </details>

2. **Як контейнери в одному Піді обмінюються файлами?**
   <details>
   <summary>Відповідь</summary>
   Через спільні томи. Визначте том (наприклад, `emptyDir`) і змонтуйте його в обох контейнерах. Вони зможуть читати/писати за однаковим шляхом.
   </details>

3. **Який паттерн ви використаєте, щоб дочекатися готовності бази даних перед стартом вашого застосунку?**
   <details>
   <summary>Відповідь</summary>
   Init-контейнер. Він запускається перед основним контейнером і може циклічно перевіряти доступність бази даних, а потім успішно завершитися.
   </details>

4. **Як переглянути логи конкретного контейнера у Піді з кількома контейнерами?**
   <details>
   <summary>Відповідь</summary>
   `kubectl logs pod-name -c container-name`. Прапор `-c` вказує, логи якого контейнера отримати.
   </details>

---

## Практична вправа

**Завдання**: Побудувати Під з init-, sidecar- та основним контейнерами.

**Сценарій**: Створіть застосунок, що:
1. Init: Завантажує конфігурацію з URL (симуляція)
2. Основний: Запускає nginx, що обслуговує конфігурацію
3. Sidecar: Моніторить та логує зміни

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: full-pattern
spec:
  initContainers:
  - name: config-init
    image: busybox
    command: ['sh', '-c', 'echo "Welcome to CKAD!" > /data/index.html']
    volumeMounts:
    - name: html
      mountPath: /data
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - name: html
      mountPath: /usr/share/nginx/html
    ports:
    - containerPort: 80
  - name: monitor
    image: busybox
    command: ['sh', '-c', 'while true; do echo "Checking..."; cat /data/index.html; sleep 10; done']
    volumeMounts:
    - name: html
      mountPath: /data
  volumes:
  - name: html
    emptyDir: {}
```

**Перевірка:**
```bash
# Застосувати
k apply -f full-pattern.yaml

# Дочекатися готовності
k get pod full-pattern -w

# Перевірити завершення init
k describe pod full-pattern | grep -A5 "Init Containers"

# Перевірити, що nginx обслуговує контент
k exec full-pattern -c nginx -- curl localhost

# Перевірити логи монітора
k logs full-pattern -c monitor

# Очищення
k delete pod full-pattern
```

---

## Практичні вправи

### Вправа 1: Базовий Init-контейнер (Ціль: 3 хвилини)

```bash
# Створити Під з init-контейнером
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: init-pod
spec:
  initContainers:
  - name: init
    image: busybox
    command: ["sh", "-c", "echo 'Init complete' && sleep 3"]
  containers:
  - name: main
    image: nginx
EOF

# Спостерігати за стартом Підa
k get pod init-pod -w

# Перевірити логи init
k logs init-pod -c init

# Очищення
k delete pod init-pod
```

### Вправа 2: Базовий Sidecar (Ціль: 3 хвилини)

```bash
# Створити Під із sidecar
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-pod
spec:
  containers:
  - name: main
    image: nginx
  - name: sidecar
    image: busybox
    command: ["sh", "-c", "while true; do echo 'Sidecar running'; sleep 5; done"]
EOF

# Перевірити обидва контейнери
k get pod sidecar-pod -o jsonpath='{.spec.containers[*].name}'

# Перевірити логи sidecar
k logs sidecar-pod -c sidecar

# Очищення
k delete pod sidecar-pod
```

### Вправа 3: Спільний том (Ціль: 4 хвилини)

```bash
# Створити Під зі спільним томом
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: shared-vol
spec:
  containers:
  - name: writer
    image: busybox
    command: ["sh", "-c", "while true; do date >> /shared/log.txt; sleep 5; done"]
    volumeMounts:
    - name: shared
      mountPath: /shared
  - name: reader
    image: busybox
    command: ["sh", "-c", "tail -f /shared/log.txt"]
    volumeMounts:
    - name: shared
      mountPath: /shared
  volumes:
  - name: shared
    emptyDir: {}
EOF

# Перевірити, що reader бачить дані writer
k logs shared-vol -c reader

# Очищення
k delete pod shared-vol
```

### Вправа 4: Init, що очікує на сервіс (Ціль: 5 хвилин)

```bash
# Спочатку створити сервіс
k create svc clusterip wait-svc --tcp=80:80

# Створити Під, що очікує на сервіс
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: wait-pod
spec:
  initContainers:
  - name: wait
    image: busybox
    command: ['sh', '-c', 'until nslookup wait-svc; do echo waiting; sleep 2; done']
  containers:
  - name: main
    image: nginx
EOF

# Перевірити статус init
k describe pod wait-pod | grep -A3 "Init Containers"

# Очищення
k delete pod wait-pod
k delete svc wait-svc
```

### Вправа 5: Паттерн Ambassador (Ціль: 5 хвилин)

```bash
# Створити Під з ambassador-проксі
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: ambassador-pod
spec:
  containers:
  - name: main
    image: busybox
    command: ["sh", "-c", "while true; do wget -qO- localhost:8080; sleep 10; done"]
  - name: proxy
    image: nginx
    ports:
    - containerPort: 8080
EOF

# Основний контейнер звертається до проксі через localhost
k logs ambassador-pod -c main

# Очищення
k delete pod ambassador-pod
```

### Вправа 6: Повне завдання з кількома контейнерами (Ціль: 8 хвилин)

**Без підказок — створіть з пам'яті:**

Створіть Під з іменем `app-complete` з:
1. Init-контейнер: Створює `/data/config.txt` з текстом "Config loaded"
2. Основний контейнер (nginx): Обслуговує директорію `/data`
3. Sidecar: Моніторить `/data/config.txt` кожні 5 секунд

Після створення перевірте:
- Під працює (Running)
- Init завершився успішно
- Sidecar показує вміст конфігурації

<details>
<summary>Відповідь</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-complete
spec:
  initContainers:
  - name: init
    image: busybox
    command: ["sh", "-c", "echo 'Config loaded' > /data/config.txt"]
    volumeMounts:
    - name: data
      mountPath: /data
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - name: data
      mountPath: /usr/share/nginx/html
  - name: monitor
    image: busybox
    command: ["sh", "-c", "while true; do cat /data/config.txt; sleep 5; done"]
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    emptyDir: {}
```

```bash
k apply -f app-complete.yaml
k get pod app-complete
k logs app-complete -c init
k logs app-complete -c monitor
k delete pod app-complete
```

</details>

---

## Наступний модуль

[Модуль 1.4: Томи для розробників](module-1.4-volumes/) — Паттерни постійного та ефемерного зберігання.
