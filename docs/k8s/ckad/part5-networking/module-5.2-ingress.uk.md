# Модуль 5.2: Інгрес

> **Складність**: `[MEDIUM]` — Важливий для зовнішнього доступу, кілька концепцій
>
> **Час на виконання**: 45–55 хвилин
>
> **Передумови**: Модуль 5.1 (Сервіси), розуміння HTTP та DNS

---

## Чому цей модуль важливий

Інгрес забезпечує HTTP/HTTPS-маршрутизацію ззовні кластера до Сервісів усередині. Замість того, щоб відкривати кілька Сервісів типу LoadBalancer (дорого) або використовувати NodePort (негарні URL), Інгрес дає вам маршрутизацію на основі хосту/шляху з єдиною точкою входу.

Іспит CKAD перевіряє:
- Створення ресурсів Інгрес
- Маршрутизацію на основі хосту та шляху
- Завершення TLS
- Розуміння контролерів Інгресу

> **Аналогія з рецепцією готелю**
>
> Інгрес — це як рецепція готелю. Гості (запити) прибувають до одного входу (Інгрес) і просять різні послуги: «ресторан» іде до Сервісу їдальні, «спа» — до Сервісу оздоровлення, «кімната 203» — до Сервісу конкретного гостя. Рецепціоніст (контролер Інгресу) направляє кожного в потрібне місце залежно від запиту.

---

## Компоненти Інгресу

### Контролер Інгресу

**Контролер Інгресу** — це під, який відстежує ресурси Інгрес і налаштовує маршрутизацію. Поширені контролери:

- **Envoy Gateway** (референсна реалізація Gateway API)
- **Traefik** (підтримує і Ingress, і Gateway API)
- **Kong** (підтримує і Ingress, і Gateway API)
- **Cilium** (CNI з вбудованою підтримкою Ingress і Gateway API)
- **NGINX Gateway Fabric** (наступник ingress-nginx)

> **Примітка**: Популярний контролер **ingress-nginx** було відкликано 31 березня 2026 року, і він більше не отримує оновлень. Для нових розгортань використовуйте **Gateway API** (див. CKA Модуль 3.5) з одним із контролерів вище.

**Важливо**: Ресурси Інгрес нічого не роблять без контролера!

```bash
# Перевірити, чи є контролер Інгресу
k get pods -n ingress-nginx
# або
k get pods -A | grep -i ingress
```

### Ресурс Інгрес

**Інгрес** — це ресурс Kubernetes, що визначає правила маршрутизації:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-service
            port:
              number: 80
```

---

## Типи шляхів

### Prefix (найпоширеніший)

Збіг за префіксом URL-шляху:

```yaml
pathType: Prefix
path: /api
# Збігається: /api, /api/, /api/users, /api/users/123
```

### Exact

Збіг лише з точним шляхом:

```yaml
pathType: Exact
path: /api
# Збігається: лише /api
# НЕ збігається: /api/, /api/users
```

### ImplementationSpecific

Залежить від IngressClass (специфічний для контролера).

---

## Шаблони маршрутизації

### Маршрутизація на основі хосту

Різні хости до різних сервісів:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-routing
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
  - host: web.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

### Маршрутизація на основі шляху

Різні шляхи до різних сервісів:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-routing
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
      - path: /web
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

### Типовий бекенд

Перехоплює всі запити без збігу:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: with-default
spec:
  defaultBackend:
    service:
      name: default-service
      port:
        number: 80
  rules:
  - host: example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
```

---

## TLS/HTTPS

### Створення TLS-секрету

```bash
# Створити TLS-секрет із сертифіката та ключа
k create secret tls my-tls-secret \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key
```

### Інгрес із TLS

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
spec:
  tls:
  - hosts:
    - secure.example.com
    secretName: my-tls-secret
  rules:
  - host: secure.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: secure-service
            port:
              number: 80
```

---

## Візуалізація

```
┌─────────────────────────────────────────────────────────────┐
│                    Потік Інгресу                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Інтернет                                                   │
│     │                                                       │
│     ▼                                                       │
│  ┌─────────────────────────────────────┐                   │
│  │     Контролер Інгресу              │                   │
│  │     (nginx, traefik тощо)          │                   │
│  │                                      │                   │
│  │  Читає правила Інгресу             │                   │
│  │  Маршрутизує за хостом/шляхом      │                   │
│  └─────────────────────────────────────┘                   │
│     │                                                       │
│     │ api.example.com/users                                │
│     │                                                       │
│     ▼                                                       │
│  ┌─────────────────────────────────────┐                   │
│  │         Ресурс Інгрес              │                   │
│  │                                      │                   │
│  │  rules:                             │                   │
│  │  - host: api.example.com            │                   │
│  │    paths:                           │                   │
│  │    - /users → user-svc:80           │                   │
│  │    - /orders → order-svc:80         │                   │
│  │  - host: web.example.com            │                   │
│  │    paths:                           │                   │
│  │    - / → frontend-svc:80            │                   │
│  └─────────────────────────────────────┘                   │
│     │                                                       │
│     ▼                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ user-svc │  │order-svc │  │frontend  │                 │
│  │   :80    │  │   :80    │  │svc :80   │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## IngressClass

Визначає, який контролер обслуговує Інгрес:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
  ingressClassName: nginx    # Який контролер
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-service
            port:
              number: 80
```

```bash
# Переглянути доступні IngressClass
k get ingressclass
```

---

## Анотації

Специфічна для контролера поведінка через анотації:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: annotated-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
```

Поширені анотації NGINX:
- `nginx.ingress.kubernetes.io/rewrite-target`: Перезапис URL
- `nginx.ingress.kubernetes.io/ssl-redirect`: Примусовий HTTPS
- `nginx.ingress.kubernetes.io/proxy-body-size`: Максимальний розмір тіла запиту

---

## Швидка довідка

```bash
# Створити Інгрес імперативно (обмежено)
k create ingress my-ingress \
  --rule="host.example.com/path=service:port"

# Переглянути Інгрес
k get ingress
k describe ingress NAME

# Отримати адресу Інгресу
k get ingress NAME -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Перевірити IngressClass
k get ingressclass

# Переглянути логи контролера
k logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

---

## Чи знали ви?

- **Інгрес — це лише конфігурація, не сервіс.** Фактичну маршрутизацію виконують поди контролера Інгресу.

- **Для одного хосту може існувати кілька ресурсів Інгрес.** Контролери зазвичай обʼєднують їх.

- **Анотація `kubernetes.io/ingress.class` застаріла.** Використовуйте `spec.ingressClassName` натомість (Kubernetes 1.18+).

- **Інгрес не може маршрутизувати не-HTTP трафік.** Для TCP/UDP використовуйте Сервіси типу LoadBalancer або новіший Gateway API.

---

## Типові помилки

| Помилка | Чим це шкодить | Рішення |
|---------|----------------|---------|
| Контролер Інгресу не встановлено | Інгрес нічого не робить | Встановити nginx-ingress або аналог |
| Неправильний pathType | Маршрути не збігаються | Використовуйте `Prefix` для більшості випадків |
| Невідповідність назви/порту Сервісу | Помилки 503 | Перевірте, що сервіс існує та порт збігається |
| Відсутній host у правилах | Збігається з усіма хостами | Додайте явний host або використовуйте обережно |
| TLS-секрет у неправильному просторі імен | TLS не працює | Секрет має бути в тому ж просторі імен, що й Інгрес |

---

## Тест

1. **Яка різниця між ресурсом Інгрес і контролером Інгресу?**
   <details>
   <summary>Відповідь</summary>
   Ресурс Інгрес — це обʼєкт Kubernetes, що визначає правила маршрутизації. Контролер Інгресу — це запущений під, який читає ресурси Інгрес і налаштовує фактичну маршрутизацію (наприклад, конфігурацію NGINX).
   </details>

2. **Як направити трафік до різних сервісів на основі URL-шляху?**
   <details>
   <summary>Відповідь</summary>
   Використовуйте кілька шляхів у правилах Інгресу:
   ```yaml
   paths:
   - path: /api
     pathType: Prefix
     backend:
       service:
         name: api-service
         port:
           number: 80
   - path: /web
     pathType: Prefix
     backend:
       service:
         name: web-service
         port:
           number: 80
   ```
   </details>

3. **Що потрібно для завершення HTTPS в Інгресі?**
   <details>
   <summary>Відповідь</summary>
   TLS-секрет, що містить сертифікат і ключ, на який посилається специфікація Інгресу:
   ```yaml
   spec:
     tls:
     - hosts:
       - example.com
       secretName: tls-secret
   ```
   </details>

4. **Що станеться, якщо контролер Інгресу не встановлено?**
   <details>
   <summary>Відповідь</summary>
   Ресурси Інгрес створюються, але не мають жодного ефекту. Маршрутизація не відбувається, бо немає нічого, що відстежувало б і реалізовувало правила.
   </details>

---

## Практична вправа

**Завдання**: Створити Інгрес із маршрутизацією на основі шляху.

**Підготовка:**
```bash
# Створити два деплойменти
k create deployment web --image=nginx
k create deployment api --image=nginx

# Створити сервіси
k expose deployment web --port=80
k expose deployment api --port=80

# Дочекатися подів
k wait --for=condition=Ready pod -l app=web --timeout=60s
k wait --for=condition=Ready pod -l app=api --timeout=60s
```

**Частина 1: Простий Інгрес**
```bash
cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: simple-ingress
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
EOF

k get ingress simple-ingress
k describe ingress simple-ingress
```

**Частина 2: Маршрутизація на основі шляху**
```bash
cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-ingress
spec:
  rules:
  - http:
      paths:
      - path: /web
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 80
EOF

k describe ingress path-ingress
```

**Частина 3: Маршрутизація на основі хосту**
```bash
cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-ingress
spec:
  rules:
  - host: web.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
  - host: api.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 80
EOF

k describe ingress host-ingress
```

**Прибирання:**
```bash
k delete ingress simple-ingress path-ingress host-ingress
k delete deployment web api
k delete svc web api
```

---

## Практичні вправи

### Вправа 1: Простий Інгрес (Ціль: 2 хвилини)

```bash
k create deployment drill1 --image=nginx
k expose deployment drill1 --port=80

cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: drill1
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: drill1
            port:
              number: 80
EOF

k get ingress drill1
k delete ingress drill1 deploy drill1 svc drill1
```

### Вправа 2: Маршрутизація на основі хосту (Ціль: 3 хвилини)

```bash
k create deployment app1 --image=nginx
k create deployment app2 --image=nginx
k expose deployment app1 --port=80
k expose deployment app2 --port=80

cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: drill2
spec:
  rules:
  - host: app1.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app1
            port:
              number: 80
  - host: app2.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app2
            port:
              number: 80
EOF

k describe ingress drill2
k delete ingress drill2 deploy app1 app2 svc app1 app2
```

### Вправа 3: Маршрутизація на основі шляху (Ціль: 3 хвилини)

```bash
k create deployment frontend --image=nginx
k create deployment backend --image=nginx
k expose deployment frontend --port=80
k expose deployment backend --port=80

cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: drill3
spec:
  rules:
  - host: myapp.local
    http:
      paths:
      - path: /frontend
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
      - path: /backend
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 80
EOF

k get ingress drill3
k delete ingress drill3 deploy frontend backend svc frontend backend
```

### Вправа 4: Інгрес із типовим бекендом (Ціль: 3 хвилини)

```bash
k create deployment default-app --image=nginx
k create deployment api-app --image=nginx
k expose deployment default-app --port=80
k expose deployment api-app --port=80

cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: drill4
spec:
  defaultBackend:
    service:
      name: default-app
      port:
        number: 80
  rules:
  - http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-app
            port:
              number: 80
EOF

k describe ingress drill4
k delete ingress drill4 deploy default-app api-app svc default-app api-app
```

### Вправа 5: Створити Інгрес імперативно (Ціль: 2 хвилини)

```bash
k create deployment drill5 --image=nginx
k expose deployment drill5 --port=80

# Створити інгрес імперативно
k create ingress drill5 --rule="drill5.local/=drill5:80"

k get ingress drill5
k describe ingress drill5

k delete ingress drill5 deploy drill5 svc drill5
```

### Вправа 6: Інгрес із TLS (Ціль: 4 хвилини)

```bash
# Створити самопідписаний сертифікат (для демо)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /tmp/tls.key -out /tmp/tls.crt \
  -subj "/CN=secure.local" 2>/dev/null

# Створити TLS-секрет
k create secret tls drill6-tls --cert=/tmp/tls.crt --key=/tmp/tls.key

k create deployment drill6 --image=nginx
k expose deployment drill6 --port=80

cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: drill6
spec:
  tls:
  - hosts:
    - secure.local
    secretName: drill6-tls
  rules:
  - host: secure.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: drill6
            port:
              number: 80
EOF

k describe ingress drill6

k delete ingress drill6 secret drill6-tls deploy drill6 svc drill6
rm /tmp/tls.key /tmp/tls.crt
```

---

## Наступний модуль

[Модуль 5.3: Мережеві політики](module-5.3-networkpolicies.uk.md) — Контроль комунікації між подами.
