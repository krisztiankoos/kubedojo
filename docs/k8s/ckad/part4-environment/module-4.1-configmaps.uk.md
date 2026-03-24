# Модуль 4.1: ConfigMaps

> **Складність**: `[MEDIUM]` — Кілька способів створення та використання
>
> **Час на виконання**: 40–50 хвилин
>
> **Передумови**: Модуль 1.1 (Поди), розуміння змінних оточення

---

## Чому цей модуль важливий

ConfigMaps відокремлюють конфігурацію від образів контейнерів. Замість того, щоб вбудовувати налаштування в образ, ви впроваджуєте їх під час запуску. Це дозволяє використовувати той самий образ у різних середовищах (dev, staging, production) з різними конфігураціями.

На іспиті CKAD часто перевіряють знання ConfigMaps, оскільки вони є фундаментальною частиною методології twelve-factor app. Очікуйте запитання щодо:
- Створення ConfigMaps з літералів, файлів та директорій
- Використання як змінних оточення
- Монтування як томів
- Оновлення конфігурацій

> **Аналогія з меню ресторану**
>
> Уявіть ConfigMaps як дошку зі спецпропозиціями ресторану. Кухня (образ контейнера) залишається незмінною, але спецпропозиції (конфігурація) змінюються щодня. Шеф-кухар не перебудовує кухню, щоб змінити меню — він просто оновлює дошку. ConfigMaps працюють так само: змініть конфігурацію, перезапустіть під, отримайте нову поведінку.

---

## Створення ConfigMaps

### З літералів

```bash
# Одна пара ключ-значення
k create configmap app-config --from-literal=APP_ENV=production

# Кілька пар ключ-значення
k create configmap app-config \
  --from-literal=APP_ENV=production \
  --from-literal=LOG_LEVEL=info \
  --from-literal=MAX_CONNECTIONS=100

# Переглянути результат
k get configmap app-config -o yaml
```

### З файлів

```bash
# Створити файл конфігурації
echo "database.host=db.example.com
database.port=5432
database.name=myapp" > app.properties

# Створити ConfigMap з файлу
k create configmap app-config --from-file=app.properties

# Власна назва ключа
k create configmap app-config --from-file=config.properties=app.properties

# Кілька файлів
k create configmap app-config \
  --from-file=app.properties \
  --from-file=logging.properties
```

### З директорій

```bash
# Усі файли в директорії стають ключами
k create configmap app-config --from-file=./config-dir/
```

### З YAML

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_ENV: production
  LOG_LEVEL: info
  app.properties: |
    database.host=db.example.com
    database.port=5432
    database.name=myapp
```

---

## Використання ConfigMaps

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
    - name: APP_ENVIRONMENT
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: APP_ENV
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
    - configMapRef:
        name: app-config
```

### Як файли тому

**Змонтувати весь ConfigMap:**
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
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

**Змонтувати конкретні ключі:**
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
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
      items:
      - key: app.properties
        path: application.properties
```

**Змонтувати в конкретний файл:**
```yaml
volumeMounts:
- name: config-volume
  mountPath: /etc/config/app.conf
  subPath: app.properties
```

---

## Патерни ConfigMap

### Конфігурація для конкретного середовища

```bash
# Розробка
k create configmap app-config \
  --from-literal=APP_ENV=development \
  --from-literal=DEBUG=true \
  -n development

# Продакшен
k create configmap app-config \
  --from-literal=APP_ENV=production \
  --from-literal=DEBUG=false \
  -n production
```

### Файли конфігурації

```bash
# nginx.conf
cat << 'EOF' > nginx.conf
server {
    listen 80;
    server_name localhost;
    location / {
        root /usr/share/nginx/html;
    }
}
EOF

k create configmap nginx-config --from-file=nginx.conf

# Змонтувати в поді
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: nginx-custom
spec:
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - name: config
      mountPath: /etc/nginx/conf.d/default.conf
      subPath: nginx.conf
  volumes:
  - name: config
    configMap:
      name: nginx-config
EOF
```

---

## Оновлення ConfigMap

### Поведінка залежно від способу використання

| Метод | Поведінка при оновленні |
|-------|------------------------|
| Змінні оточення | **НЕ оновлюються** — потрібен перезапуск пода |
| Монтування томів | **Оновлюються автоматично** (період синхронізації kubelet ~1 хв) |
| Монтування з subPath | **НЕ оновлюються** — потрібен перезапуск пода |

### Примусове оновлення

```bash
# Перезапустити поди для застосування змін змінних оточення
k rollout restart deployment/myapp

# Для конфігурацій, змонтованих як томи, зачекайте або примусово синхронізуйте
# Поди автоматично оновлюються протягом періоду синхронізації kubelet
```

---

## Візуалізація

```
┌─────────────────────────────────────────────────────────────┐
│                Використання ConfigMap                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ConfigMap: app-config                                      │
│  ┌─────────────────────────────────────┐                   │
│  │ APP_ENV: production                 │                   │
│  │ LOG_LEVEL: info                     │                   │
│  │ app.properties: |                   │                   │
│  │   database.host=db.example.com      │                   │
│  │   database.port=5432                │                   │
│  └─────────────────────────────────────┘                   │
│           │                    │                           │
│           ▼                    ▼                           │
│    ┌──────────────┐    ┌──────────────┐                   │
│    │   envFrom    │    │  монтування  │                   │
│    │              │    │    тому      │                   │
│    │  $APP_ENV    │    │              │                   │
│    │  $LOG_LEVEL  │    │ /etc/config/ │                   │
│    └──────────────┘    │  app.properties│                  │
│                        └──────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Швидка довідка

```bash
# Створити
k create configmap NAME --from-literal=KEY=VALUE
k create configmap NAME --from-file=FILE
k create configmap NAME --from-file=DIR/

# Переглянути
k get configmap NAME -o yaml
k describe configmap NAME

# Редагувати
k edit configmap NAME

# Видалити
k delete configmap NAME
```

---

## Чи знали ви?

- **ConfigMaps мають обмеження розміру 1 МБ.** Для більших конфігурацій розгляньте монтування зовнішнього сховища або використання init-контейнерів.

- **Дані ConfigMap зберігаються в etcd без шифрування** (на відміну від Secrets, які можна зашифрувати в стані спокою). Не зберігайте конфіденційні дані в ConfigMaps.

- **Поле `immutable: true`** (Kubernetes 1.21+) запобігає випадковим змінам та покращує продуктивність кластера, зменшуючи навантаження на watch.

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| Очікування оновлення змінних оточення | Застосунок використовує застарілу конфігурацію | Перезапустіть під після змін ConfigMap |
| Використання subPath з очікуванням оновлень | subPath не оновлюється автоматично | Використовуйте повне монтування тому або перезапуск |
| Зберігання секретів у ConfigMaps | Дані видимі у відкритому тексті | Використовуйте Secrets для конфіденційних даних |
| Відсутність простору імен для ConfigMaps | Конфігурація витікає між середовищами | Створюйте ConfigMaps для кожного простору імен |
| Помилка в назві ключа | Під не запуститься або отримає неправильну конфігурацію | Використовуйте `k describe cm` для перевірки |

---

## Тест

1. **Як створити ConfigMap з кількох пар ключ-значення?**
   <details>
   <summary>Відповідь</summary>
   `kubectl create configmap NAME --from-literal=KEY1=VAL1 --from-literal=KEY2=VAL2`
   </details>

2. **Як впровадити всі ключі ConfigMap як змінні оточення?**
   <details>
   <summary>Відповідь</summary>
   Використовуйте `envFrom` з `configMapRef`:
   ```yaml
   envFrom:
   - configMapRef:
       name: configmap-name
   ```
   </details>

3. **Чи оновлюються змінні оточення з ConfigMaps автоматично?**
   <details>
   <summary>Відповідь</summary>
   Ні. Змінні оточення встановлюються при запуску пода і не оновлюються. Для застосування змін потрібно перезапустити під.
   </details>

4. **Як змонтувати лише конкретні ключі з ConfigMap?**
   <details>
   <summary>Відповідь</summary>
   Використовуйте `items` у визначенні тому:
   ```yaml
   volumes:
   - name: config
     configMap:
       name: my-config
       items:
       - key: specific-key
         path: filename
   ```
   </details>

---

## Практична вправа

**Завдання**: Створити та використати ConfigMaps кількома способами.

**Підготовка:**
```bash
# Створити ConfigMap з літералів
k create configmap web-config \
  --from-literal=APP_COLOR=blue \
  --from-literal=APP_MODE=production

# Перевірити
k get configmap web-config -o yaml
```

**Частина 1: Змінні оточення**
```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: env-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'echo Color: $APP_COLOR, Mode: $APP_MODE && sleep 3600']
    envFrom:
    - configMapRef:
        name: web-config
EOF

# Перевірити оточення
k logs env-pod
```

**Частина 2: Монтування тому**
```bash
# Створити файл конфігурації
k create configmap nginx-index --from-literal=index.html='<h1>Hello from ConfigMap</h1>'

cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: vol-pod
spec:
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - name: html
      mountPath: /usr/share/nginx/html
  volumes:
  - name: html
    configMap:
      name: nginx-index
EOF

# Тестування
k exec vol-pod -- cat /usr/share/nginx/html/index.html
```

**Очищення:**
```bash
k delete pod env-pod vol-pod
k delete configmap web-config nginx-index
```

---

## Практичні вправи

### Вправа 1: Створення з літералів (Ціль: 1 хвилина)

```bash
k create configmap drill1 --from-literal=KEY1=value1 --from-literal=KEY2=value2
k get cm drill1 -o yaml
k delete cm drill1
```

### Вправа 2: Створення з файлу (Ціль: 2 хвилини)

```bash
echo "setting1=on
setting2=off" > /tmp/settings.conf

k create configmap drill2 --from-file=/tmp/settings.conf
k get cm drill2 -o yaml
k delete cm drill2
```

### Вправа 3: Змінні оточення (Ціль: 3 хвилини)

```bash
k create configmap drill3 --from-literal=DB_HOST=localhost --from-literal=DB_PORT=5432

cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill3
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'env | grep DB && sleep 3600']
    envFrom:
    - configMapRef:
        name: drill3
EOF

k logs drill3
k delete pod drill3 cm drill3
```

### Вправа 4: Монтування тому (Ціль: 3 хвилини)

```bash
k create configmap drill4 --from-literal=config.json='{"debug": true}'

cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill4
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'cat /config/config.json && sleep 3600']
    volumeMounts:
    - name: cfg
      mountPath: /config
  volumes:
  - name: cfg
    configMap:
      name: drill4
EOF

k logs drill4
k delete pod drill4 cm drill4
```

### Вправа 5: Монтування конкретного ключа (Ціль: 3 хвилини)

```bash
k create configmap drill5 \
  --from-literal=app.conf='main config' \
  --from-literal=log.conf='log config'

cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill5
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'ls /config && cat /config/application.conf && sleep 3600']
    volumeMounts:
    - name: cfg
      mountPath: /config
  volumes:
  - name: cfg
    configMap:
      name: drill5
      items:
      - key: app.conf
        path: application.conf
EOF

k logs drill5
k delete pod drill5 cm drill5
```

### Вправа 6: Повний сценарій (Ціль: 5 хвилин)

**Сценарій**: Розгорнути nginx з власною конфігурацією.

```bash
# Створити конфігурацію nginx
cat << 'NGINX' > /tmp/nginx.conf
server {
    listen 8080;
    location / {
        return 200 'Custom Config Works!\n';
        add_header Content-Type text/plain;
    }
}
NGINX

k create configmap drill6-nginx --from-file=/tmp/nginx.conf

cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill6
spec:
  containers:
  - name: nginx
    image: nginx
    ports:
    - containerPort: 8080
    volumeMounts:
    - name: nginx-config
      mountPath: /etc/nginx/conf.d/default.conf
      subPath: nginx.conf
  volumes:
  - name: nginx-config
    configMap:
      name: drill6-nginx
EOF

# Тестування (зачекайте на готовність пода)
k wait --for=condition=Ready pod/drill6 --timeout=30s
k exec drill6 -- curl -s localhost:8080

k delete pod drill6 cm drill6-nginx
```

---

## Наступний модуль

[Модуль 4.2: Secrets](module-4.2-secrets.uk.md) — Безпечне керування конфіденційними даними.
