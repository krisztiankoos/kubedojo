# Модуль 5.3: Мережеві політики

> **Складність**: `[MEDIUM]` — Важливий для безпеки, потребує розуміння селекторів
>
> **Час на виконання**: 45–55 хвилин
>
> **Передумови**: Модуль 5.1 (Сервіси), розуміння міток і селекторів

---

## Чому цей модуль важливий

Типово всі поди можуть спілкуватися з усіма іншими подами. Мережеві політики дозволяють контролювати, які поди можуть звʼязуватися з якими, реалізуючи принцип найменших привілеїв для мережевого доступу. Це критично важливо для безпеки та багатоорендних кластерів.

Іспит CKAD перевіряє:
- Створення мережевих політик
- Розуміння правил вхідного (ingress) та вихідного (egress) трафіку
- Використання селекторів для вибору подів
- Зневадження проблем зі зʼєднанням

> **Аналогія з охороною офісної будівлі**
>
> Уявіть мережеві політики як правила охорони будівлі. Типово будівля не має охорони — будь-хто може йти куди завгодно. Мережеві політики — це як додавання зчитувачів карток. Ви визначаєте, хто може входити на які поверхи (ingress) і з яких поверхів люди можуть виходити (egress). Політика «типова заборона» — це як вимога картки для кожних дверей.

---

## Основи мережевих політик

### Типова поведінка

Без мережевих політик:
- Усі поди можуть спілкуватися з усіма подами
- Усі поди можуть досягати зовнішніх точок доступу
- Жодних обмежень

### Як працюють мережеві політики

1. Мережеві політики **адитивні** — вони можуть лише дозволяти трафік, не забороняти
2. Якщо БУДЬ-ЯКА політика вибирає під, дозволяється лише трафік, дозволений політиками
3. Якщо ЖОДНА політика не вибирає під, весь трафік дозволений (типово)
4. Потрібен **CNI-плагін, що підтримує мережеві політики** (Calico, Cilium тощо)

---

## Базова структура

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: my-policy
  namespace: default
spec:
  podSelector:           # До яких подів застосовується ця політика
    matchLabels:
      app: my-app
  policyTypes:           # Які типи трафіку контролювати
  - Ingress              # Вхідний трафік
  - Egress               # Вихідний трафік
  ingress:               # Правила для вхідного трафіку
  - from:
    - podSelector:
        matchLabels:
          role: frontend
  egress:                # Правила для вихідного трафіку
  - to:
    - podSelector:
        matchLabels:
          role: database
```

---

## Типи політик

### Ingress (вхідний трафік)

Контролює, що може зʼєднуватися ДО вибраних подів:

```yaml
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

### Egress (вихідний трафік)

Контролює, до чого вибрані поди можуть зʼєднуватися:

```yaml
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: backend
    ports:
    - protocol: TCP
      port: 8080
```

---

## Типи селекторів

### podSelector

Вибирає поди в тому ж просторі імен:

```yaml
ingress:
- from:
  - podSelector:
      matchLabels:
        role: frontend
```

### namespaceSelector

Вибирає поди з конкретних просторів імен:

```yaml
ingress:
- from:
  - namespaceSelector:
      matchLabels:
        env: production
```

### Комбіновані (логіка І)

Під має відповідати обом селекторам:

```yaml
ingress:
- from:
  - namespaceSelector:
      matchLabels:
        env: production
    podSelector:           # Той самий елемент списку = І
      matchLabels:
        role: frontend
```

### Окремі елементи (логіка АБО)

Трафік дозволений від будь-якого селектора:

```yaml
ingress:
- from:
  - namespaceSelector:     # Перший елемент
      matchLabels:
        env: production
  - podSelector:           # Другий елемент = АБО
      matchLabels:
        role: frontend
```

### ipBlock

Вибір за діапазоном IP (зазвичай зовнішній):

```yaml
ingress:
- from:
  - ipBlock:
      cidr: 10.0.0.0/8
      except:
      - 10.0.1.0/24
```

---

## Візуалізація

```
┌─────────────────────────────────────────────────────────────┐
│                Концепції мережевих політик                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Типово (без політики):                                     │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐              │
│  │ Під A   │◄───►│ Під B   │◄───►│ Під C   │              │
│  └─────────┘     └─────────┘     └─────────┘              │
│       Весь трафік дозволений                                │
│                                                             │
│  З політикою (вибрано Під B):                               │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐              │
│  │ Під A   │────►│ Під B   │     │ Під C   │              │
│  │(frontend)│     │(backend)│     │(інший)  │              │
│  └─────────┘     └─────────┘     └─────────┘              │
│       ✓ дозволено     X заблоковано                         │
│                                                             │
│  Типи селекторів:                                          │
│  ┌──────────────────────────────────────────────────┐     │
│  │                                                   │     │
│  │  podSelector:        Поди того ж простору імен    │     │
│  │  namespaceSelector:  Поди з позначених просторів  │     │
│  │  ipBlock:            Зовнішні діапазони IP        │     │
│  │                                                   │     │
│  │  Комбіновані в тому ж from/to елементі = І       │     │
│  │  Окремі from/to елементи = АБО                   │     │
│  │                                                   │     │
│  └──────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Поширені шаблони

### Типова заборона всього вхідного трафіку

Заблокувати весь вхідний трафік до подів у просторі імен:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}          # Порожній = вибрати всі поди
  policyTypes:
  - Ingress
  # Без правил ingress = заборонити все
```

### Типова заборона всього вихідного трафіку

Заблокувати весь вихідний трафік з подів у просторі імен:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
spec:
  podSelector: {}
  policyTypes:
  - Egress
  # Без правил egress = заборонити все
```

### Типова заборона всього

Заблокувати обидва напрямки:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### Дозволити весь вхідний трафік

Явно дозволити все (корисно для перевизначення):

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-all-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - {}                     # Порожнє правило = дозволити все
```

### Дозволити DNS у вихідному трафіку

Необхідно при використанні типової заборони вихідного трафіку:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

---

## Повний приклад: трирівневий застосунок

```yaml
# Фронтенд: може отримувати звідусіль, може звʼязуватися з бекендом
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-policy
spec:
  podSelector:
    matchLabels:
      tier: frontend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - {}                     # Дозволити весь вхідний
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: backend
    ports:
    - port: 8080
---
# Бекенд: лише від фронтенду, може звʼязуватися з базою даних
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
spec:
  podSelector:
    matchLabels:
      tier: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: frontend
    ports:
    - port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: database
    ports:
    - port: 5432
---
# База даних: лише від бекенду
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: database-policy
spec:
  podSelector:
    matchLabels:
      tier: database
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: backend
    ports:
    - port: 5432
```

---

## Швидка довідка

```bash
# Створити мережеву політику (потрібен YAML)
k apply -f policy.yaml

# Переглянути мережеві політики
k get networkpolicy
k get netpol

# Описати політику
k describe netpol NAME

# Перевірити зʼєднання
k exec pod1 -- wget -qO- --timeout=2 pod2-svc:80

# Перевірити, чи CNI підтримує мережеві політики
k get pods -n kube-system | grep -E 'calico|cilium|weave'
```

---

## Чи знали ви?

- **Мережеві політики потребують сумісного CNI.** Flannel не підтримує їх типово. Calico, Cilium і Weave — підтримують.

- **Політики адитивні, не субтрактивні.** Ви не можете створити політику, що забороняє конкретний трафік — ви можете лише дозволяти. «Заборона» відбувається шляхом вибору пода без дозволу трафіку.

- **Порожній podSelector `{}` вибирає всі поди** у просторі імен.

- **Коли ви вказуєте порти у вихідному трафіку, вам також може знадобитися дозволити DNS** (порт 53 UDP), інакше розвʼязання імен подів не працюватиме.

---

## Типові помилки

| Помилка | Чим це шкодить | Рішення |
|---------|----------------|---------|
| CNI не підтримує мережеві політики | Політики створені, але ігноруються | Використовуйте Calico, Cilium або Weave |
| Забули DNS у забороні вихідного | Під не може розвʼязувати імена | Додайте правило egress для kube-dns |
| Плутанина І та АБО | Вибрано не ті поди | Памʼятайте: той самий елемент=І, різні елементи=АБО |
| Плутанина з порожнім podSelector | Вибрано всі поди несподівано | `{}` означає «всі поди у просторі імен» |
| Забули policyTypes | Політика робить не те, що очікувалось | Завжди вказуйте Ingress та/або Egress |

---

## Тест

1. **Що станеться з подами, які не вибрані жодною мережевою політикою?**
   <details>
   <summary>Відповідь</summary>
   Весь трафік до і від цих подів дозволений (типово відкрито).
   </details>

2. **Як заблокувати весь вхідний трафік до подів у просторі імен?**
   <details>
   <summary>Відповідь</summary>
   Створіть політику типової заборони вхідного трафіку:
   ```yaml
   spec:
     podSelector: {}
     policyTypes:
     - Ingress
   ```
   Без правил ingress весь вхідний трафік заборонений.
   </details>

3. **Яка різниця між логікою І та АБО у селекторах мережевих політик?**
   <details>
   <summary>Відповідь</summary>
   - **І**: Селектори в тому ж елементі `from/to` (namespaceSelector + podSelector разом)
   - **АБО**: Окремі елементи у списку `from/to`
   </details>

4. **Чому поди можуть не розвʼязувати DNS-імена після застосування політики типової заборони вихідного трафіку?**
   <details>
   <summary>Відповідь</summary>
   DNS-запити (порт 53 UDP) заблоковані. Потрібно явно дозволити вихідний трафік до подів kube-dns.
   </details>

---

## Практична вправа

**Завдання**: Реалізувати мережеву ізоляцію для простого застосунку.

**Підготовка:**
```bash
# Створити простір імен
k create ns netpol-demo

# Створити поди
k run frontend --image=nginx -n netpol-demo -l tier=frontend
k run backend --image=nginx -n netpol-demo -l tier=backend
k run database --image=nginx -n netpol-demo -l tier=database

# Дочекатися подів
k wait --for=condition=Ready pod --all -n netpol-demo --timeout=60s

# Створити сервіси
k expose pod frontend --port=80 -n netpol-demo
k expose pod backend --port=80 -n netpol-demo
k expose pod database --port=80 -n netpol-demo
```

**Частина 1: Тест типового зʼєднання**
```bash
# Усі поди можуть досягати всіх подів
k exec -n netpol-demo frontend -- wget -qO- --timeout=2 backend:80
k exec -n netpol-demo backend -- wget -qO- --timeout=2 database:80
k exec -n netpol-demo database -- wget -qO- --timeout=2 frontend:80
# Все має працювати
```

**Частина 2: Застосувати типову заборону**
```bash
cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: netpol-demo
spec:
  podSelector: {}
  policyTypes:
  - Ingress
EOF

# Тепер тест — все має завершитись невдачею (якщо CNI підтримує мережеві політики)
k exec -n netpol-demo frontend -- wget -qO- --timeout=2 backend:80
# Має завершитись тайм-аутом
```

**Частина 3: Дозволити фронтенду доступ до бекенду**
```bash
cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-allow-frontend
  namespace: netpol-demo
spec:
  podSelector:
    matchLabels:
      tier: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: frontend
    ports:
    - port: 80
EOF

# Тест
k exec -n netpol-demo frontend -- wget -qO- --timeout=2 backend:80
# Має працювати

k exec -n netpol-demo database -- wget -qO- --timeout=2 backend:80
# Має завершитись невдачею
```

**Прибирання:**
```bash
k delete ns netpol-demo
```

---

## Практичні вправи

### Вправа 1: Типова заборона вхідного трафіку (Ціль: 2 хвилини)

```bash
k create ns drill1
k run web --image=nginx -n drill1

cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-ingress
  namespace: drill1
spec:
  podSelector: {}
  policyTypes:
  - Ingress
EOF

k get netpol -n drill1
k delete ns drill1
```

### Вправа 2: Дозволити конкретний під (Ціль: 3 хвилини)

```bash
k create ns drill2
k run server --image=nginx -n drill2 -l role=server
k run client --image=nginx -n drill2 -l role=client
k expose pod server --port=80 -n drill2

cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-client
  namespace: drill2
spec:
  podSelector:
    matchLabels:
      role: server
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: client
    ports:
    - port: 80
EOF

k describe netpol allow-client -n drill2
k delete ns drill2
```

### Вправа 3: Політика вихідного трафіку (Ціль: 3 хвилини)

```bash
k create ns drill3
k run app --image=nginx -n drill3 -l app=web
k run db --image=nginx -n drill3 -l app=db
k expose pod db --port=80 -n drill3

cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-egress
  namespace: drill3
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: db
    ports:
    - port: 80
EOF

k get netpol -n drill3
k delete ns drill3
```

### Вправа 4: Селектор простору імен (Ціль: 3 хвилини)

```bash
k create ns drill4-source
k create ns drill4-target
k label ns drill4-source env=trusted

k run target --image=nginx -n drill4-target -l app=target
k expose pod target --port=80 -n drill4-target

cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: from-trusted
  namespace: drill4-target
spec:
  podSelector:
    matchLabels:
      app: target
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          env: trusted
EOF

k describe netpol from-trusted -n drill4-target
k delete ns drill4-source drill4-target
```

### Вправа 5: Комбіновані селектори (І) (Ціль: 3 хвилини)

```bash
k create ns drill5
k label ns drill5 env=prod

k run backend --image=nginx -n drill5 -l tier=backend
k run frontend --image=nginx -n drill5 -l tier=frontend

cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: combined-and
  namespace: drill5
spec:
  podSelector:
    matchLabels:
      tier: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          env: prod
      podSelector:
        matchLabels:
          tier: frontend
EOF

k describe netpol combined-and -n drill5
k delete ns drill5
```

### Вправа 6: Блок IP (Ціль: 3 хвилини)

```bash
k create ns drill6
k run web --image=nginx -n drill6

cat << 'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ip-block
  namespace: drill6
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - ipBlock:
        cidr: 10.0.0.0/8
        except:
        - 10.0.1.0/24
EOF

k describe netpol ip-block -n drill6
k delete ns drill6
```

---

## Наступний модуль

[Сукупний тест частини 5](part5-cumulative-quiz.uk.md) — Перевірте своє володіння Сервісами, Інгресом і мережевими політиками.
