# KubeDojo

**Free, comprehensive cloud native education.**

Kubernetes certifications. Platform engineering. SRE. DevSecOps. MLOps.

No paywalls. No upsells. Theory-first.

> **March 2026 Update**: 18 new modules added — FinOps, Kyverno, Chaos Engineering, GPU Scheduling, Cluster API, vCluster, and more. Full K8s 1.35 support. Every module quality-reviewed. [See what's new &rarr;](changelog.md)

---

## 🇺🇦 Присвята

*Цей проєкт присвячується українським ІТ-інженерам, які віддали своє життя, захищаючи Батьківщину.*

*Вони були розробниками, DevOps-інженерами, системними адміністраторами. Вони будували системи, писали код, підтримували інфраструктуру. Коли прийшла війна, вони залишили клавіатури й взяли зброю.*

*Їхній код живе. Їхня жертва — вічна. Слава Україні.*

### Заповіт
*Тарас Шевченко, 1845*

> Як умру, то поховайте  
> Мене на могилі,  
> Серед степу широкого,  
> На Вкраїні милій,  
> Щоб лани широкополі,  
> І Дніпро, і кручі  
> Було видно, було чути,  
> Як реве ревучий.
>
> Як понесе з України  
> У синєє море  
> Кров ворожу... отойді я  
> І лани і гори —  
> Все покину і полину  
> До самого Бога  
> Молитися... а до того  
> Я не знаю Бога.
>
> Поховайте та вставайте,  
> Кайдани порвіте  
> І вражою злою кров'ю  
> Волю окропіте.  
> І мене в сем'ї великій,  
> В сем'ї вольній, новій,  
> Не забудьте пом'янути  
> Незлим тихим словом.

---

## Learning Path

```
                              KUBEDOJO
    ═══════════════════════════════════════════════════════════

    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │   PREREQUISITES                        "Why Kubernetes?"│
    │   └── docs/prerequisites/                               │
    │       ├── Philosophy & Design          4 modules        │
    │       ├── Cloud Native 101             5 modules        │
    │       ├── Kubernetes Basics            8 modules        │
    │       └── Modern DevOps                6 modules        │
    │                                                         │
    └────────────────────────┬────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
    ┌─────────────────────────┐   ┌─────────────────────────┐
    │                         │   │                         │
    │   LINUX DEEP DIVE       │   │   CERTIFICATIONS        │
    │   └── docs/linux/       │   │   └── docs/k8s/         │
    │       │                 │   │       │                 │
    │       ├── foundations/  │   │       │  ENTRY LEVEL    │
    │       │  System · Cgroup│   │       ├── KCNA          │
    │       │  Network        │   │       ├── KCSA          │
    │       │                 │   │       │                 │
    │       ├── security/     │   │       │  PRACTITIONER   │
    │       │  Hardening      │   │       ├── CKAD          │
    │       │                 │   │       ├── CKA           │
    │       └── operations/   │   │       └── CKS           │
    │          Perf · Debug   │   │                         │
    │          Shell Scripts  │   │                         │
    │                         │   │                         │
    └────────────┬────────────┘   └────────────┬────────────┘
                 │                             │
                 └──────────────┬──────────────┘
                                │
                                ▼
    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │   PLATFORM ENGINEERING              Beyond Certifications│
    │   └── docs/platform/                                    │
    │       │                                                 │
    │       ├── foundations/         Theory that doesn't change│
    │       │   Systems Thinking · Reliability · Distributed  │
    │       │   Systems · Observability Theory · Security     │
    │       │                                                 │
    │       ├── disciplines/         Applied practices        │
    │       │   SRE · Platform Engineering · GitOps ·         │
    │       │   DevSecOps · MLOps · AIOps                     │
    │       │                                                 │
    │       └── toolkits/            Current tools (evolving) │
    │           Prometheus · ArgoCD · Vault · Backstage ·     │
    │           Kubeflow · and more...                        │
    │                                                         │
    └─────────────────────────────────────────────────────────┘

    ═══════════════════════════════════════════════════════════
```

---

## Status

| Track | Modules | Status |
|-------|---------|--------|
| [Prerequisites](docs/prerequisites/) | 23 | ✅ Complete |
| [Kubernetes Certifications](docs/k8s/) | 142 | ✅ Complete |
| [Linux Deep Dive](docs/linux/) | 28 | ✅ Complete |
| [Platform Engineering](docs/platform/) | 83 | ✅ Complete |

---

## Where to Start

| You are... | Start here |
|------------|------------|
| New to containers/K8s | [Prerequisites](docs/prerequisites/) |
| Want deep Linux knowledge | [Linux Deep Dive](docs/linux/) |
| Want certifications | [KCNA](docs/k8s/kcna/) (entry) or [CKA](docs/k8s/cka/) (admin) |
| Already certified | [Platform Engineering](docs/platform/) |

---

## Why This Exists

A free, text-based curriculum for learning Kubernetes and platform engineering.

- **Free** — No paywalls, open source
- **Theory-first** — Understand principles before tools
- **Text-based** — Searchable, version-controlled, no videos

**What we are not:** A replacement for paid courses like KodeKloud or Udemy. We don't offer mock exams, video lessons, or hands-on labs for every module. For exam simulation, use [killer.sh](https://killer.sh). For interactive labs, use [killercoda.com](https://killercoda.com).

---

## Philosophy

**Theory before hands-on.** You can't troubleshoot what you don't understand.

**No memorization.** K8s docs are available during exams. We teach navigation, not YAML memorization.

**Principles over tools.** Tools change. Foundations don't. Learn both, in that order.

---

## Contributing

**What we need:**
- **Hands-on exercises** — Real scenarios, not toy examples
- **War stories** — Production incidents that teach lessons
- **Tool expertise** — Deep-dives on ArgoCD, Prometheus, Vault, etc.
- **Error fixes** — Typos, outdated commands, broken YAML

**What we don't build:**
- Exam simulators — Use [killer.sh](https://killer.sh) (included with exam purchase)
- Lab environments — Use [killercoda.com](https://killercoda.com) or local kind/minikube
- Video content — Text-first, searchable, version-controlled

**How to contribute:**
- Open an issue to discuss before large PRs
- Follow existing module structure
- Test all commands and YAML before submitting

---

## License

MIT License. Free to use, share, and modify.

---

*"In the dojo, everyone starts as a white belt. What matters is showing up to train."*
