---
title: "Модуль 1.2: Основи kubectl"
slug: uk/prerequisites/kubernetes-basics/module-1.2-kubectl-basics
sidebar:
  order: 3
lab:
  id: "prereq-k8s-1.2-kubectl"
  url: "https://killercoda.com/kubedojo/scenario/prereq-k8s-1.2-kubectl"
  duration: "30 min"
  difficulty: "beginner"
  environment: "kubernetes"
---
> **Складність**: `[MEDIUM]` — Основні команди, які потрібно опанувати
>
> **Час на виконання**: 40–45 хвилин
>
> **Передумови**: Модуль 1.1 (Запущений перший кластер)

## Що ви зможете робити після цього модуля

Після цього модуля ви зможете:
- **Навігувати** ресурсами Kubernetes за допомогою `kubectl get`, `kubectl describe` та `kubectl explain`
- **Створювати** ресурси як імперативно (швидкі команди), так і декларативно (YAML-файли)
- **Дебажити** проблеми з ресурсами за допомогою подій `kubectl describe` та `kubectl logs`
- **Використовувати** форматування виводу (`-o wide`, `-o yaml`, `-o json`) для отримання потрібної інформації

---

## Чому цей модуль важливий

`kubectl` — це ваш основний інтерфейс для роботи з Kubernetes. Будь-яка взаємодія — створення ресурсів, налагодження проблем, перевірка статусу — проходить через `kubectl`. Опанування цього інструменту є критично важливим як для щоденної роботи, так і для складання іспитів на сертифікацію.

---

## Структура команди kubectl

```
kubectl [команда] [ТИП] [НАЗВА] [прапорці]

Приклади:
kubectl get pods                    # Список усіх подів
kubectl get pod nginx              # Отримати конкретний под
kubectl get pods -o wide           # Більше колонок у виводі
kubectl describe pod nginx         # Детальна інформація
kubectl delete pod nginx           # Видалити ресурс
```

---

## Основні команди

### Отримання інформації

```bash
# Список ресурсів
kubectl get pods                   # Поди у поточному просторі імен
kubectl get pods -A                # Поди у всіх просторах імен
kubectl get pods -n kube-system    # Поди у конкретному просторі імен
kubectl get pods -o wide           # Більше колонок (вузол, IP)
kubectl get pods -o yaml           # Повний YAML вивід
kubectl get pods -o json           # Вивід у форматі JSON

# Популярні типи ресурсів
kubectl get nodes                  # Вузли кластера
kubectl get deployments           # Деплойменти
kubectl get services              # Сервіси
kubectl get all                   # Усі основні ресурси
kubectl get events                # Події кластера

# Describe (детальна інформація)
kubectl describe pod nginx
kubectl describe node kind-control-plane
kubectl describe deployment myapp
```

### Створення ресурсів

```bash
# З YAML-файлу
kubectl apply -f pod.yaml
kubectl apply -f .                  # Усі YAML-файли в директорії
kubectl apply -f https://example.com/resource.yaml  # За URL-адресою

# Імперативно (швидке створення)
kubectl run nginx --image=nginx
kubectl create deployment nginx --image=nginx
kubectl expose deployment nginx --port=80

# Генерація YAML без створення ресурсу
kubectl run nginx --image=nginx --dry-run=client -o yaml
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml
```

### Зміна ресурсів

```bash
# Застосувати зміни
kubectl apply -f updated-pod.yaml

# Редагувати "живий" ресурс
kubectl edit deployment nginx

# Патчинг (швидка зміна поля)
kubectl patch deployment nginx -p '{"spec":{"replicas":3}}'

# Масштабування
kubectl scale deployment nginx --replicas=5

# Оновлення образу
kubectl set image deployment/nginx nginx=nginx:1.25
```

### Видалення ресурсів

```bash
# Видалення за назвою
kubectl delete pod nginx
kubectl delete deployment nginx

# Видалення за файлом
kubectl delete -f pod.yaml

# Видалення всіх ресурсів певного типу
kubectl delete pods --all
kubectl delete pods --all -n my-namespace

# Примусове видалення (якщо под "застряг")
kubectl delete pod nginx --force --grace-period=0
```

---

## Формати виводу

```bash
# За замовчуванням (таблиця)
kubectl get pods
# NAME    READY   STATUS    RESTARTS   AGE
# nginx   1/1     Running   0          5m

# Wide (додаткові колонки)
kubectl get pods -o wide
# NAME    READY   STATUS    RESTARTS   AGE   IP           NODE
# nginx   1/1     Running   0          5m    10.244.0.5   kind-control-plane

# YAML
kubectl get pod nginx -o yaml

# JSON
kubectl get pod nginx -o json
```

> **Бонус: Синтаксис для просунутих** (поверніться до цього, коли освоїте базу)
>
> ```bash
> # Кастомні колонки (чудово для дашбордів)
> kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase
>
> # JSONPath (вилучення конкретних полів — "золото" для іспитів!)
> kubectl get pod nginx -o jsonpath='{.status.podIP}'
> kubectl get pods -o jsonpath='{.items[*].metadata.name}'
> ```

---

## Робота з просторами імен (Namespaces)

```bash
# Список просторів імен
kubectl get namespaces
kubectl get ns

# Встановити простір імен за замовчуванням
kubectl config set-context --current --namespace=my-namespace

# Створити простір імен
kubectl create namespace my-namespace

# Виконати команду в конкретному просторі імен
kubectl get pods -n kube-system
kubectl get pods --namespace=my-namespace

# У всіх просторах імен одночасно
kubectl get pods -A
kubectl get pods --all-namespaces
```

---

## Команди для налагодження (Debugging)

```bash
# Перегляд логів
kubectl logs nginx                  # Поточні логи
kubectl logs nginx -f               # Стрімінг логів (follow)
kubectl logs nginx --tail=100       # Останні 100 рядків
kubectl logs nginx -c container1    # Логи конкретного контейнера
kubectl logs nginx --previous       # Логи попереднього екземпляра

# Виконання команди всередині контейнера
kubectl exec nginx -- ls /          # Просто виконати команду
kubectl exec -it nginx -- bash      # Інтерактивна оболонка
kubectl exec -it nginx -- sh        # Якщо bash недоступний

# Прокидання портів (Port forwarding)
kubectl port-forward pod/nginx 8080:80
kubectl port-forward svc/nginx 8080:80
# Доступ за адресою localhost:8080

# Копіювання файлів
kubectl cp nginx:/etc/nginx/nginx.conf ./nginx.conf
kubectl cp ./local-file.txt nginx:/tmp/
```

---

## Корисні прапорці

```bash
# Watch (автоматичне оновлення)
kubectl get pods -w
kubectl get pods --watch

# Мітки та селектори (Labels and selectors)
kubectl get pods -l app=nginx
kubectl get pods --selector=app=nginx,tier=frontend

# Сортування виводу
kubectl get pods --sort-by=.metadata.creationTimestamp
kubectl get pods --sort-by=.status.startTime

# Фільтрація полях
kubectl get pods --field-selector=status.phase=Running
kubectl get pods --field-selector=spec.nodeName=kind-control-plane

# Показати мітки
kubectl get pods --show-labels

# Вивід у файл
kubectl get pod nginx -o yaml > pod.yaml
```

---

## Конфігурація та контекст

```bash
# Перегляд поточної конфігурації
kubectl config view
kubectl config current-context

# Список контекстів
kubectl config get-contexts

# Перемикання контексту
kubectl config use-context kind-kind
kubectl config use-context my-cluster

# Встановити простір імен за замовчуванням для контексту
kubectl config set-context --current --namespace=default
```

---

## Візуалізація: Як працює kubectl

```
┌─────────────────────────────────────────────────────────────┐
│              ЯК ПРАЦЮЄ kubectl                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐                                       │
│  │  Ваш термінал   │                                       │
│  │  $ kubectl ...  │                                       │
│  └────────┬────────┘                                       │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │  ~/.kube/config │  ← Креденшали, інфо про кластери     │
│  │  (kubeconfig)   │                                       │
│  └────────┬────────┘                                       │
│           │                                                 │
│           ▼  HTTPS                                         │
│  ┌─────────────────┐                                       │
│  │   API Server    │  ← Перевіряє, обробляє запит         │
│  │ (K8s кластер)   │                                       │
│  └────────┬────────┘                                       │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │    Відповідь    │  ← YAML / JSON / Таблиця             │
│  │                 │                                       │
│  └─────────────────┘                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Корисні скорочення

### Аліаси (Додайте в ~/.bashrc або ~/.zshrc)

```bash
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get services'
alias kgd='kubectl get deployments'
alias kaf='kubectl apply -f'
alias kdel='kubectl delete'
alias klog='kubectl logs'
alias kexec='kubectl exec -it'
```

### Автодоповнення kubectl (Autocomplete)

```bash
# Для Bash
source <(kubectl completion bash)
echo 'source <(kubectl completion bash)' >> ~/.bashrc

# Для Zsh
source <(kubectl completion zsh)
echo 'source <(kubectl completion zsh)' >> ~/.zshrc

# Разом з аліасом
complete -F __start_kubectl k  # Bash
compdef k=kubectl              # Zsh
```

---

## Швидкий довідник

| Дія | Команда |
|-----|---------|
| Список подів | `kubectl get pods` |
| Усі простори імен | `kubectl get pods -A` |
| Детальна інформація | `kubectl describe pod НАЗВА` |
| Перегляд логів | `kubectl logs НАЗВА` |
| Доступ до оболонки | `kubectl exec -it НАЗВА -- bash` |
| Прокидання порту | `kubectl port-forward pod/НАЗВА 8080:80` |
| Створити з файлу | `kubectl apply -f файл.yaml` |
| Видалити | `kubectl delete pod НАЗВА` |
| Згенерувати YAML | `kubectl run НАЗВА --image=ОБРАЗ --dry-run=client -o yaml` |

---

## Чи знали ви?

- **kubectl спілкується з API-сервером через HTTPS.** Усі команди — це виклики API. Ви могли б використовувати `curl`, але це набагато складніше.

- **`-o yaml` — це порятунок на іспиті.** Отримайте будь-який ресурс як YAML, змініть його та застосуйте назад. Це швидше, ніж писати з нуля.

- **`--dry-run=client -o yaml` створює шаблони.** Ніколи не запам'ятовуйте структуру YAML — генеруйте її.

- **В kubectl вбудована довідка.** `kubectl explain pod.spec.containers` покаже документацію до конкретного поля.

---

## Типові помилки

| Помилка | Вирішення |
|---------|-----------|
| Забули простір імен | Використовуйте `-n простір-імен` або встановіть його за замовчуванням |
| Не той контекст | `kubectl config use-context` |
| Друкарські помилки | Використовуйте Tab для автодоповнення |
| Не використовуєте `-o yaml` | Завжди генеруйте шаблони, не пишіть по пам'яті |
| Використання `create` замість `apply` | `apply` є ідемпотентним (безпечним), надавайте йому перевагу |

---

## Тест

1. **Як побачити всі поди у всіх просторах імен кластера?**
   <details>
   <summary>Відповідь</summary>
   `kubectl get pods -A` або `kubectl get pods --all-namespaces`
   </details>

2. **Як згенерувати YAML-маніфест для пода без його створення в кластері?**
   <details>
   <summary>Відповідь</summary>
   `kubectl run nginx --image=nginx --dry-run=client -o yaml`
   </details>

3. **Як отримати інтерактивну оболонку всередині запущеного контейнера?**
   <details>
   <summary>Відповідь</summary>
   `kubectl exec -it НАЗВА_ПОДА -- bash` (або `-- sh`, якщо bash недоступний)
   </details>

4. **Як стежити за логами пода в режимі реального часу?**
   <details>
   <summary>Відповідь</summary>
   `kubectl logs НАЗВА_ПОДА -f` або `kubectl logs НАЗВА_ПОДА --follow`
   </details>

---

## Практична вправа

**Завдання**: Попрактикуйтеся з основними командами kubectl.

```bash
# 1. Створіть простір імен
kubectl create namespace practice

# 2. Запустіть под у цьому просторі імен
kubectl run nginx --image=nginx -n practice

# 3. Список подів у просторі імен
kubectl get pods -n practice

# 4. Отримайте детальну інформацію
kubectl describe pod nginx -n practice

# 5. Перегляньте логи
kubectl logs nginx -n practice

# 6. Виконайте команду всередині контейнера
kubectl exec nginx -n practice -- nginx -v

# 7. Отримайте вивід у форматі YAML
kubectl get pod nginx -n practice -o yaml

# 8. Видаліть усе створене
kubectl delete namespace practice
```

**Критерії успіху**: Усі команди виконуються без помилок.

---

## Підсумок

Основні команди kubectl:

**Інформація**:
- `kubectl get` — список ресурсів.
- `kubectl describe` — детальна інформація.
- `kubectl logs` — вивід контейнера.

**Створення**:
- `kubectl apply -f` — створення/оновлення з файлу.
- `kubectl run` — швидке створення пода.
- `kubectl create` — створення ресурсів певних типів.

**Зміна**:
- `kubectl edit` — редагування "живого" ресурсу.
- `kubectl scale` — зміна кількості реплік.
- `kubectl delete` — видалення ресурсів.

**Налагодження**:
- `kubectl exec` — команди всередині контейнера.
- `kubectl port-forward` — локальний доступ до подів.

---

## Наступний модуль

[Модуль 1.3: Поди](../module-1.3-pods/) — Атомарна одиниця Kubernetes.
