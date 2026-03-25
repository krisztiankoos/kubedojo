---
title: "\u041c\u043e\u0434\u0443\u043b\u044c 2.1: \u0414\u0435\u043f\u043b\u043e\u0439\u043c\u0435\u043d\u0442\u0438 \u2014 \u0433\u043b\u0438\u0431\u043e\u043a\u0435 \u0437\u0430\u043d\u0443\u0440\u0435\u043d\u043d\u044f"
slug: uk/k8s/ckad/part2-deployment/module-2.1-deployments
sidebar:
  order: 1
  label: "Part 2: Deployment"
---
> **Складність**: `[MEDIUM]` — ключова навичка CKAD з кількома операціями
>
> **Час на виконання**: 45–55 хвилин
>
> **Передумови**: Частина 1 завершена, розуміння Подів та ReplicaSet

---

## Чому цей модуль важливий

Деплойменти — це спосіб запуску застосунків у продакшн Kubernetes. Вони керують ReplicaSet, які керують Подами. Розуміння Деплойментів означає розуміння ковзних оновлень, відкатів, масштабування та повного життєвого циклу вашого застосунку.

CKAD активно тестує операції з Деплойментами:
- Створення та масштабування Деплойментів
- Виконання ковзних оновлень
- Відкат до попередніх версій
- Призупинення та відновлення розгортань
- Перевірка статусу та історії розгортання

> **Аналогія з конвеєром випуску ПЗ**
>
> Деплоймент — це як реліз-менеджер. Коли ви хочете випустити нову версію, реліз-менеджер (Деплоймент) створює нову виробничу лінію (ReplicaSet) з новим кодом. Він поступово переводить трафік зі старої лінії на нову. Якщо щось піде не так, він може швидко повернутися до старої лінії. Робітники (Поди) просто виконують інструкції — Деплоймент оркеструє все.

---

## Основи Деплойментів

### Створення Деплойментів

```bash
# Імперативне створення
k create deploy nginx --image=nginx:1.21 --replicas=3

# З портом
k create deploy web --image=nginx --port=80

# Згенерувати YAML
k create deploy api --image=httpd --replicas=2 --dry-run=client -o yaml > deploy.yaml
```

### Структура YAML Деплойменту

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  labels:
    app: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
```

### Ключові компоненти

| Компонент | Призначення |
|-----------|-------------|
| `replicas` | Кількість копій Подів для запуску |
| `selector.matchLabels` | Як Деплоймент знаходить свої Поди |
| `template` | Специфікація Поду (мітки мають збігатися з selector) |
| `strategy` | Спосіб виконання оновлень |

---

## Масштабування Деплойментів

### Ручне масштабування

```bash
# Масштабувати до 5 реплік
k scale deploy web-app --replicas=5

# Масштабувати до нуля (зупинити всі поди)
k scale deploy web-app --replicas=0

# Масштабувати кілька деплойментів
k scale deploy web-app api-server --replicas=3
```

### Перевірка масштабування

```bash
# Спостерігати за масштабуванням подів
k get pods -l app=web -w

# Перевірити статус деплойменту
k get deploy web-app

# Детальний статус
k describe deploy web-app | grep -A5 Replicas
```

---

## Ковзні оновлення

Ковзні оновлення замінюють Поди поступово, забезпечуючи нульовий час простою.

### Оновлення образу

```bash
# Оновити образ контейнера
k set image deploy/web-app nginx=nginx:1.22

# Оновити з записом (застаріло, але працює)
k set image deploy/web-app nginx=nginx:1.22 --record

# Оновити через patch
k patch deploy web-app -p '{"spec":{"template":{"spec":{"containers":[{"name":"nginx","image":"nginx:1.22"}]}}}}'
```

### Конфігурація стратегії оновлення

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Макс. подів понад бажану кількість під час оновлення
      maxUnavailable: 0  # Макс. подів недоступних під час оновлення
```

| Параметр | Опис | Приклад |
|----------|------|---------|
| `maxSurge` | Додаткові поди, дозволені під час оновлення | `1` або `25%` |
| `maxUnavailable` | Поди, які можуть бути недоступні під час оновлення | `0` або `25%` |

> **MaxUnavailable у StatefulSet**
>
> StatefulSet підтримують `maxUnavailable` у своїй `updateStrategy` (GA з K8s 1.27), що дозволяє паралельне оновлення подів замість послідовного по одному. Це може зробити оновлення StatefulSet **до 60% швидшими** — критично для кластерів баз даних та stateful-навантажень:
> ```yaml
> updateStrategy:
>   type: RollingUpdate
>   rollingUpdate:
>     maxUnavailable: 2  # Оновлювати 2 поди одночасно замість 1
> ```

### Типи стратегій

```yaml
# RollingUpdate (за замовчуванням) — поступова заміна
strategy:
  type: RollingUpdate

# Recreate — знищити все, потім створити нове
strategy:
  type: Recreate
```

Використовуйте `Recreate`, коли:
- Застосунок не може працювати з кількома версіями одночасно
- Міграції бази даних вимагають єдиної версії
- Час простою є прийнятним

---

## Моніторинг розгортань

### Перевірка статусу розгортання

```bash
# Спостерігати за ходом розгортання
k rollout status deploy/web-app

# Перевірити, чи завершилося розгортання
k rollout status deploy/web-app --timeout=60s
```

### Перегляд історії розгортання

```bash
# Список історії ревізій
k rollout history deploy/web-app

# Деталі конкретної ревізії
k rollout history deploy/web-app --revision=2

# Поточна ревізія
k describe deploy web-app | grep -i revision
```

### Призупинення та відновлення

```bash
# Призупинити розгортання (для пакетних змін)
k rollout pause deploy/web-app

# Внести кілька змін поки призупинено
k set image deploy/web-app nginx=nginx:1.23
k set resources deploy/web-app -c nginx --limits=memory=256Mi

# Відновити розгортання
k rollout resume deploy/web-app
```

---

## Відкати

### Відкат до попередньої версії

```bash
# Відкат до попередньої ревізії
k rollout undo deploy/web-app

# Відкат до конкретної ревізії
k rollout undo deploy/web-app --to-revision=2

# Перевірити статус відкату
k rollout status deploy/web-app
```

### Розуміння ревізій

```bash
# Кожна зміна створює новий ReplicaSet
k get rs -l app=web

# Вивід:
# NAME                  DESIRED   CURRENT   READY   AGE
# web-app-6d8f9b6b4f   3         3         3       5m   (поточний)
# web-app-7b8c9d4e3a   0         0         0       10m  (попередній)
```

Старі ReplicaSet зберігаються (масштабовані до 0) для можливості відкату.

### Обмеження історії ревізій

```yaml
spec:
  revisionHistoryLimit: 5  # Зберігати лише 5 старих ReplicaSet
```

---

## Стани Деплойменту

### Перевірка стану Деплойменту

```bash
# Отримати стани
k get deploy web-app -o jsonpath='{.status.conditions[*].type}'

# Детальні стани
k describe deploy web-app | grep -A10 Conditions
```

### Типові стани

| Стан | Значення |
|------|----------|
| `Available` | Мінімальна кількість реплік доступна |
| `Progressing` | Деплоймент оновлюється |
| `ReplicaFailure` | Не вдалося створити поди |

### Дедлайн прогресу Деплойменту

```yaml
spec:
  progressDeadlineSeconds: 600  # Збій, якщо немає прогресу протягом 10 хв
```

Якщо розгортання застрягає (наприклад, помилка завантаження образу), воно позначається як невдале після цього дедлайну.

---

## Мітки та селектори

### Правила селекторів

`selector.matchLabels` МУСИТЬ збігатися з `template.metadata.labels`:

```yaml
spec:
  selector:
    matchLabels:
      app: web        # Має збігатися з нижче
      tier: frontend
  template:
    metadata:
      labels:
        app: web      # Має збігатися з вище
        tier: frontend
        version: v1   # Може мати додаткові мітки
```

### Оновлення міток

```bash
# Додати мітку до деплойменту (лише метадані)
k label deploy web-app environment=production

# Додати мітку до подів через шаблон (запускає розгортання)
k patch deploy web-app -p '{"spec":{"template":{"metadata":{"labels":{"version":"v2"}}}}}'
```

---

## Швидкий довідник типових операцій

```bash
# Створити
k create deploy NAME --image=IMAGE --replicas=N

# Масштабувати
k scale deploy NAME --replicas=N

# Оновити образ
k set image deploy/NAME CONTAINER=IMAGE

# Оновити ресурси
k set resources deploy NAME -c CONTAINER --limits=cpu=200m,memory=512Mi

# Статус розгортання
k rollout status deploy/NAME

# Історія розгортання
k rollout history deploy/NAME

# Відкат
k rollout undo deploy/NAME

# Призупинити/Відновити
k rollout pause deploy/NAME
k rollout resume deploy/NAME

# Перезапустити всі поди (ковзний)
k rollout restart deploy/NAME
```

---

## Чи знали ви?

- **`kubectl rollout restart`** запускає ковзний перезапуск без зміни образу. Він додає анотацію з поточною міткою часу, що викликає перестворення подів. Чудово підходить для підхоплення змін у ConfigMap.

- **Деплойменти не видаляють старі ReplicaSet одразу.** Вони зберігають їх (масштабованими до 0) для можливості відкату. Керуйте цим через `revisionHistoryLimit`.

- **Прапорець `--record` є застарілим**, але все ще працює. Kubernetes 1.22+ рекомендує використовувати анотації замість нього для відстеження причин змін.

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| Селектор не збігається з мітками шаблону | Деплоймент не може знайти свої поди | Переконайтесь, що мітки збігаються точно |
| Використання `Recreate` у продакшні | Спричиняє простій | Використовуйте `RollingUpdate` з правильними налаштуваннями |
| `maxUnavailable: 100%` | Усі поди знищуються одночасно | Встановіть розумні відсотки |
| Забули перевірити статус розгортання | Не знаєте, чи оновлення вдалося | Завжди виконуйте `rollout status` |
| Не встановлено ліміти ресурсів | Поди можуть спожити всі ресурси вузла | Завжди встановлюйте requests та limits |

---

## Тест

1. **Як виконати відкат Деплойменту до ревізії 3?**
   <details>
   <summary>Відповідь</summary>
   `kubectl rollout undo deploy/NAME --to-revision=3`
   </details>

2. **Яка різниця між стратегіями `RollingUpdate` та `Recreate`?**
   <details>
   <summary>Відповідь</summary>
   `RollingUpdate` поступово замінює поди (нульовий час простою), тоді як `Recreate` завершує всі наявні поди перед створенням нових (спричиняє простій, але гарантує роботу лише однієї версії).
   </details>

3. **Як запустити ковзний перезапуск без зміни образу?**
   <details>
   <summary>Відповідь</summary>
   `kubectl rollout restart deploy/NAME`. Це додає анотацію з міткою часу, що запускає перестворення подів.
   </details>

4. **Що станеться, якщо мітки селектора не збігаються з мітками шаблону?**
   <details>
   <summary>Відповідь</summary>
   Деплоймент не зможе знайти або керувати своїми подами. API-сервер відхилить Деплоймент з помилкою валідації.
   </details>

---

## Практична вправа

**Завдання**: Відпрактикуйте повний життєвий цикл Деплойменту.

**Частина 1: Створення та масштабування**
```bash
# Створити деплоймент
k create deploy webapp --image=nginx:1.20 --replicas=2

# Перевірити
k get deploy webapp
k get pods -l app=webapp

# Масштабувати вгору
k scale deploy webapp --replicas=5

# Перевірити масштабування
k get pods -l app=webapp -w
```

**Частина 2: Ковзне оновлення**
```bash
# Оновити образ
k set image deploy/webapp nginx=nginx:1.21

# Спостерігати за розгортанням
k rollout status deploy/webapp

# Перевірити історію
k rollout history deploy/webapp

# Оновити знову
k set image deploy/webapp nginx=nginx:1.22
```

**Частина 3: Відкат**
```bash
# Відкат до попередньої
k rollout undo deploy/webapp

# Перевірити, що образ повернувся
k describe deploy webapp | grep Image

# Відкат до конкретної ревізії
k rollout history deploy/webapp
k rollout undo deploy/webapp --to-revision=1
```

**Частина 4: Призупинення та пакетні зміни**
```bash
# Призупинити
k rollout pause deploy/webapp

# Внести кілька змін
k set image deploy/webapp nginx=nginx:1.23
k set resources deploy/webapp -c nginx --limits=memory=128Mi

# Відновити
k rollout resume deploy/webapp

# Перевірити єдине розгортання
k rollout status deploy/webapp
```

**Очищення:**
```bash
k delete deploy webapp
```

---

## Практичні вправи

### Вправа 1: Базовий Деплоймент (Ціль: 2 хвилини)

```bash
# Створити деплоймент з 3 репліками
k create deploy drill1 --image=nginx --replicas=3

# Перевірити, що всі поди працюють
k get pods -l app=drill1

# Масштабувати до 5
k scale deploy drill1 --replicas=5

# Перевірити
k get deploy drill1

# Очищення
k delete deploy drill1
```

### Вправа 2: Оновлення образу (Ціль: 3 хвилини)

```bash
# Створити деплоймент
k create deploy drill2 --image=nginx:1.20

# Оновити образ
k set image deploy/drill2 nginx=nginx:1.21

# Перевірити статус розгортання
k rollout status deploy/drill2

# Перевірити новий образ
k describe deploy drill2 | grep Image

# Очищення
k delete deploy drill2
```

### Вправа 3: Відкат (Ціль: 3 хвилини)

```bash
# Створити та оновити кілька разів
k create deploy drill3 --image=nginx:1.19
k set image deploy/drill3 nginx=nginx:1.20
k set image deploy/drill3 nginx=nginx:1.21

# Перевірити історію
k rollout history deploy/drill3

# Відкат до ревізії 1
k rollout undo deploy/drill3 --to-revision=1

# Перевірити, що образ — 1.19
k describe deploy drill3 | grep Image

# Очищення
k delete deploy drill3
```

### Вправа 4: Налаштування ковзного оновлення (Ціль: 4 хвилини)

```bash
# Створити деплоймент з кастомною стратегією
cat << 'EOF' | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: drill4
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: drill4
  template:
    metadata:
      labels:
        app: drill4
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
EOF

# Оновити та спостерігати (має бути макс. 5 подів, 4 завжди готові)
k set image deploy/drill4 nginx=nginx:1.21
k get pods -l app=drill4 -w

# Очищення
k delete deploy drill4
```

### Вправа 5: Призупинення та відновлення (Ціль: 3 хвилини)

```bash
# Створити деплоймент
k create deploy drill5 --image=nginx:1.20

# Призупинити
k rollout pause deploy/drill5

# Внести зміни (розгортання поки немає)
k set image deploy/drill5 nginx=nginx:1.21
k set resources deploy/drill5 -c nginx --requests=cpu=100m

# Перевірити, що призупинено
k rollout status deploy/drill5

# Відновити
k rollout resume deploy/drill5

# Перевірити, що єдине розгортання застосувало обидві зміни
k rollout status deploy/drill5

# Очищення
k delete deploy drill5
```

### Вправа 6: Повний сценарій Деплойменту (Ціль: 6 хвилин)

**Сценарій**: Розгорнути застосунок, оновити його, зіткнутися з проблемою та виконати відкат.

```bash
# 1. Створити початковий деплоймент
k create deploy production --image=nginx:1.20 --replicas=3

# 2. Створити сервіс
k expose deploy production --port=80

# 3. Перевірити працездатність
k rollout status deploy/production
k get pods -l app=production

# 4. Оновити до "зламаного" образу (симуляція поганого релізу)
k set image deploy/production nginx=nginx:broken-tag

# 5. Перевірити, що розгортання застрягло
k rollout status deploy/production --timeout=30s

# 6. Побачити проблемні поди
k get pods -l app=production

# 7. Швидкий відкат
k rollout undo deploy/production

# 8. Перевірити відновлення
k rollout status deploy/production
k get pods -l app=production

# 9. Очищення
k delete deploy production
k delete svc production
```

---

## Наступний модуль

[Модуль 2.2: Пакетний менеджер Helm](module-2.2-helm/) — розгортання та керування застосунками за допомогою Helm-чартів.
