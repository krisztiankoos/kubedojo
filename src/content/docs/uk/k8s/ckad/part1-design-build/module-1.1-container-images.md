---
title: "\u041c\u043e\u0434\u0443\u043b\u044c 1.1: \u041e\u0431\u0440\u0430\u0437\u0438 \u043a\u043e\u043d\u0442\u0435\u0439\u043d\u0435\u0440\u0456\u0432"
slug: uk/k8s/ckad/part1-design-build/module-1.1-container-images
sidebar:
  order: 1
  label: "Part 1: Design & Build"
---
> **Складність**: `[MEDIUM]` — Потребує розуміння Dockerfile та реєстрів образів
>
> **Час на виконання**: 45–60 хвилин
>
> **Передумови**: Модуль 0.2 (Робочий процес розробника), базові знання Docker

---

## Чому цей модуль важливий

Kubernetes не запускає вихідний код — він запускає образи контейнерів. Перш ніж будь-який застосунок потрапить до кластера, його потрібно запакувати в образ. CKAD очікує, що ви розумієте, як образи збираються, тегуються, завантажуються та посилаються.

Хоча під час іспиту ви не будете збирати складні образи (немає часу), вам потрібно:
- Розуміти основи Dockerfile
- Знати конвенції іменування образів
- Виправляти типові проблеми, пов'язані з образами
- Модифікувати наявні образи за потреби

> **Аналогія з морськими контейнерами**
>
> До контейнеризації перевезення товарів було хаосом. Кожен порт обробляв вантаж по-різному. Потім з'явився стандартизований морський контейнер — однакові розміри скрізь, можна штабелювати, працює на будь-якому кораблі. Образи контейнерів — та сама ідея для програмного забезпечення. Ваш застосунок, його залежності, його конфігурація — все запаковано у стандартний формат, який працює ідентично будь-де.

---

## Конвенція іменування образів

Розуміння імен образів є критично важливим. Кожна специфікація Підa в Kubernetes посилається на образи:

```
[registry/][namespace/]image[:tag][@digest]
```

| Компонент | Обов'язковий | Приклад | За замовчуванням |
|-----------|--------------|---------|------------------|
| Реєстр | Ні | `docker.io`, `gcr.io`, `quay.io` | `docker.io` |
| Простір імен | Ні | `library`, `mycompany` | `library` |
| Образ | Так | `nginx`, `myapp` | - |
| Тег | Ні | `latest`, `1.19.0`, `alpine` | `latest` |
| Дайджест | Ні | `sha256:abc123...` | - |

### Приклади

```yaml
# Повна специфікація
image: docker.io/library/nginx:1.21.0

# Еквівалентна скорочена форма (docker.io/library мається на увазі)
image: nginx:1.21.0

# Інший реєстр
image: gcr.io/google-containers/nginx:1.21.0

# Власний простір імен
image: myregistry.com/myteam/myapp:v2.0.0

# З дайджестом (незмінне посилання)
image: nginx@sha256:abc123def456...

# Тег latest (уникайте у продакшені)
image: nginx:latest
image: nginx  # те саме, що вище
```

### Чому теги важливі

```yaml
# ПОГАНО: latest може змінитися несподівано
image: nginx:latest

# ДОБРЕ: конкретна версія, відтворювано
image: nginx:1.21.0

# КРАЩЕ: конкретна версія з базовим образом Alpine (менший)
image: nginx:1.21.0-alpine
```

---

## Основи Dockerfile

Dockerfile визначає, як збирати образ. CKAD може попросити вас зрозуміти або модифікувати прості Dockerfile-и.

### Мінімальний Dockerfile

```dockerfile
# Базовий образ
FROM python:3.9-slim

# Встановити робочу директорію
WORKDIR /app

# Спочатку скопіювати requirements (кешування шарів)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Скопіювати код застосунку
COPY . .

# Відкрити порт (документація)
EXPOSE 8080

# Команда для запуску
CMD ["python", "app.py"]
```

### Загальні інструкції

| Інструкція | Призначення | Приклад |
|------------|-------------|---------|
| `FROM` | Базовий образ | `FROM nginx:alpine` |
| `WORKDIR` | Встановити робочу директорію | `WORKDIR /app` |
| `COPY` | Скопіювати файли з контексту збірки | `COPY src/ /app/` |
| `RUN` | Виконати команду під час збірки | `RUN apt-get update` |
| `ENV` | Встановити змінну середовища | `ENV PORT=8080` |
| `EXPOSE` | Задокументувати порт (не публікує) | `EXPOSE 8080` |
| `CMD` | Команда за замовчуванням для запуску | `CMD ["nginx", "-g", "daemon off;"]` |
| `ENTRYPOINT` | Основний виконуваний файл | `ENTRYPOINT ["python"]` |

### CMD проти ENTRYPOINT

```dockerfile
# CMD: Легко перевизначити
FROM nginx
CMD ["nginx", "-g", "daemon off;"]
# Можна запустити: docker run myimage sleep 10 (замінює CMD)

# ENTRYPOINT: Важко перевизначити
FROM python
ENTRYPOINT ["python"]
CMD ["app.py"]
# Запускає: python app.py
# Можна запустити: docker run myimage script.py (замінює лише CMD)
```

У специфікаціях Підa Kubernetes:
- `ENTRYPOINT` відповідає `command:`
- `CMD` відповідає `args:`

```yaml
spec:
  containers:
  - name: app
    image: python:3.9
    command: ["python"]    # Перевизначає ENTRYPOINT
    args: ["myapp.py"]     # Перевизначає CMD
```

---

## Збірка образів

Хоча ви не будете збирати образи в середовищі іспиту (немає Docker-демона), розуміння процесу допомагає налагоджувати проблеми.

### Базова збірка

```bash
# Збірка в поточній директорії
docker build -t myapp:v1.0.0 .

# Збірка з конкретним Dockerfile
docker build -t myapp:v1.0.0 -f Dockerfile.prod .

# Збірка з аргументами збірки
docker build --build-arg VERSION=1.0.0 -t myapp:v1.0.0 .
```

### Тегування та завантаження

```bash
# Тегувати наявний образ
docker tag myapp:v1.0.0 myregistry.com/team/myapp:v1.0.0

# Завантажити до реєстру
docker push myregistry.com/team/myapp:v1.0.0

# Завантажити всі теги
docker push myregistry.com/team/myapp --all-tags
```

---

## Політика завантаження образів

Kubernetes вирішує, коли завантажувати образи, на основі `imagePullPolicy`:

```yaml
spec:
  containers:
  - name: app
    image: nginx:1.21.0
    imagePullPolicy: Always  # IfNotPresent | Never | Always
```

| Політика | Поведінка | Використовуйте, коли |
|----------|-----------|---------------------|
| `Always` | Завантажувати щоразу | Використовуєте тег `latest`, потрібен найсвіжіший образ |
| `IfNotPresent` | Завантажувати лише якщо не закешовано | Конкретні теги, економія трафіку |
| `Never` | Ніколи не завантажувати, використовувати кеш | Локальна розробка, ізольовані мережі |

### Поведінка за замовчуванням

| Тег образу | Політика за замовчуванням |
|------------|--------------------------|
| Без тегу (мається на увазі `:latest`) | `Always` |
| `:latest` | `Always` |
| Конкретний тег (`:v1.0.0`) | `IfNotPresent` |
| Дайджест (`@sha256:...`) | `IfNotPresent` |

---

## Приватні реєстри

Для завантаження з приватних реєстрів потрібна автентифікація:

### Крок 1: Створити Secret

```bash
# Створити docker-registry secret
k create secret docker-registry regcred \
  --docker-server=myregistry.com \
  --docker-username=user \
  --docker-password=password \
  --docker-email=user@example.com
```

### Крок 2: Посилання у Піді

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: private-app
spec:
  containers:
  - name: app
    image: myregistry.com/team/myapp:v1.0.0
  imagePullSecrets:
  - name: regcred
```

### Альтернатива: ServiceAccount за замовчуванням

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
imagePullSecrets:
- name: regcred
---
apiVersion: v1
kind: Pod
metadata:
  name: private-app
spec:
  serviceAccountName: myapp-sa
  containers:
  - name: app
    image: myregistry.com/team/myapp:v1.0.0
```

---

## Усунення проблем з образами

### Типові помилки

| Помилка | Причина | Рішення |
|---------|---------|---------|
| `ImagePullBackOff` | Неможливо завантажити образ | Перевірте ім'я образу, доступ до реєстру |
| `ErrImagePull` | Завантаження не вдалося | Переконайтеся, що образ існує, перевірте облікові дані |
| `InvalidImageName` | Некоректне посилання на образ | Виправте формат імені образу |
| `ImageInspectError` | Помилка інспекції образу | Перевірте маніфест образу |

### Кроки налагодження

```bash
# Перевірити події Піда
k describe pod myapp | grep -A10 Events

# Перевірити ім'я образу
k get pod myapp -o jsonpath='{.spec.containers[0].image}'

# Переконатися, що secret існує
k get secret regcred

# Тест завантаження вручну (якщо docker доступний)
docker pull myregistry.com/team/myapp:v1.0.0
```

### Приклад: Виправлення ImagePullBackOff

```bash
# Під застряг у ImagePullBackOff
k get pods
# NAME    READY   STATUS             RESTARTS   AGE
# myapp   0/1     ImagePullBackOff   0          5m

# Перевірити події
k describe pod myapp
# Events:
#   Failed to pull image "nginx:latst": rpc error: ...not found

# Знайшли: друкарська помилка в тезі (latst замість latest)

# Виправлення: Відредагувати Під або видалити та створити заново
k delete pod myapp
k run myapp --image=nginx:latest
```

---

## Найкращі практики безпеки образів

Хоча це не завжди тестується, розуміння цього робить вас кращим розробником:

### 1. Використовуйте конкретні теги

```yaml
# ПОГАНО
image: nginx:latest

# ДОБРЕ
image: nginx:1.21.0-alpine
```

### 2. Використовуйте мінімальні базові образи

```dockerfile
# 133MB
FROM python:3.9

# 45MB — набагато менший
FROM python:3.9-slim

# 17MB — ще менший
FROM python:3.9-alpine
```

### 3. Запускайте не від root

```dockerfile
FROM python:3.9-slim
RUN useradd -m appuser
USER appuser
COPY --chown=appuser:appuser . /app
```

У Kubernetes:

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
  containers:
  - name: app
    image: myapp:v1.0.0
```

### 4. Використовуйте файлову систему тільки для читання

```yaml
spec:
  containers:
  - name: app
    image: myapp:v1.0.0
    securityContext:
      readOnlyRootFilesystem: true
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {}
```

---

## Чи знали ви?

- **Образи контейнерів є шаруватими.** Кожна інструкція Dockerfile створює шар. Шари кешуються та спільно використовуються між образами, заощаджуючи дисковий простір та час збірки. Ось чому вміст, що часто змінюється (наприклад, `COPY . .`), розміщують в кінці.

- **Тег `latest` — це лише конвенція.** Він насправді не є "найновішим" за часом — це те, що було останнім завантажено без конкретного тегу. Багато проєктів оновлюють `latest` з кожною збіркою, але деякі ніколи його не оновлюють.

- **Дайджести образів (sha256:...) є незмінними.** Теги можна переміщувати, щоб вони вказували на різні образи, але дайджест завжди посилається на точно той самий вміст образу. Використовуйте дайджести для максимальної відтворюваності у продакшені.

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| Використання `latest` у продакшені | Непередбачувані оновлення | Завжди використовуйте конкретні теги |
| Друкарські помилки в іменах образів | ImagePullBackOff | Ретельно перевіряйте написання |
| Забули `imagePullSecrets` | Неможливо завантажити приватні образи | Додайте посилання на secret до Піда |
| Неправильна `imagePullPolicy` | Проблеми з кешем або зайві завантаження | Встановіть явно відповідно до потреб |
| Великі базові образи | Повільне завантаження, поверхня атаки | Використовуйте варіанти `-slim` або `-alpine` |

---

## Тест

1. **Який тег образу за замовчуванням, якщо жоден не вказано?**
   <details>
   <summary>Відповідь</summary>
   `latest`. Наприклад, `nginx` еквівалентно `nginx:latest`.
   </details>

2. **Під застряг у ImagePullBackOff. Який перший крок налагодження?**
   <details>
   <summary>Відповідь</summary>
   Виконайте `kubectl describe pod <ім'я>` та перевірте секцію Events. Там буде показано конкретну помилку завантаження, наприклад, образ не знайдено або помилка автентифікації.
   </details>

3. **Як перевизначити CMD з Dockerfile у специфікації Піда Kubernetes?**
   <details>
   <summary>Відповідь</summary>
   Використовуйте поле `args` у специфікації контейнера:
   ```yaml
   containers:
   - name: app
     image: myimage
     args: ["new", "command", "here"]
   ```
   </details>

4. **Яка різниця між `imagePullPolicy: Always` та `IfNotPresent`?**
   <details>
   <summary>Відповідь</summary>
   `Always` завантажує образ при кожному запуску Піда, навіть якщо він закешований локально. `IfNotPresent` завантажує лише якщо образу ще немає на вузлі. Використовуйте `Always` для тегів `latest`; використовуйте `IfNotPresent` для конкретних версійних тегів для економії трафіку.
   </details>

---

## Практична вправа

**Завдання**: Виправити зламаний Деплоймент з проблемами образів.

**Підготовка:**
```bash
# Створити Деплоймент з навмисними проблемами образу
k create deploy broken-app --image=nginx:nonexistent
```

**Ваші завдання:**
1. Перевірити, чому Піди не запускаються
2. Знайти правильний тег образу
3. Виправити Деплоймент

**Рішення:**
```bash
# Перевірити статус Піда
k get pods
# Показує ImagePullBackOff

# Отримати деталі
k describe pod -l app=broken-app | grep -A5 Events
# Показує: nginx:nonexistent not found

# Виправити, оновивши Деплоймент
k set image deploy/broken-app nginx=nginx:1.21.0

# Перевірити
k get pods
# Повинен показувати Running

# Очищення
k delete deploy broken-app
```

**Критерії успіху:**
- [ ] Виявлено проблему з образом
- [ ] Виправлено посилання на образ
- [ ] Під тепер працює

---

## Практичні вправи

### Вправа 1: Аналіз імені образу (Ціль: 2 хвилини)

Визначте компоненти цих посилань на образи:

```
1. nginx
   Реєстр: docker.io (за замовчуванням)
   Простір імен: library (за замовчуванням)
   Образ: nginx
   Тег: latest (за замовчуванням)

2. gcr.io/google-containers/pause:3.2
   Реєстр: gcr.io
   Простір імен: google-containers
   Образ: pause
   Тег: 3.2

3. mycompany.com/team/app:v2.0.0-alpine
   Реєстр: mycompany.com
   Простір імен: team
   Образ: app
   Тег: v2.0.0-alpine
```

### Вправа 2: Виправлення ImagePullBackOff (Ціль: 3 хвилини)

```bash
# Створити зламаний Під
k run broken --image=nginx:1.999.0

# Діагностика
k describe pod broken | grep -A5 Events

# Виправлення
k delete pod broken
k run broken --image=nginx:1.21.0

# Перевірка
k get pod broken

# Очищення
k delete pod broken
```

### Вправа 3: Secret для приватного реєстру (Ціль: 4 хвилини)

```bash
# Створити secret реєстру
k create secret docker-registry myregistry \
  --docker-server=private.registry.io \
  --docker-username=testuser \
  --docker-password=testpass

# Створити Під з посиланням на secret
cat << EOF | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: private-pod
spec:
  containers:
  - name: app
    image: private.registry.io/app:latest
  imagePullSecrets:
  - name: myregistry
EOF

# Перевірити, чи secret прив'язано
k get pod private-pod -o jsonpath='{.spec.imagePullSecrets}'

# Очищення
k delete pod private-pod
k delete secret myregistry
```

### Вправа 4: Перевизначення Command та Args (Ціль: 3 хвилини)

```bash
# Створити Під, що перевизначає CMD
cat << EOF | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: custom-cmd
spec:
  containers:
  - name: busybox
    image: busybox
    command: ["sh", "-c"]
    args: ["echo 'Custom command' && sleep 10"]
EOF

# Перевірити логи
k logs custom-cmd

# Перевірити команду
k get pod custom-cmd -o jsonpath='{.spec.containers[0].command}'
k get pod custom-cmd -o jsonpath='{.spec.containers[0].args}'

# Очищення
k delete pod custom-cmd
```

### Вправа 5: Тестування imagePullPolicy (Ціль: 3 хвилини)

```bash
# Створити Піди з різними політиками
cat << EOF | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: pull-always
spec:
  containers:
  - name: nginx
    image: nginx:1.21.0
    imagePullPolicy: Always
---
apiVersion: v1
kind: Pod
metadata:
  name: pull-ifnotpresent
spec:
  containers:
  - name: nginx
    image: nginx:1.21.0
    imagePullPolicy: IfNotPresent
EOF

# Перевірити політики
k get pod pull-always -o jsonpath='{.spec.containers[0].imagePullPolicy}'
k get pod pull-ifnotpresent -o jsonpath='{.spec.containers[0].imagePullPolicy}'

# Очищення
k delete pod pull-always pull-ifnotpresent
```

### Вправа 6: Повне усунення проблем з образами (Ціль: 5 хвилин)

**Сценарій:** Колега створив Деплоймент, але Піди не запускаються.

```bash
# Підготовка (симуляція проблеми)
k create deploy webapp --image=nginx:alpine-wrong-tag

# ВАШЕ ЗАВДАННЯ: Знайти та виправити проблему

# Крок 1: Перевірити статус Деплоймента
k get deploy webapp
k get pods -l app=webapp

# Крок 2: Дослідити помилку
k describe pods -l app=webapp | grep -A10 Events

# Крок 3: Знайти правильний тег образу
# (У реальному сценарії перевірте реєстр або документацію)
# Правильний тег — nginx:alpine

# Крок 4: Виправити
k set image deploy/webapp nginx=nginx:alpine

# Крок 5: Перевірити
k rollout status deploy/webapp
k get pods -l app=webapp

# Очищення
k delete deploy webapp
```

---

## Наступний модуль

[Модуль 1.2: Jobs та CronJobs](module-1.2-jobs-cronjobs/) — Запуск одноразових та запланованих пакетних завдань.
