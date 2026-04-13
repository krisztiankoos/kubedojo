---
title: "Розеттський камінь гіперскейлерів"
slug: uk/cloud/hyperscaler-rosetta-stone
sidebar:
  order: 2
---
**Складність**: [MEDIUM]
**Час на виконання**: 2 години
**Передумови**: Cloud Native 101 (контейнери, основи Docker)

## Чому цей модуль важливий

Наприкінці 2022 року швидкозростаюче фінтех-підприємство вирішило прийняти мультихмарну стратегію, щоб зменшити залежність від постачальника (vendor lock-in) та задовольнити регуляторні вимоги. Їхня основна інфраструктура, що будувалася протягом шести років, була глибоко вкорінена в Amazon Web Services (AWS). Вони використовували IAM-ролі, складний регіональний VPC-піринг та широкий набір сервісів ECS. Коли керівництво інженерного відділу доручило повністю відтворити їхній основний конвеєр обробки транзакцій на Google Cloud Platform (GCP) та Microsoft Azure, команда архітекторів припустила, що міграція буде простою. Вони вважали, що віртуальна машина — це просто віртуальна машина, мережа — це просто мережа, а база даних — це просто база даних.

Це припущення призвело до катастрофічної затримки на шість місяців, мільйонів спалених інвестицій та архітектурної катастрофи, що вимагала повного демонтажу. Команда намагалася перенести регіональну модель VPC від AWS безпосередньо на глобальну архітектуру VPC від GCP, що призвело до накладання підмереж, кошмарів зі складною маршрутизацією та серйозних затримок продуктивності. Вони не зрозуміли, чим сервісні акаунти GCP відрізняються від IAM-ролей AWS, що призвело до хаосу з довговічними, захардкодженими ключами, експортованими між середовищами, що зрештою спричинило серйозний провал аудиту безпеки. В Azure вони намагалися впровадити групування ресурсів точно так само, як теги AWS, ігноруючи нативну ієрархію груп ресурсів Azure, що зламало весь їхній автоматизований конвеєр розгортання та панелі відстеження витрат.

Фундаментальний розрив не був спричинений браком технічних навичок. Це були досвідчені інженери. Провал стався через відсутність вільного володіння специфічними «діалектами» гіперскейлерів. Вони намагалися розмовляти французькою, використовуючи правила іспанської граматики.

Розуміння рівня перекладу між Amazon Web Services (AWS), Google Cloud Platform (GCP) та Microsoft Azure — це не просто запам'ятовування глосарію маркетингових термінів. Це розуміння основоположних філософських відмінностей у тому, як ці платформи були спроєктовані, як їхні мережі маршрутизують пакети та як визначаються їхні периметри безпеки. Вивчаючи цей «Розеттський камінь» хмарних обчислень, інженери можуть плавно переходити між середовищами, проєктувати надійні мультихмарні архітектури, не потрапляючи в концептуальні пастки, та точно оцінювати реальну вартість і операційне навантаження при міграції. Ви навчитеся зіставляти не лише сервіси, а й структурні парадигми, які ними керують. Цей модуль забезпечує цей рівень перекладу.

---

## 1. Управління ідентифікацією та доступом (IAM): Розеттський камінь безпеки

Якщо відкинути брендинг, кожен хмарний провайдер пропонує ті самі базові блоки: спосіб запуску коду, спосіб надання дозволів та спосіб групування ресурсів. Однак реалізація управління ідентифікацією та доступом (IAM) сильно відрізняється і є джерелом найнебезпечніших помилок міграції.

### Основні філософії

Думайте про хмарних провайдерів як про різні операційні системи. AWS дуже гранульований, вимагає явних дозволів для кожної дії та значною мірою покладається на прийняття тимчасових ролей. GCP покладається на більш цілісну структуру на основі проєктів, де ідентифікатори самі по собі розглядаються як ресурси. Azure глибоко інтегрований з корпоративною ідентифікацією (Microsoft Entra ID, раніше Azure AD) і покладається на сувору ієрархічну модель управління.

```text
Порівняння моделей ідентифікації

AWS                          GCP                          Azure
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   AWS Account    │         │  GCP Organization│         │  Entra ID Tenant │
│   (root user)    │         │                  │         │  (Azure AD)      │
│  ┌────────────┐  │         │  ┌────────────┐  │         │  ┌────────────┐  │
│  │ Користувачі│  │         │  │   Папки    │  │         │  │   Групи    │  │
│  │   Групи    │  │         │  │ (опційно)  │  │         │  │ управління │  │
│  │   Ролі     │  │         │  │            │  │         │  │            │  │
│  └────────────┘  │         │  └──────┬─────┘  │         │  └──────┬─────┘  │
│        │         │         │         │        │         │         │        │
│  ┌─────▼──────┐  │         │  ┌──────▼─────┐  │         │  ┌──────▼─────┐  │
│  │  Політики  │  │         │  │  Проєкти   │  │         │  │ Передплати │  │
│  │  (JSON)    │  │         │  │  (межа)    │  │         │  │            │  │
│  │ приєднані  │  │         │  │   ролі     │  │         │  │  ┌────────┐│  │
│  │  до ролі   │  │         │  │ прив'язані │  │         │  │  │ Групи  ││  │
│  └────────────┘  │         │  │ на цьому   │  │         │  │  │ресурсів││  │
│                  │         │  │   рівні    │  │         │  │  └────────┘│  │
│ Ключова концепція:│         │  └────────────┘  │         │  │  RBAC на   │  │
│  "Assume Role"   │         │ Ключова концепція:│         │  │будь-якому  │  │
│ через STS токени │         │ "Прив'язка ролі  │         │  │   рівні    │  │
│                  │         │ до ідентифікатора│         │  └────────────┘  │
│                  │         │  на ресурсі"     │         │ Ключова концепція:│
│                  │         │                  │         │ "Керовані        │
│                  │         │                  │         │  ідентифікатори"  │
└──────────────────┘         └──────────────────┘         └──────────────────┘
```

**Філософія ідентифікації AWS**
AWS використовує модель «заборонено за замовчуванням». Ви створюєте користувачів, групи та ролі. Найважливішою концепцією є **IAM-роль**. Роль — це не користувач; це ідентифікатор, який може бути прийнятий будь-ким (або будь-яким сервісом), хто має на це дозвіл. Дозволи додаються через JSON-політики.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-company-data-bucket/*"
    }
  ]
}
```

```bash
# Створення IAM-ролі для екземпляра EC2
aws iam create-role \
    --role-name my-app-role \
    --assume-role-policy-document file://trust-policy.json

# Приєднання керованої політики
aws iam attach-role-policy \
    --role-name my-app-role \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Створення профілю екземпляра та додавання ролі
aws iam create-instance-profile --instance-profile-name my-app-profile
aws iam add-role-to-instance-profile \
    --instance-profile-name my-app-profile \
    --role-name my-app-role
```

**Філософія ідентифікації GCP**
GCP використовує акаунти Google (для людей) та **сервісні акаунти** (для машин). Сервісний акаунт діє як виділений машинний користувач. Він має власну адресу електронної пошти (наприклад, `my-app@my-project.iam.gserviceaccount.com`). Замість приєднання політик до ідентифікатора, ви прив'язуєте ролі (колекції дозволів) до ідентифікаторів на рівні конкретного ресурсу (проєкту, папки або організації).

```bash
# Створення сервісного акаунта
gcloud iam service-accounts create my-app-sa \
    --display-name="Сервісний акаунт мого застосунку"

# Надання ролі сервісному акаунту в конкретному проєкті
gcloud projects add-iam-policy-binding my-gcp-project-id \
    --member="serviceAccount:my-app-sa@my-gcp-project-id.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"

# Приєднання сервісного акаунта до екземпляра Compute Engine (ключі не потрібні!)
gcloud compute instances create my-vm \
    --service-account=my-app-sa@my-gcp-project-id.iam.gserviceaccount.com \
    --scopes=cloud-platform \
    --zone=us-central1-a
```

**Філософія ідентифікації Azure**
Azure покладається на **управління доступом на основі ролей (RBAC)**, що підтримується Entra ID. Для застосунків ви використовуєте **керовані ідентифікатори** (Managed Identities). Керований ідентифікатор — це ідентифікатор, який автоматично керується в Entra ID і тісно пов'язаний з ресурсом Azure (наприклад, віртуальною машиною). При видаленні ВМ ідентифікатор також видаляється.

```bash
# Створення ВМ із призначеним системою керованим ідентифікатором
az vm create \
    --resource-group my-rg \
    --name my-vm \
    --image Ubuntu2204 \
    --assign-identity '[system]'

# Призначення ролі керованому ідентифікатору для акаунта зберігання
az role assignment create \
    --assignee-object-id <managed-identity-object-id> \
    --role "Storage Blob Data Reader" \
    --scope /subscriptions/<sub-id>/resourceGroups/<rg-name>/providers/Microsoft.Storage/storageAccounts/<account-name>
```

### Таблиця перекладу IAM

| Концепція | AWS | GCP | Azure |
| :--- | :--- | :--- | :--- |
| Ідентифікатор людини | IAM User | Google Account / Cloud Identity | Entra ID User |
| Ідентифікатор машини | IAM Role (assumed) | Service Account | Managed Identity |
| Групування дозволів | IAM Policy (JSON) | Role (наперед визначена або власна) | Role Definition (RBAC) |
| Тимчасові креденшали | STS AssumeRole | Токени сервісного акаунта (авто) | Токени керованого ідентифікатора (авто) |
| Федерація | SAML / OIDC -> IAM | Workload Identity Federation | Entra ID Federation |
| Межа ресурсу | Account | Project | Subscription |
| Організаційне групування | AWS Organizations + OUs | Organization + Folders | Management Groups |
| Крос-сервісна автентифікація | Instance Profiles | Attached Service Account | System-Assigned Identity |

### Повчальна історія: Катастрофа з довговічним ключем

Команда DevOps, що мігрувала застосунок з AWS на GCP, потребувала, щоб їхній застосунок зчитував дані з бакета хмарного сховища. В AWS вони звикли приєднувати IAM Instance Profile до свого екземпляра EC2. Екземпляр EC2 магічним чином отримував тимчасові креденшали.

При переході на GCP вони не змогли знайти «Instance Profiles». Замість того, щоб прочитати документацію про те, як приєднати сервісний акаунт GCP до екземпляра Compute Engine (що працює аналогічно), вони створили сервісний акаунт, згенерували файл JSON з довговічним ключем, запекли цей файл у свій Docker-образ і розгорнули його. Через три місяці розробник випадково пушнув цей Dockerfile у публічний репозиторій. Оскільки ключ був довговічним і мав високі привілеї, зловмисники миттєво отримали доступ до всього їхнього проєкту GCP.

Урок: Завжди перекладайте *суть* моделі безпеки, а не лише механізм. Суть полягала в «тимчасових креденшалах, прив'язаних до екземпляра». Перекладом для AWS IAM Instance Profile є сервісний акаунт GCP, приєднаний до ВМ, або системний керований ідентифікатор Azure.

---

## 2. Мережа: З'єднання частин

Мережа — це сфера, де відбуваються найнепомітніші та найнебезпечніші помилки перекладу. Якщо ви побудуєте мережу GCP за принципами AWS, ви створите зайву складність.

### Парадигми віртуальної приватної хмари (VPC)

VPC — це ваша ізольована мережева межа.

**AWS VPC: Регіональна фортеця**
VPC в AWS суворо **регіональні**. VPC існує в межах одного регіону (наприклад, `us-east-1`). Підмережі всередині цієї VPC прив'язані до конкретних зон доступності (AZ). Якщо у вас є VPC в `us-east-1` і інша VPC в `eu-west-1`, вони повністю ізольовані. Щоб з'єднати їх, ви повинні налаштувати VPC-піринг або Transit Gateway.

```text
+-------------------------------------------------------------+
| Регіональна архітектура AWS                                 |
|                                                             |
|  [VPC us-east-1 (10.0.0.0/16)]                              |
|   |-- [Підмережа AZ-a (10.0.1.0/24)]                        |
|   |-- [Підмережа AZ-b (10.0.2.0/24)]                        |
|                                                             |
|          ^                                                  |
|          | (Вимагає явного пірингу або Transit Gateway)     |
|          v                                                  |
|                                                             |
|  [VPC eu-west-1 (10.1.0.0/16)]                              |
|   |-- [Підмережа AZ-a (10.1.1.0/24)]                        |
+-------------------------------------------------------------+
```

```bash
# Створення VPC в AWS
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --region us-east-1

# Створення підмереж у конкретних AZ
aws ec2 create-subnet \
    --vpc-id vpc-abc123 \
    --cidr-block 10.0.1.0/24 \
    --availability-zone us-east-1a

aws ec2 create-subnet \
    --vpc-id vpc-abc123 \
    --cidr-block 10.0.2.0/24 \
    --availability-zone us-east-1b

# Піринг двох VPC (навіть в одному регіоні це робиться явно)
aws ec2 create-vpc-peering-connection \
    --vpc-id vpc-abc123 \
    --peer-vpc-id vpc-def456 \
    --peer-region eu-west-1
```

**GCP VPC: Глобальний хребет**
VPC в GCP за своєю природою є **глобальними**. Одна VPC може охоплювати всі регіони світу. Підмережі є регіональними. Це означає, що віртуальна машина в Токіо може спілкуватися з віртуальною машиною в Лондоні, використовуючи їхні внутрішні приватні IP-адреси через приватну оптоволоконну мережу Google, без налаштування пірингів чи VPN.

```text
+-------------------------------------------------------------+
| Глобальна архітектура GCP                                   |
|                                                             |
|  [Глобальна VPC (типова)]                                   |
|   |                                                         |
|   |-- [Підмережа us-central1 (10.128.0.0/20)]               |
|   |      (VM A: 10.128.0.2)                                 |
|   |                                                         |
|   |-- [Підмережа europe-west1 (10.132.0.0/20)]              |
|          (VM B: 10.132.0.2)                                 |
|                                                             |
|  * VM A та VM B маршрутизуються одна до одної напряму.      |
+-------------------------------------------------------------+
```

```bash
# Створення власної VPC (вона автоматично стає глобальною)
gcloud compute networks create my-vpc --subnet-mode=custom

# Створення підмереж у різних регіонах — в одній VPC
gcloud compute networks subnets create us-subnet \
    --network=my-vpc \
    --region=us-central1 \
    --range=10.0.1.0/24

gcloud compute networks subnets create eu-subnet \
    --network=my-vpc \
    --region=europe-west1 \
    --range=10.0.2.0/24

# Піринг не потрібен! VM в us-subnet та eu-subnet можуть
# спілкуватися через приватні IP негайно.
```

**Azure VNet: Регіональна мережа**
Віртуальні мережі Azure (VNet), як і в AWS, є **регіональними**. Підмережі за замовчуванням не прив'язані до конкретних зон доступності (хоча ресурси всередині них можуть бути). Для з'єднання VNet потрібен VNet-піринг.

```bash
# Створення VNet в Azure
az network vnet create \
    --resource-group my-rg \
    --name my-vnet \
    --address-prefix 10.0.0.0/16 \
    --location eastus

# Створення підмереж (типово не залежать від AZ)
az network vnet subnet create \
    --resource-group my-rg \
    --vnet-name my-vnet \
    --name web-subnet \
    --address-prefixes 10.0.1.0/24

# Піринг двох VNet
az network vnet peering create \
    --resource-group my-rg \
    --name vnet1-to-vnet2 \
    --vnet-name my-vnet \
    --remote-vnet /subscriptions/<sub>/resourceGroups/rg2/providers/Microsoft.Network/virtualNetworks/vnet2 \
    --allow-vnet-access
```

### Таблиця швидкої довідки з мереж

| Концепція | AWS | GCP | Azure |
| :--- | :--- | :--- | :--- |
| Приватна мережа | VPC (регіональна) | VPC (глобальна) | VNet (регіональна) |
| Область підмережі | На зону доступності | На регіон | На VNet (не прив'язана до AZ) |
| Міжрегіональний приватний зв'язок | VPC Peering / Transit GW | Автоматично (та сама VPC) | VNet Peering / vWAN |
| Правила файрвола | Security Groups + NACLs | Правила файрвола (на VPC) | NSGs + Azure Firewall |
| Приватний DNS | Route 53 Private Zones | Cloud DNS Private Zones | Azure Private DNS |
| VPN шлюз | VPN Gateway | Cloud VPN | VPN Gateway |
| Пряме підключення | Direct Connect | Cloud Interconnect | ExpressRoute |

### Управління трафіком та балансування навантаження

Маршрутизація трафіку користувачів із публічного Інтернету у вашу приватну мережу покладається на керований DNS та балансувальники навантаження.

*   **AWS**: Route 53 — це DNS-сервіс. Для трафіку 7-го рівня (HTTP/HTTPS) ви використовуєте Application Load Balancer (ALB). ALB є регіональними. Для глобального балансування ви повинні використовувати маршрутизацію на основі затримки в Route 53 або AWS Global Accelerator.
*   **GCP**: Cloud DNS керує записами. Хмарне балансування навантаження GCP є величезною перевагою, оскільки воно типово використовує глобальний Anycast IP. Єдина IP-адреса направляє користувачів до найближчого здорового регіону.
*   **Azure**: Azure DNS керує записами. Azure Application Gateway забезпечує регіональне балансування навантаження 7-го рівня. Azure Front Door забезпечує глобальне балансування та можливості CDN.

| Функція балансування | AWS | GCP | Azure |
| :--- | :--- | :--- | :--- |
| Регіональне L7 (HTTP) | ALB | Регіональний HTTP(S) LB | Application Gateway |
| Глобальне L7 (HTTP) | CloudFront + ALB | Глобальний HTTP(S) LB | Front Door |
| Регіональне L4 (TCP/UDP) | NLB | Регіональний TCP/UDP LB | Load Balancer (Standard) |
| Глобальне L4 (TCP/UDP) | Global Accelerator | Глобальний TCP Proxy LB | Front Door / Traffic Manager |
| Маршрутизація за DNS | Route 53 | Cloud DNS (обмежено) | Traffic Manager |
| CDN | CloudFront | Cloud CDN | Azure CDN / Front Door |
| Єдиний глобальний IP? | Ні (мульти-регіон = мульти-IP) | Так (Anycast) | Так (Front Door) |

---

## 3. Обчислювальні примітиви: Від заліза до автомасшабування

До того, як контейнери захопили світ, віртуальні машини були основою хмарних обчислень. Розуміння перекладу чистих обчислень необхідне для застарілих навантажень та систем зі станом.

### Віртуальні машини

Угода про іменування проста:
*   **AWS**: Elastic Compute Cloud (EC2)
*   **GCP**: Google Compute Engine (GCE)
*   **Azure**: Azure Virtual Machines

Проте життєвий цикл та управління відрізняються. AWS активно використовує AMI (Amazon Machine Images), які є регіональними. Якщо ви створюєте AMI в `us-east-1`, ви повинні явно скопіювати її в `us-west-2`, щоб запускати там екземпляри. Кастомні образи GCP є глобальними ресурсами; образ, створений в одному регіоні, миттєво доступний усюди.

```bash
# AWS: Запуск екземпляра EC2
aws ec2 run-instances \
    --image-id ami-0abcdef1234567890 \
    --instance-type t3.medium \
    --key-name my-key \
    --subnet-id subnet-abc123 \
    --security-group-ids sg-abc123

# GCP: Запуск екземпляра Compute Engine
gcloud compute instances create my-vm \
    --machine-type=e2-medium \
    --zone=us-central1-a \
    --image-family=debian-12 \
    --image-project=debian-cloud

# Azure: Запуск віртуальної машини
az vm create \
    --resource-group my-rg \
    --name my-vm \
    --image Ubuntu2204 \
    --size Standard_B2s \
    --admin-username azureuser \
    --generate-ssh-keys
```

### Іменування типів екземплярів: Прихована складність

Кожна хмара має власну угоду про іменування розмірів машин. Розуміння патернів економить купу часу.

| AWS (приклад) | GCP (приклад) | Azure (приклад) | Приблизний еквівалент |
| :--- | :--- | :--- | :--- |
| `t3.micro` | `e2-micro` | `Standard_B1s` | Burstable, 1 vCPU, ~1 ГБ |
| `t3.medium` | `e2-medium` | `Standard_B2s` | Burstable, 2 vCPU, ~4 ГБ |
| `m5.xlarge` | `n2-standard-4` | `Standard_D4s_v5` | Загального призн., 4 vCPU, ~16 ГБ |
| `c5.2xlarge` | `c2-standard-8` | `Standard_F8s_v2` | Опт. для обчислень, 8 vCPU |
| `r5.large` | `Highmem-2` | `Standard_E2s_v5` | Опт. для пам'яті, 2 vCPU |
| `p3.2xlarge` | `a2-highgpu-1g` | `Standard_NC6s_v3` | Екземпляр із GPU, 1 GPU |

### Автомасштабування та групи екземплярів

Будуючи відмовостійкі архітектури, ви ніколи не запускаєте одну ВМ. Ви запускаєте групи ВМ, які автоматично розширюються під навантаженням та самовідновлюються при збоях.

*   **AWS: Auto Scaling Groups (ASG)**. Ви визначаєте шаблон запуску (Launch Template), вказуючи AMI, тип екземпляра та IAM-роль, і створюєте ASG, що охоплює кілька AZ у межах регіону.
*   **GCP: Managed Instance Groups (MIG)**. Ви визначаєте шаблон екземпляра (Instance Template). MIG можуть бути зональними (одна зона) або регіональними (охоплюють кілька зон).
*   **Azure: Virtual Machine Scale Sets (VMSS)**. Подібно до ASG, VMSS дозволяє створювати та керувати групою ідентичних ВМ із балансуванням навантаження.

### Повчальна історія: Нездорова перевірка стану

Інженерна група перекладала архітектуру AWS на Azure. В AWS їхній ALB перевіряв стан екземплярів EC2 за допомогою HTTP-ендпоінта (`/healthz`). Якщо екземпляр виходив з ладу, ASG видаляв його і запускав новий.

В Azure вони налаштували Azure Load Balancer та VMSS. Вони налаштували перевірку стану балансувальника на `/healthz`. Балансувальник правильно припинив надсилати трафік на нездорові вузли. Проте ВМ ніколи не замінювалися. Вони не усвідомили, що в Azure перевірка стану балансувальника лише керує маршрутизацією трафіку. Для авто-відновлення (видалення та заміни ВМ) їм потрібно було налаштувати *Application Health Extension* безпосередньо на VMSS. Вони припустили, що балансувальник керує життєвим циклом ВМ — це було AWS-центричне припущення, яке призвело до масштабного збою в продакшні під час стрибка трафіку.

---

## 4. Екосистема контейнерів: Автономні, керований K8s та Serverless

Сучасні застосунки рідко працюють на чистих віртуальних машинах. Вони працюють у контейнерах або як безсерверні функції. Гіперскейлери пропонують кілька рівнів абстракції для цих навантажень.

### Автономні контейнери (Контейнери як сервіс)

Коли у вас є Docker-образ і ви просто хочете його запустити без керування віртуальними машинами чи складними платформами оркестрації типу Kubernetes:

*   **AWS: ECS з Fargate**. Elastic Container Service (ECS) — це власний оркестратор контейнерів Amazon. Fargate — це безсерверний двигун обчислень для контейнерів. Ви визначаєте задачу (Task Definition), вказуєте на образ, а AWS надає ресурси "на льоту".
*   **GCP: Cloud Run**. Cloud Run побудований на Knative. Він дозволяє запускати контейнери HTTP без збереження стану. Його величезна перевага — здатність масштабуватися до абсолютного нуля, коли немає трафіку, що не коштує вам нічого.
*   **Azure: Azure Container Instances (ACI) або Azure Container Apps**. ACI призначений для простих розгортань одного контейнера. Azure Container Apps — це більш надійне безсерверне середовище, оптимізоване для мікросервісів і побудоване на базі Kubernetes та KEDA (Kubernetes Event-driven Autoscaling).

```bash
# AWS: Розгортання контейнера в ECS Fargate (спрощено)
aws ecs create-service \
    --cluster my-cluster \
    --service-name my-service \
    --task-definition my-task:1 \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-abc],securityGroups=[sg-abc]}"

# GCP: Розгортання контейнера в Cloud Run (одна команда!)
gcloud run deploy my-service \
    --image=gcr.io/my-project/my-app:latest \
    --platform=managed \
    --region=us-central1 \
    --allow-unauthenticated

# Azure: Розгортання контейнера в Azure Container Apps
az containerapp create \
    --name my-app \
    --resource-group my-rg \
    --environment my-env \
    --image myregistry.azurecr.io/my-app:latest \
    --target-port 8080 \
    --ingress external
```

### Порівняння безсерверних контейнерів

| Функція | AWS ECS Fargate | GCP Cloud Run | Azure Container Apps |
| :--- | :--- | :--- | :--- |
| Масштаб до нуля | Ні (мінімум 1 задача) | Так | Так |
| Макс. таймаут запиту | Без обмежень | 60 хв (HTTP) | 30 хв |
| Підтримка GPU | Так | Так | Так |
| Побудовано на | Власній (ECS) | Knative | Kubernetes + KEDA |
| Мінімальна одиниця білінгу | 1 секунда | 100 мс | 1 секунда |
| Макс. vCPU на екземпляр | 16 | 8 | 4 |
| Макс. пам'ять на екземпляр | 120 ГБ | 32 ГБ | 16 ГБ |
| Інтеграція з VPC | Нативна | VPC Connector | Інтеграція з VNet |
| Sidecar контейнери | Так | Так | Так |

### Керований Kubernetes: Великий зрівнювач

Kubernetes — це великий зрівнювач хмари. API стандартний; маніфест розгортання Kubernetes виглядає абсолютно однаково, чи працює він на Amazon, Google чи Microsoft. Однак керовані сервіси огортають площину управління (control plane) по-різному.

Завжди переконуйтеся, що ваші кластери працюють на сучасних підтримуваних версіях (наприклад, Kubernetes 1.35+), щоб використовувати останній Gateway API, покращене управління ресурсами та патчі безпеки. Зазвичай ви будете взаємодіяти з усіма трьома за допомогою `kubectl` (часто аліас `k`).

```text
Порівняння архітектури керованого Kubernetes

AWS EKS                      GCP GKE                      Azure AKS
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│ Площина управління│         │ Площина управління│         │ Площина управління│
│ (Керується AWS)  │         │ (Керується Google)│         │ (Керується Azure) │
│  ┌────────────┐  │         │  ┌────────────┐  │         │  ┌────────────┐  │
│  │ API Server │  │         │  │ API Server │  │         │  │ API Server │  │
│  │ etcd       │  │         │  │ etcd       │  │         │  │ etcd       │  │
│  │ scheduler  │  │         │  │ scheduler  │  │         │  │ scheduler  │  │
│  │ controller │  │         │  │ controller │  │         │  │ controller │  │
│  └────────────┘  │         │  └────────────┘  │         │  └────────────┘  │
│ Вартість: ~$73/міс│         │ Вартість: $0(std)│         │ Вартість: $0(free)│
│                  │         │ $73/міс (autoplt)│         │ $73/міс (std)    │
└────────┬─────────┘         └────────┬─────────┘         └────────┬─────────┘
         │                            │                            │
┌────────▼─────────┐         ┌────────▼─────────┐         ┌────────▼─────────┐
│  Робочі вузли    │         │  Робочі вузли    │         │  Робочі вузли    │
│  ┌────────────┐  │         │  ┌────────────┐  │         │  ┌────────────┐  │
│  │ Керовані   │  │         │  │ Standard:  │  │         │  │ Node Pools │  │
│  │ групи вузлів│  │         │  │  Пули вузлів│  │         │  │ (на базі   │  │
│  │ (на базі EC2)│  │         │  │ Autopilot: │  │         │  │  VMSS)     │  │
│  │ ВИ керуєте │  │         │  │  Без вузлів │  │         │  │ ВИ керуєте │  │
│  └────────────┘  │         │  └────────────┘  │         │  └────────────┘  │
│                  │         │                  │         │                  │
│  CNI: VPC CNI    │         │  CNI: Dataplane  │         │  CNI: Azure CNI  │
│  (pod = VPC IP)  │         │  V2 (Cilium/eBPF)│         │  або CNI Overlay │
│                  │         │                  │         │                  │
│  Auth: IAM +     │         │  Auth: Google    │         │  Auth: Entra ID  │
│  OIDC (складно)  │         │  IAM (нативно)   │         │  + Azure RBAC    │
└──────────────────┘         └──────────────────┘         └──────────────────┘
```

*   **AWS EKS (Elastic Kubernetes Service)**: Гнучко налаштовується, але потребує найбільших операційних витрат. Ви відповідаєте за управління групами вузлів, оновлення основних надбудов (як-от CNI та CoreDNS) та управління складною інтеграцією між AWS IAM та Kubernetes RBAC (через OIDC). Це "Linux" серед керованих K8s.
*   **GCP GKE (Google Kubernetes Engine)**: Вважається золотим стандартом. Google винайшов Kubernetes, і GKE глибоко інтегрований. GKE Autopilot робить крок вперед, керуючи всією інфраструктурою, включаючи вузли; ви платите лише за запити ресурсів подів.
*   **Azure AKS (Azure Kubernetes Service)**: Пропонує глибоку інтеграцію з Azure Active Directory (Entra ID) та інструментами розробника. Забезпечує швидке створення кластерів та надійну інтеграцію з мережевим стеком Azure.

```bash
# AWS: Створення кластера EKS
eksctl create cluster \
    --name my-cluster \
    --region us-east-1 \
    --version 1.35 \
    --nodegroup-name workers \
    --node-type t3.medium \
    --nodes 3

# GCP: Створення кластера GKE Autopilot
gcloud container clusters create-auto my-cluster \
    --region=us-central1 \
    --cluster-version=1.35

# Azure: Створення кластера AKS
az aks create \
    --resource-group my-rg \
    --name my-cluster \
    --kubernetes-version 1.35 \
    --node-count 3 \
    --node-vm-size Standard_B2s \
    --generate-ssh-keys
```

```yaml
# Стандартний Deployment Kubernetes — це найкращий Розеттський камінь.
# Цей самий маніфест працює без змін на EKS, GKE та AKS.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rosetta-frontend
  labels:
    app: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: web
        image: nginx:1.25-alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 250m
            memory: 256Mi
```

### Порівняння керованого Kubernetes

| Функція | AWS EKS | GCP GKE | Azure AKS |
| :--- | :--- | :--- | :--- |
| Вартість control plane | ~$73/місяць | Безкоштовно (Std), ~$73 (Autopilot/Ent) | Безкоштовно (Free), ~$73 (Std) |
| Безсерверні вузли | Fargate профілі | Autopilot (повністю керовані) | Віртуальні вузли (на базі ACI) |
| CNI за замовчуванням | VPC CNI (IP з VPC) | Dataplane V2 (Cilium/eBPF) | Azure CNI / CNI Overlay |
| Авто-провіженінг вузлів | Karpenter | Autopilot / NAP | Karpenter (preview) |
| Макс. вузлів у кластері | 5,000 | 15,000 | 5,000 |
| Час створення кластера | ~15 хвилин | ~5 хвилин (Autopilot) | ~8 хвилин |
| Вбудований service mesh | App Mesh (заст.) | Istio (керований) | Istio (керований) |
| Підтримка Windows-вузлів | Так | Так | Так |
| Підтримка GPU | Так | Так (з драйверами) | Так |
| Мультикластерне управл. | Немає (використ. Argo/Flux) | Fleet (мультикластер) | Azure Arc |

### Безсерверні функції (Serverless)

Для короткоживучого коду, що реагує на події (наприклад, завантаження файлу в сховище або HTTP-запит):

*   **AWS: AWS Lambda**. Піонер безсерверності. Підтримує багато мов, глибоко інтегрується з SQS, SNS та API Gateway.
*   **GCP: Cloud Functions**. Чудово підходить для легкої обробки даних та інтеграції вебхуків.
*   **Azure: Azure Functions**. Унікальний сервіс завдяки «прив'язкам» (bindings), які декларативно з'єднують функції з іншими сервісами Azure (наприклад, CosmosDB або Service Bus) без написання шаблонного коду з'єднання.

### Порівняння безсерверних функцій

| Функція | AWS Lambda | GCP Cloud Functions | Azure Functions |
| :--- | :--- | :--- | :--- |
| Макс. час виконання | 15 хвилин | 60 хвилин (2-ге пок.) | 10 хв (Cons.), безліміт (Ded.) |
| Макс. пам'ять | 10 ГБ | 32 ГБ (2-ге пок.) | 14 ГБ (Premium) |
| Мови | Node, Py, Java, Go, .NET, Ruby | Node, Py, Java, Go, .NET, Ruby, PHP | Node, Py, Java, C#, F#, PS |
| Холодний старт | ~100-500 мс | ~100-500 мс | ~200 мс-2 с (Cons.) |
| Резервована потужність | Так | Так (min instances) | Так (Premium plan) |
| Підтримка образів | Так | Так (2-ге пок.) | Так |
| Джерела подій | 200+ інтеграцій AWS | Eventarc + Pub/Sub | Event Grid + Service Bus |
| Унікальна фішка | Шари, розширення | На базі Cloud Run | Durable Functions (stateful) |
| Безкоштовний рівень | 1 млн запитів/міс | 2 млн викликів/міс | 1 млн викликів/міс |

---

## 5. Сховища, бази даних та спостережуваність

Ви не можете експлуатувати застосунок, якщо не можете зберігати його стан, керувати даними та моніторити здоров'я.

### Парадигми зберігання

Об'єктне сховище — основа хмарних озер даних, бекапів та статичних активів.
*   **AWS: Amazon S3 (Simple Storage Service)**. Галузевий стандарт. Використовує бакети (buckets).
*   **GCP: Cloud Storage (GCS)**. Функціонально ідентичний S3, використовує бакети, пропонує сувору глобальну узгодженість.
*   **Azure: Azure Blob Storage**. Існує в межах облікового запису зберігання Azure (Azure Storage Account). Ви створюєте контейнери, а всередині них зберігаєте блоби.

```bash
# AWS: Завантаження файлу в S3
aws s3 cp my-file.tar.gz s3://my-bucket/backups/

# GCP: Завантаження файлу в Cloud Storage
gcloud storage cp my-file.tar.gz gs://my-bucket/backups/

# Azure: Завантаження файлу в Blob Storage
az storage blob upload \
    --account-name mystorageaccount \
    --container-name backups \
    --file my-file.tar.gz \
    --name my-file.tar.gz
```

### Порівняння рівнів зберігання

Кожен провайдер пропонує рівні зберігання для оптимізації витрат. Концепція однакова: «гарячі» дані (частий доступ) коштують дорожче за ГБ, але дешевше при зчитуванні; «холодні» дані коштують менше за ГБ, але дорожче при зчитуванні.

| Патерн доступу | AWS S3 | GCP Cloud Storage | Azure Blob Storage |
| :--- | :--- | :--- | :--- |
| Частий доступ | S3 Standard | Standard | Hot |
| Нечастий доступ | S3 Standard-IA | Nearline (мін. 30 днів) | Cool (мін. 30 днів) |
| Архівний | S3 Glacier Instant Retr. | Coldline (мін. 90 днів) | Cold (мін. 90 днів) |
| Глибокий архів | S3 Glacier Deep Archive | Archive (мін. 365 днів) | Archive (мін. 180 днів) |
| Інтелектуальний рівень| S3 Intelligent-Tiering | Autoclass | Зміна рівня (вручну/політика) |
| ~Ціна ГБ/міс (гарячий) | $0.023 | $0.020 | $0.018 |
| ~Ціна ГБ/міс (холодний) | $0.004 (Glacier IR) | $0.004 (Coldline) | $0.002 (Cold) |
| Мін. термін зберігання | Немає (Standard) | Немає (Standard) | Немає (Hot) |

Блочне сховище забезпечує підключені диски для віртуальних машин.
*   **AWS**: Elastic Block Store (EBS).
*   **GCP**: Persistent Disk (PD).
*   **Azure**: Managed Disks.

### Реляційні бази даних

Керовані PostgreSQL та MySQL доступні всюди.
*   **AWS**: Amazon RDS або Amazon Aurora (власний двигун, сумісний з MySQL/PostgreSQL).
*   **GCP**: Cloud SQL або Cloud Spanner (глобально розподілена реляційна база даних).
*   **Azure**: Azure Database for PostgreSQL / MySQL.

### Таблиця перекладу сервісів баз даних

| Тип бази даних | AWS | GCP | Azure |
| :--- | :--- | :--- | :--- |
| Керовані PostgreSQL/MySQL | RDS | Cloud SQL | Database for PostgreSQL/MySQL |
| Високопрод. реляційні | Aurora | AlloyDB | Hyperscale (Citus) |
| Глобальні реляційні | Aurora Global DB | Cloud Spanner | Cosmos DB (relational API) |
| Key-value / NoSQL | DynamoDB | Firestore / Bigtable | Cosmos DB |
| Кеш у пам'яті | ElastiCache (Redis) | Memorystore | Azure Cache for Redis |
| Документна БД | DocumentDB | Firestore | Cosmos DB (MongoDB API) |
| Сховище даних (Warehouse) | Redshift | BigQuery | Synapse Analytics |
| Пошук | OpenSearch Service | (Elastic on GCP) | Azure AI Search |

### Спостережуваність та телеметрія

Розуміння поведінки системи вимагає уніфікованих логів та метрик.

*   **AWS**: Amazon CloudWatch. Ви використовуєте CloudWatch Metrics для продуктивності та CloudWatch Logs для виводу застосунків. Може здаватися фрагментованим, часто потребує додаткових сервісів, як X-Ray, для трасування.
*   **GCP**: Cloud Operations (раніше Stackdriver). Дуже уніфікований. Логи, метрики та трасування тісно інтегровані.
*   **Azure**: Azure Monitor. Надає комплексні метрики. Application Insights — надзвичайно потужний інструмент у межах Azure Monitor для глибокого моніторингу продуктивності коду.

| Стовп спостережуваності | AWS | GCP | Azure |
| :--- | :--- | :--- | :--- |
| Метрики | CloudWatch Metrics | Cloud Monitoring | Azure Monitor Metrics |
| Логи | CloudWatch Logs | Cloud Logging | Log Analytics |
| Трасування | X-Ray | Cloud Trace | Application Insights |
| Дашборди | CloudWatch Dashboards | Cloud Monitoring Dashboards | Azure Dashboards / Grafana |
| Алертинг | CloudWatch Alarms + SNS | Cloud Alerting | Azure Monitor Alerts |
| APM | X-Ray + CloudWatch | Cloud Profiler + Trace | Application Insights |
| Уніфікований досвід? | Ні (фрагментовано) | Так (Cloud Ops suite) | Переважно (Monitor як хаб) |

---

## 6. CI/CD: Збірка та розгортання в різних хмарах

Кожен гіперскейлер має нативну пропозицію CI/CD. Вони варіюються від тісно інтегрованих, але специфічних (Azure DevOps) до мінімалістичних (GCP Cloud Build). Розуміння нативних інструментів важливе, навіть якщо ви стандартизуєтеся на GitHub Actions чи GitLab CI, оскільки нативні інтеграції з IAM та реєстрами завжди тісніші.

### Співставлення сервісів CI/CD

| Можливість CI/CD | AWS | GCP | Azure |
| :--- | :--- | :--- | :--- |
| Контроль версій | CodeCommit (заст.) | Cloud Source Repos (заст.) | Azure Repos |
| Сервіс збірки | CodeBuild | Cloud Build | Azure Pipelines |
| Оркестрація конвеєрів | CodePipeline | Cloud Build (тригери + кроки) | Azure Pipelines (multi-stage) |
| Реєстр артефактів | ECR (конт.), CodeArtifact | Artifact Registry | Azure Container Reg., Artifacts |
| Сервіс розгортання | CodeDeploy | Cloud Deploy | Azure Pipelines (release) |
| Розгортання IaC | CloudFormation | Deployment Manager (заст.) / TF | ARM Templates / Bicep |

### Філософська відмінність

**AWS CodePipeline** — це оркестратор на основі стадій. Ви визначаєте стадії Source, Build, Test та Deploy. Кожна стадія містить дії, що виконуються через CodeBuild, CodeDeploy або Lambda. Він жорсткий, але передбачуваний.

**GCP Cloud Build** — це білдер на основі кроків. Ви пишете `cloudbuild.yaml` з послідовними кроками, кожен з яких працює в контейнері. Він гнучкий і більше нагадує Makefile, ніж продукт для конвеєрів. Google значною мірою перейшов на стандартизацію Cloud Deploy для фази розгортання.

**Azure DevOps Pipelines** — найбільш повна пропозиція. Включає дошки (управління проєктами), репозиторії, конвеєри, плани тестування та артефакти в одному продукті. Багатостадійні конвеєри YAML можуть нативно моделювати складні воркфлоу релізів зі схваленнями та стратегіями розгортання (canary, blue-green).

```yaml
# AWS CodeBuild buildspec.yml
version: 0.2
phases:
  install:
    commands:
      - echo Installing dependencies...
  build:
    commands:
      - echo Building the app...
      - docker build -t my-app .
  post_build:
    commands:
      - docker push $ECR_REPO:$CODEBUILD_RESOLVED_SOURCE_VERSION
```

```yaml
# GCP Cloud Build cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/my-app:$COMMIT_SHA', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/my-app:$COMMIT_SHA']
images:
  - 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/my-app:$COMMIT_SHA'
```

```yaml
# Azure Pipelines azure-pipelines.yml
trigger:
  - main
pool:
  vmImage: 'ubuntu-latest'
steps:
  - task: Docker@2
    inputs:
      command: buildAndPush
      repository: my-app
      containerRegistry: myACRConnection
      tags: $(Build.SourceVersion)
```

---

## 7. Інфраструктура як код (IaC): Нативні інструменти

Хоча Terraform та OpenTofu є міжхмарним стандартом (розглядається в нашому треку IaC), кожен провайдер має нативний інструмент IaC.

| Характеристика | AWS CloudFormation | GCP Deployment Manager | Azure ARM / Bicep |
| :--- | :--- | :--- | :--- |
| Мова | JSON або YAML | YAML + Jinja2/Python | JSON (ARM) або Bicep (DSL) |
| Управління станом | Кероване AWS | Кероване GCP | Кероване Azure |
| Відкат при збої | Автоматично | Вручну | Автоматично |
| Попередній перегляд | Change Sets | Preview | What-if |
| Мультирегіон | StackSets | Вручну | Deployment Stacks |
| Прийняття спільнотою | Високе (legacy) | Низьке (застаріло) | Зростає (Bicep) |
| Рекомендація | Для чистого AWS | Використовуйте Terraform | Для чистого Azure |

Найважливіше: **GCP Deployment Manager фактично застарів** на користь Terraform. Google активно рекомендує Terraform. AWS CloudFormation залишається першокласним інструментом, але тільки для AWS. Azure Bicep активно розвивається, але Terraform залишається стандартом для мультихмари.

---

## 8. Моделі ціноутворення: Найнебезпечніший переклад

Найдорожча мультихмарна помилка — не технічна, а фінансова. Кожен провайдер пропонує механізми знижок, які не перекладаються 1:1.

### Ціноутворення за запитом (On-Demand)

Всі три провайдери стягують плату за секунду (або годину) за обчислення. Ціни на схожі типи екземплярів дуже близькі, але не ідентичні.

| Екземпляр (~4 vCPU, 16 ГБ) | AWS | GCP | Azure |
| :--- | :--- | :--- | :--- |
| Назва типу | m5.xlarge | n2-standard-4 | Standard_D4s_v5 |
| On-demand (US, Linux, /год) | ~$0.192 | ~$0.194 | ~$0.192 |
| Місяць (730 год) | ~$140 | ~$142 | ~$140 |

Годинні витрати майже однакові. Справжні відмінності з'являються в механізмах знижок та передачі даних.

### Механізми знижок

| Тип знижки | AWS | GCP | Azure |
| :--- | :--- | :--- | :--- |
| Зобов'язання (1-3 р) | Reserved Inst. / Sav. Plans | Committed Use Disc. (CUDs) | Reserved VM Instances |
| Типова економія 1 рік | 30-40% | 28-37% | 30-40% |
| Типова економія 3 роки | 50-60% | 52-57% | 55-65% |
| Автоматичні знижки | Немає | Sustained Use Disc. (до 30%) | Немає |
| Preemptible / Spot | Spot Instances (до -90%) | Spot VMs (до -91%) | Spot VMs (до -90%) |
| Попередження про зупинку| 2 хвилини | 30 секунд | 30 секунд |
| Безкоштовний рівень | 750 год/міс t2.micro (12 м)| e2-micro always-free | 750 год/міс B1s (12 м) |

### Перевага Sustained Use Discount у GCP

GCP унікальний тим, що пропонує **Sustained Use Discounts (SUDs)** автоматично. Якщо ви запускаєте екземпляр більше 25% місяця, GCP починає нараховувати знижку. До кінця повного місяця ви отримуєте до 30% знижки без жодних зобов'язань. AWS та Azure не пропонують нічого подібного; ви повинні активно купувати Reserved Instances.

### Вихід трафіку (Data Egress): Прихована вартість

Передача даних між хмарами та в Інтернет — це місце, де рахунки вибухають.

| Тип передачі | AWS | GCP | Azure |
| :--- | :--- | :--- | :--- |
| Вхід (data in) | Безкоштовно | Безкоштовно | Безкоштовно |
| Трафік в одній зоні | Безкоштовно | Безкоштовно | Безкоштовно |
| Міжзоновий (один регіон)| ~$0.01/ГБ | Безкоштовно | Безкоштовно |
| Міжрегіональний | $0.01-0.02/ГБ | $0.01-0.08/ГБ | $0.02-0.05/ГБ |
| Вихід в інет (перші 10 ТБ)| ~$0.09/ГБ | ~$0.12/ГБ | ~$0.087/ГБ |

Критична відмінність: **AWS стягує плату за міжзоновий трафік (cross-AZ)** у межах одного регіону. Якщо ваші мікросервіси розподілені між AZ для високої доступності, кожен виклик API між зонами коштує грошей. GCP та Azure не беруть плату за трафік між зонами.

---

## Чи знали ви?

1. Глобальна мережа Google Cloud обробляє значний відсоток усього світового інтернет-трафіку до того, як він потрапить у публічну мережу. Це тому, що їхня глобальна VPC використовує той самий приватний фізичний оптоволоконний хребет, що обслуговує YouTube та Google Пошук у всьому світі.
2. AWS S3 був запущений у 2006 році з простим інтерфейсом SOAP та REST як один із перших публічних хмарних сервісів. Він масштабувався астрономічно і тепер зберігає понад сто трильйонів окремих об'єктів.
3. Azure Active Directory (тепер Entra ID) обробляє понад тридцять мільярдів запитів автентифікації щодня. Завдяки глибокій інтеграції з Microsoft 365 та Office, він діє як основний хребет ідентифікації для більшості компаній Fortune 500.
4. Хоча Kubernetes вважається стандартом, плагіни CNI від гіперскейлерів повністю змінюють поведінку вашого кластера. AWS VPC CNI призначає нативні IP-адреси VPC кожному поду, що може швидко вичерпати IP підмережі, тоді як GCP та Azure часто використовують оверлейні мережі за замовчуванням.

---

## Типові помилки

| Помилка | Чому це стається | Як виправити |
| :--- | :--- | :--- |
| **Регіональна логіка AWS у GCP** | Інженери вважають, що VPC мають бути явно з'єднані між регіонами. | Використовуйте глобальну VPC GCP за замовчуванням. |
| **Плутанина IAM Roles та Service Accounts** | Спроба приєднати сервісний акаунт GCP точно як IAM Role в AWS, або генерація ключів. | Використовуйте Workload Identity Federation та приєднуйте сервісні акаунти безпосередньо до ВМ. |
| **Ігнорування різниці CNI у керованому K8s** | Припущення, що вичерпання IP працює однаково в EKS та GKE. | Плануйте набагато більші блоки CIDR підмереж в AWS через особливості VPC CNI. |
| **Сліпий перенос конвеєрів CI/CD** | Копіювання кроків AWS CodePipeline 1:1 в GitHub Actions або Azure DevOps. | Перепроєктуйте конвеєр під сильні сторони цільової платформи. |
| **Недооцінка вартості виходу даних** | Припущення, що передача даних між регіонами коштує всюди однаково. | Проєктуйте системи так, щоб тримати інтенсивний трафік у межах однієї зони або регіону. |
| **Припущення, що 'Serverless' має однакові ліміти** | AWS Lambda має інші обмеження за часом та обсягом даних, ніж Azure Functions. | Перевіряйте ліміти та таймаути перед міграцією безсерверних архітектур. |
| **Переклад AWS тегів у Azure Resource Groups** | Azure покладається на групи ресурсів як обов'язкові межі розгортання. | Не використовуйте групи ресурсів лише для тегування. Використовуйте їх для управління життєвим циклом. |
| **Ігнорування витрат між AZ на AWS** | На GCP та Azure трафік між зонами безкоштовний. На AWS — ні. | На AWS враховуйте ціну ~$0.01/ГБ при проєктуванні систем високої доступності. |

---

## Тест

1. **Якщо ваша архітектура сильно залежить від міжрегіонального приватного зв'язку, дизайн VPC якого провайдера спрощує це найбільше?**
   <details>
   <summary>Відповідь</summary>
   Google Cloud Platform (GCP). VPC в GCP є глобальними ресурсами за замовчуванням, що дозволяє підмережам у різних регіонах спілкуватися приватно без пірингів.
   </details>

2. **Ви мігруєте веб-застосунок з AWS ECS Fargate. Який сервіс у Google Cloud є найближчим еквівалентом, що масштабується до нуля?**
   <details>
   <summary>Відповідь</summary>
   Cloud Run. Це безсерверна платформа для контейнерів, яка автоматично масштабується і дозволяє економити при відсутності трафіку.
   </details>

3. **В AWS ви надаєте дозволи EC2 через IAM Role. Як досягти того самого результату в GCP для Compute Engine?**
   <details>
   <summary>Відповідь</summary>
   Ви приєднуєте сервісний акаунт безпосередньо до екземпляра Compute Engine при створенні. ВМ аутентифікується за допомогою тимчасових креденшалів цього акаунта.
   </details>

4. **Правда чи хибна думка: AWS S3, GCP Cloud Storage та Azure Blob Storage мають єдину глобальну точку входу для читання/запису без вказання регіону?**
   <details>
   <summary>Відповідь</summary>
   Хибна думка. Хоча глобальні ендпоінти існують для певних завдань, зазвичай потрібно вказувати регіональні ендпоінти для забезпечення продуктивності та дотримання законів про зберігання даних.
   </details>

---

## Практична вправа

**Сценарій**: Ви — провідний хмарний архітектор медіа-компанії, яка розширює свою платформу доставки контенту з AWS на Azure та GCP для забезпечення високої доступності. Ваше завдання — перекласти поточну архітектуру AWS у нативні сервіси інших провайдерів.

**Базова архітектура AWS:**
*   **Мережа**: Одинарна VPC у `us-east-1` з публічними та приватними підмережами у двох зонах доступності (AZ).
*   **Обчислення**: Флот EC2 під управлінням Auto Scaling Group (ASG).
*   **Трафік**: Application Load Balancer (ALB) для маршрутизації HTTP/HTTPS.
*   **Сховище**: S3 бакет для медіафайлів.
*   **База даних**: Amazon RDS для PostgreSQL.
*   **Спостережуваність**: CloudWatch для метрик та логів.

**Завдання:**

- [ ] **Завдання 1: Спроектуйте переклад для GCP**
    Зіставте сервіси AWS із відповідниками GCP. Зверніть увагу на структуру VPC та групування екземплярів.

<details>
<summary>Рішення для Завдання 1</summary>

*   **Мережа**: Глобальна VPC. Створюємо регіональну підмережу в `us-east4`.
*   **Обчислення**: Екземпляри Compute Engine (GCE) у складі регіональної Managed Instance Group (MIG).
*   **Трафік**: Global External HTTP(S) Load Balancer (Anycast IP).
*   **Сховище**: Бакет Cloud Storage (GCS).
*   **База даних**: Cloud SQL для PostgreSQL.
*   **Спостережуваність**: Cloud Operations (Stackdriver).
</details>

- [ ] **Завдання 2: Спроектуйте переклад для Microsoft Azure**
    Зіставте сервіси з нативними відповідниками Azure, фокусуючись на термінології груп та балансування.

<details>
<summary>Рішення для Завдання 2</summary>

*   **Мережа**: Azure Virtual Network (VNet) у регіоні `East US`.
*   **Обчислення**: Azure Virtual Machines у складі Virtual Machine Scale Sets (VMSS).
*   **Трафік**: Azure Application Gateway (регіональний L7).
*   **Сховище**: Azure Blob Storage (Storage Account).
*   **База даних**: Azure Database for PostgreSQL.
*   **Спостережуваність**: Azure Monitor + Application Insights.
</details>

- [ ] **Завдання 3: Переклад безпеки ідентифікації**
    Як замінити AWS IAM Instance Profile у GCP та Azure?

<details>
<summary>Рішення для Завдання 3</summary>

*   **GCP**: Створити сервісний акаунт, надати йому роль `roles/storage.objectViewer` на бакет і приєднати до шаблону екземпляра MIG.
*   **Azure**: Увімкнути "System-Assigned Managed Identity" на VMSS і через RBAC надати роль "Storage Blob Data Reader" на контейнер зберігання.
</details>

- [ ] **Завдання 4: Переклад для керованого Kubernetes**
    Компанія переходить на K8s (v1.35+). Назвіть сервіси та їхні нативні CNI плагіни.

<details>
<summary>Рішення для Завдання 4</summary>

*   **AWS**: Amazon EKS. CNI: Amazon VPC CNI (IP з VPC).
*   **GCP**: Google GKE. CNI: GKE Dataplane V2 (Cilium/eBPF).
*   **Azure**: Azure AKS. CNI: Azure CNI або Azure CNI Overlay.
</details>

---

## Наступний модуль

Готові зануритися в екосистему Amazon і опанувати інструменти найпопулярнішого хмарного провайдера? Переходьте до **[Основ AWS DevOps](/uk/cloud/aws-essentials/)**.
