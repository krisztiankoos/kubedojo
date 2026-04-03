---
title: "\u041c\u043e\u0434\u0443\u043b\u044c 4.2: Secrets"
slug: uk/k8s/ckad/part4-environment/module-4.2-secrets
sidebar: 
  order: 2
lab: 
  id: ckad-4.2-secrets
  url: https://killercoda.com/kubedojo/scenario/ckad-4.2-secrets
  duration: "30 min"
  difficulty: intermediate
  environment: kubernetes
---
> **Складність**: `[MEDIUM]` — Схоже на ConfigMaps, але з міркуваннями безпеки
>
> **Час на виконання**: 40–50 хвилин
>
> **Передумови**: Модуль 4.1 (ConfigMaps), розуміння кодування base64

---

## Що ви зможете робити

Після завершення цього модуля ви зможете:
- **Створити** Secrets за допомогою `kubectl create secret` для типів generic, TLS та docker-registry
- **Налаштувати** Піди для безпечного використання Secrets як змінних оточення та монтування томів
- **Пояснити** як Kubernetes зберігає Secrets (base64, не зашифровано) та наслідки для безпеки
- **Діагностувати** помилки автентифікації, спричинені неправильно закодованими або відсутніми даними Secret

---

## Чому цей модуль важливий

Secrets зберігають конфіденційні дані, такі як паролі, API-ключі та TLS-сертифікати. Хоча за використанням вони схожі на ConfigMaps, Secrets мають додаткові функції безпеки та спеціально призначені для конфіденційної інформації.

На іспиті CKAD перевіряють вашу здатність:
- Створювати Secrets з літералів, файлів та YAML
- Використовувати Secrets як змінні оточення та томи
- Розуміти різні типи Secrets
- Знати наслідки для безпеки

> **Аналогія з банківською коміркою**
>
> Якщо ConfigMaps — це публічна дошка оголошень, то Secrets — це банківські комірки. Дані все ще доступні авторизованим сторонам (подам), але зберігаються ретельніше, обробляються інакше, і ви б не стали розміщувати там те, що готові показати публічно.

---

## Створення Secrets

### Загальні Secrets (з літералів)

```bash
# Одна пара ключ-значення
k create secret generic db-secret --from-literal=password=mysecretpassword

# Кілька пар ключ-значення
k create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password=mysecretpassword \
  --from-literal=host=db.example.com
```

### З файлів

```bash
# Створити файли з конфіденційними даними
echo -n 'admin' > username.txt
echo -n 'mysecretpassword' > password.txt

# Створити Secret з файлів
k create secret generic db-secret \
  --from-file=username=username.txt \
  --from-file=password=password.txt

# Очистити файли
rm username.txt password.txt
```

### З YAML (кодування Base64)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=      # base64 від 'admin'
  password: bXlzZWNyZXQ=  # base64 від 'mysecret'
```

### З YAML (відкритий текст через stringData)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
stringData:
  username: admin
  password: mysecret
```

Примітка: `stringData` доступний лише для запису та перетворюється на `data` (base64) при збереженні.

---

## Типи Secrets

| Тип | Призначення |
|-----|-------------|
| `Opaque` | За замовчуванням, довільні дані користувача |
| `kubernetes.io/service-account-token` | Токени Сервісного акаунта |
| `kubernetes.io/dockerconfigjson` | Облікові дані реєстру Docker |
| `kubernetes.io/tls` | TLS-сертифікат і ключ |
| `kubernetes.io/basic-auth` | Базова автентифікація |
| `kubernetes.io/ssh-auth` | Облікові дані SSH |

### Secret реєстру Docker

```bash
k create secret docker-registry my-registry \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=pass \
  --docker-email=user@example.com
```

### TLS Secret

```bash
k create secret tls my-tls \
  --cert=path/to/cert.pem \
  --key=path/to/key.pem
```

---

## Використання Secrets

### Як змінні оточення

**Одна змінна:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: nginx
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
```

**Усі ключі як змінні:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: nginx
    envFrom:
    - secretRef:
        name: db-secret
```

### Як файли тому

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
    - name: secret-volume
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: db-secret
```

### З конкретними правами доступу

```yaml
volumes:
- name: secret-volume
  secret:
    secretName: db-secret
    defaultMode: 0400  # Лише читання для власника
```

### Монтування конкретних ключів

```yaml
volumes:
- name: secret-volume
  secret:
    secretName: db-secret
    items:
    - key: password
      path: db-password
```

---

## Кодування/декодування Base64

```bash
# Закодувати
echo -n 'mysecret' | base64
# bXlzZWNyZXQ=

# Декодувати
echo 'bXlzZWNyZXQ=' | base64 -d
# mysecret

# Переглянути декодований secret
k get secret db-secret -o jsonpath='{.data.password}' | base64 -d
```

**Важливо**: Використовуйте `-n` з echo, щоб уникнути кодування символу нового рядка!

---

## Міркування безпеки

### Що забезпечують Secrets

- **Кодування Base64** (не шифрування!)
- **Зберігання в etcd** (можна зашифрувати у стані спокою з відповідною конфігурацією)
- **Захист RBAC** — контроль того, хто може читати secrets
- **Обмежена видимість** — не показуються у виводі `kubectl get`

### Чого Secrets не забезпечують

- **Шифрування за замовчуванням** — base64 — це кодування, а не шифрування
- **Захист пам'яті** — secrets у подах зберігаються у відкритому тексті в пам'яті
- **Захист від логування** — застосунки можуть записувати значення secrets у логи

### Найкращі практики

```yaml
# Монтувати як лише для читання
volumeMounts:
- name: secrets
  mountPath: /etc/secrets
  readOnly: true

# Використовувати конкретні права доступу
volumes:
- name: secrets
  secret:
    secretName: my-secret
    defaultMode: 0400
```

---

## Візуалізація

```
┌─────────────────────────────────────────────────────────────┐
│                     Потік Secrets                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Створення Secret                                           │
│  ┌─────────────────────────────────────┐                   │
│  │ k create secret generic db-secret   │                   │
│  │   --from-literal=pass=mysecret      │                   │
│  └─────────────────────────────────────┘                   │
│                    │                                        │
│                    ▼                                        │
│  Зберігається в etcd (base64)                              │
│  ┌─────────────────────────────────────┐                   │
│  │ data:                               │                   │
│  │   pass: bXlzZWNyZXQ=               │                   │
│  └─────────────────────────────────────┘                   │
│                    │                                        │
│         ┌─────────┴─────────┐                              │
│         ▼                   ▼                              │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │   Змінна     │    │  Монтування  │                      │
│  │  оточення    │    │    тому      │                      │
│  │              │    │              │                      │
│  │ $PASS=       │    │ /secrets/    │                      │
│  │ "mysecret"   │    │  файл pass   │                      │
│  │ (декодовано) │    │ (декодовано) │                      │
│  └──────────────┘    └──────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Secrets проти ConfigMaps

| Характеристика | ConfigMap | Secret |
|----------------|-----------|--------|
| Кодування даних | Відкритий текст | Base64 |
| Призначення | Неконфіденційна конфігурація | Конфіденційні дані |
| Обмеження розміру | 1 МБ | 1 МБ |
| Шифрування у стані спокою | Ні | За бажанням |
| Спеціальні типи | Ні | Так (TLS, docker-registry) |
| Права монтування | За замовчуванням | Можна обмежити (0400) |

---

## Швидка довідка

```bash
# Створити
k create secret generic NAME --from-literal=KEY=VALUE
k create secret generic NAME --from-file=FILE
k create secret tls NAME --cert=CERT --key=KEY
k create secret docker-registry NAME --docker-server=... --docker-username=...

# Переглянути (у кодуванні base64)
k get secret NAME -o yaml

# Декодувати конкретний ключ
k get secret NAME -o jsonpath='{.data.KEY}' | base64 -d

# Редагувати
k edit secret NAME

# Видалити
k delete secret NAME
```

---

## Чи знали ви?

- **Base64 — це не шифрування.** Будь-хто з доступом до кластера може декодувати secrets. Це лише кодування для безпечної роботи з бінарними даними у YAML.

- **Kubernetes може шифрувати secrets у стані спокою** в etcd за допомогою EncryptionConfiguration. Це налаштування адміністратора кластера, не тема іспиту CKAD.

- **Secrets мають простір імен.** Під може отримати доступ лише до secrets у своєму власному просторі імен (якщо RBAC не дозволяє міжпросторовий доступ).

- **Змінні оточення зі secrets можуть витікати** у логах, дампах збоїв або при виведенні застосунками. Монтування томів загалом безпечніше.

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| Забули `-n` при кодуванні | Символ нового рядка кодується разом з даними | Завжди використовуйте `echo -n` |
| Вважати, що base64 — це безпечно | Будь-хто може декодувати | Використовуйте належний RBAC + шифрування у стані спокою |
| Логування змінних оточення зі secrets | Secrets відкриті у логах | Монтуйте як файли, не логуйте |
| Не встановлювати readOnly | Контейнер може змінити монтування | Завжди використовуйте `readOnly: true` |
| Збереження secrets у git | Secrets відкриті у репозиторії | Використовуйте зовнішнє керування secrets |

---

## Тест

1. **Як створити secret з іменем користувача та паролем?**
   <details>
   <summary>Відповідь</summary>
   `kubectl create secret generic my-secret --from-literal=username=admin --from-literal=password=secret`
   </details>

2. **Як декодувати значення secret?**
   <details>
   <summary>Відповідь</summary>
   `kubectl get secret my-secret -o jsonpath='{.data.password}' | base64 -d`
   </details>

3. **Яка різниця між `data` та `stringData` у YAML Secret?**
   <details>
   <summary>Відповідь</summary>
   `data` вимагає значення у кодуванні base64. `stringData` приймає відкритий текст, і Kubernetes кодує його автоматично. `stringData` доступний лише для запису та перетворюється на `data` при збереженні.
   </details>

4. **Чи кодування base64 — це те саме, що шифрування?**
   <details>
   <summary>Відповідь</summary>
   Ні. Base64 — це зворотне кодування, а не шифрування. Будь-хто може його декодувати. Для справжнього шифрування потрібне шифрування etcd у стані спокою або зовнішнє керування secrets.
   </details>

---

## Практична вправа

**Завдання**: Створити та використати secrets кількома способами.

**Підготовка:**
```bash
# Створити secret
k create secret generic app-secret \
  --from-literal=api-key=supersecretkey123 \
  --from-literal=db-password=dbpass456
```

**Частина 1: Змінні оточення**
```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: secret-env
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'echo "API Key: $API_KEY" && echo "DB Pass: $DB_PASSWORD" && sleep 3600']
    env:
    - name: API_KEY
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: api-key
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: db-password
EOF

k logs secret-env
```

**Частина 2: Монтування тому**
```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: secret-vol
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'ls -la /secrets && cat /secrets/api-key && sleep 3600']
    volumeMounts:
    - name: secrets
      mountPath: /secrets
      readOnly: true
  volumes:
  - name: secrets
    secret:
      secretName: app-secret
      defaultMode: 0400
EOF

k logs secret-vol
```

**Частина 3: Декодування Secret**
```bash
# Переглянути у кодуванні
k get secret app-secret -o yaml

# Декодувати
k get secret app-secret -o jsonpath='{.data.api-key}' | base64 -d
echo  # новий рядок
```

**Очищення:**
```bash
k delete pod secret-env secret-vol
k delete secret app-secret
```

---

## Практичні вправи

### Вправа 1: Створення з літералів (Ціль: 1 хвилина)

```bash
k create secret generic drill1 --from-literal=pass=secret123
k get secret drill1 -o yaml
k delete secret drill1
```

### Вправа 2: Декодування Secret (Ціль: 2 хвилини)

```bash
k create secret generic drill2 --from-literal=token=mytoken123
k get secret drill2 -o jsonpath='{.data.token}' | base64 -d
echo
k delete secret drill2
```

### Вправа 3: Змінна оточення (Ціль: 3 хвилини)

```bash
k create secret generic drill3 --from-literal=DB_PASS=dbsecret

cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill3
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'echo $DB_PASS && sleep 3600']
    env:
    - name: DB_PASS
      valueFrom:
        secretKeyRef:
          name: drill3
          key: DB_PASS
EOF

k logs drill3
k delete pod drill3 secret drill3
```

### Вправа 4: Монтування тому (Ціль: 3 хвилини)

```bash
k create secret generic drill4 --from-literal=cert=CERTIFICATE_DATA

cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill4
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'cat /certs/cert && sleep 3600']
    volumeMounts:
    - name: certs
      mountPath: /certs
      readOnly: true
  volumes:
  - name: certs
    secret:
      secretName: drill4
EOF

k logs drill4
k delete pod drill4 secret drill4
```

### Вправа 5: YAML з stringData (Ціль: 3 хвилини)

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: drill5
type: Opaque
stringData:
  username: admin
  password: supersecret
EOF

# Перевірити, що дані закодовані
k get secret drill5 -o yaml | grep -A2 data

# Декодувати
k get secret drill5 -o jsonpath='{.data.password}' | base64 -d
echo

k delete secret drill5
```

### Вправа 6: Повний сценарій (Ціль: 5 хвилин)

**Сценарій**: Розгорнути застосунок з обліковими даними бази даних.

```bash
# Створити secret бази даних
k create secret generic drill6-db \
  --from-literal=MYSQL_USER=appuser \
  --from-literal=MYSQL_PASSWORD=apppass123 \
  --from-literal=MYSQL_DATABASE=myapp

# Розгорнути застосунок з усіма secrets як змінними оточення
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill6
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'env | grep MYSQL && sleep 3600']
    envFrom:
    - secretRef:
        name: drill6-db
EOF

k logs drill6
k delete pod drill6 secret drill6-db
```

---

## Наступний модуль

[Модуль 4.3: Вимоги до ресурсів](module-4.3-resources/) — Налаштування запитів та лімітів CPU і пам'яті.
