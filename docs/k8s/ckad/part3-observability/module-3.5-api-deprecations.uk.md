# Модуль 3.5: Застарівання API

> **Складність**: `[QUICK]` — Концептуальне розуміння з практичними командами
>
> **Час на виконання**: 20–25 хвилин
>
> **Передумови**: Розуміння версіювання API Kubernetes

---

## Чому цей модуль важливий

Kubernetes розвивається стрімко. API, які працюють сьогодні, можуть бути оголошені застарілими завтра і видалені в майбутніх версіях. Розуміння застарівання API запобігає зламаним маніфестам та невдалим розгортанням.

Іспит CKAD перевіряє:
- Обізнаність про застарілі API
- Як визначити версії API для ресурсів
- Оновлення маніфестів для використання поточних API

> **Аналогія з ремонтом дороги**
>
> Застарівання API — як ремонт дороги. Спочатку знаки попереджають, що дорогу закриють (застарівання). У вас є час знайти альтернативні маршрути (нова версія API). Врешті-решт стара дорога повністю закривається (видалення API). Якщо ви ігноруєте попередження — залишитесь ні з чим, коли дорога зникне.

---

## Основи версіювання API

### Етапи версій

| Етап | Значення | Стабільність |
|------|----------|--------------|
| `alpha` (v1alpha1) | Експериментальний, може змінитися або зникнути | Нестабільний |
| `beta` (v1beta1) | Функціонально завершений, може змінитися | Переважно стабільний |
| `stable` (v1, v2) | Готовий до продакшну, зворотно сумісний | Стабільний |

### Прогресія версій

```
v1alpha1 → v1alpha2 → v1beta1 → v1beta2 → v1
```

### Групи API

```yaml
# Основна група (без префікса)
apiVersion: v1
kind: Pod

# Іменовані групи
apiVersion: apps/v1
kind: Deployment

apiVersion: networking.k8s.io/v1
kind: Ingress

apiVersion: batch/v1
kind: Job
```

---

## Типові застарівання

### Історичні приклади

| Старий API | Поточний API | Видалено у |
|------------|--------------|------------|
| `extensions/v1beta1 Ingress` | `networking.k8s.io/v1` | 1.22 |
| `apps/v1beta1 Deployment` | `apps/v1` | 1.16 |
| `rbac.authorization.k8s.io/v1beta1` | `rbac.authorization.k8s.io/v1` | 1.22 |
| `networking.k8s.io/v1beta1 IngressClass` | `networking.k8s.io/v1` | 1.22 |
| `batch/v1beta1 CronJob` | `batch/v1` | 1.25 |
| `policy/v1beta1 PodSecurityPolicy` | Видалено (використовуйте Pod Security Admission) | 1.25 |

### Поточне середовище іспиту

Іспит CKAD використовує нещодавні версії Kubernetes. Більшість beta API вже видалено. Завжди використовуйте стабільні (`v1`) версії.

---

## Пошук правильних версій API

### Перелік ресурсів API

```bash
# Усі ресурси з версіями API
k api-resources

# Конкретний ресурс
k api-resources | grep -i deployment
# Вивід: deployments   deploy   apps/v1   true   Deployment

# З короткими назвами
k api-resources --sort-by=name
```

### Команда Explain

```bash
# Отримати версію API для ресурсу
k explain deployment
# Вивід показує: VERSION: apps/v1

k explain ingress
# Вивід показує: VERSION: networking.k8s.io/v1

k explain cronjob
# Вивід показує: VERSION: batch/v1
```

### Перегляд наявних об'єктів

```bash
# Побачити, яку версію використовують наявні об'єкти
k get deployment nginx -o yaml | head -5
# apiVersion: apps/v1
# kind: Deployment
```

---

## Перевірка на застарілі API

### kubectl Convert (якщо доступний)

```bash
# Конвертувати старий маніфест у новий API
kubectl convert -f old-deployment.yaml --output-version apps/v1
```

Примітка: `kubectl convert` може бути недоступний у всіх середовищах.

### Ручна перевірка

```bash
# Перевірити, що використовує маніфест
head -5 my-manifest.yaml

# Порівняти з поточним API
k api-resources | grep -i <resource-type>
```

### Попередження API Server

Коли ви застосовуєте застарілий API, сервер попереджає:

```bash
$ k apply -f old-ingress.yaml
Warning: networking.k8s.io/v1beta1 Ingress is deprecated in v1.19+,
unavailable in v1.22+; use networking.k8s.io/v1 Ingress
```

---

## Оновлення маніфестів

### Приклад: Оновлення Ingress

**Старий (застарілий):**
```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: my-ingress
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        backend:
          serviceName: my-service
          servicePort: 80
```

**Новий (поточний):**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
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

### Ключові зміни, які часто потрібні

1. **apiVersion** — Оновити до стабільної версії
2. **Структура spec** — Може змінюватися між версіями
3. **Нові обов'язкові поля** — Як `pathType` для Ingress

---

## Стратегія для іспиту

### Перед написанням YAML

```bash
# Завжди спочатку перевіряйте поточну версію API
k explain <resource>

# Приклад
k explain ingress
k explain cronjob
k explain networkpolicy
```

### Швидка довідка для типових ресурсів

| Ресурс | Поточний apiVersion |
|--------|---------------------|
| Pod | v1 |
| Service | v1 |
| ConfigMap | v1 |
| Secret | v1 |
| Deployment | apps/v1 |
| StatefulSet | apps/v1 |
| DaemonSet | apps/v1 |
| Job | batch/v1 |
| CronJob | batch/v1 |
| Ingress | networking.k8s.io/v1 |
| NetworkPolicy | networking.k8s.io/v1 |
| Role/RoleBinding | rbac.authorization.k8s.io/v1 |
| ClusterRole/ClusterRoleBinding | rbac.authorization.k8s.io/v1 |

---

## Політика застарівання

### Гарантії Kubernetes

1. **Beta API оголошуються застарілими щонайменше за 3 випуски** перед видаленням
2. **Стабільні API майже ніколи не видаляються** (лише при зміні мажорної версії)
3. **Попередження про застарівання** показуються у відповідях API server

### Приклад хронології

```
1.19: v1beta1 оголошено застарілим (попередження)
1.20: v1beta1 ще працює (попередження продовжується)
1.21: v1beta1 ще працює (попередження продовжується)
1.22: v1beta1 ВИДАЛЕНО (помилка при використанні)
```

---

## Чи знали ви?

- **PodSecurityPolicy було повністю видалено** в Kubernetes 1.25. Його замінив Pod Security Admission, який працює по-іншому.

- **Плагін `kubectl convert`** може конвертувати між версіями API, але він не встановлений типово і може бути відсутній на іспиті.

- **CRD можуть мати власний графік застарівання**, встановлений оператором/постачальником, який їх створив.

- **Запуск `kubectl apply` із застарілими API** все ще працює до видалення, але щоразу ви отримуватимете попередження.

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| Використання beta API у нових маніфестах | Зламається в майбутньому | Завжди використовуйте стабільні v1 |
| Копіювання старих прикладів з інтернету | Застарілі API | Перевіряйте версію через `k explain` |
| Ігнорування попереджень про застарівання | Маніфести зламаються після оновлення | Оновлюйте негайно |
| Незнання поточних версій | Витрата часу на іспиті | Запам'ятайте типові ресурси |

---

## Тест

1. **Як знайти поточну версію API для ресурсу?**
   <details>
   <summary>Відповідь</summary>
   `kubectl explain <resource>` або `kubectl api-resources | grep <resource>`
   </details>

2. **Яка поточна apiVersion для Ingress?**
   <details>
   <summary>Відповідь</summary>
   `networking.k8s.io/v1`
   </details>

3. **Яка поточна apiVersion для CronJob?**
   <details>
   <summary>Відповідь</summary>
   `batch/v1`
   </details>

4. **Що станеться, якщо використати видалену версію API?**
   <details>
   <summary>Відповідь</summary>
   API server поверне помилку, і ресурс не вдасться створити/оновити.
   </details>

---

## Практична вправа

**Завдання**: Попрактикуватися у пошуку та використанні правильних версій API.

**Частина 1: Дослідження версій API**
```bash
# Перелічити всі ресурси API
k api-resources | head -20

# Знайти конкретні ресурси
k api-resources | grep -i deployment
k api-resources | grep -i ingress
k api-resources | grep -i cronjob

# Використати explain
k explain deployment
k explain ingress
k explain cronjob
```

**Частина 2: Створення ресурсів з правильними API**
```bash
# Створити Deployment (apps/v1)
k create deploy api-test --image=nginx --dry-run=client -o yaml | head -10

# Згенерувати CronJob (batch/v1)
k create cronjob api-cron --image=busybox --schedule="*/5 * * * *" -- echo hello --dry-run=client -o yaml | head -10
```

**Частина 3: Перевірка наявних ресурсів**
```bash
# Перевірити, яку версію використовують наявні ресурси
k get deployments -A -o jsonpath='{range .items[*]}{.apiVersion}{"\t"}{.metadata.name}{"\n"}{end}'
```

---

## Практичні вправи

### Вправа 1: Ресурси API (Ціль: 2 хвилини)

```bash
# Знайти версію API для різних ресурсів
k explain pod | head -5
k explain service | head -5
k explain deployment | head -5
k explain ingress | head -5
k explain networkpolicy | head -5
```

### Вправа 2: Перелік ресурсів API (Ціль: 2 хвилини)

```bash
# Перелічити ресурси та їхні групи
k api-resources --sort-by=name | grep -E "^NAME|deployment|ingress|job|cronjob"
```

### Вправа 3: Генерація правильного YAML (Ціль: 3 хвилини)

```bash
# Згенерувати маніфести та перевірити версії API

# Deployment
k create deploy drill3-deploy --image=nginx --dry-run=client -o yaml | grep apiVersion

# Job
k create job drill3-job --image=busybox -- echo done --dry-run=client -o yaml | grep apiVersion

# CronJob
k create cronjob drill3-cron --image=busybox --schedule="* * * * *" -- echo hi --dry-run=client -o yaml | grep apiVersion
```

### Вправа 4: Визначення груп ресурсів (Ціль: 2 хвилини)

```bash
# До якої групи належить кожен?
k api-resources | grep -E "^NAME|^deployments|^services|^ingresses|^networkpolicies"

# Очікувано:
# deployments - apps
# services - core (без групи)
# ingresses - networking.k8s.io
# networkpolicies - networking.k8s.io
```

### Вправа 5: Повний пошук версій (Ціль: 3 хвилини)

**Сценарій**: Вам потрібно написати YAML для кількох ресурсів. Знайдіть правильні версії API.

```bash
# Потрібні ресурси: Deployment, Service, Ingress, ConfigMap, Secret, NetworkPolicy

# Швидкий пошук
for res in deployment service ingress configmap secret networkpolicy; do
  echo -n "$res: "
  k explain $res 2>/dev/null | grep "VERSION:" | awk '{print $2}'
done
```

---

## Підсумок Частини 3

Ви завершили розділ «Спостережуваність та обслуговування застосунків»:

- **Модуль 3.1**: Проби — Перевірка стану з liveness, readiness, startup
- **Модуль 3.2**: Логування — Доступ до логів контейнерів
- **Модуль 3.3**: Налагодження — Системний процес усунення несправностей
- **Модуль 3.4**: Моніторинг — Використання ресурсів з kubectl top
- **Модуль 3.5**: Застарівання API — Використання поточних версій API

---

## Наступні кроки

Пройдіть [Кумулятивний тест Частини 3](part3-cumulative-quiz.uk.md), щоб перевірити своє розуміння, а потім переходьте до [Частина 4: Середовище, конфігурація та безпека застосунків](../part4-environment/module-4.1-configmaps.md).
