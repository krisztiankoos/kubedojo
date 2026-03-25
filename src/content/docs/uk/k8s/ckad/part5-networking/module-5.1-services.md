---
title: "\u041c\u043e\u0434\u0443\u043b\u044c 5.1: \u0421\u0435\u0440\u0432\u0456\u0441\u0438"
sidebar:
  order: 1
  label: "Part 5: Networking"
---
> **Складність**: `[MEDIUM]` — Основна концепція мережі, кілька типів для розуміння
>
> **Час на виконання**: 45–55 хвилин
>
> **Передумови**: Модуль 1.1 (Поди), Модуль 2.1 (Деплойменти), розуміння основ мережі

---

## Чому цей модуль важливий

Сервіси забезпечують стабільну мережу для подів. Оскільки поди ефемерні й отримують нові IP при перестворенні, вам потрібні Сервіси для стабільного доступу до ваших застосунків. Сервіси — це основа того, як застосунки спілкуються в Kubernetes.

Іспит CKAD перевіряє:
- Створення Сервісів (ClusterIP, NodePort, LoadBalancer)
- Розуміння виявлення Сервісів
- Зневадження зʼєднання Сервісів
- Роботу з точками доступу (endpoints)

> **Аналогія з телефонним довідником**
>
> Сервіси — це як корпоративний телефонний довідник. Працівники (поди) приходять і йдуть, змінюють робочі місця (IP), але внутрішній номер відділу (Сервіс) залишається незмінним. Коли ви телефонуєте у «Відділ продажів» (назва Сервісу), система направляє виклик тому, хто зараз працює. Довідник (DNS) перетворює імена на номери, а комутатор (kube-proxy) маршрутизує виклик.

---

## Типи Сервісів

### ClusterIP (типовий)

Доступ лише зсередини кластера:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: ClusterIP          # Типовий, можна не вказувати
  selector:
    app: my-app
  ports:
  - port: 80               # Порт Сервісу
    targetPort: 8080       # Порт контейнера
```

```bash
# Створити імперативно
k expose deployment my-app --port=80 --target-port=8080

# Доступ зсередини кластера
curl http://my-service:80
curl http://my-service.default.svc.cluster.local:80
```

### NodePort

Відкриває на IP кожного вузла на статичному порті:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-nodeport
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
  - port: 80               # Порт Сервісу (ClusterIP)
    targetPort: 8080       # Порт контейнера
    nodePort: 30080        # Порт вузла (30000-32767)
```

```bash
# Створити імперативно
k expose deployment my-app --type=NodePort --port=80 --target-port=8080

# Доступ ззовні кластера
curl http://<node-ip>:30080
```

### LoadBalancer

Створює зовнішній балансувальник навантаження (хмарні середовища):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-loadbalancer
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 8080
```

```bash
# Створити імперативно
k expose deployment my-app --type=LoadBalancer --port=80 --target-port=8080

# Отримати зовнішню IP
k get svc my-loadbalancer
# Стовпець EXTERNAL-IP показує IP балансувальника навантаження
```

### ExternalName

Відображає на зовнішнє DNS-імʼя (без проксіювання):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-db
spec:
  type: ExternalName
  externalName: database.example.com
```

---

## Виявлення Сервісів

### DNS-імена

Kubernetes створює DNS-записи для Сервісів:

```
<назва-сервісу>.<простір-імен>.svc.cluster.local
```

| DNS-імʼя | Що резолвить |
|----------|--------------|
| `my-service` | Той самий простір імен |
| `my-service.default` | Простір імен default |
| `my-service.default.svc` | Простір імен default, svc |
| `my-service.default.svc.cluster.local` | Повний FQDN |

### Змінні середовища

Поди отримують змінні середовища для Сервісів, що існували на момент запуску пода:

```bash
# Всередині пода
env | grep MY_SERVICE
# MY_SERVICE_SERVICE_HOST=10.96.0.1
# MY_SERVICE_SERVICE_PORT=80
```

---

## Візуалізація

```
┌─────────────────────────────────────────────────────────────┐
│                    Типи Сервісів                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ClusterIP (лише внутрішній)                                │
│  ┌─────────────────────────────────────┐                   │
│  │  cluster.local:80 ──► Під:8080     │                   │
│  │                   ──► Під:8080     │                   │
│  │                   ──► Під:8080     │                   │
│  └─────────────────────────────────────┘                   │
│                                                             │
│  NodePort (ClusterIP + доступ через вузол)                  │
│  ┌─────────────────────────────────────┐                   │
│  │  <IP-вузла>:30080 ──► ClusterIP:80 ──► Поди            │
│  └─────────────────────────────────────┘                   │
│                                                             │
│  LoadBalancer (NodePort + зовнішній БН)                     │
│  ┌─────────────────────────────────────┐                   │
│  │  <Зовн-IP>:80 ──► NodePort ──► ClusterIP ──► Поди      │
│  └─────────────────────────────────────┘                   │
│                                                             │
│  Потік портів Сервісу:                                      │
│  ┌──────────────────────────────────────────────────┐     │
│  │                                                   │     │
│  │  Зовнішній ──► nodePort ──► port ──► targetPort  │     │
│  │    :80          :30080      :80       :8080       │     │
│  │                                                   │     │
│  └──────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Селектори та точки доступу

### Як Сервіси знаходять Поди

Сервіси використовують **селектори міток** для пошуку подів:

```yaml
# Сервіс
spec:
  selector:
    app: my-app
    tier: frontend

# Під (має відповідати ВСІМ міткам)
metadata:
  labels:
    app: my-app
    tier: frontend
```

### Точки доступу (Endpoints)

Точки доступу створюються та оновлюються автоматично:

```bash
# Переглянути точки доступу
k get endpoints my-service
# NAME         ENDPOINTS                         AGE
# my-service   10.244.0.5:8080,10.244.0.6:8080   5m

# Describe показує IP подів
k describe endpoints my-service
```

### Немає відповідних подів?

Якщо селектор не збігається з жодним подом:

```bash
k get endpoints my-service
# NAME         ENDPOINTS   AGE
# my-service   <none>      5m
```

---

## Безголові Сервіси (Headless)

Для прямого виявлення подів без балансування навантаження:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: headless-svc
spec:
  clusterIP: None          # Робить безголовим
  selector:
    app: my-app
  ports:
  - port: 80
```

DNS повертає всі IP подів замість IP Сервісу:

```bash
# Повертає кілька A-записів (один на кожен під)
nslookup headless-svc.default.svc.cluster.local
```

Випадки використання: StatefulSets, бази даних, виявлення пірів.

---

## Багатопортові Сервіси

```yaml
apiVersion: v1
kind: Service
metadata:
  name: multi-port
spec:
  selector:
    app: my-app
  ports:
  - name: http           # Назва обовʼязкова для багатопортових
    port: 80
    targetPort: 8080
  - name: https
    port: 443
    targetPort: 8443
```

---

## Спорідненість сесій

Маршрутизувати того самого клієнта до того самого пода:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: sticky-service
spec:
  selector:
    app: my-app
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
  ports:
  - port: 80
```

---

## Швидка довідка

```bash
# Створити Сервіс
k expose deployment NAME --port=80 --target-port=8080
k expose deployment NAME --type=NodePort --port=80
k expose deployment NAME --type=LoadBalancer --port=80

# Переглянути Сервіси
k get svc
k describe svc NAME

# Переглянути точки доступу
k get endpoints NAME
k get ep NAME

# Зневадити DNS
k run tmp --image=busybox --rm -it --restart=Never -- nslookup my-service

# Перевірити зʼєднання
k run tmp --image=busybox --rm -it --restart=Never -- wget -qO- my-service:80
```

---

## Чи знали ви?

- **kube-proxy насправді не проксіює трафік.** Попри свою назву, він налаштовує правила iptables/IPVS. Трафік йде напряму від джерела до цільового пода.

- **Сервіси існують на рівні всього кластера, хоча вони належать простору імен.** DNS-імʼя включає простір імен, але підлеглий ClusterIP працює між просторами імен.

- **NodePort використовує ВСІ вузли.** Навіть вузли без цільових подів перенаправлять трафік до правильного пода.

- **Діапазон портів 30000–32767** можна налаштувати через прапорець `--service-node-port-range` kube-apiserver.

---

## Типові помилки

| Помилка | Чим це шкодить | Рішення |
|---------|----------------|---------|
| Селектор не збігається з мітками подів | Сервіс не має точок доступу | `k get ep` для перевірки, виправити мітки |
| Неправильний targetPort | Зʼєднання відхилено | Має збігатися з портом, на якому слухає контейнер |
| Використання IP пода замість Сервісу | Ламається при перезапуску пода | Завжди використовуйте імʼя/IP Сервісу |
| Забули простір імен у DNS | Не можна дістатися до Сервісу | Використовуйте `svc.namespace` або повний FQDN |
| NodePort без правила файрволу | Немає доступу ззовні | Відкрити порт вузла у хмарному файрволі |

---

## Тест

1. **Яка різниця між `port` і `targetPort` у Сервісі?**
   <details>
   <summary>Відповідь</summary>
   `port` — це порт Сервісу (до якого підключаються клієнти). `targetPort` — це порт контейнера (куди перенаправляється трафік). Приклад: Сервіс слухає на 80, перенаправляє на порт 8080 контейнера.
   </details>

2. **Як дізнатися, до яких подів маршрутизує Сервіс?**
   <details>
   <summary>Відповідь</summary>
   `kubectl get endpoints <назва-сервісу>` показує IP та порти подів, до яких маршрутизує Сервіс.
   </details>

3. **Що станеться, якщо селектор Сервісу не збігається з жодним подом?**
   <details>
   <summary>Відповідь</summary>
   Сервіс існує, але не має точок доступу. Зʼєднання не працюватимуть. `kubectl get endpoints` покаже `<none>`.
   </details>

4. **Як поди у просторі імен A можуть звернутися до Сервісу у просторі імен B?**
   <details>
   <summary>Відповідь</summary>
   Використовуйте DNS-імʼя з простором імен: `service-name.namespace-b` або повний FQDN `service-name.namespace-b.svc.cluster.local`.
   </details>

---

## Практична вправа

**Завдання**: Створити та протестувати різні типи Сервісів.

**Підготовка:**
```bash
# Створити деплоймент
k create deployment web --image=nginx --replicas=3

# Дочекатися подів
k wait --for=condition=Ready pod -l app=web --timeout=60s
```

**Частина 1: Сервіс ClusterIP**
```bash
# Створити ClusterIP сервіс
k expose deployment web --port=80 --target-port=80

# Перевірити точки доступу
k get endpoints web

# Тест зсередини кластера
k run test --image=busybox --rm -it --restart=Never -- wget -qO- web:80

# Перевірити DNS
k run test --image=busybox --rm -it --restart=Never -- nslookup web.default.svc.cluster.local
```

**Частина 2: Сервіс NodePort**
```bash
# Видалити ClusterIP сервіс
k delete svc web

# Створити NodePort сервіс
k expose deployment web --type=NodePort --port=80 --target-port=80

# Отримати призначений NodePort
k get svc web -o jsonpath='{.spec.ports[0].nodePort}'
echo

# Тест (якщо є доступ до вузла)
# curl http://<node-ip>:<nodeport>
```

**Частина 3: Зневадження відсутніх точок доступу**
```bash
# Створити сервіс з неправильним селектором
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Service
metadata:
  name: broken-svc
spec:
  selector:
    app: wrong-label
  ports:
  - port: 80
EOF

# Перевірити точки доступу (мають бути порожніми)
k get endpoints broken-svc

# Виправити патчем селектора
k patch svc broken-svc -p '{"spec":{"selector":{"app":"web"}}}'

# Перевірити, що точки доступу тепер є
k get endpoints broken-svc
```

**Прибирання:**
```bash
k delete deployment web
k delete svc web broken-svc
```

---

## Практичні вправи

### Вправа 1: Створити ClusterIP Сервіс (Ціль: 1 хвилина)

```bash
k create deployment drill1 --image=nginx
k expose deployment drill1 --port=80
k get svc drill1
k get ep drill1
k delete deploy drill1 svc drill1
```

### Вправа 2: Створити NodePort Сервіс (Ціль: 2 хвилини)

```bash
k create deployment drill2 --image=nginx
k expose deployment drill2 --type=NodePort --port=80 --target-port=80

# Отримати NodePort
k get svc drill2 -o jsonpath='{.spec.ports[0].nodePort}'
echo

k delete deploy drill2 svc drill2
```

### Вправа 3: Тестування DNS-резолюції (Ціль: 2 хвилини)

```bash
k create deployment drill3 --image=nginx
k expose deployment drill3 --port=80

# Тестування DNS
k run dns-test --image=busybox --rm -it --restart=Never -- nslookup drill3

k delete deploy drill3 svc drill3
```

### Вправа 4: Сервіс з іменованим портом (Ціль: 2 хвилини)

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Service
metadata:
  name: drill4
spec:
  selector:
    app: drill4
  ports:
  - name: http
    port: 80
    targetPort: 80
  - name: metrics
    port: 9090
    targetPort: 9090
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: drill4
spec:
  replicas: 2
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
        image: nginx
EOF

k get svc drill4
k get ep drill4
k delete deploy drill4 svc drill4
```

### Вправа 5: Зневадження зʼєднання Сервісу (Ціль: 3 хвилини)

```bash
# Створити деплоймент і зламаний сервіс
k create deployment drill5 --image=nginx
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Service
metadata:
  name: drill5
spec:
  selector:
    app: wrong
  ports:
  - port: 80
EOF

# Зневадження
k get ep drill5                        # Немає точок доступу
k get pods --show-labels               # Перевірити мітки подів
k describe svc drill5 | grep Selector  # Перевірити селектор сервісу

# Виправлення
k patch svc drill5 -p '{"spec":{"selector":{"app":"drill5"}}}'
k get ep drill5                        # Тепер мають бути точки доступу

k delete deploy drill5 svc drill5
```

### Вправа 6: Доступ до Сервісу між просторами імен (Ціль: 3 хвилини)

```bash
# Створити простір імен і сервіс
k create ns drill6
k create deployment drill6-app --image=nginx -n drill6
k expose deployment drill6-app --port=80 -n drill6

# Доступ з простору імен default
k run test --image=busybox --rm -it --restart=Never -- wget -qO- drill6-app.drill6:80

k delete ns drill6
```

---

## Наступний модуль

[Модуль 5.2: Інгрес](module-5.2-ingress.md) — HTTP-маршрутизація та завершення TLS.
