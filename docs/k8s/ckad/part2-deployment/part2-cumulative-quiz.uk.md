# Кумулятивний тест Частини 2: Розгортання застосунків

> **Обмеження часу**: 25 хвилин (симуляція тиску іспиту)
>
> **Прохідний бал**: 80% (8/10 запитань)

Цей тест перевіряє ваше володіння:
- Деплойментами та ковзними оновленнями/відкатами
- Пакетним менеджером Helm
- Kustomize
- Стратегіями деплойменту (blue/green, canary)

---

## Інструкції

1. Спробуйте кожне запитання без підглядання у відповіді
2. Засікайте час — швидкість важлива для CKAD
3. Використовуйте лише `kubectl` та `kubernetes.io/docs`
4. Перевірте відповіді після завершення всіх запитань

---

## Запитання

### Запитання 1: Конфігурація Rolling Update
**[2 хвилини]**

Створіть Деплоймент з назвою `webapp` з 4 репліками, використовуючи `nginx:1.20`, який:
- Використовує стратегію `RollingUpdate`
- Має `maxSurge: 1`
- Має `maxUnavailable: 0`

<details>
<summary>Відповідь</summary>

```bash
cat << 'EOF' | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
EOF
```

</details>

---

### Запитання 2: Відкат
**[2 хвилини]**

Деплоймент з назвою `api` був оновлений, але зазнає збоїв. Відкотіть його до ревізії 2.

```bash
# Перевірити поточний стан
k rollout history deploy/api
```

<details>
<summary>Відповідь</summary>

```bash
# Перевірити історію
k rollout history deploy/api

# Відкат до ревізії 2
k rollout undo deploy/api --to-revision=2

# Перевірити
k rollout status deploy/api
```

</details>

---

### Запитання 3: Встановлення Helm зі значеннями
**[2 хвилини]**

Встановіть чарт із репозиторію `bitnami`:
- Назва релізу: `my-nginx`
- Чарт: `bitnami/nginx`
- Встановити `replicaCount=3`
- Простір імен: `web` (створити, якщо не існує)

<details>
<summary>Відповідь</summary>

```bash
# Додати репозиторій, якщо потрібно
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Встановити зі значеннями
helm install my-nginx bitnami/nginx \
  --set replicaCount=3 \
  -n web --create-namespace
```

</details>

---

### Запитання 4: Відкат Helm
**[1 хвилина]**

Helm-реліз `my-app` був оновлений і тепер зламаний. Відкотіть його до попередньої версії.

<details>
<summary>Відповідь</summary>

```bash
# Перевірити історію
helm history my-app

# Відкат до попередньої
helm rollback my-app

# Або до конкретної ревізії
helm rollback my-app 1
```

</details>

---

### Запитання 5: Основи Kustomize
**[3 хвилини]**

Створіть кастомізацію, яка:
- Включає `deployment.yaml`
- Встановлює простір імен `production`
- Додає префікс `prod-` до всіх імен

Потім застосуйте її.

<details>
<summary>Відповідь</summary>

```bash
# Створити kustomization.yaml
cat << 'EOF' > kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml

namespace: production
namePrefix: prod-
EOF

# Попередній перегляд
kubectl kustomize ./

# Застосувати
kubectl apply -k ./
```

</details>

---

### Запитання 6: Перевизначення образу Kustomize
**[2 хвилини]**

Створіть кастомізацію, яка перевизначає образ `nginx`, щоб використовувати тег `1.22` замість того, що вказано в базових маніфестах.

<details>
<summary>Відповідь</summary>

```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml

images:
- name: nginx
  newTag: "1.22"
```

```bash
kubectl kustomize ./
```

</details>

---

### Запитання 7: Перемикання Blue/Green
**[3 хвилини]**

У вас є два деплойменти:
- `app-blue` з міткою `version: blue`
- `app-green` з міткою `version: green`

Сервіс `app-svc` наразі вказує на blue. Перемикніть його на green.

<details>
<summary>Відповідь</summary>

```bash
# Перемикнути селектор сервісу на green
kubectl patch svc app-svc -p '{"spec":{"selector":{"version":"green"}}}'

# Перевірити
kubectl get ep app-svc
kubectl describe svc app-svc
```

</details>

---

### Запитання 8: Налаштування Canary
**[3 хвилини]**

Налаштуйте canary-деплоймент, де:
- Стабільний деплоймент `stable-app` має 9 реплік (90%)
- Canary-деплоймент `canary-app` має 1 репліку (10%)
- Єдиний Сервіс маршрутизує до обох

Обидва деплойменти вже існують з міткою `app: myapp`.

<details>
<summary>Відповідь</summary>

```bash
# Масштабувати деплойменти для 10% canary
kubectl scale deploy stable-app --replicas=9
kubectl scale deploy canary-app --replicas=1

# Створити сервіс, що збігається з обома (використовуючи спільну мітку)
kubectl expose deploy stable-app --name=myapp-svc --port=80 --selector=app=myapp

# Перевірити, що endpoints включають поди з обох деплойментів
kubectl get ep myapp-svc
```

</details>

---

### Запитання 9: Стратегія деплойменту
**[2 хвилини]**

Застосунок бази даних вимагає, щоб працювала лише одна версія одночасно (без паралельних версій). Яку стратегію Деплойменту слід використовувати і як її налаштувати?

<details>
<summary>Відповідь</summary>

Використовуйте стратегію `Recreate`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database
spec:
  strategy:
    type: Recreate
  # ... решта специфікації
```

Стратегія `Recreate` завершує всі наявні поди перед створенням нових, гарантуючи, що дві версії не працюватимуть одночасно.

</details>

---

### Запитання 10: Значення Helm
**[2 хвилини]**

Отримайте поточно застосовані значення для Helm-релізу з назвою `production-app`. Потім оновіть його, зберігаючи наявні значення, але додавши `service.type=LoadBalancer`.

<details>
<summary>Відповідь</summary>

```bash
# Отримати поточні значення
helm get values production-app

# Оновити, зберігаючи наявні значення, додавши нове
helm upgrade production-app CHART_NAME \
  --reuse-values \
  --set service.type=LoadBalancer
```

Ключове: `--reuse-values` зберігає всі наявні кастомні значення.

</details>

---

## Оцінювання

| Правильних відповідей | Бал | Статус |
|-----------------------|-----|--------|
| 10/10 | 100% | Чудово — готові до іспиту |
| 8–9/10 | 80–90% | Добре — потрібен невеликий перегляд |
| 6–7/10 | 60–70% | Перегляньте слабкі місця |
| <6/10 | <60% | Перегляньте модулі Частини 2 |

---

## Очищення

```bash
k delete deploy webapp api stable-app canary-app 2>/dev/null
k delete svc app-svc myapp-svc 2>/dev/null
helm uninstall my-nginx -n web 2>/dev/null
helm uninstall my-app 2>/dev/null
helm uninstall production-app 2>/dev/null
k delete ns web 2>/dev/null
```

---

## Ключові висновки

Якщо ви набрали менше 80%, перегляньте ці розділи:

- **Пропущено З1–2**: Перегляньте Модуль 2.1 (Деплойменти) — ковзні оновлення та відкати
- **Пропущено З3–4**: Перегляньте Модуль 2.2 (Helm) — команди встановлення, оновлення, відкату
- **Пропущено З5–6**: Перегляньте Модуль 2.3 (Kustomize) — базова структура та трансформації
- **Пропущено З7–8**: Перегляньте Модуль 2.4 (Стратегії) — патерни blue/green та canary
- **Пропущено З9–10**: Перегляньте типи стратегій та керування значеннями Helm

---

## Наступна частина

[Частина 3: Спостережуваність та обслуговування застосунків](../part3-observability/module-3.1-probes.md) — проби, логування, дебаг та застарівання API.
