---
title: "\u041c\u043e\u0434\u0443\u043b\u044c 1.2: Jobs \u0442\u0430 CronJobs"
slug: uk/k8s/ckad/part1-design-build/module-1.2-jobs-cronjobs
sidebar: 
  order: 2
lab: 
  id: ckad-1.2-jobs-cronjobs
  url: https://killercoda.com/kubedojo/scenario/ckad-1.2-jobs-cronjobs
  duration: "30 min"
  difficulty: intermediate
  environment: kubernetes
---
> **Складність**: `[MEDIUM]` — Ключова навичка CKAD зі специфічними паттернами
>
> **Час на виконання**: 45–50 хвилин
>
> **Передумови**: Модуль 1.1 (Образи контейнерів), розуміння Підів

---

## Що ви зможете робити

Після завершення цього модуля ви зможете:
- **Створити** Jobs та CronJobs з правильними лічильниками завершення, паралелізмом та лімітами повторних спроб
- **Налаштувати** розклад CronJob, політики конкурентності та ліміти історії
- **Діагностувати** невдалі Jobs шляхом перевірки логів Підів, подій та поведінки перезапуску
- **Порівняти** Jobs та CronJobs і обрати правильний ресурс для одноразових та періодичних пакетних навантажень

---

## Чому цей модуль важливий

Не кожне навантаження працює вічно. Резервне копіювання виконується одноразово. Звіти генеруються щогодини. Міграції даних завершуються і зупиняються. Це пакетні навантаження, і Kubernetes обробляє їх за допомогою Jobs та CronJobs.

CKAD активно тестує Jobs, оскільки це ключове завдання розробника. Ви побачите питання на кшталт:
- "Створіть Job, що виконується до завершення"
- "Створіть CronJob, що запускається кожні 5 хвилин"
- "Виправте Job, що не працює"
- "Налаштуйте паралельні Jobs"

> **Аналогія з фабричною зміною**
>
> Деплойменти — як постійний персонал фабрики — вони приходять і працюють, поки їх не звільнять. Jobs — як підрядники, найняті для конкретних завдань — вони приходять, виконують роботу і йдуть. CronJobs — як бригади планового обслуговування — вони з'являються у визначений час (щоночі, щопонеділка), виконують свою роботу і відходять.

---

## Jobs: Одноразові завдання

Job створює один або кілька Підів і гарантує, що вони виконаються до успішного завершення.

### Створення Jobs імперативно

```bash
# Простий Job
k create job backup --image=busybox -- echo "Backup complete"

# Job з командою оболонки
k create job report --image=busybox -- /bin/sh -c "date; echo 'Report generated'"

# Згенерувати YAML
k create job backup --image=busybox --dry-run=client -o yaml -- echo "done" > job.yaml
```

### Структура YAML для Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: backup-job
spec:
  template:
    spec:
      containers:
      - name: backup
        image: busybox
        command: ["sh", "-c", "echo 'Backing up data' && sleep 10"]
      restartPolicy: Never  # або OnFailure
  backoffLimit: 4           # Кількість спроб повтору
  ttlSecondsAfterFinished: 100  # Автоочищення
```

### Ключові властивості Job

| Властивість | Призначення | За замовчуванням |
|-------------|-------------|------------------|
| `restartPolicy` | Що робити при невдачі | Має бути `Never` або `OnFailure` |
| `backoffLimit` | Максимальна кількість повторних спроб | 6 |
| `activeDeadlineSeconds` | Максимальний час виконання Job | Немає (працює нескінченно) |
| `ttlSecondsAfterFinished` | Автовидалення після завершення | Немає (зберігається назавжди) |
| `completions` | Необхідна кількість успішних завершень | 1 |
| `parallelism` | Максимум паралельних Підів | 1 |

### restartPolicy пояснення

```yaml
# Never: Не перезапускати контейнери, що впали (створити новий Під)
restartPolicy: Never
# Під падає → Створюється новий Під (до backoffLimit)

# OnFailure: Перезапустити контейнер, що впав, у тому ж Піді
restartPolicy: OnFailure
# Контейнер падає → Той самий Під перезапускає контейнер
```

---

## Паттерни Jobs

### Паттерн 1: Одне завершення (за замовчуванням)

Запустити один Під, завершити один раз:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: single-job
spec:
  template:
    spec:
      containers:
      - name: worker
        image: busybox
        command: ["echo", "Single task done"]
      restartPolicy: Never
```

### Паттерн 2: Множинні завершення (послідовно)

Виконати завдання N разів, по одному за раз:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: sequential-job
spec:
  completions: 5        # Виконати 5 разів
  parallelism: 1        # По одному за раз
  template:
    spec:
      containers:
      - name: worker
        image: busybox
        command: ["sh", "-c", "echo Task $JOB_COMPLETION_INDEX"]
      restartPolicy: Never
```

### Паттерн 3: Паралельна обробка

Запустити кілька Підів одночасно:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: parallel-job
spec:
  completions: 10       # 10 загальних завершень
  parallelism: 3        # 3 Піди одночасно
  template:
    spec:
      containers:
      - name: worker
        image: busybox
        command: ["sh", "-c", "echo Processing batch && sleep 5"]
      restartPolicy: Never
```

### Паттерн 4: Черга роботи (паралелізм без completions)

Обробляти елементи, поки черга не спорожніє:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: queue-job
spec:
  parallelism: 3        # 3 воркери
  # Без completions: воркери обробляють, поки не завершаться з кодом 0
  template:
    spec:
      containers:
      - name: worker
        image: busybox
        command: ["sh", "-c", "process-queue && exit 0"]
      restartPolicy: Never
```

---

## CronJobs: Заплановані завдання

CronJobs запускають Jobs за розкладом.

### Створення CronJobs імперативно

```bash
# Щохвилини
k create cronjob minute-task --image=busybox --schedule="* * * * *" -- echo "Every minute"

# Щогодини на 30-й хвилині
k create cronjob hourly-task --image=busybox --schedule="30 * * * *" -- date

# Щоденно опівночі
k create cronjob daily-cleanup --image=busybox --schedule="0 0 * * *" -- echo "Daily cleanup"

# Згенерувати YAML
k create cronjob backup --image=busybox --schedule="0 2 * * *" --dry-run=client -o yaml -- /backup.sh > cronjob.yaml
```

### Структура YAML для CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-backup
spec:
  schedule: "0 2 * * *"                    # Щоденно о 2:00
  concurrencyPolicy: Forbid                 # Не перекривати
  successfulJobsHistoryLimit: 3             # Зберігати останні 3 успішні
  failedJobsHistoryLimit: 1                 # Зберігати останній 1 невдалий
  startingDeadlineSeconds: 200              # Максимальна затримка запуску
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: busybox
            command: ["sh", "-c", "echo 'Backup at $(date)'"]
          restartPolicy: OnFailure
```

### Формат розкладу Cron

```
┌───────────── хвилина (0 - 59)
│ ┌───────────── година (0 - 23)
│ │ ┌───────────── день місяця (1 - 31)
│ │ │ ┌───────────── місяць (1 - 12)
│ │ │ │ ┌───────────── день тижня (0 - 6) (Неділя = 0)
│ │ │ │ │
* * * * *
```

### Типові розклади

| Розклад | Значення |
|---------|----------|
| `* * * * *` | Щохвилини |
| `*/5 * * * *` | Кожні 5 хвилин |
| `0 * * * *` | Щогодини (на 0-й хвилині) |
| `0 */2 * * *` | Кожні 2 години |
| `0 0 * * *` | Щоденно опівночі |
| `0 0 * * 0` | Щотижня в неділю опівночі |
| `0 0 1 * *` | Щомісяця 1-го числа опівночі |
| `30 4 * * 1-5` | О 4:30 у робочі дні |

---

## Політики CronJob

### concurrencyPolicy

Що відбувається, якщо новий розклад спрацьовує, поки попередній Job ще працює?

```yaml
spec:
  concurrencyPolicy: Allow    # Запускати одночасно (за замовчуванням)
  # або
  concurrencyPolicy: Forbid   # Пропустити, якщо попередній ще працює
  # або
  concurrencyPolicy: Replace  # Зупинити попередній, запустити новий
```

| Політика | Поведінка | Сценарій використання |
|----------|-----------|----------------------|
| `Allow` | Запускати паралельні Jobs | Незалежні завдання |
| `Forbid` | Пропустити, якщо попередній працює | Уникнення конкуренції за ресурси |
| `Replace` | Зупинити попередній, запустити новий | Важливі найновіші дані |

### startingDeadlineSeconds

Скільки часу Job може бути затриманий, перш ніж його вважатимуть пропущеним:

```yaml
spec:
  startingDeadlineSeconds: 100  # Має стартувати протягом 100с від розкладу
```

Якщо Job не може стартувати протягом цього вікна (проблеми кластера, обмеження ресурсів), він пропускається.

---

## Керування Jobs та CronJobs

### Перевірка статусу

```bash
# Список Jobs
k get jobs

# Список CronJobs
k get cronjobs

# Отримати Піди Job
k get pods -l job-name=my-job

# Перевірити статус Job
k describe job my-job

# Спостерігати за завершенням Job
k get job my-job -w
```

### Перегляд логів

```bash
# Отримати логи з Підa Job
k logs job/my-job

# Отримати логи з конкретного Підa
k logs my-job-abc12

# Стежити за логами
k logs -f job/my-job
```

### Ручний запуск

```bash
# Створити Job з CronJob негайно
k create job manual-backup --from=cronjob/daily-backup
```

### Очищення

```bash
# Видалити Job
k delete job my-job

# Видалити CronJob (також видаляє створені ним Jobs)
k delete cronjob my-cronjob

# Видалити завершені Jobs старші за TTL
# (Автоматично, якщо встановлено ttlSecondsAfterFinished)
```

---

## Усунення проблем з Jobs

### Job не завершується

```bash
# Перевірити статус
k describe job my-job

# Типові проблеми:
# - Команда контейнера завершується з ненульовим кодом
# - Помилка завантаження образу
# - Занадто низькі ліміти ресурсів
# - restartPolicy встановлено неправильно

# Перевірити логи Підa
k logs $(k get pods -l job-name=my-job -o jsonpath='{.items[0].metadata.name}')
```

### Job постійно повторюється

```bash
# Перевірити backoffLimit
k get job my-job -o jsonpath='{.spec.backoffLimit}'

# Якщо досягнуто ліміту, перевірити, чому Піди падають
k describe pods -l job-name=my-job
```

### CronJob не запускається

```bash
# Перевірити статус CronJob
k describe cronjob my-cronjob

# Перевірити час останнього запуску
k get cronjob my-cronjob -o jsonpath='{.status.lastScheduleTime}'

# Перевірити, чи призупинено
k get cronjob my-cronjob -o jsonpath='{.spec.suspend}'

# Відновити, якщо призупинено
k patch cronjob my-cronjob -p '{"spec":{"suspend":false}}'
```

---

## Чи знали ви?

- **Jobs відстежують завершення за допомогою індексу завершення.** У режимі індексованого завершення кожен Під знає свій індекс через змінну середовища `JOB_COMPLETION_INDEX`. Це корисно для обробки шардованих даних.

- **CronJobs за замовчуванням використовують UTC.** Якщо ви встановите `schedule: "0 9 * * *"`, він запуститься о 9:00 UTC, а не за вашим місцевим часом. Деякі кластери підтримують анотації часового поясу.

- **`activeDeadlineSeconds` застосовується до всього часу виконання Job.** Якщо Job триватиме довше за це значення, Kubernetes його зупинить — навіть якщо завдання все ще успішно виконуються.

---

## Типові помилки

| Помилка | Чому це шкодить | Рішення |
|---------|-----------------|---------|
| `restartPolicy: Always` | Недійсне для Jobs | Використовуйте `Never` або `OnFailure` |
| Забули `backoffLimit` | Job повторюється нескінченно | Встановіть розумне обмеження |
| Неправильний синтаксис cron | Job ніколи не запускається | Перевірте через crontab.guru |
| Без `ttlSecondsAfterFinished` | Завершені Jobs накопичуються | Встановіть автоочищення |
| Перекриття CronJobs | Конкуренція за ресурси | Використовуйте `concurrencyPolicy: Forbid` |

---

## Тест

1. **Які допустимі значення restartPolicy для Job?**
   <details>
   <summary>Відповідь</summary>
   `Never` або `OnFailure`. `Always` не допускається для Jobs, оскільки контейнер ніколи не завершився б.
   </details>

2. **Як створити CronJob, що запускається кожні 15 хвилин?**
   <details>
   <summary>Відповідь</summary>
   `kubectl create cronjob myj --image=busybox --schedule="*/15 * * * *" -- echo done`

   `*/15` означає "кожні 15 хвилин".
   </details>

3. **Job має `parallelism: 3` та `completions: 10`. Що відбувається?**
   <details>
   <summary>Відповідь</summary>
   Job запускає до 3 Підів одночасно, поки 10 Підів не завершаться успішно. Він обробляє пакетами: 3 Піди працюють, коли один завершується — запускається інший, поки не буде 10 завершень.
   </details>

4. **Що робить `concurrencyPolicy: Forbid`?**
   <details>
   <summary>Відповідь</summary>
   Якщо CronJob спрацьовує, поки попередній Job ще працює, новий запуск пропускається. Це запобігає перекриванню виконань, які можуть спричинити конкуренцію за ресурси.
   </details>

---

## Практична вправа

**Завдання**: Створити систему резервного копіювання з Jobs та CronJobs.

**Частина 1: Одноразовий Job**
```bash
# Створити Job, що симулює резервне копіювання бази даних
k create job db-backup --image=busybox -- sh -c "echo 'Backing up database' && sleep 5 && echo 'Backup complete'"

# Спостерігати за завершенням
k get job db-backup -w

# Перевірити логи
k logs job/db-backup
```

**Частина 2: Запланований CronJob**
```bash
# Створити CronJob для щогодинного очищення
k create cronjob hourly-cleanup \
  --image=busybox \
  --schedule="0 * * * *" \
  -- sh -c "echo 'Cleanup at $(date)'"

# Ручний запуск для тестування
k create job manual-cleanup --from=cronjob/hourly-cleanup

# Перевірити результати
k get jobs
k logs job/manual-cleanup
```

**Частина 3: Паралельний Job**
```yaml
# Створити parallel-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: parallel-process
spec:
  completions: 6
  parallelism: 2
  template:
    spec:
      containers:
      - name: worker
        image: busybox
        command: ["sh", "-c", "echo Processing item $JOB_COMPLETION_INDEX && sleep 3"]
      restartPolicy: Never
```

```bash
k apply -f parallel-job.yaml
k get pods -l job-name=parallel-process -w
```

**Очищення:**
```bash
k delete job db-backup parallel-process
k delete job manual-cleanup
k delete cronjob hourly-cleanup
```

---

## Практичні вправи

### Вправа 1: Базове створення Job (Ціль: 2 хвилини)

```bash
# Створити Job, який:
# - Назва: hello-job
# - Запускає busybox
# - Виводить "Hello from job"

k create job hello-job --image=busybox -- echo "Hello from job"

# Перевірити завершення
k get job hello-job

# Перевірити логи
k logs job/hello-job

# Очищення
k delete job hello-job
```

### Вправа 2: CronJob з розкладом (Ціль: 2 хвилини)

```bash
# Створити CronJob, який:
# - Назва: every-minute
# - Запускається щохвилини
# - Виводить поточну дату

k create cronjob every-minute --image=busybox --schedule="* * * * *" -- date

# Зачекати 1 хвилину та перевірити
sleep 65
k get jobs

# Перевірити логи запущеного Job
k logs job/$(k get jobs -o jsonpath='{.items[0].metadata.name}')

# Очищення
k delete cronjob every-minute
```

### Вправа 3: Job з повторними спробами (Ціль: 3 хвилини)

```bash
# Створити Job, що зазнає невдачі та повторює спроби
cat << 'EOF' | k apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: retry-job
spec:
  backoffLimit: 3
  template:
    spec:
      containers:
      - name: fail
        image: busybox
        command: ["sh", "-c", "echo 'Trying...' && exit 1"]
      restartPolicy: Never
EOF

# Спостерігати за повторними спробами
k get pods -l job-name=retry-job -w

# Перевірити статус Job
k describe job retry-job | grep -A5 Conditions

# Очищення
k delete job retry-job
```

### Вправа 4: Паралельний Job (Ціль: 4 хвилини)

```bash
# Створити паралельний Job
cat << 'EOF' | k apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: parallel
spec:
  completions: 5
  parallelism: 2
  template:
    spec:
      containers:
      - name: worker
        image: busybox
        command: ["sh", "-c", "echo Worker done && sleep 2"]
      restartPolicy: Never
EOF

# Спостерігати за паралельним виконанням
k get pods -l job-name=parallel -w

# Перевірити, що все завершено
k get job parallel

# Очищення
k delete job parallel
```

### Вправа 5: CronJob з конкурентністю (Ціль: 3 хвилини)

```bash
# Створити CronJob, що забороняє перекриття
cat << 'EOF' | k apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: no-overlap
spec:
  schedule: "* * * * *"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: worker
            image: busybox
            command: ["sh", "-c", "echo 'Start' && sleep 90 && echo 'Done'"]
          restartPolicy: Never
EOF

# Перевірити політику
k get cronjob no-overlap -o jsonpath='{.spec.concurrencyPolicy}'

# Зачекати 2 хвилини та переконатися, що працює лише 1 Job
sleep 120
k get jobs -l job-name=no-overlap

# Очищення
k delete cronjob no-overlap
```

### Вправа 6: Повне рішення для резервного копіювання (Ціль: 8 хвилин)

**Побудуйте повну систему резервного копіювання:**

```bash
# 1. Створити ConfigMap зі скриптом резервного копіювання
k create configmap backup-script --from-literal=script.sh='#!/bin/sh
echo "Starting backup at $(date)"
echo "Compressing data..."
sleep 3
echo "Uploading to storage..."
sleep 2
echo "Backup complete at $(date)"
'

# 2. Створити CronJob, що використовує скрипт
cat << 'EOF' | k apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-system
spec:
  schedule: "*/5 * * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      ttlSecondsAfterFinished: 300
      template:
        spec:
          containers:
          - name: backup
            image: busybox
            command: ["sh", "/scripts/script.sh"]
            volumeMounts:
            - name: scripts
              mountPath: /scripts
          restartPolicy: OnFailure
          volumes:
          - name: scripts
            configMap:
              name: backup-script
EOF

# 3. Тест з ручним запуском
k create job test-backup --from=cronjob/backup-system

# 4. Перевірити логи
k logs job/test-backup

# 5. Перевірити ліміти історії
k get cronjob backup-system -o jsonpath='{.spec.successfulJobsHistoryLimit}'

# Очищення
k delete cronjob backup-system
k delete job test-backup
k delete configmap backup-script
```

---

## Наступний модуль

[Модуль 1.3: Під з кількома контейнерами](/uk/k8s/ckad/part1-design-build/module-1.3-multi-container-pods/) — Паттерни sidecar, init та ambassador.
