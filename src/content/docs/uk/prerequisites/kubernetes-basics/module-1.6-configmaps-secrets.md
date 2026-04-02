---
title: "Модуль 1.6: ConfigMaps та Secrets"
slug: uk/prerequisites/kubernetes-basics/module-1.6-configmaps-secrets
sidebar:
  order: 7
---
> **Складність**: `[MEDIUM]` — Основне керування конфігурацією
>
> **Час на виконання**: 35–40 хвилин
>
> **Передумови**: Модуль 1.3 (Поди)

---

## Чому цей модуль важливий

Застосункам потрібна конфігурація: URL-адреси баз даних, прапорці функцій (feature flags), API-ключі, креденшали. Прописувати їх прямо в коді або в образах контейнерів — погана практика. ConfigMaps та Secrets дозволяють відокремити конфігурацію від коду вашого застосунку.

---

## ConfigMaps проти Secrets

```
┌─────────────────────────────────────────────────────────────┐
│              CONFIGMAPS ПРОТИ SECRETS                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ConfigMap                     │  Secret                    │
│  ─────────────────────────────│────────────────────────────│
│  Нечутливі дані                │  Чутливі (секретні) дані   │
│  Зберігання у відкритому виді  │  Кодування Base64          │
│  Змінні оточення, конфіги      │  Паролі, токени, ключі     │
│                                │                            │
│  Приклади:                     │  Приклади:                │
│  • Рівні логування             │  • Паролі до БД           │
│  • Прапорці функцій            │  • API-ключі               │
│  • Вміст конфіг-файлів         │  • TLS-сертифікати         │
│                                │                            │
│  Примітка: Secrets НЕ шифруються за замовчуванням!         │
│  Base64 — це кодування, а не шифрування.                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ConfigMaps

### Створення ConfigMaps

```bash
# З конкретних значень (літералів)
kubectl create configmap app-config \
  --from-literal=LOG_LEVEL=debug \
  --from-literal=ENVIRONMENT=staging

# З файлу
kubectl create configmap nginx-config --from-file=nginx.conf

# З директорії (кожен файл стане ключем)
kubectl create configmap configs --from-file=./config-dir/

# Переглянути ConfigMap
kubectl get configmap app-config -o yaml
```

### ConfigMap YAML

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "debug"
  ENVIRONMENT: "staging"
  config.json: |
    {
      "database": "localhost",
      "port": 5432
    }
```

### Використання ConfigMaps

**Як змінні середовища (env):**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: myapp
    env:
    - name: LOG_LEVEL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: LOG_LEVEL
    # Або всі ключі одночасно:
    envFrom:
    - configMapRef:
        name: app-config
```

**Як томи (файли):**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: config
      mountPath: /etc/nginx/conf.d
  volumes:
  - name: config
    configMap:
      name: nginx-config
```

---

## Secrets

### Створення Secrets

```bash
# З конкретних значень
kubectl create secret generic db-creds \
  --from-literal=username=admin \
  --from-literal=password=secret123

# З файлу
kubectl create secret generic tls-cert \
  --from-file=cert.pem \
  --from-file=key.pem

# Перегляд секрету (значення закодовані в base64)
kubectl get secret db-creds -o yaml

# Декодування значення
kubectl get secret db-creds -o jsonpath='{.data.password}' | base64 -d
```

### Secret YAML

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-creds
type: Opaque              # Тип секрету за замовчуванням
data:                     # Значення в Base64
  username: YWRtaW4=      # echo -n 'admin' | base64
  password: c2VjcmV0MTIz  # echo -n 'secret123' | base64
---
# Або використовуйте stringData для відкритого тексту (K8s сам закодує)
apiVersion: v1
kind: Secret
metadata:
  name: db-creds
type: Opaque
stringData:               # Відкритий текст, автокодування
  username: admin
  password: secret123
```

### Використання Secrets

**Як змінні середовища:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: myapp
    env:
    - name: DB_USER
      valueFrom:
        secretKeyRef:
          name: db-creds
          key: username
    - name: DB_PASS
      valueFrom:
        secretKeyRef:
          name: db-creds
          key: password
```

**Як томи (файли):**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: myapp
    volumeMounts:
    - name: secrets
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secrets
    secret:
      secretName: db-creds
```

---

## Візуалізація

```
┌─────────────────────────────────────────────────────────────┐
│              ВИКОРИСТАННЯ CONFIGMAP/SECRET                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ConfigMap/Secret                                          │
│  ┌─────────────────────┐                                   │
│  │ data:               │                                   │
│  │   KEY1: value1      │                                   │
│  │   KEY2: value2      │                                   │
│  └──────────┬──────────┘                                   │
│             │                                               │
│    ┌────────┴────────┐                                     │
│    ▼                 ▼                                      │
│                                                             │
│  Як змінні           Як том                                 │
│  середовища          (Файли)                                │
│  ┌────────────┐     ┌────────────────────┐                │
│  │ env:       │     │ /etc/config/       │                │
│  │   KEY1=val1│     │   KEY1  (файл)     │                │
│  │   KEY2=val2│     │   KEY2  (файл)     │                │
│  └────────────┘     └────────────────────┘                │
│                                                             │
│  Використовуйте     Використовуйте томи                    │
│  envFrom для        для конфіг-файлів                      │
│  простих значень                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Практичний приклад

```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-settings
data:
  LOG_LEVEL: "info"
  CACHE_TTL: "3600"
---
# Secret
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
stringData:
  DB_PASSWORD: "supersecret"
  API_KEY: "abc123"
---
# Под, що використовує обидва ресурси
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  - name: app
    image: myapp:v1
    envFrom:
    - configMapRef:
        name: app-settings
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: DB_PASSWORD
    - name: API_KEY
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: API_KEY
```

---

## Чи знали ви?

- **Secrets НЕ шифруються в стані спокою за замовчуванням.** Вони просто закодовані в base64. Для справжньої безпеки потрібно увімкнути шифрування (Encryption at Rest) у кластері.

- **Оновлення ConfigMap/Secret не перезапускає поди автоматично.** Файли в змонтованих томах оновлюються, але змінні середовища потребують перезапуску пода для оновлення.

- **Максимальний розмір — 1МБ.** І ConfigMaps, і Secrets обмежені 1 мегабайтом даних.

- **Secrets зберігаються в etcd.** Будь-хто з доступом до etcd може їх прочитати. Використовуйте RBAC для обмеження доступу.

---

## Типові помилки

| Помилка | Наслідки | Рішення |
|---------|----------|---------|
| Збереження секретів у Git | Витік даних | Використовуйте sealed-secrets або зовнішні сховища секретів |
| Віра в те, що base64 = шифрування | Хибна безпека | Увімкніть шифрування на рівні кластера |
| Невикористання stringData | Помилки при ручному кодуванні | Використовуйте `stringData` для відкритого тексту |
| Конфігурація всередині образу | Неможливість зміни без збірки | Використовуйте ConfigMaps/Secrets |

---

## Тест

1. **Яка різниця між ConfigMaps та Secrets?**
   <details>
   <summary>Відповідь</summary>
   ConfigMaps призначені для нечутливих даних (відкритий текст). Secrets — для конфіденційних даних (закодовані в base64). Обидва ресурси можуть використовуватися як змінні середовища або монтуватися як файли.
   </details>

2. **Як декодувати значення із Secret?**
   <details>
   <summary>Відповідь</summary>
   `kubectl get secret НАЗВА -o jsonpath='{.data.КЛЮЧ}' | base64 -d`. Пам'ятайте, що це лише кодування, а не шифрування.
   </details>

3. **Що станеться з подами при оновленні ConfigMap?**
   <details>
   <summary>Відповідь</summary>
   Якщо ConfigMap змонтовано як том, файли всередині пода оновляться автоматично (зазвичай протягом хвилини). Якщо він використовується як змінні середовища — поди потрібно перезапустити вручну, щоб вони побачили нові значення.
   </details>

4. **У чому перевага використання `stringData` у маніфестах Secrets?**
   <details>
   <summary>Відповідь</summary>
   Ви можете писати значення відкритим текстом, а Kubernetes автоматично закодує їх у base64 при створенні ресурсу. Це зручніше і зменшує ризик помилок.
   </details>

---

## Практична вправа

**Завдання**: Створити та використати ConfigMaps та Secrets.

```bash
# 1. Створіть ConfigMap
kubectl create configmap app-config \
  --from-literal=LOG_LEVEL=debug \
  --from-literal=APP_NAME=myapp

# 2. Створіть Secret
kubectl create secret generic app-secret \
  --from-literal=DB_PASS=secretpassword

# 3. Створіть под, що використовує обидва ресурси
cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: config-test
spec:
  containers:
  - name: test
    image: busybox
    command: ['sh', '-c', 'env && sleep 3600']
    envFrom:
    - configMapRef:
        name: app-config
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: DB_PASS
EOF

# 4. Перевірте змінні оточення
kubectl logs config-test | grep -E "LOG_LEVEL|APP_NAME|DB_PASSWORD"

# 5. Прибирання
kubectl delete pod config-test
kubectl delete configmap app-config
kubectl delete secret app-secret
```

**Критерії успіху**: Логи пода показують усі задані змінні середовища.

---

## Підсумок

ConfigMaps та Secrets дозволяють винести конфігурацію за межі застосунку:

**ConfigMaps**:
- Нечутливі дані.
- Відкритий текст.
- Використовуються для налаштувань, конфіг-файлів.

**Secrets**:
- Чутливі дані.
- Base64 кодування (НЕ шифрування).
- Використовуються для паролів, ключів, токенів.

**Патерни використання**:
- Змінні середовища (env, envFrom).
- Монтування томів (файли).

---

## Наступний модуль

[Модуль 1.7: Простори імен та Мітки](../module-1.7-namespaces-labels/) — Організація вашого кластера.
