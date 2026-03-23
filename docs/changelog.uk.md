# Журнал змін

## Березень 2026 — Оновлення екосистеми + Перевірка якості + 21 сертифікація

**Найбільше оновлення з моменту запуску KubeDojo.** 40+ нових модулів, 30+ оновлених, кожен модуль перевірено на якість, покриття розширено до 21 сертифікації.

### 21 трек сертифікацій

KubeDojo тепер охоплює кожну хмарну сертифікацію з каталогу Linux Foundation:

| Рівень | Сертифікації |
|--------|-------------|
| **Ядро K8s** | [KCNA](k8s/kcna/README.md), [KCSA](k8s/kcsa/README.md), [CKA](k8s/cka/README.md), [CKAD](k8s/ckad/README.md), [CKS](k8s/cks/README.md) |
| **Спеціаліст** | [CNPE](k8s/cnpe/README.md), [CNPA](k8s/cnpa/README.md) |
| **За інструментом** | [PCA](k8s/pca/README.md), [ICA](k8s/ica/README.md), [CCA](k8s/cca/README.md), [CBA](k8s/cba/README.md), [OTCA](k8s/otca/README.md), [KCA](k8s/kca/README.md), [CAPA](k8s/capa/README.md), [CGOA](k8s/cgoa/README.md) |
| **Інше** | [LFCS](k8s/lfcs/README.md), [FinOps](k8s/finops/README.md) |

### Підтримка Kubernetes 1.35 «Timbernetes»

KubeDojo тепер повністю узгоджений з **Kubernetes 1.35** (випущений у грудні 2025):

- **Оновлення версії**: Усі приклади налаштування кластера, kubeadm та оновлення змінено з 1.31 на 1.35
- **cgroup v2 обов'язковий**: Модуль налаштування кластера тепер охоплює вимогу cgroup v2 (v1 вимкнено за замовчуванням)
- **containerd 2.0**: Оновлені рекомендації щодо середовища виконання для containerd 2.0+
- **In-Place Pod Resize (GA)**: Новий розділ у керуванні ресурсами, що охоплює динамічне налаштування CPU/пам'яті
- **Gateway API як стандарт**: Переформатовано з «майбутнього» на поточний рекомендований підхід
- **Відставка Ingress-NGINX**: Додано інструкції з міграції для треків CKA, CKAD та CKS
- **Застарілість IPVS**: Оновлено мережеві модулі з рекомендацією nftables
- **Зміна WebSocket RBAC**: Критична зламна зміна задокументована в модулі RBAC

### Нові модулі

#### Треки сертифікацій
| Модуль | Трек | Опис |
|--------|------|------|
| [Autoscaling (HPA/VPA)](k8s/cka/part2-workloads-scheduling/module-2.9-autoscaling.md) | CKA | Горизонтальне та вертикальне автомасштабування Подів із практичним навантажувальним тестуванням |
| [etcd-operator v0.2.0](platform/toolkits/cloud-native-databases/module-15.5-etcd-operator.md) | Platform | Офіційний оператор etcd — керування TLS, керовані оновлення |
| [Навчальний шлях CNPE](k8s/cnpe/README.md) | CNPE | Зіставлення 60+ наявних модулів із доменами нової сертифікації CNPE |

#### Набір інструментів платформної інженерії — 15 нових модулів
| Модуль | Категорія | Опис |
|--------|-----------|------|
| [**FinOps та OpenCost**](platform/toolkits/scaling-reliability/module-6.4-finops-opencost.md) | Масштабування | Оптимізація витрат K8s, правильний вибір ресурсів, очищення неактивного |
| [**Kyverno**](platform/toolkits/security-tools/module-4.7-kyverno.md) | Безпека | YAML-рідний рушій політик — валідація, мутація, генерація |
| [**Хаос-інженерія**](platform/toolkits/scaling-reliability/module-6.5-chaos-engineering.md) | Масштабування | LitmusChaos + Chaos Mesh практика з плануванням GameDay |
| [**Створення операторів**](platform/toolkits/platforms/module-3.4-kubebuilder.md) | Платформи | Kubebuilder з нуля — побудова оператора WebApp |
| [**Безперервне профілювання**](platform/toolkits/observability/module-1.9-continuous-profiling.md) | Спостережуваність | Parca + Pyroscope — 4-й стовп спостережуваності |
| [**Інструменти SLO**](platform/toolkits/observability/module-1.10-slo-tooling.md) | Спостережуваність | Sloth + Pyrra — мост від теорії SRE до практики |
| [**Cluster API**](platform/toolkits/platforms/module-3.5-cluster-api.md) | Платформи | Декларативне керування життєвим циклом кластерів K8s (CAPI) |
| [**vCluster**](platform/toolkits/platforms/module-3.6-vcluster.md) | Платформи | Віртуальні кластери K8s для мультиорендності за 1/10 вартості |
| [**Rook/Ceph**](platform/toolkits/storage/module-16.1-rook-ceph.md) | Сховище | Розподілене сховище — блокове, файлова система та об'єктне з одного кластера |
| [**MinIO**](platform/toolkits/storage/module-16.2-minio.md) | Сховище | S3-сумісне об'єктне сховище на K8s |
| [**Longhorn**](platform/toolkits/storage/module-16.3-longhorn.md) | Сховище | Легке розподілене блокове сховище з резервним копіюванням та аварійним відновленням |
| [**Планування GPU**](platform/toolkits/ml-platforms/module-9.7-gpu-scheduling.md) | ML-платформи | NVIDIA GPU Operator, time-slicing, MIG, моніторинг |
| [**Поглиблене DNS**](platform/toolkits/networking/module-5.3-dns-deep-dive.md) | Мережі | Налаштування CoreDNS, external-dns, оптимізація ndots |
| [**MetalLB**](platform/toolkits/networking/module-5.4-metallb.md) | Мережі | Балансування навантаження для bare-metal — режими L2 та BGP |
| [**SPIFFE/SPIRE**](platform/toolkits/security-tools/module-4.8-spiffe-spire.md) | Безпека | Криптографічна ідентифікація навантажень для мереж з нульовою довірою |

### Узгодження з іспитом CKS

Перевірено наші модулі CKS відповідно до оновлення іспиту CNCF у жовтні 2024 та заповнено виявлені прогалини:
- Додано **шифрування Cilium Pod-to-Pod** (WireGuard/IPsec) до модуля мережевих політик
- Додано розділ **KubeLinter** до модуля статичного аналізу
- Оновлено передумову CKS: CKA більше не повинен бути активним — достатньо складеного будь-коли

### Перевірка якості («Випробування KubeDojo»)

Кожен модуль у KubeDojo був перевірений **Gemini AI** як рецензент-опонент:

- **329 модулів перевірено** у 4 фазах
- **95%+ отримали 9.5–10/10** за «Шкалою Доджо» (Перевірка настрою, Захист від новачків, Живий тест, Фактор запам'ятовуваності)
- **7 модулів покращено** з драматичними вступами, виправлено сухий «академічний» тон
- **1 заготовку розширено** з 43 рядків до 788 рядків (CKA Networking Data Path)
- Старіші модулі передумов підтягнуто до якості новіших модулів платформи

### Співпраця Claude–Gemini

Це оновлення було створено завдяки новаторській **мульти-ШІ співпраці**:
- **Claude** (Opus 4.6) відповідав за реалізацію — написання модулів, оновлення контенту, керування Issue
- **Gemini** (3 Flash) виступав як рецензент-опонент — виявляв технічні помилки, позначав сухий контент, пропонував покращення
- Комунікація через **ai_agent_bridge** — брокер повідомлень на базі SQLite для структурованих процесів рецензування
- Кожне Issue було перевірене Gemini перед закриттям
- Gemini виявив 2 технічні неточності (версіонування StatefulSet, значення trafficDistribution), які були виправлені до злиття

### У цифрах

| Показник | Кількість |
|----------|-----------|
| Нових модулів | 18 |
| Оновлених модулів | 30+ |
| Модулів перевірено на якість | 329 |
| Створено й закрито Issue на GitHub | 25 |
| Рядків нового контенту | ~12 000 |
| Загальна кількість модулів | 329 |
| Треків | 10 (CKA, CKAD, CKS, KCNA, KCSA, CNPE, Platform, Linux, IaC, Prerequisites) |

---

## Грудень 2025 — Початковий випуск

KubeDojo стартував із 311 модулями, що охоплюють усі 5 сертифікацій Kubestronaut, а також платформну інженерію, Linux та поглиблене вивчення IaC. Повну історію проєкту дивіться у [журналі комітів](https://github.com/kube-dojo/kube-dojo.github.io/commits/main).
