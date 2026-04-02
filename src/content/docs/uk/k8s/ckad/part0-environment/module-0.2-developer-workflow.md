---
title: "\u041c\u043e\u0434\u0443\u043b\u044c 0.2: \u0420\u043e\u0431\u043e\u0447\u0438\u0439 \u043f\u0440\u043e\u0446\u0435\u0441 \u0440\u043e\u0437\u0440\u043e\u0431\u043d\u0438\u043a\u0430"
slug: uk/k8s/ckad/part0-environment/module-0.2-developer-workflow
sidebar: 
  order: 2
lab: 
  id: ckad-0.2-developer-workflow
  url: https://killercoda.com/kubedojo/scenario/ckad-0.2-developer-workflow
  duration: "30 min"
  difficulty: intermediate
  environment: kubernetes
---
> **Складність**: `[QUICK]` - Основні шаблони kubectl
>
> **Час на проходження**: 25-30 хвилин
>
> **Передумови**: Модуль 0.1 (Огляд CKAD), Модуль 0.2 CKA (Володіння оболонкою)

---

## Чому цей модуль важливий

CKAD — це про швидкість ТА правильність. У вас є 2 години на ~15-20 завдань. Кожна секунда має значення. Різниця між успішним і провальним результатом часто полягає не в знаннях, а у швидкості виконання.

Цей модуль зосереджений на специфічних для розробника шаблонах kubectl, які ви будете використовувати постійно. Якщо ви пройшли програму CKA, у вас вже налаштовані псевдоніми (aliases) та автодоповнення. Тут ми додаємо оптимізації спеціально для CKAD.

> **Аналогія: Пояс з інструментами теслі**
>
> Майстер-тесля не порпається в ящику для інструментів заради кожного цвяха. Найчастіше використовувані інструменти висять у нього на поясі, розміщені для миттєвого доступу. Аналогічно, ваші найбільш вживані шаблони kubectl повинні бути під рукою — створені як псевдоніми, запам'ятовані та відпрацьовані до рівня м'язової пам'яті.

---

## Важливі псевдоніми (Aliases) для CKAD

Якщо ви пройшли програму CKA, вони у вас уже є. Якщо ні, додайте їх зараз:

```bash
# Add to ~/.bashrc or ~/.zshrc

# Basic alias (MUST have)
alias k='kubectl'

# Common actions
alias kaf='kubectl apply -f'
alias kdel='kubectl delete'
alias kd='kubectl describe'
alias kg='kubectl get'
alias kl='kubectl logs'
alias kx='kubectl exec -it'

# Output formats
alias kgy='kubectl get -o yaml'
alias kgw='kubectl get -o wide'

# Dry-run pattern (CKAD essential)
alias kdr='kubectl --dry-run=client -o yaml'

# Quick run
alias kr='kubectl run'

# Watch
alias kgpw='kubectl get pods -w'
```

### Доповнення спеціально для CKAD

```bash
# Jobs and CronJobs (CKAD heavy)
alias kcj='kubectl create job'
alias kccj='kubectl create cronjob'

# Quick debug pod
alias kdebug='kubectl run debug --image=busybox --rm -it --restart=Never --'

# Logs with container selection
alias klc='kubectl logs -c'

# Fast context switch
alias kctx='kubectl config use-context'
alias kns='kubectl config set-context --current --namespace'
```

---

## Шаблон Dry-Run: Ваш найкращий друг

Шаблон `--dry-run=client -o yaml` генерує YAML без створення ресурсів. Це необхідно для CKAD:

```bash
# Generate pod YAML
k run nginx --image=nginx $kdr > pod.yaml

# Generate deployment YAML
k create deploy web --image=nginx --replicas=3 $kdr > deploy.yaml

# Generate job YAML
k create job backup --image=busybox -- echo done $kdr > job.yaml

# Generate service YAML
k expose deploy web --port=80 $kdr > svc.yaml
```

### Змінна $kdr

Встановіть її для ще швидшої генерації YAML:

```bash
export kdr='--dry-run=client -o yaml'

# Now use it anywhere
k run nginx --image=nginx $kdr > pod.yaml
k create deploy web --image=nginx $kdr > deploy.yaml
```

---

## Генерація YAML для багатоконтейнерного Пода

Це фірмова навичка CKAD. Ви не можете створювати багатоконтейнерні Поди імперативно — вам потрібен YAML. Ось найшвидший підхід:

### Крок 1: Згенеруйте базовий YAML

```bash
k run multi --image=nginx $kdr > multi-pod.yaml
```

### Крок 2: Додайте другий контейнер

Відредагуйте файл і продублюйте розділ контейнера:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi
spec:
  containers:
  - name: nginx
    image: nginx
  - name: sidecar          # Add this
    image: busybox         # Add this
    command: ["sleep", "3600"]  # Add this
```

### Практикуйте до автоматизму

Цей шаблон зустрічається приблизно у 20% запитань CKAD. Ви повинні вміти:
1. Згенерувати базовий YAML
2. Додати контейнер sidecar
3. Застосувати та перевірити

Усе це менш ніж за 2 хвилини.

---

## Шаблони швидкого тестування

В CKAD часто просять перевірити вашу роботу. Ці шаблони допоможуть:

### Тестування підключення від Пода до Сервісу

```bash
# One-liner test pod
k run test --image=busybox --rm -it --restart=Never -- wget -qO- http://service-name

# DNS resolution test
k run test --image=busybox --rm -it --restart=Never -- nslookup service-name

# Test with curl
k run test --image=curlimages/curl --rm -it --restart=Never -- curl http://service-name
```

### Швидка перевірка логів Пода

```bash
# Last 10 lines
k logs pod-name --tail=10

# Follow logs
k logs pod-name -f

# Specific container in multi-container pod
k logs pod-name -c container-name

# Previous container (if restarted)
k logs pod-name --previous
```

### Зневадження всередині контейнера

```bash
# Interactive shell
k exec -it pod-name -- sh

# Specific container
k exec -it pod-name -c container-name -- sh

# Run a single command
k exec pod-name -- cat /etc/config/app.conf
```

---

## JSON Path для швидкого вилучення даних

Деякі запитання CKAD вимагають конкретних значень. JSONPath стає у пригоді:

```bash
# Get pod IP
k get pod nginx -o jsonpath='{.status.podIP}'

# Get all pod IPs
k get pods -o jsonpath='{.items[*].status.podIP}'

# Get container image
k get pod nginx -o jsonpath='{.spec.containers[0].image}'

# Get node where pod runs
k get pod nginx -o jsonpath='{.spec.nodeName}'
```

### Поширені шаблони JSONPath для CKAD

```bash
# All container names in a pod
k get pod multi -o jsonpath='{.spec.containers[*].name}'

# All service cluster IPs
k get svc -o jsonpath='{.items[*].spec.clusterIP}'

# ConfigMap data
k get cm myconfig -o jsonpath='{.data.key}'

# Secret data (base64 encoded)
k get secret mysecret -o jsonpath='{.data.password}' | base64 -d
```

---

## Управління Простором імен

Запитання CKAD часто вказують Простори імен. Будьте швидкими:

```bash
# Create namespace
k create ns dev

# Set default namespace for session
k config set-context --current --namespace=dev

# Run command in specific namespace
k get pods -n prod

# All namespaces
k get pods -A
```

### Порада від профі: Спочатку перевіряйте Простір імен

Багато кандидатів провалюють завдання на іспиті, тому що працюють не в тому Просторі імен. Завжди перевіряйте:

```bash
# Check current namespace
k config view --minify | grep namespace

# Or set it explicitly in each command
k get pods -n specified-namespace
```

---

## Швидкість Vim для редагування YAML

Ви будете постійно редагувати YAML. Ці налаштування Vim допоможуть:

```vim
" Add to ~/.vimrc
set tabstop=2
set shiftwidth=2
set expandtab
set autoindent
```

### Основні команди Vim для YAML

```vim
" Copy a line
yy

" Paste below
p

" Delete a line
dd

" Indent a block (visual mode)
>>

" Unindent a block
<<

" Search for text
/searchterm

" Jump to line 50
:50

" Save and quit
:wq
```

### Копіювання блоків YAML

Додаючи контейнер sidecar, ви будете копіювати наявну специфікацію контейнера:

```vim
1. Position cursor on the line with "- name:"
2. V (visual line mode)
3. Move down to select all container lines
4. y (yank/copy)
5. Move to where you want the new container
6. p (paste)
7. Edit the pasted block
```

---

## Чи знали ви?

- **Прапорець `--restart=Never`** є критично важливим для тестових Подів. Без нього Kubernetes створює Деплоймент замість звичайного Пода. Прапорець `--rm` видаляє Под після його завершення — ідеально для одноразових тестів.

- **Ви можете поєднати `-it` та `--rm`** для ефемерних сеансів зневадження. Под запускається інтерактивно та зникає після виходу.

- **JSONPath в kubectl** використовує той самий синтаксис, що й API Kubernetes. Його практика допомагає як на іспиті, так і в реальній автоматизації.

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|--------------|----------|
| Забутий прапорець `--restart=Never` | Створює Деплоймент замість Пода | Зробіть це частиною свого шаблону тестування |
| Неправильний Простір імен | Ресурси створюються в default | Завжди спочатку перевіряйте/встановлюйте Простір імен |
| Редагування YAML з неправильним відступом | Недійсний YAML, незрозумілі помилки | Використовуйте `:set paste` у Vim перед вставленням |
| Невикористання `--dry-run` | Повільніше створення YAML | Зробіть використання змінної `$kdr` своєю другою натурою |
| Забагато пошуку в документації | Витрачений час | Запам'ятайте типові специфікації |

---

## Тест

1. **Яка команда генерує YAML для Job без створення ресурсу?**
   <details>
   <summary>Відповідь</summary>
   `kubectl create job myjob --image=busybox -- echo done --dry-run=client -o yaml`
   </details>

2. **Як створити тестовий Под, який автоматично видаляється після запуску wget?**
   <details>
   <summary>Відповідь</summary>
   `kubectl run test --image=busybox --rm -it --restart=Never -- wget -qO- http://service`
   </details>

3. **Який JSONPath використовується для отримання образу першого контейнера з Пода?**
   <details>
   <summary>Відповідь</summary>
   `kubectl get pod podname -o jsonpath='{.spec.containers[0].image}'`
   </details>

4. **Як встановити Простір імен за замовчуванням для поточного контексту?**
   <details>
   <summary>Відповідь</summary>
   `kubectl config set-context --current --namespace=namespace-name`
   </details>

---

## Практичне завдання

**Завдання**: Відпрацюйте шаблони робочого процесу розробника CKAD.

**Частина 1: Майстерність Dry-Run (Ціль: 3 хвилини)**
```bash
# Generate these YAML files using --dry-run
# 1. Pod named 'web' with nginx image
# 2. Deployment named 'api' with httpd image, 2 replicas
# 3. Job named 'backup' that echoes "complete"
# 4. CronJob named 'hourly' running every hour
```

**Частина 2: Створення кількох контейнерів (Ціль: 4 хвилини)**
```bash
# Create a pod with two containers:
# - main: nginx
# - sidecar: busybox running "sleep 3600"
```

**Частина 3: Швидке тестування (Ціль: 2 хвилини)**
```bash
# Test connectivity to a service
# Verify pod logs work
# Execute a command in a container
```

**Критерії успіху**:
- [ ] Усі файли YAML згенеровано правильно
- [ ] Багатоконтейнерний Под працює з обома контейнерами в стані Ready
- [ ] Тестові команди виконуються успішно

---

## Практичні вправи

### Вправа 1: Перевірка псевдонімів (Ціль: 1 хвилина)

Перевірте, чи працюють ваші псевдоніми:

```bash
# These should all work
k get pods
kgy pod nginx  # Get YAML of a pod
kdr            # Should echo "--dry-run=client -o yaml"
```

### Вправа 2: Швидкість генерації YAML (Ціль: 5 хвилин)

Згенеруйте YAML для кожного типу ресурсу, не підглядаючи в нотатки:

```bash
# Pod
k run nginx --image=nginx $kdr > /tmp/pod.yaml

# Deployment
k create deploy web --image=nginx $kdr > /tmp/deploy.yaml

# Service
k create svc clusterip mysvc --tcp=80:80 $kdr > /tmp/svc.yaml

# Job
k create job backup --image=busybox -- echo done $kdr > /tmp/job.yaml

# CronJob
k create cronjob hourly --image=busybox --schedule="0 * * * *" -- date $kdr > /tmp/cronjob.yaml

# ConfigMap
k create cm myconfig --from-literal=key=value $kdr > /tmp/cm.yaml

# Secret
k create secret generic mysecret --from-literal=password=secret $kdr > /tmp/secret.yaml
```

### Вправа 3: Швидкість створення багатоконтейнерного Пода (Ціль: 3 хвилини)

Створіть багатоконтейнерний Под з нуля:

```bash
# Generate base
k run multi --image=nginx $kdr > /tmp/multi.yaml

# Edit to add sidecar (use vim)
vim /tmp/multi.yaml

# Apply
k apply -f /tmp/multi.yaml

# Verify both containers running
k get pod multi -o jsonpath='{.spec.containers[*].name}'
# Expected: nginx sidecar

# Cleanup
k delete pod multi
```

### Вправа 4: Вилучення JSONPath (Ціль: 3 хвилини)

```bash
# Create a test pod first
k run nginx --image=nginx

# Wait for running
k wait --for=condition=Ready pod/nginx

# Extract these values using JSONPath:
# 1. Pod IP
k get pod nginx -o jsonpath='{.status.podIP}'

# 2. Container image
k get pod nginx -o jsonpath='{.spec.containers[0].image}'

# 3. Node name
k get pod nginx -o jsonpath='{.spec.nodeName}'

# 4. Pod phase (Running/Pending/etc)
k get pod nginx -o jsonpath='{.status.phase}'

# Cleanup
k delete pod nginx
```

### Вправа 5: Робочий процес із Просторами імен (Ціль: 2 хвилини)

```bash
# Create a namespace
k create ns ckad-test

# Set as default
k config set-context --current --namespace=ckad-test

# Verify
k config view --minify | grep namespace

# Create a pod (should go to ckad-test)
k run nginx --image=nginx

# Verify pod is in ckad-test
k get pods  # Should show nginx
k get pods -n default  # Should NOT show nginx

# Reset namespace
k config set-context --current --namespace=default

# Cleanup
k delete ns ckad-test
```

### Вправа 6: Повний робочий процес розробника (Ціль: 8 хвилин)

Зімітуйте завдання CKAD від початку до кінця:

**Сценарій**: Створіть вебдодаток із sidecar, який логує доступ.

```bash
# 1. Create namespace
k create ns web-app

# 2. Set namespace
k config set-context --current --namespace=web-app

# 3. Generate multi-container pod YAML
k run webapp --image=nginx $kdr > /tmp/webapp.yaml

# 4. Edit to add sidecar (logs container)
# Add this container:
#   - name: logger
#     image: busybox
#     command: ["sh", "-c", "tail -f /var/log/nginx/access.log"]
#     volumeMounts:
#     - name: logs
#       mountPath: /var/log/nginx

# 5. Apply
k apply -f /tmp/webapp.yaml

# 6. Verify both containers running
k get pod webapp -o wide
k describe pod webapp | grep -A5 Containers

# 7. Test connectivity
k expose pod webapp --port=80
k run test --image=busybox --rm -it --restart=Never -- wget -qO- http://webapp

# 8. Cleanup
k config set-context --current --namespace=default
k delete ns web-app
```

---

## Наступний модуль

[Модуль 1.1: Образи контейнерів](../part1-design-build/module-1.1-container-images/) — Збірка, тегування та пуш образів контейнерів для CKAD.
