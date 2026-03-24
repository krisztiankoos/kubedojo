# Модуль 3.3: Налагодження в Kubernetes

> **Складність**: `[MEDIUM]` — Критична навичка для іспиту, що вимагає системного підходу
>
> **Час на виконання**: 45–55 хвилин
>
> **Передумови**: Модуль 3.1 (Проби), Модуль 3.2 (Логування)

---

## Чому цей модуль важливий

Налагодження — це те, де виграється або програється іспит. Коли щось не працює, вам потрібен системний підхід, щоб швидко знайти проблему. Іспит CKAD навмисно включає зламані конфігурації — ви повинні діагностувати та виправити їх під тиском часу.

Цей модуль охоплює:
- Налагодження подів, що не запускаються
- Налагодження працюючих подів з проблемами
- Використання ефемерних контейнерів для налагодження
- Системний процес налагодження

> **Аналогія з детективом**
>
> Налагодження — це робота детектива. Ви прибуваєте на місце злочину (зламаний під) і мусите знайти улики. Ви перевіряєте історію жертви (`describe`), досліджуєте докази (`logs`), допитуєте свідків (`events`) і іноді потрібно діяти під прикриттям (`exec`), щоб зловити злочинця. Системне розслідування перемагає випадкові здогадки.

---

## Процес налагодження

```
┌─────────────────────────────────────────────────────────────┐
│              Системний процес налагодження                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. ПЕРЕВІРИТИ СТАТУС                                       │
│     k get pod POD -o wide                                   │
│     └── Який стан? Ready? Перезапуски? Вузол?              │
│                                                             │
│  2. ОПИСАТИ                                                 │
│     k describe pod POD                                      │
│     └── Події? Умови? Стан контейнера?                     │
│                                                             │
│  3. ЛОГИ                                                    │
│     k logs POD [--previous]                                 │
│     └── Що сказав застосунок? Помилки?                     │
│                                                             │
│  4. ВИКОНАТИ КОМАНДУ                                        │
│     k exec -it POD -- sh                                    │
│     └── Що всередині? Файли? Процеси? Мережа?             │
│                                                             │
│  5. ПОДІЇ                                                   │
│     k get events --sort-by='.lastTimestamp'                 │
│     └── Що відбулося на рівні кластера?                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Команди для налагодження

### Швидка перевірка статусу

```bash
# Огляд стану пода
k get pod POD -o wide

# Усі поди в просторі імен
k get pods

# Спостерігати за змінами
k get pods -w
```

### Describe для деталей

```bash
# Повні деталі пода
k describe pod POD

# Ключові розділи для перевірки:
# - Status/Conditions
# - Containers (State, Ready, Restart Count)
# - Events (внизу виводу)
```

### Перегляд логів

```bash
# Поточні логи
k logs POD

# Попередній екземпляр (після падіння)
k logs POD --previous

# Конкретний контейнер
k logs POD -c CONTAINER

# Потокові логи
k logs -f POD
```

### Виконання команд

```bash
# Інтерактивна оболонка
k exec -it POD -- sh
k exec -it POD -- /bin/bash

# Виконати одну команду
k exec POD -- ls /app
k exec POD -- cat /etc/config

# Конкретний контейнер
k exec -it POD -c CONTAINER -- sh
```

### Перегляд подій

```bash
# Події простору імен (відсортовані за часом)
k get events --sort-by='.lastTimestamp'

# Фільтр за типом
k get events --field-selector type=Warning

# Події для конкретного пода
k get events --field-selector involvedObject.name=POD
```

---

## Типові стани подів та їх виправлення

### Pending

**Під застряг у стані Pending.**

```bash
# Перевірити причину
k describe pod POD

# Типові причини:
# 1. Недостатньо ресурсів
#    → Перевірити ресурси вузла: k describe node
#    → Зменшити запити ресурсів пода

# 2. Немає відповідного вузла (nodeSelector/affinity)
#    → Перевірити мітки вузлів: k get nodes --show-labels
#    → Виправити селектор або додати мітки вузлам

# 3. PVC не прив'язаний
#    → Перевірити PVC: k get pvc
#    → Створити відповідний PV
```

### ImagePullBackOff / ErrImagePull

**Не вдається завантажити образ контейнера.**

```bash
# Перевірити події
k describe pod POD | grep -A5 Events

# Типові причини:
# 1. Неправильна назва/тег образу
#    → Виправити образ у специфікації пода

# 2. Приватний реєстр без облікових даних
#    → Створити imagePullSecret

# 3. Образ не існує
#    → Перевірити наявність образу в реєстрі
```

### CrashLoopBackOff

**Контейнер постійно падає.**

```bash
# Перевірити логи екземпляра, що впав
k logs POD --previous

# Перевірити код виходу
k describe pod POD | grep "Last State"

# Типові причини:
# 1. Помилка застосунку (перевірте логи)
# 2. Відсутня конфігурація/секрети
# 3. Неправильна команда/аргументи
# 4. Проба liveness вбиває справний застосунок
```

### Running, але Not Ready

**Контейнер працює, але readiness не проходить.**

```bash
# Перевірити пробу readiness
k describe pod POD | grep -A5 Readiness

# Перевірити ендпоінти
k get endpoints SERVICE

# Типові причини:
# 1. Неправильний шлях/порт проби readiness
# 2. Застосунок не повністю запустився
# 3. Залежність недоступна
```

---

## Налагодження всередині контейнерів

### Базові команди

```bash
# Отримати оболонку
k exec -it POD -- sh

# Перевірити процеси
k exec POD -- ps aux

# Перевірити мережу
k exec POD -- netstat -tlnp
k exec POD -- ss -tlnp

# Перевірити DNS
k exec POD -- nslookup kubernetes
k exec POD -- cat /etc/resolv.conf

# Перевірити з'єднання
k exec POD -- wget -qO- http://service:port
k exec POD -- curl -s http://service:port

# Перевірити файли
k exec POD -- ls -la /app
k exec POD -- cat /etc/config/file
```

### Коли оболонка недоступна

Деякі контейнери (distroless, scratch) не мають оболонки:

```bash
# Перевірити наявність оболонки
k exec POD -- /bin/sh -c 'echo works'

# Якщо оболонки немає, використайте debug-контейнер (Kubernetes 1.25+)
k debug POD -it --image=busybox --target=container-name
```

---

## Ефемерні контейнери для налагодження

Kubernetes 1.25+ підтримує ефемерні контейнери для налагодження:

```bash
# Додати debug-контейнер до працюючого пода
k debug POD -it --image=busybox --target=container-name

# Налагодження з конкретним образом
k debug POD -it --image=nicolaka/netshoot

# Скопіювати під для налагодження (не впливає на оригінал)
k debug POD -it --copy-to=debug-pod --container=debug --image=busybox
```

### Випадки використання debug-контейнерів

```bash
# Налагодження мережі (немає curl в оригінальному контейнері)
k debug POD -it --image=nicolaka/netshoot --target=app
# Потім: curl, dig, nslookup, tcpdump

# Інспекція файлової системи
k debug POD -it --image=busybox --target=app
# Потім: ls, cat, find

# Налагодження процесів
k debug POD -it --image=busybox --target=app --share-processes
# Потім: ps aux
```

---

## Налагодження Service

### Перевірка з'єднання Service-Під

```bash
# Перевірити існування сервісу
k get svc SERVICE

# Перевірити ендпоінти (повинні містити IP подів)
k get endpoints SERVICE

# Якщо ендпоінтів немає:
# - Перевірте, чи мітки подів відповідають селектору сервісу
# - Перевірте readiness пода
k get pods --show-labels
k describe svc SERVICE | grep Selector
```

### Перевірка DNS сервісу

```bash
# Зсередини пода
k exec POD -- nslookup SERVICE
k exec POD -- nslookup SERVICE.NAMESPACE.svc.cluster.local

# Створити тестовий під для налагодження
k run test --image=busybox --rm -it -- nslookup SERVICE
```

### Перевірка з'єднання з сервісом

```bash
# Зсередини пода
k exec POD -- wget -qO- http://SERVICE:PORT
k exec POD -- curl -s http://SERVICE:PORT
```

---

## Сценарії налагодження

### Сценарій 1: Під не запускається

```bash
# Крок 1: Перевірити статус
k get pod broken-pod

# Крок 2: Describe для подій
k describe pod broken-pod

# Крок 3: Перевірити, чи існує образ
# Якщо ErrImagePull: виправити назву образу
# Якщо Pending: перевірити ресурси/nodeSelector

# Крок 4: Перевірити логи, якщо контейнер запустився
k logs broken-pod
```

### Сценарій 2: Під постійно падає

```bash
# Крок 1: Отримати кількість перезапусків
k get pod crashing-pod

# Крок 2: Перевірити попередні логи
k logs crashing-pod --previous

# Крок 3: Перевірити код виходу
k describe pod crashing-pod | grep -A3 "Last State"

# Крок 4: Перевірити пробу liveness
k describe pod crashing-pod | grep -A5 Liveness
```

### Сценарій 3: Service недоступний

```bash
# Крок 1: Перевірити існування сервісу
k get svc myservice

# Крок 2: Перевірити ендпоінти
k get endpoints myservice

# Крок 3: Якщо ендпоінтів немає, перевірити мітки подів
k get pods --show-labels
k describe svc myservice | grep Selector

# Крок 4: Перевірити зсередини кластера
k run test --image=busybox --rm -it -- wget -qO- http://myservice
```

---

## Чи знали ви?

- **`kubectl debug` створює ефемерні контейнери**, що поділяють мережевий простір і простір процесів пода. Це означає, що ви можете бачити мережеві з'єднання та процеси з debug-контейнера.

- **Код виходу 137 означає OOMKilled** (Out of Memory). Контейнер було вбито, бо він перевищив ліміт пам'яті.

- **Код виходу 1 — це загальна помилка**, зазвичай від самого застосунку. Перевірте логи для деталей.

- **Код виходу 0 означає успіх** — але якщо контейнер завершився з кодом 0 і не повинен був, це все одно проблема (неправильна команда).

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| Випадкові здогадки | Витрачає час на іспиті | Дотримуйтеся системного процесу |
| Пропуск `describe` | Пропуск очевидних подій | Завжди перевіряйте події першими |
| Не перевіряєте `--previous` | Пропуск логів падіння | Перевіряйте попередній екземпляр при CrashLoop |
| Ігнорування кодів виходу | Пропуск OOM/сигнальних проблем | Перевіряйте Last State в describe |
| Забули про readiness | Під працює, але без трафіку | Перевірте ендпоінти та проби |

---

## Тест

1. **Яка команда показує логи попереднього екземпляра контейнера, що впав?**
   <details>
   <summary>Відповідь</summary>
   `kubectl logs POD --previous` або `kubectl logs POD -p`
   </details>

2. **Як отримати події, відсортовані за часовою міткою?**
   <details>
   <summary>Відповідь</summary>
   `kubectl get events --sort-by='.lastTimestamp'`
   </details>

3. **Що зазвичай означає код виходу 137?**
   <details>
   <summary>Відповідь</summary>
   OOMKilled — контейнер перевищив свій ліміт пам'яті і був вбитий ядром.
   </details>

4. **Як додати ефемерний debug-контейнер до працюючого пода?**
   <details>
   <summary>Відповідь</summary>
   `kubectl debug POD -it --image=busybox --target=container-name`
   </details>

---

## Практична вправа

**Завдання**: Відлагодити та виправити зламані поди.

**Підготовка:**
```bash
# Створити зламаний під (неправильний образ)
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: broken1
spec:
  containers:
  - name: app
    image: nginx:nonexistent-tag
EOF

# Створити під, що падає
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: broken2
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'echo "Config not found"; exit 1']
EOF

# Створити під з проблемою ресурсів
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: broken3
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:
        memory: "999Gi"
EOF
```

**Налагодження кожного:**
```bash
# Налагодити broken1
k get pod broken1
k describe pod broken1 | tail -10
# Виправлення: Змінити образ на nginx:latest

# Налагодити broken2
k get pod broken2
k logs broken2 --previous
# Виправлення: Надати правильну конфігурацію

# Налагодити broken3
k get pod broken3
k describe pod broken3 | grep -A5 Events
# Виправлення: Зменшити запит пам'яті
```

**Очищення:**
```bash
k delete pod broken1 broken2 broken3
```

---

## Практичні вправи

### Вправа 1: Describe та події (Ціль: 2 хвилини)

```bash
# Створити під
k run drill1 --image=nginx

# Описати його
k describe pod drill1

# Перевірити події
k get events --field-selector involvedObject.name=drill1

# Очищення
k delete pod drill1
```

### Вправа 2: Exec в під (Ціль: 2 хвилини)

```bash
# Створити під
k run drill2 --image=nginx

# Зайти в нього
k exec -it drill2 -- bash

# Всередині: перевірити, що nginx працює
ps aux | grep nginx
exit

# Очищення
k delete pod drill2
```

### Вправа 3: Налагодження пода, що падає (Ціль: 3 хвилини)

```bash
# Створити під, що падає
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill3
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'echo error; exit 1']
EOF

# Зачекати на падіння
k get pod drill3 -w

# Отримати логи попереднього екземпляра
k logs drill3 --previous

# Очищення
k delete pod drill3
```

### Вправа 4: Налагодження ImagePullBackOff (Ціль: 3 хвилини)

```bash
# Створити під з неправильним образом
k run drill4 --image=invalid-registry.io/no-such-image:v1

# Перевірити статус
k get pod drill4

# Describe для деталей
k describe pod drill4 | grep -A5 Events

# Очищення
k delete pod drill4
```

### Вправа 5: Налагодження Service (Ціль: 4 хвилини)

```bash
# Створити під і сервіс з невідповідними мітками
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill5
  labels:
    app: myapp
spec:
  containers:
  - name: nginx
    image: nginx
---
apiVersion: v1
kind: Service
metadata:
  name: drill5-svc
spec:
  selector:
    app: wronglabel
  ports:
  - port: 80
EOF

# Перевірити ендпоінти (мають бути порожні)
k get endpoints drill5-svc

# Знайти проблему
k get pod drill5 --show-labels
k describe svc drill5-svc | grep Selector

# Виправити через patch сервісу
k patch svc drill5-svc -p '{"spec":{"selector":{"app":"myapp"}}}'

# Перевірити, що ендпоінти з'явилися
k get endpoints drill5-svc

# Очищення
k delete pod drill5 svc drill5-svc
```

### Вправа 6: Повний сценарій налагодження (Ціль: 5 хвилин)

**Сценарій**: Застосунок розгорнуто, але він недоступний.

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
      - name: nginx
        image: nginx
        readinessProbe:
          httpGet:
            path: /nonexistent
            port: 80
---
apiVersion: v1
kind: Service
metadata:
  name: drill6-svc
spec:
  selector:
    app: drill6
  ports:
  - port: 80
EOF

# Перевірити поди (працюють, але не готові)
k get pods -l app=drill6

# Перевірити ендпоінти (порожні)
k get endpoints drill6-svc

# Describe пода для невдачі проби
k describe pod -l app=drill6 | grep -A5 Readiness

# Виправити пробу readiness
k patch deploy drill6 --type='json' -p='[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/path","value":"/"}]'

# Зачекати на розгортання
k rollout status deploy drill6

# Перевірити ендпоінти
k get endpoints drill6-svc

# Очищення
k delete deploy drill6 svc drill6-svc
```

---

## Наступний модуль

[Модуль 3.4: Моніторинг застосунків](module-3.4-monitoring.uk.md) — Моніторинг стану застосунків та використання ресурсів.
