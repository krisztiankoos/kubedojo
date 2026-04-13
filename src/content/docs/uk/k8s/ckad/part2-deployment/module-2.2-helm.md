---
title: "\u041c\u043e\u0434\u0443\u043b\u044c 2.2: \u041f\u0430\u043a\u0435\u0442\u043d\u0438\u0439 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 Helm"
slug: uk/k8s/ckad/part2-deployment/module-2.2-helm
sidebar: 
  order: 2
lab: 
  id: ckad-2.2-helm
  url: https://killercoda.com/kubedojo/scenario/ckad-2.2-helm
  duration: "30 min"
  difficulty: intermediate
  environment: kubernetes
---
> **Складність**: `[MEDIUM]` — необхідний інструмент, доданий до CKAD 2025
>
> **Час на виконання**: 45–55 хвилин
>
> **Передумови**: Модуль 2.1 (Деплойменти), розуміння YAML-шаблонів

---

## Що ви зможете робити

Після завершення цього модуля ви зможете:
- **Розгорнути** застосунки за допомогою `helm install` з власними значеннями та вказанням простору імен
- **Створити** перевизначення значень для кастомізації поведінки чарту для різних середовищ
- **Діагностувати** невдалі релізи Helm за допомогою `helm status`, `helm history` та операцій відкату
- **Пояснити** структуру чарту Helm, включно з шаблонами, значеннями та життєвим циклом релізу

---

## Чому цей модуль важливий

Helm — це пакетний менеджер для Kubernetes. Замість керування десятками YAML-файлів Helm пакує їх у «чарти», які можна встановлювати, оновлювати та відкочувати як єдине ціле. У 2025 році іспит CKAD додав Helm як обов'язкову навичку.

Ви зіткнетесь із такими питаннями:
- Встановити чарт із репозиторію
- Оновити реліз з новими значеннями
- Відкотити невдалий реліз
- Переглянути та дослідити релізи
- Створити базові кастомізації чартів

> **Аналогія з магазином застосунків**
>
> Helm — це як магазин застосунків для Kubernetes. Чарти — це застосунки — попередньо зібрані, протестовані та готові до встановлення. Так само як ви встановлюєте Slack одним натисканням замість того, щоб компілювати його самостійно, Helm дозволяє встановлювати складні застосунки (бази даних, стеки моніторингу, вебсервери) однією командою. Values — це як налаштування застосунку — ви змінюєте поведінку, не модифікуючи сам застосунок.

---

## Концепції Helm

### Ключова термінологія

| Термін | Опис |
|--------|------|
| **Chart** | Пакет ресурсів Kubernetes (як застосунок) |
| **Release** | Встановлений екземпляр чарту |
| **Repository** | Колекція чартів (як apt-репозиторії) |
| **Values** | Конфігурація для кастомізації чарту |
| **Revision** | Версія релізу після оновлення/відкату |

### Як працює Helm

```
Чарт (шаблон) + Values (конфігурація) = Реліз (працюючий застосунок)
```

```
┌─────────────────────────────────────────────────────────┐
│                  Робочий процес Helm                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Репозиторій        Чарт             Реліз              │
│  ┌─────────┐       ┌─────────┐      ┌─────────┐        │
│  │ bitnami │──────▶│  nginx  │─────▶│ my-web  │        │
│  │  repo   │ pull  │  chart  │install│ release │        │
│  └─────────┘       └─────────┘      └─────────┘        │
│                         │                 │            │
│                         ▼                 ▼            │
│                    ┌─────────┐      ┌─────────┐        │
│                    │ values  │      │  Поди   │        │
│                    │  .yaml  │      │Сервіси  │        │
│                    └─────────┘      │ConfigMaps│       │
│                                     └─────────┘        │
└─────────────────────────────────────────────────────────┘
```

---

## Команди Helm

### Керування репозиторіями

```bash
# Додати репозиторій
helm repo add bitnami https://charts.bitnami.com/bitnami

# Додати stable-репозиторій
helm repo add stable https://charts.helm.sh/stable

# Оновити кеш репозиторію
helm repo update

# Переглянути репозиторії
helm repo list

# Шукати чарти
helm search repo nginx
helm search repo bitnami/nginx

# Шукати з версіями
helm search repo nginx --versions
```

### Встановлення чартів

```bash
# Встановити зі значеннями за замовчуванням
helm install my-release bitnami/nginx

# Встановити у конкретний простір імен
helm install my-release bitnami/nginx -n production

# Встановити та створити простір імен
helm install my-release bitnami/nginx -n production --create-namespace

# Встановити з кастомним файлом значень
helm install my-release bitnami/nginx -f values.yaml

# Встановити з інлайн-значеннями
helm install my-release bitnami/nginx --set replicaCount=3

# Встановити з кількома перевизначеннями значень
helm install my-release bitnami/nginx \
  --set replicaCount=3 \
  --set service.type=NodePort

# Dry-run (побачити, що буде створено)
helm install my-release bitnami/nginx --dry-run

# Автоматично згенерувати ім'я
helm install bitnami/nginx --generate-name
```

### Перегляд релізів

```bash
# Список релізів у поточному просторі імен
helm list

# Список у всіх просторах імен
helm list -A

# Список у конкретному просторі імен
helm list -n production

# Список з усіма статусами
helm list --all

# Фільтрувати за статусом
helm list --failed
helm list --pending
```

### Дослідження чартів та релізів

```bash
# Показати інформацію про чарт
helm show chart bitnami/nginx

# Показати значення за замовчуванням
helm show values bitnami/nginx

# Показати всю інформацію
helm show all bitnami/nginx

# Отримати значення релізу
helm get values my-release

# Отримати всю інформацію про реліз
helm get all my-release

# Отримати маніфест релізу (відрендерений YAML)
helm get manifest my-release

# Отримати історію релізу
helm history my-release
```

### Оновлення релізів

```bash
# Оновити з новими значеннями
helm upgrade my-release bitnami/nginx --set replicaCount=5

# Оновити з файлом значень
helm upgrade my-release bitnami/nginx -f new-values.yaml

# Оновити або встановити, якщо не існує
helm upgrade --install my-release bitnami/nginx

# Перевикористати наявні значення та додати нові
helm upgrade my-release bitnami/nginx --reuse-values --set image.tag=1.21
```

### Відкат

```bash
# Відкат до попередньої ревізії
helm rollback my-release

# Відкат до конкретної ревізії
helm rollback my-release 2

# Спочатку перевірити історію
helm history my-release
```

### Видалення

```bash
# Видалити реліз
helm uninstall my-release

# Видалити, але зберегти історію
helm uninstall my-release --keep-history

# Видалити з простору імен
helm uninstall my-release -n production
```

---

## Робота зі значеннями (Values)

### Ієрархія значень (від найнижчого до найвищого пріоритету)

1. Значення за замовчуванням у чарті (`values.yaml`)
2. Значення батьківського чарту
3. Файл значень, переданий через `-f`
4. Окремі значення через `--set`

### Приклад файлу значень

```yaml
# my-values.yaml
replicaCount: 3

image:
  repository: nginx
  tag: "1.21"
  pullPolicy: IfNotPresent

service:
  type: NodePort
  port: 80

resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 50m
    memory: 64Mi

nodeSelector:
  disktype: ssd
```

### Використання файлів значень

```bash
# Встановити з файлом значень
helm install my-release bitnami/nginx -f my-values.yaml

# Кілька файлів значень (наступний перевизначає попередній)
helm install my-release bitnami/nginx -f values.yaml -f production.yaml

# Поєднати файл та інлайн
helm install my-release bitnami/nginx -f values.yaml --set replicaCount=5
```

### Типовий синтаксис --set

```bash
# Просте значення
--set replicaCount=3

# Вкладене значення
--set image.tag=1.21

# Рядкове значення (лапки для спецсимволів)
--set image.repository="my-registry.com/nginx"

# Значення масиву
--set nodeSelector.disktype=ssd

# Кілька значень
--set replicaCount=3,service.type=NodePort

# Елементи списку
--set ingress.hosts[0].host=example.com
```

---

## Практичні сценарії для іспиту

### Сценарій 1: Встановлення та налаштування

```bash
# Додати репозиторій
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Встановити з кастомними значеннями
helm install my-nginx bitnami/nginx \
  --set replicaCount=2 \
  --set service.type=ClusterIP \
  -n web --create-namespace

# Перевірити
helm list -n web
k get pods -n web
```

### Сценарій 2: Оновлення та відкат

```bash
# Перевірити поточний реліз
helm list
helm get values my-nginx

# Оновити
helm upgrade my-nginx bitnami/nginx --set replicaCount=3

# Щось пішло не так — відкат
helm history my-nginx
helm rollback my-nginx 1

# Перевірити
helm list
```

### Сценарій 3: Дослідження перед встановленням

```bash
# Подивитися, що встановлюєте
helm show values bitnami/nginx | head -50

# Dry run, щоб побачити згенеровані маніфести
helm install test bitnami/nginx --dry-run | less

# Потім встановити
helm install my-nginx bitnami/nginx
```

---

## Структура чарту (довідка)

```
my-chart/
├── Chart.yaml          # Метадані чарту
├── values.yaml         # Конфігурація за замовчуванням
├── charts/             # Залежні чарти
├── templates/          # Маніфести Kubernetes
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── _helpers.tpl    # Допоміжні шаблони
│   └── NOTES.txt       # Примітки після встановлення
└── README.md
```

На іспиті CKAD ви не створюватимете чарти, але розуміння структури допомагає з дебагом.

---

## Усунення проблем із Helm

### Типові проблеми

```bash
# Реліз застряг у pending-install
helm list --pending
helm uninstall stuck-release

# Подивитися, що не так
helm get manifest my-release | k apply --dry-run=server -f -

# Дебаг рендерингу шаблонів
helm template my-release bitnami/nginx --debug

# Перевірити статус релізу
helm status my-release
```

### Корисні команди для дебагу

```bash
# Побачити відрендерені шаблони
helm template my-release bitnami/nginx > rendered.yaml

# Валідувати без встановлення
helm install my-release bitnami/nginx --dry-run --debug

# Отримати примітки (інструкції після встановлення)
helm get notes my-release
```

---

## Чи знали ви?

- **Helm 3 прибрав Tiller.** Helm 2 потребував серверний компонент (Tiller) з привілеями cluster-admin. Helm 3 працює повністю на стороні клієнта, використовуючи ваші дозволи kubeconfig.

- **`helm upgrade --install`** є ідемпотентним — встановлює, якщо релізу не існує, або оновлює, якщо існує. Чудово підходить для CI/CD-пайплайнів.

- **Helm зберігає дані релізу як Secrets** (за замовчуванням) або ConfigMaps. Кожна ревізія — це окремий Secret, що дозволяє відкат до будь-якого попереднього стану.

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| Забули `helm repo update` | Встановлення старих версій чартів | Завжди оновлюйте перед встановленням |
| Неправильний простір імен | Реліз у просторі імен default | Використовуйте `-n namespace` послідовно |
| Друкарські помилки в `--set` | Значення не застосовуються | Використовуйте `--dry-run` для перевірки |
| Забули `--reuse-values` | Оновлення скидає до значень за замовчуванням | Додайте прапорець, коли змінюєте лише деякі значення |
| Не перевірили історію перед відкатом | Відкат до неправильної версії | Спочатку виконайте `helm history` |

---

## Тест

1. **Як встановити чарт і встановити `replicaCount` на 3?**
   <details>
   <summary>Відповідь</summary>
   `helm install my-release bitnami/nginx --set replicaCount=3`
   </details>

2. **Як побачити, які значення використовує реліз?**
   <details>
   <summary>Відповідь</summary>
   `helm get values my-release`

   Додайте `--all`, щоб побачити обчислені значення, включаючи значення за замовчуванням.
   </details>

3. **Як відкотити до ревізії 2?**
   <details>
   <summary>Відповідь</summary>
   `helm rollback my-release 2`
   </details>

4. **Що робить `helm upgrade --install`?**
   <details>
   <summary>Відповідь</summary>
   Встановлює реліз, якщо він не існує, або оновлює його, якщо існує. Це робить команду ідемпотентною — безпечною для багаторазового виконання.
   </details>

---

## Практична вправа

**Завдання**: Повний робочий процес Helm із реальним чартом.

**Підготовка:**
```bash
# Додати репозиторій
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

**Частина 1: Дослідження та встановлення**
```bash
# Побачити доступні значення
helm show values bitnami/nginx | head -30

# Встановити з кастомними значеннями
helm install web bitnami/nginx \
  --set replicaCount=2 \
  --set service.type=ClusterIP

# Перевірити встановлення
helm list
k get pods -l app.kubernetes.io/instance=web
```

**Частина 2: Оновлення**
```bash
# Оновити кількість реплік
helm upgrade web bitnami/nginx --reuse-values --set replicaCount=3

# Перевірити історію
helm history web

# Перевірити поди
k get pods -l app.kubernetes.io/instance=web
```

**Частина 3: Відкат**
```bash
# Відкат до ревізії 1
helm rollback web 1

# Перевірити повернення
helm get values web
k get pods -l app.kubernetes.io/instance=web
```

**Частина 4: Очищення**
```bash
helm uninstall web
```

---

## Практичні вправи

### Вправа 1: Керування репозиторіями (Ціль: 2 хвилини)

```bash
# Додати bitnami-репозиторій
helm repo add bitnami https://charts.bitnami.com/bitnami

# Оновити
helm repo update

# Шукати mysql
helm search repo mysql

# Переглянути репозиторії
helm repo list
```

### Вправа 2: Базове встановлення (Ціль: 2 хвилини)

```bash
# Встановити nginx
helm install drill2 bitnami/nginx

# Переглянути релізи
helm list

# Перевірити статус
helm status drill2

# Очищення
helm uninstall drill2
```

### Вправа 3: Встановлення зі значеннями (Ціль: 3 хвилини)

```bash
# Створити файл значень
cat << 'EOF' > /tmp/values.yaml
replicaCount: 2
service:
  type: ClusterIP
EOF

# Встановити з файлом значень
helm install drill3 bitnami/nginx -f /tmp/values.yaml

# Перевірити, що значення застосовано
helm get values drill3

# Очищення
helm uninstall drill3
```

### Вправа 4: Оновлення та відкат (Ціль: 4 хвилини)

```bash
# Встановити
helm install drill4 bitnami/nginx --set replicaCount=1

# Оновити
helm upgrade drill4 bitnami/nginx --set replicaCount=3

# Перевірити історію
helm history drill4

# Відкат
helm rollback drill4 1

# Перевірити
helm get values drill4

# Очищення
helm uninstall drill4
```

### Вправа 5: Операції з просторами імен (Ціль: 3 хвилини)

```bash
# Встановити у новий простір імен
helm install drill5 bitnami/nginx -n helm-test --create-namespace

# Переглянути у просторі імен
helm list -n helm-test

# Отримати поди у просторі імен
k get pods -n helm-test

# Очищення
helm uninstall drill5 -n helm-test
k delete ns helm-test
```

### Вправа 6: Повний сценарій (Ціль: 6 хвилин)

**Сценарій**: Розгорнути production-ready nginx.

```bash
# 1. Створити файл значень
cat << 'EOF' > /tmp/prod-values.yaml
replicaCount: 3
service:
  type: NodePort
  nodePorts:
    http: 30080
resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 50m
    memory: 64Mi
EOF

# 2. Спочатку dry-run
helm install prod-web bitnami/nginx -f /tmp/prod-values.yaml --dry-run

# 3. Встановити
helm install prod-web bitnami/nginx -f /tmp/prod-values.yaml

# 4. Перевірити
helm list
helm get values prod-web
k get pods -l app.kubernetes.io/instance=prod-web

# 5. Оновити з більшою кількістю реплік
helm upgrade prod-web bitnami/nginx -f /tmp/prod-values.yaml --set replicaCount=5

# 6. Щось не так — відкат
helm rollback prod-web 1

# 7. Очищення
helm uninstall prod-web
```

---

## Наступний модуль

[Модуль 2.3: Kustomize](/uk/k8s/ckad/part2-deployment/module-2.3-kustomize/) — кастомізація ресурсів Kubernetes без шаблонів.
