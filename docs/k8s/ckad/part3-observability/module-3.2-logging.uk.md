# Модуль 3.2: Логування контейнерів

> **Складність**: `[QUICK]` — Необхідна щоденна навичка, прості команди
>
> **Час на виконання**: 25–30 хвилин
>
> **Передумови**: Модуль 1.1 (Поди), базове розуміння stdout/stderr

---

## Чому цей модуль важливий

Логи — це ваше вікно у те, що відбувається всередині контейнерів. Коли щось іде не так, логи — зазвичай перше місце, куди ви дивитесь. Kubernetes не зберігає логи постійно — він надає доступ до stdout/stderr з працюючих контейнерів.

Іспит CKAD перевіряє вашу здатність:
- Переглядати логи контейнерів
- Отримувати логи попередніх екземплярів контейнерів
- Працювати з подами з кількома контейнерами
- Фільтрувати та шукати у виводі логів

> **Аналогія з бортовим самописцем**
>
> Логи контейнерів — як чорна скринька літака. Вони записують усе, що застосунок каже (stdout/stderr). Коли щось іде не так, ви витягуєте запис, щоб зрозуміти, що сталося. Але на відміну від чорної скриньки, Kubernetes зберігає лише нещодавні логи — якщо «літак» знищено і відбудовано, старий запис зникає.

---

## Базові команди для логів

### Перегляд логів

```bash
# Базові логи
k logs pod-name

# Слідкувати за логами (потік)
k logs -f pod-name

# Останні N рядків
k logs --tail=100 pod-name

# Логи з певного часу
k logs --since=1h pod-name
k logs --since=30m pod-name
k logs --since=10s pod-name

# Логи з конкретного моменту
k logs --since-time=2024-01-15T10:00:00Z pod-name

# Показати мітки часу
k logs --timestamps pod-name
```

### Поди з кількома контейнерами

```bash
# Вказати контейнер (обов'язково для кількох контейнерів)
k logs pod-name -c container-name

# Усі контейнери
k logs pod-name --all-containers=true

# Перелічити контейнери в поді
k get pod pod-name -o jsonpath='{.spec.containers[*].name}'
```

### Попередній екземпляр контейнера

```bash
# Логи попереднього контейнера, що впав/перезапустився
k logs pod-name --previous
k logs pod-name -p

# Попередній екземпляр конкретного контейнера
k logs pod-name -c container-name --previous
```

---

## Джерела логів

### Що записується в логи

Kubernetes захоплює:
- **stdout**: Стандартний вивід процесів контейнера
- **stderr**: Стандартний потік помилок процесів контейнера

Застосунки МУСЯТЬ писати логи в stdout/stderr, щоб `kubectl logs` працював.

### Що НЕ записується в логи

- Файли, записані всередині контейнера (наприклад, `/var/log/app.log`)
- Системні логи вузла
- Логи init-контейнерів (використовуйте `-c init-container-name`)

---

## Логи на основі Deployment та міток

### Логи подів Deployment

```bash
# Логи всіх подів з міткою
k logs -l app=myapp

# Слідкувати за логами всіх відповідних подів
k logs -l app=myapp -f

# Обмежити кількість подів
k logs -l app=myapp --max-log-requests=5

# З обмеженням рядків
k logs -l app=myapp --tail=50
```

### Комбінування фільтрів

```bash
# Мітка + контейнер + tail
k logs -l app=myapp -c nginx --tail=100

# Мітка + час
k logs -l app=myapp --since=30m
```

---

## Шаблони роботи з логами

### Потокове читання логів для налагодження

```bash
# Потік з мітками часу
k logs -f --timestamps pod-name

# Потік лише помилок (grep)
k logs -f pod-name | grep -i error

# Потік з кількох подів
k logs -f -l app=myapp --all-containers
```

### Експорт логів

```bash
# Зберегти у файл
k logs pod-name > pod-logs.txt

# Зберегти з мітками часу
k logs --timestamps pod-name > pod-logs-$(date +%s).txt

# Усі контейнери
k logs pod-name --all-containers > all-logs.txt
```

---

## Сценарії логування з кількома контейнерами

### Шаблон Sidecar

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-demo
spec:
  containers:
  - name: app
    image: nginx
  - name: sidecar
    image: busybox
    command: ['sh', '-c', 'while true; do echo sidecar running; sleep 10; done']
```

```bash
# Переглянути логи основного застосунку
k logs sidecar-demo -c app

# Переглянути логи sidecar
k logs sidecar-demo -c sidecar

# Усі контейнери
k logs sidecar-demo --all-containers
```

### Логи Init-контейнерів

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-demo
spec:
  initContainers:
  - name: init-setup
    image: busybox
    command: ['sh', '-c', 'echo Init complete']
  containers:
  - name: app
    image: nginx
```

```bash
# Переглянути логи init-контейнера
k logs init-demo -c init-setup
```

---

## Візуалізація логування

```
┌─────────────────────────────────────────────────────────────┐
│                   Логування контейнерів                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Застосунок                                                 │
│       │                                                     │
│       ▼                                                     │
│  stdout/stderr ─────────────▶ Container Runtime             │
│                                      │                      │
│                                      ▼                      │
│                              /var/log/containers/           │
│                              /var/log/pods/                 │
│                                      │                      │
│                                      ▼                      │
│                              kubectl logs                   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Під: my-pod                                         │   │
│  │ ┌──────────────┐  ┌──────────────┐                 │   │
│  │ │ Контейнер A  │  │ Контейнер B  │                 │   │
│  │ │  (stdout)    │  │  (stdout)    │                 │   │
│  │ │  (stderr)    │  │  (stderr)    │                 │   │
│  │ └──────────────┘  └──────────────┘                 │   │
│  │        │                 │                          │   │
│  │        ▼                 ▼                          │   │
│  │   k logs -c a       k logs -c b                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Швидка довідка

```bash
# Основні команди
k logs POD                      # Базові логи
k logs POD -f                   # Слідкувати/потік
k logs POD --tail=100           # Останні 100 рядків
k logs POD --since=1h           # За останню годину
k logs POD -c CONTAINER         # Конкретний контейнер
k logs POD --previous           # Попередній екземпляр
k logs POD --all-containers     # Усі контейнери
k logs -l app=myapp             # За міткою
k logs POD --timestamps         # З мітками часу
```

---

## Чи знали ви?

- **Логи зберігаються на вузлі** за шляхами `/var/log/containers/` та `/var/log/pods/`. Коли під видаляється, ці логи врешті-решт очищуються.

- **У Kubernetes немає вбудованої агрегації логів.** Для продакшну команди використовують такі інструменти, як Fluentd, Fluent Bit, Loki або Elasticsearch, щоб збирати та зберігати логи централізовано.

- **Ротацію логів виконує середовище виконання контейнерів.** Типово Docker/containerd ротує логи, щоб запобігти переповненню диска, але це означає, що старі логи зникають.

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| Забули `-c` для кількох контейнерів | Помилка: потрібно вказати контейнер | Спочатку перелічіть контейнери, потім вкажіть |
| Шукаєте логи видаленого пода | Логи зникли | Використовуйте `--previous` до перезапуску пода |
| Застосунок пише логи у файли, а не stdout | `kubectl logs` нічого не показує | Налаштуйте застосунок писати в stdout |
| Не використовуєте `--tail` для великих логів | Термінал заливає потоком даних | Завжди обмежуйте початковий вивід |
| Ігнорування логів init-контейнерів | Пропуск помилок налаштування | Перевіряйте init-контейнери з `-c` |

---

## Тест

1. **Як переглянути логи попереднього екземпляра контейнера?**
   <details>
   <summary>Відповідь</summary>
   `kubectl logs pod-name --previous` або `kubectl logs pod-name -p`
   </details>

2. **Як переглянути логи конкретного контейнера в поді з кількома контейнерами?**
   <details>
   <summary>Відповідь</summary>
   `kubectl logs pod-name -c container-name`
   </details>

3. **Як переглянути останні 50 рядків логів за останню годину?**
   <details>
   <summary>Відповідь</summary>
   `kubectl logs pod-name --since=1h --tail=50`
   </details>

4. **Як слідкувати за логами всіх подів з міткою `app=web`?**
   <details>
   <summary>Відповідь</summary>
   `kubectl logs -l app=web -f` (додайте `--max-log-requests=N`, якщо подів багато)
   </details>

---

## Практична вправа

**Завдання**: Попрактикуватися в отриманні логів з різних конфігурацій подів.

**Підготовка:**
```bash
# Створити під, що генерує логи
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: log-demo
  labels:
    app: log-demo
spec:
  containers:
  - name: logger
    image: busybox
    command: ['sh', '-c', 'i=0; while true; do echo "$(date) - Log entry $i"; i=$((i+1)); sleep 2; done']
EOF
```

**Частина 1: Базові логи**
```bash
# Переглянути логи
k logs log-demo

# Слідкувати за логами (Ctrl+C для зупинки)
k logs log-demo -f

# Останні 5 рядків
k logs log-demo --tail=5

# З мітками часу
k logs log-demo --timestamps --tail=5
```

**Частина 2: Кілька контейнерів**
```bash
# Створити під з кількома контейнерами
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: multi-log
spec:
  containers:
  - name: app
    image: nginx
  - name: sidecar
    image: busybox
    command: ['sh', '-c', 'while true; do echo Sidecar log; sleep 5; done']
EOF

# Перелічити контейнери
k get pod multi-log -o jsonpath='{.spec.containers[*].name}'

# Переглянути кожний контейнер
k logs multi-log -c app
k logs multi-log -c sidecar

# Усі контейнери
k logs multi-log --all-containers
```

**Частина 3: Попередній екземпляр**
```bash
# Створити під, що падає
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: crasher
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'echo "Starting..."; echo "About to crash!"; exit 1']
EOF

# Зачекати на перезапуск, потім перевірити попередні логи
k get pod crasher -w
k logs crasher --previous
```

**Очищення:**
```bash
k delete pod log-demo multi-log crasher
```

---

## Практичні вправи

### Вправа 1: Базові логи (Ціль: 1 хвилина)

```bash
# Створити під
k run drill1 --image=nginx

# Переглянути логи
k logs drill1

# Очищення
k delete pod drill1
```

### Вправа 2: Слідкування за логами (Ціль: 2 хвилини)

```bash
# Створити під з логуванням
k run drill2 --image=busybox -- sh -c 'while true; do echo tick; sleep 1; done'

# Слідкувати (Ctrl+C після кількох тіків)
k logs drill2 -f

# Очищення
k delete pod drill2
```

### Вправа 3: Кілька контейнерів (Ціль: 3 хвилини)

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill3
spec:
  containers:
  - name: web
    image: nginx
  - name: monitor
    image: busybox
    command: ['sh', '-c', 'while true; do echo monitoring; sleep 5; done']
EOF

# Отримати логи з кожного
k logs drill3 -c web
k logs drill3 -c monitor

# Очищення
k delete pod drill3
```

### Вправа 4: Вибір за мітками (Ціль: 2 хвилини)

```bash
# Створити кілька подів
k run drill4a --image=nginx -l app=drill4
k run drill4b --image=nginx -l app=drill4

# Логи всіх з міткою
k logs -l app=drill4

# Очищення
k delete pod -l app=drill4
```

### Вправа 5: Попередній екземпляр (Ціль: 3 хвилини)

```bash
# Створити під, що падає
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill5
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'echo "Run at $(date)"; sleep 5; exit 1']
EOF

# Спостерігати за падінням
k get pod drill5 -w

# Після перезапуску отримати попередні логи
k logs drill5 --previous

# Очищення
k delete pod drill5
```

### Вправа 6: Повний сценарій логування (Ціль: 4 хвилини)

**Сценарій**: Відлагодити застосунок, що не працює, використовуючи логи.

```bash
# Створити «зламаний» deployment
cat << 'EOF' | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: drill6
spec:
  replicas: 2
  selector:
    matchLabels:
      app: drill6
  template:
    metadata:
      labels:
        app: drill6
    spec:
      containers:
      - name: app
        image: busybox
        command: ['sh', '-c', 'echo "Starting app"; echo "ERROR: Database connection failed"; exit 1']
EOF

# Знайти поди
k get pods -l app=drill6

# Перевірити логи одного пода
k logs -l app=drill6 --tail=10

# Отримати логи попереднього екземпляра
POD=$(k get pods -l app=drill6 -o jsonpath='{.items[0].metadata.name}')
k logs $POD --previous

# Очищення
k delete deploy drill6
```

---

## Наступний модуль

[Модуль 3.3: Налагодження в Kubernetes](module-3.3-debugging.uk.md) — Усунення несправностей подів, контейнерів та проблем кластера.
