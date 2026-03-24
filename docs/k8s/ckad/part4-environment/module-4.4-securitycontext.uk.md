# Модуль 4.4: SecurityContexts

> **Складність**: `[MEDIUM]` — Важливо для безпеки, численні налаштування
>
> **Час на виконання**: 40–50 хвилин
>
> **Передумови**: Базові концепції користувачів/груп Linux, Модуль 1.1 (Поди)

---

## Чому цей модуль важливий

SecurityContexts визначають параметри привілеїв та контролю доступу для подів і контейнерів. Вони контролюють, від якого користувача працює контейнер, які можливості він має та до чого може отримати доступ на хості.

На іспиті CKAD перевіряють:
- Встановлення ідентифікаторів користувача та групи
- Запуск від імені не-root
- Керування можливостями (capabilities) Linux
- Права доступу до файлової системи

> **Аналогія з охороною будівлі**
>
> SecurityContext — це як політики безпеки будівлі. Ви контролюєте, хто може увійти (runAsUser), до яких зон вони мають доступ (capabilities), чи можуть вони щось змінювати (readOnlyRootFilesystem) і чи мають вони майстер-ключі (privileged). Різні орендарі (контейнери) в одній будівлі (поді) можуть мати різні рівні доступу.

---

## Рівні SecurityContext

### Рівень пода проти рівня контейнера

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: security-demo
spec:
  securityContext:        # Рівень пода (застосовується до всіх контейнерів)
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
  containers:
  - name: app
    image: nginx
    securityContext:      # Рівень контейнера (перевизначає рівень пода)
      runAsUser: 2000
      allowPrivilegeEscalation: false
```

**Пріоритет**: Налаштування рівня контейнера перевизначають налаштування рівня пода.

---

## Загальні налаштування

### Запуск від користувача/групи

```yaml
securityContext:
  runAsUser: 1000       # UID, від якого запускати
  runAsGroup: 3000      # GID для процесу
  fsGroup: 2000         # GID для змонтованих томів
```

### Запуск від не-root

```yaml
securityContext:
  runAsNonRoot: true    # Помилка, якщо образ намагається запуститися від root
```

### Ескалація привілеїв

```yaml
securityContext:
  allowPrivilegeEscalation: false  # Заборонити отримання додаткових привілеїв
```

### Файлова система лише для читання

```yaml
securityContext:
  readOnlyRootFilesystem: true     # Контейнер не може писати у файлову систему
```

### Привілейований контейнер

```yaml
securityContext:
  privileged: true      # Повний доступ до хоста (НЕБЕЗПЕЧНО — рідко потрібно)
```

---

## Можливості (capabilities) Linux

Можливості надають конкретні привілеї root без повного root-доступу:

```yaml
securityContext:
  capabilities:
    add:
    - NET_ADMIN          # Конфігурація мережі
    - SYS_TIME           # Системний годинник
    drop:
    - ALL                # Спочатку видалити всі можливості
```

### Поширені можливості

| Можливість | Призначення |
|------------|-------------|
| `NET_ADMIN` | Конфігурація мережі |
| `NET_BIND_SERVICE` | Прив'язка до портів < 1024 |
| `SYS_TIME` | Зміна системного годинника |
| `SYS_PTRACE` | Відлагодження інших процесів |
| `CHOWN` | Зміна власника файлів |

### Найкраща практика: видалити всі, додати конкретні

```yaml
securityContext:
  capabilities:
    drop:
    - ALL
    add:
    - NET_BIND_SERVICE
```

---

## Повні приклади

### Безпечний під (не-root)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
  containers:
  - name: app
    image: nginx
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: cache
      mountPath: /var/cache/nginx
    - name: run
      mountPath: /var/run
  volumes:
  - name: tmp
    emptyDir: {}
  - name: cache
    emptyDir: {}
  - name: run
    emptyDir: {}
```

### Під з правами доступу до томів

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: volume-perms
spec:
  securityContext:
    runAsUser: 1000
    fsGroup: 2000         # Файли тому належать цій групі
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'ls -la /data && sleep 3600']
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    emptyDir: {}
```

---

## Візуалізація

```
┌─────────────────────────────────────────────────────────────┐
│                Ієрархія SecurityContext                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SecurityContext пода                                        │
│  ┌─────────────────────────────────────────────────┐       │
│  │ runAsUser: 1000                                 │       │
│  │ runAsGroup: 3000                                │       │
│  │ fsGroup: 2000 (для томів)                       │       │
│  │                                                 │       │
│  │  Контейнер A            Контейнер B             │       │
│  │  ┌────────────────┐   ┌────────────────┐       │       │
│  │  │ (успадковує    │   │ runAsUser: 2000│       │       │
│  │  │  від пода)     │   │ (перевизначає  │       │       │
│  │  │ runAsUser:1000 │   │  під)          │       │       │
│  │  │                │   │                │       │       │
│  │  │ capabilities:  │   │ readOnly: true │       │       │
│  │  │  drop: [ALL]   │   │                │       │       │
│  │  └────────────────┘   └────────────────┘       │       │
│  └─────────────────────────────────────────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Перевірка параметрів безпеки

```bash
# Перевірити, від якого користувача працює процес
k exec my-pod -- id
# uid=1000 gid=3000 groups=2000

# Перевірити власника файлів у томі
k exec my-pod -- ls -la /data
# drwxrwsrwx 2 root 2000 ...

# Перевірити можливості
k exec my-pod -- cat /proc/1/status | grep Cap
```

---

## Швидка довідка

```yaml
# Рівень пода
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    runAsNonRoot: true

# Рівень контейнера
containers:
- name: app
  securityContext:
    runAsUser: 1000
    allowPrivilegeEscalation: false
    readOnlyRootFilesystem: true
    privileged: false
    capabilities:
      drop: ["ALL"]
      add: ["NET_BIND_SERVICE"]
```

---

## Чи знали ви?

- **`fsGroup` впливає лише на монтування томів.** Файли, створені в emptyDir або PVC, отримують цю групу-власника. Звичайна файлова система контейнера не зачіпається.

- **`runAsNonRoot: true` — це перевірка під час виконання.** Якщо стандартний користувач образу контейнера — root (UID 0), контейнер не запуститься.

- **Можливості (capabilities) специфічні для Linux.** На контейнерах Windows налаштування capabilities ігноруються.

- **`readOnlyRootFilesystem` ламає багато застосунків**, яким потрібно записувати тимчасові файли. Використовуйте томи emptyDir для /tmp та подібних шляхів.

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| `runAsNonRoot` з root-образом | Контейнер не запуститься | Використовуйте `runAsUser: 1000` явно |
| `readOnlyRootFilesystem` без tmpfs | Застосунок не може писати тимчасові файли | Змонтуйте emptyDir до /tmp |
| Не видаляти capabilities | Більша поверхня атаки | Завжди `drop: [ALL]`, додавайте конкретні |
| Плутати контекст пода/контейнера | Застосовуються неправильні налаштування | Контейнер перевизначає під |
| `privileged: true` без необхідності | Ризик безпеки | Лише для конкретних системних інструментів |

---

## Тест

1. **Яка різниця між securityContext на рівні пода та на рівні контейнера?**
   <details>
   <summary>Відповідь</summary>
   Налаштування на рівні пода застосовуються до всіх контейнерів у поді. Налаштування на рівні контейнера перевизначають налаштування рівня пода для цього конкретного контейнера.
   </details>

2. **Що контролює `fsGroup`?**
   <details>
   <summary>Відповідь</summary>
   `fsGroup` встановлює групу-власника файлів у змонтованих томах. Процеси запускаються з цією групою як додатковою.
   </details>

3. **Що відбувається, якщо встановити `runAsNonRoot: true`, але образ за замовчуванням використовує root?**
   <details>
   <summary>Відповідь</summary>
   Контейнер не запуститься. Потрібно також встановити `runAsUser` з ненульовим UID.
   </details>

4. **Як дозволити контейнеру прив'язуватися до порту 80 без запуску від root?**
   <details>
   <summary>Відповідь</summary>
   Додайте можливість `NET_BIND_SERVICE`:
   ```yaml
   capabilities:
     add: ["NET_BIND_SERVICE"]
   ```
   </details>

---

## Практична вправа

**Завдання**: Налаштувати параметри безпеки для подів.

**Частина 1: Запуск від не-root**
```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: nonroot-pod
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'id && sleep 3600']
EOF

k logs nonroot-pod
# Має показати: uid=1000 gid=3000 groups=3000
```

**Частина 2: Демонстрація fsGroup**
```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: fsgroup-pod
spec:
  securityContext:
    runAsUser: 1000
    fsGroup: 2000
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'ls -la /data && id && sleep 3600']
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    emptyDir: {}
EOF

k logs fsgroup-pod
# Файли в /data належать групі 2000
```

**Частина 3: Файлова система лише для читання**
```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: readonly-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'touch /test 2>&1 || echo "Cannot write!"; sleep 3600']
    securityContext:
      readOnlyRootFilesystem: true
EOF

k logs readonly-pod
# Має показати: Cannot write!
```

**Очищення:**
```bash
k delete pod nonroot-pod fsgroup-pod readonly-pod
```

---

## Практичні вправи

### Вправа 1: Запуск від користувача (Ціль: 2 хвилини)

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill1
spec:
  securityContext:
    runAsUser: 1000
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'id && sleep 3600']
EOF

k logs drill1
k delete pod drill1
```

### Вправа 2: Примусовий запуск від не-root (Ціль: 2 хвилини)

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill2
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
  containers:
  - name: app
    image: busybox
    command: ['sleep', '3600']
EOF

k get pod drill2
k delete pod drill2
```

### Вправа 3: Можливості (Ціль: 3 хвилини)

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill3
spec:
  containers:
  - name: app
    image: busybox
    command: ['sleep', '3600']
    securityContext:
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE
EOF

k exec drill3 -- cat /proc/1/status | grep Cap
k delete pod drill3
```

### Вправа 4: Лише для читання з тимчасовою директорією (Ціль: 3 хвилини)

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill4
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'touch /tmp/test && echo "Wrote to /tmp" && sleep 3600']
    securityContext:
      readOnlyRootFilesystem: true
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {}
EOF

k logs drill4
k delete pod drill4
```

### Вправа 5: Перевірка fsGroup (Ціль: 3 хвилини)

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill5
spec:
  securityContext:
    fsGroup: 2000
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'touch /data/file && ls -la /data && sleep 3600']
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    emptyDir: {}
EOF

k logs drill5
# Файл має належати групі 2000
k delete pod drill5
```

### Вправа 6: Повністю безпечний під (Ціль: 5 хвилин)

```bash
cat << 'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: drill6
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 2000
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'id && ls -la /data && sleep 3600']
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    emptyDir: {}
EOF

k logs drill6
k get pod drill6 -o yaml | grep -A20 securityContext
k delete pod drill6
```

---

## Наступний модуль

[Модуль 4.5: Сервісні акаунти](module-4.5-serviceaccounts.uk.md) — Налаштування ідентифікації подів для доступу до API.
