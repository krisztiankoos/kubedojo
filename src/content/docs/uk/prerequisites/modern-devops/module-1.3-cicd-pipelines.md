---
title: "Модуль 1.3: CI/CD пайплайни"
slug: uk/prerequisites/modern-devops/module-1.3-cicd-pipelines
sidebar:
  order: 4
---
> **Складність**: `[MEDIUM]` — Необхідна автоматизація
>
> **Час на виконання**: 35–40 хвилин
>
> **Передумови**: Модуль 1.1 (IaC), базові навички Git

## Що ви зможете робити після цього модуля

Після цього модуля ви зможете:
- **Пояснити** різницю між Continuous Integration, Continuous Delivery та Continuous Deployment
- **Спроєктувати** базовий CI/CD пайплайн для контейнеризованого застосунку (збірка → тести → сканування → деплой)
- **Порівняти** CI/CD інструменти (GitHub Actions, GitLab CI, Jenkins) і пояснити компроміси
- **Визначити** антипатерни пайплайнів (відсутність тестів, ручні гейти деплою, секрети в коді)

---

## Чому цей модуль важливий

Кожного разу, коли ви пушите код у репозиторій, він має автоматично тестуватися, збиратися та готуватися до розгортання. CI/CD пайплайни (pipelines) усувають проблему «на моїй машині працює» та гарантують стабільні, надійні релізи. Для Kubernetes-застосунків CI/CD — це шлях, яким збираються образи контейнерів та запускаються оновлення в кластері.

---

## CI проти CD

```
┌─────────────────────────────────────────────────────────────┐
│              CI/CD ПАЙПЛАЙН                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  БЕЗПЕРЕРВНА ІНТЕГРАЦІЯ (CI)                                │
│  "Часте злиття коду, перевірка кожної зміни"               │
│                                                             │
│  ┌─────┐    ┌─────┐    ┌─────┐    ┌─────────┐            │
│  │Push │───►│Збірка│───►│ Тест │───►│ Артефакт│            │
│  │коду │    │     │    │     │    │ (образ) │            │
│  └─────┘    └─────┘    └─────┘    └─────────┘            │
│                                                             │
│  БЕЗПЕРЕРВНА ДОСТАВКА (CD - Delivery)                       │
│  "Завжди готовий до деплою, випуск у прод однією кнопкою"  │
│                                                             │
│  ┌─────────┐    ┌───────────┐    ┌──────────┐            │
│  │Артефакт │───►│ Деплой на │───►│ Ручне    │            │
│  │ (образ) │    │ Staging   │    │ Схвалення│            │
│  └─────────┘    └───────────┘    └────┬─────┘            │
│                                       │                    │
│                                       ▼                    │
│                              ┌──────────────┐             │
│                              │ Деплой на Прод│             │
│                              └──────────────┘             │
│                                                             │
│  БЕЗПЕРЕРВНЕ РОЗГОРТАННЯ (CD - Deployment)                  │
│  "Кожна зміна йде прямо у продакшн"                         │
│  (Те саме, що й вище, але без кроку ручного схвалення)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Етапи CI пайплайну

### 1. Джерело (Source)

```yaml
# Запуск при пуші коду
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
```

### 2. Збірка (Build)

```yaml
# Збірка застосунку
steps:
  - name: Build
    run: |
      npm install
      npm run build
```

### 3. Тестування (Test)

```yaml
# Запуск усіх тестів
steps:
  - name: Unit Tests
    run: npm test

  - name: Integration Tests
    run: npm run test:integration

  - name: Lint (Перевірка стилю коду)
    run: npm run lint
```

### 4. Сканування безпеки

```yaml
# Пошук вразливостей
steps:
  - name: Security Scan
    run: |
      npm audit
      trivy fs .
```

### 5. Збірка образу

```yaml
# Створення образу контейнера
steps:
  - name: Build Docker Image
    run: |
      docker build -t myapp:${{ github.sha }} .
      docker push myapp:${{ github.sha }}
```

---

## Ландшафт інструментів CI/CD

```
┌─────────────────────────────────────────────────────────────┐
│              ІНСТРУМЕНТИ CI/CD                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ХМАРНІ (SaaS)                                              │
│  ├── GitHub Actions     (інтегровано з GitHub)             │
│  ├── GitLab CI/CD       (інтегровано з GitLab)             │
│  ├── CircleCI           (швидкий, cloud-native)            │
│  └── Travis CI          (популярний для Open Source)       │
│                                                             │
│  SELF-HOSTED (Власні сервери)                               │
│  ├── Jenkins            (найгнучкіший, найстаріший)        │
│  ├── GitLab Runner      (для власної інсталяції GitLab)    │
│  ├── Drone              (орієнтований на контейнери)       │
│  └── Tekton             (Kubernetes-native)                │
│                                                             │
│  KUBERNETES-NATIVE                                          │
│  ├── Tekton             (пайплайни як CRD)                 │
│  ├── Argo Workflows     (оркестрація складних воркфлоу)    │
│  └── JenkinsX           (спеціальна версія Jenkins для K8s)│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## GitHub Actions (Найпопулярніший)

### Базовий воркфлоу

```yaml
# .github/workflows/ci.yaml
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Run lint
        run: npm run lint

  build:
    needs: test  # Запускати тільки якщо тести пройшли успішно
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Log in to registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Push image
        run: |
          docker tag myapp:${{ github.sha }} ghcr.io/${{ github.repository }}:${{ github.sha }}
          docker push ghcr.io/${{ github.repository }}:${{ github.sha }}
```

### Ключові поняття

| Термін | Опис |
|---------|-------------|
| `workflow` | Автоматизований процес, що налаштовується |
| `job` | Набір кроків, що виконуються на одному ранері |
| `step` | Окреме завдання (команда або action) |
| `action` | Багаторазовий блок коду (готовий плагін) |
| `runner` | Машина (VM), на якій виконується воркфлоу |
| `secrets` | Зашифровані змінні середовища (паролі, токени) |

---

## GitLab CI/CD

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

test:
  stage: test
  image: node:20
  script:
    - npm ci
    - npm test
    - npm run lint
  cache:
    paths:
      - node_modules/

build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker build -t $DOCKER_IMAGE .
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker push $DOCKER_IMAGE
  only:
    - main

deploy_staging:
  stage: deploy
  script:
    - kubectl set image deployment/myapp myapp=$DOCKER_IMAGE
  environment:
    name: staging
  only:
    - main

deploy_production:
  stage: deploy
  script:
    - kubectl set image deployment/myapp myapp=$DOCKER_IMAGE
  environment:
    name: production
  when: manual  # Потребує натискання кнопки для деплою
  only:
    - main
```

---

## Пайплайн для Kubernetes

Типовий CI/CD пайплайн для Kubernetes застосунку:

```
┌─────────────────────────────────────────────────────────────┐
│              KUBERNETES CI/CD ПАЙПЛАЙН                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. КОД                                                     │
│     └── Розробник пушить у Git                             │
│                                                             │
│  2. ЗБІРКА (BUILD)                                          │
│     ├── Запуск unit-тестів                                 │
│     ├── Запуск інтеграційних тестів                        │
│     ├── Статичний аналіз (lint, security)                  │
│     └── Збірка образу контейнера                           │
│                                                             │
│  3. ПУБЛІКАЦІЯ                                              │
│     ├── Тегування образу (SHA коміту)                      │
│     ├── Пуш у реєстр контейнерів                           │
│     └── Сканування образу на вразливості                   │
│                                                             │
│  4. ОНОВЛЕННЯ МАНІФЕСТІВ                                    │
│     └── Оновлення K8s YAML новим тегом образу              │
│         (Для GitOps: коміт у GitOps репозиторій)           │
│                                                             │
│  5. ДЕПЛОЙ (DEPLOY)                                         │
│     ├── GitOps: Агент бачить зміни та синхронізує          │
│     └── Або: Пайплайн запускає kubectl/helm                │
│                                                             │
│  6. ВЕРИФІКАЦІЯ                                             │
│     ├── Smoke-тести запущеного додатка                     │
│     └── Автоматичний відкат у разі помилки                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Найкращі практики пайплайнів

### 1. Швидкий зворотний зв'язок (Fast Feedback)

```yaml
# Спочатку запускайте швидкі перевірки
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: npm run lint  # Дуже швидко, ловить явні помилки

  unit-test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test      # Середня швидкість

  integration-test:
    needs: [lint, unit-test]  # Тільки якщо швидкі перевірки пройшли
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:e2e  # Повільно, але важливо
```

### 2. Кешування залежностей

```yaml
- name: Cache node modules
  uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

### 3. Матричні збірки (Matrix Builds)

```yaml
# Тестування на декількох версіях одночасно
jobs:
  test:
    strategy:
      matrix:
        node-version: [18, 20, 22]
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm test
```

### 4. Безпека секретів

```yaml
# Ніколи не виводьте секрети в консоль (echo)!
- name: Deploy
  env:
    KUBE_CONFIG: ${{ secrets.KUBECONFIG }}
  run: |
    echo "$KUBE_CONFIG" | base64 -d > kubeconfig
    kubectl --kubeconfig=kubeconfig apply -f manifests/
    rm kubeconfig  # Прибрати за собою
```

---

## Антипатерни CI/CD (Чого уникати)

| Антипатерн | Проблема | Рішення |
|------------|----------|---------|
| Ручні кроки | Людський фактор, повільно | Автоматизуйте все |
| "Флакі" тести (Flaky tests) | Втрата довіри до CI | Виправте або видаліть нестабільні тести |
| Довгі пайплайни | Повільний розворот | Паралелізація та кешування |
| Деплой з ноутбука | Немає аудиту | Тільки через пайплайни |
| Спільні креденшали | Ризик безпеки | Окремі доступи для кожного середовища |
| Немає плану відкату | Ризик простою | Автоматизуйте rollback |

---

## Чи знали ви?

- **Jenkins уже понад 20 років** (розпочався як Hudson у 2004-му). Попри вік, він досі запускає мільйони пайплайнів щодня.

- **Ранери GitHub Actions** — це свіжі віртуальні машини для кожного завдання. Ви щоразу отримуєте чисте середовище, що запобігає проблемам накопиченого сміття.

- **Найбільша CI система у світі** — у Google. Вона запускає мільйони білдів на день на розподіленій інфраструктурі TAP (Test Automation Platform).

---

## Типові помилки

| Помилка | Наслідки | Рішення |
|---------|----------|---------|
| Тести всередині Docker build | Повільні білди, закешовані помилки | Розділяйте етапи тестування та збірки |
| Тег `latest` для базових образів | Непередбачувана збірка | Фіксуйте конкретні версії |
| Відсутність валідації YAML | Помилки при запуску | Додайте крок перевірки маніфестів |
| Довгоживучі гілки функцій | Складні конфлікти злиття | Маленькі гілки, часті мержі |
| Пропуск CI для "дрібних змін" | Непомітні баги | CI для всього без винятків |

---

## Тест

1. **Яка різниця між Continuous Delivery та Continuous Deployment?**
   <details>
   <summary>Відповідь</summary>
   Continuous Delivery: Кожна зміна готова до випуску, але деплой у продакшн потребує ручного натискання кнопки. Continuous Deployment: Кожна зміна, що пройшла тести, автоматично йде у продакшн без втручання людини.
   </details>

2. **Чому варто тегувати образи контейнерів SHA коміту замість "latest"?**
   <details>
   <summary>Відповідь</summary>
   SHA коміту забезпечує простежуваність (точно відомо, який код запущено), дозволяє легко зробити відкат до попередньої версії та запобігає проблемам із кешуванням ("latest" може вказувати на стару версію в кеші).
   </details>

3. **Навіщо потрібне кешування в CI пайплайнах?**
   <details>
   <summary>Відповідь</summary>
   Кешування дозволяє не повторювати дорогі операції (наприклад, завантаження гігабайтів бібліотек) при кожному запуску. Це прискорює пайплайни в рази (наприклад, з 10 хвилин до 2).
   </details>

4. **Як CI/CD інтегрується з GitOps?**
   <details>
   <summary>Відповідь</summary>
   CI збирає та пушить образи в реєстр. Потім CI оновлює GitOps-репозиторій новим тегом образу. GitOps-агент помічає зміну в Git і синхронізує кластер. CI не торкається кластера напряму.
   </details>

---

## Практична вправа

**Завдання**: Симуляція роботи CI пайплайну локально.

```bash
# Ця вправа демонструє етапи роботи справжнього CI

# 1. Створіть структуру проєкту
mkdir -p ~/ci-demo
cd ~/ci-demo

# 2. Створіть простий додаток
cat << 'EOF' > app.py
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

if __name__ == "__main__":
    print("Привіт від CI demo!")
EOF

# 3. Створіть тести
cat << 'EOF' > test_app.py
import app

def test_add():
    assert app.add(2, 3) == 5

def test_subtract():
    assert app.subtract(5, 3) == 2
EOF

# 4. Створіть Dockerfile
cat << 'EOF' > Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app.py .
CMD ["python", "app.py"]
EOF

# 5. Симуляція етапів CI

echo "=== ЕТАП: Lint ==="
# У справжньому CI: запуск лінтера
python3 -m py_compile app.py && echo "Lint пройдено!"

echo ""
echo "=== ЕТАП: Тестування ==="
# У справжньому CI: pytest
pip3 install pytest -q 2>/dev/null
python3 -m pytest test_app.py -v

echo ""
echo "=== ЕТАП: Збірка (Build) ==="
# Збірка образу
docker build -t ci-demo:local .

echo ""
echo "=== ЕТАП: Сканування безпеки ==="
# У справжньому CI: trivy, snyk тощо
echo "Сканування образу... (симуляція)"
echo "Вразливостей не знайдено!"

echo ""
echo "=== ЕТАП: Публікація (Push) ==="
echo "Було б відправлено в: registry/ci-demo:local"
echo "(Для демо пропускаємо)"

# 6. Прибирання
cd ..
rm -rf ~/ci-demo

echo ""
echo "=== CI Пайплайн завершено ==="
```

**Критерії успіху**: Розуміння послідовності кроків CI пайплайну.

---

## Підсумок

**CI/CD пайплайни** автоматизують шлях коду до продакшну:

**CI (Continuous Integration)**:
- Часті злиття коду.
- Збірка та тест кожної зміни.
- Раннє виявлення проблем.

**CD (Continuous Delivery/Deployment)**:
- Постійна готовність до деплою.
- Автоматизація розгортання.
- Швидкий відкат.

**Ключові практики**:
- Швидкий фідбек (спочатку швидкі етапи).
- Кешування залежностей.
- Безпечне керування секретами.
- Незмінні артефакти (образи з SHA-тегами).

---

## Наступний модуль

[Модуль 1.4: Основи спостережуваності](../module-1.4-observability/) — Моніторинг, логування та трасування.
