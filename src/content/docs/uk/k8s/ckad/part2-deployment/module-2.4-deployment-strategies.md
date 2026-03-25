---
title: "\u041c\u043e\u0434\u0443\u043b\u044c 2.4: \u0421\u0442\u0440\u0430\u0442\u0435\u0433\u0456\u0457 \u0434\u0435\u043f\u043b\u043e\u0439\u043c\u0435\u043d\u0442\u0443"
sidebar:
  order: 4
  label: "Part 2: Deployment"
---
> **Складність**: `[MEDIUM]` — концептуальне розуміння з практичною реалізацією
>
> **Час на виконання**: 40–50 хвилин
>
> **Передумови**: Модуль 2.1 (Деплойменти), розуміння Сервісів

---

## Чому цей модуль важливий

Те, як ви розгортаєте нові версії, має значення. Погана стратегія деплойменту може спричинити простій, пошкодження даних або помилки, видимі користувачам. CKAD очікує, що ви розумієте різні стратегії деплойменту та коли використовувати кожну.

Ви зіткнетесь із такими питаннями:
- Реалізувати blue/green-деплоймент
- Налаштувати canary-реліз
- Налаштувати параметри ковзного оновлення
- Обрати відповідну стратегію для сценарію

> **Аналогія з рестораном**
>
> Ковзні оновлення — це як поступова заміна страв у меню — клієнти, що замовляють у різний час, можуть отримати дещо різне меню. Blue/green — це як мати дві повноцінні кухні — ви переводите всіх клієнтів на нову кухню одночасно. Canary-релізи — це як дати нову страву спочатку 10% клієнтів — якщо їм сподобається, її отримають усі.

---

## Огляд стратегій

### Порівняння

| Стратегія | Простій | Відкат | Вартість ресурсів | Ризик |
|-----------|---------|--------|-------------------|-------|
| **Rolling Update** | Немає | Повільний (поступовий) | Низька | Середній |
| **Recreate** | Так | Швидкий (перерозгортання старого) | Низька | Високий |
| **Blue/Green** | Немає | Миттєвий | 2x ресурсів | Низький |
| **Canary** | Немає | Миттєвий | Низька–середня | Дуже низький |

### Коли використовувати кожну

| Стратегія | Найкраще для |
|-----------|--------------|
| Rolling Update | Більшість застосунків, вибір за замовчуванням |
| Recreate | Застосунки, що не можуть працювати з кількома версіями |
| Blue/Green | Критичні застосунки, що потребують миттєвого відкату |
| Canary | Обережні деплойменти, тестування з реальним трафіком |

---

## Rolling Update (за замовчуванням)

Kubernetes поступово замінює старі поди новими.

### Конфігурація

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Може перевищити кількість реплік на 1
      maxUnavailable: 1  # Максимум 1 недоступний
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
```

### Поведінка оновлення

```
З replicas=4, maxSurge=1, maxUnavailable=1:

Старт:  [v1] [v1] [v1] [v1]     (4 працюють)
Крок 1: [v1] [v1] [v1] [--] [v2] (3 старих, 1 новий стартує)
Крок 2: [v1] [v1] [--] [v2] [v2] (2 старих, 2 нових)
Крок 3: [v1] [--] [v2] [v2] [v2] (1 старий, 3 нових)
Крок 4: [v2] [v2] [v2] [v2]     (4 нових, завершено)
```

### Запуск ковзного оновлення

```bash
# Оновити образ
k set image deploy/web-app nginx=nginx:1.21

# Спостерігати за розгортанням
k rollout status deploy/web-app

# Перевірити перехід подів
k get pods -l app=web -w
```

---

## Стратегія Recreate

Усі наявні поди знищуються перед створенням нових.

### Конфігурація

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database-app
spec:
  replicas: 1
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: database
  template:
    metadata:
      labels:
        app: database
    spec:
      containers:
      - name: postgres
        image: postgres:13
```

### Поведінка оновлення

```
Старт:  [v1] [v1] [v1]
Крок 1: [--] [--] [--]  (усі старі поди завершені)
Крок 2: [v2] [v2] [v2]  (усі нові поди створені)
```

### Коли використовувати

- Застосунки баз даних з вимогою єдиного запису
- Застосунки з блокуванням файлової системи
- Застосунки, що не можуть працювати з кількома версіями, які мають доступ до спільного стану
- Stateful-застосунки без належної підтримки міграції

---

## Blue/Green-деплоймент

Запуск двох ідентичних середовищ. Миттєве перемикання трафіку через оновлення селектора Сервісу.

### Реалізація

**Крок 1: Розгортання Blue (поточний)**

```yaml
# blue-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: app
        image: myapp:1.0
```

**Крок 2: Створення Сервісу (вказує на Blue)**

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
    version: blue  # Вказує на blue
  ports:
  - port: 80
```

**Крок 3: Розгортання Green (нова версія)**

```yaml
# green-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: app
        image: myapp:2.0
```

**Крок 4: Перемикання трафіку**

```bash
# Перемикнути сервіс на green
k patch svc myapp -p '{"spec":{"selector":{"version":"green"}}}'

# Миттєвий відкат, якщо потрібно
k patch svc myapp -p '{"spec":{"selector":{"version":"blue"}}}'
```

### Повний скрипт Blue/Green

```bash
# Розгорнути blue
k apply -f blue-deployment.yaml

# Створити сервіс, що вказує на blue
k apply -f service.yaml

# Протестувати blue
k run test --image=busybox --rm -it --restart=Never -- wget -qO- http://myapp

# Розгорнути green (без трафіку)
k apply -f green-deployment.yaml

# Протестувати green напряму (port-forward або окремий сервіс)
k port-forward deploy/app-green 8080:80 &
curl localhost:8080

# Перемикнути трафік на green
k patch svc myapp -p '{"spec":{"selector":{"version":"green"}}}'

# Якщо проблеми — миттєвий відкат
k patch svc myapp -p '{"spec":{"selector":{"version":"blue"}}}'

# Після підтвердження — видалити blue
k delete deploy app-blue
```

---

## Canary-деплоймент

Направлення невеликого відсотка трафіку на нову версію. Поступове збільшення у разі успіху.

### Реалізація з кількома Деплойментами

**Стабільний Деплоймент (90% трафіку)**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-stable
spec:
  replicas: 9  # 90% трафіку
  selector:
    matchLabels:
      app: myapp
      track: stable
  template:
    metadata:
      labels:
        app: myapp
        track: stable
    spec:
      containers:
      - name: app
        image: myapp:1.0
```

**Canary-деплоймент (10% трафіку)**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary
spec:
  replicas: 1  # 10% трафіку
  selector:
    matchLabels:
      app: myapp
      track: canary
  template:
    metadata:
      labels:
        app: myapp
        track: canary
    spec:
      containers:
      - name: app
        image: myapp:2.0
```

**Сервіс (маршрутизує до обох)**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp  # Збігається і зі stable, і з canary
  ports:
  - port: 80
```

### Розподіл трафіку

З 9 стабільними подами та 1 canary-подом:
- ~90% трафіку → stable (v1.0)
- ~10% трафіку → canary (v2.0)

### Поступове canary-розгортання

```bash
# Старт: 9 стабільних, 1 canary (10%)
k scale deploy app-canary --replicas=1
k scale deploy app-stable --replicas=9

# Збільшити canary до 25%
k scale deploy app-canary --replicas=3
k scale deploy app-stable --replicas=9

# Збільшити canary до 50%
k scale deploy app-canary --replicas=5
k scale deploy app-stable --replicas=5

# Повне розгортання (100% нова версія)
k scale deploy app-canary --replicas=10
k scale deploy app-stable --replicas=0

# Очищення: перейменувати canary на stable
k delete deploy app-stable
k patch deploy app-canary -p '{"metadata":{"name":"app-stable"}}'
```

---

## Параметри Rolling Update — глибоке занурення

### maxSurge

Максимальна кількість подів, що можуть бути створені понад бажану кількість:

```yaml
rollingUpdate:
  maxSurge: 25%      # 25% додаткових подів (за замовчуванням)
  # або
  maxSurge: 2        # 2 додаткових поди
```

### maxUnavailable

Максимум подів, що можуть бути недоступні під час оновлення:

```yaml
rollingUpdate:
  maxUnavailable: 25%  # 25% можуть бути вимкнені (за замовчуванням)
  # або
  maxUnavailable: 0    # Нульовий час простою
```

### Типові конфігурації

```yaml
# Нульовий час простою (консервативний)
rollingUpdate:
  maxSurge: 1
  maxUnavailable: 0

# Швидке оновлення (агресивний)
rollingUpdate:
  maxSurge: 100%
  maxUnavailable: 50%

# Збалансований (за замовчуванням)
rollingUpdate:
  maxSurge: 25%
  maxUnavailable: 25%
```

---

## Readiness Gates та проби

Правильні проби забезпечують гладке розгортання.

### Проба готовності для Деплойментів

```yaml
spec:
  template:
    spec:
      containers:
      - name: app
        image: myapp
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

Без проб готовності Kubernetes вважає поди готовими одразу — трафік може потрапити до подів, які ще не повністю ініціалізовані.

### minReadySeconds

```yaml
spec:
  minReadySeconds: 10  # Под має бути готовим 10 с, перш ніж буде вважатися доступним
```

Це додає буфер для виявлення ранніх збоїв.

---

## Практичні сценарії для іспиту

### Сценарій 1: Ковзне оновлення з нульовим простоєм

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # Ключове: ніколи не зменшувати нижче бажаного
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
        readinessProbe:  # Важливо для нульового простою
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 2
          periodSeconds: 3
```

### Сценарій 2: Швидке перемикання Blue/Green

```bash
# Створити blue-деплоймент
k create deploy app-blue --image=nginx:1.20 --replicas=3
k label deploy app-blue version=blue

# Додати мітку версії до шаблону подів
k patch deploy app-blue -p '{"spec":{"template":{"metadata":{"labels":{"version":"blue"}}}}}'

# Створити сервіс
k expose deploy app-blue --name=myapp --port=80 --selector=version=blue

# Розгорнути green
k create deploy app-green --image=nginx:1.21 --replicas=3
k patch deploy app-green -p '{"spec":{"template":{"metadata":{"labels":{"version":"green"}}}}}'

# Перемикнути на green
k patch svc myapp -p '{"spec":{"selector":{"version":"green"}}}'
```

---

## Чи знали ви?

- **Ковзні оновлення Kubernetes є самовідновлювальними.** Якщо новий под не проходить пробу готовності, розгортання автоматично призупиняється, запобігаючи повному розгортанню поганої версії.

- **Blue/green-деплойменти потребують 2x ресурсів** під час перемикання. Це їхній головний недолік, але дозволяє миттєвий відкат.

- **Canary-деплойменти виникли в Google.** Термін походить від «канарки у вугільній шахті» — шахтарі використовували канарок для виявлення токсичних газів. Якщо канарка гинула, шахтарі знали, що треба евакуюватися.

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| Немає проби готовності | Трафік на неготові поди | Завжди додавайте проби готовності |
| `maxUnavailable: 100%` | Усі поди знищуються одночасно | Тримайте на 25% або менше |
| Неправильний селектор сервісу для blue/green | Трафік не перемикається | Перевіряйте збіг міток |
| Не тестували canary окремо | Проблеми canary не виявлені | Спочатку протестуйте canary-поди напряму |
| Забули зменшити старий деплоймент | Марнування ресурсів | Зменшуйте після успішного перемикання |

---

## Тест

1. **Яка стратегія деплойменту знищує всі старі поди перед створенням нових?**
   <details>
   <summary>Відповідь</summary>
   `Recreate`. Усі наявні поди завершуються перед створенням нових подів, що спричиняє простій.
   </details>

2. **Як миттєво перемикнути трафік у blue/green?**
   <details>
   <summary>Відповідь</summary>
   Запатчити селектор Сервісу, щоб вказати на мітки нового деплойменту:
   `kubectl patch svc myapp -p '{"spec":{"selector":{"version":"green"}}}'`
   </details>

3. **З 10 репліками та maxSurge=2, maxUnavailable=1 — скільки подів може існувати під час оновлення?**
   <details>
   <summary>Відповідь</summary>
   Максимум 12 подів (10 + maxSurge 2). Мінімум 9 доступних подів (10 - maxUnavailable 1).
   </details>

4. **Як досягти 10% canary-трафіку за допомогою кількості подів?**
   <details>
   <summary>Відповідь</summary>
   Запустити 9 стабільних подів та 1 canary-под, із Сервісом, що вибирає обох. Трафік розподіляється приблизно пропорційно кількості подів: ~90% stable, ~10% canary.
   </details>

---

## Практична вправа

**Завдання**: Реалізувати всі три стратегії деплойменту.

**Частина 1: Rolling Update з параметрами**

```bash
# Створити деплоймент з кастомним ковзним оновленням
cat << 'EOF' | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rolling-demo
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: rolling
  template:
    metadata:
      labels:
        app: rolling
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
EOF

# Оновити та спостерігати (має бути макс. 5 подів)
k set image deploy/rolling-demo nginx=nginx:1.21
k get pods -l app=rolling -w

# Очищення
k delete deploy rolling-demo
```

**Частина 2: Blue/Green-деплоймент**

```bash
# Blue-деплоймент
cat << 'EOF' | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: demo
      version: blue
  template:
    metadata:
      labels:
        app: demo
        version: blue
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
EOF

# Сервіс, що вказує на blue
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Service
metadata:
  name: demo-svc
spec:
  selector:
    app: demo
    version: blue
  ports:
  - port: 80
EOF

# Green-деплоймент
cat << 'EOF' | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: demo
      version: green
  template:
    metadata:
      labels:
        app: demo
        version: green
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
EOF

# Перемикнути на green
k patch svc demo-svc -p '{"spec":{"selector":{"version":"green"}}}'

# Відкат на blue
k patch svc demo-svc -p '{"spec":{"selector":{"version":"blue"}}}'

# Очищення
k delete deploy blue green
k delete svc demo-svc
```

**Частина 3: Canary-деплоймент**

```bash
# Стабільний деплоймент (9 реплік)
cat << 'EOF' | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: canary-demo
      track: stable
  template:
    metadata:
      labels:
        app: canary-demo
        track: stable
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
EOF

# Canary-деплоймент (1 репліка = ~10%)
cat << 'EOF' | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: canary-demo
      track: canary
  template:
    metadata:
      labels:
        app: canary-demo
        track: canary
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
EOF

# Сервіс маршрутизує до обох
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Service
metadata:
  name: canary-svc
spec:
  selector:
    app: canary-demo
  ports:
  - port: 80
EOF

# Поступове збільшення canary
k scale deploy canary --replicas=3  # ~25%
k scale deploy stable --replicas=7

# Повне розгортання
k scale deploy canary --replicas=10
k scale deploy stable --replicas=0

# Очищення
k delete deploy stable canary
k delete svc canary-svc
```

---

## Практичні вправи

### Вправа 1: Конфігурація Rolling Update (Ціль: 3 хвилини)

```bash
# Створити зі специфічними налаштуваннями ковзного оновлення
k create deploy drill1 --image=nginx:1.20 --replicas=4

# Запатчити стратегію
k patch deploy drill1 -p '{"spec":{"strategy":{"type":"RollingUpdate","rollingUpdate":{"maxSurge":1,"maxUnavailable":0}}}}'

# Оновити та спостерігати
k set image deploy/drill1 nginx=nginx:1.21
k rollout status deploy/drill1

# Очищення
k delete deploy drill1
```

### Вправа 2: Стратегія Recreate (Ціль: 2 хвилини)

```bash
# Створити зі стратегією recreate
cat << 'EOF' | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: drill2
spec:
  replicas: 3
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: drill2
  template:
    metadata:
      labels:
        app: drill2
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
EOF

# Оновити (спостерігати, як усі поди спочатку завершуються)
k set image deploy/drill2 nginx=nginx:1.21
k get pods -l app=drill2 -w

# Очищення
k delete deploy drill2
```

### Вправа 3: Перемикання Blue/Green (Ціль: 4 хвилини)

```bash
# Створити blue
k create deploy blue --image=nginx:1.20 --replicas=2
k patch deploy blue -p '{"spec":{"selector":{"matchLabels":{"version":"blue"}},"template":{"metadata":{"labels":{"version":"blue"}}}}}'

# Сервіс
k expose deploy blue --name=app --port=80 --selector=version=blue

# Створити green
k create deploy green --image=nginx:1.21 --replicas=2
k patch deploy green -p '{"spec":{"selector":{"matchLabels":{"version":"green"}},"template":{"metadata":{"labels":{"version":"green"}}}}}'

# Перемикнути
k patch svc app -p '{"spec":{"selector":{"version":"green"}}}'

# Перевірити
k get ep app

# Очищення
k delete deploy blue green
k delete svc app
```

### Вправа 4: Відсоток Canary (Ціль: 3 хвилини)

```bash
# 10% canary
k create deploy stable --image=nginx:1.20 --replicas=9
k create deploy canary --image=nginx:1.21 --replicas=1

# Додати спільну мітку
k patch deploy stable -p '{"spec":{"template":{"metadata":{"labels":{"app":"myapp"}}}}}'
k patch deploy canary -p '{"spec":{"template":{"metadata":{"labels":{"app":"myapp"}}}}}'

# Сервіс для обох
k expose deploy stable --name=myapp --port=80 --selector=app=myapp

# Перевірити, що endpoints включають обох
k get ep myapp

# Очищення
k delete deploy stable canary
k delete svc myapp
```

### Вправа 5: Перевірка нульового простою (Ціль: 3 хвилини)

```bash
# Створити деплоймент з пробою готовності
cat << 'EOF' | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: drill5
spec:
  replicas: 3
  strategy:
    rollingUpdate:
      maxUnavailable: 0
  selector:
    matchLabels:
      app: drill5
  template:
    metadata:
      labels:
        app: drill5
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
        readinessProbe:
          httpGet:
            path: /
            port: 80
EOF

# Сервіс
k expose deploy drill5 --port=80

# Оновити (нульовий простій)
k set image deploy/drill5 nginx=nginx:1.21
k rollout status deploy/drill5

# Очищення
k delete deploy drill5
k delete svc drill5
```

### Вправа 6: Повний сценарій стратегії деплойменту (Ціль: 6 хвилин)

**Сценарій**: Production-деплоймент з canary-тестуванням.

```bash
# 1. Розгорнути стабільну версію
k create deploy prod --image=nginx:1.20 --replicas=5

# 2. Створити сервіс
k expose deploy prod --name=production --port=80

# 3. Створити canary (10%)
k create deploy canary --image=nginx:1.21 --replicas=1

# 4. Спрямувати сервіс на обох
k patch deploy prod -p '{"spec":{"template":{"metadata":{"labels":{"release":"production"}}}}}'
k patch deploy canary -p '{"spec":{"template":{"metadata":{"labels":{"release":"production"}}}}}'
k patch svc production -p '{"spec":{"selector":{"release":"production"}}}'

# 5. Протестувати canary
k logs -l app=canary

# 6. Поступове розгортання
k scale deploy canary --replicas=3
k scale deploy prod --replicas=3

# 7. Повне розгортання
k scale deploy canary --replicas=5
k scale deploy prod --replicas=0

# 8. Очищення
k delete deploy prod canary
k delete svc production
```

---

## Наступний модуль

[Кумулятивний тест Частини 2](part2-cumulative-quiz.md) — перевірте свої знання з розгортання застосунків.
