---
title: "Модуль 1.1: Ваш перший кластер"
slug: uk/prerequisites/kubernetes-basics/module-1.1-first-cluster
sidebar:
  order: 2
lab:
  id: "prereq-k8s-1.1-first-cluster"
  url: "https://killercoda.com/kubedojo/scenario/prereq-k8s-1.1-first-cluster"
  duration: "25 min"
  difficulty: "beginner"
  environment: "kubernetes"
---
> **Складність**: `[MEDIUM]` — Потрібне практичне налаштування
>
> **Час на виконання**: 30–40 хвилин
>
> **Передумови**: Встановлений Docker, завершений курс «Cloud Native 101»

---

## Чому цей модуль важливий

Перш ніж ви зможете вивчати Kubernetes, вам потрібен кластер Kubernetes. Цей модуль дозволить вам отримати працюючий локальний кластер за лічені хвилини, щоб ви могли негайно розпочати практику.

Ми будемо використовувати **kind** (Kubernetes in Docker) — це швидкий, легкий інструмент, що ідеально підходить для навчання.

---

## Варіанти кластерів

### Для навчання (локальні)

| Інструмент | Плюси | Мінуси |
|------------|-------|--------|
| **kind** | Швидкий, легкий, підтримує багато вузлів | Потребує Docker |
| **minikube** | Багато функцій, різні драйвери | Важчий, довше налаштування |
| **k3d** | k3s у Docker, дуже швидкий | Дещо відрізняється від стандартного K8s |
| **Docker Desktop** | Дуже просто, якщо він уже є | Обмежені можливості конфігурації |

### Для продакшну (керовані)

| Сервіс | Провайдер |
|--------|-----------|
| EKS | AWS |
| GKE | Google Cloud |
| AKS | Azure |

**Рекомендація**: Для цього курсу використовуйте **kind**. Він найкраще відповідає середовищам, які використовуються на іспитах.

---

## Встановлення kind

### macOS

```bash
# Через Homebrew
brew install kind

# Або завантажте бінарний файл
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-darwin-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

### Linux

```bash
# Завантажте бінарний файл
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

### Windows

```powershell
# Через Chocolatey
choco install kind

# Або завантажте з:
# https://kind.sigs.k8s.io/dl/latest/kind-windows-amd64
```

### Перевірка встановлення

```bash
kind version
# kind v0.20.0 go1.20.4 darwin/amd64
```

---

## Встановлення kubectl

`kubectl` — це інструмент командного рядка для взаємодії з Kubernetes.

### macOS

```bash
# Через Homebrew
brew install kubectl

# Або завантажте бінарний файл
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
```

### Linux

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
```

### Перевірка встановлення

```bash
kubectl version --client
# Client Version: v1.28.0
```

---

## Створення вашого першого кластера

### Простий однонодовий кластер

```bash
# Створення кластера
kind create cluster

# Вивід:
# Creating cluster "kind" ...
#  ✓ Ensuring node image (kindest/node:v1.27.3) 🖼
#  ✓ Preparing nodes 📦
#  ✓ Writing configuration 📜
#  ✓ Starting control-plane 🕹️
#  ✓ Installing CNI 🔌
#  ✓ Installing StorageClass 💾
# Set kubectl context to "kind-kind"
```

### Перевірка роботи

```bash
# Перевірка інформації про кластер
kubectl cluster-info
# Kubernetes control plane is running at https://127.0.0.1:xxxxx

# Список вузлів (nodes)
kubectl get nodes
# NAME                 STATUS   ROLES           AGE   VERSION
# kind-control-plane   Ready    control-plane   60s   v1.27.3

# Перевірка всіх подів (системних)
kubectl get pods -A
# Покаже працюючі поди в просторі імен kube-system
```

---

## Багатонодовий кластер (опційно)

Для більш реалістичного тестування створіть кластер із декількома вузлами:

```yaml
# kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
```

```bash
# Створення багатонодового кластера
kind create cluster --config kind-config.yaml --name multi-node

# Перевірка
kubectl get nodes
# NAME                       STATUS   ROLES           AGE   VERSION
# multi-node-control-plane   Ready    control-plane   60s   v1.27.3
# multi-node-worker          Ready    <none>          30s   v1.27.3
# multi-node-worker2         Ready    <none>          30s   v1.27.3
```

---

## Керування кластерами

```bash
# Список кластерів
kind get clusters

# Видалення кластера
kind delete cluster                    # Видалити кластер за замовчуванням "kind"
kind delete cluster --name multi-node  # Видалити іменований кластер

# Отримати kubeconfig кластера
kind get kubeconfig --name kind

# Експортувати kubeconfig (якщо потрібно)
kind export kubeconfig --name kind
```

---

## Розуміння того, що ви отримали

```
┌─────────────────────────────────────────────────────────────┐
│              ВАШ КЛАСТЕР KIND                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Docker-контейнер                        │   │
│  │              "kind-control-plane"                    │   │
│  │                                                     │   │
│  │    ┌───────────────────────────────────────────┐   │   │
│  │    │         Control Plane                     │   │   │
│  │    │  ┌─────────┐ ┌──────────┐ ┌───────────┐  │   │   │
│  │    │  │   API   │ │Scheduler │ │Controller │  │   │   │
│  │    │  │ Server  │ │          │ │  Manager  │  │   │   │
│  │    │  └─────────┘ └──────────┘ └───────────┘  │   │   │
│  │    │           ┌──────────┐                    │   │   │
│  │    │           │   etcd   │                    │   │   │
│  │    │           └──────────┘                    │   │   │
│  │    └───────────────────────────────────────────┘   │   │
│  │                                                     │   │
│  │    ┌───────────────────────────────────────────┐   │   │
│  │    │         Worker (у тому ж контейнері)      │   │   │
│  │    │  ┌─────────┐ ┌──────────┐                │   │   │
│  │    │  │ kubelet │ │Container │                │   │   │
│  │    │  │         │ │ Runtime  │                │   │   │
│  │    │  └─────────┘ └──────────┘                │   │   │
│  │    │                                           │   │   │
│  │    │  Ваші поди працюватимуть тут              │   │   │
│  │    └───────────────────────────────────────────┘   │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Весь кластер K8s працює всередині одного Docker-контейнера │
│  (або декількох для багатонодових кластерів)               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Перші команди

Тепер, коли у вас є кластер, спробуйте ці команди:

```bash
# Подивитися, що запущено в кластері
kubectl get pods -A

# Отримати деталі про вузли
kubectl describe node kind-control-plane

# Перевірити стан компонентів
kubectl get --raw='/readyz?verbose'

# Переглянути події кластера
kubectl get events -A
```

---

## Усунення несправностей

### "Cannot connect to the Docker daemon"

```bash
# Переконайтеся, що Docker запущено
docker info

# Якщо використовуєте Docker Desktop, перевірте, чи він увімкнений
```

### "kind: command not found"

```bash
# Перевірте, чи є kind у вашому PATH
which kind

# Якщо ні, додайте його до PATH або перевстановіть
```

### "kubectl: connection refused"

```bash
# Переконайтеся, що кластер запущено
kind get clusters
docker ps  # Має показувати контейнер kind

# Перевірте контекст kubeconfig
kubectl config current-context
# Має показувати "kind-kind" або назву вашого кластера
```

---

## Чи знали ви?

- **kind розшифровується як «Kubernetes in Docker».** Він запускає вузли K8s як Docker-контейнери замість віртуальних машин.

- **kind був створений для тестування самого Kubernetes.** Проєкт K8s використовує його для власних тестів. Він достатньо надійний для цього.

- **Кожен вузол kind — це Docker-контейнер**, всередині якого працюють systemd, kubelet та containerd.

- **Кластери kind зберігаються після перезапуску Docker.** Ваш кластер виживе після перезавантаження комп'ютера (якщо ви його не видалите).

---

## Тест

1. **Що таке kind?**
   <details>
   <summary>Відповідь</summary>
   Kind (Kubernetes in Docker) — це інструмент для запуску локальних кластерів Kubernetes, де вузли кластера є Docker-контейнерами. Він легкий, швидкий та ідеальний для розробки та навчання.
   </details>

2. **Яка команда створює кластер kind?**
   <details>
   <summary>Відповідь</summary>
   `kind create cluster` створює кластер з одним вузлом. Використовуйте прапорець `--config` із YAML-файлом для багатонодових кластерів або `--name` для власної назви кластера.
   </details>

3. **Як перевірити, чи працює ваш кластер?**
   <details>
   <summary>Відповідь</summary>
   Запустіть `kubectl get nodes` для перегляду вузлів, `kubectl cluster-info` для перевірки адрес API або `kubectl get pods -A` для перегляду всіх системних подів.
   </details>

4. **Як видалити кластер kind?**
   <details>
   <summary>Відповідь</summary>
   `kind delete cluster` видаляє кластер за замовчуванням. Використовуйте `--name назва-кластера` для видалення конкретного кластера.
   </details>

---

## Практична вправа

**Завдання**: Створіть, перевірте та видаліть кластер.

```bash
# 1. Створіть кластер
kind create cluster --name practice

# 2. Переконайтеся, що вузли готові
kubectl get nodes

# 3. Список усіх подів у кластері
kubectl get pods -A

# 4. Перегляньте інформацію про кластер
kubectl cluster-info

# 5. Видаліть кластер
kind delete cluster --name practice

# 6. Переконайтеся, що його видалено
kind get clusters
```

**Критерії успіху**: Усі команди виконуються без помилок.

---

## Підсумок

Тепер у вас є працюючий кластер Kubernetes:

**Встановлені інструменти**:
- kind — створює локальні кластери K8s.
- kubectl — CLI для взаємодії з K8s.

**Основні команди**:
- `kind create cluster` — створити кластер.
- `kind delete cluster` — видалити кластер.
- `kubectl get nodes` — перевірити вузли.

Ви готові почати роботу з Kubernetes!

---

## Наступний модуль

[Модуль 1.2: Основи kubectl](../module-1.2-kubectl-basics/) — Ваш інтерфейс командного рядка для Kubernetes.
