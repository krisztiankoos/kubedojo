---
title: "Модуль 1.2: Основи Docker"
slug: uk/prerequisites/cloud-native-101/module-1.2-docker-fundamentals
sidebar:
  order: 3
---
> **Складність**: `[MEDIUM]` — Потрібна практична робота
>
> **Час на виконання**: 45–50 хвилин
>
> **Передумови**: Модуль 1.1 (Що таке контейнери?)

---

## Що ви зможете робити після цього модуля

Після цього модуля ви зможете:
- **Створювати** Docker-образ з Dockerfile та пояснити, що робить кожна інструкція
- **Запускати** контейнери з маппінгом портів, змінними середовища та монтуванням томів
- **Дебажити** контейнер, що падає, читаючи логи та заходячи в нього через exec
- **Пояснити** систему шарів образу та чому порядок шарів важливий для швидкості збирання

---

## Чому цей модуль важливий

Docker — це найпопулярніший інструмент для створення образів контейнерів. Хоча Kubernetes більше не використовує Docker як середовище виконання (runtime), він залишається стандартом для:
- Збірки образів контейнерів
- Локальної розробки
- Тестування та налагодження

Вам потрібно знати Docker «достатньо», щоб розуміти Kubernetes — ставати майстром Docker не обов'язково.

---

## Встановлення Docker

### macOS
```bash
# Встановіть Docker Desktop
# Завантажте з https://docker.com/products/docker-desktop
# Або через Homebrew:
brew install --cask docker
```

### Linux (Ubuntu/Debian)
```bash
# Офіційне встановлення
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Вийдіть і зайдіть знову, щоб зміни групи подіяли
```

### Перевірка встановлення
```bash
docker --version
# Docker version 24.x.x, build xxxxx

docker run hello-world
# Має з'явитися повідомлення "Hello from Docker!"
```

---

## Ваш перший контейнер

```bash
# Запустіть nginx (вебсервер)
docker run -d -p 8080:80 nginx

# Що сталося:
# - Завантажено образ nginx з Docker Hub
# - Створено контейнер на основі образу
# - Контейнер запущено у фоновому режимі (-d)
# - Порт 8080 (хоста) перенаправлено на порт 80 (контейнера)
```

```bash
# Перевірте роботу
curl http://localhost:8080
# Поверне HTML-код вітальної сторінки nginx

# Перегляньте запущені контейнери
docker ps
# CONTAINER ID  IMAGE  COMMAND                 STATUS         PORTS                  NAMES
# a1b2c3d4e5f6  nginx  "/docker-entrypoint.…"  Up 10 seconds  0.0.0.0:8080->80/tcp   tender_tesla

# Зупиніть контейнер
docker stop a1b2c3d4e5f6

# Видаліть контейнер
docker rm a1b2c3d4e5f6
```

---

## Основні команди Docker

### Життєвий цикл контейнера

```bash
# Запуск контейнера
docker run [ОПЦІЇ] ОБРАЗ [КОМАНДА]

# Популярні опції:
docker run -d nginx                    # Фоновий режим (detached)
docker run -it ubuntu bash             # Інтерактивний термінал
docker run -p 8080:80 nginx           # Перенаправлення портів
docker run -v /шлях/хоста:/шлях/контейнера nginx  # Монтування тома (Volume)
docker run --name myapp nginx         # Назва контейнера
docker run -e MY_VAR=value nginx      # Змінна середовища
docker run --rm nginx                 # Видалити після зупинки

# Керування контейнерами
docker ps                              # Список запущених контейнерів
docker ps -a                           # Список усіх контейнерів
docker stop CONTAINER                  # Планова зупинка
docker kill CONTAINER                  # Примусова зупинка
docker rm CONTAINER                    # Видалити зупинений контейнер
docker rm -f CONTAINER                 # Примусове видалення (stop + rm)
```

### Інспектування контейнерів

```bash
# Перегляд логів
docker logs CONTAINER
docker logs -f CONTAINER               # Слідкувати за логами (tail)
docker logs --tail 100 CONTAINER       # Останні 100 рядків

# Виконання команди в запущеному контейнері
docker exec -it CONTAINER bash         # Інтерактивна оболонка
docker exec CONTAINER ls /app          # Просто запустити команду

# Детальна інформація
docker inspect CONTAINER               # Повна інформація у форматі JSON
docker stats                           # Використання ресурсів
docker top CONTAINER                   # Список запущених процесів
```

### Керування образами

```bash
# Завантаження образів
docker pull nginx
docker pull nginx:1.25
docker pull gcr.io/project/image:tag

# Список образів
docker images

# Видалення образів
docker rmi nginx
docker image prune                     # Видалити образи, що не використовуються

# Збірка образів (розглянемо далі)
docker build -t myapp:v1 .
```

---

## Збірка образів контейнерів

### Dockerfile

Dockerfile — це текстовий файл з інструкціями для збірки образу:

```dockerfile
# Базовий образ
FROM python:3.11-slim

# Робоча директорія
WORKDIR /app

# Копіювання файлу залежностей
COPY requirements.txt .

# Встановлення залежностей
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання коду застосунку
COPY . .

# Оголошення порту (документація)
EXPOSE 8000

# Команда за замовчуванням
CMD ["python", "app.py"]
```

### Збірка та запуск

```bash
# Збірка образу
docker build -t myapp:v1 .

# Запуск контейнера з образу
docker run -d -p 8000:8000 myapp:v1
```

### Інструкції Dockerfile

| Інструкція | Призначення |
|------------|-------------|
| `FROM` | Базовий образ, на якому все будується |
| `WORKDIR` | Встановлення робочої директорії |
| `COPY` | Копіювання файлів із хоста в образ |
| `ADD` | Як COPY, але вміє розпаковувати архіви та завантажувати за URL |
| `RUN` | Виконання команди під час збірки |
| `ENV` | Встановлення змінної середовища |
| `EXPOSE` | Документування порту, який використовує додаток |
| `CMD` | Команда за замовчуванням при старті контейнера |
| `ENTRYPOINT` | Команда, що виконується завжди (CMD стає аргументами) |

---

## Практичний приклад: Вебдодаток на Python

Створіть простий застосунок на Python:

**app.py**
```python
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    name = os.getenv('NAME', 'Світ')
    return f'Привіт, {name}!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

**requirements.txt**
```
flask==3.0.0
```

**Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Спочатку копіюємо залежності (краще кешування)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код застосунку
COPY app.py .

EXPOSE 8000

CMD ["python", "app.py"]
```

**Збірка та запуск**
```bash
# Збірка
docker build -t hello-flask:v1 .

# Запуск
docker run -d -p 8000:8000 -e NAME=Docker hello-flask:v1

# Перевірка
curl http://localhost:8000
# Привіт, Docker!

# Прибирання
docker rm -f $(docker ps -q --filter ancestor=hello-flask:v1)
```

---

## Кешування шарів

Docker кешує шари для швидкої збірки. Порядок має значення:

```dockerfile
# ПОГАНО: зміни в коді скидають кеш залежностей
FROM python:3.11-slim
WORKDIR /app
COPY . .                              # Будь-яка зміна ламає кеш
RUN pip install -r requirements.txt   # Перевстановлює все щоразу!
CMD ["python", "app.py"]

# ДОБРЕ: залежності кешуються окремо
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .               # Змінюється лише при зміні deps
RUN pip install -r requirements.txt   # Кешується, поки deps ті самі
COPY . .                              # Зміни в коді не ламають кеш pip
CMD ["python", "app.py"]
```

---

## Docker Compose (Локальна робота з декількома контейнерами)

Для розробки з використанням декількох сервісів:

**docker-compose.yml**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_PASSWORD=secret
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

```bash
# Запустити всі сервіси
docker compose up -d

# Перегляд логів
docker compose logs -f

# Зупинити все
docker compose down

# Зупинити та видалити томи (volumes)
docker compose down -v
```

**Примітка**: Docker Compose — для локальної розробки. У продакшні його замінює Kubernetes.

---

## Візуалізація: Робочий процес Docker

```
┌─────────────────────────────────────────────────────────────┐
│              РОБОЧИЙ ПРОЦЕС DOCKER                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. ПИШЕМО                                                  │
│     ┌─────────────┐                                        │
│     │ Dockerfile  │                                        │
│     └──────┬──────┘                                        │
│            │                                                │
│            ▼                                                │
│  2. ЗБИРАЄМО                                                │
│     ┌─────────────┐                                        │
│     │docker build │──────► Образ (myapp:v1)                │
│     └──────┬──────┘                                        │
│            │                                                │
│            ▼                                                │
│  3. ПУБЛІКУЄМО (опційно)                                    │
│     ┌─────────────┐                                        │
│     │docker push  │──────► Реєстр (Docker Hub, ECR...)     │
│     └──────┬──────┘                                        │
│            │                                                │
│            ▼                                                │
│  4. ЗАПУСКАЄМО                                              │
│     ┌─────────────┐                                        │
│     │docker run   │──────► Контейнер (працюючий екземпляр) │
│     └─────────────┘                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Найкращі практики

### Розмір образу

```dockerfile
# ПОГАНО: повна ОС, величезний образ
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3 python3-pip
COPY . .
RUN pip3 install -r requirements.txt

# ДОБРЕ: slim база, менший образ
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# ЩЕ КРАЩЕ: Alpine (крихітна база)
FROM python:3.11-alpine
# Примітка: Alpine використовує apk замість apt, та musl замість glibc
```

### Безпека

```dockerfile
# ПОГАНО: робота від імені root
FROM python:3.11-slim
COPY . .
CMD ["python", "app.py"]  # Працює як root!

# ДОБРЕ: не-root користувач
FROM python:3.11-slim
RUN useradd -m appuser
WORKDIR /app
COPY --chown=appuser:appuser . .
USER appuser
CMD ["python", "app.py"]
```

### Один процес на контейнер

```
# ПОГАНО: декілька сервісів в одному контейнері
Контейнер: nginx + python app + redis

# ДОБРЕ: окремі контейнери
Контейнер 1: nginx
Контейнер 2: python app
Контейнер 3: redis
(Використовуйте Docker Compose або Kubernetes для оркестрації)
```

---

## Чи знали ви?

- **Образи Docker адресуються за вмістом.** SHA256-хеш образу є його справжнім ідентифікатором. Теги — це лише зручні для людей псевдоніми.

- **Багатоетапні збірки (multi-stage builds) кардинально зменшують розмір.** Збирайте в одному етапі, копіюйте тільки артефакти у фінальний етап.

- **Тег `latest` не є особливим.** Docker не оновлює його автоматично. Це просто домовленість, яка означає "те, що було запушено останнім".

- **Docker Desktop — це не те саме, що Docker.** Docker (інструмент) безкоштовний. Docker Desktop (GUI/VM для Mac/Windows) має ліцензійні вимоги для бізнесу.

---

## Поширені помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| Використання тегу `latest` | Непередбачувані версії | Використовуйте конкретні теги (`:1.25.3`) |
| Робота під root | Ризик безпеки | Додайте інструкцію `USER` |
| Ігнорування порядку шарів | Повільна збірка | Ставте те, що часто змінюється, в кінець |
| Копіювання всього підряд | Великі образи, витік секретів | Використовуйте `.dockerignore` |
| Нехтування очищенням | Диск переповнюється | Регулярно запускайте `docker system prune` |

---

## Тест

1. **Що робить команда `docker run -d -p 8080:80 nginx`?**
   <details>
   <summary>Відповідь</summary>
   Запускає контейнер nginx у фоновому режимі (-d), прокидаючи порт 8080 хост-машини на порт 80 контейнера. nginx буде доступний за адресою http://localhost:8080.
   </details>

2. **Чому варто ставити `COPY requirements.txt` перед `COPY . .` у Dockerfile?**
   <details>
   <summary>Відповідь</summary>
   Для кешування шарів. Якщо requirements.txt не змінився, Docker використає закешований шар для `pip install`. Якщо копіювати все одразу, будь-яка зміна в коді змусить Docker перевстановлювати всі залежності.
   </details>

3. **У чому різниця між `CMD` та `RUN`?**
   <details>
   <summary>Відповідь</summary>
   `RUN` виконується під час збірки образу (встановлення пакетів тощо). `CMD` визначає команду за замовчуванням, яка виконується при запуску контейнера. RUN створює шари образу, CMD — лише встановлює метадані.
   </details>

4. **Навіщо використовувати Docker Compose замість декількох команд `docker run`?**
   <details>
   <summary>Відповідь</summary>
   Docker Compose керує декількома контейнерами як єдиним застосунком. Він налаштовує мережу між сервісами, створює томи, визначає порядок запуску та описує все декларативно в одному файлі.
   </details>

---

## Практична вправа

**Завдання**: Зберіть та запустіть власний образ.

1. Створіть директорію проєкту:
```bash
mkdir hello-docker && cd hello-docker
```

2. Створіть `app.py`:
```python
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Привіт від Docker!\n')

HTTPServer(('', 8000), Handler).serve_forever()
```

3. Створіть `Dockerfile`:
```dockerfile
FROM python:3.11-alpine
WORKDIR /app
COPY app.py .
EXPOSE 8000
CMD ["python", "app.py"]
```

4. Зберіть та запустіть:
```bash
docker build -t hello-docker:v1 .
docker run -d -p 8000:8000 --name hello hello-docker:v1
curl http://localhost:8000
docker rm -f hello
```

**Критерії успіху**: `curl http://localhost:8000` повертає "Привіт від Docker!"

---

## Підсумок

Мінімум знань Docker для Kubernetes:

**Команди**:
- `docker run` — Запуск контейнерів
- `docker ps` — Список контейнерів
- `docker logs` — Перегляд виводу
- `docker exec` — Команди всередині контейнерів
- `docker build` — Створення образів
- `docker push/pull` — Обмін образами

**Основи Dockerfile**:
- `FROM` — Базовий образ
- `COPY` — Додавання файлів
- `RUN` — Виконання під час збірки
- `CMD` — Команда запуску

**Найкращі практики**:
- Використовуйте конкретні теги образів
- Оптимізуйте кешування шарів
- Працюйте від імені не-root користувача
- Один процес на один контейнер

---

## Наступний модуль

[Модуль 1.3: Що таке Kubernetes?](../module-1.3-what-is-kubernetes/) — Огляд системи оркестрації контейнерів високого рівня.
