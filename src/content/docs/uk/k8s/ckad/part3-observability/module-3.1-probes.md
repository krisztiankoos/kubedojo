---
title: "\u041c\u043e\u0434\u0443\u043b\u044c 3.1: \u041f\u0440\u043e\u0431\u0438 \u0437\u0430\u0441\u0442\u043e\u0441\u0443\u043d\u043a\u0456\u0432"
slug: uk/k8s/ckad/part3-observability/module-3.1-probes
sidebar: 
  order: 1
lab: 
  id: ckad-3.1-probes
  url: https://killercoda.com/kubedojo/scenario/ckad-3.1-probes
  duration: "30 min"
  difficulty: intermediate
  environment: kubernetes
---
> **Складність**: `[MEDIUM]` — Критична тема іспиту з кількома типами проб
>
> **Час на виконання**: 40–50 хвилин
>
> **Передумови**: Модуль 1.1 (Поди), розуміння життєвого циклу контейнера

---

## Що ви зможете робити

Після завершення цього модуля ви зможете:
- **Налаштувати** проби liveness, readiness та startup з відповідними порогами та часовими параметрами
- **Діагностувати** цикли перезапуску Підів та проблеми маршрутизації трафіку, спричинені неправильно налаштованими пробами
- **Пояснити** різницю між пробами liveness, readiness та startup і коли кожна застосовується
- **Реалізувати** проби HTTP, TCP та exec, підібрані до можливостей перевірки здоров'я вашого застосунку

---

## Чому цей модуль важливий

Проби повідомляють Kubernetes, як перевірити, чи ваш застосунок живий, чи готовий отримувати трафік, чи потребує більше часу на запуск. Без проб Kubernetes не може дізнатися, чи ваш застосунок насправді працює — він лише знає, чи процес контейнера запущений.

Іспит CKAD часто перевіряє проби, оскільки вони необхідні для продакшн-застосунків. Очікуйте запитання про:
- Налаштування проб liveness, readiness та startup
- Вибір між HTTP, TCP та exec пробами
- Встановлення відповідних порогів і часових параметрів

> **Аналогія з медичним оглядом**
>
> Уявіть проби як систему моніторингу в лікарні. **Проба liveness** перевіряє, чи пацієнт живий (якщо ні — екстрена допомога). **Проба readiness** перевіряє, чи пацієнт може приймати відвідувачів (якщо ні — відвідувачів поки не пускають). **Проба startup** дає пацієнту час прокинутися після операції, перш ніж перевіряти життєві показники. Кожна має свою мету, і використання невідповідної спричиняє проблеми.

---

## Три типи проб

### Проба Liveness

**Запитання, на яке вона відповідає**: «Чи застосунок живий, чи слід його перезапустити?»

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 10
  failureThreshold: 3
```

**Коли liveness не проходить**: Kubernetes вбиває контейнер і перезапускає його.

**Використовуйте, коли**:
- Застосунок може зависнути (deadlock, нескінченний цикл)
- Перезапуск вирішить проблему
- Вам потрібне автоматичне відновлення після помилок застосунку

### Проба Readiness

**Запитання, на яке вона відповідає**: «Чи застосунок готовий отримувати трафік?»

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
```

**Коли readiness не проходить**: Під видаляється з ендпоінтів Service (без трафіку).

**Використовуйте, коли**:
- Застосунок потребує часу на прогрів (завантаження кешів, з'єднання з БД)
- Застосунок тимчасово перевантажений
- Залежні сервіси недоступні

### Проба Startup

**Запитання, на яке вона відповідає**: «Чи застосунок завершив запуск?»

```yaml
startupProbe:
  httpGet:
    path: /healthz
    port: 8080
  failureThreshold: 30
  periodSeconds: 10
```

**Коли startup проходить успішно**: Проби liveness та readiness починають працювати.

**Використовуйте, коли**:
- Застосунок має тривалий/непередбачуваний час запуску
- Інакше довелося б встановити дуже високий `initialDelaySeconds` для liveness
- Застарілі застосунки з непередбачуваним часом завантаження

---

## Механізми проб

### HTTP GET проба

Найпоширеніша для веб-застосунків:

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
    httpHeaders:
    - name: Custom-Header
      value: Awesome
  initialDelaySeconds: 10
  periodSeconds: 5
```

- Успіх: HTTP-статус 200–399
- Невдача: Будь-який інший статус або таймаут

### TCP Socket проба

Для не-HTTP сервісів (бази даних, черги повідомлень):

```yaml
livenessProbe:
  tcpSocket:
    port: 3306
  initialDelaySeconds: 15
  periodSeconds: 10
```

- Успіх: З'єднання встановлено
- Невдача: З'єднання відхилено або таймаут

### Exec проба

Виконує команду всередині контейнера:

```yaml
livenessProbe:
  exec:
    command:
    - cat
    - /tmp/healthy
  initialDelaySeconds: 5
  periodSeconds: 5
```

- Успіх: Код виходу 0
- Невдача: Ненульовий код виходу

---

## Параметри проб

| Параметр | Опис | Типово |
|----------|------|--------|
| `initialDelaySeconds` | Очікування перед першою пробою | 0 |
| `periodSeconds` | Як часто виконувати пробу | 10 |
| `timeoutSeconds` | Таймаут проби | 1 |
| `successThreshold` | Успіхів для відновлення після невдачі | 1 |
| `failureThreshold` | Невдач перед дією | 3 |

### Розрахунок часових параметрів проб

**Час до першої проби**: `initialDelaySeconds`

**Час до дії при невдачі**:
`initialDelaySeconds + (failureThreshold × periodSeconds)`

Приклад з типовими значеннями:
- `initialDelaySeconds: 0`
- `periodSeconds: 10`
- `failureThreshold: 3`
- Час до перезапуску: `0 + (3 × 10) = 30 секунд`

---

## Типові шаблони

### Комбіновані проби для веб-застосунку

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: webapp
spec:
  containers:
  - name: app
    image: myapp:v1
    ports:
    - containerPort: 8080
    startupProbe:
      httpGet:
        path: /healthz
        port: 8080
      failureThreshold: 30
      periodSeconds: 10
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      periodSeconds: 10
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      periodSeconds: 5
      failureThreshold: 3
```

### Перевірка з'єднання з базою даних

```yaml
livenessProbe:
  exec:
    command:
    - pg_isready
    - -U
    - postgres
  initialDelaySeconds: 30
  periodSeconds: 10
```

### gRPC перевірка стану

```yaml
livenessProbe:
  grpc:
    port: 50051
  initialDelaySeconds: 10
  periodSeconds: 10
```

---

## Порівняння проб

```
┌─────────────────────────────────────────────────────────────┐
│                    Порівняння проб                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Проба Startup                                              │
│  ├── Виконується ПЕРШОЮ (перед liveness/readiness)          │
│  ├── Невдача: Продовжує спроби до порогу                   │
│  └── Успіх: Вмикає проби liveness/readiness                │
│                                                             │
│  Проба Liveness                                             │
│  ├── Виконується ПІСЛЯ успіху startup                      │
│  ├── Невдача: ВБИТИ та ПЕРЕЗАПУСТИТИ контейнер             │
│  └── Успіх: Контейнер живий, нічого не робити              │
│                                                             │
│  Проба Readiness                                            │
│  ├── Виконується ПІСЛЯ успіху startup                      │
│  ├── Невдача: ВИДАЛИТИ з ендпоінтів Service                │
│  └── Успіх: ДОДАТИ до ендпоінтів Service                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Прийоми для іспиту

### Додати пробу до наявного Pod YAML

```bash
# Згенерувати под без проб
k run webapp --image=nginx --port=80 --dry-run=client -o yaml > pod.yaml

# Додати проби вручну (найшвидше на іспиті)
```

### Швидкий під з Liveness пробою

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: liveness-demo
spec:
  containers:
  - name: app
    image: nginx
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 10
EOF
```

### Перевірка роботи проб

```bash
# Перевірити події пода на активність проб
k describe pod webapp | grep -A 10 Events

# Спостерігати за перезапусками (невдачі liveness)
k get pod webapp -w

# Перевірити членство в ендпоінтах (readiness)
k get endpoints myservice
```

---

## Чи знали ви?

- **Проба startup була додана в Kubernetes 1.16**, щоб вирішити проблему «застарілих застосунків». До цього доводилося ставити величезні `initialDelaySeconds` для проб liveness, що затримувало виявлення реальних збоїв.

- **Exec проба виконується всередині контейнера**, тобто вона має доступ до файлової системи та середовища контейнера. Це потужний інструмент для власних перевірок стану, але додає навантаження.

- **HTTP проби слідують за перенаправленнями (3xx).** Якщо ваш `/healthz` перенаправляє на `/login`, проба бачить `200 OK` від кінцевого пункту призначення і вважається успішною.

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| Занадто агресивна проба liveness | Вбиває справні повільні застосунки | Використовуйте пробу startup для повільного запуску |
| Однакова проба для liveness і readiness | Змішані різні цілі | Окремі ендпоінти: `/healthz` проти `/ready` |
| Readiness перевіряє зовнішні залежності | Увесь кластер падає, якщо одна залежність недоступна | Перевіряйте лише те, що контролює цей під |
| Без `initialDelaySeconds` | Контейнер вбито до запуску застосунку | Дайте застосунку час на ініціалізацію |
| `timeoutSeconds: 1` для повільних перевірок | Таймаути спричиняють перезапуски | Збільште для повільних ендпоінтів перевірки стану |

---

## Тест

1. **Що відбувається, коли проба liveness не проходить?**
   <details>
   <summary>Відповідь</summary>
   Kubernetes вбиває контейнер і перезапускає його. Лічильник перезапусків збільшується.
   </details>

2. **Що відбувається, коли проба readiness не проходить?**
   <details>
   <summary>Відповідь</summary>
   Під видаляється з ендпоінтів Service (перестає отримувати трафік). Контейнер НЕ перезапускається.
   </details>

3. **Коли варто використовувати пробу startup замість високого `initialDelaySeconds`?**
   <details>
   <summary>Відповідь</summary>
   Використовуйте пробу startup для застосунків із змінним або тривалим часом запуску. Проба startup дозволяє liveness використовувати агресивні налаштування після запуску, тоді як високий `initialDelaySeconds` затримує все виявлення збоїв.
   </details>

4. **Яке типове значення `failureThreshold` для проб?**
   <details>
   <summary>Відповідь</summary>
   3 послідовні невдачі перед виконанням дії.
   </details>

---

## Практична вправа

**Завдання**: Налаштуйте всі три типи проб для веб-застосунку.

**Підготовка:**
```bash
# Створити тестовий под з тривалим запуском
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: probe-demo
  labels:
    app: probe-demo
spec:
  containers:
  - name: app
    image: nginx
    ports:
    - containerPort: 80
    startupProbe:
      httpGet:
        path: /
        port: 80
      failureThreshold: 10
      periodSeconds: 5
    livenessProbe:
      httpGet:
        path: /
        port: 80
      periodSeconds: 10
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /
        port: 80
      periodSeconds: 5
      failureThreshold: 2
EOF
```

**Перевірка:**
```bash
# Спостерігати за статусом пода
k get pod probe-demo -w

# Перевірити події проб
k describe pod probe-demo | grep -A 15 Events

# Створити сервіс
k expose pod probe-demo --port=80

# Перевірити ендпоінти
k get ep probe-demo
```

**Зламайте (для навчання):**
```bash
# Змусити liveness не пройти — зайдіть в под і зламайте nginx
k exec probe-demo -- rm /usr/share/nginx/html/index.html

# Спостерігайте за перезапуском
k get pod probe-demo -w
```

**Очищення:**
```bash
k delete pod probe-demo
k delete svc probe-demo
```

---

## Практичні вправи

### Вправа 1: HTTP Liveness проба (Ціль: 2 хвилини)

```bash
# Створити під з HTTP liveness пробою
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill1
spec:
  containers:
  - name: nginx
    image: nginx
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 10
EOF

# Перевірити
k describe pod drill1 | grep Liveness

# Очищення
k delete pod drill1
```

### Вправа 2: Exec проба (Ціль: 2 хвилини)

```bash
# Створити під з exec пробою
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill2
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'touch /tmp/healthy && sleep 3600']
    livenessProbe:
      exec:
        command:
        - cat
        - /tmp/healthy
      initialDelaySeconds: 5
      periodSeconds: 5
EOF

# Перевірити запуск
k get pod drill2

# Очищення
k delete pod drill2
```

### Вправа 3: TCP проба (Ціль: 2 хвилини)

```bash
# Створити під з TCP пробою
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill3
spec:
  containers:
  - name: redis
    image: redis
    livenessProbe:
      tcpSocket:
        port: 6379
      initialDelaySeconds: 10
      periodSeconds: 5
EOF

# Перевірити
k describe pod drill3 | grep Liveness

# Очищення
k delete pod drill3
```

### Вправа 4: Readiness проба (Ціль: 3 хвилини)

```bash
# Створити deployment з readiness пробою
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
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 2
          periodSeconds: 3
EOF

# Створити сервіс
k expose deploy drill4 --port=80

# Перевірити ендпоінти (повинно бути 2)
k get endpoints drill4

# Очищення
k delete deploy drill4
k delete svc drill4
```

### Вправа 5: Комбіновані проби (Ціль: 4 хвилини)

```bash
# Створити під з startup, liveness та readiness
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill5
  labels:
    app: drill5
spec:
  containers:
  - name: app
    image: nginx
    ports:
    - containerPort: 80
    startupProbe:
      httpGet:
        path: /
        port: 80
      failureThreshold: 30
      periodSeconds: 10
    livenessProbe:
      httpGet:
        path: /
        port: 80
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /
        port: 80
      periodSeconds: 5
EOF

# Перевірити всі проби
k describe pod drill5 | grep -E "Liveness|Readiness|Startup"

# Створити сервіс і перевірити ендпоінт
k expose pod drill5 --port=80
k get ep drill5

# Очищення
k delete pod drill5 svc drill5
```

### Вправа 6: Сценарій з невдалою пробою (Ціль: 5 хвилин)

**Сценарій**: Відлагодити під, який постійно перезапускається.

```bash
# Створити навмисно зламану пробу
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill6
spec:
  containers:
  - name: app
    image: nginx
    livenessProbe:
      httpGet:
        path: /nonexistent
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 3
      failureThreshold: 2
EOF

# Спостерігати за перезапусками
k get pod drill6 -w

# Після кількох перезапусків перевірити події
k describe pod drill6 | tail -20

# Виправити пробу
k delete pod drill6
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill6
spec:
  containers:
  - name: app
    image: nginx
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 10
EOF

# Перевірити виправлення
k get pod drill6

# Очищення
k delete pod drill6
```

---

## Наступний модуль

[Модуль 3.2: Логування контейнерів](/uk/k8s/ckad/part3-observability/module-3.2-logging/) — Доступ, керування та усунення несправностей логів контейнерів.
