---
title: "\u041c\u043e\u0434\u0443\u043b\u044c 4.5: \u0421\u0435\u0440\u0432\u0456\u0441\u043d\u0456 \u0430\u043a\u0430\u0443\u043d\u0442\u0438"
sidebar:
  order: 5
  label: "Part 4: Environment"
---
> **Складність**: `[MEDIUM]` — Важливо для доступу до API та ідентифікації
>
> **Час на виконання**: 35–45 хвилин
>
> **Передумови**: Модуль 4.4 (SecurityContexts), розуміння основ RBAC

---

## Чому цей модуль важливий

Сервісні акаунти надають ідентифікацію подам для взаємодії з API Kubernetes. Коли вашому застосунку потрібно отримати список подів, створити ConfigMaps або отримати доступ до інших ресурсів кластера, він використовує облікові дані свого Сервісного акаунта.

На іспиті CKAD перевіряють:
- Створення та призначення Сервісних акаунтів
- Розуміння монтування токенів
- Налаштування ідентифікації пода
- Відмова від автоматичного монтування токенів

> **Аналогія з бейджем працівника**
>
> Сервісні акаунти — це як бейджі працівників. Кожен працівник (під) отримує бейдж (Сервісний акаунт), який ідентифікує його для систем безпеки (API-сервер). Стандартний бейдж (Сервісний акаунт за замовчуванням) дає базовий доступ, але конкретні ролі потребують конкретних бейджів. Без бейджа ви не потрапите далі лобі.

---

## Основи Сервісних акаунтів

### Сервісний акаунт за замовчуванням

Кожен простір імен має Сервісний акаунт `default`:

```bash
# Переглянути Сервісний акаунт за замовчуванням
k get serviceaccount
# NAME      SECRETS   AGE
# default   0         10d

# Описати його
k describe sa default
```

### Кожен під отримує Сервісний акаунт

```bash
# Перевірити Сервісний акаунт пода
k get pod my-pod -o jsonpath='{.spec.serviceAccountName}'
# default

# Або через describe
k describe pod my-pod | grep "Service Account"
```

---

## Створення Сервісних акаунтів

### Імперативно

```bash
# Створити Сервісний акаунт
k create serviceaccount my-app-sa

# У конкретному просторі імен
k create sa my-app-sa -n my-namespace
```

### Декларативно

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: default
```

---

## Призначення Сервісних акаунтів подам

### У специфікації пода

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  serviceAccountName: my-app-sa    # Використовувати цей Сервісний акаунт
  containers:
  - name: app
    image: nginx
```

### У Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      serviceAccountName: my-app-sa    # Шаблон пода використовує цей SA
      containers:
      - name: app
        image: nginx
```

---

## Монтування токенів

### Автоматичне монтування токенів (за замовчуванням)

За замовчуванням Kubernetes монтує токен у `/var/run/secrets/kubernetes.io/serviceaccount/`:

```bash
# Переглянути файли змонтованого токена
k exec my-pod -- ls /var/run/secrets/kubernetes.io/serviceaccount/
# ca.crt
# namespace
# token

# Переглянути токен
k exec my-pod -- cat /var/run/secrets/kubernetes.io/serviceaccount/token
```

### Вміст токена

| Файл | Призначення |
|------|-------------|
| `token` | JWT-токен для автентифікації в API |
| `ca.crt` | Сертифікат CA для перевірки API-сервера |
| `namespace` | Простір імен пода |

### Вимкнення автоматичного монтування токенів

Для подів, яким не потрібен доступ до API:

**На рівні пода:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: no-api-access
spec:
  automountServiceAccountToken: false    # Не монтувати токен
  containers:
  - name: app
    image: nginx
```

**На рівні Сервісного акаунта:**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: restricted-sa
automountServiceAccountToken: false    # За замовчуванням для подів з цим SA
```

---

## Типи токенів Сервісних акаунтів

### Прив'язані токени (Kubernetes 1.22+)

Сучасні токени:
- **Обмежені в часі** — закінчуються автоматично
- **Прив'язані до аудиторії** — дійсні лише для конкретних цілей
- **Прив'язані до об'єкта** — прив'язані до конкретного пода

```yaml
# Запит токена з конкретною аудиторією
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  serviceAccountName: my-app-sa
  containers:
  - name: app
    image: my-app
    volumeMounts:
    - name: token
      mountPath: /var/run/secrets/tokens
  volumes:
  - name: token
    projected:
      sources:
      - serviceAccountToken:
          path: token
          expirationSeconds: 3600    # 1 година
          audience: my-audience
```

### Застарілі токени (до 1.24)

До Kubernetes 1.24 довготривалі токени зберігалися в Secrets. Це застаріло.

```bash
# Старий спосіб (застарілий) — НЕ використовуйте
k create token my-app-sa    # Створює короткотривалий токен натомість
```

---

## Візуалізація

```
┌─────────────────────────────────────────────────────────────┐
│            Потік Сервісного акаунта                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Створити Сервісний акаунт                               │
│  ┌─────────────────────────────────┐                       │
│  │ k create sa my-app-sa           │                       │
│  └─────────────────────────────────┘                       │
│                    │                                        │
│                    ▼                                        │
│  2. Призначити поду                                        │
│  ┌─────────────────────────────────┐                       │
│  │ spec:                           │                       │
│  │   serviceAccountName: my-app-sa │                       │
│  └─────────────────────────────────┘                       │
│                    │                                        │
│                    ▼                                        │
│  3. Токен монтується автоматично                           │
│  ┌─────────────────────────────────┐                       │
│  │ /var/run/secrets/kubernetes.io/ │                       │
│  │   serviceaccount/               │                       │
│  │   ├── token     ← JWT-токен     │                       │
│  │   ├── ca.crt    ← серт. CA API  │                       │
│  │   └── namespace ← простір імен  │                       │
│  └─────────────────────────────────┘                       │
│                    │                                        │
│                    ▼                                        │
│  4. Під використовує токен для доступу до API              │
│  ┌─────────────────────────────────┐                       │
│  │ curl -H "Authorization:         │                       │
│  │   Bearer $(cat /var/run/...)"   │                       │
│  │   https://kubernetes/api/v1/... │                       │
│  └─────────────────────────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Використання токенів Сервісних акаунтів

### Зсередини пода

```bash
# Всередині пода — запит до API
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
NAMESPACE=$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)

# Отримати список подів у поточному просторі імен
curl -s --cacert $CACERT \
  -H "Authorization: Bearer $TOKEN" \
  https://kubernetes.default.svc/api/v1/namespaces/$NAMESPACE/pods
```

### З kubectl

```bash
# Створити короткотривалий токен
k create token my-app-sa

# Створити токен з тривалістю
k create token my-app-sa --duration=1h
```

---

## Сервісні акаунти та RBAC

Сервісні акаунти самі по собі не надають дозволів. Потрібен RBAC:

```yaml
# 1. Створити Сервісний акаунт
apiVersion: v1
kind: ServiceAccount
metadata:
  name: pod-reader-sa
---
# 2. Створити Role з дозволами
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
# 3. Прив'язати Role до Сервісного акаунта
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
subjects:
- kind: ServiceAccount
  name: pod-reader-sa
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

---

## Швидка довідка

```bash
# Створити Сервісний акаунт
k create sa NAME

# Переглянути Сервісні акаунти
k get sa
k describe sa NAME

# Призначити поду
spec:
  serviceAccountName: NAME

# Вимкнути автомонтування
spec:
  automountServiceAccountToken: false

# Створити короткотривалий токен
k create token NAME

# Перевірити SA пода
k get pod POD -o jsonpath='{.spec.serviceAccountName}'
```

---

## Чи знали ви?

- **Сервісний акаунт за замовчуванням не має спеціальних дозволів.** Він нічого не може робити, поки ви не додасте правила RBAC. Це безпечно за замовчуванням.

- **Токени — це JWT.** Ви можете декодувати їх, щоб побачити претензії: `cat token | cut -d. -f2 | base64 -d | jq`

- **Сервісні акаунти мають простір імен.** Сервісний акаунт у просторі імен A не може використовуватися подами у просторі імен B.

- **`kubectl auth can-i --as=system:serviceaccount:default:my-sa`** дозволяє перевірити, що може робити Сервісний акаунт.

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| Очікування дозволів у SA за замовчуванням | Виклики API не вдаються з 403 | Створіть RBAC для SA |
| Використання застарілих довготривалих токенів | Ризик безпеки | Використовуйте `k create token` або прив'язані токени |
| Не вимикати монтування, коли не потрібно | Зайва поверхня атаки | Встановіть `automountServiceAccountToken: false` |
| Неправильна назва Сервісного акаунта | Під використовує SA за замовчуванням | Перевірте через `k describe pod` |
| Плутати SA з RBAC | SA сам по собі не надає доступ | Потрібні SA + Role + RoleBinding |

---

## Тест

1. **Як призначити Сервісний акаунт поду?**
   <details>
   <summary>Відповідь</summary>
   Додайте `serviceAccountName: my-sa` до специфікації пода.
   </details>

2. **Де монтується токен Сервісного акаунта в поді?**
   <details>
   <summary>Відповідь</summary>
   `/var/run/secrets/kubernetes.io/serviceaccount/`, що містить файли `token`, `ca.crt` та `namespace`.
   </details>

3. **Як заборонити поду доступ до API?**
   <details>
   <summary>Відповідь</summary>
   Встановіть `automountServiceAccountToken: false` у специфікації пода або Сервісного акаунта.
   </details>

4. **Чи надає створення Сервісного акаунта автоматично якісь дозволи?**
   <details>
   <summary>Відповідь</summary>
   Ні. Сервісні акаунти не мають дозволів за замовчуванням. Потрібно створити правила RBAC (Role/ClusterRole + RoleBinding/ClusterRoleBinding) для надання дозволів.
   </details>

---

## Практична вправа

**Завдання**: Створити та використати Сервісний акаунт.

**Частина 1: Створення Сервісного акаунта**
```bash
k create sa app-sa

# Перевірити
k get sa app-sa
```

**Частина 2: Під з власним Сервісним акаунтом**
```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: sa-demo
spec:
  serviceAccountName: app-sa
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'cat /var/run/secrets/kubernetes.io/serviceaccount/namespace && sleep 3600']
EOF

# Перевірити призначений SA
k get pod sa-demo -o jsonpath='{.spec.serviceAccountName}'
echo

# Перевірити монтування токена
k exec sa-demo -- ls /var/run/secrets/kubernetes.io/serviceaccount/
```

**Частина 3: Під без монтування токена**
```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: no-token
spec:
  serviceAccountName: app-sa
  automountServiceAccountToken: false
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'ls /var/run/secrets 2>&1 || echo "No secrets mounted" && sleep 3600']
EOF

k logs no-token
# Має показати: No secrets mounted (або директорія не знайдена)
```

**Очищення:**
```bash
k delete pod sa-demo no-token
k delete sa app-sa
```

---

## Практичні вправи

### Вправа 1: Створення Сервісного акаунта (Ціль: 1 хвилина)

```bash
k create sa drill1-sa
k get sa drill1-sa
k delete sa drill1-sa
```

### Вправа 2: Під із Сервісним акаунтом (Ціль: 2 хвилини)

```bash
k create sa drill2-sa

cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill2
spec:
  serviceAccountName: drill2-sa
  containers:
  - name: app
    image: busybox
    command: ['sleep', '3600']
EOF

k get pod drill2 -o jsonpath='{.spec.serviceAccountName}'
echo

k delete pod drill2 sa drill2-sa
```

### Вправа 3: Перевірка розташування токена (Ціль: 2 хвилини)

```bash
k run drill3 --image=busybox --restart=Never -- sleep 3600

k exec drill3 -- ls /var/run/secrets/kubernetes.io/serviceaccount/
k exec drill3 -- cat /var/run/secrets/kubernetes.io/serviceaccount/namespace

k delete pod drill3
```

### Вправа 4: Вимкнення монтування токена (Ціль: 2 хвилини)

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill4
spec:
  automountServiceAccountToken: false
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'ls /var/run/secrets/kubernetes.io/serviceaccount 2>&1; sleep 3600']
EOF

k logs drill4
# Має показати помилку (директорія не існує)

k delete pod drill4
```

### Вправа 5: Створення токена (Ціль: 2 хвилини)

```bash
k create sa drill5-sa

# Створити короткотривалий токен
k create token drill5-sa

# Створити з тривалістю
k create token drill5-sa --duration=30m

k delete sa drill5-sa
```

### Вправа 6: Deployment із Сервісним акаунтом (Ціль: 3 хвилини)

```bash
k create sa drill6-sa

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
      serviceAccountName: drill6-sa
      containers:
      - name: app
        image: nginx
EOF

# Перевірити, що всі поди використовують правильний SA
k get pods -l app=drill6 -o jsonpath='{.items[*].spec.serviceAccountName}'
echo

k delete deploy drill6 sa drill6-sa
```

---

## Наступний модуль

[Модуль 4.6: Custom Resource Definitions](module-4.6-crds.md) — Розширення Kubernetes за допомогою власних ресурсів.
