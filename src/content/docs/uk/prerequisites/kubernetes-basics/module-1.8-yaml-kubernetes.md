---
title: "Модуль 1.8: YAML для Kubernetes"
slug: uk/prerequisites/kubernetes-basics/module-1.8-yaml-kubernetes
sidebar:
  order: 9
---
> **Складність**: `[MEDIUM]` — Необхідна навичка
>
> **Час на виконання**: 35–40 хвилин
>
> **Передумови**: Попередні модулі (знайомство з ресурсами K8s)

## Що ви зможете робити після цього модуля

Після цього модуля ви зможете:
- **Писати** валідний YAML для ресурсів Kubernetes без синтаксичних помилок
- **Дебажити** типові помилки YAML (відступи, неправильні типи, пропущені поля) читаючи повідомлення про помилки
- **Пояснити** чотири обов'язкові поля в кожному маніфесті K8s (apiVersion, kind, metadata, spec)
- **Використовувати** `kubectl explain` для пошуку правильних полів будь-якого ресурсу без гуглення

---

## Чому цей модуль важливий

Будь-який ресурс у Kubernetes визначається за допомогою мови YAML. Розуміння синтаксису YAML та структури ресурсів K8s є критичним для:
- Написання маніфестів (файлів конфігурації)
- Розуміння прикладів та документації
- Налагодження помилок конфігурації
- Складання іспитів на сертифікацію

---

## Основи YAML

### Структура

```yaml
# Це коментар

# Скаляри (прості значення)
string: "привіт"
number: 42
float: 3.14
boolean: true
null_value: null

# Списки (масиви)
items:
- item1
- item2
- item3

# Або в один рядок (інлайн)
items: [item1, item2, item3]

# Карти / Словники (об'єкти)
person:
  name: "Іван"
  age: 30

# Або інлайн
person: {name: "Іван", age: 30}
```

### Правила відступів (Indentation)

```yaml
# YAML використовує ПРОБІЛИ, а НЕ таби
# Зазвичай це 2 пробіли на рівень

parent:
  child:
    grandchild: value

# НЕПРАВИЛЬНО (таби призведуть до помилки):
parent:
	child:      # Тут використано TAB — ПОМИЛКА!
```

### Багаторядкові рядки

```yaml
# Блок Literal (зберігає переноси рядків)
literal: |
  Рядок 1
  Рядок 2
  Рядок 3

# Блок Folded (замінює переноси рядків пробілами)
folded: >
  Це дуже
  довге
  речення.
# Результат: "Це дуже довге речення."
```

---

## Структура ресурсу Kubernetes

Кожен ресурс K8s має таку структуру:

```yaml
apiVersion: v1              # Версія API
kind: Pod                   # Тип ресурсу
metadata:                   # Метадані ресурсу
  name: my-pod
  namespace: default
  labels:
    app: myapp
  annotations:
    description: "Мій под"
spec:                       # Бажаний стан (різний для кожного типу)
  containers:
  - name: main
    image: nginx
status:                     # Поточний стан (керується K8s, тільки для читання)
  phase: Running
```

### Обов'язкові поля

| Поле | Опис |
|------|------|
| `apiVersion` | Версія API для цього типу ресурсу |
| `kind` | Тип ресурсу (Pod, Service, Deployment тощо) |
| `metadata.name` | Унікальне ім'я в межах простору імен |
| `spec` | Специфікація бажаного стану |

---

## Поширені версії API

| Ресурс | apiVersion |
|--------|------------|
| Pod, Service, ConfigMap, Secret | `v1` |
| Deployment, ReplicaSet | `apps/v1` |
| Ingress | `networking.k8s.io/v1` |
| NetworkPolicy | `networking.k8s.io/v1` |
| PersistentVolume, PVC | `v1` |
| StorageClass | `storage.k8s.io/v1` |
| Role, ClusterRole | `rbac.authorization.k8s.io/v1` |

```bash
# Знайти версію API для будь-якого ресурсу
kubectl api-resources | grep -i deployment
# deployments    deploy    apps/v1    true    Deployment
```

---

## Генерація YAML (Не зазубрюйте!)

Ніколи не пишіть YAML з нуля — генеруйте його:

```bash
# Згенерувати YAML для Пода
kubectl run nginx --image=nginx --dry-run=client -o yaml

# Згенерувати YAML для Деплойменту
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml

# Згенерувати YAML для Сервісу
kubectl expose deployment nginx --port=80 --dry-run=client -o yaml

# Зберегти у файл
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml > deployment.yaml
```

### Команда explain (Документація)

```bash
# Отримати документацію по полях
kubectl explain pod
kubectl explain pod.spec
kubectl explain pod.spec.containers
kubectl explain pod.spec.containers.resources

# Рекурсивно (всі поля)
kubectl explain pod.spec --recursive | less
```

---

## Типові патерни

### Шаблон пода (у Деплойментах)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:                    # Тут починається шаблон пода
    metadata:
      labels:
        app: myapp             # Має збігатися з selector вище
    spec:
      containers:
      - name: main
        image: nginx:1.25
        ports:
        - containerPort: 80
```

### Змінні середовища (env)

```yaml
containers:
- name: app
  image: myapp
  env:
  # Пряме значення
  - name: LOG_LEVEL
    value: "debug"
  # З ConfigMap
  - name: DB_HOST
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: database_host
  # З Secret
  - name: DB_PASS
    valueFrom:
      secretKeyRef:
        name: app-secrets
        key: password
```

### Монтування томів (Volumes)

```yaml
spec:
  containers:
  - name: app
    image: myapp
    volumeMounts:
    - name: config
      mountPath: /etc/config
    - name: data
      mountPath: /data
  volumes:
  - name: config
    configMap:
      name: app-config
  - name: data
    persistentVolumeClaim:
      claimName: app-pvc
```

### Вимоги до ресурсів

```yaml
containers:
- name: app
  image: myapp
  resources:
    requests:
      memory: "64Mi"
      cpu: "250m"
    limits:
      memory: "128Mi"
      cpu: "500m"
```

---

## Декілька документів в одному файлі

```yaml
# Перший документ
apiVersion: v1
kind: ConfigMap
metadata:
  name: config
data:
  key: value
---                          # Розділювач документів
# Другий документ
apiVersion: v1
kind: Service
metadata:
  name: service
spec:
  # ...
---                          # Ще один документ
apiVersion: apps/v1
kind: Deployment
# ...
```

```bash
# Застосувати всі ресурси з файлу
kubectl apply -f multi-doc.yaml
```

---

## Валідація

```bash
# Валідація на стороні сервера (dry-run)
kubectl apply -f pod.yaml --dry-run=server

# Валідація на стороні клієнта
kubectl apply -f pod.yaml --dry-run=client

# Перевірка синтаксису без застосування
kubectl create -f pod.yaml --dry-run=client --validate=true

# Перевірка згенерованого YAML
kubectl apply -f pod.yaml --dry-run=client -o yaml
```

---

## Поширені помилки в YAML

### Відступи

```yaml
# НЕПРАВИЛЬНО — різні відступи
spec:
  containers:
   - name: app    # 3 пробіли
    image: nginx  # 4 пробіли — ПОМИЛКА!

# ПРАВИЛЬНО
spec:
  containers:
  - name: app
    image: nginx
```

### Лапки

```yaml
# Деякі значення потребують лапок

# НЕПРАВИЛЬНО — двокрапка викликає помилку парсингу
message: Error: something failed

# ПРАВИЛЬНО
message: "Error: something failed"

# Числа, які мають бути рядками
port: "8080"   # Якщо потрібен string, використовуйте лапки
```

### Логічні значення (Booleans)

```yaml
# Це все true:
enabled: true
enabled: True
enabled: yes
enabled: on

# Це все false:
enabled: false
enabled: False
enabled: no
enabled: off

# Будьте обережні з рядками, схожими на booleans
value: "yes"    # Це рядок "yes"
value: yes      # Це логічне true
```

---

## Чи знали ви?

- **JSON — це валідний YAML.** YAML є надмножиною JSON. Ви можете вставляти JSON прямо у YAML-файли.

- **K8s ігнорує невідомі поля** за замовчуванням. Друкарські помилки в назвах полів не викличуть помилки — вони будуть просто проігноровані.

- **`kubectl explain` — ваш найкращий друг.** Він показує документацію для будь-якого поля, отриману безпосередньо з API.

- **Server-side dry-run валідує проти кластера.** Він ловить більше помилок, ніж client-side (наприклад, перевіряє існування ConfigMap, на який ви посилаєтесь).

---

## Тест

1. **Яка різниця між `--dry-run=client` та `--dry-run=server`?**
   <details>
   <summary>Відповідь</summary>
   Client-side валідація перевіряє тільки синтаксис YAML. Server-side відправляється на API-сервер, який перевіряє маніфест за схемою та станом кластера (наприклад, чи існують згадані ConfigMaps).
   </details>

2. **Як знайти правильну версію `apiVersion` для ресурсу?**
   <details>
   <summary>Відповідь</summary>
   Команда `kubectl api-resources | grep НАЗВА` покаже групу та версію API. Також можна використати `kubectl explain НАЗВА`, версія буде вказана зверху.
   </details>

3. **Що означає `---` у YAML-файлі?**
   <details>
   <summary>Відповідь</summary>
   Це розділювач документів. Один YAML-файл може містити декілька ресурсів. `kubectl apply -f` обробить усі ресурси у файлі по черзі.
   </details>

4. **Як побачити документацію для конкретного поля?**
   <details>
   <summary>Відповідь</summary>
   За допомогою команди `kubectl explain РЕСУРС.ПОЛЕ.ШЛЯХ`, наприклад: `kubectl explain pod.spec.containers.resources`.
   </details>

---

## Практична вправа

**Завдання**: Потренуватися у генерації та валідації YAML.

```bash
# 1. Згенеруйте YAML для деплойменту
kubectl create deployment web --image=nginx --replicas=3 --dry-run=client -o yaml > web.yaml

# 2. Перегляньте вміст
cat web.yaml

# 3. Додайте ліміти ресурсів (відредагуйте файл)
# Додайте в секцію containers[0]:
#   resources:
#     requests:
#       memory: "64Mi"
#       cpu: "100m"
#     limits:
#       memory: "128Mi"
#       cpu: "200m"

# 4. Проведіть валідацію
kubectl apply -f web.yaml --dry-run=server

# 5. Застосуйте зміни
kubectl apply -f web.yaml

# 6. Перевірте результат
kubectl get deployment web

# 7. Згенеруйте YAML для сервісу
kubectl expose deployment web --port=80 --dry-run=client -o yaml > service.yaml

# 8. Застосуйте сервіс
kubectl apply -f service.yaml

# 9. Використайте explain для довідки
kubectl explain deployment.spec.strategy

# 10. Прибирання
kubectl delete -f web.yaml -f service.yaml
rm web.yaml service.yaml
```

**Критерії успіху**: Ресурси створені успішно на основі згенерованого YAML.

---

## Підсумок

**Основи YAML**:
- Пробіли для відступів (не таби).
- `-` для елементів списку.
- `:` для пар ключ-значення.
- `---` розділяє документи.

**Структура ресурсу K8s**:
- apiVersion, kind, metadata, spec.
- Використовуйте `kubectl explain` для довідки.
- Використовуйте `--dry-run=client -o yaml` для генерації.

**Валідація**:
- `--dry-run=client` для перевірки синтаксису.
- `--dry-run=server` для повної валідації API.

**Найкращі практики**:
- Ніколи не пишіть YAML з нуля.
- Генеруйте, змінюйте, застосовуйте.
- Активно користуйтеся `kubectl explain`.

---

## Трек завершено!

Вітаємо! Ви закінчили підготовчий трек **«Основи Kubernetes»**. Тепер ви розумієте:

1. Як налаштувати локальний кластер (kind).
2. Основні команди та патерни kubectl.
3. Поди — атомарна одиниця K8s.
4. Деплойменти — керування застосунками.
5. Сервіси — стабільна мережа.
6. ConfigMaps та Secrets — конфігурація.
7. Простори імен та Мітки — організація.
8. YAML для Kubernetes — написання маніфестів.

**Наступні кроки**:
- [Програма CKA](../../k8s/cka/part0-environment/module-0.1-cluster-setup/) — Сертифікація адміністратора.
- [Програма CKAD](../../k8s/ckad/part0-environment/module-0.1-ckad-overview/) — Шлях сертифікації для розробників.
- [Сучасні практики DevOps](../modern-devops/module-1.1-infrastructure-as-code/) — Супутні навички.
