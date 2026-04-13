---
title: "Просунуті мережі"
sidebar:
  order: 1
  label: "Просунуті мережі"
---
**Мережа за межами Kubernetes — що відбувається, коли трафік потрапляє в реальний світ.**

Мережа Kubernetes забезпечує взаємодію між подами. Але в реальних умовах трафік проходить крізь DNS-резолвери, CDN, правила WAF, точки пірингу BGP та балансувальники навантаження, перш ніж він потрапить у ваш кластер. Ці модулі охоплюють інфраструктуру, яка з'єднує ваші кластери з Інтернетом.

---

## Модулі

| # | Модуль | Час | Що ви вивчите |
|---|--------|------|-------------------|
| 1.1 | [DNS у масштабі та глобальний трафік](/uk/prerequisites/kubernetes-basics/module-1.1-first-cluster/) | 3 год | Anycast, GeoDNS, DNSSEC, маршрутизація за затримкою |
| 1.2 | [CDN та Edge Computing](/uk/cloud/aws-essentials/module-1.2-vpc/) | 2.5 год | Архітектура PoP, інвалідація кешу, edge-функції |
| 1.3 | [WAF та захист від DDoS](module-1.3-waf-ddos/) | 2.5 год | Правила OWASP, обмеження частоти запитів, бот-менеджмент |
| 1.4 | [BGP та основна маршрутизація](/uk/cloud/aks-deep-dive/module-7.4-aks-production/) | 3.5 год | Піринг AS, вибір шляху, Direct Connect |
| 1.5 | [Глибоке занурення в хмарне балансування](module-1.5-load-balancing/) | 3 год | L4/L7, Proxy Protocol, session affinity |
| 1.6 | [Zero Trust та альтернативи VPN](/uk/cloud/enterprise-hybrid/module-10.9-zero-trust/) | 2.5 год | BeyondCorp, IAP, Tailscale, mTLS |

**Загальний час**: ~17 годин

---

## Передумови

- Базові знання DNS та HTTP
- Kubernetes Ingress/Services (з CKA або Fundamentals)
- Основи мереж Linux (з Linux Deep Dive)
