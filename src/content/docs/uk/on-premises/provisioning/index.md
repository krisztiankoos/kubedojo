---
title: "Підготовка Bare Metal"
sidebar:
  order: 1
---

Як пройти шлях від стійки з порожніми серверами до працюючого кластера Kubernetes? Цей розділ охоплює процес завантаження, встановлення ОС та декларативну інфраструктуру, яка перетворює залізо на платформу.

## Модулі

| Модуль | Опис | Час |
|--------|------|-----|
| [2.1 Основи дата-центру](module-2.1-datacenter-fundamentals/) | Стійки, PDU, UPS, охолодження, IPMI/BMC/Redfish, out-of-band управління | 45 хв |
| [2.2 Підготовка ОС та PXE Boot](module-2.2-pxe-provisioning/) | PXE/UEFI boot, DHCP/TFTP, MAAS, Tinkerbell, autoinstall | 60 хв |
| [2.3 Незмінні ОС для Kubernetes](module-2.3-immutable-os/) | Talos Linux, Flatcar Container Linux, RHCOS, чому незмінність важлива | 45 хв |
| [2.4 Декларативний Bare Metal](module-2.4-declarative-bare-metal/) | Cluster API для bare metal, Metal3, Sidero, життєвий цикл машин | 60 хв |
