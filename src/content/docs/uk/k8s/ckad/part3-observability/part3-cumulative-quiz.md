---
title: "\u041a\u0443\u043c\u0443\u043b\u044f\u0442\u0438\u0432\u043d\u0438\u0439 \u0442\u0435\u0441\u0442 \u0427\u0430\u0441\u0442\u0438\u043d\u0438 3: \u0421\u043f\u043e\u0441\u0442\u0435\u0440\u0435\u0436\u0443\u0432\u0430\u043d\u0456\u0441\u0442\u044c \u0442\u0430 \u043e\u0431\u0441\u043b\u0443\u0433\u043e\u0432\u0443\u0432\u0430\u043d\u043d\u044f \u0437\u0430\u0441\u0442\u043e\u0441\u0443\u043d\u043a\u0456\u0432"
sidebar:
  order: 6
---
> **Обмеження часу**: 20 хвилин (імітація тиску іспиту)
>
> **Прохідний бал**: 80% (8/10 запитань)

Цей тест перевіряє ваше володіння:
- Пробами застосунків (liveness, readiness, startup)
- Логуванням контейнерів
- Технікам налагодження
- Моніторингом за допомогою kubectl top
- Застаріванням API

---

## Інструкції

1. Спробуйте кожне запитання без підглядання у відповіді
2. Засікайте час — швидкість важлива для CKAD
3. Використовуйте лише `kubectl` та `kubernetes.io/docs`
4. Перевірте відповіді після завершення всіх запитань

---

## Запитання

### Запитання 1: Проба Liveness
**[2 хвилини]**

Створіть Під з назвою `health-check` з nginx, який:
- Має HTTP liveness пробу на шляху `/` порт `80`
- Перевіряє кожні 10 секунд
- Чекає 5 секунд перед першою перевіркою

<details>
<summary>Відповідь</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: health-check
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
```

</details>

---

### Запитання 2: Проба Readiness
**[2 хвилини]**

Під `webapp` має налаштовану readiness пробу, але ніколи не стає Ready. Як ви будете досліджувати?

<details>
<summary>Відповідь</summary>

```bash
# Перевірити статус пода
k get pod webapp

# Describe для перегляду конфігурації проби та подій
k describe pod webapp | grep -A10 Readiness
k describe pod webapp | tail -20

# Перевірити ендпоінти (під не повинен бути в ендпоінтах, якщо не готовий)
k get endpoints

# Перевірити, чи правильний шлях/порт проби
k exec webapp -- curl -s localhost:8080/ready
```

</details>

---

### Запитання 3: Комбіновані проби
**[3 хвилини]**

Створіть Deployment з назвою `api-server` з 2 репліками, який:
- Використовує образ `nginx`
- Має пробу startup: HTTP GET `/` порт 80, поріг невдач 30, період 10с
- Має пробу liveness: HTTP GET `/` порт 80, період 10с
- Має пробу readiness: HTTP GET `/` порт 80, період 5с

<details>
<summary>Відповідь</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
    spec:
      containers:
      - name: nginx
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
```

</details>

---

### Запитання 4: Логи контейнерів
**[1 хвилина]**

Отримайте останні 50 рядків логів попереднього екземпляра контейнера `app` у поді `crashing-pod`.

<details>
<summary>Відповідь</summary>

```bash
k logs crashing-pod -c app --previous --tail=50
```

</details>

---

### Запитання 5: Логи кількох контейнерів
**[2 хвилини]**

Під `multi-app` має контейнери з назвами `frontend` та `backend`. Увімкніть потокове читання логів з обох контейнерів.

<details>
<summary>Відповідь</summary>

```bash
# Усі контейнери одразу
k logs multi-app --all-containers -f

# Або окремо
k logs multi-app -c frontend -f &
k logs multi-app -c backend -f
```

</details>

---

### Запитання 6: Налагодження CrashLoopBackOff
**[2 хвилини]**

Під знаходиться у стані CrashLoopBackOff. Який ваш процес налагодження?

<details>
<summary>Відповідь</summary>

```bash
# 1. Перевірити поточний статус
k get pod crashing-pod

# 2. Отримати логи екземпляра, що впав
k logs crashing-pod --previous

# 3. Перевірити код виходу та події
k describe pod crashing-pod | grep -A5 "Last State"
k describe pod crashing-pod | tail -15

# 4. Перевірити, чи не занадто агресивна проба liveness
k describe pod crashing-pod | grep -A5 Liveness

# 5. За потреби перевірити конфігурацію контейнера
k get pod crashing-pod -o yaml | grep -A20 containers
```

</details>

---

### Запитання 7: Налагодження Service
**[2 хвилини]**

Service `web-svc` не має ендпоінтів. Як знайти і виправити проблему?

<details>
<summary>Відповідь</summary>

```bash
# Перевірити ендпоінти
k get endpoints web-svc

# Отримати селектор сервісу
k describe svc web-svc | grep Selector

# Отримати мітки подів
k get pods --show-labels

# Якщо мітки не збігаються, виправити сервіс або поди
# Приклад: Виправити селектор сервісу
k patch svc web-svc -p '{"spec":{"selector":{"app":"correct-label"}}}'

# Перевірити
k get endpoints web-svc
```

</details>

---

### Запитання 8: Моніторинг ресурсів
**[2 хвилини]**

Знайдіть 5 подів з найбільшим використанням пам'яті в усіх просторах імен.

<details>
<summary>Відповідь</summary>

```bash
k top pods -A --sort-by=memory | head -6
```

(head -6, бо перший рядок — заголовок)

</details>

---

### Запитання 9: Пошук версій API
**[1 хвилина]**

Які поточні версії API для цих ресурсів?
- Ingress
- CronJob
- NetworkPolicy

<details>
<summary>Відповідь</summary>

```bash
# Швидкий пошук
k explain ingress | grep VERSION
# networking.k8s.io/v1

k explain cronjob | grep VERSION
# batch/v1

k explain networkpolicy | grep VERSION
# networking.k8s.io/v1
```

</details>

---

### Запитання 10: Exec проба
**[2 хвилини]**

Створіть Під з назвою `file-check` з busybox, який:
- Виконує `sleep 3600`
- Має liveness пробу, що перевіряє існування файлу `/tmp/healthy`
- Проба виконується кожні 5 секунд, початкова затримка 10 секунд

<details>
<summary>Відповідь</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: file-check
spec:
  containers:
  - name: busybox
    image: busybox
    command: ['sh', '-c', 'touch /tmp/healthy && sleep 3600']
    livenessProbe:
      exec:
        command:
        - cat
        - /tmp/healthy
      initialDelaySeconds: 10
      periodSeconds: 5
EOF
```

</details>

---

## Оцінювання

| Правильних відповідей | Бал | Статус |
|-----------------------|-----|--------|
| 10/10 | 100% | Чудово — Готові до іспиту |
| 8–9/10 | 80–90% | Добре — Потрібен невеликий повтор |
| 6–7/10 | 60–70% | Повторіть слабкі місця |
| <6/10 | <60% | Перегляньте модулі Частини 3 |

---

## Очищення

```bash
k delete pod health-check file-check 2>/dev/null
k delete deploy api-server 2>/dev/null
```

---

## Ключові висновки

Якщо ваш бал нижче 80%, повторіть ці теми:

- **Пропущено З1–3**: Повторіть Модуль 3.1 (Проби) — типи проб та конфігурація
- **Пропущено З4–5**: Повторіть Модуль 3.2 (Логування) — команди для логів та кілька контейнерів
- **Пропущено З6–7**: Повторіть Модуль 3.3 (Налагодження) — системне усунення несправностей
- **Пропущено З8**: Повторіть Модуль 3.4 (Моніторинг) — команди kubectl top
- **Пропущено З9**: Повторіть Модуль 3.5 (Застарівання API) — поточні версії
- **Пропущено З10**: Повторіть Модуль 3.1 (Проби) — exec проби

---

## Наступна частина

[Частина 4: Середовище, конфігурація та безпека застосунків](/uk/k8s/ckad/part4-environment/module-4.1-configmaps/) — ConfigMaps, Secrets, SecurityContexts та інше.
